# Rank preservation helped panel discovery, but does not finish the clustering method

## Verified run status

Both runs completed all 24 jobs:

- `results/research_rank_preservation/20260930T034706_021919Z`: 56.5 seconds.
- `results/research_rank_preservation/20260930T044157_487943Z`: 54.6 seconds.

The runs have the same parent experiment, configurations and seeds. Their saved model arrays, predictions and metrics are identical; 2,112 array comparisons confirmed this. They demonstrate repeatable execution, not six independent seeds.

The new read-only analyzer performed **19,013 checks with zero discrepancies**, covering both runs' 192 saved models, source identity, parent-data identity, native predictions, embeddings, metrics, support budgets, loss calculations, every saved constrained checkpoint and repeated-run equality. Exported tree text is outside this audit; its saved prediction metrics were checked. No original model source or result was changed.

Audit outputs: `results/research_rank_analysis_20260930/analysis.json` and `analysis.md`.

## The repair works, and its benefit depends on the setting

All constrained transformations satisfy `A.T A = I/2` to numerical precision. Equal nonzero coefficient singular values prevent the earlier flattening of a nominal two-column transform. They do not force the distribution of projected observations to be isotropic or multimodal.

Mean test ARI over the same three development seeds:

| Case and kernel | Previous unconstrained result | Frozen rank-preserved PCA | Optimized rank-preserved |
|---|---:|---:|---:|
| Mean shift, global | .519 | .587 | **.618** |
| Mean shift, local | .331 | .588 | .561 |
| Grouped moons, global | .524 | .560 | .549 |
| Grouped moons, local | .502 | .569 | .552 |

The mean-shift/global improvement occurs in all three paired seeds. Its panels recover **11/12, 12/12 and 11/12** planted features from 200 available columns, under the same 16-feature budget. The frozen starting panels contain 9/12, 9/12 and 10/12. Across those cases the search gains six planted features and loses none. This supports retaining the global constrained branch as a candidate panel generator. It does not establish novelty or superiority to external feature-selection methods.

The stopping rule applies by setting. Local mean-shift and both moons variants still show examples where fitness improves on discovery and validation rows while annotation ARI worsens. Rejecting every global result would ignore its mean-shift improvement; accepting the fitness as universally useful would ignore the failures. The [objective audit](rank-preservation-objective-audit-2026-09-30.md) gives paired values.

For moons, all optimized panels still include all ten planted variables, but the learned loading energy shifts substantially toward nuisance variables. In the global branch, planted-variable loading energy falls from about 94% to 56–64%. Therefore perfect feature recall alone is not enough to validate the fitted geometry. These are redundant noisy copies of two source coordinates, not a proof that ten variables are fundamentally necessary.

## A short followup already separates panel quality from assignment quality

After inspecting the rank results, I ran a bounded **posthoc** fixed-panel readout comparison, using only the global branch. For each of the 12 cases, both the frozen-PCA support and optimized support were held fixed. Ordinary two-centroid and unweighted identity-kernel models were fitted on the same discovery rows; all variants were reported. No feature search, annotation-based fitting or test-based winner selection was performed.

This is development evidence chosen after inspecting the earlier experiment, not independent confirmation. It completed in about 1.6 seconds. Artifacts are in `results/research_panel_readouts/20261001T024554_885812Z` (UTC timestamp).

| Case / fixed panel source | Original native projection | Identity kernel on panel | Centroids on panel |
|---|---:|---:|---:|
| Mean shift / frozen PCA panel | .587 | .603 | .601 |
| Mean shift / optimized panel | .618 | .666 | **.733** |
| Grouped moons / frozen PCA panel | .560 | .500 | .499 |
| Grouped moons / optimized panel | .549 | .499 | .504 |

The optimized mean-shift panels yield centroid test ARIs **.704, .738 and .756**. All three improve over applying the same centroid readout to the starting panels. This is stronger evidence of useful panel discovery than the projection's ARI alone: holding the readout family fixed shows that the changed support contributes value.

For moons, the same readout change hurts relative to the retained graph. Hence a centroid should be treated as a mean-separation model, not a universal replacement for nonlinear assignment. The current curved-data results remain too weak to claim a successful nonconvex method.

## Exact rules are now available for the centroid alternative

Each centroid readout exports a JSON and text rule in original feature units, including the discovery imputation values. Its decision is a weighted sum of the selected measurements compared with a threshold. This is an exact algebraic form of **that centroid model**, not an explanation claimed to preserve the distinct kernel classifier.

All 24 exported rules exactly reproduce their centroid model predictions on discovery, validation and test blocks: 72 replay checks. A separate saved-state review passed **521 checks**, and three relevant unit tests passed. The coefficient text is rounded for readability; JSON retains numerical coefficients. The rules still contain up to 16 features, so exactness does not yet establish sufficient compactness for a domain expert.

The original optimized depth-3 trees remain inadequate as graph explanations: none of the 12 optimized planted-case models passes the empirical 5% disagreement threshold on both validation and test. The exact centroid rule avoids approximation error for its own model, while changing the clustering family. See the [interpretability audit](rank-preservation-interpretability-audit-2026-09-30.md).

## What remains unresolved

- Gaussian negative controls still receive two-way assignments because none of these procedures implements cluster acceptance. The independent-Gaussian rank-collapse reward is largely removed, but correlated-Gaussian validation loss can remain lower than the mean-shift loss. A low loss alone cannot establish clusters.
- A fixed full-rank transformation does not prevent anisotropic projected data, especially for correlated measurements.
- The promising mean-shift panels still include nuisance variables: overall planted precision is 34/48 under the fixed 16-variable budget. No minimal-panel or certification claim is supported yet.
- Repeated execution is not independent rediscovery, and the same development test rows have now informed multiple design choices.
- Shells and covariance regimes were excluded from this rank followup because their earlier supplied-panel geometry check failed. This experiment does not resolve them. No external GroupFS/DUFS/sparse-kernel benchmark has been run here.

## Recommended next development step

Advance the surviving component as **panel discovery followed by an explicit assignment model**. Keep the global fixed-rank search as a candidate proposer and preserve the frozen-PCA panel baseline. For the mean-separation branch, the exact centroid rule is a concrete candidate to freeze and verify on new data.

The next bounded experiment should independently rediscover panels on two fresh discovery samples from the same fixed feature population, measure agreement on untouched observations, and shorten the chosen native rule using the existing independent fidelity-bound machinery. Report coverage/abstentions, irrelevant-feature retention and rule fidelity separately from annotation ARI. This tests the user's central requirement—whether the panel is reproducible, useful and verifiably compact—rather than continuing to tune a graph score.

Before any confirmatory claim, freeze the pipeline, budgets and selection rules and evaluate new seeds/data. Do not select the readout with the largest test ARI. A one-population alternative appropriate to the covariance structure remains necessary before calling a proposed split evidence of multiple populations.

Nonconvex work should proceed as an explicit shape-family branch. The earlier shared-scale/radial proposal gives a candidate exact weighted-square rule for shell-like data; it is not implemented here and must not be confused with the already-failed squared sparse-k-means experiment. Curved manifolds and covariance regimes need their own supported assignment families. A coherent framework can share panel discovery and verification while making these assumptions visible; current evidence does not justify one universal fitness.

All requested completed runs have been checked. The short fixed-panel diagnostic has also been run and saved; there is no additional pending run from this result inspection.
