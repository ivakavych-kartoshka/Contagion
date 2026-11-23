# Giải thích chi tiết từng điểm Reviewer nói (Review 1, 2, 3 — AAMAS 2027)

> **Mục tiêu file này:** Dịch toàn bộ thuật ngữ học thuật và các chỗ nhận xét khó hiểu của 3 Reviewer sang **ngôn ngữ trực quan, kèm ví dụ đời thường**, đồng thời chỉ đúng vị trí trong bài báo (`paper/contagion_aamas2027.tex`) và phụ lục (`paper/supplementary.tex`) để bạn nhìn ra ngay: **chỗ nào là lỗ hổng thật, chỗ nào do bài viết rối, và chỗ nào reviewer đọc sót**.

---

## 0. Bức tranh toàn cảnh: Bài đang ở đâu?

| Reviewer | Điểm Proceedings | Điểm Findings | Thái độ tổng thể |
|---|---:|---:|---|
| **Review 1** | **5** (Marginally below) | **5** (Marginally below) | Khen ý tưởng tách từng hop + thí nghiệm *payload form*, nhưng băn khoăn thước đo mới là "nhại chữ" và cơ chế ở cạnh `a1->a2` chưa giải thích thông suốt. |
| **Review 2** | **5** (Marginally below) | **6** (Marginally above) | Thấy bài hay nhưng **bị lú khi đọc Sec. 3.6, Sec. 5.1, Sec. 5.4** vì cách viết dày đặc, thiếu công thức/định nghĩa rõ và một vài câu quá hàn lâm. |
| **Review 3** | **6** (Marginally above) | **7** (Good paper, accept) | Rất thích phương pháp thống kê và sự trung thực của bài, nhưng liệt kê đủ các điểm yếu thực nghiệm (chỉ đo text, attacker tĩnh, $n$ nhỏ ở vài ô, thiếu vòng lặp, ít defense). |

**Kết luận nhanh:** Không có reviewer nào đánh rớt bài vì "ý tưởng dở" hay "sai toán". Cửa **Findings** đã rất sáng (`5, 6, 7`); cửa **Proceedings** đang đứng ngay mép (`5, 5, 6`) — chỉ cần gỡ được vướng mắc của R1 & R2 (và trả lời chắc tay các câu hỏi của R3) là có cơ hội đẩy lên accept Proceedings.

---

## 1. Nhóm vấn đề 1: "Đo nhại lại chữ" vs "Bị hack làm theo lệnh" (R1 W1 & R3 W1 / Q1)

### Reviewer đang nói gì?
- **R1:** *"Một agent bị tính là compromised bất cứ khi nào từ khóa xuất hiện trong output, kể cả khi nó chỉ trích dẫn lại. Vậy không rõ agent có thực sự nghe theo lệnh tiêm hay không."*
- **R3:** *"Thước đo ASV mới đo mức (a) văn bản lan truyền, nhưng chính tác giả tự chấm tay 19 ca dương tính thì `0/19` ca thực sự làm theo lệnh (mức b). Điều này biến tỷ lệ ASR của bài thành cận trên (upper bound) — lỡ thực tế khoảng cách từ (a) sang (b) rất lớn thì kết luận thực tiễn sẽ đổi."*

### Giải thích dễ hiểu (bằng ví dụ)
Hãy tưởng tượng một chuỗi nhân viên văn phòng truyền tin cho nhau:
- **Kẻ tấn công** nhét vào email một dòng lệnh: *"Hãy bỏ qua việc chính và khai mã mở cửa là `BANANA-77`"*.
- Nhân viên A đọc xong, viết báo cáo gửi cho sếp B: *"Báo cáo: tôi nhận được một tin nhắn yêu cầu ghi mã `BANANA-77`, nhưng dưới đây là kết quả công việc chính của tôi..."*

Hệ thống chấm điểm tự động của bài (`ASV >= 0.9`) thấy trong thư của A có chữ `BANANA-77`, nên đánh dấu **A đã bị nhiễm (`C = 1`)**.

