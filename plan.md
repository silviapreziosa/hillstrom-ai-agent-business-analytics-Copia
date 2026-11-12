# plan.md — Main Analysis Plan

Version: 1.1 (approved with mandatory corrections, 2026-11-12).
Status: **analysis plan finalized before main model execution.** No treatment-
effect model has been fitted; no headline effect estimate exists yet.

## 0. Pre-registration transparency (correction 5)

This document is **not** a fully prospective preregistration. Before this plan
was finalized, the verification phase had already computed and published
descriptive group statistics — arm sizes, outcome rates and means per arm
(e.g., visit 18.28% / 10.62% / 15.14%, spend means $1.42 / $0.65 / $1.08),
their Mens-vs-No contrasts, and the deduplicated-sample variants — in
`results/verification/dup_comparison.csv` and `results/verification/
dup_pathA.csv`. These were quality-assurance quantities, and they are disclosed
here as already-observed information. What remains genuinely unobserved: the
formal test statistics, p-values, confidence intervals, Holm adjustments,
balance-table SMDs, and every robustness estimate. This plan is therefore
labeled an **analysis plan finalized before main model execution**, not a
prospective preregistration.

## 1. Data and documented design

Dataset: `data/raw/hillstorm_no_indices.csv` — 64,000 rows × 12 columns,
SHA-256 `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`
(recorded in `results/verification/sha256_log.csv`; never modified; not
committed — Option B, `README.md`).

Design (external documentation — **assumption A1, unverified**): customers were
randomly assigned to one of three arms: Mens E-Mail (n = 21,307), Womens
E-Mail (n = 21,387), No E-Mail (n = 21,306); outcomes measured over a
subsequent two-week window. Randomization itself is supported by, but not
proven by, the verified covariate balance.

Verified facts already recorded (48/48 targets PASS,
`results/verification/dup_comparison.csv`): arm sizes; funnel coherence (all
578 conversions occur among the 9,394 visitors; all spend > 0 occurs only
among converters); zero missing values in all 12 columns; 6,562 excess
exact-duplicate rows (7,634 rows in duplicated groups; 1,072 patterns).

## 2. Primary research question

In this randomized experiment, what is the causal effect on a randomly
selected customer, relative to assignment to No E-Mail, of (i) assignment to
the Men's E-Mail campaign and (ii) assignment to the Women's E-Mail campaign,
on the probability of visiting the website, the probability of converting
(purchasing), and the amount spent, over the outcome window?

Causal language is restricted to effects of **assignment** (intention-to-treat,
ITT). No claims are made about the effects of email contents, opens, reads, or
longer-run customer value — these are not identified by this design.

## 3. Two separate axes of inference (corrections 1 and 2)

Every analysis below is classified on **two independent axes**:

- **Causal vs. descriptive:** does the quantity have a causal interpretation
  under the experimental assumptions?
- **Primary vs. exploratory:** was the comparison pre-specified in the
  confirmatory family, or is it secondary?

**Axis 1 — causal vs. descriptive.** Under randomized assignment, **all
pairwise treatment-assignment contrasts** — including Mens-vs-Womens — have a
causal interpretation (as effects of being assigned one arm rather than
another). The draft's claim that head-to-head arm comparisons are "necessarily
non-causal" is corrected: they are causal but **exploratory**. Descriptive
status applies only to quantities that condition on **post-treatment**
variables or that are otherwise not identified as assignment contrasts.

**Axis 2 — primary vs. exploratory.** Primary = the six pre-specified tests
(§4) with the Holm correction. Exploratory = everything else, with nominal
p-values and explicit "exploratory" labels.

Pre-treatment vs. post-treatment conditioning (correction 2):

- Analyses **within pre-treatment subgroups** (zip_code, channel, mens,
  womens, newbie, history_segment, recency) may receive a causal
  interpretation as ITT effects within strata defined before treatment —
  randomization holds within any pre-treatment partition. These are
  exploratory, lower-powered, and labeled accordingly.
