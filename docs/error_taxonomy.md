# Error taxonomy — documented agent errors, ambiguities, and unresolved assumptions

**Purpose.** A non-overlapping classification of every error item recorded in
`mistakes.md`, with the evidence, correction, re-test, and Git reference for
each. This file is a documentation index; it does not change any analysis
result and does not re-classify any item silently.

**Counting unit.** One item = one numbered entry in `mistakes.md` (1–11), one
lettered item in the transparency log (a–c), or one `M`-numbered entry
(M1–M10). Each item is assigned to **exactly one** primary category. Where an
item also illustrates a second theme, that theme is noted, not counted again.

**Date of this classification:** 2026-11-18 (revised the same day to add M10 and record its source fix).

---

## 0. Summary and arithmetic check

| Primary category | Count | Item IDs |
|---|---:|---|
| Mathematical and statistical errors | 2 | 1, 4 |
| Verification-design errors | 8 | 3, 7, 8, 9, 10, 11, M5, M9 |
| Coding and execution failures | 6 | transparency a, b, c; M1, M2, M4 |
| Tooling and reproducibility failures | 2 | M3, M7 |
| Reporting and interpretation errors | 4 | 5, M6, M8, M10 |
| **Confirmed error items** | **22** | |
| Methodological ambiguities | 2 | 2, 6 |
| **Documented items (errors + ambiguities)** | **24** | |

**Check against the records.** `mistakes.md` contains 11 numbered entries,
3 lettered transparency items, and 10 `M` entries: 11 + 3 + 10 = 24. Of these,
entries 2 and 6 are methodological ambiguities, leaving 22 confirmed error
items. Category totals: 2 + 8 + 6 + 2 + 4 = 22. The two counts agree.

**Not counted as error items.** The documentation gap in `README.md` (stale
statement that `plan.md` was empty) and the irrecoverable 2026-11-05 failure
logs (§R1) are recorded separately in §8 below. They are repository and
evidence-management issues, not analysis errors, and are not added to the
22.

---

## 1. Mathematical and statistical errors (2)

### E1 — "Affects SEs only" (duplicate rows)

- **Original (verbatim):** "Duplicate rows: keep all 64,000 (individuals,
  recommended) vs. deduplicate. Affects SEs only; needs your call."
- **Why it is wrong:** removing exact-duplicate rows re-weights the sample,
  because the duplicated rows are almost entirely zero-outcome rows. Verified
  deltas (deduplicated minus full sample, Mens minus No E-Mail): visit
  +0.002139, conversion +0.000720, spend +0.081396 (≈10.6% of the full-sample
  spend contrast). Point estimates move, not just standard errors.
- **Detection:** human-directed review round, 2026-11-05; recomputation
  against the full and deduplicated samples. Computational authorship of the
  review is not documented (see `MODEL_USE_DISCLOSURE.md` §5).
- **Correction:** primary analysis retains all 64,000 rows; deduplication is
  retained only as a labeled illustration of a potentially invalid
  data-processing decision, never as an alternative treatment-effect estimate.
- **Re-test:** `src/03_compare_and_report.py`: 48/48 reconciliation targets
  PASS on both calculation paths; cross-path maximum deviation 3.3e-16.
- **Evidence:** `mistakes.md` §1; `results/verification/dup_comparison.csv`;
  `dup_pathA.csv`; `dup_pathB.csv`; `verification_log.md`; commit `7d0c9c5`
  (tag `v0.1-verification-baseline`); classification recorded in commit
  `9b02f0e`.

### E4 — "36,288 covariate cells"

- **Original (verbatim fragment):** "A row is a point in a discrete space
  (recency 12 levels × 7 history bands × zip 3 × channel 3 × mens/womens 4
  combinations × newbie 2 × segment 3 ≈ 36,288 covariate cells)" […]
- **Why it is wrong:** the stated factors multiply to 13,608 using the three
  observed mens/womens combinations, or 18,144 with a hypothetical fourth
  combination — not 36,288.
- **Detection:** human-directed review arithmetic, 2026-11-05.
- **Correction:** number withdrawn. It was never used in any analysis,
  table, or reported estimate.
- **Re-test:** none performed; no replacement recomputation is recorded.
  The item is closed as a withdrawn unsupported number, not as a corrected
  estimate.
- **Evidence:** `mistakes.md` §4; commit `7d0c9c5`.

