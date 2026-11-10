"""Behavioral checks for blind, budget-matched feature-panel search.

Controlled objectives isolate the proposal mechanism from radial-model fitting.
These checks establish search mechanics, not scientific clustering performance.
"""

import inspect
import json
from copy import deepcopy
from itertools import combinations

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.stats import multivariate_normal

from atomic_research.radial_panels import RadialPanel
from atomic_research.radial_search import search_panels, squared_dependence
from atomic_research import radial_search_experiment


METHODS = ("random", "random_local", "dependence_local", "shuffled_dependence_local")


def data(features=12):
    rng = np.random.default_rng(118)
    return rng.normal(size=(48, features)), rng.normal(size=(37, features))


def controlled_score(support):
    return float(sum((feature + 1) ** 2 for feature in support) - 17 * len(support))


@pytest.mark.parametrize("method", METHODS)
def test_exact_unique_evaluation_budget_and_trace(method):
    X_fit, X_search = data()
    evaluated = []

    def evaluate(support):
        assert isinstance(support, tuple)
        evaluated.append(support)
        return controlled_score(support)

    result = search_panels(
        X_fit, X_search, method=method, budget=27, max_size=5, seed=813,
        evaluate=evaluate,
    )
    assert result["budget"] == 27
    assert result["evaluations"] == len(result["trace"]) == len(evaluated) == 27
    assert len(set(evaluated)) == 27
    assert evaluated == [tuple(item["support"]) for item in result["trace"]]
    assert all(1 <= len(support) <= 5 for support in evaluated)
    assert all(support == tuple(sorted(set(support))) for support in evaluated)
    assert all(0 <= feature < 12 for support in evaluated for feature in support)
    running_best = -np.inf
    for item in result["trace"]:
        assert item["size"] == len(item["support"])
        assert item["score"] == controlled_score(item["support"])
        running_best = max(running_best, item["score"])
        assert item["best_score"] == running_best
        assert item["proposal"]
    best = max(result["trace"], key=lambda item: (item["score"], -item["size"], -item["index"]))
    assert result["selected_support"] == best["support"]
    assert result["model"] is None
    assert result["background"] is None


@pytest.mark.parametrize("method", METHODS)
def test_exhausting_feasible_panels_does_not_repeat_evaluations(method):
    X_fit, X_search = data(features=4)
    expected = {support for size in range(1, 4) for support in combinations(range(4), size)}
    result = search_panels(
        X_fit, X_search, method=method, budget=14, max_size=3, seed=31,
        evaluate=controlled_score,
    )
    assert result["budget"] == 14
    assert result["evaluations"] == len(expected) == 14
    assert {tuple(item["support"]) for item in result["trace"]} == expected


@pytest.mark.parametrize("method", METHODS)
def test_seed_replays_all_search_decisions(method):
    X_fit, X_search = data()
    kwargs = dict(method=method, budget=24, max_size=5, seed=97, evaluate=controlled_score)
    first = search_panels(X_fit, X_search, **kwargs)
    second = search_panels(X_fit, X_search, **kwargs)
    for key in ("selected_support", "evaluations", "budget", "config"):
        assert first[key] == second[key]
    without_timing = lambda trace: [{key: value for key, value in item.items()
                                     if not key.endswith("seconds")} for item in trace]
    assert without_timing(first["trace"]) == without_timing(second["trace"])


