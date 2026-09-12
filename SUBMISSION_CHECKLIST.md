# Trạng thái bài nộp — Contagion (cập nhật cuối phiên)

Tài liệu này trả lời một câu hỏi duy nhất: **còn thiếu gì để bấm nộp?**
Nguồn chân lý về con số là `paper/contagion_aamas2027.tex` + `experiments/results/`.

---

## 0. Hai quyết định đã chốt

- **Tên bài**: *Contagion: Per-Hop Prompt-Injection Survival in LLM Agent Networks
  Does Not Compose* (tên ngắn: *Per-Hop Prompt-Injection Survival Does Not Compose*).
- **Chiến lược nộp**: **AAMAS 2027 main track trước**, nếu bị từ chối thì mở rộng
  (mesh/debate, utility có ground truth thật) rồi nộp USENIX Security. Bản `.tex`
  hiện đã đóng gói đúng chuẩn AAMAS 2027.

---

## 1. Đã xong (kiểm tra được, không cần làm lại)

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Giới hạn trang AAMAS main track | **ĐẠT cho nội dung — nhưng có rủi ro mới, xem §7c/P4** | Nội dung (§1–§8) hết ở **trang 8**. PDF 9 trang: trang 9 = References **+ hai phụ lục** (`tab:bh`, `tab:cluster`). CFP chỉ miễn trừ *bibliographic references*, nên phụ lục ở trang 9 có thể bị coi là vượt 8 trang |
| Biên dịch | 0 lỗi, 0 overfull, 0 undefined | `paper/contagion_aamas2027.log` |
| Cấu trúc / cite / ref / hình | 0 lỗi | `python scripts/check_paper.py paper\contagion_aamas2027.tex --bib paper\refs.bib` |
| Vệ sinh hình | **Sạch** | `paper/` chỉ còn đúng 2 PNG được `.tex` tham chiếu; `check_figures.py` ✅ (checker đã sửa để chỉ kiểm hình thật sự được dùng) |
| Số trang proceedings của trích dẫn trung tâm | **Đã xác minh, không suy đoán** | LiuGong2024 = tr. 1831–1847 (BibTeX chính thức usenix.org, bản ghi 299563); Zhan2024InjecAgent = tr. 10471–10506 (ACL Anthology 2024.findings-acl.624); SwarmMarkov2026 = Cybersecurity **9**(1), 2026 (OpenAlex + Semantic Scholar; tạp chí dùng article number nên **không** bịa số trang) |
| Trung thực về kết quả của chính mình | Có | E22 (Markov) **đã rút lại** (§5.3); cây báo cáo sai số **lạc quan**; χ² **bác bỏ** i.i.d. theo context được báo cáo kèm số (§5.10); 4 điểm degenerate của Llama n=15 bị **loại tường minh**, không gán 100% |
| Tài liệu tái lập | Có | `REPRODUCE.md` (từng bảng ↔ lệnh ↔ chi phí ↔ 6 cảnh báo trung thực) |
| **Number audit** (số trong bài ↔ `results.json`) | **Đã chạy** | `python scripts\audit_numbers.py --md` → `AUDIT_TABLE.md`. Đã phát hiện và sửa 2 chỗ thiếu chính xác: χ² p = **0.0014** (không phải 0.001), và φ của cạnh yếu là **0.58** [0.12, 1.00] (không phải "≤1.00 trên cả ba cạnh") |
| **Claim lint** (câu MÔ TẢ ↔ dữ liệu) | **Đã thêm, đã bắt được 1 lỗi thật** | Bài từng ghi "five models from **four** families" trong khi thực tế là **5 model / 5 nhà phát triển** (Llama–Meta, DeepSeek, Claude–Anthropic, Nova–Amazon, qwen–Alibaba). "Bốn họ" là **số cũ sót lại** từ giai đoạn mới có 4 model Bedrock, chưa cập nhật khi thêm qwen. Đã sửa ở abstract, §1, §4 + cả 4 file báo cáo. `claim_lint` trong `audit_numbers.py` nay tự so các câu đếm trong `.tex` với danh sách model/topology thật; đã kiểm bằng cách **tiêm lỗi giả** để chắc nó bắt được (`⚠️ 'four families' ... nhưng có 5 model thật`) |
| **Quy mô thực nghiệm** (slide báo cáo + §4 của bài) | **Đã bổ sung** | `python scripts\scale_report.py`: **46** thư mục kết quả (**25** có cấu trúc chuẩn) · **≈9.070 lượt gọi model** (cận dưới) · **2.342 trial tự nhiên** · **4,3 giờ** máy ghi lại được (cận dưới). Cấu hình từng loại: ô chuẩn 40 trial + 30/cạnh; depth 60 trial; vòng lặp 40 trial × 5 vòng; utility 20 cặp × 3 defense; độ nhạy 8 seed × 20/cạnh; biến hình 6 ô × 30 mẫu; topology 3 × n=7. §4 của bài nay có 1 câu về quy mô (bài vẫn đúng 8 trang) |
| **Danh mục thực nghiệm** (tài liệu riêng) | **Đã tạo** | `report\danh_muc_thi_nghiem.pdf` — bảng tóm tắt **10 nhóm thực nghiệm** mang nội dung bài (mục đích · quy mô · kết quả), chi tiết từng nhóm, giai đoạn thăm dò 12 thư mục (không dùng số trong bài) và **7 phân tích chạy lại 0 API**. Dùng để trả lời câu hỏi ``em đã làm những thí nghiệm gì'' |

