"""Hold pilot candidate banks fixed; compare global and size-adjusted ranking.

This is development reanalysis of already inspected pilot splits, not untouched
confirmation. New reference panels set ranking units and NEVER enter candidates.
No reference labels are used in calibration or winner selection.
"""
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
import argparse
import hashlib
import json
from math import comb
import sys

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.calibration import SizeReferenceObjective
from atomic_research.experiment import prepare, write_json, compact, fit_and_report
from atomic_research.scoring import score_panel
from atomic_research.search import FrozenObjective


def reference_panels(p, sizes, per_size, seed):
    rng = np.random.default_rng(seed)
    panels = []
    for size in sorted(sizes):
        target = min(per_size, comb(p, size))
        seen = set()
        for _ in range(max(100, target * 100)):
            seen.add(tuple(sorted(rng.choice(p, size, replace=False).tolist())))
            if len(seen) == target:
                break
        if len(seen) != target:
            raise RuntimeError(f"Could not sample {target} unique size-{size} reference panels")
        panels.extend(sorted(seen))
    return panels


def pick(records, objective):
    eligible = [r for r in records if FrozenObjective.eligible(r)]
    if not eligible:
        return None
    return min(eligible, key=lambda r: (-objective(r), len(r["panel"]), tuple(r["panel"])))


