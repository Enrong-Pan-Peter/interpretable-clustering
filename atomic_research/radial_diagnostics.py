"""Reproducible oracle-panel diagnostics for the radial node prototype.

Candidate lists deliberately use supplied synthetic support. They are not an
autonomous feature-search algorithm. Labels enter reporting only.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture


CASES = ("shells", "quartic_shells", "single_shell", "independent_gaussian", "correlated_gaussian",
         "student_t", "common_center_scale_mixture", "mean_shift")
CONTROLS = frozenset(CASES[2:-1])


def _clean(value):
    if isinstance(value, np.ndarray):
        return _clean(value.tolist())
    if isinstance(value, np.generic):
        return _clean(value.item())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_clean(v) for v in value]
    return value


def write_json(path, value):
    """Replace complete JSON records atomically; do not leave half a record."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(_clean(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=16)
def _quartic_radius_grid(dimension, component):
    """Approximate normalized inverse CDF, independent of fitted quadrature."""
    location = (2.25 if component == 0 else 12.25) * dimension
    width = 0.5 * dimension
    radius = np.linspace(0.0, np.sqrt(location + 14.0 * width), 8193)
    with np.errstate(divide="ignore"):
        log_density = (dimension - 1) * np.log(radius) - 0.5 * ((radius**2 - location) / width)**2
    density = np.exp(log_density - np.max(log_density))
    cdf = np.r_[0.0, np.cumsum(0.5 * (density[1:] + density[:-1]) * np.diff(radius))]
    cdf /= cdf[-1]
    return radius, cdf


def _signal_block(rng, n, dimension, case):
    """Return one independent population draw, before the shared feature map."""
    labels = np.zeros(n, dtype=int)
    if case in {"shells", "quartic_shells", "single_shell"}:
        directions = rng.normal(size=(n, dimension))
        directions /= np.maximum(np.linalg.norm(directions, axis=1, keepdims=True), 1e-15)
        if case == "quartic_shells":
            labels = rng.integers(0, 2, size=n)
            radius = np.empty(n)
            for component in (0, 1):
                grid, cdf = _quartic_radius_grid(dimension, component)
                mask = labels == component
                radius[mask] = np.interp(rng.uniform(size=int(mask.sum())), cdf, grid)
            return directions * radius[:, None], labels
        if case == "shells":
            labels = rng.integers(0, 2, size=n)
            radius = np.where(labels == 0, 1.5, 3.5) * np.sqrt(dimension)
        else:
            radius = np.full(n, 2.5 * np.sqrt(dimension))
        # Positive radii with modest relative thickness, not fitted centers.
        radius *= np.exp(rng.normal(-0.5 * 0.06**2, 0.06, size=n))
        return directions * radius[:, None], labels
    if case == "independent_gaussian":
        return rng.normal(size=(n, dimension)), labels
    if case == "correlated_gaussian":
        common = rng.normal(size=(n, 1))
        return np.sqrt(0.7) * common + np.sqrt(0.3) * rng.normal(size=(n, dimension)), labels
    if case == "student_t":
        # Elliptical Student-t: common row scale creates radial heavy tails.
        scale = np.sqrt(5.0 / rng.chisquare(5.0, size=n))
        return rng.normal(size=(n, dimension)) * scale[:, None], labels
    if case == "common_center_scale_mixture":
        labels = rng.integers(0, 2, size=n)
        scale = np.where(labels == 0, 0.65, 2.0)
        return rng.normal(size=(n, dimension)) * scale[:, None], labels
    if case == "mean_shift":
        labels = rng.integers(0, 2, size=n)
        return rng.normal(size=(n, dimension)) + (2 * labels - 1)[:, None] * 2.0 / np.sqrt(dimension), labels
    raise ValueError(f"Unknown case: {case}")


