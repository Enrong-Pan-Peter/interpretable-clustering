"""Population invariants for the single frozen replication/stress batch."""
from __future__ import annotations

import copy

import numpy as np
import pytest

from atomic_research.feature_set_replication_data import CONDITIONS, generate_replication_splits
from atomic_research.radial_diagnostics import CASES, generate_synthetic_splits


def generate(condition="baseline", **changes):
    arguments = dict(case="shells", dimension=3, p=12, n_fit=100, n_validation=70, n_test=80, seed=823)
    arguments.update(changes)
    return generate_replication_splits(**arguments, condition=condition)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("condition", ["baseline", "more_nuisance"])
def test_delegated_conditions_preserve_original_observations_and_metadata(case, condition):
    arguments = dict(case=case, dimension=3, p=12, n_fit=100, n_validation=70, n_test=80, seed=823)
    original = generate_synthetic_splits(**arguments)
    replicated = generate_replication_splits(**arguments, condition=condition)
    assert set(replicated) == set(original)
    for split in ("fit", "validation", "test"):
        for field in ("X", "y"):
            left, right = original["splits"][split][field], replicated["splits"][split][field]
            assert left.dtype == right.dtype and left.shape == right.shape
            assert left.tobytes() == right.tobytes()
    metadata = {key: copy.deepcopy(value) for key, value in replicated.items() if key != "splits"}
    assert metadata["population"].pop("condition") == condition
    assert metadata == {key: value for key, value in original.items() if key != "splits"}


@pytest.mark.parametrize("condition", CONDITIONS)
def test_replicates_are_deterministic_with_one_shared_feature_map(condition):
    first, second = generate(condition), generate(condition)
    assert first["feature_map"] == second["feature_map"]
    assert first["population"] == second["population"]
    assert first["split_seeds"] == second["split_seeds"]
    permutation = np.asarray(first["feature_map"]["original_column_to_latent_column"])
    assert sorted(permutation) == list(range(12))
    assert first["support"] == np.flatnonzero(permutation < 3).tolist()
    for split, n in (("fit", 100), ("validation", 70), ("test", 80)):
        np.testing.assert_array_equal(first["splits"][split]["X"], second["splits"][split]["X"])
        np.testing.assert_array_equal(first["splits"][split]["y"], second["splits"][split]["y"])
        assert first["splits"][split]["X"].shape == (n, 12)
        assert first["splits"][split]["y"].shape == (n,)
        assert np.isfinite(first["splits"][split]["X"]).all()
    assert not np.array_equal(first["splits"]["fit"]["X"][:70], first["splits"]["validation"]["X"])
    assert not np.array_equal(first["splits"]["test"]["X"][:70], first["splits"]["validation"]["X"])


@pytest.mark.parametrize("condition", ["weak_separation", "dependent_nuisance"])
def test_stress_keeps_baseline_feature_map_and_target_labels(condition):
    baseline, stress = generate(), generate(condition)
    assert stress["feature_map"] == baseline["feature_map"]
    assert stress["support"] == baseline["support"]
    for split in ("fit", "validation", "test"):
        np.testing.assert_array_equal(stress["splits"][split]["y"], baseline["splits"][split]["y"])
    for key in ("location", "scale"):
        assert stress["population"][key] == baseline["population"][key]


def test_dependent_nuisance_changes_only_recorded_distractor_features():
    baseline, stress = generate(), generate("dependent_nuisance")
    blocks = stress["population"]["distractor_supports"]
    assert len(blocks) == 2 and all(len(block) == 3 for block in blocks)
    changed = set(blocks[0]) | set(blocks[1])
    assert len(changed) == 6 and changed.isdisjoint(stress["support"])
    unchanged = sorted(set(range(12)) - changed)
    permutation = np.asarray(stress["feature_map"]["original_column_to_latent_column"])
    assert blocks[0] == np.flatnonzero((permutation >= 3) & (permutation < 6)).tolist()
    assert blocks[1] == np.flatnonzero((permutation >= 6) & (permutation < 9)).tolist()
    assert stress["population"]["remaining_matched_nuisance_support"] == np.flatnonzero(permutation >= 9).tolist()
    for split in ("fit", "validation", "test"):
        np.testing.assert_array_equal(stress["splits"][split]["X"][:, unchanged],
                                      baseline["splits"][split]["X"][:, unchanged])
        assert not np.array_equal(stress["splits"][split]["X"][:, sorted(changed)],
                                  baseline["splits"][split]["X"][:, sorted(changed)])
        assert set(stress["splits"][split]) == {"X", "y"}


