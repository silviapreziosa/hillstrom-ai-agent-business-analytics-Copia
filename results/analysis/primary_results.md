# Primary ITT analysis (plan.md §4–§5)

Source: results/analysis/primary_results.csv — produced by src/05_analysis_primary.py.
Sample: all 64,000 randomized rows (21,307 / 21,306 / 21,387). No rows dropped.
Causal scope: effects of ASSIGNMENT under randomized assignment (plan.md §9).

| Contrast | Outcome | Estimate | 95% CI | z/t (df) | raw p | Holm p | Sig (Holm 0.05) | Relative uplift |
|---|---|---|---|---|---|---|---|---|
| Mens E-Mail minus No E-Mail | visit | +0.076590 pp | [+0.069954, +0.083226] | z=22.621 | 2.71e-113 | 1.62e-112 | yes | +72.1% |
| Mens E-Mail minus No E-Mail | conversion | +0.006805 pp | [+0.005000, +0.008610] | z=7.390 | 1.47e-13 | 5.88e-13 | yes | +118.8% |
| Mens E-Mail minus No E-Mail | spend | +0.769827 $ | [+0.485140, +1.054515] | t=5.300 (df=36671.2) | 1.16e-07 | 3.49e-07 | yes | +117.9% |
| Womens E-Mail minus No E-Mail | visit | +0.045233 pp | [+0.038894, +0.051572] | z=13.985 | 1.92e-44 | 9.61e-44 | yes | +42.6% |
| Womens E-Mail minus No E-Mail | conversion | +0.003111 pp | [+0.001499, +0.004723] | z=3.782 | 0.000156 | 0.000312 | yes | +54.3% |
| Womens E-Mail minus No E-Mail | spend | +0.424412 $ | [+0.168957, +0.679868] | t=3.256 (df=40064.9) | 0.00113 | 0.00113 | yes | +65.0% |

## Statistical vs. business significance

- Statistical significance is decided ONLY by Holm-adjusted p < 0.05 (column above).
- Business significance is about magnitude: absolute effects are in percentage points
  (visit/conversion) or dollars per customer (spend), with relative uplift as context.
- The data contain no cost, margin, or campaign-cost information, so a formal
  profitability threshold cannot be computed from this dataset; magnitudes are
  reported, not a profit verdict (assumption A4, recorded in the write-up).

## Verification status

Cross-checked by src/07 (agent-authored second path; agreement is a coding-slip
check, NOT independent human validation). Human blinded review per
VERIFICATION_PROTOCOL.md is pending; no 'independently verified' label is claimed.
