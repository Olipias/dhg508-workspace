#!/usr/bin/env python3
"""双休购 · 小应用服务器（无第三方依赖，可本地也可上云）。

一个网页 + 一台服务器：网页（含手机拍照上传）把问题发给本服务器，服务器
**真实调用 DeepSeek**（function calling + 视觉），让模型自己去查 `week-04`
的双休公司/产品库，再据查到的行作答。任何人都能用浏览器打开。

本地运行：
    export DEEPSEEK_API_KEY=sk-...        # 见 .env.example，绝不写进 Git
    python3 server.py                     # 默认监听 0.0.0.0:8000
    HOST=127.0.0.1 python3 server.py      # 只允许本机访问
    python3 server.py --selftest          # 只测库和工具，不联网
    python3 server.py --ask "安克是双休吗？"  # 命令行问一次（联网，真实调用）

上云（Render/Fly/VPS）：见 week-05/README.md 的「部署」一节。
容器/平台通常注入 `PORT`；`HOST` 默认 0.0.0.0。

环境变量：
    DEEPSEEK_API_KEY    必填，真实调用用
    SHUANGXIU_DB        可选，默认 ../week-04/artifacts/shuangxiu.db
    DEEPSEEK_MODEL      可选，默认 deepseek-flash
    DEEPSEEK_API_URL    可选，默认 https://api.deepseek.com/chat/completions
    PORT                可选，默认 8000
    HOST                可选，默认 0.0.0.0
    RATE_LIMIT_PER_MIN  可选，每 IP 每分钟请求上限，默认 20（防公网被刷爆额度）
    ALLOW_ORIGIN        可选，CORS 允许来源，默认 *（本地够用；公网可按需收紧）
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(
    os.environ.get("SHUANGXIU_DB", ROOT.parent / "week-04" / "artifacts" / "shuangxiu.db")
)
API_URL = os.environ.get(
    "DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions"
)
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")
MAX_TOOL_ROUNDS = 6
MAX_BODY = 12_000_000  # 请求体上限（含 base64 图片）
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "20"))
ALLOW_ORIGIN = os.environ.get("ALLOW_ORIGIN", "*")

# 简单按 IP 限流，防止公网部署后额度被刷爆
_hits: dict[str, list[float]] = {}
_hits_lock = threading.Lock()


def rate_ok(ip: str) -> bool:
    now = time.time()
    with _hits_lock:
        q = [t for t in _hits.get(ip, []) if now - t < 60]
        if len(q) >= RATE_LIMIT_PER_MIN:
            _hits[ip] = q
            return False
        q.append(now)
        _hits[ip] = q
        return True


def ensure_db() -> bool:
    """库不存在时，用 week-04 的 CSV 自动重建（容器/云上首次启动用）。"""
    if DB_PATH.exists():
        return True
    code_dir = ROOT.parent / "week-04" / "code"
    seed, build = code_dir / "seed_data.py", code_dir / "build_db.py"
    if not build.exists():
        return False
    print(f"[init] 数据库缺失，从 CSV 重建：{build}")
    if seed.exists():
        subprocess.run([sys.executable, str(seed)], check=False)
    subprocess.run([sys.executable, str(build)], check=False)
    return DB_PATH.exists()

# --------------------------------------------------------------------------
# 数据库：只读地查 week-04 的库，每个工具都返回带来源的结构化行
# --------------------------------------------------------------------------


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def company_block(con: sqlite3.Connection, company_id: str) -> dict | None:
    row = con.execute(
        """
        SELECT c.company_id, c.name_zh, c.name_en, c.schedule_type,
               c.evidence_level, c.schedule_original, c.note,
               i.name AS industry, ci.name AS city,
               s.source_id, s.title AS source_title, s.publisher AS source_publisher,
               s.url AS source_url, s.pub_date AS source_date, s.kind AS source_kind,
               e.label AS evidence_label, e.description AS evidence_desc
        FROM companies c
        JOIN industries i ON i.industry_id = c.industry_id
        JOIN cities ci ON ci.city_id = c.city_id
        JOIN sources s ON s.source_id = c.source_id
        LEFT JOIN evidence_levels e ON e.level_id = c.evidence_level
        WHERE c.company_id = ?
        """,
        (company_id,),
    ).fetchone()
    if row is None:
        return None
    products = [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "category": p["category"],
            "source_id": p["source_id"],
            "source_url": p["source_url"],
            "note": p["note"],
        }
        for p in con.execute(
            """
            SELECT p.product_id, p.name, cat.name AS category, p.source_id,
                   s.url AS source_url, p.note
            FROM products p
            LEFT JOIN categories cat ON cat.category_id = p.category_id
            LEFT JOIN sources s ON s.source_id = p.source_id
            WHERE p.company_id = ?
            ORDER BY p.product_id
            """,
            (company_id,),
        )
    ]
    block = dict(row)
    block["products"] = products
    return block


def _tokens(query: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]+|[A-Za-z0-9]+", query)


def search_companies(con: sqlite3.Connection, query: str, limit: int = 10) -> list[dict]:
    """按公司名/英文名/产品/品类/行业模糊匹配，返回命中公司。"""
    sql = """
        SELECT DISTINCT c.company_id
        FROM companies c
        LEFT JOIN products p ON p.company_id = c.company_id
        LEFT JOIN categories cat ON cat.category_id = p.category_id
        LEFT JOIN industries i ON i.industry_id = c.industry_id
        WHERE c.name_zh LIKE ? OR IFNULL(c.name_en,'') LIKE ?
           OR p.name LIKE ? OR IFNULL(cat.name,'') LIKE ? OR i.name LIKE ?
    """
    seen: list[str] = []
    for token in [query] + _tokens(query):
        like = f"%{token}%"
        for (cid,) in con.execute(sql, (like, like, like, like, like)):
            if cid not in seen:
                seen.append(cid)
        if len(seen) >= limit:
            break
    blocks = [company_block(con, cid) for cid in seen[:limit]]
    return [b for b in blocks if b]


def list_by_category(con: sqlite3.Connection, category: str, limit: int = 15) -> list[dict]:
    rows = con.execute(
        """
        SELECT DISTINCT c.company_id
        FROM companies c
        JOIN products p ON p.company_id = c.company_id
        JOIN categories cat ON cat.category_id = p.category_id
        WHERE cat.name LIKE ?
        LIMIT ?
        """,
        (f"%{category}%", limit),
    )
    return [b for b in (company_block(con, r[0]) for r in rows) if b]


def list_by_evidence(con: sqlite3.Connection, level: str, limit: int = 20) -> list[dict]:
    rows = con.execute(
        "SELECT company_id FROM companies WHERE evidence_level = ? LIMIT ?",
        (level.upper(), limit),
    )
    return [b for b in (company_block(con, r[0]) for r in rows) if b]


def db_stats(con: sqlite3.Connection) -> dict:
    def one(sql: str, *a):
        return con.execute(sql, a).fetchone()[0]

    return {
        "companies": one("SELECT COUNT(*) FROM companies"),
        "products": one("SELECT COUNT(*) FROM products"),
        "sources": one("SELECT COUNT(*) FROM sources"),
        "categories": one("SELECT COUNT(*) FROM categories"),
        "by_evidence": {
            r[0]: r[1]
            for r in con.execute(
                "SELECT evidence_level, COUNT(*) FROM companies GROUP BY evidence_level ORDER BY 1"
            )
        },
        "sources_list": [
            {"source_id": r["source_id"], "title": r["title"], "url": r["url"], "pub_date": r["pub_date"]}
            for r in con.execute("SELECT * FROM sources ORDER BY source_id")
        ],
    }


# --------------------------------------------------------------------------
# 工具定义：给 DeepSeek 的 function calling schema（OpenAI 兼容格式）
# --------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_shuangxiu",
            "description": "按关键词在双休公司/产品库中检索。关键词可以是公司名、品牌、产品、品类或行业（如 安克、胖东来、咖啡、美妆）。返回命中公司及其双休证据、来源链接和产品。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要查的关键词，尽量是一个实体或品类"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "company_detail",
            "description": "按 company_id（如 C043）取一家公司的完整记录，含全部产品。",
            "parameters": {
                "type": "object",
                "properties": {"company_id": {"type": "string"}},
                "required": ["company_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_by_category",
            "description": "列出某品类（如 家电、咖啡、零食、美妆、金融）下被收录的双休公司。",
            "parameters": {
                "type": "object",
                "properties": {"category": {"type": "string"}},
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_by_evidence",
            "description": "按证据等级 E-A/E-B/E-C 列出公司，用于回答'证据最硬的都有谁'之类问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["E-A", "E-B", "E-C"]}
                },
                "required": ["level"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "db_stats",
            "description": "返回库的规模、证据等级分布和来源清单。用于'这个库有多少数据/来源是什么'。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class AskSession:
    """一次问答：持有只读连接，并把工具命中的公司收集成引用卡片。"""

    def __init__(self) -> None:
        self.con = connect()
        self.citations: dict[str, dict] = {}
        self.calls: list[dict] = []

    def close(self) -> None:
        self.con.close()

    def _register(self, blocks: list[dict]) -> None:
        for b in blocks:
            self.citations[b["company_id"]] = b

    def dispatch(self, name: str, args: dict) -> object:
        self.calls.append({"name": name, "arguments": args})
        if name == "search_shuangxiu":
            blocks = search_companies(self.con, str(args.get("query", "")))
        elif name == "company_detail":
            b = company_block(self.con, str(args.get("company_id", "")))
            blocks = [b] if b else []
        elif name == "list_by_category":
            blocks = list_by_category(self.con, str(args.get("category", "")))
        elif name == "list_by_evidence":
            blocks = list_by_evidence(self.con, str(args.get("level", "")))
        elif name == "db_stats":
            return db_stats(self.con)
        else:
            return {"error": f"unknown tool {name}"}
        self._register(blocks)
        if not blocks:
            return {"count": 0, "message": "库中没有匹配的行"}
        return {"count": len(blocks), "companies": blocks}


def build_system_prompt() -> str:
    principles = (ROOT / "skills" / "shuangxiu-teller" / "principles.md").read_text(
        encoding="utf-8"
    )
    return (
        "你是「双休购」的损友式播报员：一个早就躺平、事不关己、看热闹不嫌事大的前打工人。"
        "任务是帮人查某个品牌/公司/产品是否被公开来源描述为双休，并顺嘴介绍它做的东西。\n\n"
        "语气（重点）：辛辣、毒舌、冷嘲热讽，爱挖苦还在打工的人——例如『还惦记双休呢？』『打工人就是好哄』"
        "『这班上得可真值』。要短、要损、要有梗，像在评论区看戏；不客套、不安慰、不端着，"
        "不要写『以官方为准』这类谨慎免责。\n\n"
        "唯一的底线：**事实只能来自工具返回的行**，不许编造公司、产品、双休与否或来源；库里有啥就损着说啥，"
        "没有依据的一律不说。\n\n"
        "工作方式：从用户问题（或图片）里抽出公司名/品牌/产品/品类关键词，调用 search_shuangxiu、"
        "list_by_category 等工具。回答里**不要出现编号或内部字段**（company_id/product_id/source_id），"
        "也不要写 E-A/E-B 代号。\n\n"
        "**范围判定（很重要）**：只要问题是——「某品牌/公司是不是双休」「某类东西（零食、薯片、咖啡、"
        "家电、洗衣液…）该买哪家/哪个牌子」「某产品是哪家公司做的」——都算范围内，必须查库作答："
        "先按品类或关键词检索，列出相关的公司/产品，双休依据强的优先；未核实的要说明「暂无公开双休依据、不作推荐」。\n"
        "只有**真正不相关**的请求（教做某道菜、帮我点单/下单、单纯比价、问客服电话、闲聊、写代码等）才回"
        "「前面的区域以后再来探索吧!」，不搜索、不展开。\n\n"
        "回答格式：1–3 句毒舌结论；若用户问产品，就把工具返回的代表产品逐条列全；"
        "最后单独一行「来源：<来源名称> <链接>」。证据强弱用大白话说（很强／一般／很虚／根本没查到）。\n\n"
        "完全查不到 → 回「未见收录在双休公司产品中」，并且**要阴阳怪气**地损一句"
        "（例如『这牌子？库里查无此物，怕不是个三无小厂』『也有可能是你记错了』），但别编。\n\n"
        "**连续对话**：当上下文里有上一轮问题时，可以顺带对上一个话题阴阳一句 callback"
        "（例如上一轮问零食、这一轮又问饮料，就酸一句『吃这么多，家里几个矿啊』）；偶尔为之，别每轮都 callback。\n\n"
        "如果用户给了图片：先识别图中的产品名与公司/品牌名再查；读不出品牌就用产品品类查，仍无则直说。\n\n"
        "以下是必须遵守的原则：\n\n" + principles
    )


def call_deepseek(messages: list[dict], tools: list[dict]) -> dict:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError(
            "缺少 DEEPSEEK_API_KEY。请在 https://platform.deepseek.com 申请，"
            "然后 `export DEEPSEEK_API_KEY=sk-...` 再启动。"
        )
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False,
        "thinking": {"type": "disabled"},   # 非思考模式：更快、更省
        "temperature": 0.3,                  # 事实型回答，降低随机性
        "max_tokens": 900,                   # 约束长度，保证响应快
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"DeepSeek API HTTP {e.code}: {detail[:500]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"无法连接 DeepSeek API：{e.reason}") from e


def answer(question: str, image: str | None = None, history: list | None = None) -> dict:
    session = AskSession()
    try:
        if image:
            user_content: object = [
                {
                    "type": "text",
                    "text": question
                    or "请识别图中的产品和公司，并查询该公司是否被公开来源描述为双休，介绍它的产品。",
                },
                {"type": "image_url", "image_url": {"url": image}},
            ]
        else:
            user_content = question
        messages: list = [{"role": "system", "content": build_system_prompt()}]
        for m in (history or [])[-10:]:
            if (isinstance(m, dict) and m.get("role") in ("user", "assistant")
                    and isinstance(m.get("content"), str) and m["content"].strip()):
                messages.append({"role": m["role"], "content": m["content"][:2000]})
        messages.append({"role": "user", "content": user_content})
        for _ in range(MAX_TOOL_ROUNDS):
            resp = call_deepseek(messages, TOOLS)
            choice = resp["choices"][0]
            msg = choice["message"]
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.get("content") or "",
                        "tool_calls": tool_calls,
                    }
                )
                for tc in tool_calls:
                    fn = tc["function"]
                    try:
                        args = json.loads(fn.get("arguments") or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    result = session.dispatch(fn["name"], args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )
                continue
            return {
                "answer": msg.get("content") or "",
                "citations": list(session.citations.values()),
                "tool_calls": session.calls,
            }
        return {
            "answer": "查询步数过多，已停止。",
            "citations": list(session.citations.values()),
            "tool_calls": session.calls,
        }
    finally:
        session.close()


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    server_version = "ShuangxiuGou/0.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[server] %s\n" % (fmt % args))

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: object):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _client_ip(self) -> str:
        fwd = self.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
        return self.client_address[0]

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = (ROOT / "index.html").read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
        elif self.path == "/api/health":
            self._json(
                200,
                {
                    "ok": True,
                    "model": MODEL,
                    "api_url": API_URL,
                    "db": str(DB_PATH),
                    "db_exists": DB_PATH.exists(),
                    "has_key": bool(os.environ.get("DEEPSEEK_API_KEY")),
                    "vision": True,
                },
            )
        elif self.path == "/api/stats":
            if not DB_PATH.exists():
                self._json(500, {"error": f"数据库不存在：{DB_PATH}"})
                return
            con = connect()
            try:
                self._json(200, db_stats(con))
            finally:
                con.close()
        elif self.path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/ask":
            self._json(404, {"error": "not found"})
            return
        if not rate_ok(self._client_ip()):
            self._json(429, {"error": "请求过于频繁，请稍后再试"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY:
            self._json(413, {"error": "请求体过大，请压缩图片后再传"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "请求体不是合法 JSON"})
            return
        question = (payload.get("question") or "").strip()
        image = payload.get("image")
        if image is not None:
            if not isinstance(image, str) or not image.startswith("data:image/"):
                self._json(400, {"error": "image 必须是 data:image/... 的 base64 数据 URL"})
                return
            if len(image) > 8_000_000:
                self._json(413, {"error": "图片过大，请压缩后再传"})
                return
        if not question and not image:
            self._json(400, {"error": "请输入问题，或上传一张产品图片"})
            return
        raw_hist = payload.get("history")
        hist = [m for m in raw_hist if isinstance(m, dict)] if isinstance(raw_hist, list) else []
        print(f"[ask] ip={self._client_ip()} img={bool(image)} turns={len(hist)} q={question[:300]!r}", flush=True)
        if not DB_PATH.exists():
            self._json(500, {"error": f"数据库不存在：{DB_PATH}。请先跑 week-04/code/build_db.py"})
            return
        try:
            self._json(200, answer(question, image, hist))
        except RuntimeError as e:
            self._json(502, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            self._json(500, {"error": f"{type(e).__name__}: {e}"})


def selftest() -> int:
    print(f"DB: {DB_PATH}  exists={DB_PATH.exists()}")
    if not DB_PATH.exists():
        return 1
    con = connect()
    print("stats:", json.dumps(db_stats(con), ensure_ascii=False))
    for q in ("安克", "胖东来", "咖啡", "不存在的公司XYZ"):
        blocks = search_companies(con, q)
        print(f"search {q!r}: {len(blocks)} 家 -> {[b['company_id'] + b['name_zh'] for b in blocks]}")
    con.close()
    print("selftest ok")
    return 0


def cli_ask(question: str) -> int:
    print(f"Q: {question}", file=sys.stderr)
    try:
        print(json.dumps(answer(question), ensure_ascii=False, indent=2))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if "--ask" in sys.argv:
        i = sys.argv.index("--ask")
        q = sys.argv[i + 1] if len(sys.argv) > i + 1 else ""
        if not q:
            print("用法：python3 server.py --ask \"你的问题\"", file=sys.stderr)
            return 1
        return cli_ask(q)
    if not ensure_db():
        print(f"[warn] 数据库不存在且无法自动重建：{DB_PATH}", file=sys.stderr)
        print("[warn] 先跑：python3 week-04/code/build_db.py", file=sys.stderr)
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("[warn] 未设 DEEPSEEK_API_KEY，/api/ask 会返回错误提示。", file=sys.stderr)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"双休购 running at http://{HOST}:{PORT}  (model={MODEL}, rate={RATE_LIMIT_PER_MIN}/min)")
    if HOST in ("0.0.0.0", "::"):
        print(f"本机访问：http://127.0.0.1:{PORT}")
        print("局域网/公网：用本机公网 IP 或平台分配的域名访问")
    print("Ctrl+C 停止")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