def test_weak_separation_has_recorded_radii_thickness_and_paired_directions():
    stress = generate("weak_separation", n_fit=12000)
    baseline = generate(n_fit=12000)
    population = stress["population"]
    assert population["shell_radii_per_sqrt_dimension"] == [2., 3.]
    assert population["shell_log_radius_sd"] == .12
    values = (stress["splits"]["fit"]["X"] - population["location"]) / population["scale"]
    base = (baseline["splits"]["fit"]["X"] - population["location"]) / population["scale"]
    support, labels = stress["support"], stress["splits"]["fit"]["y"]
    radii = np.linalg.norm(values[:, support], axis=1)
    target_radii = np.where(labels == 0, 2., 3.) * np.sqrt(len(support))
    log_ratio = np.log(radii / target_radii)
    assert abs(log_ratio.mean() - (-.5 * .12 ** 2)) < .004
    assert abs(log_ratio.std() - .12) < .005
    directions = values[:, support] / radii[:, None]
    base_directions = base[:, support] / np.linalg.norm(base[:, support], axis=1)[:, None]
    np.testing.assert_allclose(directions, base_directions, atol=2e-14, rtol=2e-14)
    # Signal and independent nuisance coordinates have matching population
    # marginals. These moment checks detect mismatched radius/scale parameters.
    variance = 6.5 * np.exp(.12 ** 2)
    np.testing.assert_allclose(values.var(axis=0), variance, rtol=.06)
    assert np.max(np.abs(values.mean(axis=0))) / np.sqrt(variance) < .04


def test_gaussian_distractors_match_variance_and_are_independent_of_target():
    generated = generate("dependent_nuisance", n_fit=16000)
    population = generated["population"]
    X = (generated["splits"]["fit"]["X"] - population["location"]) / population["scale"]
    y = generated["splits"]["fit"]["y"]
    signal = generated["support"]
    first, second = population["distractor_supports"]
    expected_variance = .5 * (1.5 ** 2 + 3.5 ** 2) * np.exp(.06 ** 2)
    assert population["signal_coordinate_variance_before_transform"] == expected_variance
    np.testing.assert_allclose(X.var(axis=0), expected_variance, rtol=.055)
    for block in (first, second):
        correlations = np.corrcoef(X[:, block], rowvar=False)
        off_diagonal = correlations[np.triu_indices(3, k=1)]
        np.testing.assert_allclose(off_diagonal, .7, atol=.025, rtol=0)
        label_correlation = np.corrcoef(np.column_stack((X[:, block], y)), rowvar=False)[:-1, -1]
        assert np.max(np.abs(label_correlation)) < .035
        squared_label_correlation = np.corrcoef(np.column_stack((X[:, block] ** 2, y)), rowvar=False)[:-1, -1]
        assert np.max(np.abs(squared_label_correlation)) < .035
    cross = np.corrcoef(X[:, first + second + signal], rowvar=False)
    assert np.max(np.abs(cross[:3, 3:6])) < .035
    assert np.max(np.abs(cross[:6, 6:])) < .035
    description = population["dependent_nuisance"]
    assert description["number_of_blocks"] == 2 and description["block_dimension"] == 3
    assert description["alternative_cluster_labels_created"] is False
    assert "distributions differ" in population["nuisance_marginal_matching"]


def test_distractor_seed_provenance_uses_separate_streams_for_each_block_and_split():
    generated = generate("dependent_nuisance")
    assert generated["population"]["distractor_seed_root"] == {"entropy": 823, "spawn_key": [4]}
    for index, split in enumerate(("fit", "validation", "test")):
        provenance = generated["split_seeds"][split]
        assert provenance["entropy"] == 823 and provenance["spawn_key"] == [index + 1]
        assert provenance["distractor_blocks"] == [
            {"entropy": 823, "spawn_key": [4, index, 0]},
            {"entropy": 823, "spawn_key": [4, index, 1]},
        ]


def test_exact_minimum_features_for_two_distractor_blocks():
    generated = generate("dependent_nuisance", dimension=4, p=12)
    assert generated["population"]["remaining_matched_nuisance_support"] == []
    assert all(len(block) == 4 for block in generated["population"]["distractor_supports"])


@pytest.mark.parametrize("changes", [
    {"condition": "unknown"}, {"condition": "weak_separation", "case": "student_t"},
    {"condition": "dependent_nuisance", "case": "single_shell"},
    {"condition": "dependent_nuisance", "dimension": 5, "p": 14},
    {"case": "unknown"}, {"dimension": 1}, {"dimension": 13}, {"p": 2},
    {"n_fit": 1}, {"n_validation": 0}, {"n_test": -1}, {"seed": -1},
    {"p": np.inf}, {"dimension": np.nan}, {"n_fit": 40.5}, {"n_test": np.inf},
    {"seed": 1.5}, {"n_fit": True}, {"seed": False},
])
def test_invalid_conditions_and_noninteger_or_infeasible_sizes_fail(changes):
    arguments = {"condition": "baseline", **changes}
    with pytest.raises(ValueError):
        generate(**arguments)


def test_numpy_integer_inputs_are_accepted():
    result = generate(dimension=np.int64(3), p=np.int64(12), n_fit=np.int64(60), seed=np.int64(823))
    assert result["splits"]["fit"]["X"].shape == (60, 12)
