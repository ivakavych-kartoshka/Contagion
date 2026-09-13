# Hướng dẫn: chạy lại **cạnh yếu Llama ở n lớn** (Mục 11 / §3.1) rồi gửi kết quả để mình tổng hợp

> **Mục tiêu (Mục 11 trong `paper/AAMAS2027_IMPROVEMENTS.md`, dòng 140–145):** hạ
> đòn của reviewer **M4KZ + QT2W** — *"MDE ở n=40 là 0.26; nhiều verdict 'null' là
> underpowered"*. Ta chạy lại **đúng cạnh yếu đã biết** (Llama, transport-failure
> 3.75×) ở **cỡ mẫu lớn hơn nhiều** để MDE tụt xuống dưới độ lệch thật → biến cell
> transport-failure từ *"proof of existence"* thành **phát hiện dương tính thật**.
> Đây là việc [CẦN KEY] có **tỉ lệ lợi ích/chi phí cao nhất** trong nhóm còn lại.
>
> **Cạnh yếu là cạnh nào (đã kiểm trong repo, KHÔNG đoán):** trong
> `experiments/results/isolation_validity/report.md` (dòng 30), Llama chain n=4 có
> cạnh **`agent_1 -> agent_2`** với `s^controlled = 0.233` vs `s^natural = 0.875`
> ⇒ **3.75×** — chính là *"3.75× on one edge"* trong abstract. MDE hiện tại
> `= 0.2625` (từ `experiments/results/markov_formal/table.json`) chính là *"MDE 0.26"*
> mà reviewer chê. Cell chain gốc để so là **`topo_chain_n7`** (Llama, chain n=7,
> trials=40, per-edge=30).
>
> **Vì sao phải chạy chứ không tính offline:** đây là **số mới** (cỡ mẫu lớn hơn),
> phải gọi lại Llama qua Bedrock. Cần **key Bedrock còn sống**.
>
> **Phân công:** bạn chạy **Bước 2** (cần key). Mình làm **Bước 4** (0 API): đọc
> `results.json`, cập nhật MDE/p-value mới + câu §5.3/§5.6, chạy `audit_numbers.py`,
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
- **Chạy sau khi cell topology (`topo_tree_llama_n10`) đã in `[done]`.** Đừng chạy song
  song với nó để tránh rate-limit trên cùng một key.
- Chi phí ước lượng: n lớn ⇒ nhiều call hơn hẳn cell cũ. Đặt **1 cell n=200** khoảng
  **40–90 phút** (Llama nhanh, nhưng số call ≈ `trials × (n−1)` cho natural +
  `per_edge × (n−1)` cho per-edge). Cứ để chạy nền, xong ghi file.

---

## Bước 1 — (tuỳ chọn) dọn thư mục chạy dở

Nếu lần trước bị ngắt giữa chừng, xoá để chạy lại cho sạch (an toàn, chưa có số nào
vào bài):

```powershell
Remove-Item -Recurse -Force `
  experiments\results\weakedge_llama_n200 `
  experiments\results\depth_curve_llama_n15 -ErrorAction SilentlyContinue
```

---

## Bước 2 — Chạy (BẠN LÀM, cần key) — **CHỈ 1 LỆNH**

Cỡ mẫu `200/200` là **con số tối ưu** (không chọn bừa): chạy hàm calibration
`recommended_trials_for_mde(s̄=0.6, hops=3, target_mde=0.10, per_edge_ratio=1.0)` của
chính nhóm cho thấy **n=200 là ngưỡng nhỏ nhất** đưa MDE từ 0.26 xuống **≤0.10** (mean
MDE ≈ 0.0996) — đúng "mức paper muốn loại trừ" (`scripts\validate_methods.py`). Trên
cạnh yếu độ lệch thật ~0.62 ≫ 0.10 ⇒ verdict chuyển từ "null" thành **reject = phát
hiện dương tính thật**. Chạy nhiều hơn (300/400) chỉ tốn call, không cần cho bài.

```powershell
python scripts\replicate_frontier.py --backend bedrock --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 --topology chain --num-agents 4 --trials 200 --per-edge 200 --only-chain-none --skip-obfuscation --fresh-artifact --out experiments\results\weakedge_llama_n200
```

In `[done] -> ...\report.md` là xong. File cần cho mình: **`results.json`** (chứa
`chain_none.markov_formal` với `p_value` + `mde` mới ~0.10 — con số hạ đòn reviewer).

> Nếu quota/thời gian căng: hạ xuống `--trials 150 --per-edge 150` (MDE ~0.12, vẫn tụt
> rõ so với 0.26). Miễn là **báo mình đúng con số `--trials/--per-edge` đã dùng**.


