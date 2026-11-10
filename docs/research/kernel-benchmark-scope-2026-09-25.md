# A scoped benchmark for interpretable nonlinear feature panels

## Material Passport

- Origin: independent benchmark and claim design for the ATOMIC kernel/transform direction
- Origin Date: 2026-09-25
- Mode: experiment planning with primary-source verification
- Verification Status: PROPOSED; no clustering fits or new performance results
- Version Label: kernel_benchmark_scope_v1
- Inputs: existing project findings; GroupFS, DUFS, sparse kernel k-means, spectral extension and density-clustering sources linked below
- New calculations: Bayes-error expressions and numerical probability evaluations for two proposed synthetic families; these are information benchmarks, not algorithm results
- Intended output: compact original-feature panels, useful nonlinear partitions, and a frozen new-point assignment rule whose complexity can be inspected

## Immediate priority

Build and test one native nonlinear panel method now, with raw and simple-transform baselines beside it. The first useful result is a successful, reproducible six-feature shell panel with a correct new-point rule—not another large search over unrelated fitness functions.

Start with five diagnostic cases at p=50 and three fixed development seeds: two moons, a six-feature thick-shell mixture, an eight-feature covariance-regime mixture, a single correlated Gaussian, and a single thick shell. This is 15 datasets, with different claims for the two mixture families. Fit the proposed method, raw sparse k-means, a simple-transform comparator, random panels, and a supplied-panel nonlinear ability control. Integrate DUFS, GroupFS, and direct sparse kernel k-means for the frozen comparison once the native rule works. Do not use missing external baselines as a reason to postpone implementing the candidate.

Use original-feature budgets 2, 4, 8, and 16 initially. Count the union of original variables used by transformations: one squared feature costs one original variable, a pair product costs two, and a kernel on a six-variable panel still costs six. Keep a budget curve rather than choosing its best point using external labels.

## Structural claims to decide before seeing results

The proposed scope is narrower than universal clustering:

1. **Sparse nonlinear geometry:** when a small subset of original variables supports separated nonconvex populations, the method can identify a useful panel despite irrelevant variables.
2. **Distributed relevance:** at least one primary family requires more than three variables for the prespecified prediction target; success cannot be explained by recovering a padded two-dimensional picture.
3. **Stable assignment:** the frozen panel and native rule retain useful assignments on independent observations. A fresh test clustering is a separate replication diagnostic.
4. **Readable evidence:** the output names the original variables, specifies their transformations, shows representative cluster geometry, and exports the actual assignment rule. A small panel is not automatically a simple rule.

A fifth claim—correctly deciding whether multiple clusters exist—requires its own acceptance rule. Until implemented, report forced partitions on null controls as diagnostic outputs rather than accepted discoveries. Covariance-regime recovery below is explicitly a different structural target from separated density components.

Freeze the generator families, moderate and difficult settings, budgets, preprocessing, and compute allowance before the comparison. A failed spiral case stays in the results; a method that works only on radial structure should be described as such. Selecting an application scope is legitimate; silently removing unfavorable examples after observing them is not.

## A short staged matrix

| Stage | Cases | Dimensions / conditions | Question and permitted claim |
|---|---|---|---|
| 0: geometry and implementation | Moons, concentric rings, two spirals | Two informative coordinates; p=2 first, then p=50; one easy and one prespecified noisy setting | Does the representation and native readout recover the intended shape when supplied the useful panel? Padding alone proves no >3-variable capability. |
| 1: primary larger-panel task | Thick hypershells | s=6 and 12; p=50 first, p=200 after implementation; fixed radius ratio 1.35 | Does autonomous search recover distributed radial information and a useful panel beyond three features? |
| 1b: interaction diagnostic | Shared covariance regimes | s=8 and 12, paired correlations ±.8; p=50, then 200 | Can the method recover a joint dependence regime with identical one-feature class distributions? This is not a density-gap benchmark. |
| 2: density and substitute features | Stage-0 moons/spirals and stage-1 shells | Class proportions .5/.5 versus .2/.8; one fixed nonuniform within-manifold sampling setting; separate correlated-surrogate arm | Does local scaling or a kernel buy robustness? Does the method distinguish original identity from replaceable information? |
| Controls throughout | Independent Gaussian, correlated Gaussian, single thick shell; later a single curved connected manifold | Same p, comparable marginal scale and sampling budget | Can structure/fidelity be mistaken for multiple populations? Measure false declarations only if a declaration rule exists. |
| Domain follow-up | Full annotated Levine population pool; existing METABRIC contrast as development only | Fixed observation and measurement universe, with donor/patient separation where available | Do panels have independently verifiable domain usefulness and practical assignment rules? No universal biological claims. |

