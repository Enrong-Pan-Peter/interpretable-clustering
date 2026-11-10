"""exp-023 -- how many candidate pairs do we actually have to look at? Measuring the basin.

THE ARGUMENT THIS EXISTS TO SUPPORT
-----------------------------------
Every selection result in this project came from enumerating all C(p,2) pairs. That does not scale
and it is the reason we cannot move to higher-dimensional data or to panels of more than two
features. The usual response is "make the search smarter", but our own results point somewhere
simpler and more defensible.

Seed-and-grow does not need the BEST pair. It needs ANY pair from which growth climbs to a good
panel. On Levine CD4T-vs-CD8T, growth from each of the top five raw-scored pairs reached ARI >=
0.952, and 32 of 496 pairs already exceed ARI 0.5 unaided. If a fraction f of pairs lie in that
basin, then sampling s pairs at random finds one with probability 1 - (1-f)^s. At f = 0.065, fifty
draws give 96%.

So the cost of search is set by **1/f, not by p^2** -- and f is a measurable property of a dataset,
not an assumption. This script measures it, with an honest confidence interval, so it can be
reported next to every result rather than hand-waved.

WHAT IS MEASURED
----------------
  [1] BASIN FRACTION f. Draw `--probe` pairs uniformly at random. Grow each one with the real,
      unsupervised search. Count how many reach `--success` x (the label-using ceiling). f is that
      hit rate, with a Wilson interval because `--probe` is small. Reported alongside the number of
      random draws needed for 95% and 99% success.

  [2] THE NAIVE PROXY, for contrast. The fraction of pairs that ALREADY score above the bar before
      any growth. This is what people usually mean by "how many good pairs are there", and it
      UNDERSTATES the basin, because growth rescues mediocre seeds. Reporting both shows how much
      the growth step is worth.

  [3] SCREEN FIDELITY. Does scoring on a row subsample preserve the ranking? Spearman between the
      screen score at `--n-screen` rows and the full score, plus whether the full-resolution winner
      survived the screen cut. Two-resolution scanning is only legitimate if this holds, and it has
      to be checked per dataset rather than assumed.

The ceiling and the ARI of grown panels USE LABELS. They are measurement instruments, never part of
the search, and the search never sees them.

    python scripts/run_basin.py --dataset levine --contrast cd4t_cd8t --probe 30
    python scripts/run_basin.py --dataset mice --contrast Behavior --n 0 --probe 30
    python scripts/run_basin.py --dataset madelon --probe 20 --max-pairs 8000
"""
from __future__ import annotations

import inspect
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

from atomicplus.datasets.real import LOADERS
from atomicplus.evaluation import metrics
from atomicplus.evaluation.calibration import basin_fraction, grow_panel, two_resolution_scan
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

OUT = "results/basin.csv"
TERMS = {"graphcut": graphcut_term, "density": density_term}


def load(dataset, contrast, n_rows, seed):
    params = inspect.signature(LOADERS[dataset]).parameters
    kw = {}
    if contrast is not None:
        kw["contrast" if "contrast" in params else "label"] = contrast
    return LOADERS[dataset](n=n_rows, seed=seed, **kw)


