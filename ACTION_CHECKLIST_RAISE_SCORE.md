# ACTION CHECKLIST — Raising the Overall Score

> **Nguồn:** dẫn xuất trực tiếp từ `REVIEWS_AAMAS2027.md` (4 review + metareview).
> Mỗi việc trỏ về weakness/question/required-change gốc (vd `R2 W1`, `C1`) để truy vết.
> **Không phải văn bản nộp** — đây là bảng việc nội bộ.

## Điểm hiện tại & mục tiêu

| Review | Persona | Overall hiện tại | Rào cản chính | Mục tiêu sau sửa |
|---|---|---|---|---|
| R1 | MAS theorist | **6 — Accept** | title overclaim (W1); cyclic 1 instance (W2) | 6–7 |
| R2 | Security | **5 — Weak accept** | 1 payload + attacker tĩnh (W1); cell n=8/16 (W2) | 6 |
| R3 | Reproducibility | **6 — Accept** | power n=30–40 (W1) | 6–7 |
| R4 | Generalist | **4 — Borderline** | title vs evidence (W1); significance ceiling (W2) | 5 |
| — | **Decision** | **Conditional Accept (shepherded)** | 7 required changes C1–C7 | **Accept** vững |

**Đòn bẩy lớn nhất để nâng overall:** (1) sửa **title/abstract overclaim** — điểm bị *cả 4* review nhắc (R1 W1, R4 W1, checklist #2), rẻ và nâng ngay R4 + Clarity của mọi review; (2) **bound coverage** (payload + n nhỏ) — nâng R2 và Significance của R4. Hai nhóm này quyết định việc lên Accept vững.

---

## TIER 0 — Bắt buộc để đóng "Conditional" (0 API, làm ngay)

Đây chính là 7 required change của metareview. Làm xong nhóm này là đủ điều kiện chuyển Conditional Accept → Accept.

- [x] **T0.1 — Rescope title + abstract về claim có điều kiện.** ✅ (title → *"Does (and Does Not) Compose"*; abstract result (i) nêu rõ composition là identity, DeepSeek transports p=0.93 vs Llama fails 3.75× p=0.0002)
  - Đổi title: bỏ tuyệt đối hoá "Does Not Compose" → dạng có điều kiện, vd
    *"When Per-Hop Prompt-Injection Survival Does (and Does Not) Compose in LLM Agent Networks"*
    hoặc giữ tên ngắn + subtitle *"isolated per-hop estimates need not transport; the depth-slope diagnoses when"*.
  - Sửa abstract: nêu rõ **DeepSeek transports (Δ=−0.009, p=0.930)** còn **Llama fails on one edge (3.75×)** — composition là *identity*, cái fail là *transportability của ước lượng isolated*.
  - ↑ nâng: **Clarity (mọi review), R4 Overall 4→5, R1 W1 đóng**. Chi phí: ~30 phút, 0 API.

- [x] **T0.2 — Ghi MDE cạnh mọi verdict "consistent/holds".** ✅ (§5.2: DeepSeek "non-rejection at MDE≈0.26, n=40; không phải proven equal" vs Llama powered positive MDE=0.11)
  - Với mỗi ô báo "transportability holds"/"consistent", thêm MDE (vd "n=40, MDE≈0.26 → non-rejection, không phải bằng chứng bằng nhau").
  - Giữ n=200 powered positive làm headline.
  - ↑ nâng: **Soundness/Clarity, R3 W1 đóng**. 0 API.

- [x] **T0.3 — Chỉ rõ claim nào phụ thuộc cell n=8/16 và kiểm nó sống sót khi bỏ.** ✅ (§5.5 Scope: cross-model claims dựa trên Claude n=30 + chain cells, không đổi nếu bỏ 2 panel nhỏ)
  - Chạy lại phân tích Fig. 2 **loại** ô DeepSeek n=8 và qwen n=16; liệt kê câu §5.5/§5.6 nào dựa vào chúng; nếu kết luận đổi → nới caveat.
  - ↑ nâng: **R2 Overall 5→6 (một phần), Soundness**. 0 API (đọc lại dữ liệu đã có).

- [x] **T0.4 — Hoà giải giả định độc-lập-cạnh (§3.8) với χ² bác bỏ exchangeability (§5.7).** ✅ (§3.8: independence là giữa edge-activations; identity là marginal; heterogeneity theo context chỉ ảnh hưởng variance → App B)
  - Thêm 1–2 câu: identity là **biên (marginal)** đúng theo xác suất; χ² bác bỏ ở mức **điều kiện theo context**; hai mức không mâu thuẫn.
  - ↑ nâng: **Soundness (R1), khép mâu thuẫn hình thức**. 0 API.

- [x] **T0.5 — Nói rõ depth-slope diagnostic sạch nhất trên model local (qwen2.5:7b); nêu có replicate trên frontier không.** ✅ (§5.7: slope sạch nhất trên qwen 7B; Llama chết depth 11, DeepSeek phẳng → chỉ "sign of trend" transfer)
  - Một câu ở §5.7: slope +11.8 pp/hop là trên qwen 7B; Llama chết ở depth 11; DeepSeek phẳng → khẳng định phạm vi.
  - ↑ nâng: **Clarity/Soundness, R3 W3 đóng**. 0 API.

- [x] **T0.6 — Xác minh 0-API artifact tier + seed/snapshot table.** ✅ (audit_numbers khớp: Llama 0.850/0.233, DeepSeek 0.400/0.409; REPRODUCE.md §5 bổ sung bảng model-snapshot + seed note. De-anonymise để camera-ready.)
  - Chạy toàn bộ pipeline 0-API, đối chiếu từng bảng/hình với bản trong PDF.
  - Thêm phụ lục nhỏ: seed + ngày snapshot model hosted cho mỗi ô headline.
  - (Camera-ready) đổi `\documentclass[sigconf]{aamas}`, điền tác giả + `\begin{acks}`.
  - ↑ nâng: **Reproducibility → badge (R3 confidential rec), R3 W4 đóng**. 0 API.

- [x] **T0.7 — Nêu rõ phạm vi defence = literal-DLP + paraphrase (static attacker).** ✅ (§5.5 Scope: 2 defence, attacker tĩnh; learned/semantic detector + adaptive attacker out of scope. Bản thêm detector = T2.5, cần API.)
  - Rẻ nhất: 1 câu ở §5.5 giới hạn phạm vi phòng thủ.
  - Mạnh hơn: thêm 1 detector semantic/learned (cần API — xem T2).
  - ↑ nâng: **R2 W3 đóng (nếu chỉ scope), hoặc R2 Overall (nếu thêm detector)**. 0 API cho bản scope.

---

## TIER 1 — Trả lời trong REBUTTAL (20–24 Nov 2026, 0 API, dùng dữ liệu đã có)

Không sửa bài; chuẩn bị câu trả lời đanh thép cho các câu hỏi reviewer. Trả lời tốt nhóm này là cách trực tiếp kéo R4 4→5 và R2 5→6.

- [ ] **T1.1 — Cam kết rescope title/abstract (trả lời R4 Q1, R1 Q1).**
  Nói thẳng trong rebuttal rằng sẽ đổi title về dạng có điều kiện (đồng bộ T0.1). Đây là điều R4 hỏi trực tiếp và là lý do chính khiến R4 ở mức 4.

- [ ] **T1.2 — Nêu "kết quả tổng quát nhất nếu chỉ được giữ một" + số (model,edge) hỗ trợ ngoài n=40 (R4 Q2).**
  Trả lời: **content-form mechanism** (§5.4, 14×) + **transport failure powered ở n=200** (§5.2). Đưa số cặp (model,edge) đã đo.

- [ ] **T1.3 — Delta so với công trình hierarchical-chain đồng thời, trong 1 đoạn (R4 Q3, R2 gián tiếp, checklist #7/#14).**
  Nhấn: per-hop **decomposition** (không phải aggregate rate) + chứng minh **`ρ(M)=0` vacuity** + **identity vs transportability** — 3 điểm không có ở prior work (§2).

- [ ] **T1.4 — Độ nhạy theo payload (R2 Q1).**
  Nếu chưa có dữ liệu đa-payload: cam kết bound bằng 2–3 target benign khác (chuyển thành T2.1). Nếu có sẵn probe nào → trích ngay.

- [ ] **T1.5 — Cross-model defence claims sống sót khi bỏ n=8/16 (R2 Q2, R3 Q1).**
  Trình kết quả T0.3 ngay trong rebuttal (bảng đối chiếu có/không có ô nhỏ).

- [ ] **T1.6 — Xác nhận 0-API tier tái tạo mọi bảng/hình (R3 Q2).**
  Đưa log chạy `REPRODUCE` (kết quả T0.6) làm bằng chứng → xin reproducibility badge.

- [ ] **T1.7 — Reconcile independence vs χ² (R1 Q2).** Dùng lập luận T0.4 (marginal vs conditional).

---

## TIER 2 — Cần API / thí nghiệm mới (nâng từ Accept → Oral, tùy thời gian & key)

> 📄 **Câu lệnh cụ thể cho từng mục T2.1–T2.6 ở `TIER2_RUN_GUIDE.md`** (cấu hình mạnh
> nhất, n lớn, kèm chỗ nào phải sửa code + cách verify 8 trang sau khi đưa số vào bài).

Không bắt buộc để được nhận, nhưng đóng các "major" còn lại và nâng Significance/Novelty → đẩy R2, R4 cao hơn và làm bài mạnh cho vòng oral.

- [ ] **T2.1 — Đa payload (đóng R2 W1 phần "single payload").**
  Chạy transport + content-form với **2–3 target benign khác** (khác BANANA-77). Mục tiêu: cho thấy 3.75× underestimate và hiệu ứng form không phải artefact của 1 payload.
  ↑ nâng: **R2 Soundness/Significance, R4 W2 (coverage)**. Chi phí: ~vài giờ API.

- [ ] **T2.2 — Ít nhất 1 adaptive-attacker probe (đóng R2 W1 phần "static attacker", R2 Q3).**
  Một tìm kiếm obfuscation đơn giản (split/space search) chống redaction, để kiểm verdict phòng thủ dưới đối thủ thích nghi.
  ↑ nâng: **R2 Overall 5→6, Significance**. Trung bình.

- [ ] **T2.3 — Instance cyclic thứ hai (đóng R1 W2, R4 W2).**
  Thêm 1 cấu hình recurrent khác (w khác, hoặc model thứ 2 mỗi chiều) dù n nhỏ, để `w·s²>1` từ "closed-form + 1 điểm" thành quy tắc có ≥2 điểm/chiều.
  ↑ nâng: **R1 W2 đóng, biến "rule" thành có kiểm chứng**. Trung bình.

- [ ] **T2.4 — Depth-slope trên frontier model (đóng R3 W3, R1 W2).**
  Đo lại depth curve trên 1 frontier model đủ dài để xác nhận slope diagnostic không chỉ đúng trên qwen 7B.
  ↑ nâng: **R3 Soundness, tổng quát hoá diagnostic**. Cao (chain dài, nhiều call).

- [ ] **T2.5 — 1 learned/semantic detector (nâng bản T0.7 từ "scope" lên "coverage").**
  Thêm 1 defence không tầm thường vào Fig. 2 để defence landscape không chỉ có literal-DLP + paraphrase.
  ↑ nâng: **R2 W3 đóng hẳn, Significance**. Trung bình–cao.

- [ ] **T2.6 — Tăng n các ô thứ cấp lên ~200 (giảm MDE) (đóng R3 W1, R2 W2, R4 W2).**
  Ưu tiên các ô đang phát biểu "holds"/"consistent" mà chỉ n=40. Giảm MDE 0.26→~0.11 để "non-rejection" thành "equivalence" thật.
  ↑ nâng: **R3/R4 Significance, biến caveat power thành kết quả**. Cao (nhiều call).

---

## TIER 3 — Trình bày / clarity (0 API, đánh bóng, nâng Clarity + R4)

- [x] **T3.4 — Cho `R_0` một CI/bootstrap SE để tách reach/reproduction là suy luận thống kê (R1 W4).** ✅ ĐÃ LÀM — §3.6 thêm "with a Wilson interval on the underlying compromise proportions". Nằm ở §3 nên **không** tốn trang 8. Build sạch, giữ nguyên trong bài.

> **Các mục Tier 3 còn lại đã BỎ (không làm) — lý do: trang 8 đã kịch trần sau Tier 0,
> mọi việc "thêm chữ" buộc phải cắt kết quả thật ở §5 để bù, đánh đổi không đáng:**
> - ~~T3.1 — Dẫn §5 bằng content-form (Table 4) trước~~ → BỎ: đổi thứ tự §5 là thay đổi cấu trúc lớn, rủi ro layout cao, lợi ích cận biên.
> - ~~T3.2 — Đưa "prescriptions" lên sớm hơn~~ → BỎ: cùng lý do cấu trúc như T3.1.
> - ~~T3.3 — Nêu `C_0=1` trong abstract~~ → THỬ RỒI HOÀN TÁC: tốn ~2 dòng đẩy Ethics/Artifact sang trang 9; `C_0=1` đã nêu rõ ở §3.1 nên lợi ích nhỏ.
> - ~~T3.5 — Sharpen novelty delta đầu §2~~ → THỬ RỒI HOÀN TÁC: tốn ~3 dòng, buộc cắt kết quả §5 để bù; nội dung "delta" đã rải trong §1/§2.
> - ~~T3.6 — Giảm mật độ số ở §5~~ → BỎ: rủi ro mất thông tin định lượng, không đáng khi bài đã đúng 8 trang.
>
> **Chốt Tier 3:** làm **T3.4** (cải thiện soundness thật, 0 chi phí trang); 5 mục
> còn lại dừng lại để bảo toàn 8 trang + nội dung kết quả. Muốn nâng điểm tiếp phải
> sang **Tier 2** (cần API key).

---

## Thứ tự thực thi đề xuất (tối ưu điểm/chi phí)

1. **Ngay (0 API, ~nửa ngày):** T0.1 → T0.2 → T0.4 → T0.5 → T0.7(scope) → T3.1/T3.3 → build lại sạch, kiểm 8 trang.
2. **0 API, đọc lại dữ liệu:** T0.3 → T0.6 (verify + seed table).
3. **Chuẩn bị rebuttal:** T1.1–T1.7 (dựa trên kết quả bước 1–2).
4. **Nếu còn key + thời gian (nâng oral):** T2.1 → T2.2 → T2.3 (rẻ→đắt), rồi T2.6/T2.4 nếu dư.

## Bản đồ việc → điểm kỳ vọng

| Nhóm việc | Review được nâng | Tiêu chí | Kỳ vọng |
|---|---|---|---|
| T0.1 (title) + T3.* | R4, tất cả | Clarity, Significance | R4 4→5 |
| T0.2/T0.3/T0.6 | R3, R2 | Soundness, Reproducibility | R3 6→6/7, badge |
| T2.1/T2.2/T2.5 | R2 | Soundness, Significance | R2 5→6 |
| T2.3/T2.4/T2.6 | R1, R3, R4 | Significance, Novelty | củng cố 6→7, R4 5→6 |
| **Tổng** | | | **Conditional Accept → Accept; trần oral nếu làm Tier 2** |

> **Chốt:** Chỉ cần hoàn thành **Tier 0** (0 API) là đủ biến Conditional Accept thành Accept và đóng mọi required change. **Tier 2** là phần kéo lên Accept mạnh/Oral, đánh đổi bằng thời gian + API key.