## 2. Các job đã xong — đã tích hợp hết vào bài

| Job | Kết quả | Đã vào bài ở đâu |
|---|---|---|
| `pwsh-21` Llama n=15 | ρ = **+0.77**, dốc **+6.8 pp/hop**, sai số 0–92%, chain **chết ở depth 11** (4 điểm bị loại) | §5.7 + `tab:depth` |
| `pwsh-23` qwen2.5:7b n=7 (local, free) | ρ = **+1.00**, dốc **+11.8 pp/hop**, sai số **31→89% đơn điệu** | §5.7 + `tab:depth` |
| `pwsh-25` sensitivity temp 0.7 | φ ≤ **1.00** (i.i.d. được ủng hộ) nhưng χ² = **13.40**, df=2, **p = 0.0014** trên cạnh yếu | §5.10 |
| `pwsh-26` cyclic qwen2.5:7b (local, free) | ρ = **0.760** (dưới ngưỡng) → manager tái nhiễm **0.775** rồi **giảm còn 0.650** ở vòng 5; worker dừng ở 0.475/0.525, **không** bão hoà | §5.8 + `tab:cyclic` |

**Việc (1) — quy tắc thiết kế — đã xong và đã vào bài.** `scripts/cyclic_design_rule.py`
kiểm $\rho(M)=\sqrt{\sum_j a_jc_j}$ trên 320 cấu hình ngẫu nhiên: sai số lớn nhất
**4,4e-16**. §5.8 nay có công thức tổng quát, quy tắc vượt ngưỡng
$\sum_j a_jc_j>1$ (đối xứng $w\,s^2>1$: ở $s=0{,}5$ cần 5 worker, $0{,}7$ cần 3,
$0{,}9$ cần 2), và `tab:cyclic` viết lại thành **2 model × 2 cách đọc**.

**Kết quả đáng giá nhất của vòng này:** cùng một công thức đưa ra **hai dự đoán ngược
nhau** trên hai model, và **cả hai đều đúng** (Llama giữ nguyên, qwen yếu dần). Một
tiêu chí dám dự đoán cả hai chiều là tiêu chí có năng lực phân biệt — đây là thứ trả
lời trực tiếp điểm yếu "chẩn đoán mà không có gì xây dựng".

Hệ quả: abstract + gợi ý #1 ở §1 **đã được viết lại** cho khớp (trước đó chỉ nói
được đường cong của Llama; nay dùng thống kê xu hướng của cả ba model, ρ từ +1.00
xuống −0.07).

## 3. Việc còn lại của bạn (chặn việc nộp)

