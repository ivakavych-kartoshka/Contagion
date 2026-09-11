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
    hops_to_compromise,
    markov_test,
    markov_test_formal,
    per_hop_survival,
    propagation_rate,
    reproduction_number,
)
from ..runner.engine import Runner


def estimate_llm_calls(config: ContagionConfig) -> Dict:
    """Ước lượng số LLM calls cho một config (trước khi gọi backend thật).

    Trả về {natural, per_edge, utility, direct_reference, total_max}, là chặn
    TRÊN (upper bound): con số thực phụ thuộc vào propagation (agent chỉ gọi
    model khi nhận message; entry compromised luôn gọi). Dùng cho dry-run để
    ước lượng cost khi chạy LLM thật.
    """
    from ..topology.graph import build_graph

    g = build_graph(config.topology, config.num_agents)
    n_edges = len(g.edges)
    n_agents = config.num_agents

    # Natural runs: mỗi agent nhiều nhất 1 response/trial (entry + downstream).
    natural = config.trials * n_agents
    # Controlled per-edge: 1 compromised-output call mỗi edge + N trial mỗi edge.
    per_edge = n_edges * (1 + config.per_edge_trials)
    # Utility pipeline: clean + attack, mỗi cái ≤ n_agents call/trial.
    ut = config.utility_trials or config.trials
    utility = (2 * ut * n_agents) if config.measure_utility else 0
    # MR y^direct: cache theo (client, system) — upper bound = số lần assess.
    direct_reference = natural + (n_edges * 1) + utility
    total = natural + per_edge + utility + direct_reference
    return {
        "natural": natural,
        "per_edge": per_edge,
        "utility": utility,
        "direct_reference": direct_reference,
        "total_max": total,
    }


def run_benchmark(config: ContagionConfig) -> Dict:
    """Run one configuration and return a structured result with all metrics.

    Executes the protocols required by docs/metric.md:

    - *natural end-to-end runs* (:meth:`Runner.run`) → ASR, R0, propagation rate
      (metric.md §2, §5): entry is compromised by construction (C_0 = 1) and
      compromise propagates naturally downstream;
    - *controlled per-edge trials* (:meth:`Runner.run_per_edge_protocol`) →
      per-edge survival ``s`` (metric.md §1): each trial forces C_src = 1 by
      direct injection, feeds the compromised output to the receiver and judges
      it with the ASV/MR threshold rule;
    - *utility pipeline* (:meth:`Runner.run_utility_protocol`, khi
      ``config.measure_utility``) → U_clean / U_attack / Delta_U / retention
      (metric.md §7).

    Nếu ``config.dry_run=True``: KHÔNG gọi backend (mock hay thật); trả
    ``call_estimate`` (số LLM calls ước lượng) để kiểm soát cost trước khi
    chạy LLM thật.

    The propagation protocols are deliberately independent so that the
    comparison ``ASR ~ prod(s_i)`` is a valid empirical test of the Markov
    assumption.
    """
    if config.dry_run:
        return {
            "metrics": {},
            "paths": [],
            "edge_trials": [],
            "utility": None,
            "call_estimate": estimate_llm_calls(config),
            "config": asdict(config) if config is not None else None,
        }
    runner = Runner(config)
    try:
        paths = runner.run()
        edge_trials = runner.run_per_edge_protocol()
        utility = None
        if config.measure_utility:
            utility = _run_utility(config, runner)
    finally:
        runner.close()
    metrics = summarize(paths, edge_trials, config)
    if utility is not None:
        metrics["utility"] = utility["metrics"]
    return {
        "metrics": metrics,
        "paths": paths,
        "edge_trials": edge_trials,
        "utility": utility,
        "config": asdict(config) if config is not None else None,
    }


