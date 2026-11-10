"""Frozen size calibration checks; no clustering efficacy claim."""
import inspect

import numpy as np
import pytest

from atomic_research.calibration import (
    INVALID_OBJECTIVE, SizeReferenceObjective, UnsupportedPanelSizeError,
)
from atomic_research.search import FrozenObjective


def record(size, index, graphcut, density, valid=True, legacy_valid=True):
    return {"panel": tuple(range(index * 10, index * 10 + size)),
            "graphcut": graphcut, "density": density,
            "legacy_graphcut": graphcut, "legacy_density": density,
            "valid": valid, "legacy_valid": legacy_valid}


def bank():
    # Very different means by size, with controlled residuals in both components.
    return ([record(1, j, j, 3*j) for j in range(4)] +
            [record(5, j+10, 100+j, -20+3*j) for j in range(4)])


@pytest.mark.parametrize("mode", ["within", "pooled"])
def test_dimension_offsets_removed(mode):
    objective = SizeReferenceObjective(bank(), scale_mode=mode, min_count=4)
    a = record(1, 99, 2.5, 7.5)
    b = record(5, 98, 102.5, -12.5)
    assert objective(a) == pytest.approx(objective(b))
    assert objective(record(1, 100, 1.5, 4.5)) == pytest.approx(0)
    assert objective(record(5, 101, 101.5, -15.5)) == pytest.approx(0)


@pytest.mark.parametrize("mode", ["within", "pooled"])
def test_single_size_parity_with_frozen_objective(mode):
    refs = bank()[:4]
    calibrated = SizeReferenceObjective(refs, scale_mode=mode, min_count=4)
    original = FrozenObjective(refs, mode="consistent")
    # Components have unequal scales; summing raw values would fail this test.
    candidate = record(1, 200, 2.25, 1.0)
    assert calibrated(candidate) == pytest.approx(original(candidate))


def test_fitted_units_do_not_change_with_calls_or_mutated_inputs():
    refs = bank()
    objective = SizeReferenceObjective(refs, min_count=4)
    candidate = record(1, 300, 2.25, 1)
    expected, moments = objective(candidate), objective.moments
    for i in range(20):
        objective(record(5, 400+i, 50*i, -100*i))
    refs[0]["graphcut"] = 1e5
    refs.append(record(1, 600, 1000, 1000))
    inspection = objective.diagnostics
    inspection["moments"][1]["graphcut"] = (999, 1)
    assert objective.moments == moments
    assert objective(candidate) == expected


def test_insufficient_and_unseen_sizes_are_explicitly_unsupported():
    objective = SizeReferenceObjective(bank()[:4] + [record(2, 100, 1, 1)], min_count=4)
    assert objective.diagnostics["unsupported_sizes"] == [2]
    assert not objective.eligible(record(2, 101, 1, 1))
    assert not objective.eligible(record(8, 102, 1, 1))
    with pytest.raises(UnsupportedPanelSizeError, match="size 2 has 1"):
        objective(record(2, 101, 1, 1))
    with pytest.raises(UnsupportedPanelSizeError, match="size 8 has 0"):
        objective(record(8, 102, 1, 1))


def test_common_eligibility_and_finiteness_govern_reference_counts():
    refs = bank()[:4] + [record(1, 20, 4, 4, legacy_valid=False),
                        record(1, 21, 4, 4, valid=False),
                        record(1, 22, np.nan, 4)]
    objective = SizeReferenceObjective(refs, min_count=4)
    assert objective.diagnostics["counts"][1] == {
        "total": 7, "common_eligible": 5, "finite_eligible": 4}
    assert not objective.eligible(refs[-1])
    assert objective(refs[-1]) == INVALID_OBJECTIVE
    assert objective(refs[-2]) == INVALID_OBJECTIVE
    assert objective(refs[-3]) == INVALID_OBJECTIVE


def test_pooled_scales_exclude_mean_offsets_and_weight_by_reference_count():
    refs = [record(1, 0, -1, -2), record(1, 1, 1, 2)]
    refs += [record(3, i+10, 100+x, 1000+2*x) for i,x in enumerate([-3,-3,3,3])]
    pooled = SizeReferenceObjective(refs, scale_mode="pooled", min_count=2)
    within = SizeReferenceObjective(refs, scale_mode="within", min_count=2)
    expected = np.sqrt((2*1 + 4*9)/6)
    assert pooled.moments[1]["graphcut"][1] == pytest.approx(expected)
    assert pooled.moments[3]["graphcut"][1] == pytest.approx(expected)
    assert pooled.moments[1]["density"][1] == pytest.approx(2*expected)
    assert within.moments[1]["graphcut"][1] == 1
    assert within.moments[3]["graphcut"][1] == 3


def test_unsupported_sizes_do_not_contaminate_pooled_scale():
    refs = bank()[:4]
    a = SizeReferenceObjective(refs, scale_mode="pooled", min_count=4)
    b = SizeReferenceObjective(refs + [record(2, 100, 1e8, -1e8)], scale_mode="pooled", min_count=4)
    assert a.moments == b.moments


@pytest.mark.parametrize("mode", ["within", "pooled"])
def test_zero_spread_uses_explicit_finite_floor(mode):
    refs = [record(1, i, 2, 4) for i in range(8)]
    objective = SizeReferenceObjective(refs, scale_mode=mode)
    assert objective.moments[1]["graphcut"] == (2, .001)
    assert objective(record(1, 9, 2.001, 4)) == pytest.approx(1)
    assert np.isfinite(objective(record(1, 10, 3, 5)))


def test_empty_reference_bank_never_invents_support():
    objective = SizeReferenceObjective([])
    assert objective.diagnostics["supported_sizes"] == []
    with pytest.raises(UnsupportedPanelSizeError):
        objective(record(1, 0, 0, 0))


def test_duplicate_masks_cannot_manufacture_minimum_reference_count():
    with pytest.raises(ValueError, match="Duplicate reference panel"):
        SizeReferenceObjective([record(1, 0, 1, 1)] * 8)


def test_no_annotation_parameter():
    assert "y" not in inspect.signature(SizeReferenceObjective).parameters
    with pytest.raises(TypeError):
        SizeReferenceObjective(bank(), y=np.zeros(8))


@pytest.mark.parametrize("kwargs", [{"scale_mode": "global"}, {"min_count": 0},
                                     {"min_count": True}, {"scale_floor": 0},
                                     {"scale_floor": np.inf}])
def test_invalid_configuration_raises(kwargs):
    with pytest.raises(ValueError):
        SizeReferenceObjective(bank(), **kwargs)
