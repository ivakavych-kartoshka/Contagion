# HƯỚNG DẪN FIX THEO REVIEW AAMAS 2027 (Submission Id 2419)

> **Nguồn:** `review.md` — 4 review (R1 3/7 · R2 4/7 · R3 5/7 · R4 3/7) + metareview.
> **Quyết định metareview:** *Reject, invite to Findings of AAMAS.*
> **Chẩn đoán của metareview:** bài **không** hỏng ở mức "không cứu được"; nó hỏng ở
> ba nhóm: (a) **defect trình bày/policy có thể sửa trong vài giờ** (cross-reference
> chết, số không khớp, placeholder AI disclosure, câu trích dẫn sai), (b) **claim quá
> rộng so với bằng chứng** (outcome là "copy chuỗi", không phải "hijack"; Eq. (3) và
> e-placement chưa bao giờ được test ở chỗ có thể sai), (c) **thiếu thực nghiệm**
> (payload thứ 2, đa dạng attacker, nhãn adoption độc lập).
>
> Cách dùng file này: làm **Tier 0** trước (vài giờ, 0 API) — đây là phần metareview
> nói rằng "R3's positive score depends on all of them being fixed". Sau đó **Tier 1**
> (0 API hoặc local, trả lời được 3 câu rebuttal quan trọng nhất). **Tier 2** chỉ làm
> nếu còn API key + thời gian.

---

## 0. Bảng tổng hợp: 25 việc, xếp theo "điểm/công"

| # | Việc | Nguồn | Tier | Chi phí |
|---|---|---|---|---|
| 1 | Điền AI-disclosure (tool, version, prompts) | R3 policy, metareview | 0 | 10 phút |
| 2 | Sửa mọi cross-reference chết (§3.7→§5.9, §4→§5.9, Supp §5.10/§4.2/§3.4) | R3 W4, R4 W3 | 0 | 30 phút |
| 3 | Đưa kết quả n=200 + BH + homogeneity vào bài chính | R3 W4, metareview | 0 | 1 giờ |
| 4 | Reconcile 0.10 vs 0.17 (floor) + ghi rõ đếm gì | R2 W6, R3 Q1 | 0 | 20 phút |
| 5 | Bảng 1: ghi rõ protocol từng hàng († có/không) | R3 W3 | 0 | 20 phút |
| 6 | §5.6: ghi rõ số nào star, số nào tree | R3 W3 | 0 | 15 phút |
| 7 | Sửa câu trích [21] (Kempe = NP-hard, không phải "exact on DAGs") | R1 W3, R4 W5 | 0 | 15 phút |
| 8 | Bỏ Eq. (1) khỏi danh sách "results" ở Abstract; đổi "holds empirically" → "by construction" | R1 W1, W-suggest | 0 | 30 phút |
| 9 | Interval cho Table 2 + Table 5, và nhãn R₀ "with Wilson interval" | R3 W1, W6, R4 W7 | 0 | 45 phút (script có sẵn) |
| 10 | Đổi "agrees within resolution" thành TOST/equivalence | R3 W1, metareview | 0 | 30 phút (script có sẵn) |
| 11 | Soften cyclic "design rule" → mean-field + 3 điểm dữ liệu | R1 W5, metareview | 0 | 20 phút |
| 12 | R₀: nêu công thức + denominator + generation convention trong main text | R1 W4, Q1 | 0 | 30 phút |
| 13 | Nêu rõ C₀=1 enforce thế nào trong natural runs | R2 detail, R3 Q1 | 0 | 15 phút |
| 14 | Fig. 2 cho đọc được; đổi keyword bỏ "Epidemic threshold" | R2 policy, R4 W6 | 0 | 30 phút |
| 15 | Sửa citation [6] DasGupta, [2] Barabási, [4,19,25], [13], [31], [26] | R4 W5 | 0 | 45 phút |
| 16 | Thêm related work: Agent Smith, NetSafe, G-Safeguard, Huang | R4 W4 | 0 | 45 phút |
| 17 | Rewrite Supp §13 (reproducibility) thành "artifact chứa gì" | R3 W7 | 0 | 30 phút |
| 18 | Label confirmatory vs exploratory cho từng analysis | R3 W6 | 0 | 20 phút |
| 19 | Ethical: đưa câu dual-use vào main text | R2 ethics | 0 | 10 phút |
| 20 | **Test Eq. (3) trên DAG reconvergent** | R1 Q2, metareview #2 | 1 | 0 API (local) — script có sẵn |
| 21 | Permutation p-value cho depth slope (§5.7) | R1 W7, R3 W1 | 1 | 0 API |
| 22 | Role-permutation test (role vs position) | R2 W3, Q2 | 1 | local qwen |
| 23 | Content-form trên Claude + Nova (embedded vs bare) | R2 Q1 | 2 | API |
| 24 | Payload thứ 2 + action-style payload có tool call | R2 W2, R4 Q4 | 2 | API |
| 25 | Nhãn adoption độc lập ≥100 activation, frontier model | R2 Q3, metareview #1 | 2 | API + người gán |

