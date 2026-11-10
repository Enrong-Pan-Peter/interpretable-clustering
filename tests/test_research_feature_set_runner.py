"""The factorial ablation reuses frozen observations and preserves its scorer."""

from copy import deepcopy
import hashlib
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from atomic_research import radial_search_experiment as experiment
from atomic_research.radial_search import ABLATION_METHODS, search_feature_sets
from scripts import run_research_feature_set_ablation as entrypoint
from scripts import run_research_radial_search as runner


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def without_timings(value):
    if isinstance(value, dict):
        return {key: without_timings(item) for key, item in value.items() if not key.endswith("seconds")}
    if isinstance(value, list):
        return [without_timings(item) for item in value]
    return value


@pytest.fixture
def saved_observations(tmp_path):
    source = tmp_path / "source_case"
    source.mkdir()
    job = {
        "name": "saved_case", "case": "shells", "dimension": 2, "p": 6,
        "seed": 1331, "search_seed": 7931, "n_fit": 40, "n_search": 30,
        "n_validation": 30, "n_test": 30, "max_size": 4, "budget": 1,
        "methods": ["random"],
    }
    generated = experiment.generate_synthetic_splits("shells", 2, 6, 70, 30, 30, 1331)
    original = generated.pop("splits")
    splits = {
        "fit": {key: value[:40] for key, value in original["fit"].items()},
        "search": {key: value[40:] for key, value in original["fit"].items()},
        "validation": original["validation"], "test": original["test"],
    }
    arrays = {f"{split}_{key}": value for split, block in splits.items() for key, value in block.items()}
    np.savez_compressed(source / "splits.npz", **arrays)
    (source / "job.json").write_text(json.dumps({"job": job, "generator": generated}), encoding="utf-8")
    reused_job = dict(job, methods=list(ABLATION_METHODS), data_source={
        "directory": str(source), "splits_sha256": digest(source / "splits.npz"),
        "job_sha256": digest(source / "job.json"),
    })
    return source, reused_job, arrays


def test_reused_observations_are_copied_exactly_and_models_reproduce_original_fitting(saved_observations, tmp_path, monkeypatch):
    source, job, arrays = saved_observations
    source_bytes = {name: (source / name).read_bytes() for name in ("job.json", "splits.npz")}
    original = search_feature_sets(
        arrays["fit_X"], arrays["search_X"], method="random", budget=1, max_size=4, seed=7931,
    )
    monkeypatch.setattr(experiment, "generate_synthetic_splits",
                        lambda *args, **kwargs: pytest.fail("Frozen observations must not be regenerated."))
    destination = tmp_path / "reused_case"
    destination.mkdir()
    result = experiment.run_search_case(job, destination)
    assert (destination / "splits.npz").read_bytes() == source_bytes["splits.npz"]
    assert (destination / "source_job.json").read_bytes() == source_bytes["job.json"]
    assert all((source / name).read_bytes() == contents for name, contents in source_bytes.items())
    with np.load(destination / "splits.npz", allow_pickle=False) as copied:
        assert set(copied.files) == set(arrays)
        for name, expected in arrays.items():
            assert_array_equal(copied[name], expected)
    # Budget one shares the same initial feature set across every method.
    # It isolates the unchanged fitting/scoring mechanism from search policy.
    for method in ABLATION_METHODS:
        saved_search = json.loads((destination / f"{method}_search.json").read_text())
        assert without_timings(saved_search["model"]) == without_timings(original["model"])
        # Serialization preserves values exactly but may change array memory
        # order; floating reductions can then differ by a few ulps.
        for key in ("mean", "scale", "covariance", "shrinkage"):
            assert_allclose(saved_search["background"][key], original["background"][key],
                            atol=1e-13, rtol=1e-13)
        for key in ("method", "scope"):
            assert saved_search["background"][key] == original["background"][key]
        assert saved_search["search_gain"] == pytest.approx(original["search_gain"], abs=1e-12, rel=0.)
        assert result["methods"][method]["selected_support"] == original["selected_support"]


@pytest.mark.parametrize("filename", ["splits.npz", "job.json"])
def test_reuse_rejects_source_bytes_changed_since_plan(saved_observations, tmp_path, monkeypatch, filename):
    source, job, _ = saved_observations
    with (source / filename).open("ab") as stream:
        stream.write(b"changed after planning")
    monkeypatch.setattr(experiment, "search_feature_sets", lambda *args, **kwargs: pytest.fail("Unexpected search."))
    destination = tmp_path / "rejected"
    destination.mkdir()
    with pytest.raises(ValueError, match="input changed"):
        experiment.run_search_case(job, destination)


def test_reuse_rejects_configuration_disagreement_before_search(saved_observations, tmp_path, monkeypatch):
    _, job, _ = saved_observations
    changed = dict(job, search_seed=job["search_seed"] + 1)
    monkeypatch.setattr(experiment, "search_feature_sets", lambda *args, **kwargs: pytest.fail("Unexpected search."))
    destination = tmp_path / "rejected"
    destination.mkdir()
    with pytest.raises(ValueError, match="configuration differs: search_seed"):
        experiment.run_search_case(changed, destination)


