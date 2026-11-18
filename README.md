# A Verifiable Business Analytics Project

### Causal effects of email campaigns in the Hillstrom experiment — and an evidence-based evaluation of AI-agent reliability

**Status:** analysis complete · documentation finalized 2026-11-18 · independent
human verification protocol **pending**.

This repository contains a reproducible intention-to-treat (ITT) analysis of a
three-arm email experiment (64,000 randomized customers), an auditable record of
the AI agent's errors and corrections, and a verification framework that
distinguishes agent-authored checks from separate computational audits. It is
also a case study in what an AI coding agent can and cannot be trusted to
verify about its own work.

**Documentation map**

| File | Purpose |
|---|---|
| `README.md` | Project overview, methods, findings, verification, reflection |
| `plan.md` | Approved analysis plan v1.1 (commit `7f6b11c`) |
| `mistakes.md` | Verbatim error record with corrections and re-tests |
| `docs/error_taxonomy.md` | Non-overlapping error classification and evidence index |
| `MODEL_USE_DISCLOSURE.md` | What is known / reported / unknown about the AI models |
| `VERIFICATION_PROTOCOL.md` | Pending human blinded-verification protocol |
| `AGENTS.md` | The 14 governing rules |
| [docs/repeatability_evaluation.md](docs/repeatability_evaluation.md) | Fresh-session repeatability test: six reproduced ITT estimates, methodological review, and documented limitations |

---

## A. Executive Summary

This project asked whether an AI agent could produce a Business Analytics
analysis that a human could audit **without trusting the agent's word**. The
task was to estimate the causal effects of two email campaigns — Men's and
Women's — relative to no email, on website visit, conversion, and spending,
using 64,000 randomized customers.

The agent produced a complete analysis with six pre-specified confirmatory
contrasts, pre-specified robustness checks, and ten automated verification tests.
Assignment to both campaigns increased all three outcomes (ITT; under A1–A3).
The Men's campaign raised visit
probability by **+7.6590 percentage points**, conversion by **+0.6805 pp**, and
mean spending by **+$0.769827 per randomized customer**; the Women's campaign
raised them by **+4.5233 pp**, **+0.3111 pp**, and **+$0.424412**. All six
Holm-adjusted p-values are below 0.05.

The more informative result is about reliability. The loud failures were
implementation and test-code defects, and they were fixed. Two consequential
errors did **not** fail any agent-written test: a unit-label error (M6) that
understated a 7.66-percentage-point effect by a factor of 100, and an
interpretation error (M8) that described an exact arithmetic decomposition as a
causal mechanism. Both were found by **separate AI computational audits**, not by
the agent's own checks. No fully independent human audit has been completed;
`VERIFICATION_PROTOCOL.md` Stages 1–3 remain pending.

**Error posture.** 22 confirmed error items are documented across five
non-overlapping categories (2 statistical, 8 verification-design, 6
coding/execution, 2 tooling/reproducibility, 4 reporting/interpretation), plus
2 methodological ambiguities. No correction changed a final reported estimate,
standard error, confidence interval, or p-value; the M6, M8, and M10
corrections left every substantive statistical CSV byte-identical. The errors are catalogued in `mistakes.md` and indexed in
`docs/error_taxonomy.md`.

**Data privacy.** The raw dataset is **not** committed (approved Option B). Its
known SHA-256 is
`00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`.
No redistribution rights are claimed, and no source URL or license is invented.

---

## B. Research Question and Dataset

**Question.** In this randomized experiment, what is the causal effect, relative
to assignment to No E-Mail, of assignment to (i) the Men's E-Mail campaign and
(ii) the Women's E-Mail campaign on:

- the probability of visiting the website,
- the probability of converting (purchasing), and
- the amount spent,

over the outcome window?

**Design.** Customers were randomized to three arms: Men's E-Mail (n = 21,307),
No E-Mail (n = 21,306), and Women's E-Mail (n = 21,387). The analysis estimates
**intention-to-treat (ITT) effects of assignment**. It does not estimate the
effect of opening, reading, or acting on an email, and it makes no long-run or
content claims.

**Data.** `data/raw/hillstorm_no_indices.csv`: 64,000 rows × 12 columns, no
missing values. Descriptive features: 6,562 excess exact-duplicate rows
(7,634 rows in duplicated groups; 1,072 distinct patterns), and 12 rows with
spend = 499.00. Duplicates are retained in the primary analysis; the
deduplicated sample (57,438 rows) is used only as a labeled illustration of a
potentially invalid data-processing decision.

**Integrity and privacy (Option B).**

- The raw CSV is excluded from Git by `.gitignore` (`data/raw/*.csv`).
- Its identity is anchored by SHA-256
  `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`,
  logged before and after every run in `results/analysis/sha256_log.csv` and
  `results/verification/sha256_log.csv`.
- The schema is consistent with the well-known Hillstrom "MineThatData" email
  dataset, but **provenance is unverified**. No redistribution rights are
  claimed. Reviewers must obtain the file from a source they are entitled to
  use; see §J.

**Assumptions and data limitations (unverified).**

| ID | Assumption |
|---|---|
| A1 | Random assignment and the documented two-week outcome window (external documentation; balance is consistent with, but cannot prove, randomization) |
| A2 | One row = one distinct customer (duplicate collisions make this unprovable from the file alone) |
| A3 | No interference between customers (SUTVA) |
| A4 | No cost, margin, or campaign-cost data are available, so no profitability threshold is computable |

Additional unverified items: the spend = 499.00 "cap" interpretation, dataset
provenance, and the meaning of deduplicated row counts.

---

## C. AI Agent Architecture and Instructions

