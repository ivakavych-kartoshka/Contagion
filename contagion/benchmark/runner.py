"""High-level public API: build config, run experiments, compute metrics,
and serialize results/logs reproducibly."""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that lowers numpy scalars to native Python types."""

    def default(self, o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
        return super().default(o)

from ..core import ContagionConfig
from ..metrics.epidemiology import (
    PropagationPath,
    end_to_end_propagation,
    per_hop_survival,
    propagation_rate,
    reproduction_number,
)
from ..runner.engine import run_experiment


def run_benchmark(config: ContagionConfig) -> Dict:
    """Run one configuration and return a structured result with all metrics."""
    paths = run_experiment(config)
    return {
        "metrics": summarize(paths, config),
        "paths": paths,
        "config": asdict(config) if config is not None else None,
    }


def summarize(paths: List[PropagationPath], config: Optional[ContagionConfig] = None) -> Dict:
    """Aggregate raw paths into the epidemiological metric table."""
    return {
        "survival": {k: _stat(s) for k, s in per_hop_survival(paths).items()},
        "end_to_end": _stat(end_to_end_propagation(paths)),
        "r0": _stat(reproduction_number(paths)),
        "propagation_rate": _stat(propagation_rate(paths)),
        "n_trials": len(paths),
    }


def _stat(s) -> Optional[Dict]:
    return {
        "mean": s.mean,
        "std": s.std,
        "n": s.count,
        "ci_low": s.ci_low,
        "ci_high": s.ci_high,
    }


def save_results(
    results: Dict,
    out_dir: Path,
    tag: Optional[str] = None,
    write_logs: bool = True,
) -> Path:
    """Persist a summarized run (and optional raw per-hop logs) as JSON/CSV.

    Returns the directory the artifacts were written into.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = tag or time.strftime("%Y%m%d-%H%M%S")
    base = out_dir / run_id
    base.mkdir(parents=True, exist_ok=True)
    metrics = results.get("metrics")
    config = results.get("config")
    record = {"metrics": metrics, "config": config}
    (base / "summary.json").write_text(
        json.dumps(record, indent=2, cls=NumpyEncoder), encoding="utf-8"
    )
    if write_logs:
        _write_hop_logs(paths=results.get("paths", []), out=base / "hops.csv")
    write_report(results, base / "report")
    return base


def _write_hop_logs(paths: List[PropagationPath], out: Path) -> None:
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["trial", "step", "src", "dst", "src_comp", "dst_comp"])
        for p in paths:
            for h in p.hops:
                w.writerow(
                    [p.trial_id, h.step, h.src, h.dst, int(h.src_compromised), int(h.dst_compromised)]
                )


