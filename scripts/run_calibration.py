"""exp-021 -- does per-panel calibration give us a stopping rule, i.e. can the method find the
panel SIZE without being told it?

WHY THIS IS THE EXPERIMENT THAT MATTERS
---------------------------------------
The goal is a recursive tree whose every node names a few columns and splits the rows. Every node
has to choose a panel of unknown size. Today we cannot: we enumerate all PAIRS, which only works
because we told the method the answer is a pair, and our scores are not comparable across panel
sizes so "should I add another feature?" has no answer. That is the single thing standing between
"we can rank exact pairs" and "we can build the tree".

exp-018 measured the symptom and deferred the cure to a scramble-calibrated score. This is it. See
`atomicplus/evaluation/calibration.py` for the method and its prior art (it is not novel -- Vinh
et al. DMKD 2016, UMC AAAI 2017, DUSC ICDM 2007 -- and must not be claimed as such).

THREE QUESTIONS, IN ORDER OF HOW MUCH THEY MATTER
-------------------------------------------------
  [1] PEAK-AT-TRUTH. Take the true pair and pad it with 0/1/2/3 junk columns. Does calibrated z
      peak at the true size? Reported next to the RAW score, which cannot answer this at all --
      that contrast is the result. Pre-registered success: z peaks at k=2 on a majority of the
      non-convex shapes, at 20 seeds.

  [2] STOPPING RULE END-TO-END. Start from a single feature and grow while z rises. Does it stop
      at size 2, and is the panel it stops on the true one? This is the capability claim; [1] is
      the mechanism behind it.

  [3] ABSTENTION. Run the same thing on data with NO planted structure (shuffled labels / pure
      junk panels). Does the top calibrated z stay below threshold, so the method would decline to
      split? A tree that cannot decline is confidently misleading, which is the objection Ting
      raised about the first split not being guaranteed correct.

gauss2 is the CONVEX CONTROL and is reported separately, never pooled. It has an enormous signal
under every term and averaging it in has already made one verdict look like a pass when it was not.

    python scripts/run_calibration.py --quick                 # 2 shapes, 3 seeds, B=10, ~5 min
    python scripts/run_calibration.py --seeds 20 --jobs 8     # the real run
    python scripts/run_calibration.py --analyze-only

COST. Calibration multiplies every score evaluation by B. The [1] sweep is small. The [2] growth
run is the expensive one: each step scores (p - |S|) candidate panels x B nulls. Start with
--quick and read the runtime before launching the full one.
"""
from __future__ import annotations

import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atomicplus.evaluation.calibration import calibrate, grow_panel
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

OUT = "results/calibration.csv"
SHAPES = ["moons", "circles", "jain", "spiral"]      # non-convex; gauss2 handled separately
CONVEX_CONTROL = "gauss2"
TERMS = {"density": lambda Z: density_term(Z), "graphcut": lambda Z: graphcut_term(Z)}
BAR = 2.0        # pre-registered: calibrated z below this = "no structure I can defend"


def _load(shape: str, p: int, seed: int):
    """The repaired (structured-junk) benchmark. The old uniform-junk one leaked; never use it.

    Same entry point exp-018 used, so these numbers sit on exactly the same footing as its tables.
    The planted pair is at the fixed indices `INF`.
    """
    from run_method_baselines import INF, load_structured
    X, y = load_structured(shape, p, seed, "structured")
    return X, y, tuple(INF)


def q1_peak_at_truth(X, truth, term, B, seed, max_pad=3):
    """[1] pad the true pair with junk; does calibrated z peak at the true size?"""
    rng = np.random.default_rng(seed)
    others = [j for j in range(X.shape[1]) if j not in truth]
    rows = []
    for pad in range(max_pad + 1):
        extra = tuple(rng.choice(others, size=pad, replace=False)) if pad else ()
        S = tuple(sorted(tuple(truth) + extra))
        r = calibrate(TERMS[term], X, S, B=B, shared_seed=seed)
        rows.append(dict(question="peak_at_truth", term=term, k=len(S), pad=pad,
                         subset=str(S), **r))
    return rows


def q2_stopping_rule(X, truth, term, B, seed, max_size=5):
    """[2] grow from one true feature; where does it stop, and on what?"""
    start = (int(truth[rng_pick(seed, len(truth))]),)
    chosen, trace = grow_panel(TERMS[term], X, start, max_size=max_size, B=B, shared_seed=seed)
    return [dict(question="stopping_rule", term=term, k=t["size"], subset=str(t["subset"]),
                 accepted=t["accepted"], stopped_at=len(chosen),
                 found_truth=int(tuple(sorted(truth)) == tuple(sorted(chosen))),
                 recovered_both=int(set(truth) <= set(chosen)),
                 z=t["z"], raw=t["raw"], null_mean=t["null_mean"], null_sd=t["null_sd"],
                 degenerate=t["degenerate"]) for t in trace]


def q3_abstention(X, truth, term, B, seed, n_draw=30):
    """[3] on panels with NO planted structure, does z stay below the bar?"""
    rng = np.random.default_rng(seed + 9001)
    others = [j for j in range(X.shape[1]) if j not in truth]
    rows = []
    for k in (2, 3):
        for _ in range(n_draw):
            S = tuple(sorted(rng.choice(others, size=k, replace=False)))
            r = calibrate(TERMS[term], X, S, B=B, shared_seed=seed)
            rows.append(dict(question="abstention", term=term, k=k, subset=str(S), **r))
    return rows


