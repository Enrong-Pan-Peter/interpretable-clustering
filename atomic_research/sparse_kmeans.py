"""Exploratory sparse k-means panel proposals, following Witten/Tibshirani.

Alternates two-cluster weighted k-means and maximization of weighted between-
cluster sums of squares with nonnegative L2/L1 constrained feature weights.
This is an established mean-shift baseline, not CHIME or cluster validation.
"""

from __future__ import annotations

from time import perf_counter
from typing import Sequence

import numpy as np
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

from .soft_graph import ProposalResult


def _sparse_weights(scores: np.ndarray, l1_bound: float) -> np.ndarray:
    """Maximize scores @ w subject to w>=0, ||w||2<=1, ||w||1<=s.

    Nonnegative scores are assumed. Equal maxima at a very small bound have a
    symmetric optimum with inactive L2 constraint; handle it without arbitrary
    feature selection. The ordinary case uses soft thresholding and bisection.
    """
    scores = np.asarray(scores, dtype=float)
    if not np.any(scores > 0):
        return np.zeros_like(scores)
    maximum = float(scores.max())
    maxima = scores == maximum
    if l1_bound <= np.sqrt(maxima.sum()):
        return maxima.astype(float) * (l1_bound / maxima.sum())
    weights = scores / np.linalg.norm(scores)
    if weights.sum() <= l1_bound:
        return weights
    lo, hi = 0.0, maximum
    for _ in range(80):
        threshold = (lo + hi) / 2
        candidate = np.maximum(scores - threshold, 0.0)
        norm = np.linalg.norm(candidate)
        if norm == 0:
            hi = threshold
            continue
        candidate /= norm
        if candidate.sum() > l1_bound:
            lo = threshold
        else:
            hi = threshold
            weights = candidate
    return weights


