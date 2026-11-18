# mistakes.md — Auditable record of agent errors and corrections

Every entry preserves the original statement verbatim (or, where very long, an
exact truncated quote marked with […]), the verdict, the evidence, the
correction, and the outcome of re-testing. Per AGENTS.md rule 12.
Date for all entries below: 2026-11-05. All re-tests referenced were executed
via `src/01–04` with logs in `results/verification/`.

---

## Programme-level audit (professor review, 2026-11-05, first audit round)

### 1. "Affects SEs only" (duplicate rows)

- **Original (verbatim):** "Duplicate rows: keep all 64,000 (individuals, recommended) vs. deduplicate. Affects SEs only; needs your call."
- **Verdict:** Incorrect (falsified by recomputation).
- **Evidence:** Removing exact-duplicate rows re-weights the sample because duplicated rows are almost exclusively zero-outcome rows (0 of 7,634 keep=False rows have conversion=1; 0 have spend>0; only 622 have visit=1). Verified deltas (Mens − No E-Mail, dedup − full): visit +0.002139, conversion +0.000720, spend +0.081396 ≈ 10.6% of the full-sample contrast. Within-arm means also move (e.g., visit Mens 0.182757 → 0.193922).
- **Correction:** Deduplication changes point estimates **and** standard errors, not SEs alone. Primary analysis on all rows; dedup kept as a labelled sensitivity analysis reporting both samples.
- **Re-test:** V-D2 reconciliation in `src/03_compare_and_report.py`: 48/48 targets PASS on both calculation paths (pandas; pure Python + exact rationals), cross-path max deviation 3.3e-16. **PASS.**

### 2. Multiplicity family ambiguity (9 vs 6 comparisons)

- **Original (verbatim):** "Null of no difference in each case (two-sided, α = 0.05, Holm correction across the 3 arm comparisons × 3 outcomes)." — reopened later as: "whether the 9 comparisons (3 arms × 3 outcomes) or 6 (2 arms × 3 outcomes) is the right family."
- **Verdict:** Ambiguous / unsupported (analysis plan alternated between 6 and 9; no primary/exploratory split).
- **Correction:** Confirmatory family fixed at **6** (2 treatment-vs-control comparisons × 3 outcomes), Holm step-down at α = 0.05; Mens-vs-Womens head-to-head and covariate-adjusted variants are exploratory with nominal p-values.
- **Re-test:** Design decision, no numeric re-test. To be pinned as literals in `plan.md` before the main analysis.

### 3. Tautological funnel "verification" test

- **Original (verbatim):** "6. **Funnel logic test:** assert every `visit = 1` pass yields `visit = 1` (funnel coherence is preserved in any filtered subset used downstream)."
- **Verdict:** Not meaningful — as worded it is a tautology and can never fail, violating the spirit of AGENTS.md rule 13.
- **Correction:** Replaced by falsifiable assertions (spend>0 ⇒ conversion=1 ⇒ visit=1 in every derived artifact), each validated by a corrupted-fixture negative test that must fail (V-fixture-fail).
- **Re-test:** Instrument check passed: corrupted copy violates funnel coherence 1 time, assertion detects it. **INSTRUMENT VALID.**

### 4. "36,288 covariate cells"

- **Original (verbatim fragment):** "A row is a point in a discrete space (recency 12 levels × 7 history bands × zip 3 × channel 3 × mens/womens 4 combinations × newbie 2 × segment 3 ≈ 36,288 covariate cells)" […]
- **Verdict:** Unsupported arithmetic. The stated factors multiply to 13,608 (only the 3 observed mens/womens combinations) or 18,144 (with a hypothetical 4th combination) — not 36,288.
- **Correction:** Number withdrawn; to be recomputed from explicit assumptions or omitted from any write-up.
- **Re-test:** Pending (blocked until the main analysis writes-up; flagged for the write-up checklist).

### 5. "Birthday-paradox logic guarantees collisions"

- **Original (verbatim):** "…birthday-paradox logic guarantees collisions even with zero duplicate customers; the outcome dimension is nearly all (0, 0, 0.0), so once covariates match, the whole row matches."
- **Verdict:** Overclaim. Collisions are overwhelmingly *probable* (a probability that can be bounded), never "guaranteed".
- **Correction:** Report the collision probability with an explicit bound, or write "extremely likely".
- **Re-test:** Wording fix; no numeric re-test.

### 6. Assumption-labeling gaps (recorded for completeness)

