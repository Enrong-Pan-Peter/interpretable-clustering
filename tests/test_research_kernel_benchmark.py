"""Protocol and synthetic-information checks for the kernel development suite."""
from types import SimpleNamespace
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from atomic_research.kernel_benchmark import make_benchmark, fit_candidates


@pytest.mark.parametrize("case,s", [("moons", 2), ("grouped_moons", 8),
    ("distributed_moons", 8), ("rings", 2), ("spirals", 2), ("covariance_pairs", 8)])
def test_generators_are_repeatable_with_hidden_shuffled_support(case, s):
    a = make_benchmark(case, n=100, p=20, signals=s, seed=93)
    b = make_benchmark(case, n=100, p=20, signals=s, seed=93)
    np.testing.assert_array_equal(a.X, b.X)
    np.testing.assert_array_equal(a.y, b.y)
    assert a.X.shape == (100, 20)
    assert np.isfinite(a.X).all()
    assert len(a.reference_panel) == s
    assert a.reference_panel != tuple(range(s))


def test_covariance_pairs_retain_population_information_beyond_one_pair():
    d = make_benchmark("covariance_pairs", n=20000, p=12, signals=8, seed=93)
    pairs = np.asarray(d.metadata["oracle_pairs"])
    products = d.X[:, pairs[:, 0]] * d.X[:, pairs[:, 1]]
    error_full = np.mean((products.sum(axis=1) > 0) != d.y)
    error_pair = np.mean((products[:, 0] > 0) != d.y)
    assert .015 < error_full < .045
    assert .18 < error_pair < .23
    # Same N(0,1) univariate marginals; signal is in joint dependence.
    assert np.max(np.abs(d.X.mean(axis=0))) < .04


def test_fit_candidate_boundary_accepts_only_discovery_X_and_config(monkeypatch):
    import atomic_research.kernel_benchmark as module
    calls = []
    X = np.random.default_rng(4).normal(size=(40, 8))
    def capture(data, **config):
        calls.append((data.copy(), config))
        return config
    monkeypatch.setattr(module, "fit_kernel_panel", capture)
    args = SimpleNamespace(budget=6, rank=2, seed=93, steps=2, restarts=1, neighbors=7, max_samples=30)
    models = fit_candidates(X, args)
    assert len(models) == len(calls) == 5
    for data, config in calls:
        np.testing.assert_array_equal(data, X)
        assert not any(key in config for key in ("y", "reference", "test", "validation"))
    assert sum(config["mixing"] for _, config in calls) == 3


def test_pilot_grid_predeclares_nulls_and_twelve_feature_case():
    script = Path(__file__).resolve().parents[1] / "scripts/run_research_kernel_panels.py"
    spec = importlib.util.spec_from_file_location("kernel_cli", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    args = module.parser().parse_args([])
    jobs = module.jobs(args)
    assert len(jobs) == 21
    assert {j["dataset"] for j in jobs} >= {"null_correlated", "null_independent", "shells", "covariance_pairs"}
    assert all(j["budget"] >= 12 for j in jobs if j["dataset"] == "mean_shift")
    assert len({j["name"] for j in jobs}) == len(jobs)


def test_single_shell_is_one_population_not_an_annotation_recovery_task():
    d = make_benchmark("single_shell", n=400, p=20, signals=5, seed=93)
    assert np.unique(d.y).tolist() == [0]
    assert d.reference_kind == "negative_control"
    radius = np.linalg.norm(d.X[:, d.reference_panel], axis=1)
    assert radius.min() >= .98 and radius.max() <= 1.02
