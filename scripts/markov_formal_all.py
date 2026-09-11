r"""Bảng kiểm định Markov HÌNH THỨC cho MỌI cell chain đã chạy.

Vì sao
------
``markov_test`` (quy tắc "hai CI 95% có chồng nhau không") chỉ cho một verdict
thô. Bảng này dùng ``markov_test_formal_from_counts`` để sinh, cho từng cell
chain: ``ASR``, ``∏sᵢ``, ``Δ = ASR − ∏sᵢ`` + CI bootstrap, **p-value**, **MDE**
(sai lệch nhỏ nhất phát hiện được ở cỡ mẫu đó), và verdict.

Đây là **bảng kết quả cốt lõi của paper**: nó trả lời "Markov bậc 1 có đúng
không" bằng một kiểm định thật, kèm độ phân giải — thay vì chỉ nói "consistent".

Nguồn dữ liệu (chỉ đọc, không chạy lại LLM)
-------------------------------------------
- ``task_b_nlarge/summary.json``  → qwen2.5:7b (none, paraphrase), có k/n đầy đủ
- ``frontier_*/results.json``     → mọi model frontier (chain_none, chain_redact);
  ``n_per_edge`` lấy từ header ``report.md`` cùng thư mục (results.json cũ chỉ
  lưu mean), có ghi rõ trong bảng là "n/edge suy từ report".
- ``claude_obf_n30`` không có chain → bỏ qua.

CÁCH DÙNG
---------
    python scripts\markov_formal_all.py
    python scripts\markov_formal_all.py --out experiments\results\markov_formal
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contagion.metrics.epidemiology import markov_test_formal_from_counts  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "experiments" / "results"


def _per_edge_from_report(path: Path) -> int | None:
    """Đọc ``per_edge=<n>`` từ header report.md cùng thư mục (results.json cũ
    không lưu n của per-edge protocol)."""
    rp = path.parent / "report.md"
    if not rp.exists():
        return None
    m = re.search(r"per_edge=(\d+)", rp.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def collect_cells() -> list:
    """[(label, source_note, asr_k, asr_n, [(edge, k, n), ...])]."""
    cells = []

    # --- qwen (Task B n lớn) — có k/n đầy đủ trong summary.json ---
    p = RES / "task_b_nlarge" / "summary.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for defense, blk in d.items():
            surv = blk.get("survival", {})
            edges = [(e, v) for e, v in surv.items() if e != "overall"]
            if not edges:
                continue
            counts = [(e, int(round(v["mean"] * v["n"])), int(v["n"]))
                      for e, v in sorted(edges, key=lambda kv: kv[0])]
            cells.append((f"qwen2.5:7b · {defense}", "summary.json",
                          int(round(blk["asr"]["mean"] * blk["asr"]["n"])),
                          int(blk["asr"]["n"]), counts))

    # --- mọi frontier_*/results.json có chain_none ---
    for rp in sorted(RES.glob("frontier_*/results.json")):
        try:
            blk = json.loads(rp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(blk, dict):
            continue
        cn = blk.get("chain_none")
        if not isinstance(cn, dict) or not cn.get("per_edge"):
            continue
        n_edge = _per_edge_from_report(rp)
        note = "report.md (n/edge)" if n_edge else "KHÔNG rõ n/edge"
        model = str(blk.get("model", rp.parent.name))
        n_tr = int(cn.get("n") or 0)
        if not n_tr or not n_edge:
            continue
        edges = sorted(cn["per_edge"].items(),
                       key=lambda kv: int(kv[0].split("->")[1].split("_")[1]))
        counts = [(e, int(round(m * n_edge)), n_edge) for e, m in edges]
        cells.append((f"{model} · none", note,
                      int(round(float(cn["asr"]) * n_tr)), n_tr, counts))
    return cells


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=RES / "markov_formal")
    ap.add_argument("--n-boot", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cells = collect_cells()
    if not cells:
        print("[x] không tìm thấy cell chain nào")
        return 1

    rows = []
    for label, note, k, n, counts in cells:
        res = markov_test_formal_from_counts(k, n, counts, n_boot=args.n_boot,
                                             seed=args.seed)
        if res is None:
            continue
        rows.append({"label": label, "note": note, "asr_n": n,
                     "n_per_edge": counts[0][2] if counts else None, **res})

    lines = ["# Kiểm định Markov HÌNH THỨC — mọi cell chain (Task Family B)", "",
             "H0: `ASR = ∏sᵢ` (các hop độc lập, Markov bậc 1). "
             "Δ = ASR − ∏sᵢ; CI và p-value theo bootstrap 8k vòng (hai protocol "
             "độc lập nên phương sai cộng được).",
             "MDE = sai lệch nhỏ nhất phát hiện được ở cỡ mẫu này (power 0.8). "
             "**\"consistent\" chỉ có nghĩa là đã loại trừ |Δ| > MDE** — không "
             "phải bằng chứng Markov đúng.", "",
             "| cell | n trial | n/edge | ASR | ∏sᵢ | Δ | Δ 95% CI | p | MDE | verdict | nguồn n/edge |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lo, hi = r["delta_ci"]
        lines.append(
            f"| {r['label']} | {r['asr_n']} | {r['n_per_edge']} "
            f"| {r['asr']:.3f} | {r['product_s']:.3f} | **{r['delta']:+.3f}** "
            f"| [{lo:+.3f}, {hi:+.3f}] | **{r['p_value']:.4f}** "
            f"| {r['mde']:.3f} | {r['verdict']} | {r['note']} |")
    lines += ["", "## Cách đọc", "",
              "- **p < 0.05 ⇒ bác bỏ Markov bậc 1** ở cell đó: per-hop survival "
              "KHÔNG nhân được thành ASR.",
              "- ⚠️ **Trước khi tin bất kỳ verdict nào, kiểm tra nguồn s_i**: nếu "
              "cell chạy với artifact per-edge CỐ ĐỊNH (một mẫu output duy nhất "
              "cho cả 30 trial), thì ∏sᵢ có thể sai lệch theo một hướng và tạo ra "
              "vi phạm Markov GIẢ — cả sub- lẫn super-. Các verdict đáng tin phải "
              "đến từ cell có `--fresh-artifact` (xem E23).",
              "- **Δ < 0 (sub-Markov / attenuation)**: lan truyền thật THẤP hơn "
              "tích per-hop. Cơ chế ứng viên: trong natural runs nội dung "
              "compromised bị **pha loãng** qua từng hop, còn per-edge protocol "
              "giữ nội dung nguồn **cố định** ⇒ per-edge đo 'khả năng tối đa', "
              "natural runs đo 'khả năng thực tế'. Cần nêu rõ trong Limitations.",
              "- **Δ > 0 (super-Markov)**: có tương quan trong cùng trial (ví dụ "
              "regime tiềm ẩn) làm lan truyền MẠNH hơn tích.",
              "- ⚠️ **∏sᵢ = 0 vì một cạnh có s = 0**: phép so chỉ còn là "
              "'ASR > 0' ⇒ rất ít thông tin; đừng đọc là bằng chứng ủng hộ Markov.",
              "- So sánh MDE giữa các cell: cell n nhỏ (40 trial) chỉ loại trừ "
              "được sai lệch lớn ⇒ đừng đọc 'consistent' ở đó là bằng chứng.", ""]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "table.md").write_text("\n".join(lines), encoding="utf-8")
    (args.out / "table.json").write_text(
        json.dumps({"cells": rows, "n_boot": args.n_boot, "seed": args.seed},
                   indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"[done] -> {args.out / 'table.md'}")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