- "spend = 499.00 looks like a cap": the count (12 rows) is verified; the *cap interpretation* is an unverified hypothesis and must be labeled as such.
- Printed example duplicate rows were labeled as "supporting" the collision story; they are anecdotal illustration, not evidence of the duplication mechanism.

---

## Verification-design audit (professor review, 2026-11-05, second round)

### 7. NC-1 v1 — contradictory construction and wrong closed form

- **Original (verbatim):** "NC-1 (deduplication must change the contrast).** Construct, with exact integer outcomes: 10,000 control customers with 1,000 responders; 10,000 treated with 1,500 responders (true diff 0.05). Then add as rows: 300 exact copies of *treated responders* and 300 exact copies of *control non-responders*. Closed form: dedup diff = (1,200/9,700) − (1,000/9,700) = 200/9,700 (= 0.020618556…), Δ = 0.05 − 200/9,700 ≈ 0.0294."
- **Verdict:** Incorrect. Adding 300 rows to a 10,000-customer arm yields 10,300 as-given rows and dedup returns the original 10,000 unique customers: denominators of 9,700 never arise, and the deduplicated contrast would be unchanged (Δ = 0), not ≈ 0.0294.
- **Correction:** Only a construction with 10,000 as-given rows per arm containing 9,700 unique customers + 300 excess copies reproduces 200/9,700; superseded entirely by the small enumerated NC-1 (`src/fixtures/nc1_visit.csv`).
- **Re-test:** Superseded fixture executed: NC-1 contrast +0.2 → 0, Δ = −1/5 exact, both paths. **PASS.**

### 8. NC-1 v2 — incorrect group counts

- **Original (verbatim fragment):** "Nine rows as given: [5 Mens rows…; 4 No E-Mail rows…]" with "**As given:** … No E-Mail mean = 1/5 = 0.2; diff = **+0.2**".
- **Verdict:** Incorrect. The enumerated fixture had only 4 control rows, so the control mean is (1+0+0+0)/4 = 0.25, not 0.2; the as-given diff is 0.15, not 0.2. The claimed mean assumed a row that was never written.
- **Correction:** Fixture rebalanced to 5 Mens + 5 No E-Mail rows (10 rows, one enumerated copy per arm).
- **Re-test:** Executed with the corrected fixture: 0.4 / 0.2 / +0.2 as given; 0.25 / 0.25 / 0 after dedup; Δ = −0.2 exact, both paths. **PASS.**

### 9. NC-2 v2 — invalid uniqueness assumption, wrong deduplicated counts

- **Original (verbatim fragment):** "No E-Mail | 1 | 1 | 100.00 (C1) / 0 | 0 | 0.00 / 0 | 0 | 0.00 / 0 | 0 | 0.00 (copy of a zero row) … **After dedup** (6 unique rows): Mens = 100/3 ≈ 33.3333; No E-Mail = 100/3; diff = **0** … **Δdiff = −25.00 exactly.**"
- **Verdict:** Incorrect. Control rows 2–4 were three mutually identical `(0,0,0.00)` rows; full-row dedup keeps only one, so control unique = 2 rows (mean 50.00), total unique = 5 (not 6), dedup diff = −50/3 ≈ −16.6667 (not 0), Δ = −125/3 ≈ −41.6667 (not −25).
- **Correction:** Originals made distinguishable via a unique per-customer `history` value; the copy references an enumerated source row (copy of R6), so dedup removes exactly one deliberate copy.
- **Re-test:** Executed: as-given 50.00 / 25.00 / 25.00; dedup 100/3 / 100/3 / 0; Δ = −25 exact, both paths. **PASS.**

### 10. PC-1 v2 — invariance applied without the distinctness hypothesis

- **Original (verbatim fragments):** "three treated unique customers with visit = [1, 0, 0]; three control unique customers with visit = [0, 0, 0]; every row written exactly twice" and "**P-counts:** as-given arm sizes 6/6, dedup 3/3, excess per arm exactly 3" and "**Demonstration (algebra, not assertion):** … the unique-customer mean, identically."
- **Verdict:** Invalid as specified. With indistinguishable originals (two identical treated zero-rows; three identical control rows), dedup keeps {(1),(0)} and {(0)} → sizes 2 and 1, dedup treated mean 0.5 ≠ 1/3, so Δ ≠ 0. The algebra Σ2x_i/Σ2 = Σx_i/n requires that dedup retains exactly one row per customer.
- **Correction:** All six originals distinguishable (unique `history` values) before writing each row twice.
- **Re-test:** Executed: sizes 6/6 → 3/3; Δ = 0 exact; SE ratio = 1/√2 within 1e-12, both paths. **PASS.**

