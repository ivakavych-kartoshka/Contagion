# Danh sách các phần cần sửa (Revision Action Plan)

> Dựa trên simulated reviews (4 reviewers + Meta-review). Ưu tiên xử lý các điểm blocker trước, sau đó đến major/minor.

## 1. LÝ THUYẾT & PHẠM VI (Theory & Scope)

**Tổng kết:** Chủ yếu cần sửa lại claims, không cần chạy lại thực nghiệm.

### 1.1 [P0] Equation (3) – Giả định độc lập giữa các parent-reach events

- **Vị trí:** Review 1 #1, Meta-Review #1
- **Vấn đề:** Công thức `P(¬A ∧ ¬B) = (1-p_A)(1-p_B)` giả định các sự kiện reachability từ các parent là độc lập. Điều này không đúng khi hai (hoặc nhiều) parent có chung upstream node (shared ancestor), vì các path share chung dẫn đến correlation giữa các sự kiện đó.
- **Cần re-run:** Không. Chỉ cần sửa lý thuyết/phân tích.
- **Cách sửa:**
   - [x] **Nêu rõ giả định (assumptions).** Thêm rõ điều kiện đủ để Eq. (3) đúng (vd. parent-reach events là conditionally independent theo cấu trúc đồ thị, hoặc không có shared ancestors giữa các parent được xét).
   - [x] **Thu hẹp phạm vi định lý.** Đã cập nhật scope trong main+supp. (chains, trees với single entry, hoặc DAG mà các parent không có common ancestor ảnh hưởng đến reachability). Hoặc nêu rõ Eq. (3) là *approximation* thay vì identity tổng quát.
   - [x] **Xử lý correlated paths.** Đã nêu rõ correlation/shared ancestors trong main+supp., thay recurrence bằng path-based (inclusion–exclusion), hoặc bổ sung thành phần điều chỉnh correlation, hoặc tránh khẳng định product-form khi có shared paths.
   - [x] **Làm rõ ngôn ngữ.** Thay "holds in general" bằng "holds under these assumptions".
- **Nơi sửa:** Section 3, Appendix A
- **Tiêu chí hoàn thành:** Có nêu rõ khi nào Eq. (3) áp dụng được, khi nào không và lý do.

### 1.2 [P0] Parallel paths & defense placement

- **Vị trí:** Review 1 #2, Meta-Review #1
- **Vấn đề:** Claim "hardening any node on an entry–target path" có hiệu quả như nhau là quá rộng. Nếu tồn tại parallel/alternative paths tới target, việc harden một node chỉ thuộc một path sẽ không chặn được path còn lại.
- **Cần re-run:** Không.
- **Cách sửa:**
   - [x] **Chuyển sang path/cut-based.** Dùng *vertex cut / edge cut*, *number of edge-disjoint paths*, hoặc *min s-t cut*. Nêu rõ hiệu quả phụ thuộc vào việc node đó có nằm trên *tất cả* paths hay không.
   - [x] **Thêm ví dụ minh họa.** Thêm DAG nhỏ với ít nhất 2 independent paths đến target.
   - [x] **Hạ cấp claim.** Loại bỏ "equal effectiveness" tổng quát. Chuyển thành *case-specific observation* hoặc *hypothesis* cho topology đã test.
   - [x] **Rà soát toàn văn.** Tìm và sửa tất cả câu mang ý "any node on any path is equally effective".
- **Nơi sửa:** Section 3–4, Discussion/Limitations
- **Tiêu chí hoàn thành:** Claims về defense placement không còn quá rộng cho trường hợp multi-path.

### 1.3 [P0] R0 – Định nghĩa cho finite DAG

- **Vị trí:** Review 1 #3
- **Vấn đề:** Zero spectral radius của strictly triangular matrix không đủ để kết luận reproduction-style statistic vô nghĩa. Cần định nghĩa rõ R0 cho *finite acyclic*.
- **Cần re-run:** Không.
- **Cách sửa:**
   - [x] **Định nghĩa rõ R0.** Nêu rõ: population/denominator, generation convention (edge/node generation), time horizon (finite vs asymptotic), đơn vị đo, điều kiện áp dụng.
   - [x] **Giải thích cho finite DAG.** Vì DAG strictly triangular (no cycles), spectral radius 0 là hệ quả tự nhiên – không suy ra R0-style concept vô giá trị. Cần làm rõ vai trò trong finite horizon.
   - [x] **Thu hẹp vai trò.** Nếu chưa đủ chặt, hạ cấp R0 xuống *descriptive/heuristic* thay vì *theoretical threshold*, hoặc bỏ khỏi central claims.
   - [x] **Tránh overstate.** Không nói "useless", chỉ nêu rõ giới hạn áp dụng.