def generate_synthetic_splits(case, dimension, p, n_fit, n_validation, n_test, seed):
    """Three independent draws from one fixed, shuffled original-feature map.

    Each nuisance coordinate is taken from a separate independent signal block.
    Signal and nuisance therefore have identical one-coordinate population
    marginals before the shared location/scale transformation. For shell data,
    this prevents variance screening from identifying the signal coordinates.
    The population transform and support are constant across all three splits.
    """
    if case not in CASES or not 2 <= dimension <= p or min(n_fit, n_validation, n_test) < 2:
        raise ValueError("Require a supported case, 2<=dimension<=p and each split size>=2")
    if seed < 0:
        raise ValueError("Seed must be nonnegative")
    children = np.random.SeedSequence(seed).spawn(4)
    map_rng = np.random.default_rng(children[0])
    permutation = map_rng.permutation(p)
    # A common scalar transform preserves exact marginal matching across all
    # columns. The center remains unknown to every fitted model.
    location = float(map_rng.uniform(-3.0, 3.0))
    scale = float(map_rng.uniform(0.7, 1.8))
    support = np.flatnonzero(permutation < dimension).tolist()
    splits, split_seeds = {}, {}
    for name, n, child in zip(("fit", "validation", "test"), (n_fit, n_validation, n_test), children[1:]):
        rng = np.random.default_rng(child)
        signal, labels = _signal_block(rng, n, dimension, case)
        nuisance = np.empty((n, p - dimension))
        for j in range(p - dimension):
            # A distinct block and mixture label for every nuisance feature.
            nuisance[:, j] = _signal_block(rng, n, dimension, case)[0][:, 0]
        raw = np.column_stack((signal, nuisance))
        splits[name] = {"X": location + scale * raw[:, permutation], "y": labels}
        split_seeds[name] = {"entropy": child.entropy, "spawn_key": list(child.spawn_key)}
    return {"splits": splits, "support": support,
            "feature_map": {"original_column_to_latent_column": permutation.tolist(),
                            "feature_names": [f"f{j:04d}" for j in range(p)]},
            "population": {"case": case, "dimension": dimension, "p": p,
                           "location": location, "scale": scale,
                           "nuisance": "one coordinate from each independent same-population block",
                           "shell_radii_per_sqrt_dimension": [1.5, 3.5] if case == "shells" else [2.5],
                           "shell_log_radius_sd": 0.06,
                           "radial_family": "quartic spatial density; approximate inverse-CDF sampler" if case == "quartic_shells" else "off-model generator",
                           "quartic_sampler": {"grid_points": 8193, "locations": [2.25 * dimension, 12.25 * dimension],
                                               "common_width": 0.5 * dimension, "upper_radius": "sqrt(location + 14*width)",
                                               "integration": "trapezoidal CDF, linearly interpolated inverse"} if case == "quartic_shells" else None,
                           "control": case in CONTROLS},
            "split_seeds": split_seeds}