**What is documented.** The work was performed by an AI coding agent operating
in a repository with file-system and shell access; the runtime context reported
the provider as `opencode`. The agent's exact internal architecture (planning
loop, tool set, context management, model version) is **not recorded** in the
repository. The runtime-reported model identity is disclosed, as unverified, in
`MODEL_USE_DISCLOSURE.md`.

**Execution pipeline.** The agent wrote and ran a numbered pipeline:

| Script | Role |
|---|---|
| `src/01_verify_duplicates_primary.py` | Duplicate audit, path A (pandas) |
| `src/02_verify_duplicates_independent.py` | Duplicate audit, path B (pure Python + exact rationals) |
| `src/03_compare_and_report.py` | Reconciliation of 48 targets |
| `src/04_negative_controls.py` | Enumerated fixtures and negative controls |
| `src/05_analysis_primary.py` | Six ITT contrasts, CIs, Holm |
| `src/06_balance_and_robustness.py` | Balance, R2–R6 |
| `src/07_analysis_independent.py` | Second-path recomputation (VT-3) |
| `src/08_reconcile_and_report.py` | Reconciliation, VT-1…VT-10, integrity |
| `src/run.sh` | Evidence-preserving wrapper (timestamped logs, exit codes, failure copies) |

**AGENTS.md rules and how they were operationalized.** Compliance is assessed
against evidence, including violations.

| Rule | Status | Evidence / caveat |
|---|---|---|
| 1. Never modify `data/raw/` | **Met** | SHA-256 logged before/after every run; constant across all runs |
| 2. Print row counts after every filter/merge/drop | **Met** | `pipeline_log.csv` records loads and the dedup illustration; VT-1 checks 30 events |
| 3. Every number traceable to `results/` + script | **Met** | Each report names its CSV and generating script; VT-8 reconciles quoted numbers |
| 4. Follow `plan.md`; ask before changes; list choices | **Met with caveat** | Plan v1.1's confirmatory family and specified robustness checks followed; §14 choice register. The exploratory set was not fully reported: no Mens-vs-Womens or subgroup estimates appear in `results/`. VT-9/VT-10 were added later as verification tests, not method changes |
| 5. Fix seeds; log prompt, output, model name of every model call | **Partial** | Bootstrap seed 42; statistical models logged in `model_log.md`. **No AI model/prompt logging exists** |
| 6. No causal claims unless the design supports them | **Violated once, corrected** | M8; corrected in `30f1c5f` |
| 7. Explain method, assumptions, fit before analysis | **Met** | `plan.md` §5 pins formulas, estimands and assumptions |
| 8. Never silently remove observations/variables | **Met** | Withdrawn spend > 475 exclusion documented; dedup only an illustration; row prints |
| 9. Save enough to reproduce each main result | **Met** | CSVs, formulas, logs, tagged commits; partial external coverage (§F) |
| 10. Report missing data, outliers, n, limitations | **Met** | 0 missing; 12 × spend = 499 retained; A1–A4 listed |
| 11. No correlation-as-causation without identification | **Violated once, corrected** | Same event as rule 6 (M8) |
| 12. Record errors, cause, correction, re-test | **Met** | `mistakes.md`; one re-test (E4) remains unresolved and is marked |
| 13. Do not claim a test passed unless executed and inspected | **Met in final artifacts** | Logs and exit codes match claims; early 2026-11-05 failure log is lost (R1) |
| 14. Record exact model identifier and execution details | **Not met** | No verified AI model identifier; a runtime-reported identity is disclosed as unverified in `MODEL_USE_DISCLOSURE.md` |

The gap on rules 5 and 14 is itself a documented finding, not an omission from
this README: the repository records the **statistical** models but not the
**AI** model, prompts, or call timestamps. Any claim about "the model" is
therefore limited to the runtime-reported identifier.

---

## D. Statistical Methodology

The methods below are exactly those implemented in `src/05`–`src/08`. The full
specification, including formulas and analysis choices, is in `plan.md` §4–§9
and §14.

### D.1 Estimands

For each treatment arm `a` versus No E-Mail:

```
Δ_visit = P(visit | arm a) − P(visit | No E-Mail)          [risk difference]
Δ_conv  = P(conversion | arm a) − P(conversion | No E-Mail) [risk difference]
Δ_spend = E[spend | arm a] − E[spend | No E-Mail]           [USD per randomized customer]
```

Spend includes the 63,422 zero-spend customers; zero-inflation is part of the
estimand. Relative uplift (arm mean / control mean − 1) is reported only as a
secondary description and is never the primary scale.

### D.2 Primary tests (six confirmatory contrasts)

**Difference in proportions.** With `p̂_a = x_a / n_a`:

```
d = p̂_1 − p̂_0
SE(d) = sqrt[ p̂_1(1 − p̂_1)/n_1 + p̂_0(1 − p̂_0)/n_0 ]   (unpooled)
z = d / SE(d)
two-sided p = 2 · (1 − Φ(|z|))
95% CI = d ± 1.959963984540054 · SE(d)
```

This is a normal-approximation (Wald) interval based on the unpooled standard
error.

**Spend.** Welch two-sample t-test:

```
t = (x̄_1 − x̄_0) / sqrt(s_1²/n_1 + s_0²/n_0)      (s² with ddof = 1)
ν = (s_1²/n_1 + s_0²/n_0)² /
    [ (s_1²/n_1)²/(n_1 − 1) + (s_0²/n_0)²/(n_0 − 1) ]   (Welch–Satterthwaite)
95% CI = (x̄_1 − x̄_0) ± t_{0.975, ν} · sqrt(s_1²/n_1 + s_0²/n_0)
```

The script cross-checks the manual formula against
`scipy.stats.ttest_ind(equal_var=False)` to 1e-9.

