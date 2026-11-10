# A trait-first prototype: discover a sparse radial panel and its native rule

## Material Passport

- Origin Skill: academic-research-suite
- Mode: mechanism design and methodological critique
- Origin Date: 2026-10-14
- Verification Status: UNVERIFIED proposed mechanism; no model fits or code changes
- Version Label: trait_first_method_review_v1
- Scope: one minimal nonlinear node prototype, assumptions, objective, failure tests, and the boundary between a diagnostic implementation and a thesis contribution

## Recommendation

Build one **sparse concentric-band node** next. Its target is two populations distinguished by distance from a shared centre in a small original-feature panel: rings, shells, and suitably standardized elliptical bands. It directly models this geometry and returns a native squared-distance rule. It does not project a five-dimensional shell down to two dimensions before trying to recover the lost radius.

Keep the existing centroid branch as the mean-separation comparator. Do not simultaneously add arbitrary covariance regimes, moons, neural embeddings, a hierarchy, an interface, and a biomedical benchmark to this first prototype. Those are different obligations. A working radial node would resolve one concrete nonlinear failure; a failed prototype should be discarded or revised before a large benchmark.

The user's objection to benchmarking an unfinished method is reasonable. What remains necessary now is a small **mechanism test**, including controls that could falsify the idea. That is different from another broad performance table. Real applications should follow the demonstrated assumptions, rather than cytometry dictating every design choice.

## Why not simply use a sparse Gaussian mixture?

Sparse mean/variance mixtures are established. Xie, Pan and Shen explicitly develop penalized clustering with cluster-specific diagonal covariance matrices and grouped variables; that cannot be claimed as a new algorithm here. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2777718/).

A shared-centre mixture of spherical Gaussians is also the wrong description of **separated annular density bands**. Each component's spatial density decreases with radius; their positive mixture does too. Its latent components can describe scale heterogeneity and yield a useful radial classifier, but it does not create spatial density peaks on two shells. A continuous heavy-tailed scale population can also be represented by Gaussian scale mixtures. Two fitted scale components therefore do not establish two clusters.

For the next prototype, make the radial-band assumption explicit in the density itself rather than relying on an indirect scale-mixture interpretation.

## Minimal node model

Fit one preprocessing map on discovery observations. Let `z_j=(x_j-c_j)/s_j`, where the centre and positive scale are discovery-only estimates. For the first implementation, freeze these coordinates; do not add flexible centre learning, rotation, or feature-weight optimization yet. On a selected support S of size d, define

`t_S(x) = sum_{j in S} z_j^2`.

A proper single-band density in these standardized coordinates is

`g_d(z_S; a,b) = exp(-(t_S-a)^2/(2*b^2)) / Z_d(a,b)`, with b>0,

where

`Z_d(a,b) = A_(d-1) * integral_0^infinity r^(d-1) exp(-(r^2-a)^2/(2*b^2)) dr`

and `A_(d-1)=2*pi^(d/2)/Gamma(d/2)` is the unit sphere's surface area. This is a one-dimensional numerical integral. For a>0 the spatial density has a peak around a spherical band. The radial probability density also contains the `r^(d-1)` volume factor, so a is not automatically the observed mean squared radius.

The two-population model is

`g_2,S = pi_0*g_d(a_0,b) + pi_1*g_d(a_1,b)`, with a_1>a_0 and pi_0+pi_1=1.

Use a shared b in the first version. Put discovery-fixed lower bounds on b and component occupancy, and finite parameter bounds, to avoid near-point-mass fits and tiny outlier components. Start with adequately populated bands; rare-population discovery is outside this first balanced prototype. Save numerical normalization checks and fit failure reasons.

This is not ordinary k-means on squared coordinates. The model uses their **joint sum**, accounts for dimension through its normalizer, and models two radial density bands rather than centroid differences of arbitrary squared-feature clouds.

### Exact native assignment

The common width makes the posterior boundary particularly simple. Assign the outer group when

`t_S(x) > (a_0+a_1)/2 + b^2/(a_1-a_0) * log(pi_0*Z_d(a_1,b)/(pi_1*Z_d(a_0,b)))`.

Thus the exported rule is a sum of squared deviations in named original measurements, compared with a threshold. Discovery imputation, units, centre/scale constants and tie handling complete its executable definition. With two or three features it is a direct measurement-space plot; with more features it is a larger explicit rule whose cost must be reported.

The rule is the model's own assignment. It is not a surrogate promised to reproduce a distinct graph teacher. Shared width is an interpretable modelling restriction; failure on unequal-width or off-centre populations should be reported, not hidden by silently introducing a different classifier.

## A support objective with a common density interpretation

