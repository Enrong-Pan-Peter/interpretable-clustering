"""A frozen replication plan must preserve budgets, inputs and recovery state."""

from collections import Counter
from itertools import product
import json

import pytest

from scripts import run_research_feature_set_replication as runner


EXPECTED_BASELINE_CASES = {
    ("shells", 2), ("shells", 3), ("shells", 4), ("shells", 5), ("shells", 8),
    ("single_shell", 2), ("single_shell", 5), ("independent_gaussian", 5),
    ("correlated_gaussian", 5), ("student_t", 5), ("common_center_scale_mixture", 5),
    ("mean_shift", 3),
}


def test_full_plan_has_the_frozen_factorial_design_and_common_fit_budget():
    planned = runner.jobs()
    assert len(planned) == len({job["name"] for job in planned}) == 126
    assert Counter(job["condition"] for job in planned) == {
        "baseline": 72, "more_nuisance": 18, "weak_separation": 18, "dependent_nuisance": 18,
    }
    seed_pairs = set(product((5101, 5113, 5119), (6101, 6113)))
    by_condition_case = {}
    for job in planned:
        assert job["methods"] == ["moment_best", "kernel_best"]
        assert job["budget"] == 256
        assert job["max_size"] == 10
        assert {job[f"n_{split}"] for split in ("fit", "search", "validation", "test")} == {600}
        assert job["p"] == (72 if job["condition"] == "more_nuisance" else 24)
        assert "data_source" not in job, "The replication must generate fresh data."
        by_condition_case.setdefault((job["condition"], job["case"], job["dimension"]), set()).add(
            (job["seed"], job["search_seed"]))
    assert all(pairs == seed_pairs for pairs in by_condition_case.values())
    assert {(case, dimension) for condition, case, dimension in by_condition_case if condition == "baseline"} == EXPECTED_BASELINE_CASES
    for condition in ("more_nuisance", "weak_separation", "dependent_nuisance"):
        assert {(case, dimension) for candidate, case, dimension in by_condition_case if candidate == condition} == {
            ("shells", 4), ("shells", 5), ("shells", 8),
        }
    # Search random seeds repeat an unchanged dataset: 126 jobs are 63 data
    # blocks with two searches each, not 126 independent data replicates.
    data_blocks = Counter((job["condition"], job["case"], job["dimension"], job["p"], job["seed"])
                          for job in planned)
    assert len(data_blocks) == 63
    assert set(data_blocks.values()) == {2}


def test_smoke_plan_covers_all_conditions_without_using_full_run_seeds():
    smoke = runner.jobs("smoke")
    full = runner.jobs("replication")
    assert len(smoke) == 4
    assert {job["condition"] for job in smoke} == {
        "baseline", "more_nuisance", "weak_separation", "dependent_nuisance",
    }
    for job in smoke:
        assert (job["case"], job["dimension"]) == ("shells", 4)
        assert (job["seed"], job["search_seed"]) == (5903, 6907)
        assert job["budget"] == 16 and job["max_size"] == 10
        assert {job[f"n_{split}"] for split in ("fit", "search", "validation", "test")} == {120}
        assert job["p"] == (72 if job["condition"] == "more_nuisance" else 24)
        assert job["methods"] == ["moment_best", "kernel_best"]
    assert {job["seed"] for job in smoke}.isdisjoint(job["seed"] for job in full)
    assert {job["search_seed"] for job in smoke}.isdisjoint(job["search_seed"] for job in full)


def test_cli_defaults_to_replication_and_accepts_only_operational_controls():
    defaults = runner.parser().parse_args([])
    assert defaults.suite == "replication"
    assert defaults.resume is None
    assert defaults.list_only is False
    assert runner.parser().parse_args(["--suite", "smoke", "--list-only"]).list_only


@pytest.mark.parametrize("override", [["--budget", "32"], ["--rows", "100"],
                                       ["--p", "48"], ["--seeds", "123"],
                                       ["--search-seeds", "456"], ["--max-size", "5"]])
