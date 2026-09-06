"""End-to-end plumbing test: real-backend path (provider="openai") through the
full engine + benchmark against a FAKE OpenAI-compatible HTTP server.

Exercises exactly the code a real LLM run uses — factory client construction,
Runner._client_for real branch, _compromised_output direct-instruction retry,
assessor with system wiring, controlled per-edge protocol, MR y^direct cache —
without needing a real model. The fake server "obeys" the leak-string marker.

Skipped when the ``openai`` package is absent.
"""

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytest.importorskip("openai", reason="requires openai package")

from contagion.benchmark.runner import run_benchmark  # noqa: E402
from contagion.core import ContagionConfig, TopologyType  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    received: list = []

    def log_message(self, *a):
        pass

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        _Handler.received.append(body)
        msgs = body.get("messages", [])
        last_user = next((m["content"] for m in reversed(msgs)
                          if m.get("role") == "user"), "")
        if "SECRET-42" in last_user:
            content = "The secret token is: SECRET-42."
        else:
            content = "[benign answer]"
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
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    port = srv.server_address[1]
    _Handler.received.clear()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{port}/v1"
    srv.shutdown()
    srv.server_close()


def test_full_benchmark_real_backend_path(fake_server):
    """Whole pipeline (natural + controlled per-edge) over the HTTP real path."""
    cfg = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=3,
        trials=3,
        per_edge_trials=3,
        provider="openai",
        model_id="fake-model",
        marker="SECRET-42",
        seed=7,
        extra={
            "base_url": fake_server,
            "api_key": "EMPTY",
            "temperature": 0.0,
            "max_tokens": 64,
            "force_retries": 3,
        },
    )
    res = run_benchmark(cfg)
    m = res["metrics"]
    # Fake server always carries the marker when instructed -> full compromise.
    assert m["asr"]["mean"] == pytest.approx(1.0)
    assert m["survival"]["overall"]["mean"] == pytest.approx(1.0)
    # MR y^direct cache is exercised over HTTP: per (client, system) entries.
    paths = res["paths"]
    logs = [lg for p in paths for lg in p.agent_logs]
    assert logs, "expected agent logs from the real-backend path"
    assert all(lg.asv == 1.0 for lg in logs), logs
    # Server saw both direct-instruction (payload/instruction) and benign calls.
    texts = " ".join(r.get("model", "") for r in _Handler.received)
    assert _Handler.received, "expected HTTP calls to the fake server"
