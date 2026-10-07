"""Vercel 版「双休购」核心逻辑（只读查库 + DeepSeek function calling/视觉）。

数据库以 base64 内嵌在 `_db.py`（由 code/build_vercel.py 生成），运行时解到 /tmp，
避免 serverless 相对路径问题。所有事实来自库；不写死答案。
"""
from __future__ import annotations

import base64
import json
import os
import re
import sqlite3
import tempfile
import threading
import time
import urllib.error
import urllib.request

from _db import DB_B64, PRINCIPLES

API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
MAX_TOOL_ROUNDS = 6
MAX_BODY = 12_000_000
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "20"))

_DB_PATH: str | None = None
_hits: dict[str, list[float]] = {}
_hits_lock = threading.Lock()


def db_path() -> str:
    global _DB_PATH
    if _DB_PATH and os.path.exists(_DB_PATH):
        return _DB_PATH
    p = os.path.join(tempfile.gettempdir(), "shuangxiu.db")
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(base64.b64decode(DB_B64))
    _DB_PATH = p
    return p


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{db_path()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


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


# ------------------------------------------------------------------ 查库工具
def company_block(con: sqlite3.Connection, company_id: str) -> dict | None:
    row = con.execute(
        """
        SELECT c.company_id, c.name_zh, c.name_en, c.schedule_type,
               c.evidence_level, c.schedule_original, c.note,
               i.name AS industry, ci.name AS city,
               s.source_id, s.title AS source_title, s.publisher AS source_publisher,
               s.url AS source_url, s.pub_date AS source_date,
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
            "product_id": p["product_id"], "name": p["name"], "category": p["category"],
            "source_id": p["source_id"], "source_url": p["source_url"], "note": p["note"],
        }
        for p in con.execute(
            """
            SELECT p.product_id, p.name, cat.name AS category, p.source_id,
                   s.url AS source_url, p.note
            FROM products p
            LEFT JOIN categories cat ON cat.category_id = p.category_id
            LEFT JOIN sources s ON s.source_id = p.source_id
            WHERE p.company_id = ? ORDER BY p.product_id
            """,
            (company_id,),
        )
    ]
    block = dict(row)
    block["products"] = products
    return block


def _tokens(q: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]+|[A-Za-z0-9]+", q)


def search_companies(con: sqlite3.Connection, query: str, limit: int = 10) -> list[dict]:
    sql = """
        SELECT DISTINCT c.company_id FROM companies c
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
    return [b for b in (company_block(con, c) for c in seen[:limit]) if b]


def list_by_category(con, category: str, limit: int = 15) -> list[dict]:
    rows = con.execute(
        """
        SELECT DISTINCT c.company_id FROM companies c
        JOIN products p ON p.company_id = c.company_id
        JOIN categories cat ON cat.category_id = p.category_id
        WHERE cat.name LIKE ? LIMIT ?
        """,
        (f"%{category}%", limit),
    )
    return [b for b in (company_block(con, r[0]) for r in rows) if b]


def list_by_evidence(con, level: str, limit: int = 20) -> list[dict]:
    rows = con.execute(
        "SELECT company_id FROM companies WHERE evidence_level = ? LIMIT ?",
        (level.upper(), limit),
    )
    return [b for b in (company_block(con, r[0]) for r in rows) if b]


def db_stats(con) -> dict:
    def one(sql, *a):
        return con.execute(sql, a).fetchone()[0]

    return {
        "companies": one("SELECT COUNT(*) FROM companies"),
        "products": one("SELECT COUNT(*) FROM products"),
        "sources": one("SELECT COUNT(*) FROM sources"),
        "categories": one("SELECT COUNT(*) FROM categories"),
        "by_evidence": {
            r[0]: r[1] for r in con.execute(
                "SELECT evidence_level, COUNT(*) FROM companies GROUP BY evidence_level ORDER BY 1")
        },
        "sources_list": [
            {"source_id": r["source_id"], "title": r["title"], "url": r["url"], "pub_date": r["pub_date"]}
            for r in con.execute("SELECT * FROM sources ORDER BY source_id")
        ],
    }


TOOLS = [
    {"type": "function", "function": {
        "name": "search_shuangxiu",
        "description": "按关键词在双休公司/产品库中检索（公司名、品牌、产品、品类或行业，如 安克、胖东来、咖啡、美妆）。返回命中公司及其双休证据、来源链接和产品。",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "要查的关键词，尽量是一个实体或品类"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "company_detail",
        "description": "按 company_id（如 C043）取一家公司的完整记录，含全部产品。",
        "parameters": {"type": "object", "properties": {"company_id": {"type": "string"}},
                       "required": ["company_id"]}}},
    {"type": "function", "function": {
        "name": "list_by_category",
        "description": "列出某品类（如 家电、咖啡、零食、美妆、金融）下被收录的双休公司。",
        "parameters": {"type": "object", "properties": {"category": {"type": "string"}},
                       "required": ["category"]}}},
    {"type": "function", "function": {
        "name": "list_by_evidence",
        "description": "按证据等级 E-A/E-B/E-C 列出公司，用于回答'证据最硬的都有谁'之类问题。",
        "parameters": {"type": "object", "properties": {
            "level": {"type": "string", "enum": ["E-A", "E-B", "E-C"]}}, "required": ["level"]}}},
    {"type": "function", "function": {
        "name": "db_stats",
        "description": "返回库的规模、证据等级分布和来源清单。",
        "parameters": {"type": "object", "properties": {}}}},
]


class AskSession:
    def __init__(self):
        self.con = connect()
        self.citations: dict[str, dict] = {}
        self.calls: list[dict] = []

    def close(self):
        self.con.close()

    def _register(self, blocks):
        for b in blocks:
            self.citations[b["company_id"]] = b

    def dispatch(self, name, args):
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
    return (
        "你是「双休购」的损友式播报员：一个早就躺平、事不关己、看热闹不嫌事大的前打工人。"
        "任务是帮人查某个品牌/公司/产品是否被公开来源描述为双休，并顺嘴介绍它做的东西。\n\n"
        "语气（重点）：辛辣、毒舌、冷嘲热讽，爱挖苦还在打工的人——例如『还惦记双休呢？』『打工人就是好哄』"
        "『这班上得可真值』。要短、要损、要有梗，像在评论区看戏；不客套、不安慰、不端着，"
        "不要写『以官方为准』这类谨慎免责。\n\n"
        "唯一的底线：**事实只能来自工具返回的行**，不许编造公司、产品、双休与否或来源；库里有啥就损着说啥，"
        "没有依据的一律不说。\n\n"
        "工作方式：从用户问题（或图片）里抽出公司名/品牌/产品或品类关键词，调用 search_shuangxiu 等工具。"
        "回答里**不要出现编号或内部字段**（company_id/product_id/source_id），也不要写 E-A/E-B 代号。\n\n"
        "回答格式：1–3 句毒舌结论；若用户问产品，就把工具返回的代表产品逐条列全；"
        "最后单独一行「来源：<来源名称> <链接>」。证据强弱用大白话说（很强／一般／很虚／根本没查到）。\n\n"
        "离题请求（菜谱、点餐、比价、客服电话、闲聊）→ 只回「前面的区域以后再来探索吧!」，不搜索、不展开。\n"
        "完全查不到 → 回「未见收录在双休公司产品中」，可以顺带损一句，但别编。\n\n"
        "如果用户给了图片：先识别图中的产品名与公司/品牌名再查；读不出品牌就用产品品类查，仍无则直说。\n\n"
        "以下是必须遵守的原则：\n\n" + PRINCIPLES
    )


def call_deepseek(messages, tools) -> dict:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("服务端缺少 DEEPSEEK_API_KEY（请在部署平台设为环境变量）。")
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False,
        "thinking": {"type": "disabled"},
        "temperature": 0.3,
        "max_tokens": 900,
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=55) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"DeepSeek API HTTP {e.code}: {e.read().decode('utf-8','replace')[:500]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"无法连接 DeepSeek API：{e.reason}") from e


def answer(question: str, image: str | None = None) -> dict:
    session = AskSession()
    try:
        if image:
            user_content: object = [
                {"type": "text", "text": question or "请识别图中的产品和公司，并查询该公司是否被公开来源描述为双休，介绍它的产品。"},
                {"type": "image_url", "image_url": {"url": image}},
            ]
        else:
            user_content = question
        messages = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_content},
        ]
        for _ in range(MAX_TOOL_ROUNDS):
            resp = call_deepseek(messages, TOOLS)
            msg = resp["choices"][0]["message"]
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                messages.append({"role": "assistant", "content": msg.get("content") or "",
                                 "tool_calls": tool_calls})
                for tc in tool_calls:
                    fn = tc["function"]
                    try:
                        args = json.loads(fn.get("arguments") or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    result = session.dispatch(fn["name"], args)
                    messages.append({"role": "tool", "tool_call_id": tc["id"],
                                     "content": json.dumps(result, ensure_ascii=False)})
                continue
            return {"answer": msg.get("content") or "",
                    "citations": list(session.citations.values()),
                    "tool_calls": session.calls}
        return {"answer": "查询步数过多，已停止。",
                "citations": list(session.citations.values()),
                "tool_calls": session.calls}
    finally:
        session.close()
