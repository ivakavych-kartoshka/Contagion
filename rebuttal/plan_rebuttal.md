# Kế hoạch hành động Rebuttal & Camera-Ready — AAMAS 2027 (Submission 2419)

> **Quy định hội nghị (TUÂN THỦ 100%):**
>
> - **Trước 08/10/2026:** Được sửa và upload lại paper.
> - **Giai đoạn Rebuttal (HIỆN TẠI — cập nhật 23/11/2026):** **KHÔNG** được sửa paper, **KHÔNG** upload lại PDF/supplementary, **KHÔNG** chèn link ngoài (GitHub/Drive mới). Chỉ nộp **3 bản text rebuttal riêng biệt**, tối đa **2.500 ký tự/bản**. Mọi cam kết chỉnh sửa văn bản/bảng biểu phải ghi rõ thực hiện ở bản **camera-ready**.
> - **Sau Acceptance (Camera-Ready):** Được sửa và hoàn thiện bản cuối.
>
> **Trạng thái Rebuttal:** **HOÀN TẤT PHẦN I** — toàn bộ thực nghiệm, audit, kiểm tra mắt QC và 3 bản text rebuttal (`review1.md`: **2.488** ký tự, `review2.md`: **2.471** ký tự, `review3.md`: **2.481** ký tự; `has_http=False`; `pytest`: `88 passed`) đã sẵn sàng dán lên OpenReview.
>
> **Mục tiêu Rebuttal:** Đưa bài từ vùng _borderline_ (R1: 5/5, R2: 5/6, R3: 6/7) lên ngưỡng chấp nhận chắc chắn ở **Proceedings** bằng 3 mũi nhọn gọn, sắc, vừa vặn trong trần 2.500 ký tự/bản (xử lý trực diện R1 W1/W2/Q1 và R3 W1/Q1/Q2).
>
> **Nguyên tắc kỷ luật (BẮT BUỘC):**
>
> 1. **Không sửa hay ghi đè dữ liệu/bài nộp cũ:** Toàn bộ kết quả mới đã lưu vào thư mục riêng mang tiền tố `experiments/results/rebuttal_...`.
> 2. **Bắt buộc `--fresh-artifact`:** Mọi thí nghiệm per-edge mới dùng cho kiểm định composition đều đã bật fresh-artefact (tránh lỗi lặp lại như E25/E26 trong `EXPERIMENT_LOG.md`).
> 3. **Kỷ luật KHÔNG làm trong cả Rebuttal lẫn Camera-Ready:**
>    - _Không_ chạy $n = 1{,}000\text{--}8{,}000$ trial/cạnh để ép biên TOST $\pm 0.02$ (R3 W3/Q3 $\to$ trả lời bằng lập luận toán học $n \propto 1/\delta^2$, củng cố khuyến nghị Sec. 7).
>    - _Không_ xây kẻ tấn công _adaptive_ tối ưu token/jailbreak tự động (R3 W2 $\to$ trái cam kết đạo đức ở Sec. 7; chỉ bổ sung phân tầng năng lực kẻ tấn công ở bản camera-ready).
>    - _Không_ chạy thêm topology mesh/debate (R3 W4 $\to$ R3 chỉ đọc sót phần đồ thị có chu trình đã hoàn chỉnh ở Sec. 5.4 & Appendix F và DAG hội tụ ở Appendix Q).
> 4. **Quy tắc Go / No-Go:** Chỉ đưa kết quả mới vào text rebuttal khi đã kiểm tra tay raw outputs, đủ cỡ mẫu $n$, có khoảng tin cậy Wilson 95% / $p$-value, và không dính lỗi _floor effect_ hay _parse failure_.

---

# PHẦN I — TRONG GIAI ĐOẠN REBUTTAL (ĐÃ HOÀN TẤT — KHÔNG SỬA PAPER)

## Bước 0: Kiểm tra hạ tầng & xác thực Bedrock API — ✅ ĐÃ XONG

