import json
from http.server import BaseHTTPRequestHandler

from _lib import MAX_BODY, answer, rate_ok


def _json(h, code, obj):
    body = json.dumps(obj, ensure_ascii=False).encode()
    h.send_response(code)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


def _ip(h):
    fwd = h.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return h.client_address[0] if h.client_address else "?"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if not rate_ok(_ip(self)):
            _json(self, 429, {"error": "请求过于频繁，请稍后再试"})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > MAX_BODY:
            _json(self, 413, {"error": "请求体过大，请压缩图片后再传"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            _json(self, 400, {"error": "请求体不是合法 JSON"})
            return
        q = (payload.get("question") or "").strip()
        img = payload.get("image")
        if img is not None:
            if not isinstance(img, str) or not img.startswith("data:image/"):
                _json(self, 400, {"error": "image 必须是 data:image/... 的 base64 数据 URL"})
                return
            if len(img) > 8_000_000:
                _json(self, 413, {"error": "图片过大，请压缩后再传"})
                return
        if not q and not img:
            _json(self, 400, {"error": "请输入问题，或上传一张产品图片"})
            return
        try:
            _json(self, 200, answer(q, img))
        except RuntimeError as e:
            _json(self, 502, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            _json(self, 500, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, *a):
        pass