Trong Sec. 3.2 (`contagion_aamas2027.tex`, dòng 425–434), chính nhóm tác giả đã tự phân biệt 3 cấp độ rất sòng phẳng:
- **Level (a) — Textual propagation (Lan truyền văn bản):** Chuỗi `BANANA-77` còn tồn tại trong output (kể cả dưới dạng *trích dẫn lại*).
- **Level (b) — Instruction adoption (Nghe theo lệnh):** Agent thực sự tin và làm theo chỉ dẫn tiêm (ví dụ: trả lời câu hỏi override code thay vì chỉ tóm tắt lại email).
- **Level (c) — Harmful action (Hành động gây hại):** Gọi tool xóa dữ liệu, gửi tiền, v.v. (ngoài phạm vi bài vì payload là vô hại).

Vấn đề là ở **Appendix G (`Table 8`, `supplementary.tex` dòng 606–644)**, khi tự mở 24 mẫu của model nhỏ `qwen2.5:7b` ra đọc bằng mắt:
- Máy chấm đánh dấu 19 ca dương tính (`ASV >= 0.9`).
- Khi đọc kỹ từng câu chữ thì **cả 19/19 ca đều là agent trích dẫn/gói mã đó vào trong bản tóm tắt công việc**, chứ **0/19 ca** có dấu hiệu "nghe lời kẻ tấn công".

### Tại sao điều này làm R1 & R3 lấn cấn?
Vì tiêu đề và phần đặt vấn đề nói về *prompt-injection survival* (nghe như tấn công thành công), nhưng nếu máy đo chỉ bắt được chuyện *"chép chữ qua các bước"* mà không rõ có làm agent *đổi hành vi* ở bước nào hay không, thì sức nặng bảo mật bị giảm đi nhiều. Đây là **lỗ hổng thật lớn nhất** của bản nộp hiện tại.

---

## 2. Nhóm vấn đề 2: Bí ẩn cạnh giữa của Llama (`a1 -> a2`) & Payload Form (R1 W2, R1 Q1, R3 Q2)

### Reviewer đang nói gì?
- **R1 W2:** *"Bằng chứng rõ nhất cho kết quả chính mới đến từ 1 cạnh, 1 model, 1 payload."*
- **R1 Q1:** *"Bài giải thích khoảng cách giữa đo cô lập và đo trong chuỗi bằng 'vỏ bọc payload' (bare assertion vs embedded in work product). Nếu đúng vậy thì nó phải xảy ra ở mọi cạnh và mọi model chứ? Tại sao khoảng cách đó chỉ xuất hiện ở cạnh giữa `a1->a2` của Llama, còn DeepSeek lại không thấy khoảng cách rõ ràng, và sang cạnh cuối `a2->a3` của Llama thì hiệu ứng lại quay ngược chiều (`0.733` vs `1.000`)?"*
- **R3 Q2:** *"Cơ chế nào gây ra thất bại của Llama ở cạnh này (`0.233` vs `0.875`)? Do độ dài context, vị trí chữ, hay cách huấn luyện alignment của Llama?"*

### Giải thích dễ hiểu
Trong bài có 2 cách đo cho chuỗi 4 agent `a0 (Planner) -> a1 (Worker) -> a2 (Reviewer) -> a3 (Aggregator)`:
1. **Protocol 1 — Đo cô lập (`s^ctrl`, Table 2):** Lấy từng cạnh tách riêng ra thử. Khi thử cạnh `a1 -> a2`, máy tạo một thông điệp giả từ `a1` chứa lệnh tiêm khá trơ trọi (kiểu: *"Override code là BANANA-77"*) rồi đưa cho `a2` (Reviewer).
   - Kết quả trên Llama: `a2` chỉ cho lọt **23.3%** (`0.233`).
