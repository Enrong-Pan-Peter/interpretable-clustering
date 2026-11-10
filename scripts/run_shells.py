"""exp-026 -- the first testbed whose right answer is a panel of THREE features.

WHY
---
Every dataset this project has used has a two-feature answer. The synthetic shapes plant pairs;
Levine's published gates are two-marker; METABRIC is the one place where more features genuinely
help and it is the one place the search fails for an unrelated reason (overlapping rather than
separated populations, exp-022). So "can the method pick a panel bigger than two when that IS the
right answer" has never been asked. Not asked and failed -- never asked. Until that is fixed we
cannot say anything about panels of three or more, in the paper or anywhere else.

THE DATA
--------
Three concentric spherical shells, embedded in three of `p` columns, the rest junk. Radius
separates the shells perfectly and radius needs all three coordinates at once.

The honest caveat is built into the measurement rather than hidden. The shadow of a sphere is a
filled disc with a bright rim, so a two-feature view of three shells is three rings on overlapping
backgrounds -- degraded structure, not absent structure. A structure whose two-dimensional views
carry literally nothing is a parity function, and that family is provably intractable (exp-023 sec.
2). So the test is not "the best pair scores zero". The test is:

    STAGE 1 (about the DATA, uses labels)   how big is the gap between the best possible two-feature
                                            clustering and the true three-feature one?
    STAGE 2 (about the METHOD, no labels)   given that gap, does the search choose three features,
                                            and does it choose the right three?

Stage 1 has to run first and has to print a real gap, or stage 2 is meaningless. If the best pair
already reaches the triple's score, the dataset does not test what it claims and nothing about the
method can be concluded from it.

WHAT THE NUMBERS MEAN
---------------------
  ARI       Adjusted Rand Index: agreement between a clustering and the true shell labels.
            1.0 is exact, 0.0 is what random guessing gets.
  best pair the highest ARI reachable by ANY two of the p columns, found by trying all of them
            with the labels in hand. Not something the method computes -- it is the bar.
  chosen    what the unsupervised search picks when it is shown the columns and nothing else.

    python scripts/run_shells.py --quick                       # p=12, n=300, seconds
    python scripts/run_shells.py --jobs 8                      # the real run
    python scripts/run_shells.py --jobs 8 --sweep              # vary shell thickness
    python scripts/run_shells.py --jobs 8 --noise uniform      # older embedding, for comparison
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

from sklearn.cluster import SpectralClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import kneighbors_graph

from atomicplus.datasets.synthetic import shells_subspace
from atomicplus.evaluation.calibration import grow_from_pairs
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

OUT = "results/shells.csv"
TERMS = {"graphcut": graphcut_term, "density": density_term}


def ari_k(X: np.ndarray, y: np.ndarray, cols, k: int, seed: int = 0) -> float:
    """Cluster the given columns into k groups and score against the shell labels.

    Spectral clustering on a k-nearest-neighbour graph, NOT k-means: concentric shells have no
    useful centroids, so a centroid method would report failure for the wrong reason and tell us
    nothing about whether the columns carry the structure.
    """
    Z = X[:, list(cols)]
    A = kneighbors_graph(Z, n_neighbors=min(10, len(Z) - 1), mode="connectivity")
    A = 0.5 * (A + A.T).toarray()
    try:
        lab = SpectralClustering(n_clusters=k, affinity="precomputed",
                                 random_state=seed).fit_predict(A)
    except Exception:  # noqa: BLE001
        return float("nan")
    return float(adjusted_rand_score(y, lab))


def stage1(X, y, info, k, jobs):
    """What the DATA allows. Uses labels throughout -- this is the bar, not a result."""
    p = X.shape[1]
    singles = [(ari_k(X, y, [j], k), (j,)) for j in range(p)]
    pairs = list(itertools.combinations(range(p), 2))
    if jobs != 1:
        from joblib import Parallel, delayed
        pv = Parallel(n_jobs=jobs)(delayed(ari_k)(X, y, s, k) for s in pairs)
    else:
        pv = [ari_k(X, y, s, k) for s in pairs]
    pr = sorted(zip(pv, pairs), key=lambda t: -np.nan_to_num(t[0], nan=-1))
    triples = list(itertools.combinations(range(p), 3))
    if jobs != 1:
        from joblib import Parallel, delayed
        tv = Parallel(n_jobs=jobs)(delayed(ari_k)(X, y, s, k) for s in triples)
    else:
        tv = [ari_k(X, y, s, k) for s in triples]
    tr = sorted(zip(tv, triples), key=lambda t: -np.nan_to_num(t[0], nan=-1))
    true_t = ari_k(X, y, info, k)
    best_s = max(singles, key=lambda t: np.nan_to_num(t[0], nan=-1))
    return dict(best_single=best_s[0], best_single_cols=best_s[1],
                best_pair=pr[0][0], best_pair_cols=pr[0][1],
                best_triple=tr[0][0], best_triple_cols=tr[0][1],
                true_triple=true_t,
                best_pair_is_informative=set(pr[0][1]) <= set(info),
                best_triple_is_true=set(tr[0][1]) == set(info),
                pair_ranking=pr[:5], all_features=ari_k(X, y, range(p), k))


def stage2(X, y, info, term, k, cfg):
    """What the METHOD finds. No labels anywhere in the search; ARI is computed afterwards."""
    fn = TERMS[term]
    res = grow_from_pairs(fn, X, n_seeds=cfg["seeds"], max_size=cfg["max_size"],
                          B=cfg["B"], shared_seed=0, n_jobs=cfg["jobs"])
    rows = []
    for r in res:
        panel = list(r["panel"])
        rows.append(dict(term=term, seed_rank=r["seed_raw_rank"],
                         seed_pair=tuple(r["seed_pair"]), panel=tuple(panel), size=len(panel),
                         z=round(float(r["z"]), 2) if np.isfinite(r["z"]) else np.nan,
                         ari=ari_k(X, y, panel, k),
                         n_informative_in_panel=len(set(panel) & set(info)),
                         found_exactly=set(panel) == set(info)))
    return rows


def one(cfg, thickness, noise, log):
    rng = np.random.default_rng(cfg["seed"])
    df, y, info = shells_subspace(n=cfg["n"], p=cfg["p"], n_shells=cfg["shells"],
                                  thickness=thickness, noise=noise, rng=rng)
    X = df.to_numpy()
    k = cfg["shells"]
    log(f"\n### thickness {thickness}  noise {noise}  n={len(X)} p={X.shape[1]} "
        f"shells={k}  informative dims {info}")

    t0 = time.time()
    s1 = stage1(X, y, info, k, cfg["jobs"])
    gap = s1["true_triple"] - s1["best_pair"]
    log(f"  STAGE 1, what the data allows (labels used):")
    log(f"    best single feature   ARI {s1['best_single']:.3f}  {s1['best_single_cols']}")
    log(f"    best PAIR of features ARI {s1['best_pair']:.3f}  {s1['best_pair_cols']}"
        f"   {'(both informative)' if s1['best_pair_is_informative'] else '(includes junk)'}")
    log(f"    the TRUE triple       ARI {s1['true_triple']:.3f}  {tuple(info)}")
    log(f"    best triple found     ARI {s1['best_triple']:.3f}  {s1['best_triple_cols']}"
        f"   {'= the true one' if s1['best_triple_is_true'] else '!= the true one'}")
    log(f"    all {X.shape[1]} features    ARI {s1['all_features']:.3f}")
    log(f"    --> GAP (true triple - best pair) = {gap:+.3f}   "
        f"{'USABLE TESTBED' if gap > 0.20 else 'NOT A USABLE TESTBED: a pair does nearly as well'}")

    rows = []
    if s1["true_triple"] < 0.60:
        log("    !! The TRUE three-column view itself scores low. That is UNDERSAMPLING, not a")
        log("       property of the method: a sphere of radius r with m points has neighbour")
        log(f"       spacing ~2r*sqrt(pi/m), and at n={len(X)} that spacing is not comfortably")
        log("       below the gap between shells. Raise --n (measured: 600 works for 2 shells,")
        log("       1500 for 3) before reading anything else on this line.")
        return [], s1, gap
    if gap <= 0.20:
        log("    Skipping stage 2: with this gap the dataset cannot distinguish a method that")
        log("    picks three features from one that picks two, so running the search proves nothing.")
    else:
        for term in cfg["terms"]:
            log(f"  STAGE 2, what the search finds with {term} (no labels):")
            for r in stage2(X, y, info, term, k, cfg):
                r.update(thickness=thickness, noise=noise, gap=gap, n=len(X), p=X.shape[1],
                         best_pair=s1["best_pair"], true_triple=s1["true_triple"])
                rows.append(r)
                log(f"    seed {r['seed_rank']}: chose {r['size']} features {r['panel']}  "
                    f"ARI {r['ari']:.3f}  ({r['n_informative_in_panel']}/3 informative"
                    f"{', EXACT' if r['found_exactly'] else ''})")
    log(f"  {time.time() - t0:.0f}s")
    return rows, s1, gap


def main():
    a = list(sys.argv[1:])
    cfg = dict(n=1500, p=12, shells=3, seeds=5, max_size=4, B=15, jobs=1, seed=0)
    noise = "matched"
    if "--noise" in a:
        i = a.index("--noise"); noise = a[i + 1]; del a[i:i + 2]
    sweep = "--sweep" in a
    if sweep:
        a.remove("--sweep")
    if "--quick" in a:
        a.remove("--quick"); cfg.update(n=600, p=12, shells=2, seeds=3, max_size=4, B=6)
    cfg["terms"] = ["graphcut", "density"]
    if "--term" in a:
        i = a.index("--term"); cfg["terms"] = [a[i + 1]]; del a[i:i + 2]
    for k in list(cfg):
        if k == "terms":
            continue
        for f in (f"--{k}", f"--{k.replace('_', '-')}"):
            if f in a:
                i = a.index(f); cfg[k] = int(a[i + 1]); del a[i:i + 2]
                break
    if a:
        print(f"unrecognised arguments: {a}"); sys.exit(2)

    log = lambda s: print(s, flush=True)  # noqa: E731
    log(f"exp-026 -- concentric spherical shells, a three-feature answer\nconfig {cfg}")
    thicknesses = [0.05, 0.10, 0.20, 0.35] if sweep else [0.10]
    allrows = []
    for th in thicknesses:
        rows, s1, gap = one(cfg, th, noise, log)
        allrows.extend(rows)

    os.makedirs("results", exist_ok=True)
    if allrows:
        df = pd.DataFrame(allrows)
        df.to_csv(OUT, index=False)
        log(f"\nwrote {OUT}")
        log("\n" + "=" * 90 + "\nDID THE SEARCH TAKE THE THREE-FEATURE PANEL?\n" + "=" * 90)
        g = df.groupby(["thickness", "term"]).agg(
            best_ari=("ari", "max"), median_size=("size", "median"),
            picked_3plus=("size", lambda s: int((s >= 3).sum())), seeds=("size", "size"),
            exact=("found_exactly", "sum"),
            mean_informative=("n_informative_in_panel", "mean"),
            best_pair=("best_pair", "first"), true_triple=("true_triple", "first"))
        print(g.to_string())
        log("\n  picked_3plus counts seeds whose final panel had 3+ features. `exact` counts seeds")
        log("  that landed on exactly the three informative columns. Compare best_ari against")
        log("  best_pair: beating it is the only evidence that a bigger panel was actually used.")
    else:
        log("\nNo stage-2 rows: no thickness setting produced a usable gap. The construction needs")
        log("adjusting before it can test anything -- see the stage 1 numbers above.")


if __name__ == "__main__":
    main()