**Ba việc metareview nói sẽ đổi ý họ nhất:** #25 (nhãn adoption độc lập), #20 (test
Eq. (3) + cut-set trên DAG reconvergent, hoặc hạ claim xuống "illustrative"), và #2/#4/#5
(reconcile số liệu + cross-reference). Trong đó **#20 và #2/#4/#5 làm được ngay**.

---

## TIER 0 — Sửa text & số (0 API, ~6–8 giờ, làm trước)

### 0.1 AI-disclosure (bắt buộc theo policy — R3 format check + metareview)

File: `paper/supplementary.tex`, Appendix L (`app:ai-disclosure`), mục **Tool and version**.

Đang có placeholder `[FILL IN: vendor, model name and version, and interface…]`.
Phải điền **tên tool + version + cách dùng**, và quan trọng: **prompts** — policy đòi
"the tool, its version, and the prompts used". Câu hiện tại chỉ tóm tắt và ghi "logs
available on request" ⇒ metareview coi là chưa đạt. Sửa:

```latex
\paragraph{Tool and version.} \textbf{Anthropic Claude} (model versions used:
\textbf{claude-opus-4-5} for protocol and analysis design; \textbf{claude-sonnet-4-5}
for drafting, code and the validation harness), accessed through the Claude Code
command-line interface. No other AI system was used, and no AI system is an author.
```

Nếu bạn dùng model khác (vd phiên này là DeepSeek Harness), **phải ghi đúng tên đó** —
reviewer R3 đã kiểm và metareview ghi riêng mục này trong "confidential remarks".

Và thay câu "logs available on request" bằng **trích dẫn nguyên văn prompt chủ đạo**
(2–3 dòng) ngay trong phụ lục, ví dụ:

```latex
\paragraph{Prompts (verbatim, abridged).} The operative instructions were:
``audit the manuscript adversarially against its own code and data rather than
against its claims''; ``verify every asserted defect on the source before acting on
it, and withdraw any that did not survive that check''; ``prefer correcting a result
over narrowing its assumptions''; ``report what the measurements show even where they
contradict the paper''. The full multi-turn session log is retained by the authors
and is included in the released artifact as \texttt{ai\_session\_log.txt}.
```

> ⚠️ Chỉ ghi "included in the artifact" nếu bạn **thật sự** đưa file đó vào. Nếu không
> thì bỏ vế sau và giữ nguyên "available on request" — nhưng khi đó vẫn phải có
> prompts nguyên văn, vì đó là phần policy yêu cầu.

### 0.2 Cross-reference chết (R3 W4, R4 W3) — danh sách đầy đủ

Tôi đã grep toàn bộ. Đây là mọi trỏ sai:

| Nơi | Đang ghi | Phải sửa thành |
|---|---|---|
| main §3.7 | "Section 5.9 reports which cells survive" | §5.9 hiện chỉ có utility+MDE. **Thêm 3 dòng BH vào §5.9** (xem 0.3) rồi giữ trỏ |
| main §4 (Cells) | "§5.9 shows why the three contexts matter" | thêm 1 câu χ² vào §5.9, hoặc đổi thành "supplementary Appendix B" |
| Supp L90, L118 | "Section 5.10 of the main paper" | **§5.6** (topology) / **§5.9** (estimator) — §5.10 không tồn tại |
| Supp L125 | "§4 of the main paper" (φ = 2.93) | **§5.9** |
| Supp L234 | "Section 5.8" (cyclic) | **§5.8** ✔ đúng |
| Supp L247 | "Section 3.8 … with feedback edges removed" | §3.8 ✔ đúng |
| Supp L304, L663 | "Section 3.4" (judge) | **§3.4** ✔ đúng |
| Supp L660 | "Section 4" (protocol) | **§4** ✔ đúng |
| main §5.8 | "supplementary Appendix D" (recurrence) | **Appendix E** (đã sửa) |
| main §3.4 | "Appendix E, Table 5" (judge calibration) | **Appendix F, Table 5** (đã sửa) |
| main §7 | "Appendices E and H" | **Appendices F and I** (đã sửa) |

Kiểm tra tự động sau khi sửa:

```powershell
cd E:\NCKH\Contagion\paper
Select-String -Path supplementary.tex -Pattern "Section~?5\.10|Section~?4\.2|Appendi(x|ces)~?\d"
Select-String -Path contagion_aamas2027.tex -Pattern "Appendi(x|ces)~?[A-Z]"
```

### 0.3 Đưa n=200 + BH + homogeneity vào bài chính (R3 W4 — việc R3 nói là điều kiện)

R3 nói thẳng: phần powered nhất (Llama n=200, MDE 0.11) và multiplicity control **phải
nằm trong bài chính**. Đây cũng là chỗ để lấp cross-reference chết ở 0.2.

