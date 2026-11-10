"""Audit saved obstacle-suite outputs without refitting any clustering model.

Original files are read-only. Outputs are descriptive arithmetic/state checks,
not significance tests, certification of the method, or test-ARI selection.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
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
from atomic_research.experiment import prepare


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ari(a, b):
    """Independent contingency-table ARI; does not call the production metric."""
    a, b = np.asarray(a), np.asarray(b)
    if len(a) != len(b):
        raise ValueError("ARI length mismatch")
    n = len(a)
    if n < 2:
        return 1.0
    _, x = np.unique(a, return_inverse=True)
    _, y = np.unique(b, return_inverse=True)
    nrows, ncols = int(x.max()+1), int(y.max()+1)
    table = np.bincount(x * ncols + y, minlength=nrows*ncols).reshape(nrows, ncols)
    choose2 = lambda t: float(np.sum(t * (t - 1) // 2))
    together, aa, bb = choose2(table), choose2(table.sum(1)), choose2(table.sum(0))
    expected = aa * bb / (n * (n - 1) / 2)
    denominator = (aa + bb) / 2 - expected
    return 1.0 if denominator == 0 else (together - expected) / denominator


def external_ari(y, prediction):
    return None if prediction is None or len(np.unique(y)) < 2 else ari(y, prediction)


def counts(values):
    return [] if values is None else np.bincount(np.asarray(values, dtype=int), minlength=2).tolist()


class Checks:
    def __init__(self):
        self.counts = Counter()
        self.failures = []

    def check(self, category, condition, location):
        self.counts[category] += 1
        if not condition:
            self.failures.append({"category": category, "location": location})

    def near(self, category, actual, expected, location, tolerance=1e-10):
        okay = actual is expected if actual is None or expected is None else np.allclose(
            actual, expected, rtol=tolerance, atol=tolerance, equal_nan=False)
        self.check(category, bool(okay), location)


def verify_code_hashes(mapping, checks, prefix):
    for name, expected in mapping.items():
        path = ROOT / name
        checks.check("source_hash", path.is_file() and digest(path) == expected, prefix + ":" + name)


def reconstruct(config, protocol, checks, location):
    dataset, indices, scaler, arrays = prepare(SimpleNamespace(**config))
    for role, actual in zip(("discovery", "validation", "test"), indices):
        checks.check("row_reconstruction", np.array_equal(actual, protocol["rows"][role]), location + ":" + role)
    for name, value in scaler.to_dict().items():
        checks.near("scaler_reconstruction", value, protocol["preprocessing"][name], location + ":" + name, 1e-12)
    checks.check("feature_names", dataset.names == protocol["features"], location)
    checks.check("raw_source_identity", dataset.metadata.get("source") == protocol["metadata"].get("source"), location)
    return dataset, indices, arrays


def verify_fidelity(saved, target, predicted, checks, location, align=False):
    expected_ari = None if target is None or predicted is None else ari(target, predicted)
    error = None if target is None or predicted is None else float(np.mean(np.asarray(target) != np.asarray(predicted)))
    if align and error is not None:
        error = min(error, 1-error)
    checks.near("fidelity_ari", saved["ari"], expected_ari, location)
    checks.near("fidelity_disagreement", saved["disagreement"], error, location)
    if target is not None and predicted is not None:
        optional = {
            "changed_assignments": int(np.count_nonzero(np.asarray(target) != np.asarray(predicted))),
            "n": len(target), "predicted_group_sizes": counts(predicted),
            "nondegenerate": len(np.unique(predicted)) == 2,
        }
        for key, expected in optional.items():
            if key in saved:
                checks.check("fidelity_counts", saved[key] == expected, location + ":" + key)


def native_predict(X, state, representation, panel=None):
    mapped = X if representation == "raw" else X**2
    Z = (mapped - state["transform_mean"]) / state["transform_scale"]
    panel = np.arange(X.shape[1]) if panel is None else np.asarray(panel)
    positive = state["weights"][panel] > 0
    panel = panel[positive]
    distance = np.stack([
        np.sum((Z[:, panel] - state["centers"][k, panel])**2 * state["weights"][panel], axis=1)
        for k in (0, 1)
    ], axis=1)
    return np.argmin(distance, axis=1), Z


def verify_retention(report, directory, config, checks):
    location = directory.name
    protocol = read(directory / "data_protocol.json")
    replay_config = {k: config[k] for k in ("n", "p", "signal_features", "separation")}
    replay_config.update(dataset=report["dataset"], seed=report["seed"], contrast=None)
    data, indices, (Xtrain, _, Xtest) = reconstruct(replay_config, protocol, checks, location)
    ledger = [json.loads(line) for line in (directory / "comparisons.jsonl").read_text().splitlines()]
    checks.check("retention_ledger", ledger == report["rows"], location)
    with np.load(directory / "readout_predictions.npz", allow_pickle=False) as file:
        predictions = {key: file[key] for key in file.files}
    ytrain, ytest = data.y[indices[0]], data.y[indices[2]]
    full = {(r["representation"], r["l1_bound"]): r for r in report["rows"] if r["readout"] == "full_native_centroid"}
    states = {}
    for representation in ("raw", "squared"):
        bounds = sorted(bound for rep, bound in full if rep == representation)
        fitted = next(f for f in report["proposal_fits"] if f["representation"] == representation)
        for number, bound in enumerate(bounds):
            row = full[(representation, bound)]
            with np.load(directory / f"{representation}_bound{number}_model.npz", allow_pickle=False) as f:
                state = {key: f[key] for key in f.files}
            states[(representation, bound)] = state
            train_labels, Z = native_predict(Xtrain, state, representation)
            test_labels, _ = native_predict(Xtest, state, representation)
            key = row["prediction_key"]
            for name, calculated, saved in (("train", train_labels, predictions[key + "_train"]),
                                             ("test", test_labels, predictions[key + "_test"]),
                                             ("state_train", train_labels, state["train_labels"])):
                checks.check("frozen_native_prediction", np.array_equal(calculated, saved), location + ":" + key + ":" + name)
            mapped = Xtrain if representation == "raw" else Xtrain**2
            mean, scale = mapped.mean(0), mapped.std(0)
            varying = scale > np.finfo(float).eps * np.maximum(np.abs(mean), scale)
            scale[~varying] = 1.
            checks.near("native_transform", state["transform_mean"], mean, location + key, 1e-12)
            checks.near("native_transform", state["transform_scale"], scale, location + key, 1e-12)
            scores = sum(np.sum(train_labels == k) * (Z[train_labels == k].mean(0) - Z.mean(0))**2 for k in (0, 1))
            checks.near("native_objective", row["native_objective"], scores @ state["weights"], location + key)
            checks.check("native_support", row["full_active_features"] == int(np.count_nonzero(state["weights"] > 0)), location + key)
            checks.check("native_weight_constraints", np.linalg.norm(state["weights"]) <= 1+1e-10 and state["weights"].sum() <= bound+1e-10 and np.all(state["weights"] >= 0), location + key)
            final = [t for t in fitted["diagnostics"]["trace"] if t["stage"] == "final_retained_model" and t["l1_bound"] == bound]
            checks.near("native_restart_selection", row["native_objective"], max(t["native_objective"] for t in final), location + key)
    used_keys = set()
    for row in report["rows"]:
        key, group = row["prediction_key"], (row["representation"], row["l1_bound"])
        train_labels, test_labels = predictions.get(key + "_train"), predictions.get(key + "_test")
        used_keys.update(k for k in (key + "_train", key + "_test") if k in predictions)
        train_sizes, test_sizes = counts(train_labels), counts(test_labels)
        valid = len(train_sizes) == 2 and min(train_sizes) >= 5
        checks.check("prediction_group_counts", train_sizes == row["training_cluster_sizes"] and test_sizes == row["test_cluster_sizes"], location + key)
        checks.check("prediction_validity", valid == row["valid_training_partition"], location + key)
        checks.near("external_ari", row["train_ari"], external_ari(ytrain, train_labels) if valid else None, location + key + ":train")
        checks.near("external_ari", row["test_ari"], external_ari(ytest, test_labels) if valid else None, location + key + ":test")
        reference = predictions[full[group]["prediction_key"] + "_test"]
        verify_fidelity(row["test_fidelity_to_full_native"], reference, test_labels, checks, location + key, align=True)
        if row["prefix_size"] is not None:
            expected = sorted(states[group]["ranking"][:row["prefix_size"]].tolist())
            checks.check("prefix_ranking", expected == row["panel"], location + key)
        if row["readout"] == "truncated_native_centroid":
            for name, values, saved in (("train", Xtrain, train_labels), ("test", Xtest, test_labels)):
                calculated, _ = native_predict(values, states[group], row["representation"], row["panel"])
                checks.check("frozen_truncated_prediction", np.array_equal(calculated, saved), location + key + ":" + name)
    checks.check("prediction_key_coverage", used_keys == set(predictions), location)


def verify_compression(report, directory, checks):
    source = Path(report["source_run"])
    old_manifest, old_summary = read(source / "manifest.json"), read(source / "summary.json")
    verify_code_hashes(old_manifest["source_sha256"], checks, directory.name)
    protocol = read(directory / "data_protocol.json")
    data, indices, (Xtrain, _, _) = reconstruct(old_manifest["config"], protocol, checks, directory.name)
    ytrain, ytest = data.y[indices[0]], data.y[indices[2]]
    for method in report["methods"]:
        audit = read(directory / f"{method}_deletions.json")
        where = directory.name + ":" + method
        assignment_path = source / f"{method}_assignment.npz"
        checks.check("pilot_assignment_hash", digest(assignment_path) == audit["source_assignment_sha256"], where)
        ref = audit["reference"]
        reference_train = np.asarray(ref["training_labels"])
        reference_val, reference_test = np.asarray(ref["validation_predictions"]), np.asarray(ref["test_predictions"])
        with np.load(assignment_path, allow_pickle=False) as state:
            _, encoded = np.unique(state["labels"], return_inverse=True)
            checks.check("pilot_teacher_partition", np.array_equal(reference_train, encoded), where)
            checks.check("pilot_teacher_panel", state["original_panel"].tolist() == audit["original_panel"], where)
            checks.near("pilot_teacher_data", state["original_X"], Xtrain[:, audit["original_panel"]], where)
        checks.near("pilot_teacher_external_ari", external_ari(ytest, reference_test), old_summary["methods"][method]["test_transfer_ari"], where)
        folds = [np.asarray(fold, dtype=int) for fold in audit["validation_fold_indices"]]
        checks.check("validation_fold_coverage", sorted(np.concatenate(folds).tolist()) == list(range(len(reference_val))), where)
        bank = {(c["family"], tuple(c["panel"])): c for c in audit["evaluated_candidates"]}
        for (family, panel), candidate in bank.items():
            loc = where + ":" + family + ":" + str(panel)
            for field, target, predicted in (
                ("training_fidelity", reference_train, candidate["training_labels"]),
                ("training_prediction_fidelity", reference_train, candidate["training_predictions"]),
                ("validation_fidelity", reference_val, candidate["validation_predictions"]),
                ("test_fidelity", reference_test, candidate["test_predictions"]),
            ):
                verify_fidelity(candidate[field], target, predicted, checks, loc + ":" + field)
            for fold, saved in zip(folds, candidate["validation_folds"]):
                verify_fidelity(saved, reference_val[fold], np.asarray(candidate["validation_predictions"])[fold], checks, loc + ":fold")
            maximum = max(float(np.mean(reference_val[f] != np.asarray(candidate["validation_predictions"])[f])) for f in folds)
            checks.near("fold_maximum", candidate["max_fold_disagreement"], maximum, loc)
            valid = len(np.unique(candidate["training_labels"])) == 2 and not candidate["orientation_tied"] and len(np.unique(candidate["validation_predictions"])) == 2
            fold_valid = valid and all(len(np.unique(np.asarray(candidate["validation_predictions"])[f])) == 2 for f in folds)
            checks.check("compression_validity", candidate["selection_valid"] == valid and candidate["fold_selection_valid"] == fold_valid, loc)
            checks.near("compression_external_ari", candidate["external_train_ari"], external_ari(ytrain, candidate["training_labels"]), loc + ":train")
            checks.near("compression_external_ari", candidate["external_test_ari"], external_ari(ytest, candidate["test_predictions"]), loc + ":test")
        for policy_name, policy in audit["policies"].items():
            loc = where + ":" + policy_name
            current = list(audit["original_panel"])
            for step in policy["trace"]:
                checks.check("deletion_path", current == step["from_panel"] and sorted(set(current) - {step["removed"]}) == step["candidate"], loc)
                choices = []
                for removed in current:
                    candidate_panel = tuple(j for j in current if j != removed)
                    candidate = bank[(policy["model_family"], candidate_panel)]
                    criterion = policy["criterion"]
                    valid = candidate["fold_selection_valid"] if criterion == "foldwise" else candidate["selection_valid"]
                    if criterion == "ari":
                        rank = (-candidate["validation_fidelity"]["ari"], candidate_panel)
                        accept = valid and candidate["validation_fidelity"]["ari"] >= audit["settings"]["ari_threshold"]
                    elif criterion == "foldwise":
                        rank = (candidate["max_fold_disagreement"], candidate["validation_fidelity"]["disagreement"], candidate_panel)
                        accept = valid and candidate["max_fold_disagreement"] <= audit["settings"]["max_disagreement"]
                    else:
                        rank = (candidate["validation_fidelity"]["disagreement"], candidate_panel)
                        accept = valid and candidate["validation_fidelity"]["disagreement"] <= audit["settings"]["max_disagreement"]
                    choices.append((not valid, rank, accept, removed, candidate_panel))
                winner = min(choices, key=lambda x: (x[0], x[1]))
                checks.check("deletion_selection", step["removed"] == winner[3] and step["accepted"] == winner[2], loc)
                if step["accepted"]:
                    current = list(step["candidate"])
            checks.check("selected_panel", current == policy["selected_panel"] == policy["selected_model"]["panel"], loc)
            selected = bank[(policy["model_family"], tuple(current))]
            for key in ("training_labels", "validation_predictions", "test_predictions"):
                checks.check("selected_candidate_state", selected[key] == policy["selected_model"][key], loc + ":" + key)
            matching = [r for r in report["rows"] if r["method"] == method and r["policy"] == policy_name]
            checks.check("compression_row_coverage", len(matching) == 1, loc)
            if matching:
                row = matching[0]
                checks.check("compression_summary_panel", row["selected_panel"] == current, loc)
                checks.near("compression_summary_ari", row["selected_test_ari"], selected["external_test_ari"], loc)


def statistics(values):
    values = [float(v) for v in values if v is not None and np.isfinite(v)]
    return {"n": len(values), "mean": float(np.mean(values)) if values else None,
            "sd": float(np.std(values, ddof=1)) if len(values) > 1 else None,
            "min": min(values) if values else None, "max": max(values) if values else None}


def aggregate_models(reports, stage):
    groups = defaultdict(list)
    for report in reports:
        if report["stage"] != stage:
            continue
        for row in report["rows"]:
            if row["prefix_size"] in (None, 5, 8):
                groups[(report["dataset"], row["representation"], row["l1_bound"], row["prefix_size"], row["readout"])].append(row)
    result = []
    for key, rows in groups.items():
        dataset, representation, bound, prefix, readout = key
        result.append({"dataset": dataset, "representation": representation, "l1_bound": bound,
            "prefix_size": prefix, "readout": readout, "cases": len(rows),
            "valid_training_cases": sum(r["valid_training_partition"] for r in rows),
            "test_ari": statistics([r["test_ari"] for r in rows]),
            "native_fidelity_ari": statistics([r["test_fidelity_to_full_native"]["ari"] for r in rows]),
            "native_disagreement": statistics([r["test_fidelity_to_full_native"]["disagreement"] for r in rows]),
            "full_support": statistics([r["full_active_features"] for r in rows]),
            "independent_test_centroid_valid_cases": sum(r.get("test_independent_centroid_valid", False) for r in rows),
            "independent_test_centroid_fidelity": statistics([r.get("test_independent_centroid_fidelity", {}).get("ari") for r in rows]),
            "seeds": [r["seed"] for r in rows]})
    return result


def aggregate_other(reports):
    geometry, compression = defaultdict(list), defaultdict(list)
    for report in reports:
        if report["stage"] == "geometry":
            for row in report["rows"]:
                geometry[(report["n"], row["representation"], row["splitter"], row["k"])].append(row)
        elif report["stage"] == "compression":
            for row in report["rows"]:
                compression[(report["dataset"], row["policy"])].append(row)
    geometric = [{"n": k[0], "representation": k[1], "splitter": k[2], "k": k[3], "cases": len(v),
        "valid_training_cases": sum(r["valid_training_partition"] for r in v),
        "train_ari": statistics([r["train_ari"] for r in v]), "test_ari": statistics([r["test_ari"] for r in v])}
        for k, v in geometry.items()]
    compressed = []
    for (dataset, policy), rows in compression.items():
        reduced = [r for r in rows if r["deleted_any"]]
        compressed.append({"dataset": dataset, "policy": policy, "cases": len(rows),
            "selection_enabled": sum(r["selection_enabled"] for r in rows),
            "selected_model_valid": sum(r["selected_model_valid"] for r in rows),
            "reduced_cases": len(reduced),
            "reduced_with_test_disagreement_over_0_05": sum(r["test_fidelity"]["disagreement"] > .05 + 1e-12 for r in reduced),
            "reduced_with_test_ari_below_0_95": sum(r["test_fidelity"]["ari"] < .95 - 1e-12 for r in reduced),
            "original_size": statistics([r["original_size"] for r in rows]),
            "selected_size": statistics([r["selected_size"] for r in rows]),
            "selected_test_ari": statistics([r["selected_test_ari"] for r in rows]),
            "test_ari_change_from_teacher": statistics([r["selected_test_ari"]-r["teacher_test_ari"] for r in rows if r["selected_test_ari"] is not None and r["teacher_test_ari"] is not None]),
            "reduced_test_disagreement": statistics([r["test_fidelity"]["disagreement"] for r in reduced])})
    return geometric, compressed


FALLACIES = [
    ("Simpson's paradox", "Stratified by dataset, representation, fixed bound, and readout; no pooled headline accuracy."),
    ("Ecological fallacy", "Seed means describe procedures; no individual patient or clinical claims."),
    ("Berkson's paradox", "Real-data contrasts and enriched gene universe are selected populations; generalization is limited to that scope."),
    ("Collider bias", "No causal adjustment or claim; observational population filtering could induce dependencies and is not ruled out."),
    ("Base-rate neglect", "Saved group counts and admissibility are checked; single-population controls have no external ARI."),
    ("Regression to the mean", "Restarts are selected on discovery objectives; old-versus-new pilot differences are not a paired treatment effect."),
    ("Survivorship bias", "Manifest coverage is checked and invalid-model denominators retained rather than silently treated as zero."),
    ("Look-elsewhere effect", "All prescribed bounds/readouts are reported; no winner is chosen using test ARI and no significance test is performed."),
    ("Garden of forking paths", "These are development ablations designed after an earlier pilot; no preregistration or confirmatory claim is implied."),
    ("Correlation is not causation", "Label agreement and feature associations do not establish biological mechanisms or causality."),
    ("Reverse causality", "No temporal or causal direction is asserted; it cannot be inferred from these data."),
]


def write_markdown(path, result):
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    lines = ["# Saved obstacle-suite verification and descriptive analysis", "", "## Material Passport", "",
        "- Origin Skill: academic-research-suite / experiment-agent", "- Origin Mode: validate",
        f"- Origin Date: {result['created_utc']}", f"- Verification Status: {result['verification_status']}",
        "- Version Label: obstacle_saved_state_audit_v1", "",
        f"Input: `{result['input_directory']}`. Checks: {sum(result['checks_by_category'].values())}; discrepancies: {len(result['failures'])}.",
        "Original outputs were read only. No clustering model was fitted. This verifies saved arithmetic, selected state reconstruction, and listed consistency checks; it does not certify the algorithms, cluster existence, novelty, or biological correctness.", "",
        "## Verification scope", ""]
    lines += [f"- {text}" for text in result["verification_scope"]]
    lines += ["", "## Retention: fixed configurations", "",
        "Means across the prescribed seeds. Valid/total refers to discovery partition admissibility; ARI n is explicit. Neither full support nor the largest displayed prefix is automatically a selected compact panel.", "",
        "| Dataset | Mapping | Bound | Prefix | Readout | Valid/total | Test ARI mean (n) | Native fidelity ARI |",
        "|---|---|---:|---:|---|---:|---:|---:|"]
    for r in result["retention"]:
        lines.append(f"| {r['dataset']} | {r['representation']} | {r['l1_bound']:.3f} | {r['prefix_size'] or 'full'} | {r['readout']} | {r['valid_training_cases']}/{r['cases']} | {fmt(r['test_ari']['mean'])} ({r['test_ari']['n']}) | {fmt(r['native_fidelity_ari']['mean'])} |")
    lines += ["", "## Geometry: supplied-panel checks", "",
        "These aggregate saved metrics only. Prediction arrays were not saved for geometry, so the fits and ARIs were not independently replayed here. Supplied true panels and the radius construction are oracle diagnostics.", "",
        "| Total rows | Mapping | Splitter | Neighbors | Valid/total | Test ARI mean (n) |",
        "|---:|---|---|---:|---:|---:|"]
    for r in result["geometry"]:
        lines.append(f"| {r['n']} | {r['representation']} | {r['splitter']} | {r['k'] or '—'} | {r['valid_training_cases']}/{r['cases']} | {fmt(r['test_ari']['mean'])} ({r['test_ari']['n']}) |")
    lines += ["", "## Compression: reductions and held-out fidelity", "",
        "Counts pool the two prespecified proposal methods and three pilot seeds within each dataset/policy. Disagreement and ARI thresholds are different criteria. The >5% column is a common descriptive point-error check, not a confidence bound; its denominator includes only cases that actually deleted a feature. Compression reuses previously inspected pilot splits.", "",
        "| Dataset | Policy | Reduced/cases | Reduced with test disagreement >5% | Reduced with test ARI <.95 | Mean size before → after |",
        "|---|---|---:|---:|---:|---:|"]
    for r in result["compression"]:
        lines.append(f"| {r['dataset']} | {r['policy']} | {r['reduced_cases']}/{r['cases']} | {r['reduced_with_test_disagreement_over_0_05']}/{r['reduced_cases']} | {r['reduced_with_test_ari_below_0_95']}/{r['reduced_cases']} | {fmt(r['original_size']['mean'])} → {fmt(r['selected_size']['mean'])} |")
    lines += ["", "## Single-population controls", "",
        "All methods force a split. High reproducibility is not evidence that populations exist. The fixed-panel independent-test-centroid fidelity is copied from saved metrics; its separate test-fit labels were not saved and cannot be arithmetic-recomputed here.", "",
        "| Control | Mapping | Bound | Prefix | Readout | Valid/total | Native fidelity | Independently refitted test valid | Independent fidelity |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|"]
    for r in result["controls"]:
        if r["readout"] not in ("full_native_centroid", "refit_unweighted_centroid"):
            continue
        lines.append(f"| {r['dataset']} | {r['representation']} | {r['l1_bound']:.3f} | {r['prefix_size'] or 'full'} | {r['readout']} | {r['valid_training_cases']}/{r['cases']} | {fmt(r['native_fidelity_ari']['mean'])} | {r['independent_test_centroid_valid_cases']}/{r['cases']} | {fmt(r['independent_test_centroid_fidelity']['mean'])} |")
    lines += ["", "## Statistical fallacy scope: 11/11 checked", "",
        "This is a scoped interpretation audit, not proof that every possible statistical bias is absent. No p-values, confidence intervals, causal estimates, or significance labels are generated.", ""]
    lines += [f"{i}. **{name}:** {note}" for i, (name, note) in enumerate(FALLACIES, 1)]
    if result["failures"]:
        lines += ["", "## Discrepancies", "", "```json", json.dumps(result["failures"], indent=2), "```"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "results/research_obstacle_checks/20260916T145427_229536Z")
    parser.add_argument("--output", type=Path, default=ROOT / "results/research_obstacle_analysis_20260917")
    args = parser.parse_args(argv)
    source, output = args.input.resolve(), args.output.resolve()
    if output == source or source in output.parents:
        parser.error("Derived outputs must be outside the original result directory")
    started = perf_counter()
    original_hashes = {str(p.relative_to(source)): digest(p) for p in source.rglob("*") if p.is_file()}
    manifest, aggregate = read(source / "manifest.json"), read(source / "summary.json")
    reports = aggregate["reports"]
    checks = Checks()
    jobs = manifest["jobs"]
    names = [job["name"] for job in jobs]
    checks.check("manifest_completion", manifest["status"] == "complete", "manifest")
    checks.check("manifest_job_coverage", len(names) == len(set(names)) and set(names) == set(manifest["completed"]) and len(manifest["completed"]) == len(names), "manifest")
    checks.check("aggregate_coverage", aggregate["completed_cases"] == len(reports) == len(jobs), "aggregate")
    verify_code_hashes(manifest["source_sha256"], checks, "suite")
    with threadpool_limits(limits=1):
        for index, job in enumerate(jobs, 1):
            directory = source / job["name"]
            report = read(directory / "summary.json")
            matches = [r for r in reports if r["stage"] == report["stage"] and r["dataset"] == report["dataset"] and r["seed"] == report["seed"] and r.get("n") == report.get("n")]
            checks.check("aggregate_per_case_identity", len(matches) == 1 and matches[0] == report, job["name"])
            print(f"[{index}/{len(jobs)}] Verifying {job['name']}", flush=True)
            try:
                if report["stage"] in ("retention", "controls"):
                    verify_retention(report, directory, manifest["config"], checks)
                elif report["stage"] == "compression":
                    verify_compression(report, directory, checks)
            except Exception as exc:
                checks.check("verification_exception", False, f"{job['name']}: {type(exc).__name__}: {exc}")
    geometry, compression = aggregate_other(reports)
    for name, expected in original_hashes.items():
        checks.check("original_artifact_unchanged", (source / name).is_file() and digest(source / name) == expected, name)
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_directory": str(source), "job_count": len(jobs),
        "verification_status": "VERIFIED_SAVED_ARITHMETIC_AND_NATIVE_STATES" if not checks.failures else "DISCREPANCIES_FOUND",
        "checks_by_category": dict(checks.counts), "failures": checks.failures,
        "verification_scope": [
            "Manifest coverage, stored source hashes, root-versus-case equality, and retention ledgers checked.",
            "All saved retention/control prediction group counts, external ARIs, and fidelity metrics independently recalculated.",
            "Discovery rows/scalers reconstructed; native and truncated frozen centroid predictions recalculated from NPZ states without clustering fits.",
            "Compression candidate prediction arithmetic, validation-driven deletion choices, selected paths, and original teacher data/ARI checked.",
            "Compression alternative models were not refitted; agreement with their saved predictions does not independently validate their fitting code.",
            "Geometry metrics are aggregated but not fit-replayed: geometry prediction arrays were not saved.",
            "Independent test-only centroid-refit labels were not saved; those reported replication metrics were not recalculated.",
            "All prescribed configurations are retained; no test-label winner, significance test, or population-existence test is produced.",
        ],
        "input_artifact_sha256": original_hashes,
        "analysis_script_sha256": digest(Path(__file__)),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "seconds": perf_counter()-started},
        "retention": aggregate_models(reports, "retention"),
        "controls": aggregate_models(reports, "controls"),
        "geometry": geometry, "compression": compression,
        "fallacy_check_coverage": "11/11 scoped checks", "fallacy_checks": [{"name": n, "assessment": a} for n, a in FALLACIES],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    write_markdown(output / "analysis.md", result)
    print(f"{result['verification_status']}: {sum(checks.counts.values())} checks, {len(checks.failures)} discrepancies. {output}", flush=True)
    if checks.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
