"""Compare panel-deletion criteria without external annotation labels.

This is an audit of fitted assignment rules, not a test of cluster existence or
minimum signal support. Refit k-means is a distinct, mean-shift model family;
it is not a substitute for refitting arbitrary nonlinear clustering.
"""

from __future__ import annotations

from time import perf_counter
import warnings

import numpy as np
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KNeighborsClassifier
from threadpoolctl import threadpool_limits


def audit_compression(
    Xtrain,
    training_partition,
    Xval,
    Xtest,
    panel,
    seed=0,
    ari_threshold=.95,
    max_disagreement=.05,
    validation_folds=3,
):
    """Compare four greedy deletion policies against one frozen reference.

    Inputs are already preprocessed in discovery-fitted units. The only labels
    accepted are the algorithm's discovery partition. They are encoded as 0/1
    in sorted class order, recorded in ``label_values``. All returned prediction
    arrays use that encoding. Test data never determine fits, orientation,
    eligibility for deletion, candidate ranking, or selected paths.

    Policies: frozen kNN with ARI threshold; frozen kNN with point-disagreement
    threshold; the same disagreement bound in *every* fixed validation fold;
    and independently fitted two-means with point-disagreement threshold.
    K-means orientation is determined solely by discovery reference labels.

    A reference with fewer than five validation points in either class disables
    all deletion. A fold lacking either reference class disables only the
    foldwise policy. Candidate validation collapse is rejected; for the foldwise
    policy collapse within any fold is also rejected. These conservative guards
    are reported explicitly and supply no confidence guarantee.

    All one-feature deletions of the original panel are returned for both model
    families even when reduction is disabled. Unique (family,panel) fits are
    cached across policies. Timings include all audit work.
    """
    started = perf_counter()
    arrays = [np.asarray(x, dtype=float) for x in (Xtrain, Xval, Xtest)]
    if any(x.ndim != 2 for x in arrays):
        raise ValueError("Xtrain, Xval and Xtest must be two-dimensional")
    train, val, test = arrays
    if len(train) < 4 or len(val) < 2 or len(test) < 1:
        raise ValueError("Need at least four discovery, two validation and one test row")
    if len({x.shape[1] for x in arrays}) != 1 or any(not np.isfinite(x).all() for x in arrays):
        raise ValueError("All feature matrices must be finite with identical column counts")
    if not np.isfinite(ari_threshold) or not -1 <= ari_threshold <= 1:
        raise ValueError("ari_threshold must be in [-1,1]")
    if not np.isfinite(max_disagreement) or not 0 <= max_disagreement <= 1:
        raise ValueError("max_disagreement must be in [0,1]")
    if isinstance(validation_folds, bool) or not isinstance(validation_folds, (int, np.integer)) or not 2 <= validation_folds <= len(val):
        raise ValueError("validation_folds must be an integer between two and the validation row count")
    original = tuple(panel)
    if not original or any(isinstance(j, bool) or not isinstance(j, (int, np.integer)) for j in original):
        raise ValueError("panel must contain integer feature indices")
    original = tuple(sorted(int(j) for j in original))
    if len(set(original)) != len(original) or original[0] < 0 or original[-1] >= train.shape[1]:
        raise ValueError("panel must contain unique in-range column indices")
    labels = np.asarray(training_partition)
    if labels.ndim != 1 or len(labels) != len(train):
        raise ValueError("training_partition must have one value per discovery row")
    values, encoded = np.unique(labels, return_inverse=True)
    if len(values) != 2:
        raise ValueError("training_partition must contain exactly two algorithm labels")
    if labels.dtype.kind in "fc" and not np.isfinite(labels).all():
        raise ValueError("training_partition must be finite")

    folds = [np.sort(fold) for fold in np.array_split(np.random.default_rng(seed).permutation(len(val)), validation_folds)]
    raw_cache, diagnostic_cache = {}, {}
    counters = {"model_fits": 0, "knn_fits": 0, "kmeans_fits": 0,
                "kmeans_initializations_requested": 0, "prediction_calls": 0,
                "evaluation_requests": 0, "cache_hits": 0,
                "fit_seconds": 0., "prediction_seconds": 0.}

    def fit_candidate(family, columns):
        key = (family, columns)
        if key in raw_cache:
            return raw_cache[key]
        fitting_started = perf_counter()
        orientation_tied = False
        fit_warnings = []
        if family == "frozen_knn":
            model = KNeighborsClassifier(n_neighbors=min(7, len(train)), weights="distance")
            model.fit(train[:, columns], encoded)
            fitted_labels = encoded.copy()
            counters["knn_fits"] += 1
            orientation_flip = False
        else:
            model = KMeans(n_clusters=2, n_init=10, random_state=seed, max_iter=300)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                model.fit(train[:, columns])
            fit_warnings = [str(item.message) for item in caught]
            raw_labels = model.labels_.astype(int)
            direct = int(np.count_nonzero(raw_labels == encoded))
            swapped = len(encoded) - direct
            orientation_tied = direct == swapped
            orientation_flip = swapped > direct
            fitted_labels = 1 - raw_labels if orientation_flip else raw_labels
            counters["kmeans_fits"] += 1
            counters["kmeans_initializations_requested"] += 10
        fit_seconds = perf_counter() - fitting_started
        counters["fit_seconds"] += fit_seconds
        counters["model_fits"] += 1
        prediction_started = perf_counter()
        predictions = [model.predict(x[:, columns]).astype(int) for x in (train, val, test)]
        counters["prediction_calls"] += 3
        if orientation_flip:
            predictions = [1 - prediction for prediction in predictions]
        prediction_seconds = perf_counter() - prediction_started
        counters["prediction_seconds"] += prediction_seconds
        result = {"family": family, "panel": list(columns), "training_labels": fitted_labels,
                  "training_predictions": predictions[0], "validation_predictions": predictions[1],
                  "test_predictions": predictions[2], "orientation_flip": orientation_flip,
                  "orientation_tied": orientation_tied, "fit_warnings": fit_warnings,
                  "fit_seconds": fit_seconds, "prediction_seconds": prediction_seconds,
                  "training_partition_valid": len(np.unique(fitted_labels)) == 2}
        raw_cache[key] = result
        return result

    with threadpool_limits(limits=1):
        reference_raw = fit_candidate("frozen_knn", original)
        reference_val = reference_raw["validation_predictions"]
        reference_test = reference_raw["test_predictions"]
        reference_val_counts = np.bincount(reference_val, minlength=2)
        reference_fold_counts = [np.bincount(reference_val[fold], minlength=2) for fold in folds]
        reference_valid = bool(reference_val_counts.min() >= 5)
        fold_reference_valid = bool(all(counts.min() > 0 for counts in reference_fold_counts))

        def agreement(target, predicted):
            return {"ari": float(adjusted_rand_score(target, predicted)),
                    "disagreement": float(np.mean(target != predicted)),
                    "changed_assignments": int(np.count_nonzero(target != predicted)),
                    "n": int(len(target)),
                    "predicted_group_sizes": np.bincount(predicted, minlength=2).tolist(),
                    "nondegenerate": bool(len(np.unique(predicted)) == 2)}

        def evaluate(family, columns):
            counters["evaluation_requests"] += 1
            key = (family, columns)
            if key in diagnostic_cache:
                counters["cache_hits"] += 1
                return diagnostic_cache[key]
            fitted = fit_candidate(family, columns)
            record = {name: (value.tolist() if isinstance(value, np.ndarray) else value)
                      for name, value in fitted.items()}
            record["training_fidelity"] = agreement(encoded, fitted["training_labels"])
            record["training_prediction_fidelity"] = agreement(encoded, fitted["training_predictions"])
            record["validation_fidelity"] = agreement(reference_val, fitted["validation_predictions"])
            record["test_fidelity"] = agreement(reference_test, fitted["test_predictions"])
            record["validation_folds"] = [agreement(reference_val[fold], fitted["validation_predictions"][fold]) for fold in folds]
            record["max_fold_disagreement"] = max(fold["disagreement"] for fold in record["validation_folds"])
            record["selection_valid"] = bool(fitted["training_partition_valid"] and not fitted["orientation_tied"]
                                              and record["validation_fidelity"]["nondegenerate"])
            record["fold_selection_valid"] = bool(record["selection_valid"] and
                                                   all(fold["nondegenerate"] for fold in record["validation_folds"]))
            # No property of the test predictions enters these validity flags.
            diagnostic_cache[key] = record
            return record

        reference = evaluate("frozen_knn", original)
        deletion_diagnostics = {}
        for family in ("frozen_knn", "refit_kmeans"):
            deletion_diagnostics[family] = []
            if len(original) > 1:
                for removed in original:
                    candidate = tuple(j for j in original if j != removed)
                    deletion_diagnostics[family].append({"removed": removed, **evaluate(family, candidate)})

        policy_definitions = [
            ("frozen_knn_ari", "frozen_knn", "ari"),
            ("frozen_knn_disagreement", "frozen_knn", "disagreement"),
            ("frozen_knn_foldwise_disagreement", "frozen_knn", "foldwise"),
            ("refit_kmeans_disagreement", "refit_kmeans", "disagreement"),
        ]
        policies = {}
        for policy_name, family, criterion in policy_definitions:
            current, trace = original, []
            base = evaluate(family, original)
            policy_valid = reference_valid and (criterion != "foldwise" or fold_reference_valid)
            if not reference_valid:
                status = "reference_validation_group_too_small"
            elif criterion == "foldwise" and not fold_reference_valid:
                status = "reference_validation_fold_missing_group"
            else:
                status = "single_feature_panel" if len(current) == 1 else "no_acceptable_deletion"
            while policy_valid and len(current) > 1:
                trials = []
                for removed in current:
                    candidate = tuple(j for j in current if j != removed)
                    record = evaluate(family, candidate)
                    valid_candidate = record["fold_selection_valid"] if criterion == "foldwise" else record["selection_valid"]
                    val_metrics = record["validation_fidelity"]
                    if criterion == "ari":
                        acceptable = valid_candidate and val_metrics["ari"] >= ari_threshold
                        rank = (-val_metrics["ari"], candidate)
                    elif criterion == "foldwise":
                        acceptable = valid_candidate and record["max_fold_disagreement"] <= max_disagreement
                        rank = (record["max_fold_disagreement"], val_metrics["disagreement"], candidate)
                    else:
                        acceptable = valid_candidate and val_metrics["disagreement"] <= max_disagreement
                        rank = (val_metrics["disagreement"], candidate)
                    # A valid candidate is always preferred to an invalid one.
                    trials.append((not valid_candidate, rank, acceptable, removed, candidate, record))
                winner = min(trials, key=lambda entry: (entry[0], entry[1]))
                _, _, accepted, removed, candidate, record = winner
                trace.append({"from_panel": list(current), "candidate": list(candidate), "removed": removed,
                              "accepted": bool(accepted), "validation_fidelity": record["validation_fidelity"],
                              "max_fold_disagreement": record["max_fold_disagreement"],
                              "all_deletion_trials": [
                                  {"removed": entry[3], "panel": list(entry[4]), "selection_valid": not entry[0],
                                   "accepted_by_threshold": bool(entry[2]),
                                   "validation_fidelity": entry[5]["validation_fidelity"],
                                   "max_fold_disagreement": entry[5]["max_fold_disagreement"]}
                                  for entry in trials]})
                if not accepted:
                    status = "no_acceptable_deletion"
                    break
                current = candidate
                status = "single_feature_panel" if len(current) == 1 else "no_acceptable_deletion"
            final = evaluate(family, current)
            policies[policy_name] = {"model_family": family, "criterion": criterion,
                "status": status, "reference_selection_valid": bool(policy_valid),
                "selected_panel": list(current), "trace": trace,
                "original_model": base, "selected_model": final,
                "selected_validation_predictions": final["validation_predictions"],
                "selected_test_predictions": final["test_predictions"],
                "selected_training_labels": final["training_labels"]}

    counters["unique_candidates"] = len(diagnostic_cache)
    counters["elapsed_seconds"] = perf_counter() - started
    return {"status": "audit_only_no_cluster_validity_claim", "original_panel": list(original),
            "label_values": values.tolist(), "prediction_encoding": "0/1 in label_values order",
            "reference": reference,
            "reference_validity": {"validation_group_sizes": reference_val_counts.tolist(),
                "minimum_validation_group_size": 5, "selection_valid": reference_valid,
                "validation_fold_group_sizes": [counts.tolist() for counts in reference_fold_counts],
                "foldwise_selection_valid": reference_valid and fold_reference_valid,
                "test_group_sizes": np.bincount(reference_test, minlength=2).tolist()},
            "validation_fold_indices": [fold.tolist() for fold in folds],
            "settings": {"seed": int(seed), "ari_threshold": float(ari_threshold),
                "max_disagreement": float(max_disagreement), "validation_folds": int(validation_folds),
                "knn_neighbors": min(7, len(train)), "knn_weights": "distance", "kmeans_n_init": 10,
                "candidate_validation_collapse_rejected": True,
                "foldwise_candidate_fold_collapse_rejected": True,
                "kmeans_orientation_source": "discovery training_partition only",
                "test_used_for_selection": False},
            "one_feature_deletions": deletion_diagnostics, "policies": policies,
            "evaluated_candidates": list(diagnostic_cache.values()), "accounting": counters,
            "limitations": ["Fidelity is relative to a fitted reference, not biological truth.",
                "Refit two-means tests a mean-shift model family, not arbitrary nonlinear reclustering.",
                "Foldwise agreement is a sensitivity check, not a statistical confidence bound.",
                "Exact orientation ties are flagged and excluded from candidate selection.",
                "Validation rows are reused adaptively across deletions; only test evaluates final generalization."]}