---

## Implementation gating (professor correction before implementation)

### 11. V-0 — "adding customer_id eliminates duplicates" logical error

- **Original (verbatim fragment):** "same fixture rows **+ a `customer_id` column** ⇒ zero duplicate rows; without ID ⇒ the enumerated duplicate count" and (implementation-ready spec) "Expected: as-given duplicate count **changes from 2 to 0** (copies no longer full-row identical) — arithmetic pinned in the script."
- **Raised by:** professor review: "adding customer_id does not eliminate duplicates if copied rows retain the same ID."
- **Verdict:** Incorrect. The specified design had copies *inherit the source record's ID*, so copied rows remain full-row identical; duplicate count stays 2, not 0.
- **Correction:** Split into two tests: **V-0A** — exact duplicates sharing an inherited ID (duplicates remain 2; an ID column does not remove copies of the same customer) and **V-0B** — different customers with identical characteristics but different IDs (row duplicates = 0; row-deduplication counts rows, never customers).
- **Re-test:** V-0A: no_id=2, with_id=2; V-0B: duplicates=0 with 10 distinct IDs. **PASS** (both paths where applicable; logged in `results/verification/dup_negative_controls.csv`).

---

## Open assumptions (explicitly NOT yet verified)

- Provenance as the Hillstrom email dataset (schema matches; documented outcome window not verifiable from the file).
- One row = one distinct customer (collisions make this unprovable from the data alone; both scenarios carried through the plan).
- `spend = 499.00` cap interpretation (see entry 6).
- Randomized assignment (supported by verified covariate balance; not proven by it).

## Instrument implementation errors found and fixed during coding (transparency log)

Three implementation defects (code errors, not expected-value changes) produced
loud FAILs or malformed artifacts on first execution; each was fixed only in
the scripts (never in expected values, which are pre-registered literals):
(a) metric-key mismatch between the record() naming
(`asgiven.mean.<col>.<arm>`) and emission (`asgiven.<col>.<arm>`);
(b) division-by-zero in single-arm fixture NC-3 when computing a Mens-vs-No
contrast that does not exist there (mean-based Δ used instead, per the approved
specification);
(c) the `src/03` SE-table artifact writer emitted the header row
after every data row (`dup_se_point_estimates.csv`), discovered during
inspection of the write-up artifact and fixed by replacing the string-join
writer with an explicit `csv.writer`; the file was regenerated and verified
byte-clean (7 lines: header + 6 rows).
All failures were printed, inspected, and re-run to completion; fixtures,
expected values, and all PASS verdicts were unchanged.

---

## Records and decisions (2026-11-12)

### R1. Irrecoverable historical evidence — overwritten failure logs (confirmed)

The first execution of `src/04_negative_controls.py` (2026-11-05) failed loudly
(two script defects; see transparency log above). Its console transcript was
saved to a temporary file and then **overwritten** by the successful rerun;
it was never committed. The overwrite cannot be recovered from the existing
files. The failure survives only in the session transcript (the FAIL lines were
printed and inspected at the time; expected values were never changed). No
historical evidence has been fabricated to fill this gap. Future runs use
`src/run.sh`, which preserves failures as `*_first_run_fail.txt` and logs exit
codes (`results/logs/exit_codes.csv`). The repository contains no pre-wrapper
exit codes: those exist only in the session transcript.

### R2. Raw dataset not published (decision, Option B — approved 2026-11-12)

`data/raw/hillstorm_no_indices.csv` is excluded from the repository
(`.gitignore`: `data/raw/*.csv`). Its identity is anchored by SHA-256
`00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`
(`results/verification/sha256_log.csv`). Provenance as the Hillstrom
"MineThatData" dataset remains an **unverified assumption**; **no
redistribution rights are claimed** until independently verified (see
README.md, "Data provenance"). "Unchanged" in the logs means unchanged since
first recorded, not verified against an external pre-existing hash.

### R3. Classification index of documented errors

- **Confirmed errors** (falsified or arithmetically wrong; corrected and
  re-tested): entries 1, 4, 5, 7, 8, 9, 10, 11.
- **Methodological ambiguities** (resolved by explicit decision, pending
  pinning in `plan.md`): entries 2 (multiplicity family: fixed at 6),
  3 (tautological funnel test: replaced by falsifiable assertions), and the
  assumption-labeling gaps in entry 6.
