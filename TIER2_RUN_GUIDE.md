# TIER 2 — Hướng dẫn chạy (câu lệnh tốt nhất, bỏ qua chi phí API)

> **Mục tiêu:** đóng các "major" còn lại trong review (R2 W1/W2/W3, R1 W2, R3 W1/W3,
> R4 W2) → nâng R2 5→6, R4 4→5, củng cố R1/R3 6→7, đẩy bài từ *Conditional Accept*
> lên *Accept vững / hướng Oral*.
> **Nguyên tắc doc này:** cho **cấu hình mạnh nhất** (n lớn, powered), không tối ưu
> chi phí. Mọi lệnh chạy từ gốc repo `E:\NCKH\Contagion` trong PowerShell.
> **Sau khi chạy xong mỗi mục → xem mục "Cập nhật bài" cuối doc** để đưa số vào `.tex`
> (giữ đúng 8 trang, xem cảnh báo layout).

---

## 0. Chuẩn bị môi trường (làm 1 lần)

```powershell
cd E:\NCKH\Contagion

# (a) Key Bedrock — dạng bearer token (đã dùng trong repo):
$env:AWS_BEARER_TOKEN_BEDROCK = "bedrock-api-key-..."   # dán key thật
# Kiểm key còn sống + đúng loại:
python scripts\bedrock_key_diag.py

# (b) Model id (BẮT BUỘC tiền tố us. cho Meta/Anthropic):
#   Llama    us.meta.llama3-3-70b-instruct-v1:0
#   DeepSeek deepseek.v3.2
#   Claude   us.anthropic.claude-sonnet-4-5-20250929-v1:0
#   Nova     amazon.nova-pro-v1:0
#   qwen local (0 API): backend openai + Ollama (xem T2.4)

# (c) Smoke test 1 call trước khi đốt tiền:
python scripts\smoke_real_llm.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1
```

> ⚠️ Thiếu tiền tố `us.` cho Llama/Claude → `ValidationException ... on-demand isn't
> supported`. Đây là lỗi repo đã gặp thật.

> ⚠️ **`experiments/results/` bị gitignore.** Kết quả mới ghi ra đó vẫn dùng được cho
> `make_figures.py` / `audit_numbers.py`, nhưng muốn lưu vĩnh viễn phải copy ra ngoài.

---

## T2.1 — Đa payload (đóng R2 W1 "single payload", R4 W2 coverage)

**Vì sao:** mọi số headline hiện dùng đúng 1 target `BANANA-77`. Reviewer nghi 3.75×
underestimate + hiệu ứng content-form có thể là artefact của 1 payload. Chạy lại
transport + content-form với **2–3 target benign khác** để chứng minh hiệu ứng bền.

**✅ Code đã sửa sẵn — chỉ chạy lệnh.** Cả `replicate_frontier.py` và
`content_form_probe.py` giờ có flag **`--marker`** để đổi payload, không phải sửa code.

```powershell
# Lặp cho từng payload (gốc BANANA-77 đã có; chạy thêm 2 payload mới):
foreach ($p in "MANGO-42","ORCA-19") {
  # (1) transport ở n cao trên Llama (model có hiệu ứng mạnh nhất):
  python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
    --marker $p --out experiments\results\frontier_llama_payload_$p

  # (2) content-form cùng payload:
  python scripts\content_form_probe.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --num-agents 4 --trials 60 --per-edge 60 `
    --marker $p --out experiments\results\content_form_llama_$p
}
```

> ⚠️ Chọn marker dạng `WORD-NN` (có dấu `-`) để các biến thể obfuscation tách
> prefix/suffix đúng. Payload phải **benign** (mã giả, không phải secret thật).

**Đọc kết quả:** so `chain_none.markov_formal.delta` (Δ = ASR − ∏s^ctrl) giữa các payload.
Nếu cả 3 đều Δ dương lớn (≈0.6) và content-form effect ≈ +0.9 trên cạnh giữa →
hiệu ứng **không** phụ thuộc payload. Đóng R2 W1.

---

## T2.2 — Adaptive-attacker probe (đóng R2 W1 "static attacker", R2 Q3)

**Vì sao:** verdict phòng thủ hiện đo dưới attacker **tĩnh, không thích nghi**. Reviewer
muốn thấy redaction có sống sót trước đối thủ tự tìm cách né.

**✅ Code đã sửa sẵn — chỉ chạy lệnh.** `replicate_frontier.py` giờ có flag
**`--adaptive-obf`**: bật 7 style obfuscation (plain, spaced, split-word, +
**interleaved / reversed / base-hint / acrostic**) mô phỏng attacker thích nghi, tự
sinh biến thể từ marker hiện tại.

```powershell
python scripts\replicate_frontier.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --only-obfuscation --n-obf 50 --adaptive-obf `
  --out experiments\results\adaptive_obf_llama_n50
```

