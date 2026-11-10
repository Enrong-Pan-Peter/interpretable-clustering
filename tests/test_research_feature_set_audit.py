"""Independent verification of the bounded feature-set search ablation."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from atomic_research.radial_search import ABLATION_METHODS, search_feature_sets
from atomic_research.radial_search_experiment import run_search_case, write_search_summary

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("feature_set_independent_auditor",
                                             ROOT / "scripts/analyze_research_radial_search.py")
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def original(tmp_path_factory):
    run = tmp_path_factory.mktemp("feature-set-audit-original")
    job = {"name": "shells_d3_p6_seed187", "case": "shells", "dimension": 3, "p": 6,
           "seed": 187, "search_seed": 331, "n_fit": 48, "n_search": 45,
           "n_validation": 42, "n_test": 43, "max_size": 4, "budget": 18,
           "methods": list(ABLATION_METHODS)}
    directory = run / job["name"]
    directory.mkdir()
    with threadpool_limits(limits=1):
        report = run_search_case(job, directory)
    write_search_summary(run, [report])
    snapshot = run / "source_snapshot" / "fixture_source.py"
    snapshot.parent.mkdir()
    snapshot.write_text("# independent fixture provenance\n", encoding="utf-8")
    write(run / "manifest.json", {"status": "complete", "jobs": [job], "completed": [job["name"]],
                                 "source_sha256": {"fixture_source.py": digest(snapshot)}})
    return run


@pytest.fixture
def copied(original, tmp_path):
    target = tmp_path / "run"
    shutil.copytree(original, target)
    return target


def directory(run):
    return run / read(run / "manifest.json")["jobs"][0]["name"]


def audit(run):
    with threadpool_limits(limits=1):
        return auditor.audit(run)


def test_clean_four_arm_ablation_passes_independent_audit(original):
    result = audit(original)
    assert result["status"] == "passed", result["errors"]
    assert result["feature_sets"] == 72
    assert result["methods"] == 4


def test_auditor_detects_changed_kernel_matrix(copied):
    path = directory(copied) / "kernel_best_search.json"
    saved = read(path)
    saved["dependence_matrix"][0][1] += .1
    saved["dependence_matrix"][1][0] += .1
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("independent fit-only kernel dependence" in error for error in result["errors"])


def test_auditor_recomputes_bandwidth_instead_of_trusting_metadata(copied):
    path = directory(copied) / "kernel_first_search.json"
    saved = read(path)
    saved["dependence_metadata"]["bandwidths"][0] *= 2
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("fit-only bandwidth 0" in error for error in result["errors"])


def test_auditor_detects_incorrect_first_improvement_record(copied):
    path = directory(copied) / "moment_first_search.json"
    saved = read(path)
    assert saved["local_steps"]
    saved["local_steps"][0]["improved"] = not saved["local_steps"][0]["improved"]
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("strict ranked improvement" in error for error in result["errors"])


def test_auditor_detects_wrong_refinement_configuration(copied):
    path = directory(copied) / "kernel_first_search.json"
    saved = read(path)
    saved["config"]["refinement"] = "best"
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("factorial arm configuration" in error for error in result["errors"])


def test_auditor_detects_missing_local_event(copied):
    path = directory(copied) / "kernel_first_search.json"
    saved = read(path)
    assert saved["local_steps"]
    saved["local_steps"].pop(0)
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("local refinement" in error for error in result["errors"])


def test_auditor_checks_reused_raw_observation_hash(copied):
    jobdir = directory(copied)
    metadata = read(jobdir / "job.json")
    write(jobdir / "source_job.json", metadata)
    source_audit = audit(copied)
    assert source_audit["status"] == "passed"
    manifest = read(copied / "manifest.json")
    write(copied / "development_source_manifest.json", manifest)
    write(copied / "development_source_audit.json", source_audit)
    source = {"directory": str(copied / "unavailable-parent"),
              "splits_sha256": digest(jobdir / "splits.npz"),
              "job_sha256": digest(jobdir / "source_job.json"),
              "manifest_sha256": digest(copied / "development_source_manifest.json"),
              "audit_sha256": digest(copied / "development_source_audit.json")}
    job = metadata["job"]
    job["data_source"] = source
    write(jobdir / "job.json", metadata)
    manifest["jobs"][0] = job
    manifest["development_data"] = {"source_run": str(copied / "unavailable-parent"),
                                    "manifest_sha256": source["manifest_sha256"],
                                    "audit_sha256": source["audit_sha256"], "independent_replication": False}
    write(copied / "manifest.json", manifest)
    result = read(jobdir / "result.json")
    result["job"] = job
    write(jobdir / "result.json", result)
    assert audit(copied)["status"] == "passed"
    # Trailing bytes leave the NPZ arrays readable but change input identity.
    with (jobdir / "splits.npz").open("ab") as stream:
        stream.write(b"modified")
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("unchanged reused raw observations" in error for error in result["errors"])


def test_independent_kernel_replay_handles_constant_squared_features():
    rng = np.random.default_rng(92)
    X = np.column_stack((np.tile([-1., 1.], 30), rng.normal(size=60), rng.normal(size=60)))
    dependence, bandwidths, degenerate = auditor.independent_kernel_dependence(X)
    assert bandwidths[0] is None
    assert degenerate == [0]
    np.testing.assert_array_equal(dependence[0], np.zeros(3))
    np.testing.assert_array_equal(dependence[:, 0], np.zeros(3))


@pytest.mark.parametrize("method", ABLATION_METHODS)
def test_local_event_audit_including_cached_moves_and_restarts(method):
    rng = np.random.default_rng(830)
    X = rng.normal(size=(40, 6))
    # Ties ensure smallest-feature-set ordering and exhausted neighborhoods
    # are audited, including cached moves and random restarts.
    result = search_feature_sets(X, X, method=method, budget=45, max_size=4, seed=71,
                                 evaluate=lambda features: 1.)
    errors = []
    auditor.audit_local_steps(result, 6, lambda condition, message: errors.append(message) if not condition else None)
    assert errors == []
    assert any(step["cache_hit"] for step in result["local_steps"])


def test_first_improvement_audit_rejects_continuing_old_neighborhood():
    rng = np.random.default_rng(831)
    X = rng.normal(size=(40, 10))
    result = search_feature_sets(X, X, method="moment_first", budget=60, max_size=5, seed=73,
                                 evaluate=lambda features: float(sum(j + 1 for j in features)))
    event = next(i for i, step in enumerate(result["local_steps"][:-1]) if step["improved"])
    corrupted = copy.deepcopy(result)
    corrupted["local_steps"][event + 1]["parent_support"] = corrupted["local_steps"][event]["parent_support"]
    errors = []
    auditor.audit_local_steps(corrupted, 10, lambda condition, message: errors.append(message) if not condition else None)
    assert any("first-improvement exits immediately" in error for error in errors)


@pytest.mark.parametrize("seed", [11, 71, 331])
def test_moment_best_matches_archived_incumbent_trajectory(seed):
    path = (ROOT / "results/research_radial_search/20261020T174212_534139Z/source_snapshot"
            / "atomic_research/radial_search.py")
    if not path.is_file():
        pytest.skip("archived pilot source is not present in this checkout")
    manifest = read(path.parents[2] / "manifest.json")
    assert digest(path) == manifest["source_sha256"]["atomic_research/radial_search.py"]
    archive_spec = importlib.util.spec_from_file_location("atomic_research._audit_archived_feature_search", path)
    archive = importlib.util.module_from_spec(archive_spec)
    archive_spec.loader.exec_module(archive)
    rng = np.random.default_rng(182)
    X = rng.normal(size=(48, 12))
    objective = lambda features: float(sum((j + 1) ** 2 for j in features) - 17 * len(features))
    options = {"budget": 80, "max_size": 6, "seed": seed, "evaluate": objective}
    previous = archive.search_panels(X, X, method="dependence_local", **options)
    current = search_feature_sets(X, X, method="moment_best", **options)
    keys = ("support", "size", "index", "score", "best_score", "proposal", "optimizer_success", "model")
    assert [{k: row[k] for k in keys} for row in previous["trace"]] == [
        {k: row[k] for k in keys} for row in current["trace"]]
    for key in ("selected_support", "selected_index", "search_gain", "duplicate_requests", "evaluations",
                "dependence_matrix", "dependence_feature_permutation", "evaluated_size_counts"):
        assert previous[key] == current[key]
