"""Đọc file `.env` ở thư mục gốc dự án (nếu có) — nạp biến môi trường.

Mục đích: người dùng chỉ cần dán key vào file `.env` (copy từ `.env.example`)
thay vì gõ `$env:...` mỗi lần mở PowerShell. Không phụ thuộc package ngoài
(không cần python-dotenv): tự parse các dòng `KEY=VALUE`.

Chỉ nạp biến CHƯA có trong môi trường (biến env thật được ưu tiên).
"""

from __future__ import annotations

import os
from pathlib import Path

# Các biến được phép nạp từ .env (tránh nạp bừa biến lạ).
ALLOWED = {
    "AWS_BEARER_TOKEN_BEDROCK",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "AWS_REGION",
    "OPENROUTER_API_KEY",
    "OPENROUTER_BASE",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
}


def load_dotenv() -> dict:
    """Nạp .env (nếu có) và trả về dict các biến vừa nạp."""
    # tìm .env đi ngược từ file này lên tới gốc dự án
    here = Path(__file__).resolve()
    candidates = [here.parents[i] / ".env" for i in range(len(here.parents))]
    env_path = next((p for p in candidates if p.is_file()), None)
    if env_path is None:
        return {}

    loaded: dict = {}
    for raw in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key not in ALLOWED or not val:
            continue
        if not os.environ.get(key):       # env thật thắng .env
            os.environ[key] = val
            loaded[key] = val
    return loaded


def mask(secret: str) -> str:
    """Che key khi in ra log: chỉ hiện 8 ký tự đầu."""
    if not secret:
        return "(trống)"
    return secret[:12] + "..." + secret[-4:] if len(secret) > 20 else "***"
