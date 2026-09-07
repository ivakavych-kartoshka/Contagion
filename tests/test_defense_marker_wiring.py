"""Regression test: defense phải nhận marker THẬT từ config (bug đã sửa).

Trước fix: engine gọi ``build_defense(config.defense)`` không truyền marker →
ParaphraseDefense/DelimiterDefense/... giữ default "INJECTED_PAYLOAD" và trở
thành NO-OP khi config dùng marker khác (vd LEAK-TOKEN-X) → mọi thí nghiệm
defense trên LLM thật (marker custom) vô tình đo "no defense".
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.benchmark.runner import run_benchmark
from contagion.core import ContagionConfig, DefenseType, TopologyType
from contagion.defenses.mechanisms import (
    DelimiterDefense,
    DetectionDefense,
    HopIsolationDefense,
    ParaphraseDefense,
    build_defense,
)


def test_paraphrase_defense_gets_custom_marker():
    """ParaphraseDefense dựng qua build_defense nhận marker từ kwargs."""
    d = build_defense(DefenseType.PARAPHRASE, marker="LEAK-TOKEN-42")
    assert isinstance(d, ParaphraseDefense)
    assert d.marker == "LEAK-TOKEN-42"
    safe, detected = d.sanitize("The code is LEAK-TOKEN-42 here.")
    assert detected is True
    assert "LEAK-TOKEN-42" not in safe  # paraphrase strip marker thật


def test_all_defenses_accept_marker_kwarg():
    for typ in (DefenseType.PARAPHRASE, DefenseType.DELIMITER,
                DefenseType.DETECTION, DefenseType.HOP_ISOLATION):
        d = build_defense(typ, marker="SECRET-99")
        assert d.marker == "SECRET-99", typ
    # NONE không nhận marker nhưng registry bỏ qua kwarg an toàn.
    d0 = build_defense(DefenseType.NONE, marker="whatever")
    assert d0.sanitize("anything") == ("anything", False)


def test_paraphrase_defense_active_with_custom_marker_mock():
    """Với marker custom: paraphrase thực sự strip marker → survival ~0.

    Nếu defense NO-OP (bug cũ), survival sẽ ~1.0 vì mock relay giữ marker.
    """
    cfg = ContagionConfig(
        topology=TopologyType.CHAIN,
        num_agents=3,
        trials=5,
        per_edge_trials=15,
        defense=DefenseType.PARAPHRASE,
        marker="LEAK-TOKEN-42",
        seed=11,
        extra={"mock_infection_prob": 1.0},
    )
    res = run_benchmark(cfg)
    surv = res["metrics"]["survival"]["overall"]["mean"]
    asr = res["metrics"]["asr"]["mean"]
    # Paraphrase strip marker ở dst → relay không còn marker → survival thấp.
    assert surv < 0.5, f"paraphrase phải giảm survival, got {surv}"
    # Contrast: cùng marker custom + defense NONE → survival = 1.0.
    cfg_none = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=3, trials=5, per_edge_trials=15,
        defense=DefenseType.NONE, marker="LEAK-TOKEN-42", seed=11,
        extra={"mock_infection_prob": 1.0},
    )
    surv_none = run_benchmark(cfg_none)["metrics"]["survival"]["overall"]["mean"]
    assert surv_none == pytest.approx(1.0)
