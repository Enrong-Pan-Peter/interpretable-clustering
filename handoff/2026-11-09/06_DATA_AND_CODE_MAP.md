# Data and code map

All paths below are relative to `repository/` inside the ZIP. The inventory records exact included files, sizes and SHA-256 hashes.

## Code generations

| Area | Purpose and important files |
|---|---|
| Original implementation | `atomic.py`, `combine.py`, synthetic generators, `ATOMIC-interpretable-clustering.pdf`, `2d_data/`. Historical starting point. |
| ATOMIC+ | `atomicplus/engine.py`, `fitness.py`, `persistence.py`, `tree.py`, `gate.py`, operators, NSGA-II/novelty machinery, datasets and evaluation modules. The legacy tree does not silently incorporate later research models. |
| September research harness | `atomic_research/experiment.py`, `scoring.py`, `search.py`, `soft_graph.py`, `sparse_kmeans.py`, `calibration.py`, `datasets.py`. Separate controlled experiments. |
| Native models/compression | `retained_models.py`, `obstacle_audits.py`, `compression_audit.py`, `replicated_panels.py`, `fidelity_bounds.py`. Model retention, replication and feature reduction. |
| Kernel/projection experiments | `kernel_panels.py`, `kernel_benchmark.py`, `rank_preserved_kernel.py`. Experimental variants, not official GroupFS/DUFS reproductions. |
| Radial model/search | `radial_panels.py`, `radial_diagnostics.py`, `radial_search.py`, `radial_search_experiment.py`, `feature_dependence.py`, `feature_set_replication_data.py`. Latest frozen scientific branch. |
| Run/analyze entrypoints | `scripts/run_research_*.py`, `analyze_research_*.py`, `predict_research_panel.py`. Use `--help` and matching protocol before execution. |
| Tests | `tests/`, including numerical bounds, resume/provenance, saved-state audits, search budgets, scoring and native prediction. |

## Results navigation

The results directories preserve successful, failed, interrupted, smoke and development runs. Temporary pytest-product directories named `research_test_tmp_*` are omitted; genuine smoke runs remain. The machine run index lists manifests and recorded status. A directory timestamp alone is not proof of completion.

For a modern run, begin with `manifest.json`, `summary.md`, `audit.json` and the matching dated assessment. Then inspect individual `result.json`/`job.json` files, fitted models and prediction/data `.npz` arrays. Search logs are valuable for distinguishing a missed support from a rejected support. Source snapshots preserve what actually generated the outputs even when current source differs.

Do not load all candidate JSON files into a language-model prompt. Query them with Python. Large arrays are included for numerical checks, not intended for prose reading.

Legacy flat CSVs are also included when readable. The CSV inventory reports their current fields and counts. Several historical writeups describe broader contents than the currently saved file contains; this is recorded rather than silently filled in.

## Input datasets

| Data | Included material | Main caveat |
|---|---|---|
| Nonconvex shapes | `2d_data/jain.txt`, `flame.txt`, `spiral.txt` and generators | Toy geometry evidence; correct support is sometimes supplied diagnostically. |
| Synthetic research populations | Generators, exact seeds/configs, and all included run split/prediction arrays | Match the specific generator version and statistical unit; reused seeds or data are not fresh replication. |
| UCI datasets | Available cached CSV/raw files | Verify which reference label is used and whether it denotes the intended cluster notion. |
| Human activity recognition | Full `UCI HAR Dataset.zip`, metadata, and extracted files not needlessly duplicating large arrays | 561 engineered variables; official split is by subjects. Overlapping windows from one subject should not cross evaluation splits. Earlier project use makes this development evidence. |
| Mouse protein | Original XLS and cached CSV | 72 animals with 15 replicate rows each. Strip replicate suffixes/aggregate or model grouping. The original row-level result was invalidated. |
| Levine cytometry | `data/Levine_32dim.fcs` | Historical runs include label-based sampling and stopping; cells are not automatically independent donors. Verify donor metadata before a transfer claim. |
| METABRIC | Clinical files, metadata/license, reduced 250-gene table, mutations and case lists | Reduced table includes PAM50 genes plus chosen distractors; selection is not a fully blind full-gene discovery experiment. Four very large assay matrices are omitted and inventoried. |
| Madelon | Available train/validation/test measurements and labels | Binary class labels and geometric groups differ; do not interpret low binary ARI as absence of all recoverable structure. |

The omitted METABRIC files are the full mRNA matrix, its diploid-reference z-scores, methylation matrix and copy-number matrix. Their local paths, byte sizes and readable-file hashes appear in `inventory/omitted_files.json`. Metadata and the original license remain bundled. For re-acquisition, consult the preserved cBioPortal study metadata and source notes; a fresh remote download should be checked against the hash rather than assumed identical.

The HAR ZIP contains the training subject identifiers even though the existing extraction was incomplete. Use the archive as the canonical input. The handoff's independent check counted 7,352 train rows from 21 subjects and 2,947 test rows from 9 different subjects, with no overlap. This is a data-layout check, not a newly trained model result.

## Scope of reproducibility

Full source and substantive outputs make many checks possible. This is not a promise that every old command is portable unchanged: some result metadata uses the original absolute Windows path, some old output files were overwritten, and a few data matrices are intentionally omitted. Keep original evidence unchanged and write any path adaptation or new run into a new location.

Git is not a complete project backup: most thesis files are untracked in the current working tree. The ZIP captures actual files rather than relying on a Git checkout. Git internals and local virtual environments are not bundled.
