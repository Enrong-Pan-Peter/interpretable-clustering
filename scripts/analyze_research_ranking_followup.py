"""Read-only replay/accounting audit of a saved fixed-candidate ranking followup.

Recomputes ranking arithmetic from saved candidates and reference scores, never
fits clusters or edits results. Prints JSON for reproducible descriptive review.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.calibration import SizeReferenceObjective
from atomic_research.search import FrozenObjective

POLICIES = ("pilot_global", "new_global", "size_centered", "size_standardized")
TOLERANCE = 1e-9


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def assert_close(actual, expected, context):
    if actual is None or expected is None:
        if actual is not expected:
            raise AssertionError(f"{context}: {actual} != {expected}")
    elif not np.isclose(actual, expected, rtol=1e-9, atol=1e-10):
        raise AssertionError(f"{context}: {actual} != {expected}")


def check_hashes(hashes):
    mismatches = []
    for relative, digest in hashes.items():
        path = ROOT.joinpath(*relative.replace("\\", "/").split("/"))
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            mismatches.append(relative)
    return mismatches


def aggregate(rows):
    return {
        "n": len(rows),
        **{key: float(np.mean([r[key] for r in rows])) for key in (
            "train_ari", "test_transfer_ari", "training_selection_regret",
            "test_compression_fidelity")},
        "panel_size": float(np.mean([len(r["panel"]) for r in rows])),
        "reduced_size": float(np.mean([len(r["reduced_panel"]) for r in rows])),
    }


def paired_counts(pairs, key, improvement_sign):
    delta = np.asarray([improvement_sign * (new[key] - old[key]) for old, new in pairs])
    return {"improved": int(np.count_nonzero(delta > TOLERANCE)),
            "worse": int(np.count_nonzero(delta < -TOLERANCE)),
            "tied": int(np.count_nonzero(np.abs(delta) <= TOLERANCE)),
            "mean_signed_improvement": float(delta.mean()),
            "changed_panel": sum(old["panel"] != new["panel"] for old, new in pairs)}


def audit(directory):
    manifest = read(directory / "manifest.json")
    if manifest["status"] != "complete":
        raise AssertionError("Followup is not complete")
    config = manifest["config"]
    expected = {(case, seed) for case in config["datasets"] for seed in config["seeds"]}
    # The saved absolute path is provenance; resolve its repository location here.
    pilot_root = Path(config["pilot_root"])
    if not pilot_root.exists():
        pilot_root = ROOT / "results/research_diagnostics"
    hash_issues = {"followup": check_hashes(manifest["followup_sources"])}
    grouped, paired, details = defaultdict(list), defaultdict(list), []
    reference_count, candidate_count, winner_count, baseline_count = 0, 0, 0, 0
    seen = set()
    for path in sorted(directory.glob("*/summary.json")):
        report = read(path)
        key = (report["dataset"], report["seed"])
        if key in seen:
            raise AssertionError(f"Duplicate case {key}")
        seen.add(key)
        source = pilot_root / report["source_run"]
        source_manifest, pilot = read(source / "manifest.json"), read(source / "summary.json")
        if source_manifest["status"] != "complete":
            raise AssertionError(f"Incomplete pilot source {source.name}")
        hash_issues[source.name] = check_hashes(source_manifest["source_sha256"])
        if read(path.with_name("data_protocol.json")) != read(source / "data_protocol.json"):
            raise AssertionError(f"Changed data protocol for {key}")
        refs = read(path.with_name("reference_scores.json"))
        global_score = FrozenObjective(refs["records"])
        centered = SizeReferenceObjective(refs["records"], scale_mode="pooled",
                                          min_count=config["min_reference_count"])
        standardized = SizeReferenceObjective(refs["records"], scale_mode="within",
                                              min_count=config["min_reference_count"])
        if standardized.diagnostics["unsupported_sizes"]:
            raise AssertionError(f"Unsupported reference size in {key}")
        reference_count += len(refs["records"])
        policies = {"pilot_global": lambda r: r["objective"], "new_global": global_score,
                    "size_centered": centered, "size_standardized": standardized}
        for method, outputs in report["methods"].items():
            records = [json.loads(line) for line in (source / f"{method}_candidates.jsonl").read_text().splitlines()]
            eligible = [r for r in records if FrozenObjective.eligible(r)]
            candidate_count += len(records)
            best_visited = max(r["diagnostic_train_ari"] for r in eligible)
            for policy, objective in policies.items():
                chosen = min(eligible, key=lambda r: (-objective(r), len(r["panel"]), tuple(r["panel"])))
                row = outputs[policy]
                if chosen["panel"] != row["panel"]:
                    raise AssertionError(f"Winner mismatch {key}/{method}/{policy}")
                if row["unchanged_candidate_count"] != len(records):
                    raise AssertionError("Changed candidate count")
                assert_close(row["selected_objective"], objective(chosen), "selected objective")
                assert_close(row["train_ari"], chosen["diagnostic_train_ari"], "training ARI")
                assert_close(row["best_visited_train_ari"], best_visited, "best visited ARI")
                assert_close(row["training_selection_regret"], best_visited-row["train_ari"], "regret")
                if policy == "pilot_global":
                    for metric in ("train_ari", "test_transfer_ari", "test_compression_fidelity"):
                        assert_close(row[metric], pilot["methods"][method][metric], "pilot replay " + metric)
                    baseline_count += 1
                grouped[(key[0], "all_methods", policy)].append(row)
                grouped[(key[0], method, policy)].append(row)
                if policy != "pilot_global":
                    paired[(key[0], policy)].append((outputs["pilot_global"], row))
                    paired[("all_datasets", policy)].append((outputs["pilot_global"], row))
                winner_count += 1
            details.append({"dataset": key[0], "seed": key[1], "method": method,
                            "policies": {p: {"panel": r["panel"], "train_ari": r["train_ari"],
                                "test_ari": r["test_transfer_ari"], "regret": r["training_selection_regret"]}
                                for p,r in outputs.items()}})
    if seen != expected:
        raise AssertionError(f"Case mismatch: expected {expected}, found {seen}")
    return {"verification": {"cases": len(seen), "baselines_replayed": baseline_count,
                "policy_winners_checked": winner_count, "pilot_candidates_checked": candidate_count,
                "new_reference_records": reference_count, "source_hash_mismatches": hash_issues,
                "fit_reexecuted": False, "completed_seconds": manifest["seconds"]},
            "aggregates": [{"dataset": c, "method": m, "policy": p, **aggregate(rows)}
                            for (c,m,p),rows in sorted(grouped.items())],
            "paired_changes": [{"dataset": c,"policy": p,
                "training_regret": paired_counts(pairs, "training_selection_regret", -1),
                "development_test_ari": paired_counts(pairs, "test_transfer_ari", 1)}
                for (c,p),pairs in sorted(paired.items())],
            "details": details,
            "scope": "descriptive reanalysis of reused development splits; no new confirmation or significance claim"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path,
                        nargs="?", default=ROOT / "results/research_ranking_followup/20260916T025613_491524Z")
    args = parser.parse_args()
    print(json.dumps(audit(args.directory), indent=2, allow_nan=False))