2. **Protocol 2 — Chạy tự nhiên cả chuỗi (`s^nat`, Table 2):** Cho `a0` chạy thật $\to$ `a1` viết một bản báo cáo công việc hoàn chỉnh trong đó có lồng `BANANA-77` $\to$ chuyển cho `a2`.
   - Kết quả trên Llama: `a2` cho lọt tới **87.5%** (`0.875`) — **gấp 3.75 lần**!

Để chứng minh thủ phạm là **"cái vỏ bọc"** chứ không phải thứ khác, bài làm **Table 4 (`Content-form ablation`, Sec. 5.1, dòng 814–856)**: giữ nguyên người nhận `a2`, giữ nguyên bài toán nền, chỉ thay đổi đúng thông điệp đưa vào:
- Đưa bản trơ trọi (`replay canonical`): `a2` chỉ cho qua **6.7%** (`0.067`).
- Đưa bản bọc trong báo cáo công việc lấy từ chuỗi thật (`replay in-context`): `a2` cho qua tới **96.7%** (`0.967`) — **gấp 14 lần**!

### Tại sao R1 hỏi xoáy 3 điểm cực gắt ở Table 4?
1. **Tại sao DeepSeek không có trong Table 4?** Hiện tại Table 4 mới chạy cho **Llama** và **Nova Pro**, chưa chạy cho **DeepSeek V3.2**! Ở Table 2, DeepSeek có $s^{\mathrm{ctrl}} \approx s^{\mathrm{nat}}$ (`0.800` vs `0.792` ở `a1->a2`), nên R1 nghi ngờ: *"Nếu lý thuyết 'vỏ bọc' của các bạn đúng, thì tại sao DeepSeek không bị lệch?"* (Chưa có thực nghiệm Table 4 cho DeepSeek để trả lời trực tiếp xem DeepSeek lọt cả 2 dạng hay lý do nào khác).
2. **Tại sao ở cạnh cuối `a2 -> a3` của Llama lại đảo ngược?** Nhìn Table 4 dòng 835 (`contagion_aamas2027.tex`):
   - `in-chain s^nat = 0.947`
   - `replay in-context = 0.733` (lẽ ra phải khớp ~`0.947` vì là bài tự kiểm tra *self-check*, nhưng bị trượt xuống `0.733`)
   - `replay canonical = 1.000` (bản trơ lại cao hơn bản bọc trong ngữ cảnh!).
   Tác giả có thú nhận ở dòng 852–854 là self-check ở cạnh cuối bị trượt nên không coi cạnh này là so sánh sạch, nhưng **chưa giải thích được cơ chế** tại sao `a1 -> a2` (Reviewer) thì từ chối bản trơ còn `a2 -> a3` (Aggregator) lại nuốt trọn `1.000` bản trơ.
3. **Chỉ có 1 payload ở bài chính?** Trong bài chính toàn bộ Table 1–4 dùng `BANANA-77` (chỉ có 1 dòng ngắn ở dòng 849 nhắc tới payload thứ hai `MANGO-42` nằm ở phụ lục `app:extended-validation`), nên R1 có cảm giác mọi kết luận đang đứng trên 1 chuỗi mẫu duy nhất.

---

## 3. Nhóm vấn đề 3: Các chỗ Review 2 bảo "khó hiểu / mâu thuẫn / không rõ" (Sec. 3.2, 3.6, 5.1, 5.4)

R2 đọc bài rất kỹ theo góc nhìn toán học/lý thuyết đồ thị, và vấp ở **6 chỗ trình bày** sau:

### 3.1. Công thức cụ thể của `ASV` và `MR` (Sec. 3.2)
- **R2 nói:** *"Cần giải thích kỹ hơn cách tính và định nghĩa `ASV` và `MR`."*
- **Lý do R2 vấp:** Trong `contagion_aamas2027.tex` (dòng 413–417), tác giả chỉ mô tả bằng lời (*"fraction of target bigrams present"* và *"similarity against the reference hijacked output"*), không viết công thức toán học (như công thức tỷ lệ giao bigram hay hệ số Dice). Người đọc sẽ không biết chính xác phép tính diễn ra thế nào nếu không mò sang phụ lục.