**Multiplicity.** Holm step-down over the family of **6** tests (2 arms × 3
outcomes), two-sided α = 0.05:

```
order p_(1) ≤ … ≤ p_(6)
adjusted p̃_(i) = max_{j ≤ i} [ min(1, (6 − j + 1) · p_(j)) ]
reject H_i iff p̃_(i) < 0.05
```

The adjusted p-values are independently recomputed from the saved raw p-values
(VT-4).

### D.3 Balance

Standardized mean differences for the five numeric covariates, pooled-SD form:
`SMD = (x̄_arm − x̄_all) / s_all`. Maximum |SMD| across the balance table is
**0.0047**. Balance is diagnostic and non-gating: it is consistent with
randomization but cannot prove it.

### D.4 Robustness analyses

All retain all 64,000 rows except R1, which is explicitly an illustration, not
an estimate.

| ID | Analysis | Status |
|---|---|---|
| R1 | Deduplication (57,438 rows) | Illustration of a potentially invalid data-processing decision; **not** an alternative estimate |
| R2 | Covariate-adjusted OLS: linear probability models for visit/conversion, OLS for spend; HC1 SEs; adjustment set = recency, history, mens, womens, newbie, zip dummies, channel dummies | Approximate re-expression of the same ITT contrasts |
| R3a | Welch difference in `log1p(spend)` | Transformed-outcome estimand; log points, not percent |
| R3b | Two-part decomposition of the mean-spend difference | Exact arithmetic identity with midpoint weights; not causal mediation |
| R4 | Benjamini–Hochberg FDR at q = 0.05 | Beside Holm FWER |
| R5 | Bootstrap 95% CI for spend: 10,000 resamples, seed 42, arm-stratified, percentile | Beside the Welch CI |
| R6 | Funnel-stage quantities (conversion among visitors, spend among converters) | **Descriptive only** (post-treatment conditioning) |

The R3b identity is:

```
ΔE[spend] = ΔP(conversion) × (m1 + m0)/2 + ((p1 + p0)/2) × (m1 − m0)
```

where `p_a` is the conversion probability and `m_a` the mean spend among
converters in arm `a`. `term1` is the conversion-rate component; `term2` is the
conditional-spend component. Both are USD per randomized customer. The split is
an arithmetic identity: it does **not** separately identify causal mechanisms,
and `term2` conditions on a post-treatment outcome, so it is descriptive only.
The shares depend on the weighting convention; midpoint weights are the plan
choice, and control-side or treated-side weights give different shares for the
same total.

### D.5 Causal boundary

Under random assignment, the six primary contrasts and the other pairwise
assignment contrasts have a causal ITT interpretation. Quantities conditioned
on post-treatment variables — conversion among visitors, spend among
converters, funnel-stage quantities — are **descriptive only**. This boundary is
stated in `plan.md` §3 and §9 and is enforced in the write-up.

### D.6 Pre-registration status

`plan.md` v1.1 was finalized **before the main analysis was executed**, but **after**
preliminary descriptive results had been observed in the verification phase:
arm sizes, outcome rates and means per arm, Mens-vs-No descriptive contrasts,
and deduplicated-sample variants. Those quantities are disclosed in `plan.md`
§0. This is therefore an **analysis plan finalized before main execution**, not
a fully prospective preregistration. The formal test statistics, p-values,
confidence intervals, Holm adjustments, balance SMDs, and robustness estimates
were unobserved when the plan was finalized.

### D.7 Software environment

Python ≥ 3.13; `pandas`, `numpy`, `scipy`, `statsmodels` (OLS/HC1),
`matplotlib`; dependencies pinned in `pyproject.toml` and `uv.lock`. All
computations are deterministic except the bootstrap, which uses seed 42.

---

## E. Main Findings and Business Interpretation

### E.1 The six confirmatory contrasts

All 64,000 randomized rows retained; no rows dropped.

**Probability outcomes**

| Contrast | Outcome | Probability difference | Percentage points | 95% CI (pp) | Holm p |
|---|---|---:|---:|---|---:|
| Mens − No E-Mail | visit | +0.076590 | **+7.6590** | [+6.9954, +8.3226] | 1.62e-112 |
| Mens − No E-Mail | conversion | +0.006805 | **+0.6805** | [+0.5000, +0.8610] | 5.88e-13 |
| Womens − No E-Mail | visit | +0.045233 | **+4.5233** | [+3.8894, +5.1572] | 9.61e-44 |
| Womens − No E-Mail | conversion | +0.003111 | **+0.3111** | [+0.1499, +0.4723] | 0.000312 |

**Spending**

| Contrast | Estimate (USD per randomized customer) | 95% CI (USD) | Holm p |
|---|---:|---|---:|
| Mens − No E-Mail | **+0.769827** | [+0.485140, +1.054515] | 3.49e-07 |
| Womens − No E-Mail | **+0.424412** | [+0.168957, +0.679868] | 0.00113 |

**Relative uplift** (secondary description; arm mean / control mean − 1):

| Contrast | Visit | Conversion | Spend |
|---|---:|---:|---:|
| Mens vs No E-Mail | +72.1% | +118.8% | +117.9% |
| Womens vs No E-Mail | +42.6% | +54.3% | +65.0% |

Relative percentages are not percentage points. They are large partly because
the control baselines are small (visit 10.62%, conversion 0.5726%, mean spend
$0.65). The absolute effects are the primary scale.

### E.2 Statistical significance, effect size, business significance

**Statistical significance** is decided only by Holm-adjusted p < 0.05. All six
contrasts pass. With n = 64,000, even small effects can be estimated precisely,
so significance alone is not a business verdict.

