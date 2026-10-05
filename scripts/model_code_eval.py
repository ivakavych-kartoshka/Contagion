r"""Chọn model mạnh nhất cho VIỆC SINH CODE, bằng cách cho làm bài có test ẩn.

Vì sao không chọn theo tên: tên model không cho biết nó code tốt đến đâu, và trong
danh sách còn có model từ chối tham số `temperature` (opus-4-7/4-8/5, sonnet-5) nên
cần biết chúng có dùng được trong client thật hay không.

Cách đo: 3 bài lập trình nhỏ, mỗi bài có test ẩn. Lấy code model trả về, chạy test
trong tiến trình riêng, đếm số test đạt. Không chấm bằng cảm nhận.

Chạy: python scripts\model_code_eval.py
"""

from __future__ import annotations

import json
import re
import sys
import traceback
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
OUT = ROOT / "experiments" / "results" / "model_code_eval.md"

# ---------------------------------------------------------------- bài thi
TASKS = [
    {
        "name": "merge_intervals",
        "prompt": ("Write a Python function `merge_intervals(intervals)` that takes a list of "
                   "[start, end] pairs and returns a new list of non-overlapping intervals "
                   "merged, sorted by start. Touching intervals ([1,2],[2,3]) must merge. "
                   "Return ONLY the code, no explanation."),
        "tests": [
            ("cơ bản", "assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]"),
            ("chạm nhau", "assert merge_intervals([[1,2],[2,3]]) == [[1,3]]"),
            ("rỗng", "assert merge_intervals([]) == []"),
            ("lồng nhau", "assert merge_intervals([[1,10],[2,3]]) == [[1,10]]"),
            ("chưa sắp xếp", "assert merge_intervals([[5,6],[1,2]]) == [[1,2],[5,6]]"),
            ("điểm rời", "assert merge_intervals([[1,2],[3,4]]) == [[1,2],[3,4]]"),
        ],
    },
    {
        "name": "balanced_brackets",
        "prompt": ("Write a Python function `balanced(s)` that returns True if the brackets in "
                   "string s are correctly balanced and nested, considering (), [] and {}. "
                   "Any other characters are ignored. Return ONLY the code, no explanation."),
        "tests": [
            ("đơn giản", "assert balanced('()') is True"),
            ("lồng đúng", "assert balanced('{[()]}') is True"),
            ("sai thứ tự", "assert balanced('([)]') is False"),
            ("thiếu đóng", "assert balanced('(') is False"),
            ("bỏ qua ký tự khác", "assert balanced('a(b)c[d]') is True"),
            ("rỗng", "assert balanced('') is True"),
            ("đóng thừa", "assert balanced(')(') is False"),
        ],
    },
    {
        "name": "parse_pairs",
        "prompt": ("Write a Python function `parse_pairs(s)` that parses a string like "
                   "'a=1;b=2' into a dict. Rules: split on ';', ignore empty pieces, "
                   "ignore pieces without '=', keep the LAST value when a key repeats, "
                   "strip whitespace from keys and values. Return ONLY the code."),
        "tests": [
            ("cơ bản", "assert parse_pairs('a=1;b=2') == {'a':'1','b':'2'}"),
            ("bỏ phần rỗng", "assert parse_pairs('a=1;;b=2;') == {'a':'1','b':'2'}"),
            ("bỏ phần không có =", "assert parse_pairs('a=1;junk;b=2') == {'a':'1','b':'2'}"),
            ("khoá lặp lấy cuối", "assert parse_pairs('a=1;a=9') == {'a':'9'}"),
            ("strip", "assert parse_pairs(' a = 1 ; b = 2 ') == {'a':'1','b':'2'}"),
            ("giá trị có =", "assert parse_pairs('a=x=y') == {'a':'x=y'}"),
        ],
    },
]

CANDIDATES = [
    ("us.anthropic.claude-opus-4-6-v1", True),
    ("us.anthropic.claude-sonnet-4-6", True),
    ("us.anthropic.claude-opus-4-8", False),
    ("us.anthropic.claude-opus-5", False),
    ("us.anthropic.claude-sonnet-5", False),
    ("us.anthropic.claude-sonnet-4-5-20250929-v1:0", True),
    ("qwen.qwen3-coder-next", True),
    ("deepseek.v3.2", True),
    ("zai.glm-5", True),
]


def extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def run_tests(code: str, tests: list) -> tuple[int, list]:
    ns: dict = {}
    try:
        exec(code, ns)
    except Exception as exc:
        return 0, [f"lỗi khi nạp code: {type(exc).__name__}: {exc}"]
    passed, fails = 0, []
    for label, t in tests:
        try:
            exec(t, ns)
            passed += 1
        except Exception as exc:
            fails.append(f"{label}: {type(exc).__name__}")
    return passed, fails


def ask(model: str, use_temp: bool, prompt: str) -> str:
    c = BedrockClient(model=model, region=REGION, temperature=0.0, max_tokens=900)
    cfg: dict = {"maxTokens": 900}
    if use_temp:
        cfg["temperature"] = 0.0
    r = c._client.converse(
        modelId=model,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig=cfg,
    )
    c.close()
    return r["output"]["message"]["content"][0]["text"]


rows = []
for model, use_temp in CANDIDATES:
    total_p = total_t = 0
    detail = []
    for task in TASKS:
        try:
            raw = ask(model, use_temp, task["prompt"])
            code = extract_code(raw)
            p, fails = run_tests(code, task["tests"])
        except Exception as exc:
            p, fails = 0, [f"gọi model lỗi: {str(exc).splitlines()[0][:60]}"]
        total_p += p
        total_t += len(task["tests"])
        detail.append(f"{task['name']} {p}/{len(task['tests'])}")
        print(f"  {model:44} {task['name']:18} {p}/{len(task['tests'])}"
              + ("" if not fails else f"   (hỏng: {', '.join(fails)})"), flush=True)
    rows.append((model, use_temp, total_p, total_t, " · ".join(detail)))

print()
print(f"{'model':46} {'temp':5} {'điểm':8} chi tiết")
print("-" * 100)
for model, use_temp, p, t, d in sorted(rows, key=lambda r: -r[2]):
    print(f"{model:46} {'có' if use_temp else 'KHÔNG':5} {p}/{t:<5} {d}")

L = ["# Chọn model sinh code — đo bằng bài có test ẩn", "",
     f"Region {REGION}. Mỗi model làm 3 bài, tổng {sum(len(t['tests']) for t in TASKS)} test ẩn.",
     "", "| Model | Nhận `temperature`? | Điểm | Chi tiết |", "|---|---|---|---|"]
for model, use_temp, p, t, d in sorted(rows, key=lambda r: -r[2]):
    L.append(f"| `{model}` | {'có' if use_temp else '**không**'} | **{p}/{t}** | {d} |")
L += ["", "## Đề bài", ""]
for task in TASKS:
    L.append(f"### {task['name']}")
    L.append(task["prompt"])
    L += [f"- {lab}" for lab, _ in task["tests"]]
    L.append("")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"\n[đã ghi] {OUT}")
