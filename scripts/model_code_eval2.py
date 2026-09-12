r"""Vòng 2: bài KHÓ hơn để phân biệt model + gỡ lỗi response của opus-5.

Vòng 1 mọi model đều 19/19 -> bộ bài bão hoà, không kết luận được model nào hơn.
Vòng này dùng 3 bài có bẫy tinh vi hơn (off-by-one, thứ tự tie-break, BFS).

Chạy: python scripts\model_code_eval2.py
"""

from __future__ import annotations

import json
import re
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
OUT = ROOT / "experiments" / "results" / "model_code_eval2.md"

TASKS = [
    {
        "name": "min_rooms",
        "prompt": ("Write a Python function `min_rooms(intervals)` returning the minimum number "
                   "of meeting rooms needed. Intervals are [start, end) — a meeting ending at 5 "
                   "does NOT conflict with one starting at 5. Return ONLY the code."),
        "tests": [
            ("kinh điển", "assert min_rooms([[0,30],[5,10],[15,20]]) == 2"),
            ("chạm nhau không tính", "assert min_rooms([[7,10],[10,13]]) == 1"),
            ("trùng hoàn toàn", "assert min_rooms([[1,5],[1,5],[1,5]]) == 3"),
            ("rỗng", "assert min_rooms([]) == 0"),
            ("lồng nhau", "assert min_rooms([[1,10],[2,3],[4,5]]) == 2"),
            ("cần 3", "assert min_rooms([[1,4],[2,5],[3,6]]) == 3"),
            ("chưa sắp xếp", "assert min_rooms([[15,20],[0,30],[5,10]]) == 2"),
        ],
    },
    {
        "name": "top_k_frequent",
        "prompt": ("Write a Python function `top_k(words, k)` returning the k most frequent "
                   "words. Sort by frequency DESCENDING; when frequencies tie, sort "
                   "ALPHABETICALLY ASCENDING. Return ONLY the code."),
        "tests": [
            ("cơ bản", "assert top_k(['i','love','a','i','b'], 2) == ['i','a']"),
            ("tie theo alphabet", "assert top_k(['b','a','c','a','b'], 2) == ['a','b']"),
            ("k > số từ khác nhau", "assert top_k(['x'], 5) == ['x']"),
            ("tie nhiều", "assert top_k(['d','c','b','a'], 3) == ['a','b','c']"),
            ("k = 1", "assert top_k(['z','y','z'], 1) == ['z']"),
        ],
    },
    {
        "name": "bfs_grid",
        "prompt": ("Write a Python function `shortest(grid)` for a grid of 0 (open) and 1 "
                   "(blocked). Return the length of the shortest path from top-left to "
                   "bottom-right moving in 4 directions, counting the number of cells visited "
                   "INCLUDING both endpoints; return -1 if unreachable. Return ONLY the code."),
        "tests": [
            ("đường thẳng", "assert shortest([[0,0,0]]) == 3"),
            ("cần vòng", "assert shortest([[0,0],[0,0]]) == 3"),
            ("có tường", "assert shortest([[0,1],[0,0]]) == 3"),
            ("bị chặn", "assert shortest([[0,1],[1,0]]) == -1"),
            ("một ô", "assert shortest([[0]]) == 1"),
            ("ô đầu bị chặn", "assert shortest([[1,0],[0,0]]) == -1"),
        ],
    },
]

CANDIDATES = [
    ("us.anthropic.claude-opus-4-6-v1", True),
    ("us.anthropic.claude-opus-4-8", False),
    ("us.anthropic.claude-sonnet-4-6", True),
    ("us.anthropic.claude-sonnet-5", False),
    ("qwen.qwen3-coder-next", True),
    ("deepseek.v3.2", True),
    ("zai.glm-5", True),
]


def extract_code(t: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", t, re.S)
    return (m.group(1) if m else t).strip()


def run_tests(code: str, tests) -> tuple[int, list]:
    ns: dict = {}
    try:
        exec(code, ns)
    except Exception as exc:
        return 0, [f"nạp code lỗi: {type(exc).__name__}"]
    p, f = 0, []
    for label, t in tests:
        try:
            exec(t, ns)
            p += 1
        except Exception as exc:
            f.append(f"{label}({type(exc).__name__})")
    return p, f


def ask(model: str, use_temp: bool, prompt: str):
    c = BedrockClient(model=model, region=REGION, temperature=0.0, max_tokens=1200)
    cfg = {"maxTokens": 1200}
    if use_temp:
        cfg["temperature"] = 0.0
    r = c._client.converse(modelId=model,
                           messages=[{"role": "user", "content": [{"text": prompt}]}],
                           inferenceConfig=cfg)
    c.close()
    blocks = r["output"]["message"]["content"]
    return r, blocks


print("=== 0. Gỡ lỗi response của opus-5 (vòng 1 báo 'list index out of range') ===")
try:
    r, blocks = ask("us.anthropic.claude-opus-5", False, "Write a Python function `add(a,b)`.")
    print("  các loại block:", [list(b.keys()) for b in blocks])
    print("  stopReason:", r.get("stopReason"))
    print("  usage:", r.get("usage"))
    txt = next((b.get("text") for b in blocks if "text" in b), None)
    print("  có block text:", bool(txt), "| độ dài:", len(txt) if txt else 0)
except Exception as exc:
    print("  lỗi:", str(exc).splitlines()[0][:120])

print()
print("=== 1. Chấm điểm vòng 2 ===")
rows = []
for model, use_temp in CANDIDATES:
    tot_p = tot_t = 0
    det = []
    for task in TASKS:
        note = ""
        try:
            r, blocks = ask(model, use_temp, task["prompt"])
            txt = next((b.get("text") for b in blocks if "text" in b), "")
            if not txt:
                p, f = 0, ["response không có block text"]
            else:
                p, f = run_tests(extract_code(txt), task["tests"])
        except Exception as exc:
            p, f = 0, [f"gọi lỗi: {str(exc).splitlines()[0][:40]}"]
        tot_p += p
        tot_t += len(task["tests"])
        det.append(f"{task['name']} {p}/{len(task['tests'])}")
        print(f"  {model:44} {task['name']:16} {p}/{len(task['tests'])}"
              + ("" if not f else f"   hỏng: {', '.join(f)}"), flush=True)
    rows.append((model, use_temp, tot_p, tot_t, " · ".join(det)))

print()
print(f"{'model':46} {'temp':7} {'điểm':8} chi tiết")
print("-" * 104)
for m, ut, p, t, d in sorted(rows, key=lambda r: -r[2]):
    print(f"{m:46} {'có' if ut else 'KHÔNG':7} {p}/{t:<6} {d}")

L = ["# Vòng 2 — bài khó hơn (off-by-one, tie-break, BFS)", "",
     f"Region {REGION}. Tổng {sum(len(t['tests']) for t in TASKS)} test ẩn.",
     "", "| Model | Nhận `temperature`? | Điểm | Chi tiết |", "|---|---|---|---|"]
for m, ut, p, t, d in sorted(rows, key=lambda r: -r[2]):
    L.append(f"| `{m}` | {'có' if ut else '**không**'} | **{p}/{t}** | {d} |")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"\n[đã ghi] {OUT}")