After the 15-dataset development pass, freeze the implementation and use five fresh seeds for the selected primary rows. A reasonable synthetic split is 800 discovery, 400 selection/validation, and 800 test observations. These sizes are a proposed computational starting point, not a power calculation. Increase sample size in a prespecified scaling row if kernel neighborhoods become too sparse; report the failure at the original size as well.

Independent rediscovery can use a second fresh discovery sample in the final primary comparisons. Count that fit and its tuning cost. Generator seeds, algorithm restarts, and patient cohorts are different units; multiple restarts are not independent datasets.

## A genuinely larger-panel radial benchmark

For a hidden signal set S of size s, generate

`Y ∈ {0,1}` with equal probability, `U ~ Uniform(Sphere^{s-1})`,

`X_S = R_Y V U`, with `R_0=1`, `R_1=1.35`, and `V ~ Uniform(.98,1.02)` independent of Y and U.

Shuffle column positions. For each nuisance column, independently generate a *new* radial/spherical draw and retain one coordinate, so its pooled marginal distribution matches a signal coordinate. Do not construct nuisance by permuting a column across discovery and test rows. Independent nuisance draws prevent simple variance or univariate-distribution screening from revealing the answer.

The full-panel radii occupy disjoint intervals [.98,1.02] and [1.323,1.377]. A rule based on `sum_{j in S} x_j²` separates them exactly in this generator. Thickness makes each component a shell with radial variation rather than just a noiseless mathematical surface. A later coordinate-noise arm can test robustness, without claiming the same zero-error oracle.

More than three coordinates matter for a checkable information reason. Without V, for any q<s signal coordinates,

`T = ||X_T||² | Y=y ~ R_y² * Beta(q/2, (s-q)/2)`.

The projected direction has the same distribution in both classes, so the projected norm is sufficient for the Bayes rule. Its equal-prior error is

`E_q = 1/2 * integral min(f_0(t), f_1(t)) dt`,

where `f_y(t)=BetaDensity(t/R_y²; q/2,(s-q)/2)/R_y²` on its support.

Numerical integration at q=3 gives:

| Signal dimensions s | Best possible three-coordinate error, before radial jitter | Full-panel error with the specified radial jitter |
|---:|---:|---:|
| 6 | .271792 | 0 |
| 8 | .317144 | 0 |
| 12 | .340389 | 0 |

The independent multiplicative jitter is a label-independent degradation of the projected observation, so it cannot improve the best three-coordinate error. A subset containing nuisance instead of signal cannot add label information. Thus these lower bounds also rule out reliable three-variable prediction in the thick-shell version. They are bounds on pointwise class error, not bounds directly expressed in ARI.

This provides an honest larger-panel test without a parity construction or an arbitrary label assignment. The visible cluster geometry and the target label are aligned. Report the exact generating support separately from the smallest panel adequate for a nonzero error tolerance; they are not automatically the same object.

A square-transform sparse-k-means baseline is essential here. If that simple representation solves the family, the result demonstrates a representation correction, not novelty of kernel feature selection. An RBF method must earn its extra complexity on geometry beyond this radial case.

## An interaction benchmark with quantified information gain

Use m independent pairs conditional on a shared regime Y∈{-1,+1}:

`X_{2b-1}=Z_b`,

`X_{2b}=Y*rho*Z_b + sqrt(1-rho²)*epsilon_b`, for b=1,…,m,

with independent standard-normal Z and epsilon and rho=.8. Set s=2m, permute original columns, and add independent standard-normal nuisance variables. Every individual signal coordinate has the same N(0,1) distribution in each regime; nuisance matches that marginal. The pooled covariance is also the identity, so marginal means, variances, and ordinary pooled correlations do not identify the signal pairing.

The conditional log likelihood ratio is

`log p(X_S|Y=+1)/p(X_S|Y=-1) = [2*rho/(1-rho²)] * sum_b X_{2b-1}*X_{2b}`.

For m observed complete pairs, its Bayes error is

`P[F_{m,m} < (1-rho)/(1+rho)]`.

At rho=.8, one pair gives error .204833; three pairs .052044; four pairs .028; and six pairs .00856. Any three original coordinates contain at most one complete pair, and unpaired coordinates add no regime information. Therefore an eight-feature panel has an attainable 2.8% error while any three-feature panel has at least 20.48% error. These numbers were evaluated from the F distribution; no clustering algorithm was fitted.

