"""Clustering metrics with an EXPLICIT space argument and safe degenerate handling.

Internal (space-dependent): silhouette, Davies-Bouldin. External (space-invariant):
Adjusted Rand Index, Normalized Mutual Information. Degenerate label sets (one cluster,
or all singletons) return NaN rather than raising.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (adjusted_rand_score, davies_bouldin_score,
                             normalized_mutual_info_score, silhouette_score)


def _usable(labels: np.ndarray) -> bool:
    labels = np.asarray(labels)
    n_clusters = len(np.unique(labels))
    return 2 <= n_clusters < len(labels)


def silhouette(X, labels) -> float:
    if not _usable(labels):
        return float("nan")
    try:
        return float(silhouette_score(np.asarray(X, dtype=float), labels))
    except Exception:  # noqa: BLE001
        return float("nan")


def davies_bouldin(X, labels) -> float:
    if len(np.unique(labels)) < 2:
        return float("nan")
    try:
        return float(davies_bouldin_score(np.asarray(X, dtype=float), labels))
    except Exception:  # noqa: BLE001
        return float("nan")


def ari(y_true, labels) -> float:
    return float(adjusted_rand_score(y_true, labels))


def nmi(y_true, labels) -> float:
    return float(normalized_mutual_info_score(y_true, labels))
