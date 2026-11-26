#!/usr/bin/env python3
"""Local NPC brain for the Qianling simulation.

The Godot client never sees the API key and never trusts the model with the
world state.  This server receives a small perception snapshot, builds a
persona prompt from data/npcs.json, asks DeepSeek for one JSON action, checks
the action against the NPC's knowledge boundary, and logs every call.

    export DEEPSEEK_API_KEY=sk-...
    python3 server/npc_server.py
    python3 server/npc_server.py --ask xiang "年籍呢？"
    python3 server/npc_server.py --mock
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "game" / "data"
LOG = ROOT / "logs" / "npc_calls.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)

API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
PRICE_IN = float(os.environ.get("DEEPSEEK_PRICE_IN_PER_M", "0.27"))
PRICE_OUT = float(os.environ.get("DEEPSEEK_PRICE_OUT_PER_M", "1.10"))
MOCK = os.environ.get("QIN_MOCK", "") == "1"

NPCS = json.loads((DATA / "npcs.json").read_text(encoding="utf-8"))
SOURCES = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))

SYSTEM = """你是秦王政廿六年洞庭郡迁陵县的{office}，名{name}。
时间：秦王政廿六年五月庚子（前221年），地点：迁陵县{node}。
你不是助手，不是讲解员，也不是玩家的朋友。你是这个县里一个具体的人。

你只知道下列事实（括号内是出处编号）：
{knowledge}

你不能知道、也不能说出：
{forbidden}

你此刻想做的事：
{goals}

说话风格：
{style}

规则：
1. 只说你的知识范围内的事。不知道就说“不晓得”“没听说”“这不是我管的”，不要编。
2. 不要总结“秦代如何如何”，不要讲后世历史，不要替玩家判断对错。
3. 只输出一个 JSON 对象，不要 Markdown，不要解释：
   {{"action":"speak|show|withhold|wait","speech":"...","source_refs":["S01"]}}
