"""Independent probability and replay checks, not evidence of cluster validity."""

import inspect
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.integrate import quad
from scipy.special import gammaln, log_ndtr, logsumexp
from scipy.stats import multivariate_normal, norm

from atomic_research.radial_panels import (
    GaussianBackground,
    RadialPanel,
    _normalizer_stats,
    fit_radial_panel,
    log_normalizer,
    predict_radial_rule,
)


def radial_model(dimension=3, locations=(1.0, 7.0), width=0.6, weights=(0.4, 0.6)):
    """Explicit parameters keep numerical tests independent of optimization."""
    return RadialPanel(
        input_feature_count=dimension + 2,
        support=np.arange(dimension),
        center=np.linspace(-0.3, 0.5, dimension),
        scale=np.linspace(0.7, 1.9, dimension),
        locations=np.asarray(locations, dtype=float),
        width=width,
        weights=np.asarray(weights, dtype=float),
        log_z=np.array([log_normalizer(dimension, a, width) for a in locations]),
        diagnostics={},
    )


def radius_points(model, radii):
    X = np.zeros((len(radii), model.input_feature_count))
    X[:, model.support] = model.center
    X[:, model.support[0]] += np.asarray(radii) * model.scale[0]
    return X


def independent_normalizer(dimension, location, width):
    """Adaptive infinite-range integration in raw radius, including both tails."""
    area = 2 * np.pi ** (dimension / 2) / np.exp(gammaln(dimension / 2))

    def integrand(radius):
        return area * radius ** (dimension - 1) * np.exp(
            -0.5 * ((radius * radius - location) / width) ** 2
        )

    # Supplying intervals prevents an adaptive infinite integral from missing
    # a very narrow band. Unlike production, neither tail is discarded.
    cuts = sorted(set([0.0, np.sqrt(max(0, location - 8 * width)),
                       np.sqrt(location), np.sqrt(location + 8 * width), np.inf]))
    return sum(quad(integrand, lo, hi, epsabs=1e-10, epsrel=2e-11, limit=200)[0]
               for lo, hi in zip(cuts[:-1], cuts[1:]))


@pytest.mark.parametrize("dimension", [1, 2, 3, 5, 8, 16])
@pytest.mark.parametrize("location,width", [(0.0, 0.7), (1.7, 0.25), (9.0, 0.35), (2.0, 3.0), (100.0, 0.05)])
def test_normalizer_matches_independent_infinite_radius_integral(dimension, location, width):
    actual = log_normalizer(dimension, location, width)
    expected = np.log(independent_normalizer(dimension, location, width))
    assert actual == pytest.approx(expected, abs=2e-8)


@pytest.mark.parametrize("dimension", [1, 2, 3, 5, 16])
def test_zero_location_normalizer_has_closed_form(dimension):
    width = 1.3
    log_area = np.log(2) + dimension / 2 * np.log(np.pi) - gammaln(dimension / 2)
    expected = log_area - np.log(4) + dimension / 4 * np.log(2 * width**2) + gammaln(dimension / 4)
    assert log_normalizer(dimension, 0.0, width) == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("location,width", [(0.0, 1.0), (0.3, 2.1), (5.0, 0.01), (0.002, 0.0001)])
def test_two_dimensional_normalizer_has_closed_form(location, width):
    expected = np.log(np.pi * width) + 0.5 * np.log(2 * np.pi) + log_ndtr(location / width)
    assert log_normalizer(2, location, width) == pytest.approx(expected, abs=1e-9)


def test_normalizer_derivatives_match_closed_form_in_two_dimensions():
    location, width = 0.7, 1.3
    ratio = location / width
    mills = np.exp(norm.logpdf(ratio) - log_ndtr(ratio))
    _, derivative_location, derivative_log_width = _normalizer_stats(2, location, width)
    assert derivative_location == pytest.approx(mills / width, abs=1e-10)
    assert derivative_log_width == pytest.approx(1 - ratio * mills, abs=1e-10)


def test_raw_model_density_integrates_to_one_with_nonunit_feature_scales():
    model = radial_model()
    dimension = len(model.support)
    area = 2 * np.pi ** (dimension / 2) / np.exp(gammaln(dimension / 2))
    jacobian = np.prod(model.scale)

    def integrand(radius):
        return np.exp(model.logpdf(radius_points(model, [radius]))[0]) * jacobian * area * radius ** (dimension - 1)

    total = quad(integrand, 0, np.inf, epsabs=1e-9, limit=200)[0]
    assert total == pytest.approx(1.0, abs=2e-8)


