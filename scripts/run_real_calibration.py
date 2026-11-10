"""exp-022 -- the decisive experiment: does our UNSUPERVISED score find, on real data, the panels
that the label-using oracle says exist?

WHY THIS IS THE ONE THAT MATTERS
--------------------------------
`run_panel_size.py` established the ceiling on METABRIC using the labels: on HER2-vs-luminal an
eight-gene panel reaches ARI 0.744, against 0.213 for all 250 features and 0.181 for the published
50-gene PAM50 panel. So a small panel exists and it is worth +0.53 ARI over using everything. That
is a statement about the DATA.

This script asks the only question that is about our METHOD: **starting from nothing, with no
labels, does the search land anywhere near that ceiling, and does it stop at the right size?**

It is also the first time the whole pipeline runs end to end without being told the answer's size.
Everything before this enumerated pairs, which only works because we told it the answer was a pair.

THE ALGORITHM, STAGES 0-2
-------------------------
  Stage 0  Calibrated z for every single feature. Cost p x B. Maps which features carry individual
           signal WITHOUT committing to them.
  Stage 1  Seed on two channels, and the second one is the point:
             Channel A -- pairs among the TOP-scoring singletons. Cheap, and it catches everything
                          where individual signal exists. On METABRIC that is most of it.
             Channel B -- a sample of pairs among the LOW-scoring singletons. The only place a
                          jointly-necessary panel can live. Channel A will never look there, and
                          neither will any bottom-up method that prunes by downward closure.
           Keeping B is a design choice we should defend in the paper, not an afterthought.
  Stage 2  Grow each seed while calibrated z rises; stop when it falls. Panel size is DISCOVERED.

WHAT IS REPORTED, AND WHAT WOULD COUNT AS SUCCESS
-------------------------------------------------
For each seed: the panel it stopped on, that panel's size, and that panel's ARI -- next to the
label-using greedy oracle at the SAME size. Success is not matching the oracle; it is landing much
closer to the oracle than to the no-selection floor. Concretely, on HER2-vs-luminal the floor is
0.213 and the k=8 ceiling is 0.744, so a stopped panel scoring 0.5+ would be a real result and one
scoring 0.25 would not.

Also reported: how often the search stops at a size where a BETTER panel of that size existed
(a search failure) versus stopping at a size where nothing better existed (a data limit). Those
are different problems and the paper needs to say which one we have.

    python scripts/run_real_calibration.py --dataset levine --jobs 4    # 496 pairs: search vs
                                                                        # enumeration, head to head
    python scripts/run_real_calibration.py --quick                              # 1 contrast, tiny
    python scripts/run_real_calibration.py --contrast her2_luminal --jobs 8
    python scripts/run_real_calibration.py --jobs 8 --B 20 --seeds-a 5 --seeds-b 5

COST WARNING. Calibration multiplies every score by B, and growth scores (p - |S|) candidates per
step. At p=250, B=20 that is 5,000 evaluations per growth step per seed. START WITH --quick AND
READ THE PRINTED TIMING before launching the full run. If it is too slow, cut `--seeds-b` first
(Channel B is the expensive, low-yield half) and `--B` second.
"""
from __future__ import annotations

import itertools
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.cluster import KMeans

from atomicplus.datasets.pam50 import PAM50, canonical
from atomicplus.datasets.real import LEVINE_CONTRASTS, LOADERS, load_metabric
from atomicplus.evaluation import metrics
from atomicplus.evaluation.calibration import (calibrate, chosen_entry, grow_from_pairs,
                                               grow_panel)
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

OUT = "results/real_calibration.csv"
# DENSITY FIRST, DELIBERATELY. exp-021 measured which term can drive a calibrated search: density
# peaks at the true panel size in 80% of cells (passing the pre-registered majority bar) while
# graph-cut manages 52%, and on jain graph-cut's calibrated z INCREASES monotonically as junk is
# added -- it actively prefers a padded panel. Graph-cut is kept here only as a contrast; do not
# read a graph-cut-driven search as a fair test of the method.
TERMS = {"density": density_term, "graphcut": graphcut_term,
         # ARM: identical statistic, locally-scaled affinity instead of binary kNN. Run it beside
         # "graphcut", never instead of it -- numbers from the two are not comparable to the
         # existing tables and the point is the difference between them.
         "graphcut_st": lambda Z: graphcut_term(Z, affinity="selftuning")}
BAR = 2.0     # pre-registered abstention threshold, same as exp-021