def _between_ss(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-feature between-cluster sum of squares, allowing uncentered X."""
    grand_mean = X.mean(axis=0)
    scores = np.zeros(X.shape[1])
    for label in np.unique(labels):
        group = X[labels == label]
        scores += len(group) * (group.mean(axis=0) - grand_mean) ** 2
    return scores


def propose_panels(
    X: np.ndarray,
    max_features: int = 8,
    seed: int = 0,
    steps: int = 20,
    restarts: int = 3,
    *,
    l1_bounds: Sequence[float] | None = None,
    max_samples: int | None = None,
    standardize: bool = True,
    max_seconds: float | None = None,
    tolerance: float = 1e-6,
) -> ProposalResult:
    """Return ranked feature prefixes from a sparse k-means path.

    Every sparsity setting receives `restarts` initializations. Defaults test
    L1 bounds 1.25, sqrt(max_features), and sqrt(p), clipped to [1,sqrt(p)].
    Prefixes may contain zero-weight features, ranked by conditional BCSS;
    they require independent panel evaluation. No labels or planted support
    are accepted. Timing includes preprocessing, all starts, Lloyd updates,
    weight optimization, and rounding. `max_seconds` is a soft between-fit cap.
    """
    started = perf_counter()
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 4 or X.shape[1] < 1:
        raise ValueError("X must have >=4 rows and >=1 feature")
    if not np.isfinite(X).all():
        raise ValueError("X must contain finite discovery data")
    for name, value in (("max_features", max_features), ("steps", steps), ("restarts", restarts)):
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
            raise ValueError(f"{name} must be an integer >=1")
    if max_samples is not None and (
        isinstance(max_samples, bool) or not isinstance(max_samples, (int, np.integer)) or max_samples < 4
    ):
        raise ValueError("max_samples must be None or an integer >=4")
    if max_seconds is not None and (not np.isfinite(max_seconds) or max_seconds <= 0):
        raise ValueError("max_seconds must be positive and finite")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")

    mean, scale = X.mean(axis=0), X.std(axis=0)
    if not np.isfinite(mean).all() or not np.isfinite(scale).all():
        raise ValueError("Feature moments overflowed; rescale inputs")
    varying = scale > np.finfo(float).eps * np.maximum(np.abs(mean), scale)
    feature_indices = np.flatnonzero(varying)
    rng = np.random.default_rng(seed)
    rows = np.arange(len(X)) if max_samples is None or max_samples >= len(X) else np.sort(
        rng.choice(len(X), max_samples, replace=False)
    )
    diagnostics = {
        "method": "exploratory_sparse_kmeans_proposals_v1", "status": "complete",
        "input_shape": list(X.shape), "seed": int(seed),
        "excluded_constant_features": np.flatnonzero(~varying).tolist(),
        "sample_indices": rows.tolist(), "standardize": bool(standardize),
        "requested_restarts_per_bound": int(restarts), "completed_restarts": 0,
        "requested_steps_per_restart": int(steps), "max_features": int(max_features),
        "objective_evaluations": 0, "kmeans_fits": 0, "lloyd_iterations": 0,
        "l1_bounds": [], "panel_sources": [], "restart_summaries": [],
        "warnings": ["Proposal objective does not test cluster existence.",
                     "Rounded prefixes require independent evaluation; zero-weight features may be included."],
    }
    if len(feature_indices) == 0:
        diagnostics["status"] = "no_variable_features"
        return ProposalResult([], perf_counter() - started, diagnostics, [])
    Z = X[np.ix_(rows, feature_indices)] - mean[feature_indices]
    if standardize:
        Z /= scale[feature_indices]
    if not np.isfinite(Z).all():
        raise ValueError("Feature scaling overflowed")
    p = Z.shape[1]
    cap = min(max_features, p)
    if l1_bounds is None:
        bounds = sorted(set(float(np.clip(s, 1, np.sqrt(p))) for s in (1.25, np.sqrt(cap), np.sqrt(p))))
    else:
        bounds = [float(s) for s in l1_bounds]
        if not bounds or any(not np.isfinite(s) or not 1 <= s <= np.sqrt(p) + 1e-12 for s in bounds):
            raise ValueError("l1_bounds must be nonempty and within [1,sqrt(variable_features)]")
        bounds = list(dict.fromkeys(bounds))
    diagnostics["l1_bounds"] = bounds
    diagnostics["requested_restarts"] = len(bounds) * restarts
    panels, trace, seen = [], [], set()

    def collect(weights, scores, bound, restart, step):
        # Weight ties use conditional BCSS, then column order for exact ties.
        ranking = np.lexsort((np.arange(p), -scores, -weights))[:cap]
        for size in range(1, cap + 1):
            panel = tuple(sorted(int(j) for j in feature_indices[ranking[:size]]))
            if panel not in seen:
                seen.add(panel)
                panels.append(panel)
            diagnostics["panel_sources"].append({"panel": list(panel), "l1_bound": bound,
                "restart": restart, "step": step, "prefix_size": size})

    stop = False
    with threadpool_limits(limits=1):
        for bound in bounds:
            for restart in range(restarts):
                weights = np.full(p, 1 / np.sqrt(p))
                labels = None
                scores = np.zeros(p)
                fit_seed = int(rng.integers(0, 2**31 - 1))
                completed = 0
                for step in range(steps):
                    if max_seconds is not None and perf_counter() - started >= max_seconds:
                        diagnostics["status"] = "time_budget_exhausted"
                        stop = True
                        break
                    weighted = Z * np.sqrt(weights)
                    initial = "k-means++" if labels is None else np.array([
                        weighted[labels == k].mean(axis=0) for k in (0, 1)
                    ])
                    fit = KMeans(n_clusters=2, n_init=1, init=initial, random_state=fit_seed,
                                 max_iter=100, tol=1e-6).fit(weighted)
                    diagnostics["kmeans_fits"] += 1
                    diagnostics["lloyd_iterations"] += int(fit.n_iter_)
                    new_labels = fit.labels_
                    if len(np.unique(new_labels)) < 2:
                        diagnostics["warnings"].append("A weighted fit collapsed to one cluster.")
                        break
                    scores = _between_ss(Z, new_labels)
                    new_weights = _sparse_weights(scores, bound)
                    change = float(np.linalg.norm(new_weights - weights))
                    stable = labels is not None and np.array_equal(new_labels, labels) and change <= tolerance
                    labels, weights = new_labels, new_weights
                    diagnostics["objective_evaluations"] += 1
                    completed += 1
                    trace.append({"l1_bound": bound, "restart": restart, "step": step,
                        "objective": float(scores @ weights), "weight_change": change,
                        "weight_l1": float(weights.sum()), "weight_l2": float(np.linalg.norm(weights)),
                        "active_features": int(np.sum(weights > 1e-10)),
                        "child_sizes": np.bincount(labels, minlength=2).tolist(),
                        "elapsed_seconds": perf_counter() - started})
                    if step in {0, steps // 2, steps - 1} or stable:
                        collect(weights, scores, bound, restart, step)
                    if stable:
                        break
                if completed:
                    collect(weights, scores, bound, restart, completed - 1)
                    diagnostics["completed_restarts"] += 1
                    diagnostics["restart_summaries"].append({"l1_bound": bound, "restart": restart,
                        "iterations": completed, "weights": weights.tolist(),
                        "feature_indices": feature_indices.tolist()})
                if stop:
                    break
            if stop:
                break
    return ProposalResult(panels, perf_counter() - started, diagnostics, trace)
