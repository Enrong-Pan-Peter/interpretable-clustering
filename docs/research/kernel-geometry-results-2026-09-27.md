# Kernel pilot: geometry, panel discovery, and readable rules

## Material Passport

- Origin: independent interpretation of the completed kernel-panel pilot
- Origin Date: 2026-09-27
- Mode: analysis of saved results; no model refits
- Verification Status: ANALYZED; selected saved native/tree predictions independently checked against reported metrics
- Version Label: kernel_geometry_results_v1
- Inputs: `results/research_kernel_panels/20260927T043314_711791Z/summary.json`, case reports, saved predictions/splits, and the experiment code
- Scope: geometry versus discovery, matched-panel readouts, interpretation, larger panels, negative controls, and one next experiment

## Decision

The pilot finds some useful panels, especially in mean shift and grouped moons, but it has not demonstrated a useful general nonlinear geometry. **The supplied correct shell panel still fails under the current graph**, so another feature-search budget increase is not the first repair. The projection also often damages information already present in a discovered panel, and depth-three trees do not faithfully explain most projection models.

The next distinct model should target **shared latent scale on a sparse original-feature panel**, retain its native likelihood assignment, and compare joint scale evidence with an independent marginal-mixture background. Test that single change on shells and matched controls. Do not repeat the already unsuccessful autonomous squared sparse-k-means experiment or expand this kernel/rank/objective grid before fixing the mechanism.

This recommendation is a testable modeling hypothesis, not evidence that the proposed scale model works, and not a novelty claim. The existing scope remains forced binary partitions without a cluster-acceptance test.

## What this run evaluates

The suite contains seven families, seeds 26–28, and six reported variants: 21 cases and 126 outputs. Each case has 800 rows, split into 400 discovery, 200 validation, and 200 test observations. The kernel fitting uses at most 200 discovery reference rows; the preprocessing uses the discovery block. Five variants optimize feature geometry, while the sixth uses all original features with a fixed local graph.

Projection variants learn a signed rank-two linear sample map and then apply a graph kernel in that map. This is not GroupFS group discovery, and a nonlinear kernel after a rank-two map does not restore information discarded by that map. Diagonal variants use feature weights without the rank-two mixing. All variants are reported, rather than a test-chosen winner.

The depth-three tree is fitted afterward to native discovery predictions in original feature coordinates. Its disagreement measures approximation of the native classifier; its external ARI measures a different target. The supplied-panel graph and known generator rules are ability diagnostics and receive information unavailable to autonomous discovery.

## The geometry obstruction is directly observed

| Family / seed | Supplied true panel: local graph test ARI | Known generator rule test ARI |
|---|---:|---:|
| Shells / 26 | .034284 | 1.000000 |
| Shells / 27 | .011998 | 1.000000 |
| Shells / 28 | -.004635 | 1.000000 |
| Covariance pairs / 26 | .075233 | .864220 |
| Covariance pairs / 27 | .020688 | .864220 |
| Covariance pairs / 28 | .014673 | .864219 |

For shells the known rule thresholds the radius in the five generating coordinates. For covariance pairs it thresholds the sum of the four known pair products. Neither is an autonomous result. They establish that the data contain useful information and that this particular local-graph readout is not extracting it, even when feature identification is removed from the problem.

The corresponding autonomous shell ARIs are near zero throughout; the highest descriptive value is .0393 for global projection at seed 26. Covariance-pair autonomous ARIs are likewise near zero, with maximum .0074. These tiny values are not practical recoveries.

The precise conclusion is about **this graph construction, reference sample, and native extension**. Earlier supplied-panel experiments found that raw spectral shell clustering could improve at larger sample sizes and smaller neighborhoods. They also found perfect squared-spectral and radius-rule ability on the tested oracle settings. See `docs/research/obstacle-geometry-controls-audit-2026-09-17.md`. It would be wrong to infer that every raw spectral method is incapable of separating shells.

The rank-two restriction creates an additional issue: an isotropic five-dimensional shell's radius is not determined by a two-dimensional linear projection. The projected shells overlap even when the full radii do not. That limitation does not explain every observed failure—an identity map on the correct panel also fails here—but it is a reason not to optimize this projection as a general radial-information model.

## Useful feature discovery is stronger than the learned geometry

The following are means across the same three seeds. They are descriptive paired comparisons, not significance tests.

