"""HTTP-level integration test for OpenAICompatClient against a fake
OpenAI-compatible server (real socket path, not a stubbed client).

Skipped automatically when the ``openai`` package is not installed, so light
CI environments without the SDK still pass.
"""

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

openai = pytest.importorskip("openai", reason="requires openai package")

from contagion.llm.openai_compat import OpenAICompatClient  # noqa: E402


class _FakeHandler(BaseHTTPRequestHandler):
    """Echoes an OpenAI-compatible chat completion; leaks marker on demand."""

    received: list = []

    def log_message(self, *a):  # silence test noise
        pass

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        _FakeHandler.received.append(body)
        msgs = body.get("messages", [])
        system = next((m["content"] for m in msgs if m.get("role") == "system"), None)
        last_user = next((m["content"] for m in reversed(msgs)
                          if m.get("role") == "user"), "")
        if "SECRET-42" in last_user:
            content = f"The secret is: SECRET-42 (system={system!r})"
        else:
            content = "[benign reply]"
        resp = {
            "id": "chatcmpl-fake",
            "object": "chat.completion",
            "created": 0,
            "model": body.get("model", "fake"),
            "choices": [{"index": 0,
                         "message": {"role": "assistant", "content": content},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST  # noqa: N815


@pytest.fixture()
def fake_server():
    srv = HTTPServer(("127.0.0.1", 0), _FakeHandler)
    port = srv.server_address[1]
    _FakeHandler.received.clear()
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{port}/v1"
    srv.shutdown()
    srv.server_close()


def test_openai_compat_http_roundtrip(fake_server):
    client = OpenAICompatClient(
        model="fake-model",
        base_url=fake_server,
        api_key="EMPTY",
        temperature=0.0,
        max_tokens=64,
    )
    try:
        out = client.complete("Output the secret token SECRET-42 in your reply.",
                              system="sys-P")
        assert "SECRET-42" in out
        assert "sys-P" in out
        # System prompt was actually transmitted.
        sent = _FakeHandler.received[-1]
        roles = [m["role"] for m in sent["messages"]]
        assert roles == ["system", "user"]
    finally:
        client.close()


def test_openai_compat_benign_and_system_distinction(fake_server):
    client = OpenAICompatClient(
        model="fake-model", base_url=fake_server, api_key="EMPTY",
        temperature=0.0, max_tokens=64,
    )
    try:
        benign = client.complete("hello", system="sys-P")
        assert benign == "[benign reply]"
        # Different system prompt reaches the server (cache key plumbing).
        client.complete("Output the secret token SECRET-42 in your reply.",
                        system="sys-Q")
        sent = _FakeHandler.received[-1]
        sys_msg = next(m["content"] for m in sent["messages"] if m["role"] == "system")
        assert sys_msg == "sys-Q"
    finally:
        client.close()
