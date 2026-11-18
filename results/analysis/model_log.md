# Model calls log (AGENTS.md rule 5)

## src/05_analysis_primary.py
- NO statistical models fitted. Closed-form two-sample z-tests
  (proportions) and Welch t-test (spend) per plan.md §5.
  Library calls: scipy.stats.norm.sf, scipy.stats.t.sf, scipy.stats.t.ppf.
  Inputs: data/raw/hillstorm_no_indices.csv (read-only), all 64,000 rows.
  No randomness used; no seed required.

## src/06_balance_and_robustness.py
- R2: statsmodels OLS (HC1), n=64,000, design = intercept + treat_mens
  + treat_womens + recency + history + mens + womens + newbie +
  zip dummies (drop_first) + channel dummies (drop_first); outcomes:
  visit, conversion, spend. Labeled approximate re-expression of ITT
  contrasts (plan.md §8 R2). No randomness.
- R3: closed-form Welch on log1p(spend); exact two-part decomposition
  (arithmetic identity with midpoint weights; no causal mediation).
- R5: numpy default_rng(42), 10,000 arm-stratified resamples per pair.
