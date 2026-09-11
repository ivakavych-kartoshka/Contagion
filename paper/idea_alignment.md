# Đối chiếu `idea.md` ↔ hướng đi hiện tại

> Người kiểm tra: agent · Ngày: 2026-09-11
> Nguồn: `paper/idea.md` (bản gốc của bạn) vs code + thí nghiệm thật trong repo
> (`EXPERIMENT_LOG.md` E1–E29) vs bản thảo `paper/contagion_aamas2027.tex`.

---

## 1. Kết luận ngắn

**Hướng đi ĐÚNG với idea ở phần lõi, và ở một điểm quan trọng thì đã VƯỢT idea.**
Nhưng có **10 khoảng trống** so với những gì `idea.md` tự hứa; trong đó **2 khoảng
trống nghiêm trọng** vì chúng là *contribution được ghi rõ trong idea* mà chưa làm.

| | |
|---|---|
| ✅ **Khớp** | định nghĩa `s`, ASV/MR, ASR end-to-end, `R₀`, threat model black-box/1 entry point, và **kiểm định giả định Markov** |
| 🎯 **Vượt idea** | `idea.md` tự ghi *"Main risk: whether the epidemiological formalism is predictive rather than merely descriptive"* — ta đã **trả lời câu đó bằng thực nghiệm** (mục 3 dưới) |
| ⛔ **2 lỗ hổng nghiêm trọng** | (a) **defense-placement study** (idea ghi là contribution #4) **chưa làm**; (b) các **biến thể re-injection** (independent vs colluding, static vs adaptive) có code nhưng **chưa chạy thí nghiệm nào** |
| ⚠️ **Lệch** | `idea.md` ghi venue chính là **USENIX Security**, nhưng bạn đang dùng template **AAMAS 2027** → phải chốt, vì framing khác nhau |

---

## 2. Bảng đối chiếu chi tiết

Ký hiệu: ✅ đã làm & có số thật · 🟡 làm một phần · ❌ chưa làm · 💤 code có nhưng chưa chạy

### 2.1 System & threat model

| `idea.md` hứa | Thực tế | |
|---|---|---|
| Roles: planner, workers, **tool-users**, aggregator | planner / worker / reviewer / aggregator — **không có role tool-user** | 🟡 |
| Topology: star, chain, tree, **mesh, debate** | chain ✅, star ✅ (n=7 đã đo), tree 🔄 đang chạy; **mesh/debate chưa implement** (`TopologyType` mới có 3) | 🟡 |
| **3–50 agents** | đã đo n=4, n=5, n=7. **Chưa có cell ≥10** | ❌ |
| Static vs **adaptive** re-injection | `ReInjectionMode` có NONE/INDEPENDENT/COLLUDING; **mọi thí nghiệm dùng NONE** | 💤 |
| Independent vs **colluding** compromised agents | như trên | 💤 |
| Entry channel là field duy nhất attacker kiểm soát | ✅ đúng như code | ✅ |
| Out of scope: multi-entry, white-box, side channel | ✅ tuân thủ | ✅ |

### 2.2 Core idea & contributions

| `idea.md` hứa | Thực tế | |
|---|---|---|
| Per-hop survival `s` | ✅ định nghĩa + đo bằng **2 protocol độc lập** (mạnh hơn idea: idea chỉ nói "controlled trials") | ✅ |
| End-to-end propagation probability | ✅ ASR + Wilson CI | ✅ |
| `R₀` theo topology / role / **content-freedom** / defenses | topology 🟡 (chain+star, tree đang chạy), **role ✅ (phát hiện mạnh: 0.13 vs 0.87)**, content-freedom 💤 (`FieldContentFreedom` có trong code, **chưa từng biến thiên**), defenses 🟡 (2/5) | 🟡 |
| Giả thuyết **super-spreader** (broadcaster, summarizer) | role set không có broadcaster/summarizer; ta đo **receiver-role** dependence, chưa đo amplification theo out-degree | 🟡 |
| **Defense-placement study** ("which single node to harden") | ❌ **CHƯA LÀM** — chỉ đo defense ở mức toàn mạng | ❌ |
| **Proof obligation** `R₀ < 1 ⇒ subcritical` | ❌ chưa hình thức hoá; ta mới có **thực nghiệm** `R₀` vs `d·s̄` (và chỉ ra nó **sai có cấu trúc** ở star) | ❌ |
| Benchmark 3–50 agents, 5 topology | 🟡 công cụ chạy được (script + 78 test) nhưng **chưa đóng gói thành artifact phát hành** | 🟡 |

### 2.3 Evaluation strategy

| `idea.md` hứa | Thực tế | |
|---|---|---|
| Open: Llama-3, Qwen2.5, **Mistral**; Proprietary: **GPT-4o**, Claude-3.5 | ✅ Llama 3.3 70B, ✅ qwen2.5:7b, ✅ Claude Sonnet 4.5, ✅ **thêm** DeepSeek V3.2 + Nova Pro; ❌ Mistral, ❌ GPT-4o | 🟡 |
| Homogeneous **và mixed backbone** | ❌ chưa có cell heterogeneous | ❌ |
| Re-injection reach; independent vs colluding; static vs adaptive | 💤 | 💤 |
| Metrics: `s`, ASV, MR, `R₀`, propagation rate, hops-to-compromise | ✅ tất cả đã tính; **hops-to-compromise chưa đưa vào paper** | ✅ |
| Utility-under-attack | ✅ đã đo (E28) — **trước đây là lỗ hổng lớn nhất, nay đã lấp** | ✅ |
| **Communication overhead, latency, token/API cost, scalability** | ❌ chưa log/đo | ❌ |
| Baselines: no-defense ✅, paraphrase ✅, **delimiter/StrUQ** 💤, **detection** 💤, **hop isolation** 💤 | 3/5 defense có code nhưng **chưa chạy trên LLM thật** | 🟡 |
| Ablations: topology 🟡, **entry-point role placement** ❌, **content-freedom** ❌, **defense placement** ❌, **homogeneous vs heterogeneous** ❌, **Markov vs history-dependent** ✅ | | 🟡 |

### 2.4 Risks & readiness

| `idea.md` | Thực tế | |
|---|---|---|
| "we test the Markov assumption directly" | ✅✅ **đã làm, và là kết quả mạnh nhất của bài** | ✅ |
| "instantiate on MetaGPT/AutoGen-style message passing, report sensitivity to emulator choices" | ❌ ta dùng emulator tự viết; **chưa instantiate MetaGPT/AutoGen** | ❌ |
| "reduced `R₀` is not secure" (chống over-claim) | ✅ paper viết rất cẩn thận, có mục Limitations 7 điểm | ✅ |
| Ethics: chỉ dùng payload có sẵn, phát hành emulated benchmark | ✅ tuân thủ | ✅ |

---

## 3. 🎯 Chỗ ta VƯỢT idea (nên nhấn trong paper)

`idea.md` ghi: *"Main risk: whether the epidemiological formalism is **predictive**
rather than merely descriptive of LLM behavior — the empirical question the
benchmark answers."*

**Ta đã trả lời câu hỏi đó, và câu trả lời là "không, không một cách đơn giản":**

1. **`ASR = ∏ sᵢ` là ĐẲNG THỨC, không phải giả định** (khi `sᵢ` đo trong chính quá
   trình lan truyền) — vì trong chain `C_i=1 ⟹ C_{i-1}=1`. Đã kiểm chứng trên LLM
   thật: `∏s^nat = 0.850` và `ASR = 0.850`. Điều này **chỉnh lại chính công thức
   trong `idea.md`** (idea viết "end-to-end success is ∏sᵢ" như thể nó hiển nhiên).
2. **Câu hỏi thực chất là `s_i^controlled == s_i^nat`?** — tức phép đo **cách ly**
   có chuyển được sang bối cảnh trong chuỗi không. Đây đúng là giả định mà
   benchmark single-hop (InjecAgent…) đang ngầm dùng khi compose.
3. **Trả lời: KHÔNG, và thất bại có hướng phụ thuộc model.** Trên Llama 3.3 70B,
   cùng một cạnh: `s^cách ly = 0.233` vs `s^trong chuỗi = 0.875` → **lệch 3.75×**.
   Trên DeepSeek V3.2 thì chuyển được.
4. **Và ta tự bắt được một artifact của chính mình**: kết quả "bác bỏ Markov"
   (`p = 0.0030`) trên DeepSeek hoá ra do per-edge protocol giữ artifact cố định;
   sửa lại thành `p = 0.630`. Đã giữ **cả hai** trong paper như một ablation.

⇒ Đây là **câu trả lời định lượng cho rủi ro số 1 mà chính `idea.md` đặt ra** —
giá trị lớn hơn nhiều so với việc chỉ "đo thêm vài topology".

**Thêm một phát hiện không có trong idea:** **hiệu ứng sàn (floor effect)** — hiệu
quả của defense **không xác định được** nếu thiếu baseline no-defense. Cùng một
defense: trên model kháng tốt, `none·plain = 0.10` nên "redact chặn 100%" chỉ vì
chỉ có 10% để bảo vệ; trên model dễ bị lừa, `none·plain = 1.00` và redact bị
obfuscation qua mặt 100%.

---

## 4. ⚠️ Lệch lớn nhất: venue

`idea.md` ghi **"Primary USENIX Security; also IEEE S&P, ACM CCS, NDSS, and NeurIPS D&B"**.
Nhưng bạn vừa đưa **template AAMAS 2027**.

Điều này **không sai** — AAMAS thực ra rất hợp (`s` và `R₀` **không định nghĩa được**
cho một agent đơn lẻ; đây là đóng góp *fundamentally multiagent*, đúng tinh thần
AAMAS). Nhưng hệ quả:

| | Security venue (USENIX/S&P) | **AAMAS** |
|---|---|---|
| Trọng tâm reviewer | threat model, attack/defense, disclosure | **cấu trúc multiagent**: topology, vai trò, lan truyền, phối hợp |
| Độ dài | thường 13–18 trang | **8 trang nội dung** + refs không giới hạn |
| Thứ được đánh giá cao | phòng thủ mạnh, phạm vi tấn công | **mô hình + phân tích + placement/coordination** |
| Hàm ý cho ta | cần thêm defense & attack variants | **cần đẩy mạnh topology + defense placement + lý thuyết `R₀`** |

⇒ Nếu chốt AAMAS: **ưu tiên đổi** — làm (1) defense placement, (2) `R₀`/branching
theory, (3) topology ở cỡ khớp nhau. Nếu chốt security venue: ưu tiên ngược lại —
thêm attack/defense variants và threat-model rigor.

**Việc cần bạn quyết:** chốt venue, rồi tôi cập nhật cả `idea.md` lẫn paper cho khớp.

---

## 5. Việc cần làm để khớp idea — xếp theo ưu tiên (giả định chốt AAMAS)

| # | Việc | Vì sao | Chi phí | Trạng thái |
|---|---|---|---|---|
| **1** | **Defense placement study**: đo `s` khi chỉ harden **một** node, tìm node tối thiểu để `R₀ < 1` | **Contribution #4 của idea, chưa làm.** Đây là đóng góp *multiagent* rõ nhất cho AAMAS | code ~2h + chạy ~1h | ❌ |
| **2** | Chạy nốt 3 defense còn lại (**delimiter / detection / hop isolation**) trên LLM thật | cần cho (1); code đã có | ~1.5h chạy | 💤 |
| **3** | **Branching-process formalization** + điều kiện `R₀ < 1` | idea gọi là "proof obligation"; AAMAS thích lý thuyết; **không tốn API** | ~1 ngày viết | ❌ |
| **4** | Xong topology ở **cùng số agent** (chain/star/tree n=7) + bảng `R₀` vs `d·s̄` | chain n=7 chạy xong là đủ; tree đang chạy | ~30 phút | 🔄 |
| **5** | **Re-injection variants**: static vs adaptive; independent vs **colluding** | chiều tấn công *multiagent* đặc trưng; code đã có | ~1.5h chạy | 💤 |
| **6** | **Content-freedom ablation** (nối InjecAgent) | idea ghi rõ; code đã có | ~1h | 💤 |
| **7** | **Entry-point role placement** ablation (entry ở worker vs planner vs aggregator) | ablation idea liệt kê; rẻ | ~1h | ❌ |
| **8** | **Heterogeneous backbone** (mỗi role một model) | idea liệt kê; rẻ | ~1h | ❌ |
| **9** | Log **cost/latency/token** mỗi cell | idea liệt kê dưới "Utility/cost"; rẻ, thêm vào report | ~1h code | ❌ |
| **10** | Scale lên ~15 agent (1–2 cell) | idea hứa 3–50; hiện ≤7 | ~2h | ❌ |
| — | MetaGPT/AutoGen instantiation | idea nêu trong Risks | **đề xuất: khai báo ngoài phạm vi** | ❌ |

**Đề xuất thứ tự thực thi:** 4 → 2 → 1 → 5 → 3 → 6/7/8/9 → 10.
Lý do: (4) rẻ và chốt được bảng topology; (2) mở khoá cho (1); **(1) là việc giá
trị nhất còn thiếu**; (3) không tốn API nên làm song song lúc chờ job.

---

## 6. Ba chỗ cần bạn quyết

1. **Venue**: chốt AAMAS 2027 (theo template bạn đưa) hay quay lại USENIX/S&P?
   → quyết định thứ tự ưu tiên ở mục 5.
2. **Defense placement**: có làm không? Nếu không, phải **bỏ contribution #4** khỏi
   paper và ghi vào Limitations (hiện paper đã ghi là future work — trung thực,
   nhưng mất một đóng góp mà idea đã hứa).
3. **Tiêu đề**: giữ nguyên ý `idea.md` ("An Epidemiology of Prompt-Injection
   Propagation in LLM Agent Networks") hay dùng tiêu đề trong bản thảo
   ("Contagion: Measuring and Testing Prompt-Injection Propagation in LLM Agent
   Networks")? Bản thảo hiện dùng tiêu đề thứ hai vì nó phản ánh đúng kết quả
   mới (kiểm định, không chỉ mô tả).
