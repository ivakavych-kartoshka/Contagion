r"""Xoá mạnh hơn: bỏ thuộc tính read-only/hidden rồi mới xoá.

Lý do: các file trong `.git/objects` (do Cline tạo checkpoint) có thuộc tính read-only,
nên `shutil.rmtree` báo PermissionError. Cần `onerror` để đổi thuộc tính rồi thử lại.

Chạy: python scripts\remove_cline2.py
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HOME = Path.home()
APPDATA = HOME / "AppData" / "Roaming"

TARGETS = [
    ("globalStorage của Cursor",
     APPDATA / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev"),
    ("globalStorage của VS Code",
     APPDATA / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev"),
]


def force_remove(p: Path) -> None:
    """Xoá cây thư mục, tự bỏ read-only khi gặp lỗi quyền."""
    def on_error(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass
    shutil.rmtree(p, onerror=on_error)


def size_mb(p: Path) -> float:
    try:
        return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6
    except Exception:
        return 0.0


print("=== XOÁ (bỏ read-only trước) ===")
for label, p in TARGETS:
    if not p.exists():
        print(f"  (đã sạch) {label}")
        continue
    mb = size_mb(p)
    try:
        force_remove(p)
    except Exception as exc:
        print(f"  ✗ LỖI {label}: {type(exc).__name__}: {exc}")
        continue
    if p.exists():
        left = size_mb(p)
        n = sum(1 for _ in p.rglob("*"))
        print(f"  ⚠ xoá chưa hết {label}: còn {left:.1f} MB / {n} mục")
    else:
        print(f"  ✓ đã xoá {label}: {mb:.1f} MB")

print()
print("=== KIỂM TRA LẠI ===")
for label, p in TARGETS:
    print(f"  {'CÒN LẠI' if p.exists() else 'sạch  '}  {label}")