def test_native_threshold_equals_independent_posterior_assignment_and_roundtrips():
    model = radial_model()
    threshold = model.rule()["threshold"]
    assert threshold > 0
    X = radius_points(model, np.sqrt(np.r_[0.0, threshold - 1e-6, threshold + 1e-6, 30.0]))
    posterior_labels = np.argmax(model.component_logpdf(X) + np.log(model.weights), axis=1)
    assert_array_equal(posterior_labels, [0, 0, 1, 1])
    saved = json.loads(json.dumps(model.to_dict(), allow_nan=False))
    replay = RadialPanel.from_dict(saved)
    assert_array_equal(model.predict(X), posterior_labels)
    assert_array_equal(predict_radial_rule(saved["rule"], X), posterior_labels)
    assert_array_equal(replay.predict(X), posterior_labels)
    assert_allclose(replay.logpdf(X), model.logpdf(X), atol=0, rtol=0)


@pytest.mark.parametrize("locations,weights,expected", [((2.0,), (1.0,), 0), ((2.0, 2.0), (0.3, 0.7), 1), ((2.0, 2.0), (0.5, 0.5), 0)])
def test_exactly_identical_components_have_constant_posterior(locations, weights, expected):
    model = radial_model(locations=locations, weights=weights)
    X = radius_points(model, np.linspace(0, 6, 50))
    assert_array_equal(model.predict(X), np.full(len(X), expected))
    assert_array_equal(model.predict(X), np.argmax(model.component_logpdf(X) + np.log(model.weights), axis=1))


def test_nearly_identical_components_are_not_silently_replaced_by_constant_rule():
    # This is a replay edge case, not evidence of meaningful separation.
    model = radial_model(locations=(2.0, 2.0 + 5e-11), weights=(0.5, 0.5))
    X = radius_points(model, [0.0, 3.0])
    expected = np.argmax(model.component_logpdf(X) + np.log(model.weights), axis=1)
    assert_array_equal(expected, [0, 1])
    assert_array_equal(model.predict(X), expected)


@pytest.mark.parametrize("field,value", [("width", np.nan), ("width", -0.1),
                                          ("center", [np.inf, 0.0, 0.0]),
                                          ("scale", [1.0, 0.0, 1.0]),
                                          ("locations", [-1.0, 2.0]),
                                          ("weights", [0.0, 1.0]),
                                          ("log_z", [np.nan, 0.0])])
def test_invalid_saved_probabilities_are_rejected(field, value):
    saved = radial_model().to_dict()
    saved[field] = value
    with pytest.raises(ValueError):
        RadialPanel.from_dict(saved)


def test_profile_distinguishes_spatial_density_from_radial_probability():
    model = radial_model(dimension=5, locations=(2.0,), width=1.2, weights=(1.0,))
    profile = model.spatial_profile(points=10001)
    r = np.asarray(profile["radii"])
    spatial = np.asarray(profile["log_spatial_density"])
    radial = np.array([np.nan if value is None else value for value in profile["log_radial_density"]])
    expected_spatial_mode = np.sqrt(2.0)
    expected_radial_mode = np.sqrt((2.0 + np.sqrt(2.0**2 + 2 * (5 - 1) * 1.2**2)) / 2)
    spacing = r[1] - r[0]
    assert r[np.argmax(spatial)] == pytest.approx(expected_spatial_mode, abs=spacing)
    assert r[np.nanargmax(radial)] == pytest.approx(expected_radial_mode, abs=spacing)
    assert np.isnan(radial[0])
    assert profile["spatial_mode_count"] == 1
    assert profile["two_spatial_modes"] is False
    assert profile["valley_ratio"] is None
    expected = logsumexp(model.component_logpdf(radius_points(model, r)) + np.log(model.weights), axis=1) + np.log(model.scale).sum()
    assert_allclose(spatial, expected, atol=1e-12)


