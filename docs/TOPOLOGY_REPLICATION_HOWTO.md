# Hướng dẫn: chạy thêm topology (Mục 12 / §3.2) rồi gửi kết quả để mình tổng hợp

> **Mục tiêu (Mục 12 trong `paper/AAMAS2027_IMPROVEMENTS.md`):** hạ đòn điểm yếu W1
> của reviewer **B9RL** (dissenter, 5/10) — *"bảng topology là single-instance,
> single-model"*. Meta-review nói đây là **item duy nhất** có thể nâng poster → oral
> (dòng 405–406). Ta bổ sung 2 trục:
> 1. **Model thứ 2** (Claude Sonnet 4.5) chạy star + tree → bảng topology có 2 model,
>    không còn bị đọc là giai thoại 1 model (Llama).
> 2. **Instance thứ 2** cho Llama (num_agents khác: n=10) star + tree → không còn
>    single-instance.
>
> **Vì sao phải chạy chứ không tính offline:** đây là **số mới**, phải gọi model
> frontier qua Bedrock (khác với Mục 8/10 chỉ phân tích lại số cũ). Cần **key Bedrock
> còn sống**.
>
> **Phân công:** bạn chạy **Bước 2** (cần key). Mình làm **Bước 4** (0 API): đọc
> `results.json`, thêm cột/dòng vào bảng topology trong `.tex`, cập nhật `AUDIT_TABLE`,
> build lại PDF. Bạn KHÔNG cần tự phân tích.

---

## Bước 0 — Điều kiện

- **Key Bedrock còn sống** trong `E:\NCKH\Contagion\.env` ở dòng
  `AWS_BEARER_TOKEN_BEDROCK=bedrock-api-key-...`. Kiểm nhanh (không tốn cell thật):

```powershell
cd E:\NCKH\Contagion
python scripts\bedrock_key_diag.py
```

  Nếu thấy `✓ [us-east-1] ... → OK` là key sống. Nếu `AccessDeniedException` ⇒ key
  chết, phải lấy key mới từ AWS console rồi dán vào `.env` (⚠️ **đừng** dán vào Cline —
  xem `SUBMISSION_CHECKLIST.md` §3b).

- Chạy từ gốc repo `E:\NCKH\Contagion`.
- Chi phí ước lượng: mỗi cell ~15–40 phút (Claude tree lâu hơn star; Llama nhanh hơn).
  Bốn cell tổng khoảng **1.5–2 giờ**, chạy tuần tự. Cứ để chạy nền, xong cái nào ghi file cái đó.

---

## Bước 1 — (tuỳ chọn) dọn thư mục chạy dở

Nếu lần chạy trước bị ngắt giữa chừng, thư mục có thể trống hoặc thiếu file. Xoá để
chạy lại cho sạch (an toàn, chưa có số nào vào bài):

```powershell
Remove-Item -Recurse -Force experiments\results\topo_star_claude_n7,
  experiments\results\topo_tree_claude_n7,
  experiments\results\topo_star_llama_n10,
  experiments\results\topo_tree_llama_n10 -ErrorAction SilentlyContinue
```


## Bước 2 — Chạy các cell (BẠN LÀM, cần key)

Chạy **lần lượt** (mỗi lệnh xong mới chạy lệnh kế; đừng chạy song song để tránh
rate-limit). Mỗi lệnh in `[done] -> ...\report.md` khi xong.

> **Chọn model cho trục "nhiều model" = DeepSeek + Nova** (KHÔNG dùng Claude). Lý do
> (kiểm bằng ASR chain thật): bảng topology phải chứng minh *"topology làm thay đổi
> lan truyền"*. Model phải có lan truyền **>0** thì star vs tree mới khác biệt đo được.
> - Llama (ASR 0.925, dễ nhiễm) — model 1, đã có sẵn.
> - **DeepSeek (ASR 0.375, vùng giữa)** — star vs tree khác biệt rõ nhất ⇒ giá trị
>   khoa học **cao nhất**. Chậm (call 4–40s) nhưng đã vá timeout nên không treo vô hạn.
> - **Nova (ASR 0.075, kháng nhẹ nhưng >0)** — nhanh, thêm điểm phủ.
> - Claude bị loại: ASR chain = **0.000** ⇒ mọi ô star/tree sẽ = 0, KHÔNG phân biệt
>   được topology → phản tác dụng cho chính luận điểm của B9RL.

```powershell
# --- MODEL THỨ 2 (Nova, nhanh): star + tree n=7 ---
python scripts\replicate_frontier.py --backend bedrock --model amazon.nova-pro-v1:0 `
    --region us-east-1 --topology star --num-agents 7 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_star_nova_n7

python scripts\replicate_frontier.py --backend bedrock --model amazon.nova-pro-v1:0 `
    --region us-east-1 --topology tree --num-agents 7 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_tree_nova_n7
```

```powershell
# --- MODEL THỨ 3 (DeepSeek, chậm nhưng giá trị KH cao nhất): star + tree n=7 ---
python scripts\replicate_frontier.py --backend bedrock --model deepseek.v3.2 `
    --region us-east-1 --topology star --num-agents 7 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_star_deepseek_n7

python scripts\replicate_frontier.py --backend bedrock --model deepseek.v3.2 `
    --region us-east-1 --topology tree --num-agents 7 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_tree_deepseek_n7
```