- **Unresolved assumptions** (explicitly NOT verified; see "Open assumptions"
  section): Hillstrom provenance, one-row-one-customer, spend-cap
  interpretation, and randomization itself.

---

## Session log — main analysis execution (2026-11-12)

### M1. KeyError in src/05 (implementation error; first main-analysis run failed)

- **Original error (verbatim traceback):** `KeyError: 'p_conversion'` at
  `p1 = S[t_arm][f"p_{col}"]` (line 131 of the first run).
- **Cause:** per-arm statistics were stored under key `p_conv` while the
  outcome loop looked them up as `f"p_{col}"` with `col = "conversion"`.
- **Correction:** statistic key renamed to `p_conversion` so the lookup key
  matches for both outcomes.
- **Retest:** PASSED — third run of 05 exited 0 (log
  `main-analysis-2026-11-12__05_analysis_primary.20261112T101411Z.txt`);
  primary_results.csv values match the independently recomputed second path
  (VT-3, max deviation 3.331e-16) and the pre-registered verification values.
- **Logged via:** `results/logs/main-analysis-2026-11-12__05_analysis_primary
  .20261112T101218Z.txt` and failure copy `*_first_run_fail.txt` (first
  execution; exit code 1 in `results/logs/exit_codes.csv`).

### M2. Edit-induced syntax error in src/05 (implementation error; second run failed)

- **Original error (verbatim traceback):** `SyntaxError: invalid syntax` at
  `p0 = S[c_arm][f"p_{col}"]            d = p1 - p0` (line 132 of run
  `.20261112T101300Z`).
- **Cause:** a manual edit intended as a no-op collapsed the newline between
  the two statements, merging them into one line.
- **Correction:** newline restored.
- **Retest:** PASSED — same third run of 05 as in M1 (exit 0, log
  `…20261112T101411Z.txt`); script executed cleanly with restored newline.

### M3. run.sh failure-copy overwrite (tooling defect found during M1/M2 handling)

- **Original behavior:** the wrapper's failure copy used a name without a
  timestamp (`<run-id>__<script>_first_run_fail.txt`), so a second failed run
  with the same run-id overwrote the first failure copy.
- **Impact:** the M1 failure copy was overwritten by the M2 failure copy.
  **No evidence was lost:** the complete M1 failure log survives in the
  timestamped log `main-analysis-2026-11-12__05_analysis_primary
  .20261112T101218Z.txt` (timestamped logs themselves are never overwritten).
- **Correction:** failure copies now carry the UTC timestamp
  (`*_first_run_fail.<TS>.txt`), making them unique per run.
- **Retest:** PASSED — the first 08 run failure (M5) produced a timestamped
  failure copy `main-analysis-2026-11-12__08_reconcile_and_report_first_run_fail
  .20261112T101608Z.txt`; no overwriting occurred.

### M4. Dead-code term in src/06 R3 (cosmetic; zero effect on results)

- **Original code (verbatim):** `se_log = float(np.sqrt(l1.var(ddof=1) / len(l1)
  + l0.var(ddof=0) * 0 + l0.var(ddof=1) / len(l0)))` — an accidental
  `l0.var(ddof=0) * 0` term (exactly 0.0) inside the Welch SE for
  log1p(spend).
- **Cause:** leftover editing artifact when writing the R3 line.
- **Impact on results:** none — the term evaluates to exactly 0.0, so the SE
  is mathematically identical with or without it (verified below).
- **Correction:** term removed; source rerun so artifacts match final code.
- **Retest:** 06 rerun after fix (`main-analysis-2026-11-12`); outputs
  byte-compared against the pre-fix run — identical to full floating-point
  precision. Confirmed by diff of robustness_transformations.csv,
  robustness.csv and robustness_bootstrap.csv (both run logs in
  results/logs/).

### M5. VT-8 parser regex mismatch in src/08 (implementation error; first 08 run failed)

- **Original behavior (verbatim from run log):** `FAIL  VT-8: write-up
  numbers reconcile with primary_results.csv — 0 md estimates matched to CSV
  within rounding (5e-7)` — run `.20261112T101608Z`, exit 1.
- **Cause:** the VT-8 regex `r"\| ([^|]+) \| (\S+) \| ([+\-\d.]+) \|"`
  expected the write-up table's third cell to be a bare number, but the
  primary_results.md table renders estimates as `+0.076590 pp` /
  `+0.769827 $` (value plus unit inside one cell). The regex therefore
  matched 0 lines and VT-8 failed on a parser defect, not on a numerical
  disagreement.