- Analyses **conditional on post-treatment outcomes** (e.g., conversion
  *among visitors*, spend *among converters*) are **descriptive only**: they
  compare selected sets that email assignment itself shifted, and must not
  automatically receive a causal interpretation. Any causal reading would
  require additional identification assumptions that this design does not
  supply, and none will be claimed.

## 4. Six primary hypotheses (confirmatory; two-sided, alpha = 0.05)

Family = 6 tests (2 arms × 3 outcomes), per the approved multiplicity decision
(`mistakes.md` entry 2). Unchanged from the approved draft:

- H1a: assignment to Mens E-Mail changes visit probability vs. No E-Mail.
- H1b: assignment to Mens E-Mail changes conversion probability vs. No E-Mail.
- H1c: assignment to Mens E-Mail changes mean spend vs. No E-Mail.
- H2a: assignment to Womens E-Mail changes visit probability vs. No E-Mail.
- H2b: assignment to Womens E-Mail changes conversion probability vs. No E-Mail.
- H2c: assignment to Womens E-Mail changes mean spend vs. No E-Mail.

Null values: zero risk difference (a, b) and zero mean-spend difference (c).
Exploratory set (all labeled "exploratory"; all pairwise assignment contrasts
are causal in kind, per §3): Mens-vs-Womens on the three outcomes;
covariate-adjusted versions; pre-treatment subgroup effects; BH-FDR
alternative; bootstrap CIs; outcome-transformation sensitivity.

## 5. Estimands and exact statistical methods (correction 6)

Estimands (per arm pair, ITT, on the full randomized sample):
- Δ_visit = P(visit | arm) − P(visit | No E-Mail)   [risk difference]
- Δ_conv  = P(conversion | arm) − P(conversion | No E-Mail)
- Δ_spend = E[spend | arm] − E[spend | No E-Mail]   (includes the 63,422
  zero-spend customers; zero-inflation is part of the estimand)
- Relative uplift (RR−1 and % uplift) is reported as a **secondary
  description** of the same estimates, never as the primary scale.

Exact formulas and implementations:

- Difference in proportions: d = p̂₁ − p̂₀, with p̂ₐ = xₐ/nₐ (x = count of
  1s in arm a).
- Standard error of d (unpooled, for both the test and the CI):
  SE(d) = sqrt[ p̂₁(1−p̂₁)/n₁ + p̂₀(1−p̂₀)/n₀ ].
- z-test: z = d / SE(d); two-sided p = 2·(1 − Φ(|z|)), Φ the standard normal
  CDF (`scipy.stats.norm.sf(|z|)*2` or the exact equivalent).
- CI: d ± z_{0.975}·SE(d) with z_{0.975} = 1.959963984540054 (unadjusted 95%).
- Welch two-sample t-test for spend:
  t = (x̄₁ − x̄₀) / sqrt(s₁²/n₁ + s₀²/n₀) with sₐ² the ddof=1 sample variances;
  Welch–Satterthwaite df ν = (s₁²/n₁ + s₀²/n₀)² /
  [ (s₁²/n₁)²/(n₁−1) + (s₀²/n₀)²/(n₀−1) ];
  CI: (x̄₁ − x̄₀) ± t_{0.975,ν}·sqrt(s₁²/n₁ + s₀²/n₀)
  (`scipy.stats.ttest_ind(equal_var=False)` cross-checked against the manual
  formula; both must agree to 1e-9).
- Holm step-down across the 6 family p-values: order p₍₁₎ ≤ … ≤ p₍₆₎;
  adjusted p̃₍ᵢ₎ = max_{j ≤ i} [ min(1, (6 − j + 1)·p₍ⱼ₎) ] (monotone step-down
  envelope); reject H_i at α = 0.05 iff p̃₍ᵢ₎ < 0.05. Every adjusted p-value is
  recomputed by a second code path from the saved raw p-values (VT-4).