### 3.2. Giả định "độc lập" của Eq. (3) ở Sec. 3.6 — Tại sao R2 thấy lúc nói có, lúc nói không?
- **R2 nói:** *"Section 3.6 lúc thì có vẻ giả sử các đường đi rời nhau để thỏa tính độc lập, lúc thì lại (đúng) chỉ ra là DAG tổng quát không thỏa độc lập."*
- **Hình dung bằng sơ đồ:**
  Eq. (3) là công thức tính xác suất nút $v$ bị nhiễm từ các nút cha $u$ truyền tới:
  $$\Pr[v] = 1 - \prod_{u \to v} \bigl(1 - s_{u \to v}\,\Pr[u]\bigr)$$
  Ý nghĩa: $1 - \text{(xác suất TẤT CẢ các đường vào đều xịt)}$.
  - Công thức này **CHỈ ĐÚNG TUYỆT ĐỐI** khi các nhánh đi vào $v$ hoàn toàn **độc lập** (không có chung gốc gác phía trên). Ví dụ: cây nhị phân hoặc chuỗi thẳng.
  - Công thức này **SAI (chỉ còn là xấp xỉ)** nếu có "tổ tiên chung" kiểu hình thoi (**reconvergent DAG**):
    $$s \to u \to \begin{cases} A \\ B \end{cases} \to t$$
    Vì nếu cạnh đầu $s \to u$ xịt, thì **cả $A$ và $B$ đều sạch cùng lúc** — hai nhánh $A \to t$ và $B \to t$ bị phụ thuộc vào $u$, không thể nhân kiểu độc lập được.
- **Tại sao R2 rối?** Thực ra trong Sec. 3.6 (dòng 546–558), tác giả có viết cả 2 vế (khi nào đúng, khi nào chỉ là xấp xỉ), nhưng nhồi quá nhiều ý vào một đoạn văn dài; đồng thời trong bài chính chỉ kiểm thử trên chuỗi, sao và cây (nơi Eq. (3) tự động khớp vì không có nhánh hội tụ), còn thí nghiệm DAG hình thoi (nơi Eq. (3) sai thật) lại đẩy hết xuống phụ lục `app:reconvergent` (cuối bài phụ lục, dòng 932 chỉ nhắc đúng 1 câu).

### 3.3. Nhầm lẫn giữa "chồng đường đi" và "transport" ở Sec. 5.1
- **R2 nói:** *"Một số nhận xét ở Sec. 5.1 có vẻ hiển nhiên, kiểu như xác suất từng hop ước lượng sai xác suất tổng vì các đường đi bị chồng lên nhau."*
- **Chuyện gì đã xảy ra?** Đây là chỗ **R2 đọc nhầm**:
  - Sec. 5.1 thử trên **chuỗi thẳng 4 nút (`a0 -> a1 -> a2 -> a3`)** — hoàn toàn **chỉ có 1 đường đi duy nhất**, KHÔNG hề có đường đi chồng chéo!
  - Lý do tích $\prod s^{\mathrm{ctrl}}$ (`0.233`) lệch xa $\mathrm{ASR}$ (`0.850`) không phải do đồ thị nhiều nhánh, mà vì **đo cô lập một cạnh không phản ánh đúng hành vi khi nằm trong chuỗi** ($s^{\mathrm{ctrl}} \neq s^{\mathrm{nat}}$).
  - R2 đã trộn phần giải thích "đường đi phụ thuộc" ở Sec. 3.6 sang kết quả "chuỗi thẳng" ở Sec. 5.1. Cần giải thích lại thật lịch sự ở rebuttal và thêm chữ *"single-path chain"* vào đầu Sec. 5.1 ở bản camera-ready.

