"""Fair-comparison harness over cached UCI datasets, WITH honest ATOMIC solution-picking.

The paper never specifies how ATOMIC's single reported solution is chosen (caveat #7),
and the flat fitness ties every 2-component split (caveat #2). So we report ATOMIC three
ways and give it its best shot:
  * auto_best      = highest f, then fewest features (our faithful default)
  * best_sil_sub   = the front's 2-component solution with the best silhouette in its own
                     subspace  (upper bound; mimics eyeballing the nicest solution)
  * best_ari       = the front's 2-component solution best matching the labels (oracle)
The comparison table uses best_sil_sub as ATOMIC's representative (its best foot forward).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from atomicplus import AtomicConfig, atomic, preprocess          # noqa: E402
from atomicplus import genome as gm                              # noqa: E402
from atomicplus.datasets import uci                              # noqa: E402
from atomicplus.evaluation import harness, metrics               # noqa: E402

pd.set_option("display.width", 170)
pd.set_option("display.max_columns", 24)
ALL = ["glass", "ionosphere", "wholesale", "cervical_cancer", "ozone"]


def _V(ind):
    return sorted(int(i) for i in gm.selected_indices(ind.genome))


def run_one(name, subsample=None):
    X, y = uci.load_uci(name)
    if subsample and len(X) > subsample:
        idx = np.random.default_rng(0).choice(len(X), subsample, replace=False)
        X, y = X.iloc[idx].reset_index(drop=True), (y[idx] if y is not None else None)
    p = X.shape[1]
    Xp = preprocess(X).to_numpy()
    cfg = AtomicConfig(seed=0, pop_size=60, mu=60, lam=40, n_gen=25, archive_rebuild_every=30)
    res = atomic(Xp, cfg)

    cands = [i for i in res.quality_front
             if i.quality.labels is not None and i.quality.n_components == 2]
    auto = res.best()
    best_sub = max(cands, key=lambda i: metrics.silhouette(Xp[:, gm.selected_indices(i.genome)],
                                                           i.quality.labels)) if cands else auto
    best_ari = (max(cands, key=lambda i: metrics.ari(y, i.quality.labels))
                if (cands and y is not None) else None)

    def line(tag, ind):
        V = _V(ind)
        smin = int(np.bincount(ind.quality.labels).min())
        sil_full = metrics.silhouette(Xp, ind.quality.labels)
        sil_sub = metrics.silhouette(Xp[:, V], ind.quality.labels)
        ari = metrics.ari(y, ind.quality.labels) if y is not None else float("nan")
        return (f"    {tag:13s} {len(V):>2}/{p} feats {str(V):22.22s} minclust={smin:<4d} "
                f"sil_full={sil_full:+.3f} sil_sub={sil_sub:+.3f} ari={ari:+.3f}")

    print(f"\n=== {name}  (n={X.shape[0]}, p={p}, labels={'y' if y is not None else 'n'})  "
          f"k-tilde={res.k_tilde}  front={len(res.quality_front)} ===")
    print(line("auto_best", auto))
    print(line("best_sil_sub", best_sub))
    if best_ari is not None:
        print(line("best_ari", best_ari))

    V = _V(best_sub)
    tbl = harness.compare(Xp, V, best_sub.quality.labels, y_true=y, rng=0)
    print("  comparison vs baselines on ATOMIC's best-shot subspace V=%s :" % V)
    print(tbl.round(3).to_string().replace("\n", "\n    "))
    tbl.insert(0, "dataset", name)
    return tbl


def main():
    args = list(sys.argv[1:])
    subsample = None
    if "--subsample" in args:
        i = args.index("--subsample"); subsample = int(args[i + 1]); del args[i:i + 2]
    names = args if args else ALL
    os.makedirs("results", exist_ok=True)
    frames = []
    for name in names:
        try:
            frames.append(run_one(name, subsample=subsample))
        except Exception as e:  # noqa: BLE001
            print(f"\n=== {name}: SKIPPED ({type(e).__name__}: {e}) ===")
    if frames:
        import os as _os
        for _p in ("results/uci_comparison.csv", "/tmp/uci_comparison.csv"):
            try:
                _os.makedirs(_os.path.dirname(_p) or ".", exist_ok=True)
                pd.concat(frames).to_csv(_p); print(f"\nSaved {_p}"); break
            except PermissionError:
                continue


if __name__ == "__main__":
    main()