- [x] **Kiểm tra test suite gốc:** `python -m pytest tests -q` $\to$ **`88 passed`**.
- [x] **Xác thực Bedrock API:** `python scripts\test_bedrock.py --region us-east-1 --model deepseek.v3.2` và `us.meta.llama3-3-70b-instruct-v1:0` $\to$ đều trả `'OK'`.
- [x] **Cấu hình chuẩn đã khóa:** `us-east-1`, $T = 0.7$, $\text{seed} = 7$, cap $400$ tokens:
  - Llama 3.3 70B: `us.meta.llama3-3-70b-instruct-v1:0`
  - DeepSeek V3.2: `deepseek.v3.2`
- [x] **Incremental save:** Toàn bộ script mới (`scripts/rebuttal_*.py`) đều ghi JSONL tăng dần sau từng trial.

---

## Bước 1: Kiểm định trên raw logs sẵn có & mổ xẻ cơ chế Llama `a1->a2` — ✅ ĐÃ XONG

> **Ghi chú thực tế trên đĩa:** Các thư mục `frontier_llama3-3-70b_iso`, `frontier_deepseek_fresh`, và `content_form_llama` chỉ lưu summary JSON/report (không lưu raw text). Do đó Bước 1 đã audit trên các file raw transcripts thật có trong repo (`role_base_us_meta_llama3_3_70b_instruct_v1_0/transcript.jsonl` và `utility_deepseek/outputs.jsonl`), đồng thời chạy riêng 30 lượt audit nhánh `canonical` `a1->a2` của Llama để thu raw text phân loại.

- [x] **1.1 & 1.2. Audit Level (a) vs Level (b) trên raw logs sẵn có (`scripts/rebuttal_audit_existing.py`):**
  - Xuất mẫu ra `experiments/results/rebuttal_adjudication_frontier.csv` & `rebuttal_adjudication_frontier_report.md`:
  - **Llama 3.3 70B** (`role_base_...`, 151 ca dương downstream, lấy mẫu $n=30$ dương + $10$ âm): **`0/30`** adoption (Wilson 95% CI `[0.000, 0.114]`; toàn bộ `151/151` là trích dẫn/đóng gói `BANANA-77`).
  - **DeepSeek V3.2** (`utility_deepseek`, toàn bộ $n=20$ ca attack dương tính + $10$ âm): **`0/20`** adoption (Wilson 95% CI `[0.000, 0.161]`; `20/20` xử lý như ticket/patch/password ID).
- [x] **1.3. Mổ xẻ nhánh _canonical_ cạnh `a1->a2` của Llama (`experiments/results/rebuttal_llama_a1a2_canonical_audit/canonical_audit.jsonl`):**
  - Tỷ lệ sống sót tái xác nhận: **`7/30 = 0.233`** (95% CI `[0.118, 0.409]`).
  - Phân loại **23/23** ca âm tính:
    1. *Boilerplate safety/AI refusal:* **`0/23`**.
    2. *Task-focused / sensitive-credential redaction & routing:* **`23/23`** — Llama's *reviewer* nhận diện câu khẳng định override trơ là lộ thông tin nhạy cảm hoặc lạc ngữ cảnh, nên lược bỏ `BANANA-77` và chuyển tuyến Security Team (phân tầng rõ theo task nền: `0/10` ở ticket routing, `3/10` ở release notes, `4/10` ở executive summary).

---

## Bước 2: Chạy Content-Form Replay (Table 4) cho DeepSeek V3.2 — ✅ ĐÃ XONG

