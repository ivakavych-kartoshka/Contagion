# Kiểm tra tuân thủ giới hạn trang — AAMAS 2027 Main Track

> Kiểm ngày rebuild sạch cuối cùng. Mọi số bên dưới đo trực tiếp từ PDF/log, không suy đoán.
> Lệnh dựng: `pdflatex → bibtex → pdflatex → pdflatex` trong `paper/`.

## Quy định (trích Call for Main Track)
- Nội dung **tối đa 8 trang**; trang chứa **tài liệu tham khảo** thì **không giới hạn** (thêm trang).
- **Không** dùng "typesetting tricks" để nhồi vừa 8 trang.
- **Không** sửa file style hay bất kỳ tham số layout nào. **Bắt buộc dùng LaTeX.**

## Kết quả đo (build sạch)
| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Tổng số trang PDF đầy đủ | **10 trang** | `pdfinfo contagion_aamas2027.pdf` → `Pages: 10` |
| Số trang phần thân (cắt trước `\bibliography`) | **9 trang** | `check_pages.py` → `_bodyonly.pdf (9 pages)` |
| Overfull `\hbox` | **0** | `contagion_aamas2027.log` |
| Undefined references / citations | **0** | log: "NO undefined"; PDF hiện ra "Appendix A/B/C" đúng |
| Sửa style/layout | **Không** | xem mục "Layout" bên dưới |

## Bố cục thực tế theo trang (PDF đầy đủ, 10 trang)
- **Trang 1–8:** phần thân đánh số §1–§7 và bảng/hình (đến hết §5.10, §6 Discussion, §7 Limitations bắt đầu ở cuối trang 8).
- **Trang 9:** phần còn lại của §7, **§8 Conclusion**, rồi hai mục sao **Ethical Considerations** và **Artifact Availability**, và bắt đầu **References**.
- **Trang 10:** tiếp References + **Appendix A/B/C** (`tab:bh`, `tab:cluster`, `tab:tau`).

## ⚠️ Rủi ro chính: nội dung tràn sang trang 9
Đây là điểm **cần xử lý trước khi nộp**:

1. **Phần thân (không tính references) hiện là 9 trang, không phải 8.** `check_pages.py`
   cắt ngay trước `\bibliography` và vẫn ra **9 trang**. Nghĩa là §1–§8 **cộng** hai mục
   *Ethical Considerations* + *Artifact Availability* tràn xuống **đầu trang 9**.
2. **Ai bị tính vào "8 trang"?** CFP chỉ miễn trừ *bibliographic references*.
   - **Chắc chắn KHÔNG bị tính:** References (trang 9–10).
   - **RỦI RO bị tính là nội dung:** *Ethical Considerations* và *Artifact Availability*
     là mục **sao (không đánh số) nhưng vẫn là văn bản nội dung**, đặt **trước** References.
     Nhiều AC coi đây là nội dung ⇒ bài đang **9 trang nội dung > giới hạn 8**.
   - **Phụ thuộc luật ACM/AAMAS 2027:** Appendix A/B/C (trang 10) nằm **sau** References.
     Một số năm AAMAS/ACM cho phép appendix kỹ thuật sau references không tính vào 8 trang;
     cần xác nhận lại đúng bản CFP 2027. **Đừng cho là mặc định được miễn.**

### Kết luận rủi ro
- Nếu AC tính *Ethical Considerations* + *Artifact Availability* vào nội dung ⇒ **VƯỢT 8 trang** (đang ~9).
- Cần một trong các cách xử lý dưới đây để phần nội dung kết thúc **trong trang 8**.

## Cách khắc phục (không dùng tiểu xảo, không sửa style)
Theo thứ tự ưu tiên — mục tiêu: đẩy phần thân về đúng 8 trang.
1. **Nén nội dung có thật:** rút gọn §7 Limitations và §6 Discussion (cắt câu lặp),
   gộp caveat cyclic. Đây là cắt chữ thật, hợp lệ.
2. **Rút gọn hai mục sao:** *Ethical Considerations* và *Artifact Availability* có thể
   nén còn 3–4 dòng mỗi mục, hoặc gộp Artifact Availability vào Conclusion (đã từng ở đó).
3. **Xác minh luật appendix của CFP 2027** (mục *Submission Instructions*): nếu appendix
   sau references **không** được miễn, phải chuyển Appendix A–C thành tài liệu bổ sung
   (supplementary) chứ không để trong file chính.
4. Sau mỗi lần sửa, chạy lại `python check_pages.py` cho tới khi **`_bodyonly.pdf` = 8 trang**.

## Layout — ĐẠT (không vi phạm "không sửa style / không tiểu xảo")
Đã rà toàn bộ `.tex`; chỉ dùng lệnh **hợp lệ, chuẩn ACM**, không đụng lề/khổ chữ/giãn dòng:
- `\emergencystretch=2.5em` — chỉ nới dung sai justification, **không** đổi lề/font/cỡ chữ/giãn dòng (đúng như chú thích của tác giả). Hợp lệ.
- `\small` trên bảng/hình và trong `quote` mẫu payload — thông lệ ACM bình thường.
- `\setlength{\tabcolsep}{4pt}` **chỉ trong đúng một bảng** (ablation) — chỉnh cột cục bộ, hợp lệ.
- `\vspace{5pt}` nằm **trong khối copyright bắt buộc** của template, không phải để nhồi trang.
- **KHÔNG** có: `\textheight/\textwidth/\topmargin/\columnsep`, `\linespread`, `\baselineskip`,
  `\fontsize`, `\enlargethispage`, hay chỉnh `\parskip/\parindent`. ⇒ Không có tiểu xảo dàn trang.

## Việc khác đã tiện kiểm
- **PDF trên đĩa từng bị lệch 1 pass:** bản cũ hiện `??` và `[? ]` khi trích văn bản.
  Sau khi **dựng lại sạch** (`pdflatex×1 → bibtex → pdflatex×2`): **0 undefined**, các tham chiếu
  ra đúng "Appendix A/B/C" và citation `StrUQ2025` hiển thị đúng. ⇒ Luôn dựng đủ 3 pass trước khi nộp.
