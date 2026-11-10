"""Experimental smooth spectral *proposal* search, not a cluster-validity test.

The optimizer never receives labels. Its output is a candidate pool for an
independent panel evaluator, not a selected panel or a claim of clustering.
See ``docs/research/soft-graph-notes.md`` for the objective and limitations.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Sequence

import numpy as np
from scipy.linalg import eigh
from scipy.special import softmax
from threadpoolctl import threadpool_limits


@dataclass
class ProposalResult:
    panels: list[tuple[int, ...]]
    elapsed_seconds: float
    diagnostics: dict[str, Any]
    trace: list[dict[str, Any]]


def _distance_contraction(X: np.ndarray, edge_derivative: np.ndarray) -> np.ndarray:
    """Sum i<k of B_ik (X_ij-X_kj)^2 without allocating n*n*p values.

    ``edge_derivative`` must be symmetric. Its diagonal cancels algebraically.
    """
    return (X * X).T @ edge_derivative.sum(axis=1) - np.einsum(
        "ij,ij->j", X, edge_derivative @ X
    )


def _objective_gradient(
    X: np.ndarray,
    logits: np.ndarray,
    *,
    bandwidth: float = 0.7,
    entropy_strength: float = 0.02,
    degree_strength: float = 0.02,
    affinity_floor: float = 1e-6,
) -> tuple[float, np.ndarray, dict[str, float]]:
    """Analytic gradient with respect to logits at a simple second eigenvalue.

    X is the already scaled optimization sample. This private kernel assumes
    validated inputs. Eigenvalue multiplicity makes the objective nonsmooth;
    the returned gradient then represents the eigenvector selected by LAPACK.
    """
    n, p = X.shape
    weights = softmax(logits)
    weighted_X = X * np.sqrt(weights)
    squared_norms = np.einsum("ij,ij->i", weighted_X, weighted_X)
    distances = squared_norms[:, None] + squared_norms[None, :] - 2 * (
        weighted_X @ weighted_X.T
    )
    np.maximum(distances, 0, out=distances)  # Roundoff at coincident points.
    tau = 2.0 * bandwidth**2
    kernel = np.exp(-distances / tau)
    np.fill_diagonal(kernel, 0.0)
    affinity = kernel + affinity_floor
    np.fill_diagonal(affinity, 0.0)
    degree = affinity.sum(axis=1)
    inv_sqrt_degree = 1.0 / np.sqrt(degree)
    laplacian = np.eye(n) - affinity * np.outer(inv_sqrt_degree, inv_sqrt_degree)
    eigenvalues, eigenvectors = eigh(
        laplacian, subset_by_index=(0, 2), check_finite=False, driver="evr"
    )
    lambda2 = float(eigenvalues[1])
    # Generalized eigenvector: (D-A)v=lambda Dv, v.T D v=1.
    v = inv_sqrt_degree * eigenvectors[:, 1]
    v2 = v * v
    spectral_edge_gradient = (v[:, None] - v[None, :]) ** 2 - lambda2 * (
        v2[:, None] + v2[None, :]
    )

    # log(mean d)-mean(log d) penalizes isolated/very-low-degree vertices.
    # It reduces one degeneracy; it is not a minimum cluster-size guarantee.
    mean_degree = float(degree.mean())
    degree_penalty = float(np.log(mean_degree) - np.log(degree).mean())
    degree_derivative = (1.0 / mean_degree - 1.0 / degree) / n
    edge_gradient = spectral_edge_gradient + degree_strength * (
        degree_derivative[:, None] + degree_derivative[None, :]
    )
    weight_gradient = -_distance_contraction(X, kernel * edge_gradient) / tau

    # L1 would be constant on this simplex. Positive entropy penalization
    # encourages concentration while the simplex prevents distance collapse.
    log_weights = np.log(np.maximum(weights, np.finfo(float).tiny))
    entropy = float(-np.dot(weights, log_weights))
    entropy_denominator = float(np.log(p)) if p > 1 else 1.0
    weight_gradient -= entropy_strength * (log_weights + 1) / entropy_denominator
    loss = (
        lambda2
        + degree_strength * degree_penalty
        + entropy_strength * entropy / entropy_denominator
    )
    gradient = weights * (weight_gradient - np.dot(weights, weight_gradient))
    details = {
        "loss": float(loss),
        "lambda2": lambda2,
        "lambda2_gap": float(eigenvalues[2] - eigenvalues[1]),
        "entropy": entropy,
        "effective_features": float(np.exp(entropy)),
        "degree_penalty": degree_penalty,
        "mean_degree": mean_degree,
        "min_degree_over_mean": float(degree.min() / mean_degree),
        "floor_fraction_of_affinity": float(
            n * (n - 1) * affinity_floor / affinity.sum()
        ),
        "gradient_norm": float(np.linalg.norm(gradient)),
    }
    return float(loss), gradient, details


def propose_panels(
    X: np.ndarray,
    max_features: int = 8,
    seed: int = 0,
    steps: int = 80,
    restarts: int = 3,
    *,
    max_samples: int = 128,
    bandwidths: Sequence[float] = (0.7, 0.35, 1.4),
    entropy_strength: float = 0.02,
    degree_strength: float = 0.02,
    affinity_floor: float = 1e-6,
    learning_rate: float = 0.15,
    standardize: bool = True,
    max_seconds: float | None = None,
) -> ProposalResult:
    """Propose feature prefixes using a smooth spectral sparsity path.

    Parameters
    ----------
    X : array, shape (n_samples, n_features)
        Numeric, finite *discovery* rows only. No label or planted-panel input.
    max_features : int
        Upper candidate size, not an assumed true number of relevant features.
        Prefixes at every size 1..min(max_features, nonconstant features) are
        proposed at up to three checkpoints of each restart and deduplicated.
    max_samples : int
        Uniform row subsample bound for dense graph optimization. Subsampling
        can miss rare clusters. Standardization is fit on supplied rows only.
    bandwidths : sequence of positive floats
        Fixed kernel bandwidth per restart, cycled in the supplied order.
        Restarts therefore vary bandwidth as well as initialization by default.
    entropy_strength : float
        Final normalized entropy coefficient; ramps from zero after the first
        third of the run. Zero is a no-explicit-sparsity ablation.
    standardize : bool
        Center and divide by population standard deviations. Set False to
        preserve externally chosen feature scales (constants still excluded).
    max_seconds : float or None
        Soft total runtime cap, checked between objective evaluations. A single
        evaluation or preprocessing can overrun it; this is not a hard timeout.

    Notes
    -----
    The graph remains a complete weighted graph, not a binary kNN graph. The
    all-positive simplex fixes weight scale; an additive affinity floor guards
    against numerical disconnection. Nonconvex local optimization and rounded
    feature prefixes can both fail. No validity or panel-size decision is made.
    All preprocessing, eigensolves, updates, and proposal formation are timed.
    """
    started = perf_counter()
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 4 or X.shape[1] < 1:
        raise ValueError("X must be a 2-D matrix with >=4 rows and >=1 feature")
    if not np.isfinite(X).all():
        raise ValueError("X must be finite; impute missing data using discovery data")
    for name, value, minimum in (
        ("max_features", max_features, 1), ("steps", steps, 1),
        ("restarts", restarts, 1), ("max_samples", max_samples, 4),
    ):
        if not isinstance(value, (int, np.integer)) or isinstance(value, bool) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    bandwidths = tuple(float(value) for value in bandwidths)
    if not bandwidths or any(not np.isfinite(value) or value <= 0 for value in bandwidths):
        raise ValueError("bandwidths must contain finite positive numbers")
    for name, value in (("entropy_strength", entropy_strength), ("degree_strength", degree_strength)):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")
    if not np.isfinite(affinity_floor) or not 0 < affinity_floor < 1:
        raise ValueError("affinity_floor must be between zero and one")
    if max_seconds is not None and (not np.isfinite(max_seconds) or max_seconds <= 0):
        raise ValueError("max_seconds must be finite and positive")

    rng = np.random.default_rng(seed)
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    if not np.isfinite(mean).all() or not np.isfinite(scale).all():
        raise ValueError("Feature moments overflowed; rescale X before proposal search")
    # Relative tolerance is insensitive to a common change in measurement units.
    varying = scale > np.finfo(float).eps * np.maximum(np.abs(mean), scale)
    feature_indices = np.flatnonzero(varying)
    sample_indices = np.sort(rng.choice(X.shape[0], min(max_samples, X.shape[0]), replace=False))
    diagnostics: dict[str, Any] = {
        "method": "experimental_soft_spectral_proposals_v1",
        "status": "complete",
        "input_shape": list(X.shape),
        "sample_indices": sample_indices.tolist(),
        "excluded_constant_features": np.flatnonzero(~varying).tolist(),
        "seed": int(seed),
        "requested_restarts": restarts,
        "completed_restarts": 0,
        "objective_evaluations": 0,
        "requested_steps_per_restart": steps,
        "max_features": max_features,
        "max_samples": max_samples,
        "standardize": bool(standardize),
        "bandwidths": list(bandwidths),
        "entropy_strength": float(entropy_strength),
        "degree_strength": float(degree_strength),
        "affinity_floor": float(affinity_floor),
        "learning_rate": float(learning_rate),
        "max_seconds": max_seconds,
        "panel_sources": [],
        "restart_summaries": [],
        "warnings": [
            "Proposal loss is not evidence of clusters or biological validity.",
            "Random row subsampling may miss rare populations.",
            "Rounded unweighted panels need separate evaluation.",
        ],
    }
    if len(feature_indices) == 0:
        diagnostics["status"] = "no_variable_features"
        return ProposalResult([], perf_counter() - started, diagnostics, [])

    Z = X[np.ix_(sample_indices, feature_indices)].copy()
    Z -= mean[feature_indices]
    if standardize:
        Z /= scale[feature_indices]
    if not np.isfinite(Z).all():
        raise ValueError("Feature scaling overflowed; rescale X before proposal search")
    p = Z.shape[1]
    max_size = min(max_features, p)
    panels: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    trace: list[dict[str, Any]] = []
    checkpoints = {max(1, steps // 3), max(1, 2 * steps // 3), steps}

    def collect(logits: np.ndarray, restart: int, step: int, bandwidth: float) -> None:
        weights = softmax(logits)
        ranked = np.argsort(-weights, kind="stable")[:max_size]
        for size in range(1, max_size + 1):
            panel = tuple(sorted(int(j) for j in feature_indices[ranked[:size]]))
            if panel not in seen:
                seen.add(panel)
                panels.append(panel)
            diagnostics["panel_sources"].append({
                "panel": list(panel), "restart": restart, "step": step,
                "bandwidth": bandwidth, "prefix_size": size,
            })

    # Small dense eigensolves run much faster without BLAS oversubscription.
    # This context temporarily changes the process's BLAS thread limit.
    with threadpool_limits(limits=1, user_api="blas"):
        for restart in range(restarts):
            bandwidth = bandwidths[restart % len(bandwidths)]
            # First start is uniform (feature-permutation equivariant apart from
            # exact ties). Random restarts are equivariant only in distribution.
            logits = np.zeros(p) if restart == 0 else rng.normal(0, 0.75, p)
            adam_mean = np.zeros(p)
            adam_square = np.zeros(p)
            last_step = -1
            last_evaluated_logits = logits.copy()
            for step in range(steps + 1):
                if max_seconds is not None and perf_counter() - started >= max_seconds:
                    diagnostics["status"] = "time_budget_exhausted"
                    break
                strength = entropy_strength * max(0.0, (step / steps - 1 / 3) * 1.5)
                evaluated_at = perf_counter()
                loss, gradient, details = _objective_gradient(
                    Z, logits, bandwidth=bandwidth, entropy_strength=strength,
                    degree_strength=degree_strength, affinity_floor=affinity_floor,
                )
                diagnostics["objective_evaluations"] += 1
                if not np.isfinite(loss) or not np.isfinite(gradient).all():
                    raise FloatingPointError("Nonfinite soft-graph objective or gradient")
                last_step = step
                last_evaluated_logits = logits.copy()
                trace.append({
                    **details, "restart": restart, "step": step,
                    "bandwidth": bandwidth, "entropy_strength": float(strength),
                    "objective_evaluation": diagnostics["objective_evaluations"],
                    "evaluation_seconds": perf_counter() - evaluated_at,
                    "elapsed_seconds": perf_counter() - started,
                })
                if step in checkpoints:
                    collect(logits, restart, step, bandwidth)
                if step == steps:
                    diagnostics["completed_restarts"] += 1
                    break
                t = step + 1
                adam_mean = 0.9 * adam_mean + 0.1 * gradient
                adam_square = 0.999 * adam_square + 0.001 * gradient**2
                logits -= learning_rate * (adam_mean / (1 - 0.9**t)) / (
                    np.sqrt(adam_square / (1 - 0.999**t)) + 1e-8
                )
                logits -= logits.mean()  # Remove the irrelevant logit offset.
            if last_step >= 0:
                if last_step not in checkpoints:
                    collect(last_evaluated_logits, restart, last_step, bandwidth)
                weights = softmax(last_evaluated_logits)
                ranked = np.argsort(-weights, kind="stable")[:max(16, max_size)]
                diagnostics["restart_summaries"].append({
                    "restart": restart, "last_step": last_step,
                    "bandwidth": bandwidth, "final_loss": trace[-1]["loss"],
                    "top_features": feature_indices[ranked].tolist(),
                    "top_weights": weights[ranked].tolist(),
                    "effective_features": trace[-1]["effective_features"],
                })
            if diagnostics["status"] == "time_budget_exhausted":
                break
    diagnostics["unique_panels"] = len(panels)
    diagnostics["small_eigengap_evaluations"] = sum(t["lambda2_gap"] < 1e-8 for t in trace)
    diagnostics["floor_dominated_evaluations"] = sum(t["floor_fraction_of_affinity"] > 0.1 for t in trace)
    return ProposalResult(panels, perf_counter() - started, diagnostics, trace)
