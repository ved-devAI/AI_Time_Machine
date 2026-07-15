"""Zero-dependency development server for the AI Time Machine vertical slice."""

from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app.analysis import AnalysisError, analyze_bug_origin
from app.ask_repo import QUESTIONS, ask_repo
from app.git_ingest import read_timeline


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
ORBITCART = ROOT / ".data" / "orbitcart"
ANALYSIS_CACHE = ROOT / ".data" / "orbitcart-analysis.json"
CODEX_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "bug-origin.codex.json"
ASK_REPO_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "ask-repo.codex.json"


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without adding a package dependency."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _request_json(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid request size.") from exc
        if length <= 0 or length > 4096:
            raise ValueError("Request body must be between 1 and 4096 bytes.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must be valid JSON.") from exc
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json({"status": "ok", "service": "ai-time-machine"})
            return
        if path == "/api/projects/orbitcart/timeline":
            if not ORBITCART.exists():
                self._json(
                    {"error": "OrbitCart has not been generated. Run scripts/create_orbitcart.py."},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
                return
            self._json(read_timeline(ORBITCART))
            return
        if path == "/api/projects/orbitcart/questions":
            self._json({"questions": QUESTIONS})
            return
        if path == "/":
            self._file(FRONTEND / "index.html")
            return
        requested = (FRONTEND / path.lstrip("/")).resolve()
        if FRONTEND.resolve() not in requested.parents:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        self._file(requested)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        if path == "/api/projects/orbitcart/investigations/bug-origin":
            if not ORBITCART.exists():
                self._json(
                    {"error": "OrbitCart has not been generated. Run scripts/create_orbitcart.py."},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
                return
            timeline = read_timeline(ORBITCART)
            self._json(analyze_bug_origin(timeline, ANALYSIS_CACHE, CODEX_ARTIFACT))
            return
        if path == "/api/projects/orbitcart/ask":
            if not ORBITCART.exists():
                self._json(
                    {"error": "OrbitCart has not been generated. Run scripts/create_orbitcart.py."},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
                return
            try:
                payload = self._request_json()
                question_id = payload.get("question_id")
                if not isinstance(question_id, str):
                    raise ValueError("question_id must be a string.")
                self._json(ask_repo(read_timeline(ORBITCART), question_id, ASK_REPO_ARTIFACT))
            except (ValueError, AnalysisError) as exc:
                self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._json({"error": "Unknown API endpoint."}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[ai-time-machine] {format % args}")


def main() -> None:
    load_local_env(ROOT / ".env")
    host, port = "127.0.0.1", 8765
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Time Machine running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AI Time Machine")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
