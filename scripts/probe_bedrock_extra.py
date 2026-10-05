r"""Kiểm bổ sung: họ Amazon Nova + các model đòi API kiểu mới (không kèm `temperature`).

Vì sao cần script riêng:
  * Lần quét trước, bộ lọc của tôi vô tình bỏ hết `amazon.nova-*` -> thiếu cả họ Nova.
  * Một số model mới (opus-4-7/4-8/5, sonnet-5, fable-5) trả lỗi
    "`temperature` is deprecated" / "data retention mode 'default'".
    Đó KHÔNG phải lỗi quyền -> phải gọi KHÔNG kèm `temperature` mới biết có dùng được.

Cách gọi: dùng chính `BedrockClient` của dự án để nó nạp bearer token vào biến môi
trường (botocore tự dùng), rồi gọi thẳng client boto3 bên trong với `inferenceConfig`
do mình kiểm soát.

Chạy: python scripts\probe_bedrock_extra.py
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


def probe(mid: str, with_temp: bool = False, max_tokens: int = 8) -> tuple[str, str]:
    """Trả về (nhãn, ghi chú)."""
    try:
        c = BedrockClient(model=mid, region=REGION, temperature=0.0, max_tokens=max_tokens)
        cfg: dict = {"maxTokens": max_tokens}
        if with_temp:
            cfg["temperature"] = 0.0
        r = c._client.converse(              # client boto3 bên trong, đã có bearer token
            modelId=mid,
            messages=[{"role": "user", "content": [{"text": "Reply with the single word OK."}]}],
            inferenceConfig=cfg,
        )
        c.close()
        txt = r["output"]["message"]["content"][0]["text"]
        return "OK", txt.strip().replace("\n", " ")[:20]
    except Exception as e:
        m = str(e)
        for tag in ("ResourceNotFoundException", "ValidationException", "AccessDeniedException",
                    "ThrottlingException"):
            if tag in m:
                detail = m.split("operation: ")[-1].splitlines()[0]
                return tag.replace("Exception", ""), detail[:80]
        return "ERROR", m.splitlines()[0][:80]


NOVA = ["amazon.nova-pro-v1:0", "amazon.nova-lite-v1:0", "amazon.nova-micro-v1:0",
        "amazon.nova-2-lite-v1:0", "us.amazon.nova-pro-v1:0", "us.amazon.nova-lite-v1:0",
        "us.amazon.nova-micro-v1:0", "us.amazon.nova-2-lite-v1:0", "us.amazon.nova-premier-v1:0"]

NEW_API = ["us.anthropic.claude-opus-4-7", "us.anthropic.claude-opus-4-8",
           "us.anthropic.claude-opus-5", "us.anthropic.claude-sonnet-5",
           "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-fable-5",
           "us.anthropic.claude-fable-5-1"]

print("=== A. Họ Amazon Nova ===")
for mid in NOVA:
    label, note = probe(mid, with_temp=False)
    print(f"  {label:16} {mid:38} {note}")

print()
print("=== B. Model mới, gọi KHÔNG kèm temperature ===")
for mid in NEW_API:
    label, note = probe(mid, with_temp=False)
    print(f"  {label:16} {mid:38} {note}")
