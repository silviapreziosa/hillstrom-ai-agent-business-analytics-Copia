# Primary ITT analysis (plan.md §4–§5)

Source: results/analysis/primary_results.csv — produced by src/05_analysis_primary.py.
Sample: all 64,000 randomized rows (21,307 / 21,306 / 21,387). No rows dropped.
Causal scope: effects of ASSIGNMENT under randomized assignment (plan.md §9).

## Units (read before quoting numbers)

- Visit and conversion effects are **probability differences** on the 0–1 scale; the
  same quantity multiplied by 100 is given in **percentage points** (pp). These are
  absolute risk differences, not relative changes.
- Relative uplift is a **relative percentage** change (arm mean / control mean − 1);
  it is a different quantity from percentage points and from probability differences.
- Spend effects are **dollar differences in mean spending per randomized customer**
  (USD), not percentage points.

| Contrast | Outcome | Estimate | 95% CI | z/t (df) | raw p | Holm p | Sig (Holm 0.05) | Relative uplift (relative %) |
|---|---|---|---|---|---|---|---|---|
| Mens E-Mail minus No E-Mail | visit | +0.076590 (probability difference) = +7.6590 percentage points | [+0.069954, +0.083226] (probability difference) = [+6.9954, +8.3226] percentage points | z=22.621 | 2.71e-113 | 1.62e-112 | yes | +72.1% |
| Mens E-Mail minus No E-Mail | conversion | +0.006805 (probability difference) = +0.6805 percentage points | [+0.005000, +0.008610] (probability difference) = [+0.5000, +0.8610] percentage points | z=7.390 | 1.47e-13 | 5.88e-13 | yes | +118.8% |
| Mens E-Mail minus No E-Mail | spend | +$0.769827 (USD per randomized customer) | [+$0.485140, +$1.054515] (USD per randomized customer) | t=5.300 (df=36671.2) | 1.16e-07 | 3.49e-07 | yes | +117.9% |
| Womens E-Mail minus No E-Mail | visit | +0.045233 (probability difference) = +4.5233 percentage points | [+0.038894, +0.051572] (probability difference) = [+3.8894, +5.1572] percentage points | z=13.985 | 1.92e-44 | 9.61e-44 | yes | +42.6% |
| Womens E-Mail minus No E-Mail | conversion | +0.003111 (probability difference) = +0.3111 percentage points | [+0.001499, +0.004723] (probability difference) = [+0.1499, +0.4723] percentage points | z=3.782 | 0.000156 | 0.000312 | yes | +54.3% |
| Womens E-Mail minus No E-Mail | spend | +$0.424412 (USD per randomized customer) | [+$0.168957, +$0.679868] (USD per randomized customer) | t=3.256 (df=40064.9) | 0.00113 | 0.00113 | yes | +65.0% |

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
