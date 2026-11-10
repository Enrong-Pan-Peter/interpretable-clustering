"""STAGE 0 -- does correcting for "junk level" change which feature pair wins?

THE QUESTION, IN PLAIN TERMS
----------------------------
Today we score every candidate pair of features and take the highest. With hundreds of pairs,
some meaningless pair scores high by luck. The proposed fix is to judge each pair against what a
MEANINGLESS VERSION OF THAT SAME PAIR would score: scramble one column against the other so each
column keeps its own shape but any relationship between them is destroyed, score it a few hundred
times, and call that the pair's "junk level". The new score is how far the real score sits above
that pair's own junk level.

THE TRAP THIS SCRIPT EXISTS TO CATCH: if every pair has the SAME junk level, then subtracting it
is the same as subtracting a constant from everybody. The leaderboard order does not change, the
same pair wins, and the fix buys NOTHING for selection. It only helps if junk levels DIFFER
between pairs. So we measure that before building anything.

Rather than only measuring the proxy, at p=20 we can afford to measure the OUTCOME directly:
compute the true junk level of every pair, then check whether corrected ranking actually picks
the right pair more often than raw ranking does. The heterogeneity ratio then explains WHY.

WHAT IT REPORTS
---------------
  1. heterogeneity ratio  = (spread of junk levels ACROSS pairs) / (typical bounce WITHIN a pair)
     This is the pre-registered gate. Below 0.25 = junk levels are effectively identical = the
     ranking claim (Claim 1) is dead and we do not build it.
  2. rank-1 selection, RAW vs CORRECTED, per shape. The direct outcome.
  3. Spearman correlation between the raw and corrected orderings. Near 1.0 means correcting
     reordered nothing, which is the same verdict as a failed gate arriving by another route.

COST / RUNNING IT
-----------------
Each pair costs B scrambles x ~23 ms. At p=20 that is 190 pairs x 200 = ~15 min per (shape,seed).

    # sanity check first (~3 min)
    python scripts/run_stage0_junklevels.py --quick

    # the real run: exact at p=20, sampled at p=40, 25 instances. ~7h at --jobs 8.
    python scripts/run_stage0_junklevels.py --seeds 25 --jobs 8

Saves incrementally to results/stage0_junklevels.csv, so an interrupted run is not lost. Re-run
the analysis alone on an existing CSV with --analyze-only.
"""
import itertools
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scipy.stats import spearmanr

from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term, zscore

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_method_baselines import INF, KNOWN_DATASETS, load          # reuse the exact same data

OUT = "results/stage0_junklevels.csv"
GATE = 0.25                     # pre-registered: below this, junk levels count as identical


def raw_scores(Z):
    g, _ = graphcut_term(Z)
    d, _ = density_term(Z)
    return g, d


def junk_level(Xp, pair, B, rng):
    """Scramble the two columns against each other B times; return mean/sd of the junk scores."""
    Z = Xp[:, list(pair)].copy()
    gs = np.empty(B)
    ds = np.empty(B)
    n = len(Z)
    for b in range(B):
        W = np.column_stack([Z[rng.permutation(n), 0], Z[rng.permutation(n), 1]])
        gs[b], ds[b] = raw_scores(W)
    return gs.mean(), gs.std(), ds.mean(), ds.std()


def one_cell(name, p, seed, B, n_pairs):
    rng = np.random.default_rng(10_000 + seed)
    Xp, y = load(name, p, seed)
    pairs = list(itertools.combinations(range(p), 2))
    if n_pairs and n_pairs < len(pairs):
        # sample, but ALWAYS keep the true pair -- otherwise rank-1 is undefined
        keep = {tuple(INF)}
        others = [q for q in pairs if q != tuple(INF)]
        idx = rng.choice(len(others), size=n_pairs - 1, replace=False)
        keep |= {others[i] for i in idx}
        pairs = sorted(keep)
    rows = []
    for pr in pairs:
        g, d = raw_scores(Xp[:, list(pr)])
        gm, gsd, dm, dsd = junk_level(Xp, pr, B, rng)
        rows.append(dict(dataset=name, p=p, seed=seed, pair=str(pr),
                         is_true=int(pr == tuple(INF)), n_pairs=len(pairs),
                         gc=g, de=d, gc_junk_mean=gm, gc_junk_sd=gsd,
                         de_junk_mean=dm, de_junk_sd=dsd))
    return rows


