# Evidence record — agent's 2026-11-12 robustness interpretation

**Status of this statement:** it was transmitted in the agent's final report
message to the project author on 2026-11-12. It was **not previously saved in
this repository**. It is recorded here verbatim on 2026-11-18, *before* any
correction, so that the original wording is preserved in Git (Commit C,
annotated tag `pre-r3-interpretation-fix`).

**Verbatim quote** (robustness bullet from the agent's reported summary):

> **R3 transformations:** log1p(spend) Welch diffs +0.02924 (p = 1.1e-12)
> and +0.01421 (p = 1.4e-04); exact two-part decomposition reproduces the
> spend contrasts by identity (0.769827, 0.424412); converter-spend
> differences are essentially zero (−$0.0043 / +$0.0575) — the spend effect
> is driven by more converters, not higher spend per converter
> (`robustness_transformations.csv`, descriptive decomposition).

**Referenced artifacts (unchanged, committed alongside this record):**

- `results/analysis/robustness_transformations.csv`
- `results/analysis/robustness.csv`
- `results/analysis/robustness.md`
- `results/analysis/human_verification/independent_robustness_audit.md`

**Why it is preserved:** the sentence's causal-mechanism phrasing ("driven
by") and its "essentially zero" characterization of the Womens
conditional-spend contribution (+$0.0575, ≈13.5% of the +$0.4244 total;
up to ≈16.4% under alternative decomposition weights) are the subject of
`mistakes.md` entry M8. No numerical result is disputed; the claim's
interpretation is.