def test_cli_does_not_allow_unplanned_scientific_overrides(override):
    with pytest.raises(SystemExit) as error:
        runner.parser().parse_args(override)
    assert error.value.code == 2


@pytest.fixture
def frozen_repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    record_path = root / "saved_ablation/frozen_candidate.json"
    record_path.parent.mkdir(parents=True)
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "FROZEN_RECORD", record_path)
    for relative in runner.SOURCES:
        source = root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"# source fixture: {relative}\n", encoding="utf-8")
    before = (
        "def describe_panel(value):\n"
        "    return value > 0.5\n\n"
        "def run_search_case(job, directory, progress=None):\n"
        "    generated = generate_synthetic_splits(job)\n"
        "    return {'score': generated, 'flag': describe_panel(0.6)}\n"
    )
    after = before.replace("progress=None):", "progress=None, *, generator=None):").replace(
        "generate_synthetic_splits(job)", "(generator or generate_synthetic_splits)(job)")
    archived = record_path.parent / "source_snapshot" / runner.PIPELINE
    archived.parent.mkdir(parents=True)
    archived.write_text(before, encoding="utf-8")
    (root / runner.PIPELINE).write_text(after, encoding="utf-8")
    record = {
        "candidate_method": "kernel_best", "comparator_method": "moment_best", "budget": 256, "max_size": 10,
        "source_sha256": {relative: runner.digest(root / relative) for relative in runner.CORE_SOURCES},
    }
    record["source_sha256"][runner.PIPELINE] = runner.digest(archived)
    record_path.write_text(json.dumps(record), encoding="utf-8")
    return root, record_path


def test_frozen_guard_allows_only_the_optional_generator_hook(frozen_repo):
    root, record = frozen_repo
    receipt = runner.verify_frozen_core()
    assert receipt["frozen_candidate_sha256"] == runner.digest(record)
    assert receipt["current_pipeline_sha256"] == runner.digest(root / runner.PIPELINE)
    assert receipt["prior_pipeline_sha256"] == runner.digest(record.parent / "source_snapshot" / runner.PIPELINE)
    assert receipt["current_pipeline_sha256"] != receipt["prior_pipeline_sha256"]
    assert "independent_data_replication" not in receipt
    assert "distinct_populations" not in receipt
    assert "full_protocol_statistical_units" in receipt


@pytest.mark.parametrize("relative", runner.CORE_SOURCES)
def test_frozen_guard_rejects_changed_scientific_core(frozen_repo, relative):
    root, _ = frozen_repo
    (root / relative).write_text("changed frozen computation", encoding="utf-8")
    with pytest.raises(ValueError, match="scientific core changed"):
        runner.verify_frozen_core()


@pytest.mark.parametrize("before,after", [("value > 0.5", "value > 0.7"),
                                         ("'score': generated", "'score': 2 * generated"),
                                         ("generator=None", "generator=0")])
def test_frozen_guard_rejects_flag_scoring_or_interface_changes(frozen_repo, before, after):
    root, _ = frozen_repo
    source = root / runner.PIPELINE
    source.write_text(source.read_text().replace(before, after), encoding="utf-8")
    with pytest.raises(ValueError, match="computation changed|experiment interface"):
        runner.verify_frozen_core()


def test_frozen_guard_rejects_tampered_archived_pipeline(frozen_repo):
    _, record = frozen_repo
    archived = record.parent / "source_snapshot" / runner.PIPELINE
    archived.write_text("altered archive", encoding="utf-8")
    with pytest.raises(ValueError, match="archived experiment source"):
        runner.verify_frozen_core()


@pytest.mark.parametrize("binding", ["fit_radial_panel = another_fitter\n",
                                     "from replacement_fitness import fit_radial_panel\n"])
def test_frozen_guard_rejects_rebinding_scientific_dependencies(frozen_repo, binding):
    root, _ = frozen_repo
    source = root / runner.PIPELINE
    source.write_text(binding + source.read_text(), encoding="utf-8")
    with pytest.raises(ValueError, match="binding|import|module"):
        runner.verify_frozen_core()


