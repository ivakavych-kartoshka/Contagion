"""Phase-2 validation driver: chạy toàn bộ battery và ghi Markdown report.

Usage:
    python scripts/validate_methods.py [--out experiments/results/validation] [--quick]

``--quick`` dùng số replicate nhỏ để smoke (CI/CD); mặc định dùng cấu hình
đầy đủ (n_rep=300, trials=300/per_edge=200, R0 trials=600).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.metrics.validation import (
    build_report,
    markov_power,
    markov_size,
    r0_calibration_table,
    wilson_coverage_table,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("experiments/results/validation"))
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    if args.quick:
        cov = wilson_coverage_table(p_grid=(0.1, 0.5, 0.9), n_grid=(30, 100), n_rep=400)
        size = [markov_size(5, 0.6, 60, 60, n_rep=50, seed=1)]
        power = [markov_power(5, 0.4, 0.9, 0.5, 60, 60, n_rep=50, seed=2)]
        r0 = r0_calibration_table(trials=150, per_edge_trials=60, seed=7)
    else:
        cov = wilson_coverage_table()
        size = [markov_size(n, s, 300, 200, n_rep=300, seed=1)
                for n, s in ((4, 0.6), (5, 0.6), (5, 0.8))]
        power = [markov_power(5, 0.4, 0.9, 0.5, t, pe, n_rep=300, seed=2)
                 for t, pe in ((100, 100), (200, 200), (300, 200))]
        r0 = r0_calibration_table(trials=600, per_edge_trials=120, seed=7)

    report = build_report(coverage_rows=cov, size_rows=size,
                          power_rows=power, r0_rows=r0)

    args.out.mkdir(parents=True, exist_ok=True)
    md = args.out / "report.md"
    md.write_text(report, encoding="utf-8")
    payload = {
        "wilson_coverage": cov,
        "markov_size": size,
        "markov_power": power,
        "r0_vs_ds": r0,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (args.out / "validation.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print(f"[done] report -> {md}  ({payload['elapsed_s']}s)")
    print(report.split("\n\n")[1][:400])  # peek đầu report
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
