"""Collect completed diagnostic runs without modifying individual results."""
from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", default="results/research_diagnostics")
    args = cli.parse_args()
    directory = Path(args.root)
    if not directory.is_absolute():
        directory = ROOT / directory
    rows, nulls, failures = [], [], []
    for path in sorted(directory.glob("*/manifest.json")):
        manifest = json.loads(path.read_text())
        if manifest["status"] != "complete":
            failures.append((path.parent.name, manifest["status"]))
            continue
        config = manifest["config"]
        report = json.loads(path.with_name("summary.json").read_text())
        protocol = json.loads(path.with_name("data_protocol.json").read_text())
        if config["mode"] == "null-audit":
            nulls.append((config["dataset"], config["seed"], report["graphcut_independence_null"]["p_value"],
                          report["correlation_independence_null"]["p_value"]))
            continue
        for name, result in report.get("methods", report.get("objectives", {})).items():
            rows.append({"run": path.parent.name, "mode": config["mode"], "dataset": config["dataset"],
                         "contrast": protocol["metadata"].get("contrast", ""), "p": len(protocol["features"]),
                         "signal_features": config["signal_features"] if config["dataset"] not in ("metabric", "levine", "mice") else "",
                         "seed": config["seed"], "method": name, "objective": config["objective"] if config["mode"] == "search" else name,
                         "selected_size": len(result.get("panel", [])), "reduced_size": len(result.get("reduced_panel", [])),
                         "train_ari": result.get("train_ari"), "best_visited_train_ari": result.get("best_visited_train_ari"),
                         "selection_regret": result.get("training_selection_regret"),
                         "test_ari": result.get("test_transfer_ari"), "test_reduced_ari": result.get("test_reduced_transfer_ari"),
                         "compression_fidelity": result.get("test_compression_fidelity"),
                         "reference_recall": result.get("reference", {}).get("reference_recall"),
                         "search_seconds": result.get("accounting", {}).get("total_seconds"),
                         "budget": config["budget"], "max_features": config["max_features"],
                         "n": len(protocol["rows"]["discovery"]) + len(protocol["rows"]["validation"]) + len(protocol["rows"]["test"]),
                         "status": result["status"]})
    directory.mkdir(parents=True, exist_ok=True)
    if rows:
        with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    def fmt(value):
        return "—" if value is None else f"{value:.3f}" if isinstance(value, float) else str(value)
    lines = ["# Feature-panel diagnostic results", "",
             "These are prototype diagnostics. Search rows use no reference-panel seeds. Score-audit rows use a reference-augmented bank and must not be reported as discovery performance.", "",
             "Test ARI below measures transferred discovery assignments. Search seconds include proposal optimization and panel scoring; shared reference setup and post-selection reporting are additional. Budgets do not imply equal compute.", "",
             "| Case | Mode | p | s | Seed | Method / objective | Size → reduced | Best visited train ARI | Selected train ARI | Test ARI | Reduced test ARI | Search seconds |",
             "|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append("| " + " | ".join(fmt(x) for x in [row["dataset"] + (":" + row["contrast"] if row["contrast"] else ""),
            row["mode"], row["p"], row["signal_features"], row["seed"], row["method"] + "/" + row["objective"],
            f"{row['selected_size']} → {row['reduced_size']}", row["best_visited_train_ari"], row["train_ari"], row["test_ari"], row["test_reduced_ari"], row["search_seconds"]]) + " |")
    if nulls:
        lines += ["", "## Fixed-panel dependence controls", "", "Both p-values concern independence, not the absence of clusters.", "",
                  "| Case | Seed | Graphcut independence p | Correlation independence p |", "|---|---:|---:|---:|"]
        lines += ["| " + " | ".join(fmt(x) for x in row) + " |" for row in nulls]
    if failures:
        lines += ["", "Incomplete or failed runs: " + ", ".join(f"{name} ({status})" for name, status in failures)]
    lines += ["", "Inspect each run's candidate records, reference diagnostics, rule fidelity and manifest before drawing conclusions. Seed-to-seed variation is not independent cohort replication.", ""]
    (directory / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(directory / "summary.md")


if __name__ == "__main__":
    main()
