"""Run bounded sparse-kernel development fits; leave longer runs to local terminal."""
from datetime import datetime, timezone
from importlib.metadata import version
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
from types import SimpleNamespace

from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.experiment import write_json
from atomic_research.kernel_benchmark import run_case, write_summary


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=["smoke", "pilot", "geometry", "real", "all"], default="pilot")
    cli.add_argument("--seeds", type=int, nargs="+", default=[26, 27, 28])
    cli.add_argument("--budgets", type=int, nargs="+", default=[16])
    cli.add_argument("--n", type=int, default=800)
    cli.add_argument("--rank", type=int, default=2)
    cli.add_argument("--steps", type=int, default=60)
    cli.add_argument("--restarts", type=int, default=3)
    cli.add_argument("--neighbors", type=int, default=7)
    cli.add_argument("--max-samples", type=int, default=200)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_kernel_panels")
    cli.add_argument("--list-only", action="store_true")
    return cli


def jobs(args):
    if min(args.budgets) < 1 or min(args.seeds) < 0 or args.n < 80:
        raise ValueError("Require positive budgets, nonnegative seeds and n>=80")
    if min(args.rank, args.steps, args.restarts, args.neighbors) < 1 or args.max_samples < 10:
        raise ValueError("Positive rank/steps/restarts/neighbors and max-samples>=10 required")
    if len(set(args.seeds)) != len(args.seeds) or len(set(args.budgets)) != len(args.budgets):
        raise ValueError("Duplicate configurations are not replications")
    if args.rank > min(args.budgets) or args.neighbors >= min(args.max_samples, args.n // 2) - 1:
        raise ValueError("Rank must not exceed any budget; neighbors must be < landmark count-1")
    cases = []
    if args.suite in {"pilot", "all"}:
        cases += [("mean_shift", 200, 12), ("grouped_moons", 50, 10),
                  ("shells", 50, 5), ("covariance_pairs", 50, 8),
                  ("null_independent", 50, 2), ("null_correlated", 50, 2),
                  ("single_shell", 50, 5)]
    if args.suite in {"geometry", "all"}:
        cases += [("moons", 50, 2), ("rings", 50, 2), ("spirals", 50, 2),
                  ("distributed_moons", 50, 8), ("shells", 50, 12)]
    if args.suite in {"real", "all"}:
        cases += [("metabric", 250, 5)]
    if args.suite == "smoke":
        return [dict(dataset="grouped_moons", p=12, signals=6, seed=91, budget=6,
                     n=120, rank=2, steps=3, restarts=1, neighbors=7, max_samples=40,
                     name="smoke_grouped_moons_seed91")]
    return [dict(dataset=case, p=p, signals=s, seed=seed, budget=budget, n=args.n,
                 rank=args.rank, steps=args.steps, restarts=args.restarts,
                 neighbors=args.neighbors, max_samples=args.max_samples,
                 name=f"{case}_p{p}_s{s}_b{budget}_seed{seed}")
            for seed in args.seeds for budget in args.budgets for case, p, s in cases]


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    try:
        planned = jobs(args)
    except ValueError as exc:
        cli.error(str(exc))
    if args.list_only:
        print(json.dumps(planned, indent=2))
        return
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *sorted((ROOT / "atomic_research").glob("*.py")),
               *sorted((ROOT / "atomicplus").rglob("*.py"))]
    manifest = {"status": "running", "config": vars(args), "jobs": planned, "completed": [],
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "runtime": {"python": platform.python_version(), **{k: version(k) for k in ("numpy", "scipy", "scikit-learn")}},
        "scope": "development prototype, fixed binary clusters; not GroupFS reproduction or SOTA comparison",
        "no_annotation_or_test_based_selection": True, "no_cluster_acceptance_rule": True}
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} cases. Results: {output}", flush=True)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for i, job in enumerate(planned, 1):
                print(f"[{i}/{len(planned)}] {job['name']}", flush=True)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                directory = output / job["name"]
                directory.mkdir(exist_ok=False)
                reports.append(run_case(SimpleNamespace(**job), directory))
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
    print(f"Complete in {manifest['seconds'] / 60:.1f} minutes. {output / 'summary.md'}", flush=True)


if __name__ == "__main__":
    main()
