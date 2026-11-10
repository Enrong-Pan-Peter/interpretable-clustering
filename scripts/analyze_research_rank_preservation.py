"""Audit saved rank-preservation results and repeated runs without clustering fits."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import sys

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.datasets import DiscoveryScaler
from atomic_research.experiment import write_json
from atomic_research.kernel_panels import _spectral_loss
from scripts.analyze_research_kernel_results import predict_saved, mean
from scripts.analyze_research_obstacle_results import Checks, ari, external_ari, counts, digest, read


def arrays(path):
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def audit_run(run, checks):
    manifest, summary = read(run / "manifest.json"), read(run / "summary.json")
    checks.check("complete", manifest["status"] == "complete", str(run))
    checks.check("job_count", len(manifest["completed"]) == len(manifest["jobs"]) == len(summary["reports"]), str(run))
    checks.check("unique_jobs", len(set(manifest["completed"])) == len(manifest["completed"]), str(run))
    parent = Path(manifest["source_run"])
    checks.check("parent_manifest", digest(parent / "manifest.json") == manifest["parent_manifest_sha256"], str(run))
    for name, expected in manifest["source_sha256"].items():
        checks.check("source_hash", (ROOT / name).is_file() and digest(ROOT / name) == expected, name)
    model_count = 0
    for job, report in zip(manifest["jobs"], summary["reports"]):
        directory = run / job["name"]
        key = run.name + ":" + job["name"]
        config = job["parent_config"]
        parent_dir = parent / config["name"]
        checks.check("report_identity", read(directory / "report.json") == report, key)
        checks.check("job_identity", report["job"] == job, key)
        checks.check("not_smoke", not report["smoke"], key)
        data, original = arrays(directory / "data_and_splits.npz"), arrays(parent_dir / "data_and_splits.npz")
        for field, value in data.items():
            checks.check("same_parent_data", field in original and np.array_equal(value, original[field], equal_nan=True), key + field)
        X, y = data["X"], data["y"]
        scaler = DiscoveryScaler().fit(X[data["discovery"]])
        for name, entry in report["models"].items():
            location = key + ":" + name
            state = arrays(directory / (name + "_model.npz"))
            predicted = arrays(directory / (name + "_predictions.npz"))
            diagnostics = json.loads(str(state["diagnostics_json"]))
            model_count += 1
            checks.check("diagnostics_identity", diagnostics == entry["diagnostics"], location)
            checks.check("panel_identity", state["panel"].tolist() == entry["panel"], location)
            A = state["transform_matrix"]
            support = np.flatnonzero(np.linalg.norm(A, axis=1) > 1e-12)
            checks.check("support", np.array_equal(support, state["panel"]), location)
            checks.check("support_budget", len(support) == entry["panel_size"] <= config["budget"], location)
            singular = np.linalg.svd(A, compute_uv=False)
            checks.near("singular_ratio", entry["second_over_first_singular_value"], singular[1] / singular[0], location)
            checks.near("gram", entry["transform_gram"], A.T @ A, location)
            for field in ("median", "mean", "scale"):
                checks.near("discovery_preprocessing", state["scaler_" + field], getattr(scaler, field), location + field)
            landmark_rows = np.asarray(diagnostics["reference_indices"], dtype=int)
            reference = scaler.transform(X[data["discovery"]])[landmark_rows] @ A
            checks.near("landmark_projection", reference, state["reference_projection"], location)
            checks.near("discovery_loss", diagnostics["loss"], _spectral_loss(reference,
                        kernel=job["kernel"], objective="gap_ratio", neighbors=config["neighbors"])[0], location)
            for split in ("discovery", "validation", "test"):
                labels, embedding = predict_saved(X[data[split]], state)
                checks.check("independent_prediction", np.array_equal(labels, predicted[split + "_native"]), location + split)
                if split == "discovery":
                    checks.check("train_labels", np.array_equal(labels, state["train_labels"]), location)
                if split == "test":
                    checks.near("independent_embedding", embedding, predicted["test_embedding"], location, 1e-8)
                metric = entry["metrics"][split]
                checks.near("external_ari", metric["ari"], external_ari(y[data[split]], labels), location + split)
                checks.check("child_sizes", metric["cluster_sizes"] == counts(labels), location + split)
                tree = predicted[split + "_tree"]
                checks.near("tree_disagreement", metric["tree_disagreement"], float(np.mean(tree != labels)), location + split)
                checks.near("tree_fidelity", metric["tree_fidelity_ari"], ari(tree, labels), location + split)
                checks.near("tree_ari", metric["tree_ari"], external_ari(y[data[split]], tree), location + split)
                if split != "discovery":
                    loss = _spectral_loss(scaler.transform(X[data[split]]) @ A, kernel=job["kernel"],
                                          objective="gap_ratio", neighbors=config["neighbors"])[0]
                    checks.near("heldout_graph_loss", entry["heldout_graph_loss"][split], loss, location + split)
            if name == "saved_unconstrained":
                inherited = arrays(parent_dir / f"projection_gap_{job['kernel']}_model.npz")
                for field, value in state.items():
                    checks.check("saved_parent_model", np.array_equal(value, inherited[field]), location + field)
            if name.startswith("rank_preserved"):
                rank = config["rank"]
                checks.near("rank_constraint", A.T @ A, np.eye(rank) / rank, location, 1e-12)
                for row in diagnostics["trace"]:
                    checks.check("checkpoint_rank_constraint", row["gram_error"] < 1e-12
                        and abs(row["singular_ratio"] - 1) < 1e-12 and row["active_size"] <= config["budget"], location)
                eligible = [r for r in diagnostics["trace"] if r["valid_checkpoint"]]
                choices = eligible or diagnostics["trace"]
                checks.near("checkpoint_selection", diagnostics["loss"], min(r["loss"] for r in choices), location)
                for restart in diagnostics["restarts"]:
                    trace = [r["loss"] for r in diagnostics["trace"] if r["restart"] == restart["restart"]]
                    checks.check("descent_trace", np.all(np.diff(trace) < 0), location)
            if "planted_recall" in entry:
                overlap = len(set(support) & set(data["reference_panel"]))
                checks.near("planted_recall", entry["planted_recall"], overlap / len(data["reference_panel"]), location)
    return manifest, summary, model_count


def repeated_run(run, other, checks, manifest):
    earlier = read(other / "manifest.json")
    checks.check("repeat_jobs", earlier["jobs"] == manifest["jobs"], str(other))
    checks.check("repeat_sources", earlier["source_sha256"] == manifest["source_sha256"], str(other))
    checks.check("repeat_parent", earlier["parent_manifest_sha256"] == manifest["parent_manifest_sha256"], str(other))
    comparisons = 0
    for job in manifest["jobs"]:
        a, b = run / job["name"], other / job["name"]
        report_a, report_b = read(a / "report.json"), read(b / "report.json")
        for name in report_a["models"]:
            ra, rb = report_a["models"][name], report_b["models"][name]
            checks.check("repeat_metrics", ra["metrics"] == rb["metrics"], job["name"] + name)
            for suffix in ("_model.npz", "_predictions.npz"):
                state_a, state_b = arrays(a / (name + suffix)), arrays(b / (name + suffix))
                for field in state_a:
                    if field == "diagnostics_json":
                        continue  # Wall time legitimately differs.
                    checks.check("repeat_arrays", np.array_equal(state_a[field], state_b[field]), job["name"] + name + field)
                    comparisons += 1
    return comparisons


def summarize(summary):
    groups = defaultdict(list)
    paired = []
    for report in summary["reports"]:
        job = report["job"]
        groups[(job["parent_config"]["dataset"], job["kernel"])].append(report)
        a, b = report["models"]["rank_preserved_pca"], report["models"]["rank_preserved_optimized"]
        paired.append({"dataset": job["parent_config"]["dataset"], "kernel": job["kernel"],
            "seed": job["parent_config"]["seed"],
            "test_ari_change": None if a["metrics"]["test"]["ari"] is None else b["metrics"]["test"]["ari"] - a["metrics"]["test"]["ari"],
            "discovery_loss_change": b["diagnostics"]["loss"] - a["diagnostics"]["loss"],
            "validation_loss_change": b["heldout_graph_loss"]["validation"] - a["heldout_graph_loss"]["validation"],
            "initial_support": a["panel"], "final_support": b["panel"],
            "tree_validation_error": b["metrics"]["validation"]["tree_disagreement"],
            "tree_test_error": b["metrics"]["test"]["tree_disagreement"]})
    aggregate = []
    for (case, kernel), reports in groups.items():
        for name in reports[0]["models"]:
            rows = [r["models"][name] for r in reports]
            aggregate.append({"dataset": case, "kernel": kernel, "model": name, "seeds": len(rows),
                "mean_test_ari": mean([r["metrics"]["test"]["ari"] for r in rows]),
                "test_ari_each": [r["metrics"]["test"]["ari"] for r in rows],
                "mean_validation_loss": mean([r["heldout_graph_loss"]["validation"] for r in rows]),
                "mean_recall": mean([r.get("planted_recall") for r in rows]),
                "mean_tree_error": mean([r["metrics"]["test"]["tree_disagreement"] for r in rows]),
                "sizes": [r["panel_size"] for r in rows]})
    return aggregate, paired


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("run", type=Path)
    cli.add_argument("--compare-repeat", type=Path)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args(argv)
    output = args.output or ROOT / ("results/research_rank_analysis_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
    output.mkdir(parents=True, exist_ok=False)
    checks = Checks()
    with threadpool_limits(limits=1):
        manifest, summary, models = audit_run(args.run, checks)
        repeat_comparisons = 0
        if args.compare_repeat:
            _, _, older_models = audit_run(args.compare_repeat, checks)
            models += older_models
            repeat_comparisons = repeated_run(args.run, args.compare_repeat, checks, manifest)
    aggregate, paired = summarize(summary)
    result = {"source_run": str(args.run.resolve()), "repeat_run": str(args.compare_repeat.resolve()) if args.compare_repeat else None,
        "verification": {"checks": sum(checks.counts.values()), "categories": dict(checks.counts),
                         "failures": checks.failures, "saved_models": models, "repeat_array_comparisons": repeat_comparisons},
        "aggregate": aggregate, "paired": paired,
        "scope": "Descriptive paired development results, three seeds. Repeated execution is not new data. "
                 "Verification replays native assignment and saved tree metrics; it does not verify exported tree text. No clustering fits."}
    write_json(output / "analysis.json", result)
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    lines = ["# Rank-preservation audit", "", result["scope"], "",
        f"{result['verification']['checks']} checks, {len(checks.failures)} discrepancies, {models} saved models.", "",
        "| Case | Kernel | Model | Test ARI | Validation loss | Recall | Tree error | Sizes |",
        "|---|---|---|---:|---:|---:|---:|---|"]
    for row in aggregate:
        lines.append(f"| {row['dataset']} | {row['kernel']} | {row['model']} | {fmt(row['mean_test_ari'])} | "
                     f"{fmt(row['mean_validation_loss'])} | {fmt(row['mean_recall'])} | {fmt(row['mean_tree_error'])} | {row['sizes']} |")
    (output / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["verification"], indent=2))
    print(output)
    if checks.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
