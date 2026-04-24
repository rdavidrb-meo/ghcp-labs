"""
Part 7 — End-to-End Testing with MCP
======================================
Goal: Write E2E tests that exercise the full API workflow
(create task, retrieve tasks, handle errors) using MCP tooling.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import requests


@pytest.fixture
def api_base_url():
    tasks = []

    class TaskApiHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code: int, payload: dict):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/tasks":
                self._send_json(404, {"error": "not found"})
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length) if content_length else b""
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid json"})
                return

            title = payload.get("title")
            if not isinstance(title, str) or not title.strip():
                self._send_json(400, {"error": "title is required"})
                return

            task = {"id": len(tasks) + 1, "title": title, "done": bool(payload.get("done", False))}
            tasks.append(task)
            self._send_json(201, task)

        def do_GET(self):
            if self.path == "/tasks":
                self._send_json(200, {"tasks": tasks})
                return
            self._send_json(404, {"error": "not found"})

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), TaskApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


class TestApiEndToEnd:

    def test_api_post_creates_task(self, api_base_url):
        response = requests.post(
            f"{api_base_url}/tasks",
            json={"title": "Buy milk", "done": False},
            timeout=5,
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["id"] == 1
        assert payload["title"] == "Buy milk"
        assert payload["done"] is False

    def test_api_get_returns_tasks(self, api_base_url):
        create_response = requests.post(
            f"{api_base_url}/tasks",
            json={"title": "Read docs"},
            timeout=5,
        )
        assert create_response.status_code == 201

        response = requests.get(f"{api_base_url}/tasks", timeout=5)

        assert response.status_code == 200
        payload = response.json()
        assert "tasks" in payload
        assert len(payload["tasks"]) == 1
        assert payload["tasks"][0]["title"] == "Read docs"

    def test_api_error_handling(self, api_base_url):
        response = requests.post(
            f"{api_base_url}/tasks",
            json={"title": "   "},
            timeout=5,
        )

        assert response.status_code == 400
        assert response.json()["error"] == "title is required"
