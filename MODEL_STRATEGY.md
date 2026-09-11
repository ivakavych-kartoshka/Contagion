# CHIẾN LƯỢC MODEL CHO BÀI BÁO A* (Bedrock, us-east-1)

> Key đã chạy tốt: 120 model khả dụng. Không quan tâm giá → chọn bộ model để bài
> có sức nặng nhất với reviewer. Dưới đây là khuyến nghị + lệnh chạy cụ thể.

---

## 1. Vì sao KHÔNG chỉ dùng 1 model?

Reviewer A* sẽ hỏi: *"kết quả này có phải chỉ đúng với 1 model không?"* — nên bài
cần **≥3 model thuộc các họ khác nhau**:
- 2 model **frontier đóng** (Anthropic Claude) — thể hiện "model mạnh nhất"
- 1–2 model **open-weight frontier** (DeepSeek / Llama) — thể hiện "kết quả tổng
  quát, không phụ thuộc nhà cung cấp"
- (đã có) qwen2.5:7b local — baseline nhỏ, miễn phí

## 2. Bộ model khuyến nghị (đủ mạnh, đủ đa dạng)

| Vai trò trong bài | Model ID (Bedrock) | Lý do chọn |
|---|---|---|
| **Chính — headline results** | `anthropic.claude-sonnet-4-5-20250929-v1:0` | Frontier mạnh, **được literature prompt-injection dùng nhiều nhất** → so sánh trực tiếp được với InjecAgent/Adaptive Attacks |
| **Mạnh nhất (robustness check)** | `anthropic.claude-opus-4-5-20251101-v1:0` | Model mạnh nhất Anthropic — chứng minh hiện tượng vẫn tồn tại ở đỉnh cao nhất |
| **So sánh open-weight** | `deepseek.v3.2` | Frontier open-weight — chứng minh không phụ thuộc Anthropic |
| **Baseline open nhỏ hơn** | `meta.llama3-3-70b-instruct-v1:0` | Họ khác (Meta) — thêm 1 điểm dữ liệu |
| **(đã có)** | qwen2.5:7b local | Baseline nhỏ, đối chiếu |

> Nếu giảng viên giới hạn model, tối thiểu nên có: **Sonnet 4.5 + DeepSeek v3.2**
> (1 đóng + 1 mở) — đã đủ để claim không model-specific.

## 3. Quy trình chạy (làm theo thứ tự)

### Bước 0 — Test gọi được model chính
```powershell
cd E:\NCKH\Contagion
python scripts\test_bedrock.py --model anthropic.claude-sonnet-4-5-20250929-v1:0
```
Script tự thử cả dạng có prefix `us.` (inference profile) nếu dạng trực tiếp lỗi.
→ Khi thấy `✓ Gọi thành công!` và dòng `📌 DÙNG LỆNH NÀY`, copy lệnh đó.

### Bước 1 — Replicate trên model CHÍNH (Sonnet 4.5)
```powershell
python scripts\replicate_frontier.py --backend bedrock --model anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1
```
→ `experiments/results/frontier_anthropic-claude-sonnet-4-5-.../report.md`

### Bước 2 — Replicate trên model SO SÁNH (DeepSeek v3.2)
```powershell
python scripts\replicate_frontier.py --backend bedrock --model deepseek.v3.2 --region us-east-1
```

### Bước 3 (tùy chọn, nếu muốn mạnh hơn nữa) — Opus 4.5
```powershell
python scripts\replicate_frontier.py --backend bedrock --model anthropic.claude-opus-4-5-20251101-v1:0 --region us-east-1
```

### Bước 4 — Gửi tôi các report.md
Tôi sẽ lập **bảng so sánh chéo model**:
| Model | Task B surv | Redact | Obfuscation split/spaced | Kết luận |
|---|---|---|---|---|
| qwen2.5:7b (local) | 0.611 | 0.00 | 1.00 / 0.00 | baseline |
| Claude Sonnet 4.5 | ? | ? | ? | ? |
| DeepSeek v3.2 | ? | ? | ? | ? |

→ Nếu hiện tượng (propagation + role-dependence + defense arms-race) **đứng trên
cả 3 họ model** → claim của paper rất mạnh, sẵn sàng viết.

## 4. Sau replicate: các bước tăng sức nặng tiếp theo
1. **Markov power** (trials 200–300) trên Sonnet 4.5 — để claim Markov có ý nghĩa.
2. **Star/tree topology** trên Sonnet 4.5 — chứng minh role/topology tổng quát.
3. **Judge calibration** cho từng model mới (script `judge_calibration_probe.py`)
   — vì ngưỡng ASV/MR là per-model.

## 5. Lưu ý kỹ thuật
- **Inference profile**: Claude 4.x/Opus trên Bedrock thường cần `us.` prefix
  (vd `us.anthropic.claude-sonnet-4-5-20250929-v1:0`). Script `test_bedrock.py`
  đã tự thử cả 2 dạng và in ra dạng chạy được.
- **Model access**: nếu 1 model báo AccessDenied → chưa bật trong Bedrock console
  → Model access.
- **Không cần lo giá** (giảng viên tài trợ), nhưng nên chạy `--trials 20` trước
  để xác nhận pipeline chạy trơn rồi mới chạy full `--trials 40`.
