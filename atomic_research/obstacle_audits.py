"""Paired research diagnostics for model retention, geometry, and reduction.

These are ablations, not a proposed universal objective or cluster acceptance
test. External annotations are used only after model/configuration selection.
"""
from __future__ import annotations

from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
import hashlib
import json

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors

from .datasets import ROOT, DiscoveryScaler, load_dataset, split_rows
from .experiment import annotation_ari, clean, compact, prepare, write_json
from .scoring import score_panel, score_partition


def paired_fidelity(reference, prediction):
    """Label-invariant descriptive agreement; never a cluster-existence test."""
    if reference is None or prediction is None:
        return {"ari": None, "disagreement": None}
    a, b = np.asarray(reference), np.asarray(prediction)
    if len(a) != len(b):
        raise ValueError("Prediction lengths differ")
    # All diagnostic models use binary 0/1 labels. Flips are metric alignment,
    # not supervised training or a deployable label convention.
    error = float(np.mean(a != b))
    return {"ari": float(adjusted_rand_score(a, b)), "disagreement": min(error, 1-error)}


def centroid_predictions(train, test, seed=0):
    if np.unique(train, axis=0).shape[0] < 2:
        return None, None
    model = KMeans(n_clusters=2, n_init=10, random_state=seed, max_iter=200).fit(train)
    return model.labels_, model.predict(test)


def knn_prediction(train, labels, test):
    if labels is None:
        return None
    return KNeighborsClassifier(n_neighbors=min(7, len(train)), weights="distance").fit(train, labels).predict(test)


def evaluation(train_labels, test_labels, ytrain, ytest):
    sizes = np.bincount(np.asarray(train_labels, dtype=int), minlength=2) if train_labels is not None else np.array([])
    valid = bool(len(sizes) == 2 and sizes.min() >= 5)
    return {"valid_training_partition": valid, "training_cluster_sizes": sizes.tolist(),
            "test_cluster_sizes": np.bincount(np.asarray(test_labels, dtype=int), minlength=2).tolist()
                if test_labels is not None else [],
            "train_ari": annotation_ari(ytrain, train_labels) if valid else None,
            "test_ari": annotation_ari(ytest, test_labels) if valid else None}


def write_data_protocol(directory, dataset, indices, scaler):
    write_json(directory / "data_protocol.json", {"metadata": dataset.metadata, "features": dataset.names,
        "reference_panel": dataset.reference_panel, "reference_kind": dataset.reference_kind,
        "rows": dict(zip(("discovery", "validation", "test"), indices)), "preprocessing": scaler.to_dict()})


def select_native_by_bound(models):
    """Restart choice at each prespecified bound; no comparison across bounds."""
    selected = {}
    for model in models:
        bound = float(model.diagnostics["l1_bound"])
        current = selected.get(bound)
        if current is None or model.diagnostics["native_objective"] > current.diagnostics["native_objective"]:
            selected[bound] = model
    return [selected[key] for key in sorted(selected)]