---

## 2. Verification-design errors (8)

### E3 — Tautological funnel "verification" test

- **Original (verbatim):** "6. **Funnel logic test:** assert every `visit = 1`
  pass yields `visit = 1` (funnel coherence is preserved in any filtered
  subset used downstream)."
- **Why it is wrong:** as worded the assertion is a tautology and can never
  fail, violating the spirit of AGENTS.md rule 13.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** replaced by falsifiable assertions (spend > 0 ⇒
  conversion = 1 ⇒ visit = 1 in every derived artifact), each validated by a
  corrupted-fixture negative test (`V-fixture-fail`) that must fail.
- **Re-test:** instrument check passed: the corrupted copy violates funnel
  coherence once and the assertion detects it; 37/37 instrument checks PASS.
- **Evidence:** `mistakes.md` §3; `results/verification/dup_negative_controls.csv`;
  `verification_console_04.txt`; commit `7d0c9c5`.

### E7 — NC-1 v1: contradictory construction and wrong closed form

- **Original (verbatim fragment):** "10,000 control customers with 1,000
  responders; 10,000 treated with 1,500 responders … add 300 exact copies of
  treated responders and 300 exact copies of control non-responders. Closed
  form: dedup diff = (1,200/9,700) − (1,000/9,700) = 200/9,700 … Δ ≈ 0.0294."
- **Why it is wrong:** adding 300 rows to a 10,000-customer arm yields 10,300
  as-given rows; deduplication returns the original 10,000 unique customers.
  Denominators of 9,700 never arise, and the deduplicated contrast is
  unchanged (Δ = 0), not ≈0.0294.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** superseded entirely by the small enumerated NC-1 fixture
  (`src/fixtures/nc1_visit.csv`), where deduplication removes exactly one
  enumerated copy per arm.
- **Re-test:** superseded fixture executed: contrast +0.2 → 0; Δ = −1/5
  exact, both paths.
- **Evidence:** `mistakes.md` §7; `src/fixtures/nc1_visit.csv`;
  `results/verification/dup_negative_controls.csv`; commit `7d0c9c5`.

### E8 — NC-1 v2: incorrect control-group count

- **Original (verbatim fragment):** "Nine rows as given: [5 Mens rows; 4
  No E-Mail rows] … No E-Mail mean = 1/5 = 0.2; diff = **+0.2**."
- **Why it is wrong:** the enumerated fixture had only 4 control rows, so the
  control mean is (1+0+0+0)/4 = 0.25, not 0.2; the as-given difference is
  0.15, not 0.2. The claimed mean assumed a row that was never written.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** fixture rebalanced to 5 Mens + 5 No E-Mail rows (10 rows,
  one enumerated copy per arm).
- **Re-test:** as-given 0.4 / 0.2 / +0.2; deduplicated 0.25 / 0.25 / 0;
  Δ = −0.2 exact, both paths.
- **Evidence:** `mistakes.md` §8; `src/fixtures/nc1_visit.csv`;
  `dup_negative_controls.csv`; commit `7d0c9c5`.

### E9 — NC-2 v2: invalid uniqueness assumption and wrong deduplicated counts

- **Original (verbatim fragment):** "After dedup (6 unique rows): Mens =
  100/3 ≈ 33.3333; No E-Mail = 100/3; diff = 0 … Δdiff = −25.00 exactly."
- **Why it is wrong:** the three control rows 2–4 were mutually identical
  `(0,0,0.00)` rows; full-row deduplication keeps only one, so the control
  unique count is 2 (mean 50.00), total unique is 5 not 6, the deduplicated
  difference is −50/3 ≈ −16.6667 not 0, and Δ = −125/3 ≈ −41.6667 not −25.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** originals made distinguishable with a unique per-customer
  `history` value; the copy references an enumerated source row, so
  deduplication removes exactly one deliberate copy.
- **Re-test:** as-given 50.00 / 25.00 / 25.00; deduplicated 100/3 / 100/3 / 0;
  Δ = −25 exact, both paths.
- **Evidence:** `mistakes.md` §9; `src/fixtures/nc2_spend.csv`;
  `dup_negative_controls.csv`; commit `7d0c9c5`.

### E10 — PC-1 v2: invariance applied without the distinctness hypothesis

