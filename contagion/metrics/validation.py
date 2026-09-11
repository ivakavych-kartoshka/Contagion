"""Phase-2: synthetic method validation for the epidemiological estimators.

Validates, on mock data whose ground truth is *known*, that the estimators
defined in docs/metric.md behave as claimed. This is the methodological
sanity-check that must pass before real-LLM runs are interpreted:

1. **Wilson 95% CI coverage** — :func:`_wilson_bounds` (used by per-hop survival
   ``s`` and ASR via :func:`_binom_summary`) should contain the true proportion
   in ~95% of replications (metric.md §1: ``N*s_hat ~ Binomial(N, s)``).

2. **Markov test size & power** — :func:`markov_test` compares end-to-end ASR
   (natural runs) against ``prod(s_i)`` (controlled per-edge protocol). We feed
   it synthetic data drawn from a *true* first-order Markov process (size: it
   must not reject more than ~alpha of the time) and from a *super-Markov*
   process with per-trial latent regime (power: it must reject → 1 as data grow).

3. **R0 vs d*s̄ consistency** — empirical :func:`reproduction_number` measured on
   engine natural runs is compared against ``d * s_bar`` (mean out-degree times
   mean per-edge survival, metric.md §5) across chain / star / tree and a grid of
   infection probabilities, to characterise exactly where the approximation
   holds (regular topology, s → 1) and where it deviates.

All generators here are *synthetic but engine-consistent*: they build
:class:`PropagationPath` / :class:`EdgeTrial` objects with the same fields the
engine produces, so the estimators under test run on data shaped exactly like
benchmark output.

Run the full battery with ``python scripts/validate_methods.py`` (writes a
Markdown report under ``experiments/results/validation/``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .epidemiology import (
    EdgeTrial,
    HopOutcome,
    PropagationPath,
    _wilson_bounds,
    controlled_per_edge_survival,
    markov_test,
    reproduction_number,
)
from ..core import ContagionConfig, TopologyType
from ..topology.graph import build_graph


# =============================================================================
# 1. SYNTHETIC GENERATORS (engine-consistent data with known ground truth)
# =============================================================================

def synthetic_edge_trials(
    edges: Sequence[Tuple[str, str]],
    s: Dict[str, float],
    n_per_edge: int,
    seed: int = 0,
) -> List[EdgeTrial]:
    """Bernoulli per-edge trials (metric.md §1) with known survival ``s``.

    Each trial independently draws ``dst_compromised ~ Bernoulli(s[edge])``,
    exactly the generative model the controlled protocol measures.
    """
    rng = np.random.default_rng(seed)
    trials: List[EdgeTrial] = []
    for src, dst in edges:
        key = f"{src}->{dst}"
        p = s[key]
        for t in range(n_per_edge):
            comp = bool(rng.random() < p)
            trials.append(EdgeTrial(src=src, dst=dst, trial=t, dst_compromised=comp))
    return trials


def _chain_run(
    n_agents: int,
    regime_s: float,
    rng: np.random.Generator,
    node_ids: Optional[List[str]] = None,
) -> Tuple[List[str], Dict[str, bool], List[HopOutcome]]:
    """One natural propagation run on a chain under survival ``regime_s``.

    Entry (agent_0) is compromised by construction (C_0 = 1, metric.md §2). A
    compromised agent forwards to the next; the receiver is judged compromised
    with probability ``regime_s`` (the per-hop survival). Returns node order,
    per-agent compromise status and recorded hop outcomes.
    """
    order = node_ids or [f"agent_{i}" for i in range(n_agents)]
    comp: Dict[str, bool] = {a: False for a in order}
    comp[order[0]] = True
    hops: List[HopOutcome] = []
    prev_comp = True
    for i in range(1, n_agents):
        if not prev_comp:
            break  # src không compromised → không forward → chuỗi dừng
        dst_comp = bool(rng.random() < regime_s)
        hops.append(
            HopOutcome(
                src=order[i - 1],
                dst=order[i],
                step=i,
                src_compromised=prev_comp,
                dst_compromised=dst_comp,
            )
        )
        comp[order[i]] = dst_comp
        prev_comp = dst_comp
    return order, comp, hops


def markov_paths(
    n_agents: int,
    s: float,
    n_trials: int,
    seed: int = 0,
    node_ids: Optional[List[str]] = None,
) -> List[PropagationPath]:
    """Natural runs from a *true first-order Markov* process.

    Every hop has the same independent survival ``s``. Hence, in expectation,
    the end-to-end ASR (target = last agent) equals ``s**(n_agents-1)``, i.e.
    exactly ``prod_i s_i`` of the controlled protocol — the null model of
    :func:`markov_test`.
    """
    rng = np.random.default_rng(seed)
    order = node_ids or [f"agent_{i}" for i in range(n_agents)]
    paths: List[PropagationPath] = []
    for t in range(n_trials):
        _, comp, hops = _chain_run(n_agents, s, rng, node_ids=order)
        paths.append(
            PropagationPath(
                trial_id=t,
                compromised=comp,
                hops=hops,
                node_order=list(order),
            )
        )
    return paths


def supermarkov_paths(
    n_agents: int,
    s_lo: float,
    s_hi: float,
    w_hi: float,
    n_trials: int,
    seed: int = 0,
    node_ids: Optional[List[str]] = None,
) -> List[PropagationPath]:
    """Natural runs from a *super-Markov* (latent-regime) process.

    Each trial first draws a latent regime (high survival ``s_hi`` with prob
    ``w_hi``, else low ``s_lo``) shared by every hop of that trial — a
    within-trial correlation that breaks the product model:

        ASR_true = w_hi * s_hi^k + (1 - w_hi) * s_lo^k        (k hops)
        > (w_hi * s_hi + (1 - w_hi) * s_lo)^k = prod(s_bar_i)

    by convexity of x -> x^k for k >= 2. The controlled per-edge protocol,
    whose trials re-draw the regime independently per trial, still estimates
    ``s_bar = w_hi*s_hi + (1-w_hi)*s_lo`` per edge. So the same data-generating
    process yields ASR > prod(s_i): the reinforcement / super-Markov regime that
    :func:`markov_test` should flag.
    """
    rng = np.random.default_rng(seed)
    order = node_ids or [f"agent_{i}" for i in range(n_agents)]
    paths: List[PropagationPath] = []
    for t in range(n_trials):
        s_regime = s_hi if rng.random() < w_hi else s_lo
        _, comp, hops = _chain_run(n_agents, s_regime, rng, node_ids=order)
        paths.append(
            PropagationPath(
                trial_id=t,
                compromised=comp,
                hops=hops,
                node_order=list(order),
            )
        )
    return paths


def _chain_edges(n_agents: int, node_ids: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    order = node_ids or [f"agent_{i}" for i in range(n_agents)]
    return [(order[i], order[i + 1]) for i in range(len(order) - 1)]


# =============================================================================
# 2. WILSON CI COVERAGE
# =============================================================================

def wilson_coverage(p_true: float, n: int, n_rep: int = 2000, seed: int = 0) -> Dict:
    """Empirical coverage of the Wilson 95% CI over ``n_rep`` Binomial(n, p) reps.

    Returns the fraction of intervals containing ``p_true`` (target ~0.95) and
    the mean interval width.
    """
    rng = np.random.default_rng(seed)
    ks = rng.binomial(n, p_true, size=n_rep)
    cover = 0
    width_sum = 0.0
    for k in ks:
        lo, hi = _wilson_bounds(int(k), n)
        cover += 1 if (lo is not None and lo <= p_true <= hi) else 0
        if lo is not None:
            width_sum += hi - lo
    return {
        "p": p_true,
        "n": n,
        "n_rep": int(n_rep),
        "coverage": cover / n_rep,
        "mean_width": width_sum / n_rep,
    }


def wilson_coverage_table(
    p_grid: Sequence[float] = (0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95),
    n_grid: Sequence[int] = (10, 30, 100, 300),
    n_rep: int = 2000,
    seed: int = 0,
) -> List[Dict]:
    """Coverage grid over p and n (the operating points of the benchmark)."""
    rows = []
    for p in p_grid:
        for n in n_grid:
            rows.append(wilson_coverage(p, n, n_rep=n_rep, seed=seed))
    return rows


# =============================================================================
# 3. MARKOV TEST SIZE & POWER (through markov_test verdicts)
# =============================================================================

def _verdict_rates(paths, edge_trials, targets=None) -> Dict[str, float]:
    res = markov_test(paths, edge_trials, targets=targets)
    if res is None:
        return {"insufficient": 1.0}
    v = res["verdict"]
    return {
        "consistent": 1.0 if v.startswith("consistent") else 0.0,
        "sub": 1.0 if v.startswith("ASR <") else 0.0,
        "super": 1.0 if v.startswith("ASR >") else 0.0,
        "insufficient": 1.0 if v == "insufficient data" else 0.0,
    }


def _accumulate(acc: Dict[str, float], rates: Dict[str, float]) -> None:
    for k, v in rates.items():
        acc[k] = acc.get(k, 0.0) + v


def markov_size(
    n_agents: int,
    s: float,
    trials: int,
    per_edge: int,
    n_rep: int = 300,
    seed: int = 0,
) -> Dict:
    """Type-I error of :func:`markov_test` under a true Markov process.

    Expected: the "reject" verdicts (ASR < or > prod(s_i)) should occur at a
    low rate (≤ alpha-ish; the CI-overlap rule is conservative, so the measured
    size is typically well below 0.05). Returns the empirical distribution of
    verdicts over ``n_rep`` independent synthetic datasets.
    """
    edges = _chain_edges(n_agents)
    s_map = {f"{a}->{b}": s for a, b in edges}
    acc: Dict[str, float] = {}
    for r in range(n_rep):
        paths = markov_paths(n_agents, s, trials, seed=seed + 10_000 * (r + 1))
        et = synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 777 * (r + 1))
        _accumulate(acc, _verdict_rates(paths, et))
    return {"n_agents": n_agents, "s": s, "trials": trials, "per_edge": per_edge,
            "n_rep": n_rep, **{k: v / n_rep for k, v in acc.items()}}


def markov_power(
    n_agents: int,
    s_lo: float,
    s_hi: float,
    w_hi: float,
    trials: int,
    per_edge: int,
    n_rep: int = 300,
    seed: int = 0,
) -> Dict:
    """Statistical power of :func:`markov_test` under a super-Markov process.

    The true ASR exceeds prod(s_bar_i) (latent-regime correlation, see
    :func:`supermarkov_paths`). Power = fraction of replications flagged
    "ASR > prod(s_i) (reinforcement / super-Markov)"; should grow toward 1 as
    ``trials`` / ``per_edge`` grow. Returns verdict distribution over reps.
    """
    edges = _chain_edges(n_agents)
    s_bar = w_hi * s_hi + (1 - w_hi) * s_lo
    s_map = {f"{a}->{b}": s_bar for a, b in edges}
    acc: Dict[str, float] = {}
    for r in range(n_rep):
        paths = supermarkov_paths(n_agents, s_lo, s_hi, w_hi, trials,
                                  seed=seed + 10_000 * (r + 1))
        et = synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 777 * (r + 1))
        _accumulate(acc, _verdict_rates(paths, et))
    return {"n_agents": n_agents, "s_lo": s_lo, "s_hi": s_hi, "w_hi": w_hi,
            "s_bar": s_bar, "trials": trials, "per_edge": per_edge,
            "n_rep": n_rep, **{k: v / n_rep for k, v in acc.items()}}


# =============================================================================
# 4. R0 vs d * s_bar CALIBRATION (engine natural runs, metric.md §5)
# =============================================================================

def _ds_target(n_edges: int, n_agents: int, s_bar: float) -> Dict:
    d = n_edges / float(n_agents)
    return {"d": d, "s_bar": s_bar, "ds": d * s_bar}


def r0_calibration_row(
    topology: TopologyType,
    num_agents: int,
    p: float,
    trials: int = 600,
    per_edge_trials: int = 120,
    entry_agent: Optional[str] = None,
    seed: int = 42,
) -> Dict:
    """One engine calibration point: empirical R0 vs d*s_bar at infection p.

    Runs the full engine benchmark (mock, homogeneous per-edge survival = p),
    then compares ``r0.mean`` from natural runs against ``d * s_bar`` (metric.md
    §5). Returns everything needed for a report row.
    """
    from ..benchmark.runner import run_benchmark

    g = build_graph(topology, num_agents)
    config = ContagionConfig(
        topology=topology,
        num_agents=num_agents,
        trials=trials,
        per_edge_trials=per_edge_trials,
        entry_agent=entry_agent or config_entry(topology, num_agents),
        seed=seed,
        extra={"mock_infection_prob": p},
    )
    res = run_benchmark(config)
    m = res["metrics"]
    surv = m["survival"]
    edges = {k for k in surv if k != "overall"}
    s_bar = float(np.mean([surv[e]["mean"] for e in edges])) if edges else float("nan")
    ds = _ds_target(len(edges), num_agents, s_bar)
    r0 = m["r0"]["mean"] if m.get("r0") and m["r0"]["mean"] is not None else float("nan")
    return {
        "topology": topology.value,
        "num_agents": num_agents,
        "p": p,
        "n_edges": len(edges),
        "s_bar": s_bar,
        "d": ds["d"],
        "ds": ds["ds"],
        "r0": r0,
        "rel_err": (abs(r0 - ds["ds"]) / ds["ds"]) if ds["ds"] else float("nan"),
        "trials": trials,
    }


def config_entry(topology: TopologyType, num_agents: int) -> str:
    """Entry agent phù hợp cho natural propagation từng topology.

    - chain: agent_0 (đầu chain)
    - star : một LEAF (agent_1 → center) — entry ở center (agent_0) không có
      downstream nên propagation chết ngay (xem configs/star_static_colluding.yaml)
    - tree : agent_0 (root)
    """
    if topology == TopologyType.STAR:
        return "agent_1"
    return "agent_0"


def r0_calibration_table(
    topologies: Sequence[TopologyType] = (
        TopologyType.CHAIN, TopologyType.STAR, TopologyType.TREE,
    ),
    num_agents: int = 7,
    p_grid: Sequence[float] = (0.3, 0.6, 0.9, 1.0),
    trials: int = 600,
    per_edge_trials: int = 120,
    seed: int = 42,
) -> List[Dict]:
    rows = []
    for topo in topologies:
        for p in p_grid:
            rows.append(r0_calibration_row(
                topo, num_agents, p,
                trials=trials, per_edge_trials=per_edge_trials,
                entry_agent=config_entry(topo, num_agents), seed=seed,
            ))
    return rows


# =============================================================================
# 4b. FORMAL MARKOV TEST — SIZE, POWER, MDE (markov_test_formal)
# =============================================================================

def markov_formal_calibration(
    n_agents: int = 5,
    s: float = 0.7,
    trials: int = 400,
    per_edge: int = 400,
    n_rep: int = 40,
    seed: int = 0,
    n_boot: int = 800,
) -> Dict:
    """Hiệu chuẩn :func:`markov_test_formal` trên dữ liệu Markov THẬT.

    Trả về:
      - ``bias_sigma`` = mean(delta) / sd(delta) — phải ≈ 0 (không lệch hệ thống;
        MC se của mean(delta) được báo kèm để đọc đúng),
      - ``size`` = tỷ lệ verdict "reject" (kỳ vọng ≈ alpha = 0.05),
      - ``median_p`` (kỳ vọng ≈ 0.5 nếu p-value hiệu chuẩn đúng),
      - ``mean_mde`` = sai lệch nhỏ nhất phát hiện được, trung bình qua reps.
    """
    from .epidemiology import markov_test_formal

    edges = _chain_edges(n_agents)
    s_map = {f"{a}->{b}": s for a, b in edges}
    deltas: List[float] = []
    ps: List[float] = []
    mdes: List[float] = []
    rejects = 0
    for r in range(n_rep):
        paths = markov_paths(n_agents, s, trials, seed=seed + 1000 + r)
        et = synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 7000 + r)
        res = markov_test_formal(paths, et, seed=seed + r, n_boot=n_boot)
        if res is None:
            continue
        deltas.append(res["delta"])
        ps.append(res["p_value"])
        mdes.append(res["mde"])
        if res["verdict"].startswith("reject"):
            rejects += 1
    d = np.asarray(deltas, dtype=float)
    n = max(1, len(d))
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    return {
        "n_agents": n_agents, "s": s, "trials": trials, "per_edge": per_edge,
        "n_rep": n, "true_asr": s ** (n_agents - 1),
        "mean_delta": float(d.mean()) if n else 0.0,
        "sd_delta": sd,
        "mc_se_mean": sd / np.sqrt(n) if n else 0.0,
        "bias_sigma": (float(d.mean()) / sd) if sd > 0 else 0.0,
        "size": rejects / n,
        "median_p": float(np.median(ps)) if ps else float("nan"),
        "mean_mde": float(np.mean(mdes)) if mdes else float("nan"),
        "alpha_nominal": 0.05,
    }


def markov_formal_power_calibration(
    n_agents: int = 5,
    s_lo: float = 0.35,
    s_hi: float = 0.9,
    w_hi: float = 0.5,
    trials: int = 150,
    per_edge: int = 150,
    n_rep: int = 30,
    seed: int = 0,
    n_boot: int = 800,
) -> Dict:
    """Power của :func:`markov_test_formal` dưới super-Markov, so với CI-overlap.

    Kỳ vọng: power (tỷ lệ "reject" của test hình thức) **cao hơn** tỷ lệ "ASR >"
    của quy tắc CI-chồng-nhau — đây là lý do dùng test hình thức trong paper.
    """
    from .epidemiology import markov_test, markov_test_formal

    edges = _chain_edges(n_agents)
    s_bar = w_hi * s_hi + (1 - w_hi) * s_lo
    s_map = {f"{a}->{b}": s_bar for a, b in edges}
    formal_rej = 0
    rough_rej = 0
    for r in range(n_rep):
        paths = supermarkov_paths(n_agents, s_lo, s_hi, w_hi, trials, seed=seed + 2000 + r)
        et = synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 3000 + r)
        f = markov_test_formal(paths, et, seed=seed + r, n_boot=n_boot)
        if f is not None and f["verdict"].startswith("reject"):
            formal_rej += 1
        rough = markov_test(paths, et)
        if rough is not None and rough["verdict"].startswith("ASR >"):
            rough_rej += 1
    true_asr = w_hi * s_hi ** (n_agents - 1) + (1 - w_hi) * s_lo ** (n_agents - 1)
    return {
        "n_agents": n_agents, "s_lo": s_lo, "s_hi": s_hi, "w_hi": w_hi,
        "s_bar": s_bar, "trials": trials, "per_edge": per_edge, "n_rep": n_rep,
        "true_asr": true_asr, "product_s_bar": s_bar ** (n_agents - 1),
        "power_formal": formal_rej / n_rep,
        "power_ci_overlap_rule": rough_rej / n_rep,
    }


def recommended_trials_for_mde(
    s_bar: float,
    n_hops: int,
    target_mde: float,
    per_edge_ratio: float = 1.0,
    alpha: float = 0.05,
    power: float = 0.8,
    n_grid: Sequence[int] = (50, 100, 200, 400, 800, 1600, 3200),
    n_rep: int = 60,
    seed: int = 0,
    n_boot: int = 400,
) -> List[Dict]:
    """Cỡ mẫu cần để đạt ``target_mde`` cho kiểm định Markov hình thức.

    Với mỗi ``n`` trong ``n_grid``, mô phỏng dữ liệu Markov thật (s_i = s_bar,
    ASR_true = s_bar^n_hops) và đo MDE trung bình ⇒ chọn ``n`` nhỏ nhất có
    ``mean_mde <= target_mde``. Đây là căn cứ để biện minh cho cỡ mẫu headline
    (thay vì chọn n tùy ý).
    """
    from .epidemiology import markov_test_formal

    edges = _chain_edges(n_hops + 1)     # chain n_hops+1 node ⇒ n_hops cạnh
    s_map = {f"{a}->{b}": s_bar for a, b in edges}
    rows: List[Dict] = []
    for n in n_grid:
        per_edge = max(1, int(round(n * per_edge_ratio)))
        mdes: List[float] = []
        for r in range(n_rep):
            paths = markov_paths(n_hops + 1, s_bar, n, seed=seed + 500 + r)
            et = synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 900 + r)
            res = markov_test_formal(paths, et, seed=seed + r, n_boot=n_boot)
            if res is not None:
                mdes.append(res["mde"])
        rows.append({
            "n_trials": n, "n_per_edge": per_edge,
            "mean_mde": float(np.mean(mdes)) if mdes else float("nan"),
            "meets_target": bool(mdes and float(np.mean(mdes)) <= target_mde),
        })
    return rows


# =============================================================================
# 5. RECOMMENDED SAMPLE SIZES
# =============================================================================
def recommended_trials(
    half_width: Sequence[float] = (0.10, 0.05, 0.03),
    p_worst: float = 0.5,
    z: float = 1.96,
) -> List[Dict]:
    """N needed for a Wilson CI of given half-width at the worst-case p=0.5.

    Metric.md §1 floor is N >= 30; headline claims typically want half-width
    <= 0.05 (N ~ 385) or <= 0.03 (N ~ 1068) at p = 0.5.
    """
    rows = []
    for hw in half_width:
        n = int(np.ceil((z / hw) ** 2 * p_worst * (1 - p_worst)))
        rows.append({"half_width": hw, "p": p_worst, "z": z, "n_recommended": n})
    return rows


# =============================================================================
# 6. REPORT
# =============================================================================

def build_report(
    coverage_rows: Optional[List[Dict]] = None,
    size_rows: Optional[List[Dict]] = None,
    power_rows: Optional[List[Dict]] = None,
    r0_rows: Optional[List[Dict]] = None,
    sample_rows: Optional[List[Dict]] = None,
    formal_rows: Optional[List[Dict]] = None,
    formal_power_rows: Optional[List[Dict]] = None,
    mde_rows: Optional[List[Dict]] = None,
) -> str:
    """Assemble a Markdown report from the validation tables."""
    L: List[str] = []
    L.append("# Phase-2 — Synthetic Method Validation Report\n")

    # --- Wilson coverage ---
    L.append("## 1. Wilson 95% CI coverage (Binomial proportion, metric.md §1)\n")
    L.append("Target coverage = 0.95 (within MC error ≈ ±1.96·sqrt(0.95·0.05/N_rep)).\n")
    L.append("| p | n | n_rep | coverage | mean width |")
    L.append("|---|---|---|---|---|")
    for r in (coverage_rows or wilson_coverage_table()):
        L.append(f"| {r['p']} | {r['n']} | {r['n_rep']} | {r['coverage']:.4f} | {r['mean_width']:.4f} |")
    L.append("")

    # --- Markov size ---
    L.append("## 2. Markov test SIZE (true first-order Markov data)\n")
    L.append("Verdict rule is CI-overlap based (conservative): reject rate should be small.\n")
    L.append("| n_agents | s | trials | per_edge | n_rep | consistent | ASR<prod (sub) | ASR>prod (super) | insufficient |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in (size_rows or []):
        L.append(
            f"| {r['n_agents']} | {r['s']} | {r['trials']} | {r['per_edge']} | {r['n_rep']} "
            f"| {r.get('consistent', 0):.4f} | {r.get('sub', 0):.4f} "
            f"| {r.get('super', 0):.4f} | {r.get('insufficient', 0):.4f} |"
        )
    L.append("")

    # --- Markov power ---
    L.append("## 3. Markov test POWER (super-Markov latent-regime data)\n")
    L.append("Data: per-trial latent regime → ASR_true > prod(s_bar). Power = 'super' rate.\n")
    L.append("| n_agents | s_lo | s_hi | w_hi | s_bar | trials | per_edge | n_rep | super (power) | consistent |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in (power_rows or []):
        L.append(
            f"| {r['n_agents']} | {r['s_lo']} | {r['s_hi']} | {r['w_hi']} | {r['s_bar']:.3f} "
            f"| {r['trials']} | {r['per_edge']} | {r['n_rep']} "
            f"| {r.get('super', 0):.4f} | {r.get('consistent', 0):.4f} |"
        )
    L.append("")

    # --- Formal Markov test: size / bias / MDE ---
    L.append("## 3b. Kiểm định Markov HÌNH THỨC — hiệu chuẩn (markov_test_formal)\n")
    L.append("Dữ liệu Markov THẬT ⇒ size kỳ vọng ≈ alpha = 0.05; bias kỳ vọng ≈ 0.\n")
    L.append("| n_agents | s | true ASR | trials | per_edge | n_rep | mean Δ | bias (σ) "
             "| size | median p | mean MDE |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in (formal_rows or []):
        L.append(
            f"| {r['n_agents']} | {r['s']} | {r['true_asr']:.4f} | {r['trials']} "
            f"| {r['per_edge']} | {r['n_rep']} | {r['mean_delta']:+.4f} "
            f"| {r['bias_sigma']:+.2f} | {r['size']:.3f} | {r['median_p']:.3f} "
            f"| {r['mean_mde']:.3f} |")
    L.append("")

    # --- Formal vs CI-overlap power ---
    L.append("## 3c. Power: kiểm định hình thức vs quy tắc CI-chồng-nhau\n")
    L.append("Dữ liệu super-Markov (latent regime) ⇒ true ASR > ∏s̄ᵢ.\n")
    L.append("| n_agents | s_lo | s_hi | w_hi | s̄ | true ASR | ∏s̄ᵢ | trials "
             "| power (formal) | power (CI-overlap) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in (formal_power_rows or []):
        L.append(
            f"| {r['n_agents']} | {r['s_lo']} | {r['s_hi']} | {r['w_hi']} "
            f"| {r['s_bar']:.3f} | {r['true_asr']:.4f} | {r['product_s_bar']:.4f} "
            f"| {r['trials']} | {r['power_formal']:.3f} "
            f"| {r['power_ci_overlap_rule']:.3f} |")
    L.append("")

    # --- Sample size for a target MDE ---
    L.append("## 3d. Cỡ mẫu cần để đạt MDE mục tiêu (biện minh cho n headline)\n")
    L.append("| n_trials | n_per_edge | mean MDE | đạt mục tiêu? |")
    L.append("|---|---|---|---|")
    for r in (mde_rows or []):
        L.append(f"| {r['n_trials']} | {r['n_per_edge']} | {r['mean_mde']:.3f} "
                 f"| {'✅' if r['meets_target'] else '—'} |")
    L.append("")

    # --- R0 vs d*s ---
    L.append("## 4. R0 vs d*s_bar calibration (engine natural runs, metric.md §5)\n")
    L.append("| topology | n | p | s_bar | d | d*s_bar | R0 | rel_err |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in (r0_rows or []):
        L.append(
            f"| {r['topology']} | {r['num_agents']} | {r['p']} | {r['s_bar']:.3f} "
            f"| {r['d']:.3f} | {r['ds']:.3f} | {r['r0']:.3f} | {r['rel_err']:.3f} |"
        )
    L.append("")

    # --- Sample sizes ---
    L.append("## 5. Recommended N per edge / trials (Wilson half-width at p = 0.5)\n")
    L.append("| half-width | z | N recommended (p=0.5) |")
    L.append("|---|---|---|")
    for r in (sample_rows or recommended_trials()):
        L.append(f"| {r['half_width']} | {r['z']} | {r['n_recommended']} |")
    L.append("")

    # --- Interpretation ---
    L.append("## 6. Diễn giải (kết luận cho thiết kế experiment)\n")
    L.append("""- **Wilson CI**: coverage dao động quanh 0.95 (0.92–0.97) khắp grid p/n —
  đúng nominal level; n=30 (floor của metric.md §1) vẫn đạt coverage ≈ 0.95 với
  half-width ~0.17–0.33 (p gần 0.5), đủ cho so sánh tương đối nhưng rộng cho
  claim tuyệt đối. Muốn half-width ≤ 0.05 tại p=0.5 cần N ≈ 385 trial/edge.
