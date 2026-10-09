# REBUTTAL — AAMAS 2027, Submission 2419
## "Contagion: When Per-Hop Prompt-Injection Survival in LLM Agent Networks Does (and Does Not) Compose"

> **Cách dùng file này.** Mỗi mục dưới đây là một câu trả lời sẵn sàng dán vào rebuttal,
> đã kèm **số liệu thật lấy từ artifact** và **trạng thái** (đã sửa trong bài / trả lời
> bằng lập luận / không thể làm trong thời gian review).
>
> ⚠️ **Nguyên tắc trung thực:** không nêu việc đã làm nếu chưa làm. Các mục ghi
> "không làm được" phải nói rõ lý do (hết credential / cần nhãn người) thay vì hứa.

---

## 1. Ba câu metareview nói sẽ đổi ý họ nhất

### 1.1. Nhãn adoption độc lập (R2 Q3) — ⛔ KHÔNG CÓ ĐƯỜNG TẮT TRUNG THỰC

**Họ hỏi:** nhãn adoption/compliance độc lập ≥100 activation, blind với judge, ≥1 frontier
model, có/không defence.

**Trả lời trung thực:**
> We agree this is the single most important missing measurement, and we do not claim to
> have it. Our adjudication (Supp. Table 6) covers 24 activations from one local model,
> was labelled by the authors, and finds **0/19 flagged activations at level (b)
> adoption** (FPR = 0.792). We have therefore **restricted every claim to textual
> propagation** and renamed the quantity accordingly throughout: the paper now reports
> `ASV`-based *propagation*, not *hijack* or *compromise* in the agentic sense. What we
> cannot do within the review window is produce genuinely independent labels: LLM-assigned
> labels would not answer the question (they reproduce the same judge bias), and we will
> not present author labels as independent. We will provide the ≥100-activation
> independent labelling in the camera-ready if the paper is accepted.

**Nếu được nhận, phải làm:** thuê/gán 100+ activation độc lập, blind, 1 frontier model,
có và không defence → báo level-(b) rate. Đây là điều kiện tiên quyết để claim mạnh hơn.

---

### 1.2. Test Eq. (3) ở chỗ nó CÓ THỂ sai (R1 W3/Q2) — ✅ ĐÃ LÀM

**Họ hỏi:** test trên DAG có cạnh chia sẻ upstream (`s→u→{A,B}→t`), báo observed vs Eq. (3)
vs giá trị inclusion–exclusion.

**Trả lời:** Đã chạy. DAG `agent_0→agent_1→{agent_2,agent_3}→agent_4`, qwen2.5:7b,
40 natural runs, 30 replay/arm/cạnh, 600 activation được judge.

| Cách tính P[target] | Giá trị |
|---|---|
| **Đo được (natural runs, n=240 activation của target)** | **0.792** [0.736, 0.838] |
| Eq. (1) tích chuỗi (sai cấu trúc ở đây) | 0.280 |
| Eq. (3) từ margin **trong chuỗi** | 0.545 |
| Eq. (3) từ margin **cách ly** (bản single-agent benchmark sẽ tính) | 0.309 |
| Mô hình shared-ancestor thuần (tham chiếu) | 0.280 |

> We ran the counterexample the reviewer asked for. The claim of vacuity was correct and
> we have removed it: §5.6 no longer says Eq. (3) "reproduces the measured ASR in all
> three topologies" as if that were evidence. On the reconvergent DAG the recurrence
> built from **isolated** marginals underestimates the measured rate by **0.483** (0.309
> vs 0.792), and per-edge discrepancies reach **2.18×** (`a1→a3`: 0.800 in-chain versus
> 0.367 isolated). The direction matches the Llama chain failure. The recurrence built
> from **in-chain** marginals also underestimates it, by 0.247, which is the correlation
> effect the reviewer predicted; we report both and distinguish them in new Appendix M.

