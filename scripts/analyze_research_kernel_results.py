"""Replay saved kernel models without refitting; write a separate audit artifact."""
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
from atomic_research.datasets import DiscoveryScaler, split_rows
from atomic_research.experiment import write_json
from atomic_research.kernel_benchmark import make_benchmark, VARIANTS
from atomic_research.kernel_panels import _spectral_loss
from scripts.analyze_research_obstacle_results import Checks, ari, external_ari, counts, digest, read


def predict_saved(X, state):
    """Independent explicit-distance replay of the saved eigenfunction rule."""
    panel = state["panel"].astype(int)
    values = np.where(np.isfinite(X[:, panel]), X[:, panel], state["scaler_median"][panel])
    values = (values - state["scaler_mean"][panel]) / state["scaler_scale"][panel]
    projection = values @ state["transform_matrix"][panel]
    reference = state["reference_projection"]
    # Direct differences provide a check independent of the fitting distance code.
    distance = np.sum((projection[:, None, :] - reference[None, :, :])**2, axis=2)
    if str(state["kernel"]) == "local":
        positive = distance > 1e-12
        rank = np.maximum(0, np.minimum(int(state["neighbors"]), positive.sum(1)) - 1)
        ordered = np.sort(np.where(positive, distance, np.inf), axis=1)
        squared_scale = ordered[np.arange(len(distance)), rank]
        squared_scale = np.where(positive.any(1), squared_scale, 0.)
        scale = np.sqrt(np.maximum(squared_scale, 1e-12))
        denominator = scale[:, None] * state["reference_scales"][None, :]
    else:
        denominator = 2.
    affinity = np.exp(-distance / denominator) + 1e-8
    normalized = affinity / np.sqrt(affinity.sum(1)[:, None] * state["reference_degree"][None, :])
    eigenvalue = np.where(np.abs(state["adjacency_eigenvalues"]) > 1e-7,
                         state["adjacency_eigenvalues"], np.inf)
    embedding = (normalized @ state["reference_vectors"]) / eigenvalue
    embedding /= np.maximum(np.linalg.norm(embedding, axis=1, keepdims=True), 1e-14)
    labels = ((embedding[:, None, :] - state["centers"][None, :, :])**2).sum(2).argmin(1)
    return labels, embedding


def model_entries(report):
    for name, entry in report["models"].items():
        yield name, entry
        if "same_panel_identity" in entry:
            yield name + "_identity", entry["same_panel_identity"]
    if report["oracle"] is not None:
        yield "oracle_panel_local", report["oracle"]


