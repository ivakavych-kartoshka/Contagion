# Contagion

**Contagion: An Epidemiology of Prompt-Injection Propagation in LLM Agent Networks**

Mô hình dịch tễ học về sự lan truyền *Indirect Prompt Injection* trong mạng lưới tác tử LLM
(LLM multi-agent network). Framework cung cấp:

- một **multi-agent testbed** mô phỏng một *agent organization* (emulated),
- các **topology** có thể cấu hình (chain / star / tree),
- các **attack variants** (static / adaptive / re-injection),
- các **defense mechanisms** (paraphrase / delimiter / detection / hop-isolation),
- bộ **metrics** định lượng sự lan truyền theo lý thuyết dịch tễ học.

Đây là *benchmark & measurement framework* nghiên cứu, **không phải** một security guarantee.
`R0 < 1` chỉ là *proof obligation*, không đồng nghĩa với network "secure".

---

## Cài đặt

```powershell
# Tạo virtual environment và cài dependencies
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt          # core + analysis
# hoặc tối thiểu:
.\.venv\Scripts\pip install -e ".[dev]"
```

Requires Python >= 3.10. Không bắt buộc dùng GPU để chạy benchmark (có sẵn mock backend deterministic).

---

## Khái niệm trung tâm

Mỗi **communication hop** giữa hai agent là một *trust boundary*.

| Đại lượng | Ký hiệu | Định nghĩa |
|---|---|---|
| Per-hop survival rate | `s` | `P(A_{i+1} compromised | A_i compromised)` |
| End-to-end propagation | `P_E2E` | `∏ s_i` (riêng chain) |
| Reproduction number | `R0` | `E[# compromises mới per compromised agent]` |

Với `R0 < 1`: *subcritical* (xu hướng lan truyền giảm); `R0 > 1`: *supercritical*.

Input của agent `i+1` phụ thuộc vào output của agent `i` sau khi bị compromise
(`x_{i+1} ⊇ out(i)`). Chính cross-hop composition này tạo nên super-spreader structure,
epidemic threshold và propagation dynamics.

---

## Cấu trúc thư mục

```
contagion/
  core.py                 # enums & cấu trúc dữ liệu dùng chung (Message, Config, ...)
  agents/agent.py         # mô hình agent: role, system prompt, hop-step
  topology/graph.py       # AgentGraph + builders (chain/star/tree)
  attacks/strategies.py   # Payload, InjectionStrategy (static/adaptive), ReInjectionPolicy
  defenses/mechanisms.py  # NoDefense/Paraphrase/Delimiter/Detection/HopIsolation
  metrics/epidemiology.py # s, P_E2E, R0, propagation rate (+ CI/variance)
  llm/base.py             # LLMClient interface + MockLLMClient deterministic
  runner/engine.py        # vòng lặp mô phỏng propagation qua các hop
  benchmark/
    config.py             # load YAML -> ContagionConfig
    runner.py             # run_benchmark, summarize, save_results
    cli.py                # entry point contagion-run
experiments/
  configs/                # các file cấu hình YAML mẫu
  results/                # output (summary.json + hops.csv)
  logs/
scripts/
  run_experiment.py       # chạy 1 cấu hình
  sweep.py                # chạy toàn bộ experiment matrix
tests/                    # pytest smoke tests (dùng mock backend)
notebooks/
```

---

## Chạy nhanh

Chạy một cấu hình:

```powershell
.\.venv\Scripts\python scripts\run_experiment.py experiments\configs\chain_static_nodefense.yaml
```

Sweep toàn bộ matrix (chain/star/tree × 3/5/10 agents × static/adaptive × none/paraphrase/delimiter):

```powershell
.\.venv\Scripts\python scripts\sweep.py --out experiments/results/sweep
```

Chạy test:

```powershell
.\.venv\Scripts\python -m pytest -q
```

---

## Cấu hình (YAML)

```yaml
topology: chain          # chain | star | tree  (mesh/debate dự kiến mở rộng)
num_agents: 5            # 3–10 trong phạm vi nghiên cứu 1 tháng
trials: 30               # số lần lặp (giảm nhiễu LLM stochasticity)
entry_agent: agent_0     # agent nhận entry-point injection đầu tiên
attack: static           # static | adaptive
re_injection: none       # none | independent | colluding
defense: none            # none | paraphrase | delimiter | detection | hop_isolation
content_freedom: free_text   # free_text | structured (liên kết InjecAgent)
max_hops: 10
seed: 42
model_id: mock           # mock | <tên model>
```

`model_id: mock` chạy bằng backend deterministic (test/CI/tạo pipeline).
Để dùng LLM thật, cài thêm backend trong `contagion/llm/` và đặt `model_id` tương ứng.

---

## Backend LLM

- **`mock`** — deterministic, rule-based (re-emit marker khi có injection), dùng cho
  test, CI và phát triển pipeline. Tạo *survival-rate* có kiểm soát qua
  `extra.mock_infection_prob`.
- **transformers / vLLM** — model open-source local (Qwen, Llama, Mistral), ưu tiên do chi phí ~0.
- **OpenAI API** — dự phòng khi cần.

Mọi backend chia sẻ interface `LLMClient.complete(prompt, system) -> str`, nên có thể
swap backend mà không đổi orchestrator.

---

## Lưu ý về độ tin cậy

- **Không chỉ báo cáo point estimates** — mọi metric đi kèm std + 95% CI (xem `SummaryStats`).
- **Markov assumption** cần được kiểm chứng trực tiếp (context/memory effects có thể phá vỡ nó).
- **Reduced spread ≠ secure network.** `R0`/ASV giảm không phải security theorem.

---

## Phạm vi nghiên cứu (1 tháng)

- Agents: **3–10**
- Topology: **Chain, Star, Tree**
- Attack: **Static**, **Adaptive re-injection**
- Defense: **None, Paraphrase, Delimiter/Structured Input**
- Metrics: `s`, end-to-end ASR, propagation rate, `R0`, utility/latency

Mục tiêu trả lời RQ1–RQ3 (lan truyền như thế nào / topology ảnh hưởng ra sao / defense có giảm lan truyền không).

---

## Tài liệu tham khảo chính

- InjecAgent — arXiv:2403.02691
- AgentDojo — arXiv:2406.13352
- Liu & Gong — arXiv:2310.12815
- MAST — arXiv:2503.13657
- Greshake et al. — arXiv:2302.12173
- MetaGPT — arXiv:2308.00352; AutoGen — arXiv:2308.08155
