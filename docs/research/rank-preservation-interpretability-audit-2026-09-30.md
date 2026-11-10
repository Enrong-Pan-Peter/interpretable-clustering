# Rank preservation: original-feature panels and assignment interpretation

## Material Passport

- Origin: independent interpretation audit of saved rank-preservation results
- Origin Date: 2026-09-30
- Mode: read-only analysis of reports, transforms, predictions, and original split data; no model fits
- Verification Status: ANALYZED; projected-data singular values and loading allocations calculated directly from saved models
- Version Label: rank_preservation_interpretability_v1
- Main input: `results/research_rank_preservation/20260930T044157_487943Z`
- Related input: the original kernel pilot and its code; the earlier rank-preservation run is a repeated execution of the same cases, not additional independent seeds
- Scope: original-feature recovery, retained geometry, rule fidelity, and one actionable next stage

## Decision

The rank constraint fixes a real failure: useful panels and their two-dimensional transformation no longer disappear through the old global projection's numerical flattening. The strongest positive result is **global-kernel mean-shift feature recovery**, which improves from 9/9/10 planted features at the frozen initializer to 11/12/11 after optimization. The three panels each contain 16 features. No planted feature present at initialization is lost; six additional planted features are recovered across the three runs.

This is useful progress in feature discovery. It is not yet a satisfactory interpretable clustering method. The same global optimizer retains all ten grouped-moons features but moves substantial loading weight onto nuisance features without improving the clustering on average. The depth-three trees are inadequate replacements for the native mean-shift assignments. A bounded comparison of **exact native readouts on the same selected supports** is now more informative than another objective/kernel/rank grid. The parent agent is carrying out that comparison separately.

There is no novelty, universal nonlinear-clustering, or cluster-existence claim here. These are development rows that have already informed method changes.

## What was held fixed

There are four families, three generating seeds (26–28), two kernels, and four reported variants per case. There are 24 dataset/kernel jobs and 96 model outputs, but only three independently generated datasets per family. Each dataset contains 800 rows split into 400 discovery, 200 validation, and 200 test observations. Landmark fitting uses 200 discovery observations. Every output has a 16-feature panel.

The changed constraint is `A.T @ A = I / 2`, imposed after row-support selection. Preprocessing, spectral loss, native graph extension, and selection among discovery checkpoints are otherwise retained. The two PCA baselines distinguish the original initializer from its constrained polar-factor counterpart. Comparisons below use the latter, `rank_preserved_pca`, when asking whether optimization helps beyond the new constraint.

Seeds also change the generated feature permutation. Comparing the same printed feature index across different seeds would not measure biological or feature-selection stability. Within-seed planted recovery and support transitions are interpretable; independent rediscovery on fixed feature identities would be a separate experiment.

## Panels: a concrete gain for mean shift, retention without gain for moons

All quantities below are descriptive across the same three seeds.

| Family / kernel | Frozen constrained PCA: mean test ARI | Optimized constrained: mean test ARI | Frozen planted counts | Optimized planted counts |
|---|---:|---:|---|---|
| Mean shift / local | .587692 | .560726 | 9, 9, 10 of 12 | 9, 9, 10 of 12 |
| Mean shift / global | .587082 | .618306 | 9, 9, 10 of 12 | 11, 12, 11 of 12 |
| Grouped moons / local | .568884 | .552387 | 10, 10, 10 of 10 | 10, 10, 10 of 10 |
| Grouped moons / global | .559612 | .549162 | 10, 10, 10 of 10 | 10, 10, 10 of 10 |

For global mean shift, the ARI gains are positive in each seed: +.030163, +.030148, and +.033361. Recall becomes 34/36 = .944444 across the three 12-feature references, while precision is 34/48 = .708333 across the selected panels. This improves the older unconstrained global model's mean ARI of .518642 and its 8/10/11 recovered features. The gains are modest relative to the frozen comparator, and three reused seeds do not establish reliable dominance.