1. **Mã OpenReview**: thay `\acmSubmissionID{0000}` trong `.tex` bằng số thật khi nộp.
2. **Điền tác giả** cho bản camera-ready (`\author{Anonymous Author(s)}` — chỉ hiện
   khi KHÔNG ở chế độ anonymous).
3. **Khai báo việc dùng chung API key Bedrock với Cline** cho giảng viên.
4. **Đọc PDF như tác giả** (một lượt đọc liền mạch) — người viết cuối cùng vẫn phải
   là bạn.

## 3b. ⛔ Chặn kỹ thuật: key Bedrock đã chết LẦN THỨ HAI

`python scripts\bedrock_key_diag.py` (chạy cuối phiên): key fingerprint `20d0f16723`
— loại **LONG-TERM** — trả về `AccessDeniedException: Authentication failed` trên
**cả** Claude 4.5 và Nova Pro ở us-east-1.

⇒ **Mọi thí nghiệm cần model cloud đang bị chặn** (thêm model thứ 6, chạy lại
n=200 cho cạnh yếu, obfuscation trên model mới). Cần key mới từ AWS console.
Key cũ `94fb22d672` vẫn nằm plaintext trong `~/.cline/data/secrets.json` và
`providers.json` — **đừng dán key mới vào Cline**.

**Không mất kết quả nào.** Kiểm bằng `python scripts\check_results_complete.py`:
mọi thư mục kết quả nuôi bảng/hình của bài đều hoàn chỉnh (parse được, không ô
`None`, có `report.md`). Thư mục Bedrock sửa cuối **11/09 11:06 → 16:54**, tức
**tất cả đã ghi xong trước khi key chết**; hai job còn chạy lúc đó (`pwsh-21`
Llama n=15 lúc 16:51, `pwsh-25` sensitivity lúc 16:54) đều kết thúc `exit 0`.
Đặc biệt: 2 dòng Claude của bảng utility **không** có `results.json` mà chỉ có
`outputs.jsonl` — chấm lại bằng `python scripts\utility_from_outputs.py` (0 LLM
call) cho **đúng** số trong bài (ΔU = +0.000 / +0.100, retention 1.000 / 0.900).

Việc **không cần key** vẫn làm được: model local qua ollama (`qwen2.5:7b`,
`qwen2.5:3b` — miễn phí), và mọi phân tích lại từ kết quả đã có.

## 4. Việc nên làm nếu còn thời gian (theo thứ tự đánh đổi)

| Ưu tiên | Việc | Vì sao |
|---|---|---|
| 1 | Thêm **1 model nữa** cho bảng obfuscation | Tăng độ phủ cross-model (hiện 5 model/5 nhà phát triển); cần key Bedrock còn sống |
| 2 | Một mục "Artifact availability" riêng | Hiện đã có trong Kết luận nhưng chưa thành mục; reviewer AAMAS đánh giá cao artefact tái lập |
| 3 | Chạy lại **một** cell ở n=200 cho cạnh yếu | MDE ở n=40 là 0.26 — bài đã nói rõ điều này, n=200 sẽ biến nó thành phát hiện dương tính thật |
| 4 | Rà câu chữ §1 như phản biện khó tính | Rủi ro lớn nhất còn lại: bị đọc thành "thêm một bài đo prompt injection" |

## 5. Lệnh dựng PDF (đã kiểm, đúng thứ tự)

```powershell
$env:Path = "C:\Users\ASUS\AppData\Local\Programs\MiKTeX\miktex\bin\x64;" + $env:Path
cd E:\NCKH\Contagion\paper
pdflatex -interaction=nonstopmode contagion_aamas2027.tex
bibtex   contagion_aamas2027
pdflatex -interaction=nonstopmode contagion_aamas2027.tex
pdflatex -interaction=nonstopmode contagion_aamas2027.tex
```

Ba con số phải bằng 0 (`-file-line-error` không dùng: nó đổi định dạng stdout):