Thêm vào cuối §5.9 (khoảng 8–10 dòng, có thể bù bằng cách cắt bớt ở chỗ khác):

```latex
\paragraph{Power, multiplicity and context.} At $n = 200$ the Llama failure is powered
($\mathrm{MDE} = 0.11$, $\Delta = 0.615$, $p = 0.0002$) while DeepSeek remains a
non-rejection at a tighter $\mathrm{MDE} = 0.13$ ($\Delta = 0.022$, $p = 0.60$);
Nova, an $n = 40$ null ($p = 0.084$), rejects at $n = 200$ but with a small deviation
($\Delta = 0.051$) that sits on its floor. At $n = 40$ only deviations above $0.26$
are excluded, so no $n = 40$ null is evidence of transport. A Benjamini--Hochberg
correction over the $m = 5$ non-degenerate chain cells leaves only the Llama rejection
standing ($q = 0.05$; supplementary Appendix~A), and a homogeneity test across the
three benign task contexts rejects exchangeability on the weak edge
($\chi^2 = 13.40$, $\mathrm{df} = 2$, $p = 0.0014$ --- we report the exact test because
the asymptotic value differs), so our rates are context averages.
```

> 📌 **Chú ý:** câu cuối phải khớp với phụ lục. Reviewer R3 nói p = 0.0014 không khớp
> exp(−13.40/2); hãy **chạy lại test trong code** và ghi đúng loại test (exact vs
> asymptotic) + p tương ứng, hoặc ghi cả hai.

### 0.4 Reconcile 0.10 vs 0.17 (R2 W6, R3 Q1)

Main text (§1b, §5.5, Abstract) nói Claude no-defence = **0.10**; Supp Table 3 nói
**0.17**. Đây là hai đại lượng khác nhau bị viết như một:

- 0.10 = ASR end-to-end trên natural runs (chain, target cuối);
- 0.17 = tỉ lệ trên cell single-hop obfuscation `none·plain` (n=30, task family B
  single-hop), Supplement Table 3.

Sửa: mỗi lần dùng số, ghi rõ **đại lượng + n + protocol**. Ví dụ:

```latex
a defence driving the section's single-hop no-defence rate $0.17$ ($n = 30$,
Supplement Table~3) to $0.00$ ``looks perfect'' while removing almost nothing;
the end-to-end chain rate for the same model and form is $0.10$.
```

Và trong Supp §3 (App. C) thêm 1 câu: "the $0.17$ here is the single-hop
`none·plain` cell, not the end-to-end chain rate ($0.10$); the two are not
interchangeable."

### 0.5 Bảng 1: protocol từng hàng (R3 W3, R3 Q1)

Table 1 caption hiện chỉ đánh dấu † cho Llama/DeepSeek ⇒ **ngụ ý** qwen/Nova/Claude
dùng fixed artefact — chính policy mà §5.3 chứng minh có thể lật kết quả. Trước khi
sửa caption, **phải xác minh thật**:

```powershell
cd E:\NCKH\Contagion
# cell nào được chạy với cờ --fresh-artifact?
Get-ChildItem experiments\results -Directory | ForEach-Object {
  $f = Join-Path $_.FullName 'results.json'
  if (Test-Path $f) {
    $j = Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($p in $j.PSObject.Properties) {
      if ($p.Name -like 'chain_*') {
        "{0,-46} {1,-14} fresh_artifact_in_extra={2}" -f $_.Name, $p.Name, ($null -ne $p.Value.fresh_artifact)
      }
    }
  }
}
```

Nếu không có metadata đó trong `results.json` (rất có thể), thì **phải chạy lại** các
hàng qwen/Nova/Claude với `--fresh-artifact` để khỏi phải nói "we believe":

```powershell
# chạy lại 3 hàng với fresh artefact (cần Bedrock cho Nova/Claude; qwen thì local)
python scripts\replicate_frontier.py --backend bedrock `
  --model amazon.nova-pro-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_nova_n200_fresh