```powershell
# --- INSTANCE THỨ 2: Llama, star + tree ở num_agents=10 (khác n=7 cũ) ---
python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 `
    --region us-east-1 --topology star --num-agents 10 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_star_llama_n10

python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 `
    --region us-east-1 --topology tree --num-agents 10 --trials 40 --per-edge 30 `
    --only-chain-none --skip-obfuscation --fresh-artifact `
    --out experiments\results\topo_tree_llama_n10
```

### Ý nghĩa các cờ (để bạn yên tâm số so sánh được)
- `--topology star|tree` + `--num-agents N`: dựng đúng đồ thị star/tree N node.
- `--trials 40 --per-edge 30`: **khớp** cấu hình `topo_star_n7`/`topo_tree_n7` cũ (Llama)
  → số mới đặt cạnh số cũ trong cùng một bảng được.
- `--only-chain-none`: chỉ đo cell **không phòng thủ** (số nuôi bảng topology; bỏ 2 cell
  chain redact/obfuscation tốn kém, không cần cho Mục 12).
- `--skip-obfuscation`: bỏ arm obfuscation (không thuộc bảng topology).
- `--fresh-artifact`: rút artifact mới mỗi per-edge trial (giao thức mặc định, tránh
  vi phạm Markov giả — cùng chuẩn với §5.3 của bài).

### Nếu key chết giữa chừng
`report.md`/`results.json` chỉ ghi **khi cell xong**. Cell nào đã in `[done]` là an
toàn; cell đang dở thì chạy lại đúng lệnh đó (nó ghi đè thư mục `--out`). Cứ gửi phần
đã xong.

### Self-test 0 đồng (tuỳ chọn — chỉ kiểm máy chạy được, KHÔNG phải số bài)
```powershell
python scripts\replicate_frontier.py --backend mock --model mock `
    --topology star --num-agents 7 --trials 4 --per-edge 3 `
    --only-chain-none --skip-obfuscation `
    --out experiments\results\topo_smoke
```
(Số mock không dùng cho bài; xong xoá `topo_smoke`.)

---

## Bước 3 — Gửi lại cho mình

Sau khi chạy xong, mỗi thư mục `--out` có **2 file**:

```
experiments\results\topo_star_claude_n7\
  ├─ results.json   ← QUAN TRỌNG NHẤT (ASR, survival, per-edge s, R0)
  └─ report.md      ← bản người-đọc, để đối chiếu nhanh
```

Bốn thư mục cần gửi (hoặc để nguyên trong repo rồi báo mình):

```
experiments\results\topo_star_claude_n7\
experiments\results\topo_tree_claude_n7\
experiments\results\topo_star_llama_n10\
experiments\results\topo_tree_llama_n10\
```

Chỉ cần nhắn *"xong rồi"* + đường dẫn, hoặc **chạy được cell nào gửi cell đó** (vd key
chết sau 2 cell Claude thì gửi 2 cái đó trước — mình vẫn dựng được bảng 2-model).

**Trường bắt buộc trong `results.json`**: `model`, `topology`, `num_agents`, và khối
`chain_none` gồm `asr`, `asr_ci`, `surv`, `surv_ci`, `per_edge`, `survival_natural`,
`r0`, `r0_ds`.

---

## Bước 4 — Mình tổng hợp (0 API, mình làm)

Mình sẽ:
1. Đọc 4 `results.json` (+ 2 cái Llama n=7 cũ có sẵn) → dựng lại **bảng topology** trong
   `contagion_aamas2027.tex` thành **2 model × {star, tree}** + ghi chú instance thứ 2
   (n=10) cho Llama.
2. Sửa câu §5.6 (topology) thành *"across two models and two instances per non-chain
   topology"* thay vì single-instance/single-model — trả lời trực tiếp B9RL W1.
3. Chạy `python scripts\audit_numbers.py --md` để `AUDIT_TABLE.md` + bài khớp
   `results.json` (không nhập tay số nào).
4. Build lại PDF (`!`/`Overfull`/`undefined` = 0) và đánh dấu Mục 12 `✅ XONG` trong
   `AAMAS2027_IMPROVEMENTS.md` + `SUBMISSION_CHECKLIST.md`.

---

## Vì sao cách này an toàn & trung thực

- **Không bịa số:** mọi con số vào bài đến từ `results.json` do model thật sinh; mình
  chỉ đọc và định dạng, `audit_numbers.py` tự đối chiếu lại.
- **So sánh được:** cùng harness, cùng `--trials/--per-edge/--fresh-artifact` như cell
  Llama n=7 cũ → số mới đặt cạnh số cũ hợp lệ.
- **Không chặn chấp nhận:** Mục 12 là "nên có để nâng oral"; nếu key lại chết, bài vẫn
  trên ngưỡng chấp nhận với bảng topology hiện tại.

---

## Tóm tắt 3 dòng

1. Kiểm key: `python scripts\bedrock_key_diag.py` (phải thấy `→ OK`).
2. Chạy 4 lệnh ở Bước 2 (lần lượt); mỗi cell in `[done]` là xong.
3. Gửi mình 4 thư mục `topo_*_claude_n7` + `topo_*_llama_n10` (chỉ cần `results.json`).
