r"""Kiểm tra cấu trúc file LaTeX + .bib khi KHÔNG có LaTeX để biên dịch.

Bắt các lỗi làm biên dịch thất bại mà không cần pdflatex:
  1. ``\begin{x}`` / ``\end{x}`` khớp và lồng đúng;
  2. ngoặc ``{ }`` cân bằng (bỏ qua ``\{``, ``\}``);
  3. mọi ``\cite{...}`` có entry tương ứng trong .bib;
  4. mọi ``\ref{...}`` có ``\label{...}``;
  5. mọi ``\includegraphics{...}`` trỏ tới file CÓ THẬT;
  6. mọi ``\label{...}`` đều được tham chiếu (cảnh báo, không phải lỗi);
  7. .bib: mỗi entry cân bằng ngoặc + có key duy nhất;
  8. cảnh báo ký tự non-ASCII trong .tex (nguy cơ lỗi encoding khi nộp).

CÁCH DÙNG
---------
    python scripts\check_paper.py paper\contagion_aamas2027.tex
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BEGIN = re.compile(r"\\begin\{([^}]+)\}")
END = re.compile(r"\\end\{([^}]+)\}")


def strip_comments(text: str) -> str:
    """Bo comment LaTeX (%), nhung giu lai \\% da escape."""
    out = []
    for line in text.splitlines():
        buf = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line):
                buf.append(line[i:i + 2])
                i += 2
                continue
            if ch == "%":
                break
            buf.append(ch)
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def check_environments(tex: str, problems: list, warns: list) -> None:
    stack = []
    for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", tex):
        kind, name = m.group(1), m.group(2)
        line = tex[:m.start()].count("\n") + 1
        if kind == "begin":
            stack.append((name, line))
        else:
            if not stack:
                problems.append(f"dòng {line}: \\end{{{name}}} không có \\begin tương ứng")
            elif stack[-1][0] != name:
                problems.append(
                    f"dòng {line}: \\end{{{name}}} nhưng đang mở "
                    f"\\begin{{{stack[-1][0]}}} (mở ở dòng {stack[-1][1]})")
                stack.pop()
            else:
                stack.pop()
    for name, line in stack:
        problems.append(f"\\begin{{{name}}} (dòng {line}) không có \\end")


def check_braces(tex: str, problems: list) -> None:
    depth = 0
    for i, ch in enumerate(tex):
        if ch == "{" and (i == 0 or tex[i - 1] != "\\"):
            depth += 1
        elif ch == "}" and (i == 0 or tex[i - 1] != "\\"):
            depth -= 1
            if depth < 0:
                line = tex[:i].count("\n") + 1
                problems.append(f"dòng {line}: '}}' thừa (ngoặc âm)")
                depth = 0
    if depth:
        problems.append(f"thiếu {depth} dấu '}}'")


def check_citations(tex: str, bib_keys: set, problems: list) -> None:
    cited = set()
    for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", tex):
        for k in m.group(1).split(","):
            k = k.strip()
            cited.add(k)
            if k not in bib_keys:
                problems.append(f"\\cite{{{k}}} không có entry trong .bib")
    return cited


def check_refs(tex: str, problems: list, warns: list, cited: set) -> None:
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", tex))
    for r in sorted(refs - labels):
        problems.append(f"\\ref{{{r}}} không có \\label tương ứng")
    for lab in sorted(labels - refs):
        warns.append(f"\\label{{{lab}}} không được \\ref tới")
    return labels


def check_graphics(tex: str, base: Path, problems: list) -> None:
    # File do TEMPLATE của hội nghị cung cấp (không nằm trong repo này) — thiếu
    # chúng là bình thường cho tới khi chép template vào.
    TEMPLATE_FILES = {"by", "aamas27-logo-small", "aamas-logo"}
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex):
        raw = m.group(1).strip()
        if raw in TEMPLATE_FILES:
            continue
        cands = [base / raw] + [base / f"{raw}{ext}" for ext in
                                (".png", ".pdf", ".jpg", ".eps")]
        if not any(c.exists() for c in cands):
            problems.append(f"\\includegraphics{{{raw}}} → KHÔNG tìm thấy file "
                            f"(đã thử: {', '.join(str(c.name) for c in cands)})")


def check_bib(bib_path: Path, problems: list, warns: list) -> set:
    if not bib_path.exists():
        problems.append(f"không tìm thấy file .bib: {bib_path}")
        return set()
    text = strip_comments(bib_path.read_text(encoding="utf-8"))
    keys, i = set(), 0
    for m in re.finditer(r"@(\w+)\s*\{", text):
        start = m.end() - 1
        depth, j = 0, start
        while j < len(text):
            if text[j] == "{" and (j == 0 or text[j - 1] != "\\"):
                depth += 1
            elif text[j] == "}" and (j == 0 or text[j - 1] != "\\"):
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            line = text[:start].count("\n") + 1
            problems.append(f"{bib_path.name} dòng {line}: entry @{m.group(1)} "
                            f"KHÔNG cân bằng ngoặc (thiếu '}}')")
            continue
        body = text[start + 1:j]
        key = body.split(",")[0].strip()
        if not key:
            problems.append(f"{bib_path.name}: entry @{m.group(1)} không có key")
        elif key in keys:
            problems.append(f"{bib_path.name}: key trùng '{key}'")
        else:
            keys.add(key)
        i += 1
    if not i:
        warns.append(f"{bib_path.name}: không đọc được entry nào")
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", type=Path)
    ap.add_argument("--bib", type=Path, default=None)
    args = ap.parse_args()

    problems: list = []
    warns: list = []

    raw = args.tex.read_text(encoding="utf-8")
    tex = strip_comments(raw)
    print(f"File: {args.tex}  ({len(raw.splitlines())} dòng)")

    check_environments(tex, problems, warns)
    check_braces(tex, problems)
    cited = check_citations(tex, check_bib(args.bib or args.tex.with_name("refs.bib"),
                                          problems, warns), problems)
    check_refs(tex, problems, warns, cited)
    check_graphics(tex, args.tex.parent, problems)

    non_ascii = sorted({c for c in raw if ord(c) > 127})
    if non_ascii:
        warns.append("ký tự non-ASCII trong .tex: " +
                     " ".join(f"{c!r}" for c in non_ascii[:12]))

    # ``\\[`` bị TeX hiểu là ``\\[<độ dài>]`` → "Missing number, treated as zero"
    # + "Illegal unit of measure". Lỗi này KHÔNG hiện trong stdout khi biên dịch
    # với -file-line-error, nên phải kiểm riêng.
    for m in re.finditer(r"\\\\\[([^\]]{1,40})\]", tex):
        if not re.fullmatch(r"\s*[-+0-9.]*\s*(pt|mm|cm|in|ex|em|sp)?\s*", m.group(1)):
            line = tex[:m.start()].count("\n") + 1
            problems.append(f"dòng {line}: `\\\\[` bị hiểu là ngắt dòng + độ dài "
                            f"(nội dung: {m.group(1)[:30]!r}) — dùng \\par thay `\\\\`")

    # thống kê nội dung (để ước lượng độ dài so với giới hạn 8 trang)
    body = tex
    words = len(re.findall(r"[A-Za-z][A-Za-z'-]+", body))
    print(f"\nƯớc lượng: ~{words} từ trong toàn bộ .tex "
          f"(8 trang ACM 2 cột ≈ 6500–7500 từ nội dung + bảng/hình)")

    print()
    if problems:
        print(f"❌ {len(problems)} LỖI:")
        for p in problems:
            print("   -", p)
    else:
        print("✅ Không phát hiện lỗi cấu trúc (ngoặc, môi trường, cite, ref, hình).")
    if warns:
        print(f"\n⚠️  {len(warns)} cảnh báo:")
        for w in warns:
            print("   -", w)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
