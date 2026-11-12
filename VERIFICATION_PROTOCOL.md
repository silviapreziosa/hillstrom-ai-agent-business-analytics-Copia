# Independent Verification Protocol

Status qualifier: **all verification to date is agent-authored.** No result in
this repository may be labeled "independently verified" until Stage 3 below is
completed by a named human reviewer.

## Objective

Allow a human reviewer to check selected calculations **without using the
agent's scripts**, so the agent's code and arithmetic are not merely re-run by
the same agent.

## Stage 1 — blinded recomputation (reviewer; agent's code withheld)

The reviewer receives ONLY:
1. `data/raw/hillstorm_no_indices.csv` — identified by
   SHA-256 `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`
   (or the file itself, if distribution rights allow).
2. `src/fixtures/nc1_visit.csv`, `nc2_spend.csv`, `nc3_collision.csv`,
   `pc1_invariance.csv` (10/8/3/12 rows — small enough to check by hand).
3. The **expected-results table** (target values and tolerance classes only):
   the `reported_expected` + `tolerance` columns of
   `results/verification/dup_comparison.csv`, and the expected values in
   `results/verification/dup_negative_controls.csv`.

The reviewer receives **none** of `src/01–04`.

Tasks (reviewer's own tool: spreadsheet, R, SQL, awk, or hand arithmetic —
Python/pandas permitted only if the reviewer insists, and then flagged):
- T1: hand-verify all fixture quantities (NC-1: 0.4/0.2 → 0.25/0.25, Δ = −1/5;
  NC-2: 50/25 → 100/3 each, Δ = −25; NC-3: 3→2 rows, means 1/3 → 1/2, Δ = +1/6;
  PC-1: Δ = 0, sizes 6/6 → 3/3, SE ratio 1/√2).
- T2: recompute the 48 real-data targets: per-arm n, means, Mens−No contrasts
  (S1 and S2), duplicate bookkeeping (6,562 / 7,634 / 1,072 / per-arm), funnel
  counts (9,394 / 578 / 0 / 0), and the S1→S2 deltas.
- T3: independently verify `data/raw/` SHA-256 and that the file is unchanged.

## Stage 2 — comparison and sign-off

Reviewer records, for each target: their value, the reported value, match (within
tolerance class) or mismatch, tool used, and date. **Any mismatch quarantines
the affected result**: it is re-opened in `mistakes.md`, never silently fixed.

## Stage 3 — unblinding and code review

Only after Stage 2 sign-off is the agent's code (`src/01–04`) revealed, to
review the *method* (dedup semantics over all 12 columns, value canonicalisation,
tolerance definitions) — not to re-derive the numbers.

## Recording

- Reviewer's environment, tool, values, and sign-off are stored in
  `results/external/<reviewer-name>/`.
- On completion, `results/verification/verification_log.md` is amended from
  "agent-authored" to "externally verified by <name>, <date>, <tool>".
- On any discrepancy, `mistakes.md` gains a dated entry (original claim
  preserved verbatim; correction; re-test outcome).

## Non-reuse constraint

The reviewer must not open, run, or port the agent's scripts before Stage 3.
Re-running the agent's own code does not constitute independent verification.
