r"""Kiểm tra THẬT: model nào gọi được bằng Bedrock API key hiện có.

Cách làm: gọi thử `Converse` với từng model ID (không đoán từ tài liệu). Danh sách
ứng viên lấy từ catalog model mà extension Cline mang theo (phiên bản 2026), cộng
thêm vài ID không có tiền tố để kiểm chuyện inference-profile.

Phân loại kết quả:
  OK            -> gọi được, có trả lời
  NO-ACCESS     -> model tồn tại nhưng tài khoản không có quyền (ResourceNotFound)
  BAD-ID        -> ID không hợp lệ / không bật on-demand (ValidationException)
  AUTH          -> key bị từ chối ở region này
  ERROR         -> lỗi khác

Kết quả ghi dần vào `experiments/results/bedrock_models_available.md` để nếu job bị
cắt giữa chừng vẫn không mất dữ liệu.

Chạy: python scripts\probe_bedrock_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contagion.llm.envfile import load_dotenv  # noqa: E402

load_dotenv()
from contagion.llm.bedrock import BedrockClient  # noqa: E402

REGION = "us-east-1"
OUT = ROOT / "experiments" / "results" / "bedrock_models_available.md"

# Nhung chuoi khong phai model chat van ban -> bo qua
SKIP_PARTS = ("google.com", "anthropic.messages", "anthropic.sdk", "openai.mcp",
              "openai.shell", "openai.compaction", "openai.computer", "openai.custom",
              "mistral.chat", "mistral.embedding", "mistral.speech", "mistral.transcription",
              "meta.prompt", "cohere.embed", "amazon.nova-canvas", "amazon.nova-",
              "google.ai.generativelanguage", "google.generative-ai", "google.retrieval",
              "google.vertex")

cands: list[str] = []
p = ROOT / "_cands.txt"
if p.exists():
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s or any(k in s for k in SKIP_PARTS):
            continue
        cands.append(s)

# Them ID khong tien to cho cac model thuong can inference profile
extra = ["anthropic.claude-sonnet-4-5-20250929-v1:0", "anthropic.claude-haiku-4-5-20251001-v1:0",
         "meta.llama4-maverick-17b-instruct-v1:0", "openai.gpt-oss-120b-1:0",
         "qwen.qwen3-coder-480b-a35b-v1:0", "deepseek.v3-v1:0", "minimax.minimax-m2.5",
         "zai.glm-5", "moonshot.kimi-k2-thinking", "writer.palmyra-x5-v1:0"]
for e in extra:
    if e not in cands:
        cands.append(e)

seen, uniq = set(), []
for c in cands:
    if c not in seen:
        seen.add(c)
        uniq.append(c)
cands = uniq

print(f"se kiem {len(cands)} model ID o region {REGION}\n", flush=True)
ok, no_access, bad_id, auth, err = [], [], [], [], []

for i, mid in enumerate(cands, 1):
    label, note = "ERROR", ""
    try:
        c = BedrockClient(model=mid, region=REGION, temperature=0.0, max_tokens=5)
        out = c.complete("Reply with the single word OK.")
        c.close()
        label, note = "OK", (out or "").strip().replace("\n", " ")[:24]
        ok.append((mid, note))
    except Exception as e:
        msg = str(e)
        if "Authentication failed" in msg or "AccessDeniedException" in msg and "valid" in msg:
            label = "AUTH"
            auth.append(mid)
        elif "ResourceNotFoundException" in msg:
            label, note = "NO-ACCESS", "model khong mo cho tai khoan nay"
            no_access.append(mid)
        elif "ValidationException" in msg:
            label, note = "BAD-ID", msg.splitlines()[0].split("operation: ")[-1][:70]
            bad_id.append(mid)
        else:
            label, note = "ERROR", msg.splitlines()[0][:70]
            err.append(mid)
    print(f"  [{i:3}/{len(cands)}] {label:10} {mid:52} {note}", flush=True)

    # ghi dan ket qua sau moi model
    lines = ["# Model Bedrock gọi được bằng API key hiện tại", "",
             f"Region kiểm: **{REGION}** · thời điểm: {__import__('datetime').datetime.now():%Y-%m-%d %H:%M}", "",
             f"## ✅ GỌI ĐƯỢC ({len(ok)})", ""]
    lines += [f"- `{m}` → trả lời: {n!r}" for m, n in sorted(ok)]
    lines += ["", f"## ⛔ Không có quyền / không tồn tại ({len(no_access)})", ""]
    lines += [f"- `{m}`" for m in sorted(no_access)]
    lines += ["", f"## ⚠️ ID không hợp lệ cho on-demand ({len(bad_id)})", ""]
    lines += [f"- `{m}`" for m in sorted(bad_id)]
    if auth:
        lines += ["", f"## 🔑 Key bị từ chối ({len(auth)})", ""] + [f"- `{m}`" for m in auth]
    if err:
        lines += ["", f"## ❓ Lỗi khác ({len(err)})", ""] + [f"- `{m}`" for m in err]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print()
print(f"=== TỔNG KẾT: OK {len(ok)} · NO-ACCESS {len(no_access)} · BAD-ID {len(bad_id)} "
      f"· AUTH {len(auth)} · ERROR {len(err)} ===")
print(f"[đã ghi] {OUT}")
