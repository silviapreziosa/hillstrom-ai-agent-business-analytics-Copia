# Verification log — duplicate-row audit
Run date: 2026-11-05 (UTC timestamps in sha256_log.csv)
data/raw/ SHA-256: 00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0 (unchanged before/after each script; see sha256_log.csv)

## Executed commands
    .venv/bin/python src/01_verify_duplicates_primary.py
    .venv/bin/python src/02_verify_duplicates_independent.py
    .venv/bin/python src/03_compare_and_report.py
    .venv/bin/python src/04_negative_controls.py
(seeds: none required — every computation is deterministic; no randomness used)

## Environment
Python 3.13.9, pandas 3.1.1, numpy 2.5.4

## Instrument controls (this script)
See dup_negative_controls.csv / dup_negative_controls.md.
NC-1, NC-2, NC-3, PC-1, V-0A, V-0B, V-fixture-fail (corrupted-fixture negative test).

## Caveat (mandated, from NC-3)
Note: deduplicated counts are counts of distinct rows, which may undercount distinct customers when rows are indistinguishable.

## Independence statement
Both recomputation paths were authored by the analysis agent; agreement between them rules out coding slips but is not an independent audit.
True independence requires human re-derivation; the enumerated fixtures and
closed-form targets were designed to make that check minutes of work.

## Gating
Real-data reconciliation (src/03) may be reported only while every instrument
control passes. Expected values were pre-registered as literals and were never
adjusted after inspection.

## Final instrument verdict
37/37 checks PASS — INSTRUMENT VALID
