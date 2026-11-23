# Giải thích chi tiết Review 3 (Điểm: Proceedings 6 / Findings 7)

> **Vị trí của Reviewer 3:** Đánh giá **Proceedings 6** (*Marginally above*) và **Findings 7** (*Good paper, accept*). Đây là reviewer **ủng hộ bài nhất** (khen mạnh về độ chặt chẽ thống kê và trung thực khoa học), nhưng cũng viết danh sách Weaknesses dài nhất theo kiểu *"góp ý để bài hoàn hảo hơn"*. Nhiệm vụ với R3 là **giữ vững điểm `6–7`**, giải đáp thỏa đáng 4 câu hỏi và chỉnh nhẹ chỗ R3 đọc nhầm/đọc sót.

*(Lưu ý khi đọc bản copy từ OpenReview của R3: một số ký hiệu toán học LaTeX khi copy text bị mất khoảng trống, ví dụ "thresholded at [0.9]", "margin of [±0.15]", "when [R_0 / ρ(M)] becomes informative", "Llama failure ([3.75×])". Bên dưới đã điền đầy đủ để bạn dễ theo dõi.)*

---

## 1. Summary & Strengths — R3 đánh giá cao nhất điều gì?

R3 tóm tắt bài cực chuẩn và dành **3 lời khen rất nặng ký**:
1. **Phương pháp đo đạc chặt chẽ:** Thiết kế 2 giao thức bổ sung nhau (controlled per-edge vs natural-run), dùng khoảng tin cậy Wilson, bootstrap permutation test, và hiệu chỉnh đa kiểm định Benjamini–Hochberg (BH).
2. **Tìm ra cơ chế *Payload Form* (`14×`):** Phát hiện bản chất vấn đề không nằm ở việc LLM có truyền chữ tùy ý hay không, mà ở chỗ **payload có ngụy trang giống đầu ra công việc hợp lệ hay không** — gợi ý trực tiếp cho thiết kế phòng thủ.
3. **Trung thực khoa học mẫu mực:** Tự công bố kết quả trước đó là lỗi giao thức (*fixed vs fresh artefact*, Table 3) và thiết kế phép đo tự kiểm định độ nhiễu (`none·split` vs `redact·split`).

---

## 2. Weaknesses — Giải thích chi tiết 5 điểm yếu R3 nêu

### Weakness 1 (giống R1 W1): *"The outcome metric (ASV) measures textual propagation only... 0/19 cases showed adoption... The paper would be substantially strengthened by a small-scale evaluation of adoption rates."*

- **Điểm lưu ý nhỏ R3 ghi nhầm:** R3 viết *"The ASV metric, thresholded at [0.9] via cosine similarity..."* — thực ra **ASV không phải cosine similarity**, mà là tỷ lệ chứa cặp 2 từ liên tiếp (*deterministic target-bigram containment*: $|B(t) \cap B(y)| / |B(t)|$). Cần đính chính nhẹ chi tiết kỹ thuật này.
- **Ý chính của R3:** Giống R1, R3 nhấn mạnh `0/19` ca tự chấm cho thấy ASV chỉ đo **Level (a) lan truyền chữ**, chưa đo **Level (b) làm theo lệnh**. Dù bài báo đã nói đó là cận trên (*upper bound*), R3 lo khoảng cách giữa (a) và (b) có thể rất lớn, và nói rõ: *"Bài sẽ mạnh lên đáng kể nếu có thêm 1 đánh giá nhỏ về tỷ lệ adoption."*
- **Ý nghĩa chiến lược:** Vì R1 cũng hỏi đúng điểm này, nếu chạy được **Bước 1 + Bước 3 trong `plan_rebuttal.md`** (đo Level (b) gọn với nhãn tất định trên Llama/DeepSeek hoặc kiểm thêm log sẵn có) thì có cơ hội vừa kéo R1 lên `6` vừa củng cố R3 lên `7`. Nếu không chạy kịp thì phải nhấn mạnh giải pháp thiết kế cho Q1 (bên dưới).