def read_pilot(source):
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest["status"] != "complete" or manifest["config"]["mode"] != "search":
        raise ValueError(f"{source.name} is not a completed search run")
    changed = [p for p, h in manifest["source_sha256"].items()
               if not (ROOT / p).exists() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    if changed:
        raise ValueError(f"Recorded pilot code changed: {changed}; audit before replay")
    protocol = json.loads((source / "data_protocol.json").read_text())
    return manifest, protocol, json.loads((source / "summary.json").read_text())


def run_case(source, output, args):
    manifest, protocol, pilot = read_pilot(source)
    config = SimpleNamespace(**manifest["config"])
    directory = output / f"{config.dataset}_seed{config.seed}"
    directory.mkdir(exist_ok=False)
    dataset, indices, scaler, (Xtrain, Xval, Xtest) = prepare(config)
    train, val, test = indices
    expected = tuple(np.asarray(protocol["rows"][key]) for key in ("discovery", "validation", "test"))
    if not all(np.array_equal(a, b) for a, b in zip(indices, expected)):
        raise ValueError("Reconstructed row split differs from saved pilot")
    for key, value in scaler.to_dict().items():
        if not np.allclose(value, protocol["preprocessing"][key], rtol=1e-12, atol=1e-12):
            raise ValueError("Reconstructed preprocessing differs from saved pilot")
    if dataset.metadata.get("source") != protocol["metadata"].get("source"):
        raise ValueError("Raw data source hash differs from saved pilot")
    write_json(directory / "data_protocol.json", protocol)
    banks = {method: [json.loads(line) for line in (source / f"{method}_candidates.jsonl").read_text().splitlines()]
             for method in pilot["methods"]}
    sizes = {len(r["panel"]) for rows in banks.values() for r in rows if FrozenObjective.eligible(r)}
    if not sizes:
        raise ValueError("No eligible pilot candidates")
    reference_started = perf_counter()
    references = []
    panels = reference_panels(Xtrain.shape[1], sizes, args.reference_per_size, config.seed + 910000)
    print(f"  {config.dataset} seed {config.seed}: {len(panels)} new reference panels", flush=True)
    for i, panel in enumerate(panels, 1):
        references.append(score_panel(Xtrain, panel, seed=config.seed, splitter=config.splitter, k=config.k))
        if i % 40 == 0:
            print(f"    reference scores {i}/{len(panels)}", flush=True)
    fresh_global = FrozenObjective(references)
    centered = SizeReferenceObjective(references, scale_mode="pooled", min_count=args.min_reference_count)
    standardized = SizeReferenceObjective(references, scale_mode="within", min_count=args.min_reference_count)
    unsupported = {len(r["panel"]) for rows in banks.values() for r in rows
                   if FrozenObjective.eligible(r) and not standardized.eligible(r)}
    if unsupported:
        write_json(directory / "unsupported_sizes.json", standardized.diagnostics)
        raise ValueError(f"Insufficient valid references for sizes {sorted(unsupported)}; increase --reference-per-size")
    reference_seconds = perf_counter() - reference_started
    write_json(directory / "reference_scores.json", {"records": [compact(r) for r in references],
               "seconds": reference_seconds, "global_moments": fresh_global.moments,
               "centered": centered.diagnostics, "standardized": standardized.diagnostics})
    policies = {"pilot_global": lambda r: r["objective"], "new_global": fresh_global,
                "size_centered": centered, "size_standardized": standardized}
    report = {"source_run": source.name, "dataset": config.dataset, "seed": config.seed,
              "status": "development_reanalysis_not_independent_confirmation",
              "new_reference_evaluations": len(references), "new_reference_seconds": reference_seconds,
              "candidate_banks_unchanged": True, "methods": {}}
    fit_cache = {}
    for method, records in banks.items():
        # Decide ALL winners before consulting external annotations in reporting.
        winners = {name: pick(records, objective) for name, objective in policies.items()}
        if list(winners["pilot_global"]["panel"]) != pilot["methods"][method]["panel"]:
            raise AssertionError("Pilot winner failed exact replay")
        report["methods"][method] = {}
        for name, chosen in winners.items():
            panel = tuple(chosen["panel"])
            if panel not in fit_cache:
                record = score_panel(Xtrain, panel, seed=config.seed, splitter=config.splitter, k=config.k)
                if not all(np.isclose(record[k], chosen[k], rtol=1e-8, atol=1e-8)
                           for k in ("graphcut", "density", "legacy_graphcut", "legacy_density")):
                    raise AssertionError("Cached candidate score failed replay")
                fit_cache[panel] = record
            record = dict(fit_cache[panel], objective=policies[name](chosen))
            result = fit_and_report(record, Xtrain, Xval, Xtest, dataset.y[train], dataset.y[test],
                                    dataset, config, directory, f"{method}_{name}")
            result["development_reanalysis"] = True
            result["selected_objective"] = policies[name](chosen)
            result["unchanged_candidate_count"] = len(records)
            result["best_visited_train_ari"] = pilot["methods"][method]["best_visited_train_ari"]
            result["training_selection_regret"] = result["best_visited_train_ari"] - result["train_ari"]
            if name == "pilot_global":
                for key in ("train_ari", "test_transfer_ari", "test_compression_fidelity"):
                    if not np.isclose(result[key], pilot["methods"][method][key]):
                        raise AssertionError(f"Pilot baseline result failed replay: {key}")
            report["methods"][method][name] = result
        write_json(directory / "summary.partial.json", report)
    write_json(directory / "summary.json", report)
    return report


def write_report(output, reports):
    lines = ["# Fixed-candidate ranking followup", "",
        "Development reanalysis of inspected pilot data. Candidate banks and clustering partitions are held fixed for ranking; new random reference panels never enter the candidate bank. Labels enter only reporting. Test-split results below are no longer independent confirmation of this newly designed strategy.", "",
        "pilot_global: original pilot score; new_global: larger common reference bank; size_centered: size-specific means with common within-size scales; size_standardized: size-specific means and scales. None is a cluster-existence test.", "",
        "| Dataset | Seed | Proposals | Ranking | Size | Train ARI | Training selection regret | Development test ARI |",
        "|---|---:|---|---|---:|---:|---:|---:|"]
    for report in reports:
        for method, policies in report["methods"].items():
            for name, row in policies.items():
                lines.append(f"| {report['dataset']} | {report['seed']} | {method} | {name} | {len(row['panel'])} | "
                    f"{row['train_ari']:.3f} | {row['training_selection_regret']:.3f} | {row['test_transfer_ari']:.3f} |")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot-root", type=Path, default=ROOT / "results/research_diagnostics")
    cli.add_argument("--datasets", nargs="+", default=["mean_shift", "metabric"])
    cli.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    cli.add_argument("--reference-per-size", type=int, default=24)
    cli.add_argument("--min-reference-count", type=int, default=8)
    cli.add_argument("--output", type=Path, default=ROOT / "results/research_ranking_followup")
    args = cli.parse_args()
    if args.reference_per_size < args.min_reference_count or args.min_reference_count < 2:
        cli.error("Need reference-per-size >= min-reference-count >= 2")
    sources, keys = [], set()
    for path in sorted(args.pilot_root.glob("*/manifest.json")):
        m = json.loads(path.read_text())
        c = m["config"]
        if m["status"] == "complete" and c["mode"] == "search" and c["dataset"] in args.datasets and c["seed"] in args.seeds:
            key = (c["dataset"], c["seed"])
            if key in keys:
                cli.error(f"Multiple runs match {key}; use a pilot root with a single intended run per case")
            keys.add(key)
            sources.append(path.parent)
    missing = {(case, seed) for case in args.datasets for seed in args.seeds} - keys
    if missing:
        cli.error(f"Missing completed source runs: {sorted(missing)}")
    output = args.output / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    manifest = {"status": "running", "config": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
        "scope": "post-pilot development reanalysis", "source_runs": [p.name for p in sources],
        "followup_sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__), ROOT / "atomic_research/calibration.py")}}
    write_json(output / "manifest.json", manifest)
    print(f"{len(sources)} fixed-candidate runs. Results: {output}", flush=True)
    reports = []
    try:
        with threadpool_limits(limits=1):
            for source in sources:
                reports.append(run_case(source, output, args))
                write_report(output, reports)
        manifest.update(status="complete", seconds=perf_counter() - started)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
                        error=f"{type(exc).__name__}: {exc}", seconds=perf_counter() - started)
        raise
    finally:
        write_json(output / "manifest.json", manifest)
    print(output / "summary.md", flush=True)


if __name__ == "__main__":
    main()
