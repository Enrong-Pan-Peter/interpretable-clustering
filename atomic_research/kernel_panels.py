"""Bounded sparse-projection/kernel prototype with a retained native predictor.

This is not a reproduction of GroupFS and does not discover feature groups.
Only supplied discovery rows enter preprocessing, optimization and landmarks.
The graph score measures a spectral separation, not the existence of clusters.

The local affinity uses k-neighbor distances and need not be a PSD kernel.
Its analytic gradient includes the bandwidth derivative wherever neighbor
identities and the second/third eigenvalues are distinct. Unit self-affinities
are retained so the inductive eigenfunction extension agrees at landmarks.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.linalg import eigh
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

from .datasets import DiscoveryScaler


_AFFINITY_FLOOR = 1e-8
_SCALE_FLOOR = 1e-6
_EIGEN_EPS = 1e-6
_VARIANCE_FLOOR = 1e-6


def _distances(Z, reference=None):
    reference = Z if reference is None else reference
    distances = (np.sum(Z * Z, axis=1)[:, None]
                 + np.sum(reference * reference, axis=1)[None, :]
                 - 2 * Z @ reference.T)
    return np.maximum(distances, 0.0)


def _local_scales(distances, neighbors):
    """kth positive-distance neighbor, with deterministic duplicate handling.

    Zero-distance matches, including a reference point itself, are omitted.
    If fewer than k positive distances exist, use the furthest available one.
    This definition is identical for training and inductive query points.
    """
    positive = distances > 1e-12
    sortable = np.where(positive, distances, np.inf)
    order = np.argsort(sortable, axis=1, kind="stable")
    count = positive.sum(axis=1)
    positions = np.maximum(0, np.minimum(neighbors, count) - 1)
    indices = order[np.arange(len(distances)), positions]
    selected = distances[np.arange(len(distances)), indices]
    selected = np.where(count > 0, selected, 0.0)
    scales = np.sqrt(np.maximum(selected, _SCALE_FLOOR**2))
    differentiable = (count > 0) & (selected > _SCALE_FLOOR**2)
    return scales, indices, differentiable


def _affinity(Z, *, kernel, neighbors):
    distances = _distances(Z)
    # Matrix multiplication can leave small positive self-distances.
    np.fill_diagonal(distances, 0.0)
    if kernel == "local":
        scales, indices, differentiable = _local_scales(distances, neighbors)
        denominator = scales[:, None] * scales[None, :]
    elif kernel == "global":
        scales = np.ones(len(Z))
        indices = np.zeros(len(Z), dtype=int)
        differentiable = np.zeros(len(Z), dtype=bool)
        denominator = np.full_like(distances, 2.0)
    else:
        raise ValueError("kernel must be 'local' or 'global'")
    base = np.exp(-distances / denominator)
    affinity = base + _AFFINITY_FLOOR
    return affinity, (distances, scales, indices, differentiable, denominator, base)


def _spectral_loss(Z, *, objective="gap_ratio", kernel="local", neighbors=7,
                   degree_strength=0.02):
    """Return loss, derivative w.r.t. ordered distances, and retained graph.

    An ordered-distance derivative permits asymmetry from the directed choice
    of each row's bandwidth neighbor. Subsequent contractions symmetrize it.
    """
    if objective not in ("gap_ratio", "cut"):
        raise ValueError("objective must be 'gap_ratio' or 'cut'")
    affinity, data = _affinity(Z, kernel=kernel, neighbors=neighbors)
    distances, scales, indices, differentiable, denominator, base = data
    degree = affinity.sum(axis=1)
    inverse = 1.0 / np.sqrt(degree)
    laplacian = np.eye(len(Z)) - affinity * np.outer(inverse, inverse)
    eigenvalues, vectors = eigh(laplacian, subset_by_index=(0, 2),
                               check_finite=False, driver="evr")
    l2, l3 = float(eigenvalues[1]), float(eigenvalues[2])

    def edge_derivative(index):
        v = vectors[:, index] * inverse
        return 0.5 * ((v[:, None] - v[None, :])**2
                      - eigenvalues[index] * (v[:, None]**2 + v[None, :]**2))

    if objective == "gap_ratio":
        spectral = l2 / (l3 + _EIGEN_EPS)
        edge_gradient = (edge_derivative(1) / (l3 + _EIGEN_EPS)
                         - l2 * edge_derivative(2) / (l3 + _EIGEN_EPS)**2)
    else:
        spectral = l2
        edge_gradient = edge_derivative(1)
    degree_penalty = float(np.log(degree.mean()) - np.log(degree).mean())
    degree_derivative = (1.0 / degree.mean() - 1.0 / degree) / len(Z)
    edge_gradient += degree_strength * 0.5 * (degree_derivative[:, None]
                                             + degree_derivative[None, :])
    distance_gradient = -edge_gradient * base / denominator
    if kernel == "local":
        # Both (i,j) and (j,i) affinities depend on scale_i.
        scale_gradient = (2 * edge_gradient * base * distances / denominator).sum(1) / scales
        rows = np.flatnonzero(differentiable)
        distance_gradient[rows, indices[rows]] += scale_gradient[rows] / (2 * scales[rows])
    np.fill_diagonal(distance_gradient, 0.0)
    loss = float(spectral + degree_strength * degree_penalty)
    details = {
        "loss": loss, "spectral_score": float(spectral),
        "eigenvalues": eigenvalues.tolist(), "lambda2": l2, "lambda3": l3,
        "lambda3_minus_lambda2": l3 - l2,
        "degree_penalty": degree_penalty,
        "min_degree_over_mean": float(degree.min() / degree.mean()),
        "mean_degree": float(degree.mean()),
        "projected_variance": float(np.var(Z, axis=0).sum()),
        "affinity_floor_fraction": float(_AFFINITY_FLOOR * len(Z)**2 / affinity.sum()),
    }
    graph = {"degree": degree, "vectors": vectors[:, :2],
             "eigenvalues": eigenvalues, "scales": scales}
    return loss, distance_gradient, details, graph


def _objective_gradient(X, transform_matrix, *, objective="gap_ratio", kernel="local",
                        neighbors=7, degree_strength=0.02):
    """Analytic loss/gradient for a signed linear projection; no stop-gradient.

    This private function is also tested against central finite differences.
    """
    Z = X @ transform_matrix
    loss, derivative, details, _ = _spectral_loss(
        Z, objective=objective, kernel=kernel, neighbors=neighbors,
        degree_strength=degree_strength)
    symmetric = derivative + derivative.T
    grad_Z = 2 * (symmetric.sum(1)[:, None] * Z - symmetric @ Z)
    return loss, X.T @ grad_Z, details


def _metric_objective_gradient(X, weights, *, objective="gap_ratio", kernel="local",
                               neighbors=7, degree_strength=0.02):
    """Derivative w.r.t. squared diagonal metric weights, including zeros."""
    Z = X * np.sqrt(np.maximum(weights, 0.0))
    loss, derivative, details, _ = _spectral_loss(
        Z, objective=objective, kernel=kernel, neighbors=neighbors,
        degree_strength=degree_strength)
    symmetric = derivative + derivative.T
    gradient = ((X * X).T @ symmetric.sum(1)
                - np.einsum("ij,ij->j", X, symmetric @ X))
    return loss, gradient, details


def _project_rows(matrix, budget):
    norms = np.linalg.norm(matrix, axis=1)
    keep = np.argsort(-norms, kind="stable")[:budget]
    result = np.zeros_like(matrix)
    result[keep] = matrix[keep]
    norm = np.linalg.norm(result)
    if norm <= 1e-14:
        result[keep[0], 0] = 1.0
    else:
        result /= norm
    return result


def _project_metric(weights, budget):
    """Euclidean projection onto a simplex with at most budget active rows."""
    keep = np.argsort(-weights, kind="stable")[:budget]
    selected = weights[keep]
    sorted_values = np.sort(selected)[::-1]
    threshold = (np.cumsum(sorted_values) - 1) / np.arange(1, len(selected) + 1)
    last = np.flatnonzero(sorted_values > threshold)[-1]
    result = np.zeros_like(weights)
    result[keep] = np.maximum(selected - threshold[last], 0.0)
    return result


def _row_normalize(X):
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(norms, 1e-14)


def _native_state(Z, *, objective, kernel, neighbors, seed):
    loss, _, details, graph = _spectral_loss(
        Z, objective=objective, kernel=kernel, neighbors=neighbors)
    embedding = _row_normalize(graph["vectors"])
    # A constant affinity has no usable nontrivial eigenfunction. Keeping a
    # constant predictor permits explicit audit while declaring the fit invalid.
    mu = 1 - graph["eigenvalues"][:2]
    usable = bool(mu[1] > 1e-7 and details["projected_variance"] >= _VARIANCE_FLOOR)
    if usable:
        kmeans = KMeans(n_clusters=2, n_init=5, random_state=seed).fit(embedding)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
    else:
        centers = np.repeat(embedding.mean(0, keepdims=True), 2, axis=0)
        labels = np.zeros(len(Z), dtype=int)
    counts = np.bincount(labels, minlength=2)
    min_size = max(5, int(np.ceil(0.05 * len(Z))))
    valid = usable and bool(counts.min() >= min_size)
    details.update({"valid": valid, "reference_child_sizes": counts.tolist(),
                    "minimum_reference_child_size": min_size,
                    "effective_rank": int(np.linalg.matrix_rank(Z - Z.mean(0))),
                    "status": "complete" if valid else "invalid_partition"})
    return loss, graph, centers, details


@dataclass
class KernelPanelModel:
    panel: tuple[int, ...]
    transform_matrix: np.ndarray
    train_labels: np.ndarray
    scaler: DiscoveryScaler
    reference_projection: np.ndarray
    reference_scales: np.ndarray
    reference_degree: np.ndarray
    reference_vectors: np.ndarray
    adjacency_eigenvalues: np.ndarray
    centers: np.ndarray
    kernel: str
    neighbors: int
    diagnostics: dict

    def _transform(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != self.transform_matrix.shape[0]:
            raise ValueError("X must have the same original columns used for fitting")
        # Restrict multiplication to the actual panel: discarded columns cannot
        # affect assignment, including when their observed values are enormous.
        indices = np.asarray(self.panel, dtype=int)
        if len(indices) == 0:
            return np.zeros((len(X), self.transform_matrix.shape[1]))
        values = np.where(np.isfinite(X[:, indices]), X[:, indices], self.scaler.median[indices])
        values = (values - self.scaler.mean[indices]) / self.scaler.scale[indices]
        return values @ self.transform_matrix[indices]

    def embed(self, X):
        """Frozen two-dimensional graph embedding; no new-batch fitting."""
        Z = self._transform(X)
        if len(Z) == 0:
            return np.empty((0, 2))
        distances = _distances(Z, self.reference_projection)
        if self.kernel == "local":
            scales, _, _ = _local_scales(distances, self.neighbors)
            denominator = scales[:, None] * self.reference_scales[None, :]
        else:
            denominator = 2.0
        affinity = np.exp(-distances / denominator) + _AFFINITY_FLOOR
        degree = affinity.sum(1)
        normalized = affinity / np.sqrt(degree[:, None] * self.reference_degree[None, :])
        safe_eigenvalues = np.where(np.abs(self.adjacency_eigenvalues) > 1e-7,
                                    self.adjacency_eigenvalues, np.inf)
        extension = (normalized @ self.reference_vectors) / safe_eigenvalues
        return _row_normalize(extension)

    def predict(self, X):
        embedding = self.embed(X)
        distances = ((embedding[:, None, :] - self.centers[None, :, :])**2).sum(2)
        return distances.argmin(1).astype(int)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Opening explicitly prevents numpy silently appending an extension.
        with path.open("wb") as stream:
            np.savez_compressed(
                stream, schema_version=np.asarray(1), panel=np.asarray(self.panel, dtype=int),
                transform_matrix=self.transform_matrix, train_labels=self.train_labels,
                scaler_median=self.scaler.median, scaler_mean=self.scaler.mean,
                scaler_scale=self.scaler.scale, reference_projection=self.reference_projection,
                reference_scales=self.reference_scales, reference_degree=self.reference_degree,
                reference_vectors=self.reference_vectors, adjacency_eigenvalues=self.adjacency_eigenvalues,
                centers=self.centers, kernel=np.asarray(self.kernel), neighbors=np.asarray(self.neighbors),
                diagnostics_json=np.asarray(json.dumps(self.diagnostics, allow_nan=False)))

    @classmethod
    def load(cls, path):
        return load_kernel_panel(path)


def load_kernel_panel(path):
    with np.load(path, allow_pickle=False) as data:
        if int(data["schema_version"]) != 1:
            raise ValueError("Unsupported kernel-panel model schema")
        scaler = DiscoveryScaler()
        for attribute in ("median", "mean", "scale"):
            setattr(scaler, attribute, data["scaler_" + attribute].copy())
        arrays = {key: data[key].copy() for key in (
            "transform_matrix", "train_labels", "reference_projection", "reference_scales",
            "reference_degree", "reference_vectors", "adjacency_eigenvalues", "centers")}
        return KernelPanelModel(
            panel=tuple(int(j) for j in data["panel"]), scaler=scaler,
            kernel=str(data["kernel"]), neighbors=int(data["neighbors"]),
            diagnostics=json.loads(str(data["diagnostics_json"])), **arrays)


def _validate_inputs(X, *, budget, rank, steps, restarts, neighbors, max_samples, kernel, objective,
                     seed):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 10 or X.shape[1] < 1:
        raise ValueError("X must be a 2-D matrix with >=10 rows and >=1 column")
    for name, value, minimum in (("budget", budget, 1), ("rank", rank, 1),
                                 ("steps", steps, 0), ("restarts", restarts, 1),
                                 ("neighbors", neighbors, 1), ("max_samples", max_samples, 10)):
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if kernel not in ("local", "global"):
        raise ValueError("kernel must be 'local' or 'global'")
    if objective not in ("gap_ratio", "cut"):
        raise ValueError("objective must be 'gap_ratio' or 'cut'")
    if (isinstance(seed, bool) or not isinstance(seed, (int, np.integer))
            or not 0 <= seed < 2**32):
        raise ValueError("seed must be an integer between 0 and 2**32-1")
    return X


def _prepare(X, seed, max_samples):
    scaler = DiscoveryScaler().fit(X)
    scaled = scaler.transform(X)
    if not np.isfinite(scaled).all():
        raise ValueError("Feature moments overflowed; rescale supplied data first")
    varying = np.var(scaled, axis=0) > 1e-14
    indices = np.sort(np.random.default_rng(seed).choice(len(X), min(len(X), max_samples), replace=False))
    return scaler, scaled, varying, indices


def _build_model(X, scaler, scaled, indices, transform, *, objective, kernel, neighbors, seed, diagnostics):
    Z = scaled[indices] @ transform
    _, graph, centers, details = _native_state(
        Z, objective=objective, kernel=kernel, neighbors=neighbors, seed=seed)
    panel = tuple(int(j) for j in np.flatnonzero(np.linalg.norm(transform, axis=1) > 1e-12))
    diagnostics = {**diagnostics, **details, "panel": list(panel), "active_size": len(panel),
                   "reference_indices": indices.tolist(), "kernel": kernel, "objective": objective,
                   "neighbors": int(neighbors), "reference_rows": len(indices),
                   "projection_columns": transform.shape[1],
                   "projection_frobenius_norm": float(np.linalg.norm(transform)),
                   "projection_singular_values": np.linalg.svd(transform, compute_uv=False).tolist(),
                   "original_input_shape": list(X.shape),
                   "assignment": "frozen normalized-graph extension and nearest spectral center",
                   "warnings": ["Spectral separation is not evidence that multiple populations exist.",
                                "Local self-tuned affinity need not be a positive semidefinite kernel.",
                                "Sparse projections can retain nonlinear decision boundaries; a short rule needs a separate fidelity audit.",
                                "Discovery landmark sampling can miss rare populations."]}
    model = KernelPanelModel(
        panel=panel, transform_matrix=transform, train_labels=np.empty(0, dtype=int), scaler=scaler,
        reference_projection=Z, reference_scales=graph["scales"], reference_degree=graph["degree"],
        reference_vectors=graph["vectors"], adjacency_eigenvalues=1 - graph["eigenvalues"][:2],
        centers=centers, kernel=kernel, neighbors=neighbors, diagnostics=diagnostics)
    model.train_labels = model.predict(X)
    fitted_labels = (( _row_normalize(graph["vectors"])[:, None, :] - centers[None, :, :])**2).sum(2).argmin(1)
    diagnostics["reference_extension_disagreement"] = int(np.sum(model.train_labels[indices] != fitted_labels))
    diagnostics["all_discovery_child_sizes"] = np.bincount(model.train_labels, minlength=2).tolist()
    return model


def fit_frozen_kernel_panel(X, panel, transform_matrix=None, *, kernel="local", neighbors=7,
                            seed=0, max_samples=200):
    """Fit native assignment on a supplied support/transform, without selecting it.

    This supports identity-on-the-same-panel and externally supplied panel
    diagnostics. A supplied oracle panel must be labelled as an oracle by the
    caller; this function cannot make such a panel an autonomous discovery.
    """
    X = _validate_inputs(X, budget=1, rank=1, steps=0, restarts=1,
                         neighbors=neighbors, max_samples=max_samples, kernel=kernel,
                         objective="gap_ratio", seed=seed)
    panel = tuple(panel)
    if any(isinstance(j, bool) or not isinstance(j, (int, np.integer)) for j in panel):
        raise ValueError("panel must contain integer feature indices")
    panel = tuple(int(j) for j in panel)
    if not panel or len(set(panel)) != len(panel) or min(panel) < 0 or max(panel) >= X.shape[1]:
        raise ValueError("panel must contain unique valid original feature indices")
    scaler, scaled, varying, indices = _prepare(X, seed, max_samples)
    if transform_matrix is None:
        transform = np.zeros((X.shape[1], len(panel)))
        transform[np.asarray(panel), np.arange(len(panel))] = 1 / np.sqrt(len(panel))
    else:
        transform = np.asarray(transform_matrix, dtype=float).copy()
        if transform.ndim != 2 or transform.shape[0] != X.shape[1] or transform.shape[1] < 1:
            raise ValueError("transform_matrix must have shape (original columns, projection columns)")
        if not np.isfinite(transform).all() or np.linalg.norm(transform) <= 1e-14:
            raise ValueError("transform_matrix must be finite and nonzero")
        if np.any(transform[np.setdiff1d(np.arange(X.shape[1]), panel)] != 0):
            raise ValueError("transform_matrix uses columns outside the supplied panel")
    with threadpool_limits(limits=1):
        return _build_model(X, scaler, scaled, indices, transform, objective="gap_ratio", kernel=kernel,
                            neighbors=neighbors, seed=seed, diagnostics={
                                "method": "frozen_kernel_panel_diagnostic_v1", "seed": int(seed),
                                "selection": "supplied_panel", "excluded_constant_features": np.flatnonzero(~varying).tolist()})


def fit_kernel_panel(X, *, budget=8, rank=2, mixing=True, objective="gap_ratio", kernel="local",
                      seed=0, steps=60, restarts=3, neighbors=7, max_samples=200):
    """Fit a sparse original-feature projection and retain its native predictor.

    ``mixing=True`` learns a signed p-by-r matrix under unit Frobenius norm and
    a hard row-support budget. ``mixing=False`` learns diagonal squared metric
    weights on a sparse simplex. Zero-weight coordinates can re-enter either
    optimization. Rank is an upper bound only, not an orthogonality constraint.

    Dense graph work uses at most ``max_samples`` uniformly sampled discovery
    rows. All feature moments use the supplied discovery rows. No panel/label
    truth or held-out rows are accepted. The score is piecewise differentiable,
    the optimizer is local, and the minimum child-size gate is not a test of
    cluster existence. An inadmissible fit is explicitly reported as invalid.
    """
    started = perf_counter()
    X = _validate_inputs(X, budget=budget, rank=rank, steps=steps, restarts=restarts,
                         neighbors=neighbors, max_samples=max_samples, kernel=kernel,
                         objective=objective, seed=seed)
    if not isinstance(mixing, (bool, np.bool_)):
        raise ValueError("mixing must be a boolean")
    scaler, scaled, varying, indices = _prepare(X, seed, max_samples)
    columns = np.flatnonzero(varying)
    p = len(columns)
    rng = np.random.default_rng(seed + 7919)
    budget_actual = min(budget, p)
    rank_actual = min(rank, max(p, 1), len(indices))
    trace = []
    diagnostics = {"method": "sparse_native_kernel_panel_prototype_v1", "seed": int(seed),
                   "mixing": bool(mixing), "requested_budget": int(budget), "requested_rank": int(rank),
                   "requested_steps": int(steps), "requested_restarts": int(restarts),
                   "excluded_constant_features": np.flatnonzero(~varying).tolist(),
                   "objective_evaluations": 0, "restarts": [], "trace": trace}
    if p == 0:
        transform = np.zeros((X.shape[1], rank_actual))
        with threadpool_limits(limits=1):
            model = _build_model(X, scaler, scaled, indices, transform, objective=objective, kernel=kernel,
                                 neighbors=neighbors, seed=seed, diagnostics=diagnostics)
        model.diagnostics.update(status="no_variable_features", valid=False,
                                 elapsed_seconds=float(perf_counter() - started))
        return model
    optimization_X = scaled[np.ix_(indices, columns)]
    best = None
    best_valid = None

    def matrix_from(parameter):
        if mixing:
            return parameter
        active = np.flatnonzero(parameter > 1e-14)
        matrix = np.zeros((p, len(active)))
        matrix[active, np.arange(len(active))] = np.sqrt(parameter[active])
        return matrix

    def evaluate(parameter):
        diagnostics["objective_evaluations"] += 1
        function = _objective_gradient if mixing else _metric_objective_gradient
        return function(optimization_X, parameter, objective=objective, kernel=kernel, neighbors=neighbors)

    def consider(parameter, restart, iteration):
        nonlocal best, best_valid
        matrix = matrix_from(parameter)
        loss, _, _, details = _native_state(optimization_X @ matrix, objective=objective,
                                           kernel=kernel, neighbors=neighbors, seed=seed)
        candidate = (loss, matrix.copy(), restart, iteration)
        if best is None or loss < best[0]:
            best = candidate
        if details["valid"] and (best_valid is None or loss < best_valid[0]):
            best_valid = candidate
        return details

    with threadpool_limits(limits=1):
        # The first support comes from discovery-only PCA. The remaining starts
        # use a common random signed matrix in both variants. Row energies and
        # support therefore match before testing signed mixing vs a diagonal
        # metric, avoiding an initialization change hidden inside that ablation.
        _, _, right_vectors = np.linalg.svd(
            optimization_X - optimization_X.mean(0), full_matrices=False)
        pca_start = _project_rows(right_vectors[:rank_actual].T, budget_actual)
        for restart in range(restarts):
            start_matrix = pca_start if restart == 0 else _project_rows(
                rng.normal(size=(p, rank_actual)), budget_actual)
            if mixing:
                parameter = start_matrix.copy()
            else:
                parameter = np.sum(start_matrix**2, axis=1)
            initialization = "discovery_pca_rows" if restart == 0 else "random_signed_rows"
            initial_support = set(np.flatnonzero(np.linalg.norm(matrix_from(parameter), axis=1) > 1e-12))
            previous_support = initial_support
            support_change_steps = 0
            feature_entries = 0
            loss, gradient, details = evaluate(parameter)
            initial_loss = loss
            native = consider(parameter, restart, 0)
            trace.append({"restart": restart, "iteration": 0, "loss": float(loss),
                          "active_size": int(np.count_nonzero(np.linalg.norm(matrix_from(parameter), axis=1) > 1e-12)),
                          "initialization": initialization,
                          "initial_panel": columns[sorted(initial_support)].tolist(),
                          "initial_row_energies": np.sum(start_matrix**2, axis=1).tolist(),
                          "valid_checkpoint": bool(native["valid"])})
            step_size = 0.2 / max(float(np.linalg.norm(gradient)), 1e-8)
            status = "steps_complete"
            accepted = 0
            for iteration in range(1, steps + 1):
                if np.linalg.norm(gradient) < 1e-9:
                    status = "gradient_stalled"
                    break
                success = False
                for _ in range(10):
                    proposal = parameter - step_size * gradient
                    proposal = _project_rows(proposal, budget_actual) if mixing else _project_metric(proposal, budget_actual)
                    candidate_loss, candidate_gradient, candidate_details = evaluate(proposal)
                    if candidate_loss < loss - 1e-10:
                        success = True
                        break
                    step_size *= 0.5
                if not success:
                    status = "line_search_stalled"
                    break
                parameter, loss, gradient, details = proposal, candidate_loss, candidate_gradient, candidate_details
                accepted += 1
                support = set(np.flatnonzero(np.linalg.norm(matrix_from(parameter), axis=1) > 1e-12))
                support_change_steps += int(support != previous_support)
                feature_entries += len(support - previous_support)
                previous_support = support
                step_size = min(step_size * 1.3, 10.0)
                # Check each accepted state: a low-loss tiny-island state must
                # not displace an admissible earlier native partition.
                native = consider(parameter, restart, iteration)
                trace.append({"restart": restart, "iteration": iteration, "loss": float(loss),
                              "active_size": int(np.count_nonzero(np.linalg.norm(matrix_from(parameter), axis=1) > 1e-12)),
                              "support_change_steps": support_change_steps,
                              "feature_entries": feature_entries,
                              "valid_checkpoint": bool(native["valid"])})
            diagnostics["restarts"].append({"restart": restart, "initial_loss": float(initial_loss),
                                             "final_loss": float(loss), "accepted_steps": accepted,
                                             "initialization": initialization,
                                             "initial_panel": columns[sorted(initial_support)].tolist(),
                                             "initial_row_energies": np.sum(start_matrix**2, axis=1).tolist(),
                                             "final_panel": columns[sorted(previous_support)].tolist(),
                                             "support_change_steps": support_change_steps,
                                             "feature_entries": feature_entries, "status": status})
        chosen = best_valid if best_valid is not None else best
        transform = np.zeros((X.shape[1], chosen[1].shape[1]))
        transform[columns] = chosen[1]
        diagnostics.update(selected_restart=int(chosen[2]), selected_iteration=int(chosen[3]),
                           selected_initialization=diagnostics["restarts"][chosen[2]]["initialization"],
                           selection="lowest_discovery_loss_among_admissible_native_checkpoints"
                           if best_valid is not None else "no_admissible_checkpoint")
        model = _build_model(X, scaler, scaled, indices, transform, objective=objective, kernel=kernel,
                             neighbors=neighbors, seed=seed, diagnostics=diagnostics)
    model.diagnostics["elapsed_seconds"] = float(perf_counter() - started)
    return model