- **Original (verbatim fragments):** "three treated unique customers with
  visit = [1, 0, 0]; three control unique customers with visit = [0, 0, 0];
  every row written exactly twice"; "as-given arm sizes 6/6, dedup 3/3"; and a
  claimed algebraic demonstration that the unique-customer mean is unchanged.
- **Why it is wrong:** with indistinguishable originals (two identical
  treated zero-rows; three identical control rows), deduplication keeps
  {(1),(0)} and {(0)}, giving sizes 2 and 1 and a treated mean of 0.5, not
  1/3. The algebra Σ2x_i/Σ2 = Σx_i/n requires that deduplication retains
  exactly one row per customer.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** all six originals made distinguishable (unique `history`
  values) before each row is written twice.
- **Re-test:** sizes 6/6 → 3/3; Δ = 0 exact; SE ratio = 1/√2 within 1e-12,
  both paths.
- **Evidence:** `mistakes.md` §10; `src/fixtures/pc1_invariance.csv`;
  `dup_negative_controls.csv`; commit `7d0c9c5`.

### E11 — V-0: "adding customer_id eliminates duplicates"

- **Original (verbatim fragment):** "same fixture rows + a `customer_id`
  column ⇒ zero duplicate rows; without ID ⇒ the enumerated duplicate count";
  expected duplicate count "changes from 2 to 0".
- **Why it is wrong:** the specified design had copies inherit the source
  record's ID, so copied rows remain full-row identical; the duplicate count
  stays 2, not 0.
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** split into V-0A (exact duplicates sharing an inherited ID —
  duplicates remain 2) and V-0B (different customers with identical
  characteristics but different IDs — row duplicates = 0; row deduplication
  counts rows, never customers).
- **Re-test:** V-0A no_id = 2, with_id = 2; V-0B duplicates = 0 with 10
  distinct IDs. PASS.
- **Evidence:** `mistakes.md` §11; `results/verification/dup_negative_controls.csv`;
  `dup_negative_controls.md`; commit `7d0c9c5`.

### M5 — VT-8 parser regex mismatch

- **Original behavior (verbatim):** `FAIL VT-8: write-up numbers reconcile
  with primary_results.csv — 0 md estimates matched to CSV within rounding
  (5e-7)`; run `.20261112T101608Z`, exit 1.
- **Why it happened:** the VT-8 regex expected a bare number in the third
  table cell, but the write-up renders `+0.076590 pp` / `+0.769827 $` (value
  plus unit in one cell), so zero lines matched. It was a parser defect, not
  a numerical disagreement.
- **Detection:** automatic, loud test failure.
- **Correction:** regex updated to accept the unit suffix. No numerical
  output changed.
- **Re-test:** second run `.20261112T101639Z` exited 0; VT-8 reported 6/6
  estimates matched; all 9 checks PASS at that stage.
- **Evidence:** `mistakes.md` §M5; `results/logs/…08…20261112T101608Z.txt`
  (failure, preserved) and `.101639Z.txt`; commit `86eb4fe`.

### M9 — VT-10 negative control was case-sensitive

- **Original behavior (verbatim):** `FAIL VT-10: R3 decomposition:
  recomputation, shares, caveats, negative controls — negative control not
  detected`; run `.20261118T133544Z`, exit 1.
- **Why it happened:** the negative control removed the required caveat with
  `r3_md.replace("arithmetic identity", "")`, which is case-sensitive. The R3
  section contains both "Arithmetic identity with midpoint weights" and "This
  is an arithmetic identity", so the phrase survived, the caveat checker
  found nothing missing, and the control returned False. The substantive
  VT-10 checks had already passed.
- **Detection:** automatic, loud test failure.
- **Correction:** negative control now uses a case-insensitive regex
  substitution before re-running the same caveat checker.
- **Re-test:** `.20261118T133621Z` exited 0 with VT-10 PASS (11/11); the
  full sequence `.20261118T133639Z` also 11/11 PASS.
- **Evidence:** `mistakes.md` §M9; the failure log and timestamped failure
  copy in `results/logs/`; commit `30f1c5f`.

---

## 3. Coding and execution failures (6)

### Transparency a — metric-key mismatch

- **Behavior:** the `record()` naming (`asgiven.mean.<col>.<arm>`) did not
  match the emission key (`asgiven.<col>.<arm>`), producing malformed output.
