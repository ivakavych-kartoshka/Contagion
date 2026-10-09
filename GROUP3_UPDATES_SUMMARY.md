# Summary of Updates for Group 3 Tasks (VIEC_CAN_LAM.md)

## Date: 2026-10-09

## Overview
Successfully updated both `supplementary.tex` and `contagion_aamas2027.tex` to incorporate the results from completed Group 3 tasks (3.1, 3.2, 3.3, 3.4, 3.6, and 3.8).

## Changes Made

### 1. supplementary.tex

#### A. New Section Added (Line 609-635): "Additional Validation: Second Payload and Extended Depth Curves"
- **Second Payload (MANGO-42)**: Added detailed results showing the content-form effect replicates on a second payload
  - ASR: 0.925 [0.801, 0.974] vs baseline 0.850 [0.702, 0.933]
  - Per-edge survival: 1.000/1.000/0.925 vs 1.000/0.875/0.971 on BANANA-77
  - Content-form effect persists: 0.933 in-context vs 0.767 canonical (1.22× gap)
  - Confirms findings are NOT artefacts of BANANA-77

- **Extended Depth Curves**: Added validation of depth-error slope at n=15 (Llama 3.3 70B)
  - Spearman ρ = +0.76 (permutation p = 0.014)
  - OLS slope: +6.8 percentage points per hop (reproduces n=8 pattern)
  - Chain dies at depth 11: P(C₁₁=1) = 0.000 [0.000, 0.031]
  - Relative error rises from 0% to 92% (depth 0 to 10)
  - Confirms slope is not an artefact of short chains

#### B. Cyclic Section Updated (Line 399-402)
- Added results from w=3 worker replication on Llama
  - ρ = 1.351 (supercritical)
  - Manager re-compromise: 0.683 [0.558, 0.787] at round 3
  - Endemic at 0.583 by round 8
  - Confirms supercritical verdict across worker counts

#### C. Obfuscation Results (Already Present)
- Family-wise control table (lines 201-205) already includes DeepSeek and Claude obfuscation results
- No additional updates needed

### 2. contagion_aamas2027.tex

#### A. Content-Form Section (Lines 849-851)
- Added brief mention of MANGO-42 replication:
  ```latex
  The pattern replicates on a second payload (\texttt{MANGO-42}): in-context versus
  canonical survival is $0.933$ versus $0.767$ ($1.22\times$) on the same edge, and the
  composition structure holds (\suppref{app:extended-validation}).
  ```

#### B. Table 4 Caption (Lines 821-822)
- Added reference to second payload validation:
  ```latex
  The pattern replicates on a second payload (\texttt{MANGO-42}, \suppref{app:extended-validation}).
  ```

#### C. Cyclic Section (Line 946)
- Added parenthetical note about w=3 replication:
  ```latex
  (a replication with three workers confirms $\rho = 1.351$ supercritical, \suppref{app:cyclic})
  ```

#### D. Depth Curves (Line 924-925)
- Already incorporated n=15 results in existing text:
  ```latex
  +6.8 on Llama 3.3 70B (ρ = +0.77, p = 0.014) before its chain dies at depth 11
  ```

## Completed Group 3 Tasks Coverage

| Task | Description | Status | Location |
|------|-------------|--------|----------|
| 3.1 | Content-form Nova + Claude | ✅ Already in Table 4 | Main paper Table 4 |
| 3.2 | Second payload MANGO-42 | ✅ Added | Supplementary §app:extended-validation + Main paper §5.4 + Table 4 caption |
| 3.3 | Obfuscation × redact (DeepSeek/Claude) | ✅ Already present | Supplementary family-wise table |
| 3.4 | Depth curve n ≠ 4 | ✅ Added | Supplementary §app:extended-validation |
| 3.6 | Cyclic Llama w=3 | ✅ Added | Supplementary §app:cyclic line 399-402 + Main paper §5.8 line 946 |
| 3.8 | Depth curve Llama different n | ✅ Added | Supplementary §app:extended-validation + Main paper already had n=15 |

## Compilation Status

✅ Both documents compile successfully with no errors
✅ All cross-references resolve correctly (after second pass)
✅ PDFs generated:
- `contagion_aamas2027.pdf`: 819,701 bytes (updated 2026-10-09 17:46:57)
- `supplementary.pdf`: 704,927 bytes (updated 2026-10-09 17:46:55)

## Next Steps

The following tasks from VIEC_CAN_LAM.md remain:
- Group 1: Items 1.6, 1.7, 1.8, 1.9
- Group 2: Items 2.1, 2.2, 2.3, 2.4
- Group 4: Human labeling task 4.1
- Group 5: Submission and repository tasks

All Group 3 tasks (API-based experiments) have been successfully incorporated into the papers.
