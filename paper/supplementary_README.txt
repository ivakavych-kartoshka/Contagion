Supplementary Material
=====================

Paper: "Contagion: When Per-Hop Prompt-Injection Survival in LLM Agent Networks
Does (and Does Not) Compose" (AAMAS 2027, Research Paper Track)

Contents of this archive
-------------------------
  supplementary.pdf         Technical appendices A-D referenced from the main paper.
  supplementary.tex         LaTeX source for supplementary.pdf.
  supplementary_README.txt  This file.

Build: pdflatex supplementary.tex   (run twice; no BibTeX needed)

Mapping to the main paper
-------------------------
  Appendix A  Multiplicity Control for the Composition Test
              (main paper: Section 3.7, Section 5.2, Section 5.10, Section 7)
  Appendix B  Context-Clustered Interval on the Weak Edge
              (main paper: Section 4, Section 5.10)
  Appendix C  Threshold Sensitivity of the Floor Effect
              (main paper: Section 5.1, Section 5.4)
  Appendix D  Recurrence Makes the Threshold Non-Vacuous
              (main paper: Section 3.8, Section 5.8)

Cross-references are written as literal section numbers (e.g. "Section 5.10 of the
main paper") because this document does not share an .aux file with the main paper.

All tables in this supplement are produced offline from stored experimental
results; no model calls are required to reproduce them. The scripts are:

  scripts/appendix_stats.py     Appendix A (Benjamini-Hochberg) and Appendix B
                                (cluster bootstrap). NOTE: the p-values for
                                Appendix A are currently hard-coded in that
                                script; verify them against
                                experiments/results/*/results.json before reuse.
  scripts/cyclic_design_rule.py Appendix D (spectral radius of the recurrent
                                manager/worker pattern, checked against the
                                eigenvalues on 320 random configurations).
  scripts/tau_sensitivity*.py   Appendix C (re-thresholding of stored ASV
                                scores).

Case study results and the full replication manifest are in REPRODUCE.md at the
root of the code repository released with the paper.