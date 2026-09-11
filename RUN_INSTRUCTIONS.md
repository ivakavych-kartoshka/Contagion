# HƯỚNG DẪN TỐI ƯU — Replicate trên DeepSeek-V3 (qua OpenRouter)

> Đây là **cách tốt nhất** để de-risk bài báo với model frontier, tiết kiệm tối đa:
> ~$3–8, 3 lệnh chạy, ~30–45 phút tổng. Không cần hiểu code — làm theo từng bước.

---

## Bước 0 — Kiểm tra máy còn chạy được

Mở PowerShell, gõ:
```powershell
cd E:\NCKH\Contagion
python -c "import contagion; print('OK')"
```
Nếu in `OK` → tiếp tục. (Nếu lỗi, báo tôi.)

---

## Bước 1 — Tạo OpenRouter + nạp credit + lấy key (1 lần, ~5 phút)

1. Vào https://openrouter.ai → **Sign Up** (đăng ký bằng Google/GitHub/email).
2. Vào **Settings → Keys** (hoặc https://openrouter.ai/settings/keys) → **Create Key**.
3. Nạp credit: **Settings → Credits → Add Credits** — nạp **$10** là đủ (bước này
   ~$3–8, còn dư cho Markov power sau).
4. Copy key dạng `sk-or-...` (chỉ hiện 1 lần — lưu ngay).

**Kiểm tra model DeepSeek tồn tại** (lấy đúng tên để điền — quan trọng):
```powershell
curl https://openrouter.ai/api/v1/models
```
Tìm dòng có `deepseek` — lấy chuỗi dạng `deepseek/deepseek-chat-v3` hoặc
`deepseek/deepseek-chat-v3-0324`... (tên chính xác có thể khác theo thời điểm —
**lấy đúng cái bạn thấy**). Nếu không thấy DeepSeek, vào
https://openrouter.ai/models tìm "DeepSeek".

---

## Bước 2 — Đặt key vào máy (1 lệnh, mỗi lần mở PowerShell mới)

```powershell
$env:OPENROUTER_API_KEY="sk-or-...THAY_KEY_CUA_BAN..."
```
(Có thể đặt cố định: `[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY","sk-or-...","User")`
rồi mở lại PowerShell.)

---

## Bước 3 — Chạy replicate (3 lệnh, tổng ~30–45 phút)

**Lệnh 1 — toàn bộ bước de-risk** (Task B none + redact + obfuscation):
```powershell
python scripts\replicate_frontier.py --model deepseek/deepseek-chat-v3
```

> Nếu bạn chỉ muốn chạy 1 phần:
> - Chỉ chain defenses (none + redact): thêm `--only-chain-defenses`
> - Chỉ obfuscation: thêm `--only-judge-calib`? KHÔNG — xem ghi chú dưới.
> (Script mặc định chạy đủ 3 mục; 2 cờ kia để chạy lẻ khi cần.)

**Kết quả nằm tại:** `experiments/results/frontier_deepseek-deepseek-chat-v3/report.md`

---

## Bước 4 — Gửi tôi kết quả

Sau khi chạy xong, gửi tôi **nội dung file report.md** (hoặc đường dẫn). Tôi sẽ
phân tích:
- Hiện tượng propagation (chain none) còn đứng không trên DeepSeek?
- Redact còn chặn 100% không?
- Obfuscation split còn qua mặt / spaced còn fail không?
→ Rồi quyết định: viết bài hướng measurement (nếu đứng) hay xoay claim.

---

## Bảng chi phí ước tính

| Mục | Calls ước tính | Chi phí DeepSeek (~$0.27/M in, $1.10/M out) |
|---|---|---|
| Chain none (trials=40) | ~250–400 | ~$0.5–1 |
| Chain redact | ~250–400 | ~$0.5–1 |
| Obfuscation (24 ô × 8) | ~200 | ~$0.5 |
| Judge calib (nếu chạy thêm) | ~150 | ~$0.3 |
| **Tổng** | | **~$2–4** |

---

## ⚠️ Nếu gặp lỗi
- `401 Unauthorized` → key sai / chưa nạp credit → kiểm tra Bước 1–2.
- `404 model not found` → tên model sai → kiểm tra lại Bước 1 (curl models).
- Lỗi khác → copy nguyên dòng lỗi gửi tôi.

---

## Sau khi có kết quả tốt (tùy chọn, ~$5–10 thêm)
- Markov power n=200–300 cho chain none (1 cell) — tôi soạn lệnh riêng.
- Star/tree mỗi loại 1 cell.
