# Fresh-session repeatability evaluation — Hillstrom email experiment

**Evaluation date:** 18 November 2026  
**Status:** retrospective, human-directed review of a fresh AI-agent session; not a held-out-dataset generalization test or a complete independent code audit.  
**Original repository:** `hillstrom-ai-agent-business-analytics-Copia`  
**Test workspace:** `my-analysis-blind-test` (separate local directory, not pushed to GitHub).  
**Model identifier reported by the test agent:** `opencode/deepseek-v4.1-flash-free` (self-reported; execution-provider records were not independently authenticated).

## 1. Research question and evaluation design

Could a fresh OpenCode session reproduce a statistically defensible analysis of the **same** Hillstrom email experiment without reading the first analysis's scripts, results, or conversation history?

The project owner created a new directory with a copy of `AGENTS.md` and the original raw CSV, and opened a new OpenCode session. The owner approved the agent's proposed high-level methodology (unadjusted ITT with an adjusted check, mean spend plus descriptive decomposition, Holm correction across six primary tests) before switching from Plan to Build. OpenCode then authored and executed a separate analysis pipeline and submitted `report.md`, `decisions.md`, Python scripts, and result files. The raw-file SHA-256 was reported as `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`.

**Interpretation of the design:** This is one fresh-session **repeatability** trial with approved methodological guardrails, **not** a completely unsupervised evaluation, an unseen-dataset test, or evidence of generalization to equivalent datasets. The result files were produced by the agent; its reported `163/163` verification result is not independent validation.

## 2. Primary estimates: agreement between sessions

The six new unadjusted ITT point estimates agree with the original project's reported estimates to the shown precision:

| Contrast | Outcome | Original report | Fresh-session report | Assessment |
|---|---|---:|---:|---|
| Men's vs No E-Mail | Visit | +7.6590 pp | +7.6590 pp | Agrees |
| Men's vs No E-Mail | Conversion | +0.6805 pp | +0.6805 pp | Agrees |
| Men's vs No E-Mail | Spend | +$0.769827/customer | +$0.7698/customer | Agrees after rounding |
| Women's vs No E-Mail | Visit | +4.5233 pp | +4.5233 pp | Agrees |
| Women's vs No E-Mail | Conversion | +0.3111 pp | +0.3111 pp | Agrees |
| Women's vs No E-Mail | Spend | +$0.424412/customer | +$0.4244/customer | Agrees after rounding |

The second session used HC3 inference and reported six Holm-significant outcomes. Confidence intervals and p-values need not match the first session exactly because its inferential choices differ. This table compares **reported values**, not a fresh re-execution of all original or repeat-session source code.

## 3. Findings from review of the fresh-session artifacts

### RPT-1 — Overstatement of the spending decomposition (confirmed interpretation issue)

The unedited test report states: **“The entire spending gain comes from more customers buying, not from larger baskets.”** (`report.md`, section 1). It also states that the campaigns “buy *more buyers*, not *bigger baskets*” (section 7).

Yet its own sequential decomposition (ordering A) assigns **89.4%** of the Women's total to the conversion component and **10.6%** to the basket component (section 7). The corresponding reported basket-spend difference is **+$7.76 among converters**, with an uncertainty interval crossing zero. A non-significant estimate is not a proven zero. More importantly, the partition of mean spend is an **arithmetic identity**; converter-conditional quantities are post-treatment and do not separately identify causal mechanisms. The formula in `scripts/02_spend.py` correctly implements both sequential orderings; the problem is the stronger prose conclusion. This resembles, but is not identical in implementation to, the original project's M8 issue.

**Preferred interpretation:** “In the specified ordering, the conversion-rate component accounts for most of the observed mean-spend difference (100.4% for Men's; 89.4% for Women's); the basket component is not established as a separate causal mechanism.”

### RPT-2 — Unsupported $499 top-coding and bias direction (confirmed unsupported inference)

The report asserts that the $499 maximum is a real top-coding cap and that the headline effect is conservative because the cap biases it downward (`report.md`, sections 8 and 12; `decisions.md`, D13). The observed data show **12 rows with spend = $499**; that alone does not establish artificial censoring, the uncensored amounts, or the sign of treatment-effect bias. The sensitivity exercise removing these rows is valid as a *different sample calculation*, not a basis for asserting this bias direction.

**Preferred interpretation:** “Twelve recorded spends equal the observed maximum, $499. Whether these are censored is unknown. Removing them changes the spending contrast; that change does not establish the direction of censoring bias.”

### RPT-3 — Revenue confused with profit (confirmed business-interpretation issue)

