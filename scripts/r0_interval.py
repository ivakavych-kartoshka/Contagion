r"""CI cho R₀ — chỉ tính khi dữ liệu cho phép, không suy diễn (R3 W6).

Vì sao cần
----------
§3.6 hứa R₀ được báo "with a Wilson interval" nhưng bảng topology chỉ có điểm ước
lượng. R3 W6 bắt đúng chỗ này.

Công thức
---------
``R0_hat = (1/|I|) * Σ_{i∈I} Z_i`` với I = tập (agent, trial) đã bị compromise,
Z_i = số neighbour hạ nguồn trực tiếp bị compromise trong một hop
(``contagion.metrics.epidemiology.reproduction_number``). Viết lại theo cạnh:

    tử số  = Σ_e c_e   (# lần cạnh e truyền thành công, natural runs)
    mẫu số = Σ_e m_e   (# lần node nguồn của e bị compromise, natural runs)

vì một node nguồn bị compromise xuất hiện đúng một lần trong I cho mỗi cạnh ra.

⚠️ **Giới hạn dữ liệu đã lưu (đã kiểm chứng, không phải phỏng đoán).** Để tính
được, mỗi cạnh cần **cả** ``per_edge`` (natural survival của chính cạnh đó) **và**
``survival_natural`` của node nguồn. Với chain, ``survival_natural`` có đủ 6 cạnh.
Với **star và tree**, ``survival_natural`` chỉ lưu **một** giá trị tổng hợp (ASR của
centre), nên công thức không dựng lại được R₀ — script phát hiện và **từ chối in
CI** thay vì bịa. Đây là một khoảng trống của artifact, không phải điều có thể vá
bằng thống kê.

CÁCH DÙNG
---------
    python scripts/r0_interval.py --dirs topo_chain_n7 topo_star_n7 topo_tree_n7
"""

from __future__ import annotations

import argparse
import json
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
EPS = 1e-9
TOL = 0.02          # dung sai xem cong thuc co khop r0 da luu


def usable_counts(cell: dict) -> tuple:
    """(counts, lý do không dùng được).

    counts[e] = (c_e, m_e). Cạnh mà node NGUỒN không có natural survival riêng bị
    coi là nguồn entry (luôn compromised ⇒ m = N) — quy ước này đúng cho entry của
    chain và cho mọi lá của star/tree. Nhưng nếu phần LỚN cạnh rơi vào trường hợp
    đó thì không thể dựng lại R₀, và ta từ chối thay vì đoán.
    """
    n = int(cell.get("n") or 0)
    pe = cell.get("per_edge") or {}
    sn = cell.get("survival_natural") or {}
    if n <= 0 or not pe:
        return {}, "thiếu n hoặc per_edge"

    known = {e for e in pe if e in sn}                 # cạnh có natural riêng
    if not known:
        return {}, (f"không cạnh nào có natural survival riêng "
                    f"(survival_natural chỉ có {len(sn)} khoá)")
    # Chỉ tính trên các cạnh có natural survival riêng: đó mới là tập dựng lại được.
    counts = {}
    for e in sorted(known):
        src = e.split("->")[0]
        m_hat = float(sn.get(src, 1.0))
        counts[e] = (round(float(sn[e]) * n, 6), round(m_hat * n, 6))
    if len(counts) < len(pe):
        return counts, (f"chỉ {len(counts)}/{len(pe)} cạnh có natural survival riêng "
                        f"→ R₀ dựng lại được chỉ từ tập con này")
    return counts, None


def r0_of(counts: dict) -> float:
    num = sum(c for c, _ in counts.values())
    den = sum(m for _, m in counts.values())
    return (num / den) if den > EPS else float("nan")


