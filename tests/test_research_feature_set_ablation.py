"""Independent checks for the dependence-statistic by local-policy ablation.

These tests verify the comparison mechanics and information boundaries, not
scientific superiority of any feature-set discovery method.
"""

from copy import deepcopy
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.stats import multivariate_normal

from atomic_research import radial_search_experiment
from atomic_research.feature_dependence import kernel_dependence
from atomic_research.radial_panels import RadialPanel
from atomic_research.radial_search import ABLATION_METHODS, search_feature_sets


def data(features=12, rows=48):
    rng = np.random.default_rng(118)
    return rng.normal(size=(rows, features)), rng.normal(size=(37, features))


def without_timings(value):
    if isinstance(value, dict):
        return {key: without_timings(item) for key, item in value.items()
                if not key.endswith("seconds")}
    if isinstance(value, list):
        return [without_timings(item) for item in value]
    return value


def independent_kernel_alignment(X):
    """Dense reference uses an explicit centering matrix, independent of production."""
    n, p = X.shape
    centered_kernels, bandwidths = [], []
    H = np.eye(n) - np.ones((n, n)) / n
    Z = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    for column in range(p):
        values = Z[:, column] ** 2
        distances = np.abs(np.subtract.outer(values, values))
        positive = distances[np.triu_indices(n, k=1)]
        positive = positive[positive > 0]
        if not len(positive):
            centered_kernels.append(np.zeros((n, n)))
            bandwidths.append(None)
        else:
            sigma = float(np.median(positive))
            centered_kernels.append(H @ np.exp(-0.5 * (distances / sigma) ** 2) @ H)
            bandwidths.append(sigma)
    result = np.zeros((p, p))
    for left in range(p):
        for right in range(left + 1, p):
            K, L = centered_kernels[left], centered_kernels[right]
            denominator = np.linalg.norm(K) * np.linalg.norm(L)
            value = np.sum(K * L) / denominator if denominator else 0.
            result[left, right] = result[right, left] = value
    return result, bandwidths


def test_kernel_dependence_matches_independent_centered_kernel_calculation():
    X_fit, _ = data(features=5, rows=31)
    actual, metadata = kernel_dependence(X_fit)
    expected, bandwidths = independent_kernel_alignment(X_fit)
    assert_allclose(actual, expected, atol=2e-13)
    assert_allclose(metadata["bandwidths"], bandwidths, atol=1e-13)
    assert metadata["fit_rows"] == len(X_fit)
    assert metadata["kind"]
    assert_allclose(actual, actual.T, atol=1e-14)
    assert_array_equal(np.diag(actual), np.zeros(5))
    assert np.isfinite(actual).all()
    assert np.all((actual >= -1e-13) & (actual <= 1 + 1e-13))


def test_kernel_dependence_is_invariant_to_units_offsets_and_signs():
    X_fit, _ = data(features=5)
    changed_units = X_fit * np.array([2., -3., .25, 7., -1.5]) + [13., 2., -4., 5., 8.]
    original, original_metadata = kernel_dependence(X_fit)
    transformed, transformed_metadata = kernel_dependence(changed_units)
    assert_allclose(transformed, original, atol=3e-13)
    assert_allclose(transformed_metadata["bandwidths"], original_metadata["bandwidths"], atol=2e-13)


def test_kernel_dependence_respects_row_and_feature_permutation():
    X_fit, _ = data(features=5)
    matrix, metadata = kernel_dependence(X_fit)
    columns = np.array([3, 0, 4, 1, 2])
    transformed, transformed_metadata = kernel_dependence(X_fit[::-1, columns])
    assert_allclose(transformed, matrix[np.ix_(columns, columns)], atol=3e-13)
    assert_allclose(transformed_metadata["bandwidths"], np.asarray(metadata["bandwidths"])[columns], atol=3e-13)


def test_constant_squared_feature_has_zero_dependence_without_nan():
    rng = np.random.default_rng(119)
    X = np.column_stack((np.tile([-1., 1.], 24), rng.normal(size=48), rng.normal(size=48)))
    actual, metadata = kernel_dependence(X)
    assert metadata["bandwidths"][0] is None
    assert_array_equal(actual[0], np.zeros(3))
    assert_array_equal(actual[:, 0], np.zeros(3))
    assert np.isfinite(actual).all()


def test_dense_kernel_guard_refuses_insufficient_memory_before_kernel_allocation(monkeypatch):
    X_fit, _ = data(features=5)
    from atomic_research import feature_dependence

    def unexpected_allocation(*args, **kwargs):
        pytest.fail("Dense kernel allocation happened before the memory guard.")

    monkeypatch.setattr(feature_dependence.np, "zeros", unexpected_allocation)
    with pytest.raises(ValueError, match="bytes"):
        kernel_dependence(X_fit, max_bytes=1)


