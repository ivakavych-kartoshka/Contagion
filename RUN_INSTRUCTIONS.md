# HƯỚNG DẪN CHẠY THỰC NGHIỆM LLM THẬT (tự chạy, tiết kiệm API)

> Tôi (agent) không tự chạy các job LLM dài nữa để khỏi tốn thời gian query.
> Bạn chạy các lệnh dưới đây trên máy (môi trường đã có sẵn: Ollama + qwen2.5:7b
> + package). Khi xong, gửi tôi file report/đường dẫn — tôi phân tích tiếp.
>
> **Kiểm tra Ollama đang chạy trước:** `curl http://localhost:11434/api/tags`
> (thấy qwen2.5:7b là OK). Nếu không, mở Ollama app hoặc chạy
> `"C:\Users\ASUS\AppData\Local\Programs\Ollama\ollama.exe" serve`.

---

## ✅ VIỆC CẦN CHẠY BÂY GIỜ: E19 — obfuscation × redact defense (Task B)

**Trạng thái:** E18 đã xong (bạn gửi kết quả — redact chặn triệt để, survival=0).
Giờ đo **arms-race**: attacker obfuscate value (spaced "BANANA - 77" / split-word)
có qua mặt được literal redact không?

**Thời gian:** ~15–25 phút (12 ô nhỏ, n=8/ô).

**Lệnh chạy:**
```powershell
cd E:\NCKH\Contagion
python scripts\e19_obfuscation_taskb.py --n 8
```

**Kết quả:** `experiments/results/taskb_obfuscation/report.md` + `results.json`

**Cách đọc nhanh (in ngay trên màn hình):**
| defense | style | kỳ vọng |
|---|---|---|
| none | plain | cao (≈0.9) |
| redact | plain | ≈ 0.0 (xác nhận E18) |
| redact | spaced / split-word | **> 0 = obfuscation qua mặt redact** (arms-race thật) |

Sau khi xong, gửi tôi nội dung `report.md`.

---

## (Đã xong) E18 — redaction deterministic
```powershell
python scripts\e18_redact_chain.py --trials 40 --per-edge 30
```
Kết quả đã nhận: survival = 0.000 (chặn triệt để attack tĩnh).

---

## (Tùy chọn, sau E18) Các việc tiếp theo có thể chạy

Chưa chạy vội — chờ kết quả E18 rồi tôi sẽ chỉ định việc kế tiếp + lệnh chạy.
Hai ứng viên dự kiến:
1. **Task B sweep topology** (chain×star×tree, n=40/cell, ~4–6h) — dataset
   attack-side chính thức.
2. Hoặc **tách 2 loại compromise** (nếu E18 cho thấy metric gộp) — cần đổi code,
   tôi sẽ code xong rồi mới đưa lệnh chạy.

---

## Ghi chú
- Không sửa file code trừ khi tôi báo (mọi thứ đã được chuẩn bị sẵn: 64 tests pass).
- Nếu muốn chạy nhanh hơn: giảm `--trials 30` (CI rộng hơn chút, ~1 giờ).
- Muốn chạy qua đêm nhiều cell: chờ tôi đưa script sweep sau E18.