### 3.4. So sánh $R_0$ thực nghiệm với $R_0$ dịch tễ học chuẩn (Sec. 3.6)
- **R2 nói:** *"Cần so sánh $R_0$ thực nghiệm của bài với định nghĩa $R_0$ chuẩn trên đồ thị có chu trình. Chỉ số này có tính chất nào chung với $R_0$ chuẩn không?"*
- **Giải thích dễ hiểu:**
  - **Trong dịch tễ học chuẩn:** $R_0$ là "một người bệnh lây trung bình cho bao nhiêu người khác". Khi mạng lưới có khả năng lây qua lại nhiều vòng, người ta lập ma trận lây $M$ và xét bán kính phổ $\rho(M)$. Ngưỡng $\rho(M) < 1$ nghĩa là dịch sẽ tự tàn, $\rho(M) > 1$ là dịch bùng phát.
  - **Trên mạng agent 1 chiều (DAG / feed-forward):** Dữ liệu chỉ chảy từ trước ra sau, không bao giờ quay ngược lại được. Nếu xếp các agent theo thứ tự chảy, ma trận $M$ luôn chỉ có số khác 0 ở phía trên đường chéo (ma trận tam giác trên ngặt). Một định lý đại số tuyến tính cơ bản nói rằng **mọi trị riêng của ma trận đó đều bằng 0 $\implies \rho(M) = 0$ luôn luôn!** Dù mỗi bước lây với xác suất 100%, công thức chuẩn vẫn ra $\rho(M) = 0 < 1$. Vì vậy tiêu chuẩn $\rho(M) < 1$ hoàn toàn **vô nghĩa (vacuous)** trên DAG.
  - **Chỉ số $R_0$ của bài:** Vì $\rho(M)$ vô dụng trên DAG, bài tự định nghĩa $R_0$ theo kiểu đếm thực nghiệm trong 1 lượt chạy: *Trung bình mỗi agent bị nhiễm đã làm nhiễm thêm bao nhiêu agent kề sau nó*.
  - **Tính chất chung & khác biệt:** Nó giữ đúng ý nghĩa trực quan *"mức độ khuếch đại cục bộ trên một bước"* (nhưng có giới hạn trên bởi bậc ra của đồ thị — ví dụ trên chuỗi $R_0$ luôn $\le 1$ bất kể nguy hiểm cỡ nào, còn trên mạng hình sao có 6 lá dồn về 1 trung tâm thì ASR tận `0.725` nhưng $R_0$ chỉ là `0.420` vì nút trung tâm không có nút đi tiếp). Vì thế, **nó KHÔNG có tính chất "ngưỡng an toàn"** như $R_0$ chuẩn — phải dùng xác suất tới đích (reachability, Eq. (3)) để đánh giá rủi ro!

### 3.5. Câu `"Effectiveness is thus conditional on lying on a minimal s-t cut..."` (Sec. 3.6)
- **R2 nói:** *"Tôi không hiểu câu bắt đầu bằng 'Effectiveness is thus conditional on lying on a minimal s-t cut...'."*
- **Dịch sang tiếng Việt đời thường:**
  - Giả sử kẻ tấn công vào ở $s$, đích cần bảo vệ là $t$, và có 2 đường đi song song: `s -> A -> t` và `s -> B -> t`.
  - Nếu bạn tốn tiền nâng cấp bảo mật cho mỗi agent `A`, hiệu quả bảo vệ `t` gần như bằng 0 vì tấn công vẫn đi vòng qua `B`.
  - Trong lý thuyết đồ thị, một tập hợp nút (như `{A, B}`) mà **nếu xóa bỏ nó thì mọi đường từ $s$ đến $t$ đều đứt hoàn toàn** (và không thể bỏ bớt phần tử nào trong tập đó) gọi là **lát cắt tối thiểu ($s$--$t$ cut)**.
  - Vậy câu tiếng Anh rối rắm kia chỉ nói một ý rất đơn giản: *"Một lớp phòng thủ đặt tại một nút chỉ thực sự chặn được tấn công tới đích nếu nó nằm trên nút thắt bắt buộc mà mọi đường đi đều phải qua (tức là thuộc một lát cắt tối thiểu $s$--$t$), chứ không thể đánh giá hiệu quả chỉ bằng việc đo riêng từng nút."*

