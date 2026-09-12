r"""Sinh số cho phụ lục thống kê AAMAS (Mục 8 + 10) — 0 API, đọc kết quả đã lưu.

Hai bảng:
  (A) Benjamini--Hochberg trên mọi cell chain (nguồn: markov_formal/table.md
      p-values đã tính bằng bootstrap 8k vòng; ta chỉ hiệu chỉnh multiplicity).
  (B) Cluster-bootstrap CI cho cạnh yếu Llama a1->a2 (nguồn:
      sensitivity_llama/results.json, per_repeat = cụm resample; đơn vị = repeat,
      KHÔNG phải trial, vì trial trong cùng repeat tương quan — đúng với việc
      chi^2 đã bác bỏ exchangeability giữa context).

Chạy:  python scripts\appendix_stats.py
In ra số để dán vào bảng phụ lục .tex (không tự sửa .tex).
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "experiments" / "results"


def benjamini_hochberg(pvals, q=0.05):
    """Trả về ngưỡng BH và verdict cho từng p (giữ nhãn)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i][1])
    out = {}
    for rank, idx in enumerate(order, start=1):
        label, p = pvals[idx]
        thr = rank / m * q
        out[label] = (p, rank, thr, "reject" if p <= thr else "keep")
    return out


def table_a():
    # p-values đọc thẳng từ markov_formal/table.md (bootstrap 8k, đã kiểm).
    # Cell degenerate (Claude, sd(delta)=0) bị loại khỏi hiệu chỉnh.
    cells = [
        ("qwen2.5:7b none",        0.3165),
        ("qwen2.5:7b paraphrase",  0.7775),
        ("deepseek none",          0.0030),
        ("llama none",             0.0001),
        ("nova none",              0.0858),
    ]
    print("== TABLE A: Benjamini-Hochberg (m=%d non-degenerate, q=0.05) ==" % len(cells))
    res = benjamini_hochberg(cells, q=0.05)
    for label, _ in sorted(cells, key=lambda x: x[1]):
        p, rank, thr, verdict = res[label]
        print(f"  rank {rank}: {label:24s} p={p:.4f}  BH_thr={thr:.4f}  -> {verdict.upper()}")
    print("  (Claude none: degenerate, sd(delta)=0, excluded)")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def table_b():
    data = json.loads((RES / "sensitivity_llama" / "results.json").read_text(encoding="utf-8"))
    edge = "agent_1->agent_2"
    # Chỉ dùng T=0.7 để KHỚP với con số trong paper (chi^2=13.40, within-temperature).
    reps = [r for r in data["per_repeat"] if abs(r["temp"] - 0.7) < 1e-9]
    per = [tuple(r["rates"][edge]) for r in reps]  # (k, n) mỗi repeat
    k_tot = sum(k for k, _ in per)
    n_tot = sum(n for _, n in per)
    p_hat = k_tot / n_tot
    wl, wh = wilson(k_tot, n_tot)
    # Cluster bootstrap: resample REPEATS (cụm), không phải trial.
    rng = random.Random(20260911)
    B = 10000
    boot = []
    R = len(per)
    for _ in range(B):
        idx = [rng.randrange(R) for _ in range(R)]
        kk = sum(per[i][0] for i in idx)
        nn = sum(per[i][1] for i in idx)
        boot.append(kk / nn if nn else 0.0)
    boot.sort()
    cl, ch = boot[int(0.025 * B)], boot[int(0.975 * B)]
    print("\n== TABLE B: weak-edge Llama a1->a2, T=0.7 (%d repeats x 20) ==" % R)
    print(f"  per-repeat (k/n): {per}")
    print(f"  pooled p_hat = {p_hat:.3f}  (k={k_tot}, n={n_tot})")
    print(f"  Wilson 95%% (assumes i.i.d.):        [{wl:.3f}, {wh:.3f}]  width={wh-wl:.3f}")
    print(f"  Cluster-bootstrap 95%% (by repeat):  [{cl:.3f}, {ch:.3f}]  width={ch-cl:.3f}")
    print(f"  design-effect widening factor = {(ch-cl)/(wh-wl):.2f}x")


if __name__ == "__main__":
    table_a()
    table_b()