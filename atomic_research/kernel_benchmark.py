"""Development experiment for sparse kernel projections, not a GroupFS replica.

Fit choices receive discovery X only. Labels, planted panels and held-out rows
enter reporting after every autonomous candidate has been frozen. All variants
are reported; no winner or cluster-existence claim is selected here.
"""
from __future__ import annotations

from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.tree import DecisionTreeClassifier, export_text

from .datasets import Dataset, DiscoveryScaler, load_dataset, split_rows
from .experiment import annotation_ari, write_json
from .kernel_panels import fit_frozen_kernel_panel, fit_kernel_panel


VARIANTS = {
    "diagonal_cut_local": dict(mixing=False, objective="cut", kernel="local"),
    "diagonal_gap_local": dict(mixing=False, objective="gap_ratio", kernel="local"),
    "projection_cut_local": dict(mixing=True, objective="cut", kernel="local"),
    "projection_gap_local": dict(mixing=True, objective="gap_ratio", kernel="local"),
    "projection_gap_global": dict(mixing=True, objective="gap_ratio", kernel="global"),
}


def make_benchmark(case, *, n, p, signals, seed):
    """Shuffled supports. Geometry examples do not establish minimal panel size."""
    if case in {"mean_shift", "shells", "null_independent", "null_correlated", "metabric"}:
        return load_dataset(case, n=n, p=p, signal_features=max(2, signals), seed=seed)
    if not 2 <= signals <= p or n < 40:
        raise ValueError("Require n>=40 and 2<=signals<=p")
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    details = {}
    if case == "single_shell":
        direction = rng.normal(size=(n, signals))
        X[:, :signals] = direction / np.linalg.norm(direction, axis=1, keepdims=True)
        X[:, :signals] *= rng.uniform(.98, 1.02, n)[:, None]
        for j in range(signals, p):
            coordinate = rng.normal(size=n)
            X[:, j] = coordinate / np.sqrt(coordinate**2 + rng.chisquare(signals - 1, n))
            X[:, j] *= rng.uniform(.98, 1.02, n)
        y = np.zeros(n, dtype=int)
        details = {"scope": "one connected spherical population with matched marginal nuisance"}
    elif case == "covariance_pairs":
        if signals % 2:
            raise ValueError("covariance_pairs needs an even signal count")
        y = rng.integers(0, 2, n)
        rho = .8
        for j in range(0, signals, 2):
            X[:, j + 1] = (2 * y - 1) * rho * X[:, j] + np.sqrt(1 - rho**2) * X[:, j + 1]
        details = {"rho": rho, "scope": "overlapping covariance regimes, not separated density components",
                   "oracle_statistic": "sum of products of paired signal coordinates"}
    elif case in {"moons", "grouped_moons", "distributed_moons"}:
        y = rng.integers(0, 2, n)
        angle = rng.uniform(0, np.pi, n)
        Z = np.column_stack((np.where(y == 0, np.cos(angle), 1 - np.cos(angle)),
                             np.where(y == 0, np.sin(angle), .5 - np.sin(angle))))
        Z += rng.normal(0, .06, size=Z.shape)
        if case == "moons":
            if signals != 2:
                raise ValueError("moons requires exactly two signal coordinates")
            X[:, :2] = Z
        elif case == "grouped_moons":
            # Fixed generator units, not a transform estimated from test rows.
            Z = (Z - np.array([.5, .25])) / np.array([.9, .5])
            rho = .9
            for j in range(signals):
                X[:, j] = np.sqrt(rho) * Z[:, j % 2] + np.sqrt(1 - rho) * X[:, j]
            details = {"rho": rho, "scope": "redundant noisy coordinate groups; not essential-s-feature recovery",
                       "population_groups_unshuffled": [list(range(0, signals, 2)), list(range(1, signals, 2))]}
        else:
            Q, _ = np.linalg.qr(rng.normal(size=(signals, 2)))
            X[:, :signals] = Z @ Q.T * np.sqrt(signals / 2) + .1 * X[:, :signals]
            details = {"scope": "distributed noisy rank-two signal; subsets may suffice",
                       "population_loading": Q.tolist()}
    elif case == "rings":
        if signals != 2:
            raise ValueError("rings requires exactly two signal coordinates")
        y = rng.integers(0, 2, n)
        angle = rng.uniform(0, 2 * np.pi, n)
        radius = np.where(y == 0, 1., .45)
        X[:, :2] = radius[:, None] * np.column_stack((np.cos(angle), np.sin(angle)))
        X[:, :2] += rng.normal(0, .035, (n, 2))
    elif case == "spirals":
        if signals != 2:
            raise ValueError("spirals requires exactly two signal coordinates")
        y = rng.integers(0, 2, n)
        angle = rng.uniform(.3, 3 * np.pi, n)
        X[:, 0] = angle * np.cos(angle + y * np.pi) + rng.normal(0, .12, n)
        X[:, 1] = angle * np.sin(angle + y * np.pi) + rng.normal(0, .12, n)
    else:
        raise ValueError(f"Unknown kernel benchmark: {case}")
    order = rng.permutation(p)
    inverse = np.argsort(order)
    if case == "covariance_pairs":
        details["oracle_pairs"] = inverse[:signals].reshape(-1, 2).tolist()
    return Dataset(X[:, order], y, [f"f{j:04d}" for j in range(p)],
                   tuple(sorted(inverse[:signals].tolist())),
                   "negative_control" if case == "single_shell" else "planted",
                   {"case": case, "n": n, "p": p, "signal_features": signals,
                    "generator_seed": seed, "reference_is_unique_minimal_panel": False,
                    "sampling_unit": "synthetic observation", **details})


