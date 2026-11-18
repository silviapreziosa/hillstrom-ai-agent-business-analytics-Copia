# Independent computational audit — Hillstrom robustness outputs

Date: 2026-11-18

## Inputs and scope

- `hillstorm_no_indices.csv` (64,000 records)
- `robustness.csv` (six HC1 OLS treatment coefficients)
- `robustness_transformations.csv` (Welch tests on `log1p(spend)` and exact two-part decomposition)

Calculated independently of OpenCode scripts, using the raw dataset, NumPy/SciPy and statsmodels. This verifies arithmetic and specified implementations, not every modeling assumption, all robustness outputs, or the source dataset's provenance.

## OLS reproduction (HC1)

Model for each outcome: intercept + treatment indicators (Mens E-Mail; Womens E-Mail), recency, history, mens, womens, newbie, with one-hot indicators for `zip_code` and `channel` (one reference category omitted from each). N=64,000. HC1 = heteroskedasticity-consistent covariance with finite-sample adjustment.

| Outcome | Treatment | Independently reproduced coefficient | Independently reproduced HC1 SE | Match to robustness.csv |
|---|---|---:|---:|---|
| visit | Mens | 0.076016871592361 | 0.003338027635548 | Yes |
| visit | Womens | 0.045483366199912 | 0.003192510946262 | Yes |
| conversion | Mens | 0.006767758874164 | 0.000919718001282 | Yes |
| conversion | Womens | 0.003118936621346 | 0.000821945896005 | Yes |
| spend | Mens | 0.766429561912373 | 0.145103688067179 | Yes |
| spend | Womens | 0.425769958904822 | 0.130258926393361 | Yes |

Recomputed 95% confidence intervals and p-values also agree with the supplied file to floating-point precision.

## Transformed outcome and decomposition

| Contrast | log1p(spend) mean difference | Welch SE | Welch p-value | Total mean-spend difference |
|---|---:|---:|---:|---:|
| Mens minus No E-Mail | 0.029241486472441 | 0.004105341322156 | 1.076514706e-12 | 0.769827155894537 |
| Womens minus No E-Mail | 0.014209143517219 | 0.003727617591187 | 0.0001381298886 | 0.424412215936597 |

Decomposition identity used: Delta E[spend] = Delta P(conversion) * average(mean spend among converters) + average(P(conversion)) * Delta(mean spend among converters), where each average is the arithmetic midpoint across treatment and control. Both rows match `robustness_transformations.csv`.

| Group | Conversion rate | Mean spend conditional on conversion |
|---|---:|---:|
| No E-Mail | 0.005726086548390 | $114.002704918 |
| Mens E-Mail | 0.012531093068006 | $113.526928839 |
| Womens E-Mail | 0.008837144059475 | $121.894761905 |

For Womens versus No E-Mail, the **difference in conditional spending** is +$7.892056987, whereas the **contribution to unconditional mean spending** in the midpoint decomposition is +$0.057466923. For Mens the analogous values are -$0.475776079 and -$0.004343165. These quantities must not be confused.

## Interpretation and limitations

- The numerical values in both supplied CSVs are reproducible from the original dataset.
- Differences in conversion rates are larger in the treatment arms. The two-part decomposition is an **arithmetic identity**, not a causal mediation analysis. Mean spend among converters conditions on a post-treatment outcome; these groups need not be comparable under randomization.
- `log1p(spend)` is a transformed-outcome estimand, not a percentage change in arithmetic mean spending; coefficients should not be interpreted directly as percentage revenue uplift.
- The audit does not verify the separate balance, bootstrap, BH correction, or funnel CSVs, because those files were not provided in this upload.
- The audit was performed separately from OpenCode's analysis scripts, but is a computational review, not a formal proof of all agent behavior.
