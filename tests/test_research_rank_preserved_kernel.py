"""Constraint and deployment contracts for the isolated rank-collapse ablation."""
import inspect

import numpy as np
import pytest

import atomic_research.rank_preserved_kernel as module
from atomic_research.kernel_panels import (
    _objective_gradient, fit_kernel_panel, load_kernel_panel,
)
from atomic_research.rank_preserved_kernel import (
    fit_rank_preserved_kernel_panel, project_rank_preserved,
)


def _sample(seed=19, n=54, p=12):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    X[:n // 2, :5] += 1.5
    return X


@pytest.mark.parametrize("rank,budget", [(1, 4), (2, 6), (3, 3), (4, 8)])
def test_projection_has_requested_gram_and_only_retained_rows(rank, budget):
    matrix = np.random.default_rng(41).normal(size=(12, rank))
    expected = np.argsort(-np.linalg.norm(matrix, axis=1), kind="stable")[:budget]
    result = project_rank_preserved(matrix, budget)
    np.testing.assert_allclose(result.T @ result, np.eye(rank) / rank, atol=2e-14)
    np.testing.assert_allclose(np.linalg.svd(result, compute_uv=False), np.full(rank, 1 / np.sqrt(rank)))
    np.testing.assert_allclose(np.linalg.det(result.T @ result), (1 / rank)**rank)
    np.testing.assert_array_equal(np.flatnonzero(np.linalg.norm(result, axis=1)), np.sort(expected))
    np.testing.assert_allclose(np.linalg.norm(result), 1)


@pytest.mark.parametrize("matrix,budget", [
    (np.zeros((6, 2)), 4), (np.ones((6, 2)), 4),
    (np.eye(3), 2), (np.ones((1, 2)), 2),
    (np.full((6, 2), np.nan), 4), (np.empty((6, 0)), 4),
])
def test_projection_rejects_infeasible_or_rank_deficient_support(matrix, budget):
    with pytest.raises(ValueError):
        project_rank_preserved(matrix, budget)


@pytest.mark.parametrize("kernel", ["local", "global"])
def test_every_optimizer_projection_and_accepted_checkpoint_keeps_rank(monkeypatch, kernel):
    actual_project = module.project_rank_preserved
    captured = []

    def capture(matrix, budget):
        result = actual_project(matrix, budget)
        captured.append(result.copy())
        return result

    monkeypatch.setattr(module, "project_rank_preserved", capture)
    X = _sample()
    model = fit_rank_preserved_kernel_panel(X, budget=6, rank=2, kernel=kernel, steps=4, restarts=2)
    assert len(captured) > 2
    for matrix in captured:
        np.testing.assert_allclose(matrix.T @ matrix, np.eye(2) / 2, atol=2e-14)
        assert len(np.flatnonzero(np.linalg.norm(matrix, axis=1))) <= 6
    for checkpoint in model.diagnostics["trace"]:
        assert checkpoint["gram_error"] < 2e-14
        assert checkpoint["singular_ratio"] > 1 - 1e-12
        np.testing.assert_allclose(checkpoint["gram_determinant"], 0.25)
    np.testing.assert_allclose(model.transform_matrix.T @ model.transform_matrix, np.eye(2) / 2, atol=2e-14)
    assert 2 <= len(model.panel) <= 6
    assert model.diagnostics["reference_extension_disagreement"] == 0
    for restart in model.diagnostics["restarts"]:
        assert restart["final_loss"] <= restart["initial_loss"] + 1e-10


def test_original_initializations_are_matched_before_changed_constraint():
    X = _sample()
    old = fit_kernel_panel(X, budget=6, rank=2, kernel="global", steps=0, restarts=3, seed=5)
    new = fit_rank_preserved_kernel_panel(X, budget=6, rank=2, kernel="global", steps=0, restarts=3, seed=5)
    for a, b in zip(old.diagnostics["restarts"], new.diagnostics["restarts"]):
        assert a["initial_panel"] == b["initial_panel"]
        assert a["initialization"] == b["initialization"]
        np.testing.assert_allclose(a["initial_row_energies"], b["initial_row_energies"], atol=0, rtol=0)
    assert old.diagnostics["reference_indices"] == new.diagnostics["reference_indices"]


def test_zero_steps_is_exact_polar_transform_of_frozen_original_pca():
    X = _sample()
    old = fit_kernel_panel(X, budget=6, rank=2, kernel="global", steps=0, restarts=1, seed=7)
    new = fit_rank_preserved_kernel_panel(X, budget=6, rank=2, steps=0, restarts=1, seed=7)
    expected = project_rank_preserved(old.transform_matrix, 6)
    np.testing.assert_allclose(new.transform_matrix, expected, atol=1e-14)
    assert new.diagnostics["selected_iteration"] == 0


def test_retained_objective_uses_unchanged_original_fitness():
    X = _sample()
    model = fit_rank_preserved_kernel_panel(X, budget=6, steps=3, restarts=1)
    indices = model.diagnostics["reference_indices"]
    loss, _, _ = _objective_gradient(model.scaler.transform(X)[indices], model.transform_matrix,
                                      objective="gap_ratio", kernel="global", neighbors=7)
    np.testing.assert_allclose(model.diagnostics["loss"], loss, atol=1e-12)


def test_prediction_serialization_and_batch_contract(tmp_path):
    X = _sample()
    X[0, 1] = np.nan
    model = fit_rank_preserved_kernel_panel(X, budget=6, steps=3, restarts=1, max_samples=30)
    path = tmp_path / "rank-preserved-model.npz"
    model.save(path)
    loaded = load_kernel_panel(path)
    np.testing.assert_array_equal(loaded.predict(X), model.train_labels)
    query = _sample(seed=25, n=20)
    np.testing.assert_allclose(loaded.embed(query), model.embed(query), atol=0, rtol=0)
    predictions = model.predict(query)
    for j in range(len(query)):
        np.testing.assert_array_equal(model.predict(query[j:j+1]), predictions[j:j+1])
    outside = np.setdiff1d(np.arange(X.shape[1]), model.panel)
    altered = query.copy()
    altered[:, outside] = 1e200
    np.testing.assert_allclose(model.embed(altered), model.embed(query), atol=0, rtol=0)


def test_no_labels_or_reference_features_in_fit_api():
    parameters = inspect.signature(fit_rank_preserved_kernel_panel).parameters
    assert not (set(parameters) & {"y", "labels", "reference_panel", "test", "validation"})
    assert all(item.kind != inspect.Parameter.VAR_KEYWORD for item in parameters.values())
    with pytest.raises(TypeError):
        fit_rank_preserved_kernel_panel(_sample(), y=np.zeros(54))


@pytest.mark.parametrize("X,kwargs", [
    (np.ones((30, 5)), {"rank": 2}),
    (_sample(), {"budget": 1, "rank": 2}),
    (_sample(p=4), {"rank": 5}),
    (_sample(), {"rank": 11, "budget": 12, "max_samples": 10}),
])
def test_infeasible_rank_never_silently_reduced(X, kwargs):
    with pytest.raises(ValueError):
        fit_rank_preserved_kernel_panel(X, steps=0, restarts=1, **kwargs)
