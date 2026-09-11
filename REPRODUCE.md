# REPRODUCE.md — tái lập mọi con số trong paper

> Mục đích: người ngoài (reviewer, artifact chair) chạy lại **từng bảng và từng
> hình** của bản thảo. Mọi lệnh dưới đây chạy từ gốc repo
> (`E:\NCKH\Contagion`).
>
> **Nguyên tắc:** không có số nào trong paper được nhập tay. Mọi bảng/hình đều
> sinh từ `experiments/results/*/results.json` + `report.md`, và các file đó do
> script trong `scripts/` ghi ra.

---

## 0. Kiểm tra môi trường (không tốn API)

```powershell
python -m pytest tests -q                 # phải: 78 passed
python scripts\validate_methods.py        # → experiments/results/validation/
python scripts\make_figures.py --strict   # → figures/ + kiểm tra đè chữ
python scripts\check_figures.py           # 6 phép kiểm tra sâu cho figures
python scripts\threshold_analysis.py      # → percolation + placement (0 API)
```

Nếu `pytest` xanh và `make_figures --strict` báo **0 va chạm**, môi trường đúng.

---

## 1. Bảng nào sinh từ đâu

| Bảng trong paper | Script sinh ra | Chi phí |
|---|---|---|
| **B1** cross-model (5 model) | `replicate_frontier.py --only-chain-none --fresh-artifact` cho từng model | ~25 phút/model |
| **B2** transportability | `replicate_frontier.py ... --fresh-artifact` (có `survival_natural`) | như trên |
| **B3** artefact-policy ablation | chạy B2 **có** và **không** `--fresh-artifact` | ×2 |
| **B4** obfuscation × redaction | `replicate_frontier.py --only-obfuscation --n-obf 30` | ~25 phút |
| **B5** topology (chain/star/tree n=7) | `replicate_frontier.py --topology {chain,star,tree} --num-agents 7` | ~20 phút/cell |
| **B6** utility §7 | `utility_real.py` (3 defense × 2 model) | ~35 phút/defense |
| **B7** depth curve | `depth_curve.py` (3 model) | ~1–2 giờ/model |
| **B8** estimator validation | `validate_methods.py` | ~1 phút |
| **F1–F3** figures | `make_figures.py` | ~1 phút |
| **Bảng percolation/placement** | `threshold_analysis.py` | 0 (tính từ `s` đã đo) |

---

## 2. Lệnh chính xác theo từng model

`<MODEL>` nhận các giá trị đã dùng trong paper:

```
us.meta.llama3-3-70b-instruct-v1:0     # Llama 3.3 70B   (BẮT BUỘC tiền tố us.)
deepseek.v3.2                          # DeepSeek V3.2   (không cần tiền tố)
us.anthropic.claude-sonnet-4-5-20250929-v1:0   # Claude 4.5 (BẮT BUỘC us.)
amazon.nova-pro-v1:0                   # Nova Pro        (không cần tiền tố)
```

> ⚠️ Trên Bedrock, model thuộc Anthropic và Meta **phải** dùng inference-profile
> (`us.`); thiếu tiền tố sẽ báo `ValidationException ... on-demand isn't supported`.
> Đây là lỗi ta đã gặp thật khi chạy Llama.

### 2.1 Cross-model + transportability (B1, B2)

```powershell
python scripts\replicate_frontier.py --backend bedrock --model <MODEL> `
  --region us-east-1 --trials 40 --per-edge 30 --only-chain-none `
  --fresh-artifact --out experiments\results\frontier_<slug>
```

`--fresh-artifact` là **bắt buộc** cho mọi claim compositional: nó rút output
compromised mới cho từng trial thay vì dùng lại một mẫu (xem E25 trong
`EXPERIMENT_LOG.md`).

### 2.2 Ablation artefact cố định vs fresh (B3)

Chạy lại §2.1 **bỏ** `--fresh-artifact`. Chênh lệch giữa hai lần chạy là nội dung
của B3 — và là bằng chứng cho việc ta tự rút lại một claim.

### 2.3 Obfuscation × redaction (B4)

```powershell
python scripts\replicate_frontier.py --backend bedrock --model <MODEL> `
  --region us-east-1 --only-obfuscation --n-obf 30 `
  --out experiments\results\claude_obf_n30
```

### 2.4 Topology (B5)

```powershell
foreach ($t in "chain","star","tree") {
  python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --trials 40 --per-edge 30 --only-chain-none --fresh-artifact `
    --topology $t --num-agents 7 --out experiments\results\topo_${t}_n7
}
```

### 2.5 Utility §7 (B6)

```powershell
python scripts\utility_real.py --backend bedrock --model <MODEL> `
  --region us-east-1 --trials 20 --utility-trials 20 `
  --defenses none,paraphrase,redact --out experiments\results\utility_<slug>
