#!/usr/bin/env python3
"""
src/07_analysis_independent.py — Second calculation path (plan.md §10, VT-3).

Pure Python (csv + fractions) recomputation of the six headline ITT contrasts
and their statistics. Shares NO code and NO library with src/05's calculation
logic. data/raw/ is read-only; SHA-256 guarded. Agent-authored: agreement with
05 rules out coding slips but is NOT independent human validation.
Writes: results/analysis/{independent_recompute.csv,sha256_log.csv}.
"""
import csv
import hashlib
import math
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
PAIRS = [(MEN, NOE), (WOM, NOE)]
Z975 = 1.959963984540054


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_sha(stage: str, digest: str) -> None:
    p = OUT / "sha256_log.csv"
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp,script,stage,sha256\n")
        fh.write(f"{datetime.now(timezone.utc).isoformat()},07,{stage},{digest}\n")


h_before = sha256_file(RAW)
log_sha("before", h_before)

# exact accumulation per arm: visits, conversions, spend moments
acc = {a: {"n": 0, "v": 0, "c": 0, "ss": Fraction(0), "ss2": Fraction(0),
           "sc_spend": Fraction(0), "conv_n": 0}
       for a in (MEN, NOE, WOM)}
total = 0
with open(RAW, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        a = row["segment"]
        rec = acc[a]
        rec["n"] += 1
        rec["v"] += int(row["visit"])
        rec["c"] += int(row["conversion"])
        s = Fraction(row["spend"])
        rec["ss"] += s
        rec["ss2"] += s * s
        if int(row["conversion"]) == 1:
            rec["sc_spend"] += s
            rec["conv_n"] += 1
        total += 1
assert total == 64000

rows = []
for t_arm, c_arm in PAIRS:
    a1, a0 = acc[t_arm], acc[c_arm]
    n1, n0 = a1["n"], a0["n"]
    for outcome in ("visit", "conversion"):
        k1 = a1["v"] if outcome == "visit" else a1["c"]
        k0 = a0["v"] if outcome == "visit" else a0["c"]
        p1, p0 = Fraction(k1, n1), Fraction(k0, n0)
        d = p1 - p0
        se = math.sqrt(float(p1 * (1 - p1)) / n1 + float(p0 * (1 - p0)) / n0)
        z = float(d) / se
        p = math.erfc(abs(z) / math.sqrt(2.0))
        rows.append({"pair": f"{t_arm} minus {c_arm}", "outcome": outcome,
                     "estimate": float(d), "se": se, "test_stat": z,
                     "df": "", "ci_lo": float(d) - Z975 * se,
                     "ci_hi": float(d) + Z975 * se, "raw_p": p,
                     "relative_uplift": float(p1 / p0 - 1)})
    # spend: Welch
    m1 = a1["ss"] / n1
    m0 = a0["ss"] / n0
    v1 = (a1["ss2"] - a1["ss"] * a1["ss"] / n1) / (n1 - 1)
    v0 = (a0["ss2"] - a0["ss"] * a0["ss"] / n0) / (n0 - 1)
    se1, se0 = v1 / n1, v0 / n0
    se = math.sqrt(float(se1 + se0))
    d = m1 - m0
    t_stat = float(d) / se
    nu = float((se1 + se0) ** 2 / (se1 * se1 / (n1 - 1) + se0 * se0 / (n0 - 1)))
    p = float(2 * stats.t.sf(abs(t_stat), nu))
    crit = float(stats.t.ppf(0.975, nu))
    rows.append({"pair": f"{t_arm} minus {c_arm}", "outcome": "spend",
                 "estimate": float(d), "se": se, "test_stat": t_stat,
                 "df": nu, "ci_lo": float(d) - crit * se,
                 "ci_hi": float(d) + crit * se, "raw_p": p,
                 "relative_uplift": float(m1 / m0 - 1)})

with open(OUT / "independent_recompute.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pair", "outcome", "estimate", "se",
                                       "test_stat", "df", "ci_lo", "ci_hi",
                                       "raw_p", "relative_uplift"])
    w.writeheader()
    w.writerows(rows)

h_after = sha256_file(RAW)
log_sha("after", h_after)
assert h_before == h_after, "data/raw changed during run!"
print(f"[integrity] data/raw SHA-256 unchanged: {h_after}")
print(f"[done] six contrasts recomputed exactly (fractions); "
      f"wrote independent_recompute.csv")