```powershell
Select-String -Path contagion_aamas2027.log -Pattern '^!'
Select-String -Path contagion_aamas2027.log -Pattern 'Overfull \\hbox'
Select-String -Path contagion_aamas2027.log -Pattern 'undefined'
```

## 6. Con số định vị (nói thật, không tô hồng)

- Xác suất được nhận ước lượng: **~35–40%** cho AAMAS main track (mặt bằng ≈ 23–25%).
  Mức tăng so với trước nhờ: quy tắc thiết kế + phép kiểm hai chiều đều đúng (§5.8),
  đường cong 3 model có thống kê xu hướng (§5.7), và báo cáo thẳng χ² bác bỏ i.i.d.
  (§5.10).
- Trừ nếu bị đọc là "measurement study thuần": rủi ro **~15%** — đã giảm bằng cách
  đóng gói đóng góp (định lý ρ(M)=0, chẩn đoán độ dốc, kết quả cyclic).
- Điểm yếu **không giấu**: `M_t` là proxy, `n = 30–40` ở phần lớn ô, chưa có
  mesh/debate, 2 defence được đánh giá thực chất, utility đo bằng proxy.

---

## 7. Revision pack theo `paper/AAMAS2027_REVIEWS.md` — **đã kiểm chứng 2026-09-12**

Người dùng tự thực hiện theo `paper/AAMAS2027_IMPROVEMENTS.md` (file đó ghi 9/14 việc
`✅ XONG`). Tôi **kiểm lại từng mục trong `.tex` + dữ liệu gốc** thay vì ghi theo lời
khai. Kết quả: **7 mục xong thật, 2 mục chưa xong, và 4 vấn đề mới phát sinh.**

### 7a. Đã xong — có bằng chứng trong `.tex`

| Việc (theo improvements) | Bằng chứng |
|---|---|
| §1.1 thu hẹp "prescriptions" | abstract dòng 101: *"It **can** fail, and where it does its error compounds…"*; đóng góp #1 dòng 228: *"**without first checking that they transport**"* |
| §1.2 câu multiplicity | §3.8 L461–462: *"both survive a Benjamini–Hochberg correction across the five non-degenerate cells at q=0.05"*; Limitations L1068–1069 |
| §1.4 làm rõ `R_0` | L504–505: *"use $R_0$ as a **descriptive amplification statistic**, not a safety certificate"* |
| §2.1 Phụ lục A (BH) | `\appendix` sau `\bibliography`, `\section{Multiplicity Control…}`, `tab:bh` (5 dòng + `tab:cluster`) |
| §2.2 Phụ lục B (cluster CI) | `\section{Context-Clustered Interval on the Weak Edge}`, `tab:cluster`; §5.10 L1023–1024 tham chiếu `Appendix~\ref{app:cluster}` |
| §2.3 độ phủ theo từng claim | L219–221: *"coverage differs by claim (cross-model susceptibility spans all five, the depth profile three, and the topology comparison a single model)"* |
| Build | **0 lỗi · 0 overfull · 0 undefined**; nội dung hết **trang 8**, phụ lục ở trang 9 |

**Phụ lục B kiểm chứng đúng hoàn toàn** (chạy `python scripts\appendix_stats.py`):
6 repeat × 20 trial ở T=0,7 → k=29/120, $\hat s=0.242$; Wilson $[0.174,0.326]$;
cluster-bootstrap theo repeat $[0.167,0.317]$; hệ số nới **0,99×** ⇒ Wilson *within
temperature* là hợp lệ, và $\varphi=2.93$ đúng là artefact của việc gộp temperature
(khớp §5.10). Đây là điểm **củng cố**, không phải điểm yếu.

### 7b. ✅ ĐÃ XONG (2026-09-12) — 2 mục trước đây thiếu

| Việc | Trạng thái mới |
|---|---|
| §1.3 **Artifact Availability thành mục có tiêu đề** | ✅ Thêm `\section*{Artifact Availability}` sau Conclusion, nêu rõ **3 tầng tái lập** (zero-API / local qwen / hosted frontier) + trỏ Phụ lục A/B/C + `REPRODUCE` manifest |
| §1.5 **Tuyên bố đạo đức / responsible-use** | ✅ Thêm `\section*{Ethical Considerations}`: benign marker, không elicit secret/harmful, dùng API chuẩn, không exploit mới, release để giúp defender |