def objective(support):
    useful = {2, 4, 9, 11}
    selected = set(support)
    return float(2 * len(selected & useful) - len(selected - useful))


@pytest.mark.parametrize("method", ABLATION_METHODS)
def test_ablation_obeys_unique_budget_and_deterministically_replays(method):
    X_fit, X_search = data()
    calls = []

    def evaluate(support):
        calls.append(support)
        return objective(support)

    kwargs = dict(method=method, budget=45, max_size=6, seed=11)
    result = search_feature_sets(X_fit, X_search, **kwargs, evaluate=evaluate)
    repeated = search_feature_sets(X_fit, X_search, **kwargs, evaluate=objective)
    assert result["budget"] == result["evaluations"] == len(result["trace"]) == len(calls) == 45
    assert len(set(calls)) == len(calls)
    assert all(isinstance(support, tuple) and 1 <= len(support) <= 6 for support in calls)
    assert calls == [tuple(row["support"]) for row in result["trace"]]
    assert without_timings(result) == without_timings(repeated)
    best = max(result["trace"], key=lambda row: (row["score"], -row["size"], -row["index"]))
    assert result["selected_support"] == best["support"]


@pytest.mark.parametrize("statistic", ["moment", "kernel"])
def test_first_and_best_receive_identical_exploration(statistic):
    X_fit, X_search = data()
    results = [search_feature_sets(
        X_fit, X_search, method=f"{statistic}_{policy}", budget=42, max_size=6,
        seed=71, evaluate=objective,
    ) for policy in ("best", "first")]
    exploration = results[0]["config"]["exploration_budget"]
    assert exploration == 21
    assert without_timings(results[0]["trace"][:exploration]) == without_timings(results[1]["trace"][:exploration])
    assert results[0]["dependence_matrix"] == results[1]["dependence_matrix"]


@pytest.mark.parametrize("statistic", ["moment", "kernel"])
def test_proposal_dependence_is_fit_only_even_when_search_measurements_change(statistic):
    X_fit, X_search = data()
    kwargs = dict(method=f"{statistic}_first", budget=42, max_size=6, seed=71, evaluate=objective)
    original = search_feature_sets(X_fit, X_search, **kwargs)
    altered = search_feature_sets(X_fit, 7 * X_search + np.arange(12), **kwargs)
    assert without_timings(original) == without_timings(altered)
    assert original["dependence_metadata"]["fit_rows"] == len(X_fit)
    if statistic == "kernel":
        reference, _ = independent_kernel_alignment(X_fit)
        assert_allclose(original["dependence_matrix"], reference, atol=3e-13)


@pytest.mark.parametrize("method", ABLATION_METHODS)
def test_local_trace_records_real_neighbors_ranking_and_budget_cost(method):
    X_fit, X_search = data()
    result = search_feature_sets(
        X_fit, X_search, method=method, budget=60, max_size=6, seed=11, evaluate=objective,
    )
    rows = {tuple(row["support"]): row for row in result["trace"]}

    def rank(support):
        row = rows[tuple(support)]
        return row["score"], -row["size"], -row["index"]

    assert result["local_steps"]
    previous_evaluations = result["config"]["exploration_budget"]
    for step in result["local_steps"]:
        parent, candidate = set(step["parent_support"]), set(step["candidate_support"])
        added, removed = candidate - parent, parent - candidate
        if len(added) == 1 and not removed:
            expected_move = "add"
        elif len(removed) == 1 and not added:
            expected_move = "drop"
        else:
            assert len(added) == len(removed) == 1
            expected_move = "swap"
        assert step["move_type"] == expected_move
        assert 1 <= len(candidate) <= 6
        assert previous_evaluations <= step["evaluations"] <= 60
        previous_evaluations = step["evaluations"]
        assert rows[tuple(step["candidate_support"])]["index"] < step["evaluations"]
        if not step["cache_hit"]:
            assert rows[tuple(step["candidate_support"])]["index"] == step["evaluations"] - 1
        improves = rank(step["candidate_support"]) > rank(step["incumbent_before"])
        assert step["improved"] == improves
        expected_incumbent = step["candidate_support"] if improves else step["incumbent_before"]
        assert step["incumbent_after"] == expected_incumbent


@pytest.mark.parametrize("statistic", ["moment", "kernel"])
def test_first_improvement_immediately_restarts_from_the_improved_feature_set(statistic):
    X_fit, X_search = data()
    result = search_feature_sets(
        X_fit, X_search, method=f"{statistic}_first", budget=60, max_size=6,
        seed=11, evaluate=objective,
    )
    steps = result["local_steps"]
    improvements = [index for index, step in enumerate(steps[:-1]) if step["improved"]]
    assert improvements, "The controlled objective must exercise an early successful move."
    for index in improvements:
        assert steps[index + 1]["parent_support"] == steps[index]["incumbent_after"]


