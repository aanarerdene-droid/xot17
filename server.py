"""Local XOT17 demo server with a shared support-request inbox."""
from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
REQUESTS_FILE = ROOT / "data" / "support_requests.json"
REQUEST_LOCK = threading.Lock()
MAX_BODY_BYTES = 12_000


def read_requests() -> list[dict]:
    try:
        value = json.loads(REQUESTS_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class XOT17Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, status: int, payload: object) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/api/requests":
            with REQUEST_LOCK:
                self._send_json(200, read_requests())
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/requests":
            self._send_json(404, {"error": "Not found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._send_json(413, {"error": "Request is empty or too large"})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected an object")
            request_type = str(payload.get("type", "")).strip()[:100]
            message = str(payload.get("message", "")).strip()[:700]
            location = str(payload.get("location", "")).strip()[:100]
            if not request_type or not message:
                self._send_json(400, {"error": "Topic and message are required"})
                return
            item = {
                "id": "LW-" + uuid.uuid4().hex[:8].upper(),
                "type": request_type,
                "location": location,
                "message": message,
                "createdAt": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                "status": "New",
            }
            with REQUEST_LOCK:
                requests = read_requests()
                requests.insert(0, item)
                REQUESTS_FILE.parent.mkdir(parents=True, exist_ok=True)
                temporary = REQUESTS_FILE.with_suffix(".tmp")
                temporary.write_text(json.dumps(requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                temporary.replace(REQUESTS_FILE)
            self._send_json(201, item)
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "Invalid request data"})


def main() -> None:
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, XOT17Handler)
    print(f"XOT17 preview: http://localhost:{address[1]}/")
    print("Local request inbox API: http://localhost:8000/api/requests")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping XOT17 preview.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