@pytest.mark.parametrize("budget", [1, 7, 20])
def test_methods_share_the_same_random_warmup(budget):
    X_fit, X_search = data()
    traces = [search_panels(
        X_fit, X_search, method=method, budget=budget, max_size=5, seed=71,
        evaluate=controlled_score,
    )["trace"] for method in METHODS]
    warmup = min(8, max(1, budget // 2))
    expected = [item["support"] for item in traces[0][:warmup]]
    assert all([item["support"] for item in trace[:warmup]] == expected for trace in traces)


@pytest.mark.parametrize("method", METHODS)
def test_equal_scores_prefer_smaller_panels_then_earlier_evaluation(method):
    X_fit, X_search = data(features=4)
    result = search_panels(
        X_fit, X_search, method=method, budget=14, max_size=3, seed=923,
        evaluate=lambda support: 7.0,
    )
    singleton = next(item for item in result["trace"] if item["size"] == 1)
    assert result["selected_support"] == singleton["support"]


@pytest.mark.parametrize("method", METHODS)
def test_panels_are_not_capped_at_three_features(method):
    X_fit, X_search = data(features=20)
    result = search_panels(
        X_fit, X_search, method=method, budget=24, max_size=8, seed=11,
        evaluate=controlled_score,
    )
    assert max(item["size"] for item in result["trace"]) > 3
    assert all(item["size"] <= 8 for item in result["trace"])


def test_search_api_does_not_accept_oracle_support_labels_or_case_name():
    parameters = inspect.signature(search_panels).parameters
    assert set(parameters) == {"X_fit", "X_search", "method", "budget", "max_size", "seed", "evaluate"}
    assert all(parameter.kind != inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())


@pytest.mark.parametrize("changes", [
    {"budget": 0}, {"budget": -3}, {"max_size": 0}, {"max_size": 5},
    {"method": "oracle"}, {"budget": 15},
])
def test_invalid_search_constraints_are_rejected_before_scoring(changes):
    X_fit, X_search = data(features=4)
    kwargs = dict(method="random", budget=10, max_size=3, seed=7)
    kwargs.update(changes)
    calls = []
    with pytest.raises(ValueError):
        search_panels(X_fit, X_search, **kwargs, evaluate=lambda support: calls.append(support) or 0.0)
    assert calls == []


def test_local_refinement_can_improve_a_controlled_objective_at_equal_budget():
    """A concrete mechanics example, not an expected dominance guarantee."""
    X_fit, X_search = data()
    useful = {2, 4, 9, 11}

    def score(support):
        selected = set(support)
        return float(2 * len(selected & useful) - len(selected - useful))

    results = {method: search_panels(
        X_fit, X_search, method=method, budget=60, max_size=6, seed=11, evaluate=score,
    ) for method in ("random", "random_local")}
    assert results["random_local"]["evaluations"] == results["random"]["evaluations"] == 60
    assert results["random_local"]["search_gain"] > results["random"]["search_gain"]
    assert set(results["random_local"]["selected_support"]) == useful
    assert any(item["proposal"] == "local_add_drop_swap"
               for item in results["random_local"]["trace"])


@pytest.mark.parametrize("method", METHODS)
def test_selected_radial_score_replays_from_saved_fit_only_parameters(method):
    X_fit, X_search = data(features=4)
    X_search = 1.3 * X_search + 0.7
    result = search_panels(X_fit, X_search, method=method, budget=3, max_size=3, seed=43)
    model = RadialPanel.from_dict(result["model"])
    support = np.asarray(result["selected_support"])
    background = result["background"]
    mean = np.asarray(background["mean"])
    covariance = np.asarray(background["covariance"])
    independent_background = multivariate_normal.logpdf(
        X_search[:, support], mean=mean[support], cov=covariance[np.ix_(support, support)],
    )
    replayed_gain = np.mean(model.logpdf(X_search) - independent_background)
    assert result["search_gain"] == pytest.approx(replayed_gain, abs=1e-11)
    assert_allclose(model.center, X_fit[:, support].mean(axis=0), atol=1e-12)
    assert_allclose(model.scale, X_fit[:, support].std(axis=0), atol=1e-12)
    assert_allclose(mean, X_fit.mean(axis=0), atol=1e-12)


def test_squared_dependence_detects_a_pair_with_little_linear_correlation():
    rng = np.random.default_rng(133)
    x = rng.normal(size=8000)
    y = rng.choice([-1., 1.], size=len(x)) * x
    X = np.column_stack((x, y, rng.normal(size=len(x)), rng.normal(size=len(x))))
    dependence = squared_dependence(X)
    assert abs(np.corrcoef(x, y)[0, 1]) < 0.05
    assert dependence[0, 1] > 0.99
    assert dependence[0, 2] < 0.05
    assert_allclose(dependence, dependence.T, atol=1e-14)
    assert_allclose(np.diag(dependence), 0.)
    assert_allclose(squared_dependence(X * [3., -2., .4, 7.] + [9., -4., 3., 1.]),
                    dependence, atol=1e-12)


def test_shuffled_dependence_control_preserves_graph_weights_and_fit_only_normalization():
    X_fit, X_search = data()
    kwargs = dict(budget=30, max_size=5, seed=97, evaluate=controlled_score)
    guided = search_panels(X_fit, X_search, method="dependence_local", **kwargs)
    shuffled = search_panels(X_fit, X_search, method="shuffled_dependence_local", **kwargs)
    changed_search = search_panels(
        X_fit, 9 * X_search + np.arange(12), method="shuffled_dependence_local", **kwargs,
    )
    matrix = np.asarray(guided["dependence_matrix"])
    control = np.asarray(shuffled["dependence_matrix"])
    permutation = np.asarray(shuffled["dependence_feature_permutation"])
    assert sorted(permutation.tolist()) == list(range(12))
    assert not np.array_equal(permutation, np.arange(12))
    assert not np.array_equal(matrix, control)
    assert_array_equal(control, matrix[np.ix_(permutation, permutation)])
    assert_array_equal(np.sort(control.ravel()), np.sort(matrix.ravel()))
    assert_allclose(matrix, squared_dependence(X_fit), atol=1e-14)
    # The mocked objective is data-independent: changing search measurements
    # therefore isolates whether proposal preprocessing accidentally uses them.
    assert _without_timings(shuffled) == _without_timings(changed_search)
    assert guided["dependence_feature_permutation"] is None


@pytest.mark.parametrize("problem", ["nonfinite", "shape", "empty", "columns"])
def test_invalid_data_is_rejected_before_scoring(problem):
    X_fit, X_search = data(features=4)
    if problem == "nonfinite":
        X_search[0, 0] = np.nan
    elif problem == "shape":
        X_fit = X_fit[:, 0]
    elif problem == "empty":
        X_search = X_search[:0]
    else:
        X_search = X_search[:, :3]
    calls = []
    with pytest.raises(ValueError):
        search_panels(X_fit, X_search, method="random", budget=3, max_size=3, seed=7,
                      evaluate=lambda support: calls.append(support) or 0.)
    assert calls == []


@pytest.mark.parametrize("invalid_score", [np.nan, np.inf, -np.inf])
def test_nonfinite_scores_abort_instead_of_becoming_selectable(invalid_score):
    X_fit, X_search = data(features=4)
    with pytest.raises(ValueError, match="nonfinite"):
        search_panels(X_fit, X_search, method="random", budget=3, max_size=3, seed=7,
                      evaluate=lambda support: invalid_score)


def _without_timings(value):
    if isinstance(value, dict):
        return {key: _without_timings(item) for key, item in value.items()
                if not key.endswith("seconds")}
    if isinstance(value, list):
        return [_without_timings(item) for item in value]
    return value


def _manual_saved_rule(rule, X):
    """Replay the published expression without calling the model predictor."""
    if rule["constant_label"] is not None:
        return np.full(len(X), rule["constant_label"], dtype=int)
    squared_radius = np.sum(
        ((X[:, rule["support"]] - rule["center"]) / rule["scale"]) ** 2, axis=1,
    )
    return (squared_radius > rule["threshold"]).astype(int)


@pytest.mark.parametrize("perturbation", ["annotations_and_metadata", "validation_and_test_matrices"])
def test_pipeline_search_is_isolated_from_truth_and_unused_data(tmp_path, monkeypatch, perturbation):
    """Change forbidden inputs while preserving both permitted search matrices."""
    job = {
        "name": "isolation", "case": "shells", "dimension": 2, "p": 6,
        "n_fit": 60, "n_search": 40, "n_validation": 40, "n_test": 40,
        "seed": 1331, "search_seed": 7931, "budget": 10, "max_size": 4,
        "methods": list(METHODS),
    }
    generated = radial_search_experiment.generate_synthetic_splits(
        "shells", 2, 6, 100, 40, 40, 1331,
    )
    altered = deepcopy(generated)
    rng = np.random.default_rng(1789)
    if perturbation == "annotations_and_metadata":
        for block in altered["splits"].values():
            block["y"] = rng.integers(0, 3, size=len(block["y"]))
        altered["support"] = [j for j in range(6) if j not in generated["support"]][:2]
        altered["feature_map"]["original_column_to_latent_column"] = list(reversed(range(6)))
        altered["feature_map"]["feature_names"] = [f"untrusted_annotation_{j}" for j in range(6)]
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

    for method in METHODS:
        original_search = json.loads((directories[0] / f"{method}_search.json").read_text())
        altered_search = json.loads((directories[1] / f"{method}_search.json").read_text())
        assert _without_timings(original_search) == _without_timings(altered_search)
        assert original_search["selected_support"] == altered_search["selected_support"]
        X_search = generated["splits"]["fit"]["X"][60:]
        model = RadialPanel.from_dict(original_search["model"])
        direct_rule = _manual_saved_rule(original_search["model"]["rule"], X_search)
        assert_array_equal(direct_rule, model.predict(X_search))
        with np.load(directories[0] / "predictions.npz") as predictions:
            assert_array_equal(direct_rule, predictions[f"{method}__search"])
        # Every fitted proposal retains the same explicit assignment expression.
        for candidate in original_search["trace"]:
            fitted = RadialPanel.from_dict(candidate["model"])
            assert fitted.support.tolist() == candidate["support"]
            assert_array_equal(_manual_saved_rule(candidate["model"]["rule"], X_search),
                               fitted.predict(X_search))