---

### Weakness 2: *"Static non-adaptive attacker model... real world attackers are adaptive... The threat model should be discussed more explicitly in terms of attacker capability classes."*

- **Dịch dễ hiểu:**
  Bài mới dùng đúng 1 kiểu tấn công cố định (và mấy biến thể chèn dấu cách/tách chữ), trong khi hacker ngoài đời là **kẻ tấn công thích nghi (adaptive)** — họ thử sai liên tục, sửa câu chữ, dùng jailbreak riêng cho từng model để né bộ lọc.
- **Bản chất:** R3 không bắt bạn phải chạy thêm tấn công adaptive (chính Sec. 4 & Sec. 6 đã giải thích giới hạn phạm vi này và cam kết đạo đức không phát hành exploit thích nghi), mà chủ yếu đề nghị **phân loại rõ ràng các cấp năng lực kẻ tấn công** trong Threat Model (Sec. 3.1): ví dụ *Tier 1 (plain)*, *Tier 2 (structural obfuscation)*, *Tier 3 (adaptive)*. Đồng thời lưu ý: ngay cả với attacker yếu (tĩnh) mà các "bẫy" đo đạc (`3.75×`, `14×`, `floor effect`) đã xuất hiện rồi, thì với attacker thích nghi rủi ro còn lớn hơn nữa.

---

### Weakness 3: *"Limited statistical power for some analyses... MDE ≈ 0.26... TOST equivalence margin of [±0.15] is a generous equivalence margin for a security-critical application."*

- **Giải thích các khái niệm thống kê ở đây:**
  - **Cỡ mẫu $n = 30\text{--}40$ cho MDE $\approx 0.26$:** Độ phân giải tối thiểu là 26 điểm phần trăm. Tức là với $n=40$, chỉ khi hai con số lệch nhau trên 26% thì kiểm định mới chắc chắn bắt được; nếu lệch 10–15% thì dễ ra $p > 0.05$ ("không thấy khác biệt").
  - **TOST (kiểm định tương đương) với biên $\pm 0.15$:** Khác với kiểm định tìm khác biệt, TOST kiểm tra xem hai tỷ lệ có **"coi như bằng nhau" trong biên sai số $\pm 15\%$** hay không. Ở Sec. 5.5, bài báo cho biết ngay cả với biên $\pm 0.15$ thì $n=40$ trên DeepSeek vẫn **trượt** trên 2/3 cạnh, phải tăng lên $n=200$ mới đạt.
- **R3 đang thắc mắc gì?**
  Trong ứng dụng an toàn bảo mật nghiêm ngặt, cho phép sai lệch giữa "đo cô lập" và "chạy thật" lên tới **$\pm 15\%$** là quá rộng (ví dụ thực tế bị lây 20% mà đo ra 5% vẫn bị coi là "tương đương").
- **Cách trả lời cực hay (không cần chạy thêm):**
  Đồng ý 100% với R3 rằng $\pm 0.15$ chỉ là **ngưỡng sàng lọc sơ bộ (*triage bound*)**, không phải ngưỡng chứng nhận an toàn (*certification*). Và dùng chính toán học cỡ mẫu $n \propto 1/\mathrm{MDE}^2$ để chứng minh ngược lại luận điểm của bài: tại $n=200$, $\mathrm{MDE}$ mới xuống được $0.11\text{--}0.13$; nếu muốn chứng nhận biên chặt $\pm 0.02\text{--}0.05$ mỗi cạnh thì cần tới **$1{,}000\text{--}8{,}000+$ lần chạy cho MỖI cạnh** — phi thực tế về chi phí! Do đó, thay vì cố chạy $n$ khổng lồ để chứng nhận đo cô lập, đội kỹ thuật nên **đo thẳng trên chuỗi chạy thật** (Sec. 7).

---

### Weakness 4: *"Limited topological diversity... chains (4–7), star, balanced binary tree... real-world systems feature feedback, dynamic routing, conditional branching, and cycles. A brief experiment with a single cycle would significantly strengthen the paper's claims about when [$R_0$ / $\rho(M)$] becomes informative."*

