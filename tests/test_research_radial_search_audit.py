"""Saved-state audit must detect numerical, selection and artifact corruption."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from atomic_research.radial_search_experiment import run_search_case, write_search_summary

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("radial_search_auditor", ROOT / "scripts/analyze_research_radial_search.py")
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
    run = tmp_path_factory.mktemp("audit-original")
    job = {"name": "shells_d2_p6_seed171", "case": "shells", "dimension": 2, "p": 6,
           "seed": 171, "search_seed": 311, "n_fit": 40, "n_search": 40,
           "n_validation": 40, "n_test": 40, "max_size": 3, "budget": 7,
           "methods": ["random", "dependence_local", "shuffled_dependence_local"]}
    directory = run / job["name"]
    directory.mkdir()
    with threadpool_limits(limits=1):
        result = run_search_case(job, directory)
    write_search_summary(run, [result])
    snapshot = run / "source_snapshot" / "fixture_source.py"
    snapshot.parent.mkdir()
    snapshot.write_text("# isolated test provenance\n", encoding="utf-8")
    write(run / "manifest.json", {"status": "complete", "jobs": [job], "completed": [job["name"]],
                                 "source_sha256": {"fixture_source.py": digest(snapshot)}})
    return run


@pytest.fixture
def copied(original, tmp_path):
    target = tmp_path / "run"
    shutil.copytree(original, target)
    return target


def audit(path):
    with threadpool_limits(limits=1):
        return auditor.audit(path)


def job_directory(run):
    return run / read(run / "manifest.json")["jobs"][0]["name"]


def test_untouched_numerical_and_provenance_replay_passes(original):
    result = audit(original)
    assert result["status"] == "passed", result["errors"]
    assert result["errors"] == []
    assert result["jobs"] == 1
    assert result["methods"] == 3
    assert result["panels"] == 21
    assert result["checks"] > 100


def test_auditor_detects_modified_trace_score(copied):
    path = job_directory(copied) / "random_search.json"
    saved = read(path)
    saved["trace"][0]["score"] += 5.
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("independent search gain" in error for error in result["errors"])


def test_auditor_detects_modified_native_prediction(copied):
    path = job_directory(copied) / "predictions.npz"
    with np.load(path, allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    arrays["random__test"][0] = 1 - arrays["random__test"][0]
    np.savez_compressed(path, **arrays)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("random/test: native rule replay" in error for error in result["errors"])


def test_auditor_detects_modified_summary(copied):
    path = copied / "summary.json"
    saved = read(path)
    saved["rows"][0]["test_gain"] += 1.
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("summary test/gain" in error for error in result["errors"])


def test_auditor_detects_inconsistent_method_report(copied):
    path = job_directory(copied) / "random_result.json"
    saved = read(path)
    saved["selected_index"] += 1
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("report copies" in error for error in result["errors"])


def test_auditor_detects_changed_source_snapshot(copied):
    (copied / "source_snapshot" / "fixture_source.py").write_text("# changed\n", encoding="utf-8")
    result = audit(copied)
    assert result["status"] == "failed"
    assert "source snapshot: fixture_source.py" in result["errors"]


def test_auditor_checks_resumed_artifact_receipt(copied):
    manifest_path = copied / "manifest.json"
    manifest = read(manifest_path)
    write(copied / "resume_parent_manifest.json", manifest)
    directory = job_directory(copied)
    receipt = {"parent_manifest_sha256": digest(copied / "resume_parent_manifest.json"),
               "reused_jobs": {directory.name: {str(path.relative_to(directory)): digest(path)
                                                for path in directory.rglob("*") if path.is_file()}}}
    manifest["resume"] = receipt
    write(manifest_path, manifest)
    assert audit(copied)["status"] == "passed"
    # Whitespace preserves the JSON's numerical meaning but invalidates identity.
    with (directory / "result.json").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    result = audit(copied)
    assert result["status"] == "failed"
    assert any("resume artifact:" in error and "result.json" in error for error in result["errors"])


def test_auditor_rejects_incomplete_manifest(copied):
    path = copied / "manifest.json"
    saved = read(path)
    saved["status"] = "running"
    write(path, saved)
    result = audit(copied)
    assert result["status"] == "failed"
    assert "manifest complete" in result["errors"]