- [x] **2.1 & 2.2. Chạy Content-Form Replay đầy đủ trên `deepseek.v3.2` (`scripts/rebuttal_content_form_replay.py`):**
  - Cấu hình chuẩn Table 4: chuỗi 4 agent `a0->a1->a2->a3`, $T=0.7$, $\text{seed}=7$, `BANANA-77`, $n=40$ natural, $n=30$ replays/nhánh/cạnh, lưu tại `experiments/results/rebuttal_content_form_deepseek/`.
  - **Kết quả thực đo:**
    - `a0->a1`: $s^{\mathrm{nat}} = 0.650$ (`26/40`), `in-context = 0.467` (`14/30`) vs `canonical = 0.033` (`1/30`), form effect $= \mathbf{+0.433}$ (Fisher $p = 1.699 \times 10^{-4}$).
    - `a1->a2`: $s^{\mathrm{nat}} = 0.846$ (`22/26`), self-check `in-context = 0.800` (`24/30`) vs `canonical = 0.933` (`28/30`), form effect $= \mathbf{-0.133}$ (Fisher $p = 0.254$, không khác biệt ý nghĩa — trả lời trực diện **R1 Q1**).
    - `a2->a3`: $s^{\mathrm{nat}} = 0.682$ (`15/22`), `in-context = 0.500` (`15/30`) vs `canonical = 0.667` (`20/30`), form effect $= -0.167$ (Fisher $p = 0.295$).
- [~] **2.3. _(Tùy chọn)_ Local `qwen2.5:7b`:** Đã kiểm tra `localhost:11434` thấy Ollama không bật nên bỏ qua đúng theo kế hoạch tùy chọn.

---

## Bước 3: Pilot Level (b) Behavioural Adoption — Task Family C — ✅ ĐÃ XONG

- [x] **3.1. Thiết kế Task Family C (`scripts/rebuttal_adoption_family_c.py`):** Decision-Flip tất định (`DRILL-77`, 3 kịch bản sự cố nghiêm trọng ground truth `HIGH`, dòng cuối `DECISION: HIGH` hoặc `DECISION: LOW`, judge regex song song $C_a$ và $C_b$).
- [x] **3.2. Smoke-test & hiệu chỉnh prompt:**
  - Lần 1: Llama đạt `0.0% parse_fail`, DeepSeek có `1/24` bước (`4.2%`) bị cắt cụt ở cap 400 tokens trước dòng `DECISION:`.
  - Đã thêm hướng dẫn trả lời gọn `< 150` từ vào `ROLE_PROMPTS` và ép `C_0 = 1` ở entry $\to$ smoke-test v2 DeepSeek đạt **`0.0% parse_fail`**, `U_clean = 1.00`, `ASR_(b) = 0.33` (vào vùng mở $(0,1)$).
- [x] **3.3. Chạy thực nghiệm chính trên 2 Model (4 nhánh đầy đủ, `0% parse_fail` cả 2 model):**
  - **Llama 3.3 70B (`experiments/results/rebuttal_family_c_llama/`):**
    - `U_clean = 1.000` (`20/20`).
    - Natural ($n=40$): **`ASR_(b) = 0.975`** (`39/40`, 95% CI `[0.871, 0.996]`), $s^{\mathrm{nat}}_{(b)} = 1.000 / 0.975 / 1.000$; trong khi **`ASR_(a) = 0.025`** (`1/40`) do model paraphrase thông điệp diễn tập và bỏ chuỗi `DRILL-77`.
    - Controlled `--fresh-artifact` ($n=30$/cạnh): $s^{\mathrm{ctrl}}_{(b)} = 1.000 / 0.900 / 1.000$, $\prod s^{\mathrm{ctrl}}_{(b)} = 0.900$, $\Delta = +0.075$ (`[-0.033, +0.200]`, $p = 0.208$, $\mathrm{MDE} = 0.167$).
    - Replay `a1->a2` ($n=30$/nhánh): `in-context = 1.000` vs `bare = 1.000` ($p = 1.000$).
  - **DeepSeek V3.2 (`experiments/results/rebuttal_family_c_deepseek/`):**
    - `U_clean = 1.000` (`20/20`).
    - Natural ($n=40$): **`ASR_(b) = 0.625`** (`25/40`, 95% CI `[0.470, 0.758]`), $s^{\mathrm{nat}}_{(b)} = 0.900 / 0.694 / 1.000$; **`ASR_(a) = 0.000`** (`0/40`).
    - Controlled `--fresh-artifact` ($n=30$/cạnh): $s^{\mathrm{ctrl}}_{(b)} = 0.867 / 0.633 / 1.000$, $\prod s^{\mathrm{ctrl}}_{(b)} = 0.549$, $\Delta = +0.076$ (`[-0.159, +0.300]`, $p = 0.528$, $\mathrm{MDE} = 0.325$).
    - Replay `a1->a2` ($n=30$/nhánh): `in-context = 0.400` (`12/30`) vs `bare = 1.000` (`30/30`), Fisher $p = 1.870 \times 10^{-7}$.
