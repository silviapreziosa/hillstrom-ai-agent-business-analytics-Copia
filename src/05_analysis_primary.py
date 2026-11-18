#!/usr/bin/env python3
"""
src/05_analysis_primary.py — Primary ITT analysis (plan.md v1.1 §4–§5).

Six confirmatory contrasts (2 arms x 3 outcomes) on the FULL randomized
sample of 64,000 rows. Methods exactly per plan.md:
  proportions: d = p1 - p0; SE = sqrt(p1(1-p1)/n1 + p0(1-p0)/n0);
               z = d/SE; p = 2(1-Phi(|z|)); CI = d +- 1.959963984540054*SE
  spend:       Welch t with Satterthwaite df; CI via t_{0.975,df}
  Holm step-down envelope across the 6 raw p-values.
No rows are dropped or filtered (VT-1); relative uplift is a secondary
description. Statistical vs business significance is distinguished in the
write-up. Causal claims restricted to assignment-level ITT (plan.md §9).
Writes: results/analysis/{primary_results.csv,raw_pvalues.csv,
pipeline_log.csv,sha256_log.csv,primary_results.md,model_log.md}.
"""
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
ARMS = (MEN, NOE, WOM)
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
        fh.write(f"{datetime.now(timezone.utc).isoformat()},05,{stage},{digest}\n")


def log_pipeline(event: str, rows: str) -> None:
    p = OUT / "pipeline_log.csv"
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp,script,event,rows\n")
        fh.write(f"{datetime.now(timezone.utc).isoformat()},05,{event},\"{rows}\"\n")


h_before = sha256_file(RAW)
log_sha("before", h_before)

df = pd.read_csv(RAW)
total = len(df)
assert total == 64000, f"unexpected row count {total}"
print(f"[rule 2] load: {total} rows (data/raw untouched; no filters applied)")
log_pipeline("load", f"{total}")
arm_sizes = {a: int((df["segment"] == a).sum()) for a in ARMS}
print(f"[rule 2] split by segment (no rows dropped): "
      f"{arm_sizes[MEN]}/{arm_sizes[NOE]}/{arm_sizes[WOM]} "
      f"(sum {sum(arm_sizes.values())} = {total})")
log_pipeline("split_segment_no_drop", f"{arm_sizes[MEN]},{arm_sizes[NOE]},{arm_sizes[WOM]};sum={total}")
log_pipeline("no_filters_no_drops", f"{total}")
assert sum(arm_sizes.values()) == total

# per-arm summary statistics
S = {}
for a in ARMS:
    sub = df.loc[df["segment"] == a]
    S[a] = {
        "n": len(sub),
        "p_visit": float(sub["visit"].mean()),
        "p_conversion": float(sub["conversion"].mean()),
        "mean_spend": float(sub["spend"].mean()),
        "n_visit": int(sub["visit"].sum()),
        "n_conv": int(sub["conversion"].sum()),
        "mean_spend_conv": float(sub.loc[sub["conversion"] == 1, "spend"].mean()),
    }

# Holm across the 6 family p-values
def holm_adjust(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj_sorted, running = [], 0.0
    for rank, i in enumerate(order, start=1):
        val = min(1.0, (m - rank + 1) * ps[i])
        running = max(running, val)
        adj_sorted.append(running)
    out = [0.0] * m
    for pos, i in enumerate(order):
        out[i] = adj_sorted[pos]
    return out


results = []
for t_arm, c_arm in PAIRS:
    for outcome in ("visit", "conversion", "spend"):
        n1, n0 = S[t_arm]["n"], S[c_arm]["n"]
        if outcome == "spend":
            x1 = df.loc[df["segment"] == t_arm, "spend"].to_numpy()
            x0 = df.loc[df["segment"] == c_arm, "spend"].to_numpy()
            m1, m0 = float(x1.mean()), float(x0.mean())
            v1, v0 = float(x1.var(ddof=1)), float(x0.var(ddof=1))
            se = float(np.sqrt(v1 / n1 + v0 / n0))
            d = m1 - m0
            t = d / se
            nu = (v1 / n1 + v0 / n0) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v0 / n0) ** 2 / (n0 - 1))
            p = float(2 * stats.t.sf(abs(t), nu))
            crit = float(stats.t.ppf(0.975, nu))
            lo, hi = d - crit * se, d + crit * se
            uplift = m1 / m0 - 1.0
            results.append(dict(pair=f"{t_arm} minus {c_arm}", outcome="spend",
                                estimate=d, se=se, test_stat=t, df=nu,
                                ci_lo=lo, ci_hi=hi, raw_p=p,
                                relative_uplift=uplift))
        else:
            col = "visit" if outcome == "visit" else "conversion"
            p1 = S[t_arm][f"p_{col}"]
            p0 = S[c_arm][f"p_{col}"]
            d = p1 - p0
            se = float(np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0))
            z = d / se
            p = float(2 * stats.norm.sf(abs(z)))
            lo, hi = d - Z975 * se, d + Z975 * se
            uplift = p1 / p0 - 1.0
            results.append(dict(pair=f"{t_arm} minus {c_arm}", outcome=col,
                                estimate=d, se=se, test_stat=z, df=float("nan"),
                                ci_lo=lo, ci_hi=hi, raw_p=p,
                                relative_uplift=uplift))

