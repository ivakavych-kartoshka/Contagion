"""The theoretical core of Contagion.

Implements the epidemiological quantities from the proposal:

    s      per-hop injection survival rate
    P_E2E  end-to-end propagation probability (chain)
    R0     reproduction number (branching-process, used for branching topologies)

All quantities are reported with variance (never bare point estimates), because
LLM stochasticity and context/memory effects are expected to break the
Markovian survival assumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


@dataclass
class HopOutcome:
    """A single observed sender-receiver hop (one Bernoulli trial for s)."""
    src: str
    dst: str
    step: int
    src_compromised: bool
    dst_compromised: bool
    payload_present: bool = False
    defense_detected: bool = False


@dataclass
class PropagationPath:
    """A single run's compromise status across all agents."""
    trial_id: int
    compromised: Dict[str, bool] = field(default_factory=dict)
    hops: List[HopOutcome] = field(default_factory=list)
    time_to_compromise: Optional[int] = None
    hops_to_compromise: Optional[int] = None


@dataclass
class SummaryStats:
    mean: float
    std: float
    count: int
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"mu={self.mean:.4f} (±{self.std:.4f}, n={self.count}"
            + (f", 95% CI [{self.ci_low:.4f},{self.ci_high:.4f}]" if self.ci_low is not None else "")
            + ")"
        )


def _ci(proportions: np.ndarray, z: float = 1.96) -> SummaryStats:
    mean = float(np.mean(proportions))
    std = float(np.std(proportions, ddof=1)) if len(proportions) > 1 else 0.0
    n = len(proportions)
    low, high = None, None
    if n > 1:
        se = std / np.sqrt(n)
        low, high = mean - z * se, mean + z * se
    return SummaryStats(mean, std, n, low, high)


def per_hop_survival(paths: List[PropagationPath]) -> Dict[str, SummaryStats]:
    """Estimate s per (src, dst) edge and overall.

    s = P(dst compromised | src compromised), estimated only over hops where the
    source was already compromised (this is the survival conditioning).
    """
    per_edge: Dict[str, List[int]] = {}
    for path in paths:
        for hop in path.hops:
            if hop.src_compromised:
                key = f"{hop.src}->{hop.dst}"
                per_edge.setdefault(key, []).append(1 if hop.dst_compromised else 0)

    result: Dict[str, SummaryStats] = {}
    for key, vals in per_edge.items():
        result[key] = _ci(np.asarray(vals, dtype=float))
    # Overall (pooled) survival.
    all_vals = [v for k in per_edge for v in per_edge[k]]
    if all_vals:
        result["overall"] = _ci(np.asarray(all_vals, dtype=float))
    return result


def end_to_end_propagation(paths: List[PropagationPath]) -> SummaryStats:
    """Chain E2E: probability the compromise reaches the last agent.

    Estimates P(end compromised | entry compromised) over trials, matching the
    chain product P_E2E = prod s_i; the ratio of per-trial e2e successes also
    serves as the empirical analog.
    """
    vals = []
    for path in paths:
        # Compare entry vs last-actor compromise per trial.
        nodes = list(path.compromised.keys())
        if not nodes:
            continue
        entry_c = path.compromised.get(nodes[0], False)
        last_c = path.compromised.get(nodes[-1], False)
        # Only trials conditioned on entry compromise contribute.
        if entry_c:
            vals.append(1 if last_c else 0)
    return _ci(np.asarray(vals, dtype=float)) if vals else SummaryStats(0.0, 0.0, 0)


def reproduction_number(paths: List[PropagationPath], topology_hint: str = "chain") -> SummaryStats:
    """Estimate R0 = E[# new compromises per compromised agent].

    Computed per trial as (number of *newly* compromised agents) / (number of
    compromised agents that acted as senders). Pooled across trials. For
    branching topologies this is the branching factor; for a pure chain R0 ∈ [0,1].
    The ATTACKER pseudo-node is excluded from the sender set (it is not an agent).
    """
    ratios: List[float] = []
    for path in paths:
        # Only true agents are counted as potential senders (exclude ATTACKER).
        agents = set(path.compromised.keys())
        senders = {h.src for h in path.hops if h.src_compromised} & agents
        if not senders:
            continue
        total_comp = sum(1 for c in path.compromised.values() if c)
        per_agent = max(0.0, (total_comp - 1) / len(senders))
        ratios.append(per_agent)
    return _ci(np.asarray(ratios, dtype=float)) if ratios else SummaryStats(0.0, 0.0, 0)


def propagation_rate(paths: List[PropagationPath]) -> SummaryStats:
    """Fraction of all agents (excluding entry) compromised at end of run."""
    vals = []
    for path in paths:
        nodes = list(path.compromised.keys())
        if len(nodes) < 2:
            continue
        comp = sum(1 for a, c in path.compromised.items() if c)
        nodes = list(path.compromised.keys())
        # Exclude entry agent count.
        rate = max(0.0, (comp - 1) / max(1, len(nodes) - 1))
        vals.append(rate)
    return _ci(np.asarray(vals, dtype=float)) if vals else SummaryStats(0.0, 0.0, 0)
