"""Phase-2 validation tests: estimators behave correctly under known ground truth.

Expectations (docs/metric.md):
- §1  Wilson 95% CI covers the true Binomial proportion in ~95% of replications.
- §2  markov_test rarely rejects true first-order Markov data (size small) and
      rejects super-Markov latent-regime data with growing probability (power).
- §5  empirical R0 ≈ d * s_bar on regular topologies (chain/tree) as p → 1;
      star fan-in deviates structurally (center has no downstream) — documented.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import TopologyType
from contagion.metrics.epidemiology import attack_success_rate, markov_test
from contagion.metrics.validation import (
    _chain_edges,
    markov_paths,
    markov_power,
    markov_size,
    r0_calibration_row,
    supermarkov_paths,
    synthetic_edge_trials,
    wilson_coverage,
)


# ---------------------------------------------------------------------------
# 1. Wilson CI coverage
# ---------------------------------------------------------------------------

def test_wilson_coverage_nominal_over_operating_points():
    """Coverage ≈ 0.95 (within MC error) over the benchmark's p/n grid."""
    for p, n in ((0.1, 30), (0.5, 30), (0.9, 30), (0.1, 100), (0.5, 100), (0.5, 300)):
        r = wilson_coverage(p, n, n_rep=1500, seed=3)
        # MC std of coverage ~ sqrt(0.95*0.05/1500) ~ 0.0056 -> 4σ = 0.022
        assert 0.90 <= r["coverage"] <= 0.99, (p, n, r["coverage"])
        assert 0.0 < r["mean_width"] < 1.0


def test_wilson_coverage_edge_proportions():
    r = wilson_coverage(0.05, 100, n_rep=1000, seed=5)
    assert 0.88 <= r["coverage"] <= 1.0
    r2 = wilson_coverage(0.95, 100, n_rep=1000, seed=6)
    assert 0.88 <= r2["coverage"] <= 1.0


# ---------------------------------------------------------------------------
# 2. Markov test: size & power
# ---------------------------------------------------------------------------

def test_markov_data_asr_matches_product():
    """markov_paths: sample ASR ≈ s^(n-1) (product model ground truth)."""
    n, s, trials = 5, 0.6, 4000
    paths = markov_paths(n, s, trials, seed=11)
    asr = attack_success_rate(paths)
    assert abs(asr.mean - s ** (n - 1)) < 0.03


def test_supermarkov_asr_exceeds_product_marginal():
    """supermarkov_paths: true ASR > prod(s_bar) by Jensen (k >= 2)."""
    n, s_lo, s_hi, w_hi, trials = 5, 0.4, 0.9, 0.5, 8000
    s_bar = w_hi * s_hi + (1 - w_hi) * s_lo
    paths = supermarkov_paths(n, s_lo, s_hi, w_hi, trials, seed=13)
    asr = attack_success_rate(paths)
    prod = s_bar ** (n - 1)
    expected = w_hi * s_hi ** (n - 1) + (1 - w_hi) * s_lo ** (n - 1)
    assert abs(asr.mean - expected) < 0.03       # matches analytic ASR_true
    assert asr.mean > prod + 0.05                # super-Markov gap materializes


def test_markov_size_low():
    """True Markov data: markov_test rejects only rarely (conservative rule)."""
    r = markov_size(5, 0.6, trials=80, per_edge=80, n_rep=80, seed=17)
    reject = r.get("sub", 0.0) + r.get("super", 0.0)
    assert r.get("consistent", 0.0) > 0.85
    assert reject < 0.15
    assert r.get("insufficient", 0.0) == 0.0


def test_markov_power_grows_with_data():
    """Super-Markov data: power (super rate) increases with trials/per_edge."""
    small = markov_power(5, 0.4, 0.9, 0.5, trials=60, per_edge=60,
                         n_rep=120, seed=19)
    large = markov_power(5, 0.4, 0.9, 0.5, trials=250, per_edge=200,
                         n_rep=120, seed=19)
    assert large.get("super", 0.0) > small.get("super", 0.0)
    assert large.get("super", 0.0) > 0.6


def test_markov_power_high_with_enough_data():
    """Power → 1 given a strong latent-regime gap and sufficient trials."""
    r = markov_power(5, 0.4, 0.9, 0.5, trials=300, per_edge=200,
                     n_rep=150, seed=23)
    assert r.get("super", 0.0) > 0.9
    assert r.get("consistent", 0.0) < 0.1


def test_markov_test_wiring_on_synthetic_data():
    """markov_test returns a proper dict for chain-shaped synthetic data."""
    n, s, trials, per_edge = 5, 0.6, 400, 120
    edges = _chain_edges(n)
    paths = markov_paths(n, s, trials, seed=29)
    et = synthetic_edge_trials(edges, {f"{a}->{b}": s for a, b in edges}, per_edge, seed=31)
    res = markov_test(paths, et)
    assert res is not None
    assert res["chain_edges"] == ["agent_0->agent_1", "agent_1->agent_2",
                                  "agent_2->agent_3", "agent_3->agent_4"]
    assert abs(res["product_s"] - s ** (n - 1)) < 0.05
    assert abs(res["asr"] - s ** (n - 1)) < 0.05


# ---------------------------------------------------------------------------
# 3. R0 vs d*s_bar (engine natural runs)
# ---------------------------------------------------------------------------

def test_r0_ds_chain_exact_at_p1():
    """chain, p=1: every run fully compromised -> R0 == d * s_bar exactly."""
    row = r0_calibration_row(TopologyType.CHAIN, 7, 1.0,
                             trials=150, per_edge_trials=60, seed=7)
    assert abs(row["rel_err"]) < 0.01
    assert row["r0"] == pytest.approx(row["ds"], abs=0.01)


def test_r0_ds_tree_exact_at_p1():
    """tree (root entry), p=1: full compromise -> R0 == d * s_bar."""
    row = r0_calibration_row(TopologyType.TREE, 7, 1.0,
                             trials=150, per_edge_trials=60, seed=7)
    assert abs(row["rel_err"]) < 0.01


def test_r0_ds_error_shrinks_as_p_grows_chain():
    """chain: R0 -> d*s_bar as infection probability p -> 1 (monotone trend)."""
    e_mid = r0_calibration_row(TopologyType.CHAIN, 7, 0.6,
                               trials=300, per_edge_trials=80, seed=7)["rel_err"]
    e_hi = r0_calibration_row(TopologyType.CHAIN, 7, 0.95,
                              trials=300, per_edge_trials=80, seed=7)["rel_err"]
    assert e_hi < e_mid


def test_r0_star_fan_in_structural_deviation():
    """star fan-in (leaf -> center): R0 ~ p/(1+p), NOT d*s_bar — structural."""
    row = r0_calibration_row(TopologyType.STAR, 7, 1.0,
                             trials=200, per_edge_trials=60, seed=7)
    # entry = leaf agent_1 (always compromised) + center compromised w.p. p=1:
    # compromised instances = 2 (leaf, center); leaf's Z=1 (center compromised);
    # center's Z=0 (no downstream) -> R0 = 1/2.
    assert row["r0"] == pytest.approx(0.5, abs=0.02)
    assert row["rel_err"] > 0.3  # d*s_bar (0.857) is NOT the right target here
