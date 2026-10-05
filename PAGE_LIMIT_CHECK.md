# Kiểm tra tuân thủ giới hạn trang — AAMAS 2027 Main Track

> Kiểm ngày rebuild sạch cuối cùng. Mọi số bên dưới đo trực tiếp từ PDF/log, không suy đoán.
> Lệnh dựng: `latexmk -g -pdf -interaction=nonstopmode contagion_aamas2027.tex` trong `paper/`.
>
> **Nguồn chân lý duy nhất: `paper/contagion_aamas2027.tex` + `paper/refs.bib`.**
> Thư mục `paper/submission/` đã bị xóa (2026-10-05) vì là bản cũ lệch với bản nộp:
> nó thiếu `\ccsdesc` và thiếu mục "Protocol sensitivity". Đừng tạo lại.

## Quy định (trích Call for Main Track)
- Nội dung **tối đa 8 trang**; trang chứa **tài liệu tham khảo** thì **không giới hạn** (thêm trang).
- **Không** dùng "typesetting tricks" để nhồi vừa 8 trang.
- **Không** sửa file style hay bất kỳ tham số layout nào. **Bắt buộc dùng LaTeX.**

## Kết quả đo (build sạch) — ✅ ĐẠT
| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Tổng số trang PDF đầy đủ | **9 trang** | `pdfinfo contagion_aamas2027.pdf` → `Pages: 9` |
| **Số trang nội dung chính (§1–§8 + Ethical + Artifact)** | **8 trang (trang 1–8)** | References bắt đầu ở **đầu trang 9** |
| Overfull `\hbox` | **0** | `contagion_aamas2027.log` |
| Undefined references / citations | **0** | `contagion_aamas2027.log` |
| LaTeX errors | **0** | `contagion_aamas2027.log` |
| CCS concepts | **có** (bắt buộc) | 0 warning; `pdfinfo → Subject:` đã điền |
| Bookmark warnings (hyperref) | **0** | `contagion_aamas2027.log` |
| **Số mục tham khảo** | **39** | `contagion_aamas2027.bbl` → 39 `\bibitem` |
| Preprint (`@misc`) trong danh mục | **0** | Cả 39 entry đều là bản proceedings đã xác minh |
| Sửa style/layout | **Không** | xem mục "Layout" bên dưới |

## Bố cục thực tế theo trang (PDF đầy đủ, 9 trang)
- **Trang 1–8:** toàn bộ phần thân §1–§8, 7 bảng, 2 hình, kết thúc bằng
  **Conclusion**, **Ethical Considerations** và **Artifact Availability**.
- **Trang 9:** **References** (39 mục), bắt đầu từ **đầu trang 9**.

⇒ Không có văn bản nội dung nào nằm sau trang 8. Đây là trạng thái an toàn nhất:
diễn giải "8 trang không tính references" được thoả mãy dù AC có tính hay không tính
các mục *Ethical Considerations* / *Artifact Availability*.

## ⚠️ Bài học từ đợt 2026-10-05 (đừng lặp lại)

### 1. Hai bản paper đã tồn tại song song — đã xóa bản cũ
`paper/contagion_aamas2027.tex` (bản nộp, **có** `\ccsdesc`) và
`paper/submission/main/contagion_aamas2027.tex` (bản cũ) đã lệch nhau:
bản cũ **thiếu** 3 khái niệm CCS và **thiếu** mục "Protocol sensitivity".
Cả hai đều biên dịch được và đều đạt 9 trang, nên chỉ nhìn PDF sẽ không thấy —
phải kiểm `\ccsdesc` và `pdfinfo → Subject:`.

⇒ Dấu hiệu nhận biết: `aamas.cls:1924` phát
`Class aamas Warning: CCS concepts are mandatory for papers over two pages.`
Khi thấy dòng này là thiếu CCS, **không phải** bản nộp được.

### 2. Hai bản `refs.bib` dùng tên key khác nhau
Bản cũ dùng `Hong2024MetaGPT` / `Kempe2003InfluenceMaximization`; bản nộp dùng
`Hong2023MetaGPT` / `Kempe2003`. Khi chuyển entry phải theo tên key của
`paper/refs.bib`, không copy thẳng từ bản cũ.