- **Correction:** regex updated to accept the unit suffix:
  `r"\| ([^|]+) \| (\S+) \| ([+\-\d.]+) (?:pp|\$) \|"`. No numerical output
  of any script was changed.
- **Retest:** PASSED — second run of 08 exited 0 (log
  `main-analysis-2026-11-12__08_reconcile_and_report.20261112T101639Z.txt`);
  VT-8 now reports 6/6 md estimates matched to CSV within rounding (5e-7);
  all 9 checks PASS.
- **Logged via:** results/logs/main-analysis-2026-11-12__08_reconcile_and_report
  .20261112T101608Z.txt and timestamped failure copy (exit code 1 in
  results/logs/exit_codes.csv).

### M6. Probability-scale effects mislabeled as "pp" (reporting error; found by
    external computational audit, corrected 2026-11-18)

- **Original erroneous statement (verbatim):** in
  `results/analysis/primary_results.md` (pre-correction, commit 86eb4fe, tag
  `pre-unit-label-fix`), line 9:
  `| Mens E-Mail minus No E-Mail | visit | +0.076590 pp | [+0.069954,
  +0.083226] | z=22.621 | 2.71e-113 | 1.62e-112 | yes | +72.1% |`
  and the corresponding rows for Mens conversion (+0.006805), Womens visit
  (+0.045233) and Womens conversion (+0.003111) on lines 10, 12, 13. The
  same four labels appeared in `reconciliation_report.md` (lines 26-30).
  Cause in code: `unit = "$" if outcome == "spend" else "pp"` in
  `src/05_analysis_primary.py` (line 176) and
  `src/08_reconcile_and_report.py` (line 210) attached the percentage-point
  token to the raw probability difference.
- **Independent evidence identifying the error:** external computational
  audit `results/analysis/human_verification/independent_primary_audit.md`
  (12 Nov 2026): "Risk differences 0.076590, 0.045233, 0.006805, 0.003111
  correspond to 7.6590, 4.5233, 0.6805, 0.3111 percentage points,
  respectively; use `pp` only after multiplying probability differences by
  100. Spend differences are USD per randomized observation, not percentage
  points." The audit's numerical comparison
  (`independent_primary_audit.csv`) reproduced all six estimates, SEs, CIs
  and p-values (max absolute difference 3.33e-16), isolating the defect to
  the unit label: numerical accuracy was intact, reporting accuracy was not.
- **Root cause:** display formatting treated the probability difference as if
  it were already a percentage-point difference. One percentage point equals
  0.01 in probability, so the correct conversion is `pp = 100 x d`; the label
  understated visit/conversion effects by exactly a factor of 100.
- **Correction:** dual reporting in both artifacts — e.g.
  `+0.076590 (probability difference) = +7.6590 percentage points`, with
  confidence intervals converted by the same factor, and spend rows labeled
  `(USD per randomized customer)`. Unit legends distinguish probability
  differences, percentage points, relative percentage uplift and dollar
  differences. No estimate, SE, test statistic, CI, or p-value was changed;
  all ten statistical CSVs are byte-identical to the pre-correction snapshot
  (diff of `results/analysis/*.csv` vs. tag `pre-unit-label-fix`).
- **Why the previous verification tests missed it:** VT-7 checks causal
  language only (forbidden phrases), and VT-8 checked that the displayed
  number matched the CSV but not that the *unit token* was consistent with
  the number's scale. No test bound units to magnitudes, so a correct number
  with a wrong unit passed every check. VT-3/04/05 are numeric-only and were
  unaffected by a labeling defect.
- **Results of the new verification test:** VT-9 added to
  `src/08_reconcile_and_report.py` and executed
  (`main-analysis-2026-11-18`, run `.20261118T132526Z`): **PASS** — 6 table
  rows + 6 report lines verified, point estimates and CIs, tolerance
  5e-7 (probability), 5e-4 (percentage points); negative control (the
  original `+0.076590 pp` label) is **detected and rejected**; post-write
  file recheck passed 6/6. All VT-1..VT-8 + INT remain PASS (10/10 total).
- **Evidence preservation:** pre-correction scripts, results, logs and this
  file are preserved in commit 86eb4fe, annotated tag `pre-unit-label-fix`;
  the correction is a separate commit, so `git diff` shows the erroneous
  labels verbatim.