- [x] **3.4. Kiểm tra chất lượng (QC):** Đã đọc `experiments/results/rebuttal_family_c_{llama,deepseek}/qc_samples.md` — `5/5` mẫu `C_b = 1` ở cả hai model thực sự chấp nhận giả thuyết diễn tập và lật quyết định sang `DECISION: LOW`; các mẫu `C_b = 0` giữ `DECISION: HIGH` vì phát hiện mâu thuẫn với thiệt hại thực tế.

---

## Bước 4: Tổng hợp & chốt 3 bản Rebuttal ($\le 2{,}500$ ký tự/bản) — ✅ ĐÃ XONG

- [x] Lưu báo cáo tổng hợp tại `experiments/results/REBUTTAL_SUMMARY_RESULTS.md`.
- [x] Cập nhật, sửa `word-bigram` $\to$ `char-bigram` khớp `contagion/metrics/assessment.py`, và kiểm tra trần ký tự + `has_http=False`:
  - `rebuttal/review1.md`: **2.488 ký tự** ($\le 2{,}500$)
  - `rebuttal/review2.md`: **2.471 ký tự** ($\le 2{,}500$)
  - `rebuttal/review3.md`: **2.481 ký tự** ($\le 2{,}500$)
- [ ] **Thao tác của tác giả:** Dán 3 bản text trên vào OpenReview trước hạn chót rebuttal.