Do not rank supports by raw panel log likelihood: densities in different-dimensional spaces have different reference measures. Do not compare a two-feature graph score to a five-feature radial likelihood.

Fit and freeze a proper **joint background density q0(z)** on discovery data. Initially use an estimable correlated Gaussian background and modest p/n; do not impose feature independence on the correlated-Gaussian control. For every support, define a full-data replacement model

`p_S(z) = q0(z_-S | z_S) * g_2,S(z_S)`.

It is normalized because the conditional density integrates to one and g is normalized. It also uses the same conditional nuisance mechanism for both latent groups, so the posterior group assignment depends only on S. Comparing it with the same q0 on an independent search-validation block gives

`Gain(S) = mean[log g_2,S(z_S) - log q0,S(z_S)]`.

The conditional nuisance term cancels exactly. This is a difference in full-data predictive log density, measured in nats per observation, even though its evaluation only requires the panel marginal. It is not an arbitrary normalization of incompatible scores. Discovery-fixed changes of units cancel when both densities are transformed consistently.

For each support also fit a one-band model and report the two-band versus one-band predictive difference. A single annulus can strongly improve on a Gaussian background without containing two radial populations. Keep size and predictive improvement separate: record the gain–size frontier and prefer a smaller candidate only under a prespecified acceptable loss in predictive gain. Do not select the tolerance using external labels.

This construction is a valid comparison device, not a proof of cluster existence. Its meaning depends on the fitted background: q0's misspecification or poor covariance estimation can favor a panel for the wrong reason. Once a modest-dimensional prototype works, background estimation at p=200 or larger becomes an explicit research problem.

