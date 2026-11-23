# Giải thích chi tiết Review 2 (Điểm: Proceedings 5 / Findings 6)

> **Vị trí của Reviewer 2:** Đánh giá **Proceedings 5** (*Marginally below*) và **Findings 6** (*Marginally above*). Đây là reviewer thiên về **toán học / lý thuyết đồ thị**, thích phần so sánh defense ở Sec. 5.2, **nhưng bị vướng ở nhiều chỗ viết tắt/khó hiểu trong Sec. 3.2, 3.6, 5.1, 5.4**. Đây là reviewer **dễ kéo điểm lên nhất chỉ bằng văn bản giải thích rõ ràng** (không cần chạy thêm thực nghiệm).

---

## 1. Summary & Đánh giá chung của Reviewer 2

**R2 tóm tắt:**
- Bài nghiên cứu tấn công prompt injection trong mạng LLM agent.
- Đề xuất các chỉ số lây nhiễm thực nghiệm phù hợp cho đồ thị có hướng không chu trình (DAG).
- Đối chiếu tỷ lệ thành công toàn mạng với dự đoán từ từng hop, đồng thời đánh giá các phương pháp phòng thủ.

**Điểm R2 khen:** Phần so sánh hiệu quả các phương pháp phòng thủ ở **Section 5.2** (chính là phát hiện *floor effect* và *semantic paraphrase* bị áp đảo hoàn toàn bởi không làm gì) rất thú vị.

**Điểm R2 chê:** Gần như toàn bộ review của R2 là phàn nàn về **độ rõ ràng (clarity)** ở 4 đoạn trong bài chính.

---

## 2. Giải thích chi tiết từng nhận xét của Reviewer 2

### Ý 1 (Sec. 3.2): *"The paper would benefit from elaborating somewhat on the compromise judgment methods, for example, how ASV and MR are computed and defined."*

- **R2 đang hỏi gì?**
  Bài nói dùng `ASV` và `MR` để chấm xem một agent có bị nhiễm hay không, nhưng giải thích hơi sơ sài — công thức tính cụ thể của `ASV` và `MR` là gì?
- **Tại sao R2 không thấy?**
  Ở **Sec. 3.2** (`contagion_aamas2027.tex`, dòng 413–417), tác giả chỉ viết bằng chữ:
  > *"where ASV is the fraction of target bigrams present in the output and MR is a similarity against the reference hijacked output. For family B we use the ASV branch only ($\tau_{\mathrm{asv}} = 0.9$) and log MR."*
  Không có công thức ký hiệu tập hợp nào được viết ra trong bài chính.
- **Bản chất toán học cần hình dung (lấy từ `supplementary.tex` App. G & `plan_rebuttal.md`):**
  Gọi $B(x)$ là tập hợp các cặp 2 từ liên tiếp (*word-bigrams*) trong đoạn văn $x$:
  - **ASV (Attack Success Value — độ phủ bigram mục tiêu):**
    $$\mathrm{ASV}(y, t) = \frac{|B(t) \cap B(y)|}{|B(t)|}$$
    Trong đó $t$ là chuỗi mục tiêu (ví dụ `BANANA-77` và cụm từ đi kèm), $y$ là output của agent. Nếu $\ge 90\%$ bigram của $t$ có mặt trong $y$ ($\tau_{\mathrm{ASV}} = 0.9$) thì tính là $C=1$. *(Lưu ý: dùng mình ASV cho Family B, không dùng MR).*
  - **MR (Match Rate — hệ số Dice so với mẫu bị hack trực tiếp):**
    $$\mathrm{MR}(y, y_{\mathrm{ref}}) = \frac{2\,|B(y) \cap B(y_{\mathrm{ref}})|}{|B(y)| + |B(y_{\mathrm{ref}})|}$$
    Trong đó $y_{\mathrm{ref}}$ là output mẫu khi tiêm trực tiếp. Chỉ lưu log để theo dõi chứ không dùng để quyết định nhãn ở Family B (vì ở App. G Table 7, biến thể so khớp toàn phần trước đây hay chấm nhầm cả câu trả lời sạch/từ chối).

---