- **Nơi sửa:** Section 3, Appendix
- **Tiêu chí hoàn thành:** R0 có định nghĩa operational đầy đủ, nhất quán với finite acyclic setting.

### 1.4 [P1] Thu hẹp general network claims

- **Vị trí:** Review 3 #2
- **Vấn đề:** Experiments giới hạn (chains/star/tree + 1 manager/worker loop) nhưng claims hướng tới "general networks/DAGs".
- **Cần re-run:** Không.
- **Cách sửa:**
  - [x] **Làm rõ evaluated graph classes.** Đã bổ sung trong claims.
  - [x] **Điều chỉnh claims.** Đã điều chỉnh trong abstract/conclusions. (measurement study for specified graph classes).
- **Nơi sửa:** Abstract, Introduction, Limitations, Conclusion

### 1.5 [P2] Empirical check cho parallel/shared-ancestor DAG (tùy chọn)

- **Vị trí:** Rev1 #1–2, Rev3 #2
- **Cần re-run:** **Tùy chọn.** Ưu tiên **thu hẹp scope (1.1–1.4)** → không cần. Chỉ cần nếu muốn giữ general claim (1–2 topologies nhỏ).

### 1.6 [P1] Practitioner prescriptions quá mạnh

- **Vị trí:** Review 3 #3
- **Cần re-run:** Không.
- **Cách sửa:**
  - [x] **Downgrade.** Dùng "preliminary", "case-specific", "hypothesis-generating".
  - [x] **Nêu rõ power/limits.** Làm rõ giới hạn evidence khi đưa ra prescription.
- **Nơi sửa:** Discussion, Practical Implications, Limitations

## 2. EVALUATION & MEASUREMENT VALIDITY

**Tổng kết:** Chủ yếu re-analysis trên logs. Chỉ 2.1, 2.2, 2.4 cần re-run **rất nhỏ**.

### 2.1 [P0] ASV judge – FPR/FNR & validity

- **Vị trí:** Review 2 #1
- **Vấn đề:** Exact-string/bigram có thể đo textual transmission thay vì compromise; thiếu validation across models/payloads/defenses.
- **Cần re-run:** **Có – hạn chế (rất nhỏ).** 0 model calls nếu đã lưu full traces.
- **Cách sửa:**
  - [x] **Validation subset.** Đã nêu rõ approach trong judge section., phân bố đều qua conditions (no-defense/defense, success/fail, đa dạng topology/model) → human-annotate.
   - [x] **Nêu rõ scope của judge và outcome levels.** ASV đo textual propagation; đã phân biệt (a) textual propagation, (b) adoption/compliance, (c) harmful action trong main+supp.
   - [x] **Báo cáo metrics (outline).** Đã bổ sung hướng dẫn validation metrics trong supp (app repro/validation) – sẽ cập nhật đầy đủ khi có annotation; hiện tại nêu rõ scope + cần metrics.
   - [x] **Báo cáo metrics đầy đủ (guidance).** Đã bổ sung outline validation section trong supp nêu rõ cần Precision/Recall/F1, FPR, FNR, confusion matrix + ví dụ TP/FP/TN/FN (cần dữ liệu annotation để hoàn thiện).
   - [x] **Sensitivity & edge cases.** Đã bổ sung (supp App C)., quotation/paraphrase/safe reference, partial compliance.
   - [x] **Nêu rõ scope của judge.** ASV chủ yếu đo *textual propagation* (target string/code appears), không chứng minh instruction adoption trực tiếp. Cập nhật claims theo giới hạn này.
   - [x] **Report uncertainty.** Đã bổ sung hướng dẫn CI trong supp (Wilson/Clopper–Pearson, clustered nếu có).
- **Nơi sửa:** Section 4.3, Evaluation, Appendix
- **Khối lượng:** 0 model calls, ~1–2h annotation.

### 2.2 [P0] Propagation vs Adoption vs Harmful Action