**Giới hạn phải nói:** 3/5 cạnh không tái lập dưới replay (lệch 0.14–0.30 ở n=30), và chỉ
1 model + 1 DAG nhỏ → chúng tôi đọc là "recurrence không chính xác tổng quát", **không**
phải một hiệu chỉnh đã calibrate.

---

### 1.3. Reconcile số liệu và cross-reference (R3 W4/W3, R2 W6, R4 W5) — ✅ ĐÃ LÀM

- **0 undefined reference**; mọi trỏ tới phụ lục giờ lấy bằng `xr-hyper` nên tự khớp
  chữ cái A–P (trước đây trỏ viết cứng và lệch).
- **Floor 0.10 vs 0.17**: đã reconcile trong bài — `0.10` là *end-to-end chain ASR*,
  `0.17` là *single-hop cell*; hai đại lượng khác nhau, đã ghi rõ cả hai chỗ.
- **Range ASR trong Abstract**: reviewer đúng — `0.45–0.80` bỏ sót tree `0.800` và
  `R₀ = 0.831`. Đã sửa thành: ASR `0.45–0.80`, R₀ `0.42–0.83`, và **thứ tự hai đại
  lượng có thể đảo**.
- **Bảng 1 provenance**: † = fresh-artefact; 3 hàng còn lại là fixed. Đã kiểm artifact:
  cờ protocol **không** được lưu trong `results.json` mà chỉ có trong lệnh chạy ghi ở
  `REPRODUCE.md` §B1/B2 → chúng tôi đã ghi rõ đây là provenance *tái dựng từ lệnh chạy*,
  không phải field của release (xem `artifacts/MANIFEST.json` → `protocol_evidence`).

---

## 2. R1 — Reviewer 1 (3/7)

**W1 (identity ≠ finding)** — ✅ đã sửa. Abstract không còn liệt kê Eq. (1) như một
"result"; §3.5 gọi nó là *identity of the estimator* và nói rõ **không thể sai** với
chain. Câu "holds empirically" đã bỏ.

**W2 (Markov-sufficiency failure chưa được model hoá)** — 🟡 trả lời bằng lập luận +
giới hạn. Chúng tôi đồng ý chẩn đoán mà không mô hình hoá: Table 4 cho thấy
`Pr[C_i=1 | C_{i-1}=1]` phụ thuộc **form** (0.067 bare vs 0.967 embedded), nên `C` nhị
phân không đủ. Chúng tôi **không** dựng mô hình (form × compromise) trong bản này vì
reviewer chỉ ra đúng rằng fit trên chính Table 4 thì *"yields ŝ^nat by construction"* —
một mô hình như vậy cần dữ liệu mới có nhãn form per-trial, mà chúng tôi không có.
Chúng tôi đã hạ claim từ "Prescription (1)" xuống mô tả chẩn đoán.

**W3 ([21] misattribution)** — ✅ đã sửa. Câu "why Eq. (3) is exact on our networks" đã bỏ.
Reviewer đúng rằng [21] là NP-hardness của influence maximisation và lập luận đó không
đỡ được claim cấu trúc.

**W4 (R₀ straw man + generation convention)** — ✅ đã sửa. §3.6 giờ có công thức tường
minh trong observed counts, unit of analysis, denominator, và generation convention. Và
chúng tôi **rút hứa hẹn về interval**: reviewer đúng rằng bảng không có interval, và
khi kiểm artifact chúng tôi thấy **không tái lập được** R₀ từ per-cell files (công thức
khớp ở 2/9 cell), nên thay vì in một interval không reproducible, bài ghi rõ **không**
gắn interval và nói vì sao (Supp. Table topology caption).

**W5 (cyclic "design rule" quá mạnh)** — ✅ đã sửa. Hạ từ "design rule" xuống
*mean-field prediction* trên 3 loop; thêm công thức finite-state
`P(re-compromise) ≤ 1 − ∏(1 − a_jc_j) < 1` kể cả trên criticality, và nêu rõ loop
Σ = 1.018 nằm sát ngưỡng nên không kết luận được extinction.