- **Tin vui — R3 ĐỌC SÓT!**
  Bài báo **ĐÃ LÀM THÍ NGHIỆM VÒNG LẶP (CYCLE) RỒI**, không những 1 mà thử hẳn trên **3 model** (Llama, DeepSeek, qwen — kéo dài 5–8 vòng, cộng thêm bản 3-worker ở 60 trials trên Llama) nằm ngay tại **Sec. 5.4 (`contagion_aamas2027.tex`, dòng 936–951)** và **Appendix F (`supplementary.tex`, dòng 388–507)**! Ngoài ra còn có DAG phân nhánh–hội tụ (*reconvergent DAG*) ở **Appendix Q** (`Table 14`).
- **Tại sao R3 đọc sót?**
  Vì Sec. 5.4 đặt tên là *"Recurrence and multiplicity"*, nằm nén thành đúng 15 dòng ở cuối trang 8, còn danh sách topology ở Sec. 3.1 chỉ liệt kê *"chain, star and balanced binary tree"*.
- **Cách xử lý:** Chỉ cần trỏ lịch sự R3 về **Sec. 5.4 + Appendix F (Tables 5–6) + Appendix Q (Table 14)**, tóm tắt gọn số liệu đã có (`Llama 1.342`, `DeepSeek 1.009`, `qwen 0.760`), và hứa ở camera-ready sẽ đổi tên Sec. 5.4 thành *"Cyclic Topologies"* + nhắc ngay từ Sec. 1 để người đọc không bỏ sót.

---

### Weakness 5: *"Defence evaluation is narrow. Only two defence families are tested: redaction and semantic paraphrase..."*

- **Dịch dễ hiểu:**
  Mới thử có 2 kiểu phòng thủ đơn giản (xóa từ khóa và paraphrase), trong khi hệ thống thật còn có *structured output schemas, canary tokens, instruction hierarchies, LLM classifiers, sandboxing...*
- **Cách trả lời:**
  Đây là điểm R3 ghi nhận mang tính xây dựng (chính R3 cũng viết *"This is acknowledged"*). Nhấn mạnh rằng **hai bài học cốt lõi về phòng thủ** — (1) *floor effect* khi so sánh các model có baseline khác nhau, và (2) *minimal $s$--$t$ cut* khi đặt phòng thủ trên đồ thị — là **quy luật cấu trúc đúng với mọi loại phòng thủ**, và cặp đo $(\mathrm{ASR}, \Delta U)$ của bài sẵn sàng làm chuẩn để benchmark các lớp phòng thủ mạnh hơn như StruQ/CaMeL ở camera-ready / nghiên cứu tiếp theo.

---

## 3. Questions for the Authors — Tóm tắt 4 câu hỏi của R3

