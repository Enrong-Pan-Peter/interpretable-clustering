"""Adjudicate a dataset's ATOMIC split: real structure or search artifact?

    python scripts/run_significance.py ceramic
    python scripts/run_significance.py biodegradation --perms 99 --boots 50
    python scripts/run_significance.py biodegradation --subsample 400   # cap n for speed

Runs the permutation null test (is ATOMIC's separation beyond what it finds on
structure-destroyed data?) and subsample stability (does the split reproduce?).
Use >=19 permutations to be able to reach p<0.05; ~99 for a clean number.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from atomicplus import AtomicConfig, preprocess                  # noqa: E402
from atomicplus.datasets import synthetic as syn                 # noqa: E402
from atomicplus.evaluation import significance as sig            # noqa: E402


def load(name, subsample):
    if name == "noise":
        X = np.random.default_rng(7).random((200, 20))
        y = None
    elif name == "synthetic":
        rng = np.random.default_rng(0)
        Xdf, y, _ = syn.two_cluster_subspace(n=250, p=20, informative=[4, 11], rng=rng)
        X = Xdf
    else:
        from atomicplus.datasets import uci
        X, y = uci.load_uci(name)
    X = preprocess(X).to_numpy() if hasattr(X, "to_numpy") or X.dtype != float else preprocess(X)
    X = np.asarray(preprocess(X)) if not isinstance(X, np.ndarray) else X
    if subsample and len(X) > subsample:
        idx = np.random.default_rng(0).choice(len(X), subsample, replace=False)
        X = X[idx]
    return X


def main():
    args = list(sys.argv[1:])
    def opt(flag, default):
        if flag in args:
            i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
        return default
    perms = int(opt("--perms", 30))
    boots = int(opt("--boots", 20))
    fitness = opt("--fitness", "components")          # "components" (flat) | "persistence"
    mcs = int(opt("--min-cluster-size", 5))
    subsample = opt("--subsample", None)
    subsample = int(subsample) if subsample else None
    name = args[0] if args else "ceramic"

    # light config: statistic distribution, not a headline run
    X = load(name, subsample)
    cfg = AtomicConfig(seed=0, pop_size=40, mu=40, lam=24, n_gen=15, archive_rebuild_every=20,
                       fitness_mode=fitness, min_cluster_size=mcs,
                       k_tilde=(5 if fitness == "persistence" else None))
    print(f"Dataset: {name}  shape={X.shape}  fitness={fitness}  (perms={perms}, boots={boots})\n")

    print("NULL MODEL (permutation):")
    print("   ", sig.null_separation_test(X, cfg, n_permutations=perms, base_seed=0).summary())

    print("\nSTABILITY (subsample re-runs):")
    print("   ", sig.subsample_stability(X, cfg, n_runs=boots, frac=0.8, base_seed=0).summary())


if __name__ == "__main__":
    main()
