"""Scientific protocol and output-integrity checks for the staged audits."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from atomic_research import obstacle_audits as audits
from atomic_research.experiment import prepare, write_json, annotation_ari
from atomic_research.scoring import score_panel
from scripts import run_research_obstacle_suite as suite


def small_args():
    return SimpleNamespace(n=80, p=8, signal_features=3, max_features=3, separation=5.,
                           steps=3, restarts=1, neighbors=[5, 10], compression_methods=["sparse_kmeans"])


def test_restarts_chosen_only_within_each_prescribed_bound():
    models = [SimpleNamespace(diagnostics={"l1_bound": b, "native_objective": score})
              for b, score in [(2., 7.), (1.25, 3.), (2., 6.), (1.25, 4.)]]
    assert audits.select_native_by_bound(models) == [models[3], models[0]]


def test_retention_reports_all_variants_and_ledger_matches_summary(tmp_path):
    with threadpool_limits(limits=1):
        report = audits.retention_case(small_args(), "mean_shift", 17, tmp_path)
    ledger = [json.loads(line) for line in (tmp_path / "comparisons.jsonl").read_text().splitlines()]
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert ledger == summary["rows"]
    assert len(report["rows"]) == 2 * 3 * (2 + 6 * 3)
    with np.load(tmp_path / "readout_predictions.npz") as predictions:
        for row in ledger:
            if row["valid_training_partition"]:
                assert len(predictions[row["prediction_key"] + "_train"]) == 40
                assert len(predictions[row["prediction_key"] + "_test"]) == 20
    for row in ledger:
        if row["readout"] == "refit_unweighted_centroid":
            assert "test_independent_centroid_valid" in row
        if row["readout"] == "full_native_centroid":
            assert row["test_fidelity_to_full_native"] == {"ari": 1., "disagreement": 0.}
            assert "discovery_native_weighted_geometry" in row
        if row["readout"] == "truncated_native_centroid":
            assert all(key in row for key in ("discovery_native_weighted_geometry",
                "discovery_representation_geometry", "discovery_original_space_geometry"))
    assert {row["prefix_size"] for row in ledger} == {None, 1, 2, 3}


def test_test_rows_and_annotations_cannot_change_retained_models(tmp_path, monkeypatch):
    args = small_args()
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    original_prepare = audits.prepare
    with threadpool_limits(limits=1):
        first = audits.retention_case(args, "mean_shift", 19, a)
        def changed_prepare(config):
            dataset, indices, scaler, (train, val, test) = original_prepare(config)
            dataset.y = np.zeros_like(dataset.y)
            return dataset, indices, scaler, (train, val + 31., test * -4. + 9.)
        monkeypatch.setattr(audits, "prepare", changed_prepare)
        second = audits.retention_case(args, "mean_shift", 19, b)
    for path in a.glob("*_model.npz"):
        with np.load(path) as before, np.load(b / path.name) as after:
            for key in before.files:
                np.testing.assert_array_equal(before[key], after[key])
    assert [r["panel"] for r in first["rows"]] == [r["panel"] for r in second["rows"]]
    assert all(r["test_ari"] is None for r in second["rows"])


def test_oracle_geometry_is_explicit_and_all_configurations_reported(tmp_path):
    with threadpool_limits(limits=1):
        report = audits.geometry_case(small_args(), 7, 80, tmp_path)
    assert report["source"] == "oracle_true_panel_ability_check_not_discovery"
    assert len(report["panel"]) == 3
    assert len(report["rows"]) == 7
    assert {(r["representation"], r["k"]) for r in report["rows"] if r["splitter"] == "spectral"} == {
        (rep, k) for rep in ("raw", "squared") for k in (5, 10)}
    assert all(0 <= v <= 1 for v in report["ten_neighbor_cross_fraction"].values())


def make_pilot(directory):
    config = SimpleNamespace(dataset="mean_shift", n=80, p=8, signal_features=3, seed=2,
                             separation=6., contrast=None, mode="search", splitter="spectral", k=10)
    dataset, indices, scaler, (train, val, test) = prepare(config)
    panel = (0, 1, 2)
    with threadpool_limits(limits=1):
        fitted = score_panel(train, panel, seed=config.seed)
        prediction = audits.knn_prediction(train[:, panel], fitted["labels"], test[:, panel])
    assert fitted["valid"]
    source = audits.ROOT / "atomic_research/scoring.py"
    write_json(directory / "manifest.json", {"config": vars(config), "status": "complete",
        "source_sha256": {"atomic_research/scoring.py": hashlib.sha256(source.read_bytes()).hexdigest()}})
    audits.write_data_protocol(directory, dataset, indices, scaler)
    write_json(directory / "summary.json", {"methods": {"sparse_kmeans": {
        "panel": panel, "reduced_panel": panel, "test_transfer_ari": annotation_ari(dataset.y[indices[2]], prediction)}}})
    np.savez_compressed(directory / "sparse_kmeans_assignment.npz", original_panel=panel,
                        original_X=train[:, panel], labels=fitted["labels"])


def test_compression_replays_teacher_and_separates_family_change(tmp_path):
    source, output = tmp_path / "source", tmp_path / "output"
    source.mkdir()
    output.mkdir()
    make_pilot(source)
    with threadpool_limits(limits=1):
        report = audits.compression_case(small_args(), source, output)
    assert len(report["rows"]) == 4
    assert report["methods"]["sparse_kmeans"]["pilot_teacher_replayed"]
    for row in report["rows"]:
        assert "same_panel_family_test_ari" in row
        assert "test_fidelity_to_same_panel_family" in row
        assert row["selected_size"] <= row["original_size"]
    saved = json.loads((output / "sparse_kmeans_deletions.json").read_text())
    assert saved["settings"]["test_used_for_selection"] is False
    assert len(saved["one_feature_deletions"]["frozen_knn"]) == 3


def test_compression_refuses_changed_pilot_source(tmp_path):
    source, output = tmp_path / "source", tmp_path / "output"
    source.mkdir()
    output.mkdir()
    make_pilot(source)
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["source_sha256"]["atomic_research/scoring.py"] = "changed"
    write_json(source / "manifest.json", manifest)
    with pytest.raises(ValueError, match="Pilot sources changed"):
        audits.compression_case(small_args(), source, output)


def test_suite_plan_has_all_four_stages_and_no_duplicate_cases(tmp_path):
    for case in ("mean_shift", "metabric", "levine"):
        for seed in (0, 1, 2):
            path = tmp_path / f"{case}_{seed}"
            path.mkdir()
            write_json(path / "manifest.json", {"status": "complete", "config": {
                "mode": "search", "dataset": case, "seed": seed}})
    args = suite.parser().parse_args(["--pilot-root", str(tmp_path)])
    jobs = suite.plan_jobs(args)
    assert len(jobs) == len({job["name"] for job in jobs}) == 33
    assert {stage: sum(j["stage"] == stage for j in jobs) for stage in ("retention", "compression", "geometry", "controls")} == {
        "retention": 9, "compression": 9, "geometry": 9, "controls": 6}
    args.seeds = [3, 3]
    with pytest.raises(ValueError, match="duplicate"):
        suite.plan_jobs(args)


def test_suite_preserves_failure_manifest(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("controlled failure")
    monkeypatch.setattr(suite, "retention_case", fail)
    with pytest.raises(RuntimeError, match="controlled failure"):
        suite.main(["--stage", "retention", "--datasets", "mean_shift", "--seeds", "3", "--output", str(tmp_path)])
    manifests = list(tmp_path.glob("*/manifest.json"))
    assert len(manifests) == 1
    saved = json.loads(manifests[0].read_text())
    assert saved["status"] == "failed" and saved["completed"] == []
    assert saved["current_job"] == "retention_mean_shift_seed3"
    assert any(path.startswith("atomicplus") for path in saved["source_sha256"])


def test_duplicate_dataset_is_rejected_before_running():
    args = suite.parser().parse_args(["--stage", "retention", "--datasets", "mean_shift", "mean_shift"])
    with pytest.raises(ValueError, match="duplicate"):
        suite.plan_jobs(args)