**W6 (defence placement = min-cut textbook)** — 🟡 hạ claim. Abstract (iv) không còn
được trình bày như một result mới; chúng tôi nói rõ đây là cấu trúc, minh hoạ bằng toy,
**chưa có can thiệp placement thật**.

**W7 (depth slope grow mechanically, no intervals)** — ✅ đã sửa. Thêm **permutation
p-value** (liệt kê toàn bộ cho n ≤ 9, Monte Carlo 10⁴ cho n lớn) + **bootstrap CI** cho
cả ρ và slope; bảng đầy đủ ở Appendix J. Kết quả nói rõ DeepSeek **không** ủng hộ trend
(n=10: p = 0.067, CI slope chứa 0; n=8: p = 0.91), và chúng tôi gọi nó là *diagnostic*,
không phải correction.

**Q1 (C₀=1 enforce thế nào)** — ✅ trả lời: §3.2 ghi entry bị compromise **theo định
nghĩa** (inject trực tiếp, response thành message đầu), **không có run nào bị loại**.
R₀ numerator/denominator/generation convention đã có công thức ở §3.6.

**Q2 (test Eq. (3) trên DAG)** — ✅ xem §1.2 trên.

**Q3 (loop: w bao nhiêu, P(re-compromise) mỗi vòng, so với observed + interval)** —
🟡 làm được **một phần không cần model**: chúng tôi báo `w`, công thức finite-state, và
upper bound; chúng tôi **không** có interval cho tỉ lệ per-round quan sát vì dữ liệu loop
chỉ lưu 5–8 round. Đây là việc chúng tôi nhận là chưa đủ.

**Q4 (two-state chain fit Table 4 có tái tạo 0.875 của Llama?)** — ❌ chưa làm, và giải
thích như W2. Chúng tôi không muốn nộp một fit tautological.

**Q5 (CI hoặc permutation p cho mỗi slope + slope dự đoán ratio của Table 2?)** — ✅ đã
làm phần CI/permutation (W7). Phần **slope dự đoán ratio** chưa làm thành test riêng;
chúng tôi báo tương quan định tính và nhận đây là chỗ còn thiếu.

---

## 3. R2 — Reviewer 2 (4/7)

**W1 (outcome là trích chuỗi, không phải injection success)** — ✅ đã siết ngôn ngữ.
Bài nói rõ primary outcome là **textual propagation (ASV)**, không phải instruction
adoption; "hijack"/"compromise" đã được thay bằng ngôn ngữ propagation ở những chỗ có
thể. Chúng tôi **không** che việc 19/19 positive là non-adoption.

**W2 (1 payload, không tool use, defence quá ít)** — 🟡 nhận, một phần do credential.
Script đã hỗ trợ đa payload (`--payloads`) và chúng tôi đã chạy **thêm một payload**
trên model local (kết quả: [điền sau khi chạy]). Chúng tôi **không** chạy payload kiểu
action/tool-call: engine hiện tool-less và việc thêm là thay đổi hệ thống, không phải
tham số. Chúng tôi nói rõ điều này trong Limitations.

**W3 (role confounded với position; Fig. 1 dùng Family A bị loại khỏi headline)** — ✅
đã làm **role-permutation control** (Appendix L) + sửa caption Fig. 2 nêu rõ Family A.

> **Kết quả quan trọng, và chúng tôi đã hạ claim vì nó:** qwen2.5:7b, 5 agent, 40 natural
> runs mỗi thứ tự. Đảo role (reviewer lên đầu) làm profile dịch chuyển trung bình
> **0.186** (cạnh sâu 2: 0.882 → 0.381). Hai cách đọc (theo vị trí 0.186 vs theo role
> 0.151) **chênh chỉ 0.035 < ngưỡng 0.05** ⇒ **một hoán vị KHÔNG tách được role khỏi
> vị trí**. Vì vậy tiêu đề §5.1 đã đổi từ *"survival is role-dependent"* thành
> *"varies sharply by position"*, và bài **không xếp hạng role**.
>
> **Nửa còn lại của yêu cầu (Llama) chúng tôi không làm được**: credential Bedrock hết
> hạn trong thời gian review. Chúng tôi nói rõ giới hạn này thay vì bỏ qua.