### Ý 2 (Sec. 3.6 — đoạn 1): *"At times, it seems to assume that paths are disjoint to satisfy an independence assumption, while at times it (correctly) points out that independence is not satisfied for general DAGs."*

- **R2 đang lấn cấn gì?**
  R2 thấy **Sec. 3.6** lúc thì dùng công thức Eq. (3) như thể mọi đường đi độc lập với nhau, lúc thì lại bảo DAG tổng quát không độc lập — nghe hơi tiền hậu bất nhất.
- **Hình dung bằng sơ đồ:**
  Eq. (3) là công thức lan truyền từng bước theo thứ tự tô-pô:
  $$\Pr[v] = 1 - \prod_{u \to v} \bigl(1 - s_{u \to v}\,\Pr[u]\bigr)$$
  - **Khi nào công thức này ĐÚNG CHÍNH XÁC?** Khi các nút cha $u$ đi vào $v$ có **đường đi phía trên rời nhau hoàn toàn** (không chung gốc rễ trung gian), ví dụ như **chuỗi thẳng** hoặc **cây nhị phân** (từ gốc đi ra chỉ có 1 đường tới mỗi nút).
  - **Khi nào nó CHỈ LÀ XẤP XỈ (SAI)?** Khi có **tổ tiên chung (shared ancestor)** — ví dụ DAG hình thoi $s \to u \to \{A, B\} \to t$.
    - Giả sử cạnh $s \to u$ lây $50\%$, mọi cạnh sau lây $100\%$.
    - Xác suất thật để $t$ bị nhiễm là **$0.50$** (vì qua hay không phụ thuộc hoàn toàn vào mỗi cạnh $s \to u$).
    - Nhưng nếu cắm đầu tính theo Eq. (3): $\Pr[A] = 0.5$, $\Pr[B] = 0.5$, rồi giả vờ $A \to t$ và $B \to t$ độc lập: $1 - (1 - 0.5)(1 - 0.5) = \mathbf{0.75}$ $\to$ **SAI!**
- **Tại sao R2 thấy rối?**
  Trong `contagion_aamas2027.tex` dòng 546–558, tác giả gộp cả 2 ý vào 1 đoạn văn rất dài và chặt. Chỉ cần tách rõ hai vế trong rebuttal (và trong camera-ready): *(1) Chính xác khi đường đi thượng nguồn rời nhau; (2) Chỉ là xấp xỉ biên khi có tổ tiên chung* — đồng thời nhắc R2 rằng bạn **đã test đúng trường hợp bị lệch đó ở Appendix Q (`Table 14`, DAG hội tụ `a0->a1->{a2,a3}->a4`, nơi Eq. (3) từ biên trong chuỗi bị hụt `0.247`: `0.545` vs `0.792`)**.

---

### Ý 3 (Sec. 3.6 — đoạn 2): *"Furthermore, a comparison between the empirical reproduction number $R_0$ and its standard definition for non-acyclic graphs would be helpful. Does the empirical index have any properties in common with the standard reproduction number?"*

- **R2 đang hỏi gì?**
  Chỉ số $R_0$ tự định nghĩa trong bài giống và khác gì so với $R_0$ chuẩn trong lý thuyết dịch tễ học (trên đồ thị có chu trình)?