**Đọc kết quả:** trong `results.json.obfuscation`, xét các hàng `defense=redact`. Nếu
tồn tại ≥1 style đẩy `redact` rate từ 0.00 lên >0 → chứng minh redaction
**bypassable dưới adaptive attacker** → nâng R2 (không còn overclaim "redaction →
0.000" như verdict tuyệt đối). So với `defense=none` cùng style để biết style đó có
thực sự "qua mặt được" hay chỉ model không tuân.

---

## T2.3 — Instance cyclic thứ hai (đóng R1 W2, R4 W2)

**Vì sao:** design rule `ρ(M)=√(Σ_j a_j c_j)`, `w·s²>1` (Appendix D) hiện chỉ có **1
instance** (1 manager, 2 worker). R1 muốn ≥2 điểm/chiều để "rule" có kiểm chứng. Chạy
thêm cấu hình recurrent khác: **`w` khác** (3 worker) và/hoặc **model thứ 2**.

```powershell
# (a) Llama, tăng số worker (rounds cao để thấy endemic vs decay rõ):
python scripts\cyclic_probe.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --trials 60 --per-edge 40 --rounds 8 `
  --out experiments\results\cyclic_llama_w3

# (b) Model thứ 2 (DeepSeek) cùng pattern để có điểm chiều "decay/endemic" khác:
python scripts\cyclic_probe.py --backend bedrock `
  --model deepseek.v3.2 --region us-east-1 `
  --trials 60 --per-edge 40 --rounds 8 `
  --out experiments\results\cyclic_deepseek

# (c) Phân tích closed-form vs đo (0 API, sau khi có results.json):
python scripts\cyclic_design_rule.py
```

**Đọc kết quả:** đối chiếu `rho_recurrent` (đo) với `√(Σ a_j c_j)` (closed-form) trên
mỗi instance mới. Nếu instance supercritical thật sự endemic và subcritical thật sự
decay → `w·s²>1` thành **rule có ≥2 điểm mỗi chiều**. Đóng R1 W2.

---

## T2.4 — Depth-slope trên frontier model (đóng R3 W3, R1 W2)

**Vì sao:** slope diagnostic (+11.8 pp/hop) sạch nhất trên **qwen 7B local**; Llama chết
ở depth 11, DeepSeek phẳng. R3 muốn xác nhận diagnostic trên frontier model đủ dài.

```powershell
# DeepSeek (s̄ trung bình → chuỗi ngắn hơn để cuối chuỗi không tắt hẳn):
python scripts\depth_curve.py --backend bedrock `
  --model deepseek.v3.2 --region us-east-1 `
  --num-agents 10 --trials 120 --per-edge 60 `
  --out experiments\results\depth_curve_deepseek_long

# Llama (s̄ cao → n=15, trials/per-edge cao cho slope powered):
python scripts\depth_curve.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --num-agents 15 --trials 120 --per-edge 60 `
  --out experiments\results\depth_curve_llama_long

# Thống kê slope + ρ (0 API), loại điểm degenerate:
python scripts\depth_trend.py
```

> Chọn `--num-agents` theo `s̄`: nếu `s̄≈0.7` thì chuỗi 14 hop tắt (`0.7^14≈0.007`) và
> đuôi vô nghĩa. Llama (s̄ cao) n=15; DeepSeek n=8–10.

**Đọc kết quả:** nếu ρ(depth,error) và slope trên frontier model cùng dấu/hình với qwen
(hoặc phẳng khi transports) → diagnostic tổng quát hoá, không chỉ đúng trên 7B. Đóng R3 W3.

---

## T2.5 — Thêm 1 defence learned/semantic (nâng T0.7 từ "scope" → "coverage", đóng R2 W3)

**Vì sao:** defence landscape hiện chỉ có literal-DLP (redaction) + paraphrase — R2 nói
"narrow, one trivially bypassable". Framework có sẵn `DefenseType.DETECTION` và
`DefenseType.HOP_ISOLATION`.

**✅ Code đã sửa sẵn — chỉ chạy lệnh.** `replicate_frontier.py` giờ nhận flag
**`--defenses`** với giá trị trong `{none,redact,detection,hopiso}`. Chạy chain cell
cho từng defence ở n cao trên model susceptible (Llama):

```powershell
python scripts\replicate_frontier.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --fresh-artifact --only-chain-defenses `
  --defenses none,redact,detection,hopiso `
  --out experiments\results\defense_landscape_llama_n200
```

> `--only-chain-defenses` = chạy cell chain cho từng defence, **bỏ** obfuscation.
> Kết quả ghi `chain_none`, `chain_redact`, `chain_detection`, `chain_hopiso`.

**Đọc kết quả:** so `asr`/`surv` giữa 4 defence. Nếu `detection`/`hopiso` giảm ASR ở
chỗ `redact` thua → defence landscape rộng hơn 2 defence → đóng R2 W3.

---

## T2.6 — Tăng n các ô thứ cấp lên ~200 (đóng R3 W1, R2 W2, R4 W2)

**Vì sao:** đa số ô n=30–40 (MDE≈0.26) → các câu "transportability holds"/"consistent"
chỉ là **non-rejection**, không phải equivalence thật. Tăng n=200 giảm MDE→~0.11, biến
caveat power thành kết quả.

```powershell
# DeepSeek transport ở n=200 (ô đang nói "holds" chỉ với n=40):
python scripts\replicate_frontier.py --backend bedrock `
  --model deepseek.v3.2 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_deepseek_n200

# Các model khác trong Table 1 (Nova, qwen-local) nếu muốn powered toàn bảng:
python scripts\replicate_frontier.py --backend bedrock `
  --model amazon.nova-pro-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_nova_n200
```

**Đọc kết quả:** với MDE≈0.11, nếu Δ vẫn không khác 0 → **equivalence có power** (không
chỉ "không phân biệt được"). Cập nhật §5.2 đổi "non-rejection at MDE≈0.26" thành
"equivalence at MDE≈0.11". Đóng R3 W1.

---

## Sau khi chạy — cập nhật bài & verify (0 API)

1. **Regen bảng/hình + audit số:**
   ```powershell
   python scripts\make_figures.py --strict      # vẽ lại Fig, kiểm đè chữ
   python scripts\audit_numbers.py --md          # AUDIT_TABLE.md: số mới ↔ results.json
   python scripts\appendix_stats.py              # BH + cluster nếu ô mới vào Phụ lục A
   ```
2. **Đưa số vào `.tex`** (thủ công, ngắn gọn) — **⚠️ GIỮ 8 TRANG:** trang 8 đang kịch
   trần. Mỗi câu thêm phải **nén bù** ở chỗ khác. Sau mỗi lần sửa, build 3-pass và
   kiểm §8 + Ethics + Artifact vẫn trọn trang 8:
   ```powershell
   cd paper
   $mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
   & "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
   & "$mk\bibtex.exe"   contagion_aamas2027
   & "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
   & "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex
   # §8 phải ở trang 8:
   Select-String -Path contagion_aamas2027.aux -Pattern 'newlabel\{sec:conclusion\}'
   # Artifact phải trọn trang 8 (kiểm cả nội dung cuối đoạn, không chỉ tiêu đề):
   & "$mk\mgs.exe" -q -dNOPAUSE -dBATCH "-dFirstPage=9" "-dLastPage=9" `
     -sDEVICE=txtwrite "-sOutputFile=_c9.txt" contagion_aamas2027.pdf
   Select-String -Path _c9.txt -Pattern 'manifest|reproducibility tiers'   # phải KHÔNG khớp
   Remove-Item _c9.txt
   cd ..
   ```
   > Kết quả Tier 2 nhiều khả năng vào **Appendix** (sau references, không tính 8 trang)
   > là an toàn nhất — thêm câu 1 dòng ở thân trỏ tới appendix thay vì nhồi số vào §5.
3. **Chạy lại test + check paper:**
   ```powershell
   python -m pytest tests -q
   python scripts\check_paper.py paper\contagion_aamas2027.tex --bib paper\refs.bib
   ```

---

## Thứ tự ưu tiên (điểm/công)

| Ưu tiên | Việc | Đóng | Ghi chú chạy |
|---|---|---|---|
| 1 | **T2.6** DeepSeek n=200 | R3 W1, R4 W2 | Chỉ chạy lệnh, không sửa code — dễ nhất, nâng ngay |
| 2 | **T2.3** cyclic thứ 2 | R1 W2, R4 W2 | Chỉ chạy lệnh; có `cyclic_design_rule.py` phân tích sẵn |
| 3 | **T2.4** depth frontier | R3 W3, R1 W2 | Chỉ chạy lệnh; `depth_trend.py` phân tích sẵn |
| 4 | **T2.1** đa payload | R2 W1, R4 W2 | Chỉ chạy lệnh (`--marker`) |
| 5 | **T2.2** adaptive attacker | R2 W1, R2 Q3 | Chỉ chạy lệnh (`--adaptive-obf`) |
| 6 | **T2.5** detector mới | R2 W3 | Chỉ chạy lệnh (`--defenses ...,detection,hopiso`) |

**Chốt:** **cả 6 mục T2.1–T2.6 giờ chỉ cần chạy lệnh** — code đã sửa sẵn (`--marker`,
`--adaptive-obf`, `--defenses` đã thêm vào `replicate_frontier.py` + `content_form_probe.py`,
test mock 0-API pass, 78/78 pytest pass). Thứ tự nâng điểm nhanh: T2.6 → T2.3 → T2.4 →
T2.1 → T2.2 → T2.5. Sau mỗi mục, đưa số vào **Appendix** (không phá 8 trang) + build
kiểm. Đủ 6 mục → R2 5→6, R4 4→5, R1/R3 tiến tới 7, decision Conditional Accept →
**Accept / hướng Oral**.
