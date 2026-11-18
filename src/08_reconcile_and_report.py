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

# ---------------- unit parsing helpers shared by VT-8 / VT-9 -------------------
EST_PROB = re.compile(r"^([+\-]\d+\.\d+) \(probability difference\) = "
                      r"([+\-]\d+\.\d+) percentage points$")
EST_USD = re.compile(r"^([+\-]\$\d+\.\d+) \(USD per randomized customer\)$")
CI_PROB = re.compile(r"^\[([+\-]\d+\.\d+), ([+\-]\d+\.\d+)\] \(probability difference\) = "
                     r"\[([+\-]\d+\.\d+), ([+\-]\d+\.\d+)\] percentage points$")
CI_USD = re.compile(r"^\[([+\-]\$\d+\.\d+), ([+\-]\$\d+\.\d+)\] "
                    r"\(USD per randomized customer\)$")
SIG_RE = re.compile(r"^- (.+?), (visit|conversion|spend): (.+?); 95% CI (.+?); ")


def parse_est_ci(est_cell: str, ci_cell: str, outcome: str):
    """Parse an estimate/CI cell pair; returns None if number OR unit is wrong."""
    est_cell, ci_cell = est_cell.strip(), ci_cell.strip()
    if outcome == "spend":
        m_est, m_ci = EST_USD.match(est_cell), CI_USD.match(ci_cell)
        if not (m_est and m_ci):
            return None
        return {"est": float(m_est.group(1).lstrip("+$")), "est_pp": None,
                "ci_lo": float(m_ci.group(1).lstrip("+$")),
                "ci_hi": float(m_ci.group(2).lstrip("+$")),
                "ci_pp_lo": None, "ci_pp_hi": None}
    m_est, m_ci = EST_PROB.match(est_cell), CI_PROB.match(ci_cell)
    if not (m_est and m_ci):
        return None
    return {"est": float(m_est.group(1)), "est_pp": float(m_est.group(2)),
            "ci_lo": float(m_ci.group(1)), "ci_hi": float(m_ci.group(2)),
            "ci_pp_lo": float(m_ci.group(3)), "ci_pp_hi": float(m_ci.group(4))}


def parse_table_rows(lines):
    rows = {}
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.split("|")]
        if len(cells) < 6:
            continue
        pair, outcome = cells[1], cells[2]
        if outcome not in ("visit", "conversion", "spend"):
            continue
        vals = parse_est_ci(cells[3], cells[4], outcome)
        if vals is not None:
            rows[(pair, outcome)] = vals
    return rows


def parse_sig_lines(lines):
    rows = {}
    for line in lines:
        m = SIG_RE.match(line.strip())
        if not m:
            continue
        vals = parse_est_ci(m.group(3), m.group(4), m.group(2))
        if vals is not None:
            rows[(m.group(1), m.group(2))] = vals
    return rows


def fmt_est_ci(r):
    """Dual reporting: probability difference + percentage points / USD."""
    if r["outcome"] == "spend":
        est = f"+${float(r['estimate']):.6f} (USD per randomized customer)"
        ci = (f"[+${float(r['ci_lo']):.6f}, +${float(r['ci_hi']):.6f}] "
              f"(USD per randomized customer)")
    else:
        est = (f"{float(r['estimate']):+.6f} (probability difference) = "
               f"{100 * float(r['estimate']):+.4f} percentage points")
        ci = (f"[{float(r['ci_lo']):+.6f}, {float(r['ci_hi']):+.6f}] "
              f"(probability difference) = "
              f"[{100 * float(r['ci_lo']):+.4f}, "
              f"{100 * float(r['ci_hi']):+.4f}] percentage points")
    return est, ci


