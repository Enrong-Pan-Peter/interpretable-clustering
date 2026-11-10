"""Focused followup: forbid kernel projections from flattening to one dimension.

Reuses the saved pilot discovery/validation/test rows. This is a development
followup, not an independent confirmatory experiment. No test-based selection.
"""
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
import argparse
import hashlib
import json
import platform
import sys

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.datasets import DiscoveryScaler
from atomic_research.experiment import write_json
from atomic_research.kernel_benchmark import report_model
from atomic_research.kernel_panels import fit_frozen_kernel_panel, load_kernel_panel, _project_rows, _spectral_loss
from atomic_research.rank_preserved_kernel import fit_rank_preserved_kernel_panel


def reconstruct_pca(X, parent):
    """Exact first initializer, using only original discovery rows and settings."""
    d = parent.diagnostics
    scaled = parent.scaler.transform(X)
    columns = np.flatnonzero(np.var(scaled, axis=0) > 1e-14)
    selected_rows = np.asarray(d["reference_indices"], dtype=int)
    optimization_X = scaled[np.ix_(selected_rows, columns)]
    rank = min(d["requested_rank"], len(columns), len(selected_rows))
    _, _, right = np.linalg.svd(optimization_X - optimization_X.mean(0), full_matrices=False)
    partial = _project_rows(right[:rank].T, min(d["requested_budget"], len(columns)))
    matrix = np.zeros((X.shape[1], partial.shape[1]))
    matrix[columns] = partial
    panel = tuple(np.flatnonzero(np.linalg.norm(matrix, axis=1) > 1e-12).tolist())
    if list(panel) != d["restarts"][0]["initial_panel"]:
        raise ValueError("Reconstructed PCA initializer does not match saved initial support")
    loss = _spectral_loss(scaled[selected_rows] @ matrix, kernel=d["kernel"],
                          objective="gap_ratio", neighbors=d["neighbors"])[0]
    if not np.isclose(loss, d["restarts"][0]["initial_loss"], rtol=1e-8, atol=1e-10):
        raise ValueError("Reconstructed PCA initializer does not match saved initial loss")
    model = fit_frozen_kernel_panel(X, panel, matrix, kernel=d["kernel"], neighbors=d["neighbors"],
                                   seed=d["seed"], max_samples=d["reference_rows"])
    model.diagnostics["followup_role"] = "exact_unoptimized_original_pca_start"
    return model


def run_job(source, job, directory, *, smoke=False):
    config = job["parent_config"]
    case_dir = source / config["name"]
    with np.load(case_dir / "data_and_splits.npz", allow_pickle=False) as f:
        data = {k: f[k] for k in f.files}
    X = data["X"]
    indices = tuple(data[split] for split in ("discovery", "validation", "test"))
    discovery = X[indices[0]]
    parent = load_kernel_panel(case_dir / f"projection_gap_{job['kernel']}_model.npz")
    original_pca = reconstruct_pca(discovery, parent)
    kwargs = dict(budget=config["budget"], rank=config["rank"], kernel=job["kernel"], seed=config["seed"],
                  neighbors=config["neighbors"], max_samples=config["max_samples"])
    constrained_pca = fit_rank_preserved_kernel_panel(discovery, steps=0, restarts=1, **kwargs)
    constrained = fit_rank_preserved_kernel_panel(discovery, steps=3 if smoke else config["steps"],
        restarts=1 if smoke else config["restarts"], **kwargs)
    # All choices above are frozen before annotations or test metrics are read.
    models = {"original_pca": original_pca, "saved_unconstrained": parent,
              "rank_preserved_pca": constrained_pca, "rank_preserved_optimized": constrained}
    y = data["y"]
    parent_report = json.loads((case_dir / "report.json").read_text())
    reference = set(parent_report["reference_panel"])
    reports = {}
    for name, model in models.items():
        entry = report_model(model, X, y, indices, [f"f{j:04d}" for j in range(X.shape[1])], directory, name)
        singular = np.linalg.svd(model.transform_matrix, compute_uv=False)
        entry["second_over_first_singular_value"] = float(singular[1] / singular[0]) if len(singular) > 1 else 0.
        entry["transform_gram"] = (model.transform_matrix.T @ model.transform_matrix).tolist()
        entry["heldout_graph_loss"] = {}
        for split, rows in zip(("validation", "test"), indices[1:]):
            projected = model.scaler.transform(X[rows]) @ model.transform_matrix
            entry["heldout_graph_loss"][split] = _spectral_loss(projected, kernel=job["kernel"],
                 objective="gap_ratio", neighbors=config["neighbors"])[0]
        if parent_report["reference_kind"] == "planted":
            entry["planted_recall"] = len(set(model.panel) & reference) / len(reference)
        reports[name] = entry
    np.savez_compressed(directory / "data_and_splits.npz", **data)
    result = {"job": job, "models": reports, "smoke": smoke,
        "scope": "Fixed binary developmental followup on previously inspected pilot rows; no selected winner. "
                 "Validation/test graph losses are diagnostics only, not model selection or cluster-existence tests.",
        "fit_change": "hard row support followed by polar projection onto A.T A=I/rank; same gap loss and native rule"}
    write_json(directory / "report.json", result)
    return result