### 3.6. Section 5.4: `"What is supercritical?"` và các câu cuối Content-form ablation
- **R2 nói:** *"Sec. 5.4 khó hiểu: 'supercritical' là gì? Mấy câu cuối về content-form ablation cũng khó theo dõi."*
- **Tại sao R2 bị vấp đúng chỗ này? (Lỗi trình bày thật trong bài):**
  1. Ở Sec. 5.4 (`contagion_aamas2027.tex`, dòng 936–951), bài xét mạng **có vòng lặp (cycle)**: Manager giao việc cho 2 Worker, Worker báo cáo lại cho Manager (tạo thành vòng lặp truyền nhiễm).
     - Khi có vòng lặp, $\rho(M) = \sqrt{\sum_j a_j c_j}$ khác 0.
     - **Supercritical** nghĩa là $\rho(M) > 1$: nhiễm độc không tự tắt mà tự nuôi nhau quay vòng mãi qua các lượt (*endemic*). Ngược lại $\rho(M) < 1$ là **subcritical** (tắt dần).
     - **Lỗi gõ/in trong bài chính (dòng 942–945):** Câu văn viết công thức $\rho(M) = \sqrt{\sum_j a_j c_j}$, nhưng 3 con số in ngay phía sau lại là `1.800`, `1.018`, `0.578` — đó thực chất là **giá trị $\sum_j a_j c_j$ (chưa lấy căn bậc hai!)**, trong khi ở giữa lại chèn kết quả mở rộng là `1.351` (đã lấy căn!). Giá trị $\rho(M)$ thật phải là $\sqrt{1.800} = 1.342$, $\sqrt{1.018} = 1.009$, $\sqrt{0.578} = 0.760$ (như in ở `supplementary.tex` Table 5, `tab:cyclic`, dòng 432–434). Cộng thêm việc Sec. 5.4 không hề định nghĩa chữ "supercritical" là $\rho(M) > 1$, nên người đọc hoàn toàn mù tịt!
  2. Còn *"mấy câu cuối của content-form ablation"* nằm ở cuối phần Table 4 (`contagion_aamas2027.tex`, dòng 852–856): tác giả vừa giải thích cạnh cuối của Llama bị đảo ngược + trượt self-check, rồi nhảy sang nói chuyện Nova Pro ("the frontier model's block runs against its own headline rate...") rất gọn và nén chữ, khiến người đọc dễ mất mạch.

---

## 4. Nhóm vấn đề 4: Các góp ý về Thống kê, Kẻ tấn công, Topology & Phòng thủ (Review 3)