**Effect size** is reported in the outcome's natural unit: percentage points for
visit and conversion, USD per randomized customer for spend. In this sample the
Men's point estimates are larger than the Women's — about 1.7× on visit, 1.8×
on spend, and 2.2× on conversion. That is a comparison of estimated magnitudes,
not a statistically established between-campaign difference: the six
confirmatory tests are each campaign versus No E-Mail; `plan.md` lists a
Mens-vs-Womens contrast only as exploratory, and no such estimate is reported
in `results/`.

**Business significance** cannot be fully assessed from this dataset. There is
no campaign cost, margin, or customer-lifetime-value information (A4), so a
profitability threshold cannot be computed. A +$0.77 spend effect per
randomized customer is meaningful only relative to the cost of the campaign and
the margin on incremental purchases. The correct conclusion is therefore:
**both campaigns increase the measured outcomes; whether either is profitable is
not identified here.**

### E.3 Robustness concordance

| Check | Result |
|---|---|
| R2 adjusted OLS (HC1) | Same sign and similar size on each outcome's own scale; e.g. Mens visit +0.076017 vs primary +0.076590; Mens spend +0.766430 vs +0.769827; Womens spend +0.425770 vs +0.424412 |
| R3a `log1p(spend)` | Mens +0.029241 log points (p = 1.08e-12); Womens +0.014209 (p = 0.000138) |
| R3b decomposition | Mens term1 ≈ +100.6%, term2 ≈ −0.6%; Womens term1 ≈ +86.5%, term2 ≈ +13.5% (midpoint weights; ≈16.4% for Womens term2 under control-side weights) |
| R4 BH-FDR | All six reject at q = 0.05; agrees with Holm |
| R5 bootstrap | Mens [+0.486360, +1.058330]; Womens [+0.171673, +0.681706]; percentile intervals are highly similar to the Welch intervals and substantially overlapping (endpoints ≈$0.001–$0.004 higher; neither interval contains the other) |
| Balance | max \|SMD\| = 0.0047; no evidence against randomization |
| R1 deduplication | Spend contrast +0.769827 → +0.851223; illustration only, not an estimate |
| R6 funnel | Descriptive only; no causal interpretation |

The decomposition is the clearest example of why "the numbers agree" is not the
same as "the interpretation is right." The identity is exact for both arms, but
the Womens conditional-spend contribution is not "essentially zero": it is
+$0.057467, about 13.5% of the total (up to ≈16.4% under alternative weights).
The corrected R3 section states the formula, the units, the shares, the
weighting dependence, and the descriptive status of `term2`.

The R5 percentile intervals do not enclose the Welch intervals. In both arms
their endpoints sit slightly higher while their widths are nearly identical, so
they are best described as highly similar and substantially overlapping, not as
bracketing. That wording is now used in the generated
`reconciliation_report.md` and its source line in
`src/08_reconcile_and_report.py`; the source correction and regeneration are
preserved in commit `366b4af`. Re-running the report through `src/run.sh` left
VT-1…VT-10 + INT at 11/11 PASS, and every substantive statistical CSV
byte-identical (see `mistakes.md` §M10).

### E.4 What the results do and do not support

**Supported (under A1–A3):** assignment to either campaign increases visit
probability, conversion probability, and mean spending relative to no email,
over the observed window.

**Not a tested difference:** in this sample the Men's estimated absolute
effects are larger than the Women's on all three outcomes (about 1.7× visit,
1.8× spend, 2.2× conversion). The six confirmatory tests are each
campaign versus No E-Mail; no Mens-vs-Womens estimate is reported in
`results/` (`plan.md` lists that contrast only as exploratory), so this is not
a statistically established between-campaign difference.

**Not supported:** that the campaigns are profitable; that the effects come from
email content, opens, or reads; that the effects persist beyond the window;
that the decomposition components are causal mechanisms; that the effects
generalize to other populations, seasons, or campaign designs.

---

## F. Verification Framework

Verification is layered, and the layers are not equivalent. This README never
uses the label "independently verified" for the completed work.

### F.1 Layer 1 — agent-authored automated tests

`src/08_reconcile_and_report.py` runs VT-1…VT-10 plus an integrity check (INT).
Final run `.20261118T143125Z` (run ID `m10-source-fix-2026-11-18`):
**11/11 PASS**.

| ID | What it checks | Verdict |
|---|---|---|
| VT-1 | Row-count integrity; no silent drops/filters (30 pipeline events; source scan) | PASS |
| VT-2 | Spend identity per arm: mean = P(conversion) × mean \| conversion (1e-9) | PASS |
| VT-3 | Second-path recomputation of six contrasts (max deviation 3.331e-16; tolerance 1e-9) | PASS |
| VT-4 | Holm envelope recomputed from raw p-values (1e-12) | PASS |
| VT-5 | Balance table recomputed from `data/raw` (15 SMDs, 1e-9) | PASS |
| VT-6 | Funnel assertions + corrupted-fixture negative test (0 real violations; 1 fixture detected) | PASS |
| VT-7 | Language audit of write-up artifacts (0 forbidden phrases) | PASS |
| VT-8 | Write-up numbers reconcile with `primary_results.csv` (6/6, 5e-7) | PASS |
| VT-9 | Unit/scale consistency: pp = 100 × probability difference; 6 rows + 6 report lines; original bad label detected | PASS |
| VT-10 | R3 decomposition: fresh recomputation, identity, shares, required caveats, R3-specific mechanism language, negative controls | PASS |
| INT | `data/raw` SHA-256 constant across all analysis runs (21 log rows) | PASS |

