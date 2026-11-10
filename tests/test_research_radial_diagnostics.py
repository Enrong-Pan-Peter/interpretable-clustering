"""Pipeline tests for label/test isolation and the simulated population map."""
from copy import deepcopy

import numpy as np
from threadpoolctl import threadpool_limits

from atomic_research import radial_diagnostics as diagnostic


def test_generator_replays_fixed_population_and_distinct_split_streams():
    args = ("quartic_shells", 3, 9, 60, 60, 60, 1191)
    a, b = diagnostic.generate_synthetic_splits(*args), diagnostic.generate_synthetic_splits(*args)
    assert a["support"] == b["support"]
    assert a["feature_map"] == b["feature_map"]
    expected = np.flatnonzero(np.array(a["feature_map"]["original_column_to_latent_column"]) < 3)
    np.testing.assert_array_equal(a["support"], expected)
    for split in ("fit", "validation", "test"):
        np.testing.assert_array_equal(a["splits"][split]["X"], b["splits"][split]["X"])
    assert not np.array_equal(a["splits"]["fit"]["X"], a["splits"]["test"]["X"])
    assert len({tuple(s["spawn_key"]) for s in a["split_seeds"].values()}) == 3


def test_changed_annotations_and_test_data_cannot_change_fit_or_selection(tmp_path, monkeypatch):
    job = {"name": "isolation", "case": "shells", "dimension": 2, "p": 8,
           "n_fit": 60, "n_validation": 60, "n_test": 60, "seed": 1192,
           "stage": "candidate-ranking", "candidates": 3}
    original = diagnostic.generate_synthetic_splits("shells", 2, 8, 60, 60, 60, 1192)
    changed = deepcopy(original)
    rng = np.random.default_rng(1193)
    for split in changed["splits"].values():
        split["y"] = rng.integers(0, 2, len(split["y"]))
    changed["splits"]["test"]["X"] = rng.normal(size=(60, 8)) * 3. + 5.
    reports = []
    with threadpool_limits(limits=1):
        for name, data in (("original", original), ("changed", changed)):
            monkeypatch.setattr(diagnostic, "generate_synthetic_splits", lambda *args, data=data: deepcopy(data))
            directory = tmp_path / name
            directory.mkdir()
            reports.append(diagnostic.run_case(job, directory))
    a, b = reports
    assert a["selected_candidate"] == b["selected_candidate"]
    assert a["selected_support"] == b["selected_support"]
    assert a["frozen_validation_heuristic_decision"] == b["frozen_validation_heuristic_decision"]
    for left, right in zip(a["candidate_results"], b["candidate_results"]):
        for family in ("radial1", "radial2"):
            for parameter in ("support", "center", "scale", "locations", "width", "weights", "log_z", "rule"):
                assert left["models"][family][parameter] == right["models"][family][parameter]
        assert left["metrics"]["validation"]["common_full_space_gain"] == right["metrics"]["validation"]["common_full_space_gain"]
    assert a["selected_metrics"]["test"]["common_full_space_gain"] != b["selected_metrics"]["test"]["common_full_space_gain"]