def make_candidates(support, p, count, seed):
    """Fixed diagnostic candidates; uses truth only to build the oracle list."""
    support = tuple(sorted(set(int(j) for j in support)))
    if not support or support[0] < 0 or support[-1] >= p or count < 1:
        raise ValueError("Invalid support, feature count, or candidate count")
    rng = np.random.default_rng(seed)
    outside = [j for j in range(p) if j not in support]
    rng.shuffle(outside)
    candidates, seen = [], set()

    def add(kind, values):
        values = tuple(sorted(set(int(j) for j in values)))
        if values and values not in seen and len(candidates) < count:
            seen.add(values)
            candidates.append({"name": f"c{len(candidates):02d}_{kind}", "kind": kind, "support": list(values)})

    add("oracle", support)
    add("partial", support[:max(1, len(support) // 2)])
    add("partial", support[:-1])
    if outside:
        add("replacement", (*support[:-1], outside[0]))
        add("superset", (*support, outside[0]))
        add("superset", (*support, *outside[:2]))
        add("nuisance_only", outside[:len(support)])
    attempts = 0
    while len(candidates) < count and attempts < 1000:
        size = (len(support), max(1, len(support) - 1), min(p, len(support) + 2))[attempts % 3]
        add("random", rng.choice(p, size=size, replace=False))
        attempts += 1
    return candidates


def _label_metrics(labels, prediction, annotated):
    values, counts = np.unique(prediction, return_counts=True)
    return {"ari": float(adjusted_rand_score(labels, prediction)) if annotated else None,
            "group_counts": {str(int(k)): int(n) for k, n in zip(values, counts)},
            "smallest_group_fraction": float(counts.min() / len(prediction)) if len(counts) >= 2 else 0.0}


def _baseline_models(Xfit, support, seed):
    values = Xfit[:, support]
    mean, scale = values.mean(axis=0), values.std(axis=0)
    scale = np.maximum(scale, 1e-12)
    z = (values - mean) / scale
    kmeans = KMeans(n_clusters=2, n_init=10, random_state=seed).fit(z)
    gmms = {k: GaussianMixture(n_components=k, covariance_type="diag", n_init=3,
                             reg_covar=1e-6, random_state=seed).fit(z) for k in (1, 2)}
    serial = {"scaler": {"mean": mean, "scale": scale, "fit_rows_only": True},
              "kmeans2": {"centers_standardized": kmeans.cluster_centers_,
                          "centers_original": mean + scale * kmeans.cluster_centers_,
                          "inertia": kmeans.inertia_},
              **{f"diagonal_gmm{k}": {"weights": model.weights_, "means_standardized": model.means_,
                                      "variances_standardized": model.covariances_,
                                      "converged": model.converged_} for k, model in gmms.items()}}
    return mean, scale, kmeans, gmms, serial


def run_case(job, directory, progress=None):
    """Fit candidates on fit rows, select on validation, describe held-out test."""
    from .radial_panels import GaussianBackground, fit_radial_panel

    directory = Path(directory)
    started = perf_counter()
    generated = generate_synthetic_splits(job["case"], job["dimension"], job["p"],
                                         job["n_fit"], job["n_validation"], job["n_test"], job["seed"])
    splits = generated.pop("splits")
    Xfit = splits["fit"]["X"]
    background = GaussianBackground.fit(Xfit)
    candidates = make_candidates(generated["support"], job["p"],
                                 1 if job["stage"] == "known-panel" else job["candidates"], job["seed"] + 4109)
    arrays = {f"{split}_{field}": values[field] for split, values in splits.items() for field in ("X", "y")}
    np.savez_compressed(directory / "splits.npz", **arrays)
    metadata = {"job": job, "generator": generated, "candidates": candidates,
                "background": background.to_dict(),
                "scope": "supplied-panel oracle diagnostic; not autonomous discovery",
                "selection": "maximum validation common-full-space gain of radial2; tie by fewer features then candidate order",
                "test_used_for_selection": False, "inferential_guarantee": False}
    write_json(directory / "job.json", metadata)
    rows, prediction_arrays = [], {}
    for index, candidate in enumerate(candidates):
        if progress:
            progress(f"{candidate['name']} ({index + 1}/{len(candidates)})")
        support = candidate["support"]
        radial1 = fit_radial_panel(Xfit, support, components=1)
        radial2 = fit_radial_panel(Xfit, support, components=2)
        mean, scale, kmeans, gmms, baseline_serial = _baseline_models(Xfit, support, job["seed"] + index)
        profile = radial2.spatial_profile()
        # Core helper's explicit spatial-density result; never substitute modes
        # of the radial-distance histogram for spatial modes.
        fitted_valley = bool(profile["two_spatial_modes"] and profile["valley_ratio"] is not None and profile["valley_ratio"] <= 0.5)
        row = {**candidate, "size": len(support), "spatial_profile": profile, "metrics": {},
               "models": {"radial1": radial1.to_dict(), "radial2": radial2.to_dict(), "baselines": baseline_serial}}
        for split, values in splits.items():
            X, y = values["X"], values["y"]
            z = (X[:, support] - mean) / scale
            logq0 = background.logpdf_panel(X, support)
            logq0full = background.logpdf_panel(X, list(range(job["p"])))
            log1, log2 = radial1.logpdf(X), radial2.logpdf(X)
            logg = {k: model.score_samples(z) - np.log(scale).sum() for k, model in gmms.items()}
            predictions = {"radial1": radial1.predict(X), "radial2": radial2.predict(X),
                           "kmeans2": kmeans.predict(z),
                           **{f"diagonal_gmm{k}": model.predict(z) for k, model in gmms.items()}}
            posterior_scores = radial2.component_logpdf(X) + np.log(radial2.weights)
            independent_prediction = np.argmax(posterior_scores, axis=1)
            non_ties = np.abs(posterior_scores[:, 0] - posterior_scores[:, 1]) > 1e-10
            mismatches = int(np.count_nonzero(non_ties & (independent_prediction != predictions["radial2"])))
            if radial2.locations[1] - radial2.locations[0] > 1e-10 and mismatches:
                raise AssertionError("Native radial rule differs from component-posterior assignment")
            for model, prediction in predictions.items():
                prediction_arrays[f"{candidate['name']}__{split}__{model}"] = prediction
            prediction_arrays[f"{candidate['name']}__{split}__squared_radius"] = radial2.squared_radius(X)
            prediction_arrays[f"{candidate['name']}__{split}__radial2_minus_q0_panel"] = log2 - logq0
            prediction_arrays[f"{candidate['name']}__{split}__radial2_minus_radial1"] = log2 - log1
            gain, two_vs_one = float(np.mean(log2 - logq0)), float(np.mean(log2 - log1))
            label_metrics = {name: _label_metrics(y, pred, job["case"] in {"shells", "quartic_shells", "mean_shift"})
                             for name, pred in predictions.items()}
            row["metrics"][split] = {
                "radial2_minus_q0_panel": gain, "common_full_space_gain": gain,
                "radial2_minus_radial1": two_vs_one,
                "q0_full_mean_logpdf": float(np.mean(logq0full)),
                "radial2_full_mean_logpdf": float(np.mean(logq0full - logq0 + log2)),
                "radial1_minus_q0_panel": float(np.mean(log1 - logq0)),
                "diagonal_gmm1_minus_q0_panel": float(np.mean(logg[1] - logq0)),
                "diagonal_gmm2_minus_q0_panel": float(np.mean(logg[2] - logq0)),
                "diagonal_gmm2_minus_gmm1": float(np.mean(logg[2] - logg[1])),
                "native_posterior_replay_mismatches": mismatches,
                "heuristic_split_flag": bool(gain > 0 and two_vs_one > 0 and fitted_valley
                                             and label_metrics["radial2"]["smallest_group_fraction"] >= 0.1),
                "labels": label_metrics}
        rows.append(row)
        # Keep completed candidate artifacts if a later fit fails/interruption occurs.
        write_json(directory / f"{candidate['name']}.json", row)
        np.savez_compressed(directory / "predictions.npz", **prediction_arrays)
    chosen = max(range(len(rows)), key=lambda i: (rows[i]["metrics"]["validation"]["common_full_space_gain"],
                                                -rows[i]["size"], -i))
    selected = rows[chosen]
    for split in ("validation", "test"):
        scores = [row["metrics"][split]["common_full_space_gain"] for row in rows]
        # Test rank is diagnostic only and is never used by the selector.
        metadata[f"oracle_{split}_rank"] = 1 + sum(score > scores[0] for score in scores[1:])
    result = {**metadata, "candidate_results": rows, "selected_candidate": selected["name"],
              "selected_support": selected["support"], "selected_metrics": selected["metrics"],
              "frozen_validation_heuristic_decision": selected["metrics"]["validation"]["heuristic_split_flag"],
              "test_flag_scope": "descriptive recomputation only; cannot change frozen validation decision",
              "oracle_metrics": rows[0]["metrics"], "seconds": perf_counter() - started,
              "validation_flagged_candidates": sum(row["metrics"]["validation"]["heuristic_split_flag"] for row in rows),
              "test_flagged_candidates": sum(row["metrics"]["test"]["heuristic_split_flag"] for row in rows)}
    write_json(directory / "result.json", result)
    return result


def write_summary(directory, reports):
    """Incrementally write row-level metrics and plain-language limitations."""
    directory = Path(directory)
    flat = []
    for report in reports:
        job = report["job"]
        for candidate in report["candidate_results"]:
            v, t = (candidate["metrics"][key] for key in ("validation", "test"))
            flat.append({"job": job["name"], "stage": job["stage"], "case": job["case"],
                         "dimension": job["dimension"], "p": job["p"], "seed": job["seed"],
                         "candidate": candidate["name"], "kind": candidate["kind"], "size": candidate["size"],
                         "support": ",".join(map(str, candidate["support"])),
                         "selected_on_validation": candidate["name"] == report["selected_candidate"],
                         "validation_gain": v["common_full_space_gain"], "test_gain": t["common_full_space_gain"],
                         "validation_two_vs_one": v["radial2_minus_radial1"], "test_two_vs_one": t["radial2_minus_radial1"],
                         "spatial_valley": candidate["spatial_profile"]["two_spatial_modes"],
                         "valley_ratio": candidate["spatial_profile"]["valley_ratio"],
                         "radial1_optimizer_success": candidate["models"]["radial1"]["diagnostics"].get("optimizer_success"),
                         "radial2_optimizer_success": candidate["models"]["radial2"]["diagnostics"].get("optimizer_success"),
                         "validation_flag": v["heuristic_split_flag"], "test_flag": t["heuristic_split_flag"],
                         **{f"test_ari_{method}": t["labels"][method]["ari"] for method in
                            ("radial2", "kmeans2", "diagonal_gmm1", "diagonal_gmm2")}})
    with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0]) if flat else ["job"])
        writer.writeheader()
        writer.writerows(flat)
    controls = {}
    for case in sorted(CONTROLS):
        group = [r for r in reports if r["job"]["case"] == case]
        if group:
            count = sum(len(r["candidate_results"]) for r in group)
            controls[case] = {"jobs": len(group), "candidates": count,
                "validation_candidate_flag_frequency": sum(r["validation_flagged_candidates"] for r in group) / count,
                "test_candidate_flag_frequency": sum(r["test_flagged_candidates"] for r in group) / count,
                "validation_oracle_flag_frequency": float(np.mean([r["oracle_metrics"]["validation"]["heuristic_split_flag"] for r in group])),
                "test_oracle_flag_frequency": float(np.mean([r["oracle_metrics"]["test"]["heuristic_split_flag"] for r in group])),
                "validation_selected_split_frequency": float(np.mean([r["selected_metrics"]["validation"]["heuristic_split_flag"] for r in group])),
                "test_selected_split_frequency": float(np.mean([r["selected_metrics"]["test"]["heuristic_split_flag"] for r in group]))}
    write_json(directory / "summary.json", {"completed_jobs": len(reports), "controls": controls, "rows": flat,
                                           "results": [str(Path(r["job"]["name"]) / "result.json") for r in reports]})
    number = lambda x: "—" if x is None else f"{x:.3f}"
    lines = ["# Radial node diagnostic", "",
             "Supplied-panel oracle diagnostics and fixed candidate ranking only. These results do not demonstrate autonomous feature discovery, statistical split certification, or a complete clustering hierarchy.", "",
             "Candidate selection uses validation mean log-density gain on a common full-feature background; test rows only describe the frozen selection. Candidate lists deliberately contain the supplied true support, partial panels, supersets and random controls. Their ranking is an oracle-assisted diagnostic.", "",
             "The heuristic split flag requires positive radial2-minus-background gain, positive radial2-minus-radial1 gain, two fitted spatial modes with valley/smaller-peak ratio <=0.5, and at least 10% native assignment mass in each group on the reported split. The validation flag is the frozen provisional decision. A test flag is only a descriptive recomputation and never changes that decision. These are not hypothesis tests, confidence guarantees, or calibrated acceptance rules. Both per-candidate and validation-selected control frequencies are reported below.", "",
             "All models use fit-only scaling. Shell nuisance features have the same one-coordinate population marginals as signal features, drawn independently; the feature permutation and population transform are shared across independent splits. Labels never enter fitting or validation selection. The shells case uses off-model lognormal radii; quartic_shells approximates the model family with an explicitly recorded numerical inverse-CDF sampler.", "",
             "| Job | Selected panel | Val gain | Test gain | Test 2-vs-1 | Oracle val rank | Test radial ARI | Test centroid ARI | Test GMM2 ARI | Val flag | Test flag |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for report in reports:
        v, t = (report["selected_metrics"][key] for key in ("validation", "test"))
        lines.append(f"| {report['job']['name']} | {report['selected_support']} | {number(v['common_full_space_gain'])} | "
                     f"{number(t['common_full_space_gain'])} | {number(t['radial2_minus_radial1'])} | {report['oracle_validation_rank']} | "
                     f"{number(t['labels']['radial2']['ari'])} | {number(t['labels']['kmeans2']['ari'])} | "
                     f"{number(t['labels']['diagonal_gmm2']['ari'])} | {v['heuristic_split_flag']} | {t['heuristic_split_flag']} |")
    lines += ["", "## Control flag frequencies", "",
              "Frequencies below are descriptive. Candidates within a job are dependent; these are not independent trials or estimated inferential error guarantees. Common-center scale mixtures and Student-t populations are deliberate radial heavy-tail stress controls. A single-shell control specifies one connected band on the supplied panel. Its matched univariate nuisance marginals can create structured alternative subspaces, especially in two dimensions; flags on those other panels are not automatically false discoveries. Oracle-panel frequencies are reported separately.", "",
              "| Control | Jobs | Candidates | Val candidate frequency | Test candidate frequency | Val selected frequency | Test selected frequency | Val oracle frequency | Test oracle frequency |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for case, control in controls.items():
        lines.append(f"| {case} | {control['jobs']} | {control['candidates']} | "
                     f"{number(control['validation_candidate_flag_frequency'])} | {number(control['test_candidate_flag_frequency'])} | "
                     f"{number(control['validation_selected_split_frequency'])} | {number(control['test_selected_split_frequency'])} | "
                     f"{number(control['validation_oracle_flag_frequency'])} | {number(control['test_oracle_flag_frequency'])} |")
    lines += ["", "Every job saves independent raw splits and labels, the fixed feature map, candidate supports, fitted model parameters, per-split predictions and radii, and incremental candidate JSON records. The manifest records configuration, source hashes, seeds, package versions and completion state.", "",
              "The background comparison uses log q_S(x_S) + log q_0(x) - log q_{0,S}(x_S), so gains are evaluated on the same full feature space. A positive gain can reflect non-Gaussian dependence without two populations; the separate two-versus-one radial comparison and spatial profile are therefore reported. None of these diagnostics establishes semantic truth."]
    (directory / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