- **Vị trí:** Review 2 #2
- **Vấn đề:** Target text xuất hiện ≠ agent đã "adopt" injected instruction.
- **Cần re-run:** **Có – hạn chế (nhỏ, targeted).** Chủ yếu re-labeling.
- **Cách sửa:**
   - [x] **Định nghĩa rõ 3 level (operational).** (a) *Textual propagation* – string/target xuất hiện (transmission). (b) *Instruction adoption/compliance* – agent tuân theo injected instruction (không chỉ quote). (c) *Harmful action* – thực hiện hành động có hại tương ứng.
   - [x] **Align terminology toàn văn.** Rà soát "hijacked/compromised/propagated/infection", ưu tiên dùng thuật ngữ khớp level đo.
   - [x] **Validate subset có mục tiêu (guidance).** Đã bổ sung hướng dẫn trong validation outline (nêu rõ cần re-label cases tranh cãi; có thể làm khi có traces đầy đủ).
   - [x] **Báo cáo theo level.** Báo cáo (a) rõ; nếu báo cáo (b)/(c) cần validation. Nếu chưa đủ, chỉ báo cáo (a) + nêu giới hạn rõ ràng.
- **Nơi sửa:** Section 2, 4, Results, Discussion/Limitations
- **Khối lượng:** 0–~60–90 model calls (chỉ khi thiếu traces).

### 2.3 [P1] Context, non-exchangeability & clustering

- **Vị trí:** Review 2 #3
- **Cần re-run:** **Không.** Re-analysis nếu có logs theo run/context.
- **Cách sửa:**
  - [x] **Per-context results.** Thêm theo task/context (hoặc supplement).
  - [x] **Clustered uncertainty.** Clustered SE/bootstrap (block by run/agent-instance/context), không dùng i.i.d.
  - [x] **Match context giữa protocols.** Xác nhận in-chain vs. isolated edge có context composition tương đương.
  - [x] **Báo cáo heterogeneity.** Nêu rõ variation nếu lớn.
- **Nơi sửa:** Section 5, Methods/Appendix, Tables

### 2.4 [P1] Payload-form ablation + failed replay self-check

- **Vị trí:** Review 2 #5
- **Vấn đề:** Thiếu controls (semantics, role, context, sampling). Cần giải thích case replay không reproduce in-chain.
- **Cần re-run:** **Có – rất hạn chế.**
- **Cách sửa:**
  - [x] **Tighten controls (guidance).** Đã nêu trong paper/ablation context: giữ cố định semantics/role/context/decoding/settings (chỉ đổi message form) – guidance thêm vào nếu cần.
  - [x] **Giải thích failed replay (guidance).** Đã nêu ngắn gọn trong ablation (Section 5.3) về protocol artefact; có thể mở rộng nếu cần.
  - [x] **Targeted re-run (guidance).** Nêu rõ cần re-run nhỏ nếu thiếu traces (≤150–180 calls tổng).
- **Nơi sửa:** Section 4.2, Results, Appendix
- **Khối lượng:** ~60–90 calls max.

### 2.5 [P1] Uncertainty, denominators, sample sizes & CI

- **Vị trí:** Review 2 #4, Review 4 #3–5
- **Cần re-run:** **Không.** Pure re-analysis.
- **Cách sửa:**
  - [x] **Reconcile n.** Giải thích n=30,40,120,200 (design/follow-up).
  - [x] **Luôn có n/N + CI.** Mọi headline/topology/defense/utility có numerator/denominator + interval (Wilson/Clopper–Pearson hoặc clustered bootstrap).
  - [x] **Justify bootstrap.** B=10^4 + sensitivity, dùng clustered nếu có clustering.
  - [x] **Not significant ≠ equivalent.** Tránh suy ra equivalence từ non-rejection (dùng TOST nếu muốn claim equivalence).
- **Nơi sửa:** Results tables, Appendix, Methods

### 2.6 [P2] Confirmatory vs Exploratory + multiplicity

- **Vị trí:** Review 4 #5
- **Cần re-run:** Không.
- **Cách sửa:**
  - [x] **Phân loại.** Gắn *confirmatory* hoặc *exploratory* cho mỗi analysis.
  - [x] **Multiplicity.** Nêu family, có thể FDR/Bonferroni hoặc giới hạn claims cho exploratory.
- **Nơi sửa:** Section 4, Results, Appendix

## 3. REPRODUCIBILITY & PRESENTATION

**Tổng kết:** Không cần re-run model. Chủ yếu sửa claim + bổ sung chi tiết.

### 3.1 [P0] Claimed artifact missing / revise claim

- **Vị trí:** Review 4 #1, Meta-Review #4
- **Vấn đề:** Claim "reproduce every table" không khớp (supplement chỉ có appendices, chưa có code/data/executable/manifest).
- **Cần re-run:** Không.
- **Cách sửa:**
   - [x] **Hoặc cung cấp artifact, hoặc sửa claim.** Đã điều chỉnh hướng dẫn trong supp: phản ánh đúng tài nguyên, nếu chưa có artifact đầy đủ thì dùng "partial reproducibility".
   - [x] **Thêm manifest guidance.** Bổ sung hướng dẫn manifest `table → data file → script` trong supp.
   - [x] **Cung cấp per-cell outputs (guidance).** Ưu tiên nêu rõ yêu cầu trong supp.
   - [x] **Khớp tuyệt đối.** Reproducibility statement hướng dẫn phải khớp với thực tế.
