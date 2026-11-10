"""Numerical and deployment contracts, not evidence of benchmark superiority."""
import inspect

import numpy as np
import pytest

from atomic_research.kernel_panels import (
    KernelPanelModel, _metric_objective_gradient, _objective_gradient,
    fit_frozen_kernel_panel, fit_kernel_panel, load_kernel_panel,
)


def _sample(seed=5, n=60, p=12):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    X[: n // 2, :5] += 1.5
    return X


@pytest.mark.parametrize("kernel", ["local", "global"])
@pytest.mark.parametrize("objective", ["gap_ratio", "cut"])
def test_projection_gradient_includes_bandwidth_derivative(kernel, objective):
    rng = np.random.default_rng(39)
    X = rng.normal(size=(19, 5))
    matrix = rng.normal(size=(5, 2))
    matrix /= np.linalg.norm(matrix)
    _, gradient, _ = _objective_gradient(X, matrix, kernel=kernel, objective=objective, neighbors=4)
    numerical = np.zeros_like(matrix)
    for index in np.ndindex(matrix.shape):
        plus, minus = matrix.copy(), matrix.copy()
        plus[index] += 1e-6
        minus[index] -= 1e-6
        numerical[index] = (
            _objective_gradient(X, plus, kernel=kernel, objective=objective, neighbors=4)[0]
            - _objective_gradient(X, minus, kernel=kernel, objective=objective, neighbors=4)[0]
        ) / 2e-6
    np.testing.assert_allclose(gradient, numerical, rtol=2e-5, atol=1e-7)


@pytest.mark.parametrize("kernel", ["local", "global"])
@pytest.mark.parametrize("objective", ["gap_ratio", "cut"])
def test_diagonal_metric_gradient(kernel, objective):
    rng = np.random.default_rng(67)
    X = rng.normal(size=(21, 6))
    weights = rng.uniform(0.1, 0.6, 6)
    _, gradient, _ = _metric_objective_gradient(X, weights, kernel=kernel, objective=objective, neighbors=4)
    numerical = np.zeros_like(weights)
    for index in range(len(weights)):
        plus, minus = weights.copy(), weights.copy()
        plus[index] += 1e-6
        minus[index] -= 1e-6
        numerical[index] = (
            _metric_objective_gradient(X, plus, kernel=kernel, objective=objective, neighbors=4)[0]
            - _metric_objective_gradient(X, minus, kernel=kernel, objective=objective, neighbors=4)[0]
        ) / 2e-6
    np.testing.assert_allclose(gradient, numerical, rtol=2e-5, atol=1e-7)


def test_zero_metric_weight_has_available_entry_gradient():
    rng = np.random.default_rng(83)
    X = rng.normal(size=(20, 5))
    weights = np.array([0.4, 0.3, 0.2, 0.1, 0.0])
    loss, gradient, _ = _metric_objective_gradient(X, weights, kernel="global")
    plus = weights.copy()
    plus[-1] += 1e-7
    numerical = (_metric_objective_gradient(X, plus, kernel="global")[0] - loss) / 1e-7
    assert abs(gradient[-1]) > 1e-5
    np.testing.assert_allclose(gradient[-1], numerical, rtol=2e-4, atol=1e-6)


@pytest.mark.parametrize("mixing", [False, True])
def test_support_can_exceed_three_and_respects_cap(mixing):
    X = _sample()
    # Zero steps deliberately checks parameterization independent of whether
    # an optimizer retains or drops a coordinate in any particular dataset.
    model = fit_kernel_panel(X, budget=6, rank=2, mixing=mixing, steps=0, restarts=1)
    assert len(model.panel) == 6
    assert np.linalg.matrix_rank(model.transform_matrix) <= (2 if mixing else 6)
    np.testing.assert_allclose(np.linalg.norm(model.transform_matrix), 1)
    model = fit_kernel_panel(X, budget=6, rank=2, mixing=mixing, steps=3, restarts=2)
    assert 1 <= len(model.panel) <= 6
    assert model.diagnostics["objective_evaluations"] >= 2
    assert len(model.diagnostics["restarts"]) == 2
    for restart in model.diagnostics["restarts"]:
        assert restart["final_loss"] <= restart["initial_loss"] + 1e-10


@pytest.mark.parametrize("kernel", ["local", "global"])
def test_frozen_prediction_batch_independence_and_selected_columns_only(kernel):
    X = _sample()
    X[1, 0] = np.nan
    model = fit_kernel_panel(X, budget=5, kernel=kernel, steps=2, restarts=1, max_samples=30)
    query = _sample(seed=8, n=18)
    query[0, model.panel[0]] = np.nan
    prediction = model.predict(query)
    embedding = model.embed(query)
    for row in range(len(query)):
        np.testing.assert_array_equal(model.predict(query[row:row+1]), prediction[row:row+1])
        np.testing.assert_allclose(model.embed(query[row:row+1]), embedding[row:row+1], atol=1e-12)
    altered = query.copy()
    outside = np.setdiff1d(np.arange(X.shape[1]), model.panel)
    altered[:, outside] = 1e200
    np.testing.assert_array_equal(model.predict(altered), prediction)
    np.testing.assert_allclose(model.embed(altered), embedding, atol=0, rtol=0)
    np.testing.assert_array_equal(model.predict(X), model.train_labels)
    assert model.diagnostics["reference_extension_disagreement"] == 0
    assert model.predict(np.empty((0, X.shape[1]))).shape == (0,)


@pytest.mark.parametrize("kernel", ["local", "global"])
def test_serialization_preserves_predictions_and_uses_no_pickle(tmp_path, kernel):
    X = _sample()
    model = fit_kernel_panel(X, budget=6, kernel=kernel, steps=2, restarts=1)
    path = tmp_path / "native_model.npz"
    model.save(path)
    for loaded in (load_kernel_panel(path), KernelPanelModel.load(path)):
        assert loaded.panel == model.panel
        assert loaded.diagnostics == model.diagnostics
        np.testing.assert_array_equal(loaded.train_labels, model.train_labels)
        np.testing.assert_array_equal(loaded.predict(X), model.predict(X))
        np.testing.assert_allclose(loaded.embed(X), model.embed(X), atol=0, rtol=0)
    with np.load(path, allow_pickle=False) as contents:
        assert all(contents[name].dtype.kind != "O" for name in contents.files)


def test_frozen_same_transform_reproduces_native_fit():
    X = _sample()
    learned = fit_kernel_panel(X, budget=6, steps=3, restarts=1, seed=12, max_samples=35)
    frozen = fit_frozen_kernel_panel(X, learned.panel, learned.transform_matrix,
                                      seed=12, max_samples=35)
    np.testing.assert_allclose(learned.embed(X), frozen.embed(X), atol=1e-10)
    np.testing.assert_array_equal(learned.predict(X), frozen.predict(X))
    assert learned.diagnostics["reference_indices"] == frozen.diagnostics["reference_indices"]
    identity = fit_frozen_kernel_panel(X, learned.panel, seed=12, max_samples=35)
    assert identity.panel == learned.panel
    assert identity.transform_matrix.shape[1] == len(learned.panel)


def test_api_accepts_no_labels_or_reference_panels():
    parameters = inspect.signature(fit_kernel_panel).parameters
    assert not (set(parameters) & {"y", "labels", "reference_panel", "test", "validation"})
    assert all(item.kind != inspect.Parameter.VAR_KEYWORD for item in parameters.values())
    with pytest.raises(TypeError):
        fit_kernel_panel(_sample(), y=np.zeros(60))


def test_mixing_and_diagonal_start_from_matched_support_and_energies():
    X = _sample()
    diagonal = fit_kernel_panel(X, budget=6, rank=2, mixing=False, steps=1, restarts=3, seed=7)
    signed = fit_kernel_panel(X, budget=6, rank=2, mixing=True, steps=1, restarts=3, seed=7)
    for d, s in zip(diagonal.diagnostics["restarts"], signed.diagnostics["restarts"]):
        assert d["initial_panel"] == s["initial_panel"]
        assert d["initialization"] == s["initialization"]
        np.testing.assert_allclose(d["initial_row_energies"], s["initial_row_energies"], atol=0, rtol=0)
        assert d["support_change_steps"] >= 0
        assert s["feature_entries"] >= 0
    assert signed.diagnostics["restarts"][0]["initialization"] == "discovery_pca_rows"


@pytest.mark.parametrize("mixing", [False, True])
def test_constant_missing_data_abstain_finitely(mixing):
    X = np.ones((30, 7))
    X[:, 2] = np.nan
    model = fit_kernel_panel(X, budget=5, mixing=mixing, steps=2, restarts=1)
    assert model.panel == ()
    assert not model.diagnostics["valid"]
    assert model.diagnostics["status"] == "no_variable_features"
    assert np.isfinite(model.embed(X)).all()
    np.testing.assert_array_equal(model.predict(X), np.zeros(len(X)))


def test_duplicate_landmarks_preserve_extension():
    X = np.repeat(_sample(n=20, p=8), 2, axis=0)
    model = fit_frozen_kernel_panel(X, [0, 1, 2, 3, 4], seed=2)
    assert model.diagnostics["reference_extension_disagreement"] == 0
    assert np.isfinite(model.embed(X)).all()


@pytest.mark.parametrize("kwargs", [
    {"budget": 0}, {"rank": 0}, {"steps": -1}, {"restarts": 0},
    {"neighbors": 0}, {"max_samples": 9}, {"kernel": "bad"},
    {"objective": "bad"}, {"mixing": "yes"}, {"budget": True},
    {"seed": -1}, {"seed": 2.1}, {"seed": 2**32}, {"seed": True},
])
def test_bad_options_rejected(kwargs):
    with pytest.raises(ValueError):
        fit_kernel_panel(_sample(), **kwargs)


def test_supplied_projection_cannot_sneak_in_unselected_features():
    X = _sample()
    transform = np.ones((X.shape[1], 2))
    with pytest.raises(ValueError, match="outside"):
        fit_frozen_kernel_panel(X, [0, 1], transform)


@pytest.mark.parametrize("panel", [[1.2, 2], [True, 2], [0, 0], [], [-1, 2], [0, 12]])
def test_invalid_frozen_panel_rejected(panel):
    with pytest.raises(ValueError):
        fit_frozen_kernel_panel(_sample(), panel)
