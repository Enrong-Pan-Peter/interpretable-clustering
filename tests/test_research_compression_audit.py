"""Selection separation and accounting checks for the compression audit."""

import numpy as np
import pytest

from atomic_research.compression_audit import audit_compression


def _data(seed=12):
    rng = np.random.default_rng(seed)
    result = []
    for n in (80, 60, 50):
        labels = np.arange(n) % 2
        coordinate = (2 * labels - 1) * 4 + rng.normal(0, .2, n)
        X = np.column_stack([coordinate, coordinate, rng.normal(size=n)])
        result.append((X, labels))
    return result[0][0], result[0][1], result[1][0], result[2][0]


def test_test_rows_cannot_change_selected_panels_or_paths():
    train, partition, val, test = _data()
    first = audit_compression(train, partition, val, test, [0, 1, 2], seed=4)
    second = audit_compression(train, partition, val, test * -17 + 11, [0, 1, 2], seed=4)
    for name in first["policies"]:
        a, b = first["policies"][name], second["policies"][name]
        assert a["selected_panel"] == b["selected_panel"]
        assert a["trace"] == b["trace"]
        assert a["selected_validation_predictions"] == b["selected_validation_predictions"]
    assert first["settings"]["test_used_for_selection"] is False


def test_label_flip_changes_orientation_without_changing_selection():
    train, partition, val, test = _data()
    first = audit_compression(train, partition, val, test, [0, 1, 2], seed=4)
    flipped = audit_compression(train, 1 - partition, val, test, [0, 1, 2], seed=4)
    for name in first["policies"]:
        a, b = first["policies"][name], flipped["policies"][name]
        assert a["selected_panel"] == b["selected_panel"]
        assert a["trace"] == b["trace"]
        np.testing.assert_array_equal(a["selected_test_predictions"], 1 - np.array(b["selected_test_predictions"]))


def test_redundant_signal_compresses_and_all_deletion_diagnostics_are_present():
    train, partition, val, test = _data()
    result = audit_compression(train, partition, val, test, [0, 1, 2])
    for outcome in result["policies"].values():
        assert len(outcome["selected_panel"]) == 1
        assert outcome["selected_panel"][0] in (0, 1)
        assert outcome["selected_model"]["test_fidelity"]["disagreement"] == 0
    for family in ("frozen_knn", "refit_kmeans"):
        diagnostics = result["one_feature_deletions"][family]
        assert {row["removed"] for row in diagnostics} == {0, 1, 2}
        for row in diagnostics:
            assert len(row["training_labels"]) == len(train)
            assert len(row["validation_predictions"]) == len(val)
            assert len(row["test_predictions"]) == len(test)
            assert len(row["validation_folds"]) == 3


def test_shared_candidates_fit_once_and_accounting_includes_all_work():
    train, partition, val, test = _data()
    result = audit_compression(train, partition, val, test, [0, 1, 2])
    costs = result["accounting"]
    keys = [(r["family"], tuple(r["panel"])) for r in result["evaluated_candidates"]]
    assert len(keys) == len(set(keys)) == costs["model_fits"] == costs["unique_candidates"]
    assert costs["model_fits"] == costs["knn_fits"] + costs["kmeans_fits"]
    assert costs["prediction_calls"] == 3 * costs["model_fits"]
    assert costs["kmeans_initializations_requested"] == 10 * costs["kmeans_fits"]
    assert costs["evaluation_requests"] == costs["cache_hits"] + costs["unique_candidates"]
    assert costs["cache_hits"] > 0
    assert costs["elapsed_seconds"] >= costs["fit_seconds"] + costs["prediction_seconds"] > 0


def test_degenerate_validation_reference_disables_selection_but_reports_deletions():
    train, partition, val, test = _data()
    val[:, :2] = 4
    result = audit_compression(train, partition, val, test, [0, 1, 2])
    assert result["reference_validity"]["selection_valid"] is False
    for outcome in result["policies"].values():
        assert outcome["selected_panel"] == [0, 1, 2]
        assert outcome["trace"] == []
        assert outcome["status"] == "reference_validation_group_too_small"
    assert len(result["one_feature_deletions"]["frozen_knn"]) == 3


def test_fold_indices_are_fixed_disjoint_and_cover_validation():
    train, partition, val, test = _data()
    result = audit_compression(train, partition, val, test, [0, 1, 2], seed=8)
    indices = [i for fold in result["validation_fold_indices"] for i in fold]
    assert sorted(indices) == list(range(len(val)))
    for step in result["policies"]["frozen_knn_foldwise_disagreement"]["trace"]:
        if step["accepted"]:
            assert step["max_fold_disagreement"] <= .05


def test_single_feature_and_arbitrary_algorithm_label_values():
    train, partition, val, test = _data()
    result = audit_compression(train, np.where(partition, "right", "left"), val, test, [0])
    assert result["label_values"] == ["left", "right"]
    assert result["one_feature_deletions"] == {"frozen_knn": [], "refit_kmeans": []}
    assert all(p["selected_panel"] == [0] for p in result["policies"].values())


def test_invalid_arguments_rejected():
    train, partition, val, test = _data()
    with pytest.raises(ValueError, match="exactly two"):
        audit_compression(train, np.zeros(len(train)), val, test, [0, 1])
    with pytest.raises(ValueError, match="unique"):
        audit_compression(train, partition, val, test, [0, 0])