def retention_case(args, dataset_name, seed, directory):
    """Retain three fixed sparsity configurations and compare a component chain.

    Prefixes1..max_features are all reported; no test-ARI winner is selected.
    Native full models can use more features than the prefix cap. The procedure
    uses sparse k-means states; it does not reproduce DUFS or soft-graph states.
    """
    from .retained_models import fit_retained_sparse_kmeans
    config = SimpleNamespace(dataset=dataset_name, n=args.n, p=args.p, signal_features=args.signal_features,
                             seed=seed, separation=args.separation, contrast=None)
    dataset, indices, scaler, (Xtrain, Xval, Xtest) = prepare(config)
    train, _, test = indices
    ytrain, ytest = dataset.y[train], dataset.y[test]
    write_data_protocol(directory, dataset, indices, scaler)
    started = perf_counter()
    rows, fits, spectral_cache, independent_cache, predictions = [], [], {}, {}, {}
    ledger = directory / "comparisons.jsonl"

    def spectral(representation, panel, Ztrain, Ztest):
        key = (representation, tuple(panel))
        if key not in spectral_cache:
            record = score_panel(Ztrain, panel, seed=seed)
            labels = record["labels"] if record["valid"] else None
            predictions = knn_prediction(Ztrain[:, panel], labels, Ztest[:, panel])
            spectral_cache[key] = (labels, predictions, compact(record))
        return spectral_cache[key]

    def append_row(common, readout, tr_labels, te_labels, reference_test, **extra):
        prediction_key = f"row{len(rows):04d}"
        if tr_labels is not None:
            predictions[prediction_key + "_train"] = np.asarray(tr_labels)
        if te_labels is not None:
            predictions[prediction_key + "_test"] = np.asarray(te_labels)
        row = {**common, "readout": readout, **evaluation(tr_labels, te_labels, ytrain, ytest),
               "prediction_key": prediction_key,
               "test_fidelity_to_full_native": paired_fidelity(reference_test, te_labels), **extra}
        rows.append(row)
        with ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(clean(row)) + "\n")

    for representation in ("raw", "squared"):
        result = fit_retained_sparse_kmeans(Xtrain, representation=representation, max_features=args.max_features,
                                           seed=seed, steps=args.steps, restarts=args.restarts)
        fits.append({"representation": representation, "seconds": result.elapsed_seconds, "diagnostics": result.diagnostics})
        selected = select_native_by_bound(result.models)
        # All native choices are now fixed, without using y or validation/test rows.
        for model_number, model in enumerate(selected):
            Ztrain, Ztest = model.transform(Xtrain), model.transform(Xtest)
            full_train, full_test = model.predict(Xtrain), model.predict(Xtest)
            active = np.flatnonzero(model.weights > 0)
            common = {"dataset": dataset_name, "seed": seed, "representation": representation,
                      "l1_bound": model.diagnostics["l1_bound"], "restart": model.diagnostics["restart"],
                      "source": "autonomous_model", "prefix_size": None,
                      "full_active_features": int(len(active)), "native_objective": model.diagnostics["native_objective"]}
            prefix = f"{representation}_bound{model_number}"
            np.savez_compressed(directory / f"{prefix}_model.npz", weights=model.weights, centers=model.centers,
                                transform_mean=model.transform_mean, transform_scale=model.transform_scale,
                                ranking=np.asarray(model.ranking), train_labels=model.train_labels)
            full_metric_train = Ztrain * np.sqrt(model.weights)
            full_metric_test = Ztest * np.sqrt(model.weights)
            append_row(common, "full_native_centroid", full_train, full_test, full_test,
                       panel=active.tolist(), feature_names=[dataset.names[j] for j in active],
                       discovery_native_weighted_geometry=compact(score_partition(full_metric_train[:, active], full_train)))
            append_row(common, "full_native_knn_readout", full_train,
                       knn_prediction(full_metric_train, full_train, full_metric_test), full_test,
                       panel=active.tolist())
            for size in range(1, min(args.max_features, len(model.ranking)) + 1):
                panel = tuple(sorted(int(j) for j in model.ranking[:size]))
                weights = model.weights[list(panel)]
                common_panel = {**common, "prefix_size": size, "panel": panel,
                                "active_prefix_features": int(np.count_nonzero(weights > 0)),
                                "feature_names": [dataset.names[j] for j in panel],
                                "reference_kind": dataset.reference_kind,
                                "reference_overlap": len(set(panel).intersection(dataset.reference_panel))}
                prefix_train, prefix_test = model.predict(Xtrain, panel=panel), model.predict(Xtest, panel=panel)
                weighted_train = Ztrain[:, panel] * np.sqrt(weights)
                weighted_test = Ztest[:, panel] * np.sqrt(weights)
                append_row(common_panel, "truncated_native_centroid", prefix_train, prefix_test, full_test,
                    discovery_original_space_geometry=compact(score_partition(Xtrain[:, panel], prefix_train)),
                    discovery_representation_geometry=compact(score_partition(Ztrain[:, panel], prefix_train)),
                    discovery_native_weighted_geometry=compact(score_partition(weighted_train, prefix_train)))
                wt, wp = centroid_predictions(weighted_train, weighted_test, seed)
                append_row(common_panel, "refit_weighted_centroid", wt, wp, full_test)
                ut, up = centroid_predictions(Ztrain[:, panel], Ztest[:, panel], seed)
                # Reporting only: test-only refitting never changes the panel,
                # native restart, centroids, or any deployment prediction.
                key = (representation, panel)
                if key not in independent_cache:
                    independent_cache[key] = centroid_predictions(Ztest[:, panel], Ztest[:, panel], seed)[0]
                independent = independent_cache[key]
                independent_sizes = np.bincount(independent, minlength=2) if independent is not None else np.array([])
                independent_valid = bool(len(independent_sizes) == 2 and independent_sizes.min() >= 5)
                append_row(common_panel, "refit_unweighted_centroid", ut, up, full_test,
                    test_independent_centroid_valid=independent_valid,
                    test_independent_centroid_sizes=independent_sizes,
                    test_independent_centroid_fidelity=paired_fidelity(up, independent if independent_valid else None))
                append_row(common_panel, "refit_unweighted_centroid_knn", ut,
                           knn_prediction(Ztrain[:, panel], ut, Ztest[:, panel]), full_test)
                st, sp, sr = spectral(representation, panel, Ztrain, Ztest)
                append_row(common_panel, "representation_spectral_knn", st, sp, full_test,
                           discovery_representation_geometry=sr)
                rt, rp, rr = spectral("original_input", panel, Xtrain, Xtest)
                append_row(common_panel, "raw_spectral_knn", rt, rp, full_test,
                           discovery_original_space_geometry=rr)
            print(f"    {dataset_name} seed {seed} {representation} bound {model_number+1}/{len(selected)}", flush=True)
    report = {"stage": "retention", "dataset": dataset_name, "seed": seed, "rows": rows,
              "proposal_fits": fits, "seconds": perf_counter()-started, "spectral_unique_fits": len(spectral_cache),
              "native_selection": "maximum native objective among restarts within each fixed L1 bound; every bound reported",
              "original_panel_scale": "input DiscoveryScaler; model transforms also fit discovery only",
              "no_cluster_acceptance_rule": True,
              "evidence_scope": "new synthetic seed / new same-cohort real-data resample; model and native bounds predeclared"}
    np.savez_compressed(directory / "readout_predictions.npz", **predictions)
    write_json(directory / "summary.json", report)
    return report