### 3. Trang 8 vốn đã **đầy** — thêm citation phải bù bằng cách nén chữ
`paper/contagion_aamas2027.tex` trước đợt này đã dùng 113/113 dòng ở trang 8.
Thêm 12 ref tốn ~7 dòng, phải nén §2 (bỏ câu dẫn lặp, rút những vế không mang
thông tin mới) để lấy lại đúng số dòng đó. Cách dùng: **gắn citation vào câu
có sẵn** thay vì viết câu mới — ví dụ thêm `Chen2024AgentVerse` vào câu kể
MetaGPT/AutoGen, thêm `Hines2024CAMLIS`+`Debenedetti2026CaMeL` vào câu về
structured queries. Như vậy phần lớn ref mới gần như **không tốn dòng nào**.

## ⚠️ Hai việc format đã sửa ở đợt trước (và vì sao tốn dòng)

### 1. CCS concepts — BẮT BUỘC, trước đây thiếu
`aamas.cls` cảnh báo lúc cuối tài liệu:
`Class aamas Warning: CCS concepts are mandatory for papers over two pages.`
Đã thêm đúng cú pháp của class (`\ccsdesc[100]{General~Concept}`), 3 khái niệm:
- Computing methodologies → Multiagent systems
- Computing methodologies → Natural language processing
- Security and privacy → Social engineering

Khối này hiện trong title block (giữa Abstract và Keywords) và **tốn ~3 dòng**.
Nó cũng lấp đầy `pdfinfo → Subject:` (trước đây rỗng).

### 2. Bookmark PDF string — 3 warning đã xoá
`hyperref` báo `Token not allowed in a PDF string: removing math shift / subscript`
vì tiêu đề §3.8 chứa `$R_0$`. Đã bọc bằng
`\texorpdfstring{$R_0$}{R0}`. Không còn warning nào.

### Cách bù lại số dòng (không dùng tiểu xảo)
Chỉ **cắt chữ trùng lặp**, không đổi bố cục:
1. Gộp đoạn vỡ ở cuối §5.8 (một mảnh câu bị mất chủ ngữ) vào đoạn trước, bỏ lặp
   "every hop re-packages the payload".
