"""One-constraint ablation for the historical sparse kernel-panel prototype.

The spectral objective, preprocessing, landmark sampling, native prediction and
admissibility gate are imported unchanged from ``kernel_panels``. The changed
constraint is A.T @ A = I/r, imposed after row-support selection on every step.
This prevents collapse of the transformation's singular values; it does not
guarantee that the transformed data have full rank or useful clusters.
"""
from __future__ import annotations

from time import perf_counter

import numpy as np
from threadpoolctl import threadpool_limits

from .kernel_panels import (
    _build_model, _native_state, _objective_gradient, _prepare, _project_rows,
    _validate_inputs,
)


def project_rank_preserved(matrix, budget):
    """Select largest row norms, then use their full-rank scaled polar factor.

    This is a support-selection heuristic followed by the exact nearest polar
    factor on that support, not an exact global sparse-Stiefel projection.
    Rank-deficient retained rows raise ValueError; no silent rank repair occurs.
    """
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or not matrix.shape[1] or not np.isfinite(matrix).all():
        raise ValueError("matrix must be a finite 2-D array with at least one column")
    p, rank = matrix.shape
    if (isinstance(budget, bool) or not isinstance(budget, (int, np.integer))
            or budget < rank or p < rank):
        raise ValueError("budget and available rows must be at least the requested rank")
    keep = np.argsort(-np.linalg.norm(matrix, axis=1), kind="stable")[:min(budget, p)]
    left, singular, right = np.linalg.svd(matrix[keep], full_matrices=False)
    if singular[0] <= 1e-14 or singular[-1] <= 1e-12 * singular[0]:
        raise ValueError("retained row support is rank deficient")
    result = np.zeros_like(matrix)
    result[keep] = (left @ right) / np.sqrt(rank)
    return result


def _constraint_details(matrix):
    rank = matrix.shape[1]
    singular = np.linalg.svd(matrix, compute_uv=False)
    gram = matrix.T @ matrix
    return {
        "projection_singular_values": singular.tolist(),
        "singular_ratio": float(singular[-1] / singular[0]),
        "gram_error": float(np.max(np.abs(gram - np.eye(rank) / rank))),
        "gram_determinant": float(np.linalg.det(gram)),
    }


