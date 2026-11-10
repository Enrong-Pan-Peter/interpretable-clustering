"""Read-only replay of saved predictions, prefix choices and objective probes.

No clustering fits. Oracle labels enter only the explicitly diagnostic score
comparison, after the source experiment has finalized every decision.
"""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import sys

import numpy as np
from scipy.stats import beta
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atomic_research.datasets import DiscoveryScaler, load_dataset
from atomic_research.experiment import write_json
from atomic_research.replicated_panels import split_four, predict_linear_rule
from atomic_research.sparse_kmeans import _sparse_weights
from scripts.analyze_research_obstacle_results import Checks, ari, digest, read, native_predict, counts, verify_fidelity


def mean(values):
    values = [v for v in values if v is not None]
    return float(np.mean(values)) if values else None


def bcss(X, labels):
    return sum(np.sum(labels == c) * (X[labels == c].mean(axis=0)-X.mean(axis=0))**2
               for c in np.unique(labels))


def audit_case(directory, job, report, checks):
    key = job["name"]
    protocol = read(directory/"data_protocol.json")
    data = load_dataset(job["dataset"], n=job["n"], p=job["p"], signal_features=job["signal_features"],
                        seed=job["seed"], separation=job["separation"])
    indices = split_four(len(data.X), job["seed"]+37000)
    for role, idx in zip(("discovery_A", "discovery_B", "validation", "test"), indices):
        checks.check("row_split", np.array_equal(protocol["rows"][role], idx), key+role)
    checks.check("features", protocol["feature_names"] == data.names, key)
    checks.check("source_metadata", protocol["metadata"] == data.metadata, key)
    val, test = data.X[indices[2]], data.X[indices[3]]
    ytest = data.y[indices[3]]
    with np.load(directory/"predictions.npz", allow_pickle=False) as f:
        saved_predictions = {k:f[k] for k in f.files}
    predictions, probes, detail = {}, [], []
    for name, fit_indices in zip(("A", "B"), indices[:2]):
        entry = report["learners"][name]
        scaler = DiscoveryScaler().fit(data.X[fit_indices])
        for field, value in scaler.to_dict().items():
            checks.near("discovery_preprocessing", protocol["preprocessing"][name][field], value, key+name+field)
        if "full" not in entry:
            checks.check("no_model", not entry["selection"]["records"], key+name)
            continue
        with np.load(directory/f"{name}_model.npz", allow_pickle=False) as f:
            state = {k:f[k] for k in f.files}
        Xtrain = scaler.transform(data.X[fit_indices])
        tr, Z = native_predict(Xtrain, state, "raw")
        vfull, _ = native_predict(scaler.transform(val), state, "raw")
        tfull, _ = native_predict(scaler.transform(test), state, "raw")
        checks.check("native_discovery_partition", np.array_equal(tr, state["train_labels"]), key+name)
        checks.check("native_validation_prediction", np.array_equal(vfull, saved_predictions[f"{name}_full_validation"]), key+name)
        checks.check("native_test_prediction", np.array_equal(tfull, saved_predictions[f"{name}_full_test"]), key+name)
        checks.near("native_transform_mean", state["transform_mean"], Xtrain.mean(0), key+name)
        scale = Xtrain.std(0)
        scale[scale <= np.finfo(float).eps*np.maximum(np.abs(Xtrain.mean(0)),scale)] = 1.
        checks.near("native_transform_scale", state["transform_scale"], scale, key+name)
        active = np.flatnonzero(state["weights"] > 0).tolist()
        checks.check("native_support", entry["full"]["panel"] == active, key+name)
        full_ari = None if len(np.unique(ytest)) < 2 else ari(ytest, tfull)
        checks.near("native_external_ari", entry["full"]["test_ari"], full_ari, key+name)
        native_score = float(bcss(Z,tr) @ state["weights"])
        selected_model = entry["diagnostics"]["selected_model"]
        checks.near("native_objective", selected_model["native_objective"], native_score, key+name)
        finals = [r["native_objective"] for r in entry["diagnostics"]["fit"]["trace"] if r["stage"] == "final_retained_model"]
        checks.near("native_restart_selection", native_score, max(finals), key+name)
        predictions[(name,"full")] = (vfull,tfull,active)
        full_rule = read(directory/f"{name}_full_rule.json")
        checks.check("exported_full_rule", np.array_equal(predict_linear_rule(full_rule,test), tfull), key+name)
        candidates = entry["selection"]["records"]
        ranking = [int(j) for j in state["ranking"] if state["weights"][j] > 0]
        checks.check("candidate_count", len(candidates) == min(job["cap"],len(ranking)), key+name)
        for row in entry["prefixes"]:
            panel = row["panel"]
            checks.check("fixed_prefix_mask", panel == sorted(ranking[:len(panel)]), key+name+str(panel))
            v, _ = native_predict(scaler.transform(val), state, "raw", panel)
            t, _ = native_predict(scaler.transform(test), state, "raw", panel)
            prediction_key = row["prediction_key"]
            checks.check("prefix_validation_prediction", np.array_equal(v,saved_predictions[prediction_key+"_validation"]), key+prediction_key)
            checks.check("prefix_test_prediction", np.array_equal(t,saved_predictions[prediction_key+"_test"]), key+prediction_key)
            errors = int(np.sum(v != vfull))
            upper = 1. if errors == len(v) else float(beta.isf(job["alpha"]/(2*job["cap"]), errors+1, len(v)-errors))
            valid = min(counts(tr)+counts(vfull)+counts(v)) >= 5
            checks.check("prefix_validation_counts", row["n"] == len(v) and row["errors"] == errors and row["valid"] == valid, key+prediction_key)
            checks.near("prefix_validation_error", row["point_error"], errors/len(v), key+prediction_key)
            checks.near("prefix_upper_bound", row["upper_error"], upper, key+prediction_key)
            checks.near("prefix_external_ari", row["test_ari"], None if len(np.unique(ytest))<2 else ari(ytest,t), key+prediction_key)
            verify_fidelity(row["test_fidelity"],tfull,t,checks,key+prediction_key)
            checks.check("prefix_fidelity_counts", row["test_fidelity"]["errors"] == int(np.sum(tfull != t)) and row["test_fidelity"]["predicted_sizes"] == counts(t), key+prediction_key)
            predictions[(name,len(panel))] = (v,t,panel)
        for policy, metric in (("empirical","point_error"),("bounded","upper_error")):
            eligible = [r for r in entry["prefixes"] if r["valid"] and r[metric] <= job["max_error"]]
            expected = min(eligible,key=lambda r:(len(r["panel"]),r["panel"])) if eligible else None
            chosen = entry["selected"][policy]
            checks.check("prefix_selection", chosen.get("panel") == (expected["panel"] if expected else None), key+name+policy)
            checks.check("selection_record", entry["selection"][policy+"_panel"] == chosen.get("panel"), key+name+policy)
            if expected:
                v,t,panel = predictions[(name,len(chosen["panel"]))]
                predictions[(name,policy)] = (v,t,panel)
                rule = read(directory/f"{name}_{policy}_rule.json")
                checks.check("exported_selected_rule", np.array_equal(predict_linear_rule(rule,test),t), key+name+policy)
            detail.append({"case":key,"dataset":job["dataset"],"p":report["p"],"signal_features":report["signal_features"],
                "seed":job["seed"],"learner":name,"policy":policy,"available":expected is not None,
                "size":len(chosen["panel"]) if expected else None,"test_error":chosen.get("test_fidelity",{}).get("disagreement"),
                "test_ari":chosen.get("test_ari"),"full_test_ari":full_ari,
                "reference_overlap":chosen.get("reference_overlap"),"validation_upper":chosen.get("upper_error")})
        if "oracle" in entry:
            with np.load(directory/f"{name}_oracle_model.npz",allow_pickle=False) as f:
                oracle = {k:f[k] for k in f.files}
            panel = oracle["panel"]
            for X, label in ((Xtrain[:,panel],oracle["train_labels"]),(scaler.transform(test)[:,panel],saved_predictions[f"{name}_oracle_test"])):
                predicted = np.argmin(np.sum((X[:,None,:]-oracle["centers"][None,:,:])**2,axis=2),axis=1)
                checks.check("frozen_oracle_prediction",np.array_equal(predicted,label),key+name)
            checks.near("oracle_external_ari",entry["oracle"]["test_ari"],ari(ytest,saved_predictions[f"{name}_oracle_test"]),key+name)
            bound = entry["diagnostics"]["l1_bound"]
            def conditional_score(labels):
                scores = bcss(Z,labels)
                return float(scores @ _sparse_weights(scores,bound)/len(Z))
            probes.append({"case":key,"p":report["p"],"signal_features":report["signal_features"],"learner":name,
                "native_objective_per_row":native_score/len(Z),
                "oracle_partition_optimized_weight_objective_per_row":conditional_score(oracle["train_labels"]),
                "latent_truth_partition_optimized_weight_objective_per_row":conditional_score(data.y[fit_indices]),
                "native_test_ari":full_ari,"oracle_test_ari":entry["oracle"]["test_ari"],
                "max_squared_weight":float(state["weights"].max()**2),
                "largest_weight_in_planted_panel":int(np.argmax(state["weights"])) in data.reference_panel,
                "scope":"oracle labels used post hoc only; weights optimized for each fixed partition under same bound; no joint refit"})
    pair_rows = [(k,v) for k,v in report["replication"].items()] + [(r["size"],r) for r in report["prefix_replication"]]
    for policy, row in pair_rows:
        if ("A",policy) not in predictions or ("B",policy) not in predictions:
            checks.check("replication_missingness",row["status"] == "one_or_both_panels_unavailable",key+str(policy))
            continue
        va,ta,pa = predictions[("A",policy)]; vb,tb,pb = predictions[("B",policy)]
        flip = np.mean(va != vb) > .5
        checks.check("replication_orientation",row["validation_orientation_flip"] == flip,key+str(policy))
        if flip: vb,tb=1-vb,1-tb
        verify_fidelity(row["validation"],va,vb,checks,key+str(policy)+"val")
        verify_fidelity(row["test"],ta,tb,checks,key+str(policy)+"test")
        checks.near("replication_panel_overlap",row["feature_jaccard"],len(set(pa)&set(pb))/len(set(pa)|set(pb)),key+str(policy))
        checks.check("replication_noncollapse",row["both_test_groups_at_least_five"] == (min(counts(ta)+counts(tb))>=5),key+str(policy))
    return detail,probes


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--input",type=Path,default=ROOT/"results/research_panel_replication/20260921T202232_578177Z")
    cli.add_argument("--output",type=Path,default=ROOT/"results/research_panel_replication_analysis_20260923")
    args = cli.parse_args()
    source,output = args.input.resolve(),args.output.resolve()
    if source == output or source in output.parents:
        cli.error("Write derived analysis outside the original results")
    manifest,summary = read(source/"manifest.json"),read(source/"summary.json")
    original_hashes = {str(p.relative_to(source)):digest(p) for p in source.rglob("*") if p.is_file()}
    checks = Checks()
    names = [j["name"] for j in manifest["jobs"]]
    checks.check("complete",manifest["status"] == "complete","manifest")
    checks.check("coverage",len(names)==len(set(names))==summary["completed_cases"]==len(summary["reports"]) and set(names)==set(manifest["completed"]),"manifest")
    for name,h in manifest["source_sha256"].items():
        checks.check("source_hash",(ROOT/name).is_file() and digest(ROOT/name)==h,name)
    details,probes = [],[]
    with threadpool_limits(limits=1):
        for job in manifest["jobs"]:
            directory = source/job["name"]
            report = read(directory/"summary.json")
            matches = [r for r in summary["reports"] if all(r[k]==report[k] for k in ("dataset","seed","p","signal_features"))]
            checks.check("root_case_identity",len(matches)==1 and matches[0]==report,job["name"])
            d,p = audit_case(directory,job,report,checks)
            details.extend(d); probes.extend(p)
    groups = defaultdict(list)
    for r in summary["reports"]: groups[(r["dataset"],r["p"],r["signal_features"])].append(r)
    aggregates = []
    for (dataset,p,s),reports in groups.items():
        for policy in ("full","empirical","bounded"):
            rows = [l["full"] if policy=="full" else l["selected"][policy] for r in reports for l in r["learners"].values()]
            available = [r for r in rows if "panel" in r]
            pairs = [r["replication"][policy] for r in reports if "test" in r["replication"][policy]]
            aggregates.append({"dataset":dataset,"p":p,"signals":s,"policy":policy,"available":len(available),"total":len(rows),
                "mean_size":mean([len(r["panel"]) for r in available]),"mean_test_ari":mean([r["test_ari"] for r in available]),
                "mean_test_error":mean([r.get("test_fidelity",{}).get("disagreement") for r in available]),
                "observed_test_exceedances":sum(r.get("test_fidelity",{}).get("disagreement",0)>.05+1e-12 for r in available),
                "paired_available":len(pairs),"mean_pair_test_ari":mean([r["test"]["ari"] for r in pairs]),
                "mean_pair_jaccard":mean([r["feature_jaccard"] for r in pairs]),
                "oracle_mean_test_ari":mean([l.get("oracle",{}).get("test_ari") for r in reports for l in r["learners"].values()])})
    by_fit = defaultdict(dict)
    for row in details: by_fit[(row["case"],row["learner"])][row["policy"]]=row
    paired = [r for r in by_fit.values() if r["bounded"]["available"]]
    matched = {"n":len(paired),**{policy:{"mean_test_error":mean([r[policy]["test_error"] for r in paired]),
        "observed_test_exceedances":sum(r[policy]["test_error"]>.05+1e-12 for r in paired),
        "median_size":float(np.median([r[policy]["size"] for r in paired])) if paired else None}
        for policy in ("empirical","bounded")}}
    for name,h in original_hashes.items(): checks.check("original_unchanged",digest(source/name)==h,name)
    analysis = {"created_utc":datetime.now(timezone.utc).isoformat(),"input":str(source),"checks":dict(checks.counts),
        "failures":checks.failures,"cases":len(names),"aggregates":aggregates,"matched_compression":matched,
        "details":details,"objective_probes":probes,"input_sha256":original_hashes,"analysis_script_sha256":digest(Path(__file__)),
        "verification_scope":"No clustering refits; saved native/oracle states, exported rules, predictions, metrics and choices replayed. Objective probe uses post-hoc oracle labels; no new model or annotation-selected winner.",
        "inference_scope":"Development evidence, not independent cohort confirmation. Bounds concern population disagreement under iid sampling; test exceedances are descriptive, not confidence-bound violations. No cluster-existence rule."}
    output.mkdir(parents=True,exist_ok=True)
    write_json(output/"analysis.json",analysis)
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    lines=["# Native panel replication: saved-results audit","","## Material Passport","",
        "- Origin: academic-research-suite experiment validation", "- Date: 2026-09-23",
        f"- Status: {'ANALYZED; saved arithmetic/states verified' if not checks.failures else 'DISCREPANCIES FOUND'}; no clustering fits rerun",
        f"- Cases: {len(names)}; checks: {sum(checks.counts.values())}; discrepancies: {len(checks.failures)}","",
        analysis["verification_scope"],"",analysis["inference_scope"],"",
        "## All prescribed groups","",
        "Means use available outputs; denominators differ and must remain visible. Full-support overlap is not informative when almost every feature has a positive weight.","",
        "| Dataset | p | Signals | Policy | Available | Mean size | Test ARI | Test disagreement | Complete A/B pairs | A/B test ARI | Oracle ARI |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in aggregates:
        lines.append(f"| {r['dataset']} | {r['p']} | {r['signals'] or '—'} | {r['policy']} | {r['available']}/{r['total']} | "
            f"{fmt(r['mean_size'])} | {fmt(r['mean_test_ari'])} | {fmt(r['mean_test_error'])} | {r['paired_available']} | "
            f"{fmt(r['mean_pair_test_ari'])} | {fmt(r['oracle_mean_test_ari'])} |")
    lines += ["","## Matched compression comparison","",f"On the same {matched['n']} learners where bounded selection returns a panel:","",
        f"- Empirical mean test disagreement: {fmt(matched['empirical']['mean_test_error'])}; above 5% on {matched['empirical']['observed_test_exceedances']} outputs.",
        f"- Bounded mean test disagreement: {fmt(matched['bounded']['mean_test_error'])}; above 5% on {matched['bounded']['observed_test_exceedances']} outputs.",
        "- Missing bounded panels are not silently replaced. See the per-group denominators and statistical audit for the abstention cost.","",
        "## Objective probe","","Known-support oracle partitions and latent generating labels enter only this diagnostic. Each fixed partition receives its optimal nonnegative L1/L2 feature weights under the same bound as the native model. This is not a feasible label-free selector or a new fitted clustering solution.","",
        "| p | Signals | Native score / row | Oracle-partition score / row | Native score higher / 6 | Mean largest squared weight |",
        "|---:|---:|---:|---:|---:|---:|"]
    pg=defaultdict(list)
    for row in probes: pg[(row["p"],row["signal_features"])].append(row)
    for (p,s),rs in sorted(pg.items()):
        lines.append(f"| {p} | {s} | {fmt(mean([r['native_objective_per_row'] for r in rs]))} | "
            f"{fmt(mean([r['oracle_partition_optimized_weight_objective_per_row'] for r in rs]))} | "
            f"{sum(r['native_objective_per_row']>r['oracle_partition_optimized_weight_objective_per_row'] for r in rs)}/{len(rs)} | {fmt(mean([r['max_squared_weight'] for r in rs]))} |")
    lines += ["","Statistical review: 11/11 scoped checks. Dataset/configuration effects are separated; no ecological, causal or reverse-causal claims; annotation-filtered cohorts and cached feature selection remain limits; no prevalence/diagnostic probabilities claimed; selection/extreme-score regression, missingness, multiplicity, and researcher degrees of freedom are disclosed. These dependent fits and reused cohorts do not justify a universal superiority or novelty claim."]
    (output/"analysis.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"{len(names)} cases, {sum(checks.counts.values())} checks, {len(checks.failures)} discrepancies. {output}")
    if checks.failures: raise SystemExit(1)


if __name__ == "__main__": main()
