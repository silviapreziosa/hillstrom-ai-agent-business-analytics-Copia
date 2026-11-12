#!/usr/bin/env python3
"""
src/01_verify_duplicates_primary.py — Path A (pandas).

Recomputes every previously reported duplicate-row number on the real dataset,
plus point estimates and standard errors under:
  S1 = all rows (as given)
  S2 = deduplicated sample (sensitivity scenario)
Read-only w.r.t. data/raw/ (SHA-256 recorded before and after the run).
Writes: results/verification/dup_pathA.csv, results/verification/sha256_log.csv
Prints the row count after every reduction (AGENTS.md rule 2).
No randomness is used (seed n/a; deterministic computation).
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "verification"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
ARMS = (MEN, NOE, WOM)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_sha(stage: str, digest: str, log_path: Path) -> None:
    new = not log_path.exists()
    with open(log_path, "a", encoding="utf-8") as fh:
        if new:
            fh.write("timestamp,stage,sha256\n")
        fh.write(f"{datetime.now(timezone.utc).isoformat()},{stage},{digest}\n")


h_before = sha256_file(RAW)
log_sha("01:before", h_before, OUT / "sha256_log.csv")

df = pd.read_csv(RAW)
total_rows = len(df)
assert total_rows == 64000, f"unexpected raw row count {total_rows}"

metrics: list[tuple[str, float]] = []


def collect(prefix: str, d: pd.DataFrame) -> dict:
    """Group sizes, outcome means and Mens-vs-No-E-Mail contrasts."""
    stats = {}
    for arm in ARMS:
        sub = d.loc[d["segment"] == arm]
        stats[(arm, "n")] = float(len(sub))
        metrics.append((f"{prefix}.n.{arm}", float(len(sub))))
        for col in ("visit", "conversion", "spend"):
            m = float(sub[col].mean())
            stats[(arm, col)] = m
            metrics.append((f"{prefix}.mean.{col}.{arm}", m))
    for col in ("visit", "conversion", "spend"):
        c = stats[(MEN, col)] - stats[(NOE, col)]
        stats[("contrast", col)] = c
        metrics.append((f"{prefix}.contrast.{col}.MensMinusNo", c))
    return stats


s1 = collect("S1", df)

dd = df.drop_duplicates()
print(f"[rule 2] drop_duplicates (all 12 columns): {total_rows} -> {len(dd)} rows "
      f"(removed {total_rows - len(dd)} exact duplicate rows; reason: S2 sensitivity "
      f"sample; data/raw/ untouched)")

s2 = collect("S2", dd)
for col in ("visit", "conversion", "spend"):
    metrics.append((f"Delta.{col}.MensMinusNo", s2[("contrast", col)] - s1[("contrast", col)]))

# --- duplicate bookkeeping -------------------------------------------------
dups_mask = df.duplicated(keep=False)
dups = df.loc[dups_mask]
patterns = len(dups.drop_duplicates())
excess = total_rows - len(dd)
metrics += [
    ("book.total", float(total_rows)),
    ("book.unique", float(len(dd))),
    ("book.excess", float(excess)),
    ("book.keepFalse", float(len(dups))),
    ("book.patterns", float(patterns)),
    ("book.dups.visit1", float((dups["visit"] == 1).sum())),
    ("book.dups.conv1", float((dups["conversion"] == 1).sum())),
    ("book.dups.spendpos", float((dups["spend"] > 0).sum())),
]
for arm in ARMS:
    dfa = dups.loc[dups["segment"] == arm]
    dd_arm = dd.loc[dd["segment"] == arm]
    n_arm = len(df.loc[df["segment"] == arm])
    metrics.append((f"book.keepFalse.arm.{arm}", float(len(dfa))))
    metrics.append((f"book.excess.arm.{arm}", float(n_arm - len(dd_arm))))

# --- funnel coherence -------------------------------------------------------
metrics += [
    ("funnel.visitors", float(df["visit"].sum())),
    ("funnel.conversions", float(df["conversion"].sum())),
    ("funnel.bad_spend_noconv", float(((df["spend"] > 0) & (df["conversion"] == 0)).sum())),
    ("funnel.bad_conv_novisit", float(((df["conversion"] == 1) & (df["visit"] == 0)).sum())),
]


# --- standard errors (descriptive; no hypothesis tests) ----------------------
def se_of(d: pd.DataFrame, col: str) -> float:
    sub_m = d.loc[d["segment"] == MEN, col]
    sub_n = d.loc[d["segment"] == NOE, col]
    if col == "spend":
        v1, v2 = sub_m.var(ddof=1), sub_n.var(ddof=1)
    else:
        p1, p2 = sub_m.mean(), sub_n.mean()
        v1, v2 = p1 * (1 - p1), p2 * (1 - p2)
    return float(np.sqrt(v1 / len(sub_m) + v2 / len(sub_n)))


for smp, d in (("S1", df), ("S2", dd)):
    for col in ("visit", "conversion", "spend"):
        metrics.append((f"SE.{smp}.{col}", se_of(d, col)))

out_csv = OUT / "dup_pathA.csv"
out_csv.write_text("metric,value\n" + "".join(f"{m},{v!r}\n" for m, v in metrics),
                   encoding="utf-8")

h_after = sha256_file(RAW)
log_sha("01:after", h_after, OUT / "sha256_log.csv")
assert h_before == h_after, "data/raw changed during run!"
print(f"[integrity] data/raw SHA-256 unchanged: {h_after}")
print(f"[done] wrote {out_csv} ({len(metrics)} metrics)")