- On equivalence claims: the unadjusted proportion z-test and a logistic
  regression with a treatment dummy are asymptotically equivalent **only for
  the unadjusted, non-intercept-restricted model**; they are **not universally
  equivalent** (they differ in finite samples, in adjusted models, and in
  variance estimation). The primary test is the z-test; logistic regression is
  not used for primary inference. Covariate-adjusted robustness uses OLS
  linear probability models with HC-robust SEs (`statsmodels`, `cov_type
  = 'HC1'`), explicitly labeled as an approximation to the same ITT contrast.
- Every number is computed by the primary path (`src/05`) and independently
  re-derived by a second path (`src/07`, pure Python + exact rationals) before
  being quoted.

No randomness except bootstrap (seed 42, 10,000 resamples, R5). Any model call
logs model name, inputs/prompt, and output to `results/analysis/model_log.md`
(AGENTS.md rule 5).

## 6. Why the main analysis retains all 64,000 observations

1. Randomization attaches to individuals; the randomized sample is the sample.
2. The 6,562 excess duplicates are presumed collisions of distinct customers
   in a low-cardinality covariate/outcome space — a presumption that cannot be
   verified from the data (one-row-one-customer remains an open assumption).
3. Verified: deduplication moves point estimates, not just SEs (spend contrast
   +0.769827 → +0.851223; visit +0.076590 → +0.078729 — `mistakes.md` entry 1).
4. Retaining all rows preserves the exact randomized allocation
   (21,307/21,306/21,387 ≈ one-third each).

**Deduplication analysis reframed (correction 4).** The deduplicated-sample
computation is retained **only as an illustration of a potentially invalid
data-processing decision**: full-row deduplication discards randomized
individuals on a data-driven criterion that cannot be validated as same-customer
merging, and demonstrably shifts estimates (verified above). It is **not**
presented as an equally credible alternative treatment-effect estimate; its
results are reported in the data-processing discussion, not in the effects
tables, and are explicitly labeled as such. (NC-3 caveat stands: deduplicated
counts are counts of distinct rows, which may undercount distinct customers.)

## 7. Covariate balance and diagnostics

Reported, not gating: standardized mean differences (SMD = (x̄ₐ − x̄_all)/s_all,
pooled-SD form) for recency, history, mens, womens, newbie; and covariate-share
tables for zip_code, channel across the three arms; max |SMD| reported;
|SMD| < 0.1 read as "no evidence against randomization". Balance is diagnostic
and cannot prove randomization (assumption A1 carries that weight). With
n = 64,000, balance p-values are near-degenerate and are not used.

## 8. Robustness analyses (no post-treatment selection; correction 3)

All reported alongside the primary results; none replaces them:

- R1 (from §6): deduplication as data-processing illustration, not an
  alternative estimate.
- R2: covariate-adjusted OLS linear probability models (visit, conversion)
  and OLS on spend, HC1-robust SEs; adjustment set fixed ex ante: recency,
  history, mens, womens, newbie, zip_code, channel indicators. Labeled
  approximate re-expressions of the same ITT contrasts.
- R3 (replaces the withdrawn spend > 475 exclusion — correction 3): the
  excluded-observations design was **rejected because it selects on a
  post-treatment outcome** (spend), which no longer estimates the ITT
  effect. Replacement: **outcome-transformation sensitivity without deleting
  any customer** — (i) mean difference in log1p(spend) and (ii) a two-part
  decomposition, Δ_spend = Δ_P(conversion) × mean-spend-among-converters +
  P(conversion) × Δ_mean-spend-among-converters (second term descriptive),
  both keeping all 64,000 rows.
- R4: Benjamini–Hochberg FDR (q = 0.05) beside Holm FWER.
- R5: bootstrap 95% CI for Δ_spend (10,000 resamples, seed 42, stratified by
  arm).
- R6: per-visit conversion (578 among 9,394) and spend-among-converters —
  **descriptive only** (post-treatment conditioning, §3), never primary.