- **Logged via:** results/logs/main-analysis-2026-11-18__05_analysis_primary
  .20261118T132519Z.txt and
  results/logs/main-analysis-2026-11-18__08_reconcile_and_report
  .20261118T132526Z.txt (exit code 0 each, in results/logs/exit_codes.csv).

### M7. Rerun of 05 dropped the 06 section of model_log.md (artifact/provenance defect)

- **Original behavior:** `src/05_analysis_primary.py` writes
  `results/analysis/model_log.md` with `Path.write_text` (full overwrite),
  while `src/06_balance_and_robustness.py` appends its section. Rerunning 05
  after 06 therefore deleted the model-call record for the R2 statsmodels
  OLS (AGENTS.md rule 5 provenance).
- **Cause:** asymmetric write modes (overwrite vs append) combined with
  out-of-order reruns during the M6 correction (05 was rerun while 06's
  section was already on disk).
- **Impact:** no statistical output affected; all ten statistical CSVs
  remained byte-identical. The loss was confined to the model-call log.
- **Correction:** rerun 06 (append restores its section), then rerun 08 so
  the INT check reflects the enlarged sha256 log. No code change; ordering
  documented here as the operational rule: after a 05-only rerun, rerun 06
  before publishing artifacts.
- **Retest:** 06 and 08 rerun sequentially; model_log.md again contains both
  sections; VT-1..VT-9 + INT all PASS; CSVs byte-identical to tag
  `pre-unit-label-fix`.
- **Update (2026-11-18, M8 correction):** the operational rule is now enforced
  in code: 05 and 06 both use an idempotent `upsert_model_log()` that replaces
  only their own section. Verified by rerunning 05 alone (the 06 section
  survives, 1 copy) and then 06 alone (no duplicate section is created).
- **Logged via:** the 2026-11-18 run logs for 06 and 08 in results/logs/ and
  results/logs/exit_codes.csv.

### M9. VT-10 negative control was case-sensitive (test-construction defect; first 08 run failed)

- **Original behavior (verbatim from run log
  `.20261118T133544Z`):** `FAIL  VT-10: R3 decomposition: recomputation,
  shares, caveats, negative controls — negative control not detected`
  (exit 1; failure copy preserved).
- **Cause:** the negative control removed the required caveat with
  `r3_md.replace("arithmetic identity", "")`, which is case-sensitive. The
  R3 section contains both "Arithmetic identity with midpoint weights"
  (heading sentence) and "This is an arithmetic identity", so the phrase
  survived the removal, the caveat checker correctly found nothing missing,
  and the negative control returned False. All substantive VT-10 checks
  (recomputation, identity, shares) had already passed.
- **Correction:** the negative control now uses a case-insensitive regex
  substitution before re-running the same caveat checker.
- **Retest:** PASSED — rerun `.20261118T133621Z` exited 0 with VT-10 PASS
  (11/11 overall); the followed-up full sequence `.20261118T133639Z` also
  11/11 PASS. All substantive VT-10 checks had already passed before the fix;
  only the negative-control construction changed.
- **Logged via:** results/logs/main-analysis-2026-11-18__08_reconcile_and_report
  .20261118T133544Z.txt and timestamped failure copy (exit code 1 in
  results/logs/exit_codes.csv).

### M8. R3 two-part decomposition: causal overreach and missing descriptive caveat
    (interpretation/reporting error; identified by robustness audit 2026-11-18)

- **Original erroneous statement (verbatim):** agent's final report message to
  the professor, 2026-11-12 (previously unsaved; now preserved verbatim in
  results/analysis/human_verification/agent_report_claim_evidence_2026-11-12.md):
  "converter-spend differences are essentially zero (−$0.0043 / +$0.0575) —
  the spend effect is driven by more converters, not higher spend per
  converter (`robustness_transformations.csv`, descriptive decomposition)."
  Related artifact wording (results/analysis/robustness.md pre-correction):
  "term1 Δconv × avg converter spend" / "term2 avg conv rate × Δ converter
  spend", with no identity statement and no "second term descriptive" caveat
  required by plan.md §8.
