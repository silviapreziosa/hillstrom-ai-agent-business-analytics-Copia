# Reconciliation and final analysis report (plan.md §10–§12)

Run date: 2026-11-18T13:36:39.516503+00:00
data/raw SHA-256 (all runs identical): 00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0

## VT-1..VT-10 + integrity results

| ID | Check | Verdict | Detail |
|---|---|---|---|
| VT-1 | row-count integrity; no silent drops/filters | PASS | 30 pipeline events; source scan clean; all 64,000 rows retained |
| VT-2 | spend identity mean = P(conv) x mean|conv (per arm) | PASS | identity holds to 1e-9 for all three arms |
| VT-3 | second-path recomputation of six contrasts | PASS | max |05-07| deviation = 3.331e-16 (tolerance 1e-9) |
| VT-4 | Holm envelope recomputed from raw p-values | PASS | agreement to 1e-12 across 6 adjusted p-values |
| VT-5 | balance table recomputed fresh from data/raw | PASS | all 15 SMD values agree to 1e-9 |
| VT-6 | funnel assertions incl. corrupted-fixture negative test | PASS | real-data violations = 0; corrupted fixture detected = 1 |
| VT-7 | language audit of write-up artifacts | PASS | 0 forbidden phrases in model_log.md, primary_results.md, reconciliation_report.md, robustness.md |
| VT-8 | write-up numbers reconcile with primary_results.csv | PASS | 6 md estimates matched to CSV within rounding (5e-7) |
| VT-9 | unit/scale consistency: pp = 100 x probability difference | PASS | 6 table rows + 6 report lines verified (point estimates and CIs); negative control (original '+0.076590 pp' label) detected |
| VT-10 | R3 decomposition: recomputation, shares, caveats, negative controls | PASS | fresh recomputation matches CSV (1e-9); term1+term2=total; 6 md values and shares verified; required caveats present; mechanism phrases absent from R3; negative controls detected (language checks are supplementary, not proof of causal reasoning) |
| INT | data/raw sha256 constant across all analysis runs | PASS | 21 log rows, digest 00a6a868e05a9ffe... |

## Units used in this report

- Visit and conversion: absolute effects are **probability differences** on
  the 0–1 scale; multiplied by 100 they are **percentage points** (pp).
  Confidence intervals are converted with the same factor.
- **Relative uplift** is a relative percentage change (arm mean / control
  mean − 1); it is not a percentage-point difference.
- Spend: **dollar differences in mean spending per randomized customer**
  (USD); spend effects are not percentage points.

## Six primary ITT contrasts (full detail: primary_results.csv)

Under randomized assignment, these estimate the effect of ASSIGNMENT to
each arm relative to No E-Mail (plan.md §9). Causal interpretation is
assignment-level; no claims about email contents, opens, or long-run value.

- Mens E-Mail minus No E-Mail, visit: +0.076590 (probability difference) = +7.6590 percentage points; 95% CI [+0.069954, +0.083226] (probability difference) = [+6.9954, +8.3226] percentage points; z=22.62; raw p = 2.71e-113; Holm p = 1.62e-112 — significant (Holm 0.05).
- Mens E-Mail minus No E-Mail, conversion: +0.006805 (probability difference) = +0.6805 percentage points; 95% CI [+0.005000, +0.008610] (probability difference) = [+0.5000, +0.8610] percentage points; z=7.39; raw p = 1.47e-13; Holm p = 5.88e-13 — significant (Holm 0.05).
- Mens E-Mail minus No E-Mail, spend: +$0.769827 (USD per randomized customer); 95% CI [+$0.485140, +$1.054515] (USD per randomized customer); t=5.30 (df=36671.2); raw p = 1.16e-07; Holm p = 3.49e-07 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, visit: +0.045233 (probability difference) = +4.5233 percentage points; 95% CI [+0.038894, +0.051572] (probability difference) = [+3.8894, +5.1572] percentage points; z=13.99; raw p = 1.92e-44; Holm p = 9.61e-44 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, conversion: +0.003111 (probability difference) = +0.3111 percentage points; 95% CI [+0.001499, +0.004723] (probability difference) = [+0.1499, +0.4723] percentage points; z=3.78; raw p = 0.000156; Holm p = 0.000312 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, spend: +$0.424412 (USD per randomized customer); 95% CI [+$0.168957, +$0.679868] (USD per randomized customer); t=3.26 (df=40064.9); raw p = 0.00113; Holm p = 0.00113 — significant (Holm 0.05).

## Statistical vs. business significance

- Statistical significance: Holm-adjusted p < 0.05 only (see table above).
- Business significance: magnitudes — probability differences (also given
  in percentage points) for visit and conversion, and dollars per
  randomized customer for spend, with relative uplift as context. The
  dataset contains no cost/margin information, so no profitability verdict
  is possible (limitation A4). Magnitudes are reported for decision-makers;
  they do not replace a cost-benefit model.

## Verification status and independence statement

All checks above are agent-authored cross-checks. Agreement between the two
agent-written calculation paths rules out coding slips but is NOT independent
human validation. An external computational audit
(human_verification/independent_primary_audit.md) confirmed the six
estimates and identified the M6 unit-labeling error; the blinded Stage-1
review (VERIFICATION_PROTOCOL.md) and human reasoning review (plan.md §10,
§11 criterion 6) remain PENDING; no 'independently verified' label is
claimed.

## Robustness summary (full detail: 06 artifacts + robustness.md)

- R2 adjusted OLS (HC1) reproduces the primary contrasts in sign and size
  on each outcome's own scale (probability scale for visit/conversion;
  USD for spend) (robustness.csv). Quantities on different scales are not
  compared with each other.
- R3a reports a log1p(spend) difference in log points; this is not
  comparable in magnitude to the dollar contrasts (robustness_transformations.csv).
- R3b is an exact arithmetic identity with midpoint weights: term1
  (ΔP(conversion) × average converter spend) and term2 (average conversion
  rate × Δ(mean spend among converters)) sum to the mean-spend difference.
  Components are USD per randomized customer and their shares depend on
  the weighting convention. term2 conditions on post-treatment conversion
  and is descriptive only; the split does not identify causal mechanisms.
- R4: BH-FDR conclusions agree with Holm FWER (robustness_bh.csv).
- R5: bootstrap percentile CIs bracket the Welch CIs (robustness_bootstrap.csv).
- R1: deduplication remains an illustration of a potentially invalid
  data-processing decision (see robustness.md), not an alternative estimate.
- R6: funnel-stage numbers are DESCRIPTIVE ONLY (post-treatment conditioning).

## Limitations (AGENTS.md rule 10)

- A1 (unverified): randomization and the two-week outcome window rest on
  external documentation, not on the file itself.
- A2 (unverified): one row = one distinct customer.
- A3 (unverified): no interference between customers (SUTVA).
- A4: no cost/margin data — no profitability threshold computable.
- Missing data: none (verified); outliers: 12 spend = 499.00 rows retained.
- Deduplicated counts are counts of distinct rows and may undercount
  distinct customers when rows are indistinguishable.