def audit_case(directory, job, report, checks):
    key = job["name"]
    generated = make_benchmark(job["dataset"], n=job["n"], p=job["p"],
                               signals=job["signals"], seed=job["seed"])
    with np.load(directory / "data_and_splits.npz", allow_pickle=False) as f:
        data = {k: f[k] for k in f.files}
    X, y = data["X"], data["y"]
    checks.near("regenerated_X", X, generated.X, key)
    checks.check("regenerated_y", np.array_equal(y, generated.y), key)
    checks.check("reference_panel", np.array_equal(data["reference_panel"], generated.reference_panel), key)
    for split, rows in zip(("discovery", "validation", "test"), split_rows(len(X), job["seed"] + 10000)):
        checks.check("row_split", np.array_equal(data[split], rows), key + split)
    scaler = DiscoveryScaler().fit(X[data["discovery"]])
    stored_predictions = {}
    for name, entry in model_entries(report):
        location = key + ":" + name
        with np.load(directory / (name + "_model.npz"), allow_pickle=False) as f:
            state = {k: f[k] for k in f.files}
        with np.load(directory / (name + "_predictions.npz"), allow_pickle=False) as f:
            saved = {k: f[k] for k in f.files}
        diagnostics = json.loads(str(state["diagnostics_json"]))
        checks.check("model_diagnostics", diagnostics == entry["diagnostics"], location)
        checks.check("panel", state["panel"].tolist() == entry["panel"], location)
        checks.check("panel_size", len(entry["panel"]) == entry["panel_size"], location)
        support = np.flatnonzero(np.linalg.norm(state["transform_matrix"], axis=1) > 1e-12)
        checks.check("exact_support", np.array_equal(support, state["panel"]), location)
        for field in ("median", "mean", "scale"):
            checks.near("discovery_preprocessing", state["scaler_" + field], getattr(scaler, field), location + field)
        reference_rows = diagnostics["reference_indices"]
        checks.near("landmark_projection", scaler.transform(X[data["discovery"]])[reference_rows] @ state["transform_matrix"],
                    state["reference_projection"], location)
        for split in ("discovery", "validation", "test"):
            labels, embedding = predict_saved(X[data[split]], state)
            checks.check("independent_assignment", np.array_equal(labels, saved[split + "_native"]), location + split)
            if split == "discovery":
                checks.check("train_labels", np.array_equal(labels, state["train_labels"]), location)
            if split == "test":
                checks.near("independent_embedding", embedding, saved["test_embedding"], location, 1e-8)
                stored_predictions[name] = labels
            metrics = entry["metrics"][split]
            checks.near("annotation_ari", metrics["ari"], external_ari(y[data[split]], labels), location + split)
            checks.check("child_sizes", counts(labels) == metrics["cluster_sizes"], location + split)
            tree = saved[split + "_tree"]
            checks.near("tree_disagreement", metrics["tree_disagreement"], float(np.mean(tree != labels)), location + split)
            checks.near("tree_fidelity", metrics["tree_fidelity_ari"], ari(tree, labels), location + split)
            checks.near("tree_annotation_ari", metrics["tree_ari"], external_ari(y[data[split]], tree), location + split)
        checks.near("spectral_score", diagnostics["loss"], _spectral_loss(state["reference_projection"],
                    objective=diagnostics["objective"], kernel=diagnostics["kernel"], neighbors=diagnostics["neighbors"])[0], location)
        if name in VARIANTS:
            checks.check("budget", len(entry["panel"]) <= job["budget"], location)
            eligible = [r for r in diagnostics["trace"] if r["valid_checkpoint"]]
            chosen = next(r for r in diagnostics["trace"] if r["restart"] == diagnostics["selected_restart"]
                          and r["iteration"] == diagnostics["selected_iteration"])
            checks.near("checkpoint_selection", chosen["loss"], min(r["loss"] for r in (eligible or diagnostics["trace"])), location)
            checks.near("chosen_loss", diagnostics["loss"], chosen["loss"], location)
            for restart in diagnostics["restarts"]:
                trace = [r["loss"] for r in diagnostics["trace"] if r["restart"] == restart["restart"]]
                checks.check("descent_trace", np.all(np.diff(trace) < 0), location + str(restart["restart"]))
        if generated.reference_kind == "planted" and "planted_recall" in entry:
            overlap = len(set(entry["panel"]) & set(generated.reference_panel))
            checks.near("planted_recall", entry["planted_recall"], overlap / len(generated.reference_panel), location)
            checks.near("planted_precision", entry["planted_precision"], overlap / len(entry["panel"]), location)
    for name, entry in report["models"].items():
        if "same_panel_identity" in entry:
            checks.check("matched_panel", entry["panel"] == entry["same_panel_identity"]["panel"], key + name)
            checks.near("matched_assignment_ari", entry["native_vs_identity_test_ari"],
                        ari(stored_predictions[name], stored_predictions[name + "_identity"]), key + name)
    checks.near("kmeans_all_ari", report["kmeans_all_test_ari"], external_ari(y[data["test"]], data["kmeans_all_test"]), key)
    return len(list(model_entries(report)))


def mean(values):
    values = [x for x in values if x is not None]
    return float(np.mean(values)) if values else None


