"""Posthoc fixed-support readout check; no new feature search or winner selection.

Fits discovery-only centroids and identity-kernel readouts on previously frozen
global-kernel panels. Exact centroid rules describe their own model, not the
original spectral model. Reuses development data, not confirmatory evidence.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import sys
from time import perf_counter

import numpy as np
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.experiment import write_json
from atomic_research.kernel_panels import fit_frozen_kernel_panel, load_kernel_panel
from atomic_research.replicated_panels import predict_linear_rule
from scripts.analyze_research_obstacle_results import ari, counts, external_ari, read


def exact_centroid_rule(centers, panel, scaler, feature_count):
    panel = np.asarray(panel, dtype=int)
    coefficients = 2 * (centers[1] - centers[0]) / scaler.scale[panel]
    intercept = float(np.sum(centers[0]**2 - centers[1]**2) - coefficients @ scaler.mean[panel])
    return {"type": "exact_native_linear_rule", "panel": panel.tolist(),
        "feature_names": [f"f{j:04d}" for j in panel], "coefficients": coefficients.tolist(),
        "intercept": intercept, "imputation_medians": scaler.median[panel].tolist(),
        "input_feature_count": feature_count, "labels_are_arbitrary": True,
        "cluster_existence_established": False,
        "assignment": "class 1 if sum(coefficients * median_imputed_raw_features) + intercept > 0, otherwise class 0",
        "scope": "Exact for this fitted centroid model; not an approximation claimed to preserve the spectral model."}


def run_case(source, job, output):
    directory = source / job["name"]
    config = job["parent_config"]
    with np.load(directory / "data_and_splits.npz", allow_pickle=False) as data:
        X, y = data["X"], data["y"]
        rows = {split: data[split] for split in ("discovery", "validation", "test")}
        reference = set(data["reference_panel"].tolist())
    results, checks = {}, 0
    for name in ("rank_preserved_pca", "rank_preserved_optimized"):
        model = load_kernel_panel(directory / (name + "_model.npz"))
        panel = np.asarray(model.panel, dtype=int)
        Z = model.scaler.transform(X)[:, panel]
        centroid = KMeans(n_clusters=2, n_init=10, random_state=config["seed"]).fit(Z[rows["discovery"]])
        identity = fit_frozen_kernel_panel(X[rows["discovery"]], panel, kernel="global", seed=config["seed"],
            neighbors=config["neighbors"], max_samples=config["max_samples"])
        # Readout fits and rule coefficients are frozen before annotation scoring.
        rule = exact_centroid_rule(centroid.cluster_centers_, panel, model.scaler, X.shape[1])
        identity.save(output / (name + "_identity_model.npz"))
        write_json(output / (name + "_centroid_rule.json"), rule)
        terms = [f"({coefficient:.12g}) * {feature}" for coefficient, feature in
                 zip(rule["coefficients"], rule["feature_names"])]
        (output / (name + "_centroid_rule.txt")).write_text(
            "Exact centroid rule in original feature units. Impute with recorded discovery medians first.\n"
            "Class labels are arbitrary. This replaces the kernel assignment; it does not explain that different model.\n"
            "Displayed coefficients are rounded; use JSON for predictions.\n\nClass 1 if:\n"
            + " +\n".join(terms) + f"\n> {-rule['intercept']:.12g}\nOtherwise class 0.\n", encoding="utf-8")
        native_train = model.predict(X[rows["discovery"]])
        flip = bool(np.mean(centroid.labels_ != native_train) > .5)
        predictions, metrics = {}, {}
        for split, indices in rows.items():
            native = model.predict(X[indices])
            simple = centroid.predict(Z[indices])
            from_rule = predict_linear_rule(rule, X[indices])
            if not np.array_equal(simple, from_rule):
                raise AssertionError("Exported centroid rule does not reproduce the model")
            checks += 1
            graph = identity.predict(X[indices])
            oriented = 1 - simple if flip else simple
            predictions.update({split + "_native": native, split + "_centroid": simple,
                                split + "_identity": graph, split + "_rule": from_rule})
            metrics[split] = {"native_ari": external_ari(y[indices], native),
                "centroid_ari": external_ari(y[indices], simple), "identity_ari": external_ari(y[indices], graph),
                "centroid_agreement_ari": ari(native, simple),
                "centroid_disagreement_to_native": float(np.mean(oriented != native)),
                "centroid_child_sizes": counts(simple), "rule_disagreement_to_centroid": float(np.mean(simple != from_rule))}
        np.savez_compressed(output / (name + "_readout_predictions.npz"), **predictions,
                            panel=panel, centroid_centers=centroid.cluster_centers_)
        results[name] = {"panel": panel.tolist(), "panel_size": len(panel),
            "planted_recall": len(set(panel) & reference) / len(reference) if config["dataset"] in ("mean_shift", "grouped_moons") else None,
            "centroid_label_flip_for_fidelity": flip, "metrics": metrics}
    result = {"job": job, "readouts": results, "exact_rule_replay_checks": checks,
        "scope": "Posthoc fixed-panel development comparison. No new feature search, test-based choice or cluster-existence test."}
    write_json(output / "report.json", result)
    return result


def write_summary(output, reports):
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    lines = ["# Fixed-panel readout comparison", "",
        "Posthoc development check on the same observations. Centroid and identity-graph models use only discovery rows and fixed panels. "
        "All results are reported; no winner is selected. Exact rules describe the centroid model itself, not the original kernel assignment.", "",
        "| Case | Seed | Panel source | Features | Native ARI | Centroid ARI | Identity ARI | Centroid/kernel disagreement |",
        "|---|---:|---|---:|---:|---:|---:|---:|"]
    for report in reports:
        config = report["job"]["parent_config"]
        for name, row in report["readouts"].items():
            metric = row["metrics"]["test"]
            lines.append(f"| {config['dataset']} | {config['seed']} | {name} | {row['panel_size']} | "
                f"{fmt(metric['native_ari'])} | {fmt(metric['centroid_ari'])} | {fmt(metric['identity_ari'])} | "
                f"{fmt(metric['centroid_disagreement_to_native'])} |")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(output / "summary.json", {"reports": reports,
               "exact_rule_replay_checks": sum(r["exact_rule_replay_checks"] for r in reports)})


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("source", type=Path)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_panel_readouts")
    args = cli.parse_args(argv)
    parent = read(args.source / "manifest.json")
    if parent["status"] != "complete":
        cli.error("Source must be complete")
    for name, expected in parent["source_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            cli.error(f"Historical source changed: {name}")
    jobs = [job for job in parent["jobs"] if job["kernel"] == "global"]
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *sorted((ROOT / "atomic_research").glob("*.py"))]
    manifest = {"status": "running", "parent_manifest_sha256": hashlib.sha256((args.source / "manifest.json").read_bytes()).hexdigest(),
        "source_run": str(args.source.resolve()), "jobs": jobs, "completed": [],
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "readouts_frozen_before_annotation_scoring": True, "posthoc_development": True}
    write_json(output / "manifest.json", manifest)
    started, reports = perf_counter(), []
    try:
        with threadpool_limits(limits=1):
            for i, job in enumerate(jobs, 1):
                print(f"[{i}/{len(jobs)}] {job['name']}", flush=True)
                destination = output / job["name"]
                destination.mkdir(exist_ok=False)
                reports.append(run_case(args.source, job, destination))
                manifest["completed"].append(job["name"])
                write_summary(output, reports)
                write_json(output / "manifest.json", manifest)
        manifest.update(status="complete", seconds=perf_counter() - started)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        write_json(output / "manifest.json", manifest)
    print(output, flush=True)


if __name__ == "__main__":
    main()
