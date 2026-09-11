# PAPER DRAFT — Cấu trúc & nội dung dự kiến

> ⚠️ **File này là KẾ HOẠCH (tiếng Việt).** Văn bản paper thật (tiếng Anh —
> ngôn ngữ nộp hội nghị) nằm ở **`PAPER_TEXT.md`**: đã có §1 Introduction,
> §2 Related Work, §3 Method, §4 Validation, khung §5 Results, §8 Limitations.
> Quy ước trích dẫn trong file đó: `§N` = mục của paper, `metric §N` = mục của
> `docs/metric.md`.

> Draft để bạn đọc và quyết định (model/topology/cells cần chạy tiếp). Mọi con số
> trong đây là kết quả THẬT từ E10–E19 (qwen2.5:7b local). Chưa phải văn bản
> hoàn chỉnh — đây là khung + dữ liệu chính.

---

## 1. Title candidates

1. "Propagation of Prompt-Injection in LLM Agent Networks: A Measurement Study
   with Semantic Task Competition"
2. "How Far Does One Injection Go? Per-Hop Survival of Prompt Injection Across
   LLM Agent Chains"
3. "Semantic Hijacking vs. Data-Loss-Prevention: An Arms-Race View of
   Prompt-Injection Propagation in Agent Networks"

---

## 2. Research questions (RQ)

- **RQ1 (survival):** Với injected instruction NGỮ NGHĨA cạnh tranh legit task,
  per-hop survival `s` của mỗi edge là bao nhiêu — và phụ thuộc role của agent
  nhận (receiver) đến mức nào?
- **RQ2 (Markov):** Lan truyền end-to-end có khớp mô hình Markov bậc 1
  (`ASR ≈ ∏ŝᵢ`) không, hay có reinforcement/attenuation?
- **RQ3 (defense):** Defense theo kiểu DLP (redact literal secret) chặn attack
  tĩnh ra sao — và bị obfuscation (chia mảnh secret) qua mặt đến mức nào?
  (cat-and-mouse có cấu trúc)

---

## 3. Contributions (claims dự kiến)

1. **Framework đo propagation** cho LLM agent networks: per-hop survival `s`
   (controlled per-edge) + ASR/R0 (natural runs) + Markov test — đã hiện thực
   trong code, docs/metric.md, có synthetic validation (Phase 2).
2. **Task family semantic instruction-competition** (Task B): injected task có
   nghĩa, cạnh tranh legit task — đo được survival phân tán trong (0,1) trên
   LLM thật (thoát ceiling của marker-echo). Judge deterministic (ASV-only).
3. **Phát hiện role-dependence mạnh**: `s` thay đổi 0.13→0.87 theo role receiver
   (worker thấp, reviewer cao) — phải báo conditional-on-role.
4. **Defense arms-race đo được**: DLP-redact chặn attack tĩnh 100% (survival 0);
   obfuscation chia-mảnh (split) qua mặt 100%; obfuscation spaced thì thất bại
   (model không tái hợp) → "độ khó obfuscation" là biến có cấu trúc.

---

## 4. Method (tóm tắt — chi tiết trong docs/metric.md + code)

- Agent network (chain/star/tree); mỗi hop = trust boundary.
- Legit task qua `benign_contexts` (agent bận việc thật).
- Attack: entry C₀=1 by construction; payload = tool-result ngữ nghĩa
  (Task B, `target_b`).
- Judge: `C = 1[ASV ≥ 0.9]` (marker/target-bigram containment; MR báo cáo chỉ).
- Protocols độc lập: natural runs (ASR/R0/Markov) vs controlled per-edge (s).
- Defense: DLP redact (deterministic) / paraphrase (semantic LLM).
- Stats: Wilson CI; Markov product CI delta/bootstrap; Phase-2 đã validate
  coverage/size/power trên mock.

---

## 3b. Related work & positioning gap (scan 2026-04)

