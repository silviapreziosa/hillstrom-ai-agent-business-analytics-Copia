# Independent primary-results numerical audit

Audit performed 12 November 2026. Inputs: `hillstorm_no_indices.csv` and `primary_results.csv` provided separately by the project author. The recomputation used a newly written Python CSV-loop calculation with `math.fsum`, sample variance, and SciPy normal/t quantiles and survival functions, **without executing or inspecting the OpenCode analysis scripts**. This is independent computational recalculation, not formal verification or a fully independent human audit.

Raw CSV SHA-256: `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`. Number of rows: 64000.

| Treatment vs control | Outcome | Recomputed estimate | Recomputed Holm p | Comparison to OpenCode |
|---|---|---:|---:|---|
| Mens E-Mail minus No E-Mail | visit | 0.076589564 | 1.6246e-112 | Match |
| Mens E-Mail minus No E-Mail | conversion | 0.006805007 | 5.8772e-13 | Match |
| Mens E-Mail minus No E-Mail | spend | 0.769827156 | 3.4914e-07 | Match |
| Womens E-Mail minus No E-Mail | visit | 0.045233107 | 9.6149e-44 | Match |
| Womens E-Mail minus No E-Mail | conversion | 0.003111058 | 0.0003115 | Match |
| Womens E-Mail minus No E-Mail | spend | 0.424412216 | 0.0011294 | Match |

Every reported estimate, standard error, statistic, CI, unadjusted p-value and Holm-adjusted p-value agreed with the recomputation to numerical precision. See `independent_primary_audit.csv` for exact comparisons. The six numerical hypotheses were not re-selected or changed.

**Reporting correction:** Risk differences `0.076590`, `0.045233`, `0.006805`, `0.003111` correspond to 7.6590, 4.5233, 0.6805, 0.3111 **percentage points**, respectively; use `pp` only after multiplying probability differences by 100. Spend differences are USD per randomized observation, not percentage points.

**Scope and limitations:** This audit covers the six primary CSV rows and their sampling formulas, not balance/robustness analysis, causal assumptions, code integrity, or agent compliance. The two input files were not modified. Statistically significant effects do not by themselves establish profitability.