def _completed_case(directory, job):
    directory.mkdir(parents=True, exist_ok=True)
    methods = {method: {"method": method, "score": 1.25} for method in job["methods"]}
    report = {"job": job, "methods": methods}
    runner.write_json(directory / "job.json", {"job": job})
    runner.write_json(directory / "result.json", report)
    for method in job["methods"]:
        runner.write_json(directory / f"{method}_search.json", {"method": method})
        runner.write_json(directory / f"{method}_result.json", methods[method])
    for filename in ("splits.npz", "predictions.npz"):
        (directory / filename).write_bytes(b"preserve completed numerical artifact bytes")
    return report


def _files(directory):
    return {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}


def _rewrite_manifest(parent, update):
    path = parent / "manifest.json"
    manifest = json.loads(path.read_text())
    update(manifest)
    runner.write_json(path, manifest)


@pytest.fixture
def stopped_run(frozen_repo, tmp_path):
    root, record = frozen_repo
    parent = tmp_path / "stopped"
    parent.mkdir()
    planned = runner.jobs("smoke")
    for relative in runner.SOURCES:
        saved = parent / "source_snapshot" / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes((root / relative).read_bytes())
    (parent / "frozen_candidate.json").write_bytes(record.read_bytes())
    _completed_case(parent / planned[0]["name"], planned[0])
    partial = parent / planned[1]["name"]
    partial.mkdir()
    (partial / "partial_candidate.json").write_text("unfinished work", encoding="utf-8")
    runner.write_json(parent / "manifest.json", {
        "status": "failed", "suite": "smoke", "jobs": planned, "completed": [planned[0]["name"]],
        "current_job": planned[1]["name"], "replication": {
            **runner.verify_frozen_core(), "independent_data_replication": False,
            "engineering_smoke_only": True, "distinct_populations": 4,
        },
        "source_sha256": {relative: runner.digest(root / relative) for relative in runner.SOURCES},
    })
    return parent, planned


def test_resume_preserves_parent_and_completed_results_and_restarts_partial_job(stopped_run, tmp_path, monkeypatch):
    parent, planned = stopped_run
    before = _files(parent)
    calls = []

    def run_case(job, directory, progress=None, *, generator=None):
        calls.append(job["name"])
        assert not list(directory.iterdir()), "An incomplete job must restart in a fresh directory."
        assert generator.func is runner.generate_replication_splits
        assert generator.keywords == {"condition": job["condition"]}
        return _completed_case(directory, job)

    monkeypatch.setattr(runner, "run_search_case", run_case)
    monkeypatch.setattr(runner, "write_search_summary", lambda *args: None)
    output = tmp_path / "continued"
    assert runner.main(["--resume", str(parent), "--output", str(output)]) == 0
    assert calls == [job["name"] for job in planned[1:]]
    assert _files(parent) == before
    run = next(output.iterdir())
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["suite"] == "smoke"
    assert manifest["replication"]["independent_data_replication"] is False
    assert manifest["replication"]["engineering_smoke_only"] is True
    assert manifest["replication"]["distinct_populations"] == 4
    assert manifest["jobs"] == planned
    assert manifest["completed"] == [job["name"] for job in planned]
    assert manifest["current_job"] is None
    completed_name = planned[0]["name"]
    assert _files(run / completed_name) == _files(parent / completed_name)
    receipt = manifest["resume"]
    assert receipt["parent_manifest_sha256"] == runner.digest(parent / "manifest.json")
    assert receipt["parent_manifest_sha256"] == runner.digest(run / "resume_parent_manifest.json")
    for relative, expected in receipt["reused_jobs"][completed_name].items():
        assert runner.digest(run / completed_name / relative) == expected
    for relative, expected in manifest["source_sha256"].items():
        assert runner.digest(run / "source_snapshot" / relative) == expected == runner.digest(runner.ROOT / relative)