@pytest.mark.parametrize("statistic", ["moment", "kernel"])
def test_best_improvement_completes_an_anchor_neighborhood_before_moving(statistic):
    X_fit, X_search = data()
    result = search_feature_sets(
        X_fit, X_search, method=f"{statistic}_best", budget=120, max_size=6,
        seed=11, evaluate=objective,
    )
    steps = result["local_steps"]
    completed = 0
    start = 0
    while start < len(steps):
        parent = steps[start]["parent_support"]
        end = start + 1
        while end < len(steps) and steps[end]["parent_support"] == parent:
            end += 1
        if end < len(steps):
            size = len(parent)
            expected = (12 - size if size < 6 else 0) + (size if size > 1 else 0) + size * (12 - size)
            assert end - start == expected
            assert len({tuple(step["candidate_support"]) for step in steps[start:end]}) == expected
            completed += 1
        start = end
    assert completed, "The budget must exercise at least one complete local neighborhood."


@pytest.mark.parametrize("method", ABLATION_METHODS)
def test_every_saved_score_remains_the_same_radial_density_gain(method):
    X_fit, X_search = data(features=5, rows=50)
    X_search = 1.3 * X_search + .7
    result = search_feature_sets(X_fit, X_search, method=method, budget=4, max_size=3, seed=43)
    background = result["background"]
    mean, covariance = np.asarray(background["mean"]), np.asarray(background["covariance"])
    assert_allclose(mean, X_fit.mean(axis=0), atol=1e-12)
    for row in result["trace"]:
        model = RadialPanel.from_dict(row["model"])
        support = np.asarray(row["support"])
        independent_background = multivariate_normal.logpdf(
            X_search[:, support], mean=mean[support], cov=covariance[np.ix_(support, support)],
        )
        assert row["score"] == pytest.approx(np.mean(model.logpdf(X_search) - independent_background), abs=1e-11)
        assert_allclose(model.center, X_fit[:, support].mean(axis=0), atol=1e-12)
        assert_allclose(model.scale, X_fit[:, support].std(axis=0), atol=1e-12)


@pytest.mark.parametrize("perturbation", ["annotations_and_metadata", "validation_and_test_matrices"])
def test_ablation_pipeline_never_selects_on_truth_or_holdout_data(tmp_path, monkeypatch, perturbation):
    job = {
        "name": "ablation_isolation", "case": "shells", "dimension": 2, "p": 6,
        "n_fit": 60, "n_search": 40, "n_validation": 40, "n_test": 40,
        "seed": 1331, "search_seed": 7931, "budget": 10, "max_size": 4,
        "methods": list(ABLATION_METHODS),
    }
    generated = radial_search_experiment.generate_synthetic_splits("shells", 2, 6, 100, 40, 40, 1331)
    altered = deepcopy(generated)
    rng = np.random.default_rng(1789)
    if perturbation == "annotations_and_metadata":
        for block in altered["splits"].values():
            block["y"] = rng.integers(0, 3, size=len(block["y"]))
        altered["support"] = [j for j in range(6) if j not in generated["support"]][:2]
        altered["feature_map"]["original_column_to_latent_column"] = list(reversed(range(6)))
        altered["feature_map"]["feature_names"] = [f"different_annotation_{j}" for j in range(6)]
        altered["population"].update(case="different_annotation", location=31., scale=7.)
    else:
        for split in ("validation", "test"):
            altered["splits"][split]["X"] = rng.normal(size=(40, 6)) * 2.1 + 1.7
    assert_array_equal(generated["splits"]["fit"]["X"], altered["splits"]["fit"]["X"])
    directories = []
    for index, source in enumerate((generated, altered)):
        directory = tmp_path / f"run_{index}"
        directory.mkdir()
        directories.append(directory)
        monkeypatch.setattr(radial_search_experiment, "generate_synthetic_splits",
                            lambda *args, source=source, **kwargs: deepcopy(source))
        radial_search_experiment.run_search_case(job, directory)
    for method in ABLATION_METHODS:
        original = json.loads((directories[0] / f"{method}_search.json").read_text())
        changed = json.loads((directories[1] / f"{method}_search.json").read_text())
        assert without_timings(original) == without_timings(changed)
        with np.load(directories[0] / "predictions.npz") as before, np.load(directories[1] / "predictions.npz") as after:
            assert_array_equal(before[f"{method}__search"], after[f"{method}__search"])
