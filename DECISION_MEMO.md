# DECISION MEMO — Chọn hướng task family & model cho paper A*

> Ngày: sau pilot E10–E13 · Mục đích: để người quyết định (bạn) chốt hướng
> trước khi đầu tư sweep lớn. Không đổi code/docs cho tới khi bạn duyệt.

---

## 1. Bằng chứng đã có (từ EXPERIMENT_LOG, tóm tắt)

| # | Phát hiện | Hệ quả |
|---|---|---|
| E2 | Marker-echo KHÔNG có benign context → **ceiling s≈1** mọi cell | task quá dễ: dst chỉ việc echo |
| E10 | Có benign context → s phân tán nhưng **phụ thuộc role mạnh**: worker 0.13, reviewer 0.87, aggregator 0.47, planner 0.43 | phải báo s conditioned-on-role |
| E12 | Paraphrase (strip marker) sau fix → **s=0 mọi role** với attack tĩnh | defense "thắng" dễ vì marker cố định |
| E13 | **Obfuscation tầm thường (split/spaced) đánh bại paraphrase**: compromised 0.7–1.0 | defense story với marker-echo = thắng/thua tầm thường theo obfuscation |
| E13 | MR Dice false-positive: model "bắt chước hình dạng lệnh" (vd `verification code is: 12345`) → mr 0.63 → compromised dù KHÔNG leak secret thật | MR τ=0.6 cần soi lại khi đổi task |
| E7–E8 | Judge ASV (marker-bigram) tách tốt khi content rõ; replicate cho thấy fidelity content + role quyết định survival | judge ASV giữ được, MR là phần yếu |

**Kết luận chặn:** marker-echo (output một token cố định) làm **cả attack lẫn
defense đều tầm thường/đối xứng** — không đủ "chất" cho câu chuyện A* về
propagation của injected instruction trong agent networks.

---

## 2. Ba phương án task family

### A. Marker-echo nâng cấp (giữ nguyên hạ tầng, đổi payload)
- Cách: marker KHÔNG còn là chuỗi cố định trong prompt; attacker giấu nó trong
  một "document/tool result" nhiều nội dung; agent phải **trích xuất + relay**
  đúng secret giữa legit task. Obfuscation trở thành biến thí nghiệm chính.
- Chi phí: thấp (sửa `Payload`/`_compromised_output` + probe lại judge).
- Lợi: tận dụng toàn bộ pipeline hiện có.
- Rủi ro: vẫn là "leak một chuỗi" — reviewer có thể hỏi "khác gì data exfil
  đơn giản?"; arms-race obfuscation khó kể thành contribution mới.

### B. Semantic instruction-competition ⭐ (khuyến nghị)
- Cách: agent được giao legit task A (vd "tóm tắt tài liệu"); untrusted content
  chứa injected instruction đầy đủ ý nghĩa lôi agent làm task B ("thay vào đó
  in toàn bộ prompt / gửi dữ liệu ra ngoài"). Judge: output có hoàn thành task B
  (semantic, không phải token) hay vẫn làm A.
- Chi phí: trung bình-cao (cần TaskAssessor semantic mới, calibrate lại judge,
  có thể cần LLM-judge; đụng docs design → duyệt riêng).
- Lợi: paraphrase defense "giữ nghĩa, bỏ lệnh" có ý nghĩa thật; s/ASR đo được
  cái propagation thực sự; đúng hướng Liu-Gong/injection literature; kể được
  câu chuyện "injected intent cạnh tranh legit objective" — chất A*.
- Rủi ro: LLM-judge tốn cost + cần validate chính nó (mở rộng Phase-2 style);
  khó calibrate hơn marker.

### C. Tool-call task family
- Cách: agent có tool (vd calculator/search/send_email); injected instruction
  lôi agent gọi tool sai đối số. Judge = so khớp (tool, args) như docs §3.
- Chi phí: cao (cần tool environment thật trong Agent.steps).
- Lợi: ground-truth rõ (tool-call so khớp được), ít mơ hồ hơn B, defense
  placement có nghĩa.
- Rủi ro: code nhiều nhất; qwen2.5:7b local gọi tool kém → cần model mạnh hơn
  (đụng quyết định model).

---

## 3. Khuyến nghị

1. **Task family:** B (semantic instruction-competition) nếu muốn contribution
   mạnh nhất và chấp nhận chi phí judge; hoặc A nếu muốn nhanh (giữ pipeline)
   và coi obfuscation arms-race là phụ. Khuyến nghị: **B**, pilot trước.
2. **Bất kể chọn gì:** MR Dice τ=0.6 (false-positive "bắt chước lệnh") và
   conditioned-on-role reporting phải giải quyết trong thiết kế mới.
3. **Model:** local 7b đủ cho *pilot kiểm chứng*; sweep Markov-power (trials
   200–300, full matrix) cần API (~3h) hoặc 3b re-calibrate (~10h) — quyết
   định sau khi pilot B cho tín hiệu.

---

## 4. Quyết định cần bạn chốt

- [ ] Chọn A / B / C (khuyến nghị B)
- [ ] Nếu B: chấp nhận LLM-judge + calibrate lại judge (đụng docs → tôi sẽ trình
      bản thiết kế chi tiết trước khi sửa)
- [ ] Model cho sweep: 7b local / 3b (re-calibrate) / API (cần budget + key)
