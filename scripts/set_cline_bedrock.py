r"""Ghi cấu hình Bedrock cho Cline: model mạnh nhất + sửa 3 lỗi cấu hình.

File Cline thật sự đọc (đã kiểm trong mã extension):
    CLINE_PROVIDER_SETTINGS_PATH  ||  <CLINE_DIR>/settings/providers.json
    CLINE_DIR mặc định = ~/.cline      =>  ~/.cline/data/settings/providers.json

Ba thứ được sửa:
  1. aws.authentication = "api-key"   (thiếu -> Cline lấy mặc định "iam" -> lỗi
     'Could not load credentials from any providers', đúng lỗi người dùng gặp)
  2. aws.region = "us-east-1"         (đang là region khác -> key bị từ chối)
  3. model = model mạnh nhất gọi được (đang là ID không tồn tại)

Có sao lưu .bak trước khi ghi. Không in key ra màn hình.

Chạy: python scripts\set_cline_bedrock.py [--model <id>] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CFG = Path.home() / ".cline" / "data" / "settings" / "providers.json"
DEFAULT_MODEL = "us.anthropic.claude-opus-5"   # 96% SWE-bench Verified (9/2026), #1 gọi được
REGION = "us-east-1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CFG.exists():
        print(f"[x] không thấy {CFG}")
        return 1

    data = json.loads(CFG.read_text(encoding="utf-8", errors="replace"))
    prov = data.setdefault("providers", {})
    bed = prov.setdefault("bedrock", {})
    st = bed.setdefault("settings", {})

    old_model = st.get("model")
    old_aws = json.dumps(st.get("aws", {}), ensure_ascii=False)
    old_region = st.get("region")

    st["provider"] = "bedrock"
    st["model"] = args.model
    aws = st.setdefault("aws", {})
    aws["authentication"] = "api-key"     # (1) nguyên nhân gốc của lỗi credential
    aws["region"] = REGION                # (2)
    aws["useCrossRegionInference"] = True # model có tiền tố us. = inference profile
    aws["usePromptCache"] = True          # tiết kiệm chi phí hội thoại dài
    st["region"] = REGION                 # giữ cả khoá cũ cho tương thích
    data["lastUsedProvider"] = "bedrock"  # để Cline mở lên là dùng Bedrock

    print("=== THAY ĐỔI ===")
    print(f"  model : {old_model!r}\n       -> {args.model!r}")
    print(f"  aws   : {old_aws}\n       -> {json.dumps(aws, ensure_ascii=False)}")
    print(f"  region: {old_region!r} -> {REGION!r}")
    print(f"  lastUsedProvider -> 'bedrock'")

    if args.dry_run:
        print("\n[dry-run] không ghi gì.")
        return 0

    bak = CFG.with_suffix(f".json.bak-{datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(CFG, bak)
    CFG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[đã sao lưu] {bak}")
    print(f"[đã ghi]     {CFG}")

    # đọc lại và in phần bedrock (che key)
    back = json.loads(CFG.read_text(encoding="utf-8"))
    b = back["providers"]["bedrock"]["settings"]
    safe = {k: (f"<ẩn, dài {len(str(v))}>" if k == "apiKey" else v) for k, v in b.items()}
    print("\n=== ĐỌC LẠI ĐỂ CHẮC ===")
    print(json.dumps(safe, ensure_ascii=False, indent=2))
    print(f"lastUsedProvider = {back.get('lastUsedProvider')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