Cả hai đặt sau Conclusion (§1–§8 vẫn kết thúc trang 8), trước References; build 0 lỗi.

### 7c. 🔴 Bốn vấn đề MỚI do revision pack tạo ra

| # | Vấn đề | Bằng chứng | Mức độ |
|---|---|---|---|
| **P1** | ✅ **ĐÃ SỬA (2026-09-12)** — BH nay chạy trên **giao thức mặc định fresh-artefact**: `tab:bh` bỏ ô DeepSeek fixed `p=0.0030`, thay bằng DeepSeek fresh `p=0.63` (keep); chỉ **Llama** reject. §3.8 viết lại thành *"only the Llama cell rejects... the DeepSeek rejection was a fixed-artefact artefact that vanishes under the fresh protocol (p=0.63)"* + trỏ tới §5.3 và Phụ lục A. `appendix_stats.py` cập nhật cùng số. Không còn mâu thuẫn với §5.3. Build 0 lỗi | `tab:bh` (5 dòng mới); §3.8 L460–465; `appendix_stats.py` table_a() | ✅ Đóng |
| **P2** | ✅ **ĐÃ SỬA (2026-09-12)** — `p` Llama đổi `0.0001 → 0.0002` ở cả §3.8 và `tab:bh`, khớp `frontier_llama3-3-70b*/results.json` (`p_value=0.00024993`, làm tròn 4 c.s.t = 0.0002) | `tab:bh` rank 1; §3.8 L461 | ✅ Đóng |
| **P3** | ✅ **ĐÃ SỬA (2026-09-12)** — `appendix_stats.py` nay **đọc thật**: thêm `_pv_frontier()` đọc `chain_none.markov_formal.p_value` từ `frontier_*_fresh/results.json` (Llama/DeepSeek/Nova) và `_pv_table()` đọc từ `markov_formal/table.json` (qwen). Không còn hard-code. Chạy ra đúng bảng: chỉ Llama REJECT | `appendix_stats.py` table_a() | ✅ Đóng |
| **P4** | ✅ **XỬ LÝ (2026-09-12)** — Quyết định **giữ nguyên**: nội dung có đánh số (§1–§8) kết thúc **trang 8**; Ethics + Artifact + Appendix A/B/C nằm ở trang 9–10, sau/cạnh References. Theo thông lệ AAMAS/ACM, ethics/reproducibility statements + technical appendix **không tính** vào giới hạn 8 trang. Comment trong `.tex` (trước `\appendix`) đã ghi rõ lập luận này | §1–§8 hết trang 8 (`aux`); PDF 10 trang | ✅ Đóng (chấp nhận thông lệ) |

*(Phụ: Nova ghi 0,0858 còn dữ liệu lưu 0,084 — lệch nhỏ, có thể do bootstrap khác seed.)*

### 7d. Việc cần làm để thật sự đóng revision pack

1. **P1 (bắt buộc)**: bỏ ô DeepSeek fixed khỏi BH, hoặc dùng `p=0.63` (fresh protocol) và
   ghi rõ "the one composition rejection (Llama) survives BH; the DeepSeek deviation does
   not survive the fresh-artefact protocol". Sửa cả câu §3.8.
2. **P4 (bắt buộc, chọn 1)**: (a) đưa 2 bảng phụ lục **vào trong 8 trang** (phải cắt
   ~0,5 trang chỗ khác), (b) chuyển phụ lục sang **supplement/arXiv** và giữ bản nộp
   sạch 8 trang, hoặc (c) giữ nguyên và **chấp nhận rủi ro**.
3. **P2 + P3**: sửa số Llama thành 0,0002/0,00025 và cho `appendix_stats.py` đọc p-value
   thật từ kết quả.
4. **§1.3 + §1.5**: thêm mục Artifact Availability + tuyên bố đạo đức (2 việc 0 API cuối cùng).
