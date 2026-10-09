"""Sinh artifacts/MANIFEST.json -- inventory machine-readable cho bundle (R3 W7).

Một dòng cho mỗi cell đã lưu, đọc TRỰC TIẾP từ file kết quả (không viết tay), gồm:
model, backend, topology, defence, payload, protocol (fresh/fixed nếu suy được),
số natural runs, per-edge trials, n, seed, và file nguồn.

CÁCH DÙNG:  python scripts/build_manifest.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "experiments" / "results"
OUT = ROOT / "artifacts" / "MANIFEST.json"

sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thu muc -> script sinh ra no (ghi tay được vì đây là provenance, không phải số liệu)
SCRIPT_HINTS = [
    ("topo_", "scripts/threshold_analysis.py"),
    ("utility_", "scripts/utility_real.py"),
    ("content_form_", "scripts/content_form_probe.py"),
    ("rerun_chain", "scripts/rerun_chain_raw.py"),
    ("task_b", "scripts/task_b_nlarge.py"),
    ("frontier_", "scripts/replicate_frontier.py"),
    ("depth_curve_", "scripts/depth_trend.py"),
    ("validation_qwen", "scripts/validation_probe.py"),
    ("dag_reconv", "scripts/validation_probe.py"),
    ("role_base", "scripts/validation_probe.py"),
    ("role_perm", "scripts/validation_probe.py"),
    ("transport_tests", "scripts/transport_tests.py"),
]


def _looks_like_cell(d) -> bool:
    return isinstance(d, dict) and (
        "asr" in d or "survival_natural" in d or "surv" in d or "rel_err" in d
        or "rho_recurrent" in d or "compromised" in d)


def extract_cells(o: dict) -> list:
    """Rút mọi 'cell' khỏi một results.json, chấp nhận nhiều định dạng.

    Các định dạng đã gặp trong repo:
      - {backend, model, chain_none: {...}}                 (probe/runner)
      - {backend, model, cells: [ {...}, ... ]}             (content_form, utility)
      - {backend, model, cells: {key: {...}}}               (sensitivity)
      - {"chain n=7 (Llama...)": {...}}                     (threshold_analysis)
      - {..., rows: [...]}                                  (depth_curve)
      - {..., s_isolated, rho_recurrent, ...}               (cyclic)
    Trả list các dict cell đã gắn thêm 'cell_key'.
    """
    out = []
    if _looks_like_cell(o):
        c = dict(o)
        c["cell_key"] = "root"
        out.append(c)
    for k, v in o.items():
        if k in ("backend", "model", "region", "decoding"):
            continue
        if isinstance(v, dict):
            if _looks_like_cell(v):
                c = dict(v)
                c["cell_key"] = k
                out.append(c)
            else:
                for k2, v2 in v.items():
                    if _looks_like_cell(v2):
                        c = dict(v2)
                        c["cell_key"] = f"{k}.{k2}"
                        out.append(c)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            for i, v2 in enumerate(v):
                if _looks_like_cell(v2):
                    c = dict(v2)
                    c["cell_key"] = f"{k}[{i}]"
                    out.append(c)
                elif "depth" in v2 and "rel_err" in v2:
                    c = {"depth": v2.get("depth"), "rel_err": v2.get("rel_err"),
                         "cell_key": f"{k}[{i}]"}
                    out.append(c)
    return out


def script_for(name: str) -> str:
    for pre, s in SCRIPT_HINTS:
        if name.startswith(pre):
            return s
    return "scripts/run_experiment.py"


def main() -> int:
    cells = []
    for p in sorted(RES.rglob("results.json")):
        rel = str(p.relative_to(ROOT))
        try:
            o = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:                      # noqa: BLE001
            cells.append({"source": rel, "error": f"unreadable: {exc}"})
            continue
        if not isinstance(o, dict):
            continue
        collected = datetime.fromtimestamp(
            p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        found = extract_cells(o)
        if not found:
            cells.append({"source": rel, "script": script_for(p.parent.name),
                          "collected": collected, "model": o.get("model"),
                          "backend": o.get("backend"),
                          "note": "không rút được cell nào (định dạng lạ)",
                          "top_keys": list(o.keys())[:10]})
            continue
        for c in found:
            proto = None
            for k in ("per_edge_fresh_artifact", "fresh_artifact", "protocol"):
                if k in c:
                    proto = c[k]
                    break
            cells.append({
                "source": rel,
                "script": script_for(p.parent.name),
                "collected": collected,
                "cell_key": c.get("cell_key"),
                "model": c.get("model") or o.get("model"),
                "backend": c.get("backend") or o.get("backend"),
                "region": c.get("region") or o.get("region"),
                "topology": c.get("topology") or o.get("topology"),
                "num_agents": c.get("num_agents") or o.get("num_agents"),
                "defense": c.get("defense") or c.get("defense_kind"),
                "natural_runs": c.get("n") or c.get("trials"),
                "per_edge_trials": c.get("per_edge") or o.get("per_edge"),
                "asr": c.get("asr"),
                "asr_ci": c.get("asr_ci"),
                "survival": c.get("surv"),
                "r0": c.get("r0"),
                "protocol": proto if proto is not None else "not recorded",
                "decoding": {"temperature": 0.7, "max_tokens": 400},
            })

    doc = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("Một dòng cho mỗi cell. Trường 'protocol' ghi 'not recorded' khi file "
                 "kết quả không lưu cờ protocol — ĐÚNG với toàn bộ bundle hiện tại: "
                 "không results.json nào chứa cờ fresh/fixed. Nhãn protocol trong "
                 "Table 1 của bài chính được suy từ LỆNH CHẠY ghi ở REPRODUCE.md "
                 "(mục B1/B2 dùng --fresh-artifact), không phải từ file kết quả. "
                 "Đây là khoảng trống provenance của artifact, không phải suy đoán."),
        "protocol_evidence": {
            "in_per_cell_files": False,
            "where_to_look": "REPRODUCE.md §B1/B2 (lệnh chạy có --fresh-artifact)",
            "affected_claim": "cột † của Table 1 trong bài chính",
        },
        "decoding_default": {"temperature": 0.7, "max_tokens": 400},
        "n_cells": len(cells),
        "cells": cells,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[done] {OUT} · {len(cells)} cell")

    nr = sum(1 for c in cells if c.get("protocol") == "not recorded")
    print(f"  protocol 'not recorded': {nr}/{len(cells)} cell "
          f"-> phải nói rõ trong bài, không được claim đã ghi")
    models = sorted({c.get("model") for c in cells if c.get("model")})
    print(f"  models ({len(models)}): {', '.join(models)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
