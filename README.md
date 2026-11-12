# my-analysis

Business Analytics project: evaluation of an AI agent performing a
reproducible, verifiable analysis (see `AGENTS.md` for the governing rules).

## Status

- **Verification of the duplicate-row audit is agent-authored.** Two
  calculation paths were both written by the analysis agent; agreement between
  them rules out coding slips but has **not** received independent human
  validation. See `results/verification/verification_log.md` and
  `VERIFICATION_PROTOCOL.md` for the protocol that will change this status.
- `mistakes.md` records every detected error, its correction, and re-test
  outcomes. `plan.md` is intentionally empty until the analysis plan is
  approved.

## Data provenance

- File: `data/raw/hillstorm_no_indices.csv` (12 columns, 64,000 rows + header).
- **SHA-256:** `00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0`
  (recorded across all execution stages in `results/verification/sha256_log.csv`).
- **The raw dataset is NOT committed to this repository** (approved Option B,
  2026-11-12). Its contents are never modified by any script (AGENTS.md rule 1).
- Schema is consistent with the well-known Hillstrom "MineThatData Email
  Analytics" dataset (64,000 customers, three-arm email experiment), but this
  provenance is **unverified** and **no redistribution rights are claimed**
  until independently confirmed. Obtainers must locate and verify the source
  themselves; the SHA-256 above is the integrity anchor.
