r"""Thống kê QUY MÔ thực nghiệm: đã chạy bao nhiêu ô, bao nhiêu trial, bao nhiêu
lượt gọi model, tốn bao nhiêu thời gian máy.

Nguyên tắc: chỉ đọc những gì file kết quả GHI LẠI. Chỗ nào phải suy ra thì ghi rõ
công thức và đánh dấu là "ước lượng", không trộn lẫn với số đo trực tiếp.

Chạy: python scripts\scale_report.py
"""

from __future__ import annotations

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


def load(d: Path):
    p = d / "results.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    rows = []          # (dir, kind, model, calls_est, trials, per_edge, elapsed_s, note)
    tot_calls = 0
    tot_natural = 0
    tot_peredge = 0
    tot_elapsed = 0.0
    n_dirs = 0

    for d in sorted(RESULTS.iterdir()):
        if not d.is_dir() or d.name.startswith("_") or d.name == "figures":
            continue
        j = load(d)
        if not isinstance(j, dict):
            continue
        n_dirs += 1
        kind, calls, trials, pe, note = "?", 0, 0, 0, ""

        if isinstance(j.get("chain_none"), dict):
            c = j["chain_none"]
            na = int(j.get("num_agents") or 4)
            trials = int(c.get("n") or 0)
            pe = int(c.get("per_edge", 0) or 0) if not isinstance(c.get("per_edge"), dict) else 0
            n_edges = len(c.get("per_edge") or {}) or (na - 1)
            per_edge_trials = (c.get("markov_formal") or {}).get("per_edge_counts") or {}
            if per_edge_trials:
                pe = max((v[1] for v in per_edge_trials.values()), default=30)
            calls = trials * na + pe * n_edges
            note = f"natural {trials}×{na} + per-edge {pe}×{n_edges}"
            kind = "replicate"
        elif isinstance(j.get("rows"), list) and j.get("num_agents"):
            na = int(j["num_agents"])
            trials = int(j.get("trials") or 0)
            pe = int(j.get("per_edge") or 0)
            calls = trials * na + pe * (na - 1)
            note = f"natural {trials}×{na} + per-edge {pe}×{na-1}"
            kind = "depth curve"
        elif "rho_recurrent" in j:
            na = 3
            trials = int(j.get("trials") or 0)
            rounds = int(j.get("rounds") or 0)
            n_edges = len(j.get("s_isolated") or {}) or 4
            pe = 30
            calls = pe * n_edges + trials * rounds * na
            note = f"per-edge 30×{n_edges} + hồi quy {trials}×{rounds} vòng×{na}"
            kind = "cyclic"
        elif isinstance(j.get("cells"), dict) and "utility" in json.dumps(j["cells"])[:4000]:
            na = 4
            tot = 0
            for c in j["cells"].values():
                nt = int(c.get("n_trials") or 0)
                tot += 2 * nt * na          # clean + attack
                trials += nt
            calls = tot
            note = f"{len(j['cells'])} defense × (clean+attack) × {na} agent"
            kind = "utility"
        elif "per_repeat" in j:
            ks = 0
            for c in (j.get("cells") or {}).values():
                ks += int(c.get("n_total") or 0)
            calls = ks
            trials = ks
            note = "tổng trial ở mọi seed × temperature"
            kind = "sensitivity"
        else:
            continue

        el = 0.0
        for c in ([j["chain_none"]] if isinstance(j.get("chain_none"), dict)
                  else list((j.get("cells") or {}).values()) if isinstance(j.get("cells"), dict)
                  else []):
            if isinstance(c, dict) and c.get("elapsed_s"):
                el += float(c["elapsed_s"])
        tot_elapsed += el
        tot_calls += calls
        tot_natural += trials
        tot_peredge += pe
        rows.append((d.name, kind, str(j.get("model") or "—"), calls, trials, pe, el, note))

    print(f"{'thư mục':40} {'loại':12} {'lượt gọi (ước lượng)':>20} {'thời gian máy':>14}")
    print("-" * 100)
    for name, kind, model, calls, trials, pe, el, note in rows:
        h = f"{el/3600:.2f} h" if el else "—"
        print(f"{name:40} {kind:12} {calls:>20,} {h:>14}")

    print()
    print("=== TỔNG ===")
    n_all = sum(1 for d in RESULTS.iterdir() if d.is_dir() and not d.name.startswith("_"))
    print(f"  thư mục trong experiments/results/   : {n_all} "
          f"(trong đó {n_dirs} có results.json có cấu trúc)")
    print(f"  lượt gọi model (ƯỚC LƯỢNG, cận dưới): {tot_calls:,}")
    print(f"  tổng trial 'tự nhiên' đã chạy        : {tot_natural:,}")
    print(f"  thời gian máy GHI LẠI được          : {tot_elapsed/3600:.2f} giờ "
          f"({tot_elapsed/86400:.2f} ngày)")
    print()
    print("  Lưu ý: 'thời gian máy' là CẬN DƯỚI — chỉ ~8 script có ghi `elapsed_s`.")
    print("  Hai họ script KHÔNG ghi thời gian: đường cong chiều sâu và cyclic")
    print("  (mỗi job chạy local mất khoảng 1,5–2 giờ theo đồng hồ job).")
    print()
    print("  Cách tính lượt gọi (ghi rõ để không ai tưởng là số đo trực tiếp):")
    print("   * replicate : n_tự_nhiên × số_agent + per_edge × số_cạnh")
    print("   * depth     : trials × số_agent + per_edge × (số_agent − 1)")
    print("   * cyclic    : 30 × số_cạnh + trials × số_vòng × 3")
    print("   * utility   : 2 × n_trials × 4 agent cho mỗi defense")
    print("   * sensitiv. : tổng n_total ở mọi seed × temperature")
    print("  ⇒ Đây là CẬN DƯỚI: chưa tính các lần retry khi ép output compromised,")
    print("    chưa tính lần chạy hỏng/bị hủy, và chưa tính các lần chấm lại.")
    print()
    print("  Lưu ý: 'thời gian máy' cũng là cận dưới — chỉ những ô có ghi elapsed_s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
