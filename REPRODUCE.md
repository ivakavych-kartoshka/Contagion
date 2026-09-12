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
| **B7** depth curve (3 model) | `depth_curve.py`; thống kê hình dạng bằng `depth_trend.py` | ~1–2 giờ/model |
| **B8** estimator validation | `validate_methods.py` | ~1 phút |
| **χ² / φ theo temperature** | `sensitivity.py --temps 0.7` | ~20 phút/model |
| **F1–F2** figures (paper dùng 2) | `make_figures.py` | ~1 phút |
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

Biến thể **dùng cho χ² trong §5.10**: chỉ **một** temperature (φ và χ² phải tính
*trong* một temperature — gộp temperature làm φ phồng lên vô nghĩa):

```powershell
python scripts\sensitivity.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --per-edge 20 --seeds 1,2,3,4,5,6,7,8 --temps 0.7 `
  --out experiments\results\sensitivity_llama_t07
```

### 2.8 Kiểm định judge (nếu đổi model hoặc đổi target)

```powershell
python scripts\judge_calibration_probe.py --model <local-model> --n 12
```

---

## 3. Sinh lại toàn bộ bảng/hình từ kết quả đã có (0 API)

```powershell
python scripts\make_figures.py --strict     # hình dùng trong paper + kiểm đè chữ
python scripts\markov_formal_all.py         # bảng kiểm định composition
python scripts\threshold_analysis.py        # percolation, ρ(M), placement
python scripts\isolation_validity.py        # s^controlled vs s^natural
python scripts\utility_from_outputs.py      # chấm lại §7 từ raw output
python scripts\depth_trend.py --dirs depth_curve_llama depth_curve_qwen depth_curve_deepseek
python scripts\cyclic_design_rule.py        # quy tắc thiết kế ρ = sqrt(Σ a_j·c_j) (0 API)
python scripts\scale_report.py              # quy mô: số trial, lượt gọi model, giờ máy
python scripts\audit_numbers.py --md        # → AUDIT_TABLE.md (number audit + claim lint)
python scripts\check_results_complete.py    # mọi thư mục kết quả có hoàn chỉnh không
python scripts\check_paper.py paper\contagion_aamas2027.tex --bib paper\refs.bib
python scripts\check_figures.py             # 6 phép kiểm tra hình (0 API)
python scripts\appendix_stats.py            # BH (Phụ lục A) + cluster CI (Phụ lục B)
```

> ⚠️ **`appendix_stats.py` chưa đọc dữ liệu cho Phụ lục A.** Nó **hard-code** cả 5
> p-value của bảng Benjamini–Hochberg (dòng 45–51), nên nó chỉ in lại số đã gõ chứ
> không kiểm chứng gì. Phụ lục B thì đọc thật từ `sensitivity_llama/results.json` và
> **khớp hoàn toàn** (29/120, Wilson [0.174,0.326], cluster [0.167,0.317], nới 0,99×).
> Ngoài ra `tab:bh` đang ghi `p=0.0001` cho Llama trong khi dữ liệu lưu là **0,00025**,
> và **ô DeepSeek `p=0.0030` là kết quả đã bị rút lại** ở §5.3 — xem
> `SUBMISSION_CHECKLIST.md` §7c trước khi dùng bảng đó.

`depth_trend.py` là script sinh **cột ρ và slope** của Table trong §5.7: nó tính
Spearman hạng giữa depth và sai số tương đối, độ dốc OLS, và **loại tường minh**
các điểm degenerate (`P(C_i=1)=0` ⇒ sai số không xác định) rồi in ra số điểm bị loại.

---

## 4. Biên dịch paper

```powershell
cd paper
$mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\bibtex.exe"   contagion_aamas2027
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
& "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
```

Đếm trang **nội dung** (giới hạn 8; tài liệu tham khảo được thêm trang):
`paper/check_pages.py` **không tồn tại** — dùng một trong hai cách đã kiểm chứng:

```powershell
# (a) số trang của một mục bất kỳ, đọc trực tiếp từ .aux:
Select-String -Path contagion_aamas2027.aux -Pattern 'newlabel\{sec:limits\}'
# (b) nội dung kết thúc ở trang nào: tạm đặt \label{zzendcontent} ngay TRƯỚC
#     \bibliographystyle, dựng lại 1 lần, đọc .aux, rồi xoá label đi.
# (c) trang 9 chỉ được chứa tài liệu tham khảo — giải mã PDF bằng Ghostscript
#     kèm trong MiKTeX (KHÔNG cần cài thêm gì):
& "$mk\mgs.exe" -q -dNOPAUSE -dBATCH -dFirstPage=9 -dLastPage=9 `
  -sDEVICE=txtwrite "-sOutputFile=pg9.txt" contagion_aamas2027.pdf
Select-String -Path pg9.txt -Pattern 'Conclusion'   # phải KHÔNG khớp
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
5. **Điểm degenerate trong depth curve**: khi `P(C_i=1) = 0` thì sai số tương đối
   *không xác định* (chia cho 0). `depth_trend.py` **loại** các điểm đó và in ra số
   điểm bị loại (Llama n=15: bỏ 4 điểm cuối vì chain chết ở depth 11). Nếu gán
   chúng bằng 100% thì đường cong "đẹp" hơn thực tế — đó là cách tự lừa cần tránh.
6. **φ phải tính trong MỘT temperature**. Gộp temperature (0.0/0.7/1.0) cho
   φ = 2.93 — con số đó đo yếu tố hệ thống, không đo overdispersion.