| Câu hỏi | R3 hỏi gì? | Bản chất & hướng trả lời |
|---|---|---|
| **Q1** | Với `0/19` adoption, bạn có thiết kế thí nghiệm nào đo trực tiếp *adoption / hành vi* ở quy mô lớn mà vẫn khả thi không? | Nêu rõ ý tưởng **deterministic behavioural sinks** (chốt đầu ra cấu trúc, ép lật quyết định `HIGH/LOW` hoặc gọi tool giả lập không cần LLM-judge — tức là tránh được nhiễu và chi phí judge). Nếu kịp làm pilot (Task Family C ở `plan_rebuttal.md`) thì báo luôn kết quả thật; nếu không kịp thì đề xuất rõ kiến trúc này trong Sec. 6. |
| **Q2** | Cơ chế nào gây ra lỗi Llama (`3.75×`) — do độ dài context, vị trí token, hay alignment training của Llama? | Đây là câu hỏi phân tích rất hay. Trong Table 4, bài đã đưa **bản trơ vs bản trong báo cáo vào CÙNG 1 fresh receiver với CÙNG bài toán nền**, mà vẫn chênh `14×` (`0.067` vs `0.967`, $p = 2.3 \times 10^{-13}$) $\implies$ **loại trừ yếu tố tích tụ độ dài context hay trượt vị trí chuỗi**. Cộng thêm App. O (Llama bám sát nhãn *role*: `0.039` vs `0.166`) và Sec. 5.5 ($\chi^2 = 13.40$), nguyên nhân nghiêng mạnh về **alignment/framing sensitivity**: vai Reviewer của Llama gạt bỏ câu khẳng định/lệnh trơ, nhưng lại tóm tắt bình thường khi nó được gói thành dữ liệu trong báo cáo công việc. |
| **Q3** | Với TOST `±0.15`, theo tác giả biên bao nhiêu mới có ý nghĩa cho chứng nhận bảo mật? | Trả lời thẳng như mục W3 ở trên: `±0.15` chỉ dùng để **sàng lọc (triage)**, chứng nhận bảo mật cần cỡ `±0.02–0.05`, nhưng đòi hỏi $1{,}000\text{--}8{,}000+$ trial/cạnh — càng chứng minh lời khuyên cuối bài (đo trực tiếp trên chuỗi triển khai). |
| **Q4** | Đã thử nghiệm sơ bộ cấu trúc có vòng lặp (cyclic) nào chưa? | **Đã có đầy đủ** ở Sec. 5.4 + Appendix F (Tables 5–6): vòng lặp Manager–Worker trên Llama, DeepSeek, qwen (5–8 vòng) + bản 3-worker 60 trials trên Llama! |

---

## 4. Tổng kết chiến lược cho Reviewer 3

- **Điểm hiện tại:** Proceedings `6` / Findings `7` (đang là người kéo bài lên accept).
- **Cần làm với R3:**
  1. Chỉ nhẹ nhàng chỗ R3 đọc sót **cyclic topologies** (Sec. 5.4, App. F) và đính chính nhẹ `ASV` là *target-bigram containment* chứ không phải cosine similarity.
  2. Trả lời sắc nét cơ chế Llama (Q2) và bài toán cỡ mẫu biên TOST (Q3).
  3. Đáp ứng thật tốt câu hỏi **Level (b) adoption (W1/Q1)** — bằng thiết kế *deterministic behavioural sinks* (và kết quả pilot thật nếu bạn chạy thêm kịp).

---

## 5. Kế hoạch hành động riêng cho Reviewer 3 (tách từ `plan_rebuttal.md`)

> **Mục tiêu:** Giữ vững và củng cố R3 từ Proceedings `6` / Findings `7` lên `7 / 7`, đặc biệt giải đáp **W1/Q1, Q2, W4/Q4**.
> **Nguyên tắc bắt buộc:** **KHÔNG** sửa/upload lại PDF, **KHÔNG** chèn link ngoài, trần **$\le 2{,}500$ ký tự** cho `rebuttal/review3.md`.

### A. Kỷ luật KHÔNG làm (cả trong Rebuttal lẫn Camera-Ready)

1. **KHÔNG chạy $n = 1{,}000\text{--}8{,}000$ trial/cạnh** để ép biên TOST xuống $\pm 0.02\text{--}0.05$ (**R3 W3/Q3** $\to$ trả lời bằng lập luận toán học $n \propto 1/\delta^2$, càng củng cố lời khuyên ở Sec. 7 là đo thẳng trên chuỗi triển khai).
2. **KHÔNG xây kẻ tấn công *adaptive*** tự động tối ưu token/jailbreak (**R3 W2** $\to$ trái cam kết đạo đức ở Sec. 7; chỉ bổ sung phân tầng năng lực attacker ở Camera-Ready).
3. **KHÔNG chạy thêm topology mesh/debate** (**R3 W4** $\to$ thực chất R3 đọc sót phần vòng lặp đã hoàn chỉnh ở Sec. 5.4 / App. F và DAG hội tụ ở App. Q).

### B. Giai đoạn Rebuttal (HIỆN TẠI — các bước phục vụ trực tiếp R3)

