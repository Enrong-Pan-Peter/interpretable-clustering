"""Run staged supplied-panel radial diagnostics; larger searches are deferred."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import sys
from time import perf_counter

from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.radial_diagnostics import run_case, write_json, write_summary

# Only this reviewed predecessor is compatible with the optimizer-boundary
# repair. A different model/experiment implementation requires a fresh run.
BOUNDARY_FIX_PREDECESSOR = "8df4a032264a49a1cdc7d8847662cea6ad3f02c06f965b68b6d772c19f0752bf"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_resume(directory):
    """Validate a previous run without modifying it or fitting any models."""
    directory = Path(directory).resolve()
    parent = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if parent["status"] not in {"failed", "interrupted", "complete"}:
        raise ValueError("resume requires a stopped run; its manifest still says running")
    hashes = {key.replace('\\', '/'): value for key, value in parent["source_sha256"].items()}
    for relative, expected in hashes.items():
        snapshot = (directory / "source_snapshot" / relative).resolve()
        if not snapshot.is_relative_to(directory / "source_snapshot") or not snapshot.is_file() or digest(snapshot) != expected:
            raise ValueError(f"saved source snapshot is missing or changed: {relative}")
    helper = "atomic_research/radial_diagnostics.py"
    core = "atomic_research/radial_panels.py"
    if hashes.get(helper) != digest(ROOT / helper):
        raise ValueError("experiment/generator code changed; use a fresh run instead of mixing results")
    if hashes.get(core) not in {digest(ROOT / core), BOUNDARY_FIX_PREDECESSOR}:
        raise ValueError("model version is not compatible with the reviewed boundary repair")
    names = [job["name"] for job in parent["jobs"]]
    if len(names) != len(set(names)) or any(Path(name).name != name or name in {'.', '..'} for name in names):
        raise ValueError("invalid or duplicate saved job names")
    completed = parent["completed"]
    if len(completed) != len(set(completed)) or not set(completed).issubset(names):
        raise ValueError("invalid saved completion list")
    reports = {}
    for job in parent["jobs"]:
        if job["name"] in completed:
            report = json.loads((directory / job["name"] / "result.json").read_text(encoding="utf-8"))
            if report["job"] != job:
                raise ValueError(f"completed job configuration differs: {job['name']}")
            if not (directory / job["name"] / "splits.npz").is_file() or not (directory / job["name"] / "predictions.npz").is_file():
                raise ValueError(f"completed job lacks its data or predictions: {job['name']}")
            reports[job["name"]] = report
    return directory, parent, reports


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=("smoke", "pilot"), default="smoke")
    cli.add_argument("--stage", choices=("known-panel", "candidate-ranking"), default="candidate-ranking")
    cli.add_argument("--seeds", type=int, nargs="+", default=None)
    cli.add_argument("--p", type=int, default=None)
    cli.add_argument("--n-fit", type=int, default=None)
    cli.add_argument("--n-validation", type=int, default=None)
    cli.add_argument("--n-test", type=int, default=None)
    cli.add_argument("--candidates", type=int, default=10)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_radial_diagnostic")
    cli.add_argument("--list-only", action="store_true")
    cli.add_argument("--resume", type=Path, help="Copy completed jobs into a new run and finish the recorded plan; preserve the original run")
    return cli


def jobs(args):
    seeds = args.seeds if args.seeds is not None else ([811] if args.suite == "smoke" else [1201, 1213, 1229])
    p = args.p if args.p is not None else (12 if args.suite == "smoke" else 24)
    sizes = {key: getattr(args, key) if getattr(args, key) is not None else (160 if args.suite == "smoke" else 600)
             for key in ("n_fit", "n_validation", "n_test")}
    if not seeds or min(seeds) < 0 or len(set(seeds)) != len(seeds):
        raise ValueError("Require distinct nonnegative seeds")
    if min(sizes.values()) < 40 or not 1 <= args.candidates <= 12:
        raise ValueError("Each split must have >=40 rows; candidates must be between 1 and 12")
    if args.suite == "smoke":
        cases = [("shells", 2), ("shells", 5), ("correlated_gaussian", 3), ("student_t", 3), ("mean_shift", 3)]
    else:
        cases = [("shells", d) for d in (2, 3, 5, 8)]
        cases += [("single_shell", d) for d in (2, 5)]
        cases += [(case, 5) for case in ("independent_gaussian", "correlated_gaussian", "student_t", "common_center_scale_mixture")]
        cases += [("mean_shift", 3), ("quartic_shells", 3)]
    if p < max(d for _, d in cases) + 4:
        raise ValueError("p must leave at least four nuisance features beyond the largest supplied panel")
    return [{"name": f"{case}_d{dimension}_p{p}_seed{seed}", "case": case, "dimension": dimension,
             "p": p, "seed": seed, **sizes, "stage": args.stage, "candidates": args.candidates}
            for seed in seeds for case, dimension in cases]


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    resume = None
    try:
        if args.resume is not None:
            flags = {arg.split('=')[0] for arg in (sys.argv[1:] if argv is None else argv) if arg.startswith('--')}
            if flags - {'--resume', '--output', '--list-only'}:
                raise ValueError("--resume uses the saved configuration; only --output and --list-only may accompany it")
            resume = load_resume(args.resume)
            planned = resume[1]["jobs"]
        else:
            planned = jobs(args)
    except ValueError as exc:
        cli.error(str(exc))
    if args.list_only:
        print(json.dumps({"jobs": len(planned), "reusable_jobs": len(resume[2]) if resume else 0, "planned": planned}, indent=2))
        return 0
    if resume and len(resume[2]) == len(planned):
        print(f"Run already complete: {resume[0]}", flush=True)
        return 0
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), ROOT / "atomic_research/radial_diagnostics.py", ROOT / "atomic_research/radial_panels.py"]
    for source in sources:
        snapshot = output / "source_snapshot" / source.relative_to(ROOT)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source.read_bytes())
    manifest = {"status": "running", "created_utc": datetime.now(timezone.utc).isoformat(),
                "config": resume[1]["config"] if resume else vars(args), "jobs": planned, "completed": [], "current_job": None,
                "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
                "runtime": {"python": platform.python_version(), "threads": 1,
                            **{package: version(package) for package in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
                "scope": "supplied-panel oracle diagnostics; no autonomous feature discovery or inferential guarantees",
                "label_use": "oracle candidate construction and descriptive reporting only",
                "source_snapshot_directory": "source_snapshot",
                "test_used_for_selection": False}
    reports = []
    if resume:
        parent_dir, parent, cached = resume
        receipt = {"parent_run": str(parent_dir), "parent_manifest_sha256": digest(parent_dir / "manifest.json"),
                   "parent_source_sha256": parent["source_sha256"], "reused_jobs": {},
                   "repair": "roundoff-only optimizer-bound clipping; unchanged density, objective, seeds and selection"}
        shutil.copyfile(parent_dir / "manifest.json", output / "resume_parent_manifest.json")
        shutil.copytree(parent_dir / "source_snapshot", output / "resume_parent_sources")
        for job in planned:
            name = job["name"]
            if name in cached:
                source, target = parent_dir / name, output / name
                shutil.copytree(source, target)
                files = {str(path.relative_to(target)): digest(path) for path in target.rglob('*') if path.is_file()}
                if any(digest(source / relative) != expected for relative, expected in files.items()):
                    raise ValueError(f"copied job changed during resume: {name}")
                receipt["reused_jobs"][name] = {"files_sha256": files}
                manifest["completed"].append(name)
                reports.append(cached[name])
        manifest["resume"] = receipt
        print(f"Reusing {len(reports)} completed jobs; {len(planned) - len(reports)} remain. Original run preserved.", flush=True)
        write_summary(output, reports)
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} jobs, stage={planned[0]['stage']}. Results: {output}", flush=True)
    started = perf_counter()
    try:
        with threadpool_limits(limits=1):
            for index, job in enumerate(planned, 1):
                if job["name"] in manifest["completed"]:
                    continue
                print(f"[{index}/{len(planned)}] {job['name']}", flush=True)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                directory = output / job["name"]
                directory.mkdir(exist_ok=False)
                report = run_case(job, directory, progress=lambda message: print(f"  {message}", flush=True))
                reports.append(report)
                manifest["completed"].append(job["name"])
                write_summary(output, reports)
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