def ari_of(X, y, cols, seed=0):
    return float(metrics.ari(y, KMeans(2, n_init=10, random_state=seed)
                             .fit_predict(X[:, list(cols)])))


def greedy_ceiling(X, y, max_k, seed=0):
    """ORACLE, uses labels. The ceiling our unsupervised search is measured against, per size."""
    chosen, out, rem = [], {}, list(range(X.shape[1]))
    for _ in range(max_k):
        a, j = max((ari_of(X, y, chosen + [j], seed), j) for j in rem)
        chosen.append(j); rem.remove(j); out[len(chosen)] = a
    return out


def run(contrast, term, n_rows, B, seeds_a, seeds_b, max_size, seed, max_greedy,
        b_screen=5, pool_top=50, pool_low=20, dataset="metabric", seeding="both",
        max_pairs=6000):
    # Loaders disagree on what the "which question" argument is called: metabric and levine take
    # `contrast`, mice and har take `label`, madelon takes neither. Dispatch on the signature
    # rather than hardcoding -- guessing here is what raised
    # "load_mice() got an unexpected keyword argument 'contrast'".
    import inspect
    _params = inspect.signature(LOADERS[dataset]).parameters
    _kw = {}
    if contrast is not None:
        if "contrast" in _params:
            _kw["contrast"] = contrast
        elif "label" in _params:
            _kw["label"] = contrast
        else:
            raise ValueError(f"{dataset} takes no contrast/label argument; drop --contrast")
    X, y, names = LOADERS[dataset](n=n_rows, seed=seed, **_kw)
    p = X.shape[1]
    # The "known panel" differs by dataset. METABRIC has PAM50 (a 50-gene 5-way classifier, so a
    # loose reference). Levine has the PUBLISHED TWO-MARKER GATE for each contrast -- a true
    # answer key at panel level, which is what makes it the sharper test.
    # A "known panel" only exists for two datasets. For mice, har and madelon there is none, and
    # matching PAM50 gene symbols against protein or sensor names would silently invent one.
    if dataset == "levine":
        panel = {names.index(m) for m in LEVINE_CONTRASTS[contrast]["true_panel"] if m in names}
    elif dataset == "metabric":
        panel = {j for j, nm in enumerate(names) if canonical(nm) in {canonical(g) for g in PAM50}}
    else:
        panel = set()
    fn = TERMS[term]
    t0 = time.time()

    print(f"\n### {contrast} / {term}   n={len(X)}  p={p}", flush=True)
    floor = ari_of(X, y, range(p))
    ceil = greedy_ceiling(X, y, max_greedy, seed)
    print(f"  floor (all {p} features, no selection) ARI {floor:.3f}")
    print(f"  oracle ceiling by size: " + "  ".join(f"k={k}:{v:.3f}" for k, v in ceil.items()),
          flush=True)

    # ---- Stage 0: calibrated z for every singleton -------------------------------------------
    # Cheap B here (b_screen): stage 0 only has to ORDER the singletons, not report them.
    singles = np.array([calibrate(fn, X, (j,), B=b_screen, shared_seed=seed)["z"] for j in range(p)])
    singles = np.nan_to_num(singles, nan=-np.inf)
    order = np.argsort(-singles)
    print(f"  stage 0 done ({time.time() - t0:.0f}s, B={b_screen}). top singletons by calibrated z: " +
          ", ".join(f"{names[j]} {singles[j]:.1f}" for j in order[:5]), flush=True)

    # ---- Stage 1: seed on two channels --------------------------------------------------------
    rng = np.random.default_rng(seed)
    top = list(order[:max(4, seeds_a)])
    low = list(order[-max(20, seeds_b * 4):])
    seeds = ([("A", (int(top[i]),)) for i in range(min(seeds_a, len(top)))] +
             [("B", (int(rng.choice(low)),)) for _ in range(seeds_b)])
    # Growth shortlist, recorded because it is a search decision: the pool_top best singletons
    # plus pool_low drawn from the rest, so Channel B seeds still have somewhere to grow into.
    rest = [int(j) for j in order[pool_top:]]
    pool = sorted(set(int(j) for j in order[:pool_top]) |
                  set(int(j) for j in rng.choice(rest, size=min(pool_low, len(rest)),
                                                 replace=False)))
    steps = max_size - 1
    print(f"  growth pool {len(pool)} of {p} features; ~{len(pool) * B * steps * len(seeds)} "
          f"scored panels ahead", flush=True)

    # ---- Stage 2: grow with the stopping rule -------------------------------------------------
    rows = []

    def record(channel, seed_label, chosen, trace):
        a = ari_of(X, y, chosen); k = len(chosen); c_k = ceil.get(k, np.nan)
        # z OF THE CHOSEN PANEL. `trace[-1]` is the REJECTED extension whenever growth stopped
        # because z fell -- i.e. on exactly the runs that stopped for the principled reason -- so
        # reading it under-reported z and over-reported abstention. See calibration.chosen_z and
        # CORRECTIONS C10. `z_last` keeps the old number so the two can be compared.
        e = chosen_entry(trace) or {}
        z = float(e.get("z", np.nan))
        rows.append(dict(contrast=contrast, term=term, channel=channel, seed_feature=seed_label,
                         stopped_at=k, panel=str(tuple(names[j] for j in chosen)),
                         z=z, z_last=trace[-1]["z"] if trace else np.nan,
                         degenerate=float(e.get("degenerate", np.nan)),
                         ari=a, oracle_at_same_k=c_k, floor=floor, n=len(X), p=p, B=B,
                         frac_of_ceiling=(a - floor) / max(abs(c_k - floor), 1e-3),
                         pool_size=len(pool), b_screen=b_screen, seeding=channel[0],
                         dataset=dataset, n_true_panel=len(panel),
                         in_pam50=len(set(chosen) & panel),
                         hit_cap=int(k >= max_size),
                         abstain=int((z if np.isfinite(z) else 0) < BAR)))
        print(f"    [{channel}] {seed_label:<22s} -> k={k}  ARI {a:.3f}  "
              f"(oracle@k {c_k:.3f}, floor {floor:.3f})  z={z:.1f}"
              f"{'  ABSTAIN' if rows[-1]['abstain'] else ''}"
              f"{'  HIT-CAP' if rows[-1]['hit_cap'] else ''}", flush=True)

    # PAIR SEEDING. Seeds are the top pairs by the RAW score; the calibrated z is used only for
    # the stopping rule. Singleton seeding assumes a good panel contains a good single feature --
    # the downward-closure assumption we criticise bottom-up methods for -- and it is measurably
    # what broke the search: raw graph-cut ranks Levine's (CD4, CD8) at 5 of 496 while neither
    # marker alone is a standout, so no singleton seed ever starts there.
    if seeding in ("pairs", "both"):
        allp = list(itertools.combinations(range(p), 2))
        if len(allp) > max_pairs:
            sel = rng.choice(len(allp), size=max_pairs, replace=False)
            allp = [allp[i] for i in sorted(sel)]
            print(f"  pair seeding: SAMPLED {len(allp)} of {p*(p-1)//2} pairs "
                  f"(not silent truncation)", flush=True)
        else:
            print(f"  pair seeding: scanning all {len(allp)} pairs with the raw score", flush=True)
        for r in grow_from_pairs(fn, X, n_seeds=seeds_a + seeds_b, max_size=max_size, B=B,
                                 shared_seed=seed, pool=pool, pair_pool=allp):
            record(f"P{r['seed_raw_rank']}",
                   f"{names[r['seed_pair'][0]]},{names[r['seed_pair'][1]]}",
                   list(r["panel"]), r["trace"])

    if seeding == "pairs":
        print(f"  total {time.time() - t0:.0f}s", flush=True)
        return rows

    for channel, s0 in seeds:
        chosen, trace = grow_panel(fn, X, s0, max_size=max_size, B=B, shared_seed=seed, pool=pool)
        record(channel, names[s0[0]], chosen, trace)
    print(f"  total {time.time() - t0:.0f}s", flush=True)
    return rows


