# HƯỚNG DẪN DÙNG AMAZON BEDROCK (key dạng `bedrock-api-key-...`)

> Giảng viên đã đưa key dạng `bedrock-api-key-...` = **Amazon Bedrock API key**.
> Loại này DỄ dùng nhất: không cần Access Key/Secret, không cần cấu hình AWS phức
> tạp. Chỉ cần đặt 1 biến môi trường. Code đã được chuẩn bị sẵn (BedrockClient).

---

## BƯỚC 1 — Cài thư viện AWS (1 lệnh)
Mở PowerShell:
```powershell
python -m pip install boto3
```

## BƯỚC 2 — Đặt key vào máy (chọn 1 trong 2 cách)

### Cách A (KHUYẾN NGHỊ) — dùng file `.env`, dán 1 lần, không phải gõ lại

1. Trong PowerShell, tại thư mục dự án, tạo file `.env` từ file mẫu:
```powershell
cd E:\NCKH\Contagion
Copy-Item .env.example .env
```
2. Mở file `.env` bằng Notepad:
```powershell
notepad .env
```
3. Dán key vào **sau dấu `=`** ở dòng `AWS_BEARER_TOKEN_BEDROCK=`:
```
AWS_BEARER_TOKEN_BEDROCK=bedrock-api-key-...DAN_KEY_THAT_CUA_BAN...
AWS_DEFAULT_REGION=us-east-1
```
4. **Lưu** (Ctrl+S) rồi **đóng Notepad**. Xong — mọi script tự đọc file này.

> File `.env` nằm ngay trong `E:\NCKH\Contagion\.env` (cùng chỗ với README.md).
> File này đã được `.gitignore` bỏ qua → **không bị đẩy lên git**, an toàn.

### Cách B — đặt biến môi trường tạm (mất khi đóng PowerShell)
```powershell
$env:AWS_BEARER_TOKEN_BEDROCK="bedrock-api-key-...DAN_KEY_CUA_BAN..."
```

> ⚠️ **Đừng dán key vào chat** — nếu đã lộ thì phải nhờ giảng viên cấp key mới.

### Kiểm tra key đã được nạp chưa
```powershell
python scripts\test_bedrock.py
```
Dòng đầu sẽ in `✓ Có xác thực: Bedrock API key` — nghĩa là đã đọc được key.

## BƯỚC 3 — Kiểm tra kết nối + tìm model khả dụng
```powershell
cd E:\NCKH\Contagion
python scripts\test_bedrock.py
```
Script tự thử các region phổ biến và **liệt kê model bạn được phép dùng**.

Kết quả mong đợi:
```
✓ Có xác thực: Bedrock API key
✓ [us-east-1] kết nối OK — N model khả dụng:
    - anthropic.claude-sonnet-4-5-20250929-v1:0
    - amazon.nova-pro-v1:0
    ...
→ Region dùng được: us-east-1
```

**Nếu lỗi:**
- `AccessDenied` / 0 model → giảng viên chưa bật **Model access** trong Bedrock console → nhờ bật.
- Không region nào kết nối → key hết hạn (loại 30 ngày) hoặc key sai → nhờ cấp lại.

## BƯỚC 4 — Gọi thử 1 model (xác nhận chạy được)
Lấy 1 mã model từ Bước 3, vd:
```powershell
python scripts\test_bedrock.py --region us-east-1 --model anthropic.claude-sonnet-4-5-20250929-v1:0
```
Kết quả mong đợi: `✓ Gọi thành công! Output: 'OK'`
→ Nếu OK, bạn **đã sẵn sàng chạy thí nghiệm**.

## BƯỚC 5 — Chạy replicate (thí nghiệm chính)
```powershell
python scripts\replicate_frontier.py --backend bedrock --model anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1
```

**Kết quả:** `experiments/results/frontier_<model>/report.md`

## BƯỚC 6 — Gửi tôi report.md để phân tích
Tôi sẽ so sánh với baseline qwen2.5:7b local:
- Task B none: ASR 0.30 / surv 0.61
- Redact: surv 0.00
- Obfuscation: split qua mặt 100%, spaced fail
→ Rồi kết luận hiện tượng có đứng trên Claude không.

---

## Tùy chọn khi chạy
| Muốn gì | Thêm |
|---|---|
| Chạy nhẹ trước (nhanh, ít tốn) | `--trials 20 --per-edge 15 --n-obf 5` |
| Chỉ 2 cell chain (bỏ obfuscation) | `--only-chain-defenses` |
| Bỏ hẳn obfuscation | `--skip-obfuscation` |
| Đổi model khác | thay `--model` bằng id từ Bước 3 |
| Đổi region | `--region us-west-2` |

---

## Chi phí (giảng viên tài trợ)
Claude Sonnet 4.5 trên Bedrock ≈ $3/M input + $15/M output.
- Replicate đầy đủ (~600 call, ~0.5M token) ≈ **$2–5**
- Chạy nhẹ `--trials 20` ≈ **$1**
- Markov power (n=200–300, 2 cells) ≈ **$10–20**
→ Tổng tới khi nộp paper ≈ **$15–30**.

---

## Checklist
- [ ] B1: `pip install boto3`
- [ ] B2: đặt `$env:AWS_BEARER_TOKEN_BEDROCK`
- [ ] B3: `python scripts\test_bedrock.py` → thấy model + region
- [ ] B4: gọi thử 1 model → ra `OK`
- [ ] B5: chạy replicate
- [ ] B6: gửi tôi `report.md`

**Báo tôi khi xong B3 hoặc nếu gặp lỗi** — tôi sẽ hỗ trợ ngay bước tiếp.
