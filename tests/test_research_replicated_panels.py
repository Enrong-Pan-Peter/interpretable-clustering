"""Protocol separation, rule algebra and saved-result checks."""
import inspect
import json
from types import SimpleNamespace

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from atomic_research import replicated_panels as panels
from scripts import run_research_panel_replication as suite


def sample(seed=11, n=100, p=8):
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 2, n)
    X = rng.normal(size=(n, p))
    X[:, :3] += (2*group-1)[:, None]*2.
    return X * np.geomspace(.02, 15., p) + np.linspace(-40, 70, p)


@pytest.fixture
def fitted():
    X = sample()
    X[0, 0] = np.nan
    with threadpool_limits(limits=1):
        return panels.fit_panel_ladder(X, cap=5, seed=11, steps=5, restarts=1)


def test_four_way_split_disjoint_complete_reproducible():
    split = panels.split_four(803, 9)
    assert [len(x) for x in split] == [200, 200, 200, 203]
    assert sorted(np.concatenate(split).tolist()) == list(range(803))
    assert all(np.array_equal(a, b) for a, b in zip(split, panels.split_four(803, 9)))
    with pytest.raises(ValueError):
        panels.split_four(79, 9)


def test_ladder_is_training_only_nested_and_has_no_zero_weight_fillers(fitted):
    assert fitted.model is not None
    assert len(fitted.panels) <= 5
    for k, panel in enumerate(fitted.panels, 1):
        assert len(panel) == k
        assert all(fitted.model.weights[j] > 0 for j in panel)
        if k > 1:
            assert set(fitted.panels[k-2]).issubset(panel)
    assert not {"y", "labels", "Xval", "Xtest"}.intersection(inspect.signature(panels.fit_panel_ladder).parameters)


def test_exported_rule_matches_native_predictions_in_original_units_with_missing_values(fitted):
    X = sample(seed=12, n=137)
    X[0, :] = np.nan
    X[2, 1] = np.inf
    X[3, 2] = -np.inf
    names = [f"feature_{j}" for j in range(X.shape[1])]
    for panel in [None, *fitted.panels]:
        rule = panels.linear_rule(fitted, names, panel)
        serialized = json.loads(json.dumps(rule))
        np.testing.assert_array_equal(panels.predict_linear_rule(serialized, X), fitted.predict(X, panel))
    with pytest.raises(ValueError, match="integer"):
        panels.linear_rule(fitted, names, [0.5])


def test_no_bounded_prefix_is_reported_without_fallback_when_validation_too_small(fitted):
    selected = panels.validation_selection(fitted, sample(seed=14, n=20), family_size=10)
    assert selected["bounded_panel"] is None
    assert all(record["upper_error"] > .05 for record in selected["records"])
    assert "Xtest" not in inspect.signature(panels.validation_selection).parameters


def test_alignment_for_replication_is_frozen_on_validation():
    a_val = np.array([0, 0, 1, 1]*5)
    a_test = np.array([0, 0, 0, 1]*5)
    # Opposite labels on validation, identical labels on test: fixing the
    # validation flip must report 100% test disagreement, not realign test.
    report = panels.replication(a_val, 1-a_val, a_test, a_test, [0, 1], [1, 2])
    assert report["validation_orientation_flip"]
    assert report["validation"]["disagreement"] == 0
    assert report["test"]["disagreement"] == 1
    assert report["feature_jaccard"] == pytest.approx(1/3)


def test_constant_discovery_has_no_model_or_selected_panel():
    fitted = panels.fit_panel_ladder(np.ones((30, 5)), cap=4)
    selected = panels.validation_selection(fitted, np.ones((20, 5)), family_size=8)
    assert fitted.model is None
    assert selected["empirical_panel"] is None and selected["bounded_panel"] is None


def test_full_case_test_rows_and_annotations_cannot_change_models_or_selections(tmp_path, monkeypatch):
    args = SimpleNamespace(dataset="mean_shift", seed=18, n=160, p=10, signal_features=5,
        separation=3., cap=6, steps=4, restarts=1, alpha=.05, max_error=.05)
    a, b = tmp_path/"a", tmp_path/"b"
    a.mkdir()
    b.mkdir()
    with threadpool_limits(limits=1):
        before = panels.run_case(args, a)
        loader = panels.load_dataset
        def change_only_test_and_all_annotations(*arg, **kw):
            dataset = loader(*arg, **kw)
            _, _, _, test = panels.split_four(len(dataset.X), args.seed+37000)
            dataset.X[test] = -3*dataset.X[test]+19
            dataset.y[:] = 0
            return dataset
        monkeypatch.setattr(panels, "load_dataset", change_only_test_and_all_annotations)
        after = panels.run_case(args, b)
    for name in ("A", "B"):
        assert before["learners"][name]["selection"] == after["learners"][name]["selection"]
        with np.load(a/f"{name}_model.npz") as old, np.load(b/f"{name}_model.npz") as new:
            for key in old.files:
                np.testing.assert_array_equal(old[key], new[key])
        assert after["learners"][name]["full"]["test_ari"] is None
        for row in after["learners"][name]["prefixes"]:
            assert row["test_ari"] is None and row["rule_export_verified"]
    assert (a/"summary.json").exists() and (a/"predictions.npz").exists()
    protocol = json.loads((a/"data_protocol.json").read_text())
    rows = sum(protocol["rows"].values(), [])
    assert len(rows) == len(set(rows)) == args.n


def test_suite_plan_checks_beyond_three_features_without_enumeration():
    planned = suite.jobs(suite.parser().parse_args([]))
    assert len(planned) == len({j["name"] for j in planned}) == 27
    assert {j["signal_features"] for j in planned if j["dataset"] == "mean_shift"} == {5, 8, 12}
    assert {j["p"] for j in planned if j["dataset"] == "mean_shift"} == {50, 200}
    assert all(j["cap"] == 16 for j in planned)


def test_failed_suite_records_failure_and_current_case(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("controlled failure")
    monkeypatch.setattr(suite, "run_case", fail)
    with pytest.raises(RuntimeError, match="controlled failure"):
        suite.main(["--suite", "smoke", "--output", str(tmp_path)])
    manifest = json.loads(next(tmp_path.glob("*/manifest.json")).read_text())
    assert manifest["status"] == "failed" and manifest["completed"] == []
    assert manifest["current_job"] == "smoke_mean_shift_seed19"