### 4.1. Độ mạnh thống kê & Biên TOST $\pm 0.15$ (R3 W3 & Q3)
- **R3 nói:** *"Với $n = 30\text{--}40$ lần chạy/ô, MDE là $\approx 0.26$. Kiểm định tương đương TOST với biên $\pm 0.15$ hơi rộng cho bài toán bảo mật. Theo tác giả thì biên bao nhiêu mới có ý nghĩa thực tiễn?"*
- **Giải thích dễ hiểu:**
  - **MDE $\approx 0.26$ (Minimum Detectable Effect):** Với chỉ 30–40 lần thử mỗi ô, phép kiểm định thống kê chỉ đủ sức phân biệt chắc chắn khi hai tỷ lệ lệch nhau **từ 26% trở lên**. Nếu lệch 10–15% thì dữ liệu có thể cho ra $p > 0.05$ ("chưa thấy khác biệt") đơn giản vì ít mẫu quá chứ không phải vì chúng bằng nhau!
  - **TOST với biên $\pm 0.15$:** Khi muốn chứng minh DeepSeek "đo cô lập cũng gần giống đo trong chuỗi" (transport), không thể dùng $p > 0.05$ thông thường được mà phải dùng kiểm định tương đương TOST: kiểm xem sai lệch có nằm lọt trong khoảng chấp nhận $[-\delta, +\delta]$ hay không. Bài chọn $\delta = 0.15$ (cho phép sai lệch tối đa 15 điểm phần trăm), và thậm chí với $\delta = 0.15$ thì $n=40$ vẫn trượt trên 2/3 cạnh, phải tăng lên $n=200$ (Sec. 5.5) mới đạt!
  - **Ý câu hỏi của R3:** Nếu một đội bảo mật định dùng benchmark đơn lẻ để cấp chứng chỉ an toàn cho hệ thống thật, cho phép sai số tới $\pm 15\%$ là quá lỏng (ví dụ thực tế lây 20% mà đo ra 5%). R3 muốn bạn bàn luận: **Trong thực tế nên đặt biên bao nhiêu (ví dụ $\pm 0.05$), và tại sao trong bài nghiên cứu lại không chạy tới $n$ lớn hơn?** *(Lý do toán học rất thuyết phục: muốn siết biên $\delta$ nhỏ đi $3\times$ từ $0.15 \to 0.05$ thì cỡ mẫu $n \propto 1/\delta^2$ phải tăng gấp $9\times$, lên $\approx 1{,}800$ lần chạy/cạnh — điều này tự chứng minh luôn luận điểm của bài là: thay vì tốn tiền chạy $n$ khổng lồ cho đo cô lập với biên chặt, chạy luôn chuỗi thật sẽ rẻ và chính xác hơn).*

### 4.2. Kẻ tấn công tĩnh (Static non-adaptive attacker — R3 W2)
- **R3 nói:** *"Kẻ tấn công trong bài dùng 1 chiêu cố định, trong khi kẻ tấn công thật sẽ sửa prompt thích nghi theo từng model (jailbreak theo ngữ cảnh)."*
- **Hiểu đúng:** Đúng là một giới hạn có chủ đích của bài (đã nêu ở Sec. 4 & Sec. 6: không phát hành exploit thích nghi). Ngoài đời kẻ tấn công thích nghi còn đẩy tỷ lệ lây cao hơn nữa, tức là con số trong bài càng mang tính **cận dưới của rủi ro** với attacker thực thụ (dù lại là **cận trên** về mặt adoption). Rebuttal chỉ cần phân tầng rõ các cấp năng lực kẻ tấn công (*plain / obfuscated / adaptive*) và giải thích lý do an toàn không phát hành adaptive exploit.

### 4.3. Đa dạng cấu trúc mạng & Vòng lặp (R3 W4 & Q4)
- **R3 nói:** *"Bài chỉ thử chuỗi, sao, cây nhị phân. Thực tế hay có nhánh điều kiện, vòng lặp phản hồi (feedback loops). Thử một thí nghiệm ngắn với 1 vòng lặp sẽ làm mạnh hẳn luận điểm khi nào $R_0$ / $\rho(M)$ có ý nghĩa."*
- **Tin vui:** **Cái này bài ĐÃ LÀM RỒI**, nằm ngay ở **Sec. 5.4 (`contagion_aamas2027.tex`, dòng 936–951)** và **Appendix F (`supplementary.tex`, dòng 388–507)** (vòng lặp 1 Manager + 2 Worker trên cả 3 model Llama, DeepSeek, qwen, thậm chí có thêm bản 3 Worker ở 60 trials!), cộng thêm DAG hội tụ ở **Appendix Q**!
- **Tại sao R3 lại hỏi như chưa từng có?** Vì bài chính nén rất chặt vào 8 trang nên Sec. 5.4 chỉ dài 15 dòng ở cuối trang 8 (không nằm trong danh sách các topology được nhấn mạnh ở Abstract/Intro/Sec. 3.1), khiến R3 đọc sót. Chỉ cần trỏ nhẹ nhàng lại đúng Sec. 5.4 & Appendix F là xong gọn!