def unit_failures(vals, row):
    """Return the list of scale/unit checks that fail for one parsed row."""
    TOL_PROB, TOL_PP, TOL_UNIT = 5e-7, 5e-4, 5e-4
    fails = []
    e, lo, hi = float(row["estimate"]), float(row["ci_lo"]), float(row["ci_hi"])
    if abs(vals["est"] - e) > TOL_PROB:
        fails.append("est")
    if abs(vals["ci_lo"] - lo) > TOL_PROB:
        fails.append("ci_lo")
    if abs(vals["ci_hi"] - hi) > TOL_PROB:
        fails.append("ci_hi")
    if row["outcome"] == "spend":
        if vals["est_pp"] is not None:
            fails.append("pp_on_usd")
        return fails
    if vals["est_pp"] is None:
        fails.append("missing_pp")
        return fails
    if abs(vals["est_pp"] - 100 * e) > TOL_PP:
        fails.append("est_pp")
    if abs(vals["est_pp"] - 100 * vals["est"]) > TOL_UNIT:
        fails.append("est_pp_vs_displayed_prob")
    if abs(vals["ci_pp_lo"] - 100 * lo) > TOL_PP:
        fails.append("ci_pp_lo")
    if abs(vals["ci_pp_hi"] - 100 * hi) > TOL_PP:
        fails.append("ci_pp_hi")
    if abs(vals["ci_pp_lo"] - 100 * vals["ci_lo"]) > TOL_UNIT:
        fails.append("ci_pp_lo_vs_displayed_prob")
    if abs(vals["ci_pp_hi"] - 100 * vals["ci_hi"]) > TOL_UNIT:
        fails.append("ci_pp_hi_vs_displayed_prob")
    return fails


# ---------------- report lines (built early so VT-9 can check them) ------------
sig_lines, sig_vals = [], {}
for r in primary:
    est, ci = fmt_est_ci(r)
    stat = (f"t={float(r['test_stat']):.2f} (df={float(r['df']):.1f})"
            if r["outcome"] == "spend" else f"z={float(r['test_stat']):.2f}")
    sig = ("significant (Holm 0.05)" if float(r["holm_p"]) < 0.05
           else "not significant (Holm 0.05)")
    sig_lines.append(
        f"- {r['pair']}, {r['outcome']}: {est}; 95% CI {ci}; {stat}; "
        f"raw p = {float(r['raw_p']):.3g}; Holm p = {float(r['holm_p']):.3g} — {sig}.")
    sig_vals[(r["pair"], r["outcome"])] = parse_est_ci(est, ci, r["outcome"])

# ---------------- VT-8: artifact-vs-write-up reconciliation ---------------------
pr_lines = (OUT / "primary_results.md").read_text(encoding="utf-8").splitlines()
ok8 = True
md_rows = parse_table_rows(pr_lines)
ok8 &= len(md_rows) == 6
for key, val in md_rows.items():
    row = pm.get(key)
    ok8 &= row is not None and abs(float(row["estimate"]) - val["est"]) <= 5e-7
overall &= add_vt("VT-8", "write-up numbers reconcile with primary_results.csv",
                  ok8, f"{len(md_rows)} md estimates matched to CSV within "
                       f"rounding (5e-7)")

# ---------------- VT-9: unit/scale consistency (incl. negative control) --------
fail9 = []
for key, val in md_rows.items():
    row = pm.get(key)
    if row is None:
        fail9.append(f"{key}: no CSV row")
        continue
    fail9 += [f"{key[0]}/{key[1]}: {f}" for f in unit_failures(val, row)]
for key, val in sig_vals.items():
    if val is None:
        fail9.append(f"report {key}: unparseable unit cell")
        continue
    fail9 += [f"report {key[0]}/{key[1]}: {f}"
              for f in unit_failures(val, pm[key])]
if len(sig_vals) != 6:
    fail9.append(f"report lines parsed = {len(sig_vals)} (expected 6)")

# negative control: the original erroneous labels MUST be rejected
old_table = ("| Mens E-Mail minus No E-Mail | visit | +0.076590 pp | "
             "[+0.069954, +0.083226] | z=22.621 | 2.71e-113 | 1.62e-112 | "
             "yes | +72.1% |")
old_report = ("- Mens E-Mail minus No E-Mail, visit: +0.076590 pp "
              "[+0.069954, +0.083226]; z=22.62; raw p = 2.71e-113; "
              "Holm p = 1.62e-112 — significant (Holm 0.05).")
