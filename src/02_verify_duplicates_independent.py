#!/usr/bin/env python3
"""
src/02_verify_duplicates_independent.py — Path B (pure Python, exact rational
arithmetic). Shares no code and no library with Path A (01_verify_duplicates_
primary.py). Reads data/raw/ read-only with SHA-256 guards. Values are
canonicalised to the same typing a parser would use (history/spend -> exact
Fraction, integer columns -> int, strings kept), so deduplication semantics
equal pandas drop_duplicates over all 12 columns.
Writes: results/verification/dup_pathB.csv, appends sha256_log.csv.
Prints row count after the only reduction, deduplication (AGENTS.md rule 2).
No randomness (deterministic).
"""
import csv
import hashlib
import math
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hillstorm_no_indices.csv"
OUT = ROOT / "results" / "verification"
OUT.mkdir(parents=True, exist_ok=True)

MEN, NOE, WOM = "Mens E-Mail", "No E-Mail", "Womens E-Mail"
ARMS = (MEN, NOE, WOM)
INT_COLS = {"recency", "mens", "womens", "newbie", "visit", "conversion"}
DEC_COLS = {"history", "spend"}


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


def canon_val(name: str, v: str):
    if name in DEC_COLS:
        return Fraction(v)
    if name in INT_COLS:
        return int(v)
    return v


h_before = sha256_file(RAW)
log_sha("02:before", h_before, OUT / "sha256_log.csv")

