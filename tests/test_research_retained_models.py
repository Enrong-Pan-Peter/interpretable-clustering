"""Correctness of retained states and deployment, not clustering efficacy."""

import inspect

import numpy as np
import pytest

from atomic_research.retained_models import fit_retained_sparse_kmeans


def _sample(seed=5, n=60, p=8):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    X[: n // 2, :3] += 2.0
    return X


@pytest.mark.parametrize("representation", ["raw", "squared"])
def test_final_labels_equal_frozen_predict_and_objective_uses_final_state(representation):
    X = _sample()
    result = fit_retained_sparse_kmeans(X, representation=representation, steps=4, restarts=2)
    assert result.models
    for model in result.models:
        np.testing.assert_array_equal(model.train_labels, model.predict(X))
        Z = model.transform(X)
        manual = np.argmin(np.stack([
            ((Z - model.centers[k])**2 * model.weights).sum(axis=1) for k in (0, 1)
        ]), axis=0)
        np.testing.assert_array_equal(manual, model.train_labels)
        # The retained native centers must come from a fit in final weights,
        # not the stale centroids preceding the last alternating weight update.
        positive = model.weights > 0
        for k in (0, 1):
            np.testing.assert_allclose(
                model.centers[k, positive], Z[model.train_labels == k][:, positive].mean(0),
                atol=1e-10, rtol=1e-10,
            )
        bss = sum(
            np.sum(model.train_labels == k) * (Z[model.train_labels == k].mean(0) - Z.mean(0))**2
            for k in (0, 1)
        )
        tss = ((Z - Z.mean(0))**2).sum(0)
        np.testing.assert_allclose(bss @ model.weights, model.diagnostics["native_objective"])
        np.testing.assert_allclose((bss @ model.weights)/(tss @ model.weights), model.diagnostics["native_ratio"])
        assert 0 <= model.diagnostics["native_ratio"] <= 1 + 1e-12
        assert model.weights.sum() <= model.diagnostics["l1_bound"] + 1e-10
        assert np.linalg.norm(model.weights) <= 1 + 1e-10
    assert result.diagnostics["completed_restarts"] == len(result.models)
    assert result.diagnostics["final_kmeans_refits"] == len(result.models)
    assert result.diagnostics["kmeans_fits"] == result.diagnostics["weight_updates"] + len(result.models)
    assert result.diagnostics["objective_evaluations"] == len(result.diagnostics["trace"])
    assert result.elapsed_seconds >= result.diagnostics["trace"][-1]["elapsed_seconds"]


@pytest.mark.parametrize("representation", ["raw", "squared"])
def test_transform_uses_discovery_moments_even_for_shifted_new_batch(representation):
    X = _sample()
    model = fit_retained_sparse_kmeans(X, representation, steps=2, restarts=1).models[0]
    mean_before, scale_before = model.transform_mean.copy(), model.transform_scale.copy()
    discovery = X if representation == "raw" else X**2
    np.testing.assert_allclose(model.transform_mean, discovery.mean(0))
    np.testing.assert_allclose(model.transform_scale, discovery.std(0))
    new = X[:6] + 20
    values = new if representation == "raw" else new**2
    np.testing.assert_allclose(model.transform(new), (values-discovery.mean(0))/discovery.std(0))
    model.predict(new)
    np.testing.assert_array_equal(model.transform_mean, mean_before)
    np.testing.assert_array_equal(model.transform_scale, scale_before)
    assert np.linalg.norm(model.transform(new).mean(0)) > 1


def test_squared_transform_and_predictions_are_sign_symmetric():
    X = _sample()
    result = fit_retained_sparse_kmeans(X, "squared", steps=3, restarts=1)
    sign = np.random.default_rng(7).choice([-1, 1], X.shape)
    for model in result.models:
        np.testing.assert_array_equal(model.transform(X), model.transform(X * sign))
        np.testing.assert_array_equal(model.predict(X), model.predict(X * sign))


def test_prefix_prediction_restricts_frozen_centers_without_refitting():
    X = _sample()
    model = fit_retained_sparse_kmeans(X, steps=3, restarts=1).models[-1]
    panel = model.ranking[:3]
    centers_before = model.centers.copy()
    Z = model.transform(X)[:, panel]
    for weighted in (True, False):
        w = model.weights[panel] if weighted else np.ones(len(panel))
        expected = np.argmin(np.stack([
            ((Z-model.centers[k, panel])**2 * w).sum(1) for k in (0, 1)
        ]), axis=0)
        np.testing.assert_array_equal(model.predict(X, panel=panel, weighted=weighted), expected)
    np.testing.assert_array_equal(model.centers, centers_before)


def test_prefix_cap_does_not_claim_full_support_is_capped():
    X = _sample(p=12)
    result = fit_retained_sparse_kmeans(X, max_features=2, steps=3, restarts=1)
    assert result.diagnostics["full_native_support_is_not_capped"] is True
    full = [m for m in result.models if m.diagnostics["l1_bound"] == pytest.approx(np.sqrt(12))][0]
    assert full.diagnostics["full_native_support_size"] > 2
    assert full.diagnostics["prefix_cap"] == 2
    assert len(full.ranking) == 12
    assert full.diagnostics["full_native_support"] == np.flatnonzero(full.weights > 0).tolist()


def test_constants_are_excluded_and_all_constant_data_return_no_models():
    X = np.column_stack([_sample(p=5), np.zeros(60), np.ones(60)])
    result = fit_retained_sparse_kmeans(X, steps=2, restarts=1)
    assert result.diagnostics["excluded_constant_features"] == [5, 6]
    for model in result.models:
        assert model.weights[5] == model.weights[6] == 0
        assert set(model.ranking) == set(range(5))
        np.testing.assert_array_equal(model.predict(X), model.train_labels)
        with pytest.raises(ValueError, match="positive metric weights"):
            model.predict(X, panel=[5, 6])
    for constant in (np.zeros((10, 5)), np.ones((10, 5))):
        empty = fit_retained_sparse_kmeans(constant)
        assert empty.models == []
        assert empty.diagnostics["status"] == "no_variable_features"
        assert empty.diagnostics["kmeans_fits"] == 0


def test_squared_sign_varying_but_constant_magnitude_features_are_excluded():
    X = np.array([[1., -2.], [-1., 2.]] * 5)
    result = fit_retained_sparse_kmeans(X, representation="squared")
    assert result.models == []
    assert result.diagnostics["status"] == "no_variable_features"


def test_same_seed_reproduces_complete_retained_state_without_label_input():
    X = _sample()
    a = fit_retained_sparse_kmeans(X, seed=7, steps=3, restarts=1)
    b = fit_retained_sparse_kmeans(X, seed=7, steps=3, restarts=1)
    assert len(a.models) == len(b.models)
    for ma, mb in zip(a.models, b.models):
        np.testing.assert_array_equal(ma.weights, mb.weights)
        np.testing.assert_array_equal(ma.centers, mb.centers)
        np.testing.assert_array_equal(ma.train_labels, mb.train_labels)
        assert ma.ranking == mb.ranking
    parameters = inspect.signature(fit_retained_sparse_kmeans).parameters
    assert "y" not in parameters and "labels" not in parameters


@pytest.mark.parametrize("bad", [np.ones((3, 4)), np.ones(5), np.array([[1, np.nan]] * 5)])
def test_invalid_data_fail_visibly(bad):
    with pytest.raises(ValueError):
        fit_retained_sparse_kmeans(bad)


@pytest.mark.parametrize("kwargs", [
    {"representation": "log"}, {"steps": 0}, {"restarts": 0},
    {"max_features": 2.5}, {"max_features": True}, {"l1_bounds": []},
    {"l1_bounds": [0.5]}, {"tolerance": -1}, {"max_seconds": 0},
])
def test_invalid_controls_fail_visibly(kwargs):
    with pytest.raises(ValueError):
        fit_retained_sparse_kmeans(_sample(), **kwargs)


def test_invalid_prediction_inputs_fail_visibly():
    X = _sample()
    model = fit_retained_sparse_kmeans(X, steps=2, restarts=1).models[0]
    for bad in (X[:, :3], X[:0], X * np.nan):
        with pytest.raises(ValueError):
            model.predict(bad)
    for panel in ([], [1, 1], [0.0], [-1], [99], [True]):
        with pytest.raises(ValueError):
            model.predict(X, panel=panel)


def test_squaring_overflow_fails_instead_of_silently_changing_geometry():
    with pytest.raises(ValueError, match="overflowed"):
        fit_retained_sparse_kmeans(np.full((5, 2), 1e200), representation="squared")
