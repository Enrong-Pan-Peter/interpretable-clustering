"""The fair benchmark (audit H4 + method-vs-baselines), multi-seed with stats.

Two tracks:
  * H4 single-split: does the EA beat greedy / random / the flat baseline-ATOMIC at finding a
    good 2-way split? (ARI/NMI vs labels, persistence, #features)  -- "does the search earn its cost?"
  * partition: ATOMIC+ tree vs k-means / GMM / spectral / DBSCAN (ARI/NMI, #clusters).

The EA uses the Phase-5 operators (set-based crossover + asymmetric mutation); baseline-ATOMIC
keeps the faithful OR + symmetric + flat fitness. Reports mean +/- std per dataset and, across
datasets, a Friedman test + average ranks per track.

    python scripts/run_benchmark.py --quick                 # tiny smoke run (2 datasets, 2 seeds)
    python scripts/run_benchmark.py --seeds 30              # the full run (slow; run on your box)
    python scripts/run_benchmark.py --seeds 30 --datasets glass ionosphere synthetic2
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from atomicplus import AtomicConfig, atomic, preprocess          # noqa: E402
from atomicplus import genome as gm                              # noqa: E402
from atomicplus import tree as T                                 # noqa: E402
from atomicplus.datasets import synthetic as syn                 # noqa: E402
from atomicplus.evaluation import baselines, metrics             # noqa: E402
from atomicplus.evaluation.search_baselines import (              # noqa: E402
    greedy_forward_persistence, random_search_persistence)
from atomicplus.evaluation.diversity import n_alternative_panels  # noqa: E402

pd.set_option("display.width", 170)
pd.set_option("display.max_columns", 30)

SYNTHETIC = {
    "synthetic2": lambda rng: syn.two_cluster_subspace(n=200, p=20, informative=[4, 11], rng=rng)[:2],
    "hier3": lambda rng: syn.hierarchical_subspace(n=210, p=15, rng=rng)[:2],
    "moons": lambda rng: syn.moons_subspace(n=240, p=12, informative=[3, 8], rng=rng)[:2],
    "circles": lambda rng: syn.circles_subspace(n=240, p=12, informative=[3, 8], rng=rng)[:2],
}
UCI = ["glass", "ionosphere", "wholesale", "ceramic", "biodegradation"]


def load(name, seed):
    if name in SYNTHETIC:                       # regenerate per seed (data+method variance)
        X, y = SYNTHETIC[name](np.random.default_rng(seed))
        return preprocess(X).to_numpy(), np.asarray(y)
    from atomicplus.datasets import uci          # fixed data; seed varies the method rng
    X, y = uci.load_uci(name)
    return preprocess(X).to_numpy(), (None if y is None else np.asarray(y))


def _ari_nmi(y, labels):
    if y is None or labels is None:
        return np.nan, np.nan
    return metrics.ari(y, labels), metrics.nmi(y, labels)


def run_cell(name, Xp, y, seed, cfg_ea, cfg_flat, quick):
    rows = []
    p = Xp.shape[1]
    n_evals = cfg_ea.pop_size + cfg_ea.n_gen * cfg_ea.lam

    def rec(track, method, labels, nfeat=np.nan, extra=0.0, panels=1):
        ari, nmi = _ari_nmi(y, labels)
        k = int(len(np.unique(labels))) if labels is not None else 0
        rows.append(dict(dataset=name, seed=seed, track=track, method=method,
                         ari=ari, nmi=nmi, nfeat=nfeat, nclusters=k, score=extra, panels=panels))

    # ---- H4 single-split track ----
    res_ea = atomic(Xp, cfg_ea, np.random.default_rng(seed))
    ea = res_ea.best()
    if ea is not None:
        rec("H4", "ATOMIC+ (EA)", ea.quality.labels, len(gm.selected_indices(ea.genome)),
            ea.quality.f, panels=n_alternative_panels(res_ea, max_features=4))
    gf, gs, gl = greedy_forward_persistence(Xp, min_cluster_size=cfg_ea.min_cluster_size)
    rec("H4", "greedy", gl, len(gf), gs)
    rf, rs, rl = random_search_persistence(Xp, n_evals=n_evals, min_cluster_size=cfg_ea.min_cluster_size,
                                           rng=np.random.default_rng(seed))
    rec("H4", "random", rl, len(rf), rs)
    fl = atomic(Xp, cfg_flat, np.random.default_rng(seed)).best()
    if fl is not None:
        rec("H4", "baseline-ATOMIC", fl.quality.labels, len(gm.selected_indices(fl.genome)))

    # ---- partition track ----
    try:
        tr = T.build_tree(Xp, config=cfg_ea, min_persistence=1.4, max_depth=(3 if quick else 5),
                          beam=(1 if quick else 3), gate_mode="stability", gate_n_sub=(3 if quick else 5))
        rec("partition", "ATOMIC+ tree", tr.labels(), np.nan)
    except Exception as e:  # noqa: BLE001
        rec("partition", "ATOMIC+ tree", None)
    rec("partition", "kmeans", baselines.kmeans_best(Xp, rng=seed)[0])
    rec("partition", "gmm", baselines.gmm_best(Xp, rng=seed)[0])
    rec("partition", "spectral", baselines.spectral_best(Xp, rng=seed)[0])
    rec("partition", "dbscan", baselines.dbscan_default(Xp)[0])
    return rows


def summarize(df):
    for track in ["H4", "partition"]:
        sub = df[df.track == track]
        if sub.empty:
            continue
        print(f"\n===== {track} track: mean ARI by dataset x method =====")
        piv = sub.pivot_table(index="dataset", columns="method", values="ari", aggfunc="mean")
        print(piv.round(3).to_string())
        if track == "H4":
            print("-- H4 also by PERSISTENCE (the search objective; the fair EA-vs-greedy metric) --")
            print(sub.pivot_table(index="dataset", columns="method", values="score",
                                  aggfunc="mean").round(2).to_string())
            print("-- H4 also by #FEATURES (interpretability; lower=better) --")
            print(sub.pivot_table(index="dataset", columns="method", values="nfeat",
                                  aggfunc="mean").round(1).to_string())
            print("-- H4 DIVERSITY: mean #alternative panels (greedy/random=1 by construction) --")
            print(sub.pivot_table(index="dataset", columns="method", values="panels",
                                  aggfunc="mean").round(1).to_string())
        # Friedman + average ranks across datasets (higher ARI = better)
        piv2 = piv.dropna(axis=0, how="any")
        if piv2.shape[0] >= 3 and piv2.shape[1] >= 3:
            from scipy.stats import friedmanchisquare
            arrs = [piv2[m].values for m in piv2.columns]
            stat, pval = friedmanchisquare(*arrs)
            ranks = piv2.rank(axis=1, ascending=False).mean(0).sort_values()
            print(f"Friedman chi2={stat:.2f} p={pval:.4f}  |  avg ranks (1=best): "
                  + ", ".join(f"{m} {r:.2f}" for m, r in ranks.items()))
        else:
            print("(need >=3 datasets with all methods for Friedman; run more datasets)")


def main():
    args = list(sys.argv[1:])
    quick = "--quick" in args
    if quick:
        args.remove("--quick")
    seeds = 2 if quick else 10
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = int(args[i + 1]); del args[i:i + 2]
    datasets = args if args else (["synthetic2", "glass"] if quick else list(SYNTHETIC) + UCI)

    base = dict(fitness_mode="persistence", k_tilde=5, min_cluster_size=5,
                crossover_mode="set_based", mutation_mode="asymmetric", archive_rebuild_every=25,
                pair_seed_init=True)
    if quick:
        cfg_ea = AtomicConfig(pop_size=30, mu=30, lam=18, n_gen=8, **base)
    else:
        cfg_ea = AtomicConfig(pop_size=60, mu=60, lam=36, n_gen=25, **base)
    cfg_flat = AtomicConfig(fitness_mode="components", k_tilde=None, min_cluster_size=5,
                            pop_size=cfg_ea.pop_size, mu=cfg_ea.mu, lam=cfg_ea.lam, n_gen=cfg_ea.n_gen,
                            crossover_mode="or", mutation_mode="symmetric", archive_rebuild_every=25)

    print(f"Benchmark: datasets={datasets}  seeds={seeds}  quick={quick}")
    all_rows = []
    for name in datasets:
        for seed in range(seeds):
            try:
                Xp, y = load(name, seed)
            except Exception as e:  # noqa: BLE001
                print(f"  {name}: load failed ({e})"); break
            all_rows += run_cell(name, Xp, y, seed, cfg_ea, cfg_flat, quick)
        print(f"  done {name}")
    df = pd.DataFrame(all_rows)
    for path in ("results/benchmark.csv", "/tmp/benchmark.csv"):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            df.to_csv(path, index=False); print(f"\nsaved {path}"); break
        except PermissionError:
            continue
    summarize(df)


if __name__ == "__main__":
    main()
