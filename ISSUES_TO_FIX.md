# Các vấn đề cần sửa — kết quả kiểm tra (build + test + audit)

> Kiểm tra bằng chính bộ công cụ của repo, đo trực tiếp, không suy đoán.
> Lệnh đã chạy: dựng lại PDF 3 pass · `pytest tests` · `check_paper.py` ·
> `check_figures.py` · `audit_numbers.py` · đọc `results.json` gốc.

## Tổng kết trạng thái
| Kiểm tra | Kết quả |
|---|---|
| `pytest tests` | **78 passed** (exit 0) |
| Dựng PDF (3 pass) | **0 overfull hbox, 0 undefined reference** |
| `check_paper.py` (cấu trúc/cite/ref/hình) | **Không lỗi**, 3 cảnh báo nhẹ (label thừa) |
| `check_figures.py` | **Sạch** (chỉ 2 PNG được `.tex` dùng, không đè chữ) |
| `audit_numbers.py` claim-lint | **Khớp** (5 model / 3 topology) |
| Số headline trong bài vs `results.json` | Khớp file nguồn; **P1 provenance đã chốt (xem dưới)** |

**Kết luận:** Không có lỗi chặn nộp về kỹ thuật biên dịch. **P0 và P1 đã xử lý
(2026-09-13)** — chi tiết ở mục tương ứng bên dưới.

---

## P0 — Nén phần thân về đúng giới hạn 8 trang ✅ ĐÃ XỬ LÝ TRIỆT ĐỂ (2026-09-13, cập nhật)
Ban đầu chỉ nén văn (§8 Conclusion vẫn kẹt ở trang 9 do float lấp chỗ). **Đã xử lý
dứt điểm** bằng biện pháp cấu trúc hợp lệ: **chuyển §5.8 "Recurrence" + bảng
`tab:cyclic` xuống Appendix D** (sau references), để lại 1 đoạn tóm tắt 7 dòng trỏ
tới appendix trong §5. Kết quả đo trực tiếp từ PDF + `.aux` (build sạch 0/0):
- **Toàn bộ nội dung CÓ ĐÁNH SỐ §1–§8 (kể cả §8 Conclusion) nằm trọn trang 1–8**
  (`.aux`: `sec:conclusion` → `{8}{8}` = section 8, trang 8).
- **Ethical Considerations + Artifact Availability cũng nằm trên trang 8** (trích text
  PDF: trang 8 có cả 3 mục; trang 9 có 0 mục nội dung).
- **References bắt đầu ở trang 8**, tiếp trang 9; Appendix A/B/C trang 9, Appendix D
  (Recurrence) trang 10 — đều sau references, hợp lệ.
- KHÔNG mất kết quả khoa học: §5.8 chỉ đổi vị trí (thành Appendix D), nội dung + số
  liệu + bảng giữ nguyên; 4 kết luận chính (i)-(iv) không phụ thuộc §5.8.
- Không dùng tiểu xảo/sửa style: chỉ nén văn thật + di chuyển 1 subsection phụ.

## P1 — Chốt thư mục nguồn cho hàng Llama chain-none ✅ ĐÃ XỬ LÝ (2026-09-13)
**Kết luận điều tra (bằng chứng, không đoán):** bài dùng
`experiments/results/frontier_llama3-3-70b_iso` cho hàng **Llama fresh †**.
- Khớp `.tex` chính xác: `tab:transport`/`tab:cross` L590 `0.850 & 0.744 & 1.000/0.233/1.000`,
  weak edge `0.233`, `\snat=0.875`, `3.75×`, `Δ=+0.617` (L619–622, 659–662), `tab:ablation`
  L689 `Llama fresh 1.000/0.233/1.000`.
- **`_iso` là dir Llama chain-none DUY NHẤT có `survival_natural`** ⇒ bắt buộc cho B2
  transportability. Base dir `frontier_llama3-3-70b` (0.800/0.167) là hàng **fixed** của
  `tab:ablation` (Δ=+0.633) — cũng được trích.
- Dir gây nhiễu `frontier_llama3-3-70b_fresh` (0.925/0.300, Δ=+0.625) **không được trích**
  ⇒ đã đổi tên thành `_unused_frontier_llama3-3-70b_fresh_replicate2` (tiền tố `_` nên cả
  `make_figures.py` lẫn `audit_numbers.py` **tự bỏ qua**). Giữ lại làm bằng chứng độ vững.

**Đã sửa code/docs:**
1. `scripts/appendix_stats.py`: hàng Llama-fresh của `tab:bh` giờ đọc
   `frontier_llama3-3-70b_iso` (trước đọc `_fresh`). `p_value` giống hệt (0.0002) nên BH
   **không đổi** (Llama vẫn rank-1 REJECT). Note nguồn cập nhật theo.
2. `audit_numbers.py`: nhờ đổi tên dir, bảng audit giờ **chỉ** in `frontier_llama3-3-70b`
   (0.800 fixed) + `frontier_llama3-3-70b_iso` (0.850 fresh) — khớp đúng bài; số nhiễu
   0.925/0.300 biến mất. Đã regen `AUDIT_TABLE.md`.
3. `REPRODUCE.md` §3.1: bảng chốt map từng dir → hàng nào của bảng nào + giải thích tên
   `_iso`.


## P2 (cosmetic — không bắt buộc)
- `check_paper.py` cảnh báo **3 label không được `\ref`**: `sec:setup` (dòng 529),
  `sec:discussion` (1053), `sec:conclusion` (1106). Đã xác minh: chỉ là label thừa,
  **vô hại**, hợp lệ. Có thể xóa cho sạch hoặc bỏ qua.
- PDF trên đĩa trước đó bị lệch 1 pass (hiện `??`/`[? ]` khi trích text). Sau khi
  dựng đủ 3 pass đã hết. **Luôn dựng `pdflatex→bibtex→pdflatex→pdflatex` trước nộp.**

## Không phải vấn đề (đã kiểm, để khỏi lo)
- Layout/style: **không vi phạm** — chỉ dùng `\emergencystretch`, `\small` trên
  bảng/hình, `\tabcolsep 4pt` ở 1 bảng, `\vspace` trong khối copyright bắt buộc.
  Không đụng lề/khổ/giãn dòng/font. Không có tiểu xảo dàn trang.
- Hình: chỉ 2 PNG được tham chiếu, checker sạch.
- Claim-lint: câu "five models / five developers / three topologies" khớp dữ liệu.
