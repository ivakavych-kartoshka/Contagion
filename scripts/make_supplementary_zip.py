"""Đóng gói supplementary material thành 1 file zip <=25MB (quy định AAMAS 2027).

Quy định (trích Submission Instructions):
  "Supplementary material should be submitted as a single zip file and should not
   exceed 25MB." ... "you must ensure that your supplementary material does not
   compromise the anonymity of your submission."

Script này:
  1. Liệt kê những gì SẼ đưa vào (code + kết quả + phụ lục + manifest + hướng dẫn).
  2. Loại những gì KHÔNG được public: ghi chú nội bộ, bản nháp, môi trường ảo, cache,
     file tạm, và bất kỳ thứ gì chứa tên/đường dẫn cá nhân.
  3. Cảnh báo nếu có file nghi lộ danh tính (tên người, email, đường dẫn máy).
  4. Zip và báo kích thước so với 25MB.

CÁCH DÙNG
---------
    python scripts/make_supplementary_zip.py            # chỉ kiểm tra, không ghi
    python scripts/make_supplementary_zip.py --write    # ghi file zip
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_MB = 25.0

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thư mục lấy vào bundle
INCLUDE_DIRS = ["contagion", "scripts", "tests", "artifacts", "experiments"]
INCLUDE_FILES = ["README.md", "REPRODUCE.md", "requirements.txt", "pyproject.toml",
                 "setup.py", "setup.cfg", "MANIFEST.in"]
INCLUDE_GLOBS = ["paper/supplementary.tex", "paper/supplementary.pdf"]

# Không bao giờ đưa vào
EXCLUDE_DIRS = {".venv", "venv", ".git", "__pycache__", ".pytest_cache", ".mypy_cache",
                ".ruff_cache", "node_modules", ".idea", ".vscode", "data_raw"}
# Ghi chú nội bộ / bản nháp — KHÔNG public
EXCLUDE_FILES = {
    "EXPERIMENT_LOG.md", "DECISION_MEMO.md", "PAPER_DRAFT.md", "PAPER_TEXT.md",
    "REVIEWS_AAMAS2027.md", "REVIEW_PROMPT_V2.md", "ACTION_CHECKLIST_RAISE_SCORE.md",
    "ISSUES_TO_FIX.md", "SUBMISSION_CHECKLIST.md", "AUDIT_TABLE.md", "DATA_DETAIL.md",
    "MODEL_STRATEGY.md", "RESEARCH_SUMMARY.md", "RUN_INSTRUCTIONS.md",
    "TASK_B_DESIGN.md", "TIER2_RUN_GUIDE.md", "BEDROCK_FIRST_TIME.md",
    "BEDROCK_MODELS.md", "HUONG_DAN_MUC11_llama_n200.md", "PAGE_LIMIT_CHECK.md",
    # script debug cá nhân, chứa đường dẫn máy — không liên quan tới bài
    "find_cline_error_code.py",
}
# Mẫu bị coi là false-positive của scanner danh tính (nội dung payload giả trong thí
# nghiệm / template của class), KHÔNG cần sửa.
IDENTITY_ALLOWLIST = [
    ("support@company.com", "email giả trong payload thí nghiệm"),
    ("security-team@ourcompany.com", "email giả trong payload thí nghiệm"),
    ("anonymous@example.org", "template affiliation của class"),
]
EXCLUDE_SUFFIX = {".zip", ".pyc", ".pyo", ".log", ".aux", ".out", ".toc", ".blg"}

# Mẫu nghi lộ danh tính trong nội dung file text
IDENTITY_PATTERNS = [
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I), "đường dẫn Windows có tên user"),
    (re.compile(r"/home/[a-z0-9_.-]+/", re.I), "đường dẫn Linux có tên user"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "địa chỉ email"),
    (re.compile(r"\bASUS\b", re.I), "tên máy"),
]


def excluded(p: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return True
    if p.name in EXCLUDE_FILES:
        return True
    if p.suffix.lower() in EXCLUDE_SUFFIX:
        return True
    if p.name.startswith("_") and p.suffix == ".py":
        return True
    return False


def collect() -> list:
    out = []
    for d in INCLUDE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and not excluded(p.relative_to(ROOT)):
                out.append(p)
    for f in INCLUDE_FILES:
        p = ROOT / f
        if p.exists():
            out.append(p)
    for g in INCLUDE_GLOBS:
        out.extend(q for q in ROOT.glob(g) if q.is_file())
    return sorted(set(out))


def scan_identity(paths: list) -> list:
    """Tìm dấu vết danh tính trong file text (cảnh báo, không tự sửa).

    Bỏ qua các mẫu trong IDENTITY_ALLOWLIST (payload giả / template của class).
    """
    allow = [a for a, _ in IDENTITY_ALLOWLIST]
    hits = []
    for p in paths:
        if p.suffix.lower() not in {".md", ".py", ".json", ".txt", ".yaml", ".yml",
                                    ".toml", ".cfg", ".tex", ".csv"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # loại các dòng chỉ chứa mẫu được phép
        reduced = "\n".join(ln for ln in text.splitlines()
                            if not any(a in ln for a in allow))
        for rx, what in IDENTITY_PATTERNS:
            m = rx.search(reduced)
            if m:
                hits.append((str(p.relative_to(ROOT)), what, m.group(0)[:40]))
                break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="ghi file zip")
    ap.add_argument("--out", type=Path, default=ROOT / "supplementary_material.zip")
    args = ap.parse_args()

    files = collect()
    total = sum(p.stat().st_size for p in files)
    print(f"file se dua vao : {len(files)}")
    print(f"tong kich thuoc  : {total / 1e6:.2f} MB  (gioi han {MAX_MB} MB)")
    print(f"con lai          : {MAX_MB - total / 1e6:.2f} MB")

    hits = scan_identity(files)
    if hits:
        print(f"\n[!] {len(hits)} file co dau vet danh tinh (xem xet sua truoc khi public):")
        for f, what, ex in hits[:25]:
            print(f"    {f:<58} {what:<28} {ex}")
        if len(hits) > 25:
            print(f"    ... va {len(hits) - 25} file nua")
    else:
        print("\n[ok] khong thay dau vet danh tinh trong cac file text")

    big = sorted(files, key=lambda p: -p.stat().st_size)[:8]
    print("\nfile lon nhat:")
    for p in big:
        print(f"    {p.stat().st_size / 1e6:7.2f} MB  {p.relative_to(ROOT)}")

    over = total / 1e6 > MAX_MB
    if over:
        print(f"\n[x] VUOT {MAX_MB} MB — phai loai bot (thuong la experiments/results)")
        return 2

    if args.write:
        with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                z.write(p, p.relative_to(ROOT))
        size = args.out.stat().st_size / 1e6
        print(f"\n[done] {args.out}  ({size:.2f} MB)")
        if size > MAX_MB:
            print(f"[x] zip {size:.2f} MB > {MAX_MB} MB")
            return 2
    else:
        print("\n(chay lai voi --write de ghi zip)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