The caution is structural, not just statistical: these two Gaussian components share their mean and overlap, and their mixture has a mode at the common center. Treat this as recovery of latent covariance regimes, not evidence of disconnected high-density clusters. A method advertised only for geometric separation may legitimately decline it. If included in the method's scope, count it as a distinct claim and compare against an interaction-capable model. The analytically supplied likelihood rule is an information reference, not an autonomous feature-selection competitor.

## How to use moons, spirals, and variable density

Moons, rings, and spirals are valuable because they reveal whether the native geometry works before feature search obscures the diagnosis. Run supplied two-feature panels first. Failure there is a representation, bandwidth, or assignment problem; a better subset optimizer cannot repair it.

Noisy duplicate sensors of the same two latent coordinates test denoising and substitute-feature selection. They do not by themselves establish twelve-dimensional intrinsic cluster structure or unique necessity of twelve measured features. Keep that arm to compare group discovery, but do not let it replace the shell and interaction tasks.

For variable density, predeclare the same shapes with a 20% minority population and nonuniform sampling along each arm/surface. Change one factor at a time before combining them. Keep a separate bridge/overlap stress case rather than silently redefining the original clusters when their supports connect. Local affinity scaling is a relevant established comparator: [Zelnik-Manor and Perona's self-tuning spectral clustering](https://proceedings.neurips.cc/paper/2004/hash/40173ea48d9567f1f393b20c855bb40b-Abstract.html) was designed to address different local scales and clutter. That motivation does not guarantee success on every density contrast.

## Comparators that answer different questions

| Comparator | Role in this project |
|---|---|
| Raw sparse k-means, preserving its native weighted centroid rule | Established mean-separation baseline already available in the repo; measures the gain from changing representation. |
| Raw plus square transforms, with costs counted by original-variable union | Cheap radial comparator. Report it explicitly as a transform baseline; do not market it as a general nonlinear solution. |
| Random panels of the same original-feature budget, with the same nonlinear readout | Tests whether selection contributes beyond geometry. Include their fitting cost and average over a fixed random-panel allowance. |
| Supplied planted panel with the same readout; all-feature readout | Separates representation ability from search and quantifies nuisance damage. The supplied-panel result is an oracle diagnostic, not an unsupervised competitor. |
| DUFS plus a common frozen nonlinear readout | Differentiable graph/gate comparator. [DUFS](https://proceedings.neurips.cc/paper/2021/hash/0bc10d8a74dbafbf242e30433e83aa56-Abstract.html) explicitly learns a graph on gated inputs, addressing contamination of an all-feature graph. Its authors' implementation is available through [featselectlib](https://github.com/LindenbaumLab/project-featselectlib). |
| GroupFS plus that same readout | Direct group-discovery/interpretability comparator; retain its group output as well as original-feature support. |
| Sparse kernel k-means (SKKM) | Direct nonlinear feature-selection comparator, not just a linear baseline. [Park et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11727190/) use sparse ANOVA-kernel components and provide [author R code](https://github.com/bbeomjin/skkm). This is close prior art for sparse nonlinear panel/interaction discovery. |
| HDBSCAN on supplied and selected panels | Density-based ability comparator in the density stress stage. Include noise coverage and unassigned points, so it is not rewarded for dropping difficult observations. |

Classical [Laplacian Score](https://proceedings.neurips.cc/paper/2909-laplacian-score-for-feature-selection.pdf) can be added as a low-cost graph-filter baseline; it should not substitute for DUFS/GroupFS or SKKM. There is no need to launch a catalogue of dozens of methods before the first native nonlinear prototype runs.

Use two comparison views. For feature-selector comparison, every selected panel feeds the same training-fitted nonlinear readout, with matched budget and hyperparameter allowance. For end-to-end comparison, retain each method's native geometry and assignment rule. Name the view in the result table; do not credit a readout improvement entirely to feature selection.

## GroupFS comparison: preserve the useful idea and distinguish evaluation protocols

[GroupFS](https://ojs.aaai.org/index.php/AAAI/article/view/39521) jointly learns feature groups and their gates with sample/feature graph objectives. Its [official implementation](https://github.com/ShiraLifshitz/GroupFS) is available. The paper's moons experiment expands two coordinates into noisy copies, useful for group recovery but different from the larger-panel constructions here. Section 5.3 evaluates selected features using k-means with the known class count; its adaptive-budget setting is explicitly accuracy-guided, and its fixed-budget description also derives the shared budget using a local maximum of model accuracy. Therefore its reported budgets should not be imported as label-free choices. See the [primary extended paper](https://arxiv.org/html/2511.09166v1).

For this project's controlled comparison, freeze shared original-feature budgets independently of labels and train GroupFS on discovery rows only. Evaluate its learned group union at the actual feature count. If whole groups cross a budget boundary, report that actual count or prespecify a truncation rule; do not quietly trim the group after checking test accuracy. Record parameter settings, checkpoint selection, restarts, and full training cost. A paper-reproduction table and a new label-blind protocol table answer different questions.

## Native new-point assignment is part of the method

For a fixed kernel and discovery clusters C_g, kernel k-means has a direct frozen assignment:

`assign x to argmin_g [K(x,x) - (2/|C_g|)*sum_{i in C_g} K(x,x_i) + (1/|C_g|²)*sum_{i,j in C_g} K(x_i,x_j)]`.

This is the RKHS centroid distance, also given in equation 3 of [the SKKM paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11727190/). It avoids replacing the learned geometry with an unrelated generic classifier. Store the feature panel, preprocessing, kernel parameters, cluster membership, and any chosen prototypes/landmarks. A prototype approximation is another model whose discrepancy must be measured.

For a spectral method, implement an explicitly frozen Nyström/eigenfunction extension and discovery-fitted cluster readout; out-of-sample spectral extension has longstanding [primary prior art](https://papers.nips.cc/paper/2003/hash/cf05968255451bdefe3c5bc64d550517-Abstract.html). Local kernel scales for new points must use training neighbors without rebuilding the training graph from test data. Recomputing a joint training/test embedding is a transductive experiment and should have a separate label.

HDBSCAN's [documented approximate prediction](https://hdbscan.readthedocs.io/en/latest/prediction_tutorial.html) holds the trained condensed tree fixed and can leave points unassigned; it is not a fresh reclustering of the new batch. Preserve that distinction in comparisons.

## What to measure and show

| Output property | Primary measurement | Interpretation limit |
|---|---|---|
| Useful clustering | Held-out ARI/AMI; cluster sizes; balanced class error after alignment using non-test rows if error is reported | Existing labels are external targets, not optimization input. Geometric components and covariance regimes have different meanings. |
| Original panel | Size and acquisition cost; planted recall/false discovery on synthetics | Known generating support is not necessarily the unique smallest adequate panel. |
| Feature stability | Jaccard plus group/substitute coverage across independent discovery samples | Equivalent correlated substitutes can have low exact Jaccard. Dense full support can give meaningless high Jaccard. |
| Rule stability | Independent-model assignment agreement on a common untouched evaluation set | Stable partitions can occur in a single correlated Gaussian. |
| Readability | Number of original variables, transform terms, interactions, prototypes, and rule branches | A six-variable RBF rule using 800 reference points is compact in measurements but not automatically readable. |
| Shape | Original-panel conditional slices, radial/interaction statistics where appropriate, representative observations, boundary margins | A two-dimensional projection or UMAP picture is not proof of high-dimensional cluster separation. |
| Compression | Full-to-short-rule disagreement, availability/abstention, external quality before and after shortening | Fidelity only certifies approximation of the chosen teacher; retain the earlier separation between fidelity and truth. |
| Domain usefulness | Predetermined marker/pathway overlap, original-unit distributions, independent donor/cohort replication, blinded expert checks where possible | A plausible gene name or a post hoc pathway story does not verify usefulness. |
| Search efficiency | Total fitting, graph construction, bandwidth trials, transforms, restarts, wall time and memory | A final fast prediction step does not represent total search cost. |
| Null behavior | Number of declared clusters or explicit abstentions under a prespecified acceptance rule | A forced two-way splitter has no cluster-existence guarantee to score. |

The domain panel report should say what each measurement contributes, how replacing it with a correlated substitute changes the rule, and what is still unverified. Conditional perturbation or deletion diagnostics are useful descriptions; do not rename arbitrary column permutation effects as causal importance. For panels larger than three, show exact radial/product rules if learned, or a clearly labeled surrogate with its fidelity and coverage. Do not present an attractive low-dimensional plot as the actual assignment mechanism.

## A concrete decision after the first run

If supplied-panel nonlinear clustering fails on a shape, fix the geometry/readout before tuning feature search. If it succeeds but autonomous panels fail, inspect the selector against random panels and the simple-transform baseline. If shell panels succeed but spirals fail, keep a radial claim and investigate a more flexible native kernel without rewriting the result as general success. If both geometry and selection work but nulls are still partitioned, report useful partitions with an explicit unimplemented acceptance stage; do not attach a significance claim to them.

The plausible research contribution is a demonstrated combination of panel discovery, constrained nonlinear geometry, inspectable assignment, and independently checked usefulness. Whether that combination has a distinct novel contribution remains to be established against the direct kernel and group-selection prior art. The immediate experimental priority is to make one such combination work on the prespecified shell task and one nonradial shape, then expand scope only when the evidence supports it.