def fit_candidates(X, args):
    """Freeze all autonomous fits without accepting y, references or test X."""
    models = {}
    for name, config in VARIANTS.items():
        models[name] = fit_kernel_panel(
            X, budget=args.budget, rank=args.rank, seed=args.seed,
            steps=args.steps, restarts=args.restarts, neighbors=args.neighbors,
            max_samples=args.max_samples, **config)
    return models


def _sizes(labels):
    return np.bincount(np.asarray(labels, dtype=int), minlength=2).tolist()


def report_model(model, X, y, indices, names, directory, name):
    """Frozen native assignment and separately identified tree approximation."""
    train, val, test = indices
    panel = np.asarray(model.panel, dtype=int)
    predicted = [model.predict(X[rows]) for rows in indices]
    median = DiscoveryScaler().fit(X[train]).median
    imputed = np.where(np.isfinite(X[:, panel]), X[:, panel], median[panel])
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=0)
    tree.fit(imputed[train], predicted[0])
    tree_predictions = [tree.predict(imputed[rows]) for rows in indices]
    model.save(directory / f"{name}_model.npz")
    np.savez_compressed(directory / f"{name}_predictions.npz",
                        **{f"{split}_{kind}": values[i]
                           for kind, values in (("native", predicted), ("tree", tree_predictions))
                           for i, split in enumerate(("discovery", "validation", "test"))},
                        test_embedding=model.embed(X[test]))
    (directory / f"{name}_tree.txt").write_text(
        "Approximation only: depth-3 tree in ORIGINAL feature units, fitted to the frozen native rule.\n"
        "Impute nonfinite values using the following discovery medians first:\n"
        + str({names[j]: float(median[j]) for j in panel}) + "\n\n"
        + export_text(tree, feature_names=[names[j] for j in panel]), encoding="utf-8")
    return {"panel": panel.tolist(), "feature_names": [names[j] for j in panel],
            "panel_size": len(panel), "diagnostics": model.diagnostics,
            "metrics": {split: {
                "ari": annotation_ari(y[rows], predicted[i]),
                "cluster_sizes": _sizes(predicted[i]),
                "tree_disagreement": float(np.mean(tree_predictions[i] != predicted[i])),
                "tree_fidelity_ari": float(adjusted_rand_score(predicted[i], tree_predictions[i])),
                "tree_ari": annotation_ari(y[rows], tree_predictions[i])}
                for i, (split, rows) in enumerate(zip(("discovery", "validation", "test"), indices))}}


