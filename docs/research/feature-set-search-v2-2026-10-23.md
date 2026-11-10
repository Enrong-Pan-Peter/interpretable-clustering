# Feature-set search v2: implementing the planned comparison

## Material Passport

- Origin Skill: academic-research-suite, experiment implementation and verification
- Origin Date: 2026-10-23
- Version Label: feature_set_search_v2
- Verification Status at protocol creation: implementation complete; software verification in progress; full ablation not run
- Verification update (2026-10-25): relevant software tests and small end-to-end execution/audit passed; full ablation not run
- Full-run update (2026-10-25, subsequent to the small check): full ablation and independent audit passed; see [results and decision](feature-set-ablation-assessment-2026-10-25.md). The earlier protocol and small-run observations below are preserved.
- Terminology: use **feature sets** in new reports and discussion. Historical artifacts and compatibility identifiers retain their original names.
- Basis: [pilot assessment and bounded design](radial-search-pilot-assessment-2026-10-20.md)
- Scope: development of support discovery for interpretable radial rules; no established novelty or general clustering guarantee

## Implemented changes

The new search offers two independent choices: how feature relationships propose candidate sets, and how refinement reacts to an improvement. The fitted radial density, original-measurement assignment rule, shared Gaussian background, predictive fitness, allowable feature-set sizes and distinct-fit budget are unchanged.

| Variant | Relationship statistic | Refinement |
|---|---|---|
| `moment_best` | Absolute correlation of squared standardized measurements | Complete the current neighborhood before following its best improvement |
| `moment_first` | Same squared correlation | Immediately follow the first improving move |
| `kernel_best` | Normalized centered Gaussian-kernel similarity on squared measurements | Complete the current neighborhood |
| `kernel_first` | Same kernel similarity | Immediately follow the first improving move |

`moment_best` preserves the previous dependence-guided algorithm's numerical behavior. Every variant shares eight initial random feature sets. Each uses half its fit budget for exploration and half for refinement. For a given relationship statistic, both refinements share the entire exploration sequence. Each variant has its own cache and is charged for every distinct fitted feature set.

The kernel statistic uses only fitting observations. Each measurement is centered/scaled on fitting rows, then squared. Its Gaussian bandwidth is the median strictly positive absolute pairwise difference among these squared values. Center the Gram matrix on both axes and divide its pairwise Frobenius inner products by the respective norms. This is the fixed normalized HSIC-related proposal described in the earlier design, with no bandwidth sweep or target labels. A constant squared coordinate contributes zero similarity. Raw constant measurements are rejected, consistent with the model. An allocation guard refuses dense computations estimated above 512 MiB; this prototype does not establish scalability to thousands of features.

First-improvement refinement immediately changes its anchor after a strict improvement in the same score/tie ordering. It can revisit cached candidates without charging another fit. Every local attempt records its anchor, candidate, move type, incumbent before/after, cache use, evaluation count and acceptance. The native rule remains a threshold on a sum of squared standardized original measurements; kernels do not appear in that rule.

## Data and comparison fixed before execution

Reuse the exact raw fitting, search, validation and test blocks from `results/research_radial_search/20261020T174212_534139Z`. Copy them byte-for-byte, verify their hashes, preserve source job metadata, and record the source manifest and audit. The fitter source must match the original pilot. No regenerated population or feature permutation can change the comparison.

The full ablation retains all 36 cases, including the difficult four-/five-feature shells, the successful two-/three-/eight-feature cases, controls and the out-of-scope mean-shift cases. Each variant gets **256 distinct fits**, the same maximum size of ten, and the same data/search seeds. There are **36,864 search fits** in this one planned ablation batch. Outcomes on reused validation/test data are development evidence, even though those rows remain inaccessible to search. Fresh-seed replication is a subsequent, separate stage after selecting and freezing a version.

A short implementation check uses the first prior seed's four-/five-/eight-feature shell cases and correlated Gaussian, with **48 fits per variant**. These four cases check execution and auditability. They do not decide the winning method or replace the full fixed-budget comparison.

## Verification completed on 2026-10-25

All **243 distinct relevant tests** passed across the focused test batches, including the existing fitter/search checks and new kernel, search-policy, saved-data, runner and independent-auditor checks. An overly strict test of serialized background statistics was corrected to allow floating reduction differences of a few ulps when an array's memory layout changes; raw observations still match exactly, and no production fitness or fitting code was changed for that correction.

The small run completed all four cases and 16 method runs in **44.96 seconds**, evaluating **768 feature sets**. Its independent audit passed **23,478 checks with zero errors**. Results and the audit are saved together in [the run directory](../../results/research_feature_set_ablation/20261025T180331_174188Z/summary.md). The audit checks saved numerical state, scores, budgets, kernel statistics, local move acceptance, frozen selection, assignment rules and data provenance; it does not refit every model or reconstruct all random exploration choices.

At this deliberately reduced budget, the kernel versions improved test ARI in the four-feature case (0.290 to 0.634), but reduced it in the eight-feature case (0.967 to 0.768). In the five-feature case, first-improvement with moment proposals reduced ARI from 0.745 to 0.480; the two kernel variants obtained 0.786. These observations come from one reused seed, and none of the 12 shell method runs recovered the exact feature set. The correlated-Gaussian control was unflagged by all four variants. There were no recorded optimizer nonconvergences.

These mixed outcomes justify retaining the planned four-way comparison. They do not select a winner, establish reliable recovery, or justify a new parameter sweep. The full comparison remains fixed at 256 fits per variant across the original 36 cases, followed by the separate fresh-seed stage only after a version is selected and frozen.

## Run the full ablation

```powershell
Set-Location "C:\Users\Peter\Desktop\Github\ATOMIC_Clustering"
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_feature_set_ablation.py"
```

The default is the full planned ablation. The previous equally sized pilot took 36.12 minutes; allow roughly 35–60 minutes initially, with kernel overhead and hardware load affecting runtime. New results go under `results/research_feature_set_ablation/` in a timestamped directory. The source run and earlier results are preserved.

To inspect its configuration without running:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_feature_set_ablation.py" --list-only
```

To audit the completed output:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\analyze_research_radial_search.py" ".\results\research_feature_set_ablation\REPLACE_WITH_RUN_DIRECTORY"
```

If execution is interrupted or fails, use `--resume` with that output directory. It reuses completed jobs only when source/configuration checks pass; unfinished jobs restart. It preserves the parent run. The unchanged source development data must remain available for unfinished jobs.

## Decisions after this batch

Compare changes within each population and seed, not only an average across different geometries. Ask whether the kernel improves proposals in the four-/five-feature cases, whether first-improvement uses the same budget more effectively, whether successful cases regress, and whether validation gains, rule complexity or control flags deteriorate. Count ordinary feature-set/model evaluations and report kernel preprocessing time separately.

If a change helps, freeze that version for the one planned fresh-seed replication/stress batch. If it does not, inspect its recorded path for one specific repair at most, then narrow or replace the approach. Keep the predictive fitness stable unless the result exposes a ranking failure it can address. This remains the bounded sequence agreed in the prior assessment; it does not establish novelty from assembling standard components.
