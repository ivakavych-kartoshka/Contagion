"""Tests for the Contagion framework using the deterministic mock backend.

Expectations follow docs/metric.md:
- §1  per-hop survival s is measured by the CONTROLLED per-edge protocol
      (force C_src = 1, judge the receiver with the ASV/MR threshold rule).
- §2  end-to-end ASR is measured on independent natural runs, entry
      compromised by construction (C_0 = 1), every trial counted.
- §5  R0_hat = mean over compromised instances of Z_i (# downstream neighbors
      compromised within one hop); report alongside d * s_bar as a consistency
      check. For a fully-compromised chain of n agents: R0_hat = (n-1)/n
      (= avg out-degree d of the chain when s_bar = 1).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import (
    AttackStrategy,
    ContagionConfig,
    DefenseType,
    TopologyType,
)
from contagion.benchmark.runner import run_benchmark
from contagion.metrics.epidemiology import (
    attack_success_rate,
    controlled_per_edge_survival,
    propagation_rate,
    reproduction_number,
)
from contagion.topology.graph import build_graph


def test_build_chain():
    g = build_graph(TopologyType.CHAIN, 5)
    assert len(g.nodes) == 5
    assert len(g.edges) == 4
    assert g.successors("agent_0") == ["agent_1"]


def test_build_star():
    g = build_graph(TopologyType.STAR, 7)
    assert len(g.nodes) == 7
    # 6 leaves fan into the aggregator.
    assert all(e.dst == "agent_0" for e in g.edges)
    assert len(g.edges) == 6


def test_build_tree():
    g = build_graph(TopologyType.TREE, 7)
    assert len(g.nodes) == 7
    assert len(g.edges) == 6


def test_full_chain_run_mock():
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=10,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    paths = result["paths"]
    edge_trials = result["edge_trials"]
    assert len(paths) == 10

    # metric.md §1: per-edge s measured by the CONTROLLED protocol. Naive mock
    # with infection_prob=1.0 always relays the marker → s = 1.0.
    surv = controlled_per_edge_survival(edge_trials)
    assert surv["overall"].mean == 1.0
    # Every edge of the chain is measured by the protocol.
    assert {k for k in surv if k != "overall"} == {
        "agent_0->agent_1", "agent_1->agent_2", "agent_2->agent_3", "agent_3->agent_4",
    }

    # metric.md §2: ASR measured end-to-end; entry compromised by construction.
    asr = attack_success_rate(paths)
    assert asr.mean == 1.0

    # metric.md §5: fully compromised chain of n=5 → R0_hat = (n-1)/n = 0.8,
    # matching d * s_bar (d = avg out-degree 4/5, s_bar = 1).
    r0 = reproduction_number(paths)
    assert r0.mean == pytest.approx(0.8)

    pr = propagation_rate(paths)
    assert pr.mean == 1.0


def test_mock_infection_prob_controls_per_hop_s():
    """metric.md §1: controlled per-edge survival tracks the mock Bernoulli p."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=3,
        trials=10,
        per_edge_trials=200,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        extra={"mock_infection_prob": 0.7},
    )
    result = run_benchmark(config)
    surv = controlled_per_edge_survival(result["edge_trials"])
    # Two edges in a 3-agent chain; each ≈ 0.7 within MC noise.
    assert surv["agent_0->agent_1"].mean == pytest.approx(0.7, abs=0.15)
    assert surv["agent_1->agent_2"].mean == pytest.approx(0.7, abs=0.15)
    assert surv["overall"].mean == pytest.approx(0.7, abs=0.15)


def test_e2e_asr_consistent_with_controlled_product():
    """metric.md §2 relationship: ASR (e2e) ~= prod of controlled per-hop s."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=4,
        trials=200,
        per_edge_trials=200,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        extra={"mock_infection_prob": 0.7},
    )
    result = run_benchmark(config)
    surv = controlled_per_edge_survival(result["edge_trials"])
    s_edges = [surv["agent_0->agent_1"].mean,
               surv["agent_1->agent_2"].mean,
               surv["agent_2->agent_3"].mean]
    prod = s_edges[0] * s_edges[1] * s_edges[2]
    asr = attack_success_rate(result["paths"])
    assert asr.mean == pytest.approx(prod, abs=0.15)


def test_delimiter_defense_blocks():
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=10,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.DELIMITER,
        model_id="mock",
        seed=0,
    )
    # Delimiter wrapping does not remove the marker, so naive mock still relays.
    result = run_benchmark(config)
    assert controlled_per_edge_survival(result["edge_trials"])["overall"].mean == 1.0


def test_paraphrase_defense_reduces_survival():
    """ParaphraseDefense strips the marker from the untrusted content → s → 0."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=10,
        per_edge_trials=50,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.PARAPHRASE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    surv = controlled_per_edge_survival(result["edge_trials"])
    assert surv["overall"].mean == 0.0


def test_summarize_shape():
    config = ContagionConfig(trials=5, seed=0)
    result = run_benchmark(config)
    m = result["metrics"]
    assert set(m) >= {"survival", "asr", "r0", "propagation_rate", "n_trials"}
    assert m["n_trials"] == 5
    assert "overall" in m["survival"]
