r"""Chẩn đoán nhanh Bedrock key — KHÔNG bao giờ in giá trị key.

Trả lời 4 câu hỏi khi key "tự nhiên không chạy nữa":

1. **Key thuộc loại nào?** (quyết định "hết hạn" nghĩa là gì)
   - SHORT-TERM: là pre-signed URL, chứa ``X-Amz-`` — sống tối đa **12 giờ** hoặc
     theo session sinh ra nó. Không thể deactivate/reset riêng lẻ.
   - LONG-TERM: không có dấu pre-signed; là 1 IAM user — sống tới **ngày hết hạn
     cấu hình** trong console, và có thể bị **Deactivate / Reset / Delete**.
     ⚠️ Long-term key KHÔNG tự hết theo giờ ⇒ nếu nó chết giữa buổi thì gần như
     chắc là do Deactivate/Reset, hoặc bị đổi IAM policy.
   (Nguồn: docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html và
    .../api-keys-revoke.html)

2. **Key còn dùng được không?** — gọi ``ListFoundationModels`` ở vài region.

3. **Key có bị lưu plaintext ở chỗ khác trên máy không?** (vd extension IDE)
   Một bearer token lộ ra là ai cầm cũng tiêu được tiền của tài khoản.

4. **Có mấy key khác nhau?** — in fingerprint (SHA-256 rút gọn) để so sánh mà
   không lộ giá trị.

CÁCH DÙNG
---------
    python scripts\bedrock_key_diag.py
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contagion.llm.envfile import load_dotenv  # noqa: E402

load_dotenv()

# Nơi các công cụ hay lưu key dạng plaintext (chỉ để CẢNH BÁO, không đọc giá trị).
PLAINTEXT_SPOTS = [
    Path.home() / ".cline/data/secrets.json",
    Path.home() / ".cline/data/settings/providers.json",
    Path(os.environ.get("APPDATA", "")) / "Code/User/globalStorage",
    Path.home() / ".continue/config.json",
    Path.home() / ".aider.conf.yml",
]
KEY_PAT = re.compile(r"bedrock-api-key-[A-Za-z0-9+/=]{40,}")


def fp(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:10]


def classify(key: str) -> str:
    if "X-Amz-" in key:
        return "SHORT-TERM (pre-signed URL) — tối đa 12h hoặc theo session"
    return "LONG-TERM (IAM user) — hết theo NGÀY cấu hình; có thể bị Deactivate/Reset/Delete"


def main() -> int:
    key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or ""
    print("=" * 72)
    if not key:
        print("[x] Không thấy AWS_BEARER_TOKEN_BEDROCK. Kiểm tra file .env")
        return 2
    print(f"1. LOẠI KEY : {classify(key)}")
    print(f"   fingerprint={fp(key)} · độ dài={len(key)} · "
          f"tiền tố={key[:15]}... · có khoảng trắng thừa={key != key.strip()}")
    body = key.replace("bedrock-api-key-", "", 1)
    print(f"   ký tự ngoài base64: "
          f"{sorted(set(c for c in body if not (c.isalnum() or c in '+/=')))}")

    print()
    print("2. KIỂM TRA SỐNG/CHẾT (gọi thẳng BedrockClient — cùng code path với "
          "các script thí nghiệm)")
    try:
        from contagion.llm.bedrock import BedrockClient
        for region, model in (("us-east-1", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
                              ("us-east-1", "amazon.nova-pro-v1:0")):
            try:
                c = BedrockClient(model=model, region=region, temperature=0.0,
                                  max_tokens=8, bearer_token=key)
                out = c.complete("Reply with the single word OK.")
                c.close()
                print(f"   ✓ [{region}] {model[:34]} → OK ({(out or '').strip()[:20]!r})")
            except Exception as exc:
                msg = str(exc).split("\n")[0][:110]
                print(f"   ✗ [{region}] {model[:34]} → {type(exc).__name__}: {msg}")
    except ImportError as exc:
        print(f"   (không import được client: {exc})")

    print()
    print("3. KEY CÓ BỊ LƯU PLAINTEXT Ở CHỖ KHÁC KHÔNG?")
    exposures = []
    for spot in PLAINTEXT_SPOTS:
        if not spot.exists():
            continue
        files = [spot] if spot.is_file() else [
            p for p in spot.rglob("*") if p.is_file() and p.stat().st_size < 12_000_000]
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            found = set(KEY_PAT.findall(text))
            if not found:
                continue
            fps = sorted({fp(k) for k in found})
            exposures.append((p, fps))
            tag = "TRÙNG key .env" if fp(key) in fps else "key KHÁC .env"
            print(f"   ⚠️  {p}\n        {len(found)} key · fingerprint={fps} · {tag}")
    if not exposures:
        print("   ✓ không thấy key lưu plaintext ở các vị trí đã biết")

    print()
    print("4. KẾT LUẬN NHANH")
    print("   - LONG-TERM + chết giữa buổi  => nghi Deactivate/Reset/Delete trên")
    print("     console (hoặc đổi IAM policy), KHÔNG phải hết hạn theo giờ.")
    print("   - Có key KHÁC .env ở nơi khác => key đã được luân chuyển; cập nhật .env.")
    print("   - Chỉ có 1 key và trùng .env   => key hỏng ở mức tài khoản; cần key mới.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
