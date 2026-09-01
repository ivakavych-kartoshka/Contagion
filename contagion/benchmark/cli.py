"""Console entry point mirroring scripts/run_experiment.py."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..benchmark.config import load_config
from ..benchmark.runner import run_benchmark, save_results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="contagion-run", description="Run a Contagion experiment.")
    parser.add_argument("config", type=Path)
    parser.add_argument("--out", type=Path, default=Path("experiments/results"))
    parser.add_argument("--tag", type=str, default=None)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    result = run_benchmark(config)
    base = save_results(result, args.out, tag=args.tag)
    m = result["metrics"]
    print(f"[done] topology={config.topology.value} n={config.num_agents} "
          f"attack={config.attack.value} defense={config.defense.value}")
    print(f"  survival={m['survival'].get('overall', {}).get('mean')} "
          f"e2e={m['end_to_end']['mean']:.3f} r0={m['r0']['mean']:.3f}")
    print(f"  -> {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
