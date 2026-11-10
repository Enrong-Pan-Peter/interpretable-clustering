"""Run staged supplied-panel radial diagnostics; larger searches are deferred."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.radial_diagnostics import run_case, write_json, write_summary


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
    try:
        planned = jobs(args)
    except ValueError as exc:
        cli.error(str(exc))
    if args.list_only:
        print(json.dumps({"jobs": len(planned), "planned": planned}, indent=2))
        return 0
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), ROOT / "atomic_research/radial_diagnostics.py", ROOT / "atomic_research/radial_panels.py"]
    for source in sources:
        snapshot = output / "source_snapshot" / source.relative_to(ROOT)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source.read_bytes())
    manifest = {"status": "running", "created_utc": datetime.now(timezone.utc).isoformat(),
                "config": vars(args), "jobs": planned, "completed": [], "current_job": None,
                "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
                "runtime": {"python": platform.python_version(), "threads": 1,
                            **{package: version(package) for package in ("numpy", "scipy", "scikit-learn", "threadpoolctl")}},
                "scope": "supplied-panel oracle diagnostics; no autonomous feature discovery or inferential guarantees",
                "label_use": "oracle candidate construction and descriptive reporting only",
                "source_snapshot_directory": "source_snapshot",
                "test_used_for_selection": False}
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} jobs, stage={args.stage}. Results: {output}", flush=True)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for index, job in enumerate(planned, 1):
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