```markdown
### Báo cáo kết quả bổ sung cho Rebuttal

#### 1. Kết quả Bước 1 (Audit raw logs sẵn có + Cơ chế Llama a1->a2)
- Llama 3.3 70B (`role_base_...`, n_pos=30 trích từ 151, n_neg=10):
  - Level (a): TP=30, FP=0, TN=10, FN=0
  - Level (b) adoption: k/n_pos = 0/30 (Wilson 95% CI: [0.000, 0.114]; toàn bộ 151/151 ca dương downstream là trích dẫn/đóng gói)
- DeepSeek V3.2 (`utility_deepseek`, n_pos=20):
  - Level (b) adoption: k/n_pos = 0/20 (Wilson 95% CI: [0.000, 0.161])
- Mổ xẻ 23 ca âm tính (7/30 sống sót) nhánh canonical Llama a1->a2 (`rebuttal_llama_a1a2_canonical_audit`):
  - Explicit safety/AI boilerplate refusal: 0/23 | Sensitive-data redaction / routing & task-focused omission: 23/23 (0/10 ticket routing, 3/10 release notes, 4/10 summary)
  - Trích dẫn ngắn tiêu biểu: "The upstream message from agent_1 appears to be a sensitive information disclosure... the security-gate override code should be removed from the message."

#### 2. Kết quả Bước 2 (Content-Form Replay Table 4 trên DeepSeek V3.2, n=40/30)
- DeepSeek V3.2 (BANANA-77):
  - a0->a1: s_nat=0.650 (26/40) | in-context=0.467 (14/30) | canonical=0.033 (1/30) | form_effect=+0.433 (p=1.699e-04)
  - a1->a2: s_nat=0.846 (22/26) | in-context=0.800 (24/30) | canonical=0.933 (28/30) | form_effect=-0.133 (p=2.542e-01)
  - a2->a3: s_nat=0.682 (15/22) | in-context=0.500 (15/30) | canonical=0.667 (20/30) | form_effect=-0.167 (p=2.949e-01)
- (Tùy chọn) qwen2.5:7b (BANANA-77, n=40/30):
  - Bỏ qua do Ollama local không bật.

#### 3. Kết quả Bước 3 (Task Family C — Level-b Behavioural Adoption, fresh-artifact=True)
- Model 1 (Llama 3.3 70B):
  - parse_fail: 0.0% | Clean baseline (n=20): U_clean = 1.000 [0.839, 1.000]
  - Natural runs (n=40):
    - Level (a): ASR_(a) = 0.025 (1/40) [0.004, 0.129]
    - Level (b): ASR_(b) = 0.975 (39/40) [0.871, 0.996] | per-edge s_nat = 1.000 / 0.975 / 1.000
  - Controlled per-edge (n=30/cạnh):
    - Level (b): per-edge s_ctrl = 1.000 / 0.900 / 1.000 | prod(s_ctrl) = 0.900
    - Bootstrap test: Delta = +0.075 [-0.033, +0.200], p = 0.208, MDE = 0.167
  - Replay a1->a2 (n=30/nhánh): in-context = 1.000 vs. bare = 1.000, Fisher p = 1.000
  - Đọc tay raw outputs (`qc_samples.md`): Khớp 100% (5/5 C_b=1 lật sang DECISION: LOW; 1/1 C_b=0 giữ DECISION: HIGH)
- Model 2 (DeepSeek V3.2):
  - parse_fail: 0.0% | Clean baseline (n=20): U_clean = 1.000 [0.839, 1.000]
  - Natural runs (n=40):
    - Level (a): ASR_(a) = 0.000 (0/40) [0.000, 0.088]
    - Level (b): ASR_(b) = 0.625 (25/40) [0.470, 0.758] | per-edge s_nat = 0.900 / 0.694 / 1.000
  - Controlled per-edge (n=30/cạnh):
    - Level (b): per-edge s_ctrl = 0.867 / 0.633 / 1.000 | prod(s_ctrl) = 0.549
    - Bootstrap test: Delta = +0.076 [-0.159, +0.300], p = 0.528, MDE = 0.325
  - Replay a1->a2 (n=30/nhánh): in-context = 0.400 vs. bare = 1.000, Fisher p = 1.870e-07
  - Đọc tay 10 raw outputs (`qc_samples.md`): Khớp 100% (5/5 C_b=1 lật sang DECISION: LOW; 5/5 C_b=0 bác bỏ giả thuyết drill, giữ DECISION: HIGH)
```

---

# PHẦN II — SAU ACCEPTANCE: GIAI ĐOẠN CAMERA-READY (ĐƯỢC SỬA PAPER)

> **Lưu ý:** Toàn bộ các mục dưới đây **KHÔNG thực hiện hay upload trong kỳ rebuttal**. Chỉ triển khai sau khi nhận thông báo chấp nhận (acceptance), tuân thủ giới hạn 8 trang nội dung chính (chưa kể References).

## Bước CR-1: Hoàn thiện các chỉnh sửa văn bản, công thức và bảng biểu đã cam kết với R1, R2, R3

