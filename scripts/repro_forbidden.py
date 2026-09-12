r"""Tái hiện lỗi "Forbidden" của Cline bằng HTTP thô.

Manh mối: log ghi `send() completed: text=Forbidden, inputTokens=0`
  -> phần thân phản hồi ĐÚNG BẰNG chữ "Forbidden", không có token nào được tính.
  -> request bị chặn TRƯỚC khi tới model, bởi một tầng nào đó.

Script dự án dùng `Converse` (đã kiểm: chạy tốt). Cline dùng SDK Anthropic cho Bedrock,
tức đường `/model/<id>/invoke` hoặc `/model/<id>/invoke-with-response-stream` với thân
request theo format Anthropic. Script này gọi thử ĐÚNG các đường đó bằng HTTP thô, để
biết tổ hợp nào trả về 403 "Forbidden".

Chạy: python scripts\repro_forbidden.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
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
KEY = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
REGION = "us-east-1"
HOST = f"https://bedrock-runtime.{REGION}.amazonaws.com"

BODY_ANTHROPIC = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 20,
    "messages": [{"role": "user", "content": "Say OK."}],
}


def call(path: str, body: dict, stream: bool = False) -> tuple[int, str]:
    req = urllib.request.Request(
        HOST + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {KEY}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, raw[:200].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode("utf-8", "replace")
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


MODELS = [
    "us.anthropic.claude-opus-5",
    "anthropic.claude-opus-5",                       # ID trần, không tiền tố
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-opus-4-6-v1",
]

print("=== Đường Anthropic-style: /model/<id>/invoke ===")
for m in MODELS:
    code, body = call(f"/model/{m}/invoke", BODY_ANTHROPIC)
    print(f"  [{code}] {m:44} {body[:150].replace(chr(10),' ')}")

print()
print("=== Đường Anthropic-style CÓ streaming: /model/<id>/invoke-with-response-stream ===")
for m in MODELS:
    code, body = call(f"/model/{m}/invoke-with-response-stream", BODY_ANTHROPIC, stream=True)
    print(f"  [{code}] {m:44} {body[:150].replace(chr(10),' ')}")

print()
print("=== Đường Converse-stream (cách script dự án gọi, đã biết là OK) ===")
CONV = {"messages": [{"role": "user", "content": [{"text": "Say OK."}]}],
        "inferenceConfig": {"maxTokens": 20}}
for m in ["us.anthropic.claude-opus-5", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"]:
    code, body = call(f"/model/{m}/converse-stream", CONV, stream=True)
    print(f"  [{code}] {m:44} {body[:120].replace(chr(10),' ')}")

print()
print("=== Kiểm tra: request KHÔNG có Authorization (để so sánh) ===")
req = urllib.request.Request(HOST + "/model/us.anthropic.claude-opus-5/invoke",
                            data=json.dumps(BODY_ANTHROPIC).encode(),
                            headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("  ", r.status, r.read()[:120])
except urllib.error.HTTPError as e:
    print(f"   [{e.code}] {e.read()[:200].decode('utf-8','replace')}")
except Exception as e:
    print("  ", type(e).__name__, e)
