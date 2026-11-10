"""Run one predeclared fresh-seed replication/stress batch of the frozen search."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
from functools import partial
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import shutil
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from threadpoolctl import threadpool_limits
from atomic_research.radial_diagnostics import write_json
from atomic_research.radial_search_experiment import run_search_case, write_search_summary
from atomic_research.feature_set_replication_data import generate_replication_splits
from scripts.run_research_radial_search import digest

FROZEN_RECORD = ROOT / "results/research_feature_set_ablation/20261025T184818_942365Z/frozen_candidate.json"
CORE_SOURCES = ("atomic_research/radial_panels.py", "atomic_research/radial_diagnostics.py",
                "atomic_research/radial_search.py", "atomic_research/feature_dependence.py")
PIPELINE = "atomic_research/radial_search_experiment.py"
SOURCES = (*CORE_SOURCES, PIPELINE, "atomic_research/feature_set_replication_data.py",
           "scripts/run_research_feature_set_replication.py", "scripts/run_research_radial_search.py",
           "scripts/analyze_research_radial_search.py")
METHODS = ["moment_best", "kernel_best"]
DATA_SEEDS = (5101, 5113, 5119)
SEARCH_SEEDS = (6101, 6113)


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=("replication", "smoke"), default="replication")
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_feature_set_replication")
    cli.add_argument("--resume", type=Path)
    cli.add_argument("--list-only", action="store_true")
    return cli


def jobs(suite="replication"):
    if suite not in {"replication", "smoke"}:
        raise ValueError("unknown replication suite")
    baseline = ([("shells", d) for d in (2, 3, 4, 5, 8)]
                + [("single_shell", d) for d in (2, 5)]
                + [(case, 5) for case in ("independent_gaussian", "correlated_gaussian", "student_t", "common_center_scale_mixture")]
                + [("mean_shift", 3)])
    settings = [("baseline", case, d, 24) for case, d in baseline]
    settings += [(condition, "shells", d, 72 if condition == "more_nuisance" else 24)
                 for condition in ("more_nuisance", "weak_separation", "dependent_nuisance") for d in (4, 5, 8)]
    smoke = suite == "smoke"
    if smoke:
        settings = [(condition, "shells", 4, 72 if condition == "more_nuisance" else 24)
                    for condition in ("baseline", "more_nuisance", "weak_separation", "dependent_nuisance")]
    data_seeds, search_seeds = ((5903,), (6907,)) if smoke else (DATA_SEEDS, SEARCH_SEEDS)
    rows, budget = (120, 16) if smoke else (600, 256)
    return [{"name": f"{condition}_{case}_d{d}_p{p}_seed{seed}_search{search}",
             "experiment": "feature_set_replication", "condition": condition,
             "case": case, "dimension": d, "p": p, "seed": seed, "search_seed": search,
             "n_fit": rows, "n_search": rows, "n_validation": rows, "n_test": rows,
             "budget": budget, "max_size": 10, "methods": list(METHODS)}
            for condition, case, d, p in settings for seed in data_seeds for search in search_seeds]


def _scientific_function_tree(source, name):
    """Ignore only the explicit optional data-generator hook, not scientific logic."""
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    if name == "run_search_case":
        if node.args.kwonlyargs:
            if ([a.arg for a in node.args.kwonlyargs] != ["generator"]
                    or len(node.args.kw_defaults) != 1
                    or not isinstance(node.args.kw_defaults[0], ast.Constant)
                    or node.args.kw_defaults[0].value is not None):
                raise ValueError("unexpected change to experiment interface")
            node.args.kwonlyargs = []
            node.args.kw_defaults = []

        class NormalizeGenerator(ast.NodeTransformer):
            def visit_Call(self, call):
                self.generic_visit(call)
                if (isinstance(call.func, ast.BoolOp) and isinstance(call.func.op, ast.Or)
                        and [ast.dump(value) for value in call.func.values] ==
                        [ast.dump(ast.Name(id="generator", ctx=ast.Load())),
                         ast.dump(ast.Name(id="generate_synthetic_splits", ctx=ast.Load()))]):
                    call.func = ast.Name(id="generate_synthetic_splits", ctx=ast.Load())
                return call

        node = NormalizeGenerator().visit(node)
    return ast.dump(node, include_attributes=False)


def verify_frozen_core():
    record = json.loads(FROZEN_RECORD.read_text(encoding="utf-8"))
    if (record["candidate_method"] != "kernel_best" or record["comparator_method"] != "moment_best"
            or record["budget"] != 256 or record["max_size"] != 10):
        raise ValueError("frozen candidate configuration differs")
    for relative in CORE_SOURCES:
        if digest(ROOT / relative) != record["source_sha256"][relative]:
            raise ValueError(f"frozen scientific core changed: {relative}")
    archived = FROZEN_RECORD.parent / "source_snapshot" / PIPELINE
    if digest(archived) != record["source_sha256"][PIPELINE]:
        raise ValueError("archived experiment source differs from frozen record")
    before, after = archived.read_text(encoding="utf-8"), (ROOT / PIPELINE).read_text(encoding="utf-8")
    for name in ("describe_panel", "run_search_case"):
        if _scientific_function_tree(before, name) != _scientific_function_tree(after, name):
            raise ValueError(f"frozen experiment computation changed: {name}")
    def module_bindings(source):
        # The report writer is presentation-only. All other module-level
        # imports/bindings and additional code must retain their frozen AST.
        return [ast.dump(node, include_attributes=False) for node in ast.parse(source).body
                if not (isinstance(node, ast.FunctionDef)
                        and node.name in {"describe_panel", "run_search_case", "write_search_summary"})]
    if module_bindings(before) != module_bindings(after):
        raise ValueError("frozen experiment module bindings changed")
    return {"frozen_candidate_sha256": digest(FROZEN_RECORD),
            "core_sha256": {name: record["source_sha256"][name] for name in CORE_SOURCES},
            "prior_pipeline_sha256": record["source_sha256"][PIPELINE],
            "current_pipeline_sha256": digest(ROOT / PIPELINE),
            "pipeline_equivalence": "AST identity of fitting/reporting and split flags after removing optional data-generator hook",
            "independent_data_replication": True,
            "statistical_units": "63 populations, each searched with 2 search seeds; 126 jobs are not 126 independent datasets"}


def load_resume(directory):
    directory = directory.resolve()
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] not in {"failed", "interrupted", "complete"}:
        raise ValueError("resume requires a stopped run")
    if manifest["jobs"] != jobs(manifest["suite"]):
        raise ValueError("resume configuration differs from the fixed protocol")
    if set(manifest["source_sha256"]) != set(SOURCES):
        raise ValueError("resume source set differs")
    for source, expected in manifest["source_sha256"].items():
        if digest(ROOT / source) != expected or digest(directory / "source_snapshot" / source) != expected:
            raise ValueError(f"resume source changed: {source}")
    receipt = manifest["replication"]
    if digest(directory / "frozen_candidate.json") != receipt["frozen_candidate_sha256"]:
        raise ValueError("resume frozen candidate record differs")
    names, completed = [job["name"] for job in manifest["jobs"]], manifest["completed"]
    if (len(set(names)) != len(names) or any(not re.fullmatch(r"[A-Za-z0-9_]+", n) for n in names)
            or len(set(completed)) != len(completed) or not set(completed) <= set(names)):
        raise ValueError("invalid completion record")
    reports = {}
    for job in manifest["jobs"]:
        name = job["name"]
        if name not in completed:
            continue
        d = directory / name
        required = ["job.json", "result.json", "splits.npz", "predictions.npz"]
        required += [f"{method}_{suffix}.json" for method in job["methods"] for suffix in ("search", "result")]
        if any(not (d / path).is_file() for path in required):
            raise ValueError(f"completed artifacts missing: {name}")
        report = json.loads((d / "result.json").read_text(encoding="utf-8"))
        metadata = json.loads((d / "job.json").read_text(encoding="utf-8"))
        if report["job"] != job or metadata["job"] != job or set(report["methods"]) != set(job["methods"]):
            raise ValueError(f"completed configuration differs: {name}")
        for method in job["methods"]:
            saved = json.loads((d / f"{method}_result.json").read_text(encoding="utf-8"))
            if saved != report["methods"][method]:
                raise ValueError(f"completed method result differs: {name}/{method}")
        reports[name] = report
    return directory, manifest, reports


def main(argv=None):
    args = parser().parse_args(argv)
    resume = None
    try:
        frozen = verify_frozen_core()
        if args.resume:
            flags = {value.split("=")[0] for value in (sys.argv[1:] if argv is None else argv) if value.startswith("--")}
            if flags - {"--resume", "--output", "--list-only"}:
                raise ValueError("resume uses saved configuration; only --output and --list-only may accompany it")
            resume = load_resume(args.resume)
            suite, planned = resume[1]["suite"], resume[1]["jobs"]
            if resume[1]["replication"] != frozen:
                raise ValueError("frozen replication receipt changed")
        else:
            suite, planned = args.suite, jobs(args.suite)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        parser().error(str(exc))
    if args.list_only:
        print(json.dumps({"suite": suite, "jobs": len(planned), "arms": len(METHODS),
                          "unique_fits": sum(j["budget"] * len(j["methods"]) for j in planned),
                          "planned": planned}, indent=2))
        return 0
    if resume and len(resume[2]) == len(planned):
        print(f"Already complete: {resume[0]}", flush=True)
        return 0
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    for source in SOURCES:
        target = output / "source_snapshot" / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
    shutil.copyfile(FROZEN_RECORD, output / "frozen_candidate.json")
    manifest = {"status": "running", "suite": suite, "created_utc": datetime.now(timezone.utc).isoformat(),
                "jobs": planned, "completed": [], "current_job": None, "replication": frozen,
                "source_sha256": {s: digest(ROOT / s) for s in SOURCES},
                "runtime": {"python": platform.python_version(), "threads": 1,
                            **{p: version(p) for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
                "scope": "frozen two-arm replication and predeclared stress conditions; smoke is engineering verification only",
                "selection": "fit models on fit rows, select on search rows; validation and test never select or refit",
                "oracle_role": "post-search diagnostic only, no oracle support or labels supplied to search",
                "fit_budget": "same unique radial2 fits per arm; post-selection radial1/oracle fits separate"}
    reports = []
    if resume:
        parent, _, complete = resume
        receipt = {"parent_run": str(parent), "parent_manifest_sha256": digest(parent / "manifest.json"), "reused_jobs": {}}
        shutil.copyfile(parent / "manifest.json", output / "resume_parent_manifest.json")
        for job in planned:
            name = job["name"]
            if name not in complete:
                continue
            shutil.copytree(parent / name, output / name)
            receipt["reused_jobs"][name] = {str(f.relative_to(output / name)): digest(f)
                                           for f in (output / name).rglob("*") if f.is_file()}
            if any(digest(parent / name / f) != sha for f, sha in receipt["reused_jobs"][name].items()):
                raise ValueError(f"copied job changed during resume: {name}")
            reports.append(complete[name])
            manifest["completed"].append(name)
        manifest["resume"] = receipt
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} jobs, 2 arms, {planned[0]['budget']} unique feature-set fits per arm. Results: {output}", flush=True)
    started = perf_counter()
    try:
        with threadpool_limits(limits=1):
            for index, job in enumerate(planned, 1):
                if job["name"] in manifest["completed"]:
                    continue
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                print(f"[{index}/{len(planned)}] {job['name']}", flush=True)
                directory = output / job["name"]
                directory.mkdir()
                report = run_search_case(job, directory, progress=lambda msg: print(f"  {msg}", flush=True),
                                         generator=partial(generate_replication_splits, condition=job["condition"]))
                reports.append(report)
                manifest["completed"].append(job["name"])
                write_search_summary(output, reports)
                write_json(output / "manifest.json", manifest)
        manifest.update(status="complete", current_job=None, seconds=perf_counter() - started)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
                        error=f"{type(exc).__name__}: {exc}", seconds=perf_counter() - started)
        raise
    finally:
        write_json(output / "manifest.json", manifest)
    print(f"Complete in {manifest['seconds'] / 60:.2f} minutes. {output / 'summary.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
