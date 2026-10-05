r"""Định lượng HÌNH DẠNG của đường cong chiều sâu (cho §5.7 của paper).

Câu hỏi: sai số tương đối của phép đo cách ly có TĂNG theo độ sâu không?
Trả lời bằng số, không bằng mắt:

  * Spearman rho giữa depth và rel_err (đo tính đơn điệu; không giả định tuyến tính),
  * độ dốc OLS (điểm phần trăm mỗi hop),
  * mean / min / max rel_err,
  * độ sâu lớn nhất còn "informative" (P(C_i=1) > 0 và tích cách ly > 0).

Điểm bị loại: khi P(C_i=1) = 0 thì rel_err không xác định (chia 0) -> loại, và
nói rõ đã loại bao nhiêu điểm. Đây là chỗ dễ tự lừa nhất: nếu giữ các điểm đó
bằng cách gán rel_err = 1.0 thì "đường cong tăng" trông đẹp hơn thực tế.

CÁCH DÙNG
---------
    python scripts\depth_trend.py --dirs depth_curve_llama depth_curve_qwen depth_curve_deepseek
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _rank(xs: list[float]) -> list[float]:
    """Hạng trung bình cho các giá trị bằng nhau (rank ties)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / (sxx * syy) ** 0.5


def _spearman(xs: list[float], ys: list[float]) -> float:
    return _pearson(_rank(xs), _rank(ys))


def _ols_slope(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def analyze(path: Path) -> dict:
    data = json.loads((path / "results.json").read_text(encoding="utf-8"))
    rows = data["rows"]
    keep, dropped = [], 0
    for r in rows:
        d, pe, pm = r["depth"], r["rel_err"], r["p_measured"]
        if d == 0:
            continue
        # "degenerate": đo được 0 (hoặc tích cách ly 0) -> rel_err vô nghĩa
        if pm <= 0.0 or r["product_isolated"] <= 0.0:
            dropped += 1
            continue
        keep.append((d, pe, pm, r["product_isolated"]))

    depths = [k[0] for k in keep]
    errs = [100.0 * k[1] for k in keep]
    return {
        "model": data["model"],
        "n_agents": data["num_agents"],
        "trials": data["trials"],
        "per_edge": data["per_edge"],
        "n_points": len(keep),
        "n_dropped_degenerate": dropped,
        "max_depth_informative": max(depths) if depths else None,
        "mean_err": sum(errs) / len(errs) if errs else float("nan"),
        "min_err": min(errs) if errs else float("nan"),
        "max_err": max(errs) if errs else float("nan"),
        "spearman": _spearman(depths, errs) if len(set(depths)) > 2 else float("nan"),
        "slope_pp_per_hop": _ols_slope(depths, errs),
        "err_by_depth": {d: round(e, 1) for d, e in zip(depths, errs)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True,
                    help="tên thư mục trong experiments/results/")
    args = ap.parse_args()

    out = []
    for name in args.dirs:
        p = RESULTS / name
        if not (p / "results.json").exists():
            print(f"[skip] {name}: không có results.json")
            continue
        out.append(analyze(p))

    print("| model | chain | điểm dùng | bỏ (degenerate) | sâu nhất | mean | min | max | Spearman(depth, err) | dốc (pp/hop) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for a in out:
        sp = a["spearman"]
        sp_s = "—" if sp != sp else f"{sp:+.2f}"
        sl = a["slope_pp_per_hop"]
        sl_s = "—" if sl != sl else f"{sl:+.1f}"
        print(
            f"| {a['model']} | n={a['n_agents']} | {a['n_points']} | "
            f"{a['n_dropped_degenerate']} | {a['max_depth_informative']} | "
            f"{a['mean_err']:.0f}% | {a['min_err']:.0f}% | {a['max_err']:.0f}% | "
            f"{sp_s} | {sl_s} |"
        )

    print()
    for a in out:
        pts = ", ".join(f"d{d}:{e:.0f}%" for d, e in sorted(a["err_by_depth"].items()))
        print(f"{a['model']}: {pts}")
    print()
    print("Đọc: Spearman ≈ 0 và dốc ≈ 0 ⇒ đường cong PHẲNG (đo cách ly chuyển được);")
    print("     Spearman ≈ +1 ⇒ sai số TĂNG ĐƠN ĐIỆU theo độ sâu (không chuyển được).")
    print("     Số điểm bị bỏ phải được nêu trong paper, không được ẩn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
