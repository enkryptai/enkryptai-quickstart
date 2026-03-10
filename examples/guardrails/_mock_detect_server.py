"""Minimal mock for unified POST /detect (image/audio). Usage: python _mock_detect_server.py"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8765


class DetectHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") == "/detect":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(body)
                mode = data.get("mode", "")
                if mode == "image":
                    resp = {"summary": {"multimodal_guardrails": 0}, "details": {"response": "Mock: image accepted."}}
                elif mode == "audio":
                    resp = {"summary": {"multimodal_guardrails": 0}, "details": {"response": "Mock: audio accepted."}}
                else:
                    resp = {"summary": {}, "details": {"error": "mock only supports image/audio"}}
            except Exception:
                resp = {"summary": {}, "details": {"error": "invalid request"}}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("", PORT), DetectHandler)
    print(f"Mock detect at http://127.0.0.1:{PORT}/detect")
    server.serve_forever()