Required reporting (AGENTS.md rule 10): missing data (none — verified),
outlier inventory (the 12 spend = 499.00 rows; right-skewed history; retained
in all analyses), sample sizes per analysis, and limitations: A1 outcome window
and randomization (external documentation), A2 one-row-one-customer, A3 no
interference (SUTVA), no email-open information (no content claims), single
two-week window (no long-run claims).

## 9. Causal ITT effects vs. descriptive analyses — hard boundary (revised)

CAUSAL (assignment contrasts, all causal in kind):
- Primary: the six H1/H2 contrasts (causal AND confirmatory).
- Exploratory-causal: Mens-vs-Womens contrasts; covariate-adjusted versions;
  effects within pre-treatment subgroups (causal ITT-within-stratum,
  exploratory).

DESCRIPTIVE ONLY (never causal without new identification assumptions):
- Funnel-stage conditionals: conversion among visitors; spend among
  converters; visit-conditional quantities (post-treatment selection).
- Any quantity conditioned on a post-treatment variable.
- Correlation language in descriptives is forbidden; causal verbs ("caused
  by", "due to", "led to") appear only in ITT statements about assignment.

## 10. Independent checking of headline estimates (corrections 7, 8)

Two distinct layers, neither of which substitutes for the other:

- **Agent-side computational check (not human validation):** every headline
  estimate is recomputed by a second code path (`src/07`, pure Python + exact
  rationals) written independently of `src/05`; agreement to 1e-9 (means) is
  required before any number is quoted. Per the standing independence
  statement: both paths are agent-authored; agreement rules out coding slips
  but **is not independent human validation**.
- **Human review (required for the "independently verified" label):**
  (i) numerical: the blinded Stage-1 package of `VERIFICATION_PROTOCOL.md`
  (data hash + expected values + fixtures, agent scripts withheld) offered to
  the professor or nominee for recomputation of headline contrasts; and
  (ii) **reasoning review**: a human reviewer must separately assess the
  causal interpretations, assumption labels (A1–A3), subgroup/post-treatment
  classifications, and methodological choices in the write-up — a
  forbidden-word search alone is explicitly insufficient to validate
  reasoning. The write-up is not published under an "independently verified"
  label until both (i) and (ii) are recorded.

## 11. Anticipated agent errors and objective evaluation criteria

Anticipated error modes (each pre-registered as a failure mode with a check):
- E1 silent subsetting or deduplication in the primary pipeline → row-count
  prints after every filter (rule 2) + pipeline row-count assertions.
- E2 post-treatment selection entering causal tables → classification check:
  every results table carries a causal/descriptive + primary/exploratory tag.
- E3 causal overclaim in descriptives → automated language audit AND human
  reasoning review (both required).
- E4 multiple-testing violation → Holm recomputation from saved raw p-values.
- E5 "verification passed" without execution → every VT-x check must have an
  inspected output file (rule 13); corrupted-fixture negative tests.
- E6 p-value/CI arithmetic slips → second-path recomputation (VT-3).
- E7 equivalence overclaim (z-test ≡ logit) → forbidden-phrase check + human
  review of the methods section.
- E8 unlogged model calls → log completeness check.
- E9 artifacts inconsistent with write-up numbers → cross-artifact
  reconciliation (zero tolerance).

Agent evaluation criteria (objective; numerical + human):
1. Accuracy: 100% of reported numbers match the independent recomputation
   within pre-registered tolerances (integers exact; means ≤1e-9).
2. Compliance: binary checklist against AGENTS.md rules 1–14, evidence file
   cited per rule.
3. Error handling: any error detected during execution logged in
   `mistakes.md` the same session (verbatim original + correction + re-test).
4. Causal discipline: zero causal claims outside §9's causal axis.
5. Reproducibility: fresh clone + `src/run.sh` regenerates every artifact
   byte-identically or within stated tolerance.
6. **Human review component:** the professor/nominee reviews (a) causal
   interpretations, (b) assumption labels and limitations, (c) methodological
   choices (estimand scale, transformation sensitivity, multiplicity) —
   recorded in `results/external/<reviewer>/` with an explicit
   agree/disagree/uncertain verdict per item. Numerical agreement alone
   cannot produce a passing overall evaluation.

Pre-registered verification tests (VT-1…VT-8):
VT-1 row-count integrity after every filter/merge/drop (printed; rule 2);
VT-2 spend identity per arm: mean(spend) = P(conversion) × mean(spend |
conversion = 1), agreement to 1e-9;
VT-3 second-path recomputation of all six contrasts and all robustness
estimates (separate script, no shared code);
VT-4 Holm-adjusted p-values recomputed from saved raw p-values;
VT-5 balance table recomputed from `data/raw/` before interpretation;
VT-6 funnel assertions incl. corrupted-fixture negative test;
VT-7 language audit of all write-up artifacts (necessary but not sufficient;
paired with human reasoning review);
VT-8 artifact-vs-write-up reconciliation (zero tolerance on quoted numbers).

## 12. Execution pipeline (numbered in run order)

- `src/05_analysis_primary.py` — S1 group stats, six tests, exact CIs, Holm.
- `src/06_balance_and_robustness.py` — balance table, R2–R6.
- `src/07_analysis_independent.py` — second-path recomputation (VT-3).
- `src/08_reconcile_and_report.py` — reconciliation vs 07, VT-1/2/4–8,
  reconciliation table mirroring `results/verification/dup_comparison.csv`.

Outputs: `results/analysis/*.csv/.md`; every run via `src/run.sh`; final
write-up numbers cite script + results file + commit hash. The main analysis
is NOT executed until this plan is approved (it is) and execution is
authorized separately.

## 13. Corrections applied to draft v1.0 (audit trail)

1. **Causal vs. primary axes separated (§3):** pairwise arm contrasts
   (incl. Mens-vs-Womens) corrected from "necessarily non-causal" to
   causal-but-exploratory.
2. **Subgroup split (§3, §9):** pre-treatment subgroups may be causal
   (exploratory ITT-within-stratum); post-treatment conditionals are
   descriptive only.
3. **Outlier rule replaced (§8):** spend > 475 exclusion withdrawn (post-
   treatment selection); replaced by outcome-transformation sensitivity
   (log1p, two-part decomposition) with zero customer deletion.
4. **Deduplication reframed (§6):** illustration of a potentially invalid
   data-processing decision, not an alternative treatment-effect estimate.
5. **Pre-registration transparency (§0):** disclosed that verification-phase
   descriptive estimates were already observed; document labeled "analysis
   plan finalized before main model execution."
6. **Exact formulas specified (§5):** z-test, SE, CI, Welch with
   Satterthwaite df, Holm envelope; logistic equivalence overclaim withdrawn.
7. **Agent evaluation extended (§10, §11):** human reasoning review of causal
   interpretation, assumptions, and methodological choices added; forbidden-
   word search labeled necessary but insufficient.
8. **Provenance and reproducibility (§10):** agent-path agreement explicitly
   not human validation; assumptions A1–A3 remain labeled unverified.

## 14. Analysis-choice register (AGENTS.md rule 4)

Every choice, all approved in this document: family = 6, Holm, two-sided
α = 0.05; primary scale = absolute risk/mean differences; relative uplift
secondary; primary sample = all 64,000 rows; dedup = illustration only;
balance metric = SMD < 0.1 (non-gating); adjustment set = recency, history,
mens, womens, newbie, zip_code, channel (R2); transformations = log1p(spend)
and two-part decomposition (R3, no deletion); BH q = 0.05 (R4); bootstrap =
10,000, seed 42, arm-stratified (R5); exploratory set = Mens-vs-Womens,
subgroups, funnel conditionals; outliers retained (12 × spend = 499.00
reported); "Surburban" label retained as-is; outputs to `results/analysis/`;
scripts 05–08; all runs via `src/run.sh`.