def fit_rank_preserved_kernel_panel(X, *, budget=16, rank=2, kernel="global", seed=0,
                                     steps=60, restarts=3, neighbors=7, max_samples=200):
    """Optimize the original gap-ratio fitness with a fixed-rank transformation.

    All supplied rows must be discovery data. No labels or truth panels are
    accepted. Steps=0 and restarts=1 gives a frozen, constrained PCA start.
    The original PCA/random starts are computed before the changed projection,
    allowing direct initialization matching to ``fit_kernel_panel``. A rank-
    deficient start is skipped and reported; every deficient line-search
    proposal is rejected and counted. If every start fails, raise ValueError.
    """
    started = perf_counter()
    X = _validate_inputs(X, budget=budget, rank=rank, steps=steps, restarts=restarts,
                         neighbors=neighbors, max_samples=max_samples, kernel=kernel,
                         objective="gap_ratio", seed=seed)
    if budget < rank:
        raise ValueError("budget must be at least rank")
    scaler, scaled, varying, indices = _prepare(X, seed, max_samples)
    columns = np.flatnonzero(varying)
    if len(columns) < rank:
        raise ValueError("fewer varying original features than the requested rank")
    if len(indices) < rank:
        raise ValueError("fewer reference rows than the requested rank")
    p, budget_actual = len(columns), min(budget, len(columns))
    optimization_X = scaled[np.ix_(indices, columns)]
    rng = np.random.default_rng(seed + 7919)
    diagnostics = {
        "method": "rank_preserved_native_kernel_panel_v1", "seed": int(seed),
        "mixing": True, "requested_budget": int(budget), "requested_rank": int(rank),
        "requested_steps": int(steps), "requested_restarts": int(restarts),
        "constraint": "A.T @ A = I / rank; at most budget nonzero rows",
        "excluded_constant_features": np.flatnonzero(~varying).tolist(),
        "objective_evaluations": 0, "rank_deficient_proposals": 0,
        "restarts": [], "trace": [],
    }
    best = best_valid = None

    def evaluate(matrix):
        diagnostics["objective_evaluations"] += 1
        return _objective_gradient(optimization_X, matrix, objective="gap_ratio",
                                   kernel=kernel, neighbors=neighbors)

    def panel(matrix):
        return set(np.flatnonzero(np.linalg.norm(matrix, axis=1) > 1e-12))

    def consider(matrix, restart, iteration, loss, initialization):
        nonlocal best, best_valid
        native_loss, _, _, native = _native_state(
            optimization_X @ matrix, objective="gap_ratio", kernel=kernel,
            neighbors=neighbors, seed=seed)
        candidate = (native_loss, matrix.copy(), restart, iteration, initialization)
        if best is None or native_loss < best[0]:
            best = candidate
        if native["valid"] and (best_valid is None or native_loss < best_valid[0]):
            best_valid = candidate
        entry = {"restart": restart, "iteration": iteration, "loss": float(loss),
                 "panel": columns[sorted(panel(matrix))].tolist(), "active_size": len(panel(matrix)),
                 "valid_checkpoint": bool(native["valid"]), **_constraint_details(matrix)}
        diagnostics["trace"].append(entry)
        return entry

    with threadpool_limits(limits=1):
        _, _, right_vectors = np.linalg.svd(
            optimization_X - optimization_X.mean(0), full_matrices=False)
        pca_start = _project_rows(right_vectors[:rank].T, budget_actual)
        for restart in range(restarts):
            original_start = pca_start if restart == 0 else _project_rows(
                rng.normal(size=(p, rank)), budget_actual)
            initialization = "discovery_pca_rows" if restart == 0 else "random_signed_rows"
            record = {"restart": restart, "initialization": initialization,
                      "initial_panel": columns[sorted(panel(original_start))].tolist(),
                      "initial_row_energies": np.sum(original_start**2, axis=1).tolist(),
                      "rank_deficient_proposals": 0}
            try:
                matrix = project_rank_preserved(original_start, budget_actual)
            except ValueError as error:
                record.update(status="rank_deficient_initialization", reason=str(error), accepted_steps=0)
                diagnostics["restarts"].append(record)
                continue
            record["constrained_initial_row_energies"] = np.sum(matrix**2, axis=1).tolist()
            loss, gradient, _ = evaluate(matrix)
            record["initial_loss"] = float(loss)
            consider(matrix, restart, 0, loss, initialization)
            previous_support = panel(matrix)
            step_size = 0.2 / max(float(np.linalg.norm(gradient)), 1e-8)
            status, accepted, support_changes, feature_entries = "steps_complete", 0, 0, 0
            for iteration in range(1, steps + 1):
                if np.linalg.norm(gradient) < 1e-9:
                    status = "gradient_stalled"
                    break
                success = False
                for _ in range(10):
                    try:
                        proposal = project_rank_preserved(matrix - step_size * gradient, budget_actual)
                    except ValueError:
                        diagnostics["rank_deficient_proposals"] += 1
                        record["rank_deficient_proposals"] += 1
                        step_size *= 0.5
                        continue
                    candidate_loss, candidate_gradient, _ = evaluate(proposal)
                    if candidate_loss < loss - 1e-10:
                        success = True
                        break
                    step_size *= 0.5
                if not success:
                    status = "line_search_stalled"
                    break
                matrix, loss, gradient = proposal, candidate_loss, candidate_gradient
                accepted += 1
                support = panel(matrix)
                support_changes += int(support != previous_support)
                feature_entries += len(support - previous_support)
                previous_support = support
                step_size = min(step_size * 1.3, 10.0)
                entry = consider(matrix, restart, iteration, loss, initialization)
                entry.update(support_change_steps=support_changes, feature_entries=feature_entries)
            record.update(final_loss=float(loss), accepted_steps=accepted, status=status,
                          final_panel=columns[sorted(previous_support)].tolist(),
                          support_change_steps=support_changes, feature_entries=feature_entries,
                          **_constraint_details(matrix))
            diagnostics["restarts"].append(record)
        if best is None:
            raise ValueError("All requested starts have rank-deficient retained row supports")
        chosen = best_valid if best_valid is not None else best
        transform = np.zeros((X.shape[1], rank))
        transform[columns] = chosen[1]
        diagnostics.update(
            selected_restart=int(chosen[2]), selected_iteration=int(chosen[3]),
            selected_initialization=chosen[4],
            selection="lowest_discovery_loss_among_admissible_native_checkpoints"
            if best_valid is not None else "no_admissible_checkpoint", **_constraint_details(transform))
        model = _build_model(X, scaler, scaled, indices, transform, objective="gap_ratio",
                             kernel=kernel, neighbors=neighbors, seed=seed, diagnostics=diagnostics)
    model.diagnostics["elapsed_seconds"] = float(perf_counter() - started)
    return model
