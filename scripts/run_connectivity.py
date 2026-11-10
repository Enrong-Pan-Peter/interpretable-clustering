"""ATOMIC's niche: non-convex clusters hidden in a noisy subspace.

For each dataset (moons/circles/jain/flame embedded in a noisy subspace), run single-split
ATOMIC (pair-seed) to get its selected features + partition, then compare k-means / GMM /
DBSCAN / spectral / HDBSCAN scored in FULL space AND re-fit in ATOMIC's subspace. The story:
centroid methods fail (non-convex); density methods fail in full space (noise) but recover when
handed ATOMIC's subspace -- which they can't find themselves. ATOMIC finds the few named features
AND clusters them, interpretably.

    python scripts/run_connectivity.py                       # moons circles jain flame, 5 seeds
    python scripts/run_connectivity.py --seeds 10 moons flame
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from atomicplus import AtomicConfig, atomic, preprocess          # noqa: E402
from atomicplus import genome as gm                              # noqa: E402
from atomicplus.datasets import synthetic as syn                 # noqa: E402
from atomicplus.evaluation import harness, metrics               # noqa: E402
from atomicplus.evaluation.diversity import n_alternative_panels  # noqa: E402

pd.set_option("display.width", 160)
DATA2D = os.path.join(os.path.dirname(__file__), "..", "2d_data")
INFORMATIVE = [2, 7]
P = 10


def _embed(xy, y, p, rng):
    xy = (xy - xy.min(0)) / (np.ptp(xy, axis=0) + 1e-12)
    X = rng.random((len(xy), p))
    X[:, INFORMATIVE[0]], X[:, INFORMATIVE[1]] = xy[:, 0], xy[:, 1]
    return preprocess(pd.DataFrame(X)).to_numpy(), np.asarray(y)


def load(name, seed):
    rng = np.random.default_rng(seed)
    if name == "moons":
        X, y, _ = syn.moons_subspace(n=240, p=P, informative=INFORMATIVE, rng=rng)
        return preprocess(X).to_numpy(), y
    if name == "circles":
        X, y, _ = syn.circles_subspace(n=240, p=P, informative=INFORMATIVE, rng=rng)
        return preprocess(X).to_numpy(), y
    arr = np.loadtxt(os.path.join(DATA2D, f"{name}.txt"), skiprows=1)
    return _embed(arr[:, :2].astype(float), arr[:, 2].astype(int), P, rng)


def main():
    args = list(sys.argv[1:])
    seeds = 5
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = int(args[i + 1]); del args[i:i + 2]
    datasets = args if args else ["moons", "circles", "jain", "flame"]
    cfg = AtomicConfig(fitness_mode="persistence", k_tilde=5, pop_size=50, mu=50, lam=30,
                       n_gen=15, archive_rebuild_every=25, min_cluster_size=8,
                       crossover_mode="set_based", mutation_mode="asymmetric", pair_seed_init=True)
    rows = []
    for name in datasets:
        for seed in range(seeds):
            Xp, y = load(name, seed)
            res = atomic(Xp, cfg, np.random.default_rng(seed))
            ea = res.best()
            V = sorted(int(i) for i in gm.selected_indices(ea.genome))
            tbl = harness.compare(Xp, V, ea.quality.labels, y_true=y, rng=0)
            for method, r in tbl.iterrows():
                rows.append(dict(dataset=name, seed=seed, method=method, ari=r["ari"]))
            rows.append(dict(dataset=name, seed=seed, method="_ATOMIC #feat", ari=len(V)))
            rows.append(dict(dataset=name, seed=seed, method="_ATOMIC #panels",
                             ari=n_alternative_panels(res)))
        print(f"  done {name}")
    df = pd.DataFrame(rows)
    for path in ("results/connectivity.csv", "/tmp/connectivity.csv"):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            df.to_csv(path, index=False); print(f"saved {path}"); break
        except PermissionError:
            continue
    print("\n===== mean ARI by dataset x method (ATOMIC vs baselines full-space & in ATOMIC's subspace) =====")
    piv = df.pivot_table(index="dataset", columns="method", values="ari", aggfunc="mean")
    cols = [c for c in piv.columns if not c.startswith("_")]
    print(piv[cols].round(3).to_string())
    extra = [c for c in piv.columns if c.startswith("_")]
    if extra:
        print("\nATOMIC interpretability/diversity:")
        print(piv[extra].round(1).to_string())
    # per-seed reliability of ATOMIC (the key question: how often does it recover the structure?)
    ea = df[df.method == "ATOMIC"]
    print("\nATOMIC ARI reliability (mean +/- std [min..max], #seeds ARI>0.5):")
    for name, g in ea.groupby("dataset"):
        a = g["ari"].values
        print("  %-9s %.2f +/- %.2f  [%.2f .. %.2f]   %d/%d seeds >0.5"
              % (name, a.mean(), a.std(), a.min(), a.max(), int((a > 0.5).sum()), len(a)))


if __name__ == "__main__":
    main()
