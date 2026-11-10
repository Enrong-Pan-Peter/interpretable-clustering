"""Tests for the distinction between ranking a partition and validating clusters."""
import inspect

import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score

from atomic_research.scoring import (
    column_permutation_calibration, dependence_permutation_diagnostic,
    score_panel, score_partition,
)
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term


def separated(seed=17):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.normal(-3, 0.2, (18, 2)), rng.normal(3, 0.2, (18, 2))])


def test_components_are_invariant_to_partition_label_names():
    X = separated()
    labels = np.repeat([0, 1], 18)
    a = score_partition(X, labels, k=5, core_k=3)
    b = score_partition(X, np.where(labels == 0, 28, -11), k=5, core_k=3)
    assert a["valid"] and b["valid"]
    assert a["graphcut"] == pytest.approx(b["graphcut"])
    assert a["density"] == pytest.approx(b["density"])
    assert a["density"] > 0.8


@pytest.mark.parametrize("splitter", ["spectral", "mst"])
def test_both_terms_score_exact_returned_partition(splitter):
    X = separated()
    a = score_panel(X, [1, 0], splitter=splitter, k=5, core_k=3)
    b = score_partition(X, a["labels"], k=5, core_k=3)
    assert a["panel"] == (0, 1)
    assert a["graphcut"] == pytest.approx(b["graphcut"])
    assert a["density"] == pytest.approx(b["density"])


def test_legacy_components_match_existing_code_on_continuous_data():
    X = np.random.default_rng(10).normal(size=(36, 3))
    a = score_panel(X, [0, 1, 2], k=6, core_k=3, seed=12)
    gc, gc_labels = graphcut_term(X, k=6, rng=12)
    density, mst_labels = density_term(X, core_k=3)
    assert a["legacy_graphcut"] == pytest.approx(gc)
    assert a["legacy_density"] == pytest.approx(density)
    assert adjusted_rand_score(a["labels"], gc_labels) == 1
    assert adjusted_rand_score(a["legacy_labels"], mst_labels) == 1


def test_fitting_api_does_not_accept_external_labels():
    assert "y" not in inspect.signature(score_panel).parameters
    with pytest.raises(TypeError):
        score_panel(separated(), [0, 1], y=np.zeros(36))
    a = score_panel(separated(), [0, 1], seed=2)
    b = score_panel(separated(), [0, 1], seed=2)
    assert np.array_equal(a["labels"], b["labels"])


@pytest.mark.parametrize("labels", [np.zeros(36), np.arange(36), np.r_[0, np.ones(35)]])
def test_degenerate_partitions_rejected(labels):
    result = score_partition(separated(), labels)
    assert not result["valid"]
    assert result["density"] == -9


def test_constant_and_tiny_panels_do_not_invent_clusters():
    assert score_panel(np.ones((20, 4)), [0, 1])["reason"] == "constant_panel"
    assert score_panel(np.ones((3, 4)), [0, 1])["reason"] == "too_few_rows"


def test_duplicate_observations_keep_zero_weight_mst_edges():
    # Each group has repeated endpoints. Sparse MST code can silently omit the
    # zero edges; the complete graph's true within-group bottleneck is exactly 1.
    Z = np.repeat(np.array([[0.0], [1.0], [10.0], [11.0]]), 5, axis=0)
    result = score_partition(Z, np.repeat([0, 1], 10), k=3, core_k=1)
    assert result["valid"]
    assert result["within_bottleneck"] == 1
    assert result["separation"] == 9
    assert result["density"] == pytest.approx(8 / 9)


def test_overlapping_assignment_has_negative_density():
    X = separated()
    result = score_partition(X, np.tile([0, 1], 18), k=5, core_k=3)
    assert result["valid"]
    assert result["density"] < 0


@pytest.mark.parametrize("panel", [[], [0, 0], [-1], [2], [0.5]])
def test_invalid_panels_raise(panel):
    with pytest.raises(ValueError):
        score_panel(separated(), panel)


def test_singleton_gapped_distribution_has_identical_permutation_null():
    X = separated()[:, [0]]
    def largest_gap(Z):
        return float(np.diff(np.sort(Z[:, 0])).max())
    result = column_permutation_calibration(X, largest_gap, B=19, seed=4)
    assert result["raw"] > 4
    assert result["degenerate"]
    assert result["z"] is None
    assert result["p_value"] == 1
    assert np.all(result["null_scores"] == result["raw"])


def test_correlated_single_gaussian_rejects_independence_null():
    rng = np.random.default_rng(10)
    latent = rng.normal(size=180)
    X = np.column_stack([latent, latent + rng.normal(0, 0.05, size=180)])
    result = dependence_permutation_diagnostic(X, B=99, seed=1)
    assert result["p_value"] == 0.01
    assert result["raw"] > 0.95
    assert "independence" in result["null_target"]
    assert result["selection_adjusted"] is False


def test_dependence_statistic_and_null_are_zero_for_singleton():
    result = dependence_permutation_diagnostic(separated()[:, [0]], B=9)
    assert result["raw"] == 0
    assert result["degenerate"] and result["p_value"] == 1
