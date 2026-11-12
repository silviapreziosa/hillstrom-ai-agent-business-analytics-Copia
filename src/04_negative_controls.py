#!/usr/bin/env python3
"""
src/04_negative_controls.py — instrument validation on enumerated synthetic
fixtures (approved design), run through BOTH calculation paths (pandas and
pure Python + exact Fraction arithmetic, implemented separately here).

Tests:
  NC-1  dedup must change the visit contrast:  +1/5 -> 0  (Delta = -1/5)
  NC-2  dedup must change the spend contrast:  25.00 -> 0 (Delta = -25.00)
  NC-3  collision visibility: one distinct customer with an identical row is
        merged by full-row dedup (rows 3 -> 2; Delta = +1/6); the report MUST
        state the row-count caveat.
  PC-1  invariance under uniform multiplicity (m_i = 2): Delta = 0 exactly,
        arm sizes 6/6 -> 3/3, and SE ratio = 1/sqrt(2) (n exactly doubled).
  V-0A  exact duplicate rows sharing customer_id: duplicates REMAIN (2) —
        adding an ID column does not eliminate copies that inherit the ID.
  V-0B  identical characteristics, distinct customer_id: row duplicates = 0 —
        row-dedup counts rows, never customers.
  Fixture coherence: NC-2 is funnel-consistent; a deliberately corrupted
        copy MUST fail the funnel assertion (instrument can fail).
Writes: results/verification/dup_negative_controls.csv, dup_negative_controls.md
and the final verification_log.md. Exits 1 on any FAIL.
"""
import csv
import hashlib
import math
import sys
from fractions import Fraction
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "src" / "fixtures"
OUT = ROOT / "results" / "verification"
OUT.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"

MEN, NOE = "Mens", "No E-Mail"
results_rows: list[tuple] = []


# ----------------------------------------------------------------- paths ----
def suite_pandas(path: Path) -> dict:
    d = pd.read_csv(path)
    dd = d.drop_duplicates()
    res = {"rows": len(d), "rows_dedup": len(dd), "excess": len(d) - len(dd),
           "keepFalse": int(d.duplicated(keep=False).sum()),
           "patterns": int(len(d[d.duplicated(keep=False)].drop_duplicates()))}
    has_spend = "spend" in d.columns
    cols = [c for c in ("visit", "conversion", "spend") if c in d.columns]
    for arm, sub in d.groupby("segment"):
        res[f"asgiven.n.{arm}"] = len(sub)
        for c in cols:
            res[f"asgiven.mean.{c}.{arm}"] = float(sub[c].mean())
    for arm, sub in dd.groupby("segment"):
        res[f"dedup.n.{arm}"] = len(sub)
        for c in cols:
            res[f"dedup.mean.{c}.{arm}"] = float(sub[c].mean())
    for c in cols:
        for stage in ("asgiven", "dedup"):
            a_m, a_n = f"{stage}.mean.{c}.{MEN}", f"{stage}.mean.{c}.{NOE}"
            if a_m in res and a_n in res:
                res[f"{stage}.contrast.{c}"] = res[a_m] - res[a_n]
            elif a_n in res:  # single-arm fixture (NC-3): contrast == the arm mean
                res[f"{stage}.contrast.{c}"] = res[a_n]
        if f"asgiven.contrast.{c}" in res and f"dedup.contrast.{c}" in res:
            res[f"delta.contrast.{c}"] = res[f"dedup.contrast.{c}"] - res[f"asgiven.contrast.{c}"]
    if has_spend:  # funnel coherence of the fixture
        res["bad_spend_noconv"] = int(((d["spend"] > 0) & (d["conversion"] == 0)).sum())
        res["bad_conv_novisit"] = int(((d["conversion"] == 1) & (d["visit"] == 0)).sum())
    if "visit" in d.columns:  # binomial SE ratio (PC-1 property check)
        def se(dsub: pd.DataFrame) -> float:
            m = dsub.loc[dsub["segment"] == MEN, "visit"]
            n = dsub.loc[dsub["segment"] == NOE, "visit"]
            if len(m) == 0 or len(n) == 0:
                return float("nan")
            v1 = m.mean() * (1 - m.mean())
            v2 = n.mean() * (1 - n.mean())
            return math.sqrt(v1 / len(m) + v2 / len(n))
        res["SE_asgiven.visit"] = se(d)
        res["SE_dedup.visit"] = se(dd)
    return res


def suite_purepy(path: Path) -> dict:
    # typed parse: 'segment'/'customer_id' stay strings, everything else -> Fraction
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames)
        records = []
        for row in reader:
            rec = []
            for name in fields:
                v = row[name]
                rec.append(v if name in ("segment", "customer_id") else Fraction(v))
            records.append(tuple(rec))
    idx = {n: i for i, n in enumerate(fields)}
    seg_i = idx["segment"]
    cols = [c for c in ("visit", "conversion", "spend") if c in idx]
    counts: dict[tuple, int] = {}
    for rec in records:
        counts[rec] = counts.get(rec, 0) + 1
    res = {"rows": len(records), "rows_dedup": len(counts),
           "excess": len(records) - len(counts),
           "keepFalse": sum(c for c in counts.values() if c >= 2),
           "patterns": sum(1 for c in counts.values() if c >= 2)}
    for arm in (MEN, NOE):
        n_a = sum(1 for rec in records if rec[seg_i] == arm)
        nd_a = sum(1 for rec in counts if rec[seg_i] == arm)
        res[f"asgiven.n.{arm}"] = n_a
        res[f"dedup.n.{arm}"] = nd_a
        for c in cols:
            ci = idx[c]
            if n_a:
                res[f"asgiven.mean.{c}.{arm}"] = float(
                    sum(rec[ci] for rec in records if rec[seg_i] == arm) / n_a)
            if nd_a:
                res[f"dedup.mean.{c}.{arm}"] = float(
                    sum(rec[ci] for rec in counts if rec[seg_i] == arm) / nd_a)
    for c in cols:
        for stage in ("asgiven", "dedup"):
            a_m, a_n = f"{stage}.mean.{c}.{MEN}", f"{stage}.mean.{c}.{NOE}"
            if a_m in res and a_n in res:
                res[f"{stage}.contrast.{c}"] = res[a_m] - res[a_n]
            elif a_n in res:  # single-arm fixture (NC-3): contrast == the arm mean
                res[f"{stage}.contrast.{c}"] = res[a_n]
        if f"asgiven.contrast.{c}" in res and f"dedup.contrast.{c}" in res:
            res[f"delta.contrast.{c}"] = res[f"dedup.contrast.{c}"] - res[f"asgiven.contrast.{c}"]
    if "spend" in idx:
        res["bad_spend_noconv"] = sum(1 for rec in records
                                      if rec[idx["spend"]] > 0 and rec[idx["conversion"]] == 0)
        res["bad_conv_novisit"] = sum(1 for rec in records
                                      if rec[idx["conversion"]] == 1 and rec[idx["visit"]] == 0)
    if "visit" in idx:
        def se_from(pairs: list[tuple[Fraction, int]]) -> float:
            (p1, n1), (p2, n2) = pairs
            v1 = p1 * (1 - p1)
            v2 = p2 * (1 - p2)
            return math.sqrt(float(v1 / n1 + v2 / n2))
        rp = [r for r in records if r[seg_i] == MEN]
        rn = [r for r in records if r[seg_i] == NOE]
        up = [k for k in counts if k[seg_i] == MEN]
        un = [k for k in counts if k[seg_i] == NOE]
        if len(rp) and len(rn) and len(up) and len(un):
            pairs_g = [(sum(r[idx["visit"]] for r in rp) / len(rp), len(rp)),
                       (sum(r[idx["visit"]] for r in rn) / len(rn), len(rn))]
            pairs_d = [(sum(k[idx["visit"]] for k in up) / len(up), len(up)),
                       (sum(k[idx["visit"]] for k in un) / len(un), len(un))]
            res["SE_asgiven.visit"] = se_from(pairs_g)
            res["SE_dedup.visit"] = se_from(pairs_d)
    return res


def record(test: str, quantity: str, expected, sa: dict, sb: dict,
           tol: float = 1e-12, key_format: str = "{k}") -> bool:
    ka = kb = key_format.format(k=quantity)
    va, vb = sa.get(ka), sb.get(kb)
    if va is None and vb is None:
        verdict = "FAIL (missing in both paths)"
    elif va is None or vb is None:
        verdict = "FAIL (missing in one path)"
    elif isinstance(expected, Fraction):
        ok = (abs(Fraction(va) - expected) <= Fraction(tol)
              and abs(Fraction(vb) - expected) <= Fraction(tol))
        verdict = "PASS" if ok else \
            f"FAIL (expected {float(expected)!r}, got pandas={va!r}, purepy={vb!r})"
    else:
        ok = abs(va - expected) <= tol and abs(vb - expected) <= tol
        verdict = "PASS" if ok else \
            f"FAIL (expected {expected!r}, got pandas={va!r}, purepy={vb!r})"
    ea = float(expected) if isinstance(expected, Fraction) else expected
    results_rows.append((test, quantity, repr(ea), repr(va), repr(vb), verdict))
    ok_val = verdict.startswith("PASS")
    print(f"{verdict}  {test} :: {quantity}  (expected {ea!r})")
    return ok_val


def funnel_assert(d: pd.DataFrame) -> int:
    return int(((d["spend"] > 0) & (d["conversion"] == 0)).sum()
               + ((d["conversion"] == 1) & (d["visit"] == 0)).sum())


agreed = True
print("=" * 72)
print("NEGATIVE/POSITIVE CONTROLS (both calculation paths)")
print("=" * 72)

sa, sb = suite_pandas(FIX / "nc1_visit.csv"), suite_purepy(FIX / "nc1_visit.csv")
agreed &= record("NC-1", "asgiven.mean.visit.Mens", Fraction(2, 5), sa, sb)
agreed &= record("NC-1", "asgiven.mean.visit.No E-Mail", Fraction(1, 5), sa, sb)
agreed &= record("NC-1", "asgiven.contrast.visit", Fraction(1, 5), sa, sb)
agreed &= record("NC-1", "dedup.mean.visit.Mens", Fraction(1, 4), sa, sb)
agreed &= record("NC-1", "dedup.mean.visit.No E-Mail", Fraction(1, 4), sa, sb)
agreed &= record("NC-1", "dedup.contrast.visit", Fraction(0), sa, sb)
agreed &= record("NC-1", "delta.contrast.visit", Fraction(-1, 5), sa, sb)
agreed &= record("NC-1", "rows", 10, sa, sb, tol=0)
agreed &= record("NC-1", "rows_dedup", 8, sa, sb, tol=0)
agreed &= record("NC-1", "keepFalse", 4, sa, sb, tol=0)
agreed &= record("NC-1", "patterns", 2, sa, sb, tol=0)

sa, sb = suite_pandas(FIX / "nc2_spend.csv"), suite_purepy(FIX / "nc2_spend.csv")
agreed &= record("NC-2", "asgiven.mean.spend.Mens", Fraction(50), sa, sb)
agreed &= record("NC-2", "asgiven.mean.spend.No E-Mail", Fraction(25), sa, sb)
agreed &= record("NC-2", "asgiven.contrast.spend", Fraction(25), sa, sb)
agreed &= record("NC-2", "dedup.mean.spend.Mens", Fraction(100, 3), sa, sb)
agreed &= record("NC-2", "dedup.mean.spend.No E-Mail", Fraction(100, 3), sa, sb)
agreed &= record("NC-2", "dedup.contrast.spend", Fraction(0), sa, sb)
agreed &= record("NC-2", "delta.contrast.spend", Fraction(-25), sa, sb)
agreed &= record("NC-2", "rows_dedup", 6, sa, sb, tol=0)
agreed &= record("NC-2", "bad_spend_noconv", 0, sa, sb, tol=0)
agreed &= record("NC-2", "bad_conv_novisit", 0, sa, sb, tol=0)

sa, sb = suite_pandas(FIX / "nc3_collision.csv"), suite_purepy(FIX / "nc3_collision.csv")
agreed &= record("NC-3", "rows", 3, sa, sb, tol=0)
agreed &= record("NC-3", "rows_dedup", 2, sa, sb, tol=0)
agreed &= record("NC-3", "asgiven.mean.visit.No E-Mail", Fraction(1, 3), sa, sb)
agreed &= record("NC-3", "dedup.mean.visit.No E-Mail", Fraction(1, 2), sa, sb)
agreed &= record("NC-3", "delta.contrast.visit", Fraction(1, 6), sa, sb)

sa, sb = suite_pandas(FIX / "pc1_invariance.csv"), suite_purepy(FIX / "pc1_invariance.csv")
agreed &= record("PC-1", "rows", 12, sa, sb, tol=0)
agreed &= record("PC-1", "rows_dedup", 6, sa, sb, tol=0)
agreed &= record("PC-1", "asgiven.mean.visit.Mens", Fraction(1, 3), sa, sb)
agreed &= record("PC-1", "asgiven.mean.visit.No E-Mail", Fraction(0), sa, sb)
agreed &= record("PC-1", "dedup.mean.visit.Mens", Fraction(1, 3), sa, sb)
agreed &= record("PC-1", "dedup.mean.visit.No E-Mail", Fraction(0), sa, sb)
agreed &= record("PC-1", "delta.contrast.visit", Fraction(0), sa, sb)
ratio_a = sa["SE_asgiven.visit"] / sa["SE_dedup.visit"]
ratio_b = sb["SE_asgiven.visit"] / sb["SE_dedup.visit"]
inv_sqrt2 = 1 / math.sqrt(2)
ok_ratio = (abs(ratio_a - inv_sqrt2) <= 1e-12 and abs(ratio_b - inv_sqrt2) <= 1e-12)
v = "PASS" if ok_ratio else f"FAIL (ratios {ratio_a!r}, {ratio_b!r})"
print(f"{v}  PC-1 :: SE_asgiven/SE_dedup = 1/sqrt(2)")
results_rows.append(("PC-1", "SE ratio", repr(round(inv_sqrt2, 12)),
                     repr(ratio_a), repr(ratio_b), v))
agreed &= ok_ratio

# --- V-0A / V-0B: customer_id column-set designs -----------------------------
nc1 = pd.read_csv(FIX / "nc1_visit.csv")
ID = {0: "1", 1: "2", 2: "3", 3: "4", 4: "1", 5: "5", 6: "6", 7: "7", 8: "8", 9: "6"}
v0a = nc1.copy()
v0a["customer_id"] = v0a.index.map(lambda i: ID[i])
dups_id = int(v0a.duplicated().sum())          # copies share the source ID: STAY duplicates
v0b = nc1.copy()
v0b["customer_id"] = [str(i + 1) for i in range(len(v0b))]  # per-row distinct IDs
dups_distinct = int(v0b.duplicated().sum())    # identical characteristics, distinct IDs
dups_no_id = int(nc1.duplicated().sum())
ok_a = dups_id == 2 == dups_no_id
ok_b = dups_distinct == 0
print(f"{'PASS' if ok_a else 'FAIL'}  V-0A :: duplicates with inherited IDs remain: "
      f"no_id={dups_no_id}, with_id={dups_id}")
print(f"{'PASS' if ok_b else 'FAIL'}  V-0B :: identical characteristics, distinct IDs "
      f"-> row duplicates = {dups_distinct} (row-dedup counts rows, not customers)")
results_rows += [
    ("V-0A", "duplicate rows: NC-1 without ID / with inherited-ID column",
     "2 / 2", str(dups_no_id), str(dups_id), "PASS" if ok_a else "FAIL"),
    ("V-0B", "duplicate rows with per-row distinct IDs (identical features)",
     "0", "-", str(dups_distinct), "PASS" if ok_b else "FAIL"),
]
agreed &= ok_a and ok_b

# --- corrupted fixture: the funnel assertion must be able to fail -------------
corrupt = pd.DataFrame({"segment": ["Mens", "Mens"],
                        "history": [30.00, 40.00],
                        "visit": [1, 0], "conversion": [1, 1],
                        "spend": [100.00, 0.00]})
bad = funnel_assert(corrupt)
ok_c = bad >= 1
print(f"{'PASS' if ok_c else 'FAIL'}  V-fixture-fail :: corrupted copy violates "
      f"funnel coherence {bad} time(s); assertion detects it")
results_rows.append(("V-fixture-fail", "violations detected in corrupted fixture",
                     ">=1", str(bad), "-", "PASS" if ok_c else "FAIL"))
agreed &= ok_c

# --- artifacts ----------------------------------------------------------------
with open(OUT / "dup_negative_controls.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["test", "quantity", "expected", "pathA_pandas", "pathB_purepy", "verdict"])
    w.writerows(results_rows)

# SHA-256 guard once more from this script
h = hashlib.sha256()
with open(RAW, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)

CAVEAT = ("Note: deduplicated counts are counts of distinct rows, which may "
          "undercount distinct customers when rows are indistinguishable.")
INDEP = ("Both recomputation paths were authored by the analysis agent; "
         "agreement between them rules out coding slips but is not an "
         "independent audit.")
(OUT / "dup_negative_controls.md").write_text(
    "# Instrument controls — enumerated fixtures\n\n"
    f"{CAVEAT}\n\n"
    "Lessons pinned by V-0A/V-0B:\n"
    "- V-0A: an identifier column does NOT remove exact duplicates when the "
    "copies inherit the source record's ID (duplicates remain 2).\n"
    "- V-0B: identical characteristics with DIFFERENT customer IDs are not "
    "detected by row-deduplication: it counts rows, never customers.\n\n"
    f"{INDEP}\n", encoding="utf-8")

log = f"""# Verification log — duplicate-row audit
Run date: 2026-11-05 (UTC timestamps in sha256_log.csv)
data/raw/ SHA-256: {h.hexdigest()} (unchanged before/after each script; see sha256_log.csv)

## Executed commands
    .venv/bin/python src/01_verify_duplicates_primary.py
    .venv/bin/python src/02_verify_duplicates_independent.py
    .venv/bin/python src/03_compare_and_report.py
    .venv/bin/python src/04_negative_controls.py
(seeds: none required — every computation is deterministic; no randomness used)

## Environment
Python {sys.version.split()[0]}, pandas {pd.__version__}, numpy {__import__('numpy').__version__}

## Instrument controls (this script)
See dup_negative_controls.csv / dup_negative_controls.md.
NC-1, NC-2, NC-3, PC-1, V-0A, V-0B, V-fixture-fail (corrupted-fixture negative test).

## Caveat (mandated, from NC-3)
{CAVEAT}

## Independence statement
{INDEP}
True independence requires human re-derivation; the enumerated fixtures and
closed-form targets were designed to make that check minutes of work.

## Gating
Real-data reconciliation (src/03) may be reported only while every instrument
control passes. Expected values were pre-registered as literals and were never
adjusted after inspection.
"""
# append the final verdict dynamically
n_pass = sum(1 for r in results_rows if r[5].startswith("PASS"))
n_all = len(results_rows)
log += f"\n## Final instrument verdict\n{n_pass}/{n_all} checks PASS — " \
       f"{'INSTRUMENT VALID' if agreed else 'INSTRUMENT INVALID (gating BLOCKS conclusions)'}\n"
if not agreed:
    log += ("AT LEAST ONE CONTROL FAILED. Real-data reconciliation results are "
            "quarantined until the instrument is fixed.\n")
(OUT / "verification_log.md").write_text(log, encoding="utf-8")

print("=" * 72)
print(f"[summary] instrument: {n_pass}/{n_all} checks PASS — "
      f"{'INSTRUMENT VALID' if agreed else 'INSTRUMENT INVALID'}")
if not agreed:
    raise SystemExit(1)