@pytest.mark.parametrize("field", ["fit_X", "search_X", "test_y"])
def test_reuse_rejects_wrong_saved_shapes_even_with_matching_file_hash(saved_observations, tmp_path, monkeypatch, field):
    source, job, arrays = saved_observations
    malformed = dict(arrays)
    malformed[field] = arrays[field][:-1] if field != "search_X" else arrays[field][:, :-1]
    np.savez_compressed(source / "splits.npz", **malformed)
    job["data_source"]["splits_sha256"] = digest(source / "splits.npz")
    monkeypatch.setattr(experiment, "search_feature_sets", lambda *args, **kwargs: pytest.fail("Unexpected search."))
    destination = tmp_path / "rejected"
    destination.mkdir()
    with pytest.raises(ValueError, match="block shape differs"):
        experiment.run_search_case(job, destination)


@pytest.fixture
def audited_source_run(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    fitter = root / "atomic_research/radial_panels.py"
    fitter.parent.mkdir(parents=True)
    fitter.write_text("unchanged radial model and scoring implementation", encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", root)
    planned = runner.jobs(runner.parser().parse_args(["--suite", "pilot"]))
    source = tmp_path / "audited_source"
    source.mkdir()
    for job in planned:
        directory = source / job["name"]
        directory.mkdir()
        (directory / "job.json").write_text(json.dumps({"job": job, "generator": {}}), encoding="utf-8")
        (directory / "splits.npz").write_bytes(b"frozen development observation fixture")
    manifest = {
        "status": "complete", "jobs": planned, "completed": [job["name"] for job in planned],
        "source_sha256": {"atomic_research/radial_panels.py": digest(fitter)},
    }
    (source / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (source / "audit.json").write_text(json.dumps({"status": "passed", "errors": []}), encoding="utf-8")
    return source, planned


def test_full_ablation_retains_source_conditions_and_smoke_has_four_fixed_cases(audited_source_run):
    source, original = audited_source_run
    full = runner.jobs(runner.parser().parse_args(["--suite", "ablation", "--source-run", str(source)]))
    smoke = runner.jobs(runner.parser().parse_args(["--suite", "ablation-smoke", "--source-run", str(source)]))
    assert len(full) == 36
    for before, after in zip(original, full):
        assert {key: value for key, value in after.items() if key not in {"methods", "data_source"}} == {
            key: value for key, value in before.items() if key != "methods"
        }
        assert after["methods"] == list(ABLATION_METHODS)
        assert after["data_source"]["splits_sha256"] == digest(source / before["name"] / "splits.npz")
        assert after["data_source"]["job_sha256"] == digest(source / before["name"] / "job.json")
    assert len(smoke) == 4
    assert {(job["case"], job["dimension"]) for job in smoke} == {
        ("shells", 4), ("shells", 5), ("shells", 8), ("correlated_gaussian", 5),
    }
    assert all(job["budget"] == 48 and job["seed"] == original[0]["seed"] for job in smoke)


@pytest.mark.parametrize("override", [["--budget", "256"], ["--rows", "600"],
                                       ["--max-size", "8"], ["--search-seeds", "3203"]])
def test_ablation_does_not_accept_scientific_configuration_overrides(audited_source_run, override):
    source, _ = audited_source_run
    args = runner.parser().parse_args(["--suite", "ablation", "--source-run", str(source), *override])
    with pytest.raises(ValueError, match="do not override"):
        runner.jobs(args)


def test_ablation_rejects_changed_model_or_fitness_implementation(audited_source_run):
    source, _ = audited_source_run
    (runner.ROOT / "atomic_research/radial_panels.py").write_text("different model or fitness", encoding="utf-8")
    args = runner.parser().parse_args(["--suite", "ablation", "--source-run", str(source)])
    with pytest.raises(ValueError, match="model/fitness implementation differs"):
        runner.jobs(args)


@pytest.mark.parametrize("problem", ["incomplete", "failed_audit", "job_disagreement"])
def test_ablation_requires_consistent_completed_audited_source(audited_source_run, problem):
    source, original = audited_source_run
    if problem == "incomplete":
        path = source / "manifest.json"
        contents = json.loads(path.read_text())
        contents["completed"].pop()
    elif problem == "failed_audit":
        path = source / "audit.json"
        contents = {"status": "failed", "errors": ["deliberate fixture failure"]}
    else:
        path = source / original[0]["name"] / "job.json"
        contents = json.loads(path.read_text())
        contents["job"]["budget"] += 1
    path.write_text(json.dumps(contents), encoding="utf-8")
    args = runner.parser().parse_args(["--suite", "ablation", "--source-run", str(source)])
    with pytest.raises(ValueError):
        runner.jobs(args)


def test_ablation_entrypoint_defaults_to_full_comparison_but_preserves_resume(monkeypatch):
    calls = []
    monkeypatch.setattr(entrypoint, "run", lambda args: calls.append(args) or 0)
    assert entrypoint.main(["--list-only"]) == 0
    assert entrypoint.main(["--suite=ablation-smoke", "--list-only"]) == 0
    assert entrypoint.main(["--resume", "saved_run"]) == 0
    assert calls == [["--suite", "ablation", "--list-only"],
                     ["--suite=ablation-smoke", "--list-only"], ["--resume", "saved_run"]]