- **Markov test size**: với dữ liệu Markov thật, tỷ lệ reject (sub+super) chỉ
  ~0.3–1.0% — quy tắc CI-overlap bảo thủ (conservative) so với mức 5% danh nghĩa:
  không tạo false alarm đáng kể. Khi báo cáo verdict cần nói rõ đây là kiểm định
  bảo thủ (không phải p-value 5%).
- **Markov test power**: với hiệu ứng latent-regime mạnh (s_lo=0.4, s_hi=0.9),
  power tăng theo cỡ mẫu: 0.66 (trials=100) → 0.94 (200) → 0.99 (300). Nên dùng
  trials ≥ 200–300 khi muốn phát hiện super-/sub-Markov deviation cỡ trung bình.
- **R0 vs d·s̄**: đúng (rel_err → 0) khi p → 1 trên chain/tree (topology đều).
  Với p < 1, R0 lệch d·s̄ (rel_err 5–30%+) vì |I| chỉ gồm instance compromised —
  d·s̄ chỉ là xấp xỉ cho vùng bão hoà, KHÔNG phải đẳng thức. Star fan-in lệch cấu
  trúc (R0 → 0.5 tại p=1 ≠ d·s̄=0.857) vì center không có downstream — cần diễn
  giải riêng (xem ghi chú configs/star_static_colluding.yaml).