| Family / projection variant | Native test ARI | Same-panel identity graph ARI | Same-panel ordinary centroid ARI |
|---|---:|---:|---:|
| Mean shift / cut local | .26828 | .42602 | .43480 |
| Mean shift / gap local | .33136 | .37429 | .39239 |
| Mean shift / gap global | .51864 | .60660 | .65062 |
| Grouped moons / cut local | .27711 | .28773 | .28043 |
| Grouped moons / gap local | .50203 | .47718 | .44794 |
| Grouped moons / gap global | .52414 | .50883 | .50856 |

An identity comparison retains the selected original panel and the kernel family while removing the learned projection. It refits the graph on that representation, so it is a matched-support representation comparison, not a parameter-identical perturbation. The centroid comparison changes the model family more substantially and is reported separately.

The most consistent mean-shift proposal in this pilot, global gap projection, finds 8, 10, and 11 of the 12 planted features in 16-feature panels. Its seed-level results show the distinction:

| Seed | Planted features / 16 | Native ARI | Identity ARI | Centroid ARI |
|---|---:|---:|---:|---:|
| 26 | 8 | .2763 | .5012 | .5754 |
| 27 | 10 | .5755 | .5453 | .6382 |
| 28 | 11 | .7041 | .7733 | .7383 |

Thus the seed-28 native result is useful, but calling it a benefit of the learned projection would conceal that the same panel performs better with the identity graph. All-feature local graph ARIs are .5157, .4735, and .4461; ordinary all-feature k-means gives .4456, .5159, and .6064. There is no uniform across-seed dominance.

On grouped moons, global gap projection includes all ten generating measurements in every 16-feature panel. Native ARIs are .5305, .6222, and .4196; same-panel identity ARIs are .5160, .5909, and .4196. The geometry gains are therefore modest. The supplied true ten-feature local graph gives .6064, .7041, and .4735, so even the ability control is not a near-perfect separation of these noisy groups.

Local gap projection is less consistent on grouped moons: it captures all ten features in seeds 26 and 27 but only two in seed 28. Its native ARIs are .6223, .6065, and .2773. A report that selected the best kernel variant separately for every case would obscure this variability and constitute a new test-guided selection procedure.

## Large outputs do not yet establish a larger-panel nonlinear method

All 63 projection outputs contain exactly 16 original features. This demonstrates that the implementation can search and return panels above three features without exhaustive subset enumeration. It does not demonstrate that 16 features are necessary, that they are all useful, or that the nonlinear geometry succeeds because of their joint information.

- Mean shift provides evidence of useful distributed feature discovery, but is a mean-separation task; none of the global-projection panels recovers all 12 planted features.
- Grouped moons use noisy copies of two latent coordinates. Recovering ten measurements is useful group/denoising evidence, not proof that more than three independent structural coordinates are required.
- Shells and covariance pairs are the joint-information tests in this suite. They fail under the current autonomous methods and supplied-panel graph.

The shell generator in this actual run uses five signal coordinates and radii around 1 and 2. It is not the six-/twelve-dimensional, radius-ratio-1.35 benchmark proposed in the earlier scope document. Its results must not be attributed to that unrun stronger construction.

## The current trees are not faithful explanations of the projection models

Of 63 projection trees, only two have test disagreement at most 5%. Only one has validation disagreement at most 5%, and **none has both**. This is an empirical diagnostic threshold, not a confidence guarantee or a tree-selection rule.

For mean-shift global projection, tree disagreement is 29%, 25.5%, and 22.5% on the 200-row test sets. The saved seed-28 native/tree predictions differ on 45 of 200 observations. Presenting that tree as “the rule” would materially misdescribe the classifier.

Grouped moons are easier to approximate: global-projection tree disagreement is 7%, 6%, and 5%, though validation disagreement remains 8%, 8%, and 8.5%. Local gap projection has 6%, 5%, and 15% test disagreement. Their readability results must retain the poorer seed, not just the favorable tree.

Conversely, diagonal cut selects exactly one feature in all 21 cases and its trees have at most 1.5% test disagreement. Those simple rules mostly fail the intended labels and also partition every null. Readability alone is not usefulness.

A depth-three axis-aligned tree is a restrictive explanation family for an oblique or radial rule. These failures do not prove that no readable explanation exists. A native centroid on an original panel has an exact oblique linear boundary; a scale model can have an exact weighted-square boundary. Prefer exporting the native rule for the next model over assuming a small tree will faithfully approximate it.