def analyze(df):
    print("\n" + "=" * 78)
    print("STAGE 0 RESULTS")
    print("=" * 78)

    print("\n[1] HETEROGENEITY RATIO -- the pre-registered gate (fires below %.2f)" % GATE)
    print("    = spread of junk levels across pairs / typical bounce within one pair")
    print("    Computed on NOISE pairs only (the true pair is excluded; it is not junk).")
    het = []
    for (ds_, p_), g in df[df.is_true == 0].groupby(["dataset", "p"]):
        for term in ("gc", "de"):
            between = g.groupby("seed")[f"{term}_junk_mean"].std().mean()
            within = g[f"{term}_junk_sd"].mean()
            het.append(dict(dataset=ds_, p=p_, term=term,
                            ratio=between / within if within > 1e-12 else np.nan))
    h = pd.DataFrame(het)
    print(h.pivot_table(index=["dataset", "p"], columns="term", values="ratio").round(3).to_string())
    overall = h.groupby("term")["ratio"].mean()
    print("\n    mean ratio:  " + "  ".join(f"{t}={v:.3f}" for t, v in overall.items()))
    verdict = "PASS (junk levels differ -> correcting can reorder)" if overall.max() >= GATE \
        else "FAIL (junk levels effectively identical -> Claim 1 is DEAD, do not build it)"
    print(f"    GATE VERDICT: {verdict}")

    print("\n[2] DIRECT OUTCOME -- rank-1 selection, raw vs corrected")
    print("    raw       = current hybrid, z(graphcut) + z(density) across pairs")
    print("    corrected = each term measured against that pair's own junk level")
    out = []
    for (ds_, p_, sd_), g in df.groupby(["dataset", "p", "seed"]):
        g = g.reset_index(drop=True)
        ti = int(np.flatnonzero(g.is_true.values == 1)[0])
        raw = zscore(g.gc.values) + zscore(g.de.values)
        corr = ((g.gc.values - g.gc_junk_mean.values) / np.maximum(g.gc_junk_sd.values, 1e-9)
                + (g.de.values - g.de_junk_mean.values) / np.maximum(g.de_junk_sd.values, 1e-9))
        rho = spearmanr(raw, corr).statistic if len(raw) > 2 else np.nan
        out.append(dict(dataset=ds_, p=p_, seed=sd_,
                        raw_r1=int(np.argmax(raw) == ti), corr_r1=int(np.argmax(corr) == ti),
                        spearman=rho))
    o = pd.DataFrame(out)
    print(o.pivot_table(index="dataset", columns="p",
                        values=["raw_r1", "corr_r1"], aggfunc="mean").round(2).to_string())
    print("\n    overall:  raw=%.3f   corrected=%.3f   (delta %+.3f)"
          % (o.raw_r1.mean(), o.corr_r1.mean(), o.corr_r1.mean() - o.raw_r1.mean()))

    print("\n[3] SPEARMAN between raw and corrected orderings (near 1.0 = nothing reordered)")
    print(o.pivot_table(index="dataset", columns="p", values="spearman",
                        aggfunc="mean").round(3).to_string())
    print("\nReminder: [2] is the outcome that matters. [1] and [3] explain it. If [1] fails but")
    print("[2] improves anyway, TRUST [2] and work out why the gate was wrong -- do not bury it.")


def main():
    args = list(sys.argv[1:])
    seeds, B, jobs = 25, 200, 1
    grid = [(20, None), (40, 100)]          # (p, n_pairs) -- None = every pair
    if "--analyze-only" in args:
        analyze(pd.read_csv(OUT)); return
    if "--quick" in args:
        args.remove("--quick"); seeds, B, grid = 2, 40, [(12, 30)]
    for flag, cast in (("--seeds", int), ("--B", int), ("--jobs", int)):
        if flag in args:
            i = args.index(flag); v = cast(args[i + 1]); del args[i:i + 2]
            seeds, B, jobs = (v if flag == "--seeds" else seeds,
                              v if flag == "--B" else B,
                              v if flag == "--jobs" else jobs)
    datasets = args if args else list(KNOWN_DATASETS)
    bad = [d for d in datasets if d not in KNOWN_DATASETS]
    if bad:
        print(f"ERROR: unknown dataset(s) {bad}; valid: {' '.join(KNOWN_DATASETS)}", file=sys.stderr)
        sys.exit(2)

    os.makedirs("results", exist_ok=True)
    rows, t0 = [], time.time()
    for name in datasets:
        for p, npairs in grid:
            if jobs == 1:
                for s in range(seeds):
                    rows.extend(one_cell(name, p, s, B, npairs))
            else:
                from joblib import Parallel, delayed
                for chunk in Parallel(n_jobs=jobs)(
                        delayed(one_cell)(name, p, s, B, npairs) for s in range(seeds)):
                    rows.extend(chunk)
            pd.DataFrame(rows).to_csv(OUT, index=False)
            print(f"  done {name} p={p}  ({time.time() - t0:.0f}s)", flush=True)
    analyze(pd.DataFrame(rows))


if __name__ == "__main__":
    main()