def rng_pick(seed, n):
    return np.random.default_rng(seed).integers(n)


def one_cell(shape, p, seed, B, light=False):
    X, _y, truth = _load(shape, p, seed)
    out = []
    for term in TERMS:
        out += q1_peak_at_truth(X, truth, term, B, seed, max_pad=2 if light else 3)
        out += q2_stopping_rule(X, truth, term, B, seed, max_size=3 if light else 5)
        out += q3_abstention(X, truth, term, B, seed, n_draw=6 if light else 30)
    for r in out:
        r.update(dataset=shape, p=p, seed=seed, B=B, truth=str(tuple(truth)))
    return out


def analyze(df):
    pd.set_option("display.width", 200)
    print("\n" + "=" * 78)
    print("exp-021 -- PER-PANEL CALIBRATION")
    print("=" * 78)
    nc = df[df.dataset != CONVEX_CONTROL]

    print("\n[1] PEAK-AT-TRUTH -- true pair padded with junk. Does calibrated z peak at k=2?")
    print("    (raw score shown alongside: it is on an arbitrary per-size scale and CANNOT be")
    print("     compared across k at all, which is the whole reason this experiment exists)")
    q = nc[nc.question == "peak_at_truth"]
    for term, g in q.groupby("term"):
        print(f"\n  --- {term} ---")
        print(g.pivot_table(index="dataset", columns="k", values="z").round(2).to_string())
        print("  raw:")
        print(g.pivot_table(index="dataset", columns="k", values="raw").round(2).to_string())
        peaks = g.loc[g.groupby(["dataset", "seed"]).z.idxmax()]
        rate = (peaks.k == 2).mean()
        print(f"  peaks at k=2 in {rate:.0%} of (shape, seed) cells"
              f"   [pre-registered bar: majority]")

    print("\n[2] STOPPING RULE -- grow from one true feature while z rises.")
    s = nc[nc.question == "stopping_rule"]
    if len(s):
        last = s.groupby(["dataset", "term", "seed"]).tail(1)
        print(last.pivot_table(index="dataset", columns="term",
                               values=["stopped_at", "found_truth", "recovered_both"]
                               ).round(2).to_string())
        print("    stopped_at = final panel size (2 is correct); found_truth = exactly the planted")
        print("    pair; recovered_both = contains both true features, possibly plus junk")

    print(f"\n[3] ABSTENTION -- junk-only panels. Fraction with z above the bar ({BAR}) is the")
    print("    false-split rate; it should be small, and IS the abstention claim.")
    a = nc[nc.question == "abstention"]
    if len(a):
        tbl = a.assign(over=(a.z > BAR).astype(float)).pivot_table(
            index="dataset", columns="term", values="over")
        print(tbl.round(3).to_string())
        print(f"    overall false-split rate: {(a.z > BAR).mean():.3f}")
        t = nc[nc.question == "peak_at_truth"]
        print(f"    for contrast, true panels above the bar: {(t.z > BAR).mean():.3f}")

    cc = df[df.dataset == CONVEX_CONTROL]
    if len(cc):
        print(f"\n[convex control {CONVEX_CONTROL}, reported separately, NEVER pooled]")
        print(cc[cc.question == "peak_at_truth"].pivot_table(
            index="term", columns="k", values="z").round(2).to_string())

    deg = df.degenerate.fillna(0).mean() if "degenerate" in df else 0.0
    print(f"\n  null-sd floor fired on {deg:.1%} of panels"
          f"{'  <- INVESTIGATE, z is unreliable there' if deg > 0.02 else ''}")


def main():
    args = list(sys.argv[1:])
    if "--analyze-only" in args:
        analyze(pd.read_csv(OUT)); return
    seeds, ps, B, jobs, light = 20, [20, 40], 30, 1, False
    shapes = SHAPES + [CONVEX_CONTROL]
    if "--quick" in args:
        args.remove("--quick"); seeds, ps, B, shapes, light = 2, [12], 5, ["moons"], True
    for flag in ("--seeds", "--B", "--jobs"):
        if flag in args:
            i = args.index(flag); v = int(args[i + 1]); del args[i:i + 2]
            seeds = v if flag == "--seeds" else seeds
            B = v if flag == "--B" else B
            jobs = v if flag == "--jobs" else jobs

    cells = [(sh, p, sd) for sh in shapes for p in ps for sd in range(seeds)]
    print(f"{len(cells)} cells (shape x p x seed), B={B}", flush=True)
    os.makedirs("results", exist_ok=True)
    t0 = time.time()
    if jobs == 1:
        rows = [r for c in cells for r in one_cell(*c, B, light)]
    else:
        from joblib import Parallel, delayed
        rows = [r for blk in Parallel(n_jobs=jobs)(delayed(one_cell)(*c, B, light) for c in cells)
                for r in blk]
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(df)} rows, {time.time() - t0:.0f}s)")
    analyze(df)


if __name__ == "__main__":
    main()