def write_report(results: Dict, out: Path) -> Path:
    """Write a human-readable Markdown report (config + metrics table + hop log).

    Returns the path of the written report file.
    """
    out = Path(out)
    metrics = results.get("metrics", {})
    config = results.get("config", {})
    paths = results.get("paths", [])

    def _fmt(v):
        # Bỏ phần "Namespace." để hiển thị giá trị enum gọn (vd TopologyType.CHAIN -> chain)
        if hasattr(v, "value"):
            return str(v.value)
        return str(v)

    lines = []
    lines.append("# Contagion — Pilot Report")
    lines.append("")
    lines.append(f"Ngày tạo: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Config
    lines.append("## 1. Cấu hình (Config)")
    lines.append("")
    lines.append("| Tham số | Giá trị |")
    lines.append("|---|---|")
    if config:
        lines.append(f"| topology | `{_fmt(config.get('topology'))}` |")
        lines.append(f"| num_agents | `{_fmt(config.get('num_agents'))}` |")
        lines.append(f"| trials | `{_fmt(config.get('trials'))}` |")
        lines.append(f"| entry_agent | `{_fmt(config.get('entry_agent'))}` |")
        lines.append(f"| attack | `{_fmt(config.get('attack'))}` |")
        lines.append(f"| re_injection | `{_fmt(config.get('re_injection'))}` |")
        lines.append(f"| defense | `{_fmt(config.get('defense'))}` |")
        lines.append(f"| content_freedom | `{_fmt(config.get('content_freedom'))}` |")
        lines.append(f"| seed | `{_fmt(config.get('seed'))}` |")
        lines.append(f"| model_id | `{_fmt(config.get('model_id'))}` |")
        lines.append("")

    # Metrics
    lines.append("## 2. Metrics")
    lines.append("")
    lines.append(f"- **n_trials**: {metrics.get('n_trials')}")
    lines.append("")
    lines.append("| Metric | mean | std | n | 95% CI |")
    lines.append("|---|---|---|---|---|")
    surv = metrics.get("survival", {})
    overall = surv.get("overall", {})
    lines.append(
        f"| per-hop survival `s` (overall) | {overall.get('mean', 0):.4f} | "
        f"{overall.get('std', 0):.4f} | {overall.get('n', 0)} | "
        f"[{overall.get('ci_low', 0):.4f}, {overall.get('ci_high', 0):.4f}] |"
    )
    for key, m in surv.items():
        if key == "overall":
            continue
        lines.append(
            f"| `s` ({key}) | {m.get('mean', 0):.4f} | {m.get('std', 0):.4f} | "
            f"{m.get('n', 0)} | [{m.get('ci_low', 0):.4f}, {m.get('ci_high', 0):.4f}] |"
        )
    e2e = metrics.get("end_to_end", {})
    r0 = metrics.get("r0", {})
    pr = metrics.get("propagation_rate", {})
    lines.append(
        f"| end-to-end `P_E2E` | {e2e.get('mean', 0):.4f} | {e2e.get('std', 0):.4f} | "
        f"{e2e.get('n', 0)} | [{e2e.get('ci_low', 0):.4f}, {e2e.get('ci_high', 0):.4f}] |"
    )
    lines.append(
        f"| reproduction `R0` | {r0.get('mean', 0):.4f} | {r0.get('std', 0):.4f} | "
        f"{r0.get('n', 0)} | [{r0.get('ci_low', 0):.4f}, {r0.get('ci_high', 0):.4f}] |"
    )
    lines.append(
        f"| propagation rate | {pr.get('mean', 0):.4f} | {pr.get('std', 0):.4f} | "
        f"{pr.get('n', 0)} | [{pr.get('ci_low', 0):.4f}, {pr.get('ci_high', 0):.4f}] |"
    )
    lines.append("")

    # Hop log (first few trials)
    lines.append("## 3. Hop log (ví dụ 5 trial đầu)")
    lines.append("")
    lines.append("| trial | step | src | dst | src_comp | dst_comp |")
    lines.append("|---|---|---|---|---|---|")
    for p in paths[:5]:
        for h in p.hops:
            lines.append(
                f"| {p.trial_id} | {h.step} | {h.src} | {h.dst} | "
                f"{'✔' if h.src_compromised else '✘'} | {'✔' if h.dst_compromised else '✘'} |"
            )
    lines.append("")

    # Interpretation
    lines.append("## 4. Diễn giải")
    lines.append("")
    lines.append(
        f"- `s = {overall.get('mean', 0):.2f}` → payload {100 * overall.get('mean', 0):.0f}% "
        "sống sót qua mỗi hop."
    )
    lines.append(
        f"- `R0 = {r0.get('mean', 0):.2f}` → "
        + ("**supercritical** (R0 ≥ 1): lây lan duy trì/bùng nổ." if r0.get("mean", 0) >= 1 else "**subcritical** (R0 < 1): lây lan suy giảm.")
    )
    lines.append(
        f"- `P_E2E = {e2e.get('mean', 0):.2f}` → injection tới được agent cuối "
        f"trong {100 * e2e.get('mean', 0):.0f}% các trial."
    )

    report_path = out.parent / f"{out.name}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path