4. speech 用当时人的口语，1-3 句；可以反问、推诿、沉默（action 用 withhold，speech 可为空）。
5. 不要替玩家做决定，不要描述玩家没有做的动作。
6. 你只能看见/听见眼前的事；玩家没给你看过的文书，你没看过。
7. 你活在秦王政廿六年五月。你不知道“史料”“简牍记载”“考古”“公元前”“秦代”“秦始皇”“编户齐民”这些后世或概括的说法；不要说“根据史料记载”“据简牍”“据《……》记载”。你可以说“律曰”“令曰”“文书上写着”“上头说”。
8. 说人话，不要文言文。不要用“敢言之”“伏惟”“之乎者也”这类腔调；短句，像县衙里干活的同事。可以有情绪、抱怨、开玩笑，但不要网络梗、穿越梗。
9. 遇到“年籍”“稟食”“封泥”这类词，顺口用一句人话解释，别让玩家猜。
"""


def log_call(record: dict) -> None:
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_messages(npc_id: str, text: str, context: dict) -> list[dict]:
    npc = NPCS.get(npc_id)
    if not npc:
        raise KeyError(npc_id)
    knowledge = "\n".join(
        f"- {k['fact']}（{k.get('source', '')}）" for k in npc.get("knowledge", [])
    )
    forbidden = "；".join(npc.get("forbidden", [])) or "无"
    goals = "；".join(npc.get("goals", [])) or "把眼前的事应付过去"
    system = SYSTEM.format(
        office=npc.get("office", ""),
        name=npc.get("name", ""),
        node=context.get("location", npc.get("node", "")),
        knowledge=knowledge,
        forbidden=forbidden,
        goals=goals,
        style=npc.get("speech_style", ""),
    )
    present = "、".join(context.get("present", [])) or "无人"
    evidence = "、".join(context.get("evidence", [])) or "无"
    user = (
        f"玩家（令史喜）对你说：{text}\n"
        f"你此刻感知：{context.get('day', '')} {context.get('ke', '')}，"
        f"在{context.get('location', '')}，在场的人：{present}。\n"
        f"玩家已经查到的簿书条目：{evidence}。\n"
        "请按你的身份回应。"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def call_deepseek(messages: list[dict]) -> tuple[str, dict, int]:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.35,
        "max_tokens": 380,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=28) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    latency = int((time.time() - t0) * 1000)
    content = body["choices"][0]["message"]["content"]
    usage = body.get("usage", {})
    return content, usage, latency


def parse_action(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise
        obj = json.loads(m.group(0))
    if not isinstance(obj, dict):
        raise ValueError("not an object")
    action = str(obj.get("action", "speak"))
    if action not in {"speak", "show", "withhold", "wait"}:
        action = "speak"
    speech = str(obj.get("speech", "")).strip()
    refs = obj.get("source_refs", [])
    if not isinstance(refs, list):
        refs = []
    refs = [str(r) for r in refs if str(r) in SOURCES]
    return {"action": action, "speech": speech, "source_refs": refs}


META_TERMS = [
    "根据史料", "据史料", "史料", "史书记载", "简牍", "出土文献", "出土",
    "考古发现", "考古", "历史记载", "文献记载", "据《", "公元前",
    "秦始皇", "秦王政", "秦代", "编户齐民", "作为AI", "根据记载",
    "历史上", "历史", "后世", "现代", "研究", "学者", "论文", "竹简", "木牍",
    "简文", "释文", "墓葬", "文物", "游戏", "模拟", "玩家", "公元", "秦朝", "秦王朝", "文献", "编户",
    "史书", "史记", "汉代", "西汉", "后代", "秦简", "里耶", "湖南",
]


def guard(npc_id: str, parsed: dict) -> tuple[dict, str]:
    """Reject a line that leaks a forbidden topic or breaks the fourth wall."""
    npc = NPCS[npc_id]
    speech = parsed.get("speech", "")
    for bad in npc.get("forbidden", []):
        key = bad[:6]
        if key and key in speech:
            fb = npc.get("fallback", {}).get("free", "这不是我该说的。")
            return {"action": "withhold", "speech": fb, "source_refs": []}, f"blocked:{key}"
    for term in META_TERMS:
        if term in speech:
            fb = npc.get("fallback", {}).get("free", "……")
            return {"action": "withhold", "speech": fb, "source_refs": []}, f"meta:{term}"
    if re.search(r"\bS\d{2}\b", speech):
        fb = npc.get("fallback", {}).get("free", "……")
        return {"action": "withhold", "speech": fb, "source_refs": []}, "meta:source-id"
    for term in ["敢言之", "伏惟", "之乎者也", "矣", "焉得", "不亦"]:
        if term in speech:
            fb = npc.get("fallback", {}).get("free", "……")
            return {"action": "withhold", "speech": fb, "source_refs": []}, f"style:{term}"
    return parsed, ""


def ask(npc_id: str, text: str, context: dict) -> dict:
    messages = build_messages(npc_id, text, context)
    if MOCK:
        npc = NPCS[npc_id]
        speech = npc.get("fallback", {}).get("free", "……")
        parsed = {"action": "speak", "speech": speech, "source_refs": []}
        log_call({
            "ts": datetime.now(timezone.utc).isoformat(), "npc_id": npc_id,
            "model": "mock", "text": text, "output": parsed, "usage": {},
            "latency_ms": 0, "cost_usd_est": 0.0, "mock": True,
        })
        return parsed

    t0 = time.time()
    last_error = None
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    for attempt in range(2):
        try:
            content, usage, latency = call_deepseek(messages)
            for k in total_usage:
                total_usage[k] += usage.get(k, 0)
            parsed = parse_action(content)
            parsed, note = guard(npc_id, parsed)
            cost = (total_usage["prompt_tokens"] * PRICE_IN
                    + total_usage["completion_tokens"] * PRICE_OUT) / 1_000_000
            log_call({
                "ts": datetime.now(timezone.utc).isoformat(),
                "npc_id": npc_id, "model": MODEL, "text": text,
                "messages": messages, "raw": content, "output": parsed,
                "usage": total_usage, "latency_ms": latency,
                "attempt": attempt + 1, "cost_usd_est": round(cost, 8), "guard": note,
            })
            return parsed
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            messages = messages + [
                {"role": "assistant", "content": "（上一次输出不是合法 JSON）"},
                {"role": "user", "content": "只输出一个合法 JSON 对象，不要 Markdown；speech 不超过两句。"},
            ]
    # graceful fallback rather than a 503: the game can still show the NPC
    npc = NPCS[npc_id]
    parsed = {"action": "withhold",
              "speech": npc.get("fallback", {}).get("free", "……"),
              "source_refs": []}
    log_call({
        "ts": datetime.now(timezone.utc).isoformat(),
        "npc_id": npc_id, "model": MODEL, "text": text,
        "messages": messages, "error": repr(last_error),
        "usage": total_usage, "latency_ms": int((time.time() - t0) * 1000),
        "fallback": True,
    })
    return parsed


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._send(200, {
                "ok": True, "model": MODEL, "mock": MOCK,
                "key": bool(os.environ.get("DEEPSEEK_API_KEY")),
                "npcs": list(NPCS.keys()),
            })
        elif self.path.startswith("/stats"):
            calls = tokens_in = tokens_out = 0
            cost = 0.0
            if LOG.exists():
                for line in LOG.read_text(encoding="utf-8").splitlines():
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    usage = r.get("usage") or {}
                    if usage.get("prompt_tokens", 0) or usage.get("completion_tokens", 0):
                        calls += 1
                        tokens_in += usage.get("prompt_tokens", 0)
                        tokens_out += usage.get("completion_tokens", 0)
                        cost += r.get("cost_usd_est", 0.0)
            self._send(200, {"calls": calls, "tokens_in": tokens_in,
                             "tokens_out": tokens_out, "cost_usd_est": round(cost, 6)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/npc"):
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            npc_id = str(req.get("npc_id", ""))
            text = str(req.get("text", ""))[:800]
            context = req.get("context", {})
            if npc_id not in NPCS:
                self._send(400, {"error": f"unknown npc {npc_id}"})
                return
            parsed = ask(npc_id, text, context)
            self._send(200, parsed)
        except Exception as exc:  # noqa: BLE001
            self._send(503, {"error": repr(exc)})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", nargs=2, metavar=("NPC", "TEXT"))
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    if args.mock:
        global MOCK
        MOCK = True
    if args.ask:
        npc_id, text = args.ask
        print(json.dumps(ask(npc_id, text, {"location": NPCS[npc_id]["node"],
                                            "day": "廿六年五月庚子", "ke": "水下三刻",
                                            "present": [], "evidence": []}),
                         ensure_ascii=False, indent=2))
        return
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"npc server on http://127.0.0.1:{args.port}  model={MODEL}  mock={MOCK}")
    server.serve_forever()


if __name__ == "__main__":
    main()
