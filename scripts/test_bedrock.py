"""Kiểm tra kết nối Amazon Bedrock + liệt kê model khả dụng.

Cách dùng:
    $env:AWS_BEARER_TOKEN_BEDROCK="bedrock-api-key-..."
    python scripts\test_bedrock.py                  # tự dò region phổ biến
    python scripts\test_bedrock.py --region us-west-2 --model anthropic.claude-sonnet-4-5-20250929-v1:0

Script sẽ:
1. Thử các region phổ biến (us-east-1, us-west-2, ap-southeast-1, eu-central-1...)
2. Liệt kê model Bedrock thấy được ở region đó
3. Gọi thử 1 completion ngắn với model chỉ định (nếu có)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.llm.envfile import load_dotenv  # noqa: E402

load_dotenv()  # đọc key từ file .env (nếu có)

REGIONS = ["us-east-1", "us-west-2", "ap-southeast-1", "ap-northeast-1",
           "eu-central-1", "eu-west-1"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=None, help="bỏ trống = tự dò")
    ap.add_argument("--model", default=None,
                    help="vd anthropic.claude-sonnet-4-5-20250929-v1:0")
    args = ap.parse_args()

    try:
        import boto3
    except ImportError:
        print("❌ Chưa cài boto3. Chạy: python -m pip install boto3")
        return 2

    key = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
    has_iam = bool(os.environ.get("AWS_ACCESS_KEY_ID")
                   and os.environ.get("AWS_SECRET_ACCESS_KEY"))
    if not key and not has_iam:
        print('❌ Chưa có xác thực. Chạy trước:\n'
              '   $env:AWS_BEARER_TOKEN_BEDROCK="bedrock-api-key-..."')
        return 2
    print(f"✓ Có xác thực: {'Bedrock API key' if key else 'IAM keys'}")

    regions = [args.region] if args.region else REGIONS
    working = None
    for rg in regions:
        try:
            ctl = boto3.client("bedrock", region_name=rg)
            models = ctl.list_foundation_models().get("modelSummaries", [])
            if not models:
                print(f"  [{rg}] kết nối OK nhưng 0 model (chưa bật Model access?)")
                working = working or rg
                continue
            print(f"\n✓ [{rg}] kết nối OK — {len(models)} model khả dụng:")
            ids = sorted(m.get("modelId", "") for m in models)
            for mid in ids:
                if any(k in mid.lower() for k in ("claude", "nova", "llama", "deepseek")):
                    print(f"    - {mid}")
            working = rg
            break
        except Exception as e:  # noqa: BLE001
            msg = str(e)[:120]
            print(f"  [{rg}] lỗi: {msg}")

    if not working:
        print("\n❌ Không region nào kết nối được. Kiểm tra key/region với giảng viên.")
        return 1

    print(f"\n→ Region dùng được: {working}")

    # gọi thử completion nếu có model
    if args.model:
        from contagion.llm.bedrock import BedrockClient
        # Claude/Nova mới trên Bedrock thường cần INFERENCE PROFILE (prefix vùng,
        # vd "us.anthropic....") thay vì model id trực tiếp. Thử lần lượt.
        candidates = [args.model]
        if not args.model.startswith(("us.", "eu.", "apac.")):
            candidates.append(f"us.{args.model}")
        last_err = None
        for mid in candidates:
            print(f"\nThử gọi model: {mid} ...")
            try:
                cl = BedrockClient(model=mid, region=working,
                                   temperature=0.0, max_tokens=20)
                out = cl.complete("Reply with exactly: OK")
                cl.close()
                print(f"✓ Gọi thành công! Output: {out[:60]!r}")
                print(f"\n📌 DÙNG LỆNH NÀY cho replicate:\n"
                      f"   python scripts\\replicate_frontier.py --backend bedrock "
                      f"--model {mid} --region {working}")
                return 0
            except Exception as e:  # noqa: BLE001
                last_err = str(e)[:300]
                print(f"  ✗ {last_err[:150]}")
        print(f"\n❌ Tất cả dạng id đều thất bại. Lỗi cuối: {last_err}")
        print("   → Có thể model chưa bật (Bedrock console → Model access), "
              "hoặc cần inference profile khác vùng.")
        return 1
    else:
        print("\n(Thêm --model <id> để gọi thử completion.)")
        print("Gợi ý model mạnh cho nghiên cứu (xem BEDROCK_FIRST_TIME.md mục chọn model):")
        print("  --model anthropic.claude-sonnet-4-5-20250929-v1:0   (khuyến nghị chính)")
        print("  --model anthropic.claude-opus-4-5-20251101-v1:0     (mạnh nhất Anthropic)")
        print("  --model deepseek.v3.2                              (so sánh, open-weight)")
        print("  --model meta.llama3-3-70b-instruct-v1:0            (baseline open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
