#!/usr/bin/env python
"""Sweep the experiment matrix for the one-month Contagion study.

Runs the (topology x agent-count x attack x defense) grid and aggregates all
results into a single summary table (CSV + JSON) under experiments/results/.

Usage:
    .\\\\.venv\\\\Scripts\\\\python scripts\\sweep.py --out experiments/results/sweep
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import (
    AttackStrategy,
    ContagionConfig,
    DefenseType,
    ReInjectionMode,
    TopologyType,
)
from contagion.benchmark.runner import run_benchmark

TOPOLOGIES = {
    "chain": (TopologyType.CHAIN, [
        ContagionConfig(topology=TopologyType.CHAIN, num_agents=n) for n in (3, 5, 10)
    ]),
}


def build_matrix() -> list[tuple[dict, ContagionConfig]]:
    jobs = []
    for tname in ("chain", "star", "tree"):
        for n in (3, 5, 10):
            base = ContagionConfig(topology=TopologyType(tname), num_agents=n, trials=20, seed=0)
            for attack in (AttackStrategy.STATIC, AttackStrategy.ADAPTIVE):
                for defense in (DefenseType.NONE, DefenseType.PARAPHRASE, DefenseType.DELIMITER):
                    cfg = ContagionConfig(
                        topology=base.topology,
                        num_agents=n,
                        trials=20,
                        seed=0,
                        attack=attack,
                        defense=defense,
                        model_id="mock",
                    )
                    label = f"{tname}_n{n}_{attack.value}_{defense.value}"
                    jobs.append(({"label": label, "topology": tname, "n": n,
                                  "attack": attack.value, "defense": defense.value}, cfg))
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("experiments/results/sweep"))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    jobs = build_matrix()
    if args.limit:
        jobs = jobs[: args.limit]

    rows = []
    for meta, cfg in jobs:
        print(f"[running] {meta['label']}")
        result = run_benchmark(cfg)
        m = result["metrics"]
        rows.append({
            **meta,
            "survival_overall": m["survival"].get("overall", {}).get("mean"),
            "asr": m["asr"]["mean"],
            "r0": m["r0"]["mean"],
            "propagation_rate": m["propagation_rate"]["mean"],
            "n_trials": m["n_trials"],
        })

    cols = ["label", "topology", "n", "attack", "defense",
            "survival_overall", "asr", "r0", "propagation_rate", "n_trials"]
    with open(args.out / "matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    (args.out / "matrix.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote matrix to {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