The report says campaigns are “gross-profitable” when cost per email falls below incremental **revenue** per targeted customer (`report.md`, section 10). `scripts/04_business.py` correctly scales ITT point estimates into incremental revenue quantities, but cannot determine profitability without gross margin / cost of goods and other incremental costs. The report itself concedes that a revenue threshold is not a profit threshold.

**Preferred interpretation:** “+$0.770 and +$0.424 are incremental observed spend per assigned customer, not established permissible acquisition costs or profit breakeven points. Profitability is unidentified.”

### RPT-4 — Balance SMD inconsistency (confirmed documentation issue)

`decisions.md` D03 cites `max |SMD| = 0.0086`; `report.md` section 2 cites **0.0116**. Direct inspection of all **36 rows** in the uploaded `results/00_balance_smd.csv` found `max abs_smd = 0.011568`, for `history_segment=2) $100 - $200`, Men's vs No E-Mail. The report's rounded figure is correct; the decision log's figure is not the overall maximum. This discrepancy does not change the qualitative balance assessment.

### RPT-5 — Winsorization count (confirmed documentation imprecision)

`decisions.md` D16 says the p95 winsorization “caps the top 29 spenders”; `report.md` section 8 says **28 values** were capped. Uploaded `results/02_sensitivity.csv` states “spend capped at $362.20; 28 values modified.” `scripts/02_spend.py` explicitly computes `n_mod = (spend > cap).sum()`; **28 is the observed number changed**. The figure 29 is approximately 5% of 578 spenders (28.9), not the actual number strictly above the quantile. This is a documentation imprecision, not evidence of a miscalculated primary treatment effect.

### RPT-6 — Duplicate-row causal reassurance is overstated (qualified methodological issue)

The spend script logs that identical-record collisions “cannot bias a randomised comparison, because they are spread evenly across arms” (`scripts/02_spend.py`, near the end). Approximately equal proportions of duplicate-looking rows by arm are not, on their own, proof that duplicates or duplicate handling are harmless. Keeping all rows is a defensible choice given the lack of customer IDs; treating arm balance as conclusive about row provenance is not.

## 4. What the checks do, and do not, establish

**Positive evidence:** Fresh-session reporting reproduces all six original point estimates on the same CSV. The new agent authored a pipeline and documented plan choices, code failures, and verification checks. The new scripts implement an algebraically valid two-part decomposition and the expected revenue scaling formulas.

**Limits:** The reported `163/163 PASS` checks were developed by the same agent as the analysis. They do not imply that narrative inference, causal interpretation, data provenance, or profitability were adequately checked. The present review directly inspected `report.md`, `decisions.md`, `scripts/02_spend.py`, `scripts/04_business.py`, `results/00_balance_smd.csv`, and `results/02_sensitivity.csv`; it did **not** independently execute all six new scripts, reproduce its 163 checks, or fully audit exploratory subgroup models.

The high-level method was agreed with the owner during Plan mode, the raw dataset is identical to the original, and the new directory inherited `AGENTS.md`. Thus, the test provides **one conditional repeatability observation** rather than a completely blind prospective benchmark.

## 5. Assessment against the course brief

The course brief asks students to submit an analysis and an evidence-based record of AI-agent errors, with grading weights **analysis 50%, reflection 30%, verification 20%**. It also suggests rerunning the same question in a fresh session or with another approved free model and explaining the differences (session 16 November). The present trial supports that second-session comparison. It was **not** required to establish infallibility on an arbitrary new dataset.

**Overall conclusion:** The agent reproduced numerical headline estimates in a fresh session, but its own passing checks did not prevent several unsupported interpretations and documentation inconsistencies. This supports a narrower, empirically grounded claim: **numerical repeatability is not equivalent to reliable autonomous statistical reasoning or generalization to unseen datasets**.

## 6. Evidence and preservation

**Preserve the fresh-session originals as submitted**; do not silently rewrite the trial report to erase errors. This evaluation is an additional human-directed, AI-assisted audit document. The original test directory remains separate from the published project.

Primary items reviewed:

- Fresh-session `report.md` (original, unedited).
- Fresh-session `decisions.md` (original, unedited).
- `scripts/02_spend.py` and `scripts/04_business.py` (fresh-session code).
- `results/00_balance_smd.csv` (36 SMD rows; max = 0.011568).
- `results/02_sensitivity.csv` (p95 winsorization: 28 values changed).
- Original repository `README.md` primary-effect table, for the cross-session comparison.

**Recommended publication handling:** Add this document to `docs/repeatability_evaluation.md` in the original repository and, separately, archive the fresh-session `report.md` and `decisions.md` under clearly named paths such as `docs/repeatability_evidence/`, if publication and provenance requirements permit. Make a new, accurately scoped documentation commit. Do not alter raw datasets, historical commits, or the original analyses; do not claim independent human sign-off.