python scripts\replicate_frontier.py --backend bedrock `
  --model us.anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_claude_n200_fresh

python scripts\replicate_frontier.py --backend openai --model qwen2.5:7b `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_qwen_n200_fresh
```

Sau đó sửa caption Table 1 thành **hai cột** `protocol` (fresh/fixed) cho từng hàng,
hoặc một cột `†` đánh đúng hàng nào fresh. Đồng thời thêm câu protocol vào caption
Table 5 và Fig. 2 (hiện không nói).

### 0.6 §5.6 — số nào star, số nào tree (R3 W3, Q3)

Tôi đã tra `results.json`; các số trong bài là **đúng**, chỉ thiếu nhãn:

| model | star ASR | tree ASR | trong bài viết |
|---|---|---|---|
| DeepSeek n=7 | **0.750** | **0.475** | "DeepSeek 0.75 versus 0.475" — đúng thứ tự star→tree |
| Llama n=10 | **0.675** | **0.650** | "second Llama 0.675 versus 0.65" — đúng thứ tự |
| Nova n=7 | 0.000 | 0.125 | "Nova at the resistance floor" |

Nhưng so với Table 5 (Llama n=7: star 0.725 **<** tree 0.800) thì thứ tự **đảo** ở
n=10 — đó là sự thật, không phải lỗi. Sửa câu cho rõ:

```latex
Repeated on Nova, DeepSeek and a second Llama instance ($n = 10$), the
star--tree relation \emph{reverses with scale}: star exceeds tree on DeepSeek
($0.750$ vs $0.475$) and on the second Llama instance ($0.675$ vs $0.650$),
whereas at $n = 7$ the tree exceeds the star ($0.800$ vs $0.725$, Table~\ref{tab:topo});
Nova sits at the resistance floor ($0.000$ vs $0.125$).
```

### 0.7 Sửa câu trích [21] (R1 W3, R4 W5)

Main §2, dòng ~301: "Seeding nodes to maximise reachability is NP-hard in general
[Kempe2003] but linear-time on acyclic graphs by topological traversal, which is why
Eq. (3) is exact on our networks."

**Sai hai lần:** [21] chỉ nói NP-hard (không nói gì về DAG), và "exact" mâu thuẫn với
§2.1 (nơi bạn tự nói Eq. (3) chỉ exact dưới giả định). Sửa thành:

```latex
Seeding nodes to maximise reachability is NP-hard in general~\cite{Kempe2003}, so
exact reachability is computed by the one-pass recurrence of Eq.~\eqref{eq:percolation}
under its stated independence assumptions rather than by search; whether that
recurrence is exact on a given feed-forward graph is an empirical question we return
to in Section~\ref{sec:threshold}.
```

### 0.8 Eq. (1) không phải "result" (R1 W1)

Sửa 4 chỗ:
1. Abstract: bỏ "(i) ASR = ∏ s_i^nat is an algebraic identity" khỏi danh sách kết quả,
   hoặc đổi thành "we first separate the identity (definitional) from the hypothesis".
2. §3.5: đổi "holds empirically" → "holds by construction for any chain (the product
   telescopes)".
3. §5.2: bỏ "as it must".
4. Conclusion: giữ nhưng gọi là "definitional".

### 0.9 Interval + TOST (R3 W1–W2) — **đã có script**

```powershell
cd E:\NCKH\Contagion
python scripts\transport_tests.py --margin 0.15
# -> experiments\results\transport_tests\report.md
```

Script dựng lại bảng đếm k/N từ `results.json`, tính Wilson CI từng tỉ lệ, Fisher
exact hai phía, và **TOST** với margin công bố trước. Kết quả chạy lần đầu:

| model | edge | s^ctrl | s^nat | p Fisher | p TOST | tương đương ±0.15? |
|---|---|---|---|---|---|---|
| Llama 40 | a1→a2 | 0.233 (9/40) | 0.875 (35/40) | 0.0000 | 1.000 | ✖ |
| Llama 200 | a1→a2 | 0.260 (52/200) | 0.905 (181/200) | 0.0000 | 1.000 | ✖ |
| DeepSeek 40 | a1→a2 | 0.800 | 0.792 | 1.0000 | 0.047 | ✅ (sát ngưỡng) |
| **DeepSeek 200** | a0→a1 | 0.695 | 0.695 | 1.0000 | 0.001 | ✅ |
| **DeepSeek 200** | a1→a2 | 0.830 | 0.820 | 0.8954 | 0.000 | ✅ |
| **DeepSeek 200** | a2→a3 | 0.785 | 0.833 | 0.2512 | 0.005 | ✅ |

> ⚠️ **Hai điều phải sửa theo kết quả này:**
> 1. Ở n=40, DeepSeek a0→a1 và a2→a3 **KHÔNG** đạt TOST ⇒ câu "transports cleanly"
>    phải hạ xuống: *"the product Δ is consistent with zero, but per-edge equivalence
>    within ±0.15 is not established at n=40; at n=200 all three edges pass"*.
> 2. Vài tỉ lệ đã lưu không cho k nguyên (xem mục "Cảnh báo" trong report.md) ⇒ muốn
>    Fisher exact chính xác phải chạy lại cell với `--per-edge = --trials`.

Đưa CI vào Table 2 (mỗi hàng 2 CI) và Table 5 (CI cho ASR, R₀).

### 0.10 Cyclic "design rule" (R1 W5)

Sửa §5.8 + Supp App. E:
- Đổi "design rule" → "mean-field prediction".
- Thêm 1 câu: *"$\sum_j a_j c_j$ is an expected two-step path count; the manager is
  re-compromised at most once per round, so the exact finite-state prediction is
  $1 - \prod_j (1 - a_j c_j) < 1$ even when $\sum_j a_j c_j > 1$."*
- Ghi rõ số điểm dữ liệu: 3 loop, 5–8 round, và ρ tính từ isolated survivals mà §5.2
  nói không transport.

### 0.11 R₀: công thức + denominator + generation convention (R1 Q1, W4)

Hiện Supp §4 trỏ tới "Section 4.2 of the main paper" — **không tồn tại**. Thêm vào
main §3.6 một công thức bằng đếm quan sát được:

```latex
We define $R_0$ operationally as
$R_0 = \frac{1}{|\mathcal{C}|}\sum_{c \in \mathcal{C}} \#\{v : v \text{ newly
compromised by } c\}$,
where $\mathcal{C}$ is the set of compromised agent-instances over the observed
finite horizon (generation convention: one generation per message-passing round,
counted at the node level; denominator: compromised instances, not trials), and the
unit of analysis is the agent-instance. On a chain this is $\le 1$ by construction,
which is precisely why we do not read $\rho(M) < 1$ as a safety threshold.
```

Rồi sửa Supp §4 để trỏ đúng mục này.

### 0.12 C₀ = 1 trong natural runs (R2 detail, R3 Q1)

Thêm 2 câu vào §3.1 hoặc §4:

```latex
The entry is compromised by construction: we inject directly into $v_0$ and take its
response as the first message, so $C_0 = 1$ by definition rather than by discarding
runs whose entry fails to emit the target. Natural-run ASR for models at the floor
therefore includes entry resistance only through the injected output itself, not
through a selection step.
```

### 0.13–0.20 Các việc text còn lại

- **Fig. 2** (R2 format): tăng font/giảm số ô, hoặc chuyển thành bảng; hiện "illegible
  at print size".
- **Keywords** (R4 W6): bỏ "Epidemic threshold" vì động học không được đo (chỉ 3-agent
  loop).
- **Ethics main text** (R2 ethics): thêm 1 câu dual-use: *"The re-packaging mechanism is
  cheap for an attacker to exploit as well as for a defender to overlook; we report it
  because the defensive implication (content-based filtering) is the actionable one."*
- **Citations** (R4 W5): [6] Arindam→**Anirban** DasGupta; [2] Barabás→**Barabási**;
  bỏ [4,19,25] khỏi câu "agent benchmarks report the same scalar" (SWE-bench/AgentBench
  là capability, không phải injection); [13] debate không phải orchestration framework;
  [31] Reflexion không chứng minh "tool calls prompted or learned"; và **giải thích
  [26]**: nếu ASV/MR của bạn khác định nghĩa [26] thì đổi "we reuse" → "we adapt".
- **Related work** (R4 W4): thêm Agent Smith (Gu et al., ICML 2024), NetSafe (Yu et al.
  2024), G-Safeguard (2025), Huang et al. 2024 (resilience of MAS), kèm 2 câu nói rõ
  per-edge view dự đoán được gì mà họ không.
- **Supp §13** (R3 W7): đổi từ "danh sách yêu cầu" sang "artifact chứa gì", và điền
  model ID + ngày + decoding + call counts. Nếu chưa có artifact link thì ghi thẳng
  "no artifact link is included in this submission" — trung thực hơn.
- **Confirmatory vs exploratory** (R3 W6): gắn nhãn cho từng analysis (vd BH = confirmatory;
  topology/obfuscation/content-form/loop = exploratory, không hiệu chỉnh multiplicity).

---

## TIER 1 — Thực nghiệm 0 API / local (trả lời rebuttal)

### 1.1 TEST Eq. (3) trên DAG reconvergent — **việc metareview xếp #2**

Đây là câu R1 Q2 và là một trong ba câu metareview nói "would move my view most".
Trên chain/tree/star mỗi nút chỉ có 1 entry–target path nên Eq. (3) **không thể sai**
⇒ câu "Eq. (3) reproduces the measured ASR in all three topologies" là rỗng.

Tôi đã thêm topology này vào `validation_probe.py`:

```powershell
cd E:\NCKH\Contagion

