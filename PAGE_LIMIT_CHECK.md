# Kiểm tra tuân thủ giới hạn trang — AAMAS 2027 Main Track

> Kiểm ngày rebuild sạch cuối cùng. Mọi số bên dưới đo trực tiếp từ PDF/log, không suy đoán.
> Lệnh dựng: `pdflatex → bibtex → pdflatex → pdflatex` trong `paper/`.

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
| Số mục tham khảo | **27** | `contagion_aamas2027.bbl` → 27 `\bibitem` |
| Preprint trong danh mục | **0** | `refs.bib` không còn `@misc` |
| Sửa style/layout | **Không** | xem mục "Layout" bên dưới |

## Bố cục thực tế theo trang (PDF đầy đủ, 9 trang)
- **Trang 1–8:** toàn bộ phần thân §1–§8, 8 bảng, 2 hình, kết thúc bằng
  **Ethical Considerations** và **Artifact Availability**.
- **Trang 9:** **References** (27 mục) — bắt đầu từ **đầu trang 9**, tràn hết trang 9.

⇒ Không còn văn bản nội dung nào nằm sau trang 8. Đây là trạng thái an toàn nhất:
diễn giải "8 trang không tính references" được thoả mãn dù AC có tính hay không tính
các mục *Ethical Considerations* / *Artifact Availability*.

## ⚠️ Lưu ý về `check_pages.py` (đã xác minh là chỉ số SAI)
`_bodyonly.pdf` **không còn là tiêu chí đáng tin**. Script cắt trước `\bibliography`, nên
tài liệu kết thúc ở đó và LaTeX **cân bằng 2 cột cuối cùng** (balanced last page) → nhồi
được nhiều văn bản hơn. Bản đầy đủ không có bước cân bằng đó (references đứng sau), nên
`_bodyonly.pdf` có thể báo **8 trang** trong khi bài thật vẫn tràn sang trang 9.

Đã quan sát đúng hiện tượng này: `_bodyonly.pdf` = 8 trang nhưng `contagion_aamas2027.pdf`
vẫn đẩy *Artifact Availability* xuống trang 9.

**⇒ Tiêu chí đúng: build đầy đủ (`pdflatex → bibtex → pdflatex ×2`) rồi kiểm tra trang
đầu tiên có mục `References` nằm ở đâu.** Đây là cách đã dùng để chốt 8 trang.

## Layout — ĐẠT (không vi phạm "không sửa style / không tiểu xảo")
Đã rà toàn bộ `.tex`; chỉ dùng lệnh **hợp lệ, chuẩn ACM**, không đụng lề/khổ chữ/giãn dòng:
- `\emergencystretch=2.5em` — chỉ nới dung sai justification, **không** đổi lề/font/cỡ chữ/giãn dòng (đúng như chú thích của tác giả). Hợp lệ.
- `\small` trên bảng/hình và trong `quote` mẫu payload — thông lệ ACM bình thường.
- `\setlength{\tabcolsep}{4pt}` **chỉ trong đúng một bảng** (ablation) — chỉnh cột cục bộ, hợp lệ.
- `\vspace{5pt}` nằm **trong khối copyright bắt buộc** của template, không phải để nhồi trang.
- **KHÔNG** có: `\textheight/\textwidth/\topmargin/\columnsep`, `\linespread`, `\baselineskip`,
  `\fontsize`, `\enlargethispage`, hay chỉnh `\parskip/\parindent`. ⇒ Không có tiểu xảo dàn trang.

## Cách đã rút gọn để vừa 8 trang (cắt chữ thật, không tiểu xảo)
Không đổi bố cục, chỉ nén văn bản và gộp chi tiết hỗ trợ:
1. **Caption bảng/hình:** rút từ ~399 còn ~250 từ; chi tiết replicate/sampling chuyển sang
   supplementary (App. B).
2. **Gộp đoạn lặp:** kết quả chi tiết validator (φ, χ², Nova floor) gộp còn một đoạn;
   số liệu percolation trên isolated rates chuyển sang App. B.
3. **Cắt diễn giải trùng:** các đoạn "reading/interpretation" lặp lại kết luận đã nêu ở
   Introduction và §6 Discussion.
4. **Rút gọn Setup/Framework:** mô tả protocol, cảnh báo tương quan, calibration MR.
5. **Giữ nguyên chiều sâu:** abstract (210 từ), §6 Discussion (323 từ), §7 Limitations
   (286 từ), §8 Conclusion (293 từ) — các mục này **không** bị cắt xuống mức quá ngắn.

## Việc khác đã tiện kiểm
- **PDF từng bị lệch 1 pass:** bản cũ hiện `??` và `[? ]` khi trích văn bản. Sau khi dựng
  sạch 3 pass: **0 undefined**. Luôn dựng đủ pass trước khi nộp.
- **Double-blind:** không có tên/affiliation/email thật; `\email{anonymous@example.org}` là
  placeholder chính thức của template; `acks` rỗng; PDF metadata không có trường Author;
  `supplementary.tex` dùng `Anonymous Author(s)` và `\date{}`.
- **Supplementary:** 3 trang, build sạch, 0 lỗi; đã sửa tiêu đề (khớp "Does (and Does Not)
  Compose") và các tham chiếu "Section ~x of the main paper" bị cũ (3.8→3.7 cho phép
  bootstrap; "Section 5"→5.10 cho homogeneity/φ; φ trong §4).

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
   - `supplementary.zip` = **0.16 MB** — `supplementary.pdf`, `supplementary.tex`,
     `supplementary_README.txt`.
   - `paper-contagion.zip` = **1.90 MB** — PDF chính + PDF bổ sung + `submission/main/`
     (tex, bib, bbl, cls, bst, `by.pdf`, 2 hình) + `submission/supplementary/`.
   - Cả hai đã **dựng lại từ file hiện hành** (bản cũ trong zip bị cũ và thiếu README).
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