The global mean-shift optimized panels retain the following nuisance and missed feature indices. These are synthetic shuffled column identifiers, not domain annotations.

| Seed | Selected planted count | Selected nuisance indices | Missed planted indices |
|---|---:|---|---|
| 26 | 11 | 13, 67, 72, 123, 188 | 105 |
| 27 | 12 | 7, 79, 120, 185 | none |
| 28 | 11 | 8, 10, 19, 52, 92 | 75 |

The local mean-shift optimizer changes no selected support in any of the three seeds. Its changes concern the geometry within the same panel, with test ARI worsening in two seeds. The global optimizer makes a genuine support improvement rather than merely preserving a successful initial panel.

For grouped moons, all constrained outputs retain every planted feature, and thus have recall 1 and precision 10/16 = .625. This improves robustness over the old local optimizer's seed-28 loss of eight planted features. It does not mean the new optimizer improves the useful geometry: both kernels are slightly worse than frozen constrained PCA on average, and all of the support replacements are between nuisance columns. Global frozen-versus-optimized support Jaccard similarities are .524, .524, and .455 despite identical planted membership.

## Retaining a feature does not mean retaining its useful weight

Let the loading allocation to the planted panel be

`E_signal = sum_{j in planted} ||A[j,:]||^2 / ||A||_F^2`.

This is a descriptive, output-rotation-invariant measure of coefficient allocation in discovery-standardized feature coordinates. It is not a causal importance score and does not account for correlations by itself.

| Family / kernel | Frozen constrained planted loading allocation, seeds 26/27/28 | Optimized constrained planted allocation |
|---|---|---|
| Mean shift / global | .486 / .477 / .544 | .866 / .835 / .755 |
| Grouped moons / local | .935 / .942 / .942 | .909 / .917 / .908 |
| Grouped moons / global | .935 / .942 / .942 | .641 / .605 / .565 |

The global mean-shift improvement is supported by both membership and stronger coefficient allocation to signal. For global moons, the optimizer keeps all ten signals but increases the nuisance allocation from roughly 6% to 36–44%. Therefore a perfect recall score alone overstates the quality of the learned representation. These numbers do not prove that every nuisance loading is harmful, but the accompanying lack of an ARI improvement makes this an actionable concern.

## Transformation rank and data shape are different quantities

All constrained transforms have two equal singular values, as intended. This does not whiten or isotropize the observations: if standardized input covariance is `Sigma`, then projected covariance is `A.T @ Sigma @ A`, not automatically `I / 2`.

I computed the ratio of the second to first singular value of each **centered held-out projected data matrix**, using its saved discovery preprocessing and transform. This is distinct from both the transform's singular-value ratio and the final graph embedding.

| Family / kernel | Frozen constrained projected-data ratio, seeds 26/27/28 | Optimized constrained projected-data ratio |
|---|---|---|
| Mean shift / global | .658 / .680 / .691 | .586 / .652 / .567 |
| Grouped moons / local | .596 / .595 / .661 | .632 / .587 / .707 |
| Grouped moons / global | .596 / .595 / .661 | .440 / .366 / .363 |
| Independent Gaussian null / global | .974 / .820 / .970 | .907 / .936 / .941 |
| Correlated Gaussian null / global | .132 / .122 / .122 | .141 / .139 / .166 |

The old unconstrained global model's corresponding ratios on mean shift were about 2.6e-5, 4.5e-5, and 3.4e-5; the rank constraint removes that extreme flattening. The optimized moons projections are still anisotropic, but their .36–.44 ratios are not numerical rank collapse. The second direction retains roughly 12–16% of the total projected test variance. Penalizing every such anisotropy would erase legitimate population structure.

The correlated Gaussian control is particularly important: a mathematically full-rank transformation can still show a thin, easily divided cloud from a single correlated population. Shape alone and a low spectral loss do not establish multiple clusters. All null outputs still return a forced binary assignment.