def aggregate(reports):
    groups = defaultdict(list)
    for report in reports:
        groups[report["case"]["dataset"]].append(report)
    result = {}
    for case, rows in groups.items():
        result[case] = {"cases": len(rows), "variants": {},
                      "kmeans_all_test_ari": mean([r["kmeans_all_test_ari"] for r in rows]),
                      "oracle_graph_test_ari": mean([r["oracle"]["metrics"]["test"]["ari"] for r in rows if r["oracle"]]),
                      "oracle_rule_test_ari": mean([r["oracle"].get("population_rule_test_ari") for r in rows if r["oracle"]])}
        for name in rows[0]["models"]:
            entries = [r["models"][name] for r in rows]
            result[case]["variants"][name] = {
                "test_ari": mean([e["metrics"]["test"]["ari"] for e in entries]),
                "test_ari_each_seed": [e["metrics"]["test"]["ari"] for e in entries],
                "discovery_ari": mean([e["metrics"]["discovery"]["ari"] for e in entries]),
                "identity_test_ari": mean([e.get("same_panel_identity", {}).get("metrics", {}).get("test", {}).get("ari") for e in entries]),
                "centroid_test_ari": mean([e.get("same_panel_centroid_test_ari") for e in entries]),
                "tree_disagreement": mean([e["metrics"]["test"]["tree_disagreement"] for e in entries]),
                "recall": mean([e.get("planted_recall") for e in entries]),
                "sizes": [e["panel_size"] for e in entries],
                "mean_loss": mean([e["diagnostics"]["loss"] for e in entries]),
                "valid_count": sum(e["diagnostics"]["valid"] for e in entries)}
    return result


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("run", type=Path)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args(argv)
    output = args.output or ROOT / ("results/research_kernel_analysis_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
    output.mkdir(parents=True, exist_ok=False)
    manifest, summary = read(args.run / "manifest.json"), read(args.run / "summary.json")
    checks, model_count = Checks(), 0
    checks.check("complete", manifest["status"] == "complete", str(args.run))
    checks.check("case_count", len(manifest["completed"]) == len(manifest["jobs"]) == len(summary["reports"]), str(args.run))
    for name, expected in manifest["source_sha256"].items():
        checks.check("source_hash", (ROOT / name).is_file() and digest(ROOT / name) == expected, name)
    with threadpool_limits(limits=1):
        for job, report in zip(manifest["jobs"], summary["reports"]):
            directory = args.run / job["name"]
            checks.check("report_identity", report == read(directory / "report.json"), job["name"])
            checks.check("job_identity", report["case"] == job, job["name"])
            model_count += audit_case(directory, job, report, checks)
    result = {"source_run": str(args.run.resolve()), "verification": {"checks": sum(checks.counts.values()),
        "categories": dict(checks.counts), "failures": checks.failures, "saved_models": model_count},
        "aggregate": aggregate(summary["reports"]),
        "scope": "Descriptive development audit; no clustering refits; three seeds do not establish superiority. "
                 "Independent replay verifies native predictions and saved tree metrics, not exported tree text or unsaved same-panel centroid models."}
    write_json(output / "analysis.json", result)
    lines = ["# Kernel pilot: verified descriptive results", "", result["scope"], "",
             f"{result['verification']['checks']} checks; {len(checks.failures)} discrepancies; {model_count} saved models.", "",
             "| Case | Variant | Test ARI | Same-panel identity ARI | Recall | Tree disagreement | Sizes |",
             "|---|---|---:|---:|---:|---:|---|"]
    fmt = lambda x: "—" if x is None else f"{x:.3f}"
    for case, group in result["aggregate"].items():
        for name, row in group["variants"].items():
            lines.append(f"| {case} | {name} | {fmt(row['test_ari'])} | {fmt(row['identity_test_ari'])} | "
                         f"{fmt(row['recall'])} | {fmt(row['tree_disagreement'])} | {row['sizes']} |")
    (output / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["verification"], indent=2))
    print(output)
    if checks.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