VT-7 and VT-10 are **language checks**. They are supplementary nets: they can
detect missing caveats or banned phrases, but they cannot judge whether a
sentence is causally valid. VT-10 says this in its own artifact.

### F.2 Layer 2 — separate AI computational audits

Two audits were performed independently of the analysis scripts:

| Audit | Date | Scope | Result |
|---|---|---|---|
| `human_verification/independent_primary_audit.md` (+ `.csv`) | 2026-11-12 | Six primary contrasts: estimate, SE, CI, raw and Holm p | All match to numerical precision (max \|Δ\| 3.33e-16); identified the M6 unit-label error |
| `human_verification/independent_robustness_audit.md` | 2026-11-18 | R2 OLS coefficients/SE/CI/p; R3a log1p Welch; R3b decomposition terms | All match at floating-point precision; identified the M8 interpretive overreach |

These are **separate AI computational audits**, not human audits. Neither file
names its author or model. Their independence is from the analysis scripts, not
from AI assistance.

### F.3 Coverage: what was externally recomputed, what was not

| Result | Externally recomputed? | Verification route |
|---|---|---|
| Six primary contrasts (estimate, SE, CI, raw/Holm p) | **Yes** | Audit 1; max \|Δ\| 3.33e-16 |
| R2 OLS coefficients, HC1 SEs, CIs, p | **Yes** | Audit 2; floating-point match |
| R3a `log1p(spend)` Welch tests | **Yes** | Audit 2 |
| R3b decomposition terms | **Yes** | Audit 2 |
| Balance / 15 SMDs | **No** | Agent-authored VT-5 only |
| BH-adjusted p-values | **No** | Agent-authored only |
| Bootstrap CIs | **No** | Agent-authored only |
| Funnel / R6 descriptives | **No** | Agent-authored only |
| R1 deduplication quantities | **No** | Agent-authored verification artifacts |
| VT-1…VT-10 themselves | **No** | Agent-authored; not externally reviewed |

### F.4 Layer 3 — human verification protocol (pending)

`VERIFICATION_PROTOCOL.md` defines three stages:

1. **Blinded recomputation** by a named human reviewer, using the data hash,
   the hand-checkable fixtures, and the expected-value table, with the agent's
   scripts withheld.
2. **Comparison and sign-off**, with any mismatch quarantined and re-opened in
   `mistakes.md`.
3. **Unblinding and code review** of method, not re-derivation.

No stage has been completed. The repository therefore claims **agent-authored
verification plus separate AI computational audits**, not independent human
validation.

### F.5 Evidence preservation

- Tag `v0.1-verification-baseline` (`7d0c9c5`): pre-analysis verification state.
- Tag `pre-unit-label-fix` (`86eb4fe`): preserves the M6 labels verbatim.
- Tag `pre-r3-interpretation-fix` (`f71ea24`): preserves the M8 claim verbatim.
- `results/logs/exit_codes.csv`: 21 wrapper-era runs (17 exit 0, 4 exit 1),
  with timestamped logs and 3 preserved failure copies.
- `git diff` between a pre-correction tag and the correction commit is the
  auditable record of exactly what changed.

---

## G. Selected Error Case Studies

Five cases illustrate the range of failure modes. Full entries and evidence are
in `mistakes.md` and `docs/error_taxonomy.md`.

### G.1 Duplicate-row reasoning error (E1)

- **Original claim:** "Duplicate rows: keep all 64,000 (individuals,
  recommended) vs. deduplicate. Affects SEs only; needs your call."
- **Detection:** human-directed review round, 2026-11-05; recomputation against
  the full and deduplicated samples.
- **Evidence:** `results/verification/dup_comparison.csv`, `dup_pathA.csv`,
  `dup_pathB.csv`; `verification_log.md`; commit `7d0c9c5`.
- **Why it was wrong:** the duplicated rows are almost entirely zero-outcome
  rows, so removing them re-weights the sample. Deduplicated minus full:
  visit +0.002139, conversion +0.000720, spend +0.081396 (≈10.6% of the
  spend contrast). Point estimates move, not just SEs.
- **Correction:** primary analysis on all 64,000 rows; deduplication retained
  only as a labeled illustration of a potentially invalid data-processing
  decision.
- **Re-test:** 48/48 reconciliation targets PASS on both paths; cross-path
  maximum deviation 3.3e-16.
- **Lesson:** dropping rows can change the estimand's composition, not merely
  its precision. "Affects SEs only" is a substantive statistical claim that
  needs checking.

### G.2 Verification-fixture construction errors (E7–E10)

- **Original errors:** (E7) a closed form with denominators of 9,700 that could
  never arise from the stated 10,000-customer arms (true Δ = 0, not ≈0.0294);
  (E8) a control mean of 0.2 computed from a phantom fifth row (actual 0.25);
  (E9) a claim of 6 unique rows and Δ = −25 when identical zero-rows collapse to
  5 unique rows and Δ = −125/3; (E10) an invariance argument applied to
  indistinguishable originals, where deduplication keeps 2 and 1 rows, not 3
  and 3.
- **Detection:** human-directed review, 2026-11-05; each fixture was checked
  against its enumerated rows.
- **Evidence:** `mistakes.md` §7–§10; `src/fixtures/nc1_visit.csv`,
  `nc2_spend.csv`, `pc1_invariance.csv`; `dup_negative_controls.csv`.
- **Why they were wrong:** the fixtures were designed narratively rather than
  derived from the actual enumerated rows, and the uniqueness/distinctness
  conditions required for full-row deduplication were not stated.
- **Correction:** small, enumerated fixtures with pre-specified exact expected
  values (pinned as literals before execution) and distinguishable originals; a
  corrupted-fixture negative test.
