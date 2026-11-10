"""Retain native sparse-k-means metrics, partitions, and assignment rules.

This diagnostic module does not change the earlier mask-only pilot. Sparse
k-means is an established baseline, not a new clustering method or a test of
cluster existence. ``max_features`` controls a prefix comparison budget; it
does NOT cap the full fitted model's number of positive feature weights.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Sequence

import numpy as np
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

from .sparse_kmeans import _between_ss, _sparse_weights


def _mapped_values(X: np.ndarray, representation: str, p: int | None = None) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 1 or X.shape[1] < 1:
        raise ValueError("X must be a nonempty two-dimensional numeric matrix")
    if p is not None and X.shape[1] != p:
        raise ValueError("X must have the same feature count as discovery data")
    if not np.isfinite(X).all():
        raise ValueError("X must contain only finite values; impute before fitting")
    if representation == "raw":
        return X
    if representation != "squared":
        raise ValueError("representation must be 'raw' or 'squared'")
    with np.errstate(over="ignore", invalid="ignore"):
        mapped = X**2
    if not np.isfinite(mapped).all():
        raise ValueError("Squared representation overflowed; rescale the inputs")
    return mapped


def _indices(panel: Sequence[int] | None, p: int) -> np.ndarray:
    if panel is None:
        return np.arange(p)
    values = tuple(panel)
    if not values or any(
        not isinstance(j, (int, np.integer)) or isinstance(j, (bool, np.bool_))
        for j in values
    ):
        raise ValueError("panel must contain unique integer feature indices")
    if len(set(values)) != len(values) or min(values) < 0 or max(values) >= p:
        raise ValueError("panel indices must be unique and in bounds")
    return np.asarray(values, dtype=int)


@dataclass
class RetainedModel:
    representation: str
    transform_mean: np.ndarray
    transform_scale: np.ndarray
    weights: np.ndarray
    centers: np.ndarray
    train_labels: np.ndarray
    ranking: list[int]
    diagnostics: dict[str, Any]

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Apply the frozen discovery transform; never fit on prediction rows.

        Raw: ``(X - mean(X_discovery)) / std(X_discovery)``.
        Squared: ``(X**2 - mean(X_discovery**2)) / std(X_discovery**2)``.
        Thus squared inputs are sign-invariant about zero in the supplied
        coordinates. For squares about a discovery-estimated raw center, the
        caller must center inputs consistently BEFORE fitting this module.
        """
        mapped = _mapped_values(X, self.representation, len(self.weights))
        with np.errstate(over="ignore", invalid="ignore"):
            transformed = (mapped - self.transform_mean) / self.transform_scale
        if not np.isfinite(transformed).all():
            raise ValueError("Frozen transformation overflowed; rescale the inputs")
        return transformed

    def predict(
        self, X: np.ndarray, panel: Sequence[int] | None = None, weighted: bool = True
    ) -> np.ndarray:
        """Nearest frozen centroid, optionally truncating features/metric.

        Full native prediction uses every positive weight. Supplying a panel
        truncates the frozen model WITHOUT reclustering or changing centroids.
        ``weighted=False`` uses unit weights on the requested coordinates and
        remains a frozen-centroid ablation. Exact distance ties choose class 0.
        """
        if not isinstance(weighted, (bool, np.bool_)):
            raise ValueError("weighted must be Boolean")
        transformed = self.transform(X)
        selected = _indices(panel, len(self.weights))
        effective_weights = self.weights[selected] if weighted else np.ones(len(selected))
        positive = effective_weights > 0
        if not np.any(positive):
            raise ValueError("The requested panel has no positive metric weights")
        selected, effective_weights = selected[positive], effective_weights[positive]
        with np.errstate(over="ignore", invalid="ignore"):
            distances = np.column_stack([
                np.square(transformed[:, selected] - self.centers[k, selected]) @ effective_weights
                for k in (0, 1)
            ])
        if not np.isfinite(distances).all():
            raise ValueError("Prediction distances overflowed; rescale the inputs")
        return np.argmin(distances, axis=1).astype(int)


@dataclass
class RetainedFit:
    models: list[RetainedModel]
    diagnostics: dict[str, Any]
    elapsed_seconds: float


