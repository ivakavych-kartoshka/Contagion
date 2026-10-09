"""Kiểm tra ``role_order`` trong build_graph (R2 W3/Q2).

Vì sao cần: role luôn được gán theo cùng một thứ tự trên chain, nên "survival phụ
thuộc role" bị confound với vị trí. Kiểm soát này chạy cùng một chain với thứ tự
role hoán vị; nếu ``role_order`` âm thầm bị bỏ qua thì cả phép so là vô nghĩa —
đúng lỗi đã xảy ra một lần (xem ``_graph_factory`` trong ``scripts/validation_probe.py``).

Chạy:  ``pytest tests/test_role_order.py -q``   hoặc   ``python tests/test_role_order.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.core import AgentRole, TopologyType            # noqa: E402
from contagion.topology.graph import build_graph              # noqa: E402


def roles_of(graph) -> list:
    return [graph.roles[n].value for n in graph.nodes]


def test_default_cycle_unchanged():
    g = build_graph(TopologyType.CHAIN, 4)
    assert roles_of(g) == ["planner", "worker", "reviewer", "aggregator"]


def test_default_cycle_repeats_for_n5():
    # n > 4 tất yếu lặp role (planner hai lần) — kiểm tra để tài liệu hoá hành vi
    # này, vì nó là lý do role_order phải CHO PHÉP role trùng.
    g = build_graph(TopologyType.CHAIN, 5)
    assert roles_of(g) == ["planner", "worker", "reviewer", "aggregator", "planner"]


def test_permuted_order_is_applied():
    order = ["reviewer", "worker", "planner", "aggregator", "planner"]
    g = build_graph(TopologyType.CHAIN, 5, role_order=order)
    assert roles_of(g) == order


def test_edges_unchanged_by_permutation():
    a = build_graph(TopologyType.CHAIN, 4)
    b = build_graph(TopologyType.CHAIN, 4,
                    role_order=["reviewer", "worker", "planner", "aggregator"])
    assert [(e.src, e.dst) for e in a.edges] == [(e.src, e.dst) for e in b.edges]


def test_accepts_agent_role_enum():
    g = build_graph(TopologyType.CHAIN, 3,
                    role_order=[AgentRole.REVIEWER, AgentRole.PLANNER,
                                AgentRole.WORKER])
    assert [g.roles[n] for n in g.nodes] == [AgentRole.REVIEWER, AgentRole.PLANNER,
                                             AgentRole.WORKER]


def test_duplicate_roles_allowed():
    order = ["worker", "worker", "planner", "aggregator"]
    assert roles_of(build_graph(TopologyType.CHAIN, 4, role_order=order)) == order


@pytest.mark.parametrize("bad", [
    ["worker", "planner"],                                 # sai độ dài
    ["khong-ton-tai", "planner", "worker", "reviewer"],    # role lạ
])
def test_invalid_role_order_rejected(bad):
    with pytest.raises(ValueError):
        build_graph(TopologyType.CHAIN, 4, role_order=bad)


def test_role_order_rejected_for_star_and_tree():
    with pytest.raises(ValueError):
        build_graph(TopologyType.STAR, 4,
                    role_order=["worker", "planner", "reviewer", "aggregator"])
    with pytest.raises(ValueError):
        build_graph(TopologyType.TREE, 7, role_order=["worker"] * 7)


def test_star_and_tree_unchanged_without_role_order():
    assert len(build_graph(TopologyType.STAR, 4).nodes) == 4
    assert len(build_graph(TopologyType.TREE, 7).nodes) == 7


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  OK   {fn.__name__}")
        except Exception:
            failed += 1
            print(f"  FAIL {fn.__name__}")
            traceback.print_exc()
    print("\nKET QUA:", "TAT CA PASS" if not failed else f"{failed} FAIL")
    sys.exit(1 if failed else 0)
