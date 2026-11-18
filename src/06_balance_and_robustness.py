#!/usr/bin/env python3
"""
src/06_balance_and_robustness.py — Balance + robustness (plan.md §7–§8).

Balance: SMD = (mean_arm - mean_all)/s_all (ddof=1) for the five numeric
covariates, plus covariate-share tables for zip_code/channel. Non-gating.
Robustness, all keeping all 64,000 rows:
  R2 covariate-adjusted OLS (HC1) — approximate re-expression of ITT contrasts
  R3 outcome-transformation sensitivity: log1p(spend) Welch diff + exact
     two-part decomposition (zero customer deletion; no post-treatment selection)
  R4 Benjamini-Hochberg FDR beside the Holm FWER
  R5 bootstrap 95% CI for the spend contrast (10,000 resamples, seed 42,
     arm-stratified)
  R6 funnel-stage descriptives — DESCRIPTIVE ONLY (post-treatment conditioning)
R1 (deduplication illustration) is cited from the committed verification
artifacts, not recomputed here.
Writes: results/analysis/{balance.csv,balance_shares.csv,robustness.csv,
funnel_descriptive.csv,model_log.md,sha256_log.csv,pipeline_log.csv,robustness.md}.
"""
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
ARMS = (MEN, NOE, WOM)
PAIRS = [(MEN, NOE), (WOM, NOE)]


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
        fh.write(f"{datetime.now(timezone.utc).isoformat()},06,{stage},{digest}\n")


def log_pipeline(event: str, rows: str) -> None:
    p = OUT / "pipeline_log.csv"
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp,script,event,rows\n")
        fh.write(f"{datetime.now(timezone.utc).isoformat()},06,{event},\"{rows}\"\n")


def upsert_model_log(title: str, body: str) -> None:
    """Idempotent model_log.md update: replace only this script's section.

    Rerunning any single script must not destroy or duplicate sections
    produced by another script (mistakes.md M7)."""
    path = OUT / "model_log.md"
    header = "# Model calls log (AGENTS.md rule 5)"
    sections: dict[str, str] = {}
    if path.exists():
        for part in path.read_text(encoding="utf-8").split("\n## ")[1:]:
            name, _, rest = part.partition("\n")
            sections[name.strip()] = rest.strip("\n")
    sections[title] = body.strip("\n")
    text = header + "\n\n" + "\n\n".join(
        f"## {name}\n{content}" for name, content in sorted(sections.items()))
    path.write_text(text + "\n", encoding="utf-8")


h_before = sha256_file(RAW)
log_sha("before", h_before)

df = pd.read_csv(RAW)
total = len(df)
assert total == 64000
print(f"[rule 2] load: {total} rows (no filters applied)")
log_pipeline("load", f"{total}")
log_pipeline("no_filters_no_drops_all_robustness", f"{total}")

# ---- Balance (SMD, non-gating) ----------------------------------------------
num_covs = ["recency", "history", "mens", "womens", "newbie"]
all_mean = {c: float(df[c].mean()) for c in num_covs}
all_sd = {c: float(df[c].std(ddof=1)) for c in num_covs}
bal_rows = []
for c in num_covs:
    for a in ARMS:
        m = float(df.loc[df["segment"] == a, c].mean())
        bal_rows.append({"covariate": c, "arm": a, "mean_arm": m,
                         "mean_all": all_mean[c], "sd_all": all_sd[c],
                         "smd": (m - all_mean[c]) / all_sd[c]})
with open(OUT / "balance.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["covariate", "arm", "mean_arm",
                                       "mean_all", "sd_all", "smd"])
    w.writeheader()
    w.writerows(bal_rows)
max_smd = max(abs(r["smd"]) for r in bal_rows)
print(f"[balance] max |SMD| = {max_smd:.4f} (non-gating; read as no evidence "
      f"against randomization if < 0.1)")