def fit_retained_sparse_kmeans(
    X: np.ndarray,
    representation: str = "raw",
    max_features: int = 8,
    seed: int = 0,
    steps: int = 40,
    restarts: int = 3,
    *,
    l1_bounds: Sequence[float] | None = None,
    tolerance: float = 1e-6,
    max_seconds: float | None = None,
) -> RetainedFit:
    """Fit native weighted centroid models without labels or test-data access.

    Default L1 settings are 1.25, sqrt(min(max_features,p)), and sqrt(p),
    clipped to the feasible range, with repeated settings removed. Every bound
    receives ``restarts`` initializations. All inputs are discovery rows.

    Each final weight update is followed by a new KMeans fit in that final
    weighted geometry. Returned ``train_labels`` are recomputed by the frozen
    model's ``predict``, so the training partition and deployed rule agree.
    The final-refit cost is recorded even after a soft time budget expires.

    ``native_objective`` is weighted between-cluster sum of squares;
    ``native_ratio`` divides this by weighted total sum of squares. Neither
    quantity tests cluster existence or supplies significance calibration.
    """
    started = perf_counter()
    mapped = _mapped_values(X, representation)
    X = np.asarray(X, dtype=float)
    if len(X) < 4:
        raise ValueError("At least four discovery rows are required")
    for name, value in (("max_features", max_features), ("steps", steps), ("restarts", restarts)):
        if not isinstance(value, (int, np.integer)) or isinstance(value, (bool, np.bool_)) or value < 1:
            raise ValueError(f"{name} must be an integer >=1")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    if max_seconds is not None and (not np.isfinite(max_seconds) or max_seconds <= 0):
        raise ValueError("max_seconds must be finite and positive")

    with np.errstate(over="ignore", invalid="ignore"):
        mean, scale = mapped.mean(axis=0), mapped.std(axis=0)
    if not np.isfinite(mean).all() or not np.isfinite(scale).all():
        raise ValueError("Discovery moments overflowed; rescale the inputs")
    varying = scale > np.finfo(float).eps * np.maximum(np.abs(mean), scale)
    feature_indices = np.flatnonzero(varying)
    scale[~varying] = 1.0
    total_p = X.shape[1]
    diagnostics: dict[str, Any] = {
        "method": "retained_sparse_kmeans_diagnostic_v1",
        "status": "complete", "representation": representation,
        "transform": "standardize_raw" if representation == "raw" else "standardize_squared",
        "input_shape": list(X.shape), "seed": int(seed),
        "max_features_prefix_cap": int(max_features),
        "full_native_support_is_not_capped": True,
        "excluded_constant_features": np.flatnonzero(~varying).tolist(),
        "requested_steps_per_restart": int(steps),
        "requested_restarts_per_bound": int(restarts), "requested_restarts": 0,
        "completed_restarts": 0, "failed_restarts": 0,
        "kmeans_fits": 0, "final_kmeans_refits": 0, "lloyd_iterations": 0,
        "weight_updates": 0, "objective_evaluations": 0,
        "max_seconds": max_seconds, "l1_bounds": [], "trace": [],
        "warnings": [
            "Native objectives are not cluster-existence evidence.",
            "A prefix cap does not limit full native model support.",
            "Squared representation may erase a sign-based mean shift.",
        ],
    }
    if not len(feature_indices):
        diagnostics["status"] = "no_variable_features"
        return RetainedFit([], diagnostics, perf_counter() - started)
    Z = (mapped[:, varying] - mean[varying]) / scale[varying]
    if not np.isfinite(Z).all():
        raise ValueError("Discovery transformation overflowed; rescale the inputs")
    p = Z.shape[1]
    cap = min(max_features, p)
    if l1_bounds is None:
        bounds = sorted(set(float(np.clip(v, 1, np.sqrt(p))) for v in (1.25, np.sqrt(cap), np.sqrt(p))))
    else:
        bounds = list(dict.fromkeys(float(v) for v in l1_bounds))
        if not bounds or any(not np.isfinite(v) or not 1 <= v <= np.sqrt(p) + 1e-12 for v in bounds):
            raise ValueError("l1_bounds must be nonempty and within [1,sqrt(variable_features)]")
    diagnostics["l1_bounds"] = bounds
    diagnostics["requested_restarts"] = len(bounds) * restarts
    rng = np.random.default_rng(seed)
    total_ss = np.square(Z - Z.mean(axis=0)).sum(axis=0)
    models: list[RetainedModel] = []
    stop = False

    def kmeans_fit(weights, labels, fit_seed):
        weighted = Z * np.sqrt(weights)
        initial = "k-means++" if labels is None else np.asarray([
            weighted[labels == k].mean(axis=0) for k in (0, 1)
        ])
        fit = KMeans(n_clusters=2, n_init=1, init=initial, random_state=fit_seed,
                     max_iter=100, tol=1e-6).fit(weighted)
        diagnostics["kmeans_fits"] += 1
        diagnostics["lloyd_iterations"] += int(fit.n_iter_)
        return fit

    with threadpool_limits(limits=1):
        for bound in bounds:
            for restart in range(restarts):
                weights = np.full(p, 1 / np.sqrt(p))
                labels = None
                fit_seed = int(rng.integers(0, 2**31 - 1))
                completed = 0
                converged = False
                failed = False
                for step in range(steps):
                    if max_seconds is not None and perf_counter() - started >= max_seconds:
                        diagnostics["status"] = "time_budget_exhausted"
                        stop = True
                        break
                    fit = kmeans_fit(weights, labels, fit_seed)
                    new_labels = fit.labels_
                    if len(np.unique(new_labels)) != 2:
                        diagnostics["failed_restarts"] += 1
                        failed = True
                        break
                    scores = _between_ss(Z, new_labels)
                    new_weights = _sparse_weights(scores, bound)
                    if not np.any(new_weights > 0):
                        diagnostics["failed_restarts"] += 1
                        failed = True
                        break
                    change = float(np.linalg.norm(new_weights - weights))
                    converged = labels is not None and np.array_equal(new_labels, labels) and change <= tolerance
                    labels, weights = new_labels, new_weights
                    completed += 1
                    diagnostics["weight_updates"] += 1
                    diagnostics["objective_evaluations"] += 1
                    diagnostics["trace"].append({
                        "l1_bound": bound, "restart": restart, "step": step,
                        "stage": "alternating_update", "native_objective": float(scores @ weights),
                        "weight_change": change, "positive_weight_features": int(np.sum(weights > 0)),
                        "elapsed_seconds": perf_counter() - started,
                    })
                    if converged:
                        break
                if completed and not failed:
                    # Label and weight updates were staggered. This extra fit is
                    # essential before retaining a deployed native classifier.
                    final_fit = kmeans_fit(weights, labels, fit_seed)
                    diagnostics["final_kmeans_refits"] += 1
                    if len(np.unique(final_fit.labels_)) != 2:
                        diagnostics["failed_restarts"] += 1
                    else:
                        positive = weights > 0
                        centers = np.zeros((2, total_p))
                        # Zero-weight coordinates retain descriptive means for
                        # unweighted ablations; they do not affect native labels.
                        for k in (0, 1):
                            centers[k, feature_indices] = Z[final_fit.labels_ == k].mean(axis=0)
                        centers[:, feature_indices[positive]] = final_fit.cluster_centers_[:, positive] / np.sqrt(weights[positive])
                        full_weights = np.zeros(total_p)
                        full_weights[feature_indices] = weights
                        model = RetainedModel(
                            representation, mean.copy(), scale.copy(), full_weights,
                            centers, np.empty(0, dtype=int), [], {},
                        )
                        frozen_labels = model.predict(X)
                        if len(np.unique(frozen_labels)) != 2:
                            diagnostics["failed_restarts"] += 1
                        else:
                            scores = _between_ss(Z, frozen_labels)
                            ranking = np.lexsort((feature_indices, -scores, -weights))
                            native_objective = float(scores @ weights)
                            native_total = float(total_ss @ weights)
                            model.train_labels = frozen_labels
                            model.ranking = feature_indices[ranking].tolist()
                            model.diagnostics = {
                                "l1_bound": bound, "restart": restart, "fit_seed": fit_seed,
                                "outer_iterations": completed, "alternation_converged": bool(converged),
                                "native_objective": native_objective,
                                "native_total_ss": native_total,
                                "native_ratio": native_objective / native_total if native_total > 0 else None,
                                "weight_l1": float(weights.sum()), "weight_l2": float(np.linalg.norm(weights)),
                                "full_native_support": feature_indices[positive].tolist(),
                                "full_native_support_size": int(positive.sum()),
                                "effective_support_1e10": feature_indices[weights > 1e-10].tolist(),
                                "prefix_cap": cap, "variable_feature_count": p,
                                "child_sizes": np.bincount(frozen_labels, minlength=2).tolist(),
                                "final_refit_label_changes": int(np.sum(final_fit.labels_ != labels)),
                                "frozen_predict_roundoff_changes": int(np.sum(frozen_labels != final_fit.labels_)),
                                "final_kmeans_n_iter": int(final_fit.n_iter_),
                                "transform_fit_rows": len(X),
                            }
                            diagnostics["objective_evaluations"] += 1
                            diagnostics["completed_restarts"] += 1
                            diagnostics["trace"].append({
                                "l1_bound": bound, "restart": restart, "stage": "final_retained_model",
                                "native_objective": native_objective,
                                "native_ratio": model.diagnostics["native_ratio"],
                                "positive_weight_features": int(positive.sum()),
                                "elapsed_seconds": perf_counter() - started,
                            })
                            models.append(model)
                if stop:
                    break
            if stop:
                break
    if not models and diagnostics["status"] == "complete":
        diagnostics["status"] = "no_two_cluster_models"
    return RetainedFit(models, diagnostics, perf_counter() - started)
