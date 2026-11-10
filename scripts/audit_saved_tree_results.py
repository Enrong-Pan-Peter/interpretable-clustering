"""Recompute metrics from saved Levine tree counts without fitting any models.

These are IN-SAMPLE results. The experimental tree builders use reference labels
to stop at a single population, so some leaves are ORACLE STOPPED. This audit does
not establish label-free stopping, held-out transfer, or biological discovery.

Final-partition ARI needs only a population-by-leaf contingency table. The saved
`went.left` / `went.right` counts supply it exactly; every node count and every
parent/child population count is checked before calculating metrics. No SciPy or
scikit-learn is needed. NumPy is used only for the isolated control-flow probe.

Run from any directory:
    python scripts/audit_saved_tree_results.py

The label-control probe executes the actual `present` and `split_node` functions
extracted from their source, with expensive search replaced by a recording stub.
It holds X fixed and changes the reference labels, demonstrating whether labels
can change the decision to search. It does not rerun the clustering experiment.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parents[1]


def choose_two(n):
    return n * (n - 1) / 2


def audit_tree(path):
    source_bytes = path.read_bytes()
    tree = json.loads(source_bytes.decode("utf-8"))
    internal, leaves, contingency = [], [], []

    def walk(node, incoming=None):
        if incoming is not None:
            assert sum(incoming.values()) == node["n"], (path, node["id"])
        if node["leaf"]:
            leaves.append(node)
            if incoming is not None:
                contingency.append(incoming)
            return
        internal.append(node)
        counts = Counter(node["went"]["left"]) + Counter(node["went"]["right"])
        assert sum(counts.values()) == node["n"], (path, node["id"])
        if incoming is not None:
            assert counts == Counter(incoming), (path, node["id"], "population mismatch")
        assert len(node["children"]) == 2
        for child, side in zip(node["children"], ("left", "right")):
            walk(child, node["went"][side])

    walk(tree)
    # Stability files keep the split measurements inside `consensus`.
    def measurements(node):
        return node.get("consensus", node)

    measures = [measurements(node) for node in internal]
    purities = [m["purity"] for m in measures]
    checkable = [m for m in measures if m.get("boundary")]
    minimality = [n["minimality"] for n in internal if n.get("minimality")]
    result = {
        "file": path.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "saved_config": tree.get("_config"),
        "n": tree["n"],
        "internal_nodes": len(internal),
        "leaves": len(leaves),
        "mean_node_population_retention": sum(purities) / len(purities) if purities else None,
        "worst_node_population_retention": min(purities) if purities else None,
        "nodes_below_0_90_retention": sum(p < 0.9 for p in purities),
        "canonical_primary_hits": sum(m.get("primary_hit", False) for m in checkable),
        "checkable_boundaries": len(checkable),
        "panels_assessed_for_drop_one": len(minimality),
        "drop_one_retention_cost_le_0_005": sum(m["cost_of_dropping"] <= 0.005 for m in minimality),
        "leaf_reasons": dict(Counter(n["reason"] for n in leaves)),
        "final_partition": None,
    }
    if contingency:
        populations = Counter()
        for counts in contingency:
            populations.update(counts)
        n = sum(populations.values())
        assert n == tree["n"]
        row_sum = sum(choose_two(sum(c.values())) for c in contingency)
        col_sum = sum(choose_two(c) for c in populations.values())
        observed = sum(choose_two(c) for counts in contingency for c in counts.values())
        expected = row_sum * col_sum / choose_two(n)
        denominator = (row_sum + col_sum) / 2 - expected
        ari = (observed - expected) / denominator if denominator else 1.0
        best_f1 = {
            population: max(2 * counts.get(population, 0) /
                            (total + sum(counts.values())) for counts in contingency)
            for population, total in populations.items()
        }
        result["final_partition"] = {
            "ari": ari,
            "leaf_purity": sum(max(c.values()) for c in contingency) / n,
            "macro_best_leaf_f1": sum(best_f1.values()) / len(best_f1),
            "best_leaf_f1_by_population": dict(sorted(best_f1.items())),
            "population_totals": dict(sorted(populations.items())),
            "contingency_counts": contingency,
        }
    else:
        result["unavailable_reason"] = "Root is a leaf; saved file has no population count table."
    return result


def label_control_probe():
    import numpy as np

    path = ROOT / "scripts" / "run_levine_tree.py"
    source = ast.parse(path.read_text(encoding="utf-8"))
    extracted = ast.Module(body=[node for node in source.body
                                if isinstance(node, ast.FunctionDef)
                                and node.name in ("present", "split_node")], type_ignores=[])
    calls = []

    def search_stub(*args, **kwargs):
        calls.append(True)
        return []

    context = dict(np=np, time=time, LEVINE_POPULATIONS=["A", "B"], MIN_CELLS=60,
                   MIN_POP=3, MIN_POP_FRAC=0.02, TERMS={"graphcut": None},
                   grow_from_pairs=search_stub)
    exec(compile(extracted, str(path), "exec"), context)
    X = np.random.default_rng(4).normal(size=(100, 2))
    config = dict(depth=2, term="graphcut", split_term="graphcut", seeds=1,
                  max_size=2, B=5, jobs=1)
    findings = []
    for condition, labels in [("constant_reference_labels", np.zeros(100, dtype=int)),
                              ("balanced_reference_labels", np.arange(100) % 2)]:
        calls.clear()
        result = context["split_node"](X, labels, np.arange(100), ["x1", "x2"],
                                       0, "root", config, lambda message: None)
        findings.append(dict(condition=condition, reason=result["reason"], search_calls=len(calls)))
    assert findings[0]["search_calls"] == 0 and findings[1]["search_calls"] == 1
    return dict(source="scripts/run_levine_tree.py", fixed_X_shape=[100, 2],
                source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                method="Actual source functions with search stub; no clustering fitted",
                label_independent_control_flow=False, conditions=findings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / f"audit_saved_tree_results_{date.today()}.json")
    args = parser.parse_args()
    files = sorted((ROOT / "results").glob("levine_tree*.json"))
    files += sorted((ROOT / "results").glob("levine_stability*.json"))
    report = {
        "caveat": "In-sample saved trees; reference labels influence stopping. No held-out validation.",
        "node_metric_note": "Node purity measures population retention, not final clustering quality.",
        "macro_f1_note": "For each reference population choose its best leaf F1, then average equally. This is a diagnostic, not one-to-one matching.",
        "trees": [audit_tree(path) for path in files],
        "label_control_probe": label_control_probe(),
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for result in report["trees"]:
        final = result["final_partition"]
        if final:
            print(f"{Path(result['file']).name}: ARI={final['ari']:.4f}; "
                  f"leaf purity={final['leaf_purity']:.4f}; "
                  f"macro best-leaf F1={final['macro_best_leaf_f1']:.4f}")


if __name__ == "__main__":
    main()
