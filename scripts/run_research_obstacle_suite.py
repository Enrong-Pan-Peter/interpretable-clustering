"""Stage model, compression, geometry and negative-control diagnostics.

Reports every prescribed configuration. No external labels choose a winner.
Original pilot files are read-only. Each invocation gets a new results folder.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.experiment import write_json
from atomic_research.obstacle_audits import retention_case, compression_case, geometry_case


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--stage", choices=["all", "retention", "compression", "geometry", "controls"], default="all")
    cli.add_argument("--datasets", nargs="+", default=None,
                     choices=["mean_shift", "shells", "metabric", "levine", "null_independent", "null_correlated"],
                     help="Override dataset list for retention/controls/compression (single-stage runs only)")
    cli.add_argument("--seeds", nargs="+", type=int, default=[3, 4, 5], help="New model/geometry/control seeds")
    cli.add_argument("--pilot-seeds", nargs="+", type=int, default=[0, 1, 2])
    cli.add_argument("--compression-methods", nargs="+", choices=["soft_graph", "sparse_kmeans"],
                     default=["soft_graph", "sparse_kmeans"])
    cli.add_argument("--n", type=int, default=480)
    cli.add_argument("--p", type=int, default=50)
    cli.add_argument("--signal-features", type=int, default=5)
    cli.add_argument("--separation", type=float, default=3.)
    cli.add_argument("--max-features", type=int, default=8)
    cli.add_argument("--steps", type=int, default=40)
    cli.add_argument("--restarts", type=int, default=3)
    cli.add_argument("--geometry-sizes", nargs="+", type=int, default=[480, 960, 1920])
    cli.add_argument("--neighbors", nargs="+", type=int, default=[5, 10, 20])
    cli.add_argument("--pilot-root", type=Path, default=ROOT / "results/research_diagnostics")
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_obstacle_checks")
    cli.add_argument("--list-only", action="store_true")
    return cli


def plan_jobs(args):
    if args.datasets is not None and args.stage in ("all", "geometry"):
        raise ValueError("--datasets applies only to a single retention, controls or compression stage")
    if args.n < 40 or min(args.geometry_sizes) < 40:
        raise ValueError("Use at least 40 rows per generated dataset")
    if not 1 <= args.signal_features <= args.p or not 1 <= args.max_features <= args.p:
        raise ValueError("signal-features and max-features must be between 1 and p")
    if args.steps < 1 or args.restarts < 1 or min(args.neighbors) < 1:
        raise ValueError("steps, restarts and neighbors must be positive")
    for values in (args.seeds, args.pilot_seeds, args.geometry_sizes, args.neighbors, args.compression_methods, args.datasets or []):
        if len(values) != len(set(values)):
            raise ValueError("Repeated seeds/configurations would duplicate evidence; remove duplicates")
    stages = ["retention", "compression", "geometry", "controls"] if args.stage == "all" else [args.stage]
    jobs = []
    for stage in stages:
        if stage in ("retention", "controls"):
            defaults = ["mean_shift", "metabric", "shells"] if stage == "retention" else ["null_independent", "null_correlated"]
            for dataset in args.datasets or defaults:
                if stage == "controls" and not dataset.startswith("null_"):
                    raise ValueError("The controls stage requires a null dataset")
                for seed in args.seeds:
                    jobs.append({"stage": stage, "dataset": dataset, "seed": seed,
                                 "name": f"{stage}_{dataset}_seed{seed}"})
        elif stage == "geometry":
            for n in args.geometry_sizes:
                for seed in args.seeds:
                    jobs.append({"stage": stage, "dataset": "shells", "seed": seed, "n": n,
                                 "name": f"geometry_shells_n{n}_seed{seed}"})
        else:
            datasets = args.datasets or ["mean_shift", "metabric", "levine"]
            wanted = {(case, seed) for case in datasets for seed in args.pilot_seeds}
            sources = {}
            for path in sorted(args.pilot_root.glob("*/manifest.json")):
                saved = json.loads(path.read_text())
                c = saved["config"]
                key = (c["dataset"], c["seed"])
                if key not in wanted or saved["status"] != "complete" or c["mode"] != "search":
                    continue
                if key in sources:
                    raise ValueError(f"Ambiguous pilot sources for {key}; use a pilot-root with a single intended run")
                sources[key] = path.parent
            if wanted - sources.keys():
                raise ValueError(f"Missing completed pilot cases: {sorted(wanted - sources.keys())}")
            for (dataset, seed), source in sorted(sources.items()):
                jobs.append({"stage": stage, "dataset": dataset, "seed": seed, "source": str(source),
                             "name": f"compression_{dataset}_seed{seed}"})
    return jobs


def write_report(output, reports):
    def num(value):
        return "—" if value is None else f"{value:.3f}"

    lines = ["# Obstacle diagnostics", "",
        "All configurations are prescribed and reported; no test-ARI winner is selected. Fresh seeds on real data are resamples of the same cohort. Compression reuses the inspected pilot. These are development diagnostics, not evidence of a novel validated method.", "",
        "Full native support can exceed the feature-prefix cap. Squared coordinates are squared discovery-standardized original features, then standardized again on discovery rows. Each original feature is counted once.", "",
        "The compact table shows the largest prescribed prefix and the full models. Every smaller prefix, feature name, assignment and geometry score is retained in case files. Showing a prefix here does not select it as best.", ""]
    model_reports = [r for r in reports if r["stage"] in ("retention", "controls")]
    if model_reports:
        lines += ["## Model retention and single-population controls", "",
            "ARI compares to external annotations, when available. Fidelity compares test assignments to the full native model, which itself may be wrong. Invalid discovery partitions have blank external ARI. Controls have no external ARI or accepted/rejected status: the procedure always proposes a split.", "",
            "| Case | Seed | Mapping | L1 bound | Prefix size | Full support | Assignment | Test ARI | Fidelity ARI |",
            "|---|---:|---|---:|---:|---:|---|---:|---:|"]
        for report in model_reports:
            cap = max((r["prefix_size"] or 0 for r in report["rows"]), default=0)
            for row in report["rows"]:
                if row["prefix_size"] is not None and row["prefix_size"] != cap:
                    continue
                lines.append(f"| {report['dataset']} | {report['seed']} | {row['representation']} | "
                    f"{row['l1_bound']:.3f} | {row['prefix_size'] or 'full'} | {row['full_active_features']} | "
                    f"{row['readout']} | {num(row['test_ari'])} | {num(row['test_fidelity_to_full_native']['ari'])} |")
        lines += ["", "Test-only centroid refitting on fixed panels is reported in case files. It checks replication of a fixed panel, not independent rediscovery of its features. Stability of this forced split is not a cluster-existence test.", ""]
    compression_reports = [r for r in reports if r["stage"] == "compression"]
    if compression_reports:
        lines += ["## Compression", "",
            "Teacher = original spectral partition with frozen kNN assignment. Same-panel family = the policy's full-panel model before deletion. The refit policy replaces the model family before deleting anything; that change and deletion must be judged separately. ARI 0.95 is not 95% assignment agreement. The foldwise criterion is a sensitivity check, not a confidence bound.", "",
            "| Case | Seed | Method | Deletion policy | Size before → after | Teacher test ARI | Same-panel family ARI | Reduced test ARI | Val disagreements | Test disagreements | Test fidelity ARI |",
            "|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for report in compression_reports:
            for row in report["rows"]:
                lines.append(f"| {report['dataset']} | {report['seed']} | {row['method']} | {row['policy']} | "
                    f"{row['original_size']} → {row['selected_size']} | {num(row['teacher_test_ari'])} | "
                    f"{num(row['same_panel_family_test_ari'])} | {num(row['selected_test_ari'])} | "
                    f"{num(row['validation_fidelity']['disagreement'])} | {num(row['test_fidelity']['disagreement'])} | "
                    f"{num(row['test_fidelity']['ari'])} |")
        lines += ["", "Every single-feature deletion, validation trace, validity guard and cost is saved in each method's deletions file. External annotations never choose a deletion.", ""]
    geometry_reports = [r for r in reports if r["stage"] == "geometry"]
    if geometry_reports:
        lines += ["## Oracle geometry ability check", "",
            "The true features are supplied here. This is a representation/splitter check, not feature discovery. The radius rule receives a radial inductive bias. Compare the separate autonomous squared-model retention results before claiming discoverability.", "",
            "| Rows | Seed | Mapping | Splitter | Graph neighbors | Train ARI | Test ARI |",
            "|---:|---:|---|---|---:|---:|---:|"]
        for report in geometry_reports:
            for row in report["rows"]:
                lines.append(f"| {report['n']} | {report['seed']} | {row['representation']} | {row['splitter']} | "
                    f"{row['k'] or '—'} | {num(row['train_ari'])} | {num(row['test_ari'])} |")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(output / "summary.json", {"completed_cases": len(reports), "reports": reports})


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    try:
        jobs = plan_jobs(args)
    except ValueError as exc:
        cli.error(str(exc))
    if args.list_only:
        print(json.dumps(jobs, indent=2))
        return
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *sorted((ROOT / "atomic_research").glob("*.py")),
               *sorted((ROOT / "atomicplus").rglob("*.py"))]
    manifest = {"status": "running", "config": vars(args), "jobs": jobs, "completed": [],
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "runtime": {"python": platform.python_version(), "numpy": version("numpy"), "scipy": version("scipy"),
                    "scikit-learn": version("scikit-learn"), "threads": 1},
        "no_test_label_selection": True, "no_cluster_acceptance_rule": True,
        "scope": "development ablations; compression reuses pilot, real-data seeds reuse cohorts"}
    write_json(output / "manifest.json", manifest)
    print(f"{len(jobs)} cases. Results: {output}", flush=True)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for index, job in enumerate(jobs, 1):
                print(f"[{index}/{len(jobs)}] {job['name']}", flush=True)
                directory = output / job["name"]
                directory.mkdir(exist_ok=False)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                if job["stage"] == "compression":
                    report = compression_case(args, Path(job["source"]), directory)
                elif job["stage"] == "geometry":
                    report = geometry_case(args, job["seed"], job["n"], directory)
                else:
                    report = retention_case(args, job["dataset"], job["seed"], directory)
                    report["stage"] = job["stage"]
                    write_json(directory / "summary.json", report)
                reports.append(report)
                manifest["completed"].append(job["name"])
                write_report(output, reports)
                write_json(output / "manifest.json", manifest)
        manifest.update(status="complete", current_job=None, seconds=perf_counter()-started)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
                        error=f"{type(exc).__name__}: {exc}", seconds=perf_counter()-started)
        raise
    finally:
        write_json(output / "manifest.json", manifest)
    print(f"Complete in {manifest['seconds']/60:.1f} minutes. {output / 'summary.md'}", flush=True)


if __name__ == "__main__":
    main()