def test_common_space_background_cancellation_uses_covariance_marginal():
    rng = np.random.default_rng(104)
    covariance = np.array([[1.0, 0.7, -0.4], [0.7, 1.3, 0.1], [-0.4, 0.1, 1.1]])
    fit_rows = rng.multivariate_normal([0.5, -0.4, 1.0], covariance, 120)
    X = rng.multivariate_normal([0.5, -0.4, 1.0], covariance, 17)
    background = GaussianBackground.fit(fit_rows)
    S, R = np.array([0, 2]), np.array([1])
    marginal = background.covariance[np.ix_(S, S)]
    expected_panel = multivariate_normal.logpdf(X[:, S], background.mean[S], marginal)
    assert_allclose(background.logpdf_panel(X, S), expected_panel, atol=1e-12)
    cross = background.covariance[np.ix_(R, S)]
    conditional_mean = background.mean[R] + (X[:, S] - background.mean[S]) @ np.linalg.solve(marginal, cross.T)
    conditional_cov = background.covariance[np.ix_(R, R)] - cross @ np.linalg.solve(marginal, cross.T)
    conditional_logpdf = norm.logpdf(X[:, R].ravel(), conditional_mean.ravel(), np.sqrt(conditional_cov.item()))
    full_logpdf = multivariate_normal.logpdf(X, background.mean, background.covariance)
    assert_allclose(conditional_logpdf + expected_panel, full_logpdf, atol=1e-11)
    model = radial_model(dimension=2)
    model.input_feature_count = 3
    model.support = S
    panel_gain = model.logpdf(X) - background.logpdf_panel(X, S)
    full_gain = model.logpdf(X) + conditional_logpdf - full_logpdf
    assert_allclose(panel_gain, full_gain, atol=1e-11)


@pytest.fixture(scope="module")
def small_fit():
    rng = np.random.default_rng(105)
    X = rng.normal(size=(100, 5))
    directions = rng.normal(size=(100, 2))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    radii = np.where(np.arange(100) % 2, 2.0, 0.8) + rng.normal(0, 0.06, 100)
    X[:, [1, 3]] = directions * radii[:, None]
    return X, fit_radial_panel(X, [1, 3], components=2, maxiter=100)


def test_frozen_preprocessing_and_prediction_ignore_unselected_coordinates(small_fit):
    X, model = small_fit
    before = json.dumps(model.to_dict(), sort_keys=True)
    changed = X.copy()
    changed[:, [0, 2, 4]] = changed[:, [0, 2, 4]] * 1e4 + 500
    assert_array_equal(model.predict(changed), model.predict(X))
    assert_allclose(model.logpdf(changed), model.logpdf(X), atol=0, rtol=0)
    assert before == json.dumps(model.to_dict(), sort_keys=True)
    assert_allclose(model.center, X[:, [1, 3]].mean(0))
    assert_allclose(model.scale, X[:, [1, 3]].std(0))
    assert model.diagnostics["native_discovery_counts"] == np.bincount(model.predict(X), minlength=2).tolist()


def test_end_to_end_gain_and_native_rules_are_invariant_to_feature_units(small_fit):
    X, model = small_fit
    units = np.array([0.4, 7.0, 2.0, 0.3, 1.2])
    offsets = np.array([0.2, -20.0, 0.0, 5.0, -1.0])
    transformed = X * units + offsets
    converted = fit_radial_panel(transformed, [1, 3], components=2, maxiter=100)
    background, converted_background = GaussianBackground.fit(X), GaussianBackground.fit(transformed)
    expected_jacobian = np.log(units[[1, 3]]).sum()
    assert_allclose(converted.logpdf(transformed), model.logpdf(X) - expected_jacobian, atol=2e-6)
    assert_allclose(converted_background.logpdf_panel(transformed, [1, 3]), background.logpdf_panel(X, [1, 3]) - expected_jacobian, atol=1e-10)
    assert_array_equal(converted.predict(transformed), model.predict(X))
    gain = model.logpdf(X) - background.logpdf_panel(X, [1, 3])
    converted_gain = converted.logpdf(transformed) - converted_background.logpdf_panel(transformed, [1, 3])
    assert_allclose(converted_gain, gain, atol=2e-6)


def test_fitting_api_has_no_annotation_or_validation_input():
    for function in [fit_radial_panel, GaussianBackground.fit]:
        assert not ({"y", "labels", "X_test", "X_validation"} & set(inspect.signature(function).parameters))


@pytest.mark.parametrize("support", [[], [0, 0], [-1], [5], [True], [0.5]])
def test_invalid_support_is_rejected(support):
    X = np.random.default_rng(106).normal(size=(25, 5))
    with pytest.raises(ValueError):
        fit_radial_panel(X, support)


def test_nonfinite_values_and_constant_selected_columns_are_explicit_errors():
    X = np.random.default_rng(107).normal(size=(25, 5))
    X[0, 1] = np.nan
    with pytest.raises(ValueError, match="finite"):
        fit_radial_panel(X, [1, 3])
    X[:, 1] = 2.0
    with pytest.raises(ValueError, match="constant"):
        fit_radial_panel(X, [1, 3])
    with pytest.raises(ValueError, match="constant"):
        GaussianBackground.fit(X)
