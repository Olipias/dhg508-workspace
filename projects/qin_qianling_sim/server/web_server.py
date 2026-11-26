#!/usr/bin/env python3
"""Serve the web build and proxy NPC calls to DeepSeek.

    export DEEPSEEK_API_KEY=sk-...
    python3 server/web_server.py
    open http://127.0.0.1:8788

Static files come from web/ (HTML/CSS/JS); /assets/* and /data/* are served
from the Godot project so the two builds stay in sync.  /npc is the same
endpoint the Godot build uses, with the same logging and guards.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WEB = ROOT / "web"
GAME = ROOT / "game"
sys.path.insert(0, str(HERE))

import npc_server  # noqa: E402


class Handler(SimpleHTTPRequestHandler):
    server_version = "QianlingWeb/1.0"

    def _send_json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def _file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "not found")
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = unquote(parsed.path)
        if route in ("/health", "/stats"):
            if route == "/health":
                self._send_json(200, {"ok": True, "model": npc_server.MODEL,
                                      "mock": npc_server.MOCK,
                                      "npcs": list(npc_server.NPCS.keys())})
            else:
                calls = tin = tout = 0
                cost = 0.0
                if npc_server.LOG.exists():
                    for line in npc_server.LOG.read_text(encoding="utf-8").splitlines():
                        try:
                            r = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        u = r.get("usage") or {}
                        if u.get("prompt_tokens", 0) or u.get("completion_tokens", 0):
                            calls += 1
                            tin += u.get("prompt_tokens", 0)
                            tout += u.get("completion_tokens", 0)
                            cost += r.get("cost_usd_est", 0.0)
                self._send_json(200, {"calls": calls, "tokens_in": tin,
                                      "tokens_out": tout, "cost_usd_est": round(cost, 6)})
            return
        if route == "/":
            route = "/index.html"
        if route.startswith("/assets/"):
            self._file(GAME / "assets" / route[len("/assets/"):])
        elif route.startswith("/data/"):
            self._file(GAME / "data" / route[len("/data/"):])
        else:
            self._file(WEB / route.lstrip("/"))

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/npc"):
            self.send_error(404, "not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            npc_id = str(req.get("npc_id", ""))
            text = str(req.get("text", ""))[:800]
            context = req.get("context", {})
            if npc_id not in npc_server.NPCS:
                self._send_json(400, {"error": f"unknown npc {npc_id}"})
                return
            parsed = npc_server.ask(npc_id, text, context)
            self._send_json(200, parsed)
        except Exception as exc:  # noqa: BLE001
            self._send_json(503, {"error": repr(exc)})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8788")))
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    if args.mock:
        npc_server.MOCK = True
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"web + npc on http://{args.host}:{args.port}  model={npc_server.MODEL}  mock={npc_server.MOCK}")
    server.serve_forever()


if __name__ == "__main__":
    main()