def analyze(df):
    pd.set_option("display.width", 200)
    print("\n" + "=" * 78)
    print("exp-022 -- UNSUPERVISED SEARCH ON REAL DATA vs THE LABEL-USING CEILING")
    print("=" * 78)
    for (c, t), g in df.groupby(["contrast", "term"]):
        best = g.loc[g.ari.idxmax()]
        print(f"\n### {c} / {t}   floor {g.floor.iloc[0]:.3f}")
        print(f"  best stopped panel: k={best.stopped_at}  ARI {best.ari:.3f}  "
              f"(oracle at k={best.stopped_at}: {best.oracle_at_same_k:.3f})")
        print(f"  fraction of the achievable gain captured: {best.frac_of_ceiling:.1%}")
        print(f"  panel: {best.panel}")
        print(f"  stopped sizes across seeds: {sorted(g.stopped_at.tolist())}")
        print(f"  abstained on {int(g.abstain.sum())} of {len(g)} seeds")
        if "seeding" in g:
            print("  --- by seeding arm (P = pair-seeded, A/B = singleton channels) ---")
            for arm, gg in g.groupby("seeding"):
                nm = {"P": "pairs", "A": "singleton-top", "B": "singleton-low"}.get(arm, arm)
                print(f"    {nm:15s} best ARI {gg.ari.max():.3f}  median {gg.ari.median():.3f}"
                      f"  sizes {sorted(gg.stopped_at.tolist())}"
                      f"  hit-cap {int(gg.hit_cap.sum())}/{len(gg)}")
            print("    hit-cap counts runs that stopped only because max_size was reached --")
            print("    those do NOT test the stopping rule, they test seeding. Raise --max-size.")
    print("\n  frac_of_ceiling = (our ARI - floor) / (oracle ARI at the same size - floor).")
    print("  1.0 means we matched what the labels could achieve at that panel size; 0 means")
    print("  selection bought nothing over using every feature. The oracle is a diagnostic, not")
    print("  a competitor -- it cannot run without the answer.")