- **Giải thích trực quan:**
  - **$R_0$ chuẩn (trong dịch tễ / đồ thị có vòng lặp):** Định nghĩa qua giá trị riêng lớn nhất (bán kính phổ $\rho(M)$) của ma trận lây nhiễm giữa các nhóm/nút. Nó có **tính chất ngưỡng (threshold property)**: $\rho(M) < 1$ thì dịch tàn, $\rho(M) > 1$ thì dịch bùng phát.
  - **Tại sao $R_0$ chuẩn gãy trên đồ thị truyền thẳng (DAG)?**
    Trên DAG, tin nhắn chỉ đi một chiều không bao giờ quay lại. Khi xếp các nút theo chiều chảy, ma trận $M$ luôn là **ma trận tam giác trên ngặt** (đường chéo và nửa dưới toàn số 0). Về mặt đại số tuyến tính, **mọi trị riêng của ma trận này đều bằng 0**, suy ra $\rho(M) = 0 < 1$ **một cách hiển nhiên**, dù tỷ lệ lây từng bước có cao tới `100%`!
  - **$R_0$ thực nghiệm của bài ($R_0 = |\mathcal{C}|^{-1} \sum_{c \in \mathcal{C}} n(c)$):** Đếm trung bình 1 agent bị nhiễm đã làm nhiễm thêm bao nhiêu hàng xóm ngay sau nó trong 1 lượt chạy.
  - **Điểm chung & khác biệt:**
    - *Giống nhau:* Cùng giữ ý nghĩa **hệ số nhân cục bộ trên 1 bước** (*local branching average* — trên đồ thị đều nó bằng bậc ra $\times$ tỷ lệ sống sót $d \cdot \bar{s}$).
    - *Khác nhau:* Nó **không có tính chất ngưỡng an toàn**. Trên chuỗi thẳng, mỗi nút chỉ có tối đa 1 nút sau nên $R_0$ luôn $\le 1$ dù cả chuỗi bị nhiễm sạch; trên mạng hình sao (6 lá trỏ vào 1 trung tâm), tỷ lệ nhiễm đích là `0.725` nhưng $R_0 = 0.420 < 1$ vì nút trung tâm chẳng có ai phía sau để lây tiếp.

---

### Ý 4 (Sec. 3.6 — đoạn 3): *"I did not follow the sentence that started 'Effectiveness is thus conditional on lying on a minimal s-t cut...'"*

- **Nguyên văn câu đó trong bài (`contagion_aamas2027.tex`, dòng 590–591):**
  > *"Effectiveness is thus conditional on lying on a minimal $s$--$t$ cut, and where a unique path exists it is path-specific; we therefore avoid general 'equal effectiveness' claims..."*
- **Tại sao R2 không hiểu?** Câu này viết theo văn phong lý thuyết đồ thị rất cô đặc, lại dùng từ *"minimal $s$--$t$ cut"* khá đột ngột.
- **Dịch nôm na dễ hiểu nhất:**
  - $s$ là điểm nguồn bị tiêm, $t$ là agent đích cuối cùng.
  - Giả sử từ $s$ đến $t$ có **2 đường song song**: `s -> A -> t` và `s -> B -> t`.
  - Nếu bạn chỉ đặt phòng thủ ở `A`, tấn công vẫn chui qua `B` để tới `t` bình thường. Muốn chặn tuyệt đối tới `t`, bạn phải chặn đồng thời `{A, B}` — tập các nút ít nhất mà khi chặn hết thì **không còn đường nào từ $s$ tới $t$** được gọi là **lát cắt tối thiểu ($s$--$t$ cut)**.
  - Nói cách khác: *"Một lớp phòng thủ đặt tại 1 nút đơn lẻ chỉ triệt tiêu được tấn công tới đích khi nút đó là cổ chai bắt buộc mọi đường đi đều phải đi qua (tức là tự nó tạo thành một lát cắt kích thước 1); nếu có đường song song thì phải chặn cả tập hợp các nút trên lát cắt."*

---

### Ý 5 (Sec. 5.1): *"Certain claims in the evaluation section in Section 5.1 seem straightforward, i.e., that per-hop compromise probabilities do a poor job of estimating overall compromise probability due to overlapping paths."*

- **Cảnh báo — ĐÂY LÀ CHỖ R2 ĐỌC NHẦM!**
  - R2 tưởng Sec. 5.1 đang chứng minh một chuyện *"hiển nhiên"*: nhân xác suất từng bước bị sai là vì các đường đi bị **chồng chéo lên nhau** (*overlapping paths*).
  - **Sự thật trong bài (Sec. 5.1, Tables 1–4):** Thí nghiệm ở Sec. 5.1 chạy trên **chuỗi thẳng 4 agent (`a0 -> a1 -> a2 -> a3`)** — hoàn toàn **chỉ có 1 đường đi duy nhất (single-path)**, KHÔNG hề có nhánh nào chồng lên nhau cả!
  - Nếu hệ thống tuân theo giả định Markov độc lập thông thường, thì trên chuỗi 1 đường đi, tích $\prod s_i^{\mathrm{ctrl}}$ **bắt buộc phải khớp** $\mathrm{ASR}$. Thế nhưng trên Llama nó lệch tới `3.75x` (`0.233` vs `0.850`, Table 2). Thủ phạm không phải chồng đường đi, mà là **đo cô lập không phản ánh đúng môi trường chuỗi** (*non-transportability*: `0.067` bản trơ vs `0.967` bản bọc trong báo cáo ở Table 4).
  - **Cách trả lời:** Lịch sự đính chính lại cho R2 hiểu Sec. 5.1 là **chuỗi 1 đường đi**, không có chồng đường đi (phần đường đi chồng lên nhau / tổ tiên chung nằm riêng ở Appendix Q). Khi R2 nhận ra mình đọc nhầm chỗ này, giá trị phát hiện của Sec. 5.1 sẽ tăng vọt trong mắt R2!

