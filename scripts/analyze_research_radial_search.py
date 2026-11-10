"""Independently replay saved feature-set search results without refitting.

No radial implementation or search code is imported. This verifies saved-state
numerics and accounting, not the causal absence of leakage or cluster validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from scipy.integrate import quad
from scipy.signal import find_peaks
from scipy.special import gammaln, logsumexp
from scipy.stats import multivariate_normal
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ("fit", "search", "validation", "test")
ABLATION_METHODS = {"moment_best": ("moment", "best"), "moment_first": ("moment", "first"),
                    "kernel_best": ("kernel", "best"), "kernel_first": ("kernel", "first")}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def density(model, X):
    support = np.asarray(model["support"], dtype=int)
    radius2 = np.sum(((X[:, support] - model["center"]) / model["scale"]) ** 2, axis=1)
    weighted = (-.5 * ((radius2[:, None] - model["locations"]) / model["width"]) ** 2
                - np.asarray(model["log_z"]) + np.log(model["weights"]))
    return logsumexp(weighted, axis=1) - np.log(model["scale"]).sum(), weighted


def rule_prediction(rule, X):
    if rule["constant_label"] is not None:
        return np.full(len(X), rule["constant_label"], dtype=int)
    radius2 = np.sum(((X[:, rule["support"]] - rule["center"]) / rule["scale"]) ** 2, axis=1)
    return (radius2 > rule["threshold"]).astype(int)


def gaussian(background, X, support):
    support = np.asarray(support, dtype=int)
    mean, covariance = np.asarray(background["mean"]), np.asarray(background["covariance"])
    return multivariate_normal.logpdf(X[:, support], mean[support], covariance[np.ix_(support, support)])


def independent_kernel_dependence(X):
    """Reconstruct centered Gaussian-kernel alignment from fit observations.

    This does not import the proposal implementation or use its saved bandwidths.
    Off-diagonal positive distances determine each feature's median bandwidth.
    """
    X = np.asarray(X, dtype=float)
    values = ((X - X.mean(axis=0)) / X.std(axis=0)) ** 2
    kernels, bandwidths, degenerate = [], [], []
    for column in values.T:
        distances = np.abs(column[:, None] - column[None, :])
        positive = distances[np.triu_indices(len(column), k=1)]
        positive = positive[positive > 0]
        if not len(positive):
            bandwidths.append(None)
            degenerate.append(len(kernels))
            kernels.append(np.zeros_like(distances))
            continue
        bandwidth = float(np.median(positive))
        gram = np.exp(-.5 * (distances / bandwidth) ** 2)
        centered = gram - gram.mean(axis=0)[None, :] - gram.mean(axis=1)[:, None] + gram.mean()
        norm = np.sqrt(np.sum(centered * centered))
        if norm == 0:
            degenerate.append(len(kernels))
        kernels.append(centered / norm if norm > 0 else np.zeros_like(centered))
        bandwidths.append(bandwidth)
    result = np.zeros((len(kernels), len(kernels)))
    for i in range(len(kernels)):
        for j in range(i):
            result[i, j] = result[j, i] = np.clip(np.sum(kernels[i] * kernels[j]), 0., 1.)
    return result, bandwidths, degenerate


def audit_local_steps(search, p, check):
    """Verify refinement events, cache accounting and first-improvement exits.

    Checks saved move order and complete neighborhoods where required; it does
    not reconstruct the random permutation used to order those neighborhoods.
    """
    method = search["method"]
    prefix = method + ": local refinement"
    refinement = ABLATION_METHODS[method][1]
    trace, steps = search["trace"], search["local_steps"]
    lookup = {tuple(row["support"]): row for row in trace}
    count = min(search["config"]["exploration_budget"], len(trace))
    initial = trace[:count]
    rank = lambda support: (lookup[support]["score"], -len(support), -lookup[support]["index"])
    current = tuple(max(initial, key=lambda row: (row["score"], -row["size"], -row["index"]))["support"])
    anchor, visited, previous_improved = None, set(), False
    newly_logged = set()

    def neighbors(support):
        inside = set(support)
        outside = set(range(p)) - inside
        result = set()
        if len(inside) < search["config"]["max_size"]:
            result.update(tuple(sorted(inside | {j})) for j in outside)
        if len(inside) > 1:
            result.update(tuple(sorted(inside - {j})) for j in inside)
        result.update(tuple(sorted(inside - {old} | {new})) for old in inside for new in outside)
        return result

    for i, step in enumerate(steps):
        label = prefix + f"/move{i}"
        parent = tuple(step["parent_support"])
        candidate = tuple(step["candidate_support"])
        target_before = step["evaluations"] - (0 if step["cache_hit"] else 1)
        check(target_before >= count, label + ": monotone evaluation count")
        # Random restarts are fitted trace rows between neighborhood sweeps.
        for index in range(count, target_before):
            row = trace[index]
            check(row["proposal"] == "random_restart", label + ": intervening restart")
            check(anchor is not None and not previous_improved and current == anchor
                  and visited == neighbors(anchor), label + ": restart follows exhausted local optimum")
            current = tuple(row["support"])
        count = target_before
        if parent != anchor:
            if anchor is not None:
                check((refinement == "first" and previous_improved) or visited == neighbors(anchor),
                      label + ": previous neighborhood exit")
            check(parent == current, label + ": new neighborhood starts at incumbent")
            anchor, visited = parent, set()
        else:
            check(not (refinement == "first" and previous_improved),
                  label + ": first-improvement exits immediately")
        check(candidate in neighbors(parent), label + ": add/drop/swap neighbor")
        check(candidate not in visited, label + ": no repeated neighbor within sweep")
        visited.add(candidate)
        removed, added = set(parent) - set(candidate), set(candidate) - set(parent)
        move_type = "add" if not removed else "drop" if not added else "swap"
        check(step["move_type"] == move_type, label + ": move type")
        row = lookup[candidate]
        check(step["cache_hit"] == (row["index"] < count), label + ": cache lookup accounting")
        if not step["cache_hit"]:
            check(row["index"] == count and row["proposal"] == "local_add_drop_swap",
                  label + ": unique fitted move index")
            check(row.get("parent_support") == list(parent) and row.get("move_type") == move_type,
                  label + ": fitted move provenance")
            newly_logged.add(row["index"])
            count += 1
        check(step["evaluations"] == count and count <= search["budget"], label + ": evaluation budget")
        check(step["incumbent_before"] == list(current), label + ": incumbent before")
        improved = rank(candidate) > rank(current)
        check(step["improved"] == improved, label + ": strict ranked improvement")
        if improved:
            current = candidate
        check(step["incumbent_after"] == list(current), label + ": incumbent after")
        previous_improved = improved
    for row in trace[count:]:
        check(row["proposal"] == "random_restart", prefix + ": final unmatched evaluation is restart")
        check(anchor is not None and current == anchor and visited == neighbors(anchor),
              prefix + ": final restart follows exhausted local optimum")
        count += 1
    expected = {row["index"] for row in trace if row["proposal"] == "local_add_drop_swap"}
    check(newly_logged == expected, prefix + ": every fitted local move logged exactly once")
    check(count == len(trace), prefix + ": complete evaluation accounting")


def audit(run):
    run = Path(run).resolve()
    checks, errors, notes = 0, [], []
    jobs_checked, methods_checked, panels_checked = 0, 0, 0

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not bool(condition):
            errors.append(message)

    def close(actual, expected, message, atol=2e-8):
        check(np.shape(actual) == np.shape(expected)
              and np.allclose(actual, expected, atol=atol, rtol=1e-9), message)

    def identity(base, relative, expected, label):
        path = (base / relative).resolve()
        check(path.is_relative_to(base.resolve()) and path.is_file()
              and hashlib.sha256(path.read_bytes()).hexdigest() == expected, label)

    def fitted_state(model, X, support, prefix):
        check(model["support"] == list(support), prefix + ": model support")
        check(model["input_feature_count"] == X.shape[1], prefix + ": input feature count")
        close(model["center"], X[:, support].mean(0), prefix + ": fit-only center")
        close(model["scale"], X[:, support].std(0), prefix + ": fit-only scale")
        weights = np.asarray(model["weights"])
        check(np.isfinite(model["locations"]).all() and np.all(np.asarray(model["locations"]) >= 0)
              and np.all(np.diff(model["locations"]) >= 0), prefix + ": ordered feasible locations")
        check(np.isfinite(model["width"]) and model["width"] > 0, prefix + ": positive width")
        check(np.isfinite(weights).all() and np.all(weights > 0), prefix + ": positive weights")
        close(weights.sum(), 1., prefix + ": weights sum")
        rule = model["rule"]
        for key in ("support", "center", "scale", "input_feature_count"):
            check(rule[key] == model[key], prefix + ": rule " + key)
        check(rule["tie_label"] == 0, prefix + ": rule tie label")
        a = np.asarray(model["locations"])
        if len(a) == 1 or a[0] == a[1]:
            check(rule["constant_label"] == int(np.argmax(weights)) and rule["threshold"] is None,
                  prefix + ": constant rule")
        else:
            threshold = (float(a.mean()) + model["width"] ** 2 / (a[1] - a[0])
                         * (np.log(weights[0] / weights[1]) + model["log_z"][1] - model["log_z"][0]))
            check(rule["constant_label"] is None, prefix + ": nonconstant rule")
            close(rule["threshold"], threshold, prefix + ": posterior threshold")

    def normalized(model, prefix):
        d = len(model["support"])
        area = np.log(2.) + d / 2 * np.log(np.pi) - gammaln(d / 2)
        for i, (a, logz) in enumerate(zip(model["locations"], model["log_z"])):
            def integrand(r):
                if r == 0 and d > 1:
                    return 0.
                log_r = 0. if d == 1 else (d - 1) * np.log(r)
                return np.exp(area + log_r - .5 * ((r * r - a) / model["width"]) ** 2 - logz)
            pivot = np.sqrt(a)
            mass = quad(integrand, 0., pivot, epsabs=2e-9, limit=200)[0] if pivot > 0 else 0.
            mass += quad(integrand, pivot, np.inf, epsabs=2e-9, limit=200)[0]
            close(mass, 1., prefix + f": component {i} independent density mass", atol=2e-7)

    def background_state(background, X, prefix):
        mean, scale = X.mean(0), X.std(0)
        close(background["mean"], mean, prefix + ": fit-only background mean")
        close(background["scale"], scale, prefix + ": fit-only background scale")
        alpha = background["shrinkage"]
        check(np.isfinite(alpha) and 0 <= alpha <= 1, prefix + ": shrinkage range")
        z = (X - mean) / scale
        empirical = z.T @ z / len(X)
        expected = ((1 - alpha) * empirical + alpha * np.trace(empirical) / X.shape[1] * np.eye(X.shape[1]))
        expected *= scale[:, None] * scale[None, :]
        close(background["covariance"], expected, prefix + ": joint shrinkage covariance")

    def describe(saved, name, data, predictions, annotated, prefix):
        model, one = saved["model"], saved["one_band_model"]
        support = model["support"]
        for family, state in (("two-band", model), ("one-band", one)):
            fitted_state(state, data["fit_X"], support, prefix + "/" + family)
            normalized(state, prefix + "/" + family)
        check(len(model["locations"]) == 2 and len(one["locations"]) == 1, prefix + ": component counts")
        background_state(saved["background"], data["fit_X"], prefix)
        profile = saved["spatial_profile"]
        r = np.asarray(profile["radii"])
        close(r, np.linspace(0., np.sqrt(max(model["locations"]) + 10 * model["width"]), len(r)),
              prefix + ": profile grid")
        spatial = logsumexp(-.5 * ((r[:, None] ** 2 - model["locations"]) / model["width"]) ** 2
                           - np.asarray(model["log_z"]) + np.log(model["weights"]), axis=1)
        close(profile["log_spatial_density"], spatial, prefix + ": spatial profile")
        peaks = list(find_peaks(spatial)[0])
        if spatial[0] > spatial[1]:
            peaks.insert(0, 0)
        check(profile["spatial_mode_count"] == len(peaks), prefix + ": profile mode count")
        check(profile["two_spatial_modes"] == (len(peaks) >= 2), prefix + ": two-mode indicator")
        close(profile["spatial_mode_radii"], r[peaks], prefix + ": profile mode radii")
        valley = None
        if len(peaks) >= 2:
            chosen = sorted(sorted(peaks, key=lambda i: spatial[i], reverse=True)[:2])
            valley = float(np.exp(np.min(spatial[chosen[0]:chosen[1] + 1])
                                  - min(spatial[chosen[0]], spatial[chosen[1]])))
            close(profile["valley_ratio"], valley, prefix + ": spatial valley ratio")
        else:
            check(profile["valley_ratio"] is None, prefix + ": absent valley")
        for split in SPLITS:
            X, y = data[f"{split}_X"], data[f"{split}_y"]
            logp, weighted = density(model, X)
            logone, _ = density(one, X)
            gain = float(np.mean(logp - gaussian(saved["background"], X, support)))
            two_vs_one = float(np.mean(logp - logone))
            prediction = rule_prediction(model["rule"], X)
            metric = saved["metrics"][split]
            label = prefix + "/" + split
            check(np.array_equal(prediction, predictions[f"{name}__{split}"]), label + ": native rule replay")
            posterior = np.argmax(weighted, axis=1)
            disagreement = posterior != prediction
            # Near-identical components can differ only by floating point ties.
            check(not disagreement.any() or np.all(np.ptp(weighted[disagreement], axis=1) <= 1e-10),
                  label + ": native rule agrees with posterior except numerical ties")
            close(metric["gain"], gain, label + ": predictive gain")
            close(metric["two_vs_one"], two_vs_one, label + ": two-versus-one gain")
            counts = np.bincount(prediction, minlength=2)
            check(metric["counts"] == counts.tolist(), label + ": native counts")
            smallest = float(counts.min() / len(X))
            close(metric["smallest_fraction"], smallest, label + ": native mass")
            if annotated:
                close(metric["ari"], adjusted_rand_score(y, prediction), label + ": ARI")
            else:
                check(metric["ari"] is None, label + ": control ARI omitted")
            flag = gain > 0 and two_vs_one > 0 and valley is not None and valley <= .5 and smallest >= .1
            check(metric["heuristic_split_flag"] == flag, label + ": provisional flag")

    try:
        manifest = read(run / "manifest.json")
        jobs = manifest["jobs"]
        names = [job["name"] for job in jobs]
        check(manifest["status"] == "complete", "manifest complete")
        check(len(set(names)) == len(names), "unique job names")
        check(len(manifest["completed"]) == len(jobs) and set(manifest["completed"]) == set(names),
              "completed job identities")
        if any("data_source" in job for job in jobs):
            development = manifest["development_data"]
            identity(run, "development_source_manifest.json", development["manifest_sha256"],
                     "archived development manifest hash")
            identity(run, "development_source_audit.json", development["audit_sha256"],
                     "archived development audit hash")
            previous_development = read(run / "development_source_manifest.json")
            previous_audit = read(run / "development_source_audit.json")
            check(previous_development["status"] == "complete" and previous_audit["status"] == "passed"
                  and not previous_audit["errors"], "development source complete and audited")
            check(development["independent_replication"] is False, "development reuse not called replication")
            previous_jobs = {job["name"]: job for job in previous_development["jobs"]}
            for job in jobs:
                source = job["data_source"]
                check(source["manifest_sha256"] == development["manifest_sha256"]
                      and source["audit_sha256"] == development["audit_sha256"],
                      job["name"] + ": shared development source identity")
                check(job["name"] in previous_jobs, job["name"] + ": known development job")
        for relative, expected in manifest["source_sha256"].items():
            identity(run / "source_snapshot", relative, expected, "source snapshot: " + relative)
            current = ROOT / relative
            if current.is_file() and hashlib.sha256(current.read_bytes()).hexdigest() != expected:
                notes.append(f"Current {relative} differs; audit used saved states and snapshot identity.")
        if "resume" in manifest:
            receipt = manifest["resume"]
            identity(run, "resume_parent_manifest.json", receipt["parent_manifest_sha256"], "resume parent manifest")
            previous = read(run / "resume_parent_manifest.json")
            check(previous["jobs"] == jobs, "resume job configuration identity")
            check(previous["source_sha256"] == manifest["source_sha256"], "resume source identity")
            check(set(receipt["reused_jobs"]) <= set(previous["completed"]), "resume reused completed jobs")
            for name, files in receipt["reused_jobs"].items():
                check(name in names, "resume reused job present: " + name)
                for relative, expected in files.items():
                    identity(run / name, relative, expected, f"resume artifact: {name}/{relative}")
            notes.append(f"{len(receipt['reused_jobs'])} reused jobs checked against their artifact hashes.")
    except Exception as exc:
        errors.append(f"manifest/provenance cannot be audited: {type(exc).__name__}: {exc}")
        jobs = []

    all_results = {}
    for job in jobs:
        name = job["name"]
        try:
            check(bool(re.fullmatch(r"[A-Za-z0-9_]+", name)), name + ": safe job name")
            if not re.fullmatch(r"[A-Za-z0-9_]+", name):
                continue
            directory = run / name
            result, metadata = read(directory / "result.json"), read(directory / "job.json")
            all_results[name] = result
            check(result["job"] == metadata["job"] == job, name + ": job configuration copies")
            check(result["generator"] == metadata["generator"], name + ": generator copies")
            check(set(result["methods"]) == set(job["methods"]), name + ": method identities")
            if "data_source" in job:
                source = job["data_source"]
                identity(directory, "splits.npz", source["splits_sha256"], name + ": unchanged reused raw observations")
                identity(directory, "source_job.json", source["job_sha256"], name + ": source job metadata hash")
                source_job = read(directory / "source_job.json")
                check(source_job["generator"] == metadata["generator"], name + ": unchanged source feature map")
                for key in ("case", "dimension", "p", "seed", "search_seed", "n_fit", "n_search",
                            "n_validation", "n_test", "max_size"):
                    check(source_job["job"][key] == job[key], name + ": reused input setting " + key)
                check(source_job["job"] == previous_jobs[name], name + ": source job matches archived manifest")
                notes.append(name + ": development observations reused byte-for-byte; not fresh replication.")
            truth = set(result["generator"]["support"])
            annotated = job["case"] in {"shells", "quartic_shells", "mean_shift"}
            warmup_reference = None
            background_reference = None
            kernel_reference = None
            with np.load(directory / "splits.npz", allow_pickle=False) as data, np.load(directory / "predictions.npz", allow_pickle=False) as predictions:
                for split in SPLITS:
                    X, y = data[f"{split}_X"], data[f"{split}_y"]
                    check(X.shape == (job["n_" + split], job["p"]) and np.isfinite(X).all(),
                          name + "/" + split + ": data dimensions and finite values")
                    check(y.shape == (len(X),), name + "/" + split + ": label dimensions")
                for method in job["methods"]:
                    prefix = name + "/" + method
                    saved = result["methods"][method]
                    search = read(directory / f"{method}_search.json")
                    check(read(directory / f"{method}_result.json") == saved, prefix + ": report copies")
                    check(search["method"] == saved["method"] == method, prefix + ": method identity")
                    trace = search["trace"]
                    check(len(trace) == search["evaluations"] == saved["evaluations"] == job["budget"] == search["budget"],
                          prefix + ": equal exact evaluation budget")
                    supports = [tuple(row["support"]) for row in trace]
                    check(len(set(supports)) == len(supports), prefix + ": no duplicate evaluated feature sets")
                    check(search["config"]["max_size"] == job["max_size"]
                          and search["config"]["seed"] == job["search_seed"], prefix + ": search configuration")
                    if method in ABLATION_METHODS:
                        expected_kind, expected_refinement = ABLATION_METHODS[method]
                        check(search["config"]["dependence_kind"] == expected_kind
                              and search["config"]["refinement"] == expected_refinement,
                              prefix + ": factorial arm configuration")
                        check(search["config"]["exploration_budget"] == max(1, job["budget"] // 2),
                              prefix + ": fixed exploration allocation")
                    if background_reference is None:
                        background_reference = search["background"]
                    check(search["background"] == background_reference == saved["background"], prefix + ": common background")
                    warmup = min(8, max(1, job["budget"] // 2))
                    warm = supports[:warmup]
                    if warmup_reference is None:
                        warmup_reference = warm
                    check(warm == warmup_reference and search["config"]["warmup"] == warmup,
                          prefix + ": shared random warmup")
                    check(all(row["proposal"] == "shared_random_warmup" for row in trace[:warmup]),
                          prefix + ": warmup provenance")
                    running = -np.inf
                    for i, row in enumerate(trace):
                        support = row["support"]
                        label = prefix + f"/feature_set{i}"
                        check(support == sorted(set(support)) and all(isinstance(j, int) and 0 <= j < job["p"] for j in support)
                              and 1 <= len(support) <= job["max_size"], label + ": feasible support")
                        check(row["index"] == i and row["size"] == len(support), label + ": index and size")
                        fitted_state(row["model"], data["fit_X"], support, label)
                        check(len(row["model"]["locations"]) == 2, label + ": radial2 fit")
                        score = float(np.mean(density(row["model"], data["search_X"])[0]
                                              - gaussian(search["background"], data["search_X"], support)))
                        close(row["score"], score, label + ": independent search gain")
                        running = max(running, score)
                        close(row["best_score"], running, label + ": running best gain")
                        check(row["optimizer_success"] == row["model"]["diagnostics"]["optimizer_success"],
                              label + ": optimizer status")
                        panels_checked += 1
                    best = max(trace, key=lambda row: (row["score"], -row["size"], -row["index"]))
                    check(search["selected_support"] == saved["selected_support"] == best["support"],
                          prefix + ": frozen search-only argmax support")
                    check(search["selected_index"] == saved["selected_index"] == best["index"],
                          prefix + ": frozen argmax index")
                    check(search["model"] == saved["model"] == best["model"], prefix + ": frozen model identity")
                    close(search["search_gain"], best["score"], prefix + ": selected search gain")
                    close(saved["metrics"]["search"]["gain"], best["score"], prefix + ": reported selected gain")
                    counts = {str(k): sum(len(s) == k for s in supports) for k in range(1, job["max_size"] + 1)}
                    check(search["evaluated_size_counts"] == counts, prefix + ": size histogram")
                    check(saved["optimizer_nonconvergence"] == sum(row["optimizer_success"] is False for row in trace),
                          prefix + ": nonconvergence count")
                    found = set(saved["selected_support"])
                    check(saved["selected_size"] == len(found) and saved["support_exact"] == (found == truth),
                          prefix + ": support size and exact recovery")
                    close(saved["support_precision"], len(found & truth) / len(found), prefix + ": support precision")
                    close(saved["support_recall"], len(found & truth) / len(truth), prefix + ": support recall")
                    check(saved["oracle_evaluated_naturally"] == any(set(s) == truth for s in supports),
                          prefix + ": natural oracle visit")
                    for split in ("search", "validation"):
                        close(saved[f"oracle_{split}_gain_gap"],
                              result["oracle"]["metrics"][split]["gain"] - saved["metrics"][split]["gain"],
                              prefix + ": oracle " + split + " gap")
                    check(saved["oracle_test_ari"] == result["oracle"]["metrics"]["test"]["ari"], prefix + ": oracle ARI")
                    check(saved["frozen_validation_flag"] == saved["metrics"]["validation"]["heuristic_split_flag"],
                          prefix + ": frozen validation diagnostic")
                    if method in {"dependence_local", "shuffled_dependence_local", "moment_best", "moment_first"}:
                        X = data["fit_X"]
                        squared = ((X - X.mean(0)) / X.std(0)) ** 2
                        centered = squared - squared.mean(0)
                        norms = np.linalg.norm(centered, axis=0)
                        denominator = norms[:, None] * norms[None, :]
                        dep = np.divide(centered.T @ centered, denominator,
                                        out=np.zeros_like(denominator), where=denominator > 0)
                        dep = np.clip(np.abs(dep), 0., 1.)
                        np.fill_diagonal(dep, 0.)
                        permutation = search["dependence_feature_permutation"]
                        if method == "shuffled_dependence_local":
                            check(sorted(permutation) == list(range(job["p"])), prefix + ": dependence permutation")
                            expected = np.random.default_rng(job["search_seed"] + 200003).permutation(job["p"])
                            check(np.array_equal(permutation, expected), prefix + ": recorded permutation seed")
                            dep = dep[np.ix_(permutation, permutation)]
                        else:
                            check(permutation is None, prefix + ": no dependence shuffle")
                        close(search["dependence_matrix"], dep, prefix + ": fit-only dependence")
                        if method in ABLATION_METHODS:
                            dm = search["dependence_metadata"]
                            check(dm["kind"] == "absolute_squared_correlation" and dm["fit_rows"] == len(X),
                                  prefix + ": moment dependence metadata")
                    elif method in {"kernel_best", "kernel_first"}:
                        if kernel_reference is None:
                            kernel_reference = independent_kernel_dependence(data["fit_X"])
                        dep, bandwidths, degenerate = kernel_reference
                        close(search["dependence_matrix"], dep, prefix + ": independent fit-only kernel dependence")
                        check(search["dependence_feature_permutation"] is None, prefix + ": kernel identities unshuffled")
                        dm = search["dependence_metadata"]
                        check(dm["kind"] == "normalized_centered_rbf_squared", prefix + ": kernel kind")
                        check(dm["fit_rows"] == job["n_fit"] and dm["subsampled"] is False,
                              prefix + ": full fit-only kernel rows")
                        check(len(dm["bandwidths"]) == len(bandwidths), prefix + ": bandwidth count")
                        for j, bandwidth in enumerate(bandwidths):
                            if bandwidth is None:
                                check(dm["bandwidths"][j] is None, prefix + f": degenerate bandwidth {j}")
                            else:
                                close(dm["bandwidths"][j], bandwidth, prefix + f": fit-only bandwidth {j}")
                        check(dm["degenerate_features"] == degenerate, prefix + ": degenerate squared features")
                        expected_bytes = 8 * (job["p"] + 8) * job["n_fit"] ** 2
                        check(dm["estimated_working_bytes"] == expected_bytes
                              and dm["maximum_working_bytes"] >= expected_bytes, prefix + ": kernel memory accounting")
                    else:
                        check(search["dependence_matrix"] is None and search["dependence_feature_permutation"] is None,
                              prefix + ": blind method dependence state")
                    if method in ABLATION_METHODS:
                        audit_local_steps(search, job["p"], lambda condition, message: check(condition, name + "/" + message))
                    describe(saved, method, data, predictions, annotated, prefix)
                    methods_checked += 1
                check(set(result["oracle"]["support"]) == truth, name + ": oracle support")
                check(result["oracle"]["model"]["support"] == result["oracle"]["support"], name + ": oracle model support")
                describe(result["oracle"], "oracle", data, predictions, annotated, name + "/oracle")
            jobs_checked += 1
        except Exception as exc:
            errors.append(f"{name}: audit could not finish: {type(exc).__name__}: {exc}")
    try:
        summary = read(run / "summary.json")
        check(summary["completed_jobs"] == len(jobs), "summary completed job count")
        expected_keys = {(job["name"], method) for job in jobs for method in job["methods"]}
        rows = summary["rows"]
        check(len(rows) == len(expected_keys) and {(r["job"], r["method"]) for r in rows} == expected_keys,
              "summary method rows")
        for row in rows:
            report = all_results[row["job"]]["methods"][row["method"]]
            for key, value in report.items():
                if key in row:
                    check(row[key] == value, f"{row['job']}/{row['method']}: summary {key}")
            for split in ("search", "validation", "test"):
                for key in ("gain", "ari", "heuristic_split_flag"):
                    check(row[f"{split}_{key}"] == report["metrics"][split][key],
                          f"{row['job']}/{row['method']}: summary {split}/{key}")
    except Exception as exc:
        errors.append(f"summary cannot be audited: {type(exc).__name__}: {exc}")
    return {"status": "passed" if not errors else "failed", "run": str(run), "checks": checks,
            "jobs": jobs_checked, "methods": methods_checked, "feature_sets": panels_checked, "panels": panels_checked,
            "errors": errors, "notes": notes,
            "scope": "saved-state numerical, native-rule, budget, score, frozen-selection, metric and provenance replay; "
                     "independent normalization for selected/oracle models only; no refitting, "
                     "new-arm local moves replayed but exploration and random neighbor ordering not reconstructed; "
                     "no independent proof of leakage absence, no cluster-validity guarantee"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    with threadpool_limits(limits=1):
        result = audit(args.run)
    (args.run / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