- **Independent audit evidence:** independent_robustness_audit.md:
  "The two-part decomposition is an arithmetic identity, not a causal
  mediation analysis. Mean spend among converters conditions on a
  post-treatment outcome; these groups need not be comparable under
  randomization." The audit reproduced every number (OLS coefficients/SEs/CIs,
  log1p Welch tests, decomposition terms) at floating-point precision and
  reported: Womens conditional-spend difference +$7.892057 contributing
  +$0.057467 (≈13.5% of the +$0.424412 total; midpoint weights; ≈16.4% under
  control-side weights; Mens ≈−0.6%). Therefore "essentially zero" is valid
  only for Mens, and "not higher spend per converter" is incorrect for
  Womens. No numerical error existed: the defect was interpretive.
- **Root cause:** the agent read an exact arithmetic decomposition of a
  randomized total as a causal mechanism split ("driven by"), used the
  plan's midpoint weighting without disclosing weighting sensitivity, and
  omitted the plan-mandated statement that the conditional-spend term is
  descriptive (post-treatment conditioning).
- **Correction:** robustness.md R3 rewritten: explicit formula
  ΔE[spend] = ΔP(conversion) × (m1 + m0)/2 + ((p1 + p0)/2) × (m1 − m0);
  component definitions with units (USD per randomized customer) and
  share-of-total percentages; "arithmetic identity, not a causal mediation
  analysis" statement; post-treatment descriptive caveat; weighting-convention
  note. R2 table units labeled; R1 scope clarified ("R2–R6 retain all rows").
  reconciliation_report.md summary now compares quantities only on their own
  scales. No estimate, SE, CI or p-value changed: all substantive statistical
  CSVs are byte-identical to the pre-correction snapshot (tags
  `pre-r3-interpretation-fix`).
- **Test results:** VT-10 executed in the 08 runs `.20261118T133621Z` and
  `.20261118T133639Z`: PASS. It independently recomputes term1/term2/total
  from data/raw (agreement ≤1e-9), verifies term1+term2=total, checks the six
  displayed values and percentage shares (tolerance 5e-7 and 0.1 pp), requires
  the caveat phrases, rejects R3-specific mechanism language ("driven by",
  "attributable to", "mediated by", "because of the email") inside the R3
  section only, and runs negative controls (missing caveat, mechanism
  sentence, wrong share) — all detected. VT-1..VT-9 + INT remain PASS
  (11/11). Language checks are supplementary and are not proof of correct
  causal reasoning.
- **Remaining limitations:** the audit is a separate computational review,
  not a full independent human audit; it did not cover balance, BH, bootstrap,
  funnel, R1, or causal assumptions. Shares remain weighting-convention
  dependent (midpoint weights are the plan choice). VT-10 tests the generated
  R3 section, not manually written text or reasoning quality. Human blinded
  review (VERIFICATION_PROTOCOL.md) is still pending.
- **Preservation:** original wording is in Commit C (`f71ea24`, annotated tag
  `pre-r3-interpretation-fix`) as the dated evidence record; the correction is
  a separate commit, so the pre/post difference is auditable in Git.
- **Logged via:** results/logs/main-analysis-2026-11-18__06_balance_and_robustness
  .20261118T133537Z.txt, `.20261118T133635Z.txt`, and the 08 logs
  `.20261118T133621Z.txt`, `.20261118T133639Z.txt` (exit 0 each).

---

## Documentation update (2026-11-18) — attribution, entry-4 closure, README gap

This section is **append-only**: no earlier entry, quote, number, or verdict in
this file has been altered. It records clarifications required before
publication.

### Attribution clarification

- The labels "professor review" in the 2026-11-05 entries record
  **human-directed review rounds** — project-owner oversight and accept/reject
  decisions. The **computational authorship** of the recomputations performed
  in those rounds is not documented. This file does not claim that the
  professor personally performed, typed, or independently re-derived any
  calculation.
- The two audit reports in `results/analysis/human_verification/` are
  **separate AI computational audits**. Their model and author identities are unrecorded.
  They are not a human audit and are not described as one.
- The duplicate-row instrument controls and VT-1…VT-10 are **agent-authored
  automated verification**. Agreement between two agent-written calculation
  paths rules out coding slips; it does not establish independence.
- **No fully independent human audit has been completed.**
  `VERIFICATION_PROTOCOL.md` Stages 1–3 remain pending.
- No verified AI model identity, prompt log, or model-call timestamp record
  exists; see `MODEL_USE_DISCLOSURE.md` for the verified / reported / unknown
  tiers.

### Entry 4 closure — "36,288 covariate cells"

- The number **36,288 is withdrawn**. The stated factors multiply to **13,608**
  using the three observed mens/womens combinations, or **18,144** with a
  hypothetical fourth combination.