## Null controls and uncertainty

All 54 outputs across independent Gaussian, correlated Gaussian, and single-shell controls are marked numerically valid. Their test assignments have nontrivial groups; the smallest child ranges from 18 to 99 out of 200 across variants. This is not a measured false-positive rate because the procedure is explicitly forced to propose two groups and contains no acceptance test.

Null independent seed 26 illustrates the separation of concepts: global projection has a balanced 96/104 native test partition, and its tree disagrees on 67/200 points. Diagonal cut on the same null yields a nearly exact one-feature tree. Neither complex geometry nor an easy explanation establishes multiple populations.

Three seeds locate large, repeatable qualitative failures—such as the supplied shell graph failing while the radius rule succeeds—but do not establish broad superiority or small ARI differences. The 126 outputs are not 126 independent datasets: variants reuse rows, and outcomes within a case are paired. Test sets have 200 observations. No method has been selected as the best using an independent selection protocol, no GroupFS/DUFS/direct sparse-kernel comparator has been run in this suite, and no numerical state-of-the-art claim is supported.

## One next experiment: sparse shared-scale discovery

Do not repeat simple squaring followed by the old sparse-k-means objective. The earlier autonomous squared models reached only modest shell ARI and did not find the planted support, despite a successful supplied-panel transformed geometry. That distinguishes representation availability from a suitable discovery objective.

A concrete different model is a shared two-state scale explanation, compared with features having independent states. This makes the earlier geometry report's still-unimplemented mixture recommendation explicit; it is not a new literature discovery. Let `f_cj(x_j)` be low/high-scale densities with a common center for each variable, and let `q_j(x_j) = sum_c pi_c f_cj(x_j)` be their matched marginal. Fit feature participation weights `r_j in [0,1]` through

`p_r(x) = sum_c pi_c product_j [r_j f_cj(x_j) + (1-r_j) q_j(x_j)]`.

This is a normalized density. At `r=0` it is the independent marginal background `product_j q_j(x_j)`. If only one feature participates, summing over the latent state again gives that same background. Consequently a single feature's two-scale marginal cannot, by itself, supply a joint-model gain. This directly addresses the observed attraction to a one-variable split while keeping a different objective from Euclidean sparse k-means on squared coordinates.

Use a sparsity penalty and explicit original-feature cap, train-only component/scale restrictions to avoid likelihood singularities, and a held-out comparison of `log p_r(x) - sum_j log q_j(x_j)`. Parameter estimation, score selection, and any hardening of feature gates must be frozen before test. Retain the native posterior rule. With hard selected features and Gaussian equal-center scale components, its log odds are a constant plus a weighted sum of squared centered measurements, which can be exported exactly.

There are two limits to state before running it. Conditional independence within a component is misspecified for exact spherical shells, and the independent marginal background tests shared dependence rather than cluster existence. A single correlated Gaussian or single shell can therefore still favor a shared explanation. Successful fit is not automatically an accepted biological cluster or a calibrated rejection of unimodality.

The bounded next experiment is shells plus independent-Gaussian and single-shell controls, at the current p=50 and sample budget, with fresh fixed seeds. Include the supplied true panel as an ability control and the old squared sparse-k-means result as the existing baseline; do not open a new kernel/neighborhood/rank grid. Report autonomous support, native test ARI, exact rule complexity, held-out joint-versus-marginal gain, and all null outputs. If the supplied-panel scale model works but autonomous fitting fails, the next work is its sparse estimation/initialization. If even the supplied panel fails, this likelihood family needs revision before search changes.

This is a scoped radial/scale-family repair. It does not solve spirals or the covariance-pair regime, and sparse mixture modeling already has prior art. Its value must come from whether it discovers a verifiable original-feature panel and an accurate readable native rule on the declared task, rather than from renaming a standard component.

## Interpretation coverage

The ARS statistical checklist was reviewed across all 11 categories. The material issues here are paired comparisons versus pooled winners, three-seed uncertainty, repeated test inspection, an enriched set of designed tasks rather than a universal population, and omission of external comparators. All variants, nulls, unfavorable seeds, and oracle information are identified. No causal, population-wide, significance, or novelty claim is made from these outputs.
