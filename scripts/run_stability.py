"""exp-025 -- SELECTION STABILITY: is the gate we report reproducible, and does asking that
question make the gate BETTER?

WHY THIS EXPERIMENT EXISTS
--------------------------
Every measure of selection quality in this project needs an answer key: ARI compares a clustering to
a reference partition, TPR/FDR compares a chosen feature set to a known one, and the canonical-marker
check in exp-024 compares a panel to the immunology textbook. None of them can run on a user's own
data, where no answer key exists. So the method currently cannot tell a user whether the panel it
just handed them is trustworthy -- and for an interpretability paper, "here is your answer and here
is how much to believe it" is most of the product.

Selection stability is the one measure that needs nothing. Resample the cells, run the selection
again, and count how often each feature comes back. That number is computable at runtime on unlabelled
data, and it is what an interactive interface should print next to every gate.

The four exp-024 runs already hinted at the shape of the answer. Across resampled versions of Levine,
the BOUNDARY recurred but the PANEL did not: the marker that defines each boundary came back almost
every time (CD3 4/4 for T cells, CD7 4/4 for NK, CD19 2/2 for B, CD34 2/2 for progenitors) while its
partner in the pair was different nearly every run. This experiment measures that properly, at fixed
nodes, with enough resamples to put a number on it.

THE SECOND, LARGER QUESTION
---------------------------
Stability is not only a diagnostic. Meinshausen & Bühlmann (JRSS-B 72:417-473, 2010) introduced it as
a SELECTION PROCEDURE: choose the features that recur across resamples rather than the ones that win
once. If the consensus panel beats the single-run panel, this stops being a caveat and becomes a
method improvement, which is a very different thing to report.

So every node here is scored twice, on the same cells, paired:

    SINGLE-RUN panel   the top pair by raw score on all the node's cells -- what exp-024 does now
    CONSENSUS panel    the two markers most often selected across B resamples of the node's cells

and both are judged by split purity and by whether they name the marker the textbook uses.

A THIRD THING THIS TESTS, FOR FREE
----------------------------------
exp-024 found that the calibrated-z bar cannot decide when to decline a split: the z values of splits
that cut through a population (2.66-6.72) overlapped those of clean splits (3.99-11.37), so no
threshold separates them. Stability offers a different bar -- decline when no marker recurs in at
least `stab_bar` of the resamples -- and this run measures whether that one separates them. If it
does, it replaces a rule we already know does not work.

WHAT IS MEASURED, IN PLAIN TERMS
--------------------------------
  selection frequency  of 30 resamples of this node's cells, how many picked marker X. 1.00 means
                       every resample chose it; 0.10 means it was a coin toss that landed once.
  split purity         for each cell population at this node, the fraction of its cells that ended
                       up on the same side as the majority of its own kind, averaged over
                       populations. 1.0 = the split kept every population whole; 0.5 = it cut one
                       straight down the middle.
  primary marker       the single marker an immunologist would draw this particular gate on.

Labels are used ONLY to check that selection frequency means what we think it means. The frequency
itself never sees them.

    python scripts/run_stability.py --jobs 8 --quick        # depth 2, B 10, a few minutes
    python scripts/run_stability.py --jobs 8                # the real run
    python scripts/run_stability.py --analyze-only results/levine_stability_cap60_B30_s0.json
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
import warnings
from collections import Counter

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atomicplus.evaluation.calibration import calibrate
from run_levine_tree import (LEVINE_POPULATIONS, MIN_CELLS, TERMS, describe, load_capped,
                             majority_sides, name_boundary, present, purity)

BAR_Z = 2.0        # the calibrated-z abstention bar from exp-021, kept only for comparison


# ------------------------------------------------------------------------------------------------
# The resampling core
# ------------------------------------------------------------------------------------------------

def best_pair(fn, Z: np.ndarray, pairs) -> tuple:
    """Top-scoring pair of columns by the RAW score. This is the selection procedure, one run of it."""
    best, arg = -np.inf, pairs[0]
    for s in pairs:
        v = fn(Z[:, list(s)])[0]
        if np.isfinite(v) and v > best:
            best, arg = v, s
    return arg


def _one_resample(fn, Z: np.ndarray, pairs, seed: int, frac: float) -> tuple:
    """Draw a subsample of the ROWS and re-run the selection on it. Top level so joblib can pickle."""
    rng = np.random.default_rng(seed)
    m = max(MIN_CELLS, int(round(frac * len(Z))))
    idx = rng.choice(len(Z), size=min(m, len(Z)), replace=False)
    return best_pair(fn, Z[idx], pairs)


def stability(fn, Z: np.ndarray, pairs, B: int, frac: float, seed: int, jobs: int) -> dict:
    """Selection frequency of every marker, and of every pair, over B resamples of the rows.

    Subsampling without replacement at `frac` rather than a with-replacement bootstrap: duplicated
    rows sit at distance zero from each other, which inflates every local-density and
    nearest-neighbour quantity our scores are built from. Subsampling is the standard substitute in
    the stability-selection literature for exactly this reason.
    """
    if jobs != 1 and B > 1:
        from joblib import Parallel, delayed
        picks = Parallel(n_jobs=jobs)(
            delayed(_one_resample)(fn, Z, pairs, seed * 1000 + b, frac) for b in range(B))
    else:
        picks = [_one_resample(fn, Z, pairs, seed * 1000 + b, frac) for b in range(B)]
    marker = Counter()
    for s in picks:
        marker.update(s)
    pair = Counter(tuple(sorted(s)) for s in picks)
    return {"marker_freq": {int(k): v / B for k, v in marker.items()},
            "pair_freq": {str(k): v / B for k, v in pair.items()},
            "top_pair": list(max(pair.items(), key=lambda kv: kv[1])[0]),
            "top_pair_freq": max(pair.values()) / B,
            "top_marker_freq": max(marker.values()) / B if marker else 0.0}


def consensus_panel(marker_freq: dict, k: int = 2) -> list:
    """The k markers most often selected across resamples. Ties broken by column index, so the
    result is reproducible rather than dependent on dict ordering."""
    return sorted(sorted(marker_freq, key=lambda j: (-marker_freq[j], j))[:k])


# ------------------------------------------------------------------------------------------------
# One node, scored two ways on the same cells
# ------------------------------------------------------------------------------------------------

def score_panel(fn, sub, y_node, panel, names):
    """Split on `panel` and report what the split did. Returns None if the split is degenerate."""
    lab = fn(sub[:, list(panel)])[1]
    if lab is None or lab.sum() in (0, len(lab)):
        return None
    side = lab.astype(bool)
    pu, pw = purity(y_node, side)
    left, right = majority_sides(y_node, side)
    bnd = name_boundary(left, right)
    pn = [names[j] for j in panel]
    return dict(panel=pn, purity=pu, purity_weighted=pw, side=side,
                boundary=bnd["name"] if bnd else None,
                primary=bnd["primary"] if bnd else None,
                primary_hit=bool(bnd and bnd["primary"] in pn),
                any_hit=bool(bnd and ({bnd["primary"]} | set(bnd["also"])) & set(pn)))


def walk(X, y, idx, names, depth, node_id, cfg, fn, pairs, log):
    sub, y_node = X[idx], y[idx]
    here = sorted(LEVINE_POPULATIONS[c] for c in present(y_node))
    node = {"id": node_id, "depth": depth, "n": int(len(idx)), "populations_present": here}
    pad = "  " * depth

    if len(idx) < MIN_CELLS or len(here) < 2 or depth >= cfg["depth"]:
        node["leaf"] = True
        node["reason"] = ("too few cells" if len(idx) < MIN_CELLS else
                          "single population" if len(here) < 2 else "depth limit")
        log(f"{pad}[{node_id}] LEAF n={len(idx)} ({node['reason']}) {here}")
        return node

    t0 = time.time()
    single = best_pair(fn, sub, pairs)                      # what exp-024 would pick
    st = stability(fn, sub, pairs, cfg["B"], cfg["frac"], cfg["seed"] + depth, cfg["jobs"])
    cons = consensus_panel(st["marker_freq"], 2)            # what recurrence picks

    s_single = score_panel(fn, sub, y_node, single, names)
    s_cons = score_panel(fn, sub, y_node, cons, names)
    z = calibrate(fn, sub, cons, B=15, shared_seed=0)["z"]

    node.update(
        n_resamples=cfg["B"], resample_frac=cfg["frac"],
        marker_freq={names[j]: round(v, 3) for j, v in
                     sorted(st["marker_freq"].items(), key=lambda kv: -kv[1])},
        top_marker_freq=round(st["top_marker_freq"], 3),
        top_pair_freq=round(st["top_pair_freq"], 3),
        panel_single=[names[j] for j in single],
        panel_consensus=[names[j] for j in cons],
        agree=bool(tuple(sorted(single)) == tuple(cons)),
        z_consensus=None if not np.isfinite(z) else round(float(z), 2),
        seconds=round(time.time() - t0, 1))
    for tag, s in (("single", s_single), ("consensus", s_cons)):
        node[tag] = None if s is None else {k: v for k, v in s.items() if k != "side"}

    # ABSTENTION, decided by recurrence rather than by the calibrated-z bar. The z is recorded
    # alongside so the two rules can be compared on the same nodes after the fact.
    if st["top_marker_freq"] < cfg["stab_bar"] or s_cons is None:
        node["leaf"] = True
        node["reason"] = (f"ABSTAIN (no marker recurred in >= {cfg['stab_bar']:.0%} of resamples; "
                          f"best {st['top_marker_freq']:.0%})" if s_cons is not None
                          else "degenerate split")
        log(f"{pad}[{node_id}] ABSTAIN n={len(idx)} top-marker {st['top_marker_freq']:.0%} {here}")
        return node

    node["leaf"] = False
    top3 = list(node["marker_freq"].items())[:3]
    log(f"{pad}[{node_id}] n={len(idx):4d} consensus=({','.join(node['panel_consensus'])}) "
        f"single=({','.join(node['panel_single'])}) "
        f"purity {s_cons['purity']:.3f} vs {s_single['purity'] if s_single else float('nan'):.3f}  "
        f"freq {top3}"
        + (f"  -> {s_cons['boundary']}: {s_cons['primary']} "
           f"{'NAMED' if s_cons['primary_hit'] else 'missed'}" if s_cons["boundary"] else ""))

    side = fn(sub[:, list(cons)])[1].astype(bool)
    node["went"] = describe(y_node, side)
    node["children"] = [walk(X, y, idx[~side], names, depth + 1, node_id + "L", cfg, fn, pairs, log),
                        walk(X, y, idx[side], names, depth + 1, node_id + "R", cfg, fn, pairs, log)]
    return node


# ------------------------------------------------------------------------------------------------

def summarise(tree):
    rows = []

    def w(n):
        if n.get("leaf"):
            rows.append(dict(id=n["id"], depth=n["depth"], n=n["n"], leaf=n["reason"]))
            return
        s, c = n.get("single") or {}, n["consensus"]
        rows.append(dict(
            id=n["id"], depth=n["depth"], n=n["n"], leaf="",
            top_marker=round(n["top_marker_freq"], 2), top_pair=round(n["top_pair_freq"], 2),
            consensus=",".join(n["panel_consensus"]), single=",".join(n["panel_single"]),
            agree=n["agree"], pur_cons=round(c["purity"], 3),
            pur_single=round(s.get("purity", np.nan), 3) if s else np.nan,
            boundary=c.get("boundary") or "", primary=c.get("primary") or "",
            hit_cons=("" if not c.get("boundary") else
                      "PRIMARY" if c["primary_hit"] else "related" if c["any_hit"] else "miss"),
            hit_single=("" if not (s and s.get("boundary")) else
                        "PRIMARY" if s["primary_hit"] else "related" if s["any_hit"] else "miss")))
        for ch in n["children"]:
            w(ch)
    w(tree)
    df = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print("\n" + "=" * 118 + "\nexp-025 -- SELECTION STABILITY\n" + "=" * 118)
    print(df.to_string(index=False))
    I = df[df.leaf == ""]
    if not len(I):
        print("\n  every node abstained -- nothing to compare."); return df

    print("\n[1] HOW REPRODUCIBLE IS A GATE?  (1.00 = every resample picked it)")
    print(f"    most-selected MARKER per node: median {I.top_marker.median():.2f}   "
          f"range {I.top_marker.min():.2f}-{I.top_marker.max():.2f}")
    print(f"    most-selected PAIR   per node: median {I.top_pair.median():.2f}   "
          f"range {I.top_pair.min():.2f}-{I.top_pair.max():.2f}")
    print("    If the marker number is high and the pair number is low, the method knows WHICH")
    print("    marker the split is about but not which partner to plot it against.")

    print("\n[2] DOES PICKING BY RECURRENCE BEAT PICKING ONCE?  (same cells, paired per node)")
    d = I.pur_cons - I.pur_single
    print(f"    nodes where the two procedures chose the same pair: {int(I.agree.sum())}/{len(I)}")
    print(f"    split purity  consensus {I.pur_cons.mean():.3f}  vs  single-run "
          f"{I.pur_single.mean():.3f}   (difference {d.mean():+.3f})")
    print(f"    consensus better on {int((d > 0.001).sum())} nodes, worse on "
          f"{int((d < -0.001).sum())}, tied on {int((d.abs() <= 0.001).sum())}")
    ck = I[I.boundary != ""]
    if len(ck):
        print(f"    named the textbook marker: consensus "
              f"{int((ck.hit_cons == 'PRIMARY').sum())}/{len(ck)}  vs  single-run "
              f"{int((ck.hit_single == 'PRIMARY').sum())}/{len(ck)}")

    print("\n[3] CAN RECURRENCE DECIDE WHEN TO DECLINE A SPLIT?")
    bad, good = I[I.pur_cons < 0.90], I[I.pur_cons >= 0.99]
    if len(bad) and len(good):
        print(f"    splits that cut through a population (purity<0.90): {len(bad)}; "
              f"top-marker frequency {bad.top_marker.min():.2f}-{bad.top_marker.max():.2f}")
        print(f"    clean splits (purity>=0.99): {len(good)}; top-marker frequency "
              f"{good.top_marker.min():.2f}-{good.top_marker.max():.2f}")
        print(f"    -> the two ranges "
              f"{'SEPARATE' if bad.top_marker.max() < good.top_marker.min() else 'OVERLAP'}"
              f"   (Spearman frequency vs purity "
              f"{I.top_marker.corr(I.pur_cons, method='spearman'):+.3f})")
        print("    Compare exp-024, where the calibrated-z ranges overlapped and no bar worked.")
    else:
        print(f"    not enough of both kinds to compare ({len(bad)} unclean, {len(good)} clean).")
    print(f"\n    declined to split: {int(df.leaf.str.contains('ABSTAIN').sum())} nodes   "
          f"single population: {int(df.leaf.str.contains('single population').sum())}   "
          f"too few cells: {int(df.leaf.str.contains('too few').sum())}")
    print("\n  Selection frequency uses no labels and is computable on a user's own data.")
    print("  Purity and the marker check use labels, and only to verify that frequency means")
    print("  what we claim it means.")
    return df


def main():
    a = list(sys.argv[1:])
    cfg = dict(depth=6, cap=60, B=30, frac=0.7, stab_bar=0.5, jobs=1, seed=0, term="graphcut",
               n_prop=800)
    if "--analyze-only" in a:
        i = a.index("--analyze-only")
        summarise(json.load(open(a[i + 1]))); return
    proportional = "--proportional" in a
    if proportional:
        a.remove("--proportional")
    if "--quick" in a:
        a.remove("--quick"); cfg.update(depth=2, cap=40, B=10)
    for k in list(cfg):
        for f in (f"--{k}", f"--{k.replace('_', '-')}"):
            if f in a:
                i = a.index(f)
                cfg[k] = (a[i + 1] if k == "term" else
                          float(a[i + 1]) if k in ("frac", "stab_bar") else int(a[i + 1]))
                del a[i:i + 2]
                break
    if a:
        print(f"unrecognised arguments: {a}"); sys.exit(2)

    X, y, names = load_capped(cfg["cap"], cfg["seed"], proportional, cfg["n_prop"])
    fn = TERMS[cfg["term"]]
    pairs = list(itertools.combinations(range(X.shape[1]), 2))
    print(f"Levine: {X.shape[0]} cells x {X.shape[1]} markers, {len(set(y.tolist()))} populations")
    print(f"  {cfg['B']} resamples per node at {cfg['frac']:.0%} of the node's cells, "
          f"{len(pairs)} pairs each\n  config {cfg}\n", flush=True)

    t0 = time.time()
    tree = walk(X, y, np.arange(len(X)), names, 0, "root", cfg, fn, pairs,
                lambda s: print(s, flush=True))
    tree["_config"] = {**cfg, "proportional": proportional}
    os.makedirs("results", exist_ok=True)
    tag = f"prop{cfg['n_prop']}" if proportional else f"cap{cfg['cap']}"
    out = f"results/levine_stability_{tag}_B{cfg['B']}_s{cfg['seed']}.json"
    json.dump(tree, open(out, "w"), indent=1)
    print(f"\nwrote {out}  ({time.time() - t0:.0f}s)")
    summarise(tree)


if __name__ == "__main__":
    main()
