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
    assert set(m) >= {"survival", "asr", "r0", "propagation_rate", "n_trials",
                      "hops_to_compromise", "markov_check"}
    assert m["n_trials"] == 5
    assert "overall" in m["survival"]


# --- Group B: Wilson CI, Markov check, hops-to-compromise ---

def test_wilson_ci_bounds():
    """metric.md §1: s CI là Wilson (0..1), không phải normal approximation."""
    from contagion.metrics.epidemiology import _binom_summary, _wilson_bounds

    # Edge case: 0/N và N/N → CI không vượt ra ngoài [0, 1].
    lo, hi = _wilson_bounds(0, 30)
    assert lo >= 0.0 and hi >= 0.0 and hi > 0
    lo, hi = _wilson_bounds(30, 30)
    assert lo <= 1.0 and hi <= 1.0 and lo < 1.0

    # k=15/N=30 → Wilson khác normal approx (Wald) ở giữa nhị thức.
    w = _binom_summary([0, 1] * 15)
    assert w.count == 30
    assert w.mean == pytest.approx(0.5)
    assert w.ci_low is not None and w.ci_high is not None
    assert 0.0 <= w.ci_low <= w.ci_high <= 1.0


def test_survival_ci_is_wilson():
    """CI của controlled per-edge s nằm trong [0,1] và bao quanh p."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=3,
        trials=10,
        per_edge_trials=200,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        extra={"mock_infection_prob": 0.5},
    )
    result = run_benchmark(config)
    surv = controlled_per_edge_survival(result["edge_trials"])
    for key, st in surv.items():
        assert st.ci_low is not None and st.ci_high is not None
        assert 0.0 <= st.ci_low <= st.ci_high <= 1.0
        # mean nằm trong khoảng CI (Wilson luôn bao quanh point estimate).
        assert st.ci_low <= st.mean <= st.ci_high


def test_markov_check_reports_consistent_for_chain():
    """metric.md §2: chain với mock đồng nhất → ASR ≈ ∏ŝ → verdict consistent."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=4,
        trials=200,
        per_edge_trials=200,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=1,
        extra={"mock_infection_prob": 0.6},
    )
    result = run_benchmark(config)
    mc = result["metrics"]["markov_check"]
    assert mc is not None
    assert mc["chain_edges"] == ["agent_0->agent_1", "agent_1->agent_2", "agent_2->agent_3"]
    # ASR empirical ≈ product của controlled per-edge ŝ.
    assert mc["asr"] == pytest.approx(mc["product_s"], abs=0.2)
    assert "consistent" in mc["verdict"] or "reinforcement" in mc["verdict"] \
        or "attenuation" in mc["verdict"]


def test_markov_check_returns_none_for_star():
    """metric.md §2: không-chain (star) → không có product hợp lệ → None."""
    config = ContagionConfig(
        topology=TopologyType.STAR,
        num_agents=5,
        trials=20,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        entry_agent="agent_1",
    )
    result = run_benchmark(config)
    mc = result["metrics"]["markov_check"]
    assert mc is None


def test_hops_to_compromise_chain():
    """metric.md §6: chain n=5 mock p=1 → target compromised ở round 4, không censored."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=20,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    htc = result["metrics"]["hops_to_compromise"]
    # Naive mock luôn relay → agent_4 compromised đúng round 4 (sau 4 hops).
    assert htc["mean"] == pytest.approx(4.0)
    assert htc["median"] == 4.0
    assert htc["censored_rate"] == 0.0
    assert htc["n_total"] == 20
    # PropagationPath lưu round compromised ĐẦU TIÊN (bất kỳ agent) = 1
    # (agent_1 compromised ở round 1). Metric target-specific (§6) nằm ở trên.
    p = result["paths"][0]
    assert p.hops_to_compromise == 1


def test_hops_to_compromise_censored_with_low_p():
    """metric.md §6: p nhỏ → nhiều trial target không bao giờ bị compromise (censored)."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=50,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        extra={"mock_infection_prob": 0.1},
    )
    result = run_benchmark(config)
    htc = result["metrics"]["hops_to_compromise"]
    assert htc["censored_rate"] > 0.5  # p^4 = 0.0001 → gần như luôn censored


# --- Group C: Utility Under Attack (§7) + cross-metric logging ---

def test_utility_clean_no_attack():
    """metric.md §7: pipeline sạch (không attack) → U_clean = 1."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=20,
        measure_utility=True,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    ut = result["metrics"]["utility"]
    assert ut["u_clean"] == pytest.approx(1.0)
    assert ut["n_clean"] == 20 and ut["n_attack"] == 20
    assert ut["task"] == "clean_answer"


def test_utility_attack_reduces_utility_nodefense():
    """metric.md §7: không defense, mock p=1 → attack làm hỏng final output."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=20,
        measure_utility=True,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
        extra={"mock_infection_prob": 1.0},
    )
    result = run_benchmark(config)
    ut = result["metrics"]["utility"]
    assert ut["u_clean"] == pytest.approx(1.0)
    assert ut["u_attack"] < 0.5          # entry compromised → payload lan khắp chain
    assert ut["delta_u"] > 0.0
    assert ut["retention"] is not None and ut["retention"] < 0.5


def test_utility_retention_with_paraphrase_defense():
    """metric.md §7: paraphrase (strip marker) giữ final output sạch → retention cao."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=20,
        measure_utility=True,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.PARAPHRASE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    ut = result["metrics"]["utility"]
    assert ut["u_clean"] == pytest.approx(1.0)
    # Paraphrase strip marker tại hop đầu → downstream không bị nhiễm → final sạch.
    assert ut["u_attack"] > 0.9
    assert ut["retention"] is not None and ut["retention"] > 0.9


def test_agent_logs_collected():
    """Cross-metric logging: mỗi agent-instance có role/input/output/asv/mr/mt/C."""
    config = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=5,
        trials=3,
        measure_utility=True,
        attack=AttackStrategy.STATIC,
        defense=DefenseType.NONE,
        model_id="mock",
        seed=0,
    )
    result = run_benchmark(config)
    # Propagation paths có agent_logs.
    p = result["paths"][0]
    assert len(p.agent_logs) >= 1
    first = p.agent_logs[0]
    assert first.agent_id == "agent_0"
    assert first.role  # role non-empty
    assert first.inputs   # provenance
    assert first.output   # full output text
    # Utility run cũng có agent_logs + final_output.
    ut = result["utility"]
    assert len(ut["clean_paths"]) == 3 and len(ut["attack_paths"]) == 3
    assert ut["clean_paths"][0].final_output is not None
    assert all(a.role for a in ut["attack_paths"][0].agent_logs)