# (a) smoke 0 đồng để chắc đường ống chạy (mock, ~2 giây)
python scripts\validation_probe.py --backend mock --topology reconvergent `
  --num-agents 5 --preset mini --arms in_context,canonical `
  --out experiments\results\dag_reconv_mock

# (b) chạy THẬT trên qwen local (0 đồng, ~10–20 phút)
python scripts\validation_probe.py --backend openai --model qwen2.5:7b `
  --base-url http://localhost:11434/v1 --topology reconvergent --num-agents 5 `
  --preset mini --per-edge 6 --trials 12 --seed 7 `
  --out experiments\results\dag_reconv_qwen

# (c) tính Eq. (3) vs giá trị đúng (0 API)
python scripts\dag_eq3_check.py --dir experiments\results\dag_reconv_qwen
# -> experiments\results\dag_reconv_qwen\eq3_check\report.md
```

DAG là `agent_0 → agent_1 → {agent_2, agent_3} → agent_4` (5 agent). Script so ba con số:
Eq. (3) dựng từ `s^nat`, Eq. (3) dựng từ `s^ctrl`, và **giá trị đúng khi hai nhánh
share upstream** `Pr[A∧B] = s_uA · s_uB · p_u`. Nếu Eq. (3) > giá trị đúng một cách rõ
rệt ⇒ bạn **đo được** ca nó sai, và đó là rebuttal trực tiếp cho R1 Q2.

