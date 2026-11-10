"""Hidden-panel search experiment: freeze on search, diagnose on fresh rows."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
from time import perf_counter

import numpy as np
from sklearn.metrics import adjusted_rand_score

from .radial_diagnostics import generate_synthetic_splits, write_json
from .radial_panels import GaussianBackground, RadialPanel, fit_radial_panel
from .radial_search import search_feature_sets


def describe_panel(model, one_band, background, splits, annotated):
    """Post-selection only; this function cannot alter the frozen search."""
    profile = model.spatial_profile()
    fitted_valley = (profile["two_spatial_modes"] and profile["valley_ratio"] is not None
                     and profile["valley_ratio"] <= .5)
    metrics, predictions = {}, {}
    for split, values in splits.items():
        X, y = values["X"], values["y"]
        prediction = model.predict(X)
        gain = float(np.mean(model.logpdf(X) - background.logpdf_panel(X, model.support)))
        two_vs_one = float(np.mean(model.logpdf(X) - one_band.logpdf(X)))
        counts = np.bincount(prediction, minlength=2)
        smallest = float(counts.min() / len(X))
        metrics[split] = {"gain": gain, "two_vs_one": two_vs_one,
                          "ari": float(adjusted_rand_score(y, prediction)) if annotated else None,
                          "counts": counts.tolist(), "smallest_fraction": smallest,
                          "heuristic_split_flag": bool(gain > 0 and two_vs_one > 0 and fitted_valley and smallest >= .1)}
        predictions[split] = prediction
    return metrics, predictions, profile


def run_search_case(job, directory, progress=None, *, generator=None):
    directory = Path(directory)
    started = perf_counter()
    n = job["n_fit"]
    if "data_source" in job:
        source = job["data_source"]
        parent = Path(source["directory"])
        for filename, hash_key in (("splits.npz", "splits_sha256"), ("job.json", "job_sha256")):
            if hashlib.sha256((parent / filename).read_bytes()).hexdigest() != source[hash_key]:
                raise ValueError(f"saved development input changed: {parent / filename}")
        saved = json.loads((parent / "job.json").read_text(encoding="utf-8"))
        for key in ("case", "dimension", "p", "seed", "search_seed", "n_fit", "n_search", "n_validation", "n_test", "max_size"):
            if saved["job"][key] != job[key]:
                raise ValueError(f"saved development configuration differs: {key}")
        generated = saved["generator"]
        with np.load(parent / "splits.npz", allow_pickle=False) as archive:
            splits = {split: {field: archive[f"{split}_{field}"].copy() for field in ("X", "y")}
                      for split in ("fit", "search", "validation", "test")}
        for split, block in splits.items():
            if block["X"].shape != (job["n_" + split], job["p"]) or block["y"].shape != (job["n_" + split],):
                raise ValueError(f"saved {split} block shape differs")
        shutil.copyfile(parent / "splits.npz", directory / "splits.npz")
        shutil.copyfile(parent / "job.json", directory / "source_job.json")
        if hashlib.sha256((directory / "splits.npz").read_bytes()).hexdigest() != source["splits_sha256"]:
            raise ValueError("development data changed while copying")
    else:
        generated = (generator or generate_synthetic_splits)(job["case"], job["dimension"], job["p"],
                                             job["n_fit"] + job["n_search"], job["n_validation"],
                                             job["n_test"], job["seed"])
        original = generated.pop("splits")
        splits = {"fit": {key: values[:n] for key, values in original["fit"].items()},
                  "search": {key: values[n:] for key, values in original["fit"].items()},
                  "validation": original["validation"], "test": original["test"]}
        np.savez_compressed(directory / "splits.npz", **{f"{s}_{k}": v for s, block in splits.items() for k, v in block.items()})
    write_json(directory / "job.json", {"job": job, "generator": generated,
               "search_input": "fit and search matrices, size cap, budget, method, independent search seed only",
               "validation_role": "independent diagnostics of frozen selected panel; no reselection or refit",
               "test_role": "external descriptive evaluation only; no selection",
               "fit_search_split": f"first {n} rows of generated fit block fit models; remaining rows guide search"})
    reports, arrays = {}, {}
    for method in job["methods"]:
        if progress:
            progress(f"{method}: {job['budget']} unique feature-set fits")
        # Deliberately pass ONLY matrices and generic search configuration.
        result = search_feature_sets(splits["fit"]["X"], splits["search"]["X"], method=method,
                               budget=job["budget"], max_size=job["max_size"], seed=job["search_seed"])
        write_json(directory / f"{method}_search.json", result)
        model = RadialPanel.from_dict(result["model"])
        saved = result["background"]
        background = GaussianBackground(np.asarray(saved["mean"]), np.asarray(saved["covariance"]),
                                        saved["shrinkage"], np.asarray(saved["scale"]))
        one_band = fit_radial_panel(splits["fit"]["X"], model.support, components=1)
        metrics, predictions, profile = describe_panel(model, one_band, background, splits,
                                                     job["case"] in {"shells", "quartic_shells", "mean_shift"})
        # Support truth is read only AFTER search has returned its frozen result.
        found, truth = set(result["selected_support"]), set(generated["support"])
        report = {"method": method, "selected_support": sorted(found), "selected_size": len(found),
                  "selected_index": result["selected_index"], "evaluations": result["evaluations"],
                  "search_seconds": result["seconds"], "preprocessing_seconds": result["preprocessing_seconds"],
                  "support_exact": found == truth, "support_precision": len(found & truth) / len(found),
                  "support_recall": len(found & truth) / len(truth),
                  "oracle_evaluated_naturally": any(set(row["support"]) == truth for row in result["trace"]),
                  "metrics": metrics, "model": result["model"], "one_band_model": one_band.to_dict(),
                  "spatial_profile": profile, "background": result["background"],
                  "frozen_validation_flag": metrics["validation"]["heuristic_split_flag"],
                  "optimizer_nonconvergence": sum(row["optimizer_success"] is False for row in result["trace"])}
        reports[method] = report
        for split, prediction in predictions.items():
            arrays[f"{method}__{split}"] = prediction
        write_json(directory / f"{method}_result.json", report)
        np.savez_compressed(directory / "predictions.npz", **arrays)
    # The supplied-support diagnostic is evaluated AFTER every search arm.
    # Its cost is separate and it never seeds the search cache.
    oracle_started = perf_counter()
    truth = generated["support"]
    Xfit = splits["fit"]["X"]
    background = GaussianBackground.fit(Xfit)
    oracle = fit_radial_panel(Xfit, truth, components=2)
    one = fit_radial_panel(Xfit, truth, components=1)
    metrics, predictions, profile = describe_panel(oracle, one, background, splits,
                                                 job["case"] in {"shells", "quartic_shells", "mean_shift"})
    for split, prediction in predictions.items():
        arrays[f"oracle__{split}"] = prediction
    np.savez_compressed(directory / "predictions.npz", **arrays)
    for report in reports.values():
        report["oracle_search_gain_gap"] = metrics["search"]["gain"] - report["metrics"]["search"]["gain"]
        report["oracle_validation_gain_gap"] = metrics["validation"]["gain"] - report["metrics"]["validation"]["gain"]
        report["oracle_test_ari"] = metrics["test"]["ari"]
        write_json(directory / f"{report['method']}_result.json", report)
    result = {"job": job, "generator": generated, "methods": reports,
              "oracle": {"support": truth, "metrics": metrics, "model": oracle.to_dict(),
                         "one_band_model": one.to_dict(), "spatial_profile": profile,
                         "background": background.to_dict(), "seconds": perf_counter() - oracle_started},
              "seconds": perf_counter() - started,
              "scope": "unknown-support search with a separate post-search oracle diagnostic; development evidence only"}
    write_json(directory / "result.json", result)
    return result


def write_search_summary(directory, reports):
    directory = Path(directory)
    rows = []
    for report in reports:
        job = report["job"]
        for name, method in report["methods"].items():
            row = {"job": job["name"], "case": job["case"], "dimension": job["dimension"],
                   "p": job["p"], "seed": job["seed"], "search_seed": job["search_seed"], "method": name,
                   **{key: method[key] for key in ("selected_size", "support_exact", "support_precision", "support_recall",
                      "oracle_evaluated_naturally", "evaluations", "search_seconds", "preprocessing_seconds",
                      "optimizer_nonconvergence", "oracle_search_gain_gap", "oracle_validation_gain_gap", "oracle_test_ari")},
                   "selected_support": method["selected_support"]}
            if "condition" in job:
                row["condition"] = job["condition"]
            for split in ("search", "validation", "test"):
                row.update({f"{split}_{key}": method["metrics"][split][key] for key in ("gain", "ari", "heuristic_split_flag")})
            rows.append(row)
    write_json(directory / "summary.json", {"completed_jobs": len(reports), "rows": rows})
    if rows:
        with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    ablation = any("data_source" in report["job"] for report in reports)
    lines = ["# Interpretable feature-set search", "",
             "Development comparison: all arms have equal unique feature-set fits, the same size cap, and no supplied support. "
             "Random/local and dependence/local use half their budget for proposals and the remainder for identical add/drop/swap refinement. "
             "The dependence proposal uses fit-only absolute squared-coordinate correlation; its extra preprocessing and wall time are recorded.", "",
             "Shuffled-dependence local search permutes the feature identities of the dependence matrix before building the same chains. "
             "It preserves the matrix values and proposal procedure while breaking their association with the measurements. "
             "Evaluated size histograms are saved for every arm. The ordinary random/local comparison alone does not isolate the statistic from chain structure.", "",
             "Models fit on fit rows; adaptive search and final feature-set choice use search rows. Validation and test are excluded from this selection. "
             "The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. "
             "Exact support recovery is not meaningful for control cases with no special planted cluster support. "
             "This is not a comparison with established sparse-clustering methods or evidence of novelty.", "",
             "| Job | Method | Feature set | Exact support | Oracle visited | Search gain | Val gain | Test ARI | Val flag | Fits | Seconds |",
             "|---|---|---|---|---|---|---|---|---|---:|---:|"]
    if ablation:
        lines[2:6] = [
            "Controlled 2x2 development comparison: squared-correlation versus nonlinear kernel proposals, crossed with best-improvement versus first-improvement refinement. "
            "Every arm has the same unique-fit budget, model, fitness, size cap and initial random candidates. "
            "For a given dependence statistic, both refinement variants share all exploration candidates.", "",
            "Raw data are copied byte-for-byte from the audited preceding pilot; their hashes and original metadata are retained. "
            "These previously inspected validation/test blocks are reused development evidence, not fresh confirmation. "
            "Kernel similarities use fitting observations only; the original-feature assignment rule is unchanged. "
            "Kernel preprocessing costs and optimizer status are recorded separately from unique fit counts.", ""]
    elif reports and all(report["job"].get("experiment") == "feature_set_replication" for report in reports):
        lines[2:6] = [
            "Frozen candidate replication/stress comparison: moment_best versus kernel_best, with identical predictive fitness, "
            "original-feature rules and unique-fit budgets. Data seeds are separate from development and smoke seeds. "
            "Each full-run population is searched with two independently specified search seeds.", "",
            "Conditions are baseline replication, more nuisance measurements, weaker shell separation, and two dependent Gaussian nuisance blocks. "
            "Repeated search seeds reuse the same observations and are not independent data replications. Report each condition separately. "
            "The smoke suite checks execution only and uses a reduced budget on separate seeds.", ""]
    for row in rows:
        ari = "—" if row["test_ari"] is None else f"{row['test_ari']:.3f}"
        lines.append(f"| {row['job']} | {row['method']} | {row['selected_support']} | {row['support_exact']} | "
                     f"{row['oracle_evaluated_naturally']} | {row['search_gain']:.3f} | {row['validation_gain']:.3f} | "
                     f"{ari} | {row['validation_heuristic_split_flag']} | {row['evaluations']} | {row['search_seconds']:.2f} |")
    (directory / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
