"""Baseline clusterers (k-means, GMM, DBSCAN) with the paper's model-selection rules.

Each returns integer labels. Model selection follows paper §3.3 where sensible:
  * k-means over k=2..20. NOTE: the paper says it picked the result "which minimized
    the within-cluster sum of squared errors" — but WCSS decreases monotonically in k,
    so that literally selects k=20. We default to silhouette (a real criterion) and
    expose `criterion="sse"` to reproduce the degenerate rule. Flagged in the harness.
  * GMM over all covariance types and 2..20 components, selected by BIC.
  * DBSCAN with eps from the k-distance knee (the authors'-suggested heuristic).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors

from .metrics import silhouette


def kmeans_best(X, k_min: int = 2, k_max: int = 20, criterion: str = "silhouette",
                rng: int = 0) -> Tuple[np.ndarray, int]:
    X = np.asarray(X, dtype=float)
    hi = min(k_max, len(X) - 1)
    best = None
    for k in range(k_min, hi + 1):
        labels = KMeans(n_clusters=k, n_init=10, random_state=rng).fit_predict(X)
        if criterion == "sse":
            km = KMeans(n_clusters=k, n_init=10, random_state=rng).fit(X)
            score = -km.inertia_
        else:
            score = silhouette(X, labels)
        if score != score:  # NaN
            continue
        if best is None or score > best[0]:
            best = (score, labels, k)
    if best is None:
        labels = KMeans(n_clusters=2, n_init=10, random_state=rng).fit_predict(X)
        return labels, 2
    return best[1], best[2]


def gmm_best(X, n_min: int = 2, n_max: int = 20, rng: int = 0) -> Tuple[np.ndarray, int]:
    X = np.asarray(X, dtype=float)
    hi = min(n_max, len(X) - 1)
    best = None
    for cov in ("full", "tied", "diag", "spherical"):
        for n in range(n_min, hi + 1):
            try:
                g = GaussianMixture(n_components=n, covariance_type=cov,
                                    random_state=rng).fit(X)
            except Exception:  # noqa: BLE001
                continue
            bic = g.bic(X)
            if best is None or bic < best[0]:
                best = (bic, g.predict(X), n)
    if best is None:
        return np.zeros(len(X), dtype=int), 1
    return best[1], best[2]


def dbscan_default(X, min_samples: int = None, rng: int = 0) -> Tuple[np.ndarray, int]:
    """DBSCAN with eps from the knee of the sorted k-distance curve (Ester et al.)."""
    X = np.asarray(X, dtype=float)
    d = X.shape[1]
    if min_samples is None:
        min_samples = max(4, min(2 * d, len(X) - 1))
    nn = NearestNeighbors(n_neighbors=min_samples).fit(X)
    dists, _ = nn.kneighbors(X)
    kdist = np.sort(dists[:, -1])
    # knee = point of maximum curvature on the sorted k-distance curve
    eps = _knee(kdist)
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    return labels, n_clusters


def _knee(curve: np.ndarray) -> float:
    n = len(curve)
    if n < 3:
        return float(curve[-1]) if n else 1.0
    x = np.arange(n, dtype=float)
    x0, x1 = x[0], x[-1]
    y0, y1 = curve[0], curve[-1]
    denom = np.hypot(x1 - x0, y1 - y0) + 1e-12
    dist = np.abs((y1 - y0) * x - (x1 - x0) * curve + x1 * y0 - y1 * x0) / denom
    eps = float(curve[int(np.argmax(dist))])
    return eps if eps > 0 else float(np.median(curve))


def spectral_best(X, k_min: int = 2, k_max: int = 10, rng: int = 0):
    """Spectral clustering (nearest-neighbour affinity), k chosen by silhouette."""
    from sklearn.cluster import SpectralClustering
    X = np.asarray(X, dtype=float)
    hi = min(k_max, len(X) - 1)
    best = None
    for k in range(k_min, hi + 1):
        try:
            labels = SpectralClustering(n_clusters=k, affinity="nearest_neighbors",
                                        random_state=rng, assign_labels="kmeans").fit_predict(X)
        except Exception:  # noqa: BLE001
            continue
        sc = silhouette(X, labels)
        if sc == sc and (best is None or sc > best[0]):
            best = (sc, labels, k)
    if best is None:
        return np.zeros(len(X), dtype=int), 1
    return best[1], best[2]


def hdbscan_best(X, min_cluster_size: int = 10, rng: int = 0):
    """HDBSCAN (density-based, handles non-convex + noise); labels -1 are noise points."""
    try:
        from sklearn.cluster import HDBSCAN
    except Exception:  # noqa: BLE001
        return np.zeros(len(X), dtype=int), 1
    X = np.asarray(X, dtype=float)
    # copy=True set explicitly: sklearn 1.10 changes this default, and pinning it here keeps
    # behaviour identical across versions and silences the FutureWarning that floods long runs.
    labels = HDBSCAN(min_cluster_size=max(5, min_cluster_size), copy=True).fit_predict(X)
    n = len(set(labels)) - (1 if -1 in labels else 0)
    return labels, n
