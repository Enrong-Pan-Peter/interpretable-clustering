"""ONE-TIME reduction of the METABRIC expression matrix. Run this once, then never touch the big
file again.

WHY
---
`data/brca_metabric/data_mrna_illumina_microarray.txt` is ~689 MB of genes x samples. Nothing in
the pipeline should read it directly: it is too big to hold per candidate subspace, too big to move
between machines, and re-reading it on every run makes experiments slow enough that we would stop
re-running them. This script reads it once and writes a small cached CSV.

WHAT IT KEEPS, AND WHY THAT IS THE EXPERIMENT
---------------------------------------------
Two groups of columns:

  * the PAM50 genes -- the PUBLISHED panel (see atomicplus/datasets/pam50.py). These are the
    planted answer. This is the first time in this project that "did the method name the right
    features?" is answerable on real data rather than being proxied by clustering quality.
  * `--distractors N` non-PAM50 genes as junk, drawn at random with a fixed seed from genes that
    clear a variance floor.

That is deliberately our synthetic setup -- known signal, known junk -- on real data with somebody
else's answer key. Draw the distractors at RANDOM rather than taking the top-N by variance: picking
the most variable junk would make the junk unusually structured, and picking the least variable
would make it unusually easy. Random is the only choice that is not an argument. The variance floor
only removes genes that are flat or near-flat across all patients, which carry no information at
all and would be free wins.

The reduced file is patients x genes (rows = samples) so it matches every other loader.

    python scripts/reduce_metabric.py                      # PAM50 + 200 distractors
    python scripts/reduce_metabric.py --distractors 450    # p=500, matching madelon
    python scripts/reduce_metabric.py --all-genes          # keep everything (large; for variance work)

Output: data/brca_metabric/reduced_pam50_plus<N>.csv  and a sidecar .meta.json recording exactly
which genes were kept, the seed, and how many of the 50 panel genes were actually found. READ THE
MATCH COUNT. A silent 43-of-50 match changes the answer key without telling you.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from atomicplus.datasets.pam50 import PAM50, canonical, expand_aliases  # noqa: E402

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "brca_metabric")
EXPR = os.path.join(RAW, "data_mrna_illumina_microarray.txt")
CLIN = os.path.join(RAW, "data_clinical_patient.txt")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--distractors", type=int, default=200,
                    help="how many non-PAM50 genes to keep as junk (default 200)")
    ap.add_argument("--all-genes", action="store_true", help="keep every gene instead")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--var-floor", type=float, default=0.01,
                    help="drop genes whose variance across patients is below this (default 0.01)")
    args = ap.parse_args()

    if not os.path.exists(EXPR):
        sys.exit(f"ERROR: {EXPR} not found.\n"
                 f"Download study `brca_metabric` from https://www.cbioportal.org/datasets and "
                 f"extract it into data/brca_metabric/.")

    print(f"reading {EXPR} ({os.path.getsize(EXPR) / 1e6:.0f} MB) -- this takes a minute", flush=True)
    # cBioPortal mRNA files are: Hugo_Symbol, Entrez_Gene_Id, then one column per sample.
    expr = pd.read_csv(EXPR, sep="\t", low_memory=False)
    sym_col = "Hugo_Symbol" if "Hugo_Symbol" in expr.columns else expr.columns[0]
    drop = [c for c in ("Hugo_Symbol", "Entrez_Gene_Id") if c in expr.columns]
    expr = expr.dropna(subset=[sym_col])
    genes = expr[sym_col].astype(str).map(canonical)
    values = expr.drop(columns=drop)
    print(f"  {len(expr)} probes x {values.shape[1]} samples", flush=True)

    # Collapse duplicate symbols by mean, so one gene is one column.
    values.index = genes.values
    values = values.apply(pd.to_numeric, errors="coerce").groupby(level=0).mean()
    print(f"  {len(values)} unique gene symbols after collapsing duplicates", flush=True)

    wanted = {canonical(g) for g in expand_aliases()}
    present_panel = sorted(set(values.index) & wanted)
    missing = sorted({canonical(g) for g in PAM50} - set(present_panel))
    print(f"  PAM50 genes found: {len(present_panel)} of 50")
    if missing:
        print(f"  MISSING (answer key is incomplete by this much): {missing}")

    if args.all_genes:
        keep = list(values.index)
        distractors: list[str] = []
    else:
        var = values.var(axis=1, skipna=True)
        pool = [g for g in values.index if g not in present_panel and var.get(g, 0) >= args.var_floor]
        rng = np.random.default_rng(args.seed)
        n_take = min(args.distractors, len(pool))
        if n_take < args.distractors:
            print(f"  WARNING: only {n_take} genes clear the variance floor; asked for "
                  f"{args.distractors}")
        distractors = sorted(rng.choice(np.array(pool, dtype=object), size=n_take, replace=False))
        keep = present_panel + distractors

    out = values.loc[keep].T                      # -> patients x genes
    out.index.name = "SAMPLE_ID"

    clin = pd.read_csv(CLIN, sep="\t", comment="#")
    if "PATIENT_ID" in clin.columns:
        clin = clin.set_index("PATIENT_ID")
    labelled = out.join(clin[["CLAUDIN_SUBTYPE"]], how="inner")
    print(f"  {len(out)} samples in the matrix, {len(labelled)} of them have a subtype call")

    tag = "all" if args.all_genes else f"pam50_plus{len(distractors)}"
    path = os.path.join(RAW, f"reduced_{tag}.csv")
    labelled.to_csv(path)
    meta = {
        "source": os.path.basename(EXPR), "seed": args.seed, "var_floor": args.var_floor,
        "n_samples": int(len(labelled)), "n_genes": int(out.shape[1]),
        "pam50_found": present_panel, "pam50_missing": missing,
        "n_pam50_found": len(present_panel), "distractors": distractors,
        "subtype_counts": labelled.CLAUDIN_SUBTYPE.value_counts(dropna=False).to_dict(),
    }
    with open(path.replace(".csv", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2, default=str)
    print(f"\nwrote {path}  ({os.path.getsize(path) / 1e6:.1f} MB)")
    print(f"      {path.replace('.csv', '.meta.json')}")
    print(f"\nsubtype counts:\n{labelled.CLAUDIN_SUBTYPE.value_counts(dropna=False).to_string()}")
    print("\nNEXT: python scripts/run_one_column_gate.py metabric")
    print("Do not score anything on this dataset until the gate result is in.")


if __name__ == "__main__":
    main()
