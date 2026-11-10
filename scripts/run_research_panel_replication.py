"""Native feature-panel rediscovery and conservative fixed-prefix validation.

Four disjoint row blocks: two discovery fits, shared validation, untouched test.
No enumeration of feature combinations, no annotation-based model selection.
"""
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

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.experiment import write_json
from atomic_research.replicated_panels import run_case


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=["all", "scaling", "real", "controls", "smoke"], default="all")
    cli.add_argument("--seeds", type=int, nargs="+", default=[6, 7, 8])
    cli.add_argument("--n", type=int, default=800)
    cli.add_argument("--ps", type=int, nargs="+", default=[50, 200])
    cli.add_argument("--signals", type=int, nargs="+", default=[5, 8, 12])
    cli.add_argument("--cap", type=int, default=16)
    cli.add_argument("--separation", type=float, default=3.)
    cli.add_argument("--steps", type=int, default=40)
    cli.add_argument("--restarts", type=int, default=3)
    cli.add_argument("--alpha", type=float, default=.05)
    cli.add_argument("--max-error", type=float, default=.05)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_panel_replication")
    cli.add_argument("--list-only", action="store_true")
    return cli


def jobs(args):
    if args.n < 80 or min(args.ps) < 1 or min(args.signals) < 1 or max(args.signals) > min(args.ps):
        raise ValueError("Need n>=80, p>=1 and 1<=signal count<=every p")
    if args.cap < 1 or args.steps < 1 or args.restarts < 1:
        raise ValueError("cap, steps and restarts must be positive")
    if not np.isfinite(args.alpha) or not 0 < args.alpha < 1 or not np.isfinite(args.max_error) or not 0 <= args.max_error < 1:
        raise ValueError("Require 0<alpha<1 and 0<=max-error<1")
    if not np.isfinite(args.separation) or args.separation < 0:
        raise ValueError("separation must be finite and nonnegative")
    if any(len(v) != len(set(v)) for v in (args.seeds, args.ps, args.signals)):
        raise ValueError("Duplicate configurations are not independent replications")
    if min(args.seeds) < 0:
        raise ValueError("Seeds must be nonnegative")
    if args.suite == "smoke":
        return [dict(dataset="mean_shift", seed=19, n=160, p=12, signal_features=5,
                     cap=8, steps=5, restarts=1, separation=3., alpha=.05, max_error=.05,
                     name="smoke_mean_shift_seed19")]
    result = []
    for seed in args.seeds:
        cases = []
        if args.suite in ("all", "scaling"):
            cases += [("mean_shift", p, s) for p in args.ps for s in args.signals]
        if args.suite in ("all", "real"):
            cases += [("metabric", 250, 5)]
        if args.suite in ("all", "controls"):
            cases += [(case, max(args.ps), 5) for case in ("null_independent", "null_correlated")]
        for case, p, s in cases:
            result.append(dict(dataset=case, seed=seed, n=args.n, p=p, signal_features=s, cap=args.cap,
                steps=args.steps, restarts=args.restarts, separation=args.separation, alpha=args.alpha,
                max_error=args.max_error, name=f"{case}_p{p}_s{s}_seed{seed}"))
    return result


