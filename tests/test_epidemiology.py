"""Smoke tests for the Contagion framework using the deterministic mock backend."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import (
    AttackStrategy,
    ContagionConfig,
    DefenseType,
    FieldContentFreedom,
    ReInjectionMode,
    TopologyType,
)
from contagion.benchmark.runner import run_benchmark, summarize
from contagion.metrics.epidemiology import (
    end_to_end_propagation,
    per_hop_survival,
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
    assert len(paths) == 10

    s = per_hop_survival(paths)
    assert "overall" in s
    # Naive mock always relays the marker.
    assert s["overall"].mean == 1.0

    e2e = end_to_end_propagation(paths)
    assert e2e.mean == 1.0

    r0 = reproduction_number(paths)
    assert r0.mean == 1.0

    pr = propagation_rate(paths)
    assert pr.mean == 1.0


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
    assert per_hop_survival(result["paths"])["overall"].mean == 1.0