holm = holm_adjust([r["raw_p"] for r in results])
for r, h in zip(results, holm):
    r["holm_p"] = h

with open(OUT / "primary_results.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pair", "outcome", "estimate", "se",
                                       "test_stat", "df", "ci_lo", "ci_hi",
                                       "raw_p", "holm_p", "relative_uplift"])
    w.writeheader()
    w.writerows(results)

with open(OUT / "raw_pvalues.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["pair", "outcome", "raw_p"])
    for r in results:
        w.writerow([r["pair"], r["outcome"], repr(r["raw_p"])])

# write-up (numbers copied from primary_results.csv; VT-8 reconciles)
lines = [
    "# Primary ITT analysis (plan.md §4–§5)",
    "",
    "Source: results/analysis/primary_results.csv — produced by src/05_analysis_primary.py.",
    "Sample: all 64,000 randomized rows (21,307 / 21,306 / 21,387). No rows dropped.",
    "Causal scope: effects of ASSIGNMENT under randomized assignment (plan.md §9).",
    "",
    "## Units (read before quoting numbers)",
    "",
    "- Visit and conversion effects are **probability differences** on the 0–1 scale; the",
    "  same quantity multiplied by 100 is given in **percentage points** (pp). These are",
    "  absolute risk differences, not relative changes.",
    "- Relative uplift is a **relative percentage** change (arm mean / control mean − 1);",
    "  it is a different quantity from percentage points and from probability differences.",
    "- Spend effects are **dollar differences in mean spending per randomized customer**",
    "  (USD), not percentage points.",
    "",
    "| Contrast | Outcome | Estimate | 95% CI | z/t (df) | raw p | Holm p | Sig (Holm 0.05) | Relative uplift (relative %) |",
    "|---|---|---|---|---|---|---|---|---|",
]
for r in results:
    stat = (f"t={r['test_stat']:.3f} (df={r['df']:.1f})" if r["outcome"] == "spend"
            else f"z={r['test_stat']:.3f}")
    sig = "yes" if r["holm_p"] < 0.05 else "no"
    if r["outcome"] == "spend":
        est = f"+${r['estimate']:.6f} (USD per randomized customer)"
        ci = (f"[+${r['ci_lo']:.6f}, +${r['ci_hi']:.6f}] "
              f"(USD per randomized customer)")
    else:
        est = (f"{r['estimate']:+.6f} (probability difference) = "
               f"{100 * r['estimate']:+.4f} percentage points")
        ci = (f"[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}] (probability difference) = "
              f"[{100 * r['ci_lo']:+.4f}, {100 * r['ci_hi']:+.4f}] percentage points")
    lines.append(
        f"| {r['pair']} | {r['outcome']} | {est} | "
        f"{ci} | {stat} | {r['raw_p']:.3g} | "
        f"{r['holm_p']:.3g} | {sig} | {100 * r['relative_uplift']:+.1f}% |")
lines += [
    "",
    "## Statistical vs. business significance",
    "",
    "- Statistical significance is decided ONLY by Holm-adjusted p < 0.05 (column above).",
    "- Business significance is about magnitude: absolute effects are in percentage points",
    "  (visit/conversion) or dollars per customer (spend), with relative uplift as context.",
    "- The data contain no cost, margin, or campaign-cost information, so a formal",
    "  profitability threshold cannot be computed from this dataset; magnitudes are",
    "  reported, not a profit verdict (assumption A4, recorded in the write-up).",
    "",
    "## Verification status",
    "",
    "Cross-checked by src/07 (agent-authored second path; agreement is a coding-slip",
    "check, NOT independent human validation). Human blinded review per",
    "VERIFICATION_PROTOCOL.md is pending; no 'independently verified' label is claimed.",
]
(OUT / "primary_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

(OUT / "model_log.md").write_text(
    "# Model calls log (AGENTS.md rule 5)\n\n"
    "- src/05_analysis_primary.py: NO statistical models fitted. Closed-form\n"
    "  two-sample z-tests (proportions) and Welch t-test (spend) per plan.md §5.\n"
    "  Library calls: scipy.stats.norm.sf, scipy.stats.t.sf, scipy.stats.t.ppf.\n"
    "  Inputs: data/raw/hillstorm_no_indices.csv (read-only), all 64,000 rows.\n"
    "  No randomness used; no seed required.\n",
    encoding="utf-8")

h_after = sha256_file(RAW)
log_sha("after", h_after)
assert h_before == h_after, "data/raw changed during run!"
print(f"[integrity] data/raw SHA-256 unchanged: {h_after}")
print(f"[done] six primary contrasts computed; wrote primary_results.csv, "
      f"raw_pvalues.csv, primary_results.md")
