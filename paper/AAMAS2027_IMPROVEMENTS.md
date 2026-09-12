# Contagion — Khuyến nghị cải thiện trước khi nộp AAMAS 2027

> Tài liệu này **gắn liền** với `paper/AAMAS2027_REVIEWS.md`: mỗi khuyến nghị dưới
> đây trả lời một điểm yếu cụ thể mà 4 reviewer (AC7Q, M4KZ, QT2W, B9RL) và
> meta-review đã nêu, hoặc một rủi ro tôi đọc trực tiếp trong
> `contagion_aamas2027.tex`. Mục tiêu: đưa điểm kỳ vọng từ mean **6.25** (chấp nhận
> có điều kiện) lên vùng an toàn, và biến reviewer B9RL (5/10) thành trung lập.
>
> **Ràng buộc thực tế đã biết** (từ `SUBMISSION_CHECKLIST.md` §3b): key Bedrock đã
> chết lần 2 → **mọi việc cần model cloud đang bị chặn**. Vì vậy mỗi việc dưới đây
> được gắn nhãn **[0 API]** (làm được ngay) hoặc **[CẦN KEY]** (chờ credentials mới).
> Ưu tiên tuyệt đối các việc **[0 API]** vì chúng đủ để thỏa 5 điều kiện bắt buộc
> của meta-review.

---

## 0. Tóm tắt điều hành (đọc cái này nếu chỉ có 5 phút)

Meta-review chấp nhận **có điều kiện**. Năm điều kiện bắt buộc **đều là [0 API]** và
có thể xong trong ~1 ngày viết:

1. Thu hẹp ngôn ngữ "prescriptions" trong abstract + danh sách đóng góp.
2. Thêm câu về **đa phép kiểm (multiplicity)** + đếm số test.
3. Nâng "Artifact availability" thành **mục có tiêu đề**.
4. Làm rõ **`R_0` dùng để làm gì** (1–2 câu).
5. Thêm **tuyên bố đạo đức / responsible-use**.

Làm xong 5 việc này là paper **đủ điều kiện in camera-ready**. Mọi thứ còn lại là
"nên có" để nâng chất lượng và giảm rủi ro bị đọc lệch.

---

## 1. Bắt buộc theo meta-review (điều kiện chấp nhận) — làm trước, tất cả [0 API]

### 1.1 Thu hẹp "prescriptions" cho khớp bằng chứng — [0 API] · ~1h
**Vấn đề (B9RL W4, M4KZ W2):** câu "Do not compose isolated results" trong abstract
và danh sách đóng góp bị đọc là kết luận tổng quát, trong khi thất bại transport chỉ
được chứng minh trên **một cạnh của một model** (Llama, 3.75×) và **giữ vững** trên
model khác (DeepSeek).
**Sửa cụ thể:**
- Abstract dòng "It does not, and its error compounds with distance": đổi thành dạng
  *tồn tại* — "isolation *can* fail, and where it does its error compounds with
  distance (Llama, 3.75× on one edge), while on another model it transports (DeepSeek,
  flat profile)." Giữ nguyên số, chỉ đổi lượng từ.
- Đóng góp #1 (`\item Do not compose...`): thêm mệnh đề "when the depth-profile slope
  is positive" để biến prescription thành **có điều kiện kiểm được** (chính là chẩn
  đoán độ dốc bạn đã có ở §5.7).
- Giữ chữ mạnh **chỉ** ở §5.6/§5.7 nơi có số đỡ lưng.

### 1.2 Thêm câu về đa phép kiểm — [0 API] · ~1–2h
**Vấn đề (QT2W W2):** lưới model × defence × attack × edge không hiệu chỉnh FWER.
**Sửa cụ thể:**
- Trong §5 (Estimators hoặc Estimator validation) thêm 2 câu: *tổng số test* trong
  lưới, và xác nhận các kết quả có ý nghĩa (Llama `p<0.001`) **vẫn sống** sau
  Benjamini–Hochberg ở `q=0.05`.
- Cách lấy số **[0 API]**: viết một pass BH nhỏ đọc các `p` đã lưu trong
  `experiments/results/*/results.json` (dùng lại `scripts/audit_numbers.py` làm khung).
  Không cần gọi model — mọi `p` đã có trong kết quả cũ.

