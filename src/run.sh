#!/usr/bin/env bash
# src/run.sh — evidence-preserving execution wrapper (approved 2026-11-12).
#
# Usage:  src/run.sh <script-filename> <run-id>
#   e.g. src/run.sh 01_verify_duplicates_primary.py baseline-rerun-1
#
# Behaviour:
#   * Runs .venv/bin/python src/<script> with stdout+stderr captured to
#     results/logs/<run-id>__<script-stem>.<UTC-timestamp>.txt
#   * NEVER overwrites an existing log (timestamped filenames; append-only).
#   * Appends one line to results/logs/exit_codes.csv:
#         script,run_id,timestamp_utc,exit_code
#   * On a non-zero exit, additionally copies the log to
#     <run-id>__<script-stem>_first_run_fail.txt so failures are preserved
#     as evidence, not overwritten by later successful reruns.
#
# Note (documented limitation): the first-run failure logs of the 2026-11-05
# verification session were overwritten before this wrapper existed and cannot
# be recovered from the existing files; they survive only in the session
# transcript. See mistakes.md.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="${1:-}"
RUN_ID="${2:-}"

if [ -z "$SCRIPT" ] || [ -z "$RUN_ID" ]; then
    echo "usage: src/run.sh <script-filename> <run-id>" >&2
    exit 64
fi
if [ ! -f "$ROOT/src/$SCRIPT" ]; then
    echo "script not found: src/$SCRIPT" >&2
    exit 66
fi

LOGDIR="$ROOT/results/logs"
mkdir -p "$LOGDIR"
STEM="${SCRIPT%.py}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOGDIR/${RUN_ID}__${STEM}.${TS}.txt"

"$ROOT/.venv/bin/python" "$ROOT/src/$SCRIPT" > "$LOG" 2>&1
EC=$?

EC_FILE="$LOGDIR/exit_codes.csv"
if [ ! -f "$EC_FILE" ]; then
    printf 'script,run_id,timestamp_utc,exit_code\n' > "$EC_FILE"
fi
printf '%s,%s,%s,%d\n' "$SCRIPT" "$RUN_ID" "$TS" "$EC" >> "$EC_FILE"

if [ "$EC" -ne 0 ]; then
    cp "$LOG" "$LOGDIR/${RUN_ID}__${STEM}_first_run_fail.txt"
    echo "[run.sh] NONZERO EXIT $EC — log preserved: $LOG (failure copy: ${RUN_ID}__${STEM}_first_run_fail.txt)"
else
    echo "[run.sh] exit $EC — log: $LOG"
fi
exit "$EC"
