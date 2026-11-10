"""Single-node diagnostics. Discovery, compression, and confirmation stay distinct.

External annotations appear ONLY in reporting functions after panel selection.
No split-existence test is implemented: even negative controls produce candidates.
"""
from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
import hashlib
import json
import platform
import warnings

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from threadpoolctl import threadpool_limits

from .datasets import ROOT, DiscoveryScaler, load_dataset, split_rows
from .scoring import score_panel, score_partition, dependence_permutation_diagnostic, column_permutation_calibration
from .search import FrozenObjective, ScoreCache, random_panels, search_discrete, COMPONENTS
from .soft_graph import propose_panels


def clean(value):
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False), encoding="utf-8")


def compact(record):
    return {k: v for k, v in record.items() if k not in ("labels", "legacy_labels")}


def transfer(Xfit, labels, Xnew, panel):
    model = KNeighborsClassifier(n_neighbors=min(7, len(Xfit)), weights="distance")
    return model.fit(Xfit[:, panel], labels).predict(Xnew[:, panel])


def compress_panel(Xfit, labels, Xval, panel, fidelity=.95):
    """Backward deletion preserves a frozen full-panel rule on validation rows.

    This establishes fidelity to this rule, not correctness or global minimality.
    The same validation rows choose every deletion; final reporting uses test.
    """
    original = tuple(panel)
    target = transfer(Xfit, labels, Xval, original)
    if len(np.unique(target)) != 2 or np.bincount(np.unique(target, return_inverse=True)[1]).min() < 5:
        return original, [], "validation_target_too_small_for_reduction"
    current, trace = original, []
    while len(current) > 1:
        trials = []
        for j in current:
            candidate = tuple(k for k in current if k != j)
            predicted = transfer(Xfit, labels, Xval, candidate)
            agreement = float(adjusted_rand_score(target, predicted))
            trials.append((agreement, candidate, j))
        agreement, candidate, removed = max(trials, key=lambda t: (t[0], tuple(-j for j in t[1])))
        accepted = agreement >= fidelity
        trace.append({"from_panel": current, "candidate": candidate, "removed": removed,
                      "validation_fidelity": agreement, "accepted": accepted,
                      "all_deletion_trials": [{"removed": j, "fidelity": a} for a, _, j in trials]})
        if not accepted:
            break
        current = candidate
    return current, trace, "locally_irreducible_at_validation_tolerance"


def annotation_ari(y, labels):
    # ARI for a known single population is not useful as an optimization metric.
    return None if labels is None or len(np.unique(y)) < 2 else float(adjusted_rand_score(y, labels))


def panel_reference_stats(panel, dataset):
    reference = set(dataset.reference_panel)
    overlap = len(reference.intersection(panel))
    return {"reference_kind": dataset.reference_kind, "reference_overlap": overlap,
            "reference_recall": overlap / len(reference) if reference else None,
            "reference_precision": overlap / len(panel) if reference else None}


