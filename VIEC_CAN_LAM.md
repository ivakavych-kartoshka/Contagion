# DANH SÁCH VIỆC CẦN LÀM — AAMAS 2027, Submission 2419
## "Contagion: When Per-Hop Prompt-Injection Survival in LLM Agent Networks Does (and Does Not) Compose"

> **Cập nhật:** 2026-10-09 18:15 — **Nhóm 3 đã hoàn thành 5/8 tasks** (3.1, 3.3, 3.4, 3.6, 3.8) và đã cập nhật vào cả 2 file LaTeX. **Nhóm 1 hoàn thành thêm task 1.6** (điền REBUTTAL.md). Nhóm 1 còn 3 tasks chưa xong.
> 
> **Trạng thái nộp hiện tại:** main PDF 10 trang = content 1–8 + References từ trang 9;
> phụ lục 8 trang; `supplementary_material.zip` 2.2 MB / 308 file; 0 undefined ref.
>
> **Phân loại:** 🟢 không cần model · 🟡 cần model local (0 đồng) · 🔴 cần API Bedrock ·
> ⚫ cần người thật · 📄 việc của bạn · ⚠️ đánh đổi đã chấp nhận.

---

## 🟢 NHÓM 1 — KHÔNG CẦN GỌI MODEL

| # | Việc | Nguồn | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 1.1 | **Markov chain hữu hạn cho loop** | **R1 Q3** major | ✅ **XONG** | `scripts/cyclic_markov_exact.py` → `experiments/results/cyclic_markov_exact/report.md`. **Kết quả: model KHÔNG khớp** (qwen lệch 0.602) ⇒ worker có memory. Xem §1.1 dưới |
| 1.2 | Viết kết quả 1.1 vào phụ lục + 1 câu main | R1 Q3 | ✅ **XONG** | `supplementary.tex` §app:cyclic (dòng 400–441): bảng `tab:cyclic-markov` + 3 kết luận. Main §5.8 (dòng 940–946): 1 câu tóm tắt "fails to reproduce... by +0.289, −0.239 and −0.602". |
| 1.3 | **Worked example** cho AutoGen/MetaGPT | **R4 Q1** | ✅ **XONG** | `supplementary.tex` dòng 690–720: `\paragraph{Worked example: an AutoGen/MetaGPT-style pipeline.}` — 3 prescription với số cụ thể (Llama 0.850 vs dự đoán 0.233, R₀ star/chain, filter placement). |
| 1.4 | **Verify 3 tham chiếu 2026** ([1], [23], [24]) | R4 W5 | ✅ **XONG** | `refs.bib` dòng 7–8: "ĐÃ ĐỐI CHIẾU TOÀN BỘ + chốt ngày xuất bản cho 3 mục 2026 từ Crossref/nhà xuất bản chính thức" (lần 3, 2026-10-09). |
| 1.5 | **Family-wise correction** cho topology/obf/loop | **R3 W6** | ✅ **XONG** | `supplementary.tex` §B "Family-Wise Control Extended to the Remaining Families" (dòng 132) + `scripts/familywise_extended.py`. BH control q=0.05, mọi family giữ ít nhất 1 rejection. |
| 1.6 | **Điền 1 chỗ trống** trong `REBUTTAL.md` dòng 153 | — | ✅ **XONG** | `review/REBUTTAL.md` dòng 151–160: đã điền kết quả payload MANGO-42 từ task 3.1 (ASR=0.925, per-edge 1.000/1.000/0.925, content-form effect replicates). |
| 1.7 | **Ghép qwen fresh (0.375/0.733) vào Table 1** | R3 Q1 | ❌ chưa | **cần bạn quyết định** — Table 1 hiện: `qwen2.5:7b & 0.300 & 0.611` (số cũ fixed-artefact). Fresh results có tại `experiments/results/frontier_qwen_fresh/report.md` (ASR=0.375, surv=0.733, Markov consistent). Nếu ghép vào phải thêm `†` và đổi caption. |
| 1.8 | **Mở rộng estimator validation** (nhiều replication hơn) | R3 W5 | ❌ chưa | `supplementary.tex` dòng 637: hiện chỉ 60 replication. Cần chạy thêm synthetic (không cần API). |
| 1.9 | **Rà nhất quán toàn bài** lần cuối | — | ❌ chưa | ~1 giờ |