---

### Ý 6 (Sec. 5.4 & cuối Sec. 5.1): *"Section 5.4 is difficult to follow: what is 'supercritical'? The last few sentences on the content-form ablation are also hard to follow."*

Đây là **2 lỗi trình bày có thật** trong bài chính vì nén 8 trang quá chặt:

1. **`"what is supercritical?"` (Sec. 5.4, dòng 936–951):**
   - Trong mạng có **vòng lặp (cycle)** — 1 Manager giao việc cho nhiều Worker, Worker gửi báo cáo ngược lại cho Manager — khi đó ma trận truyền nhiễm không còn tam giác trên nữa nên $\rho(M) = \sqrt{\sum_j a_j c_j} > 0$.
   - **Supercritical (siêu tới hạn)** nghĩa là $\rho(M) > 1$: mỗi vòng lặp tự sinh ra nhiều hơn 1 ca nhiễm mới, nên sự lây nhiễm **tự duy trì mãi không tắt**. (Ngược lại $\rho(M) < 1$ là **subcritical**, tắt dần).
   - **Lỗi gõ/in chết người ở dòng 942–945:** Câu văn viết công thức $\rho(M) = \sqrt{\sum_j a_j c_j}$, nhưng 3 con số in ngay bên dưới lại là `1.800`, `1.018`, `0.578` — đó là giá trị **chưa lấy căn** ($\sum_j a_j c_j$), trong khi số ở giữa dòng 943 lại là `1.351` (đã lấy căn $\sqrt{\dots}$)! Đáng lẽ $\rho(M)$ của 3 model phải ghi là **`1.342`, `1.009`, `0.760`** (như đã in đúng ở `supplementary.tex` Table 5). Không định nghĩa "supercritical" cộng thêm in nhầm số chưa lấy căn làm R2 đọc không thể hiểu nổi!
2. **`"The last few sentences on the content-form ablation are also hard to follow"` (cuối Sec. 5.1, dòng 852–856):**
   - Đoạn cuối Table 4 chỉ có 5 dòng nhưng dồn 2 ý nhảy cóc: vừa nói cạnh cuối `a2->a3` của Llama bị đảo chiều + trượt self-check (`0.733` vs `0.947`), vừa chuyển phắt sang nhận xét về Nova Pro (*"the frontier model's block runs against its own headline rate..."*) mà không giải thích chuyển đoạn.

---

## 3. Tổng kết chiến lược cho Reviewer 2

- **Điểm hiện tại:** Proceedings `5` / Findings `6`.
- **Cơ hội:** R2 là reviewer **dễ kéo từ 5 lên 6–7 nhất** vì R2 không yêu cầu thêm bất kỳ thí nghiệm nào! Toàn bộ vướng mắc của R2 đều là:
  1. Đính chính hiểu nhầm Sec. 5.1 (*single-path chain*, không phải chồng đường đi).
  2. Ghi rõ công thức `ASV` và `MR`.
  3. Tách bạch 3 ý ở Sec. 3.6 (Eq. (3) khi nào chính xác/xấp xỉ, $R_0$ thực nghiệm vs $R_0$ chuẩn, giải thích dân dã câu *minimal $s$--$t$ cut*).
  4. Định nghĩa `supercritical` ($\rho(M) > 1$) và sửa lại bộ 3 con số đã lấy căn (`1.342 / 1.009 / 0.760`).