2. Bỏ câu caveat ở cuối §5.6 đã trùng với §7 Limitations.
3. Viết lại câu ở §3.1 (bản gốc dính câu, "…is therefore framed as benign-looking
   infrastructure text, the difference between 0% and 60–100% compliance").

⇒ Trang 8 vẫn **đầy** (deepest text `yMax = 699.5`, đáy khung chữ `710.5`), References
vẫn bắt đầu ở đầu trang 9. Không có dòng nào bị đẩy sang trang 9.

## Layout — ĐẠT (không vi phạm "không sửa style / không tiểu xảo")
Đã rà toàn bộ `.tex`; chỉ dùng lệnh **hợp lệ, chuẩn ACM**, không đụng lề/khổ chữ/giãn dòng:
- `\emergencystretch=2.5em` — chỉ nới dung sai justification, **không** đổi lề/font/cỡ chữ/giãn dòng (đúng như chú thích của tác giả). Hợp lệ.
- `\small` trên bảng/hình và trong `quote` mẫu payload — thông lệ ACM bình thường.
- `\setlength{\tabcolsep}{4pt}` **chỉ trong đúng một bảng** (ablation) — chỉnh cột cục bộ, hợp lệ.
- `\vspace{5pt}` nằm **trong khối copyright bắt buộc** của template, không phải để nhồi trang.
- **KHÔNG** có: `\textheight/\textwidth/\topmargin/\columnsep`, `\linespread`, `\baselineskip`,
  `\fontsize`, `\enlargethispage`, hay chỉnh `\parskip/\parindent`. ⇒ Không có tiểu xảo dàn trang.

## Chi tiết nguồn `.tex` đã làm sạch (đều ảnh hưởng phần hiển thị)
| Vấn đề | Cách sửa |
|---|---|
| `\usepackage{balance}` trùng với class | Bỏ — `aamas.cls` tự `\RequirePackage{balance}` và gọi `\balance` |
| `\pending` định nghĩa nhưng không dùng | Bỏ khỏi preamble |
| Comment "CUT-CANDIDATE" không còn marker nào | Thay bằng mô tả trạng thái thật + trỏ `PAGE_LIMIT_CHECK.md` |
| `\scite{}` / `\snat{}` in ra subscript rỗng (7 chỗ) | Thêm `\scites` / `\snats` cho dạng không chỉ số hop |
| Caption bảng tự tham chiếu chính nó | `tab:utility`: bỏ `(Section 5.9)` |
| `\small` lặp 2 lần trong `tab:ablation` | Bỏ bản thừa |
| `n=7` … ở **text mode** (thiếu khoảng trắng toán) | Bọc `$n = 7$` trong `tab:depth`; đồng bộ mọi `$n = \cdot$` |
| `\prod_i \hat s_i` ở §5.3 lệch ký hiệu §5.2 | Đổi thành `\prod_i \scite{i}` |
| "We differ from **all four**" nhưng liệt kê 5 công trình | Đổi thành "all of these" |
| Tense lệch: "Section 3.8 **proved**" (mục lý thuyết) | Đổi thành "shows" |
| Caption thiếu sample size | Thêm `40 natural runs, 30 controlled trials` vào `tab:cross`, `tab:transport`, `tab:ablation` |
| `\label{fig:obf}` dính chữ vào caption | Tách xuống dòng riêng |
| File bị ghi kèm **UTF-8 BOM** khi chỉnh bằng PowerShell | Đã gỡ BOM (file giờ bắt đầu bằng `%%%`) |

## Hai mâu thuẫn nội bộ đã sửa ( reviewer sẽ bắt ngay )
1. **`$\dagger$` mang hai nghĩa.** §4 ghi "`$\dagger$` = cần Bedrock inference-profile",
   còn caption `tab:cross` ghi "`$\dagger$` = dùng fresh-artefact protocol". Giữ nghĩa thứ hai
   (vì §5.3–§5.4 dựa vào nó) và sửa §4 thành: "the Llama and Claude endpoints require
   Bedrock inference-profile identifiers".
2. **"the most capable model we test is the most susceptible"** — mâu thuẫn với chính
   `tab:cross` (Claude ASR 0.000, Nova 0.075 ở hai cuối; Llama 70B 0.850 ở đầu). Đổi thành
   claim đúng với bảng: hai model frontier thương mại nằm cuối bảng, model 70B mở nằm đầu.

## ⚠️ Lưu ý về `check_pages.py` (đã xác minh là chỉ số SAI)
`_bodyonly.pdf` **không còn là tiêu chí đáng tin**. Script cắt trước `\bibliography`, nên
tài liệu kết thúc ở đó và LaTeX **cân bằng 2 cột cuối cùng** (balanced last page) → nhồi
được nhiều văn bản hơn. Bản đầy đủ không có bước cân bằng đó (references đứng sau), nên
`_bodyonly.pdf` có thể báo **8 trang** trong khi bài thật vẫn tràn sang trang 9.

Đã quan sát đúng hiện tượng này: `_bodyonly.pdf` = 8 trang nhưng `contagion_aamas2027.pdf`
vẫn đẩy *Artifact Availability* xuống trang 9.

**⇒ Tiêu chí đúng: build đầy đủ (`pdflatex → bibtex → pdflatex ×3`) rồi kiểm tra trang
đầu tiên có mục `References` nằm ở đâu.** Đây là cách đã dùng để chốt 8 trang.

## Việc khác đã tiện kiểm
- **PDF từng bị lệch 1 pass:** bản cũ hiện `??` và `[? ]` khi trích văn bản. Sau khi dựng
  sạch 4 pass: **0 undefined**. Luôn dựng đủ pass trước khi nộp.
- **Double-blind:** không có tên/affiliation/email thật; `\email{anonymous@example.org}` là
  placeholder chính thức của template; `acks` rỗng; **PDF metadata ở cấp document không có
  trường Author** (`pdfinfo` → chỉ có `Title`, `Subject` = CCS, `Creator`, `Producer`).
- **Supplementary:** 3 trang, build sạch, 0 lỗi; đã sửa tiêu đề (khớp "Does (and Does Not)
  Compose") và các tham chiếu "Section ~x of the main paper" bị cũ.
- **Tham chiếu Appendix trong bài chính:** đồng bộ thành "supplementary Appendix~A/B/C/D".

## Trạng thái cuối — ✅ tất cả đã xong
1. **Metadata đã kiểm chứng:**
   - `Lee2025Infection` — đối chiếu DOI `10.1007/978-3-032-16092-8_28`: Springer ghi
     **(2026)**, ESORICS 2025 International Workshops, LNCS, pp. 511–520, Springer.
     Bib (year=2026, pages, series, publisher, DOI) **khớp hoàn toàn**. Khóa tên
     `Lee2025Infection` chỉ là nội bộ, không xuất hiện trong bản in.
   - `Wu2024AutoGen` — venue/year (COLM 2024) xác nhận qua trang publication của
     Microsoft Research. **URL OpenReview `vYQxJ6kP89` không xác minh được**
     (OpenReview chặn bot, DBLP bị Anubis chặn, Crossref không có COLM) và **đã gỡ khỏi
     `refs.bib`** vì URL đó in ra trong danh mục. Ba URL OpenReview còn lại
     (MetaGPT/ICLR'24, ReAct/ICLR'24, ASB/ICLR'25) là hợp lệ.
2. **Kích thước gói nộp (≤ 25 MB):**
   - `supplementary.zip` = **0,16 MB** — `supplementary.pdf` (3 trang, build lại
     2026-10-05), `supplementary.tex`, `supplementary_README.txt`.
   - `paper-contagion.zip` **đã xóa** (2026-10-05): nó là bundle thừa, chứa bản
     `.tex`/`.pdf` cũ ở `paper/submission/`. Không nộp file này.
   - Không còn thư mục `paper/submission/`.
3. **Appendix trong file chính:** không còn (Appendices A–D nằm ở `supplementary.tex`) ⇒
   rủi ro "appendix sau references có được miễn không" **đã gỡ hoàn toàn**.

## 🔒 Sửa lỗi rò rỉ danh tính trong PDF (double-blind)
`by.pdf` (artwork CC-BY đi kèm template ACM) **chứa `/Author (Alex Roberts)`** trong
cả XMP stream lẫn Info dictionary ⇒ tên người nằm trong byte thô của
`contagion_aamas2027.pdf`. Đây là asset của ACM chứ không phải tên tác giả bài nộp,
nhưng vẫn là rủi ro mất ẩn danh nên **đã gỡ**:
- Thay chuỗi bằng chuỗi **cùng độ dài** (`CC-BY badge;`) để **không phá xref table**.
- Kiểm tra lại: `Alex Roberts` còn **0** lần trong PDF; `/Author` nay là `CC-BY badge;`.
- Hai hình PNG chỉ mang metadata `Matplotlib 3.11.1`, không có dấu vết nhận dạng.

## Kết quả `scripts/_anon_check.py` (chạy lại sau khi sửa)
- `contagion_aamas2027.pdf`: chuỗi đáng ngờ **KHÔNG có**; `/Author` = `CC-BY badge;`.
- `supplementary.pdf`: `/Author` **rỗng**.
- `supplementary.zip`: 3 file, README **0 dòng** chứa đường dẫn/email.
- `contagion_aamas2027.tex` / `supplementary.tex`: **0 dòng** chứa chuỗi định danh.

> Lưu ý khi đọc output của script: nó quét **Info dictionary đầu tiên** tìm thấy, thuộc
> ảnh `by.pdf` nhúng vào (`/Title (by.eps)`, `/Creator Adobe Illustrator(R)`). Metadata
> **cấp document** mà trình đọc PDF hiển thị là dict của trailer — đó mới là cái cần kiểm,
> và nó sạch (xem mục Double-blind ở trên).