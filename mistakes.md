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