share_rows = []
for c in ("zip_code", "channel"):
    tab = pd.crosstab(df["segment"], df[c], normalize="index")
    for a in ARMS:
        for lvl in tab.columns:
            share_rows.append({"covariate": c, "level": lvl, "arm": a,
                               "share": float(tab.loc[a, lvl])})
with open(OUT / "balance_shares.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["covariate", "level", "arm", "share"])
    w.writeheader()
    w.writerows(share_rows)

# ---- R2: covariate-adjusted OLS (HC1) ----------------------------------------
X = pd.concat([
    pd.DataFrame({"treat_mens": (df["segment"] == MEN).astype(float).to_numpy(),
                  "treat_womens": (df["segment"] == WOM).astype(float).to_numpy(),
                  "recency": df["recency"].astype(float).to_numpy(),
                  "history": df["history"].astype(float).to_numpy(),
                  "mens": df["mens"].astype(float).to_numpy(),
                  "womens": df["womens"].astype(float).to_numpy(),
                  "newbie": df["newbie"].astype(float).to_numpy()}),
    pd.get_dummies(df["zip_code"], prefix="zip", drop_first=True, dtype=float),
    pd.get_dummies(df["channel"], prefix="chan", drop_first=True, dtype=float),
], axis=1)
X = sm.add_constant(X)
model_rows = []
for outcome in ("visit", "conversion", "spend"):
    fit = sm.OLS(df[outcome].astype(float).to_numpy(), X).fit(cov_type="HC1")
    for tname in ("treat_mens", "treat_womens"):
        model_rows.append({"model": f"OLS {outcome} (HC1)", "term": tname,
                           "estimate": float(fit.params[tname]),
                           "se_hc1": float(fit.bse[tname]),
                           "ci_lo": float(fit.conf_int().loc[tname, 0]),
                           "ci_hi": float(fit.conf_int().loc[tname, 1]),
                           "p_value": float(fit.pvalues[tname])})
with open(OUT / "robustness.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["model", "term", "estimate", "se_hc1",
                                       "ci_lo", "ci_hi", "p_value"])
    w.writeheader()
    w.writerows(model_rows)

# ---- R3: outcome transformations (zero deletion) ------------------------------
r3_rows = []
for t_arm, c_arm in PAIRS:
    x1 = df.loc[df["segment"] == t_arm, "spend"]
    x0 = df.loc[df["segment"] == c_arm, "spend"]
    l1, l0 = np.log1p(x1.to_numpy()), np.log1p(x0.to_numpy())
    d_log = float(l1.mean() - l0.mean())
    se_log = float(np.sqrt(l1.var(ddof=1) / len(l1) + l0.var(ddof=1) / len(l0)))
    t_log = d_log / se_log
    nu = (l1.var(ddof=1) / len(l1) + l0.var(ddof=1) / len(l0)) ** 2 / (
        (l1.var(ddof=1) / len(l1)) ** 2 / (len(l1) - 1)
        + (l0.var(ddof=1) / len(l0)) ** 2 / (len(l0) - 1))
    p_log = float(2 * stats.t.sf(abs(t_log), nu))
    # exact two-part decomposition: total = p1*m1 - p0*m0 (identity)
    c1 = df.loc[(df["segment"] == t_arm) & (df["conversion"] == 1), "spend"]
    c0 = df.loc[(df["segment"] == c_arm) & (df["conversion"] == 1), "spend"]
    p1 = df.loc[df["segment"] == t_arm, "conversion"].mean()
    p0 = df.loc[df["segment"] == c_arm, "conversion"].mean()
    m1, m0 = float(c1.mean()), float(c0.mean())
    total_diff = p1 * m1 - p0 * m0
    term1 = (p1 - p0) * (m1 + m0) / 2.0
    term2 = ((p1 + p0) / 2.0) * (m1 - m0)
    assert abs(term1 + term2 - total_diff) < 1e-9, "two-part decomposition failed"
    r3_rows += [
        {"pair": f"{t_arm} minus {c_arm}", "analysis": "R3a log1p(spend) Welch diff",
         "estimate": d_log, "se": se_log, "df": nu, "p_value": p_log},
        {"pair": f"{t_arm} minus {c_arm}",
         "analysis": "R3b two-part: term1 Δconv × avg converter spend",
         "estimate": term1, "se": float("nan"), "df": float("nan"), "p_value": float("nan")},
        {"pair": f"{t_arm} minus {c_arm}",
         "analysis": "R3b two-part: term2 avg conv rate × Δ converter spend",
         "estimate": term2, "se": float("nan"), "df": float("nan"), "p_value": float("nan")},
        {"pair": f"{t_arm} minus {c_arm}",
         "analysis": "R3b two-part: total (identity check)",
         "estimate": total_diff, "se": float("nan"), "df": float("nan"),
         "p_value": float("nan")},
    ]
