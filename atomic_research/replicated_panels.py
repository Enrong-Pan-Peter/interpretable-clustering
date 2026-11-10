"""Independently rediscover native sparse panels and validate frozen prefixes.

Raw sparse two-means is an established baseline. This experimental protocol
keeps its metric and assignment rule, separates feature rediscovery from rule
compression, and never treats fidelity/stability as evidence that clusters exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from .datasets import DiscoveryScaler, load_dataset
from .experiment import annotation_ari, write_json
from .retained_models import RetainedModel, fit_retained_sparse_kmeans


@dataclass
class FittedPanelLadder:
    scaler: DiscoveryScaler
    model: RetainedModel | None
    panels: list[tuple[int, ...]]
    diagnostics: dict

    def predict(self, X, panel=None):
        if self.model is None:
            raise ValueError("No native model was fitted")
        return self.model.predict(self.scaler.transform(X), panel=panel)


def split_four(n, seed):
    if not isinstance(n, (int, np.integer)) or isinstance(n, (bool, np.bool_)) or n < 80:
        raise ValueError("Need at least 80 independent rows for four disjoint blocks")
    order = np.random.default_rng(seed).permutation(n)
    q = n // 4
    return order[:q], order[q:2*q], order[2*q:3*q], order[3*q:]


def fit_panel_ladder(X, cap=16, seed=0, steps=40, restarts=3):
    """One predeclared L1 bound, sqrt(min(cap, variable feature count)).

    Native objective chooses among restarts, using only this discovery block.
    Prefixes use only positive-weight features and never add zero-weight filler.
    The full model can still have more positive weights than cap.
    """
    if not isinstance(cap, (int, np.integer)) or isinstance(cap, (bool, np.bool_)) or cap < 1:
        raise ValueError("cap must be a positive integer")
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or len(X) < 5 or X.shape[1] < 1:
        raise ValueError("Need a discovery matrix with at least five rows and one feature")
    scaler = DiscoveryScaler().fit(X)
    Z = scaler.transform(X)
    variable = int(np.count_nonzero(Z.std(axis=0) > np.finfo(float).eps))
    bound = float(np.sqrt(min(cap, max(1, variable))))
    fitted = fit_retained_sparse_kmeans(Z, max_features=cap, seed=seed, steps=steps,
                                      restarts=restarts, l1_bounds=[bound])
    diagnostics = {"fit": fitted.diagnostics, "seconds": fitted.elapsed_seconds,
                   "l1_bound": bound, "selection": "maximum native objective among restarts; one fixed bound"}
    if not fitted.models:
        return FittedPanelLadder(scaler, None, [], diagnostics)
    model = max(fitted.models, key=lambda m: m.diagnostics["native_objective"])
    positive = [j for j in model.ranking if model.weights[j] > 0]
    panels = [tuple(sorted(positive[:k])) for k in range(1, min(cap, len(positive))+1)]
    diagnostics["selected_model"] = model.diagnostics
    return FittedPanelLadder(scaler, model, panels, diagnostics)


def group_sizes(labels):
    return np.bincount(np.asarray(labels, dtype=int), minlength=2).tolist()


def validation_selection(fitted, Xval, family_size, alpha=.05, max_error=.05):
    """No test data or external labels enter this decision.

    Label orientation is the frozen model's own orientation for every prefix.
    No validation-dependent flips/refits/feature substitutions are permitted.
    """
    from .fidelity_bounds import select_prefix
    if fitted.model is None:
        return {"status": "no_native_model", "records": [], "empirical_panel": None, "bounded_panel": None}
    target = fitted.predict(Xval)
    reference_valid = min(group_sizes(fitted.model.train_labels)) >= 5 and min(group_sizes(target)) >= 5
    records = []
    for panel in fitted.panels:
        prediction = fitted.predict(Xval, panel)
        records.append({"panel": list(panel), "n": len(Xval), "errors": int(np.sum(target != prediction)),
                        "valid": bool(reference_valid and min(group_sizes(prediction)) >= 5)})
    selected = select_prefix(records, max_error=max_error, alpha=alpha, family_size=family_size)
    selected.update(status="candidate_fidelity_only", reference_validation_sizes=group_sizes(target),
                    reference_valid=bool(reference_valid))
    return selected


def linear_rule(fitted, names, panel=None):
    """Export the exact frozen nearest-centroid boundary in input feature units.

    After discovery-median imputation, assign class 1 if beta*x+intercept > 0.
    This is an algebraic equivalent, not a tree surrogate or a probability.
    """
    model, scaler = fitted.model, fitted.scaler
    if model is None or model.representation != "raw":
        raise ValueError("Linear rule export requires a retained raw model")
    if len(names) != len(model.weights):
        raise ValueError("Feature-name count differs from model")
    panel = tuple(np.flatnonzero(model.weights > 0)) if panel is None else tuple(panel)
    if not panel or any(not isinstance(j, (int, np.integer)) or isinstance(j, (bool, np.bool_)) for j in panel):
        raise ValueError("Rule panel must contain integer feature indices")
    if len(set(panel)) != len(panel) or any(j < 0 or j >= len(names) for j in panel):
        raise ValueError("Rule panel must be nonempty, unique and in range")
    j = np.asarray(panel, dtype=int)
    coefficient_z = 2 * model.weights[j] * (model.centers[1, j] - model.centers[0, j])
    beta = coefficient_z / (scaler.scale[j] * model.transform_scale[j])
    offset_z = np.sum(model.weights[j] * (model.centers[0, j]**2 - model.centers[1, j]**2))
    intercept = float(offset_z - np.sum(coefficient_z *
        (scaler.mean[j]/scaler.scale[j] + model.transform_mean[j]) / model.transform_scale[j]))
    return {"type": "exact_native_linear_rule", "panel": [int(v) for v in j],
            "feature_names": [names[v] for v in j], "coefficients": beta.tolist(), "intercept": intercept,
            "imputation_medians": scaler.median[j].tolist(), "input_feature_count": len(names),
            "assignment": "class 1 if sum(coefficients * median_imputed_raw_features) + intercept > 0, otherwise class 0",
            "labels_are_arbitrary": True, "cluster_existence_established": False}


def predict_linear_rule(rule, X):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != rule["input_feature_count"]:
        raise ValueError("Input must contain all original columns in recorded order")
    Z = X[:, rule["panel"]]
    Z = np.where(np.isfinite(Z), Z, np.asarray(rule["imputation_medians"]))
    return (Z @ np.asarray(rule["coefficients"]) + rule["intercept"] > 0).astype(int)


def fidelity(reference, prediction):
    return {"ari": float(adjusted_rand_score(reference, prediction)),
            "disagreement": float(np.mean(np.asarray(reference) != prediction)),
            "errors": int(np.sum(np.asarray(reference) != prediction)), "n": len(reference),
            "predicted_sizes": group_sizes(prediction)}


def replication(a_val, b_val, a_test, b_test, a_panel, b_panel):
    """Independent model comparison; orientation fixed on validation for reporting.

    This alignment never feeds either model's prefix selection or coefficients.
    It is distinct from the unflipped prefix/teacher fidelity bound.
    """
    if any(x is None for x in (a_val, b_val, a_test, b_test, a_panel, b_panel)):
        return {"status": "one_or_both_panels_unavailable"}
    direct = int(np.sum(np.asarray(a_val) != b_val))
    flip = direct > len(a_val)/2
    b_val = 1-np.asarray(b_val) if flip else np.asarray(b_val)
    b_test = 1-np.asarray(b_test) if flip else np.asarray(b_test)
    union = set(a_panel).union(b_panel)
    return {"status": "report_only_no_cluster_validity_claim", "validation_orientation_flip": flip,
            "validation_orientation_tied": 2*direct == len(a_val),
            "validation": fidelity(a_val, b_val), "test": fidelity(a_test, b_test),
            "a_validation_sizes": group_sizes(a_val), "a_test_sizes": group_sizes(a_test),
            "both_validation_groups_at_least_five": min(group_sizes(a_val)+group_sizes(b_val)) >= 5,
            "both_test_groups_at_least_five": min(group_sizes(a_test)+group_sizes(b_test)) >= 5,
            "feature_jaccard": len(set(a_panel).intersection(b_panel))/len(union) if union else None,
            "panel_a": list(a_panel), "panel_b": list(b_panel)}


def _write_rule(directory, name, rule):
    write_json(directory / f"{name}.json", rule)
    terms = [f"({coefficient:.12g}) * {feature}" for feature, coefficient in
             zip(rule["feature_names"], rule["coefficients"])]
    text = ("Exact native centroid boundary in original input units.\n"
            "First replace nonfinite values using the discovery medians in the accompanying JSON.\n"
            "Labels 0/1 are arbitrary; this rule does not establish that clusters exist.\n"
            "Displayed coefficients are rounded; use JSON for numerical predictions.\n\nClass 1 if:\n" +
            " +\n".join(terms) + f"\n> {-rule['intercept']:.12g}\nOtherwise class 0.\n")
    (directory / f"{name}.txt").write_text(text, encoding="utf-8")


def run_case(args, directory):
    directory = Path(directory)
    started = perf_counter()
    dataset = load_dataset(args.dataset, n=args.n, p=args.p, signal_features=args.signal_features,
                           seed=args.seed, separation=args.separation)
    ia, ib, iv, it = split_four(len(dataset.X), args.seed+37000)
    Xa, Xb, Xval, Xtest = (dataset.X[j] for j in (ia, ib, iv, it))
    fits = {"A": fit_panel_ladder(Xa, args.cap, args.seed+10000, args.steps, args.restarts),
            "B": fit_panel_ladder(Xb, args.cap, args.seed+20000, args.steps, args.restarts)}
    # Both candidate ladders are frozen before shared validation is examined.
    selections = {name: validation_selection(fitted, Xval, 2*args.cap, args.alpha, args.max_error)
                  for name, fitted in fits.items()}
    report = {"dataset": args.dataset, "seed": args.seed, "n": len(dataset.X), "p": dataset.X.shape[1],
              "signal_features": args.signal_features if args.dataset in ("mean_shift", "shells") else None,
              "cap": args.cap, "learners": {}, "replication": {}, "prefix_replication": [],
              "no_cluster_acceptance_rule": True,
              "bound_scope": "simultaneous over at most 2*cap frozen prefix rules in this case, conditional on discovery fits and iid validation rows; fidelity to each own full teacher only",
              "no_test_data_or_annotations_in_selection": True}
    protocol = {"metadata": dataset.metadata, "feature_names": dataset.names,
                "reference_panel": dataset.reference_panel, "reference_kind": dataset.reference_kind,
                "rows": dict(zip(("discovery_A", "discovery_B", "validation", "test"), (ia, ib, iv, it))),
                "preprocessing": {name: fit.scaler.to_dict() for name, fit in fits.items()}}
    write_json(directory / "data_protocol.json", protocol)
    prediction_store, lookup = {}, {}
    # Reporting starts only after every model and prefix decision is final.
    for name, fitted in fits.items():
        selected = selections[name]
        entry = {"diagnostics": fitted.diagnostics, "selection": selected, "prefixes": [], "selected": {}}
        report["learners"][name] = entry
        if fitted.model is None:
            continue
        model = fitted.model
        full_val, full_test = fitted.predict(Xval), fitted.predict(Xtest)
        active = np.flatnonzero(model.weights > 0).tolist()
        entry["full"] = {"panel": active, "support_size": len(active),
                         "test_ari": annotation_ari(dataset.y[it], full_test),
                         "train_sizes": group_sizes(model.train_labels), "test_sizes": group_sizes(full_test)}
        lookup[(name, "full")] = (full_val, full_test, active)
        prediction_store[f"{name}_full_validation"] = full_val
        prediction_store[f"{name}_full_test"] = full_test
        np.savez_compressed(directory / f"{name}_model.npz", weights=model.weights, centers=model.centers,
            transform_mean=model.transform_mean, transform_scale=model.transform_scale,
            ranking=np.asarray(model.ranking), train_labels=model.train_labels)
        _write_rule(directory, f"{name}_full_rule", linear_rule(fitted, dataset.names))
        for record in selected["records"]:
            panel = tuple(record["panel"])
            val, test = fitted.predict(Xval, panel), fitted.predict(Xtest, panel)
            rule = linear_rule(fitted, dataset.names, panel)
            if not np.array_equal(predict_linear_rule(rule, Xtest), test):
                raise AssertionError("Exported linear rule differs from frozen model on test rows")
            key = f"{name}_prefix{len(panel)}"
            prediction_store[key+"_validation"], prediction_store[key+"_test"] = val, test
            lookup[(name, len(panel))] = (val, test, panel)
            meaningful_reference = dataset.reference_kind != "negative_control"
            overlap = len(set(panel).intersection(dataset.reference_panel)) if meaningful_reference else None
            row = {**record, "feature_names": [dataset.names[j] for j in panel],
                   "test_ari": annotation_ari(dataset.y[it], test), "test_fidelity": fidelity(full_test, test),
                   "reference_overlap": overlap, "reference_kind": dataset.reference_kind,
                   "prediction_key": key, "rule_export_verified": True}
            entry["prefixes"].append(row)
        for policy in ("empirical", "bounded"):
            panel = selected[f"{policy}_panel"]
            if panel is None:
                entry["selected"][policy] = {"status": "no_valid_prefix_meets_fidelity_within_cap"}
                continue
            chosen = next(row for row in entry["prefixes"] if row["panel"] == panel)
            entry["selected"][policy] = {"status": "fidelity_candidate_only", **chosen}
            lookup[(name, policy)] = lookup[(name, len(panel))]
            _write_rule(directory, f"{name}_{policy}_rule", linear_rule(fitted, dataset.names, panel))
        print(f"    {name}: full support {len(active)}; empirical {selected['empirical_panel']}; bounded {selected['bounded_panel']}", flush=True)
    # Supplied-support ability benchmark, completely downstream of autonomous
    # decisions. It does not propose features or choose a prefix/model.
    if args.dataset == "mean_shift":
        oracle_panel = list(dataset.reference_panel)
        for name, Xfit in (("A", Xa), ("B", Xb)):
            scaler = fits[name].scaler
            Zfit, Ztest = scaler.transform(Xfit)[:, oracle_panel], scaler.transform(Xtest)[:, oracle_panel]
            oracle = KMeans(n_clusters=2, n_init=10, random_state=args.seed+30000, max_iter=200).fit(Zfit)
            prediction = oracle.predict(Ztest)
            prediction_store[f"{name}_oracle_test"] = prediction
            report["learners"][name]["oracle"] = {"source": "supplied_planted_support_not_discovery",
                "panel": oracle_panel, "method": "unweighted_two_means_10_starts", "test_ari": annotation_ari(dataset.y[it], prediction),
                "train_sizes": group_sizes(oracle.labels_), "test_sizes": group_sizes(prediction)}
            np.savez_compressed(directory / f"{name}_oracle_model.npz", centers=oracle.cluster_centers_,
                                panel=np.asarray(oracle_panel), train_labels=oracle.labels_)
    for key in ("full", "empirical", "bounded"):
        a, b = lookup.get(("A", key), (None, None, None)), lookup.get(("B", key), (None, None, None))
        report["replication"][key] = replication(a[0], b[0], a[1], b[1], a[2], b[2])
    sizes_a = {k for name, k in lookup if name == "A" and isinstance(k, int)}
    sizes_b = {k for name, k in lookup if name == "B" and isinstance(k, int)}
    for size in sorted(sizes_a.intersection(sizes_b)):
        a, b = lookup[("A", size)], lookup[("B", size)]
        report["prefix_replication"].append({"size": size, **replication(a[0], b[0], a[1], b[1], a[2], b[2])})
    np.savez_compressed(directory / "predictions.npz", **prediction_store)
    report["seconds"] = perf_counter()-started
    write_json(directory / "summary.json", report)
    return report