def geometry_case(args, seed, n, directory):
    """Supplied true-panel ability check, kept separate from autonomous discovery."""
    dataset = load_dataset("shells", n=n, p=args.p, signal_features=args.signal_features, seed=seed)
    indices = split_rows(len(dataset.X), seed+20000)
    train, _, test = indices
    scaler = DiscoveryScaler().fit(dataset.X[train])
    Xtrain, Xtest = scaler.transform(dataset.X[train]), scaler.transform(dataset.X[test])
    write_data_protocol(directory, dataset, indices, scaler)
    panel = tuple(dataset.reference_panel)
    A, B = Xtrain[:, panel], Xtest[:, panel]
    squared_scaler = DiscoveryScaler().fit(A**2)
    A2, B2 = squared_scaler.transform(A**2), squared_scaler.transform(B**2)
    radius_a, radius_b = np.sum(A**2, axis=1)[:, None], np.sum(B**2, axis=1)[:, None]
    rows = []
    for name, Ztrain, Ztest in (("raw", A, B), ("squared", A2, B2)):
        for k in args.neighbors:
            record = score_panel(Ztrain, tuple(range(len(panel))), seed=seed, k=k)
            labels = record["labels"] if record["valid"] else None
            prediction = knn_prediction(Ztrain, labels, Ztest)
            rows.append({"representation": name, "splitter": "spectral", "k": k,
                         **evaluation(labels, prediction, dataset.y[train], dataset.y[test]),
                         "geometry": compact(record)})
    for name, Ztrain, Ztest in (("raw", A, B), ("squared", A2, B2), ("radius_squared", radius_a, radius_b)):
        tr, te = centroid_predictions(Ztrain, Ztest, seed)
        rows.append({"representation": name, "splitter": "centroid", "k": None,
                     **evaluation(tr, te, dataset.y[train], dataset.y[test])})
    # Explicit query avoids sklearn's self-exclusion convention ambiguity.
    directed = NearestNeighbors(n_neighbors=min(11, len(A))).fit(A).kneighbors(A, return_distance=False)
    neighbors = np.array([[j for j in row if j != i][:10] for i, row in enumerate(directed)])
    labels = dataset.y[train]
    cross = np.mean(labels[neighbors] != labels[:, None], axis=1)
    report = {"stage": "geometry", "dataset": "shells", "seed": seed, "n": n, "panel": panel, "rows": rows,
              "source": "oracle_true_panel_ability_check_not_discovery",
              "ten_neighbor_cross_fraction": {str(k): float(cross[labels==k].mean()) for k in (0,1)},
              "group_mean_scaled_radius": {str(k): float(radius_a[labels==k].mean()) for k in (0,1)},
              "squared_transform": squared_scaler.to_dict(),
              "note": "All k/representations are reported; no test-label model selection. Radius model has supplied radial inductive bias."}
    write_json(directory / "summary.json", report)
    return report