- **Detection / correction / re-test:** loud FAIL on first execution;
  corrected in the script only; artifacts regenerated and checked. Expected
  values were never changed.
- **Evidence:** `mistakes.md` transparency log (a); commit `7d0c9c5`.

### Transparency b — division by zero in single-arm fixture NC-3

- **Behavior:** computing a Mens-vs-No contrast inside a single-arm fixture
  divided by zero.
- **Detection / correction / re-test:** loud FAIL; mean-based Δ used instead,
  per the approved specification; fixture re-run.
- **Evidence:** `mistakes.md` transparency log (b); commit `7d0c9c5`.

### Transparency c — SE-table header after every row

- **Behavior:** the `src/03` SE-table writer emitted the header row after
  every data row in `dup_se_point_estimates.csv`.
- **Detection / correction / re-test:** found during inspection of the
  write-up artifact; string-join writer replaced with an explicit
  `csv.writer`; file regenerated as 7 lines (header + 6 rows).
- **Evidence:** `mistakes.md` transparency log (c);
  `results/verification/dup_se_point_estimates.csv`; commit `7d0c9c5`.

### M1 — `KeyError: 'p_conversion'` in `src/05`

- **Behavior (verbatim traceback):** `KeyError: 'p_conversion'` at
  `p1 = S[t_arm][f"p_{col}"]`.
- **Cause:** statistics stored under `p_conv` but looked up as
  `p_conversion`.
- **Detection:** automatic, first main-analysis run failed.
- **Correction:** key renamed to `p_conversion`.
- **Re-test:** third run of 05 exited 0 (`.20261112T101411Z`); values match
  the second path (VT-3, 3.331e-16).
- **Evidence:** `mistakes.md` §M1; failure log `.20261112T101218Z.txt` and
  failure copy; commit `86eb4fe`.

### M2 — edit-induced `SyntaxError` in `src/05`

- **Behavior (verbatim traceback):** `SyntaxError: invalid syntax` at
  `p0 = S[c_arm][f"p_{col}"]            d = p1 - p0`.
- **Cause:** a manual edit intended as a no-op collapsed the newline between
  two statements.
- **Detection:** automatic, second run failed.
- **Correction:** newline restored.
- **Re-test:** third run exited 0 (`.20261112T101411Z`).
- **Evidence:** `mistakes.md` §M2; log `.20261112T101300Z.txt`; commit
  `86eb4fe`.

### M4 — dead `* 0` term in the R3 Welch SE

- **Original code (verbatim fragment):** `se_log = float(np.sqrt(l1.var(ddof=1)
  / len(l1) + l0.var(ddof=0) * 0 + l0.var(ddof=1) / len(l0)))`.
- **Impact:** none — the term evaluates to exactly 0.0, so the SE is
  mathematically identical with or without it.
- **Detection:** agent inspection during code review (manual).
- **Correction:** term removed; script rerun so artifacts match final code.
- **Re-test:** outputs byte-compared against the pre-fix run — identical to
  full floating-point precision (`robustness_transformations.csv`,
  `robustness.csv`, `robustness_bootstrap.csv`).
- **Evidence:** `mistakes.md` §M4; commit `86eb4fe`.

---

## 4. Tooling and reproducibility failures (2)

### M3 — `run.sh` failure-copy overwrite

- **Original behavior:** the wrapper's failure copy used a name without a
  timestamp (`<run-id>__<script>_first_run_fail.txt`), so a second failed run
  with the same run-id overwrote the first failure copy. The M1 copy was
  overwritten by the M2 copy.
- **Impact:** no evidence was lost — the complete M1 failure log survives in
  the timestamped log `.20261112T101218Z.txt`, which is never overwritten.
- **Detection:** agent inspection during M1/M2 handling (manual).
- **Correction:** failure copies now carry the UTC timestamp
  (`*_first_run_fail.<TS>.txt`).
- **Re-test:** the first 08 failure (M5) produced a timestamped failure copy
  `.20261112T101608Z.txt`; no overwriting occurred.
- **Evidence:** `mistakes.md` §M3; `src/run.sh`; commit `0dfbb73` (wrapper);
  documentation in `86eb4fe`.

### M7 — rerunning 05 deleted the 06 section of `model_log.md`

- **Original behavior:** `src/05` wrote `model_log.md` with
  `Path.write_text` (full overwrite), while `src/06` appended its section.
  Rerunning 05 after 06 therefore deleted the R2 statsmodels record.
