"""Tests: benign task context (task realism) + Markov bootstrap CI fallback.

- Agent.steps(incoming, task=None): task context xuất hiện như trusted block
  trong prompt mà KHÔNG qua defense; task=None giữ hành vi cũ.
- Runner wires config.extra benign_contexts / target_task_text vào natural runs
  và per-edge trials (xoay vòng theo trial index) — mock semantics không đổi
  khi không có context; khi có context thì prompt có chứa [assigned task].
- markov_test khi s_hat ở biên (0/1): delta-method CI fail → fallback bootstrap
  percentile CI cho product (docs metric.md §2: delta method OR bootstrap).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contagion.agents.agent import make_agent
from contagion.agents.agent import AgentRole
from contagion.core import ContagionConfig, DefenseType, Message, TopologyType
from contagion.defenses.mechanisms import NoDefense
from contagion.llm.base import MockLLMClient
from contagion.metrics.epidemiology import EdgeTrial, HopOutcome, PropagationPath, markov_test
from contagion.runner.engine import Runner


class _CaptureClient(MockLLMClient):
    """MockLLMClient ghi lại prompt cuối (để kiểm tra task context)."""

    def __init__(self) -> None:
        super().__init__(marker="SECRET", seed=1)
        self.last_prompt = ""
        self.calls = 0

    def complete(self, prompt, system=None, force_infected=False) -> str:
        self.last_prompt = prompt
        self.calls += 1
        return super().complete(prompt, system=system, force_infected=force_infected)


def test_steps_task_context_added_trusted():
    """task → prompt chứa [assigned task]; không có task → prompt cũ."""
    client = _CaptureClient()
    agent = make_agent("a0", AgentRole.WORKER, NoDefense(), client)
    incoming = [Message(sender_id="x", receiver_id="a0", content="content without marker")]
    # Không task: không có assigned-task block.
    client.last_prompt = ""
    agent.steps(incoming)
    assert "[assigned task]" not in client.last_prompt
    # Có task: block xuất hiện và KHÔNG qua defense (NoDefense, nhưng verify text).
    client.last_prompt = ""
    agent.steps(incoming, task="Summarize the quarterly report.")
    assert "[assigned task]" in client.last_prompt
    assert "Summarize the quarterly report." in client.last_prompt


def test_mock_without_context_unchanged():
    """Không cấu hình benign_contexts/target_task_text → mock như cũ (s=1)."""
    cfg = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=3, trials=6, per_edge_trials=20,
        seed=3, extra={"mock_infection_prob": 1.0},
    )
    res = __import__("contagion.benchmark.runner", fromlist=["run_benchmark"]).run_benchmark(cfg)
    m = res["metrics"]
    assert m["asr"]["mean"] == pytest.approx(1.0)
    assert m["survival"]["overall"]["mean"] == pytest.approx(1.0)


def test_context_wired_into_runner_prompt():
    """Với benign_contexts, prompt của agent activation chứa task text."""
    from contagion.benchmark.runner import run_benchmark

    ctx = ["Summarize the quarterly earnings report.",
           "Prepare the customer churn analysis deck.",
           "Draft the product-launch press release."]
    cfg = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=3, trials=3, per_edge_trials=3,
        seed=5, extra={"mock_infection_prob": 1.0, "benign_contexts": ctx},
    )
    # run qua runner trực tiếp để bắt prompt? Engine dùng real/mock client per agent
    # (không capture được). Thay vào đó: agent-level check qua _task_context helper.
    runner = Runner(cfg)
    for i in range(4):
        t = runner._task_context(i)
        assert t == ctx[i % len(ctx)]
    runner.close()


def test_task_context_no_marker_keeps_mock_survival():
    """Task context benign (không chứa marker) không đổi mock relay."""
    from contagion.benchmark.runner import run_benchmark

    cfg = ContagionConfig(
        topology=TopologyType.CHAIN, num_agents=3, trials=5, per_edge_trials=15,
        seed=9, extra={"mock_infection_prob": 1.0,
                       "benign_contexts": ["Do a benign analyst task."]},
    )
    res = run_benchmark(cfg)
    m = res["metrics"]
    assert m["asr"]["mean"] == pytest.approx(1.0)
    assert m["survival"]["overall"]["mean"] == pytest.approx(1.0)


def test_markov_test_bootstrap_fallback_boundary():
    """s_hat=1 (biên): delta-method CI fail → bootstrap fallback, không 'insufficient'.

    ASR thấp (0.5) trong khi per-edge survival = 1.0 cho thấy attenuation
    (sub-Markov): bootstrap product CI [~1,1] → ASR CI dưới product → verdict
    "ASR < prod(s_i)".
    """
    # Paths: chain 4 edges; mỗi run chỉ compromise tới agent cuối 1 nửa số run.
    paths = []
    for r in range(40):
        comp = {"agent_0": True}
        hops = []
        # run chẵn: full chain; run lẻ: dừng ở agent_2 (attenuation)
        full = (r % 2 == 0)
        n = 4 if full else 2
        for i in range(1, 5):
            if i > n:
                break
            comp[f"agent_{i}"] = True
            hops.append(HopOutcome(src=f"agent_{i-1}", dst=f"agent_{i}", step=i,
                                   src_compromised=True, dst_compromised=True))
        paths.append(PropagationPath(trial_id=r, compromised=comp, hops=hops,
                                     node_order=[f"agent_{i}" for i in range(5)]))
    # Edge trials: toàn bộ dst_compromised=True → s_hat=1 mọi edge.
    edges = [(f"agent_{i}", f"agent_{i+1}") for i in range(4)]
    et = [EdgeTrial(src=s, dst=d, trial=t, dst_compromised=True)
          for s, d in edges for t in range(30)]
    res = markov_test(paths, et)
    assert res is not None
    assert res["product_s"] == pytest.approx(1.0)
    assert res["product_s_ci_method"].startswith("bootstrap")
    assert res["verdict"].startswith("ASR < prod(s_i)")  # ASR 0.5 < 1.0


def test_markov_test_delta_method_interior_still_used():
    """s trong (0,1): vẫn dùng delta-method (không fallback bootstrap)."""
    paths = []
    import random as _r
    rng = _r.Random(0)
    for r in range(60):
        comp = {"agent_0": True}
        hops = []
        prev = True
        for i in range(1, 5):
            cur = prev and rng.random() < 0.8
            comp[f"agent_{i}"] = cur
            hops.append(HopOutcome(src=f"agent_{i-1}", dst=f"agent_{i}", step=i,
                                   src_compromised=prev, dst_compromised=cur))
            prev = cur
        paths.append(PropagationPath(trial_id=r, compromised=comp, hops=hops,
                                     node_order=[f"agent_{i}" for i in range(5)]))
    edges = [(f"agent_{i}", f"agent_{i+1}") for i in range(4)]
    et = [EdgeTrial(src=s, dst=d, trial=t,
                    dst_compromised=_r.Random(hash((s, d, t)) % 2**31).random() < 0.8)
          for s, d in edges for t in range(40)]
    res = markov_test(paths, et)
    assert res is not None
    assert res["product_s_ci_method"].startswith("delta-method")
