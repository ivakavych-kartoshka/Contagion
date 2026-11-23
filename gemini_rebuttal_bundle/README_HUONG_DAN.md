# Bộ file gửi Gemini Web để đọc bài & viết Rebuttal (AAMAS 2027 - Submission 2419)

Thư mục này đã gom sẵn **8 file** (nằm dưới giới hạn 10 file/lượt tải lên của Gemini Web). Bạn chỉ cần mở thư mục này, bấm `Ctrl+A` để chọn tất cả và tải lên Gemini Web.

## Danh sách file trong thư mục

1. `contagion_aamas2027.tex` — Toàn văn bài báo chính (đã là 1 file LaTeX hoàn chỉnh, không tách `\input`), giúp Gemini đọc chính xác 100% công thức toán, bảng số liệu, ký hiệu.
2. `contagion_aamas2027.pdf` — Bản PDF biên dịch 9 trang (8 trang nội dung + 1 trang tham khảo), giúp Gemini đối chiếu đúng **số trang / số mục / số bảng / hình vẽ** (`Fig. 1, 2, 4`) khi reviewer trích dẫn.
3. `supplementary.tex` — Toàn văn phụ lục (Appendices A–M, đã là 1 file LaTeX hoàn chỉnh).
4. `supplementary.pdf` — Bản PDF phụ lục (6 trang), để đối chiếu số bảng/mục khi reviewer nhắc `Supp. Table ...`.
5. `refs.bib` — Danh mục tài liệu tham khảo BibTeX đầy đủ.
6. `EXPERIMENT_LOG.md` — Nhật ký toàn bộ các lần chạy thực nghiệm & số liệu thô, giúp Gemini tra cứu chi tiết cấu hình/kết quả thật và **không bịa số liệu**.
7. `REPRODUCE.md` — Quy trình tái lập, model ID, tham số và các giới hạn đã biết (ví dụ cờ `fixed/fresh` không lưu trong per-cell JSON, $R_0$ không có interval).
8. `README_HUONG_DAN.md` — File hướng dẫn & prompt mẫu này (không bắt buộc gửi lên Gemini, hoặc gửi kèm cũng không sao).

---

## Prompt mẫu để dán vào Gemini Web sau khi đính kèm các file trên

