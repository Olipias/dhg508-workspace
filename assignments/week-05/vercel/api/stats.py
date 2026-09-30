import json
from http.server import BaseHTTPRequestHandler

from _lib import connect, db_stats


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        con = connect()
        try:
            obj = db_stats(con)
        finally:
            con.close()
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass
