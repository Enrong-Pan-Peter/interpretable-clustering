# Mathematical directions for discovering larger feature panels

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-09-14
- Verification Status: UNVERIFIED — research proposals; no new benchmark results
- Version Label: math_search_directions_v1
- Scope: independent mathematical/statistical assessment for the ATOMIC project
- Sources inspected: the 9 September project assessment; current calibration/search code; experiments 022–023; primary research sources linked below.

## Main assessment

There is no established reason to give up on panels larger than three. There is also no evidence that replacing the current fitness by one better scalar will solve the problem. Three distinct issues matter:

1. **What counts as a cluster?** A density valley, a recoverable mixture component, and an externally named biological group are different targets. A score for one can systematically reject another.
2. **What information reaches search?** The current mask-based optimizers receive a scalar after evaluating a subset. Joint models can use the whole data matrix to estimate conditional contributions from many features in one update.
3. **What makes a panel sufficient?** A panel can reveal a separation without being minimal, stable, biologically specific, or adequate for assigning future samples. Those are separate properties.

The strongest statistical alternative to the proposed smooth graph learner is **sparse discriminant mixture fitting**. The most economical nonlinear alternative to investigate afterward is **sparse projection pursuit with a small dictionary of linear and quadratic terms**. Neither family is new. Their value here is to expose which structural assumptions actually help ATOMIC, and to provide serious comparators before developing a new method.

## 1. A precise alternative: sparse discriminant mixture proposals

### Target and update

For a binary local split, assume

\[
X\mid Z=k\sim N(\mu_k,\Sigma),\qquad P(Z=1)=\pi.
\]

The Gaussian posterior log odds are

\[
\log\frac{P(Z=1\mid x)}{P(Z=0\mid x)}
=\log\frac{\pi}{1-\pi}+\beta^T\left(x-\frac{\mu_1+\mu_0}{2}\right),
\quad \beta=\Sigma^{-1}(\mu_1-\mu_0).
\]

Sparsity of **beta**, rather than just the mean difference, gives a panel that directly controls the assignment rule. A conditional update can use

\[
\hat\beta^{(t+1)}=\arg\min_b
\left\{\frac12 b^T\hat\Sigma^{(t+1)}b
-b^T(\hat\mu_1^{(t+1)}-\hat\mu_0^{(t+1)})
+\lambda_t\|b\|_1\right\}.
\]

Soft memberships update the means and covariance; the sparse direction updates memberships. This is the established CHIME approach, not an ATOMIC invention. Its theory is conditional on a Gaussian mixture model, sparsity, signal and initialization assumptions; it is not a guarantee for arbitrary biological data. The [CHIME paper and code](https://drjingma.com/papers/cai-chime) are directly relevant. [Azizyan, Singh and Wasserman (2015)](https://proceedings.mlr.press/v38/azizyan15.html) also combine nonspherical mixture estimation with sparse discriminant analysis.

### Why the distinction between beta and mean differences matters

This elementary two-feature example is useful when interpreting panels. Let

\[
\Sigma=\begin{pmatrix}1&\rho\\\rho&1\end{pmatrix},
\quad \mu_1-\mu_0=(d,0)^T.
\]

Then

\[
\beta=\frac{d}{1-\rho^2}(1,-\rho)^T.
\]

The second feature has no mean shift, yet helps assign a sample by adjusting for correlated variation. Conversely, two correlated features can both shift in their means while only one is conditionally necessary. A panel intended for assignment therefore need not coincide with a list of marginal markers. Reports should distinguish a marker role from an adjustment role; neither automatically implies a causal mechanism.

### Proposed ATOMIC experiment

Use CHIME or a clearly labeled practical variant as a proposal engine, then pass its support and partition through the same evaluation interface as graph proposals. Include sparse k-means as a simpler comparator. Run a fixed sparsity path with several starts and retain distinct partitions, rather than just the solution with the largest in-sample objective. Panel size is selected on validation data under a declared tolerance; do not tune the path by external ARI.

Test a single Gaussian with correlated features against two overlapping mean-shift components in the same covariance structure. This comparison directly probes the project's difficulty on expression contrasts. If covariance estimation is unstable, a shared low-rank-plus-diagonal covariance is a practical variant to test, not a free guarantee. Penalized factor mixtures already address correlated high-dimensional expression data: [Xie, Pan and Shen (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2852217/).

Record two different conclusions:

- **Component recovery:** held-out agreement with planted/external groups, posterior uncertainty, replication, and predictive density relative to a prespecified one-component model.
- **Density separation:** evidence of an actual valley in the selected coordinates.

A mixture can improve predictive density and approximate a skewed or heavy-tailed single population by several components. Therefore predictive likelihood improvement is not proof of discrete clusters. Compare against a robust one-population model, and do not silently relabel overlapping components as topological clusters.

**Decisive outcome:** if this model finds useful 5–10-feature panels where graph candidates rank poorly even when given the same panels, the problem is partly a mismatch between a gap-seeking objective and the desired biological grouping. If good graph candidates exist but the graph search misses them, proposal generation remains implicated. If both methods succeed, the research question becomes compactness and verification rather than basic discoverability.

**Limitations:** a linear discriminant does not separate concentric shells or arbitrary nonconvex populations. Correlated substitutes can make an exact support nonunique. Sparse EM can converge to an unhelpful local optimum. CHIME is a strong comparator, not a replacement universal clustering theory.

## 2. A concrete nonlinear proposal: sparse linear/quadratic projection pursuit

### Representation

After fitting centering/scaling on discovery rows, construct a small dictionary

\[
\phi_j(x)=(\tilde x_j,\ \widetilde{x_j^2}),\qquad
u_\theta(x)=\sum_{j=1}^p\{b_j\tilde x_j+c_j\widetilde{x_j^2}\}.
\]

Both dictionary entries belong to the same original-feature group. Optimize

\[
\max_\theta\;\operatorname{Dip}(\hat F_{u_\theta})
-\lambda\sum_j\sqrt{b_j^2+c_j^2},
\qquad \|\theta\|_2=1,
\]

with a numerical minimum-variance condition on the projected discovery values. An alternative is a constrained low-density cut objective with minimum child mass. Do not use unpenalized unrestricted nonlinear transformations.

The support is the set of original variables whose two-coefficient group is active. The output can be a readable rule `u(x) > t`. The dictionary has 2p columns, rather than all subsets or all pairwise products. A sparse dip implementation needs care with sorting and piecewise derivatives; projection-pursuit optimization of the dip itself predates this project: [Krause and Liebscher](https://las.inf.ethz.ch/files/krause05multimodal.pdf). Density-based and spectral projection pursuit also already exist: [Minimum Density Hyperplanes](https://jmlr.org/papers/v17/15-307.html) and [Minimum Spectral Connectivity Projection Pursuit](https://arxiv.org/abs/1509.01546).

This is a proposed restricted representation experiment, not a novelty claim for sparse polynomial projection pursuit.

### How this goes beyond three features

A five-dimensional radial split can have the form

\[
\sum_{j\in S}(x_j-a_j)^2>r^2,\qquad |S|=5.
\]

Expanding the square fits the dictionary above up to an intercept. All five features can contribute to one scalar radial coordinate. The optimizer can update their coefficients together without waiting for a complete five-feature mask to be sampled. Several weak mean shifts are similarly represented by the linear terms.

This changes the representation and available feedback; it does not prove that the optimizer will find the right support. The dip objective still has local optima, correlated nuisance can dominate, and increasingly flexible dictionaries can fit accidental gaps. General spirals are outside this simple family; cross terms would increase cost and need their own hierarchy/regularization design.

### What must be verified

A nonlinear transformation can create modes from a connected single population. For example, saturating transformations can compress a Gaussian's tails toward two extremes. Therefore a large projected dip is **only a proposal score** for this branch. Freeze the proposed panel, transformation and partition, then check the corresponding separation in the original selected coordinates on independent rows. The projected rule should not overrule failed original-space evidence.

For the linear branch, a confirmed multimodal projection has a stronger interpretation against log-concave one-population models: linear projections preserve log-concavity. That restricted null is still not equivalent to every possible meaning of “one cluster.” Avoid claiming that a fixed-projection test automatically adjusts for choosing among many projected candidates on the same validation rows.

### Minimal decisive comparison

Compare linear-only, quadratic-only and grouped linear-plus-quadratic proposals on:

1. Five weak mean-shift variables plus independent nuisance.
2. Five-dimensional concentric shells plus nuisance with matched one-dimensional marginals.
3. A single correlated Gaussian and a single curved continuous population.

Use the same held-out panel/partition evaluation as the smooth graph learner, and include oracle supports as diagnostics. The quadratic branch is worth retaining only if it expands useful candidate coverage on shells without creating an unacceptable increase in accepted negative-control splits. Improved training dip alone is a failure of this experiment's target.

## 3. Dependence sketches and group testing: useful ideas with strong conditions

The independent-column calibration currently uses a null closer to feature independence than to absence of clusters. That same contrast can still be useful for **proposal generation** if its meaning is kept explicit.

Let

\[
T(S)=D_{KL}\left(P_{X_S}\,\middle\|\,\prod_{j\in S}P_{X_j}\right).
\]

This is total correlation. Its increment is

\[
T(S\cup\{j\})-T(S)=I(X_j;X_S)\ge0.
\]

An ideal joint-versus-product classifier estimates a density ratio related to this quantity. It can use nonlinear interactions and inspect a large context at once. A leave-group-out comparison could identify groups that supply dependence only conditionally on other features, which singleton screening misses.

However:

- A correlated Gaussian has positive total correlation without multiple density modes.
- High-dimensional density-ratio or mutual-information estimation can require a large sample and is vulnerable to nuisance dependence.
- Monotonicity of population total correlation does not imply the graph clustering score stays useful after adding nuisance variables.
- A discriminator must be evaluated on held-out genuine and shuffled rows; memorizing discovery samples creates a misleadingly strong contrast.

Group testing only becomes a scaling argument when a valid group oracle exists. If `q(A)` reliably indicated whether a candidate set retained the needed structure despite irrelevant variables, backward group deletion could localize a small support. Current gap scores do not have that monotonicity: adding nuisance may erase the geometry. A large random context also contains an unknown support of size s with probability roughly alpha^s if each feature is retained with probability alpha. This is better coverage than uniformly sampling tiny masks, but does not address the harder question of recognizing signal inside that context.

I would not implement a neural dependence oracle before the two simpler mechanisms above. If both fail specifically on matched-marginal interactions despite good oracle panels, it becomes a motivated third experiment. It must still feed a separate clustering check.

## 4. What is and is not an informative higher-order benchmark

“Needs five features” can mean at least three things:

| Case | Information in smaller panels | What failure means |
|---|---|---|
| Several weak mean shifts | Small but nonzero signal accumulates | Search/estimation can exploit distributed evidence |
| Nonlinear geometric structure such as shells | Proper projections overlap, but joint moments/dependence may reveal support | Representation and conditional feedback matter |
| Arbitrary parity labels on an otherwise symmetric cloud | The supplied labeling may not be identifiable from the unlabeled distribution | Binary label ARI can be the wrong target |

For example, if all hypercube vertices occur symmetrically and binary labels are assigned by an unknown parity, observing X alone does not distinguish that labeling from many other assignments. If the distribution instead contains only vertices satisfying a parity constraint, the distribution itself changes, so it is a different problem. Do not transfer a hardness conclusion between these cases or to ordinary continuous biological data.

For shells, draw nuisance coordinates independently from the informative coordinate marginal. This removes easy marginal shortcuts while retaining a meaningful joint radial structure. For mean shifts, vary support size under both fixed per-feature signal and fixed total signal. In the latter design, each feature becomes weaker as support grows; declining oracle performance is a sample-size/separation issue, not automatically a search failure.

To establish a method beyond size three, show that an autonomously found panel larger than three beats its best tested smaller reductions on held-out evidence. Returning five coordinates, or raising a size cap, does not establish that the extra coordinates help.

## 5. Graph learning, neural models and reinforcement learning

**Fixed global graph:** a full-space graph can be dominated by nuisance features. A feature selector evaluated only against that graph may learn to explain the nuisance geometry. [SC-FS](https://arxiv.org/abs/2210.15801) gives an existing example of initial clustering followed by conditional feature scoring and reclustering, with guarantees in a sparse Gaussian-mixture setting. It is a valuable baseline; its initialization assumptions should not be omitted.

**Jointly learned graph:** allows the geometry to change as irrelevant features disappear, but can reinforce an arbitrary split. Bandwidth collapse, extreme feature weights and tiny disconnected groups are potential objective shortcuts. Fix or explicitly regularize scale, constrain child mass, use multiple starts, and verify finalists under one common evaluation protocol. Compare the unweighted selected panel as well as the learned weighted geometry: a list of features may not reproduce a separation that depends on extremely precise weights.

**Neural networks:** can supply useful nonlinear proposal gradients and share statistical strength across features. The useful information comes from the data, architecture, training objective, or external prior. Reconstruction can favor nuisance variance; joint/product classification can favor dependence; a nonlinear embedding can manufacture separation. A network trained on those objectives does not create an independent reason to trust its clusters. DUFS and [GroupFS](https://ojs.aaai.org/index.php/AAAI/article/view/39521) already occupy much of the differentiable feature/group-selection territory.

**Reinforcement learning:** a policy acting only on masks and receiving the same scalar reward will not repair the reward's target mismatch. It may still learn a better search policy if trained across many related tasks or given informative data summaries. That is a new, costly learning problem, and its advantage should exceed random-plus-local-search at matched total computation, including policy training. A policy trained using biological labels or pretrained biological knowledge is legitimate when disclosed, but makes the final method weakly supervised or prior-informed rather than purely data-only unsupervised discovery.

**Evolutionary search:** retains a plausible role after a useful panel/partition exists: substitutions, multiple irreducible panels, nonlinear rule search and maintaining diverse partitions. No theorem says evolutionary computation must win. Its present failure does not demonstrate that a different representation cannot work.

## 6. A bounded next experiment and decision rules

The root task is building a common diagnostic harness; this note does not add competing scripts. The following additions are recommendations, with commands to be supplied only after implementation.

Use discovery/selection/confirmation rows, preserving independent biological sampling units where available. Fix the candidate-generation budget and selection rules before inspecting labels. Start with 5–10 seeds for debugging and extend only the promising comparisons.

| Diagnostic | Measurement | Decision it supports |
|---|---|---|
| Candidate coverage | Best external ARI among proposed panels, used only after fitting | Can the proposal mechanism reach useful structure? |
| Selection regret | Diagnostic best-candidate ARI minus selected-candidate ARI | Is useful structure present but ranked away? |
| Compression | Held-out loss after each deletion/replacement | Do larger panels have necessary features? |
| Original-space evidence | Same-partition geometry and replication | Does a learned representation preserve a meaningful separation? |
| Negative controls | Accepted splits versus search budget | Does longer search manufacture apparent discoveries? |
| Resource scaling | Wall time, memory, unique panels, total proposal training cost | Is an apparent gain bought by greater computation? |

Use one Levine contrast and one METABRIC contrast as scoped development cases alongside controlled data. A label-selected contrast is a diagnostic population, not evidence that the complete unlabeled hierarchy was discovered. Keep an untouched real-data case for later confirmation.

The immediate comparison should be current search, random masks, smooth sparse graph proposals, sparse k-means, and a sparse discriminant mixture comparator. Add quadratic projection proposals if the graph branch fails on the shell regime or if readable nonlinear rules become a decisive objective. Do not launch a large neural or RL training study until the diagnostics identify a missing capability that it can plausibly supply.

## 7. Where a contribution might emerge

Sparse clustering, sparse discriminant vectors, joint feature/partition optimization, factor mixtures and projection pursuit are already established. Even sparse Bayesian mixture fitting with adaptive cluster count has recent coverage: [Yao, Xie and Xu, JMLR 2025](https://www.jmlr.org/papers/v26/23-0142.html). These ingredients cannot alone carry a novelty claim.

A possible ATOMIC contribution is a defined procedure that discovers **local, compact original-feature panels**, distinguishes alternative explanations from different partitions, reduces panels under a reproducibility constraint, and returns evidence about the actual partition. The new part would need to be a specific search or verification mechanism with measurable benefit over straightforward combinations of the existing methods.

There is a tractable theoretical target once an implementation works: characterize panel reduction under a partition-preservation margin, with correlated substitutes treated as an equivalence class. A theorem about a known panel or fixed graph would not automatically cover adaptive panel discovery. Do not promise a universal theorem or a universal cluster-confidence z-score.

This review found plausible routes and close prior art. It did not establish novelty, run these candidates, or conclude that any one route will win on the project's data.

## Implemented comparator after this review

`atomic_research/sparse_kmeans.py` now provides a deliberately simpler established comparator: alternating weighted two-cluster k-means and nonnegative feature weights with L2/L1 constraints, following the sparse-clustering framework of [Witten and Tibshirani (2010)](https://pubmed.ncbi.nlm.nih.gov/20811510/). It generates panel candidates across a sparsity path and random starts; it does not implement CHIME, select a final panel, or validate cluster existence. Its elapsed time and diagnostics include all clustering and weight updates.

Eight focused checks passed using `.venv-research/Scripts/python.exe -m pytest tests/test_research_sparse_kmeans.py -q`. These compare the weight update against an independent constrained solver, check the between-cluster objective and alternating improvement, and exercise reproducibility, feature permutation, scaling, constant features and input validation. This establishes implementation checks, not empirical improvement on ATOMIC benchmarks. The primary harness will supply those results.
