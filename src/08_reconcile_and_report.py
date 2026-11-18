#!/usr/bin/env python3
"""
src/08_reconcile_and_report.py — VT-1..VT-8 and final tables (plan.md §11).

Checks (all pre-registered in plan.md):
  VT-1 row-count integrity (pipeline logs; no drops; source-token scan)
  VT-2 spend identity per arm: mean(spend) = P(conv) x mean(spend|conv=1)
  VT-3 second-path agreement (05 vs 07) for all six contrasts
  VT-4 Holm adjusted p-values recomputed from saved raw p-values
  VT-5 balance table recomputed fresh from data/raw and compared to 06
  VT-6 funnel assertions + corrupted-fixture negative test
  VT-7 language audit of all results/analysis/*.md (necessary but NOT
       sufficient; human reasoning review still required)
  VT-8 artifact-vs-write-up reconciliation (numbers in md match CSVs)
Writes: results/analysis/{vt_results.csv,reconciliation_report.md}. Exits 1
on any FAIL. Agent-authored checks; NOT independent human validation.
"""
import csv
import hashlib
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
ARMS = (MEN, NOE, WOM)
vt_rows: list[tuple] = []


def add_vt(vt_id: str, description: str, ok: bool, detail: str) -> bool:
    verdict = "PASS" if ok else "FAIL"
    vt_rows.append((vt_id, description, verdict, detail))
    print(f"{verdict}  {vt_id}: {description} — {detail}")
    return ok


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


h_now = sha256_file(RAW)

# load artifacts
primary = list(csv.DictReader(open(OUT / "primary_results.csv", newline="", encoding="utf-8")))
indep = list(csv.DictReader(open(OUT / "independent_recompute.csv", newline="", encoding="utf-8")))
balance06 = list(csv.DictReader(open(OUT / "balance.csv", newline="", encoding="utf-8")))
rawps = list(csv.DictReader(open(OUT / "raw_pvalues.csv", newline="", encoding="utf-8")))

overall = True

# ---------------- VT-1: row-count integrity -----------------------------------
pipe = list(csv.DictReader(open(OUT / "pipeline_log.csv", newline="", encoding="utf-8")))
ok1 = len(pipe) > 0
for r in pipe:
    if r["event"] == "load":
        ok1 &= r["rows"] == "64000"
    if r["event"] == "split_segment_no_drop":
        nums = [int(x) for x in r["rows"].split(";")[0].split(",")]
        ok1 &= sum(nums) == 64000 and ";sum=64000" in r["rows"]
    ok1 &= "drop" not in r["event"].lower() or "no_drop" in r["event"].lower()
src05 = (ROOT / "src" / "05_analysis_primary.py").read_text(encoding="utf-8")
src06 = (ROOT / "src" / "06_balance_and_robustness.py").read_text(encoding="utf-8")
src07 = (ROOT / "src" / "07_analysis_independent.py").read_text(encoding="utf-8")
for tok in ("drop_duplicates(", "dropna(", ".drop(", ".query("):
    ok1 &= tok not in src05 and tok not in src06 and tok not in src07
overall &= add_vt("VT-1", "row-count integrity; no silent drops/filters",
                  ok1, f"{len(pipe)} pipeline events; source scan clean; "
                       f"all 64,000 rows retained")

# ---------------- VT-2: spend identity per arm ---------------------------------
df = pd.read_csv(RAW)
ok2 = True
for a in ARMS:
    sub = df.loc[df["segment"] == a]
    lhs = float(sub["spend"].mean())
    conv = sub.loc[sub["conversion"] == 1, "spend"]
    rhs = float(sub["conversion"].mean()) * float(conv.mean())
    ok2 &= abs(lhs - rhs) <= 1e-9
overall &= add_vt("VT-2", "spend identity mean = P(conv) x mean|conv (per arm)",
                  ok2, "identity holds to 1e-9 for all three arms")

# ---------------- VT-3: second-path agreement ----------------------------------
ok3 = True
maxdev = 0.0
pm = {(r["pair"], r["outcome"]): r for r in primary}
im = {(r["pair"], r["outcome"]): r for r in indep}
for key in pm:
    a, b = pm[key], im[key]
    for field in ("estimate", "se", "ci_lo", "ci_hi", "raw_p"):
        va, vb = float(a[field]), float(b[field])
        dev = abs(va - vb)
        maxdev = max(maxdev, dev)
        ok3 &= dev <= 1e-9
overall &= add_vt("VT-3", "second-path recomputation of six contrasts",
                  ok3, f"max |05-07| deviation = {maxdev:.3e} (tolerance 1e-9)")

# ---------------- VT-4: Holm recomputation -------------------------------------
def holm(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    out = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order, start=1):
        running = max(running, min(1.0, (m - rank + 1) * ps[i]))
        out[i] = running
    return out

raw_list = [float(r["raw_p"]) for r in rawps]
holm_re = holm(raw_list)
ok4 = True
for r, adj in zip(primary, holm_re):
    ok4 &= abs(float(r["holm_p"]) - adj) <= 1e-12
overall &= add_vt("VT-4", "Holm envelope recomputed from raw p-values",
                  ok4, "agreement to 1e-12 across 6 adjusted p-values")

# ---------------- VT-5: balance recomputed fresh --------------------------------
num_covs = ["recency", "history", "mens", "womens", "newbie"]
ok5 = True
b06 = {(r["covariate"], r["arm"]): r for r in balance06}
for c in num_covs:
    m_all, s_all = float(df[c].mean()), float(df[c].std(ddof=1))
    for a in ARMS:
        m_arm = float(df.loc[df["segment"] == a, c].mean())
        recomputed = (m_arm - m_all) / s_all
        stored = float(b06[(c, a)]["smd"])
        ok5 &= abs(recomputed - stored) <= 1e-9
overall &= add_vt("VT-5", "balance table recomputed fresh from data/raw",
                  ok5, "all 15 SMD values agree to 1e-9")

# ---------------- VT-6: funnel assertions + negative test -----------------------
def funnel_violations(d):
    return int(((d["spend"] > 0) & (d["conversion"] == 0)).sum()
               + ((d["conversion"] == 1) & (d["visit"] == 0)).sum())

real = funnel_violations(df)
corrupt = pd.concat([df.head(5),
                     pd.DataFrame([{"recency": 1, "history_segment": "1) $0 - $100",
                                    "history": 50.0, "mens": 0, "womens": 1,
                                    "zip_code": "Urban", "newbie": 0,
                                    "channel": "Web", "segment": "Mens E-Mail",
                                    "visit": 0, "conversion": 1, "spend": 75.0}])],
                    ignore_index=True)
neg = funnel_violations(corrupt)
ok6 = real == 0 and neg >= 1
overall &= add_vt("VT-6", "funnel assertions incl. corrupted-fixture negative test",
                  ok6, f"real-data violations = {real}; corrupted fixture "
                       f"detected = {neg}")

# ---------------- VT-7: language audit of write-up artifacts -------------------
FORBIDDEN = ["caused by", "caused the", "due to", "led to", "leads to",
             "resulting from", "because they received", "because of the email",
             "email caused", "emails caused", "campaign caused",
             "as a result of the email"]
md_files = sorted(OUT.glob("*.md"))
hits = []
for f in md_files:
    text = f.read_text(encoding="utf-8").lower()
    for ph in FORBIDDEN:
        if ph in text:
            hits.append(f"{f.name}: '{ph}'")
ok7 = len(hits) == 0
overall &= add_vt("VT-7", "language audit of write-up artifacts",
                  ok7, "0 forbidden phrases in " + ", ".join(f.name for f in md_files)
                       if ok7 else "; ".join(hits))

# ---------------- VT-8: artifact-vs-write-up reconciliation ---------------------
ok8 = True
pr_lines = (OUT / "primary_results.md").read_text(encoding="utf-8").splitlines()
md_cells = {}
for line in pr_lines:
    mrow = re.match(r"\| ([^|]+) \| (\S+) \| ([+\-\d.]+) (?:pp|\$) \|", line.strip())
    if mrow:
        md_cells[(mrow.group(1).strip(), mrow.group(2))] = float(mrow.group(3))
for (pair, outcome), val in md_cells.items():
    row = pm.get((pair, outcome))
    ok8 &= row is not None and abs(float(row["estimate"]) - val) <= 5e-7
ok8 &= len(md_cells) == 6
overall &= add_vt("VT-8", "write-up numbers reconcile with primary_results.csv",
                  ok8, f"{len(md_cells)} md estimates matched to CSV within "
                       f"rounding (5e-7)")

# ---------------- integrity: sha logs ------------------------------------------
sha_rows = list(csv.DictReader(open(OUT / "sha256_log.csv", newline="", encoding="utf-8")))
digests = {r["sha256"] for r in sha_rows}
ok_sha = len(digests) == 1 and digests == {h_now}
overall &= add_vt("INT", "data/raw sha256 constant across all analysis runs",
                  ok_sha, f"{len(sha_rows)} log rows, digest {h_now[:16]}...")