def boot_ci(counts: dict, n_boot: int, seed: int, alpha: float = 0.05) -> dict:
    rng = random.Random(seed)
    edges = list(counts.values())
    if not edges:
        return {"ci": [None, None], "n_boot_used": 0}
    vals = []
    for _ in range(n_boot):
        num = den = 0.0
        for _ in edges:
            c, m = rng.choice(edges)
            num += c
            den += m
        if den > EPS:
            vals.append(num / den)
    if not vals:
        return {"ci": [None, None], "n_boot_used": 0}
    vals.sort()
    return {"ci": [round(vals[int(alpha / 2 * (len(vals) - 1))], 4),
                   round(vals[int((1 - alpha / 2) * (len(vals) - 1))], 4)],
            "n_boot_used": len(vals)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=RESULTS / "r0_intervals")
    args = ap.parse_args()

    ok_rows, partial, blocked, mismatch = [], [], [], []
    for name in args.dirs:
        p = RESULTS / name / "results.json"
        if not p.exists():
            blocked.append((name, f"thiếu `{p}`"))
            continue
        o = json.loads(p.read_text(encoding="utf-8"))
        cn = o.get("chain_none") or {}
        counts, why = usable_counts(cn)
        if not counts:
            blocked.append((name, why or "không dựng được counts"))
            continue
        r0_hat = r0_of(counts)
        stored = cn.get("r0")
        # Chỉ nhận khi công thức khớp giá trị đã lưu — nếu không, không in CI.
        if stored is not None and abs(r0_hat - float(stored)) > TOL:
            mismatch.append((name, r0_hat, float(stored), why))
            continue
        ci = boot_ci(counts, args.n_boot, args.seed)
        row = {
            "dir": name, "model": o.get("model"), "topology": o.get("topology"),
            "n_trials": cn.get("n"), "n_edges_usable": len(counts),
            "n_edges_total": len(cn.get("per_edge") or {}),
            "asr": cn.get("asr"), "asr_ci": cn.get("asr_ci"),
            "r0_stored": stored, "r0_recomputed": round(r0_hat, 4),
            "r0_ci_edge_bootstrap": ci["ci"], "n_boot_used": ci["n_boot_used"],
            "caveat": why,
        }
        if why:
            partial.append(row)
        else:
            ok_rows.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "r0_intervals.json").write_text(
        json.dumps({"computed_full": ok_rows, "computed_partial": partial,
                    "blocked": [{"dir": d, "reason": r} for d, r in blocked],
                    "formula_mismatch": [{"dir": d, "recomputed": round(a, 4),
                                          "stored": b, "caveat": w}
                                         for d, a, b, w in mismatch],
                    "n_boot": args.n_boot, "seed": args.seed},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    L = ["# CI cho R₀ — chỉ tính khi dữ liệu cho phép (0 API)", "",
         "R₀ = Σ_e (nguồn truyền thành công) / Σ_e (nguồn bị compromise), suy từ "
         "`per_edge` và `survival_natural` của natural runs. "
         f"Bootstrap theo cạnh, {args.n_boot} lần, seed {args.seed}.", ""]
    if ok_rows:
        L += ["## Dựng lại được đầy đủ (công thức khớp `r0` đã lưu)", "",
              "| thư mục | model | topology | N | ASR [CI] | R₀ đã lưu | R₀ tính lại "
              "| CI95 R₀ |", "|---|---|---|---|---|---|---|---|"]
        for r in ok_rows:
            m = (r["model"] or "").split(".")[-1][:16]
            L.append(f"| `{r['dir']}` | {m} | {r['topology']} | {r['n_trials']} | "
                     f"{r['asr']:.3f} {r['asr_ci']} | {r['r0_stored']:.3f} | "
                     f"{r['r0_recomputed']:.3f} | {r['r0_ci_edge_bootstrap']} |")
        L.append("")
    if partial:
        L += ["## ⚠️ Chỉ dựng lại được từ MỘT TẦM CON cạnh — không dùng làm CI", "",
              "| thư mục | topology | cạnh dùng được | R₀ tính lại | R₀ đã lưu | lý do |",
              "|---|---|---|---|---|---|"]
        for r in partial:
            L.append(f"| `{r['dir']}` | {r['topology']} | "
                     f"{r['n_edges_usable']}/{r['n_edges_total']} | "
                     f"{r['r0_recomputed']:.3f} | "
                     f"{(r['r0_stored'] if r['r0_stored'] is None else round(r['r0_stored'], 3))} "
                     f"| {r['caveat']} |")
        L.append("")
    if mismatch:
        L += ["## ⛔ Tính lại lệch giá trị đã lưu — không in CI", ""]
        for d, a, b, w in mismatch:
            L.append(f"- `{d}`: tính lại {a:.4f} vs đã lưu {b:.4f}"
                     + (f" ({w})" if w else ""))
        L.append("")
    if blocked:
        L += ["## ⛔ Không tính được", ""] + [f"- `{d}`: {r}" for d, r in blocked] + [""]
    L += ["## Hệ quả cho bài (đề xuất sửa §3.6)", "",
          "§3.6 hiện hứa R₀ \"with a Wilson interval\". Có hai lựa chọn trung thực:",
          "",
          "1. **Bỏ hứa hẹn** đó và nói rõ: R₀ là statistic mô tả, báo kèm ASR với "
          "interval; trên chain vẫn báo được interval bootstrap theo cạnh (ở trên).",
          "2. Hoặc báo R₀ chỉ cho chain, và ghi rõ vì sao star/tree không có interval.",
          "",
          "Không nên in interval cho star/tree từ dữ liệu này.", ""]
    (args.out / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}")
    for line in L:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
