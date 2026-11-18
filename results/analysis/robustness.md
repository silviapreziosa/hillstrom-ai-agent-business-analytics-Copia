# Balance and robustness (plan.md §7–§8)

Source: results/analysis/{balance.csv,balance_shares.csv,robustness.csv,
robustness_transformations.csv,robustness_bh.csv,robustness_bootstrap.csv,
funnel_descriptive.csv} — produced by src/06_balance_and_robustness.py.
All robustness analyses retain all 64,000 rows; no customer is deleted.

## Balance (non-gating)

max |SMD| over the five numeric covariates and three arms = 0.0047;
values < 0.1 are read as no evidence against randomization (diagnostic only;
randomization itself is assumption A1). Full table: balance.csv; shares:
balance_shares.csv.

## R1 deduplication (illustration only — NOT an alternative estimate)

Cited from the committed verification artifacts (results/verification/
dup_pathA.csv, 48/48 targets PASS): the deduplicated sample shifts the
spend contrast from +0.769827 to +0.851223. This is retained as an
illustration of a potentially invalid data-processing decision (dropping
randomized individuals on an unverifiable criterion), not as an
alternative treatment-effect estimate.

## R2 covariate-adjusted OLS (HC1) — approximate re-expression

| Model | Term | Estimate | HC1 SE | 95% CI | p |
|---|---|---|---|---|---|
| OLS visit (HC1) | treat_mens | +0.076017 | 0.003338 | [+0.069474, +0.082559] | 8.49e-115 |
| OLS visit (HC1) | treat_womens | +0.045483 | 0.003193 | [+0.039226, +0.051741] | 4.69e-46 |
| OLS conversion (HC1) | treat_mens | +0.006768 | 0.000920 | [+0.004965, +0.008570] | 1.86e-13 |
| OLS conversion (HC1) | treat_womens | +0.003119 | 0.000822 | [+0.001508, +0.004730] | 0.000148 |
| OLS spend (HC1) | treat_mens | +0.766430 | 0.145104 | [+0.482032, +1.050828] | 1.28e-07 |
| OLS spend (HC1) | treat_womens | +0.425770 | 0.130259 | [+0.170467, +0.681073] | 0.00108 |

## R3 outcome transformations (no deletion)

| Pair | Analysis | Estimate |
|---|---|---|
| Mens E-Mail minus No E-Mail | R3a log1p(spend) Welch diff | +0.029241 |
| Mens E-Mail minus No E-Mail | R3b two-part: term1 Δconv × avg converter spend | +0.774170 |
| Mens E-Mail minus No E-Mail | R3b two-part: term2 avg conv rate × Δ converter spend | -0.004343 |
| Mens E-Mail minus No E-Mail | R3b two-part: total (identity check) | +0.769827 |
| Womens E-Mail minus No E-Mail | R3a log1p(spend) Welch diff | +0.014209 |
| Womens E-Mail minus No E-Mail | R3b two-part: term1 Δconv × avg converter spend | +0.366945 |
| Womens E-Mail minus No E-Mail | R3b two-part: term2 avg conv rate × Δ converter spend | +0.057467 |
| Womens E-Mail minus No E-Mail | R3b two-part: total (identity check) | +0.424412 |

## R4 Benjamini-Hochberg (beside Holm)

| Pair | Outcome | raw p | BH-adjusted | reject at q=0.05 |
|---|---|---|---|---|
| Mens E-Mail minus No E-Mail | visit | 2.71e-113 | 1.62e-112 | yes |
| Mens E-Mail minus No E-Mail | conversion | 1.47e-13 | 2.94e-13 | yes |
| Mens E-Mail minus No E-Mail | spend | 1.16e-07 | 1.75e-07 | yes |
| Womens E-Mail minus No E-Mail | visit | 1.92e-44 | 5.77e-44 | yes |
| Womens E-Mail minus No E-Mail | conversion | 0.000156 | 0.000187 | yes |
| Womens E-Mail minus No E-Mail | spend | 0.00113 | 0.00113 | yes |

## R5 bootstrap CI (spend, 10,000 resamples, seed 42)

| Pair | bootstrap mean | 95% percentile CI |
|---|---|---|
| Mens E-Mail minus No E-Mail | +0.770320 | [+0.486360, +1.058330] |
| Womens E-Mail minus No E-Mail | +0.425539 | [+0.171673, +0.681706] |

## R6 funnel-stage descriptives — DESCRIPTIVE ONLY

These condition on post-treatment outcomes (plan.md §3/§9) and carry no
causal interpretation.

| Arm | n | visitors | conv among visitors | converted | mean spend among converted |
|---|---|---|---|---|---|
| Mens E-Mail | 21307 | 3894 | 0.068567 | 267 | 113.526929 |
| No E-Mail | 21306 | 2262 | 0.053935 | 122 | 114.002705 |
| Womens E-Mail | 21387 | 3238 | 0.058369 | 189 | 121.894762 |

## Verification status

Cross-checks by src/07/08 are agent-authored; agreement rules out coding
slips but is NOT independent human validation. Human blinded review per
VERIFICATION_PROTOCOL.md is pending.