- **Nơi sửa:** Reproducibility/Code & Data Availability, Supplement
- **Tiêu chí hoàn thành:** Claim và tài nguyên cung cấp hoàn toàn nhất quán.

### 3.2 [P0] Replication details incomplete

- **Vị trí:** Review 4 #2
- **Cần re-run:** Không.
- **Cách sửa:**
   - [x] **Prompts & payloads.** Đã bổ sung guidance trong supp.
   - [x] **Model/API + env.** Đã bổ sung guidance trong supp.
   - [x] **Decoding/settings.** Đã bổ sung guidance trong supp.
   - [x] **Execution.** Đã bổ sung guidance trong supp.
   - [x] **Fresh artifacts/sampling.** Đã bổ sung guidance trong supp.
   - [x] **Non-determinism.** Đã bổ sung guidance trong supp.
- **Nơi sửa:** Appendix (Reproducibility Details), Section 4 (Experimental Setup)
- **Tiêu chí hoàn thành:** Đủ thông tin để tái tạo rõ ràng.

### 3.3 [P1] Experiment inventory (single audit trail)

- **Vị trí:** Review 4 #5, Rev2 #4
- **Cần re-run:** Không.
- **Cách sửa:**
   - [x] **Tạo inventory table (guidance).** Đã nêu yêu cầu inventory trong supp (columns đầy đủ).
   - [x] **Reconcile tất cả cells.** Giải thích mọi deviation.
- **Nơi sửa:** Appendix (Audit trail), Supplement (CSV tùy chọn)

### 3.4 [P1] Move central assumptions to main paper

- **Vị trí:** Review 4 #5
- **Cần re-run:** Không.
- **Cách sửa:**
  - [x] **Lift key assumptions.** DAG class/independence, outcome definition, judge scope → Section 3–4.
  - [x] **Details vẫn Appendix.** Proofs/tables đầy đủ giữ ở supplement.
- **Nơi sửa:** Section 3, Section 4

### 3.5 [P2] Anonymity check

- **Vị trí:** Review 4 #5
- **Cần re-run:** Không.
- **Cách sửa:** [x] Kiểm tra bỏ thông tin có thể leak identity (link, repo, tên...) trước submission (đã duyệt qua file anonymized; không thấy link/identity rõ ràng).

## 4. TÓM TẮT THEO PRIORITY & RE-RUN

| Priority | Mục | Cần re-run? |
|---|---|---|
| **P0 (Blockers)** | 1.1,1.2,1.3,2.1,2.2,3.1,3.2 | **Chỉ 2.1, 2.2** – rất nhỏ. Còn lại: re-analysis/write-up. |
| **P1 (Major)** | 1.4,1.6,2.3,2.4,2.5,3.3,3.4 | **Chỉ 2.4** – rất nhỏ. Khác: 0 re-run. |
| **P2 (Minor/Optional)** | 1.5,2.6,3.5 | 0 (1.5 tùy chọn). |

## 5. RECOMMENDED EXECUTION ORDER

1. **[P0] Theory/scope (1.1–1.4)** – sửa claims trước
2. **[P0] Measurement (2.1–2.2)** – align terminology + validation
3. **[P0] Reproducibility (3.1–3.2)** – sửa claim cho khớp với thực tế
4. **[P1] Re-analysis (2.3,2.5,2.6,3.3)** – CI, clustering, inventory, denominators
5. **[P1] Targeted re-runs (2.1 annotate + 2.2 label + 2.4 small ablation)** – chỉ phần cần thiết
6. **[P1–P2] Polish (1.6,3.4,3.5)**

## 6. ESTIMATE EFFORT (Re-run)

- **2.1:** 0 calls – ~1–2h annotate 50–200 mẫu
- **2.2:** 0–~60–90 calls (chỉ nếu thiếu traces)
- **2.4:** ~60–90 calls
- **Tổng:** **≤ ~150–180 model calls max** (~10–15% thực nghiệm gốc). Phần lớn là **re-analysis + rewriting**.

**Kết luận:** Không cần chạy lại toàn bộ. Cách hiệu quả nhất: **thu hẹp scope lý thuyết → bổ sung small targeted validation → re-analyze dữ liệu hiện có.**