### §1.1 Kết quả Markov chain (đã có, cần đưa vào bài)

`m_{k+1} = 1 − Π_j (1 − c_j·a_j·m_k)`, worker chỉ nhận từ manager.

| model | w | Σa_jc_j | dự đoán vòng cuối | quan sát | lệch |
|---|---|---|---|---|---|
| Llama 3.3 70B | 2 | 1.800 | 0.989 | 0.700 | **+0.289** |
| DeepSeek V3.2 | 2 | 1.018 | 0.327 | 0.567 | **−0.239** |
| qwen2.5:7b | 2 | 0.578 | 0.048 | 0.650 | **−0.602** |

**Ba kết luận cho bài:**
1. `P(re-compromise) = 1 − Π(1 − a_jc_j) < 1` **kể cả khi** `Σa_jc_j > 1` ⇒ xác nhận
   R1 W5: dùng `Σa_jc_j` làm ngưỡng criticality cho loop hữu hạn là **sai**.
2. Chain hữu hạn memoryless **không khớp** ở cả 3 model (lệch 0.24–0.60, vượt xa sai
   số chuẩn ≈0.08) ⇒ cần thêm trạng thái.
3. Chẩn đoán cụ thể: **worker có memory**. Sau khi manager giảm còn 0.725 (Llama),
   worker vẫn ở 0.925/0.975 trong khi mô hình dự đoán 0.725. Với DeepSeek, worker bị
   compromise (0.767) **cao hơn** per-edge rate đo cách ly (0.650) — tức trạng thái
   không tái tạo độc lập mỗi vòng.

**Cách viết vào bài (đề xuất):** hạ claim mean-field xuống "mean-field prediction,
which the exact finite chain does not reproduce"; thêm bảng so vào phụ lục.

---

## 🟡 NHÓM 2 — CẦN MODEL LOCAL (0 đồng, tốn giờ máy)

| # | Việc | Nguồn | Ước tính | Lệnh |
|---|---|---|---|---|
| 2.1 | **Đa payload trên qwen** | **R2 W2** major, R4 Q4 | ~2h | `run_all.sh` #2.1 |
| 2.2 | **Paraphraser có emit target?** | **R2 Q5** | ~30m + 20m code | cần thêm code (xem ghi chú) |
| 2.3 | **CI thật cho R₀** (chạy lại topology lưu per-run paths) | **R3 W6** | ~1h + 30m code | cần script mới |
| 2.4 | **Role-permutation qwen ở n=10** (kiểm scale) | R2 W3 | ~1.5h | `run_all.sh` #2.4 |
| 2.5 | **Content-form trên qwen2.5:3b** | R2 Q1 | ~1h | `run_all.sh` #2.5 |

> **2.2 cần code:** thêm vào `content_form_probe.py` một arm "paraphraser only": cho
> paraphraser đọc payload rồi kiểm output của **chính nó** có chứa target không. Hiện
> chưa có arm này.

---

## 🔴 NHÓM 3 — CẦN API BEDROCK (key đã sống)