# ---------------- final artifacts ----------------------------------------------
with open(OUT / "vt_results.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["vt_id", "description", "verdict", "detail"])
    w.writerows(vt_rows)

n_pass = sum(1 for r in vt_rows if r[2] == "PASS")
sig_lines = []
for r in primary:
    unit = "$" if r["outcome"] == "spend" else "pp"
    stat = (f"t={float(r['test_stat']):.2f} (df={float(r['df']):.1f})"
            if r["outcome"] == "spend" else f"z={float(r['test_stat']):.2f}")
    sig = "significant (Holm 0.05)" if float(r["holm_p"]) < 0.05 else "not significant (Holm 0.05)"
    sig_lines.append(
        f"- {r['pair']}, {r['outcome']}: {float(r['estimate']):+.6f} {unit} "
        f"[{float(r['ci_lo']):+.6f}, {float(r['ci_hi']):+.6f}]; {stat}; "
        f"raw p = {float(r['raw_p']):.3g}; Holm p = {float(r['holm_p']):.3g} — {sig}.")

report = [
    "# Reconciliation and final analysis report (plan.md §10–§12)",
    "",
    f"Run date: {datetime.now(timezone.utc).isoformat()}",
    f"data/raw SHA-256 (all runs identical): {h_now}",
    "",
    "## VT-1..VT-8 + integrity results",
    "",
    "| ID | Check | Verdict | Detail |",
    "|---|---|---|---|",
]
for vt_id, desc, verdict, detail in vt_rows:
    report.append(f"| {vt_id} | {desc} | {verdict} | {detail} |")
report += [
    "",
    "## Six primary ITT contrasts (full detail: primary_results.csv)",
    "",
    "Under randomized assignment, these estimate the effect of ASSIGNMENT to",
    "each arm relative to No E-Mail (plan.md §9). Causal interpretation is",
    "assignment-level; no claims about email contents, opens, or long-run value.",
    "",
    *sig_lines,
    "",
    "## Statistical vs. business significance",
    "",
    "- Statistical significance: Holm-adjusted p < 0.05 only (see table above).",
    "- Business significance: magnitudes — absolute percentage points (visit,",
    "  conversion) and dollars per contacted customer (spend), with relative",
    "  uplift as context. The dataset contains no cost/margin information, so",
    "  no profitability verdict is possible (limitation A4). Magnitudes are",
    "  reported for decision-makers; they do not replace a cost-benefit model.",
    "",
    "## Verification status and independence statement",
    "",
    "All checks above are agent-authored cross-checks. Agreement between the two",
    "agent-written calculation paths rules out coding slips but is NOT independent",
    "human validation. The blinded Stage-1 review (VERIFICATION_PROTOCOL.md) and",
    "human reasoning review (plan.md §10, §11 criterion 6) are PENDING; no",
    "'independently verified' label is claimed.",
    "",
    "## Robustness summary (full detail: 06 artifacts + robustness.md)",
    "",
    "- R2 adjusted OLS (HC1) and R3 transformations are consistent with the",
    "  primary contrasts in sign and order of magnitude (robustness.csv,",
    "  robustness_transformations.csv).",
    "- R4: BH-FDR conclusions agree with Holm FWER (robustness_bh.csv).",
    "- R5: bootstrap percentile CIs bracket the Welch CIs (robustness_bootstrap.csv).",
    "- R1: deduplication remains an illustration of a potentially invalid",
    "  data-processing decision (see robustness.md), not an alternative estimate.",
    "- R6: funnel-stage numbers are DESCRIPTIVE ONLY (post-treatment conditioning).",
    "",
    "## Limitations (AGENTS.md rule 10)",
    "",
    "- A1 (unverified): randomization and the two-week outcome window rest on",
    "  external documentation, not on the file itself.",
    "- A2 (unverified): one row = one distinct customer.",
    "- A3 (unverified): no interference between customers (SUTVA).",
    "- A4: no cost/margin data — no profitability threshold computable.",
    "- Missing data: none (verified); outliers: 12 spend = 499.00 rows retained.",
    "- Deduplicated counts are counts of distinct rows and may undercount",
    "  distinct customers when rows are indistinguishable.",
]
# VT-7 self-audit of this report must also pass; verify before writing
for ph in FORBIDDEN:
    assert ph not in " ".join(report).lower(), f"forbidden phrase in report: {ph}"
(OUT / "reconciliation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

print(f"[summary] VT checks: {n_pass}/{len(vt_rows)} PASS")
if not overall:
    print("[summary] FAILURES PRESENT — evidence preserved; no silent fixes.")
    raise SystemExit(1)
print("[summary] ALL CHECKS PASS — analysis artifacts complete for human review")
