"""The fair-comparison harness — the point of Phase 0/1.

Scores every method's partition in BOTH the full space (ℝᵖ) and ATOMIC's selected
subspace (ℝ^|V|), plus space-invariant ARI/NMI vs. ground truth. If ATOMIC's edge
evaporates once baselines are also scored/re-fit in the subspace, the original win
was largely the space, not the method.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import metrics
from .baselines import dbscan_default, gmm_best, hdbscan_best, kmeans_best, spectral_best


def score_partition(X_full: np.ndarray, V, labels, y_true=None) -> Dict[str, float]:
    """Silhouette/DB for one partition, in full space and in subspace V; + ARI/NMI."""
    X_full = np.asarray(X_full, dtype=float)
    V = np.asarray(V, dtype=int)
    row = {
        "n_clusters": int(len(np.unique(labels))),
        "sil_full": metrics.silhouette(X_full, labels),
        "db_full": metrics.davies_bouldin(X_full, labels),
        "sil_sub": metrics.silhouette(X_full[:, V], labels) if len(V) else float("nan"),
        "db_sub": metrics.davies_bouldin(X_full[:, V], labels) if len(V) else float("nan"),
    }
    if y_true is not None:
        row["ari"] = metrics.ari(y_true, labels)
        row["nmi"] = metrics.nmi(y_true, labels)
    return row


_BASELINES = {
    "KMeans": lambda X, rng: kmeans_best(X, rng=rng)[0],
    "GMM": lambda X, rng: gmm_best(X, rng=rng)[0],
    "DBSCAN": lambda X, rng: dbscan_default(X, rng=rng)[0],
    "spectral": lambda X, rng: spectral_best(X, rng=rng)[0],
    "HDBSCAN": lambda X, rng: hdbscan_best(X, rng=rng)[0],
}


def compare(X_full, V, atomic_labels, y_true=None,
            refit_in_subspace: bool = True, rng: int = 0) -> pd.DataFrame:
    """Comparison table (rows = methods, cols = metrics).

    ATOMIC's partition is scored in full & subspace. Each baseline is (a) fit in full
    space then scored in both spaces, and (b) — if `refit_in_subspace` — re-fit inside
    V (subspace parity) and scored there. Read down `sil_sub`/`db_sub` and `ari`/`nmi`
    to see whether ATOMIC still leads once everyone shares the same space.
    """
    X_full = np.asarray(X_full, dtype=float)
    V = np.asarray(V, dtype=int)
    rows: Dict[str, Dict[str, float]] = {}

    rows["ATOMIC"] = score_partition(X_full, V, atomic_labels, y_true)

    for name, fitfn in _BASELINES.items():
        full_labels = fitfn(X_full, rng)
        rows[f"{name} (fit=full)"] = score_partition(X_full, V, full_labels, y_true)
        if refit_in_subspace and len(V):
            sub_labels = fitfn(X_full[:, V], rng)
            rows[f"{name} (fit=sub)"] = score_partition(X_full, V, sub_labels, y_true)

    return pd.DataFrame(rows).T


def subspace_parity_demo(X_full, V, labels) -> pd.DataFrame:
    """Take ONE fixed partition and show its silhouette/DB in full space vs. subspace V.

    Same points, same labels, two spaces. If silhouette jumps and DB drops in the
    subspace, that gap is the metric-space effect — pure measurement, since the
    partition never changed. This isolates the confound without any clustering.
    """
    X_full = np.asarray(X_full, dtype=float)
    V = np.asarray(V, dtype=int)
    return pd.DataFrame({
        "full_space": {
            "silhouette": metrics.silhouette(X_full, labels),
            "davies_bouldin": metrics.davies_bouldin(X_full, labels),
            "n_dims": X_full.shape[1],
        },
        "subspace_V": {
            "silhouette": metrics.silhouette(X_full[:, V], labels),
            "davies_bouldin": metrics.davies_bouldin(X_full[:, V], labels),
            "n_dims": len(V),
        },
    }).T