def _run_utility(config: ContagionConfig, runner: Runner) -> Dict:
    """Paired clean/attack pipeline runs → §7 utility metrics."""
    from ..metrics.utility import build_target_task, result_to_dict, utility_under_attack

    clean_paths = runner.run_utility_protocol(attack=False)
    attack_paths = runner.run_utility_protocol(attack=True)
    task = build_target_task(
        marker=config.marker,
        reference=config.extra.get("target_task_reference"),
    )
    res = utility_under_attack(
        task,
        clean_outputs=[p.final_output for p in clean_paths],
        attack_outputs=[p.final_output for p in attack_paths],
    )
    return {
        "clean_paths": clean_paths,
        "attack_paths": attack_paths,
        "metrics": result_to_dict(res),
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
    - ``hops_to_compromise``: metric.md §6 — mean/median/min/max hops until
      the target is compromised, plus the right-censoring rate (trials where
      the target was never compromised within the horizon).
    - ``markov_check``: metric.md §2 / theory §2.5 — compares the empirical
      ASR against prod_i s_hat_i (controlled per-edge); only defined for pure
      chains (None otherwise).
    """
    surv = controlled_per_edge_survival(edge_trials or [])
    edges = {k for k in surv if k != "overall"}
    targets = None
    entry_agent = config.entry_agent if config is not None else "agent_0"
    if config is not None:
        tg = config.extra.get("target_agents")
        if isinstance(tg, (list, tuple)) and tg:
            targets = tg
    return {
        "survival": {k: _stat(s) for k, s in surv.items()},
        # Per-hop survival đo TRỰC TIẾP trên natural runs: s_i^nat =
        # P(C_i = 1 | C_{i-1} = 1) trong chính quá trình lan truyền thật.
        #
        # Vì trong chain C_i = 1 ⟹ C_{i-1} = 1, ta có ĐẲNG THỨC
        #     ASR = ∏_i s_i^nat
        # (không phải giả định!). Do đó "kiểm định Markov" có ý nghĩa thực chất
        # KHÔNG phải là kiểm tra đẳng thức đó, mà là kiểm tra xem **ước lượng
        # cách ly** s_i^controlled (per-edge protocol, artifact chuẩn hoá) có
        # chuyển được sang bối cảnh trong chuỗi hay không:
        #     s_i^controlled  ==  s_i^nat  ?
        # Xem scripts/isolation_validity.py.
        "survival_natural": {k: _stat(s) for k, s in per_hop_survival(paths).items()},
        "asr": _stat(attack_success_rate(paths, targets=targets)),
        "r0": _stat(reproduction_number(paths)),
        "r0_ds_check": _ds_check(surv, config, edges),
        "propagation_rate": _stat(propagation_rate(paths)),
        "hops_to_compromise": hops_to_compromise(paths, targets=targets),
        "markov_check": markov_test(paths, edge_trials or [], targets=targets, entry_agent=entry_agent),
        # Kiểm định hình thức (p-value + MDE) — xem epidemiology.markov_test_formal:
        # "consistent" của markov_check là quy tắc CI-chồng-nhau thô; key này cho
        # p-value bootstrap và sai lệch nhỏ nhất phát hiện được ở cỡ mẫu hiện tại.
        "markov_test_formal": markov_test_formal(
            paths, edge_trials or [], targets=targets, entry_agent=entry_agent
        ),
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
    """Persist a summarized run (and optional raw logs) as JSON/CSV/JSONL.

    Writes:
    - ``summary.json`` — metrics (incl. utility khi đo) + config;
    - ``hops.csv`` — per-hop propagation log (natural runs);
    - ``agent_logs.jsonl`` — cross-metric per-agent-instance log (metric.md
      "Cross-Metric Logging Requirements") từ natural runs + utility pipeline
      (khi ``measure_utility``), mỗi dòng một JSON;
    - ``report.md`` — report Markdown đọc được.
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
        _write_agent_logs(results, base / "agent_logs.jsonl")
    write_report(results, base / "report")
    return base


def _collect_agent_logs(results: Dict) -> List[Dict]:
    """Gom agent-instance logs từ mọi nguồn (natural + utility clean/attack)."""
    rows: List[Dict] = []
    mode = "propagation"
    for p in results.get("paths", []):
        for lg in p.agent_logs:
            rows.append({"mode": mode, **asdict(lg)})
    util = results.get("utility")
    if util:
        for mode, key in (("utility_clean", "clean_paths"), ("utility_attack", "attack_paths")):
            for p in util.get(key, []):
                for lg in p.agent_logs:
                    rows.append({"mode": mode, **asdict(lg)})
    return rows


def _write_agent_logs(results: Dict, out: Path) -> None:
    rows = _collect_agent_logs(results)
    if not rows:
        return
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, cls=NumpyEncoder) + "\n")


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

    # Hops-to-compromise (metric.md §6)
    htc = metrics.get("hops_to_compromise")
    if htc and htc.get("n_total"):
        lines.append("| Metric | giá trị |")
        lines.append("|---|---|")
        lines.append(f"| hops-to-compromise mean | {htc.get('mean')} |")
        lines.append(f"| hops-to-compromise median | {htc.get('median')} |")
        lines.append(f"| min / max | {htc.get('min')} / {htc.get('max')} |")
        lines.append(f"| trials target compromised | {htc.get('n_compromised')} / {htc.get('n_total')} |")
        lines.append(f"| censored (never compromised) rate | {htc.get('censored_rate'):.3f} |")
        lines.append("")

    # Markov check (metric.md §2)
    mc = metrics.get("markov_check")
    if mc:
        lines.append("| Kiểm định Markov | ASR | prod(s_i) | verdict |")
        lines.append("|---|---|---|---|")
        lo, hi = mc.get("product_s_ci") or [None, None]
        ci_txt = "n/a" if lo is None else f"[{lo:.4f}, {hi:.4f}]"
        lines.append(
            f"| ASR vs ∏sᵢ | {mc.get('asr'):.4f} | {mc.get('product_s'):.4f} {ci_txt} | {mc.get('verdict')} |"
        )
        lines.append("")

    # Utility Under Attack (metric.md §7)
    ut = metrics.get("utility")
    if ut:
        ret = ut.get("retention")
        ret_txt = "n/a (U_clean=0)" if ret is None else f"{ret:.4f}"
        lines.append("| Utility (§7) | giá trị |")
        lines.append("|---|---|")
        lines.append(f"| U_clean | {ut.get('u_clean'):.4f} |")
        lines.append(f"| U_attack | {ut.get('u_attack'):.4f} |")
        lines.append(f"| Delta_U = U_clean − U_attack | {ut.get('delta_u'):.4f} |")
        lines.append(f"| Utility retention = U_attack / U_clean | {ret_txt} |")
        lines.append(f"| n_clean / n_attack | {ut.get('n_clean')} / {ut.get('n_attack')} |")
        lines.append(f"| target task family | `{ut.get('task')}` |")
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

    # Agent-instance log (cross-metric logging, first few rows)
    logs = _collect_agent_logs(results)
    if logs:
        lines.append("## 3b. Agent-instance log (cross-metric; 3 dòng đầu)")
        lines.append("")
        lines.append("| mode | trial | agent | role | step | asv | mr | C |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for lg in logs[:3]:
            lines.append(
                f"| {lg.get('mode')} | {lg.get('trial_id')} | {lg.get('agent_id')} | "
                f"{lg.get('role')} | {lg.get('step')} | {lg.get('asv')} | {lg.get('mr')} | "
                f"{'✔' if lg.get('compromised') else '✘'} |"
            )
        lines.append(f"  (đầy đủ: `agent_logs.jsonl`, {len(logs)} rows)")
        lines.append("")

    # Interpretation
    lines.append("## 4. Diễn giải")
    lines.append("")
    lines.append(
        f"- `s = {overall.get('mean', 0):.2f}` → payload {100 * overall.get('mean', 0):.0f}% "
        "sống sót qua mỗi hop (controlled per-edge protocol, metric.md §1; CI Wilson)."
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
        "`ASR` đo bằng các run end-to-end độc lập (metric.md §2); "
        "`CI` của `s` và `ASR` là Wilson score interval (metric.md §1)."
    )
    if mc:
        lines.append(
            f"- Kiểm định Markov (metric.md §2): ASR = {mc.get('asr'):.4f} vs "
            f"∏ŝᵢ = {mc.get('product_s'):.4f} → {mc.get('verdict')}."
        )

    report_path = out.parent / f"{out.name}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path