- **Impact:** no statistical output affected; all ten statistical CSVs stayed
  byte-identical. The loss was confined to the model-call log (AGENTS.md
  rule 5 provenance).
- **Detection:** agent diff inspection during the M6 correction (manual, not
  automatic).
- **Correction:** initially an operational rule (rerun 06 before publishing);
  later enforced in code: 05 and 06 both use an idempotent
  `upsert_model_log()` that replaces only their own section.
- **Re-test:** rerunning 05 alone leaves the 06 section intact (one copy);
  rerunning 06 alone creates no duplicate; VT-1…VT-10 + INT 11/11 PASS.
- **Evidence:** `mistakes.md` §M7; `results/analysis/model_log.md`; commits
  `2f87409` (documentation) and `30f1c5f` (idempotent guard).

---

## 5. Reporting and interpretation errors (4)

### E5 — "birthday-paradox logic guarantees collisions"

- **Original (verbatim):** "…birthday-paradox logic guarantees collisions even
  with zero duplicate customers; the outcome dimension is nearly all
  (0, 0, 0.0), so once covariates match, the whole row matches."
- **Why it is wrong:** collisions are overwhelmingly *probable* — a
  probability that can be bounded — never "guaranteed".
- **Detection:** human-directed review, 2026-11-05.
- **Correction:** report the collision probability with an explicit bound, or
  write "extremely likely".
- **Re-test:** wording fix; no numeric re-test.
- **Evidence:** `mistakes.md` §5; commit `7d0c9c5`.

### M6 — probability-scale effects mislabeled as "pp"

- **Original (verbatim):** `| Mens E-Mail minus No E-Mail | visit | +0.076590
  pp | …` and the corresponding rows for Mens conversion (+0.006805), Womens
  visit (+0.045233) and Womens conversion (+0.003111). The same labels
  appeared in `reconciliation_report.md`.
- **Why it is wrong:** one percentage point equals 0.01 in probability, so
  `pp = 100 × d`. The labels understated the effects by exactly a factor of
  100 (e.g., +0.076590 is +7.6590 pp, not +0.076590 pp). The numbers were
  correct; the unit token was not.
- **Detection:** separate AI computational audit (audit 1), 2026-11-12:
  `results/analysis/human_verification/independent_primary_audit.md`. The
  audit reproduced all six estimates, SEs, CIs and p-values (max absolute
  difference 3.33e-16), isolating the defect to the unit label.
- **Correction:** dual reporting in both artifacts — probability difference
  and percentage points, CIs converted by the same factor, spend labeled USD
  per randomized customer. No estimate, SE, statistic, CI or p-value changed.
- **Re-test:** VT-9 added and executed (`main-analysis-2026-11-18`, run
  `.20261118T132526Z`): PASS; 6 table rows + 6 report lines verified;
  negative control (the original `+0.076590 pp` label) detected and rejected.
  All ten statistical CSVs are byte-identical to the pre-correction snapshot.
- **Evidence:** `mistakes.md` §M6; tag `pre-unit-label-fix` (commit
  `86eb4fe`); correction commit `2f87409`; audit md/csv; VT-9 in
  `results/analysis/vt_results.csv`.

### M8 — R3 decomposition read as a causal mechanism

- **Original (verbatim):** "converter-spend differences are essentially zero
  (−$0.0043 / +$0.0575) — the spend effect is driven by more converters, not
  higher spend per converter (`robustness_transformations.csv`, descriptive
  decomposition)." The pre-correction `robustness.md` also lacked the
  identity statement and the plan-mandated "second term descriptive" caveat.
- **Why it is wrong:** the two-part decomposition is an exact arithmetic
  identity, not a causal mediation analysis. Mean spend among converters
  conditions on a post-treatment outcome, so those groups need not be
  comparable under randomization. "Essentially zero" is valid for Mens
  (−$0.004343, ≈−0.6% of the total) but not for Womens (+$0.057467, ≈13.5%
  of the +$0.424412 total under midpoint weights; ≈16.4% under control-side
  weights). The split does not separately identify causal mechanisms.
- **Detection:** separate AI computational audit (audit 2), 2026-11-18:
  `results/analysis/human_verification/independent_robustness_audit.md`. The
  audit reproduced the OLS coefficients/SEs/CIs, the log1p Welch tests and
  the decomposition terms at floating-point precision; no numerical error
  existed. The defect was interpretive.