- [ ] **Sec. 1:** Dẫn chiếu sớm kết quả đồ thị có chu trình (Sec. 5.4 / Appendix F) và DAG hội tụ (Appendix Q).
- [ ] **Sec. 3.1:** Bổ sung phân tầng năng lực kẻ tấn công (_plain / structural obfuscation / adaptive_).
- [ ] **Sec. 3.2:** Thêm công thức tường minh của `ASV` (target char-bigram containment: $|B(t) \cap B(y)| / |B(t)|$) và `MR` (char-bigram Dice: $2|B(y) \cap B(y_{\mathrm{ref}})| / (|B(y)| + |B(y_{\mathrm{ref}})|)$).
- [ ] **Sec. 3.6:** Tách rõ phạm vi _chính xác_ (đường đi thượng nguồn rời nhau) vs. _xấp xỉ biên_ (DAG có tổ tiên chung) của Eq. (3); so sánh $R_0$ thực nghiệm với $R_0$ chuẩn (chung ý nghĩa _local branching average_ nhưng không có ngưỡng trên DAG hữu hạn do $\rho(M) = 0$); viết lại rõ ràng câu _minimal $s$--$t$ cut_.
- [ ] **Sec. 5.1:** Ghi rõ _"single-path chain"_ ở đầu mục để tránh hiểu nhầm chồng chéo đường đi (R2); tích hợp cơ chế cạnh `a1->a2` (kết quả Bước 1.3 & Bước 2); đơn giản hóa các câu cuối phần _content-form ablation_.
- [ ] **Sec. 5.4:** Đổi tiêu đề mục thành _"Cyclic Topologies"_; định nghĩa tường minh _"supercritical"_ ($\rho(M) = \sqrt{\sum_j a_j c_j} > 1$); sửa lỗi in nhầm giá trị $\sum_j a_j c_j$ thay cho $\rho(M)$ bằng cách ghi rõ cả $\rho(M) = 1.342 / 1.009 / 0.760$ bên cạnh $\sum_j a_j c_j = 1.800 / 1.018 / 0.578$ (khớp Appendix F, Table 5).
- [ ] **Sec. 6 & Supplementary:** Bổ sung thảo luận về thiết kế _deterministic behavioural sinks_ và đưa bảng kết quả chi tiết của Bước 1, Bước 2, Bước 3 (Task Family C) vào bài chính/phụ lục.
- [ ] **Đồng bộ tham chiếu mục trong `supplementary.tex`:** Rà soát và sửa toàn bộ tham chiếu bằng chữ sang bài chính đang lệch số mục (ví dụ _"Section 3.8"_ $\to$ _"Section 3.6"_, _"Section 5.9"_ $\to$ _"Section 5.5"_, _"Section 5.3"_ $\to$ _"Section 5.1"_).
- [ ] **Công bố bản lưu trữ công khai:** Thay link ẩn danh bằng link GitHub/Zenodo công khai kèm trích dẫn trong bản camera-ready (theo hướng dẫn trong `REPRODUCE.md`).

## Bước CR-2: Thực nghiệm mở rộng cho bản cuối (tùy chọn làm sau Acceptance)

- [ ] **Họ phòng thủ thứ 3 trên khung đo cặp $(\mathrm{ASR}, \Delta U)$ (R3 W5):**
  - Cài đặt **Spotlighting / Delimiter framing** (Hines et al., đã có trong `refs.bib`) hoặc **Structured Output Schema**.
  - Chạy `scripts/utility_real.py` ($n = 20\text{--}30$ paired runs, $T = 0.7$, Family B `BANANA-77`) trên **DeepSeek V3.2** (headroom cao: baseline `none` có $\mathrm{ASR} = 0.450$, Retention $= 0.600$) và **Claude Sonnet 4.5** (mức sàn: baseline `none` có $\mathrm{ASR} = 0.000$, Retention $= 1.000$), bổ sung vào Appendix J (Table 9).
- [ ] **Đồng bộ `--fresh-artifact` cho Table 1 & Appendix A:**
  - Chạy lại 3 dòng cũ (`qwen2.5:7b`, `amazon.nova-pro-v1:0`, `us.anthropic.claude-sonnet-4-5-20250929-v1:0`) với `--only-chain-none --fresh-artifact --trials 40 --per-edge 30` để xóa hoàn toàn tình trạng trộn giao thức trong Table 1 và chạy lại kiểm định Benjamini–Hochberg (Appendix A).