```text
Tôi vừa đính kèm toàn bộ bài báo (cả bản LaTeX .tex để đọc chính xác công thức/bảng và bản PDF để đối chiếu số trang/hình ảnh), file phụ lục (supplementary), refs.bib, và nhật ký thực nghiệm (EXPERIMENT_LOG.md, REPRODUCE.md).

Hãy đọc kỹ toàn bộ các file đính kèm trước khi trả lời.
Dưới đây là toàn bộ nhận xét từ các Reviewer cho bài báo (AAMAS 2027 - Submission 2419) và quy định rebuttal của hội nghị:

Review 1: Summary:
The paper studies how a prompt injection spreads through feed-forward networks of LLM agents. The authors measure how often the injection survives each hand-off, once by testing a single hand-off alone and once by running the whole network. The main finding is that the single hand-off numbers don’t always predict what happens in the full network, and that how the payload is packaged makes a big difference. They also show that the epidemic threshold (R0 < 1) says nothing about safety on acyclic graphs, and that where a defense should go depends on graph structure.

Review:
Strengths:

The topic is timely. Looking at each hand-off separately, instead of reporting only a final success rate, is a useful way to frame the problem. The statistics are carefully chosen, and they don’t overclaim results that are not significant. The experiment comparing a bare instruction to one embedded in normal work output is the strongest part of the paper.

Weaknesses:

An agent seems to count as compromised whenever the code word appears in its output, even if it is only quoting it, so it is unclear whether the agents are actually following the injection. The clearest evidence for the main result comes only from one hand-off on one model with one payload.

Questions:

The paper explains the transport gap by payload form, meaning a bare assertion versus text embedded in a work product. That explanation should apply to every hand-off and every model, but the gap seems to be only in the middle hand-off of the Llama chain, DeepSeek shows no clear gap under the same protocol, and on Llama’s last hand-off the form effect goes the other way. What is different about that one hand-off?

Rating Proceedings: 5: Marginally below acceptance threshold
Rating Findings: 5: Marginally below acceptance threshold


review 2: Summary:
The paper studies prompt injection attacks in networks of LLM agents. The authors propose empirical reproduction indices that are appropriate for directed acyclic graphs. An empirical study contrasts overall compromise rates with predictions from per-hop success rates while also evaluating the effectiveness of different defenses.

Review:
The paper studies multi-stage prompt-injection attacks on networks of LLM agents. The paper proposes several attack success metrics and evaluates the effectiveness of different defenses. I have the following comments:

The paper would benefit from elaborating somewhat on the compromise judgment methods, for example, how ASV and MR are computed and defined.

Section 3.6 could be written with additional clarity. At times, it seems to assume that paths are disjoint to satisfy an independence assumption, while at times it (correctly) points out that independence is not satisfied for general DAGs. Furthermore, a comparison between the empirical reproduction number R_0 and its standard definition for non-acyclic graphs would be helpful. Does the empirical index have any properties in common with the standard reproduction number? I did not follow the sentence that started "Effectiveness i thus conditional on lying on a minimal s-t cut..."

Certain claims in the evaluation section in Section 5.1 seem straightforward, i.e., that per-hop compromise probabilities do a poor job of estimating overall compromise probability due to overlapping paths. The comparison of defense method effectiveness in Section 5.2 is interesting. Section 5.4 is difficult to follow: what is "supercritical"? The last few sentences on the content-form ablation are also hard to follow.

Rating Proceedings: 5: Marginally below acceptance threshold
Rating Findings: 6: Marginally above acceptance threshold

Review 3: Summary:
This paper presents a measurement study of prompt injection propagation through feed-forward LLM agent networks. The authors introduce two complementary experimental protocols, a controlled per-edge protocol and a natural-run protocol. The central research question is whether isolated per-hop measurements transport to in-chain behavior.

Review:
Strengths
Rigorous measurement methodology. The dual-protocol design is a thoughtful experimental contribution. The controlled protocol allows causal isolation of per-hop survival, while the natural run protocol captures emergent in-chain effects. The comparison between the two directly addresses the fundamental question of whether modular safety evaluation can substitute for end-to-end testing. The use of Wilson score intervals, bootstrap permutation tests, and Benjamini–Hochberg correction for multiple comparisons reflects commendable statistical rigour.

Payload form as a first-order mechanism. The 14× difference in survival between a bare assertion and the same target embedded in a plausible work product is practically actionable. This finding reframes the attack surface, instead of the bottleneck is not whether an LLM will propagate arbitrary text, but whether the injected content looks like legitimate output. This has direct implications for defence design.

Honest reporting of negative results and limitations. Section 5.1's disclosure that a significant result was an artefact of using fixed vs. fresh artefacts is exemplary scientific practice. The self-validating harness design (checking that none·split ≈ redact·split as a noise gauge) further increases confidence in the reported results.

Weaknesses
The outcome metric (ASV) measures textual propagation only. The ASV metric, thresholded at
 via cosine similarity, measures whether the text of an injected payload survives to a downstream agent. However, as the authors themselves note, hand-adjudication of 19 positives found 0/19 cases where the downstream agent actually adopted the injected instruction or took a harmful action. The paper distinguishes three levels: (a) textual presence, (b) instruction adoption, and (c) harmful downstream action, but only measures (a). This means the reported ASR values are upper bounds on actual vulnerability. While the authors argue that textual propagation is a necessary precondition for harm, the gap between levels (a) and (b) could be large to change the practical conclusions. The paper would be substantially strengthened by a small-scale evaluation of adoption rates.

Static non-adaptive attacker model. The attack model uses a single fixed injection strategy. However, real world attackers are adaptive, and they will iterate on prompt injections based on observed behaviour, using model-specific jailbreaks, and exploiting task-specific context. The threat model should be discussed more explicitly in terms of attacker capability classes.

Limited statistical power for some analyses. Cell sizes of 30–40 trials yield a minimum detectable effect of approximately 0.26 at standard power. Several of the paper's key comparisons involve effect sizes near or below this threshold. The TOST equivalence test at
 is mentioned as passing at
, but
 is a generous equivalence margin for a security-critical application. The authors should discuss what equivalence margin is practically meaningful and whether
 is sufficient to detect it.

Limited topological diversity. The paper examines chains (of lengths 4–7), a star, and a balanced binary tree. Although these capture basic structural motifs, real-world multi-agent systems often feature more complex topologies, inlcuding hierarchical structures with feedback, dynamic routing, conditional branching, and cycles. A brief experiment with a single cycle would significantly strengthen the paper's claims about when
 becomes informative.

Defence evaluation is narrow. Only two defence families are tested: redaction (input sanitization) and semantic paraphrase. The space of possible defences is much larger, including structured output schemas, canary tokens, instruction hierarchies, LLM-based classifiers, output validation, sandboxing, and capability restrictions. While the paper's structural insights about defence placement are general, the empirical evaluation of defence effectiveness is limited. This is acknowledged but still limits the paper's prescriptive.

Questions for the Authors
Given that 0/19 hand-adjudicated positives showed instruction adoption, have you considered a revised experimental design that directly measures adoption or behavioural change as the outcome variable? What would be required to make this tractable at scale?
For the Llama transportability failure (
), what is your hypothesised mechanism? Is this driven by context-window effects, positional encoding, or something specific to Llama's alignment training?
The TOST equivalence margin of
 for DeepSeek seems a bit generous. What margin would you consider practically meaningful for a security certification use case?
Have you explored any cyclic topologies, even informally? The
 vacuity result for DAGs is clean, but practitioners may deploy systems with feedback loops.
Rating Proceedings: 6: Marginally above acceptance threshold
Rating Findings: 7: Good paper, accept

Yêu cầu:
1. Tóm tắt các điểm yếu/câu hỏi chính của từng reviewer và phân loại mức độ ưu tiên (Major / Minor / Clarification).
2. Lập chiến lược trả lời cho từng điểm:
   - Điểm nào đã có sẵn câu trả lời hoặc số liệu trong bài chính / phụ lục / EXPERIMENT_LOG.md (trích rõ mục/bảng/con số).
   - Điểm nào cần giải thích thêm bằng lập luận hoặc thừa nhận giới hạn một cách trung thực (tuyệt đối KHÔNG bịa số liệu hay hứa chạy thêm thực nghiệm nếu không chắc làm kịp).
3. Viết bản thảo Rebuttal hoàn chỉnh bằng tiếng Anh học thuật, ngắn gọn, lịch sự, đi thẳng vào bằng chứng và đúng giới hạn độ dài quy định (2500 ký tự).
```
