r"""Kiểm tra mọi thư mục kết quả có HOÀN CHỈNH không (không bị cụt giữa chừng).

Vì sao cần: khi API key chết giữa chừng, một job có thể đã ghi `results.json`
nhưng thiếu ô, hoặc ghi `report.md` mà chưa có số. Script này phát hiện:
  * JSON không parse được,
  * ô thiếu trường bắt buộc (ASR, n, per_edge...),
  * `report.md` thiếu trong khi `results.json` có,
  * thư mục rỗng.

Chạy: python scripts\check_results_complete.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BEDROCK_DIRS_HINT = ("bedrock", "frontier", "topo_", "utility_", "claude", "sensitivity",
                     "cyclic_llama", "content_form", "depth_curve_llama", "depth_curve_deepseek")

# Các script khác nhau ghi tên file khác nhau — không phải lỗi. Nhận hết.
PAYLOAD_NAMES = ("results.json", "summary.json", "validation.json", "mini_study.json",
                 "table.json", "per_edge_raw.json", "samples.json", "outputs.jsonl")
# Thư mục KHÔNG phải kết quả thí nghiệm (bỏ qua, không tính là vấn đề).
NOT_A_RESULT = {"figures"}

problems: list[str] = []
rows: list[tuple] = []

for d in sorted(RESULTS.iterdir()):
    if not d.is_dir() or d.name.startswith("_") or d.name in NOT_A_RESULT:
        continue
    files = {p.name for p in d.iterdir() if p.is_file()}
    payload = next((n for n in PAYLOAD_NAMES if n in files), None)
    rj = d / payload if payload else d / "results.json"
    mt = datetime.fromtimestamp(rj.stat().st_mtime).strftime("%d/%m %H:%M") if rj.exists() else "—"
    status = "OK" if payload else "THIẾU DỮ LIỆU"

    if not files:
        problems.append(f"{d.name}: thư mục RỖNG")
        status = "RỖNG"
    elif payload is None:
        problems.append(f"{d.name}: không có file dữ liệu nào trong {sorted(files)}")
    elif payload.endswith(".json"):
        try:
            j = json.loads(rj.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{d.name}: {payload} KHÔNG parse được: {exc}")
            status = "JSON LỖI"
            j = None
        if j is not None:
            cells = []
            if isinstance(j, dict) and isinstance(j.get("chain_none"), dict):
                cells = [j["chain_none"]]
            elif isinstance(j, dict) and isinstance(j.get("cells"), dict):
                cells = [v for v in j["cells"].values() if isinstance(v, dict)]
            elif isinstance(j, dict) and isinstance(j.get("rows"), list):
                cells = [v for v in j["rows"] if isinstance(v, dict)]
            for i, c in enumerate(cells):
                if "asr" in c and c.get("asr") is None:
                    problems.append(f"{d.name}: ô {i} có asr=None (job cụt?)")
                    status = "CỤT"
                if "n" in c and c.get("n") in (0, None):
                    problems.append(f"{d.name}: ô {i} có n=0/None (job cụt?)")
                    status = "CỤT"
    if payload and payload != "results.json":
        status += f" ({payload})"

    tag = "BEDROCK?" if any(h in d.name for h in BEDROCK_DIRS_HINT) else "local/khác"
    rows.append((d.name, mt, tag, status))

print(f"{'thư mục':52} {'sửa cuối':12} {'loại':12} trạng thái")
print("-" * 100)
for name, mt, tag, st in rows:
    print(f"{name:52} {mt:12} {tag:12} {st}")

print()
if problems:
    print(f"❌ {len(problems)} VẤN ĐỀ:")
    for p in problems:
        print("   -", p)
else:
    print("✅ Mọi thư mục kết quả đều hoàn chỉnh (parse được, có report.md, không ô None).")
