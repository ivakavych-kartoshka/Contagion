# Model Bedrock gọi được bằng API key hiện tại

**Region: `us-east-1`** · kiểm bằng cách **gọi thật** `Converse` cho từng ID (không
suy đoán từ tài liệu). Key: fingerprint `3c1844fe71`.

Sinh bởi `scripts/probe_bedrock_models.py` + `scripts/probe_bedrock_extra.py`
(quét 108 ID lấy từ catalog model mà extension Cline 4.1.17 mang theo, cộng các ID
bổ sung).

> ⚠️ **Hai quy tắc bắt buộc:**
> 1. Region phải là **`us-east-1`**. Cùng key đó ở `ap-northeast-1` bị từ chối:
>    `Authentication failed: Please make sure your API Key is valid`.
> 2. Model Anthropic và Meta **phải có tiền tố `us.`**. Dùng ID trần
>    (`anthropic.claude-sonnet-4-5-20250929-v1:0`) sẽ lỗi
>    `on-demand throughput isn't supported`.

---

## ✅ Gọi được — 51 model

### Anthropic (Claude) — 9
| Model ID | Ghi chú |
|---|---|
| `us.anthropic.claude-opus-4-8` | mạnh nhất; **không gửi `temperature`** |
| `us.anthropic.claude-opus-4-7` | **không gửi `temperature`** |
| `us.anthropic.claude-opus-5` | **không gửi `temperature`** |
| `us.anthropic.claude-sonnet-5` | **không gửi `temperature`** |
| `us.anthropic.claude-opus-4-6-v1` | nhận `temperature` bình thường |
| `us.anthropic.claude-sonnet-4-6` | nhận `temperature` bình thường |
| `us.anthropic.claude-opus-4-5-20251101-v1:0` | nhận `temperature` |
| `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | **model dự án đang dùng** |
| `us.anthropic.claude-haiku-4-5-20251001-v1:0` | nhẹ, rẻ |

### Amazon (Nova) — 7
`amazon.nova-pro-v1:0` · `amazon.nova-lite-v1:0` · `amazon.nova-micro-v1:0` ·
`us.amazon.nova-pro-v1:0` · `us.amazon.nova-lite-v1:0` · `us.amazon.nova-micro-v1:0` ·
`us.amazon.nova-2-lite-v1:0`

### Mistral AI — 8
`mistral.mistral-large-3-675b-instruct` · `mistral.magistral-small-2509` ·
`mistral.devstral-2-123b` · `mistral.ministral-3-14b-instruct` ·
`mistral.ministral-3-8b-instruct` · `mistral.ministral-3-3b-instruct` ·
`mistral.voxtral-small-24b-2507` · `mistral.voxtral-mini-3b-2507`

### Qwen (Alibaba) — 5
`qwen.qwen3-coder-next` · `qwen.qwen3-coder-30b-a3b-v1:0` · `qwen.qwen3-32b-v1:0` ·
`qwen.qwen3-next-80b-a3b` · `qwen.qwen3-vl-235b-a22b`

### NVIDIA — 4
`nvidia.nemotron-super-3-120b` · `nvidia.nemotron-nano-3-30b` ·
`nvidia.nemotron-nano-12b-v2` · `nvidia.nemotron-nano-9b-v2`

### OpenAI (bản open-weight) — 4
`openai.gpt-oss-120b-1:0` · `openai.gpt-oss-20b-1:0` ·
`openai.gpt-oss-safeguard-120b` · `openai.gpt-oss-safeguard-20b`

### MiniMax — 3
`minimax.minimax-m2.5` · `minimax.minimax-m2.1` · `minimax.minimax-m2`

### Z.ai — 3
`zai.glm-5` · `zai.glm-4.7` · `zai.glm-4.7-flash`

### Meta (Llama) — 3
`us.meta.llama3-3-70b-instruct-v1:0` (model chính của dự án) ·
`us.meta.llama4-maverick-17b-instruct-v1:0` · `us.meta.llama4-scout-17b-instruct-v1:0`

### DeepSeek — 2
`deepseek.v3.2` (dự án đang dùng) · `us.deepseek.r1-v1:0`

### Google — 2
`google.gemma-3-27b-it` · `google.gemma-3-4b-it`

### Moonshot — 1
`moonshot.kimi-k2-thinking`

**Tổng: 12 nhà phát triển** (Anthropic, Amazon, Mistral AI, Alibaba, NVIDIA, OpenAI,
MiniMax, Z.ai, Meta, DeepSeek, Google, Moonshot).

---

## ⛔ Không gọi được

| Nhóm | Model | Lý do thật |
|---|---|---|
| Claude | `us.anthropic.claude-3-5-sonnet-20241022-v2:0`, `us.anthropic.claude-3-7-sonnet-20250219-v1:0`, `us.anthropic.claude-3-5-haiku-20241022-v1:0`, `us.anthropic.claude-opus-4-20250514-v1:0`, `us.anthropic.claude-opus-4-1-20250805-v1:0`, `us.anthropic.claude-sonnet-4-20250514-v1:0` | `model không mở cho tài khoản này` / AccessDenied — model cũ chưa được bật |
| Claude | `us.anthropic.claude-fable-5`, `-5-1` | `data retention mode 'default' is not available` — cần chế độ lưu dữ liệu khác, không phải lỗi quyền |
| Amazon | `us.amazon.nova-premier-v1:0` | bị đánh dấu **Legacy**, tài khoản chưa được bật |
| Meta | `us.meta.llama3-1-8b/70b-instruct-v1:0`, `meta.llama4-*` (ID trần) | cần inference-profile → phải có tiền tố `us.` |
| OpenAI | `openai.gpt-5.4`, `openai.gpt-5.5`, `openai.gpt-6-astra`, `openai.gpt-oss-120b` (trần) | ID không hợp lệ / không bật on-demand. **`openai.gpt-6-astra` chính là model Cline của bạn đang trỏ tới → hỏng** |
| OpenAI | `global.openai.gpt-5.6-luna/sol/terra`, mọi `global.*`, mọi `eu.*` | AccessDenied / ID không hợp lệ — tài khoản này chỉ dùng được endpoint `us.` |
| Mistral | `mistral.pixtral-large-2502-v1:0` | cần inference-profile |
| Qwen | `qwen.qwen3-coder-480b-a35b-v1:0`, `qwen.qwen3-235b-a22b-2507-v1:0` | ID không hợp lệ / chưa bật |
| Writer | `writer.palmyra-x4-v1:0`, `x5-v1:0` | cần inference-profile |
| DeepSeek | `deepseek.r1-v1:0` (trần) | cần tiền tố `us.` |

---

## Gợi ý chọn model để **sinh code** trong Cline

| Ưu tiên | Model ID | Vì sao |
|---|---|---|
| 1 | `us.anthropic.claude-sonnet-4-6` | Mạnh, ổn định, **nhận `temperature`** nên hợp với mọi client |
| 2 | `us.anthropic.claude-opus-4-6-v1` | Mạnh nhất trong nhóm nhận `temperature` |
| 3 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Đang dùng trong dự án, đã kiểm kỹ |
| 4 | `qwen.qwen3-coder-next` | Chuyên code, nhẹ |
| 5 | `deepseek.v3.2` | Mạnh về code, đã dùng trong dự án |
| 6 | `zai.glm-5` / `mistral.devstral-2-123b` / `openai.gpt-oss-120b-1:0` | Phương án thay thế |

**Tránh** các model `opus-4-7`, `opus-4-8`, `opus-5`, `sonnet-5` nếu client còn gửi
`temperature` — chúng báo `` `temperature` is deprecated ``. Chúng gọi được, nhưng chỉ
khi client không gửi tham số đó.
