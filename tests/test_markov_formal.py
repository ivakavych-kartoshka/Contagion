"""Tests: kiểm định Markov HÌNH THỨC (markov_test_formal) + MDE.

Vì sao cần: ``markov_test`` chỉ hỏi "hai CI 95% có chồng nhau không" — thô, bảo
thủ, không có p-value và không cho biết cỡ mẫu hiện tại đủ bác bỏ sai lệch lớn
cỡ nào. Với paper measurement, "consistent" mà không kèm MDE là phát biểu rỗng.

Bốn tính chất được khoá lại ở đây:
1. **Size** — dữ liệu Markov THẬT ⇒ tỷ lệ bác bỏ ≈ alpha (không false alarm).
2. **Power** — dữ liệu super-Markov (latent regime) ⇒ bác bỏ tăng theo n, và
   **mạnh hơn** quy tắc CI-overlap của ``markov_test``.
3. **MDE giảm theo n** (nhiều trial hơn ⇒ phát hiện được sai lệch nhỏ hơn).
4. **Biên** — ASR = ∏sᵢ = 1 ⇒ không bác bỏ, delta = 0 (không có verdict
   "attenuation" giả do artifact số thực).

Toàn bộ chạy trên dữ liệu tổng hợp có ground truth biết trước (validation.py),
offline, deterministic theo seed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.metrics.epidemiology import markov_test, markov_test_formal
from contagion.metrics.validation import (
    _chain_edges,
    markov_paths,
    supermarkov_paths,
    synthetic_edge_trials,
)


def _dataset(n_agents, s, trials, per_edge, seed=0):
    edges = _chain_edges(n_agents)
    s_map = {f"{a}->{b}": s for a, b in edges}
    return (markov_paths(n_agents, s, trials, seed=seed),
            synthetic_edge_trials(edges, s_map, per_edge, seed=seed + 1))


def test_formal_detects_true_markov_as_consistent():
    """Dữ liệu Markov thật ⇒ delta nhỏ và nằm trong MDE.

    LƯU Ý THỐNG KÊ (đã kiểm chứng bằng ``scripts/validate_methods.py`` mục 3b):
    đây là tính chất **xác suất**, KHÔNG được assert verdict tại MỘT seed — với
    alpha=0.05 thì ~5% replicate Markov thật sẽ bị bác bỏ một cách hợp lệ (đã
    gặp đúng trường hợp này ở seed=11, delta ≈ 2.3σ). Vì vậy:
      - test này chỉ kiểm tra cấu trúc + độ lớn (|delta| ≤ MDE),
      - tỷ lệ bác bỏ được kiểm ở :func:`test_formal_size_is_close_to_nominal`
        và ở mục 3b của validation report (bias +0.06σ, size 0.033 @ nominal 0.05).
    """
    paths, et = _dataset(5, 0.7, 400, 400, seed=11)
    res = markov_test_formal(paths, et, seed=1)
    assert res is not None
    assert abs(res["delta"]) < 0.08, res
    assert abs(res["delta"]) <= res["mde"] + 1e-12, res
    assert res["p_value"] > 0.001          # không được là bằng chứng cực mạnh
    assert res["n_trials"] == 400


def test_formal_size_is_close_to_nominal():
    """Size: trên nhiều replicate Markov thật, tỷ lệ reject nên ~< 0.10 (alpha=0.05)."""
    rejects = 0
    reps = 40
    for r in range(reps):
        paths, et = _dataset(5, 0.6, 120, 120, seed=1000 + r)
        res = markov_test_formal(paths, et, seed=r, n_boot=600)
        if res is not None and res["verdict"].startswith("reject"):
            rejects += 1
    assert rejects / reps <= 0.15, f"size quá cao: {rejects}/{reps}"


def test_formal_majority_consistent_over_many_seeds():
    """Trên nhiều replicate Markov thật, ĐA SỐ phải "consistent" (kiểm theo tỷ lệ,
    không theo 1 seed — xem docstring test đầu)."""
    consistent = 0
    reps = 20
    for r in range(reps):
        paths, et = _dataset(5, 0.7, 200, 200, seed=4000 + r)
        res = markov_test_formal(paths, et, seed=r, n_boot=600)
        assert res is not None
        if res["verdict"].startswith("consistent"):
            consistent += 1
    assert consistent / reps >= 0.80, f"chỉ {consistent}/{reps} consistent"


def test_formal_power_beats_ci_overlap_rule():
    """Super-Markov: test hình thức phải mạnh hơn hẳn quy tắc CI-chồng-nhau."""
    formal_rej = 0
    rough_rej = 0
    reps = 30
    for r in range(reps):
        edges = _chain_edges(5)
        paths = supermarkov_paths(5, 0.35, 0.9, 0.5, 150, seed=2000 + r)
        s_bar = 0.5 * 0.9 + 0.5 * 0.35
        et = synthetic_edge_trials(edges, {f"{a}->{b}": s_bar for a, b in edges},
                                   150, seed=3000 + r)
        f = markov_test_formal(paths, et, seed=r, n_boot=600)
        assert f is not None
        if f["verdict"].startswith("reject"):
            formal_rej += 1
        rough = markov_test(paths, et)
        if rough is not None and rough["verdict"].startswith("ASR >"):
            rough_rej += 1
    assert formal_rej / reps >= 0.8, f"power thấp: {formal_rej}/{reps}"
    assert formal_rej >= rough_rej, (formal_rej, rough_rej)


def test_mde_shrinks_with_sample_size():
    """MDE (sai lệch nhỏ nhất phát hiện được) phải giảm khi n tăng."""
    mdes = []
    for trials in (60, 240, 960):
        paths, et = _dataset(5, 0.6, trials, trials, seed=77)
        res = markov_test_formal(paths, et, seed=5, n_boot=800)
        assert res is not None
        mdes.append(res["mde"])
    assert mdes[0] > mdes[1] > mdes[2], mdes


def test_formal_boundary_no_spurious_attenuation():
    """ASR = ∏sᵢ = 1: delta = 0, MDE = 0 → KHÔNG bác bỏ, mà phải gắn cờ
    'degenerate' (sd = 0 ⇒ kiểm định vô nghĩa, không được in 'consistent')."""
    paths, et = _dataset(4, 1.0, 50, 50, seed=3)
    res = markov_test_formal(paths, et, seed=2)
    assert res is not None
    assert res["delta"] == 0.0
    assert res["mde"] == 0.0
    assert res["verdict"].startswith("degenerate"), res["verdict"]
    # Quy tắc cũ cũng phải không báo attenuation giả (đã fix _EPS trước đó).
    rough = markov_test(paths, et)
    assert rough is not None and not rough["verdict"].startswith("ASR <")


def test_natural_product_is_an_identity_not_an_assumption():
    """ĐẲNG THỨC: trong chain, ``ASR = ∏ s_i^nat`` (s_i đo trên natural runs).

    Vì ``C_i = 1 ⟹ C_{i-1} = 1``, ta có
        P(C_k=1) = P(C_1=1)·P(C_2=1|C_1=1)···P(C_k=1|C_{k-1}=1)
    tức tích các conditional ĐO TRONG CHÍNH chuỗi bằng ASR **theo định nghĩa**.

    Hệ quả khái niệm (quan trọng cho paper): "kiểm định Markov" KHÔNG phải kiểm
    tra đẳng thức này (nó luôn đúng), mà là kiểm tra xem ước lượng **cách ly**
    ``s_i^controlled`` có chuyển được sang bối cảnh trong chuỗi hay không —
    tức ``s_i^controlled == s_i^nat``? Đây là giả định mà các benchmark
    single-agent đang ngầm dùng khi compose kết quả.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from contagion.benchmark.runner import summarize
    from contagion.core import ContagionConfig, TopologyType
    from contagion.runner.engine import Runner

    cfg = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=4, trials=300,
        per_edge_trials=0, entry_agent="agent_0", provider="mock",
        model_id="mock", marker="BANANA-77", seed=11,
        extra={"mock_infection_prob": 0.55, "target_b": "BANANA-77"},
    )
    runner = Runner(cfg)
    try:
        paths = runner.run()
    finally:
        runner.close()
    m = summarize(paths, None, cfg)

    nat = m["survival_natural"]
    edges = [k for k in nat if k != "overall"]
    prod = 1.0
    for e in edges:
        prod *= nat[e]["mean"]
    assert abs(prod - m["asr"]["mean"]) < 1e-12, (prod, m["asr"]["mean"])
    # Lưu ý bẫy: ``survival_natural["overall"]`` là TRUNG BÌNH các s_i, KHÔNG
    # phải tích — dùng nó để thay cho ∏sᵢ là lỗi. Ở đây chúng khác nhau rõ rệt.
    assert abs(prod - nat["overall"]["mean"]) > 0.05, (
        "pooled mean tình cờ bằng tích — kiểm tra lại định nghĩa")