- **No replacement recomputation is recorded.** The number was never used in
  any analysis, table, or reported estimate.
- Status: **closed as a withdrawn unsupported number**. The re-test column
  remains "none recorded" rather than "PASS"; this is a resolved
  documentation item, not a verified numerical result.

### README documentation gap

- The pre-existing `README.md` sentence "`plan.md` is intentionally empty until
  the analysis plan is approved" was stale. `plan.md` v1.1 was approved in
  commit `7f6b11c` (2026-11-12), and the main analysis was executed afterwards.
- The sentence has been replaced in the 2026-11-18 documentation commit. This
  gap was not previously recorded in `mistakes.md`; it is a repository
  documentation defect, not an analysis error, and is not counted among the
  21 confirmed error items.

### Classification note

The earlier §R3 "Classification index" was a preliminary grouping. The
authoritative, non-overlapping classification and the checked totals
(21 confirmed error items + 2 methodological ambiguities = 23 documented
items) are in `docs/error_taxonomy.md`. Items are counted once by primary
category; cross-references are not double-counted.

---

## Final accuracy correction (2026-11-18) — README interval description (M10)

This section is **append-only**: no earlier entry, quote, number, or verdict has
been altered.

### M10. README claimed the bootstrap percentile intervals "bracket" the Welch intervals

- **Original (verbatim):** "R5 bootstrap | Mens [+0.486360, +1.058330];
  Womens [+0.171673, +0.681706]; percentile CIs bracket the Welch CIs"
  (`README.md` §E.3, commit `e3ca0ea`). The same sentence is emitted by
  `src/08_reconcile_and_report.py` (line 541) into
  `results/analysis/reconciliation_report.md`.
- **Why it is wrong:** "bracket" asserts that the percentile interval encloses
  the Welch interval. The Welch spend intervals are Mens
  [+0.485140, +1.054515] and Womens [+0.168957, +0.679868]
  (`primary_results.csv`). Both percentile endpoints are higher than the
  corresponding Welch endpoints: Mens +0.001220 / +0.003815, Womens
  +0.002716 / +0.001838 USD. Neither interval contains the other; the widths
  are nearly identical (Mens 0.571970 vs 0.569375; Womens 0.510032 vs
  0.510911 USD), so the intervals are highly similar and substantially
  overlapping, not nested.
- **Detection:** human-directed final README accuracy review,
  2026-11-18; endpoint comparison performed by the agent against
  `results/analysis/robustness_bootstrap.csv` and `primary_results.csv`.
  The correction was specified in the review; the comparison is not a
  completed human audit.
- **Correction:** `README.md` §E.3 now reports the intervals as highly similar
  and substantially overlapping, notes the small upward endpoint shift and the
  absence of containment, and flags that the generated
  `reconciliation_report.md` still carries the earlier wording. No estimate,
  SE, CI, p-value or other numerical result changed.
- **Verification:** direct endpoint arithmetic (values above), re-checked
  against both CSVs. No automated VT covers this sentence; VT-7/VT-8/VT-10 do
  not test interval containment, so no PASS is claimed. Correcting the
  generated report would require changing `src/08` and rerunning it, which this
  documentation-only correction does not do.

### Related qualifications (not separate error items)

- The README statements comparing campaigns were rewritten to distinguish
  larger observed point estimates from a statistically established
  between-campaign difference. The Men's estimates are larger in this sample
  (ratios ≈1.69 visit, ≈1.81 spend, ≈2.19 conversion), but the six confirmatory
  tests are each campaign versus No E-Mail; `plan.md` lists a Mens-vs-Womens
  contrast only as exploratory, and no such estimate is reported. The revision
  adds no test.
- The reproducibility section now states that the exact file matching the
  documented SHA-256 is required and that the repository does not guarantee
  access to it.
- Open item (not counted as an error): `plan.md` §4/§14 lists Mens-vs-Womens
  and pre-treatment subgroup analyses in the exploratory set, but no such
  estimates are reported in `results/`. The README rule-4 caveat records this
  incompleteness. Whether the exploratory list was a requirement or a menu is
  not documented, so it is flagged as an unresolved plan-compliance question,
  not scored as a failure.

### Count supersession

This entry adds one reporting/interpretation error (M10). The authoritative
counts are therefore **22 confirmed error items + 2 methodological ambiguities
= 24 documented items**; category totals 2 + 8 + 6 + 2 + 4 = 22. The 21/23
figures in earlier sections of this file are retained unaltered as the
pre-M10 record.