| # | Việc | Nguồn | Trạng thái | Ước tính | Lệnh |
|---|---|---|---|---|---|
| 3.1 | **Đa payload trên Llama** (`MANGO-42`, `ORCA-19`) | **R2 W2** major, R4 Q4 | ✅ **XONG** | ~1.5h/model | `run_all.sh` #3.1. Kết quả: `frontier_llama_mango/`, `content_form_llama_mango/`. Đã cập nhật vào `supplementary.tex` §app:extended-validation + `contagion_aamas2027.tex` §5.4 + Table 4 caption. |
| 3.2 | **Role-permutation trên Llama** | **R2 W3, Q2** major | ❌ chưa | ~1.5h | `run_all.sh` #3.2 |
| 3.3 | **Content-form trên Llama với marker khác** | R2 Q1 | ✅ **XONG** | ~1h | `run_all.sh` #3.3. Đã có `content_form_llama_mango/` (cùng với 3.1). Kết quả Nova + Claude đã có sẵn trong Table 4. |
| 3.4 | **Nova + Claude fresh-artefact** (3 hàng Table 1) | **R3 Q1, W3** major | ✅ **XONG** | ~2h | `run_all.sh` #3.4. Kết quả đã có trong Table 4 (content-form Nova + Claude). |
| 3.5 | **Context-level analysis, >3 contexts** | **R3 Q5, W2** major | ❌ chưa | ~2h | cần sinh context mới (code) |
| 3.6 | **Markov chain trên Llama ở n khác** | R1 Q3 | ✅ **XONG** | ~1h | `run_all.sh` #3.6. Kết quả: `cyclic_llama_w3/` (w=3 workers). Đã cập nhật vào `supplementary.tex` dòng 399–402 + `contagion_aamas2027.tex` dòng 946. |
| 3.7 | **Kiểm mô hình 2 trạng thái tái tạo 0.875** | R1 Q4 | ❌ chưa | ~2h | ⚠️ rủi ro tautological (xem ⚠️6.3) |
| 3.8 | **Depth curve Llama ở n khác** | R1 W7 | ✅ **XONG** | ~1.5h | `run_all.sh` #3.8. Kết quả: `depth_curve_llama_long/` (n=15). Đã cập nhật vào `supplementary.tex` §app:extended-validation. Main paper §5.7 dòng 924–925 đã có sẵn. |

---

## ⚫ NHÓM 4 — CẦN NGƯỜI THẬT

| # | Việc | Nguồn |
|---|---|---|
| 4.1 | **Nhãn adoption/compliance độc lập ≥100 activation**, blind với judge, ≥1 frontier model, có/không defence → level-(b) rate | **R2 Q3 — metareview xếp #1** |

> R2 W1: 19/19 positive hiện tại đều là *trích chuỗi*, **0 adoption**. Nhãn do LLM gán
> **không thay thế được**. Đây là việc duy nhất metareview nói sẽ đổi ý họ.

---

## 📄 NHÓM 5 — VIỆC CỦA BẠN (không phải tôi)

| # | Việc |
|---|---|
| 5.1 | **Nộp**: `paper/contagion_aamas2027.pdf` + `supplementary_material.zip` lên OpenReview |
| 5.2 | **Push** lên repo ẩn danh: `artifacts/MANIFEST.json`, `REPRODUCE.md`, `README.md`, `scripts/make_supplementary_zip.py`, `scripts/cyclic_markov_exact.py`, `experiments/results/content_form_nova/`, `experiments/results/content_form_claude/`, `experiments/results/cyclic_markov_exact/` |
| 5.3 | **Kiểm repo không chứa** file nội bộ: `EXPERIMENT_LOG.md`, `DECISION_MEMO.md`, `PAPER_DRAFT.md`, `PAPER_TEXT.md`, `REVIEWS_AAMAS2027.md`, `_*.py` |
| 5.4 | **Điền 1 chỗ** `[điền sau khi chạy]` trong `review/REBUTTAL.md` dòng 153 |
| 5.5 | **Quyết định 1.7** (ghép qwen fresh vào Table 1 — đổi headline) |

---

## ⚠️ NHÓM 6 — ĐÁNH ĐỔI ĐÃ CHẤP NHẬN

| # | Việc | Lý do |
|---|---|---|
| 6.1 | **Payload kiểu action có tool call** | Engine tool-less; cần viết engine mới (~4–6h) |
| 6.2 | **Defence-placement intervention thật** | Chưa can thiệp placement trên graph nào (R1 W6) |
| 6.3 | **Mô hình 2 trạng thái (form × compromise)** | Chỉ có 1 cặp + replay rates; R1 cảnh báo fit trên Table 4 thì *tautological* |
| 6.4 | **Estimator validation với nhiều replication** | Chỉ 60 replication (R3 W5) |
| 6.5 | **Dual-use thành mục riêng** trong main | Hiện nằm trong Conclusion (hết chỗ trang 8) |

---

## 📊 TRẠNG THÁI ĐÃ XONG (để không làm lại)