def test_controlled_vs_natural_can_diverge_on_mock():
    """Trên mock, hai phép đo trùng nhau (cùng cơ chế Bernoulli) — nên nếu chúng
    LỆCH trên LLM thật thì đó là hiệu ứng bối cảnh thật, không phải lỗi code."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from contagion.benchmark.runner import summarize
    from contagion.core import ContagionConfig, TopologyType
    from contagion.runner.engine import Runner

    cfg = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=4, trials=300,
        per_edge_trials=300, entry_agent="agent_0", provider="mock",
        model_id="mock", marker="BANANA-77", seed=5,
        extra={"mock_infection_prob": 0.6, "target_b": "BANANA-77"},
    )
    runner = Runner(cfg)
    try:
        paths = runner.run()
        et = runner.run_per_edge_protocol()
    finally:
        runner.close()
    m = summarize(paths, et, cfg)
    ctrl = m["survival"]["overall"]["mean"]
    nat = m["survival_natural"]["overall"]["mean"]
    assert abs(ctrl - nat) < 0.10, (ctrl, nat)


def test_formal_degenerate_when_chain_never_reaches_target():
    """Trường hợp thực tế (Claude E20): chuỗi không bao giờ tới đích ⇒ ASR = 0 và
    ∏sᵢ = 0 ⇒ sd(delta) = 0 ⇒ kiểm định KHÔNG có thông tin, phải nói thẳng."""
    from contagion.metrics.epidemiology import markov_test_formal_from_counts

    # per-edge 0.00 / 0.60 / 0.03 (Claude, n=30) ⇒ ∏sᵢ = 0; ASR = 0/40.
    counts = [("agent_0->agent_1", 0, 30), ("agent_1->agent_2", 18, 30),
              ("agent_2->agent_3", 1, 30)]
    res = markov_test_formal_from_counts(0, 40, counts, n_boot=400)
    assert res is not None
    assert res["product_s"] == 0.0
    assert res["delta"] == 0.0
    assert res["mde"] == 0.0
    assert res["verdict"].startswith("degenerate"), res["verdict"]


def test_formal_returns_none_off_chain():
    """Topology không phải chain thuần từ entry ⇒ None (không bịa product)."""
    from contagion.core import TopologyType
    from contagion.metrics.epidemiology import EdgeTrial, PropagationPath

    order = ["center", "a", "b"]
    paths = [PropagationPath(trial_id=0, compromised={"center": True, "a": True, "b": True},
                             node_order=list(order))]
    et = [EdgeTrial(src="a", dst="center", trial=i, dst_compromised=True)
          for i in range(5)]
    assert markov_test_formal(paths, et, entry_agent="center") is None
    assert TopologyType.STAR.value == "star"      # sanity: enum dùng ở đây
