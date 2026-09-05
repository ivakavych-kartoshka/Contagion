#!/usr/bin/env python
"""Run a Contagion experiment from a config file and save results.

Usage:
    .\\.venv\\Scripts\\python scripts\\run_experiment.py experiments\\configs\\chain_static_nodefense.yaml

Options:
    --out DIR   Write results into DIR (default: experiments/results)
    --tag NAME  Override the result tag/directory name
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.benchmark.config import load_config  # noqa: E402
from contagion.benchmark.runner import run_benchmark, save_results  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Contagion experiment.")
    parser.add_argument("config", type=Path, help="Path to experiment config YAML.")
    parser.add_argument("--out", type=Path, default=Path("experiments/results"))
    parser.add_argument("--tag", type=str, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    print(f"Running: topology={config.topology.value} agents={config.num_agents} "
          f"attack={config.attack.value} defense={config.defense.value} "
          f"trials={config.trials}")

    result = run_benchmark(config)
    base = save_results(result, args.out, tag=args.tag)

    m = result["metrics"]
    print("\n=== Summary ===")
    print(f"  n_trials        : {m['n_trials']}")
    print(f"  per-hop survival: {m['survival']}")
    print(f"  ASR (e2e)       : {m['asr']['mean']:.4f}")
    print(f"  R0              : {m['r0']['mean']:.4f}")
    print(f"  propagation rate: {m['propagation_rate']['mean']:.4f}")
    print(f"\nResults written to: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