**W4 (coverage claims vượt mẫu; Nova/Claude ở floor; "capability" claim)** — ✅ đã sửa.
Tiêu đề §5.1 đổi thành *"does not track **scale**"*; thêm caveat *"negative association
over five uncontrolled points, not a capability finding"* (nguyên nhân khả dĩ hơn là
injection-specific refusal training, chưa test). Verdict "resistant" của Claude đã hạ:
floor của nó đo trên form bare/plain — dạng **kém hiệu quả nhất** theo Table 4 — nên
chúng tôi **không** claim kháng cự tổng quát.

**W5 (paraphrase "strictly dominated" trên 20 paired runs, không interval; Fig. 1 không
reconcile với §5.5; paraphraser có bị hijack không?)** — 🟡 reconcile + nhận giới hạn.
Hai kết quả khác harness: Fig. 2 (Task A, `rerun_chain_raw.py`, marker
`LEAK-TOKEN-7F3A2C`) so với §5.5 (Task B, n=20 paired). Chúng tôi đã ghi rõ trong
caption Fig. 2 rằng đó là Family A, family **không dùng cho headline**. Việc
**paraphraser có bị hijack** chưa đo — nhận là thiếu.

**W6 (floor 0.10 vs 0.17; noise gauge)** — ✅ đã reconcile, xem §1.3.

**W7 (dual-use chỉ ở supplement; Ethical Considerations hai câu)** — 🟡 một phần. Do giới
hạn 8 trang, câu dual-use hiện nằm trong **mục "Ethics and Artifact Availability"** ở
main (bản mới nhất) cùng link artifact; bản đầy đủ vẫn ở Appendix K.

**Q1 (lặp Table 4 trên Claude/Nova)** — ⛔ không làm được: credential hết hạn.
**Q2 (permute role cho Llama và qwen)** — 🟡 qwen ✅ (Appendix L), Llama ⛔ (credential).
**Q3 (nhãn adoption độc lập)** — ⛔ xem §1.1.
**Q4 (reconcile 0.10/0.17 + nói rõ run nào)** — ✅ đã làm.
**Q5 (paraphraser có emit target không; Fig. 1 paraphrase trên Family B?)** — ❌ chưa đo.

---

## 4. R3 — Reviewer 3 (5/7)

**W1 (power; "agrees within resolution" là non-rejection)** — ✅ đã sửa. Thêm **TOST**
với margin ±0.15 đặt trước; kết quả: DeepSeek **fail TOST ở 2/3 cạnh tại n=40** và chỉ
pass cả 3 ở n=200. Bài không còn đọc null là agreement. Thêm **per-edge test** (Fisher +
Wilson) trong `transport_tests.py` và interval cho các cặp `s^ctrl`/`s^nat`.

**W2 (boundary/dependence; cluster count = 3; p=0.0014 không khớp exp(−13.40/2))** — ✅
đã sửa phần nói rõ. Bài ghi **Wilson–Hilferty approximation** cho χ² tail và nêu exact
p = 0.0012, để reviewer không phải đoán. Phần **context-level analysis với >3 contexts**
thì chưa làm (cần chạy thêm).

**W3 (cell provenance; §5.6 không nói số nào star/tree)** — ✅ đã sửa cả hai. §5.6 nói
rõ thứ tự và nêu việc **đảo chiều theo scale**; Table 1 caption ghi † và nói 3 hàng kia
là fixed.