def write_summary(output, reports):
    fmt = lambda x: "—" if x is None else f"{x:.3f}"
    lines = ["# Rank-preservation development followup", "",
        "This reuses the kernel pilot rows and labels for diagnostic reporting. It is not independent confirmation. "
        "No winner is chosen and no cluster-existence test is implemented. Native prediction, panel size and tree fidelity stay separate.", "",
        "| Dataset | Seed | Kernel | Variant | Status | Test ARI | Val graph loss | Sigma2/sigma1 | Features | Tree error |",
        "|---|---:|---|---|---|---:|---:|---:|---:|---:|"]
    for report in reports:
        config = report["job"]["parent_config"]
        for name, row in report["models"].items():
            lines.append(f"| {config['dataset']} | {config['seed']} | {report['job']['kernel']} | {name} | "
                f"{row['diagnostics']['status']} | {fmt(row['metrics']['test']['ari'])} | "
                f"{fmt(row['heldout_graph_loss']['validation'])} | {fmt(row['second_over_first_singular_value'])} | "
                f"{row['panel_size']} | {fmt(row['metrics']['test']['tree_disagreement'])} |")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(output / "summary.json", {"completed_jobs": len(reports), "reports": reports})


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path)
    cli.add_argument("--suite", choices=["targeted", "smoke"], default="targeted")
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_rank_preservation")
    cli.add_argument("--list-only", action="store_true")
    args = cli.parse_args(argv)
    if args.source is None:
        sources = sorted((ROOT / "results/research_kernel_panels").glob("*/manifest.json"))
        if not sources:
            cli.error("No saved kernel pilot; pass --source")
        args.source = sources[-1].parent
    source_manifest = json.loads((args.source / "manifest.json").read_text())
    if source_manifest["status"] != "complete":
        cli.error("Source pilot must be complete")
    changed = [p for p, h in source_manifest["source_sha256"].items()
               if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    if changed:
        cli.error(f"Historical source changed: {changed}; cannot assert matched reconstruction")
    cases = [job for job in source_manifest["jobs"]
             if job["dataset"] in {"mean_shift", "grouped_moons", "null_independent", "null_correlated"}]
    if args.suite == "smoke":
        cases = cases[:1]
    planned = [dict(name=case["name"] + "_" + kernel, parent_config=case, kernel=kernel)
               for case in cases for kernel in ("local", "global")]
    if not planned:
        cli.error("Source run has no eligible cases")
    if args.list_only:
        print(json.dumps(planned, indent=2))
        return
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *sorted((ROOT / "atomic_research").glob("*.py"))]
    manifest = {"status": "running", "source_run": str(args.source.resolve()),
        "parent_manifest_sha256": hashlib.sha256((args.source / "manifest.json").read_bytes()).hexdigest(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "runtime": {"python": platform.python_version(), **{k: version(k) for k in ("numpy", "scipy", "scikit-learn")}},
        "jobs": planned, "completed": [], "suite": args.suite,
        "no_test_or_annotation_selection": True, "reuses_development_rows": True}
    write_json(output / "manifest.json", manifest)
    print(f"{len(planned)} jobs from {args.source}. Output: {output}", flush=True)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for i, job in enumerate(planned, 1):
                print(f"[{i}/{len(planned)}] {job['name']}", flush=True)
                manifest["current_job"] = job["name"]
                write_json(output / "manifest.json", manifest)
                directory = output / job["name"]
                directory.mkdir(exist_ok=False)
                reports.append(run_job(args.source, job, directory, smoke=args.suite == "smoke"))
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
