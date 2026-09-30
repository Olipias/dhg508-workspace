import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _lib import MODEL, db_path  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        obj = {
            "ok": True,
            "model": MODEL,
            "db_exists": os.path.exists(db_path()),
            "has_key": bool(os.environ.get("DEEPSEEK_API_KEY")),
            "vision": True,
        }
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass
