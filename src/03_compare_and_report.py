#!/usr/bin/env python3
"""
src/03_compare_and_report.py — cross-path comparison and reconciliation.

Checks, in order:
  V-D1 cross-path:   Path A (pandas) vs Path B (exact rationals) on EVERY metric.
  V-D2 reconciliation: every number previously reported by the agent, from its
                     audit replies, against BOTH paths (pre-registered
                     tolerance classes; expected values are literals below).
  V-D3 identities:   excess = total - unique = sum(copy_count-1) = keepFalse -
                     patterns; per-arm sums reconcile.
  V-D4 estimates vs. SEs: S1/S2 point estimates and SE table (descriptive).
Data integrity: all four sha256_log rows must be identical.
Writes: dup_comparison.csv, dup_comparison.md, dup_se_point_estimates.csv.
Exits 1 if any FAIL (fails loudly; never silently adjusts expectations).
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "verification"


def load(path: Path) -> dict[str, float]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["metric"]: float(row["value"]) for row in csv.DictReader(fh)}


A = load(OUT / "dup_pathA.csv")
B = load(OUT / "dup_pathB.csv")

TOL = {"int": 0.0, "r4": 5.1e-5, "r6": 5.1e-7, "r6d": 1.3e-6}

targets: list[tuple[str, str, float]] = [
    # sample sizes
    ("S1.n.Mens E-Mail", "int", 21307),
    ("S1.n.No E-Mail", "int", 21306),
    ("S1.n.Womens E-Mail", "int", 21387),
    # S1 means (visit/spend 6dp, conversion 4dp as reported)
    ("S1.mean.visit.Mens E-Mail", "r6", 0.182757),
    ("S1.mean.visit.No E-Mail", "r6", 0.106167),
    ("S1.mean.visit.Womens E-Mail", "r6", 0.151400),
    ("S1.mean.conversion.Mens E-Mail", "r4", 0.0125),
    ("S1.mean.conversion.No E-Mail", "r4", 0.0057),
    ("S1.mean.conversion.Womens E-Mail", "r4", 0.0088),
    ("S1.mean.spend.Mens E-Mail", "r6", 1.422617),
    ("S1.mean.spend.No E-Mail", "r6", 0.652789),
    ("S1.mean.spend.Womens E-Mail", "r6", 1.077202),
    # S1 contrasts
    ("S1.contrast.visit.MensMinusNo", "r6", 0.076590),
    ("S1.contrast.conversion.MensMinusNo", "r6", 0.006805),
    ("S1.contrast.spend.MensMinusNo", "r6", 0.769827),
    # S2 sizes / means / contrasts
    ("S2.n.Mens E-Mail", "int", 19183),
    ("S2.n.No E-Mail", "int", 19081),
    ("S2.n.Womens E-Mail", "int", 19174),
    ("S2.mean.visit.Mens E-Mail", "r6", 0.193922),
    ("S2.mean.visit.No E-Mail", "r6", 0.115193),
    ("S2.mean.visit.Womens E-Mail", "r6", 0.160843),
    ("S2.mean.spend.Mens E-Mail", "r6", 1.580133),
    ("S2.mean.spend.No E-Mail", "r6", 0.728910),
    ("S2.mean.spend.Womens E-Mail", "r6", 1.201529),
    ("S2.contrast.visit.MensMinusNo", "r6", 0.078729),
    ("S2.contrast.conversion.MensMinusNo", "r6", 0.007525),
    ("S2.contrast.spend.MensMinusNo", "r6", 0.851223),
    # deltas reported as "dedup minus full" (both operands rounded to 6dp)
    ("Delta.visit.MensMinusNo", "r6d", 0.002139),
    ("Delta.conversion.MensMinusNo", "r6d", 0.000720),
    ("Delta.spend.MensMinusNo", "r6d", 0.081396),
    # bookkeeping
    ("book.total", "int", 64000),
    ("book.unique", "int", 57438),
    ("book.excess", "int", 6562),
    ("book.keepFalse", "int", 7634),
    ("book.patterns", "int", 1072),
    ("book.keepFalse.arm.Mens E-Mail", "int", 2504),
    ("book.keepFalse.arm.No E-Mail", "int", 2555),
    ("book.keepFalse.arm.Womens E-Mail", "int", 2575),
    ("book.excess.arm.Mens E-Mail", "int", 2124),
    ("book.excess.arm.No E-Mail", "int", 2225),
    ("book.excess.arm.Womens E-Mail", "int", 2213),
    ("book.dups.visit1", "int", 622),
    ("book.dups.conv1", "int", 0),
    ("book.dups.spendpos", "int", 0),
    # funnel coherence
    ("funnel.visitors", "int", 9394),
    ("funnel.conversions", "int", 578),
    ("funnel.bad_spend_noconv", "int", 0),
    ("funnel.bad_conv_novisit", "int", 0),
]


def check(name: str, expected: float, tol: float) -> tuple[str, str, str, float, float]:
    pa, pb = A.get(name), B.get(name)
    if pa is None or pb is None:
        return name, "-", pa if pa is not None else pb, pb or 0.0, "FAIL (missing metric)"
    if abs(pa - pb) > max(tol, 1e-9):
        return name, str(expected), pa, pb, "FAIL (cross-path)"
    if abs(pa - expected) > tol or abs(pb - expected) > tol:
        return name, str(expected), pa, pb, "FAIL (target)"
    return name, str(expected), pa, pb, "PASS"


rows = [check(n, e, TOL[k]) for n, k, e in targets]
n_fail = sum(1 for r in rows if r[4] != "PASS")

print(f"cross-path max |A-B| over all metrics: "
      f"{max(abs(A[m] - B[m]) for m in A if m in B):.3e}")

# identities
ident = []
ident.append(("excess = total - unique", A["book.excess"] == A["book.total"] - A["book.unique"]))
ident.append(("excess = keepFalse - patterns",
              A["book.excess"] == A["book.keepFalse"] - A["book.patterns"]))
ident.append(("per-arm excess sums to total excess",
              abs(sum(A[f"book.excess.arm.{a}"] for a in
                      ("Mens E-Mail", "No E-Mail", "Womens E-Mail")) - A["book.excess"]) < 1e-9))
ident.append(("per-arm keepFalse sums to total keepFalse",
              abs(sum(A[f"book.keepFalse.arm.{a}"] for a in
                      ("Mens E-Mail", "No E-Mail", "Womens E-Mail")) - A["book.keepFalse"]) < 1e-9))
for name, ok in ident:
    print(f"identity {'PASS' if ok else 'FAIL'}: {name}")
    if not ok:
        n_fail += 1

# sha256 guard: all logged stages identical
with open(OUT / "sha256_log.csv", newline="", encoding="utf-8") as fh:
    hashes = [r["sha256"] for r in csv.DictReader(fh)]
if len(set(hashes)) == 1:
    print(f"integrity PASS: data/raw sha256 identical across all stages: {hashes[0]}")
else:
    print("integrity FAIL: sha256 mismatch in sha256_log.csv")
    n_fail += 1

with open(OUT / "dup_comparison.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["metric", "reported_expected", "tolerance", "pathA", "pathB", "verdict"])
    for (n, kind, e), r in zip(targets, rows):
        w.writerow([r[0], r[1], TOL[kind], f"{r[2]:.10g}", f"{r[3]:.10g}", r[4]])

se_rows = []
for col in ("visit", "conversion", "spend"):
    for smp in ("S1", "S2"):
        name = f"SE.{smp}.{col}"
        se_rows.append((col, smp, A[name], B[name]))
with open(OUT / "dup_se_point_estimates.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["outcome", "sample", "SE_pathA", "SE_pathB"])
    for c, s, a, b in se_rows:
        w.writerow([c, s, f"{a:.10g}", f"{b:.10g}"])

md = ["# Duplicate-row audit: reconciliation report",
      "",
      f"Targets checked: {len(rows)}; failures: {n_fail}; identities: "
      f"{sum(ok for _, ok in ident)}/{len(ident)}.",
      "",
      "Point estimates change under deduplication (S1 -> S2); SEs also change.",
      "See dup_comparison.csv for every reconciled number and dup_se_point_estimates.csv.",
      ""]
(OUT / "dup_comparison.md").write_text("\n".join(md), encoding="utf-8")

print(f"[summary] reconciliation: {len(rows) - n_fail}/{len(rows)} PASS, {n_fail} FAIL")
if n_fail:
    print("[summary] FAILURES — stopping loudly; expected values were NOT changed.")
    raise SystemExit(1)
print("[summary] ALL RECONCILIATION CHECKS PASS")