def main():
    args = list(sys.argv[1:])
    if "--analyze-only" in args:
        analyze(pd.read_csv(OUT)); return
    dataset, seeding, max_pairs = "metabric", "both", 6000
    if "--seeding" in args:
        i = args.index("--seeding"); seeding = args[i + 1]; del args[i:i + 2]
        if seeding not in ("pairs", "singleton", "both"):
            sys.exit("--seeding must be pairs | singleton | both")
    if "--max-pairs" in args:
        i = args.index("--max-pairs"); max_pairs = int(args[i + 1]); del args[i:i + 2]
    if "--dataset" in args:
        i = args.index("--dataset"); dataset = args[i + 1]; del args[i:i + 2]
    contrasts = (sorted(LEVINE_CONTRASTS) if dataset == "levine"
                 else ["her2_luminal", "claudinlow_basal", "basal_luminal", "lumA_lumB"]
                 if dataset == "metabric" else [None])
    terms, n_rows, B, sa, sb, max_size, seed, jobs, max_greedy = \
        ["density", "graphcut"], 300, 20, 4, 2, 6, 0, 1, 8
    if "--quick" in args:
        args.remove("--quick")
        contrasts, terms, B, sa, sb, max_size, max_greedy = \
            [contrasts[0]], ["density"], 5, 2, 1, 3, 4
        n_rows = 200
    if "--contrast" in args:
        i = args.index("--contrast"); contrasts = [args[i + 1]]; del args[i:i + 2]
    if "--term" in args:
        i = args.index("--term"); terms = [args[i + 1]]; del args[i:i + 2]
    bs, ptop, plow = 5, 50, 20
    for flag in ("--n", "--B", "--seeds-a", "--seeds-b", "--max-size", "--jobs", "--max-greedy",
                 "--b-screen", "--pool-top", "--pool-low"):
        if flag in args:
            i = args.index(flag); v = int(args[i + 1]); del args[i:i + 2]
            n_rows = (None if v <= 0 else v) if flag == "--n" else n_rows
            B = v if flag == "--B" else B
            sa = v if flag == "--seeds-a" else sa
            sb = v if flag == "--seeds-b" else sb
            max_size = v if flag == "--max-size" else max_size
            jobs = v if flag == "--jobs" else jobs
            max_greedy = v if flag == "--max-greedy" else max_greedy
            bs = v if flag == "--b-screen" else bs
            ptop = v if flag == "--pool-top" else ptop
            plow = v if flag == "--pool-low" else plow

    cells = [(c, t) for c in contrasts for t in terms]
    os.makedirs("results", exist_ok=True)
    t0 = time.time()
    if jobs == 1:
        rows = [r for c, t in cells for r in run(c, t, n_rows, B, sa, sb, max_size, seed,
                                                 max_greedy, bs, ptop, plow, dataset, seeding,
                                                 max_pairs)]
    else:
        from joblib import Parallel, delayed
        rows = [r for blk in Parallel(n_jobs=min(jobs, len(cells)))(
            delayed(run)(c, t, n_rows, B, sa, sb, max_size, seed, max_greedy, bs, ptop, plow,
                         dataset, seeding, max_pairs) for c, t in cells)
            for r in blk]
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {OUT} ({len(df)} rows, {time.time() - t0:.0f}s)")
    analyze(df)


if __name__ == "__main__":
    main()