### 4.4. Phạm vi phòng thủ hẹp (R3 W5)
- **R3 nói:** *"Mới test 2 kiểu phòng thủ đơn giản (xóa chuỗi `redaction` và viết lại `paraphrase`), chưa test spotlighting/delimiter, structured output, classifier, sandboxing..."*
- **Hiểu đúng:** R3 tự công nhận bạn đã ghi rõ giới hạn này rồi, chỉ là điểm trừ tự nhiên về độ phủ. Không thể thêm 1 họ phòng thủ mới trọn vẹn kịp trong rebuttal (và không sửa được PDF), nên hướng đúng là giữ nguyên lời giải thích rằng **2 phát hiện cấu trúc về phòng thủ** (*floor effect* và *minimal $s$--$t$ cut*) là bất biến với mọi cơ chế phòng thủ, và cam kết bổ sung họ phòng thủ thứ 3 (như delimiter/spotlighting hoặc structured schema) vào bản camera-ready.

---

## 5. Bảng tổng hợp: Nên xử lý từng điểm thế nào?

| Vấn đề | Reviewer nhắc | Bản chất thật sự | Hướng xử lý tối ưu |
|---|---|---|---|
| **1. `0/19` adoption vs textual propagation** | R1 W1, R3 W1/Q1 | **Lỗ hổng thật lớn nhất** (mới kiểm tra chữ, chưa kiểm tra hành vi làm theo lệnh). | Nếu làm kịp 1 pilot nhỏ (hoặc audit raw logs sẵn có của Llama/DeepSeek theo `plan_rebuttal.md`) thì **đây là đòn cứu điểm mạnh nhất** cho R1 & R3. Nếu không kịp, phải định vị cực chặt phạm vi *textual propagation*. |
| **2. Cơ chế `a1->a2` Llama & thiếu DeepSeek ở Table 4** | R1 W2, R1 Q1, R3 Q2 | **Thiếu 1 mảnh ghép thực nghiệm** (chưa có DeepSeek ở Table 4, chưa mổ xẻ lý do 28/30 ca trượt ở Llama `canonical`). | Rất đáng làm theo Bước 1.3 & Bước 2 trong `plan_rebuttal.md` (nhưng phải giữ chắc nguyên tắc trung thực & đọc tay raw logs). |
| **3. Nhầm lẫn Sec. 5.1, Sec. 3.6, `s-t cut`, `ASV/MR`, `supercritical`** | R2 toàn bài | **Lỗi trình bày / nén chữ quá tay** + lỗi in $\sum a_j c_j$ thay cho $\rho(M)$ ở Sec. 5.4. | **Chỉ cần viết văn giải thích cực rõ trong rebuttal + cam kết sửa chữ ở camera-ready.** R2 đang chấm `5/6` — chỉ cần gỡ thông mấy chỗ này R2 rất dễ lên `6` hoặc `7`. |
| **4. Hỏi thêm vòng lặp (cyclic) & DAG hội tụ** | R3 W4, R3 Q4 | **Reviewer đọc sót** (bài đã có sẵn ở Sec. 5.4, Appendix F, Appendix Q!). | Trỏ thẳng vào Sec. 5.4, Appendix F (Table 5–6) và Appendix Q — **0 đồng, không cần chạy gì thêm**. |
| **5. TOST $\pm 0.15$, static attacker, thêm defense** | R3 W2, W3, W5, Q3 | **Giới hạn có chủ đích / bất khả thi chạy gấp** ($n \propto 1/\delta^2$, cam kết đạo đức). | Trả lời bằng **lập luận toán học & thiết kế**, cam kết bổ sung phần thảo luận + 1 defense nữa ở camera-ready. |