```

`utility_real.py` ghi `results.json` **tăng dần sau mỗi defense**, và
`outputs.jsonl` chứa **raw final output** của mọi trial. Nhờ vậy:
- job chết giữa chừng **không mất** các ô đã xong;
- chấm lại §7 **không cần gọi LLM**:
  `python scripts\utility_from_outputs.py`

### 2.6 Depth curve (B7) — nguồn của hình headline

```powershell
python scripts\depth_curve.py --backend bedrock --model <MODEL> `
  --region us-east-1 --num-agents 15 --trials 60 --per-edge 30 `
  --out experiments\results\depth_curve_<slug>
```

Model local (không tốn API):
```powershell
$env:OPENAI_BASE_URL="http://localhost:11434/v1"; $env:OPENAI_API_KEY="EMPTY"
python scripts\depth_curve.py --backend openai --model qwen2.5:7b `
  --num-agents 7 --trials 60 --per-edge 25 --out experiments\results\depth_curve_qwen
```

Chọn `--num-agents` theo `s̄` của model: nếu `s̄ ≈ 0.7` thì chuỗi 14 hop tắt hẳn
(`0.7^14 ≈ 0.007`) và đường cong vô nghĩa ở cuối. Llama (s̄ cao) dùng n=15;
DeepSeek/qwen dùng n=7–8.

### 2.7 Sensitivity / overdispersion

```powershell
python scripts\sensitivity.py --backend bedrock --model <MODEL> `
  --region us-east-1 --per-edge 20 --seeds 1,2,3,4,5,6 --temps 0.0,0.7,1.0 `
  --out experiments\results\sensitivity_<slug>
```

### 2.8 Kiểm định judge (nếu đổi model hoặc đổi target)

```powershell
python scripts\judge_calibration_probe.py --model <local-model> --n 12
```

---

## 3. Sinh lại toàn bộ bảng/hình từ kết quả đã có (0 API)

```powershell
python scripts\make_figures.py --strict     # 3 hình dùng trong paper + kiểm đè chữ
python scripts\markov_formal_all.py         # bảng kiểm định composition
python scripts\threshold_analysis.py        # percolation, ρ(M), placement
python scripts\isolation_validity.py        # s^controlled vs s^natural
python scripts\utility_from_outputs.py      # chấm lại §7 từ raw output
python scripts\check_paper.py paper\contagion_aamas2027.tex
```

---

## 4. Biên dịch paper

```powershell
cd paper
$mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\bibtex.exe"   contagion_aamas2027
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
python check_pages.py     # đếm số trang NỘI DUNG (giới hạn 8)
```

Cần có trong `paper/`: `aamas.cls`, `by.pdf`/`by.eps`,
`ACM-Reference-Format.bst` (đi kèm gói template AAMAS-2027).

**Kiểm tra sạch:** `^!` trong `.log` = 0, `Overfull \hbox` = 0,
`Citation ... undefined` = 0, số trang nội dung ≤ 8.

---

## 5. Seed, tham số, và những gì cố định

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| seed | 7 (mặc định trong script) | `sensitivity.py` quét seed 1–6 |
| temperature | 0.7 | sensitivity quét thêm 0.0 và 1.0 |
| `tau_asv` | 0.9 | cố định; Task B dùng nhánh ASV-only |
| `tau_mr` | 0.6 | chỉ áp cho Task Family A |
| target (Task B) | `BANANA-77` | `extra["target_b"]` |
| `force_retries` | 3 | số lần thử ép output compromised |
| benign contexts | 3 chuỗi, xoay vòng theo trial | `extra["benign_contexts"]` |

---

## 6. Cảnh báo trung thực khi tái lập

1. **Sampling**: cùng cấu hình chạy lại cho số **khác** (ví dụ DeepSeek chain-none
   cho ASR 0.375 / 0.400 / 0.475 ở ba lần chạy, n=40). Đây là lý do paper báo
   **MDE** chứ không chỉ verdict — đừng kỳ vọng trùng khít.
2. **`--fresh-artifact`**: không có nó, `∏sᵢ` có thể lệch và tạo vi phạm
   composition **giả** ở cả hai hướng (E25/E26). Mọi claim compositional phải có nó.
3. **API key Bedrock hết hạn** giữa phiên là chuyện đã xảy ra (E29). Khi đó
   `scripts/bedrock_key_diag.py` cho biết loại key, còn sống không, và key có bị
   dán lặp ở chỗ khác trên máy không.
4. **`experiments/results/` bị gitignore**: muốn chia sẻ artifact phải copy ra
   ngoài hoặc bỏ dòng ignore.