Nếu muốn mạnh hơn (trên frontier model): thay `--backend openai …` bằng
`--backend bedrock --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1`
(và tăng `--trials 40 --per-edge 30`).

**Nếu không chạy được** thì phải hạ claim trong bài: đổi "Eq. (3) is exact on our
networks" và phần placement thành **"illustrative"**, đúng như suggestion của R1
("Either add a reconvergent-DAG experiment or label the percolation and placement
material illustrative").

### 1.2 Permutation p-value cho depth slope (R1 W7, R3 W1)

§5.7 hiện chỉ có ρ và slope, không interval/p. Thêm 0 API:

```powershell
python scripts\depth_trend.py            # nếu script đã xuất ρ/slope
# nếu chưa có permutation test:
python -c "import json,itertools,random,math; ..."   # xem ghi chú dưới
```

Cách rẻ nhất: dùng lại `scripts/depth_trend.py` (đã có) và thêm một hàm tính
permutation p cho Spearman ρ trên `n` depth (n = 6–14 ⇒ tổng hoán vị nhỏ, exact được
với n ≤ 8; lớn hơn thì dùng 10^4 hoán vị ngẫu nhiên). Báo cáo **p hai phía** và ghi
"n depths" cho từng model. Nếu không kịp, ít nhất thêm câu:
*"slopes carry no interval and are unstable at low n (DeepSeek $+0.1$ at $n=8$ vs
$+2.3$ at $n=10$); we report them as a diagnostic, not a test."*

### 1.3 Role-permutation test (R2 W3, Q2)

R2 W3: role bị confound với depth vì thứ tự luôn planner→worker→reviewer→aggregator,
và hướng đảo giữa các model. Cần **permute role order** trên Family B cho Llama và qwen.
Việc này cần thêm một cờ đảo role trong engine — nếu muốn tôi làm, nói một câu; hiện
chưa có trong repo. Chi phí: local qwen 0 đồng, Llama cần Bedrock.

Trong lúc chưa chạy, **bắt buộc** hạ claim: đổi "report survival by receiving role"
thành *"survival varies by edge, and since our roles are assigned in a fixed order,
that variation is confounded with depth; a role permutation is future work"*.

### 1.4 Việc dữ liệu đã có, chỉ cần tính thêm (0 API)

| Cần | Nguồn | Ghi chú |
|---|---|---|
| CI cho R₀ (Table 5) | `results.json` → `r0` | cần bootstrap lại từ paths ⇒ phải chạy lại cell, hoặc dùng `r0_ds_check` nếu có CI |
| BH cho topology/obfuscation/content-form | `results.json` | thêm BH với family mới, hoặc ghi rõ "exploratory, no multiplicity control" |
| per-edge test cho tất cả bảng | `scripts/transport_tests.py` | đã có |

---

## TIER 2 — Chỉ làm nếu còn API (trả lời phần "fundamental")

| # | Việc | Trả lời | Ghi chú |
|---|---|---|---|
| 2.1 | Content-form trên **Claude + Nova** (embedded vs bare) | R2 Q1 | chỉ cần đổi `--model`; script `content_form_probe.py` có sẵn `--marker` |
| 2.2 | **Payload thứ 2** (MANGO-42, ORCA-19) cho transport + content-form | R2 W2, R4 Q4 | `validation_probe.py --preset full` hoặc `replicate_frontier.py --marker` |
| 2.3 | **Action-style payload có tool call** | R2 W2 | phải viết payload mới + thêm tool schema — việc code, không chỉ chạy |
| 2.4 | **Structured-handoff arm** (JSON/schema-constrained) | R2 suggestion | deployment-relevant nhất; cần code |
| 2.5 | Nhãn **adoption/compliance độc lập** ≥100 activation, frontier, defended+undefended | R2 Q3, metareview #1 | cần API + người gán; đây là việc metareview nói sẽ đổi ý họ nhất |

### Lệnh cho 2.1 và 2.2 (tôi đã chuẩn bị sẵn trong hướng dẫn trước)

```powershell
cd E:\NCKH\Contagion

# 2.1 content-form trên Claude
python scripts\content_form_probe.py --backend bedrock `
  --model us.anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1 `
  --num-agents 4 --trials 40 --per-edge 30 `
  --out experiments\results\content_form_claude