- **Re-test:** Δ = −1/5, −0.2, −25, 0; sizes 6/6 → 3/3; SE ratio 1/√2 within
  1e-12; 37/37 instrument checks PASS.
- **Lesson:** a verification test that cannot fail proves nothing. Fixtures need
  exact pre-specified values, explicit distinctness assumptions, and a negative
  control that must fail.

### G.3 M6 — probability versus percentage-point labeling

- **Original statement:** `+0.076590 pp` for the Mens visit effect, with
  analogous labels for Mens conversion (+0.006805), Womens visit (+0.045233)
  and Womens conversion (+0.003111), in `primary_results.md` and
  `reconciliation_report.md`.
- **Detection:** separate AI computational audit, 2026-11-12. The audit
  reproduced every number to 3.33e-16 and isolated the defect to the unit
  label.
- **Evidence:** tag `pre-unit-label-fix` (`86eb4fe`); audit
  `independent_primary_audit.md`; `mistakes.md` §M6.
- **Why it was wrong:** one percentage point = 0.01 in probability, so
  `pp = 100 × d`. The label understated the effects by a factor of 100:
  +0.076590 is +7.6590 pp, not +0.076590 pp.
- **Correction:** dual reporting — probability difference and percentage
  points, CIs converted by the same factor, spend labeled USD per randomized
  customer.
- **Re-test:** VT-9 added: 6 table rows + 6 report lines verified; the original
  bad label is detected as a negative control; all substantive CSVs
  byte-identical; commit `2f87409`.
- **Lesson:** correct arithmetic with the wrong unit passes every numeric test.
  Units must be tested against magnitudes, separately from the numbers.

### G.4 M8 — arithmetic decomposition versus causal interpretation

- **Original statement:** "converter-spend differences are essentially zero
  (−$0.0043 / +$0.0575) — the spend effect is driven by more converters, not
  higher spend per converter."
- **Detection:** separate AI computational audit, 2026-11-18. The audit
  reproduced the OLS, log1p and decomposition numbers at floating-point
  precision and flagged the interpretation: the decomposition is an arithmetic
  identity, not a causal mediation analysis; mean spend among converters
  conditions on a post-treatment outcome.
- **Evidence:** dated evidence record in commit `f71ea24` (tag
  `pre-r3-interpretation-fix`); `independent_robustness_audit.md`;
  `mistakes.md` §M8.
- **Why it was wrong:** "driven by" asserts a mechanism the design does not
  identify. "Essentially zero" is valid for Mens (−$0.004343, ≈−0.6%) but not
  for Womens (+$0.057467, ≈13.5% under midpoint weights; ≈16.4% under
  control-side weights). The pre-correction R3 section also omitted the
  plan-mandated descriptive caveat.
- **Correction:** R3 rewritten with the explicit midpoint identity, component
  units and shares, the weighting-convention note, and the statement that this
  is an arithmetic identity, not a causal mediation analysis.
- **Re-test:** VT-10 added: fresh recomputation from `data/raw` (≤1e-9),
  identity check, six displayed values/shares, required caveats, R3-specific
  mechanism-language check, and negative controls. 11/11 PASS; substantive CSVs
  byte-identical; commit `30f1c5f`.
- **Lesson:** an arithmetic identity is not a causal explanation. Numerical
  agreement cannot validate the sentence wrapped around the number.

### G.5 M7 — logging and reproducibility failure

- **Original behavior:** `src/05` wrote `model_log.md` with `Path.write_text`
  (full overwrite), while `src/06` appended its section. Rerunning 05 after 06
  deleted the R2 statsmodels record.
- **Detection:** manual diff inspection during the M6 correction.
- **Evidence:** `results/analysis/model_log.md`; `mistakes.md` §M7.
- **Why it mattered:** no statistical output changed, but the provenance record
  for a model call was lost — a rule 5 failure caused by asymmetric write
  modes, not by a numerical bug.
- **Correction:** initially an operational rule (rerun 06 before publishing);
  later enforced in code with an idempotent `upsert_model_log()` in both 05 and
  06, so each script replaces only its own section.
- **Re-test:** rerunning 05 alone leaves the 06 section intact (one copy);
  rerunning 06 alone creates no duplicate; 11/11 PASS.
- **Lesson:** logging is part of reproducibility. Append/overwrite asymmetry is
  a provenance bug waiting for an out-of-order rerun.

---

## H. Critical Reflection