| Công trình | Đo gì | Khác ta |
|---|---|---|
| [InjecAgent (ACL Findings 2024)](https://aclanthology.org/2024.findings-acl.624/) | Indirect prompt injection, tool-integrated **single agent**; ASV/MR + τ | KHÔNG đo **propagation giữa các agent**; không có per-hop s / Markov |
| [Cascading Instruction Influence (SOIC 2026)](https://iapress.org/index.php/soic/article/view/3574) | Injection qua 3-tier hierarchical chain; compromise rate; Cohen's d | Không tách s per-edge controlled vs ASR natural; không Markov test; journal thường |
| [Cross-layer contagion in multi-agent swarms: multiplex Markov (Cybersecurity 2026)](https://link.springer.com/article/10.1186/s42400-026-00628-w) | Lý thuyết Markov contagion trong swarms | Mô hình lý thuyết + emulation; ta đo **empirical per-hop survival** trên LLM thật |
| [Adaptive Attacks Break Defenses vs Indirect PI (arXiv 2503.00061)](https://ar5iv.labs.arxiv.org/html/2503.00061) | Defense + adaptive attack (single agent) | Ta đo arms-race **trong propagation multi-agent** |
| "Zombie agents"/mind-virus báo chí (NUS) | Contagion giữa agents, ~55% | Truyền thông; chưa peer-review metrics framework |

**Gap đề xuất (điểm bán):**
1. **Per-hop survival framework đo EMPIRICAL trên LLM thật** với hai protocol độc
   lập (controlled per-edge `s` vs natural `ASR`) + Markov test — tới nay các bài
   gần nhất hoặc single-agent (InjecAgent) hoặc lý thuyết (swarm Markov) hoặc
   aggregate compromise rate (CII).
2. **Role-dependence định lượng** của `s` (receiver role quyết định) — chưa thấy
   bài nào báo conditional-on-role như vậy.
3. **Defense arms-race trong propagation** với phát hiện "obfuscation có cấu
   trúc: split qua mặt DLP, spaced thì fail (model không tái hợp)".
4. **Task family semantic competition + judge deterministic (ASV-only)** để tránh
   ceiling marker-echo — đóng góp về phương pháp đo.

⚠️ **Rủi ro cạnh tranh:** chủ đề rất nóng 2025–2026 — phải đối chiếu kỹ hơn
(đọc đủ InjecAgent, CII, swarm-Markov) trước khi khẳng định novelty; và cần
replicate trên model mạnh để claim "LLM thật" có trọng lượng.

## 3c. Đọc sâu (deep-read) — kết quả & hệ quả cho positioning

**InjecAgent (Zhan et al., ACL Findings 2024):** benchmark 1,054 test case,
**tool-integrated single agent** (ReAct); 30 LLM agents; ReAct-GPT-4 ASR 24%.
→ Xác nhận: họ đo **1 agent + tool call**, KHÔNG có hop giữa nhiều agent; ASV/MR
của họ là "output có gọi đúng tool attacker không" — khác hoàn toàn per-hop
survival của ta. Framework ta mượn khái niệm ASV/MR/τ nhưng áp cho propagation.

**Adaptive Attacks Break Defenses vs IPI (Zhan et al., arXiv 2503.00061):**
8 defenses (detection/input-level/model-level: instructional prevention, data
isolation, sandwich, **paraphrasing**, detector, perplexity, adversarial
finetune) trên **single-agent IPI**; adaptive attacks (GCG/AutoDAN/M-GCG/T-GCG)
bypass MỌI defense >50% ASR, kể cả **paraphrasing bị T-GCG đánh bại**.
→ **Hệ quả trực tiếp cho ta:**
  1. Phát hiện "paraphrase vô hiệu" (E17) của ta **khớp literature** — không
     phải bug/artifact; các tác giả cũng thấy paraphrasing bị qua mặt.
  2. Nhưng ta khác: (a) đo trong **propagation multi-hop** (không single-turn);
     (b) defense của ta (redact-DLP) + obfuscation bằng **ngôn ngữ tự nhiên có
     cấu trúc** (split/spaced) — KHÔNG phải adversarial token tối ưu (GCG).
     Đây là "thực tế deployment hơn" (attacker không white-box tối ưu token).
  3. Model họ dùng: Vicuna-7B / Llama3-8B — **cỡ 7B là chuẩn literature này**
     → củng cố: qwen2.5:7b local KHÔNG phải điểm yếu chí mạng; nhưng họ cũng
     cho thấy finetuned-agent (Llama3-8B) ASR chỉ 9% → model/agent-type quyết
     định mức độ — ta nên thêm 1 model nữa (khác họ qwen) để claim rộng.

**Cascading Instruction Influence (SOIC 2026):** 3-tier hierarchical chain, 10
production LLMs, đo **compromise rate aggregate** + Cohen's d (hierarchical ≫
centralized), CII model, sandbox mitigation giảm còn 23.4%.
→ Gần nhất về "multi-agent propagation" nhưng: (a) không tách per-hop s controlled
vs ASR natural; (b) không Markov test / CI Wilson per-edge; (c) journal thường,
không phải A*-venue chuẩn. Gap của ta về **metric framework empirical** vẫn đứng.

**Swarm multiplex Markov (Cybersecurity 2026):** mô hình lý thuyết contagion +
emulation — không phải đo empirical per-hop trên LLM thật.

→ **Kết luận positioning (sau deep-read):**
- Claim cốt lõi **"empirical per-hop survival framework trong multi-agent
  propagation, 2 protocol độc lập + Markov test + conditional-on-role"** vẫn
  trống trong literature (các bài: single-agent / lý thuyết / aggregate).
- Defense arms-race của ta nên định vị là **"deployment-realistic obfuscation
  (natural-language structural) vs DLP trong propagation"** — khác adaptive-token
  optimization (GCG) của họ.
- **Bắt buộc thêm:** ít nhất 1 model khác họ (vd Llama-3.1-8B local hoặc API
  mạnh) để claim không phụ thuộc qwen; và đối chiếu rõ "single-hop IPI literature
  (InjecAgent/Adaptive) ≠ multi-hop propagation measurement" trong paper.

---

## 5. Kết quả chính (số thật)

### 5.0 🔥 SO SÁNH CHÉO MODEL (E20 — quyết định độ tin cậy của paper)

| Chỉ số (Task B chain, trials=40, per_edge=30) | qwen2.5:7b (local) | **Claude Sonnet 4.5 (Bedrock)** |
|---|---|---|
| Survival (không defense) | 0.611 [0.51, 0.71] | **0.211 [0.14, 0.31]** |
| ASR | 0.300 | **0.000** [0, 0.088] |
| Survival + REDACT DLP | 0.000 | **0.000** |
| Per-edge (none) | 0.13 / 0.87 / 0.47 / 0.43 | **0.00 / 0.60 / 0.03** |
| Obfusc. split × redact | **1.00** | **0.25** |

→ **Hiện tượng cốt lõi đứng trên CẢ HAI model** (propagation, role-dependence,
DLP chặn tĩnh 100%). Khác biệt: **model mạnh chống injection ~3× tốt hơn** và
**obfuscation kém hiệu quả hơn nhiều** (0.25 vs 1.00) → phát hiện "arms-race phụ
thuộc model" — điểm mới.

### 5.1 RQ1 — survival theo role (E10, qwen2.5:7b, chain n=5, per-edge n=30)
| edge | dst role | s | 95% CI |
|---|---|---|---|
| agent_0→agent_1 | worker | 0.133 | [0.053, 0.297] |
| agent_1→agent_2 | reviewer | 0.867 | [0.703, 0.947] |
| agent_2→agent_3 | aggregator | 0.467 | [0.302, 0.639] |
| agent_3→agent_4 | planner | 0.433 | [0.274, 0.608] |

→ **Role-dependence mạnh (6.5× giữa worker/reviewer).** Trên Claude (E20) cũng
vậy: 0.00 → 0.60 → 0.03 → role-dependence không phải artifact của model nhỏ.

### 5.2 RQ2 — Markov (E17, Task B chain n=4, n=40)
- none: ASR 0.300 [0.181,0.454]; ∏ŝ = 0.205 [0.118,0.356] → "consistent"
- paraphrase: ASR 0.275; ∏ŝ = 0.247 → "consistent"
- Claude none: ASR 0.000; ∏ŝ = 0.000 → "consistent" (surv quá thấp)
→ Chưa đủ power (n=40); cần n=200–300 để phân biệt deviation (Phase-2).

### 5.3 RQ3 — defense (E17/E18/E19/E20)
| Cấu hình | qwen2.5:7b | Claude Sonnet 4.5 |
|---|---|---|
| Task B none | ASR 0.300 · surv 0.611 | ASR 0.000 · surv 0.211 |
| + paraphrase semantic | ASR 0.275 · surv 0.644 | (chưa đo) |
| + **redact DLP** | ASR 0.000 · surv **0.000** | ASR 0.000 · surv **0.000** |
| arms-race: redact × plain/spaced/split | 0.00 / 0.00 / **1.00** | 0.00 / 0.00 / **0.25** |

→ **DLP chặn attack tĩnh 100% trên cả 2 model** (ổn định); **obfuscation split
qua mặt được nhưng phụ thuộc model** (qwen 100% vs Claude 25%).

---

## 6. Figures dự kiến

> **Đã vẽ được (2026-09-11)** bằng `python scripts\make_figures.py` → PNG trong
> `experiments/results/figures/` (nguồn từng hình + cảnh báo: `figure_notes.md`).

1. Framework pipeline (agent hop + judge + protocols). → `fig1_framework.png`
2. Survival per-edge theo role (bar + CI) — chain none vs paraphrase. → `fig2_per_role_survival.png`
3. Task B survival/ASR theo defense (none/paraphrase/redact). → `fig3_taskb_defenses.png`
4. Defense arms-race heatmap: defense × attack-style (E19). → `fig4_obfuscation_heatmap.png`
   (⚠️ n=8 → CI rộng; chờ P1 `--n-obf 30`)
5. Cross-model: qwen2.5:7b vs frontier (Bedrock). → `fig5_cross_model.png`
6. Markov ASR vs ∏ŝ với CI. → `fig6_markov.png` (⚠️ n=40 chưa đủ power → P4)
7. (Chưa có) Star/tree để cho thấy topology ảnh hưởng → cần P5.
8. (Chưa có) §7 trade-off plot (ASR vs Retention) → cần P3 `utility_real.py`.

---

## 7. Discussion

- Role-dependence ⇒ "s của agent" không phải hằng số model; báo conditional.
- Markov: hiện consistent; power chưa đủ — cần n lớn trước khi kết luận.
- Defense chỉ mạnh dưới giả định DLP (biết secret) + attack tĩnh; obfuscation
  có cấu trúc phá defense — bài học: defense phải đối phó cả obfuscation.
- Phát hiện phụ: paraphrase semantic vô hiệu trên chain (giữ fact); MR Dice
  false-positive (bắt chước lệnh) → chọn ASV-only.

---

## 8. Limitations (nói thẳng)

1. **Model yếu & local**: qwen2.5:7b (7.6B, 4GB VRAM) — không đại diện SOTA;
   ngưỡng judge là per-model → cần re-calibrate nếu đổi model.
2. **n nhỏ**: Markov power cần trials 200–300; hiện 40.
3. **1 task family + 1 target** (BANANA-77); chưa đa dạng câu hỏi B.
4. **Chủ yếu chain**; star/tree mới pilot nhỏ.
5. Refusal/compliance phụ thuộc framing — đã kiểm soát (benign wording).

---

## 9. Quyết định còn mở (bạn chốt)

- [ ] **Model**: (a) giữ 7b local cho draft/baseline; (b) API mạnh (GPT-4o-mini/
      DeepSeek/Claude) — cần budget + re-calibrate judge; (c) 3b (rẻ, yếu hơn).
- [ ] **Topology**: chỉ chain cho số liệu chính, hay chạy thêm star/tree
      (mỗi cell ~1.5–3h local).
- [ ] **Sample size**: chấp nhận n=40 (CI rộng, báo giới hạn) hay chạy
      Markov-power n=200–300 cho 1–2 cells headline (~3–6h/cell local).
- [ ] **Defense arms-race ở chain** (E19 mới 1-hop): có chạy chain split×redact
      (~2–3h) để có bảng end-to-end không.

---

## 10. Ước lượng còn lại để nộp A*

- Đã làm ≈ 40% (framework + validation + task B + defense story cấp hop).
- Còn: chốt model/scale, 1–2 bảng headline end-to-end, figures/notebooks,
  related-work đối chiếu, và viết (~60% còn lại, viết chiếm nhiều nhất).
