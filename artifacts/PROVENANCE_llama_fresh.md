# PROVENANCE — Llama "fresh" replicate: hai lần chạy, chọn lần nào và vì sao

> **Mục đích.** Reviewer 3 (W3, Q1) yêu cầu nói rõ **hàng nào của Table 1 sinh bởi
> protocol nào**, và đã bị chặn một lần vì nhãn `†` không kiểm chứng được. File này là
> bản ghi để bất kỳ ai mở artifact cũng **tự kiểm được**: có **HAI** replicate
> fresh-artefact cho Llama chain-none, bài chỉ trích **một**, và đây là lý do.
>
> Cập nhật: 2026-10-09. Liên quan: `REPRODUCE.md` §3.1, `paper/contagion_aamas2027.tex`
> Table 1 (`tab:cross`), Table 2 (`tab:transport`), Table 3 (`tab:ablation`),
> Appendix A (`tab:bh`).

## 1. Ba lần chạy Llama chain-none (chain n=4, 40 natural runs, 30 per-edge, T=0.7)

| Thư mục | Artefact | ASR | cạnh yếu `a1→a2` | $\prod_i s_i$ | $\Delta$ | Bài dùng ở đâu |
|---|---|---|---|---|---|---|
| `frontier_llama3-3-70b` | **fixed** | 0.800 | 0.167 | 0.167 | **+0.633** | hàng **fixed** của `tab:ablation` (bằng chứng bài tự rút lại một claim) |
| `frontier_llama3-3-70b_iso` | **fresh** | 0.850 | 0.233 | 0.233 | **+0.617** | hàng **fresh †** của `tab:cross`, `tab:transport`, `tab:ablation`; rank-1 REJECT của `tab:bh` |
| `_unused_frontier_llama3-3-70b_fresh_replicate2` | **fresh** | 0.925 | 0.300 | 0.300 | **+0.625** | **không trích trong bài** (xem §3) |

## 2. Vì sao thư mục fresh lại tên `_iso`

`_iso` là tên **lịch sử** (nó bắt đầu như một lần chạy isolated-protocol rồi được
dùng cho fresh). Nội dung của nó **là fresh-artefact**: `extra.per_edge_fresh_artifact`
đã bật, và nó là **thư mục duy nhất** có `survival_natural` cho cả ba cạnh — điều kiện
bắt buộc cho phân tích transportability của Table 2.

Đổi tên thư mục sẽ phải sửa nhiều tham chiếu trong repo, nên nhóm **giữ tên `_iso`** và
ghi rõ ý nghĩa ở đây thay vì đổi tên. Đây là lựa chọn về chi phí, không phải về số liệu.

## 3. Vì sao bài chọn 0.850 (fresh #1) chứ không phải 0.925 (fresh #2)

**Lý do chính:** `_iso` (fresh #1) là bản **duy nhất** lưu `survival_natural` cho từng
cạnh. Table 2 (`tab:transport`) cần `s^nat` per-edge để so với `s^ctrl`, và
`frontier_llama3-3-70b_fresh_replicate2` **không có** trường đó ⇒ không dùng được cho
kết quả trung tâm. Dùng cùng một thư mục cho mọi bảng giữ tính nhất quán nội tại.

**Hệ quả cần biết (và chúng tôi không giấu):** 0.850 là bản **bảo thủ hơn** trong hai
bản. Chọn bản kia sẽ cho ASR cao hơn (0.925) và sai số composition vẫn lớn
($\Delta = +0.625$ so với $+0.617$), nên **không kết luận nào của bài phụ thuộc vào
việc chọn bản nào**: cả hai replicate fresh đều cho $\Delta$ dương lớn, tức kết luận
super-Markov của Llama đứng vững ở cả hai.

**Bản thứ hai vẫn nằm trong artifact** (tiền tố `_` để `make_figures.py` và
`audit_numbers.py` bỏ qua — cả hai script skip thư mục bắt đầu bằng `_`), để người
kiểm tự chạy lại và thấy cùng kết luận.

## 4. Cách tự kiểm (0 API)

```powershell
# cả ba lần chạy, đọc thẳng từ results.json
python -c "
import json, pathlib
for d in ['frontier_llama3-3-70b','frontier_llama3-3-70b_iso',
          '_unused_frontier_llama3-3-70b_fresh_replicate2']:
    o = json.loads((pathlib.Path('experiments/results')/d/'results.json').read_text(encoding='utf-8'))
    c = o['chain_none']
    print('%-48s ASR=%.3f  per_edge=%s' % (d, c['asr'],
          ' / '.join('%.3f' % c['per_edge'][k] for k in sorted(c['per_edge']))))
"
```

Kỳ vọng: `0.800 (fixed)`, `0.850 (fresh #1)`, `0.925 (fresh #2)` — khớp §1 ở trên.

## 5. Điều KHÔNG kiểm chứng được (nói thẳng)

- Cờ `fresh` **không** được lưu trong bất kỳ `results.json` nào (xem
  `artifacts/MANIFEST.json` → `protocol_evidence`). Bằng chứng duy nhất là **lệnh chạy**
  ghi ở `REPRODUCE.md` §B1/B2 và bản ghi này. Đây là khoảng trống provenance của
  artifact, không phải suy đoán.
- `markov_formal` trong các file này không lưu `p_value`; giá trị $p$ cho Appendix A
  được `scripts/appendix_stats.py` tính lại từ `p_value` của chính thư mục đó.