- **Correction:** `robustness.md` R3 rewritten with the explicit formula
  `ΔE[spend] = ΔP(conversion) × (m1 + m0)/2 + ((p1 + p0)/2) × (m1 − m0)`,
  component units and share-of-total percentages, the "arithmetic identity,
  not a causal mediation analysis" statement, the post-treatment descriptive
  caveat, and the weighting-convention note. R2 units labeled; R1 scope
  clarified; `reconciliation_report.md` no longer compares quantities on
  incompatible scales. No estimate, SE, CI or p-value changed.
- **Re-test:** VT-10 executed in runs `.20261118T133621Z` and
  `.20261118T133639Z`: PASS. It independently recomputes term1/term2/total
  from `data/raw` (≤1e-9), verifies the identity, checks the six displayed
  values and shares, requires the caveat phrases, rejects R3-specific
  mechanism language, and runs negative controls. Overall 11/11 PASS.
- **Evidence:** `mistakes.md` §M8; dated evidence record in commit `f71ea24`
  (tag `pre-r3-interpretation-fix`); correction commit `30f1c5f`; both audit
  files; VT-10 in `results/analysis/vt_results.csv`.

### M10 — README said the bootstrap intervals "bracket" the Welch intervals

- **Original (verbatim):** "R5 bootstrap | Mens [+0.486360, +1.058330];
  Womens [+0.171673, +0.681706]; percentile CIs bracket the Welch CIs"
  (`README.md` §E.3, commit `e3ca0ea`). The same sentence is emitted by
  `src/08_reconcile_and_report.py` into `reconciliation_report.md`.
- **Why it is wrong:** "bracket" asserts containment. The Welch spend
  intervals are Mens [+0.485140, +1.054515] and Womens
  [+0.168957, +0.679868]. Both percentile endpoints are higher than the
  corresponding Welch endpoints (Mens +0.001220 / +0.003815; Womens
  +0.002716 / +0.001838 USD), so neither interval contains the other. The
  widths are nearly identical (Mens 0.571970 vs 0.569375; Womens 0.510032 vs
  0.510911 USD): the intervals are highly similar and substantially
  overlapping, not nested.
- **Detection:** human-directed final README accuracy review, 2026-11-18;
  the endpoint comparison was performed by the agent against
  `robustness_bootstrap.csv` and `primary_results.csv`. This is not a
  completed human audit.
- **Correction:** `README.md` §E.3 reworded; the small upward endpoint shift
  and the absence of containment are stated. The same wording was subsequently
  corrected at source in `src/08_reconcile_and_report.py`, and
  `reconciliation_report.md` was regenerated in commit `366b4af`. No estimate,
  SE, CI or p-value changed.
- **Re-test:** direct endpoint arithmetic, re-checked against both CSVs. After
  the source correction, `src/run.sh 08_reconcile_and_report.py
  m10-source-fix-2026-11-18` regenerated the report (exit 0, log
  `.20261118T143125Z`); VT-1…VT-10 + INT passed 11/11, and every substantive
  statistical CSV was byte-identical to the previous commit. No individual VT
  tests interval containment, so correctness of the sentence rests on the
  endpoint arithmetic above.
- **Evidence:** `mistakes.md` §M10; `robustness_bootstrap.csv`;
  `primary_results.csv`; original wording commit `e3ca0ea`; README correction
  `3d10978`; source correction and regeneration `366b4af`.

---

## 6. Methodological ambiguities (2)

### AMB-1 — multiplicity family: 6 vs 9 comparisons

- **Original (verbatim fragment):** "Null of no difference in each case
  (two-sided, α = 0.05, Holm correction across the 3 arm comparisons × 3
  outcomes)." Reopened later as whether the family is 9 (3 arms × 3 outcomes)
  or 6 (2 treatment-vs-control arms × 3 outcomes).
- **Status:** resolved by explicit decision, not by a numerical re-test. The
  confirmatory family is fixed at 6; Mens-vs-Womens and adjusted variants are
  exploratory with nominal p-values.
- **Evidence:** `mistakes.md` §2; `plan.md` §4 and §14; commit `7f6b11c`.

### AMB-2 — assumption-labeling gaps

