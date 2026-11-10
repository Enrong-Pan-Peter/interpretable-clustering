"""Budgeted feature-set discovery, without annotations or supplied support.

All arms use the same radial predictive gain. The dependence proposal is a
development heuristic, not a new clustering or inferential guarantee.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
from time import perf_counter

import numpy as np

from .radial_panels import GaussianBackground, _matrix, fit_radial_panel
from .feature_dependence import kernel_dependence


METHODS = ("random", "random_local", "dependence_local", "shuffled_dependence_local")
ABLATION_METHODS = ("moment_best", "moment_first", "kernel_best", "kernel_first")


def squared_dependence(X):
    """Absolute correlation of squared, fit-standardized coordinates.

    Captures some radial dependencies, including negative ones. It can miss
    higher-order dependence or cancelling pairwise moments. No held-out data.
    """
    X = _matrix(X)
    scale = X.std(axis=0)
    if np.any(scale <= np.finfo(float).eps):
        raise ValueError("constant features are not supported")
    squared = ((X - X.mean(axis=0)) / scale) ** 2
    centered = squared - squared.mean(axis=0)
    norm = np.linalg.norm(centered, axis=0)
    denominator = norm[:, None] * norm[None, :]
    scores = np.divide(centered.T @ centered, denominator,
                       out=np.zeros((X.shape[1], X.shape[1])), where=denominator > 0)
    scores = np.clip(np.abs(scores), 0., 1.)
    np.fill_diagonal(scores, 0.)
    return scores


def _blocks(dependence, max_size, rng):
    """At most p growing chains; no exhaustive subset generation."""
    p = len(dependence)
    roots = rng.permutation(p)
    chains = []
    for root in roots:
        chain = [int(root)]
        while len(chain) < max_size:
            remaining = [j for j in range(p) if j not in chain]
            # Seeded ordering gives a reproducible, arbitrary tie breaker.
            remaining = rng.permutation(remaining).tolist()
            next_feature = max(remaining, key=lambda j: float(dependence[j, chain].mean()))
            chain.append(int(next_feature))
        chains.append(chain)
    # Cycle lengths, then roots: do not give early roots every budget slot.
    for size in range(2, max_size + 1):
        for chain in chains:
            yield tuple(sorted(chain[:size]))


def _neighbors(support, p, max_size, rng):
    inside = list(support)
    outside = [j for j in range(p) if j not in support]
    neighbors = []
    if len(inside) < max_size:
        neighbors.extend(tuple(sorted((*inside, j))) for j in outside)
    if len(inside) > 1:
        neighbors.extend(tuple(j for j in inside if j != removed) for removed in inside)
    neighbors.extend(tuple(sorted([j for j in inside if j != removed] + [added]))
                     for removed in inside for added in outside)
    # This enumerates one local neighborhood, not all feature subsets. Every
    # fitted neighbor consumes a slot from the same strict evaluation budget.
    rng.shuffle(neighbors)
    return neighbors


def search_feature_sets(X_fit, X_search, *, method, budget, max_size, seed, evaluate=None):
    """Return a frozen feature set selected only by search-split predictive gain.

    No case, planted dimension, annotations, oracle support, validation or test
    block is accepted by this API. Callback evaluation is for search unit tests.
    Each arm owns its own fit cache; no models/results are shared across arms.
    """
    started = perf_counter()
    X_fit, X_search = _matrix(X_fit), _matrix(X_search)
    p = X_fit.shape[1]
    if X_search.shape[1] != p or min(len(X_fit), len(X_search)) < 3:
        raise ValueError("matching feature counts and at least three rows per block required")
    if method not in METHODS + ABLATION_METHODS:
        raise ValueError(f"unknown search method: {method}")
    if not isinstance(budget, int) or budget < 1 or not isinstance(max_size, int) or not 1 <= max_size <= p:
        raise ValueError("positive integer budget and 1<=max_size<=p required")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("nonnegative integer seed required")
    available = sum(comb(p, k) for k in range(1, max_size + 1))
    if budget > available:
        raise ValueError("budget exceeds number of distinct allowed feature sets")
    rng = np.random.default_rng(seed)
    background = GaussianBackground.fit(X_fit) if evaluate is None else None
    cache, models, trace = {}, {}, []
    duplicate_requests = 0
    preprocessing_seconds = 0.
    dependence = None
    dependence_permutation = None
    dependence_metadata = None
    dependence_kind = ("kernel" if method.startswith("kernel_") else "moment"
                       if method in {"dependence_local", "shuffled_dependence_local", "moment_best", "moment_first"}
                       else "none")
    refinement = "first" if method in {"moment_first", "kernel_first"} else "none" if method == "random" else "best"
    local_steps = []

    def rank(support):
        row = cache[support]
        return row["score"], -len(support), -row["index"]

    def add(support, proposal, parent=None, move_type=None):
        nonlocal duplicate_requests
        support = tuple(sorted(support))
        if support in cache:
            duplicate_requests += 1
            return False
        if len(trace) >= budget:
            return False
        fit_started = perf_counter()
        if evaluate is None:
            model = fit_radial_panel(X_fit, support, components=2)
            score = float(np.mean(model.logpdf(X_search) - background.logpdf_panel(X_search, support)))
            models[support] = model
        else:
            score = float(evaluate(support))
        if not np.isfinite(score):
            raise ValueError(f"nonfinite feature-set score for {support}")
        row = {"index": len(trace), "support": list(support), "size": len(support),
               "score": score, "proposal": proposal, "evaluation_seconds": perf_counter() - fit_started,
               "parent_support": list(parent) if parent is not None else None, "move_type": move_type}
        cache[support] = row
        trace.append(row)
        row["best_score"] = max(record["score"] for record in trace)
        row["optimizer_success"] = bool(models[support].diagnostics["optimizer_success"]) if evaluate is None else None
        row["model"] = models[support].to_dict() if evaluate is None else None
        return True

    def random_panel():
        nonlocal duplicate_requests
        for _ in range(10000):
            size = int(rng.integers(1, max_size + 1))
            proposal = tuple(sorted(rng.choice(p, size=size, replace=False).tolist()))
            if proposal not in cache:
                return proposal
            duplicate_requests += 1
        # Tiny nearly exhausted test spaces only; random choice over remaining
        # panels preserves the intended uniform-over-available-size sampling.
        # Production searches never use this fallback (guarded by space size).
        if available <= 10000:
            remaining = {k: [s for s in combinations(range(p), k) if s not in cache]
                         for k in range(1, max_size + 1)}
            sizes = [k for k, values in remaining.items() if values]
            probabilities = np.array([len(remaining[k]) / comb(p, k) for k in sizes])
            k = int(rng.choice(sizes, p=probabilities / probabilities.sum()))
            return remaining[k][int(rng.integers(len(remaining[k])))]
        raise RuntimeError("unable to sample unseen feature set; reduce budget or increase search space")

    exploration = max(1, budget // 2)
    warmup = min(8, exploration)
    for _ in range(warmup):
        add(random_panel(), "shared_random_warmup")
    if dependence_kind != "none":
        preprocess_started = perf_counter()
        if dependence_kind == "kernel":
            dependence, dependence_metadata = kernel_dependence(X_fit)
        else:
            dependence = squared_dependence(X_fit)
            dependence_metadata = {"kind": "absolute_squared_correlation", "fit_rows": len(X_fit)}
        if method == "shuffled_dependence_local":
            # Preserve graph weights and chain construction but scramble their
            # association with the actual measurements. Data are not permuted.
            dependence_permutation = np.random.default_rng(seed + 200003).permutation(p)
            dependence = dependence[np.ix_(dependence_permutation, dependence_permutation)]
        block_rng = np.random.default_rng(seed + 100003)
        blocks = list(_blocks(dependence, max_size, block_rng))
        block_rng.shuffle(blocks)
        preprocessing_seconds = perf_counter() - preprocess_started
        for block in blocks:
            if len(trace) >= exploration:
                break
            add(block, "kernel_dependence_chain" if dependence_kind == "kernel" else "squared_dependence_chain")
    target = budget if method == "random" else exploration
    while len(trace) < target:
        add(random_panel(), "random_exploration")
    if method != "random":
        current = max(cache, key=rank)
        while len(trace) < budget:
            old = current
            for candidate in _neighbors(current, p, max_size, rng):
                move_type = "add" if len(candidate) > len(old) else "drop" if len(candidate) < len(old) else "swap"
                before, cached = current, candidate in cache
                add(candidate, "local_add_drop_swap", parent=old, move_type=move_type)
                improved = candidate in cache and rank(candidate) > rank(current)
                if improved:
                    current = candidate
                local_steps.append({"parent_support": list(old), "candidate_support": list(candidate),
                                    "incumbent_before": list(before), "incumbent_after": list(current),
                                    "cache_hit": cached, "evaluations": len(trace), "improved": improved,
                                    "move_type": move_type})
                if len(trace) >= budget or (refinement == "first" and improved):
                    break
            if current == old and len(trace) < budget:
                current = random_panel()
                add(current, "random_restart")
    selected = max(cache, key=rank)
    return {"method": method, "selected_support": list(selected), "search_gain": cache[selected]["score"],
            "selected_index": cache[selected]["index"], "trace": trace, "evaluations": len(trace),
            "budget": budget, "duplicate_requests": duplicate_requests,
            "preprocessing_seconds": preprocessing_seconds, "seconds": perf_counter() - started,
            "model": models[selected].to_dict() if evaluate is None else None,
            "background": background.to_dict() if background is not None else None,
            "dependence_matrix": dependence.tolist() if dependence is not None else None,
            "dependence_feature_permutation": dependence_permutation.tolist() if dependence_permutation is not None else None,
            "dependence_metadata": dependence_metadata, "local_steps": local_steps,
            "evaluated_size_counts": {str(k): sum(len(s) == k for s in cache) for k in range(1, max_size + 1)},
            "config": {"max_size": max_size, "min_size": 1, "seed": seed, "exploration_budget": exploration,
                       "warmup": warmup, "selection": "largest search gain; ties fewer features then first evaluated",
                       "random_distribution": "uniform size then uniform support, rejecting already evaluated feature sets",
                       "dependence_kind": dependence_kind, "refinement": refinement},
            "scope": "budgeted discovery heuristic; neither calibrated split inference nor novelty established"}


# Compatibility for archived experiments and callers; new terminology uses
# feature sets. Model class/function names in the historical fitter are stable.
search_panels = search_feature_sets