def fit_and_report(record, Xtrain, Xval, Xtest, ytrain, ytest, dataset, args, directory, name):
    if record is None or record["labels"] is None or not record["valid"]:
        return {"status": "no_admissible_returned_partition"}
    panel, labels = tuple(record["panel"]), record["labels"]
    reduced, reduction_trace, reduction_status = compress_panel(
        Xtrain, labels, Xval, panel, fidelity=args.fidelity)
    test_full = transfer(Xtrain, labels, Xtest, panel)
    test_reduced = transfer(Xtrain, labels, Xtest, reduced)
    independent = score_panel(Xtest, panel, seed=args.seed, splitter=args.splitter, k=args.k)
    reduced_independent = score_panel(Xtest, reduced, seed=args.seed, splitter=args.splitter, k=args.k)
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=args.seed)
    tree.fit(Xtrain[:, reduced], labels)
    tree_text = export_text(tree, feature_names=[dataset.names[j] for j in reduced])
    tree_test = tree.predict(Xtest[:, reduced])
    # Only selected points in feature space and algorithm labels, never patient names/y.
    np.savez_compressed(directory / f"{name}_assignment.npz", X=Xtrain[:, reduced], labels=labels,
                        panel=np.asarray(reduced), original_panel=np.asarray(panel),
                        original_X=Xtrain[:, panel])
    (directory / f"{name}_rule.txt").write_text(
        "Depth-3 surrogate in discovery-standardized feature units.\n"
        "Classes are arbitrary algorithm labels. This is an approximation to the kNN rule.\n\n" + tree_text,
        encoding="utf-8")
    return {"status": "candidate_only_no_split_acceptance_test",
            "panel": panel, "feature_names": [dataset.names[j] for j in panel],
            "reduced_panel": reduced, "reduced_feature_names": [dataset.names[j] for j in reduced],
            "discovery_score": compact(record), "train_ari": annotation_ari(ytrain, labels),
            "test_transfer_ari": annotation_ari(ytest, test_full),
            "test_reduced_transfer_ari": annotation_ari(ytest, test_reduced),
            "test_reclustered_ari": annotation_ari(ytest, independent["labels"]) if independent["valid"] else None,
            "test_reduced_reclustered_ari": annotation_ari(ytest, reduced_independent["labels"]) if reduced_independent["valid"] else None,
            "test_replication_fidelity": annotation_ari(test_full, independent["labels"]) if independent["valid"] else None,
            "test_independent_reclustering": compact(independent),
            "test_reduced_independent_reclustering": compact(reduced_independent),
            "test_compression_fidelity": float(adjusted_rand_score(test_full, test_reduced)),
            "test_surrogate_fidelity_to_reduced_rule": float(adjusted_rand_score(test_reduced, tree_test)),
            "test_surrogate_ari": annotation_ari(ytest, tree_test),
            "test_full_geometry": compact(score_partition(Xtest[:, panel], test_full, k=args.k)),
            "test_reduced_geometry": compact(score_partition(Xtest[:, reduced], test_reduced, k=args.k)),
            "reduction_status": reduction_status, "reduction_trace": reduction_trace,
            "reference": panel_reference_stats(panel, dataset),
            "reduced_reference": panel_reference_stats(reduced, dataset)}


def prepare(args):
    dataset = load_dataset(args.dataset, args.n, args.p, args.signal_features, args.seed,
                           args.separation, args.contrast)
    train, val, test = split_rows(len(dataset.X), args.seed + 20000)
    scaler = DiscoveryScaler().fit(dataset.X[train])
    Xtrain, Xval, Xtest = (scaler.transform(dataset.X[i]) for i in (train, val, test))
    return dataset, (train, val, test), scaler, (Xtrain, Xval, Xtest)


def make_run_directory(args):
    parent = Path(args.output)
    if not parent.is_absolute():
        parent = ROOT / parent
    parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    dimensions = "" if args.dataset in ("metabric", "levine", "mice") else f"_p{args.p}_s{args.signal_features}"
    directory = parent / f"{args.mode}_{args.dataset}{dimensions}_seed{args.seed}_{stamp}"
    directory.mkdir(exist_ok=False)
    return directory


def run(args):
    directory = make_run_directory(args)
    started = perf_counter()
    manifest = {"status": "running", "config": vars(args), "python": platform.python_version(),
                "dependencies": {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "pandas", "threadpoolctl", "flowio", "xlrd")},
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for folder in (ROOT / "atomic_research", ROOT / "atomicplus", ROOT / "scripts")
                                  for p in sorted(folder.rglob("*.py"))
                                  if folder.name != "scripts" or "research" in p.name},
                "scientific_status": "diagnostic prototype, not validated method or novelty proof"}
    write_json(directory / "manifest.json", manifest)
    print(f"Results: {directory}", flush=True)
    try:
        with threadpool_limits(limits=1):
            dataset, indices, scaler, (Xtrain, Xval, Xtest) = prepare(args)
            train, val, test = indices
            write_json(directory / "data_protocol.json", {"metadata": dataset.metadata,
                       "features": dataset.names, "reference_panel": dataset.reference_panel,
                       "reference_kind": dataset.reference_kind,
                       "rows": {"discovery": train, "validation": val, "test": test},
                       "preprocessing": scaler.to_dict()})
            if args.mode == "null-audit":
                report = null_audit(args, Xtest, dataset)
            else:
                reference_started = perf_counter()
                # Reference masks fix comparison units; the masks are not proposal seeds.
                reference_panels = random_panels(Xtrain.shape[1], args.max_features, args.reference_budget, args.seed + 60000)
                references = [score_panel(Xtrain, p, seed=args.seed, splitter=args.splitter, k=args.k)
                              for p in reference_panels]
                reference_seconds = perf_counter() - reference_started
                objectives = {mode: FrozenObjective(references, mode)
                              for mode in ("consistent", "legacy", "graphcut", "density")}
                write_json(directory / "reference_scores.json", {
                    "records": [compact(r) for r in references], "seconds": reference_seconds,
                    "moments": objectives["consistent"].moments,
                    "eligible_reference_count": objectives["consistent"].reference_eligible,
                    "eligibility": "Common valid AND legacy_valid intersection across every objective",
                    "note": "Shared discovery-only setup cost. Comparison units, not significance z-scores."})
                if args.mode == "score-audit":
                    report = score_audit(args, directory, dataset, Xtrain, Xval, Xtest,
                                         dataset.y[train], dataset.y[test], objectives)
                else:
                    report = search_audit(args, directory, dataset, Xtrain, Xval, Xtest,
                                          dataset.y[train], dataset.y[test], objectives[args.objective])
                report["shared_reference_seconds"] = reference_seconds
                report["shared_reference_evaluations"] = len(references)
            write_json(directory / "summary.json", report)
        manifest.update(status="complete", total_seconds=perf_counter() - started)
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update(status="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed",
                        error=f"{type(exc).__name__}: {exc}", total_seconds=perf_counter() - started)
        write_json(directory / "manifest.json", manifest)
        raise
    write_json(directory / "manifest.json", manifest)
    print(f"Completed in {manifest['total_seconds']:.1f}s", flush=True)
    return directory


