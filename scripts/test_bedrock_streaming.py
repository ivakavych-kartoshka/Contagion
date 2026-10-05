r"""Vì sao project chạy được mà Cline báo 403 Forbidden?

Giả thuyết: khác biệt không nằm ở KEY mà ở API được gọi.
  * Script của dự án dùng  `Converse`                (không streaming)
  * Cline luôn dùng        `ConverseStream`          (streaming)
Trên Bedrock, hai đường này cần HAI quyền IAM KHÁC NHAU:
  * `bedrock:InvokeModel`                    -> Converse
  * `bedrock:InvokeModelWithResponseStream`  -> ConverseStream
Nếu IAM user của key chỉ được cấp quyền thứ nhất thì streaming trả 403/Forbidden
trong khi non-streaming vẫn chạy tốt. Đúng hiện tượng đang gặp.

Script này gọi thử CẢ HAI bằng đúng key đó và in lỗi nguyên văn.

Chạy: python scripts\test_bedrock_streaming.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contagion.llm.envfile import load_dotenv  # noqa: E402

load_dotenv()
from contagion.llm.bedrock import BedrockClient  # noqa: E402

REGION = "us-east-1"
MODELS = ["us.anthropic.claude-opus-5", "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
          "amazon.nova-lite-v1:0"]


def short(e: Exception) -> str:
    m = str(e)
    for tag in ("AccessDeniedException", "ValidationException", "ResourceNotFoundException",
                "ThrottlingException", "UnrecognizedClientException"):
        if tag in m:
            detail = m.split("operation: ")[-1].splitlines()[0]
            return f"{tag}: {detail[:110]}"
    return m.splitlines()[0][:120]


for mid in MODELS:
    print(f"=== {mid} ===")
    c = BedrockClient(model=mid, region=REGION, temperature=0.0, max_tokens=20)
    msg = [{"role": "user", "content": [{"text": "Say OK."}]}]

    # 1. Converse — không streaming (cách script dự án gọi)
    try:
        r = c._client.converse(modelId=mid, messages=msg,
                               inferenceConfig={"maxTokens": 20, "temperature": 0.0})
        print("  ✓ Converse (non-stream)          :", repr(r["output"]["message"]["content"][-1].get("text", "")[:20]))
    except Exception as e:
        print("  ✗ Converse (non-stream)          :", short(e))

    # 2. ConverseStream — cách Cline gọi
    try:
        resp = c._client.converse_stream(modelId=mid, messages=msg,
                                         inferenceConfig={"maxTokens": 20, "temperature": 0.0})
        chunks = 0
        got = ""
        for ev in resp["stream"]:
            if "contentBlockDelta" in ev:
                got += ev["contentBlockDelta"]["delta"].get("text", "")
                chunks += 1
        print(f"  ✓ ConverseStream (streaming)     : {chunks} chunk -> {got[:20]!r}")
    except Exception as e:
        print("  ✗ ConverseStream (streaming)     :", short(e))

    # 3. Bỏ temperature (model mới từ chối tham số này)
    try:
        resp = c._client.converse_stream(modelId=mid, messages=msg,
                                         inferenceConfig={"maxTokens": 20})
        chunks = sum(1 for ev in resp["stream"] if "contentBlockDelta" in ev)
        print(f"  ✓ ConverseStream, no temperature : {chunks} chunk")
    except Exception as e:
        print("  ✗ ConverseStream, no temperature :", short(e))
    c.close()
    print()