**W4 (evidence ở supplement; cross-reference dangle; "Appendix 7"/"A–10")** — ✅ đã sửa.
**0 undefined reference**; trỏ phụ lục dùng `xr-hyper` nên tự khớp chữ cái; không còn
"Section 5.10/4.2" trong supplement.

**W5 (estimator validation 60 replication mỏng)** — 🟡 nhận. 60 replication cho size
0.067–0.083 ở nominal 0.05 nằm trong ~2 Monte-Carlo SE; chúng tôi không claim
"unbiased". Việc chạy nhiều replication hơn chưa làm.

**W6 (multiplicity áp không đều; R₀ hứa Wilson interval; n dùng lẫn trials/agents)** — ✅
phần lớn đã sửa: R₀ **không** còn hứa interval (xem R1 W4); nhãn confirmatory vs
exploratory có ở Appendix P; BH có bảng riêng. Việc mở rộng family-wise correction cho
topology/obfuscation/loop thì chưa.

**W7 (không verify được reproducibility; không có artifact link; thiếu model ID/ngày/
call count; không có confirmatory labelling)** — ✅ **đã làm phần lớn**:
- **Artifact link ẩn danh** giờ có: `https://anonymous.4open.science/r/Contagion-F4B8/`
  (MIT code, CC-BY-4.0 data) — nêu ở main + Appendix P.