### 1.3 Nâng "Artifact availability" thành mục có tiêu đề — [0 API] · ~30–45p
**Vấn đề (B9RL W3, M4KZ W4):** hiện chỉ có 1 câu ở Kết luận; reviewer AAMAS đánh giá
cao artefact.
**Sửa cụ thể:** thêm `\section*{Artifact Availability}` (hoặc paragraph trước
References) nói rõ **ba tầng tái lập**, khớp với `REPRODUCE.md`:
- **[0 API] tái lập được ngay:** code, toàn bộ `outputs.jsonl`/`results.json` mỗi
  cell, `pytest` (78 passed), `validate_methods.py`, `threshold_analysis.py`,
  `make_figures.py`, và mọi phân tích lại (percolation, placement, χ², BH).
- **Local model miễn phí:** `qwen2.5:7b` qua ollama chạy lại được không cần credentials.
- **[CẦN KEY] chỉ để tái sinh số frontier:** 4 model Bedrock cần credentials trả phí
  (ghi rõ inference-profile `us.` cho Anthropic/Meta để người khác không vấp lỗi bạn
  đã gặp).

### 1.4 Làm rõ `R_0` dùng để làm gì — [0 API] · ~20p
**Vấn đề (AC7Q W3):** paper đo `R_0` rồi lại bảo đừng dùng nó làm tiêu chí an toàn.
**Sửa cụ thể:** thêm 1–2 câu ở §5.5: `R_0` **là** thước đo *khuếch đại trung bình*
(hữu ích để so sánh topology và bắt độ lệch cấu trúc như star fan-in), **không phải**
thước đo *reachability*; hai rủi ro này tách nhau (đã có ví dụ star: `R_0=0.42` nhưng
`ASR=0.725`). Nói thẳng: "we measure it as a descriptive amplification statistic, not
as a certificate."

### 1.5 Thêm tuyên bố đạo đức / responsible-use — [0 API] · ~15p
**Vấn đề (M4KZ ethics flag):** thiếu mục đạo đức.
**Sửa cụ thể:** 3 câu trong `\begin{acks}` hoặc mục Ethics riêng: payload là marker
lành tính (`BANANA-77`), chỉ tấn công harness của chính nhóm, không có hệ thống thật
bị khai thác, và framework hướng tới **phòng thủ** (đo để hardening). Đây là chuẩn của
cả AAMAS lẫn các venue security.

> ✅ Xong mục 1 = thỏa toàn bộ điều kiện chấp nhận. Các mục sau là "nên có".

---

## 2. Nên có — nâng chất lượng, phần lớn [0 API]

> **Cập nhật trạng thái:** §2.1 (Mục 8) và §2.2 (Mục 10) **ĐÃ LÀM** — thêm Phụ lục A
> (bảng Benjamini--Hochberg) và Phụ lục B (CI cluster-bootstrap cho cạnh yếu) vào
> `.tex`, đặt **sau References** nên không tính vào 8 trang. Số sinh bằng
> `scripts/appendix_stats.py` (0 API). §2.4 (Mục 9 — độ nhạy ngưỡng τ) **KHÔNG làm
> được offline**: `results.json`/`report.md` của các cell obfuscation chỉ lưu
> rate/k/n (đã nhị phân hoá ở τ=0.9), **không lưu điểm ASV liên tục per-trial**, nên
> muốn chấm lại ở τ∈{0.8,1.0} phải gọi lại model ⇒ chuyển sang nhóm **[CẦN KEY]**.
> Phát hiện phụ đáng chú ý ở Phụ lục B: tính đúng *within-temperature* (T=0.7) thì
> cluster-bootstrap CI gần **trùng** Wilson (nới 0.99×) — φ=2.93 chỉ là artefact của
> pooling cross-temperature, đúng như §5.10 đã nói. Đây là điểm **củng cố** tính hợp
> lệ của Wilson interval, không phải điểm yếu.

### 2.1 Bảng phụ lục "test count + BH" — [0 API] · ~1h
Ngoài câu ở §1.2, thêm một bảng nhỏ trong phụ lục (references không tính trang) liệt
kê từng test, `p` thô, `p` sau BH, verdict. Reviewer QT2W sẽ chuyển từ "lo ngại" sang
"đã kiểm". Rẻ và tăng độ tin cậy thống kê rõ rệt.

### 2.2 Khoảng tin cậy phân cụm theo context cho cạnh yếu — [0 API] · ~2h
**Vấn đề (QT2W câu hỏi 2):** χ² đã **bác bỏ** trao đổi được (exchangeability) giữa các
context benign trên cạnh yếu (`p=0.0014`), nhưng Wilson interval giả định i.i.d.
Bernoulli.
**Sửa:** với riêng cạnh yếu, báo thêm một CI phân cụm theo context (cluster bootstrap
trên 3 context) bên cạnh Wilson, và 1 câu thừa nhận Wilson là *within-context*. Dữ
liệu trial-level đã có trong `outputs.jsonl` → không cần API.

