"""Run the budgeted hidden-support experiment; preserve every run and source."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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
from atomic_research.radial_search import METHODS
from atomic_research.radial_search_experiment import run_search_case, write_search_summary

SOURCES = ("atomic_research/radial_panels.py", "atomic_research/radial_diagnostics.py",
           "atomic_research/radial_search.py", "atomic_research/radial_search_experiment.py",
           "scripts/run_research_radial_search.py")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=("smoke", "pilot"), default="smoke")
    cli.add_argument("--budget", type=int)
    cli.add_argument("--max-size", type=int, default=10)
    cli.add_argument("--p", type=int)
    cli.add_argument("--rows", type=int, help="rows in EACH of fit, search, validation, test")
    cli.add_argument("--seeds", nargs="+", type=int)
    cli.add_argument("--search-seeds", nargs="+", type=int)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_radial_search")
    cli.add_argument("--resume", type=Path)
    cli.add_argument("--list-only", action="store_true")
    return cli


def jobs(args):
    smoke = args.suite == "smoke"
    seeds = args.seeds if args.seeds is not None else ([2309] if smoke else [2401, 2411, 2423])
    search_seeds = args.search_seeds if args.search_seeds is not None else ([3101] if smoke else [3203, 3217, 3221])
    if len(seeds) != len(search_seeds) or not seeds or len(set(seeds)) != len(seeds) or min(seeds + search_seeds) < 0:
        raise ValueError("supply paired nonnegative data/search seeds, with distinct data seeds")
    p = args.p if args.p is not None else (14 if smoke else 24)
    rows = args.rows if args.rows is not None else (160 if smoke else 600)
    budget = args.budget if args.budget is not None else (48 if smoke else 256)
    if rows < 40 or p < 12 or not 1 <= args.max_size <= p or budget < 1:
        raise ValueError("require rows>=40, p>=12, 1<=max-size<=p, budget>=1")
    from math import comb
    if budget > sum(comb(p, k) for k in range(1, args.max_size + 1)):
        raise ValueError("budget exceeds number of available panels")
    cases = ([("shells", d) for d in (2, 4, 8)] + [("single_shell", 5), ("correlated_gaussian", 5), ("mean_shift", 3)]
             if smoke else [("shells", d) for d in (2, 3, 4, 5, 8)]
             + [("single_shell", d) for d in (2, 5)]
             + [(case, 5) for case in ("independent_gaussian", "correlated_gaussian", "student_t", "common_center_scale_mixture")]
             + [("mean_shift", 3)])
    return [{"name": f"{case}_d{d}_p{p}_seed{seed}_search{search_seed}", "case": case, "dimension": d,
             "p": p, "seed": seed, "search_seed": search_seed, "n_fit": rows, "n_search": rows,
             "n_validation": rows, "n_test": rows, "max_size": args.max_size, "budget": budget,
             "methods": list(METHODS)} for seed, search_seed in zip(seeds, search_seeds) for case, d in cases]


def load_resume(directory):
    directory = directory.resolve()
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] not in {"failed", "interrupted", "complete"}:
        raise ValueError("resume requires a stopped run")
    if set(manifest["source_sha256"]) != set(SOURCES):
        raise ValueError("resume source set differs")
    for source, sha in manifest["source_sha256"].items():
        if digest(ROOT / source) != sha or digest(directory / "source_snapshot" / source) != sha:
            raise ValueError(f"resume source changed: {source}")
    names = [job["name"] for job in manifest["jobs"]]
    if len(set(names)) != len(names) or any(not re.fullmatch(r"[A-Za-z0-9_]+", name) for name in names):
        raise ValueError("invalid resume job names")
    if len(set(manifest["completed"])) != len(manifest["completed"]) or not set(manifest["completed"]) <= set(names):
        raise ValueError("invalid completion record")
    reports = {}
    for job in manifest["jobs"]:
        name = job["name"]
        if name not in manifest["completed"]:
            continue
        result = json.loads((directory / name / "result.json").read_text(encoding="utf-8"))
        if result["job"] != job:
            raise ValueError(f"completed configuration differs: {name}")
        reports[name] = result
    return directory, manifest, reports


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    resume = None
    try:
        if args.resume is not None:
            flags = {s.split('=')[0] for s in (sys.argv[1:] if argv is None else argv) if s.startswith('--')}
            if flags - {"--resume", "--output", "--list-only"}:
                raise ValueError("resume uses saved configuration; only --output and --list-only may accompany it")
            resume = load_resume(args.resume)
            planned = resume[1]["jobs"]
        else:
            planned = jobs(args)
    except (ValueError, FileNotFoundError) as exc:
        cli.error(str(exc))
    if args.list_only:
        print(json.dumps({"jobs": len(planned), "fits_per_arm": planned[0]["budget"], "planned": planned}, indent=2))
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
    manifest = {"status": "running", "created_utc": datetime.now(timezone.utc).isoformat(),
                "jobs": planned, "completed": [], "current_job": None,
                "source_sha256": {s: digest(ROOT / s) for s in SOURCES},
                "runtime": {"python": platform.python_version(), "threads": 1,
                            **{p: version(p) for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
                "scope": "development comparison of hidden-panel search; no novelty or split-validity guarantee",
                "selection": "adaptive search block only; validation/test never select a panel",
                "oracle_role": "post-search diagnostic only, never injected into discovery",
                "fit_budget": "same unique radial2 fits per arm; post-selection radial1/oracle fits separate"}
    reports = []
    if resume:
        parent, previous, completed = resume
        receipt = {"parent_run": str(parent), "parent_manifest_sha256": digest(parent / "manifest.json"), "reused_jobs": {}}
        shutil.copyfile(parent / "manifest.json", output / "resume_parent_manifest.json")
        for job in planned:
            name = job["name"]
            if name in completed:
                shutil.copytree(parent / name, output / name)
                receipt["reused_jobs"][name] = {str(f.relative_to(output / name)): digest(f)
                    for f in (output / name).rglob('*') if f.is_file()}
                reports.append(completed[name])
                manifest["completed"].append(name)
        manifest["resume"] = receipt
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} jobs, {len(METHODS)} arms, {planned[0]['budget']} unique fits per arm. Results: {output}", flush=True)
    started = perf_counter()
    try:
        with threadpool_limits(limits=1):
            for i, job in enumerate(planned, 1):
                if job["name"] in manifest["completed"]:
                    continue
                print(f"[{i}/{len(planned)}] {job['name']}", flush=True)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                directory = output / job["name"]
                directory.mkdir()
                report = run_search_case(job, directory, progress=lambda msg: print(f"  {msg}", flush=True))
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