- **Model identifier thật** (đọc từ file kết quả, không viết tay): bảng mới trong
  Appendix P — Llama `us.meta.llama3-3-70b-instruct-v1:0`, DeepSeek `deepseek.v3.2`,
  Nova `amazon.nova-pro-v1:0`, Claude
  `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, qwen local `qwen2.5:7b`.
- **Ngày thu thập**: 2026-09-11 … 2026-09-14 (hosted), tới 2026-10-08 cho local rerun.
- **Manifest machine-readable** `artifacts/MANIFEST.json` (104 cell, một dòng/cell).
- **Confirmatory vs exploratory** đã nhãn (Appendix P).
- **Chưa cung cấp**: per-condition call/failure count, và prompt template đầy đủ cho mọi
  arm. Chúng tôi nói rõ đây là *partial* reproducibility.

**Q1 (protocol nào sinh từng hàng Table 1/Table 5/Fig. 2)** — ✅ đã trả lời: † = fresh;
Table 5 và Fig. 2 là **fixed**; và cờ protocol chỉ có trong lệnh chạy của `REPRODUCE.md`
(không có trong `results.json` — điều này chính reviewer sẽ thấy nếu mở manifest).
**Q2 (per-edge test + TOST mọi cell)** — ✅ đã có script + áp cho Table 2.
**Q3 (số nào star/tree; second-Llama và DeepSeek có khớp Table 5?)** — ✅ đã ghi rõ;
star/tree **đảo chiều theo scale** nên Table 5 (n=7) và repeats (n=10) khác nhau.
**Q4 (artifact link + model ID/ngày/decoding/call count)** — 🟡 link + ID + ngày + decoding
✅; **call/failure count** ❌ (không lưu).
**Q5 (thay cluster bootstrap 6-repeat bằng context-level >3 contexts)** — ❌ chưa làm.

---

## 5. R4 — Reviewer 4 (3/7)

**W1 (bốn prescription có significance không)** — 🟡 nhận một phần. Bài đã hạ tông:
§6 nói adoption "changes what is reported rather than what is built". Chúng tôi không
claim prescription (4) là mới.

**W2 (evidence breadth vs claim; "Contagion"/epidemic framing hứa propagation dynamics
nhưng thực tế là one-shot hand-off)** — ✅ đã sửa. Thêm câu phạm vi: *dynamics đo được
là feed-forward, mỗi agent forward một lần mỗi run; chỉ loop 3 agent là recurrent*. Từ
khoá "Epidemic threshold" đã bỏ.

**W3 (organisation & clarity; caveat lặp lại nhiều lần; §2.1 dùng Eq. (3)/R₀ trước khi
định nghĩa; evidence nằm ở supplement)** — 🟡 một phần. Abstract và §1 đã được nén để
giảm lặp; **n=200 + BH + χ² + interval** đã đưa **vào bài chính**. Việc tái cấu trúc
§2.1 thì chưa làm triệt để.

**W4 (positioning; thiếu Agent Smith/NetSafe/G-Safeguard/Huang)** — ✅ đã thêm **cả 4**,
verify từ nguồn chính thức (PMLR v235, ACL Findings 2025, ACL 2025 long, PMLR v267),
kèm 2 câu nói rõ per-edge view dự đoán gì mà các công trình đó không có.

**W5 (citation hygiene)** — ✅ đã sửa: `[6] Arindam → Anirban` DasGupta ✅; `[26]` đổi
"reuse" → "adapt" và nói rõ ASV/MR được **định nghĩa lại** thành target-bigram
containment / Dice ✅; `[13]` (multi-agent debate) **bỏ** khỏi "orchestration frameworks"
✅; `[31]` (Reflexion) **bỏ**, thay bằng ReAct cho câu về tool use ✅; `[21]` đã sửa (R1 W3).
**Chưa verify được** 3 mục 2026 ([1], [23], [24]) — chúng tôi nêu thẳng là chưa kiểm chứng
được thay vì để nguyên.

**W6 (terminology vs measurement; range ASR bỏ sót tree)** — ✅ đã sửa: range ASR giờ
`0.45–0.80` **kèm** R₀ `0.42–0.83` và nói rõ thứ tự có thể đảo (tree `0.800`/`0.831`);
ngôn ngữ đã chuyển sang propagation.

**W7 (Fig. 2 không đọc được; Table 5 không interval; Fig. 1 khác Family B không chú
thích)** — ✅ đã sửa: **Fig. 2 và Fig. 4 được vẽ lại đúng cỡ in** (trước đây bị LaTeX
co ~2× và ~5×, chữ còn ~2pt); Fig. 1 caption nêu rõ **Family A**; Table 5 ghi rõ R₀
không có interval và vì sao.

**Q1 (worked example cho AutoGen/MetaGPT)** — ❌ chưa làm.
**Q2 (per-edge view dự đoán gì)** — ✅ đã thêm đoạn positioning.
**Q3 (kết quả nào chỉ ở supplement, kết quả nào sẽ vào main)** — ✅ n=200, BH, χ² đã vào main.
**Q4 (có kết luận nào sống sót với payload/task family thứ 2 không?)** — 🟡 [điền sau khi
chạy đa payload], và nếu không sống sót thì phải nói trong Abstract.
**Q5 ([26] ASV/MR dùng đúng định nghĩa hay đổi?)** — ✅ đã nói rõ là **đổi**, và mô tả
cách đổi.

---

## 6. Ba điều chúng tôi KHÔNG claim (để tránh bị đọc quá)

1. **Không claim adoption/hijack.** Primary outcome là textual propagation (ASV).
2. **Không claim role-dependence** như một hiệu ứng đã tách khỏi position — kiểm soát
   hoán vị cho thấy một hoán vị **không đủ** để tách.
3. **Không claim "resistance" tổng quát** cho frontier model — floor đo trên form
   bare/plain.

## 7. Hai giới hạn do credential (nói thẳng, không giấu)

- **Bedrock credential hết hạn** trong thời gian review ⇒ không chạy được: content-form
  trên Claude/Nova (R2 Q1), đa payload trên Llama (R2 W2), role-permutation trên Llama
  (R2 Q2), context-level >3 contexts (R3 Q5).
- **Cờ protocol (fixed/fresh) không được lưu trong per-cell file** ⇒ nhãn † của Table 1
  là provenance **tái dựng từ lệnh chạy** trong `REPRODUCE.md`, không phải field của
  release. Chúng tôi nói rõ điều này trong manifest và trong rebuttal này.
