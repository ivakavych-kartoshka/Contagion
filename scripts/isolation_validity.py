r"""Tính HỢP LỆ CỦA PHÉP ĐO CÁCH LY (isolation validity) — câu hỏi Markov đúng.

Phát hiện lý thuyết quan trọng (đã khoá bằng test
``tests/test_markov_formal.py::test_natural_product_is_an_identity_not_an_assumption``)
-------------------------------------------------------------------------------
Trong một chain, compromise chỉ lan được từ node trước, nên ``C_i = 1 ⟹
C_{i-1} = 1``. Hệ quả:

    ASR = P(C_k = 1) = ∏_i P(C_i = 1 | C_{i-1} = 1) = ∏_i s_i^nat   ← ĐẲNG THỨC

Vậy **``ASR = ∏ s_i`` KHÔNG phải một giả định về Markov**; nó đúng theo định
nghĩa *miễn là* các ``s_i`` được đo **trong chính quá trình lan truyền**
(``s_i^nat``, từ natural runs). Kiểm định "Markov" mà literature hay nói tới,
diễn đạt cho đúng, là câu hỏi khác:

    s_i^controlled  ?=  s_i^nat

tức: **ước lượng per-hop đo trong điều kiện CÁCH LY (một mình agent nhận + một
artifact chuẩn hoá) có chuyển được sang bối cảnh trong chuỗi hay không?**
Đây chính là giả định mà mọi benchmark single-agent (vd InjecAgent) đang ngầm
dùng khi compose kết quả của họ để dự đoán hành vi pipeline.

Nếu ``s^controlled ≠ s^nat`` một cách hệ thống, thì:
- **không thể** compose kết quả single-hop để dự đoán multi-hop;
- và dấu/độ lớn của sai số có thể phụ thuộc model (ta đo được cả hai hướng).

CÁCH DÙNG
---------
    python scripts\isolation_validity.py
    python scripts\isolation_validity.py --out experiments\results\isolation_validity

Đọc từ mọi ``frontier_*/results.json`` **có** key ``survival_natural`` (tức các
run chạy sau khi thêm phép đo này). In bảng so sánh từng cạnh + verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RES = Path(__file__).resolve().parents[1] / "experiments" / "results"


def collect() -> list:
    """[(label, cell)] cho mọi cell có cả s^controlled và s^natural."""
    out = []
    for rp in sorted(RES.glob("*/results.json")):
        if rp.parent.name.lower().startswith(("smoke", "_", "mini", "test")):
            continue
        try:
            blk = json.loads(rp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(blk, dict):
            continue
        model = blk.get("model", rp.parent.name)
        for key in ("chain_none", "chain_redact"):
            cell = blk.get(key)
            if isinstance(cell, dict) and cell.get("survival_natural"):
                out.append((f"{model} · {key.replace('chain_', '')}", cell))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=RES / "isolation_validity")
    args = ap.parse_args()

    cells = collect()
    if not cells:
        print("[x] chưa có cell nào chứa `survival_natural`.\n"
              "    Chạy lại một cell bằng:\n"
              "      python scripts\\replicate_frontier.py --backend bedrock "
              "--model <id> --only-chain-none --fresh-artifact --out <dir>")
        return 1

    lines = ["# Tính hợp lệ của phép đo CÁCH LY (isolation validity)", "",
             "Câu hỏi đúng (thay cho cách phát biểu 'Markov' thông thường):",
             "**`s_i^controlled == s_i^nat` ?** — ước lượng per-hop đo cách ly có",
             "chuyển được sang bối cảnh trong chuỗi không?", "",
             "(`ASR = ∏ s_i^nat` là ĐẲNG THỨC, không phải giả định — xem docstring.)",
             ""]
    results = []

    for label, cell in cells:
        ctrl = cell.get("per_edge") or {}
        nat = cell.get("survival_natural") or {}
        asr = cell.get("asr")
        edges = sorted(set(ctrl) & set(nat),
                       key=lambda e: int(e.split("->")[1].split("_")[1]))
        prod_c = 1.0
        prod_n = 1.0
        for e in edges:
            prod_c *= ctrl[e]
            prod_n *= nat[e]
        lines += [f"## {label}", "",
                  f"- ASR = **{asr:.3f}** · ∏s^controlled = **{prod_c:.3f}** · "
                  f"∏s^natural = **{prod_n:.3f}**",
                  f"- ASR − ∏s^controlled = **{asr - prod_c:+.3f}** "
                  f"(≠0 ⇒ phép đo cách ly KHÔNG chuyển được sang chuỗi)",
                  f"- ASR − ∏s^natural = {asr - prod_n:+.3f} "
                  f"(≈0 là điều bắt buộc theo đẳng thức; lệch nhiều ⇒ bug)",
                  "",
                  "| edge | s^controlled | s^natural | hiệu | tỉ lệ |",
                  "|---|---|---|---|---|"]
        for e in edges:
            c, n = ctrl[e], nat[e]
            ratio = (n / c) if c > 0 else float("inf")
            lines.append(f"| {e} | {c:.3f} | {n:.3f} | {n - c:+.3f} "
                         f"| {'—' if c == 0 else f'{ratio:.2f}×'} |")
        lines.append("")
        results.append({"label": label, "asr": asr,
                        "prod_controlled": prod_c, "prod_natural": prod_n,
                        "delta_controlled": asr - prod_c,
                        "delta_natural": asr - prod_n,
                        "per_edge": {e: {"controlled": ctrl[e],
                                         "natural": nat[e]} for e in edges}})

    lines += ["## Cách đọc", "",
              "- **`∏s^natural ≈ ASR`** là điều BẮT BUỘC (đẳng thức). Nếu lệch ⇒ "
              "có bug trong đo natural hop, phải sửa trước khi báo cáo.",
              "- **`∏s^controlled ≠ ASR`** là phát hiện: phép đo cách ly không "
              "dự đoán được hành vi trong chuỗi. Dấu của độ lệch cho biết chiều:",
              "  - Δ = ASR − ∏s^controlled **> 0**: cách ly **đánh giá thấp** "
              "lan truyền (payload trong ngữ cảnh công việc thật hiệu quả hơn "
              "artifact trần).",
              "  - Δ **< 0**: cách ly **đánh giá cao** (artifact trần hiệu quả "
              "hơn payload đã bị 'pha' trong output công việc).",
              "- Hệ quả cho literature: benchmark single-agent (InjecAgent và "
              "tương tự) đo trong điều kiện cách ly ⇒ **không compose được** để "
              "dự đoán pipeline, và sai số không cùng dấu trên mọi model.", ""]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    (args.out / "results.json").write_text(
        json.dumps({"cells": results}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