with open(OUT / "robustness_transformations.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pair", "analysis", "estimate", "se",
                                       "df", "p_value"])
    w.writeheader()
    w.writerows(r3_rows)

# ---- R4: Benjamini-Hochberg over the six primary p-values ---------------------
with open(OUT / "raw_pvalues.csv", newline="", encoding="utf-8") as fh:
    raw = [(r["pair"], r["outcome"], float(r["raw_p"])) for r in csv.DictReader(fh)]
m = len(raw)
order = sorted(range(m), key=lambda i: raw[i][2])
bh_adj, running = [0.0] * m, 1.0
for rank in range(m, 0, -1):
    i = order[rank - 1]
    running = min(running, min(1.0, m * raw[i][2] / rank))
    bh_adj[i] = running
bh_reject = sorted(rank for rank in range(1, m + 1)
                   if raw[order[rank - 1]][2] <= rank / m * 0.05)
bh_rows = []
for i, (pair, outcome, p) in enumerate(raw):
    bh_rows.append({"pair": pair, "outcome": outcome, "raw_p": p,
                    "bh_adjusted": bh_adj[i],
                    "bh_reject_0.05": "yes" if bh_adj[i] <= 0.05 else "no"})
with open(OUT / "robustness_bh.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pair", "outcome", "raw_p",
                                       "bh_adjusted", "bh_reject_0.05"])
    w.writeheader()
    w.writerows(bh_rows)

# ---- R5: bootstrap CI for spend contrast (seed 42, arm-stratified) ------------
rng = np.random.default_rng(42)
boot_rows = []
for t_arm, c_arm in PAIRS:
    x1 = df.loc[df["segment"] == t_arm, "spend"].to_numpy()
    x0 = df.loc[df["segment"] == c_arm, "spend"].to_numpy()
    n1, n0 = len(x1), len(x0)
    boots = np.empty(10000)
    for b in range(10000):
        s1 = x1[rng.integers(0, n1, n1)].mean()
        s0 = x0[rng.integers(0, n0, n0)].mean()
        boots[b] = s1 - s0
    boot_rows.append({"pair": f"{t_arm} minus {c_arm}", "outcome": "spend",
                      "bootstrap_mean": float(boots.mean()),
                      "ci_lo_percentile": float(np.percentile(boots, 2.5)),
                      "ci_hi_percentile": float(np.percentile(boots, 97.5)),
                      "resamples": 10000, "seed": 42})
with open(OUT / "robustness_bootstrap.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pair", "outcome", "bootstrap_mean",
                                       "ci_lo_percentile", "ci_hi_percentile",
                                       "resamples", "seed"])
    w.writeheader()
    w.writerows(boot_rows)
log_pipeline("bootstrap_resample_not_row_deletion", "all 64000 retained")

# ---- R6: funnel-stage descriptives (DESCRIPTIVE ONLY) -------------------------
r6_rows = []
for a in ARMS:
    sub = df.loc[df["segment"] == a]
    vis = sub.loc[sub["visit"] == 1]
    con = sub.loc[sub["conversion"] == 1]
    r6_rows.append({"arm": a, "n": len(sub),
                    "n_visit": len(vis),
                    "conv_rate_among_visitors": float(vis["conversion"].mean()),
                    "n_converted": len(con),
                    "mean_spend_among_converted": float(con["spend"].mean())})