---

## Ý nghĩa các cờ (để bạn yên tâm số so sánh được)

- `--topology chain --num-agents 4`: **giữ nguyên** chain n=4 như cell
  isolation-validity cũ → cạnh `agent_1->agent_2` vẫn là cùng một cạnh, số n=200 đặt
  cạnh số n=40 cũ hợp lệ.
- `--trials 200 --per-edge 200`: **cỡ mẫu lớn** — đây là toàn bộ mục đích của Mục 11
  (nâng power ⇒ hạ MDE). Cell cũ là `40 / 30`.
- `--only-chain-none`: chỉ đo cell **không phòng thủ** (đúng cell cho claim
  transport-failure; bỏ redact/obfuscation không liên quan).
- `--skip-obfuscation`: bỏ arm obfuscation.
- `--fresh-artifact`: rút artifact compromised mới mỗi per-edge trial (giao thức mặc
  định §5.3, tránh vi phạm Markov giả — cùng chuẩn với các cell fresh khác).

### Nếu key chết giữa chừng

`report.md`/`results.json` chỉ ghi **khi cell xong**. Cell nào đã in `[done]` là an
toàn; cell đang dở thì chạy lại đúng lệnh đó (nó ghi đè thư mục `--out`). Cứ gửi phần
đã xong — chỉ cần **Đường A** là mình dựng được câu trả lời cho M4KZ/QT2W.

---

## Bước 3 — Gửi lại cho mình

Sau khi chạy xong, thư mục `--out` có **2 file**:

```
experiments\results\weakedge_llama_n200\
  ├─ results.json   ← QUAN TRỌNG NHẤT (chain_none.markov_formal.p_value + .mde mới)
  └─ report.md      ← bản người-đọc, để đối chiếu nhanh
```

Chỉ cần nhắn *"xong rồi"* + đường dẫn, **kèm con số `--trials/--per-edge` bạn đã dùng**
(nếu bạn hạ khỏi 200/200). Nếu chạy cả Đường B thì gửi thêm
`experiments\results\depth_curve_llama_n15\results.json`.

**Trường bắt buộc trong `results.json`** (Đường A): `model`, `topology`, `num_agents`,
và khối `chain_none` gồm `asr`, `asr_ci`, `surv`, `surv_ci`, `per_edge`,
`survival_natural`, `markov_formal` (đặc biệt `p_value` + `mde`), `r0`, `r0_ds`.

---

## Bước 4 — Mình tổng hợp (0 API, mình làm)

Mình sẽ:
1. Đọc `weakedge_llama_n200\results.json` → lấy `mde` mới (kỳ vọng ≪ 0.26) và
   `p_value` mới cho cạnh yếu.
2. Cập nhật §5.3/§5.6 + `tab:bh`: đổi câu *"underpowered / proof of existence"* thành
   **phát hiện dương tính** với MDE mới, nêu rõ cỡ mẫu n=200.
3. Chạy `python scripts\audit_numbers.py --md` để `AUDIT_TABLE.md` + bài khớp
   `results.json` (không nhập tay số nào).
4. Build lại PDF (`!`/`Overfull`/`undefined` = 0), đánh dấu Mục 11 `✅ XONG` trong
   `AAMAS2027_IMPROVEMENTS.md` + `SUBMISSION_CHECKLIST.md`.

---

## Vì sao cách này an toàn & trung thực

- **Không bịa số:** mọi con số vào bài đến từ `results.json` do Llama thật sinh; mình
  chỉ đọc và định dạng, `audit_numbers.py` tự đối chiếu lại.
- **So sánh được:** cùng harness, cùng chain n=4, cùng `--fresh-artifact` như cell
  isolation-validity cũ → chỉ khác cỡ mẫu; số n=200 đặt cạnh số n=40 hợp lệ.
- **Không chặn chấp nhận:** Mục 11 là *"nên có để nâng oral"*; nếu key lại chết, bài
  vẫn trên ngưỡng chấp nhận với kết quả hiện tại (đã ghi rõ MDE ở n=40).

---

## Tóm tắt 3 dòng

1. Kiểm key: `python scripts\bedrock_key_diag.py` (phải thấy `→ OK`).
2. Chạy **Đường A** ở Bước 2 (chain n=4, `--trials 200 --per-edge 200`); in `[done]`
   là xong. (Đường B tuỳ chọn.)
3. Gửi mình `experiments\results\weakedge_llama_n200\results.json` + báo con số
   `--trials/--per-edge` đã dùng.
