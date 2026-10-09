r"""Markov chain hữu hạn chính xác cho loop manager–worker (R1 Q3) — 0 API.

Reviewer R1 Q3 hỏi: với loop manager → w workers → manager, **w bằng bao nhiêu**, và
**P(manager bị compromise lại) mỗi vòng** theo chain Markov hữu hạn dựng từ các
``a_j, c_j`` ĐÃ ĐO là bao nhiêu, so với tỉ lệ quan sát được?

Vì sao cần
----------
§5.8 hiện báo một *mean-field* prediction dựa trên ``ρ(M) = sqrt(Σ_j a_j c_j)``. Với
một loop hữu hạn, node nhị phân, manager chỉ có thể bị compromise lại **một lần mỗi
vòng**, nên ``Σ_j a_j c_j > 1`` **không** hàm ý criticality. Reviewer đúng ở điểm này.
Script này thay mean-field bằng **toàn bộ phân phối trạng thái hữu hạn**.

Mô hình (khớp đúng cách dữ liệu được sinh ra)
--------------------------------------------
Round 0: manager bị compromise (C_m = 1). Worker w_j **chỉ** nhận từ manager, nên
worker chỉ có thể bị compromise nếu manager bị compromise ở vòng trước:

    P(W_j^{(k)} = 1) = a_j · m_{k-1}              (a_j = P(worker bị compromise | m))

Worker báo lại manager với xác suất ``c_j``. Manager bị compromise lại khi **ít nhất
một** worker báo thành công:

    m_{k+1} = 1 - Π_j (1 - c_j · a_j · m_k)

(tương đương ``P(re-compromise) = 1 - Π_j (1 - a_j c_j m_k) ≤ 1``, đúng như R1 nói:
luôn < 1 kể cả khi ``Σ a_j c_j > 1``.)

Script in **dự đoán theo từng vòng** cạnh **tỉ lệ quan sát được** trong
``experiments/results/cyclic_*/results.json``, kèm khoảng Wilson cho tỉ lệ quan sát,
và báo độ lệch. Nó cũng chạy một biến thể **có tương quan** (dùng ``c_j`` hiệu dụng
lớn nhất) để cho biết độ lệch có thể do correlation giữa các worker hay không.

CÁCH DÙNG
---------
    python scripts/cyclic_markov_exact.py --dirs cyclic_llama cyclic_deepseek cyclic_qwen
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

RESULTS = Path(__file__).resolve().parents[1] / "experiments" / "results"


def wilson(k: int, n: int) -> list:
    from contagion.metrics.epidemiology import _wilson_bounds
    if n <= 0:
        return [None, None]
    lo, hi = _wilson_bounds(int(k), int(n))
    return [round(float(lo), 3), round(float(hi), 3)]


def parse_loop(s_isolated: dict) -> tuple:
    """Rút (a_j, c_j) và w từ dict ``s_isolated`` của cyclic_* runs.

    Khoá có dạng ``m->w1``, ``w1->m``. ``a_j`` = P(worker j bị compromise | manager),
    ``c_j`` = P(manager bị compromise lại | worker j báo).
    """
    a, c = {}, {}
    for k, v in s_isolated.items():
        if "->" not in k:
            continue
        src, dst = k.split("->")
        if src == "m" and dst.startswith("w"):
            a[dst] = float(v)
        elif dst == "m" and src.startswith("w"):
            c[src] = float(v)
    workers = sorted(set(a) | set(c), key=lambda x: (len(x), x))
    return workers, a, c


def predict_rounds(workers: list, a: dict, c: dict, rounds: int,
                   correlated: bool = False) -> list:
    """Trả [m_0, m_1, ..., m_rounds] theo chain hữu hạn.

    correlated=True dùng ``c_eff = max_j c_j`` cho MỌI worker, tức giả định các
    worker báo lại một cách hoàn hảo tương quan — cho biết cận trên của dự đoán khi
    bỏ giả định độc lập.
    """
    if correlated:
        c = {w: max(c.values()) for w in workers}
    ms = [1.0]                                   # m_0 = 1 (manager bị compromise)
    # P(W_j^{(1)}=1) = a_j * m_0
    prev_worker = {w: a.get(w, 0.0) * ms[0] for w in workers}
    for _ in range(rounds):
        # manager bị compromise lại nếu >=1 worker báo thành công ở vòng này
        prod = 1.0
        for w in workers:
            prod *= (1.0 - c.get(w, 0.0) * prev_worker[w])
        m_next = 1.0 - prod
        ms.append(m_next)
        # cập nhật trạng thái worker cho vòng sau (worker chỉ nhận từ manager)
        prev_worker = {w: a.get(w, 0.0) * m_next for w in workers}
    return ms


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True,
                    help="vd cyclic_llama cyclic_deepseek cyclic_qwen")
    ap.add_argument("--out", type=Path, default=RESULTS / "cyclic_markov_exact")
    args = ap.parse_args()

    L = ["# Markov chain hữu hạn chính xác cho loop — R1 Q3 (0 API)", "",
         "Mô hình: `m_{k+1} = 1 − Π_j (1 − c_j · a_j · m_k)`, worker chỉ nhận từ",
         "manager nên `P(W_j=k) = a_j · m_{k−1}`. Với mỗi lần chạy, script in dự đoán",
         "theo vòng cạnh tỉ lệ quan sát và khoảng Wilson của tỉ lệ đó.", ""]
    summary = {}

    for name in args.dirs:
        p = RESULTS / name / "results.json"
        if not p.exists():
            L += [f"## `{name}` — ⛔ thiếu `{p}`", ""]
            continue
        o = json.loads(p.read_text(encoding="utf-8"))
        workers, a, c = parse_loop(o.get("s_isolated") or {})
        trials = int(o.get("trials") or 0)
        rounds = int(o.get("rounds") or 0)
        rates = o.get("rates") or {}
        if not workers or not rates:
            L += [f"## `{name}` — ⛔ không rút được `a_j, c_j` hoặc `rates`", ""]
            continue

        pred_ind = predict_rounds(workers, a, c, rounds, correlated=False)
        pred_cor = predict_rounds(workers, a, c, rounds, correlated=True)
        sigma = sum(a.get(w, 0.0) * c.get(w, 0.0) for w in workers)

        L += [f"## `{name}` · model `{o.get('model')}`", "",
              f"- **w = {len(workers)}** worker ({', '.join(workers)}) · "
              f"{trials} trial · {rounds} vòng",
              f"- `a_j` (worker bị compromise | manager): "
              + ", ".join(f"{w}={a.get(w, 0.0):.3f}" for w in workers),
              f"- `c_j` (manager bị compromise lại | worker): "
              + ", ".join(f"{w}={c.get(w, 0.0):.3f}" for w in workers),
              f"- `Σ a_j c_j` = **{sigma:.3f}**"
              + ("  (> 1 ⇒ mean-field gọi là supercritical)" if sigma > 1 else
                 "  (< 1 ⇒ mean-field gọi là subcritical)"),
              "",
              "| vòng | P(m) dự đoán (độc lập) | P(m) dự đoán (tương quan max) "
              "| P(m) quan sát | k/n | CI95 Wilson |",
              "|---|---|---|---|---|---|"]
        for rnd in sorted(rates, key=lambda x: int(x)):
            obs = rates[rnd].get("m")
            if obs is None:
                continue
            k = round(obs * trials)
            pred = pred_ind[int(rnd)] if int(rnd) < len(pred_ind) else float("nan")
            pc = pred_cor[int(rnd)] if int(rnd) < len(pred_cor) else float("nan")
            L.append(f"| {rnd} | {pred:.3f} | {pc:.3f} | {obs:.3f} | {k}/{trials} | "
                     f"{wilson(k, trials)} |")
        L.append("")

        # so ở vòng cuối (nơi mean-field dự đoán extinction)
        last = max(int(r) for r in rates)
        obs_last = rates[str(last)].get("m")
        pred_last = pred_ind[last] if last < len(pred_ind) else float("nan")
        summary[name] = {"w": len(workers), "sigma": round(sigma, 3),
                         "last_round": last,
                         "predicted_m_last": round(pred_last, 4),
                         "observed_m_last": obs_last}
        L += [f"- **Vòng cuối ({last}):** dự đoán {pred_last:.3f} vs quan sát "
              f"{obs_last:.3f}"
              + (f" → lệch {pred_last - obs_last:+.3f}" if obs_last is not None
                 else ""),
              ""]

    L += ["## Đọc kết quả", "",
          "1. Nếu `P(re-compromise) = 1 − Π(1 − a_j c_j)` **< 1** ở mọi vòng kể cả khi",
          "   `Σ a_j c_j > 1`, thì luận điểm của R1 W5 được xác nhận: dùng `Σ a_j c_j`",
          "   làm ngưỡng criticality cho loop hữu hạn là **sai**, và bài phải nói rõ.",
          "2. Nếu dự đoán khớp quan sát ⇒ chain hữu hạn (với giả định độc lập) là mô",
          "   hình đủ cho loop này.",
          "3. Nếu dự đoán **thấp hơn** quan sát rõ rệt ⇒ các worker báo lại **tương",
          "   quan** (cột 'tương quan max' cho biết cận trên). Phải ghi là giới hạn.",
          "",
          "⚠️ Ở n≥5 vòng và 40 trial, sai số chuẩn của tỉ lệ quan sát ≈ "
          "`sqrt(0.25/40) ≈ 0.08`, nên chỉ đọc lệch > ~0.16 là có ý nghĩa.", ""]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text("\n".join(L), encoding="utf-8")
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[done] -> {args.out / 'report.md'}")
    for line in L:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