For visual interpretation, show the actual `standardized X @ A` coordinates with original-feature loading formulas. The exported `test_embedding` is a row-normalized graph eigenfunction embedding used by the classifier; its visual shape is not the original feature-panel shape. A plot of that embedding cannot by itself validate a claimed geometric cluster shape in the measurements.

## Readable trees remain approximate and often weak

The saved tree is a depth-three classifier fitted to native discovery assignments in original feature coordinates. Its fidelity to the graph and its external ARI measure different targets. None of the 12 optimized planted-case trees has at most 5% disagreement with the native rule on **both** validation and test. Across all 24 optimized outputs the count is also zero. This is an empirical threshold check, not a confidence-bound claim.

| Family / kernel | Validation disagreement, seeds 26/27/28 | Test disagreement |
|---|---|---|
| Mean shift / local | .275 / .275 / .230 | .185 / .245 / .185 |
| Mean shift / global | .240 / .275 / .280 | .265 / .320 / .235 |
| Grouped moons / local | .075 / .060 / .070 | .060 / .035 / .065 |
| Grouped moons / global | .075 / .070 / .070 | .065 / .050 / .065 |

Every feature used in these 12 optimized planted-case trees belongs to the planted reference. Nevertheless, global mean-shift tree external ARIs are only .163082, .111184, and .344912, versus native .575306, .575496, and .704116. Recognizable variables and a short rule are not sufficient: the rule must actually retain the useful assignment. The moons trees are closer but still not certified faithful, and a tree that approximates the existing mediocre partition does not improve its external usefulness.

The native graph model does have a frozen out-of-sample rule, using the selected original variables, learned projection, 200 saved reference observations, graph extension, and two spectral centers. That is reproducible and deployable. It is substantially more complex than the exported shallow tree, so the tree should remain explicitly marked as an approximation.

## One next step, with a decision attached

Freeze the two global discovery supports—constrained PCA and constrained optimized—and compare three clearly separated native readouts on each support: the saved projection/graph, a supplied-support identity graph, and ordinary two-means on the discovery-standardized original panel. Report all three, including nulls; do not choose a method independently for each test case. This asks whether the stronger panel can support a simpler exact assignment, rather than introducing another feature optimizer. It is a development diagnostic and is being performed separately by the parent agent.

For two-means, the native rule can be exported exactly as a weighted sum of original measurements. If discovery-standardized coordinates are `z_j = (x_j - mean_j) / scale_j` and cluster centers are `c0,c1`, assign group 1 when

`2 * sum_j (c1_j - c0_j) * z_j > ||c1||^2 - ||c0||^2`.

Discovery imputation, the threshold, and equality tie handling complete the rule. This is a different native clustering model; it is not an approximation promised to reproduce the graph's labels. Keep its external utility and graph disagreement separate.

If this exact readout retains the panel's useful separation, advance that fixed panel-plus-rule procedure to a fresh, prespecified evaluation rather than continuing to tune the old spectral fitness. If the graph offers no consistent advantage on grouped moons, do not claim a nonlinear benefit from it. If both readouts remain weak there, the next repair concerns the representation or assignment family, not another small improvement to panel recall.

The method can now search and return 16-feature supports without exhaustive enumeration. These experiments still do not establish that more than three measurements are necessary for nonlinear clustering: grouped moons contains redundant noisy copies of two latent coordinates, and mean shift is a centroid-separation family. The genuinely joint shell/covariance-regime tasks remain separate unresolved targets.

## Statistical and interpretation limits

The analysis avoids treating repeated executions as new evidence, comparing shuffled feature identities across seeds, selecting the best kernel per case, equating planted recall with necessary-feature recovery, substituting a tree's readability for its fidelity, or using null partitions as proof of clusters. There are only three reused generating seeds per family, no real-data interpretation test in this followup, and no independent confidence claim. Loading allocation and observed anisotropy are diagnostics rather than causal explanations. The justified outcome is a repaired numerical constraint and stronger mean-shift panels, with clear remaining work on the exact useful assignment.
