"""Independently replay saved radial diagnostics; never refit or select on test.

Uses saved parameters, scipy's Gaussian density and independent adaptive
integration, without importing the fitted radial implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import gammaln, logsumexp
from scipy.stats import multivariate_normal
from sklearn.metrics import adjusted_rand_score

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit(run):
    run = Path(run).resolve()
    manifest = read(run / "manifest.json")
    checks, errors, notes = 0, [], []

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not bool(condition):
            errors.append(message)

    def close(actual, expected, message, atol=2e-8):
        check(np.allclose(actual, expected, atol=atol, rtol=1e-9), message)

    check(manifest["status"] == "complete", "manifest is incomplete")
    check(len(manifest["completed"]) == len(manifest["jobs"]), "job completion count")
    if "resume" in manifest:
        receipt = manifest["resume"]
        parent_manifest = run / "resume_parent_manifest.json"
        check(parent_manifest.is_file() and hashlib.sha256(parent_manifest.read_bytes()).hexdigest() == receipt["parent_manifest_sha256"],
              "resume parent manifest identity")
        for relative, expected in receipt["parent_source_sha256"].items():
            source = run / "resume_parent_sources" / relative
            check(source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == expected,
                  f"resume parent source: {relative}")
        for job, reused in receipt["reused_jobs"].items():
            for relative, expected in reused["files_sha256"].items():
                path = run / job / relative
                check(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                      f"reused artifact identity: {job}/{relative}")
        notes.append(f"{len(receipt['reused_jobs'])} completed jobs reused byte-for-byte with recorded predecessor source identity.")
    for relative, expected in manifest["source_sha256"].items():
        snapshot = run / "source_snapshot" / relative
        source = snapshot if snapshot.exists() else ROOT / relative
        check(source.exists() and hashlib.sha256(source.read_bytes()).hexdigest() == expected,
              f"source identity: {relative}")
        current = ROOT / relative
        if current.exists() and hashlib.sha256(current.read_bytes()).hexdigest() != expected:
            notes.append(f"Current {relative} differs; audited saved snapshot and parameters.")

    candidate_count = 0
    for job in manifest["jobs"]:
        directory = run / job["name"]
        result = read(directory / "result.json")
        stored_job = read(directory / "job.json")
        background = stored_job["background"]
        mean, covariance = np.asarray(background["mean"]), np.asarray(background["covariance"])
        with np.load(directory / "splits.npz", allow_pickle=False) as data, np.load(directory / "predictions.npz", allow_pickle=False) as predictions:
            rows = result["candidate_results"]
            candidate_count += len(rows)
            oracle = stored_job["generator"]["support"]
            check(rows[0]["support"] == oracle, job["name"] + ": oracle identity")
            for row in rows:
                name = row["name"]
                check(read(directory / f"{name}.json") == row, f"{job['name']}/{name}: candidate copy differs")
                S = np.asarray(row["support"], dtype=int)
                d = len(S)
                for family in ("radial1", "radial2"):
                    model = row["models"][family]
                    b = model["width"]
                    log_area = np.log(2.) + d / 2. * np.log(np.pi) - gammaln(d / 2.)
                    for component, (a, logz) in enumerate(zip(model["locations"], model["log_z"])):
                        def integrand(r):
                            if r == 0 and d > 1:
                                return 0.
                            log_r = 0. if d == 1 else (d - 1) * np.log(r)
                            return np.exp(log_area + log_r - .5 * ((r * r - a) / b)**2 - logz)
                        pivot = np.sqrt(a)
                        mass = quad(integrand, 0., pivot, epsabs=2e-9, limit=200)[0] if pivot > 0 else 0.
                        mass += quad(integrand, pivot, np.inf, epsabs=2e-9, limit=200)[0]
                        close(mass, 1., f"{job['name']}/{name}/{family}/{component}: density mass", atol=2e-7)
                for split, expected_n in (("fit", job["n_fit"]), ("validation", job["n_validation"]), ("test", job["n_test"])):
                    X, y = data[f"{split}_X"], data[f"{split}_y"]
                    prefix = f"{job['name']}/{name}/{split}"
                    check(X.shape == (expected_n, job["p"]), prefix + ": row/feature count")
                    logq = multivariate_normal.logpdf(X[:, S], mean[S], covariance[np.ix_(S, S)])
                    logs = {}
                    for family in ("radial1", "radial2"):
                        model = row["models"][family]
                        z = (X[:, S] - model["center"]) / model["scale"]
                        t = np.sum(z**2, axis=1)
                        weighted = (-.5 * ((t[:, None] - np.asarray(model["locations"])) / model["width"])**2
                                    - np.asarray(model["log_z"]) + np.log(model["weights"]))
                        logs[family] = logsumexp(weighted, axis=1) - np.log(model["scale"]).sum()
                        posterior = np.argmax(weighted, axis=1)
                        saved = predictions[f"{name}__{split}__{family}"]
                        check(np.array_equal(posterior, saved), prefix + f": {family} posterior replay")
                        rule = model["rule"]
                        rule_t = np.sum(((X[:, rule["support"]] - rule["center"]) / rule["scale"])**2, axis=1)
                        from_rule = ((rule_t > rule["threshold"]).astype(int) if rule["constant_label"] is None
                                     else np.full(len(X), rule["constant_label"]))
                        check(np.array_equal(from_rule, saved), prefix + f": {family} rule replay")
                        if family == "radial2":
                            close(t, predictions[f"{name}__{split}__squared_radius"], prefix + ": radius replay")
                    metric = row["metrics"][split]
                    for saved_name, calculated in (("radial2_minus_q0_panel", logs["radial2"] - logq),
                                                   ("radial2_minus_radial1", logs["radial2"] - logs["radial1"])):
                        close(calculated, predictions[f"{name}__{split}__{saved_name}"], prefix + ": gain vector " + saved_name)
                        close(calculated.mean(), metric[saved_name], prefix + ": gain metric " + saved_name)
                    # Native comparator predictions independently from their saved state.
                    baseline = row["models"]["baselines"]
                    z = (X[:, S] - baseline["scaler"]["mean"]) / baseline["scaler"]["scale"]
                    centers = np.asarray(baseline["kmeans2"]["centers_standardized"])
                    centroid = np.argmin(np.sum((z[:, None, :] - centers)**2, axis=2), axis=1)
                    check(np.array_equal(centroid, predictions[f"{name}__{split}__kmeans2"]), prefix + ": centroid replay")
                    for k in (1, 2):
                        g = baseline[f"diagonal_gmm{k}"]
                        variance = np.asarray(g["variances_standardized"])
                        density = (-.5 * (d * np.log(2*np.pi) + np.log(variance).sum(1)
                                          + np.sum((z[:, None, :] - g["means_standardized"])**2 / variance, axis=2))
                                   + np.log(g["weights"]))
                        check(np.array_equal(np.argmax(density, axis=1), predictions[f"{name}__{split}__diagonal_gmm{k}"]),
                              prefix + f": gmm{k} replay")
                    for family in ("radial2", "kmeans2", "diagonal_gmm1", "diagonal_gmm2"):
                        reported = metric["labels"][family]["ari"]
                        if reported is not None:
                            close(adjusted_rand_score(y, predictions[f"{name}__{split}__{family}"]), reported, prefix + f": {family} ARI")
            chosen = max(range(len(rows)), key=lambda i: (rows[i]["metrics"]["validation"]["common_full_space_gain"], -rows[i]["size"], -i))
            check(rows[chosen]["name"] == result["selected_candidate"], job["name"] + ": validation selection replay")
            check(rows[chosen]["metrics"] == result["selected_metrics"], job["name"] + ": selected metrics identity")
            check(rows[chosen]["metrics"]["validation"]["heuristic_split_flag"] == result["frozen_validation_heuristic_decision"], job["name"] + ": frozen decision identity")
    return {"status": "passed" if not errors else "failed", "run": str(run), "checks": checks,
            "jobs": len(manifest["jobs"]), "candidates": candidate_count, "errors": errors, "notes": notes,
            "scope": "saved-state numerical, native-rule, metric and selection audit; not an independent experiment or cluster-validity guarantee"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    result = audit(args.run)
    (args.run / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