Conditional modelling of non-clustering variables already appears in model-based variable selection. Raftery and Dean compare models in which an added variable contributes clustering information or is explained by selected variables; Maugis and colleagues distinguish clustering, redundant and independent variables. The common-space formulation here should be compared with that work, not claimed as an unprecedented insight. [Raftery and Dean, 2006](https://sites.stat.washington.edu/raftery/Research/PDF/dean2006.pdf); [Maugis et al., 2009](https://www.sciencedirect.com/science/article/pii/S0167947309001686).

## Bounded feature search after the supplied-panel model works

Use a small beam of supports, with addition, deletion, and swap moves, cached fitted states and warm starts. Include several initial sizes and direct random multi-feature starts. Evaluate complete proposed supports under the normalized model; do not require every retained feature or pair to look individually clusterable.

The first inexpensive version can use 12 starting supports and a fixed total candidate-fit budget, with one search-validation block shared across the search. The budget and seed schedule are frozen before results. This search-validation set is an optimization resource, not an independent certification sample; reserve untouched rows for the final selected node.

A larger support may only become useful after several features cooperate. One-feature greedy ascent is therefore not sufficient. Retain some worse immediate candidates at distinct support sizes, allow block-addition moves, and reserve random multi-feature exploration. These provisions reduce a known failure mode; they do not guarantee recovery of arbitrary hidden high-order structure. Use the small known-support experiment below to distinguish objective failure from search failure.

Do not make an EA or reinforcement learner the central new mechanism yet. Either could eventually navigate these support moves, but it would optimize the same density objective. It cannot make that objective identify meaningful populations when its modelling assumptions fail.

## What counts as a split, including heavy-tailed controls

Positive predictive gain over a Gaussian is insufficient: a single heavy-tailed population can improve substantially under a richer radial model. Likewise, a two-component density may remain unimodal and should not automatically be presented as two separated bands.

The prototype should return both a **candidate radial model** and a separate split-evidence status. If the intended target is separated spatial bands, first require a valley between material modes in the fitted **spatial density profile** `r -> g_2,S(r)`. Do not substitute the radial probability density, which contains the volume factor. A common-centre scale mixture can have a monotone spatial profile even when its radius distribution has separated peaks.

Assess the frozen radius on untouched observations as a supplementary check. A standard dip statistic is an available diagnostic for unimodality of the scalar score distribution, with calibration and multiplicity made explicit; it does **not** certify a valley in the original-space density. [Hartigan and Hartigan's computation paper](https://rss.onlinelibrary.wiley.com/doi/10.2307/2347485). A valid population-level test of spatial band separation remains to be specified. Until then, label the fitted valley and scalar test as distinct diagnostics, and make no finite-sample spatial-cluster guarantee.

The first control set must include a correlated single Gaussian, a single elliptical Student-t population, one noisy shell, a continuous broad scale distribution, and a common-centre two-scale Gaussian mixture. The last case is a positive example for latent scale-component discovery but a negative control for multiple separated spatial bands. Plot the held-out radius distribution and fitted spatial profile separately and report split outcomes against the declared target. The score mapping and support are frozen before these held-out tests; if several supports or mappings can win, account for that full family. Lack of evidence should leave a node unsplit. Do not claim exact finite-sample control until the chosen implementation and calibration have been checked.

These controls test the intended trait: two separated radial bands, rather than generic non-Gaussianity or continuous heterogeneity. Even a successful result remains evidence under a declared shape/population interpretation, not proof of biological subtypes. Distribution-free cluster existence is not the target.

## Three milestones before a broad benchmark

### 1. Verify the mechanism on supplied panels

Use a small fixed matrix: two bands in 2, 3 and 5 informative dimensions; a mildly standardized elliptical version; one-band, correlated-Gaussian and heavy-tailed controls. Include both samples generated exactly from the proposed radial density and an off-model noisy-shell generator. Keep the data independent of the already-inspected pilot.

Fit only the native model on supplied S. Check proper normalization, parameter degeneracy, exact rule replay, out-of-sample assignments, one-versus-two-band evidence and runtime. Compare with an ordinary centroid rule and the old supplied-panel graph. The known-radius rule is an explicitly labelled ability ceiling, not autonomous performance.

**Go/no-go:** if the proposed density/rule cannot recover clearly separated supplied bands reliably, stop and repair the model or numerical fit. Do not compensate with a wider feature search. If it splits one-band/heavy-tailed controls frequently, the splitting criterion is not ready.

### 2. Verify the objective before the optimizer

Add independently generated nuisance measurements with matched univariate marginals. On this small diagnostic, evaluate the fitted predictive objective for the known panel, partial panels, matched-size random panels, and supersets containing nuisance variables. External labels and true supports are used only to inspect the resulting ordering.

**Go/no-go:** the known useful joint panel should consistently receive a useful predictive advantage on fresh rows. If it loses to nuisance panels under the intended objective, the failure is not fixed by stronger search. If useful supersets dominate everywhere without a defensible size tradeoff, automatic panel size is unresolved. This is one bounded objective test, not a broad benchmark campaign.

### 3. Demonstrate autonomous discovery

Run the bounded support search on the same prespecified population family, now without supplying S. Compare with an equal-budget random-support search. Record best candidate found, selected candidate, held-out native utility, support precision/recall, required size, and all failed/abstaining runs. Keep five- and eight-feature cases to test that the method is not restricted to enumeration of triples.

If the objective ranks the true panel well but autonomous search misses it, work on the search mechanism. If search finds a good panel but chooses a worse one, work on selection/validation. Only after these decisions should the method enter a small real-data study and broader comparator suite. A real dataset is chosen because the relevant trait is plausible and testable, not because it happens to give the best result.

## Scope and deliberate failures

The prototype assumes a common centre, approximately radial or axis-standardized elliptical geometry in selected original coordinates, and enough observations to fit a proper low-dimensional density. It is not expected to solve two moons, spirals, arbitrary connected manifolds, off-centre multiple groups, or covariance-sign regimes whose informative statistic is a sum of pair products. Those failures help define the method's domain; they should remain visible.

The existing centroid branch addresses a different trait, mean separation. The twelve-weak-signal generator may legitimately require more than three measurements; retaining a larger explicit rule is consistent with the user's current preference. A future method could select between declared native families using common predictive density comparisons, but adding all families now would blur the mechanism being tested.

If rare populations later enter scope, global 5% surrogate disagreement is inadequate: deleting a 1% population can pass that criterion. Require per-target false-negative and contamination/precision checks with their conditional sample counts, native assignment coverage and appropriate multiplicity. Cell dependence within subjects must be respected. This is not a reason to enlarge the balanced mechanism prototype prematurely.

## What would constitute an actual thesis contribution?

The quartic radial density, finite mixtures, coordinate support search, exact quadratic rules, held-out likelihood and stability checks are not individually defensible novelty claims without a more targeted literature review. A simple combination is a working baseline, not yet the thesis result.

The potentially substantive advance would be a demonstrated solution to **joint original-feature discovery for a declared nonlinear trait**, including cases with weak marginal evidence and more than three necessary measurements, together with a native interpretable assignment and a principled compactness/abstention procedure. Examples of meaningful methodological work include a support-update mechanism with a recovery or separation argument, a calibrated contrast that distinguishes discrete radial bands from continuous scale heterogeneity, or a dimension-comparable objective whose behavior can be characterized analytically and improves upon established model-based variable selection.

The first implementation's job is to reveal whether that advance is feasible. If an established model-selection method already solves the same trait and gives the same panels/rules at similar cost, the thesis needs a different differentiating problem or a smaller, honest contribution. A new name, a 3D display, or an interactive chooser does not substitute for that evidence.
