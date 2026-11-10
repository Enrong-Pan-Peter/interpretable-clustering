"""Audit and aggregate a completed pilot without changing its run folders."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]


def stats(values):
    values = [v for v in values if v is not None]
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "min": min(values) if values else None, "max": max(values) if values else None}


def analyze(root):
    groups, sources, cases, references, score_audits = defaultdict(list), [], [], [], []
    failures, signatures = [], set()
    seconds = 0
    for path in sorted(root.glob("*/manifest.json")):
        manifest = json.loads(path.read_text())
        mismatches = [str(p) for p, h in manifest["source_sha256"].items()
                      if not (ROOT / p).exists() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
        signature = hashlib.sha256(json.dumps(manifest["source_sha256"], sort_keys=True).encode()).hexdigest()
        signatures.add(signature)
        sources.append({"run": path.parent.name, "status": manifest["status"],
                        "source_signature": signature, "current_source_mismatches": mismatches,
                        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        if manifest["status"] != "complete":
            failures.append(path.parent.name)
            continue
        config = manifest["config"]
        protocol = json.loads(path.with_name("data_protocol.json").read_text())
        indices = [j for section in protocol["rows"].values() for j in section]
        if len(indices) != len(set(indices)):
            raise ValueError(f"Overlapping splits in {path.parent.name}")
        report = json.loads(path.with_name("summary.json").read_text())
        seconds += manifest["total_seconds"]
        cases.append((config["mode"], config["dataset"], config["seed"]))
        if config["mode"] == "score-audit":
            score_audits.append({"dataset": config["dataset"], "run": path.parent.name,
                "candidate_count": report["candidate_count"],
                "results": {name: {"panel_size": len(r.get("panel", [])), "test_ari": r.get("test_transfer_ari"),
                            "origin_note": "reference-augmented bank, not discovery"} for name, r in report["objectives"].items()}})
        if config["mode"] != "search":
            continue
        reference = report.get("reference_panel_diagnostic_not_search_seed", {})
        references.append({"dataset": config["dataset"], "seed": config["seed"],
                           "train_ari": reference.get("train_ari"), "test_ari": reference.get("test_transfer_ari")})
        truth = set(protocol["reference_panel"])
        for method, result in report["methods"].items():
            rows = [json.loads(line) for line in (path.parent / f"{method}_candidates.jsonl").read_text().splitlines()]
            eligible = [r for r in rows if r["valid"] and r["legacy_valid"]]
            exact_rank = None
            if protocol["reference_kind"] == "planted":
                ranked = sorted(eligible, key=lambda r: (-r["objective"], len(r["panel"]), r["panel"]))
                exact_rank = next((i+1 for i, r in enumerate(ranked) if set(r["panel"]) == truth), None)
            groups[(config["dataset"], method)].append({"run": path.parent.name, "seed": config["seed"],
                "train_ari": result.get("train_ari"), "best_visited_train_ari": result.get("best_visited_train_ari"),
                "selection_regret": result.get("training_selection_regret"),
                "test_ari": result.get("test_transfer_ari"), "reduced_test_ari": result.get("test_reduced_transfer_ari"),
                "compression_fidelity": result.get("test_compression_fidelity"),
                "selected_size": len(result.get("panel", [])), "reduced_size": len(result.get("reduced_panel", [])),
                "reference_recall": result.get("reference", {}).get("reference_recall"),
                "exact_planted_panel_rank": exact_rank, "unique_candidates": len(rows),
                "search_seconds": result["accounting"]["total_seconds"],
                "features": result.get("feature_names"), "reduced_features": result.get("reduced_feature_names")})
    expected = [("null-audit", case, 0) for case in ("null_independent", "null_correlated", "bimodal")]
    expected += [("score-audit", case, 0) for case in ("mean_shift", "shells", "metabric", "levine")]
    expected += [("search", case, seed) for case in ("mean_shift", "shells", "metabric", "levine") for seed in range(3)]
    counts = Counter(cases)
    metrics = ("train_ari", "best_visited_train_ari", "selection_regret", "test_ari", "reduced_test_ari",
               "compression_fidelity", "selected_size", "reduced_size", "reference_recall", "unique_candidates", "search_seconds")
    aggregates = [{"dataset": key[0], "method": key[1], "runs": rows,
                   "statistics": {metric: stats([r[metric] for r in rows]) for metric in metrics}}
                  for key, rows in sorted(groups.items())]
    return {"completed_jobs": len(cases), "failed_or_incomplete": failures,
            "missing_default_pilot_jobs": [case for case in expected if case not in counts],
            "duplicate_jobs": [case for case, count in counts.items() if count > 1],
            "source_signature_count": len(signatures), "summed_job_seconds": seconds,
            "sources": sources, "aggregates": aggregates, "references": references, "score_audits": score_audits,
            "scope": "Descriptive three-seed development experiment; no independent-cohort or novelty claim"}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=ROOT / "results/research_diagnostics")
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_pilot_analysis_20260915")
    args = cli.parse_args()
    report = analyze(args.root)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "analysis.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Pilot audit and aggregates", "",
        f"Completed jobs: {report['completed_jobs']}; source hash configurations: {report['source_signature_count']}; summed job time: {report['summed_job_seconds']:.1f}s.", "",
        "All numbers below are descriptive across three seeds. Same-method test ARI means transferred discovery labels. Candidate generation and scalar selection had no access to reference labels. Best-visited ARI is retrospective and training-only.", "",
        "| Dataset | Method | Mean test ARI [range] | Mean best-visited train ARI | Mean selected train ARI | Mean panel size | Mean candidates | Mean search seconds |",
        "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group in report["aggregates"]:
        s = group["statistics"]
        ari = s["test_ari"]
        lines.append(f"| {group['dataset']} | {group['method']} | {ari['mean']:.3f} [{ari['min']:.3f}, {ari['max']:.3f}] | "
                     f"{s['best_visited_train_ari']['mean']:.3f} | {s['train_ari']['mean']:.3f} | {s['selected_size']['mean']:.1f} | "
                     f"{s['unique_candidates']['mean']:.1f} | {s['search_seconds']['mean']:.2f} |")
    lines += ["", "## Compression failures on confirmation rows", "",
              "Validation required ARI >= .95 to the full-panel rule. The following accepted reductions fell below .95 on test rows; this is not a 95% point-agreement requirement.", "",
              "| Dataset | Method | Seed | Test compression fidelity | Full → reduced test label ARI |", "|---|---|---:|---:|---:|"]
    for group in report["aggregates"]:
        for row in group["runs"]:
            if row["reduced_size"] < row["selected_size"] and row["compression_fidelity"] < .95:
                lines.append(f"| {group['dataset']} | {group['method']} | {row['seed']} | {row['compression_fidelity']:.3f} | "
                             f"{row['test_ari']:.3f} → {row['reduced_test_ari']:.3f} |")
    lines += ["", "## Integrity", "",
              f"Missing default pilot cases: {report['missing_default_pilot_jobs']}",
              f"Duplicate cases: {report['duplicate_jobs']}", f"Failed or incomplete: {report['failed_or_incomplete']}",
              f"Runs with current source mismatches: {sum(bool(r['current_source_mismatches']) for r in report['sources'])}", "",
              "The JSON includes per-run manifests and source checks. New analysis modules are not part of the historical manifest; edits to recorded modules would be reported as mismatches.", ""]
    (args.output / "analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print(args.output / "analysis.md")


if __name__ == "__main__":
    main()