def write_report(output, reports):
    def num(v):
        return "—" if v is None else f"{v:.3f}"
    lines = ["# Native panel replication", "",
        "Sparse two-means is an established baseline. This experiment preserves its assignment rule, independently fits two discovery samples, and shortens each rule using a training-only prefix ladder. It does not test whether clusters exist or establish novelty.", "",
        "Empirical: observed validation disagreement <= the prescribed tolerance. Bounded: one-sided Clopper–Pearson upper disagreement <= tolerance, with Bonferroni across at most 2*cap prefixes in a case. Conditional on fixed discovery fits and independent identically distributed validation rows, this controls the family of fidelity bounds; it does not cover cluster truth, independent cohorts, all suite cases jointly, or future tuning.", "",
        "## Each learner and selected panel", "",
        "Missing bounded panels are reported, not replaced with a favorable candidate. Test error can exceed the tolerance by sampling variation even when a population-risk bound holds; a single test exceedance is not proof of bound failure.", "",
        "| Case | p | Planted | Seed | Learner | Policy | Full support | Selected size | Val error | Val upper | Test error | Full test ARI | Selected test ARI | Supplied-panel oracle ARI |",
        "|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for report in reports:
        for name, learner in report["learners"].items():
            full = learner.get("full", {})
            for policy in ("empirical", "bounded"):
                row = learner["selected"].get(policy, {})
                lines.append(f"| {report['dataset']} | {report['p']} | {report['signal_features'] or '—'} | {report['seed']} | "
                    f"{name} | {policy} | {full.get('support_size', '—')} | {len(row['panel']) if 'panel' in row else 'none'} | "
                    f"{num(row.get('point_error'))} | {num(row.get('upper_error'))} | {num(row.get('test_fidelity', {}).get('disagreement'))} | "
                    f"{num(full.get('test_ari'))} | {num(row.get('test_ari'))} | {num(learner.get('oracle', {}).get('test_ari'))} |")
    lines += ["", "## Independent rediscovery", "",
        "Each A/B model has its own feature panel and scaler. Label orientation is aligned on validation only for this comparison; that alignment never changes the prefix-vs-teacher fidelity calculation or selected rules. Jaccard measures exact feature overlap; equivalent biological substitutes may differ.", "",
        "| Case | p | Planted | Seed | Policy | Val agreement ARI | Test agreement ARI | Test disagreement | Feature Jaccard | Both val groups >=5 | Both test groups >=5 |",
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|"]
    for report in reports:
        for policy, pair in report["replication"].items():
            lines.append(f"| {report['dataset']} | {report['p']} | {report['signal_features'] or '—'} | {report['seed']} | {policy} | "
                f"{num(pair.get('validation', {}).get('ari'))} | {num(pair.get('test', {}).get('ari'))} | "
                f"{num(pair.get('test', {}).get('disagreement'))} | {num(pair.get('feature_jaccard'))} | "
                f"{pair.get('both_validation_groups_at_least_five', '—')} | {pair.get('both_test_groups_at_least_five', '—')} |")
    lines += ["", "Full prefix curves, cluster sizes, source hashes, prediction arrays and exact linear rules in original feature units are saved per case. Every rule applies its recorded discovery-median imputation first. Rule coefficients are not calibrated class probabilities.", "",
        "Real-data results reuse the same cached cohort and feature universe. The iid assumption is a model assumption, not a donor/external-cohort validation. Planted signal count is not guaranteed to be the minimum useful panel size. Correlated Gaussian controls may be highly stable despite containing only one generated population.", "",
        "The mean-shift oracle fits ordinary unweighted two-means after being supplied the planted panel, on each learner's own discovery rows. It is an ability benchmark, not autonomous feature discovery or the same optimizer. Oracle results never enter model or prefix selection."]
    (output / "summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    write_json(output / "summary.json", {"completed_cases": len(reports), "reports": reports})


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
    sources = [Path(__file__), *sorted((ROOT / "atomic_research").glob("*.py")), *sorted((ROOT / "atomicplus").rglob("*.py"))]
    manifest = {"status": "running", "config": vars(args), "jobs": planned, "completed": [],
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                "runtime": {"python": platform.python_version(), **{k: version(k) for k in ("numpy", "scipy", "scikit-learn")}, "threads": 1},
                "method_scope": "raw mean-separation model family; not a shell/shape discovery solution",
                "no_annotation_or_test_based_selection": True, "no_cluster_acceptance_rule": True}
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} cases. Results: {output}", flush=True)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for index, job in enumerate(planned, 1):
                print(f"[{index}/{len(planned)}] {job['name']}", flush=True)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                directory = output / job["name"]
                directory.mkdir(exist_ok=False)
                reports.append(run_case(SimpleNamespace(**job), directory))
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