def run_case(args, directory):
    started = perf_counter()
    dataset = make_benchmark(args.dataset, n=args.n, p=args.p, signals=args.signals, seed=args.seed)
    X = dataset.X
    indices = split_rows(len(X), args.seed + 10000)
    train, val, test = indices
    # All model fits below have no access to annotations or the planted panel.
    models = fit_candidates(X[train], args)
    matched = {
        name: fit_frozen_kernel_panel(X[train], model.panel, kernel=VARIANTS[name]["kernel"],
            neighbors=args.neighbors, max_samples=args.max_samples, seed=args.seed)
        for name, model in models.items() if VARIANTS[name]["mixing"]
    }
    all_features = fit_frozen_kernel_panel(X[train], tuple(range(X.shape[1])),
        kernel="local", neighbors=args.neighbors, max_samples=args.max_samples, seed=args.seed)
    scaler = DiscoveryScaler().fit(X[train])
    Z = scaler.transform(X)
    kmeans = KMeans(n_clusters=2, n_init=10, random_state=args.seed).fit(Z[train])
    # Only now can references/annotations enter, for reporting and marked oracles.
    reports = {}
    for name, model in {**models, "all_features_local": all_features}.items():
        report = report_model(model, X, dataset.y, indices, dataset.names, directory, name)
        if dataset.reference_kind == "planted":
            overlap = len(set(model.panel) & set(dataset.reference_panel))
            report["planted_recall"] = overlap / len(dataset.reference_panel)
            report["planted_precision"] = overlap / len(model.panel)
        if name in matched:
            report["same_panel_identity"] = report_model(matched[name], X, dataset.y, indices,
                dataset.names, directory, name + "_identity")
            # A paired change of downstream geometry on the same support.
            mask = np.asarray(model.panel, dtype=int)
            centroid = KMeans(n_clusters=2, n_init=10, random_state=args.seed).fit(Z[train][:, mask])
            centroid_test = centroid.predict(Z[test][:, mask])
            report["same_panel_centroid_test_ari"] = annotation_ari(dataset.y[test], centroid_test)
            report["native_vs_identity_test_ari"] = float(adjusted_rand_score(
                model.predict(X[test]), matched[name].predict(X[test])))
        reports[name] = report
    oracle = None
    if dataset.reference_kind == "planted":
        model = fit_frozen_kernel_panel(X[train], dataset.reference_panel,
            kernel="local", neighbors=args.neighbors, max_samples=args.max_samples, seed=args.seed)
        oracle = report_model(model, X, dataset.y, indices, dataset.names, directory, "oracle_panel_local")
        oracle["scope"] = "supplied planted panel, identity map; ability diagnostic, not feature discovery"
        if args.dataset == "covariance_pairs":
            pairs = np.asarray(dataset.metadata["oracle_pairs"], dtype=int)
            statistic = (X[test][:, pairs[:, 0]] * X[test][:, pairs[:, 1]]).sum(axis=1)
            oracle["population_rule_test_ari"] = annotation_ari(dataset.y[test], statistic > 0)
            oracle["population_rule_scope"] = "known generator pairs and likelihood rule; not fitted or autonomous"
        elif args.dataset == "shells":
            radius = np.linalg.norm(X[test][:, dataset.reference_panel], axis=1)
            oracle["population_rule_test_ari"] = annotation_ari(dataset.y[test], radius > 1.5)
            oracle["population_rule_scope"] = "known generator coordinates, center and radius threshold; not autonomous"
    np.savez_compressed(directory / "data_and_splits.npz", X=X, y=dataset.y,
                        discovery=train, validation=val, test=test, reference_panel=dataset.reference_panel,
                        kmeans_all_test=kmeans.predict(Z[test]))
    report = {"case": vars(args), "dataset_metadata": dataset.metadata, "reference_kind": dataset.reference_kind,
              "reference_panel": dataset.reference_panel, "models": reports, "oracle": oracle,
              "kmeans_all_test_ari": annotation_ari(dataset.y[test], kmeans.predict(Z[test])),
              "seconds": perf_counter() - started,
              "scope": "forced two-way development experiment; no test of cluster existence, no selected winner",
              "representation_note": "Sample projection is our extension, not GroupFS's feature-group Q matrix."}
    write_json(directory / "report.json", report)
    return report


def write_summary(directory, reports):
    lines = ["# Sparse kernel projection development experiment", "",
             "All prespecified variants are reported. No annotation-based choice of panels, restarts, kernel, rank or winner. "
             "Every model proposes two groups; even valid/stable negative-control splits are not evidence of clusters. "
             "A local affinity is a graph kernel here, not a claim of a positive-semidefinite Mercer kernel.", "",
             "The rank-two sample projection is an experimental extension, NOT a reproduction of GroupFS's feature embedding. "
             "Tree rules are approximations; fidelity is separate from ARI. Support budgets are upper bounds, not certified minimal sizes.", "",
             "| Case | Seed | Budget | Variant | Status | Features | Test ARI | Same-panel identity ARI | Tree disagreement | Planted recall |",
             "|---|---:|---:|---|---|---:|---:|---:|---:|---:|"]
    def fmt(value):
        return "—" if value is None else f"{value:.3f}"
    for report in reports:
        case = report["case"]
        for name, row in report["models"].items():
            identity = row.get("same_panel_identity", {}).get("metrics", {}).get("test", {}).get("ari")
            lines.append(f"| {case['dataset']} | {case['seed']} | {case['budget']} | {name} | "
                f"{row['diagnostics'].get('status', 'see diagnostics')} | {row['panel_size']} | "
                f"{fmt(row['metrics']['test']['ari'])} | {fmt(identity)} | "
                f"{fmt(row['metrics']['test']['tree_disagreement'])} | {fmt(row.get('planted_recall'))} |")
    lines += ["", "Per-case reports also include supplied-panel geometry diagnostics and ordinary k-means. "
              "Oracles must never be counted as autonomous performance. Full model files, split indices, native/tree predictions, "
              "test embeddings and readable approximate rules are retained. No numerical SOTA claim is supported by this suite."]
    (Path(directory) / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(Path(directory) / "summary.json", {"completed_cases": len(reports), "reports": reports})
