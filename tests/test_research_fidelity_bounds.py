"""Exact coverage and validation-selection checks for frozen prefix families."""

from copy import deepcopy
import inspect

import numpy as np
import pytest
from scipy.stats import binom

from atomic_research.fidelity_bounds import binomial_upper_bound, select_prefix


def _record(panel, errors=0, n=200, valid=True):
    return {"panel": panel, "errors": errors, "n": n, "valid": valid}


@pytest.mark.parametrize("n,alpha", [(1, .05), (200, .05 / 32), (1000, 1e-12)])
def test_zero_errors_matches_analytic_bound(n, alpha):
    assert binomial_upper_bound(0, n, alpha) == pytest.approx(1 - alpha ** (1 / n))
    assert binomial_upper_bound(n, n, alpha) == 1
    assert binomial_upper_bound(0, 200, .05 / 32) == pytest.approx(.03179103385062347)


@pytest.mark.parametrize("n,alpha", [(1, .05), (9, .1), (30, .05), (200, .05 / 32)])
def test_binomial_enumeration_has_one_sided_coverage_at_boundaries(n, alpha):
    upper = np.array([binomial_upper_bound(k, n, alpha) for k in range(n + 1)])
    # Include values on either side of discontinuities in the coverage function.
    probabilities = np.unique(np.concatenate([
        np.linspace(0, 1, 121), upper,
        np.nextafter(upper, 0), np.nextafter(upper, 1),
    ]))
    probabilities = probabilities[(probabilities >= 0) & (probabilities <= 1)]
    for p in probabilities:
        failure_probability = binom.pmf(np.arange(n + 1), n, p)[upper < p].sum()
        assert failure_probability <= alpha + 2e-12


def test_bound_is_monotone_in_errors_sample_size_and_confidence():
    assert np.all(np.diff([binomial_upper_bound(k, 40) for k in range(41)]) > 0)
    assert np.all(np.diff([binomial_upper_bound(3, n) for n in (5, 10, 50, 100)]) < 0)
    assert binomial_upper_bound(3, 100, .001) > binomial_upper_bound(3, 100, .05)
    # Extremely small alpha should not be rounded away by forming 1-alpha.
    assert np.isfinite(binomial_upper_bound(3, 1000, 1e-30))
    assert binomial_upper_bound(3, 1000, 1e-30) < 1


def test_empirical_and_bounded_selectors_have_distinct_thresholds():
    records = [_record([3], 10), _record([3, 2], 0), _record([3, 2, 4], 0)]
    result = select_prefix(records, family_size=32)
    assert result["empirical_panel"] == [3]
    assert result["bounded_panel"] == [3, 2]
    assert result["records"][0]["point_error"] == .05
    assert result["records"][0]["upper_error"] > .05
    assert result["family_size"] == 32
    assert result["alpha"] == result["max_error"] == .05


def test_invalid_records_still_count_and_ties_are_deterministic():
    records = [_record([5], valid=False), _record([4, 6]), _record([2, 7])]
    before = deepcopy(records)
    result = select_prefix(records)
    assert result["empirical_panel"] == result["bounded_panel"] == [2, 7]
    assert result["family_size"] == 3
    assert result["records"][0]["upper_error"] == binomial_upper_bound(0, 200, .05 / 3)
    assert records == before
    reversed_result = select_prefix(list(reversed(records)))
    assert reversed_result["bounded_panel"] == result["bounded_panel"]
    result["records"][0]["panel"].append(8)
    result["bounded_panel"].append(9)
    assert records == before


def test_more_candidates_never_tightens_bound_and_no_eligible_means_none():
    records = [_record([1], 0, n=60)]
    one = select_prefix(records)
    many = select_prefix(records, family_size=32)
    assert one["bounded_panel"] == [1]
    assert many["bounded_panel"] is None
    assert many["empirical_panel"] == [1]
    rejected = select_prefix([_record([1], 200)])
    assert rejected["empirical_panel"] is rejected["bounded_panel"] is None
    invalid = select_prefix([_record([1], valid=False)])
    assert invalid["empirical_panel"] is invalid["bounded_panel"] is None


def test_selector_has_no_test_data_interface():
    assert set(inspect.signature(select_prefix).parameters) == {
        "records", "max_error", "alpha", "family_size",
    }
    records = [_record([0], 0), _record([0, 1], 0)]
    first = select_prefix(records)
    arbitrary_test_data = np.random.default_rng(1).normal(size=(50, 20))
    arbitrary_test_data[:] = np.nan
    assert select_prefix(records) == first
    with pytest.raises(TypeError):
        select_prefix(records, test_data=arbitrary_test_data)


@pytest.mark.parametrize("errors,n,alpha", [
    (-1, 10, .05), (11, 10, .05), (0, 0, .05), (0, -1, .05),
    (True, 10, .05), (0, True, .05), (1., 10, .05), (0, 10., .05),
    (np.nan, 10, .05), (0, np.inf, .05), (0, 10, np.nan),
    (0, 10, np.inf), (0, 10, 0), (0, 10, 1), (0, 10, True),
    ("1", 10, .05), (0, 10, ".05"),
])
def test_binomial_rejects_malformed_input(errors, n, alpha):
    with pytest.raises(ValueError):
        binomial_upper_bound(errors, n, alpha)


@pytest.mark.parametrize("records,kwargs", [
    ([], {}), (None, {}), ([None], {}), ([{}], {}),
    ([_record([])], {}), ([_record([1, 1])], {}), ([_record([-1])], {}),
    ([_record([1.])], {}), ([_record([True])], {}), ([_record((1,))], {}),
    ([_record([1], valid=1)], {}), ([_record([1], errors=201)], {}),
    ([_record([1], n=0)], {}), ([_record([1]), _record([2], n=201)], {}),
    ([_record([1]), _record([2])], {"family_size": 1}),
    ([_record([1])], {"family_size": 0}),
    ([_record([1])], {"family_size": 2.}),
    ([_record([1])], {"family_size": True}),
    ([_record([1])], {"max_error": np.nan}),
    ([_record([1])], {"max_error": -1}),
    ([_record([1])], {"max_error": 1.1}),
    ([_record([1])], {"alpha": 0}),
    ([_record([1])], {"alpha": np.inf}),
    ([_record([1])], {"alpha": 5e-324, "family_size": 32}),
])
def test_selector_rejects_malformed_input(records, kwargs):
    with pytest.raises(ValueError):
        select_prefix(records, **kwargs)
