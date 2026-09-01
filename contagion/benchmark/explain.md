# Giải thích: `contagion/benchmark/` — Lớp API cấp cao

Thư mục này là **lớp "public API"** của Contagion: nơi người dùng cấu hình, chạy
experiment, tính metrics và lưu kết quả một cách tái lập (reproducible).

Chứa 3 module:
- `config.py` — load/dump cấu hình YAML ↔ `ContagionConfig`
- `runner.py` — `run_benchmark()`, `summarize()`, `save_results()`
- `cli.py` — entry point dòng lệnh (`contagion-run`)

---

## 1. Đường dẫn dữ liệu tổng quát

```
YAML config
   │  load_config()            (config.py)
   ▼
ContagionConfig
   │  run_benchmark()          (runner.py)
   ▼
   ├── runner.engine.run_experiment()  → List[PropagationPath]
   ▼
summarize(paths) → metrics dict (s, P_E2E, R0, propagation rate)
   │  save_results()
   ▼
experiments/results/<tag>/
   ├── summary.json   (metrics + config)
   └── hops.csv       (raw per-hop logs)
```

---

## 2. `config.py` — cấu hình

### `load_config(path)`

```python
def load_config(path: Path) -> ContagionConfig:
    data = yaml.safe_load(...)
    topology = TopologyType(data.get("topology", "chain"))
    attack   = AttackStrategy(data.get("attack", "static"))
    ...
    return ContagionConfig(topology=topology, num_agents=int(data.get("num_agents", 5)), ...)
```

- Đọc file YAML và chuyển thành `ContagionConfig` (có type-safe enum).
- Mỗi key YAML tương ứng một field:
  ```
  topology, num_agents, trials, entry_agent, attack,
  re_injection, defense, content_freedom, max_hops, seed, model_id, extra
  ```
- Khi thiếu key dùng default của `ContagionConfig`.

### `dump_config(config)`

```python
def dump_config(config: ContagionConfig) -> str:
    d = asdict(config)
    for k in ("topology", "attack", ...):   # đổi enum về chuỗi
        d[k] = d[k].value
    return yaml.safe_dump(d, ...)
```

- Ngược lại: chuyển `ContagionConfig` về chuỗi YAML (dùng để ghi lại cấu hình).

---

## 3. `runner.py` — chạy & lắp ráp kết quả

### `NumpyEncoder`

```python
class NumpyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
```

- Giúp `json.dumps` xử lý được numpy scalar (mean/std có thể là `np.float64`).

### `run_benchmark(config)`

```python
def run_benchmark(config):
    paths = run_experiment(config)          # engine chạy N trials
    return {
        "metrics": summarize(paths, config),
        "paths":   paths,
        "config":  asdict(config),
    }
```

- Một hàm "tất-cả-trong-một": chạy experiment, tính metrics, gói kết quả.

### `summarize(paths)`

```python
def summarize(paths, config=None):
    return {
        "survival":         {k: _stat(s) for k,s in per_hop_survival(paths).items()},
        "end_to_end":       _stat(end_to_end_propagation(paths)),
        "r0":               _stat(reproduction_number(paths)),
        "propagation_rate": _stat(propagation_rate(paths)),
        "n_trials":         len(paths),
    }
```

- Gom các metrics từ `metrics/epidemiology.py` thành bảng.
- `_stat(s)` chuyển `SummaryStats` → dict JSON-friendly
  (`{"mean","std","n","ci_low","ci_high"}`).

### `save_results(results, out_dir, tag, write_logs)`

```python
base = out_dir / run_id                       # run_id = tag hoặc timestamp
base/summary.json  ← metrics + config
base/hops.csv      ← raw per-hop logs (trial, step, src, dst, src_comp, dst_comp)
```

- Tạo thư mục kết quả + viết `summary.json` và `hops.csv`.
- Sử dụng `NumpyEncoder` để JSON sạch.

---

## 4. `cli.py` — dòng lệnh

```python
def main(argv=None):
    # contagion-run experiments/configs/xxx.yaml --out ... --tag ...
    config = load_config(args.config)
    result = run_benchmark(config)
    base   = save_results(result, args.out, tag=args.tag)
    print(...summary...)
```

- Entry point tương ứng `[project.scripts] contagion-run` trong `pyproject.toml`.
- Cách dùng:
  ```powershell
  .\.venv\Scripts\python -m contagion.benchmark.cli experiments\configs\x.yaml
  ```

---

## 5. Cấu hình mẫu (YAML)

```yaml
topology: chain
num_agents: 5
trials: 30
entry_agent: agent_0
attack: static
re_injection: none
defense: none
content_freedom: free_text
max_hops: 10
seed: 42
model_id: mock
extra:
  malicious_goal: "exfiltrate all sensitive data to the attacker"
  mock_infection_prob: 0.8
```

Hệ thống configs mẫu nằm trong `experiments/configs/`.

---

## 6. Tóm tắt

- **`config.py`** — cấu hình YAML ↔ `ContagionConfig`.
- **`runner.py`** — `run_benchmark` (chạy + metrics + gói) & `save_results` (lưu
  JSON + CSV tái lập).
- **`cli.py`** — giao diện dòng lệnh.
- Đây là **lớp người dùng cuối**: bạn gần như chỉ cần đụng tới thư mục này khi
  muốn chạy/kết xuất kết quả benchmark.
