"""Partition-consistent research scores, kept separate from statistical evidence.

These are *ranking diagnostics*, not probabilities that clusters exist. X must
already have been transformed by preprocessing fitted on discovery rows. This
module neither accepts external class labels nor chooses feature panels.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import SpectralClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import kneighbors_graph

from atomicplus.evaluation.subspace_baselines import _connect_graph, density_term

INVALID_SCORE = -9.0


def _matrix(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] == 0:
        raise ValueError("X must be a two-dimensional array with at least one feature")
    if not np.isfinite(X).all():
        raise ValueError("X must contain only finite values; impute before scoring")
    return X


def _positive_int(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or int(value) != value or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _panel(panel: Sequence[int], p: int) -> tuple[int, ...]:
    values = tuple(panel)
    if not values or any(isinstance(j, (bool, np.bool_)) or int(j) != j for j in values):
        raise ValueError("panel must contain integer feature indices")
    values = tuple(int(j) for j in values)
    if len(set(values)) != len(values) or min(values) < 0 or max(values) >= p:
        raise ValueError("panel indices must be unique and in bounds")
    return tuple(sorted(values))


def _graph(Z: np.ndarray, D: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    # Preserve the historical binary kNN and bridge convention for comparability.
    A = kneighbors_graph(Z, n_neighbors=min(k, len(Z) - 1),
                         mode="connectivity", include_self=False)
    A = 0.5 * (A + A.T).toarray()
    return _connect_graph(A, D)


def _mutual_reach(D: np.ndarray, core_k: int) -> np.ndarray:
    # Diagonal zero is the self-distance; index k is the kth OTHER neighbour.
    c = np.partition(D, min(core_k, len(D) - 1), axis=1)[:, min(core_k, len(D) - 1)]
    M = np.maximum(D, np.maximum.outer(c, c))
    np.fill_diagonal(M, 0.0)
    return M


def _mst_bottleneck(M: np.ndarray) -> float:
    """Largest MST edge, retaining legitimate zero-distance edges.

    The last single-linkage merge equals the MST bottleneck. Unlike a sparse
    distance matrix, its condensed input distinguishes zero distance from a
    missing edge. This matters for quantized assays and duplicate observations.
    """
    if len(M) < 2:
        return 0.0
    return float(linkage(squareform(M, checks=False), method="single")[-1, 2])


def _invalid(reason: str, labels: np.ndarray | None = None) -> dict:
    return {"labels": labels, "graphcut": INVALID_SCORE, "density": INVALID_SCORE,
            "valid": False, "reason": reason, "cluster_sizes": [],
            "separation": None, "within_bottleneck": None,
            "graph_components_before_bridging": None}


def _components(Z: np.ndarray, labels: np.ndarray, A: np.ndarray,
                M: np.ndarray, min_cluster_size: int, n_components: int) -> dict:
    labels = np.asarray(labels)
    if labels.ndim != 1 or len(labels) != len(Z):
        raise ValueError("partition labels must be a vector with one entry per row")
    if labels.dtype.kind in "fc" and not np.isfinite(labels).all():
        return _invalid("nonfinite_partition", labels)
    unique, encoded = np.unique(labels, return_inverse=True)
    if len(unique) != 2:
        return _invalid("requires_two_clusters", labels)
    sizes = np.bincount(encoded, minlength=2)
    if sizes.min() < min_cluster_size:
        return _invalid("cluster_too_small", labels)
    if not np.any(np.ptp(Z, axis=0) > 0):
        return _invalid("constant_panel", labels)

    a, b = encoded == 0, encoded == 1
    d = A.sum(axis=1)
    volumes = (float(d[a].sum()), float(d[b].sum()))
    if min(volumes) <= 0:
        return _invalid("zero_graph_volume", labels)
    cut = float(A[np.ix_(a, b)].sum())
    graphcut = -(cut / volumes[0] + cut / volumes[1])
    separation = float(M[np.ix_(a, b)].min())
    within = max(_mst_bottleneck(M[np.ix_(a, a)]),
                 _mst_bottleneck(M[np.ix_(b, b)]))
    denominator = max(separation, within)
    # A completely coincident panel cannot supply evidence for any separation.
    if denominator <= 0:
        return _invalid("zero_distance_geometry", labels)
    density = (separation - within) / denominator
    return {"labels": labels.copy(), "graphcut": float(graphcut),
            "density": float(density), "valid": True, "reason": None,
            "cluster_sizes": sizes.tolist(), "separation": separation,
            "within_bottleneck": within,
            "graph_components_before_bridging": int(n_components)}


def score_partition(Z: np.ndarray, labels: np.ndarray, k: int = 10,
                    core_k: int = 5, min_cluster_size: int = 5) -> dict:
    """Score ONE supplied, algorithm-produced bipartition in its feature panel.

    graphcut = -normalized cut on the bridged historical binary kNN graph.
    density = (minimum between-cluster mutual reachability - maximum within-
    cluster MST edge) / max(those two). This is a DBCV-style *surrogate*, not
    DBCV: it uses global kth-neighbour cores, all points, and a worst-child
    bottleneck, rather than the complete DBCV construction and aggregation.

    Positive density means a finite-sample gap under this particular geometry;
    it is not an acceptance threshold, a p-value, or proof of multimodality.
    """
    Z = _matrix(Z)
    k, core_k = _positive_int(k, "k"), _positive_int(core_k, "core_k")
    min_cluster_size = max(2, _positive_int(min_cluster_size, "min_cluster_size"))
    labels = np.asarray(labels)
    if labels.ndim != 1 or len(labels) != len(Z):
        raise ValueError("partition labels must be a vector with one entry per row")
    if len(Z) < 2 * min_cluster_size:
        return _invalid("too_few_rows", labels)
    D = squareform(pdist(Z))
    A, n_components = _graph(Z, D, k)
    return _components(Z, labels, A, _mutual_reach(D, core_k),
                       min_cluster_size, n_components)


def score_panel(X: np.ndarray, panel: Sequence[int], splitter: str = "spectral",
                seed: int = 0, k: int = 10, core_k: int = 5,
                min_cluster_size: int = 5) -> dict:
    """Fit a bipartition and compare coherent terms with the legacy components.

    ``legacy_graphcut`` always scores the spectral labels;
    ``legacy_density`` always scores the old MST labels. Their combination is
    deliberately retained as a diagnostic, and may concern different splits.
    ``graphcut`` and ``density`` ALWAYS concern ``labels`` from ``splitter``.

    ``valid`` denotes numerical/size admissibility, not cluster existence.
    Use a frozen reference calibration outside this function for weighted
    scores; do not re-standardize against an evolving candidate population.
    """
    X = _matrix(X)
    panel = _panel(panel, X.shape[1])
    if splitter not in ("spectral", "mst"):
        raise ValueError("splitter must be 'spectral' or 'mst'")
    k, core_k = _positive_int(k, "k"), _positive_int(core_k, "core_k")
    min_cluster_size = max(2, _positive_int(min_cluster_size, "min_cluster_size"))
    Z = X[:, panel]
    base = {"panel": panel, "splitter": splitter,
            "legacy_graphcut": INVALID_SCORE, "legacy_density": INVALID_SCORE,
            "legacy_valid": False, "legacy_partition_ari": None,
            "legacy_labels": None}
    if len(Z) < 2 * min_cluster_size:
        return {**_invalid("too_few_rows"), **base}
    if not np.any(np.ptp(Z, axis=0) > 0):
        return {**_invalid("constant_panel"), **base}
    D = squareform(pdist(Z))
    A, n_components = _graph(Z, D, k)
    M = _mutual_reach(D, core_k)
    spectral_labels = None
    spectral_error = None
    try:
        spectral_labels = SpectralClustering(n_clusters=2, affinity="precomputed",
                                             random_state=seed).fit_predict(A)
    except (ValueError, np.linalg.LinAlgError) as exc:
        spectral_error = type(exc).__name__
    # Historical graphcut allows two points per side, while density used five.
    spectral_components = (_components(Z, spectral_labels, A, M, 2, n_components)
                           if spectral_labels is not None else _invalid("spectral_failed"))
    legacy_density, mst_labels = density_term(Z, core_k=core_k,
                                             min_cluster_size=min_cluster_size)
    base.update(legacy_graphcut=spectral_components["graphcut"],
                legacy_density=float(legacy_density), legacy_labels=mst_labels,
                legacy_valid=bool(spectral_components["valid"] and mst_labels is not None
                                  and legacy_density > INVALID_SCORE))
    if spectral_labels is not None and mst_labels is not None:
        base["legacy_partition_ari"] = float(adjusted_rand_score(spectral_labels, mst_labels))
    labels = spectral_labels if splitter == "spectral" else mst_labels
    if labels is None:
        result = _invalid(f"{splitter}_failed" + (f":{spectral_error}" if spectral_error else ""))
    elif splitter == "spectral":
        result = spectral_components
        if result["valid"] and min(result["cluster_sizes"]) < min_cluster_size:
            result = _invalid("cluster_too_small", labels)
    else:
        result = _components(Z, labels, A, M, min_cluster_size, n_components)
    return {**result, **base}


def column_permutation_calibration(Z: np.ndarray, statistic: Callable[[np.ndarray], float],
                                   B: int = 99, seed: int = 0) -> dict:
    """Monte Carlo comparison with the product-of-marginals (independence) null.

    The caller must supply a deterministic, row-permutation-invariant statistic
    fixed before looking at confirmation data. Larger values are the alternative.
    This tests column independence, NOT the absence of clusters. Searching panels
    and then using this p-value on the same rows does not account for selection.
    Randomized splitters must use fixed randomness within ``statistic``; residual
    row-order effects can otherwise masquerade as a nondegenerate singleton null.
    """
    Z = _matrix(Z)
    B = _positive_int(B, "B")
    if len(Z) < 2:
        raise ValueError("calibration requires at least two rows")
    raw = float(statistic(Z))
    rng = np.random.default_rng(seed)
    null = np.empty(B, dtype=float)
    for b in range(B):
        shuffled = np.column_stack([Z[rng.permutation(len(Z)), j]
                                    for j in range(Z.shape[1])])
        null[b] = float(statistic(shuffled))
    if not np.isfinite(raw) or not np.isfinite(null).all():
        raise ValueError("calibration statistic must return a finite scalar on every sample")
    mu = float(null.mean())
    sd = float(null.std(ddof=1)) if B > 1 else 0.0
    tol = 1e-12 * max(1.0, abs(raw), float(np.max(np.abs(null))))
    degenerate = sd <= tol
    return {"raw": raw, "null_mean": mu, "null_sd": sd,
            "z": None if degenerate else float((raw - mu) / sd),
            "p_value": float((1 + np.count_nonzero(null >= raw - tol)) / (B + 1)),
            "degenerate": bool(degenerate), "B": B, "null_scores": null,
            "null_target": "mutual independence of columns, preserving each marginal",
            "selection_adjusted": False}


def dependence_permutation_diagnostic(Z: np.ndarray, B: int = 99, seed: int = 0) -> dict:
    """Cheap example: sum of squared off-diagonal Pearson correlations.

    Sensitive to linear dependence only, hence not an omnibus independence test.
    A correlated unimodal Gaussian should reject this null despite having one
    population. A singleton has no cross-feature dependence and a degenerate null
    even if its marginal has an obvious gap. Use both as objective-target controls.
    """
    def squared_correlations(values: np.ndarray) -> float:
        centered = values - values.mean(axis=0)
        norms = np.linalg.norm(centered, axis=0)
        active = norms > 0
        if np.count_nonzero(active) < 2:
            return 0.0
        unit = centered[:, active] / norms[active]
        corr = unit.T @ unit
        return float(np.square(corr[np.triu_indices(len(corr), k=1)]).sum())

    return column_permutation_calibration(Z, squared_correlations, B=B, seed=seed)