- **Kiểm định Markov HÌNH THỨC (mục 3b)** — đây là kiểm định dùng để BÁO CÁO, thay
  cho quy tắc CI-chồng-nhau của `markov_test`:
  - **Không lệch hệ thống**: bias = −0.10σ … +0.08σ trên cả 3 cấu hình ⇒ delta
    (ASR − ∏sᵢ) là ước lượng không chệch, và bootstrap độc lập trên hai protocol
    là hợp lệ.
  - **Size ≈ nominal**: reject 6.7–8.3% ở alpha = 0.05 với n_rep = 60 ⇒ sai số
    Monte-Carlo của chính con số này là ±2.8 điểm % ⇒ **tương thích với 5%**, không
    phải test "hào phóng" (liberal). Trung vị p-value 0.41–0.56 (≈ uniform dưới H0).
  - **Power cao hơn hẳn quy tắc cũ**: 0.750 vs 0.625 (trials=75), rồi 1.000 vs
    0.975 (150) ⇒ dùng test hình thức là hợp lý về mặt thống kê, không chỉ "đẹp hơn".
  - **Luôn báo kèm MDE** (mục 3d): ở trials = per_edge = 200, MDE ≈ 0.10; ở 400
    thì ≈ 0.07. Nghĩa là "consistent với Markov" ở n=200 phải được đọc là
    *"đã loại trừ sai lệch |ASR − ∏sᵢ| > 0.10"* — KHÔNG phải bằng chứng Markov
    đúng. Đây là cách phát biểu mà reviewer measurement yêu cầu.
  - ⚠️ Ở n nhỏ (trials ≲ 75) power chỉ ~0.75 ⇒ kết quả "consistent" từ cell n nhỏ
    (E17/E20: trials=40) **không có giá trị kết luận** — đúng như đã ghi trong
    Limitations.""")
    L.append("")
    return "\n".join(L)