def compression_case(args, source, directory):
    """Replay pilot teachers, then compare deletion policies on the same rows.

    This deliberately reuses inspected pilot splits to diagnose their reduction
    failures. It is development evidence, not an independent confirmation.
    """
    from .compression_audit import audit_compression
    source = Path(source)
    manifest = json.loads((source / "manifest.json").read_text())
    config = SimpleNamespace(**manifest["config"])
    if manifest["status"] != "complete" or config.mode != "search":
        raise ValueError("Compression requires a completed pilot search")
    changed = [p for p, digest in manifest["source_sha256"].items()
               if not (ROOT / p).exists() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest]
    if changed:
        raise ValueError(f"Pilot sources changed; audit before replay: {changed}")
    protocol = json.loads((source / "data_protocol.json").read_text())
    pilot = json.loads((source / "summary.json").read_text())
    dataset, indices, scaler, (Xtrain, Xval, Xtest) = prepare(config)
    train, _, test = indices
    expected = tuple(np.asarray(protocol["rows"][key]) for key in ("discovery", "validation", "test"))
    if not all(np.array_equal(a, b) for a, b in zip(indices, expected)):
        raise ValueError("Reconstructed rows differ from pilot")
    if any(not np.allclose(value, protocol["preprocessing"][key], rtol=1e-12, atol=1e-12)
           for key, value in scaler.to_dict().items()):
        raise ValueError("Reconstructed preprocessing differs from pilot")
    if dataset.metadata.get("source") != protocol["metadata"].get("source"):
        raise ValueError("Raw data source differs from pilot")
    write_json(directory / "data_protocol.json", protocol)
    report = {"stage": "compression", "dataset": config.dataset, "seed": config.seed,
              "source_run": str(source), "source_hashes_verified": True, "rows": [], "methods": {},
              "scope": "diagnostic reuse of inspected pilot splits, not independent confirmation"}
    for method in args.compression_methods:
        saved = pilot["methods"][method]
        panel = tuple(saved["panel"])
        assignment_path = source / f"{method}_assignment.npz"
        with np.load(assignment_path, allow_pickle=False) as assignment:
            if tuple(assignment["original_panel"]) != panel or not np.allclose(assignment["original_X"], Xtrain[:, panel]):
                raise ValueError("Saved teacher panel/data differs from reconstructed pilot")
            labels = assignment["labels"].copy()
        replay = score_panel(Xtrain, panel, seed=config.seed, splitter=config.splitter, k=config.k)
        if not replay["valid"] or adjusted_rand_score(labels, replay["labels"]) < 1-1e-12:
            raise ValueError("Saved teacher partition failed replay")
        audit = audit_compression(Xtrain, labels, Xval, Xtest, panel, seed=config.seed,
                                  ari_threshold=.95, max_disagreement=.05, validation_folds=3)
        # All paths are finalized before the external annotations below enter.
        def annotate(candidate):
            candidate["external_train_ari"] = annotation_ari(dataset.y[train], candidate["training_labels"])
            candidate["external_test_ari"] = annotation_ari(dataset.y[test], candidate["test_predictions"])
            candidate["feature_names"] = [dataset.names[j] for j in candidate["panel"]]
            candidate["reference_overlap"] = len(set(candidate["panel"]).intersection(dataset.reference_panel))

        annotate(audit["reference"])
        for candidate in audit["evaluated_candidates"]:
            annotate(candidate)
        for family in audit["one_feature_deletions"].values():
            for candidate in family:
                annotate(candidate)
                candidate["removed_feature_name"] = dataset.names[candidate["removed"]]
                candidate["removed_in_reference_panel"] = candidate["removed"] in dataset.reference_panel
        if not np.isclose(audit["reference"]["external_test_ari"], saved["test_transfer_ari"]):
            raise ValueError("Full-panel teacher test ARI failed pilot replay")
        for name, policy in audit["policies"].items():
            base, final = policy["original_model"], policy["selected_model"]
            annotate(base)
            annotate(final)
            report["rows"].append({"dataset": config.dataset, "seed": config.seed, "method": method, "policy": name,
                "original_size": len(panel), "selected_size": len(policy["selected_panel"]),
                "selected_panel": policy["selected_panel"], "feature_names": final["feature_names"],
                "deleted_any": len(policy["selected_panel"]) < len(panel),
                "teacher_test_ari": audit["reference"]["external_test_ari"],
                "same_panel_family_test_ari": base["external_test_ari"],
                "selected_test_ari": final["external_test_ari"],
                "same_panel_family_test_fidelity": base["test_fidelity"],
                "validation_fidelity": final["validation_fidelity"], "test_fidelity": final["test_fidelity"],
                "test_fidelity_to_same_panel_family": paired_fidelity(base["test_predictions"], final["test_predictions"]),
                "selection_enabled": policy["reference_selection_valid"],
                "selected_model_valid": final["selection_valid"], "status": policy["status"]})
        audit.update(source_assignment_sha256=hashlib.sha256(assignment_path.read_bytes()).hexdigest(),
                     dataset=config.dataset, seed=config.seed, method=method,
                     reference_kind=dataset.reference_kind, development_reanalysis=True,
                     original_pilot_reduced_panel=saved["reduced_panel"],
                     legacy_path_matches=audit["policies"]["frozen_knn_ari"]["selected_panel"] == saved["reduced_panel"],
                     legacy_difference_note="New policies explicitly reject collapsed validation predictions and tied KMeans orientations.")
        write_json(directory / f"{method}_deletions.json", audit)
        report["methods"][method] = {"accounting": audit["accounting"],
                                      "legacy_path_matches": audit["legacy_path_matches"], "pilot_teacher_replayed": True}
        print(f"    compression {config.dataset} seed {config.seed}: {method}", flush=True)
    write_json(directory / "summary.json", report)
    return report