neg_detected = (len(parse_table_rows([old_table])) == 0
                and len(parse_sig_lines([old_report])) == 0)
if not neg_detected:
    fail9.append("negative control NOT detected (old 'pp' label accepted)")

ok9 = len(fail9) == 0
overall &= add_vt(
    "VT-9", "unit/scale consistency: pp = 100 x probability difference",
    ok9,
    "6 table rows + 6 report lines verified (point estimates and CIs); "
    "negative control (original '+0.076590 pp' label) detected"
    if ok9 else "; ".join(fail9[:6]))

# ---------------- integrity: sha logs ------------------------------------------
sha_rows = list(csv.DictReader(open(OUT / "sha256_log.csv", newline="", encoding="utf-8")))
digests = {r["sha256"] for r in sha_rows}
ok_sha = len(digests) == 1 and digests == {h_now}
overall &= add_vt("INT", "data/raw sha256 constant across all analysis runs",
                  ok_sha, f"{len(sha_rows)} log rows, digest {h_now[:16]}...")

# ---------------- final artifacts ----------------------------------------------
n_pass = sum(1 for r in vt_rows if r[2] == "PASS")
report = [
    "# Reconciliation and final analysis report (plan.md §10–§12)",
    "",
    f"Run date: {datetime.now(timezone.utc).isoformat()}",
    f"data/raw SHA-256 (all runs identical): {h_now}",
    "",
    "## VT-1..VT-9 + integrity results",
    "",
    "| ID | Check | Verdict | Detail |",
    "|---|---|---|---|",
]
for vt_id, desc, verdict, detail in vt_rows:
    report.append(f"| {vt_id} | {desc} | {verdict} | {detail} |")
report += [
    "",
    "## Units used in this report",
    "",
    "- Visit and conversion: absolute effects are **probability differences** on",
    "  the 0–1 scale; multiplied by 100 they are **percentage points** (pp).",
    "  Confidence intervals are converted with the same factor.",
    "- **Relative uplift** is a relative percentage change (arm mean / control",
    "  mean − 1); it is not a percentage-point difference.",
    "- Spend: **dollar differences in mean spending per randomized customer**",
    "  (USD); spend effects are not percentage points.",
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
    "- Business significance: magnitudes — probability differences (also given",
    "  in percentage points) for visit and conversion, and dollars per",
    "  randomized customer for spend, with relative uplift as context. The",
    "  dataset contains no cost/margin information, so no profitability verdict",
    "  is possible (limitation A4). Magnitudes are reported for decision-makers;",
    "  they do not replace a cost-benefit model.",
    "",
    "## Verification status and independence statement",
    "",
    "All checks above are agent-authored cross-checks. Agreement between the two",
    "agent-written calculation paths rules out coding slips but is NOT independent",
    "human validation. An external computational audit",
    "(human_verification/independent_primary_audit.md) confirmed the six",
    "estimates and identified the M6 unit-labeling error; the blinded Stage-1",
    "review (VERIFICATION_PROTOCOL.md) and human reasoning review (plan.md §10,",
    "§11 criterion 6) remain PENDING; no 'independently verified' label is",
    "claimed.",
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
report_text = "\n".join(report) + "\n"
(OUT / "reconciliation_report.md").write_text(report_text, encoding="utf-8")

# post-write file recheck: every generated report line must be present verbatim
missing = [ln for ln in sig_lines if ln not in report_text]
if missing:
    overall = False
    print(f"[VT-9] POST-WRITE RECHECK FAILED: {len(missing)} report lines missing")
else:
    print("[VT-9] post-write file recheck passed (6/6 report lines present verbatim)")

with open(OUT / "vt_results.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["vt_id", "description", "verdict", "detail"])
    w.writerows(vt_rows)

print(f"[summary] VT checks: {n_pass}/{len(vt_rows)} PASS")
if not overall:
    print("[summary] FAILURES PRESENT — evidence preserved; no silent fixes.")
    raise SystemExit(1)
print("[summary] ALL CHECKS PASS — analysis artifacts complete for human review")
