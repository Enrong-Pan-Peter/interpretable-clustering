"""Regressions for the October 2026 pilot's floating-point boundary failure."""
import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from atomic_research.radial_panels import _optimizer_point, fit_radial_panel, log_normalizer
from atomic_research.radial_diagnostics import generate_synthetic_splits, make_candidates


def test_roundoff_at_both_bounds_is_projected_but_interior_is_unchanged():
    bounds = [(0., 28.), (-4., 3.)]
    np.testing.assert_array_equal(_optimizer_point([-6.938893903907228e-18, np.nextafter(3., np.inf)], bounds), [0., 3.])
    np.testing.assert_array_equal(_optimizer_point([7., -2.], bounds), [7., -2.])


@pytest.mark.parametrize('point', [[-1e-6, 0.], [28.001, 0.], [0., float('nan')], [float('inf'), 0.]])
def test_invalid_optimizer_values_still_raise(point):
    with pytest.raises(ValueError):
        _optimizer_point(point, [(0., 28.), (-4., 3.)])


def test_public_normalizer_does_not_silently_accept_negative_location():
    with pytest.raises(ValueError):
        log_normalizer(7, -6.938893903907228e-18, 4.029654507857382)


def test_original_failed_pilot_candidate_finishes_and_replays_native_rule():
    data = generate_synthetic_splits('single_shell', 5, 24, 600, 600, 600, 1213)
    candidate = make_candidates(data['support'], 24, 10, 1213 + 4109)[9]
    assert candidate['support'] == [4, 8, 9, 10, 14, 18, 19]
    with threadpool_limits(limits=1):
        model = fit_radial_panel(data['splits']['fit']['X'], candidate['support'], components=2)
    assert np.all(model.locations >= 0)
    assert model.diagnostics['optimizer_success']
    # Specific optimizers/BLAS builds need not reproduce the ulp excursion, so
    # actual correction counts are recorded rather than required for portability.
    assert model.diagnostics['maximum_optimizer_boundary_correction'] < 1e-12
    query = data['splits']['test']['X']
    assert np.isfinite(model.logpdf(query)).all()
    np.testing.assert_array_equal(model.predict(query), np.argmax(model.component_logpdf(query) + np.log(model.weights), axis=1))