def search_audit(args, directory, dataset, Xtrain, Xval, Xtest, ytrain, ytest, objective):
    report = {"methods": {}, "target": "two-way local split; no end-to-end tree claim"}
    for method in args.methods:
        print(f"  {method}: discovering panels", flush=True)
        def save_progress(record):
            # No annotations in this ledger; each completed score survives interruption.
            with (directory / f"{method}_progress.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(clean(compact(record))) + "\n")
        cache = ScoreCache(Xtrain, objective, args.budget, seed=args.seed, splitter=args.splitter,
                           k=args.k, on_evaluation=save_progress)
        if method in ("random", "forward", "evolutionary"):
            accounting = search_discrete(method, cache, args.max_features, args.seed + 70000)
        else:
            if method == "soft_graph":
                proposal = propose_panels(Xtrain, max_features=args.max_features, seed=args.seed,
                    steps=args.steps, restarts=args.restarts, max_samples=args.proposal_rows,
                    standardize=False, max_seconds=args.proposal_seconds)
            elif method == "sparse_kmeans":
                from .sparse_kmeans import propose_panels as sparse_kmeans_proposals
                proposal = sparse_kmeans_proposals(Xtrain, max_features=args.max_features, seed=args.seed,
                    steps=args.steps, restarts=args.restarts, standardize=False,
                    max_seconds=args.proposal_seconds)
            else:
                raise ValueError(f"Unknown method {method}")
            # Random order avoids giving small prefixes all the budget when capped.
            order = np.random.default_rng(args.seed + 1000).permutation(len(proposal.panels))
            for index in order:
                if cache.full:
                    break
                cache.evaluate(proposal.panels[int(index)])
            accounting = {"method": method, "proposal_seconds": proposal.elapsed_seconds,
                          "proposal_diagnostics": proposal.diagnostics, "proposal_panels": len(proposal.panels),
                          "unique_evaluations": len(cache.records), "requests": cache.requests,
                          "scoring_seconds": cache.scoring_seconds, "total_seconds": perf_counter() - cache.started,
                          "budget_kind": "panel cap PLUS separately charged optimizer work; not matched compute"}
            write_json(directory / f"{method}_proposal_trace.json", proposal.trace)
        ranked = cache.ranked()
        # Selection was completed without y. Labels enter only these reports.
        selected = next((r for r in ranked if objective.eligible(r)), None)
        with (directory / f"{method}_candidates.jsonl").open("w", encoding="utf-8") as stream:
            for record in cache.records.values():
                stream.write(json.dumps(clean({**compact(record), "diagnostic_train_ari": annotation_ari(ytrain, record["labels"]),
                                                **panel_reference_stats(record["panel"], dataset)})) + "\n")
        outcome = fit_and_report(selected, Xtrain, Xval, Xtest, ytrain, ytest, dataset, args, directory, method)
        ari_values = [annotation_ari(ytrain, r["labels"]) for r in ranked if objective.eligible(r)]
        ari_values = [a for a in ari_values if a is not None]
        best_visited = max(ari_values) if ari_values else None
        outcome.update(accounting=accounting, best_visited_train_ari=best_visited,
                       training_selection_regret=(best_visited - outcome["train_ari"])
                       if best_visited is not None and outcome.get("train_ari") is not None else None)
        report["methods"][method] = outcome
        write_json(directory / "summary.partial.json", report)
        print(f"  {method}: {len(cache.records)} panels, {accounting['total_seconds']:.2f}s; "
              f"test transfer ARI={outcome.get('test_transfer_ari')}", flush=True)
    if dataset.reference_panel:
        # May exceed max_features (e.g., PAM50); it is an ability diagnostic only.
        record = score_panel(Xtrain, dataset.reference_panel, seed=args.seed, splitter=args.splitter, k=args.k)
        report["reference_panel_diagnostic_not_search_seed"] = fit_and_report(
            record, Xtrain, Xval, Xtest, ytrain, ytest, dataset, args, directory, "reference")
    return report


def score_audit(args, directory, dataset, Xtrain, Xval, Xtest, ytrain, ytest, objectives):
    bank = {p: "random" for p in random_panels(Xtrain.shape[1], args.max_features, args.budget, args.seed + 90000)}
    if dataset.reference_panel:
        panel = dataset.reference_panel
        bank[panel] = "reference_full"
        # Explicit diagnostic panels ONLY: never used in search-mode initialization.
        for j in panel:
            bank[(j,)] = "reference_singleton"
            if len(panel) > 1:
                bank[tuple(k for k in panel if k != j)] = "reference_leave_one_out"
    records = []
    for index, (panel, origin) in enumerate(bank.items()):
        record = score_panel(Xtrain, panel, seed=args.seed, splitter=args.splitter, k=args.k)
        record.update(origin=origin, scores={key: obj(record) for key, obj in objectives.items()})
        records.append(record)
        if (index + 1) % 20 == 0:
            print(f"  paired score audit: {index + 1}/{len(bank)} panels", flush=True)
    rows = [{**compact(r), "diagnostic_train_ari": annotation_ari(ytrain, r["labels"]),
             **panel_reference_stats(r["panel"], dataset)} for r in records]
    write_json(directory / "paired_panel_scores.json", rows)
    report = {"candidate_count": len(records), "oracle_augmented_diagnostic_bank": True,
              "note": "These rankings diagnose scores; they are NOT search-recovery results.", "objectives": {}, "by_size": {}}
    for name in objectives:
        eligible = [r for r in records if objectives[name].eligible(r)]
        chosen = max(eligible, key=lambda r: (r["scores"][name], -len(r["panel"]))) if eligible else None
        outcome = fit_and_report(chosen, Xtrain, Xval, Xtest, ytrain, ytest, dataset, args, directory, name)
        pairs = [(r["scores"][name], annotation_ari(ytrain, r["labels"])) for r in records
                 if objectives[name].eligible(r)]
        pairs = [(s, a) for s, a in pairs if a is not None]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            correlation = float(spearmanr(np.array(pairs)[:, 0], np.array(pairs)[:, 1]).statistic) if len(pairs) > 2 else None
        outcome["score_vs_train_ari_spearman"] = correlation
        report["objectives"][name] = outcome
    for size in sorted(set(len(r["panel"]) for r in records)):
        subset = [r for r in records if len(r["panel"]) == size and objectives["consistent"].eligible(r) and r["origin"] == "random"]
        report["by_size"][size] = {"random_valid_panels": len(subset),
                                   **{key: float(np.median([r[key] for r in subset])) if subset else None for key in COMPONENTS}}
    return report


def null_audit(args, Xtest, dataset):
    panel = dataset.reference_panel or tuple(range(min(2, Xtest.shape[1])))
    Z = Xtest[:, panel]
    def statistic(values):
        # Canonical row order makes a singleton shuffle exactly invariant, including
        # spectral initialization randomness. Not a correction for adaptive search.
        order = np.lexsort(tuple(values[:, j] for j in range(values.shape[1] - 1, -1, -1)))
        result = score_panel(values[order], range(values.shape[1]), seed=args.seed, k=args.k, splitter=args.splitter)
        return result["graphcut"]
    return {"fixed_panel": panel, "feature_names": [dataset.names[j] for j in panel],
            "graphcut_independence_null": column_permutation_calibration(Z, statistic, B=args.permutations, seed=args.seed),
            "correlation_independence_null": dependence_permutation_diagnostic(Z, B=args.permutations, seed=args.seed),
            "warning": "Both nulls concern dependence, not whether clusters exist. No split acceptance rule here."}