- **Items:** the spend = 499.00 rows (count verified as 12) invite a "cap"
  interpretation that is an unverified hypothesis; printed example duplicate
  rows were labeled as "supporting" the collision story although they are
  anecdotal illustration, not evidence of the duplication mechanism.
- **Status:** labels corrected; the spend-cap interpretation remains an
  unresolved assumption. This is an ambiguity/labeling item, not a numerical
  error.
- **Evidence:** `mistakes.md` §6; `plan.md` §8 and §10 (assumption labels).

---

## 7. Unresolved assumptions (not errors)

These are explicitly **not verified** and are carried as limitations in
`README.md` §I and `results/analysis/reconciliation_report.md`:

1. provenance as the Hillstrom "MineThatData" dataset (schema matches;
   outcome window not verifiable from the file);
2. one row = one distinct customer (collisions make this unprovable from the
   data alone);
3. randomized assignment and the two-week outcome window (supported by
   covariate balance, not proven by it);
4. no interference between customers (SUTVA);
5. the spend = 499.00 cap interpretation (discussed in AMB-2 above);
6. no cost, margin, or campaign-cost data — no profitability threshold is
   computable;
7. deduplicated counts are counts of distinct rows, which may undercount
   distinct customers when rows are indistinguishable.

Reference: `plan.md` §1, §7–§9; `results/analysis/reconciliation_report.md`
"Limitations".

---

## 8. Repository documentation gap and evidence-loss event

### Documentation gap — stale `README.md` statement

- **Original text:** "`plan.md` is intentionally empty until the analysis plan
  is approved."
- **Why it is wrong:** `plan.md` v1.1 was approved in commit `7f6b11c`
  (2026-11-12) and the main analysis was executed afterwards.
- **Status:** corrected in the documentation commit that adds this file; the
  statement is replaced by the actual plan state. This gap was not previously
  recorded in `mistakes.md` and is not counted among the 22 error items.

### R1 — irrecoverable 2026-11-05 failure logs

- **Event:** the first execution of `src/04_negative_controls.py` (2026-11-05)
  failed loudly with two script defects. Its console transcript was saved to
  a temporary file and then overwritten by the successful rerun; it was never
  committed. The failure survives only in the session transcript.
- **Status:** acknowledged, not reconstructed. No historical evidence was
  fabricated. Future runs use `src/run.sh`, which preserves failures and logs
  exit codes. This is an evidence-preservation limitation, not an analysis
  error, and is not counted among the 22.
- **Evidence:** `mistakes.md` §R1; commit `9b02f0e`; `src/run.sh`.

---

## 9. Cross-reference index

| Item | Primary category | Main evidence | Commit / tag |
|---|---|---|---|
| 1 | Statistical | `dup_comparison.csv` | `7d0c9c5` / `v0.1-verification-baseline` |
| 2 | Ambiguity | `plan.md` §4, §14 | `7f6b11c` |
| 3 | Verification design | `dup_negative_controls.csv` | `7d0c9c5` |
| 4 | Statistical | `mistakes.md` §4 | `7d0c9c5` |
| 5 | Reporting | `mistakes.md` §5 | `7d0c9c5` |
| 6 | Ambiguity | `plan.md` §8, §10 | `7d0c9c5` |
| 7–11 | Verification design | `src/fixtures/*.csv`; controls | `7d0c9c5` |
| a–c | Coding/execution | `results/verification/*` | `7d0c9c5` |
| M1, M2, M4 | Coding/execution | `results/logs/` | `86eb4fe` |
| M5 | Verification design | `results/logs/` | `86eb4fe` |
| M3 | Tooling | `src/run.sh` | `0dfbb73`, `86eb4fe` |
| M6 | Reporting | audit 1; VT-9 | `86eb4fe` / `pre-unit-label-fix`; `2f87409` |
| M7 | Tooling | `model_log.md` | `2f87409`, `30f1c5f` |
| M8 | Reporting | audit 2; VT-10 | `f71ea24` / `pre-r3-interpretation-fix`; `30f1c5f` |
| M9 | Verification design | VT-10 failure log | `30f1c5f` |
| M10 | Reporting | `robustness_bootstrap.csv`; `primary_results.csv` | `e3ca0ea` (original); `3d10978` (README); `366b4af` (source) |
| R1 | Evidence loss (not an error) | `mistakes.md` §R1 | `9b02f0e` |