def main():
    a = list(sys.argv[1:])
    cfg = dict(dataset="levine", contrast=None, term="graphcut", n=300, probe=30,
               max_pairs=6000, max_size=6, B=20, success=0.8, n_screen=150, seed=0, pool=40)
    for k in list(cfg):
        f = f"--{k.replace('_', '-')}"
        if f in a:
            i = a.index(f); v = a[i + 1]; del a[i:i + 2]
            cfg[k] = v if k in ("dataset", "contrast", "term") else (
                float(v) if k == "success" else int(v))
    if cfg["n"] <= 0:
        cfg["n"] = None

    X, y, names = load(cfg["dataset"], cfg["contrast"], cfg["n"], cfg["seed"])
    p = X.shape[1]
    fn = TERMS[cfg["term"]]
    ari = lambda c: float(metrics.ari(  # noqa: E731
        y, KMeans(2, n_init=10, random_state=0).fit_predict(X[:, list(c)])))

    print(f"\n### {cfg['dataset']}/{cfg['contrast']} term={cfg['term']}  n={len(X)} p={p}",
          flush=True)
    allp = list(itertools.combinations(range(p), 2))
    rng = np.random.default_rng(cfg["seed"])
    if len(allp) > cfg["max_pairs"]:
        sel = rng.choice(len(allp), size=cfg["max_pairs"], replace=False)
        allp = [allp[i] for i in sorted(sel)]
        print(f"  SAMPLED {len(allp)} of {p*(p-1)//2} pairs (not silent truncation)", flush=True)

    # ceiling: best ARI any single pair achieves, as the yardstick for "good"
    t0 = time.time()
    pair_ari = np.array([ari(s) for s in allp])
    ceiling = float(pair_ari.max())
    bar = cfg["success"] * ceiling
    print(f"  pair ceiling ARI {ceiling:.3f} ({names[allp[int(np.argmax(pair_ari))][0]]},"
          f"{names[allp[int(np.argmax(pair_ari))][1]]});  success bar {bar:.3f}"
          f"   [{time.time()-t0:.0f}s]", flush=True)

    # [2] naive proxy -- pairs already above the bar, before any growth
    naive = float((pair_ari >= bar).mean())
    print(f"  [2] pairs already above the bar WITHOUT growth: {naive:.3%}", flush=True)

    # [1] the basin
    # GROWTH SHORTLIST. Without it, every growth step scores all p features x B nulls: at p=500
    # that is ~10,000 evaluations per step, seven steps, twenty-five probes -- about 55 hours,
    # which is exactly what the first Madelon attempt cost. The shortlist is a search decision and
    # is recorded in the output so it cannot pass as an implementation detail.
    scr = np.array([fn(X[:, [j]])[0] for j in range(p)], dtype=float)
    pool = sorted(int(j) for j in np.argsort(-np.nan_to_num(scr, nan=-np.inf))[:cfg["pool"]])
    print(f"  growth shortlist: {len(pool)} of {p} features (top by raw single-feature score)",
          flush=True)

    def grow(pair):
        return grow_panel(fn, X, pair, max_size=cfg["max_size"], B=cfg["B"],
                          shared_seed=cfg["seed"],
                          pool=sorted(set(pool) | {int(j) for j in pair}))[0]

    b = basin_fraction(grow, ari, allp, n_probe=cfg["probe"], success=cfg["success"],
                       ceiling=ceiling, seed=cfg["seed"])
    if b.get("aborted"):
        print(f"  [1] ABORTED: {b['aborted']}")
        print("      Report this dataset as having no pair-level signal. That is a finding about")
        print("      the DATA, not about our method -- it is the k-junta case the hardness result")
        print("      describes, and seed-and-grow provably cannot start from pairs there.")
        sys.exit(0)
    print(f"  [1] BASIN FRACTION f = {b['basin_fraction']:.3%}  "
          f"(95% CI {b['ci_low']:.1%}-{b['ci_high']:.1%}, {b['hits']}/{b['n_probe']} probes)")
    print(f"      random pairs needed: {b['draws_for_95pct']} for 95% success, "
          f"{b['draws_for_99pct']} for 99%")
    print(f"      mean ARI of grown panels {b['mean_grown_ari']:.3f}")
    lift = b["basin_fraction"] / naive if naive > 0 else float("inf")
    print(f"      growth multiplies the usable-seed fraction by {lift:.1f}x "
          f"({naive:.1%} -> {b['basin_fraction']:.1%})", flush=True)

    # [3] does a row subsample preserve the ranking?
    sub = allp if len(allp) <= 2000 else [allp[i] for i in
                                          sorted(rng.choice(len(allp), 2000, replace=False))]
    sc = two_resolution_scan(fn, X, sub, n_screen=cfg["n_screen"], keep_frac=1.0)
    s_scr = np.array([r["screen"] for r in sc]); s_full = np.array([r["full"] for r in sc])
    m = np.isfinite(s_scr) & np.isfinite(s_full)
    rho = np.corrcoef(s_scr[m].argsort().argsort().astype(float),
                      s_full[m].argsort().argsort().astype(float))[0, 1]
    top2 = int(np.ceil(0.02 * m.sum()))
    survives = bool(np.argmax(s_full[m]) in set(np.argsort(-s_scr[m])[:top2]))
    print(f"  [3] screen at n={cfg['n_screen']} vs full n={len(X)}: Spearman {rho:+.3f}; "
          f"full winner in the screen's top 2% ({top2} of {int(m.sum())}): {survives}", flush=True)

    os.makedirs("results", exist_ok=True)
    row = dict(**{k: v for k, v in cfg.items()}, p=p, n_rows=len(X), n_pairs=len(allp),
               ceiling=ceiling, bar=bar, naive_fraction=naive, screen_spearman=float(rho),
               screen_keeps_winner=survives, **b)
    pd.DataFrame([row]).to_csv(OUT, mode="a", header=not os.path.exists(OUT), index=False)
    print(f"\n  appended to {OUT}")
    print("  NOTE f and the ceiling use labels. They measure the DATA so we can state the cost of")
    print("  search on it; they are never available to the search itself.")


if __name__ == "__main__":
    main()