with open(OUT / "funnel_descriptive.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["arm", "n", "n_visit",
                                       "conv_rate_among_visitors",
                                       "n_converted", "mean_spend_among_converted"])
    w.writeheader()
    w.writerows(r6_rows)

# ---- write-up ----------------------------------------------------------------
lines = [
    "# Balance and robustness (plan.md §7–§8)",
    "",
    "Source: results/analysis/{balance.csv,balance_shares.csv,robustness.csv,",
    "robustness_transformations.csv,robustness_bh.csv,robustness_bootstrap.csv,",
    "funnel_descriptive.csv} — produced by src/06_balance_and_robustness.py.",
    "R2–R6 retain all 64,000 rows; no customer is deleted in those analyses.",
    "The R1 deduplication illustration (cited from the verification artifacts)",
    "deletes rows and is not an alternative estimate.",
    "",
    "## Balance (non-gating)",
    "",
    f"max |SMD| over the five numeric covariates and three arms = {max_smd:.4f};",
    "values < 0.1 are read as no evidence against randomization (diagnostic only;",
    "randomization itself is assumption A1). Full table: balance.csv; shares:",
    "balance_shares.csv.",
    "",
    "## R1 deduplication (illustration only — NOT an alternative estimate)",
    "",
    "Cited from the committed verification artifacts (results/verification/",
    "dup_pathA.csv, 48/48 targets PASS): the deduplicated sample shifts the",
    "spend contrast from +0.769827 to +0.851223. This is retained as an",
    "illustration of a potentially invalid data-processing decision (dropping",
    "randomized individuals on an unverifiable criterion), not as an",
    "alternative treatment-effect estimate.",
    "",
    "## R2 covariate-adjusted OLS (HC1) — approximate re-expression",
    "",
    "Visit and conversion coefficients are probability-scale differences",
    "(×100 = percentage points); spend coefficients are USD per randomized",
    "customer. HC1 = heteroskedasticity-consistent standard errors.",
    "",
    "| Model | Term | Estimate | HC1 SE | 95% CI | p |",
    "|---|---|---|---|---|---|",
]
for r in model_rows:
    lines.append(f"| {r['model']} | {r['term']} | {r['estimate']:+.6f} | "
                 f"{r['se_hc1']:.6f} | [{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}] | "
                 f"{r['p_value']:.3g} |")
lines += [
    "",
    "## R3 outcome transformations (no deletion)",
    "",
    "### R3a — log1p(spend) Welch difference",
    "",
    "Values are differences in mean log1p(spend), in **log points** on the",
    "log1p scale. This is a transformed-outcome estimand, not a percentage",
    "change in arithmetic mean spending.",
    "",
    "| Pair | log1p diff (log points) | Welch SE | df | p |",
    "|---|---|---|---|---|",
]
for r in r3_rows:
    if r["analysis"].startswith("R3a"):
        lines.append(f"| {r['pair']} | {r['estimate']:+.6f} | {r['se']:.6f} | "
                     f"{r['df']:.1f} | {r['p_value']:.3g} |")