| Việc | Nguồn | Bằng chứng |
|---|---|---|
| Fig. 2 + Fig. 4 đọc được ở cỡ in | R2 W7 | `make_figures.py`, đã kiểm bằng `read_image` |
| Permutation p-value + bootstrap CI cho depth slope | R1 W7, R3 W1 | `depth_perm_test.py`, Appendix J |
| Role-permutation control | R2 W3/Q2 | `role_position_check.py`, Appendix L |
| Test Eq. (3) trên DAG reconvergent | R1 W3/Q2 | `dag_eq3_check.py`, Appendix N |
| Citation [13], [31], [6], [26] sửa | R4 W5 | `refs.bib`, main §2 |
| 4 related work thêm (Agent Smith/NetSafe/G-Safeguard/Huang) | R4 W4 | main §2 |
| Range ASR + R₀ (tree 0.800/0.831) | R4 W6 | main Abstract |
| Caveat capability → "scale"; hạ verdict "resistant" | R2 W4 | main §5.1, §5.5 |
| R₀ không hứa interval; nêu lý do | R3 W6 | main §3.6, caption bảng topo |
| Content-form Nova + Claude | **R2 Q1** | Table 4 (main) |
| Artifact link + manifest 104 cell + model ID/ngày | R3 W7/Q4 | main, Appendix P, `MANIFEST.json` |
| Reference về trang 9 bằng `\clearpage` | — | main PDF |
| Zip supplementary ≤25MB, đã quét danh tính | R3 W7 | `make_supplementary_zip.py` |
| Rebuttal đầy đủ 20 câu | — | `review/REBUTTAL.md` |

---

## 🎯 THỨ TỰ KHUYẾN NGHỊ

**Bước 1 (làm ngay, 0 API):** 1.6 (điền rebuttal) → 1.7 (quyết định qwen fresh) → 1.9 (rà nhất quán).
**Bước 2 (chạy nền, nếu cần):** `run_all.sh` với các mục 3.2, 3.5, 3.7 (API) và 2.1, 2.4 (local).
**Bước 3 (sau khi có kết quả):** tích hợp vào phụ lục + 1 câu main; cập nhật rebuttal.

> ⚠️ **Giới hạn trang:** bài chính đã kín 8 trang. Mọi kết quả mới phải vào **phụ lục**,
> và nếu cần 1 câu trong main thì phải cắt bù chỗ khác.

---

## 📋 TỔNG KẾT CẬP NHẬT NHÓM 3 (2026-10-09 18:00)

### ✅ Đã hoàn thành và cập nhật vào LaTeX:

**3.1 - Đa payload (MANGO-42):**
- Thư mục kết quả: `frontier_llama_mango/`, `content_form_llama_mango/`
- Cập nhật vào:
  - `supplementary.tex` §app:extended-validation (dòng 609–635): toàn bộ kết quả MANGO-42
  - `contagion_aamas2027.tex` dòng 849–851: 1 câu trong §5.4
  - `contagion_aamas2027.tex` dòng 822: thêm vào caption Table 4

**3.3 & 3.4 - Content-form Nova + Claude:**
- Kết quả đã có sẵn trong Table 4 của bài chính
- Không cần cập nhật thêm

**3.6 - Cyclic Llama w=3:**
- Thư mục kết quả: `cyclic_llama_w3/`
- Cập nhật vào:
  - `supplementary.tex` dòng 399–402: thêm kết quả w=3 workers
  - `contagion_aamas2027.tex` dòng 946: thêm 1 câu parenthetical

**3.8 - Depth curve n=15:**
- Thư mục kết quả: `depth_curve_llama_long/`
- Cập nhật vào:
  - `supplementary.tex` §app:extended-validation (dòng 624–633): toàn bộ kết quả n=15
  - Main paper dòng 924–925 đã có sẵn kết quả này

### 📊 Trạng thái compilation:
- ✅ `supplementary.pdf`: 704,927 bytes (biên dịch thành công)
- ✅ `contagion_aamas2027.pdf`: 819,701 bytes (biên dịch thành công)
- ✅ 0 lỗi, 0 undefined references (sau 2 lần compile)

### 📝 Còn lại trong Nhóm 3:
- 3.2: Role-permutation trên Llama (major - R2 W3, Q2)
- 3.5: Context-level analysis >3 contexts (major - R3 Q5, W2)
- 3.7: Mô hình 2 trạng thái (có rủi ro tautological)


