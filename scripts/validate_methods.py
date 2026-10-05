"""Phase-2 validation driver: chạy toàn bộ battery và ghi Markdown report.

Usage:
    python scripts/validate_methods.py [--out experiments/results/validation] [--quick]

``--quick`` dùng số replicate nhỏ để smoke (CI/CD); mặc định dùng cấu hình
đầy đủ (n_rep=300, trials=300/per_edge=200, R0 trials=600).

Battery gồm 6 phần:
  1. Wilson CI coverage (metric.md §1)
  2. Markov test size (true Markov data)
  3. Markov test power (super-Markov latent regime)
  3b. Hiệu chuẩn kiểm định Markov HÌNH THỨC (size/bias/MDE của markov_test_formal)
  3c. Power: hình thức vs quy tắc CI-chồng-nhau
  3d. Cỡ mẫu cần để đạt MDE mục tiêu (biện minh cho n headline)
  4. R0 vs d·s̄ (chain/star/tree)
  5. N khuyến nghị cho Wilson half-width
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.metrics.validation import (  # noqa: E402
    build_report,
    markov_formal_calibration,
    markov_formal_power_calibration,
    markov_power,
    markov_size,
    r0_calibration_table,
    recommended_trials_for_mde,
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
        formal = [markov_formal_calibration(trials=120, per_edge=120, n_rep=20,
                                            seed=3, n_boot=400)]
        formal_pow = [markov_formal_power_calibration(trials=100, per_edge=100,
                                                      n_rep=15, seed=4, n_boot=400)]
        mde = recommended_trials_for_mde(0.6, 3, target_mde=0.15,
                                         n_grid=(50, 200), n_rep=10, n_boot=300)
        r0 = r0_calibration_table(trials=150, per_edge_trials=60, seed=7)
    else:
        cov = wilson_coverage_table()
        size = [markov_size(n, s, 300, 200, n_rep=300, seed=1)
                for n, s in ((4, 0.6), (5, 0.6), (5, 0.8))]
        power = [markov_power(5, 0.4, 0.9, 0.5, t, pe, n_rep=300, seed=2)
                 for t, pe in ((100, 100), (200, 200), (300, 200))]
        # Hiệu chuẩn kiểm định hình thức: 2 chế độ (s thấp/cao) × n vừa/lớn.
        formal = [markov_formal_calibration(s=s, trials=n, per_edge=n, n_rep=60,
                                            seed=10 + i, n_boot=800)
                  for i, (s, n) in enumerate(((0.6, 120), (0.7, 400), (0.9, 400)))]
        formal_pow = [markov_formal_power_calibration(trials=t, per_edge=t,
                                                      n_rep=40, seed=20 + i, n_boot=800)
                      for i, t in enumerate((75, 150, 300))]
        # Cỡ mẫu cho MDE mục tiêu 0.10 (mức mà paper muốn loại trừ).
        mde = recommended_trials_for_mde(0.6, 3, target_mde=0.10,
                                         n_grid=(100, 200, 400, 800, 1600),
                                         n_rep=40, n_boot=500)
        r0 = r0_calibration_table(trials=600, per_edge_trials=120, seed=7)

    report = build_report(coverage_rows=cov, size_rows=size,
                          power_rows=power, r0_rows=r0,
                          formal_rows=formal, formal_power_rows=formal_pow,
                          mde_rows=mde)

    args.out.mkdir(parents=True, exist_ok=True)
    md = args.out / "report.md"
    md.write_text(report, encoding="utf-8")
    payload = {
        "wilson_coverage": cov,
        "markov_size": size,
        "markov_power": power,
        "markov_formal": formal,
        "markov_formal_power": formal_pow,
        "mde_by_n": mde,
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
