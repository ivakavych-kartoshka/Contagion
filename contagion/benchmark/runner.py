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
    EdgeTrial,
    PropagationPath,
    SummaryStats,
    attack_success_rate,
    controlled_per_edge_survival,
    propagation_rate,
    reproduction_number,
)
from ..runner.engine import Runner


def run_benchmark(config: ContagionConfig) -> Dict:
    """Run one configuration and return a structured result with all metrics.

    Executes BOTH protocols required by docs/metric.md:

    - *natural end-to-end runs* (:meth:`Runner.run`) → ASR, R0, propagation rate
      (metric.md §2, §5): entry is compromised by construction (C_0 = 1) and
      compromise propagates naturally downstream;
    - *controlled per-edge trials* (:meth:`Runner.run_per_edge_protocol`) →
      per-edge survival ``s`` (metric.md §1): each trial forces C_src = 1 by
      direct injection, feeds the compromised output to the receiver and judges
      it with the ASV/MR threshold rule.

    The two protocols are deliberately independent so that the comparison
    ``ASR ~ prod(s_i)`` is a valid empirical test of the Markov assumption.
    """
    runner = Runner(config)
    try:
        paths = runner.run()
        edge_trials = runner.run_per_edge_protocol()
    finally:
        runner.close()
    return {
        "metrics": summarize(paths, edge_trials, config),
        "paths": paths,
        "edge_trials": edge_trials,
        "config": asdict(config) if config is not None else None,
    }


def summarize(
    paths: List[PropagationPath],
    edge_trials: Optional[List[EdgeTrial]] = None,
    config: Optional[ContagionConfig] = None,
) -> Dict:
    """Aggregate the two protocols into the epidemiological metric table.

    - ``survival``: per-edge ``s`` estimated from the CONTROLLED per-edge
      protocol (metric.md §1), where C_src = 1 was forced; overall = pooled.
    - ``asr``: end-to-end attack success rate measured on the NATURAL runs
      (metric.md §2): mean of Y^(r) over all completed runs, target = last
      agent of each path's node order (chain end-to-end semantics).
    - ``r0``: empirical reproduction number (metric.md §5).
    - ``r0_ds_check``: metric.md §5 consistency check — d * s_bar (d = mean
      out-degree over nodes, s_bar = mean per-edge survival) reported
      alongside ``r0``.
    - ``propagation_rate``: fraction of agents (excluding entry) compromised.
    """
    surv = controlled_per_edge_survival(edge_trials or [])
    edges = {k for k in surv if k != "overall"}
    targets = None
    if config is not None:
        tg = config.extra.get("target_agents")
        if isinstance(tg, (list, tuple)) and tg:
            targets = tg
    return {
        "survival": {k: _stat(s) for k, s in surv.items()},
        "asr": _stat(attack_success_rate(paths, targets=targets)),
        "r0": _stat(reproduction_number(paths)),
        "r0_ds_check": _ds_check(surv, config, edges),
        "propagation_rate": _stat(propagation_rate(paths)),
        "n_trials": len(paths),
        "n_per_edge_trials": _per_edge_n(edge_trials),
    }


def _ds_check(
    surv: Dict[str, SummaryStats],
    config: Optional[ContagionConfig],
    edges: set,
) -> Optional[Dict]:
    """d * s_bar consistency target for R0 (metric.md §5).

    d = average out-degree over network nodes = |E| / |V| for these topologies;
    s_bar = mean per-edge survival over measured edges. R0_hat should converge
    toward d * s_bar when the topology is regular and s homogeneous.
    """
    if config is None or not edges:
        return None
    s_bar = float(np.mean([surv[e].mean for e in edges]))
    d = len(edges) / float(config.num_agents)
    return {"d": d, "s_bar": s_bar, "ds": d * s_bar}


def _per_edge_n(edge_trials: Optional[List[EdgeTrial]]) -> int:
    trials = edge_trials or []
    keys = {f"{t.src}->{t.dst}" for t in trials}
    return len(trials) // max(1, len(keys)) if keys else 0


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
    asr = metrics.get("asr", {})
    r0 = metrics.get("r0", {})
    pr = metrics.get("propagation_rate", {})
    lines.append(
        f"| ASR (end-to-end) | {asr.get('mean', 0):.4f} | {asr.get('std', 0):.4f} | "
        f"{asr.get('n', 0)} | [{asr.get('ci_low', 0):.4f}, {asr.get('ci_high', 0):.4f}] |"
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
        "sống sót qua mỗi hop (controlled per-edge protocol, metric.md §1)."
    )
    lines.append(
        f"- `R0 = {r0.get('mean', 0):.2f}` → "
        + ("**supercritical** (R0 ≥ 1): lây lan duy trì/bùng nổ." if r0.get("mean", 0) >= 1 else "**subcritical** (R0 < 1): lây lan suy giảm.")
    )
    lines.append(
        f"- `ASR = {asr.get('mean', 0):.2f}` → injection tới được agent cuối "
        f"trong {100 * asr.get('mean', 0):.0f}% các trial end-to-end."
    )
    lines.append(
        "- Ghi chú: `s` đo bằng giao thức controlled per-edge (metric.md §1); "
        "`ASR` đo bằng các run end-to-end độc lập (metric.md §2). So sánh "
        "`ASR` với tích các `s_i` là kiểm định giả định Markov (chưa tự động)."
    )

    report_path = out.parent / f"{out.name}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path

