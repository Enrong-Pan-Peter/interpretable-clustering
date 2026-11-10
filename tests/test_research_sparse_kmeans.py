"""Sparse-clustering mathematical/API checks, not efficacy benchmarks."""

import numpy as np
import pytest
from scipy.optimize import minimize

from atomic_research.sparse_kmeans import _between_ss, _sparse_weights, propose_panels


def test_sparse_weight_solver_matches_independent_constrained_optimizer():
    scores = np.array([0.4, 3.0, 1.8, 0.9, 0.2])
    for bound in (1.0, 1.3, 1.8, np.sqrt(5)):
        weights = _sparse_weights(scores, bound)
        reference = minimize(lambda w: -scores @ w, np.full(5, bound / 5),
            method="SLSQP", bounds=[(0, None)] * 5,
            constraints=[{"type": "ineq", "fun": lambda w: 1 - w @ w},
                         {"type": "ineq", "fun": lambda w: bound - w.sum()}],
            options={"ftol": 1e-11, "maxiter": 300})
        assert reference.success
        assert weights.sum() <= bound + 1e-10
        assert np.linalg.norm(weights) <= 1 + 1e-10
        np.testing.assert_allclose(scores @ weights, -reference.fun, atol=1e-7)


def test_tied_maxima_have_symmetric_feasible_optimum():
    w = _sparse_weights(np.array([3., 3., 1.]), 1.2)
    np.testing.assert_allclose(w, [0.6, 0.6, 0])
    np.testing.assert_array_equal(_sparse_weights(np.zeros(3), 1.2), np.zeros(3))


def test_between_ss_matches_total_minus_within_ss():
    X = np.random.default_rng(2).normal(size=(40, 5))
    labels = np.arange(40) % 2
    total = ((X - X.mean(0)) ** 2).sum(0)
    within = sum(((X[labels == k] - X[labels == k].mean(0)) ** 2).sum(0) for k in (0, 1))
    np.testing.assert_allclose(_between_ss(X, labels), total - within, atol=1e-12)


def test_reproducibility_feature_permutation_and_training_costs():
    X = np.random.default_rng(7).normal(size=(55, 9))
    kwargs = dict(max_features=6, seed=2, steps=10, restarts=2, l1_bounds=[1.4, 2.4])
    first, repeated = propose_panels(X, **kwargs), propose_panels(X, **kwargs)
    permutation = np.array([3, 1, 8, 0, 4, 6, 2, 7, 5])
    permuted = propose_panels(X[:, permutation], **kwargs)
    assert first.panels == repeated.panels
    mapped = {tuple(sorted(int(permutation[j]) for j in panel)) for panel in permuted.panels}
    assert set(first.panels) == mapped
    np.testing.assert_allclose([r["objective"] for r in first.trace], [r["objective"] for r in repeated.trace])
    assert first.diagnostics["completed_restarts"] == 4
    assert first.diagnostics["objective_evaluations"] == first.diagnostics["kmeans_fits"] == len(first.trace)
    assert first.diagnostics["lloyd_iterations"] >= len(first.trace)
    assert first.elapsed_seconds >= first.trace[-1]["elapsed_seconds"] > 0
    assert {len(panel) for panel in first.panels} == set(range(1, 7))
    for bound in (1.4, 2.4):
        for restart in range(2):
            objectives = [r["objective"] for r in first.trace if r["l1_bound"] == bound and r["restart"] == restart]
            assert np.all(np.diff(objectives) >= -1e-8)


def test_constants_are_excluded_and_standardization_respects_units():
    X = np.random.default_rng(9).normal(size=(35, 5))
    kwargs = dict(steps=5, restarts=1, max_features=8, seed=4)
    first = propose_panels(np.column_stack([X, np.ones(35)]), **kwargs)
    second = propose_panels(np.column_stack([X * [2, 3, 7, 4, 8] + 10, np.ones(35)]), **kwargs)
    assert first.panels == second.panels
    assert first.diagnostics["excluded_constant_features"] == [5]
    assert all(5 not in panel for panel in first.panels)
    assert propose_panels(np.ones((10, 4))).diagnostics["status"] == "no_variable_features"


@pytest.mark.parametrize("bad", [np.array([[1., np.nan]] * 5), np.ones((3, 4)), np.ones(5)])
def test_invalid_data_rejected(bad):
    with pytest.raises(ValueError):
        propose_panels(bad)
