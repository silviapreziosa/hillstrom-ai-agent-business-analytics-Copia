# Reconciliation and final analysis report (plan.md §10–§12)

Run date: 2026-11-12T10:16:39.844535+00:00
data/raw SHA-256 (all runs identical): 00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0

## VT-1..VT-8 + integrity results

| ID | Check | Verdict | Detail |
|---|---|---|---|
| VT-1 | row-count integrity; no silent drops/filters | PASS | 12 pipeline events; source scan clean; all 64,000 rows retained |
| VT-2 | spend identity mean = P(conv) x mean|conv (per arm) | PASS | identity holds to 1e-9 for all three arms |
| VT-3 | second-path recomputation of six contrasts | PASS | max |05-07| deviation = 3.331e-16 (tolerance 1e-9) |
| VT-4 | Holm envelope recomputed from raw p-values | PASS | agreement to 1e-12 across 6 adjusted p-values |
| VT-5 | balance table recomputed fresh from data/raw | PASS | all 15 SMD values agree to 1e-9 |
| VT-6 | funnel assertions incl. corrupted-fixture negative test | PASS | real-data violations = 0; corrupted fixture detected = 1 |
| VT-7 | language audit of write-up artifacts | PASS | 0 forbidden phrases in model_log.md, primary_results.md, reconciliation_report.md, robustness.md |
| VT-8 | write-up numbers reconcile with primary_results.csv | PASS | 6 md estimates matched to CSV within rounding (5e-7) |
| INT | data/raw sha256 constant across all analysis runs | PASS | 9 log rows, digest 00a6a868e05a9ffe... |

## Six primary ITT contrasts (full detail: primary_results.csv)

Under randomized assignment, these estimate the effect of ASSIGNMENT to
each arm relative to No E-Mail (plan.md §9). Causal interpretation is
assignment-level; no claims about email contents, opens, or long-run value.

- Mens E-Mail minus No E-Mail, visit: +0.076590 pp [+0.069954, +0.083226]; z=22.62; raw p = 2.71e-113; Holm p = 1.62e-112 — significant (Holm 0.05).
- Mens E-Mail minus No E-Mail, conversion: +0.006805 pp [+0.005000, +0.008610]; z=7.39; raw p = 1.47e-13; Holm p = 5.88e-13 — significant (Holm 0.05).
- Mens E-Mail minus No E-Mail, spend: +0.769827 $ [+0.485140, +1.054515]; t=5.30 (df=36671.2); raw p = 1.16e-07; Holm p = 3.49e-07 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, visit: +0.045233 pp [+0.038894, +0.051572]; z=13.99; raw p = 1.92e-44; Holm p = 9.61e-44 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, conversion: +0.003111 pp [+0.001499, +0.004723]; z=3.78; raw p = 0.000156; Holm p = 0.000312 — significant (Holm 0.05).
- Womens E-Mail minus No E-Mail, spend: +0.424412 $ [+0.168957, +0.679868]; t=3.26 (df=40064.9); raw p = 0.00113; Holm p = 0.00113 — significant (Holm 0.05).

## Statistical vs. business significance

- Statistical significance: Holm-adjusted p < 0.05 only (see table above).
- Business significance: magnitudes — absolute percentage points (visit,
  conversion) and dollars per contacted customer (spend), with relative
  uplift as context. The dataset contains no cost/margin information, so
  no profitability verdict is possible (limitation A4). Magnitudes are
  reported for decision-makers; they do not replace a cost-benefit model.

## Verification status and independence statement

All checks above are agent-authored cross-checks. Agreement between the two
agent-written calculation paths rules out coding slips but is NOT independent
human validation. The blinded Stage-1 review (VERIFICATION_PROTOCOL.md) and
human reasoning review (plan.md §10, §11 criterion 6) are PENDING; no
'independently verified' label is claimed.

## Robustness summary (full detail: 06 artifacts + robustness.md)

- R2 adjusted OLS (HC1) and R3 transformations are consistent with the
  primary contrasts in sign and order of magnitude (robustness.csv,
  robustness_transformations.csv).
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
