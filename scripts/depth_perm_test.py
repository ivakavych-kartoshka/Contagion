r"""Permutation p-value + bootstrap CI cho depth slope (R1 W7, R3 W1) — 0 API.

Vì sao cần
----------
§5.7 của bài chính báo Spearman rho và độ dốc OLS của sai số theo độ sâu, nhưng
**không có khoảng tin cậy và không có kiểm định**. Reviewer R1 (W7) và R3 (W1) đều
nêu: độ dốc có thể bất định ở n nhỏ, và thiếu interval là thiếu kỷ luật thống kê.
Script này bổ sung đúng hai thứ đó, từ chính ``results.json`` của các lần chạy
``depth_curve_*`` — không gọi model.

Phương pháp
-----------
Với mỗi model, dùng các điểm (depth, rel_err%) còn "informative" (bỏ depth 0 và các
điểm mà p_measured = 0 hoặc tích cách ly = 0, đúng quy ước của ``depth_trend.py``):

  1. **Permutation test cho Spearman rho**: hoán vị nhãn rel_err so với depth.
     - n ≤ 9  → **liệt kê toàn bộ** n! hoán vị (chính xác).
     - n > 9  → Monte Carlo ``--n-perm`` hoán vị; báo cả p và số hoán vị đã dùng.
     - p hai phía = tỉ lệ |rho_perm| ≥ |rho_obs|.
  2. **Bootstrap CI 95%** cho độ dốc OLS và cho rho: resample các cặp (depth, err)
     có hoàn lại ``--n-boot`` lần (percentile interval).
  3. In cả số điểm và cảnh báo khi n < 8.

ĐẦU RA
------
    experiments/results/depth_perm/report.md      bảng + câu LaTeX sẵn để dán
    experiments/results/depth_perm/depth_perm.json

CÁCH DÙNG
---------
    python scripts/depth_perm_test.py --dirs depth_curve_qwen depth_curve_llama \
        depth_curve_llama_long depth_curve_deepseek depth_curve_deepseek_long
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RESULTS = Path(__file__).resolve().parents[1] / "experiments" / "results"


def _rank(xs: list) -> list:
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


def _pearson(xs: list, ys: list) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / (sxx * syy) ** 0.5


def spearman(xs: list, ys: list) -> float:
    return _pearson(_rank(xs), _rank(ys))


def ols_slope(xs: list, ys: list) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return float("nan")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def permutation_p(depths: list, errs: list, n_perm: int,
                  rng: random.Random) -> tuple:
    """p hai phía cho Spearman; liệt kê toàn bộ nếu n! nhỏ."""
    rho_obs = spearman(depths, errs)
    n = len(errs)
    total_fact = math.factorial(n)
    if total_fact <= 400000:                      # n <= 9 → liệt kê chính xác
        count = tot = 0
        for perm in itertools.permutations(errs):
            tot += 1
            r = spearman(depths, list(perm))
            if not math.isnan(r) and abs(r) >= abs(rho_obs) - 1e-12:
                count += 1
        return rho_obs, count / tot, tot, "exact"
    count = 0
    for _ in range(n_perm):
        shuffled = errs[:]
        rng.shuffle(shuffled)
        r = spearman(depths, shuffled)
        if not math.isnan(r) and abs(r) >= abs(rho_obs) - 1e-12:
            count += 1
    return rho_obs, count / n_perm, n_perm, "monte-carlo"


def bootstrap_ci(depths: list, errs: list, n_boot: int, rng: random.Random,
                 alpha: float = 0.05) -> dict:
    pairs = list(zip(depths, errs))
    slopes, rhos = [], []
    for _ in range(n_boot):
        sample = [rng.choice(pairs) for _ in pairs]
        xs = [p[0] for p in sample]
        ys = [p[1] for p in sample]
        if len(set(xs)) < 2:
            continue
        slopes.append(ols_slope(xs, ys))
        r = spearman(xs, ys)
        if not math.isnan(r):
            rhos.append(r)

    def pct(vals):
        if not vals:
            return [None, None]
        vals = sorted(vals)
        return [round(vals[int(alpha / 2 * (len(vals) - 1))], 3),
                round(vals[int((1 - alpha / 2) * (len(vals) - 1))], 3)]

    return {"slope_ci": pct(slopes), "rho_ci": pct(rhos), "n_boot_used": len(slopes)}


def load_points(d: Path) -> dict:
    data = json.loads((d / "results.json").read_text(encoding="utf-8"))
    keep, dropped = [], 0
    for r in data["rows"]:
        if r["depth"] == 0:
            continue
        if r["p_measured"] <= 0.0 or r["product_isolated"] <= 0.0:
            dropped += 1
            continue
        keep.append((r["depth"], 100.0 * r["rel_err"]))
    return {
        "model": data.get("model"), "n_agents": data.get("num_agents"),
        "trials": data.get("trials"), "per_edge": data.get("per_edge"),
        "n_points": len(keep), "n_dropped": dropped,
        "depths": [k[0] for k in keep], "errs": [k[1] for k in keep],
        "dir": d.name,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=RESULTS / "depth_perm")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows, warns = [], []
    for name in args.dirs:
        d = RESULTS / name
        if not (d / "results.json").exists():
            warns.append(f"thiếu `{d / 'results.json'}`")
            continue
        pt = load_points(d)
        if pt["n_points"] < 3:
            warns.append(f"{name}: chỉ {pt['n_points']} điểm informative → bỏ qua")
            continue
        rho, p, n_perm_used, how = permutation_p(pt["depths"], pt["errs"],
                                                 args.n_perm, rng)
        ci = bootstrap_ci(pt["depths"], pt["errs"], args.n_boot, rng)
        slope = ols_slope(pt["depths"], pt["errs"])
        rows.append({
            "dir": name, "model": pt["model"], "n_agents": pt["n_agents"],
            "trials": pt["trials"], "per_edge": pt["per_edge"],
            "n_points": pt["n_points"], "n_dropped_degenerate": pt["n_dropped"],
            "max_depth": max(pt["depths"]),
            "rho": round(rho, 3), "rho_ci": ci["rho_ci"],
            "p_perm": round(p, 4), "perm_method": how, "n_perm": n_perm_used,
            "slope": round(slope, 2), "slope_ci": ci["slope_ci"],
            "n_boot_used": ci["n_boot_used"],
        })
        if pt["n_points"] < 8:
            warns.append(f"{name}: chỉ {pt['n_points']} điểm — interval rộng, "
                         "đọc như diagnostic chứ không phải test")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "depth_perm.json").write_text(
        json.dumps({"rows": rows, "warnings": warns, "n_perm": args.n_perm,
                    "n_boot": args.n_boot, "seed": args.seed},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    L = ["# Permutation p-value + bootstrap CI cho depth slope (0 API)", "",
         f"{args.n_perm} hoán vị (Monte Carlo khi n > 9) · {args.n_boot} bootstrap · "
         f"seed {args.seed}. p hai phía cho Spearman; CI 95% percentile.", "",
         "| model | lần chạy | điểm | bỏ | sâu nhất | rho | CI95 rho | p (perm) | "
         "slope (pp/hop) | CI95 slope |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['model']} | n={r['n_agents']} | {r['n_points']} | "
                 f"{r['n_dropped_degenerate']} | {r['max_depth']} | "
                 f"{r['rho']:+.2f} | {r['rho_ci']} | {r['p_perm']:.4f} "
                 f"({r['perm_method']}) | {r['slope']:+.1f} | {r['slope_ci']} |")
    L.append("")
    if warns:
        L += ["## ⚠️ Cảnh báo", ""] + [f"- {w}" for w in warns] + [""]
    L += ["## Câu LaTeX sẵn để dán vào §5.7", ""]
    if rows:
        q = next((r for r in rows if "qwen" in (r["model"] or "")), rows[0])
        d = next((r for r in rows if "deepseek" in (r["model"] or "").lower()
                  and r["n_points"] >= 10), None)
        L += ["```latex",
              f"Across models the slopes span {min(r['slope'] for r in rows):+.1f} to "
              f"{max(r['slope'] for r in rows):+.1f} points per hop; the rank "
              f"correlation is significant where the chain is long enough to test it "
              f"({q['model']}: $\\rho = {q['rho']:+.2f}$, permutation "
              f"$p = {q['p_perm']:.3f}$, $n = {q['n_points']}$ depths) and "
              "indistinguishable from chance on the shortest profiles "
              "([fill in from the table]). We report the profile as a diagnostic, "
              "not a calibrated correction: at these depths the bootstrap interval "
              "for the slope is wide, and a short low-power chain can read as flat.",
              "```", ""]
        if d:
            L += [f"(Ví dụ model ngắn nhất: {d['model']}, "
                  f"$\\rho = {d['rho']:+.2f}$, permutation $p = {d['p_perm']:.3f}$, "
                  f"$n = {d['n_points']}$.)", ""]
    L += ["## Cách đọc", "",
          "1. `p (perm)` là kiểm định **hoán vị** cho Spearman — không giả định phân "
          "phối chuẩn, phù hợp vì n rất nhỏ.",
          "2. **Cảnh báo quan trọng:** với n ≤ 9 điểm, ngay cả một `rho` hoàn hảo cũng "
          "chỉ đạt p ≈ 0.002–0.01 ở dạng hai phía; `p` KHÔNG chứng minh độ dốc ổn "
          "định. Đây là lý do phải viết \"diagnostic, not a test\".",
          "3. CI bootstrap là **percentile**, tính trên các cặp (depth, err) — không "
          "hiệu chỉnh cho tương quan giữa các độ sâu của cùng một chuỗi.", ""]
    (args.out / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}")
    for line in L[:16]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