### 2.3 Làm rõ "5 model" vs độ phủ từng claim — [0 API] · ~30p
**Vấn đề (B9RL W2):** "five models from five developers" bị đọc là mọi claim đều có
5 model, trong khi depth-profile là 3 model và bảng topology chỉ Llama.
**Sửa:** trong §4 (Cells) hoặc chú thích bảng, ghi **rõ số model cho từng phân tích**
("cross-model susceptibility: 5; depth profile: 3; topology: 1 (Llama)"). Trung thực
về độ phủ tốt hơn là để reviewer tự phát hiện.

### 2.4 Một câu về độ nhạy ngưỡng ASV τ=0.9 — [0 API] · ~30p
**Vấn đề (M4KZ câu hỏi 1):** model "kháng" ở 0.10 có thể đang nằm sát biên quyết định
của judge.
**Sửa:** báo lại ASR ở `τ∈{0.8, 0.9, 1.0}` cho cell floor-effect bằng cách **chấm lại**
`outputs.jsonl` đã lưu (ASV là quy tắc xác định, tính lại không cần model). Nếu kết
luận floor-effect ổn định qua τ → củng cố mạnh; nếu không → cần nói rõ.

---

## 3. Mạnh nhưng [CẦN KEY] — chỉ làm khi có credentials mới (không chặn chấp nhận)

> Meta-review nói rõ: **không cần** hứa thí nghiệm frontier mới để được nhận. Nhóm
> việc này để nâng từ "poster" lên "oral" hoặc để dành cho bản mở rộng (USENIX).

### 3.1 Chạy lại cạnh yếu Llama ở n≈200 — [CẦN KEY] · ~2h chạy
**Vấn đề (M4KZ + QT2W):** MDE ở n=40 là 0.26; nhiều verdict "null" là *underpowered*.
**Lợi ích:** biến cell transport-failure thành **phát hiện dương tính thật** thay vì
"proof of existence". Đây là việc [CẦN KEY] có tỉ lệ lợi ích/chi phí cao nhất.
Lệnh: `depth_curve.py`/`replicate_frontier.py` trên cạnh giữa, `--fresh-artifact`,
n=200.

### 3.2 Thêm ≥1 instance cho star/tree và ≥1 model cho bảng topology — [CẦN KEY] · ~1–2h
**Vấn đề (B9RL W1, W2):** topology hiện là **single-instance, single-model**.
**Lợi ích:** trực tiếp hạ đòn W1 của B9RL — claim "topology thay đổi spread" hết bị
đọc là giai thoại. Lệnh: `replicate_frontier.py --topology {star,tree} --num-agents 7`
trên model thứ 2 (vd DeepSeek).

### 3.3 Thí nghiệm re-injection (independent vs colluding) — [CẦN KEY] · ~1.5h
**Vấn đề (AC7Q W1):** đây là mặt tấn công *đặc trưng multiagent* mà code đã hỗ trợ
(`ReInjectionMode` NONE/INDEPENDENT/COLLUDING) nhưng **chưa chạy**.
**Lợi ích:** thêm chiều multiagent mà reviewer AAMAS (AC7Q) mong đợi nhất; hiện đang
để ở future work.

### 3.4 Model thứ 6 cho bảng obfuscation — [CẦN KEY] · ~25p chạy
Tăng độ phủ cross-model, thay các cell `n=8` (khoảng tin cậy rộng, chính nhóm không
diễn giải) bằng số chắc hơn.

---

## 4. Rủi ro framing lớn nhất còn lại (đọc kỹ)

`idea_alignment.md` và `SUBMISSION_CHECKLIST.md` đều cảnh báo cùng một rủi ro, và cả
4 reviewer chạm vào nó: **bị đọc thành "thêm một benchmark đo prompt injection"**.
Cách phòng thủ, tất cả [0 API]:

- **Đưa 3 kết quả *âm/định lý* lên trước** trong Introduction: `ρ(M)=0` vacuity,
  composition-là-identity, floor effect. Đây là phần reviewer khen đồng loạt và là
  thứ phân biệt paper với InjecAgent/AgentDojo. Đừng để chúng bị chôn sau phần đo.
- **Nhấn "fundamentally multiagent"**: `s`, `R_0`, percolation recurrence **không định
  nghĩa được** cho 1 agent. Câu này nên xuất hiện sớm (đúng tinh thần AAMAS, giúp AC7Q).
- **Giữ nguyên phần trung thực** (E22 rút lại, χ² tự bác bỏ, cell degenerate gắn nhãn):
  cả 4 reviewer coi đây là điểm cộng lớn — **đừng cắt** khi rút gọn cho vừa 8 trang.

