r"""Per-edge transport tests: Wilson intervals, two-sample tests, and a TOST
equivalence test — **0 model call**, chỉ đọc ``experiments/results/*/results.json``.

Vì sao có script này
--------------------
Review (R3 W1–W2, metareview) yêu cầu:
  - mỗi cạnh của bảng transportability phải có **interval** (hiện Table 2 chỉ có
    điểm), và
  - "DeepSeek agrees within resolution" phải là **equivalence test** (TOST với
    margin công bố trước), không phải "không bác bỏ được H0".

Số đã lưu trong ``results.json`` là **tỉ lệ** ``s^ctrl`` (per_edge) và ``s^nat``
(survival_natural), kèm ``n`` (số natural trial) và ``per_edge_trials``. Từ đó ta
dựng lại **bảng đếm k/N** cho từng cạnh và chạy:

    H0: s^nat − s^ctrl = 0        (two-sample, Fisher exact hai phía)
    TOST: |s^nat − s^ctrl| < margin  (hai phép one-sided ở ±margin)

với CI Wilson cho từng tỉ lệ. Fisher exact cần số nguyên ⇒ script kiểm tra
``p * N`` có ra số nguyên không và **cảnh báo** nếu không (khi đó kết quả là
xấp xỉ và nên chạy lại cell với ``--per-edge`` khớp ``--trials``).

ĐẦU RA
------
    experiments/results/transport_tests/report.md   bảng cho paper (forest-style)
    experiments/results/transport_tests/tests.json  mọi số, máy đọc được

CÁCH DÙNG
---------
    python scripts\transport_tests.py --margin 0.15
    python scripts\transport_tests.py --margin 0.15 --dir frontier_llama3-3-70b_iso
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RES = Path(__file__).resolve().parents[1] / "experiments" / "results"

# thư mục được ưu tiên khi cùng một model có nhiều lần chạy (fresh-artefact trước)
PREFERRED = {
    "Llama 3.3 70B": "frontier_llama3-3-70b_iso",
    "Llama 3.3 70B (n=200)": "weakedge_llama_n200",
    "DeepSeek V3.2": "frontier_deepseek_iso",
    "DeepSeek V3.2 (n=200)": "frontier_deepseek_n200",
    "Nova Pro (n=200)": "frontier_nova_n200",
    "Nova Pro": "frontier_nova-pro",
    "qwen2.5:7b": "topo_chain_n7",
}


def wilson(k: int, n: int) -> tuple:
    from contagion.metrics.epidemiology import _wilson_bounds
    if n <= 0:
        return (None, None)
    lo, hi = _wilson_bounds(int(k), int(n))
    return (round(float(lo), 4), round(float(hi), 4))


def fisher(a: int, b: int, c: int, d: int) -> float:
    """p-value hai phía, Fisher exact trên bảng 2x2 [[a,b],[c,d]]."""
    try:
        from scipy.stats import fisher_exact      # type: ignore
        return float(fisher_exact([[a, b], [c, d]])[1])
    except Exception:
        # fallback: hypergeometric hai phía (chính xác, không cần scipy)
        from math import comb
        n = a + b + c + d
        r1, c1 = a + b, a + c
        def pr(x: int) -> float:
            return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
        p_obs = pr(a)
        lo = max(0, c1 - (n - r1))
        hi = min(r1, c1)
        return min(1.0, sum(pr(x) for x in range(lo, hi + 1)
                            if pr(x) <= p_obs + 1e-12))


def tost(k_ctrl: int, n_ctrl: int, k_nat: int, n_nat: int, margin: float) -> dict:
    """TOST hai phía một-sample-ish: so hai tỉ lệ độc lập với margin ``margin``.

    Dùng Wald SE gộp (pooled) vì cỡ mẫu vừa phải và tỉ lệ trong (0,1):
        se = sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)
        z_lower = ((p2 - p1) - (-margin)) / se
        z_upper = ((p2 - p1) - (+margin)) / se
    p_TOST = max(1 - Phi(z_lower), Phi(z_upper))  (max của hai one-sided)
    """
    from math import erf, sqrt

    def phi(z: float) -> float:
        return 0.5 * (1.0 + erf(z / sqrt(2.0)))

    p1 = k_ctrl / n_ctrl
    p2 = k_nat / n_nat
    se = sqrt(p1 * (1 - p1) / n_ctrl + p2 * (1 - p2) / n_nat) if n_ctrl and n_nat else 0.0
    if se == 0:
        # cả hai ô đều 0/1 tuyệt đối → không có bằng chứng equivalence
        return {"delta": round(p2 - p1, 4), "se": 0.0, "p_tost": None,
                "equivalent": False, "note": "SE = 0 (tỉ lệ ở biên 0/1)"}
    d = p2 - p1
    z_lo = (d + margin) / se
    z_hi = (d - margin) / se
    p_tost = max(1.0 - phi(z_lo), phi(z_hi))
    return {"delta": round(d, 4), "se": round(se, 4),
            "p_tost": round(p_tost, 4), "equivalent": bool(p_tost < 0.05),
            "note": ""}


def exact_counts(p: float, n: int) -> tuple:
    """(k, exact?) — dựng lại k từ tỉ lệ đã lưu; exact=False nếu không nguyên."""
    if not n:
        return (0, True)
    kf = p * n
    k = int(round(kf))
    return (k, abs(kf - k) < 1e-6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--margin", type=float, default=0.15,
                    help="margin tương đương cho TOST (công bố trước, vd 0.15)")
    ap.add_argument("--dir", default=None, help="chỉ chạy một thư mục kết quả")
    ap.add_argument("--out", type=Path, default=RES / "transport_tests")
    args = ap.parse_args()

    targets = ([args.dir] if args.dir else list(dict.fromkeys(PREFERRED.values())))
    rows, warns = [], []
    for name in targets:
        d = RES / name
        rp = d / "results.json"
        if not rp.exists():
            warns.append(f"thiếu `{rp}`")
            continue
        blk = json.loads(rp.read_text(encoding="utf-8"))
        model = blk.get("model", name)
        label = next((k for k, v in PREFERRED.items() if v == name), model)
        for cell_name, cell in blk.items():
            if not (isinstance(cell, dict) and cell_name.startswith("chain_")):
                continue
            ctrl = cell.get("per_edge") or {}
            nat = cell.get("survival_natural") or {}
            n_nat = int(cell.get("n") or 0)
            n_ctrl = int(cell.get("per_edge_trials") or n_nat or 0)
            if not ctrl or not nat:
                continue
            for edge in sorted(set(ctrl) & set(nat)):
                kc, okc = exact_counts(ctrl[edge], n_ctrl)
                kn, okn = exact_counts(nat[edge], n_nat)
                if not (okc and okn):
                    warns.append(
                        f"{label}/{cell_name}/{edge}: k không nguyên từ tỉ lệ đã lưu "
                        f"(n_ctrl={n_ctrl}, n_nat={n_nat}) → chạy lại cell với "
                        f"--per-edge = --trials để có số nguyên")
                p_fish = fisher(kc, n_ctrl - kc, kn, n_nat - kn)
                t = tost(kc, n_ctrl, kn, n_nat, args.margin)
                rows.append({
                    "label": label, "dir": name, "cell": cell_name, "edge": edge,
                    "n_ctrl": n_ctrl, "k_ctrl": kc, "s_ctrl": round(ctrl[edge], 4),
                    "ctrl_ci": wilson(kc, n_ctrl),
                    "n_nat": n_nat, "k_nat": kn, "s_nat": round(nat[edge], 4),
                    "nat_ci": wilson(kn, n_nat),
                    "ratio": (round(nat[edge] / ctrl[edge], 3) if ctrl[edge] else None),
                    "p_fisher": round(p_fish, 4),
                    "tost": t,
                    "exact_counts": bool(okc and okn),
                })
        # Δ tổng hợp + kiểm định hình thức đã lưu
        mf = (blk.get("chain_none") or {}).get("markov_formal")
        if isinstance(mf, dict):
            rows.append({"label": label, "dir": name, "cell": "chain_none",
                         "edge": "ALL (Δ = ASR − ∏s)", "summary": True,
                         "delta": mf.get("delta"), "delta_ci": mf.get("delta_ci"),
                         "p_value": mf.get("p_value"), "mde": mf.get("mde"),
                         "verdict": mf.get("verdict")})

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tests.json").write_text(
        json.dumps({"margin": args.margin, "rows": rows, "warnings": warns},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    L = ["# Per-edge transport tests (0 model call)", "",
         f"TOST margin = **{args.margin}** (công bố trước). "
         "CI = Wilson 95%. `p_Fisher` = kiểm định hai phía s^nat vs s^ctrl. "
         "`p_TOST` < 0.05 ⇒ **tương đương trong margin** (được phép viết "
         "\"agrees within resolution\").", "",
         "| model | edge | s^ctrl (k/N) | CI95 | s^nat (k/N) | CI95 | ratio | "
         "p Fisher | Δ | p TOST | tương đương? |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("summary"):
            L.append(f"| {r['label']} | **{r['edge']}** | | | | | | | "
                     f"{r['delta']:+.3f} [{r['delta_ci'][0]:+.3f}, {r['delta_ci'][1]:+.3f}] | "
                     f"p = {r['p_value']:.4f} (MDE {r['mde']:.2f}) | {r['verdict']} |")
            continue
        t = r["tost"]
        pt = "—" if t["p_tost"] is None else f"{t['p_tost']:.3f}"
        eq = ("✅ có" if t["equivalent"] else
              ("✖ không" if t["p_tost"] is not None else "—"))
        L.append(
            f"| {r['label']} | `{r['edge']}` | {r['s_ctrl']:.3f} "
            f"({r['k_ctrl']}/{r['n_ctrl']}) | [{r['ctrl_ci'][0]:.2f}, {r['ctrl_ci'][1]:.2f}] "
            f"| {r['s_nat']:.3f} ({r['k_nat']}/{r['n_nat']}) "
            f"| [{r['nat_ci'][0]:.2f}, {r['nat_ci'][1]:.2f}] "
            f"| {r['ratio']}× | {r['p_fisher']:.4f} | {t['delta']:+.3f} | {pt} | {eq} |")
    L.append("")
    if warns:
        L += ["## ⚠️ Cảnh báo (phải xử lý trước khi đưa số vào bài)", ""]
        L += [f"- {w}" for w in sorted(set(warns))]
        L.append("")
    L += ["## Cách dùng trong bài", "",
          "1. Thay Table 2 bằng bảng này (thêm 2 cột CI + p) — hoặc đưa bảng vào "
          "phụ lục và giữ Table 2 gọn với CI ở mỗi hàng.",
          "2. Đổi câu \"agrees within resolution\" thành \"equivalent within "
          f"±{args.margin} (TOST p = …)\" CHỈ ở những hàng có ✅; các hàng ✖ vẫn "
          "phải viết là non-rejection.",
          "3. Câu \"s^nat ở cạnh sau là conditional on survivors\" nên ghi ngay "
          "dưới bảng (đúng như R3 W1 nêu).", ""]
    (args.out / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}  ({len(rows)} dòng)")
    for line in L[:14]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
