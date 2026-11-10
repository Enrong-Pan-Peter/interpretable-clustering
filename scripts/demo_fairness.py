"""End-to-end demo of the fairness question.

    preprocess -> run ATOMIC -> (1) subspace-parity of a TRUSTED partition/subspace
                             -> (2) full comparison vs. KMeans/GMM/DBSCAN, scored in
                                full space AND the subspace.

On synthetic data we KNOW the separating dims, so the comparison uses that trusted
subspace (and we separately check whether ATOMIC recovers it). On a UCI set we use
ATOMIC's own selected subspace and judge it by ARI/NMI vs. labels.

Run:
    python scripts/demo_fairness.py                 # synthetic (always works)
    python scripts/demo_fairness.py ionosphere      # a cached UCI set (after fetch_uci.py)

Reading it: if ATOMIC's lead on sil_sub/db_sub and ari/nmi survives once baselines are
re-fit in the subspace, the advantage is real; if it collapses, the silhouette/DB win
was largely a metric-space artifact.
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

pd.set_option("display.width", 150)
pd.set_option("display.max_columns", 20)


def load(name):
    if name == "synthetic":
        rng = np.random.default_rng(0)
        X, y, informative = syn.two_cluster_subspace(n=200, p=20, informative=[4, 11], rng=rng)
        return X, y, informative
    from atomicplus.datasets import uci
    X, y = uci.load_uci(name)
    return X, y, None


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "synthetic"
    X, y, informative = load(name)
    print(f"Dataset: {name}   shape={X.shape}   labels={'yes' if y is not None else 'no'}")
    Xp = preprocess(X).to_numpy()

    cfg = AtomicConfig(seed=0, pop_size=80, mu=80, lam=50, n_gen=30, archive_rebuild_every=30)
    res = atomic(Xp, cfg)
    best = res.best()
    V_atomic = sorted(int(i) for i in gm.selected_indices(best.genome))
    ari_best = metrics.ari(y, best.quality.labels) if y is not None else float("nan")
    print(f"k-tilde (auto, smallest-stable-k) = {res.k_tilde}")
    print(f"ATOMIC best: {best.quality.size} feats {V_atomic} -> {best.quality.n_components} "
          f"components   ARI-vs-labels={ari_best:.3f}")

    if informative is not None:
        on_front = any(set(informative).issubset(set(int(i) for i in gm.selected_indices(ind.genome)))
                       and ind.quality.n_components == 2 for ind in res.quality_front)
        print(f"true informative dims={informative}   true split present on quality front? {on_front}")
        if abs(ari_best) < 0.5:
            print("  (NOTE: small k-tilde maximises single-linkage chaining -> the flat "
                  "fitness admits spurious noise splits. This is caveat #2/#3 -> Phase 2.)")

    # Trusted subspace for the fairness question: true dims on synthetic, else ATOMIC's.
    V = informative if informative is not None else V_atomic
    labels_demo = y if y is not None else best.quality.labels

    print(f"\n(1) SUBSPACE PARITY on subspace {list(V)} — same partition, two spaces:")
    print(harness.subspace_parity_demo(Xp, V, labels_demo).round(3).to_string())

    print(f"\n(2) COMPARISON — methods scored in full space (R^{Xp.shape[1]}) vs subspace "
          f"(R^{len(V)}={list(V)}):")
    atomic_labels = labels_demo if informative is not None else best.quality.labels
    tbl = harness.compare(Xp, V, atomic_labels, y_true=y, rng=0)
    print(tbl.round(3).to_string())
    print("\nsil_* higher=better, db_* lower=better; _full=all dims, _sub=subspace; "
          "ari/nmi vs. ground truth are space-invariant.")


if __name__ == "__main__":
    main()