def test_resume_rejects_even_an_explicit_same_suite_override(stopped_run):
    parent, _ = stopped_run
    with pytest.raises(SystemExit) as error:
        runner.main(["--resume", str(parent), "--suite", "smoke"])
    assert error.value.code == 2


def test_resume_rejects_a_changed_saved_protocol(stopped_run):
    parent, _ = stopped_run
    _rewrite_manifest(parent, lambda manifest: manifest["jobs"][0].update(budget=17))
    with pytest.raises(ValueError, match="fixed protocol"):
        runner.load_resume(parent)


@pytest.mark.parametrize("location", ["current_generator", "source_snapshot", "frozen_record"])
def test_resume_rejects_changed_sources_or_freeze_record(stopped_run, location):
    parent, _ = stopped_run
    if location == "current_generator":
        target = runner.ROOT / "atomic_research/feature_set_replication_data.py"
    elif location == "source_snapshot":
        target = parent / "source_snapshot" / runner.CORE_SOURCES[0]
    else:
        target = parent / "frozen_candidate.json"
    target.write_text("changed since stopped run", encoding="utf-8")
    with pytest.raises(ValueError, match="source changed|frozen candidate record differs"):
        runner.load_resume(parent)


@pytest.mark.parametrize("problem", ["missing_predictions", "metadata_job", "method_result"])
def test_resume_rejects_incomplete_or_inconsistent_completed_artifacts(stopped_run, problem):
    parent, planned = stopped_run
    complete = parent / planned[0]["name"]
    if problem == "missing_predictions":
        (complete / "predictions.npz").unlink()
    elif problem == "metadata_job":
        metadata = json.loads((complete / "job.json").read_text())
        metadata["job"]["seed"] += 1
        runner.write_json(complete / "job.json", metadata)
    else:
        runner.write_json(complete / "moment_best_result.json", {"score": -1.})
    with pytest.raises(ValueError, match="artifacts missing|configuration differs|method result differs"):
        runner.load_resume(parent)


@pytest.mark.parametrize("exception,status", [(RuntimeError("controlled failure"), "failed"),
                                              (KeyboardInterrupt(), "interrupted")])
def test_failed_resume_keeps_checkpoint_and_original_data(stopped_run, tmp_path, monkeypatch, exception, status):
    parent, planned = stopped_run
    before = _files(parent)

    def fail(job, directory, progress=None, *, generator=None):
        (directory / "partial.txt").write_text("new partial result", encoding="utf-8")
        raise exception

    monkeypatch.setattr(runner, "run_search_case", fail)
    output = tmp_path / "continued"
    with pytest.raises(type(exception)):
        runner.main(["--resume", str(parent), "--output", str(output)])
    run = next(output.iterdir())
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == status
    assert manifest["completed"] == [planned[0]["name"]]
    assert manifest["current_job"] == planned[1]["name"]
    assert (run / planned[1]["name"] / "partial.txt").read_text() == "new partial result"
    assert _files(parent) == before


def test_list_only_never_runs_or_creates_a_replication(frozen_repo, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "run_search_case", lambda *args, **kwargs: pytest.fail("Unexpected experiment execution."))
    output = tmp_path / "not_created"
    assert runner.main(["--list-only", "--output", str(output)]) == 0
    listing = json.loads(capsys.readouterr().out)
    assert listing["suite"] == "replication" and listing["jobs"] == 126
    assert listing["unique_fits"] == 64512
    assert not output.exists()


def test_resuming_complete_run_creates_no_duplicate_output(stopped_run, tmp_path, monkeypatch):
    parent, planned = stopped_run
    for job in planned[1:]:
        _completed_case(parent / job["name"], job)
    _rewrite_manifest(parent, lambda manifest: manifest.update(
        status="complete", completed=[job["name"] for job in planned], current_job=None))
    before = _files(parent)
    monkeypatch.setattr(runner, "run_search_case", lambda *args, **kwargs: pytest.fail("Unexpected rerun."))
    output = tmp_path / "not_created"
    assert runner.main(["--resume", str(parent), "--output", str(output)]) == 0
    assert not output.exists()
    assert _files(parent) == before
