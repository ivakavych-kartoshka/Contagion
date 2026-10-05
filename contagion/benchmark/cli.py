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
    if config.dry_run or not m:
        est = result.get("call_estimate")
        if est:
            print(f"  [dry-run] estimated LLM calls: "
                  f"natural={est['natural']} per_edge={est['per_edge']} "
                  f"utility={est['utility']} direct_ref={est['direct_reference']} "
                  f"total_max={est['total_max']}")
    else:
        print(f"  survival={m['survival'].get('overall', {}).get('mean')} "
              f"asr={m['asr']['mean']:.3f} r0={m['r0']['mean']:.3f}")
        ut = m.get("utility")
        if ut:
            print(f"  utility: U_clean={ut['u_clean']:.3f} U_attack={ut['u_attack']:.3f} "
                  f"retention={ut['retention']}")
    print(f"  -> {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
