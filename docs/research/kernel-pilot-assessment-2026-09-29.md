# Kernel pilot: diagnosis and the next bounded correction

The completed kernel pilot does not fix the clustering method. It provides direct evidence that the spectral fitness can reward changes that reduce the intended clustering quality. It also exposes a transformation collapse that is worth removing in one controlled followup before deciding whether to retire this score for the tested settings.

## Verified results

Source: `results/research_kernel_panels/20260927T043314_711791Z`. All 21 cases completed in 186.4 seconds. The read-only analyzer independently replayed 201 saved native models, their embeddings, annotation metrics, support budgets, checkpoint selection and saved tree metrics. All **6,966 checks passed**, including 46 historical source hashes. The audit does not reconstruct the exported tree text or unsaved same-panel centroid models. No original source or experimental result was changed.

Audit artifacts: `results/research_kernel_analysis_20260927/analysis.json` and `analysis.md`. Reproduction command:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\analyze_research_kernel_results.py .\results\research_kernel_panels\20260927T043314_711791Z
```

Mean held-out ARI over three seeds, shown descriptively rather than as a superiority test:

| Case | Local projection/gap | Global projection/gap | Supplied true panel, raw local graph | Supplied generator rule |
|---|---:|---:|---:|---:|
| Mean shift, 12 relevant out of 200 | .331 | .519 | .710 | — |
| Grouped moons, 10 relevant out of 50 | .502 | .524 | .595 | — |
| Shells, 5 relevant out of 50 | -.002 | .014 | .014 | 1.000 |
| Covariance pairs, 8 relevant out of 50 | .002 | -.002 | .037 | .864 |

These are prespecified variants, not a retrospectively selected winner. Supplied-panel/rule results are privileged ability checks, not autonomous discovery. Three seeds do not establish small performance differences or general superiority.

## What is hindering the method

**Fitness is a substantive problem.** Reconstructing the exact sparse-PCA initial map showed that local gap optimization improves its loss in all six mean-shift/moons cases, but worsens test ARI in five and ties once. The selected final map may come from a different restart, so this diagnoses the optimization-and-selection process, not always a single trajectory. Recomputing the loss on separate validation rows still favors four of those harmful local changes. Extra validation alone therefore does not repair the score's preference.

**The global sample transformation almost becomes a line.** All 21 global gap models have second/first singular-value ratio below .00861; 20 are below .00015. A Frobenius norm constraint permits this even with two requested columns. On independent Gaussian input, the population global-kernel gap ratio improves from about 1 for an equal two-dimensional projection to 2/3 for a line, despite there being only one population. The small degree penalty cannot offset that reward. The [objective audit](kernel-objective-results-2026-09-27.md) gives the derivation, assumptions and per-seed reconstructions. This is a structural score issue, not merely insufficient optimization time.

**Useful panels can survive even when the learned map is worse.** On mean shift the global model recovers 8, 10 and 11 of 12 relevant features in panels of 16. Keeping those exact panels but using identity instead of learned mixing gives mean ARI .607 versus .519 for the native projection. This diagnostic does not retrospectively authorize choosing the better readout on test labels; it supports separating discovery from geometric distortion.

**Shells have an additional geometry problem.** Even the supplied correct panel fails under this particular raw local graph with 200 landmarks, whereas the known radial rule succeeds. This does not prove raw spectral clustering can never recover shells: the earlier obstacle suite already showed a sample-size/neighborhood dependence. More feature-search effort alone cannot repair this evaluated assignment. Covariance-regime recovery is a separate dependence problem, not a density-separated clustering task.

**The current small trees are not faithful explanations.** None of the 63 projection models has at most 5% disagreement with its depth-3 tree on both validation and test. For mean shift/global projection, test disagreement averages 25.7%. These are approximate summaries, not the actual rule. An exact oblique or radial rule could be more appropriate than an axis-aligned tree. See the [geometry and interpretability audit](kernel-geometry-results-2026-09-27.md).

The diagonal cut model shrinks to one feature in all 21 cases. All 54 outputs across the three negative-control families are numerically valid. That is not a measured false-positive rate: the current pipeline deliberately proposes two groups and has no cluster-acceptance test. Readability, stability and low spectral loss remain distinct from useful clusters.

## Next run: remove rank collapse and test whether optimization adds value

The new module `atomic_research/rank_preserved_kernel.py` imposes `A.T @ A = I/r` after selecting the row support. A scaled polar factor fixes the coefficient singular values. It preserves the original-feature budget and rejects rank-deficient retained supports explicitly. This prevents transformation collapse; it does not promise full-rank projected data, accurate panels or valid clusters.

The historical kernel objective, gradient, preprocessing, landmarks, native readout and child-size gate are reused unchanged. The constraint is the intentional difference. The followup compares four objects for each case/kernel:

1. Exact original sparse-PCA initialization, frozen without optimization.
2. The saved unconstrained final model from the completed pilot.
3. A frozen rank-preserved version of the same PCA initialization.
4. The rank-preserved model after optimization.

Comparing both frozen maps matters: truncating PCA loadings to a sparse row support already alters its column geometry. No ARI-based winner selection occurs. Validation/test graph losses are diagnostics, not selection rules. Initial support, final support, singular values, score, assignment ARI, panel size and tree fidelity are saved.

The full followup has **24 jobs**: mean shift, grouped moons, independent Gaussian and correlated Gaussian x three original seeds x local/global kernels. It reuses the existing development rows; it is not a fresh confirmation study. Only the rank-preserved arm requires an optimized fit; the existing model is loaded and the two starts are reconstructed. Shell/covariance models and broad real-data benchmarks are intentionally deferred until their representation issues are addressed.

From this repository in PowerShell:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_rank_preservation.py --suite targeted
```

By default the script reads the latest kernel-pilot directory, requires it to be complete, and prints it. To pin the source explicitly:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_rank_preservation.py --suite targeted --source .\results\research_kernel_panels\20260927T043314_711791Z
```

Results go into a new timestamped directory under `results/research_rank_preservation`. No new package or GPU is needed. Source hashes are checked before using saved models.

## Verification and decision rule

On 2026-09-29, **75 tests passed**, covering the historical kernel implementation, independent saved-state replay, the benchmark boundary and the new constraint. The two-job, three-step smoke run completed at `results/research_rank_preservation_smoke/20260929T184637_260866Z`. Its eight models passed 36 independent prediction/embedding/constraint checks. All 46 historical source hashes still match. This is an engineering check, not evidence that rank preservation improves clustering.

If the constrained optimizer still damages the frozen baseline while improving training and independent-row fitness, stop using this spectral score as the primary model-selection objective for those settings. Do not spend another broad EA/restart/kernel grid optimizing it. If preventing collapse materially helps, retain the constraint and test support discovery and assignment fidelity separately on fresh prespecified cases.

For the radial branch, the next distinct model candidate is the previously proposed shared-scale mixture with a matched independent-marginal background and an exact weighted-square assignment rule. It is not another squared sparse-k-means run, which already failed in the prior obstacle suite. That model is not implemented in this followup, does not automatically distinguish dependence from multiple populations, and would need its own scoped tests. The current evidence supports narrowing the claim and separating shape families, not claiming universal nonconvex clustering or SOTA performance.
