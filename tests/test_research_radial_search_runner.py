"""Runner recovery preserves results, scientific configuration and source state."""

import json

import pytest

from scripts import run_research_radial_search as runner


@pytest.fixture
def stopped_search_run(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    monkeypatch.setattr(runner, "ROOT", root)
    parent = tmp_path / "stopped"
    parent.mkdir()
    hashes = {}
    for relative in runner.SOURCES:
        source = root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(relative, encoding="utf-8")
        snapshot = parent / "source_snapshot" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source.read_bytes())
        hashes[relative] = runner.digest(source)
    defaults = {
        "case": "shells", "dimension": 2, "p": 12, "seed": 2137, "search_seed": 31,
        "n_fit": 40, "n_search": 40, "n_validation": 40, "n_test": 40,
        "max_size": 4, "budget": 4, "methods": list(runner.METHODS),
    }
    planned = [dict(defaults, name="done"), dict(defaults, name="unfinished", seed=2138)]
    completed = parent / "done"
    completed.mkdir()
    report = {"job": planned[0], "marker": "preserve exact completed result bytes",
              "methods": {method: {} for method in runner.METHODS}}
    (completed / "result.json").write_text(json.dumps(report), encoding="utf-8")
    (completed / "job.json").write_text(json.dumps({"job": planned[0]}), encoding="utf-8")
    for name in ("splits.npz", "predictions.npz"):
        (completed / name).write_bytes(b"previous artifact bytes")
    for method in runner.METHODS:
        for suffix in ("search", "result"):
            (completed / f"{method}_{suffix}.json").write_text("{}", encoding="utf-8")
    manifest = {
        "status": "failed", "jobs": planned, "completed": ["done"],
        "source_sha256": hashes, "current_job": "unfinished",
    }
    (parent / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return parent, planned


def rewrite_manifest(parent, update):
    path = parent / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    update(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")


def saved_files(directory):
    return {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def test_resume_copies_completed_job_and_runs_only_missing_job(stopped_search_run, tmp_path, monkeypatch):
    parent, planned = stopped_search_run
    before = saved_files(parent)
    calls, summaries = [], []

    def run_case(job, directory, progress=None):
        calls.append(job)
        report = {"job": job}
        runner.write_json(directory / "result.json", report)
        return report

    monkeypatch.setattr(runner, "run_search_case", run_case)
    monkeypatch.setattr(runner, "write_search_summary", lambda directory, reports: summaries.append(list(reports)))
    output = tmp_path / "continued"
    assert runner.main(["--resume", str(parent), "--output", str(output)]) == 0
    assert calls == [planned[1]]
    assert saved_files(parent) == before
    runs = list(output.iterdir())
    assert len(runs) == 1
    run = runs[0]
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["jobs"] == planned
    assert manifest["status"] == "complete"
    assert manifest["completed"] == ["done", "unfinished"]
    assert manifest["current_job"] is None
    assert [report["job"]["name"] for report in summaries[-1]] == ["done", "unfinished"]
    receipt = manifest["resume"]
    assert receipt["parent_manifest_sha256"] == runner.digest(parent / "manifest.json")
    assert receipt["parent_manifest_sha256"] == runner.digest(run / "resume_parent_manifest.json")
    assert saved_files(parent / "done") == saved_files(run / "done")
    for relative, expected in receipt["reused_jobs"]["done"].items():
        assert runner.digest(run / "done" / relative) == expected == runner.digest(parent / "done" / relative)
    for relative, expected in manifest["source_sha256"].items():
        assert runner.digest(run / "source_snapshot" / relative) == expected


@pytest.mark.parametrize("override", [
    ["--suite", "pilot"], ["--budget", "7"], ["--max-size", "6"], ["--p", "24"],
    ["--rows", "80"], ["--seeds", "47"], ["--search-seeds", "79"],
])
def test_resume_rejects_experiment_configuration_overrides(stopped_search_run, override):
    parent, _ = stopped_search_run
    with pytest.raises(SystemExit) as error:
        runner.main(["--resume", str(parent), *override])
    assert error.value.code == 2


@pytest.mark.parametrize("relative", runner.SOURCES)
def test_resume_rejects_changed_live_scientific_sources(stopped_search_run, relative):
    parent, _ = stopped_search_run
    (runner.ROOT / relative).write_text("changed scientific source", encoding="utf-8")
    with pytest.raises(ValueError, match="source changed"):
        runner.load_resume(parent)


def test_resume_rejects_changed_saved_source(stopped_search_run):
    parent, _ = stopped_search_run
    (parent / "source_snapshot" / runner.SOURCES[0]).write_text("tampered source", encoding="utf-8")
    with pytest.raises(ValueError, match="source changed"):
        runner.load_resume(parent)


def test_resume_rejects_missing_source_in_manifest(stopped_search_run):
    parent, _ = stopped_search_run
    rewrite_manifest(parent, lambda manifest: manifest["source_sha256"].pop(runner.SOURCES[0]))
    with pytest.raises(ValueError, match="source set"):
        runner.load_resume(parent)


def test_resume_rejects_changed_completed_configuration(stopped_search_run):
    parent, _ = stopped_search_run
    path = parent / "done/result.json"
    result = json.loads(path.read_text())
    result["job"]["budget"] += 1
    path.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="configuration differs"):
        runner.load_resume(parent)


@pytest.mark.parametrize("artifact", ["job.json", "splits.npz", "predictions.npz"] + [
    f"{method}_{kind}.json" for method in runner.METHODS for kind in ("search", "result")
])
def test_resume_rejects_incomplete_completed_job_artifacts(stopped_search_run, artifact):
    parent, _ = stopped_search_run
    (parent / "done" / artifact).unlink()
    with pytest.raises(ValueError, match="artifacts missing"):
        runner.load_resume(parent)


def test_resume_rejects_mismatched_copies_of_method_result(stopped_search_run):
    parent, _ = stopped_search_run
    path = parent / "done" / f"{runner.METHODS[0]}_result.json"
    path.write_text(json.dumps({"selected_support": [0, 2]}), encoding="utf-8")
    with pytest.raises(ValueError, match="method result differs"):
        runner.load_resume(parent)


def test_resume_rejects_incomplete_arm_set(stopped_search_run):
    parent, _ = stopped_search_run
    path = parent / "done/result.json"
    result = json.loads(path.read_text())
    result["methods"].pop(runner.METHODS[0])
    path.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="search arms differ"):
        runner.load_resume(parent)


def test_resume_rejects_bytes_changed_during_copy(stopped_search_run, tmp_path, monkeypatch):
    parent, _ = stopped_search_run
    before = saved_files(parent)
    original_copytree = runner.shutil.copytree

    def corrupted_copy(source, destination, *args, **kwargs):
        copied = original_copytree(source, destination, *args, **kwargs)
        (destination / "predictions.npz").write_bytes(b"different copied bytes")
        return copied

    monkeypatch.setattr(runner.shutil, "copytree", corrupted_copy)
    with pytest.raises(ValueError, match="changed during resume"):
        runner.main(["--resume", str(parent), "--output", str(tmp_path / "continued")])
    assert saved_files(parent) == before


@pytest.mark.parametrize("problem", ["duplicate_name", "path_name", "duplicate_completion", "unknown_completion", "running"])
def test_resume_rejects_invalid_manifest_state(stopped_search_run, problem):
    parent, _ = stopped_search_run

    def update(manifest):
        if problem == "duplicate_name":
            manifest["jobs"][1]["name"] = "done"
        elif problem == "path_name":
            manifest["jobs"][1]["name"] = "../outside"
        elif problem == "duplicate_completion":
            manifest["completed"].append("done")
        elif problem == "unknown_completion":
            manifest["completed"].append("missing_job")
        else:
            manifest["status"] = "running"

    rewrite_manifest(parent, update)
    with pytest.raises(ValueError):
        runner.load_resume(parent)


def test_resume_list_only_does_not_create_output(stopped_search_run, tmp_path, capsys):
    parent, planned = stopped_search_run
    output = tmp_path / "not_created"
    assert runner.main(["--resume", str(parent), "--output", str(output), "--list-only"]) == 0
    assert not output.exists()
    listing = json.loads(capsys.readouterr().out)
    assert listing["planned"] == planned
    assert listing["fits_per_arm"] == planned[0]["budget"]


def test_already_complete_resume_is_a_noop(stopped_search_run, tmp_path, monkeypatch):
    parent, _ = stopped_search_run
    rewrite_manifest(parent, lambda manifest: manifest.update(status="complete", jobs=manifest["jobs"][:1]))
    before = saved_files(parent)
    monkeypatch.setattr(runner, "run_search_case", lambda *args, **kwargs: pytest.fail("unexpected rerun"))
    output = tmp_path / "not_created"
    assert runner.main(["--resume", str(parent), "--output", str(output)]) == 0
    assert not output.exists()
    assert saved_files(parent) == before


@pytest.mark.parametrize("exception,status", [(RuntimeError("deliberate failure"), "failed"),
                                              (KeyboardInterrupt(), "interrupted")])
def test_failed_continuation_preserves_checkpoint_and_parent(stopped_search_run, tmp_path, monkeypatch, exception, status):
    parent, planned = stopped_search_run
    before = saved_files(parent)

    def fail(job, directory, progress=None):
        (directory / "partial.txt").write_text("partial candidate output", encoding="utf-8")
        raise exception

    monkeypatch.setattr(runner, "run_search_case", fail)
    output = tmp_path / "continued"
    with pytest.raises(type(exception)):
        runner.main(["--resume", str(parent), "--output", str(output)])
    run = next(output.iterdir())
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == status
    assert manifest["completed"] == ["done"]
    assert manifest["current_job"] == "unfinished"
    assert manifest["jobs"] == planned
    assert (run / "unfinished/partial.txt").read_text() == "partial candidate output"
    assert saved_files(parent) == before


@pytest.mark.parametrize("arguments", [
    ["--seeds", "1", "2", "--search-seeds", "3"],
    ["--seeds", "1", "1", "--search-seeds", "3", "4"],
    ["--seeds", "-1", "--search-seeds", "3"],
    ["--rows", "39"], ["--p", "11"], ["--max-size", "0"],
    ["--p", "12", "--max-size", "13"], ["--budget", "0"],
    ["--p", "12", "--max-size", "1", "--budget", "13"],
])
def test_new_plan_rejects_invalid_budgets_sizes_and_seed_pairing(arguments):
    with pytest.raises(ValueError):
        runner.jobs(runner.parser().parse_args(arguments))


def test_frozen_pilot_pairs_data_and_search_seeds_and_includes_all_arms():
    planned = runner.jobs(runner.parser().parse_args(["--suite", "pilot"]))
    assert len(planned) == 36
    assert len({job["name"] for job in planned}) == len(planned)
    assert {(job["seed"], job["search_seed"]) for job in planned} == {
        (2401, 3203), (2411, 3217), (2423, 3221),
    }
    assert all(job["budget"] == 256 and job["max_size"] == 10 for job in planned)
    assert all(job["methods"] == list(runner.METHODS) for job in planned)
    assert "shuffled_dependence_local" in runner.METHODS
