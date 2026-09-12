r"""Kiểm tra key Bedrock còn sót ở đâu trên máy sau khi gỡ Cline.

Quét các thư mục khả nghi nhất (không quét cả ổ đĩa cho nhanh), tìm chuỗi tiền tố
`bedrock-api-key-`. KHÔNG in ra key, chỉ in đường dẫn file + số lần xuất hiện.

Chạy: python scripts\scan_key_leaks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOME = Path.home()
APPDATA = HOME / "AppData" / "Roaming"
PREFIX = b"bedrock-api-key-"

DIRS = [
    ("project (mong đợi CÓ, cần cho script)", Path(r"E:\NCKH\Contagion")),
    ("VS Code extensions", HOME / ".vscode"),
    ("Cursor extensions", HOME / ".cursor"),
    ("VS Code user data", APPDATA / "Code" / "User"),
    ("Cursor user data", APPDATA / "Cursor" / "User"),
    ("thư mục home (file .env, config...)", HOME),
    (".cline (đã xoá - kiểm lại)", HOME / ".cline"),
    (".aws", HOME / ".aws"),
]
SKIP_DIR_NAMES = {"node_modules", ".git", "__pycache__", ".venv", "venv", "site-packages",
                  "results", "logs", ".pytest_cache"}
MAX_BYTES = 5_000_000

found: list[tuple[str, Path, int]] = []
for label, d in DIRS:
    if not d.exists():
        print(f"  (không tồn tại) {label}")
        continue
    hits = 0
    n_files = 0
    for p in d.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            n_files += 1
            data = p.read_bytes()
        except Exception:
            continue
        if PREFIX in data:
            found.append((label, p, data.count(PREFIX)))
            hits += 1
    print(f"  quét {label}: {n_files} file -> {hits} file chứa key")

print()
print("=== KẾT QUẢ ===")
if not found:
    print("  Không tìm thấy chuỗi key ở đâu cả (kể cả .env?)")
for label, p, n in found:
    mark = "  ← CẦN GIỮ (script dự án dùng)" if str(p).lower().endswith(".env") else "  ← NÊN XOÁ"
    print(f"  [{label}] {p}  ({n} lần){mark}")