lines += [
    "",
    "### R3b — exact two-part decomposition of the mean-spend difference",
    "",
    "Arithmetic identity with midpoint weights (plan.md §8):",
    "",
    "    ΔE[spend] = ΔP(conversion) × (m1 + m0)/2 + ((p1 + p0)/2) × (m1 − m0)",
    "",
    "where p_a is the conversion probability and m_a the mean spend among",
    "converters in arm a. term1 is the conversion-rate component; term2 is the",
    "conditional-spend component. Components are USD per randomized customer;",
    "each share is component / total × 100.",
    "",
    "This is an arithmetic identity, not a causal mediation analysis. term2,",
    "and the weights used in both components, condition on a post-treatment",
    "outcome (conversion); those quantities are descriptive only (plan.md",
    "§8, §9). The ITT effects on total mean spending and on conversion",
    "probability are causal under randomization, but the split into components",
    "does not separately identify causal mechanisms. The shares depend on the",
    "weighting convention: midpoint weights are the plan choice, and",
    "control-side or treated-side weights give different shares for the same",
    "total.",
    "",
    "| Pair | Component | Value (USD per randomized customer) | Share of total |",
    "|---|---|---|---|",
]
for t_arm, c_arm in PAIRS:
    pair = f"{t_arm} minus {c_arm}"
    comp = {r["analysis"]: r["estimate"] for r in r3_rows if r["pair"] == pair}
    term1 = comp["R3b two-part: term1 Δconv × avg converter spend"]
    term2 = comp["R3b two-part: term2 avg conv rate × Δ converter spend"]
    total = comp["R3b two-part: total (identity check)"]
    for label, val in (
        ("term1: ΔP(conversion) × average converter spend", term1),
        ("term2: average conversion rate × Δ(mean spend among converters)", term2),
        ("total: ITT effect on mean spending (identity check)", total),
    ):
        lines.append(f"| {pair} | {label} | {val:+.6f} | "
                     f"{100.0 * val / total:+.1f}% |")
lines += [
    "",
    "## R4 Benjamini-Hochberg (beside Holm)",
    "",
    "| Pair | Outcome | raw p | BH-adjusted | reject at q=0.05 |",
    "|---|---|---|---|---|",
]
for r in bh_rows:
    lines.append(f"| {r['pair']} | {r['outcome']} | {r['raw_p']:.3g} | "
                 f"{r['bh_adjusted']:.3g} | {r['bh_reject_0.05']} |")
lines += [
    "",
    "## R5 bootstrap CI (spend, 10,000 resamples, seed 42)",
    "",
    "| Pair | bootstrap mean | 95% percentile CI |",
    "|---|---|---|",
]
for r in boot_rows:
    lines.append(f"| {r['pair']} | {r['bootstrap_mean']:+.6f} | "
                 f"[{r['ci_lo_percentile']:+.6f}, {r['ci_hi_percentile']:+.6f}] |")
lines += [
    "",
    "## R6 funnel-stage descriptives — DESCRIPTIVE ONLY",
    "",
    "These condition on post-treatment outcomes (plan.md §3/§9) and carry no",
    "causal interpretation.",
    "",
    "| Arm | n | visitors | conv among visitors | converted | mean spend among converted |",
    "|---|---|---|---|---|---|",
]
for r in r6_rows:
    lines.append(f"| {r['arm']} | {r['n']} | {r['n_visit']} | "
                 f"{r['conv_rate_among_visitors']:.6f} | {r['n_converted']} | "
                 f"{r['mean_spend_among_converted']:.6f} |")
lines += [
    "",
    "## Verification status",
    "",
    "Cross-checks by src/07/08 are agent-authored; agreement rules out coding",
    "slips but is NOT independent human validation. Human blinded review per",
    "VERIFICATION_PROTOCOL.md is pending.",
]
(OUT / "robustness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

upsert_model_log(
    "src/06_balance_and_robustness.py",
    "- R2: statsmodels OLS (HC1), n=64,000, design = intercept + treat_mens\n"
    "  + treat_womens + recency + history + mens + womens + newbie +\n"
    "  zip dummies (drop_first) + channel dummies (drop_first); outcomes:\n"
    "  visit, conversion, spend. Labeled approximate re-expression of ITT\n"
    "  contrasts (plan.md §8 R2). No randomness.\n"
    "- R3: closed-form Welch on log1p(spend); exact two-part decomposition\n"
    "  (arithmetic identity with midpoint weights; no causal mediation).\n"
    "- R5: numpy default_rng(42), 10,000 arm-stratified resamples per pair.\n")

h_after = sha256_file(RAW)
log_sha("after", h_after)
assert h_before == h_after, "data/raw changed during run!"
print(f"[integrity] data/raw SHA-256 unchanged: {h_after}")
print("[done] balance + robustness written")