---

## 5. Bảng ưu tiên tổng hợp (làm theo thứ tự này)

| # | Việc | Reviewer đỡ lưng | API? | Chi phí | Chặn chấp nhận? | **Đã làm?** |
|---|---|---|---|---|---|---|
| 1 | Thu hẹp "prescriptions" (§1.1) | B9RL, M4KZ | 0 API | 1h | ✅ Bắt buộc | ✅ **XONG** |
| 2 | Câu + số multiplicity/BH (§1.2) | QT2W | 0 API | 1–2h | ✅ Bắt buộc | ✅ **XONG** |
| 3 | Mục Artifact availability (§1.3) | B9RL, M4KZ | 0 API | 45p | ✅ Bắt buộc | ✅ **XONG** |
| 4 | Làm rõ `R_0` (§1.4) | AC7Q | 0 API | 20p | ✅ Bắt buộc | ✅ **XONG** |
| 5 | Tuyên bố đạo đức (§1.5) | M4KZ | 0 API | 15p | ✅ Bắt buộc | ✅ **XONG** |
| 6 | Đưa 3 kết quả định lý lên trước (§4) | tất cả | 0 API | 1h | ⭐ Rất nên | ✅ **XONG** |
| 7 | Nêu rõ độ phủ model/claim (§2.3) | B9RL | 0 API | 30p | ⭐ Rất nên | ✅ **XONG** |
| 8 | Bảng BH phụ lục (§2.1 → Phụ lục A) | QT2W | 0 API | 1h | Nên | ✅ **XONG** |
| 9 | Độ nhạy τ cho floor-effect (§2.4) | M4KZ | 1 lần chạy model rồi 0 API | 30p | Nên | 🟡 **CÔNG CỤ SẴN SÀNG** — `tau_sensitivity_probe.py` (bạn chạy) + `tau_sensitivity_analyze.py` (mình chấm) + `docs/TAU_SENSITIVITY_HOWTO.md`; chỉ chờ bạn chạy probe (ollama miễn phí hoặc Bedrock) |
| 10 | CI cluster-bootstrap cạnh yếu (§2.2 → Phụ lục B) | QT2W | 0 API | 2h | Nên | ✅ **XONG** |
| 11 | Cạnh yếu Llama n≈200 (§3.1) | M4KZ, QT2W | CẦN KEY | 2h | Không (nâng oral) | ⏳ Chờ key |
| 12 | Topology +1 instance/+1 model (§3.2) | B9RL | CẦN KEY | 1–2h | Không (nâng oral) | ⏳ Chờ key |
| 13 | Re-injection colluding (§3.3) | AC7Q | CẦN KEY | 1.5h | Không (bản mở rộng) | ⏳ Chờ key |
| 14 | Model thứ 6 obfuscation (§3.4) | M4KZ | CẦN KEY | 25p | Không | ⏳ Chờ key |

**Trạng thái tổng:** 9/14 xong (toàn bộ 5 việc bắt buộc + 2 việc chống framing +
2 bảng phụ lục). Còn lại **5 việc đều [CẦN KEY]** (Mục 9, 11–14) — chờ key Bedrock
mới; không việc nào chặn chấp nhận. Mọi việc [0 API] khả thi **đã hoàn tất**.

**Đường đi khuyến nghị:** làm 1→5 (đủ điều kiện in) → 6→7 (chống framing lệch) →
8→10 (khi còn thời gian) → 11→14 **chỉ khi có key Bedrock mới**.

---

## 6. Việc kỹ thuật vụn nhưng đừng quên (từ checklist review) — [0 API]

- [ ] Thay `\acmSubmissionID{0000}` bằng OpenReview ID thật khi nộp.
- [ ] Điền `\author{}` cho camera-ready (bỏ chế độ anonymous đúng thời điểm).
- [ ] Chạy lại chuỗi build 3 lần + 3 lệnh `Select-String` (mục 5 của
      `SUBMISSION_CHECKLIST.md`): `!`, `Overfull \hbox`, `undefined` **phải = 0**.
- [ ] Chạy `python scripts\audit_numbers.py --md` + `claim_lint` lần cuối để chắc mọi
      số trong `.tex` khớp `results.json` (đã từng bắt lỗi "four families").
- [ ] Đọc PDF một lượt liền mạch như tác giả — người viết cuối vẫn phải là bạn.

---

*Hết. Ưu tiên 5 việc [0 API] ở mục 1; mọi việc [CẦN KEY] chờ credentials và không chặn
việc được chấp nhận.*