- **Bước 0 (5 phút, nếu chạy thêm Bước 1 hoặc 3):** Chạy `pytest tests -q` (`78 passed`), kiểm tra Bedrock (`test_bedrock.py`, `bedrock_key_diag.py`), khóa $T=0.7$, $\text{seed}=7$, cap $400$ tokens.
- **Bước 1 — Kiểm định 0 đồng trên raw logs ĐÃ NỘP (30–60 phút, trả lời R3 W1/Q1 & Q2):**
  - **1.1 & 1.2:** Chấm tay Level (a) vs Level (b) trên raw logs Llama ($n=30$ dương + $5\text{--}10$ âm từ `frontier_llama3-3-70b_iso`) và DeepSeek ($n=20$ dương từ `frontier_deepseek_fresh`/`iso`) $\to$ `experiments/results/rebuttal_adjudication_frontier.csv`.
  - **1.3:** Mổ xẻ `28/30` ca âm tính nhánh *canonical* `a1->a2` của Llama (*refusal* vs *task-focused ignore*) để tăng bằng chứng cơ chế trả lời **R3 Q2**.
- **Bước 3 — Pilot gọn Level (b) Behavioural Adoption — Task Family C (Đòn bẩy cao nhất cho R3 W1/Q1):**
  - Thiết kế Decision-Flip tất định (`DRILL-77`, dòng cuối `DECISION: HIGH` / `DECISION: LOW`, judge regex không LLM-judge), smoke-test $n=3+3$, chạy `scripts/rebuttal_adoption_family_c.py` đủ 4 nhánh trên Llama 3.3 70B & DeepSeek V3.2 (`--fresh-artifact`), QC đọc tay 10 mẫu/model.
  - *(Nếu không chạy kịp Bước 3: vẫn giữ trả lời R3 Q1 bằng thiết kế **deterministic behavioural sinks** như trong `rebuttal/review3.md`.)*
- **Bước 4 — Chốt bản `rebuttal/review3.md` ($\le 2{,}500$ ký tự):**
  - Đảm bảo đủ 4 ý: (1) Trỏ cyclic đã có sẵn ở Sec. 5.4 / App. F / App. Q; (2) Đính chính nhẹ `ASV` là bigram containment (không phải cosine similarity) + Level (b) audit/pilot hoặc thiết kế sink; (3) Cơ chế Llama `a1->a2` loại trừ độ dài context/vị trí nhờ replay fresh receiver; (4) TOST $\pm 0.15$ là ngưỡng triage & lập luận $n \propto 1/\delta^2$.

### C. Giai đoạn Camera-Ready (SAU ACCEPTANCE)

- **Bước CR-1 (Sửa văn bản):**
  - **Sec. 1:** Dẫn chiếu sớm kết quả đồ thị có chu trình (Sec. 5.4 / App. F) và DAG hội tụ (App. Q).
  - **Sec. 3.1:** Bổ sung phân tầng năng lực kẻ tấn công (*plain / structural obfuscation / adaptive*) để trả lời R3 W2.
  - **Sec. 5.4:** Đổi tiêu đề mục thành *"Cyclic Topologies"* để người đọc không sót.
  - **Sec. 6 & Supplementary:** Bổ sung thảo luận về *deterministic behavioural sinks* và đưa bảng kết quả Bước 1 & 3 (nếu chạy) vào bài/phụ lục.
- **Bước CR-2 (Tùy chọn mở rộng cho R3 W5 — thêm họ phòng thủ thứ 3):**
  - Cài đặt **Spotlighting / Delimiter framing** (Hines et al.) hoặc **Structured Output Schema**.
  - Chạy `scripts/utility_real.py` ($n = 20\text{--}30$ paired runs, $T = 0.7$, Family B `BANANA-77`) trên **DeepSeek V3.2** (headroom cao: baseline `none` $\mathrm{ASR} = 0.450$, Retention $= 0.600$) và **Claude Sonnet 4.5** (mức sàn: baseline `none` $\mathrm{ASR} = 0.000$, Retention $= 1.000$), bổ sung vào Appendix J (Table 9).