*(Lưu ý kiểm tra: File nháp `rebuttal/review2.md` hiện tại đã viết đúng cả 4 điểm này rất gọn gàng và sát số liệu trong bài.)*

---

## 4. Kế hoạch hành động riêng cho Reviewer 2 (tách từ `plan_rebuttal.md`)

> **Mục tiêu:** Kéo R2 từ Proceedings `5` / Findings `6` lên `6+ / 7`.
> **Tin vui:** Với R2, **KHÔNG cần chạy thêm bất kỳ thực nghiệm nào** — toàn bộ câu hỏi của R2 xử lý bằng text rebuttal ($\le 2{,}500$ ký tự) + cam kết chỉnh sửa văn phong/ký hiệu ở bản **Camera-Ready**.

### A. Giai đoạn Rebuttal (HIỆN TẠI — KHÔNG sửa PDF)

- **Bước 4 (Rà & chốt `rebuttal/review2.md` $\le 2{,}500$ ký tự):**
  - Giữ đúng 4 điểm cốt lõi đã soạn trong `rebuttal/review2.md`:
    1. Đính chính nhẹ Sec. 5.1 là **single-path chain** (`a0->a1->a2->a3`, không chồng đường đi — phần chồng đường đi nằm ở App. Q Table 14).
    2. Ghi tường minh công thức `ASV` ($|B(t)\cap B(y)|/|B(t)|$) và `MR` ($2|B(y)\cap B(y_{\mathrm{ref}})|/(|B(y)|+|B(y_{\mathrm{ref}})|)$).
    3. Tách rõ 3 ý ở Sec. 3.6: phạm vi chính xác vs xấp xỉ của Eq. (3), điểm chung/khác giữa $R_0$ thực nghiệm và $R_0$ chuẩn, và giải nghĩa bình dân *minimal $s$--$t$ cut*.
    4. Định nghĩa rõ *supercritical* ($\rho(M) = \sqrt{\sum_j a_j c_j} > 1$) kèm đủ bộ số đã lấy căn (`1.342`, `1.009`, `0.760`, App. F Table 5).
  - Đảm bảo mọi chỗ hứa sửa đều ghi rõ thực hiện ở *"In the camera-ready version..."*, không chèn link ngoài, kiểm tra độ dài $\le 2{,}500$ ký tự.

### B. Giai đoạn Camera-Ready (SAU ACCEPTANCE — thực hiện theo `Bước CR-1`)

- **Sec. 3.2:** Thêm công thức tường minh của `ASV` và `MR` vào bài chính.
- **Sec. 3.6:**
  - Tách rõ phạm vi *chính xác* (đường đi thượng nguồn rời nhau) vs *xấp xỉ biên* (DAG có tổ tiên chung) của Eq. (3).
  - Viết phần so sánh $R_0$ thực nghiệm với $R_0$ chuẩn (chung ý nghĩa *local branching average* nhưng không có ngưỡng trên DAG hữu hạn do $\rho(M)=0$).
  - Viết lại cho dễ đọc câu *minimal $s$--$t$ cut*.
- **Sec. 5.1:** Thêm cụm *"single-path chain"* ngay đầu mục để tránh hiểu nhầm chồng đường đi; đơn giản hóa các câu cuối của *content-form ablation*.
- **Sec. 5.4:** Đổi tiêu đề mục thành *"Cyclic Topologies"*; định nghĩa tường minh *"supercritical"* ($\rho(M) = \sqrt{\sum_j a_j c_j} > 1$); sửa lỗi in nhầm $\sum_j a_j c_j$ bằng cách in rõ cả $\rho(M) = 1.342 / 1.009 / 0.760$ bên cạnh $\sum_j a_j c_j = 1.800 / 1.018 / 0.578$ (khớp App. F Table 5).
- **Đồng bộ `supplementary.tex`:** Rà soát và sửa toàn bộ tham chiếu bằng chữ sang bài chính đang lệch số mục (*"Section 3.8"* $\to$ *"Section 3.6"*, *"Section 5.9"* $\to$ *"Section 5.5"*, *"Section 5.3"* $\to$ *"Section 5.1"*).