with open(RAW, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    fields = list(reader.fieldnames)
    keys_count: dict[tuple, int] = {}
    total = 0
    visitors = conv_total = 0
    bad_spend_noconv = bad_conv_novisit = 0
    # per-arm S1 accumulators (rows as given)
    S1 = {a: {"n": 0, "sv": 0, "sv2": 0, "sc": 0, "sc2": 0, "ss": Fraction(0),
              "ss2": Fraction(0)} for a in ARMS}
    for row in reader:
        k = tuple(canon_val(name, row[name]) for name in fields)
        seg_i = fields.index("segment")   # fixed by header; hoistable, but cheap
        S1[k[seg_i]]["n"] += 1
        S1[k[seg_i]]["sv"] += k[fields.index("visit")]
        S1[k[seg_i]]["sv2"] += k[fields.index("visit")] ** 2
        S1[k[seg_i]]["sc"] += k[fields.index("conversion")]
        S1[k[seg_i]]["sc2"] += k[fields.index("conversion")] ** 2
        ss = k[fields.index("spend")]
        S1[k[seg_i]]["ss"] += ss
        S1[k[seg_i]]["ss2"] += ss * ss
        keys_count[k] = keys_count.get(k, 0) + 1
        # funnel counters
        v, c = k[fields.index("visit")], k[fields.index("conversion")]
        sp = k[fields.index("spend")]
        visitors += v
        conv_total += c
        if sp > 0 and c == 0:
            bad_spend_noconv += 1
        if c == 1 and v == 0:
            bad_conv_novisit += 1
        total += 1

seg_i = fields.index("segment")
unique = len(keys_count)
excess = total - unique
keepFalse_keys = [k for k, c in keys_count.items() if c >= 2]
keepFalse_rows = sum(c for c in keys_count.values() if c >= 2)
patterns = len(keepFalse_keys)
print(f"[rule 2] drop_duplicates (all 12 columns): {total} -> {unique} rows "
      f"(removed {excess} exact duplicate rows; reason: S2 sensitivity sample; "
      f"data/raw/ untouched)")

vis_i, con_i, spe_i = fields.index("visit"), fields.index("conversion"), fields.index("spend")

# ---- S2 accumulators (deduplicated: one row per distinct key) ----------------
S2 = {a: {"n": 0, "sv": 0, "sv2": 0, "sc": 0, "sc2": 0, "ss": Fraction(0),
          "ss2": Fraction(0)} for a in ARMS}
for k in keys_count:
    a = S1  # alias unused; compute directly
    arm = k[seg_i]
    S2[arm]["n"] += 1
    S2[arm]["sv"] += k[vis_i]
    S2[arm]["sv2"] += k[vis_i] ** 2
    S2[arm]["sc"] += k[con_i]
    S2[arm]["sc2"] += k[con_i] ** 2
    S2[arm]["ss"] += k[spe_i]
    S2[arm]["ss2"] += k[spe_i] ** 2

metrics: list[tuple[str, float]] = []


def emit_sample(prefix: str, accs: dict) -> None:
    for arm in ARMS:
        a = accs[arm]
        n = a["n"]
        metrics.append((f"{prefix}.n.{arm}", float(n)))
        for col, num in (("visit", a["sv"]), ("conversion", a["sc"])):
            metrics.append((f"{prefix}.mean.{col}.{arm}", float(Fraction(num, n))))
        metrics.append((f"{prefix}.mean.spend.{arm}", float(a["ss"] / n)))
    for col in ("visit", "conversion"):
        c = Fraction(accs[MEN]["sv"] if col == "visit" else accs[MEN]["sc"],
                     accs[MEN]["n"]) \
            - Fraction(accs[NOE]["sv"] if col == "visit" else accs[NOE]["sc"],
                       accs[NOE]["n"])
        metrics.append((f"{prefix}.contrast.{col}.MensMinusNo", float(c)))
        accs[("contrast", col)] = c
    c = accs[MEN]["ss"] / accs[MEN]["n"] - accs[NOE]["ss"] / accs[NOE]["n"]
    metrics.append((f"{prefix}.contrast.spend.MensMinusNo", float(c)))
    accs[("contrast", "spend")] = c


emit_sample("S1", S1)
emit_sample("S2", S2)
for col in ("visit", "conversion", "spend"):
    d = S2[("contrast", col)] - S1[("contrast", col)]
    metrics.append((f"Delta.{col}.MensMinusNo", float(d)))

# bookkeeping (exact)
metrics += [
    ("book.total", float(total)),
    ("book.unique", float(unique)),
    ("book.excess", float(excess)),
    ("book.keepFalse", float(keepFalse_rows)),
    ("book.patterns", float(patterns)),
    ("book.dups.visit1", float(sum(c for k, c in keys_count.items()
                                   if c >= 2 and k[vis_i] == 1))),
    ("book.dups.conv1", float(sum(c for k, c in keys_count.items()
                                  if c >= 2 and k[con_i] == 1))),
    ("book.dups.spendpos", float(sum(c for k, c in keys_count.items()
                                     if c >= 2 and k[spe_i] > 0))),
]
excess_by_arm = {a: S1[a]["n"] - S2[a]["n"] for a in ARMS}
kf_by_arm = {a: sum(c for k, c in keys_count.items() if c >= 2 and k[seg_i] == a)
             for a in ARMS}
for arm in ARMS:
    metrics.append((f"book.keepFalse.arm.{arm}", float(kf_by_arm[arm])))
    metrics.append((f"book.excess.arm.{arm}", float(excess_by_arm[arm])))

metrics += [
    ("funnel.visitors", float(visitors)),
    ("funnel.conversions", float(conv_total)),
    ("funnel.bad_spend_noconv", float(bad_spend_noconv)),
    ("funnel.bad_conv_novisit", float(bad_conv_novisit)),
]


def var_of(a: dict, col: str) -> Fraction:
    """Exact sample variance (ddof=1) from accumulated raw moments."""
    n = a["n"]
    if col == "visit":
        return (Fraction(a["sv2"]) - Fraction(a["sv"] * a["sv"], n)) / (n - 1)
    if col == "conversion":
        return (Fraction(a["sc2"]) - Fraction(a["sc"] * a["sc"], n)) / (n - 1)
    return (a["ss2"] - a["ss"] * a["ss"] / n) / (n - 1)


def exact_se(accs: dict, col: str) -> float:
    n_m, n_n = accs[MEN]["n"], accs[NOE]["n"]
    if col == "spend":
        v1, v2 = var_of(accs[MEN], "spend"), var_of(accs[NOE], "spend")
    else:
        p1 = Fraction(accs[MEN]["sv"] if col == "visit" else accs[MEN]["sc"],
                      accs[MEN]["n"])
        p2 = Fraction(accs[NOE]["sv"] if col == "visit" else accs[NOE]["sc"],
                      accs[NOE]["n"])
        v1, v2 = p1 * (1 - p1), p2 * (1 - p2)
    return math.sqrt(v1 / n_m + v2 / n_n)


for smp, accs in (("S1", S1), ("S2", S2)):
    for col in ("visit", "conversion", "spend"):
        metrics.append((f"SE.{smp}.{col}", exact_se(accs, col)))

out_csv = OUT / "dup_pathB.csv"
out_csv.write_text("metric,value\n" + "".join(f"{m},{v!r}\n" for m, v in metrics),
                   encoding="utf-8")

h_after = sha256_file(RAW)
log_sha("02:after", h_after, OUT / "sha256_log.csv")
assert h_before == h_after, "data/raw changed during run!"
print(f"[integrity] data/raw SHA-256 unchanged: {h_after}")
print(f"[done] wrote {out_csv} ({len(metrics)} metrics)")
