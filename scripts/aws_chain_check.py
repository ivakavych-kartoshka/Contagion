r"""Tái hiện ĐÚNG lỗi của Cline: chuỗi credential mặc định của AWS SDK.

Cline (và AWS SDK nói chung) có hai đường xác thực KHÁC NHAU:

  (A) "AWS Credentials" / "AWS Profile" / "default chain"
      -> cần accessKeyId + secretAccessKey, lấy theo thứ tự:
         biến môi trường -> ~/.aws/credentials -> IAM role -> SSO
  (B) "Bedrock API Key" (bearer token, dạng `bedrock-api-key-...`)
      -> gửi trong header Authorization, KHÔNG đi qua chuỗi credential

Thông báo "Could not load credentials from any providers. Please ensure your
credential provider returns valid AWS credentials with accessKeyId and
secretAccessKey properties" là của đường (A) khi KHÔNG tìm thấy gì.

Script này chỉ kiểm đường (A). Nó KHÔNG đọc .env của dự án, vì .env chứa bearer
token cho đường (B) — trộn hai đường lại chính là chỗ gây nhầm lẫn.

Chạy: python scripts\aws_chain_check.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOME = Path.home()

print("=== 1. Các nguồn credential mà AWS SDK SẼ tìm (đường A) ===")
env_pairs = [("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"),
             ("AWS_ACCESS_KEY", "AWS_SECRET_KEY")]
found_env = False
for a, b in env_pairs:
    if os.environ.get(a):
        found_env = True
        print(f"  ✓ biến môi trường {a} = {os.environ[a][:4]}… (đã che)")
        print(f"    {b} đặt: {bool(os.environ.get(b))}")
if not found_env:
    print("  ✗ KHÔNG có biến môi trường AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY")

cred = HOME / ".aws" / "credentials"
conf = HOME / ".aws" / "config"
print(f"  {'✓' if cred.exists() else '✗'} {cred}")
print(f"  {'✓' if conf.exists() else '✗'} {conf}")
if cred.exists():
    names = [ln.strip()[1:-1] for ln in cred.read_text(errors="replace").splitlines()
             if ln.strip().startswith("[") and ln.strip().endswith("]")]
    print(f"    profile có trong credentials: {names}")

region = (os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
          or os.environ.get("AWS_REGION_NAME"))
print(f"  region từ môi trường: {region or '(không có)'}")

print()
print("=== 2. Hỏi thẳng SDK xem nó tìm được gì ===")
try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ProfileNotFound, ClientError
except Exception as exc:
    print(f"  (không import được boto3: {exc})")
    raise SystemExit(1)

try:
    session = boto3.Session()
    c = session.get_credentials()
    if c is None:
        print("  ✗ session.get_credentials() trả về None")
        print("    => ĐÂY CHÍNH LÀ lỗi Cline báo: 'Could not load credentials from any providers'")
    else:
        frozen = c.get_frozen_credentials()
        print(f"  ✓ tìm thấy credential, method = {c.method}")
        print(f"    access key = {frozen.access_key_id[:4]}… (đã che)")
        print(f"    có session token (credential tạm): {bool(frozen.token)}")
except Exception as exc:
    print(f"  ✗ {type(exc).__name__}: {exc}")

print()
print("=== 3. Thử gọi Bedrock bằng ĐƯỜNG A (nếu tìm được credential) ===")
for reg in ("us-east-1", "ap-northeast-1"):
    try:
        cli = boto3.client("bedrock-runtime", region_name=reg)
        r = cli.converse(modelId="amazon.nova-lite-v1:0",
                         messages=[{"role": "user", "content": [{"text": "ping"}]}],
                         inferenceConfig={"maxTokens": 5})
        txt = r["output"]["message"]["content"][0]["text"]
        print(f"  ✓ [{reg}] GỌI ĐƯỢC -> {txt.strip()[:20]!r}")
    except NoCredentialsError:
        print(f"  ✗ [{reg}] NoCredentialsError (không có credential nào)")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "?")
        msg = exc.response.get("Error", {}).get("Message", "")[:90]
        print(f"  ✗ [{reg}] {code}: {msg}")
    except Exception as exc:
        print(f"  ✗ [{reg}] {type(exc).__name__}: {str(exc)[:90]}")

print()
print("=== KẾT LUẬN CÁCH ĐỌC ===")
print("  * Nếu mục 1 và 2 đều trống  => máy KHÔNG có credential cho đường (A).")
print("    Cline phải được chuyển sang chế độ 'Bedrock API Key', hoặc bạn phải")
print("    cung cấp accessKeyId/secretAccessKey thật.")
print("  * Nếu mục 3 báo 'Authentication failed' / 'InvalidSignatureException'")
print("    => credential CÓ nhưng SAI hoặc đã bị thu hồi.")
print("  * Hai lỗi này KHÁC NHAU và cách sửa cũng khác nhau.")
