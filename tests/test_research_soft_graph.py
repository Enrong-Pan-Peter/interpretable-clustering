"""Numerical correctness checks; these are not performance benchmarks."""

import numpy as np
import pytest

from atomic_research.soft_graph import (
    _distance_contraction,
    _objective_gradient,
    propose_panels,
)


def _standardized(seed=21, n=23, p=7):
    X = np.random.default_rng(seed).normal(size=(n, p))
    return (X - X.mean(axis=0)) / X.std(axis=0)


@pytest.mark.parametrize("bandwidth", [0.35, 1.1])
def test_full_analytic_gradient_matches_central_differences(bandwidth):
    X = _standardized()
    logits = np.array([-0.3, 0.8, 0.25, -0.5, 0.1, 0.75, -1.0])
    kwargs = dict(bandwidth=bandwidth, entropy_strength=0.07, degree_strength=0.13)
    _, analytic, details = _objective_gradient(X, logits, **kwargs)
    assert details["lambda2_gap"] > 1e-5  # Simple eigenvalue for this check.
    delta = 1e-5
    numeric = np.empty_like(logits)
    for j in range(len(logits)):
        direction = np.zeros_like(logits)
        direction[j] = delta
        plus = _objective_gradient(X, logits + direction, **kwargs)[0]
        minus = _objective_gradient(X, logits - direction, **kwargs)[0]
        numeric[j] = (plus - minus) / (2 * delta)
    np.testing.assert_allclose(analytic, numeric, atol=2e-7, rtol=1e-4)


def test_distance_contraction_equals_explicit_pair_calculation():
    X = _standardized(n=11, p=5)
    B = np.random.default_rng(5).normal(size=(11, 11))
    B = (B + B.T) / 2
    explicit = np.zeros(X.shape[1])
    for i in range(len(X)):
        for k in range(i):
            explicit += B[i, k] * (X[i] - X[k]) ** 2
    np.testing.assert_allclose(_distance_contraction(X, B), explicit, atol=1e-12)


def test_objective_and_gradient_respect_feature_permutation_and_logit_offset():
    X = _standardized()
    logits = np.random.default_rng(4).normal(size=X.shape[1])
    permutation = np.array([5, 1, 6, 3, 0, 2, 4])
    loss, gradient, _ = _objective_gradient(X, logits)
    permuted_loss, permuted_gradient, _ = _objective_gradient(
        X[:, permutation], logits[permutation] + 5
    )
    np.testing.assert_allclose(loss, permuted_loss, atol=1e-12)
    np.testing.assert_allclose(gradient[permutation], permuted_gradient, atol=1e-12)
    assert abs(gradient.sum()) < 1e-12


def test_uniform_start_proposals_respect_feature_permutation():
    X = _standardized(n=36, p=9)
    permutation = np.random.default_rng(7).permutation(X.shape[1])
    first = propose_panels(X, max_features=6, steps=12, restarts=1, seed=2)
    second = propose_panels(X[:, permutation], max_features=6, steps=12, restarts=1, seed=2)
    mapped = {tuple(sorted(int(permutation[j]) for j in panel)) for panel in second.panels}
    assert set(first.panels) == mapped


def test_proposals_cover_sizes_beyond_three_without_constants_and_account_for_work():
    X = np.column_stack([_standardized(n=34, p=10), np.ones(34)])
    result = propose_panels(X, max_features=8, steps=9, restarts=2, max_samples=24)
    assert {len(panel) for panel in result.panels} == set(range(1, 9))
    assert all(10 not in panel and len(set(panel)) == len(panel) for panel in result.panels)
    assert result.diagnostics["excluded_constant_features"] == [10]
    assert result.diagnostics["objective_evaluations"] == len(result.trace) == 20
    assert result.diagnostics["completed_restarts"] == 2
    assert len(result.diagnostics["sample_indices"]) == 24
    assert result.elapsed_seconds >= result.trace[-1]["elapsed_seconds"] > 0
    assert all(np.isfinite(row["loss"]) for row in result.trace)
    assert all(row["floor_fraction_of_affinity"] < 0.1 for row in result.trace)


def test_same_seed_reproduces_panels_and_losses():
    X = _standardized(n=25, p=6)
    first = propose_panels(X, max_features=5, steps=5, restarts=2, seed=11)
    second = propose_panels(X, max_features=5, steps=5, restarts=2, seed=11)
    assert first.panels == second.panels
    assert first.diagnostics["sample_indices"] == second.diagnostics["sample_indices"]
    np.testing.assert_allclose(
        [row["loss"] for row in first.trace],
        [row["loss"] for row in second.trace],
        rtol=1e-12, atol=1e-12,
    )


def test_affinity_floor_exposes_instead_of_hiding_kernel_underflow():
    X = np.eye(5) * 1e4
    loss, gradient, details = _objective_gradient(X, np.zeros(5), bandwidth=0.1)
    assert np.isfinite(loss) and np.isfinite(gradient).all()
    assert details["floor_fraction_of_affinity"] == pytest.approx(1.0)
    # A floor-only complete graph has no apparent disconnected components.
    assert details["lambda2"] == pytest.approx(5 / 4)


def test_constant_input_returns_no_arbitrary_panel():
    result = propose_panels(np.ones((12, 4)))
    assert result.panels == []
    assert result.diagnostics["status"] == "no_variable_features"
    assert result.diagnostics["objective_evaluations"] == 0


@pytest.mark.parametrize("kwargs", [
    {"max_features": 0}, {"max_features": 2.5}, {"steps": 0},
    {"max_samples": 3}, {"restarts": 0}, {"bandwidths": []},
    {"bandwidths": [0]}, {"affinity_floor": 0}, {"entropy_strength": -1},
    {"max_seconds": 0},
])
def test_invalid_controls_fail_visibly(kwargs):
    with pytest.raises(ValueError):
        propose_panels(_standardized(), **kwargs)


def test_nan_input_is_not_silently_imputed():
    X = _standardized()
    X[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        propose_panels(X)