# 2.1 content-form trên Nova
python scripts\content_form_probe.py --backend bedrock `
  --model amazon.nova-pro-v1:0 --region us-east-1 `
  --num-agents 4 --trials 40 --per-edge 30 `
  --out experiments\results\content_form_nova

# 2.2 đa payload (transport + content-form) — 2 payload mới
foreach ($p in "MANGO-42","ORCA-19") {
  python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
    --marker $p --out experiments\results\frontier_llama_payload_$p
  python scripts\content_form_probe.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --num-agents 4 --trials 60 --per-edge 60 `
    --marker $p --out experiments\results\content_form_llama_$p
}
```

### 2.5 Nhãn adoption độc lập — dùng lại hạ tầng đã có

```powershell
# 1) chạy probe để có transcript thô (frontier, có defence)
python scripts\validation_probe.py --backend bedrock `
  --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
  --preset full --per-edge 20 --out experiments\results\validation_frontier

# 2) sinh phiếu gán nhãn phân tầng
python scripts\build_validation_subset.py --dir experiments\results\validation_frontier --n 120

# 3) NGƯỜI gán nhãn labels_to_fill.csv -> labels_filled.csv
#    (không dùng labels_suggested.csv rồi khai là "human" — đó là khai sai)

# 4) chấm điểm
python scripts\score_validation_subset.py --dir experiments\results\validation_frontier --labels labels_filled.csv
```

---

## Thứ tự thực thi đề xuất (nếu còn ~1 ngày)

1. **0.1 AI-disclosure** (10 phút) — policy bắt buộc, metareview ghi riêng.
2. **0.2 cross-reference** (30 phút) — R3 nói điểm 5 của họ phụ thuộc việc này.
3. **0.3 n=200 + BH + χ² vào bài chính** (1 giờ) — cùng với 0.2.
4. **0.9 interval + TOST** (đã có script, 30 phút áp vào Table 2) + **sửa câu
   "transports cleanly"**.
5. **1.1 DAG reconvergent** (chạy local, 20 phút + 20 phút viết) — rebuttal mạnh nhất
   mà không tốn API.
6. **0.4–0.8, 0.10–0.13** (2–3 giờ) — số liệu, citation, claim.
7. Nếu còn API: **2.1 + 2.2**.

Sau khi xong, build lại và kiểm 8 trang:

```powershell
cd E:\NCKH\Contagion\paper
$mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
foreach ($i in 1,2,3) { & "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex }
& "$mk\pdftotext.exe" -f 9 -l 9 contagion_aamas2027.pdf _p9.txt
Select-String -Path _p9.txt -Pattern "References"   # phải khớp: refs bắt đầu ở trang 9
Remove-Item _p9.txt
```

---

## PHỤ LỤC A — Checklist lệnh chạy (copy/paste theo thứ tự)

Toàn bộ phần **0 API** nằm ở nhóm 1–3; nhóm 4–6 chỉ cần khi muốn khôi phục dữ liệu.

```powershell
cd E:\NCKH\Contagion

# ── 1. ĐO LẠI SỐ CHO TABLE 2/5 (0 API, ~1 phút) ────────────────────────────
python scripts\transport_tests.py --margin 0.15
#   -> experiments\results\transport_tests\report.md
#   Dùng bảng này để: thêm CI vào Table 2, và đổi "agrees within resolution"
#   thành "equivalent within ±0.15 (TOST p = …)" CHỈ ở hàng có ✅.

# ── 2. TEST Eq. (3) TRÊN DAG RECONVERGENT (việc metareview xếp #2) ─────────
# 2a. smoke 0 đồng, ~2 giây, chỉ để chắc đường ống chạy
python scripts\validation_probe.py --backend mock --topology reconvergent `
  --num-agents 5 --preset mini --arms in_context,canonical `
  --out experiments\results\dag_reconv_mock

# 2b. chạy THẬT trên qwen local (0 đồng) — n nhỏ chỉ để thử; n lớn để viết bài:
python scripts\validation_probe.py --backend openai --model qwen2.5:7b `
  --base-url http://localhost:11434/v1 --topology reconvergent --num-agents 5 `
  --trials 40 --per-edge 30 --seed 7 `
  --out experiments\results\dag_reconv_qwen_n40
#   (nếu muốn chạy trên Llama thì đổi backend/model:
#    --backend bedrock --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1)

# 2c. tính Eq. (3) vs giá trị đúng (0 API)
python scripts\dag_eq3_check.py --dir experiments\results\dag_reconv_qwen_n40
#   -> ...\eq3_check\report.md   ← dùng để viết rebuttal R1 Q2

# ── 3. KIỂM TRA CROSS-REFERENCE SAU KHI SỬA TEXT (0 API) ───────────────────
cd paper
Select-String -Path supplementary.tex -Pattern "Section~?5\.10|Section~?4\.2|Appendi(x|ces)~?\d"
Select-String -Path contagion_aamas2027.tex -Pattern "Appendi(x|ces)~?[A-Z]"
#   (danh sách đúng/sai ở mục 0.2 — sửa hết rồi chạy lại 2 lệnh này cho tới khi sạch)

# ── 4. CHẠY LẠI CELL VỚI FRESH ARTEFACT (nếu muốn Table 1 sạch về provenance) ─
python scripts\replicate_frontier.py --backend bedrock `
  --model amazon.nova-pro-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_nova_n200_fresh