**What went wrong.** The agent produced a complete, numerically reproducible
analysis, but the record contains 22 confirmed error items across five
categories. Two consequential errors were not computational. The
duplicate-row error (E1) was a statistical-reasoning error: "affects SEs only"
was false, and the deduplicated spend contrast moved by ≈10.6%. The fixture
errors (E7–E10) were verification-design errors: several controls were built so
that they could not prove what they claimed. M6 was a unit error: the numbers
were right, the label was wrong by a factor of 100, so a 7.66-percentage-point
effect appeared as 0.0766 "pp". M8 was an interpretation error: an exact
arithmetic identity was described as a causal mechanism ("the spend effect is
driven by more converters"), when the conditional-spend component was
post-treatment and descriptive, and the Womens contribution was not
"essentially zero." M7 was a provenance error: rerunning one script deleted
another script's model-log section.

**Why they occurred.** For E1, the evidence is that duplicated rows are
overwhelmingly zero-outcome rows, so deduplication reweights the sample; the
hypothesis is that the agent conflated precision (SEs) with composition (point
estimates). For the fixtures, the evidence is arithmetic: the stated
denominators and counts do not match the enumerated rows; the hypothesis is that
the examples were designed narratively without re-deriving them from the row
list. For M6, the evidence is code-level: the formatting layer attached "pp" to
a probability-scale number, and no test bound units to magnitudes. For M8, the
evidence is textual and numerical: the identity is exact, but the prose used
mechanism language and omitted the post-treatment caveat; the hypothesis is
that the agent read an arithmetic decomposition as a causal one. For M7, the
evidence is the asymmetric write modes; the hypothesis is that out-of-order
reruns were not considered. These hypotheses are interpretations, not proven
mental states.

**How they were detected.** Implementation and test-code defects announced
themselves: a `KeyError`, a `SyntaxError`, a parser matching zero rows, a
negative control that never triggered. They produced non-zero exits and were
preserved in `results/logs/`. The statistical and interpretive defects did not.
E1 and the fixture errors were caught in human-directed review. M6 and M8 were
caught by separate AI computational audits that recomputed the numbers and read
the claims; the agent's existing tests passed in both cases. M7 was caught by
manual diff inspection. No automated test caught a semantic overclaim.

**What was corrected and how it was tested.** E1: primary analysis on all rows,
dedup as illustration; 48/48 targets, 3.3e-16. Fixtures: enumerated,
pre-specified exact values (pinned before execution); Δ = −1/5, −0.2, −25, 0; SE ratio 1/√2; 37/37
instrument checks. M6: dual reporting; VT-9 + negative control; CSVs
byte-identical. M8: R3 rewrite + VT-10 + negative controls; 11/11; CSVs
byte-identical. M7: idempotent upsert; single-script reruns verified. Every
re-test passed on the corrected case.

**What this does and does not show.** It shows effective **local correction**:
each specific defect was fixed, re-executed, and, where applicable, guarded by a
new test with a negative control. It does **not** show general improvement. The
error classes did not decline monotonically — the observed sequence ran
statistical → fixture-design → implementation → verification-format →
reporting-unit → interpretation → test-construction. Each phase surfaced a new
kind of defect. No prospective,
held-out test of the agent's behavior was run. The durable change is the
**detection surface**: tagged pre-correction snapshots, timestamped failure
logs, VT-9/VT-10 with negative controls, and idempotent logging. Those make the
next error easier to see; they do not prove the agent will see it.

**The division of labour.** Automated checks are good at consistency, identities,
units, reproducibility, and loud failure. They are weak at semantics: whether a
sentence overclaims, whether an identity is being read causally, whether a
weighting convention is disclosed. Phrase-based language checks (VT-7, VT-10)
are a net, not a proof; VT-10 says so in its own artifact. Human methodological
judgment remains necessary for estimand choice, multiplicity, decomposition
interpretation, and business relevance.

**A transparency gap in the project itself.** `AGENTS.md` required logging the
model name, prompt, and output of every model call. The repository does not
contain a verified AI model identity, a prompt log, or model-call timestamps;
the two external audits do not name their models. This is disclosed in
`MODEL_USE_DISCLOSURE.md`, not papered over. Two separate AI audits are not a
human audit, and this README does not describe them as one. The human protocol
remains pending.

---

## I. Limitations

**Evidence and verification**

- The two external audits are **separate AI computational audits**, not human
  audits. Their authors and models are unrecorded.
- Audit coverage is partial: the six primary contrasts and the R2/R3 robustness
  outputs were externally recomputed; balance, BH, bootstrap, funnel, R1 and the
  VT tests themselves were not.
- No fully independent human audit has been completed. `VERIFICATION_PROTOCOL.md`
  Stages 1–3 are pending.
- VT-7 and VT-10 are phrase-based language checks and cannot validate causal
  reasoning. They are supplementary.
- The 2026-11-05 first-run failure logs for `src/04` were overwritten before the
  wrapper existed and are irrecoverable (§R1). No evidence was fabricated.
- E4 ("36,288 cells") was withdrawn but no replacement recomputation is
  recorded; the number was never used in any result.
- No verified AI model identity, prompt log, or model-call timestamp record
  exists; see `MODEL_USE_DISCLOSURE.md`.

**Data and design**

- Provenance as the Hillstrom dataset is unverified; no redistribution rights
  are claimed.
- One row = one distinct customer is unverified; duplicate collisions are
  consistent with either distinct customers or copied rows.
- Randomization and the two-week window rest on external documentation;
  covariate balance is consistent with randomization but cannot prove it.
- SUTVA / no interference is assumed.
- The spend = 499.00 cap interpretation is unverified.
- There is no cost, margin, or lifetime-value data, so no profitability or
  long-run verdict is possible.
- The analysis is a single experiment, single window, and one population; it
  does not establish external validity.
- Deduplicated counts are counts of distinct rows and may undercount distinct
  customers when rows are indistinguishable.

**Interpretation**

- Statistical significance is not business significance; with n = 64,000,
  precise small effects are expected.
- The R3b decomposition shares depend on the weighting convention; midpoint
  weights are the plan choice, not a unique answer.
- `log1p(spend)` is a transformed-outcome estimand, not a percentage revenue
  uplift.
- The agent's local corrections are not evidence of general reliability on new
  tasks.

---

## J. Reproducibility

### J.1 Environment

- Python ≥ 3.13.
- Dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`
  (`pyproject.toml`, `uv.lock`).
- From the repository root:

```bash
uv sync
```

This creates/uses `.venv` and installs the pinned environment. The repository
was developed with `uv` 0.13.7; `uv lock --check` confirms that `uv.lock` is
consistent with `pyproject.toml`. If `uv` is not on your `PATH`, install it
from its official distribution or invoke it by absolute path.

### J.2 Data acquisition and integrity

The raw dataset is **not** distributed in this repository, and no download URL
or license is asserted. Reproducing the numerical results in `results/`
requires the **exact** file whose SHA-256 matches the digest below. A file with
the same schema, column names, or row count is not sufficient. The repository
does not supply, link to, or guarantee access to that file; obtaining it from a
source you are entitled to use is the reviewer's responsibility. The schema is
consistent with the Hillstrom "MineThatData" email dataset (64,000 customers,
three arms, 12 columns), but provenance is unverified.

Place the file at:

```
data/raw/hillstorm_no_indices.csv
```

Verify the SHA-256 before running anything:

```bash
# macOS
shasum -a 256 data/raw/hillstorm_no_indices.csv

# Linux
sha256sum data/raw/hillstorm_no_indices.csv
```

Expected digest:

```
00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0
```

If the digest differs, stop: the analysis is not reproducible against this
record. The raw file is never modified by any script (AGENTS.md rule 1).

### J.3 Run order

All runs go through the evidence-preserving wrapper:

```bash
src/run.sh 01_verify_duplicates_primary.py verify-rerun
src/run.sh 02_verify_duplicates_independent.py verify-rerun
src/run.sh 03_compare_and_report.py verify-rerun
src/run.sh 04_negative_controls.py verify-rerun

src/run.sh 05_analysis_primary.py main-rerun
src/run.sh 06_balance_and_robustness.py main-rerun
src/run.sh 07_analysis_independent.py main-rerun
src/run.sh 08_reconcile_and_report.py main-rerun
```

The wrapper writes a timestamped log per run to `results/logs/`, appends the
exit code to `results/logs/exit_codes.csv`, and preserves non-zero exits as
`*_first_run_fail.<timestamp>.txt`. Logs are never overwritten.

**Expected result of the final step:** VT-1…VT-10 plus INT all PASS
(`[summary] VT checks: 11/11 PASS`) and
`[summary] ALL CHECKS PASS — analysis artifacts complete for human review`.

Rerunning regenerates the artifacts in `results/verification/` and
`results/analysis/` and appends to the logs. Compare the regenerated
substantive CSVs with the committed versions; the raw data hash must stay
constant. The 2026-11-18 corrections left every substantive statistical CSV
byte-identical.

### J.4 Hand-checkable fixtures

The fixtures in `src/fixtures/` are small enough to verify by hand:

| Fixture | Rows | Purpose |
|---|---:|---|
| `nc1_visit.csv` | 10 | Deduplication contrast change (Δ = −1/5) |
| `nc2_spend.csv` | 8 | Uniqueness/distinctness (Δ = −25) |
| `nc3_collision.csv` | 3 | Collision caveat (Δ = +1/6) |
| `pc1_invariance.csv` | 12 | Invariance with distinguishable originals (Δ = 0; SE ratio 1/√2) |

### J.5 Reproducing a pre-correction state

```bash
git checkout pre-unit-label-fix        # M6 labels preserved verbatim
git checkout pre-r3-interpretation-fix # M8 claim preserved verbatim
git checkout main
```

These are annotated tags. `git diff <tag>..<correction-commit>` shows exactly
what changed. Do not run analysis scripts from a detached pre-correction state
unless you intend to reproduce the historical artifacts.

---

## K. Repository Structure

```
.
├── AGENTS.md                     # 14 governing rules
├── README.md                     # this file
├── MODEL_USE_DISCLOSURE.md       # verified / reported / unknown model identities
├── plan.md                       # approved analysis plan v1.1
├── mistakes.md                   # verbatim error record and re-tests
├── VERIFICATION_PROTOCOL.md      # pending human blinded-verification protocol
├── pyproject.toml
├── uv.lock
├── data/
│   ├── raw/                      # hillstorm_no_indices.csv — excluded by .gitignore
│   └── derived/                  # empty placeholder
├── docs/
│   └── error_taxonomy.md         # non-overlapping error classification
├── src/
│   ├── 01_verify_duplicates_primary.py
│   ├── 02_verify_duplicates_independent.py
│   ├── 03_compare_and_report.py
│   ├── 04_negative_controls.py
│   ├── 05_analysis_primary.py
│   ├── 06_balance_and_robustness.py
│   ├── 07_analysis_independent.py
│   ├── 08_reconcile_and_report.py
│   ├── run.sh
│   └── fixtures/
│       ├── nc1_visit.csv
│       ├── nc2_spend.csv
│       ├── nc3_collision.csv
│       └── pc1_invariance.csv
└── results/
    ├── verification/             # duplicate-row audit, controls, consoles, logs
    ├── analysis/                 # primary/robustness CSVs, reports, VT results
    │   └── human_verification/   # two separate AI computational audits + evidence record
    └── logs/                     # timestamped run logs, failure copies, exit_codes.csv
```

**Key artifacts**

| Path | Contents |
|---|---|
| `results/analysis/primary_results.csv` / `.md` | Six contrasts, CIs, raw/Holm p, units |
| `results/analysis/robustness.csv` / `robustness.md` | Balance, R2–R6 |
| `results/analysis/vt_results.csv` | VT-1…VT-10 + INT verdicts |
| `results/analysis/reconciliation_report.md` | Final reconciliation and limitations |
| `results/verification/dup_comparison.csv` | 48 duplicate-audit targets |
| `results/verification/dup_negative_controls.csv` | Fixture and instrument controls |
| `results/logs/exit_codes.csv` | Every wrapper-era run and exit code |
| `results/analysis/human_verification/` | Two separate AI audits + dated M8 evidence record |

---

## Citation and data-use note

No license is asserted for the raw dataset, and it is not redistributed here.
If you reuse this repository's code or documentation, cite the repository and
the commit or tag you used. The numerical results are only reproducible with
the exact file matching the SHA-256 above; that file is not distributed here,
and access to it is not guaranteed by this repository.