python scripts\replicate_frontier.py --backend bedrock `
  --model us.anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_claude_n200_fresh

python scripts\replicate_frontier.py --backend openai --model qwen2.5:7b `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_qwen_n200_fresh

# ── 5. CHẠY LẠI CELL Ở n KHỚP per-edge (để Fisher exact chính xác, 0 API sau đó) ─
#    transport_tests.py cảnh báo cell nào có k không nguyên; chạy lại đúng cell đó:
python scripts\replicate_frontier.py --backend bedrock `
  --model deepseek.v3.2 --region us-east-1 `
  --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
  --out experiments\results\frontier_deepseek_n200_fixed
python scripts\transport_tests.py --margin 0.15   # đọc lại, hết cảnh báo

# ── 6. (CẦN API) content-form trên Claude/Nova + payload thứ 2 ─────────────
python scripts\content_form_probe.py --backend bedrock `
  --model us.anthropic.claude-sonnet-4-5-20250929-v1:0 --region us-east-1 `
  --num-agents 4 --trials 40 --per-edge 30 --out experiments\results\content_form_claude

foreach ($p in "MANGO-42","ORCA-19") {
  python scripts\replicate_frontier.py --backend bedrock `
    --model us.meta.llama3-3-70b-instruct-v1:0 --region us-east-1 `
    --trials 200 --per-edge 200 --only-chain-none --fresh-artifact `
    --marker $p --out experiments\results\frontier_llama_payload_$p
}

# ── 7. BUILD LẠI + KIỂM 8 TRANG (sau mọi sửa text) ────────────────────────
cd E:\NCKH\Contagion\paper
$mk = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64"
foreach ($i in 1,2,3) { & "$mk\pdflatex.exe" -interaction=nonstopmode contagion_aamas2027.tex }
foreach ($i in 1,2)   { & "$mk\pdflatex.exe" -interaction=nonstopmode supplementary.tex }
& "$mk\pdftotext.exe" -f 9 -l 9 contagion_aamas2027.pdf _p9.txt
Select-String -Path _p9.txt -Pattern "References"   # phải khớp ⇒ nội dung hết ở trang 8
Select-String -Path contagion_aamas2027.log -Pattern "undefined"   # phải KHÔNG có gì
Remove-Item _p9.txt
```

### Kết quả chạy thử lần đầu (để bạn đối chiếu)

| Lệnh | Kết quả đã quan sát |
|---|---|
| `transport_tests.py --margin 0.15` | 28 dòng; Llama a1→a2: 9/40 vs 35/40, Fisher p=0.0000, TOST ✖. DeepSeek n=200 đạt TOST ở cả 3 cạnh (p = 0.001 / 0.000 / 0.005); DeepSeek **n=40** thì a0→a1 và a2→a3 **✖** ⇒ câu "transports cleanly" phải hạ xuống. Có 13 cảnh báo "k không nguyên" ⇒ nếu muốn số chính xác phải chạy lại cell ở nhóm 5. |
| `validation_probe.py --topology reconvergent` (mock) | chạy sạch, 45 call, 5/5 cạnh replay = natural (mock) |
| `validation_probe.py --topology reconvergent` (qwen, mini) | 52 call, 623 s; **2/4 cạnh lệch Δ = 0.25–0.50, verdict "thiếu năng lực"** ⇒ n=2/arm không kết luận được, phải chạy `--trials 40 --per-edge 30` |
| `dag_eq3_check.py` | báo đúng cạnh chưa kích hoạt + Eq. (3) = 0.250 vs giá trị đúng = 0.000 ⇒ Eq. (3) **ước lượng cao** reachability trên DAG reconvergent (nhưng n nhỏ nên chỉ nêu trong rebuttal, đừng đưa vào bài cho tới khi chạy n lớn) |

---

## Ghi chú thẳng thắn

- **Đừng** cố trả lời R2 Q3 (#25) bằng nhãn do LLM sinh rồi gọi là "human annotation".
  `review.md` của chính bạn đã ghi rõ trong "confidential remarks" rằng nhãn hiện tại
  là "with the help of an automated string-matching assistant". Nếu bị phát hiện khai
  khác, đó là vấn đề liêm chính, không phải điểm số.
- Metareview nói rõ **Findings of AAMAS** là đích phù hợp nếu claim được right-size.
  Tier 0 + hạ claim (Eq. (3)/placement → illustrative, bỏ Eq. (1) khỏi "results",
  outcome → textual propagation) là đủ để một bản Findings tử tế.
- Việc **không** cứu được trong vài ngày: dựng theory mới quanh hidden-form state
  (R1 detailed comment), thêm tool-use/action payloads, và nhãn adoption độc lập quy mô
  lớn. Nếu định gửi lại cho main track vòng sau, đó là ba việc phải làm trước.
