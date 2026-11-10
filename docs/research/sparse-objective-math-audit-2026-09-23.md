# Population audit: sparse BCSS can prefer a low-information split

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: mathematical audit and experiment planning
- Origin Date: 2026-09-23
- Verification Status: ANALYZED; derivation, numerical constants and conditional weight optimization checked; no new clustering fits run
- Version Label: sparse_objective_math_v1
- Sources inspected: `atomic_research/datasets.py`, `sparse_kmeans.py`, `retained_models.py`, `replicated_panels.py`
- Trigger: the completed panel-replication experiment, `results/research_panel_replication/20260921T202232_578177Z`; this document does not independently re-audit that run's results

**The proposed counterexample is correct.** In the population version of the current standardized mean-shift benchmark with 12 equally informative features and total mean separation 3, the Bayes-direction split has optimized weighted BCSS per observation **0.59054**. Splitting one independent Gaussian nuisance feature gives **0.63662** under the same weight constraints. The intended partition therefore is not a global maximizer of this objective. This is a mismatch between the objective and the desired partition, beyond finite-sample search failures.

It is not a proof that the global optimum must be pure noise, that all useful partitions lose, or that every finite run fails. A one-signal-coordinate split is another higher-scoring, much less informative competitor. The appropriate conclusion is that better optimization alone cannot guarantee recovery of the intended distributed signal.

## What objective is actually implemented

The code's `_between_ss` returns the ordinary per-feature sum of squared differences between group means and the grand mean, weighted by group counts. `_sparse_weights` maximizes their weighted sum under nonnegative weights, L2 norm at most 1, and L1 norm at most the specified bound. `fit_panel_ladder` sets that bound to sqrt(cap), which is **4** for the default cap 16 when at least 16 features vary. The retained learner uses this native weighted BCSS to choose among restarts.

This follows the established sparse-k-means formulation of [Witten and Tibshirani (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2930825/). Their pairwise-distance expression differs by a common factor of two from the code's ordinary BCSS convention; that factor does not affect the comparison. The paper also distinguishes the nonconvex alternating optimization from a guaranteed global solution. The counterexample below concerns the objective itself, even before optimization quality is considered.

In the population limit, the two successive raw standardizations in the current pipeline reduce to unit marginal variance. Finite discovery samples use estimated moments and need not have exactly the population ordering derived here.

## Derivation for the observed-data split

Use `s` for the number of signal features, `a=1.5` for half the separation, and `L=4` for the L1 weight bound. The generator has

\[
X_j=\epsilon_j+\frac{a}{\sqrt{s}}Y,\qquad j\in S,
\]

where Y is equally likely -1 or +1, and all noise coordinates are independent standard Gaussians. Nuisance features have no Y term. Each signal coordinate has variance `1+a²/s`; after population standardization, call it Z_j.

Let `u` have coefficients `1/sqrt(s)` on the signal panel and zero elsewhere. The projection

\[
T=u^T X=aY+G,\qquad G\sim N(0,1)
\]

has equal mixtures of N(-1.5,1) and N(1.5,1). The intended observed-data partition is `C=sign(T)`. It is the Bayes classifier of the latent group under this known generator, not the latent group labels themselves.

The conditional-mean step is important. For each signal coordinate,

\[
X_j=\frac{T}{\sqrt{s}}+r_j,
\qquad r_j=\epsilon_j-\frac{G}{\sqrt{s}}.
\]

The Gaussian residual r_j is independent of G, and also independent of Y. Therefore it is independent of T and has mean zero conditional on C. Symmetry gives `P(C=+1)=1/2` and

\[
\mathbb E[Z_j\mid C=\pm1]
=\pm\frac{m}{\sqrt{s+a^2}},\qquad
m=\mathbb E|T|
=2\phi(a)+a\{2\Phi(a)-1\}.
\]

Numerically, `m=1.5586135875252092` and `m²=2.429276315218203`. Every nuisance conditional mean is zero. Consequently the population BCSS per observation for each signal feature is `m²/(s+a²)`.

For this fixed partition all `s` positive BCSS values are equal. Cauchy–Schwarz gives their optimal nonnegative L2-constrained weights as `w_j=1/sqrt(s)` on S. Their L1 norm is sqrt(s), so they are feasible for `s<=16` under L=4. Thus

\[
J_{\rm signal}(s)
=\max_w\frac{\operatorname{BCSS}_w(C)}{n}
=\frac{m^2\sqrt{s}}{s+a^2}.
\]

These centroids and weights also reproduce `sign(T)` as their nearest-centroid boundary. The comparison does not depend on using an infeasible labeling rule.

## A feasible nuisance competitor

Choose one nuisance coordinate q and partition at `X_q=0`. Its group means are ±sqrt(2/pi), with balanced groups. All other conditional means are zero because they are independent of this coordinate. Put weight 1 on q and zero elsewhere. Both weight constraints hold, the nearest-centroid boundary reproduces the sign split, and

\[
J_{\rm noise}=\frac{2}{\pi}=0.6366197723675814.
\]

| Signal features s | Optimized score for sign(T) | Score using latent Y labels | One-Gaussian-feature score | Observed-signal minus noise |
|---:|---:|---:|---:|---:|
| 5 | 0.749245 | 0.693952 | 0.636620 | +0.112625 |
| 8 | 0.670344 | 0.620874 | 0.636620 | +0.033725 |
| 12 | 0.590545 | 0.546963 | 0.636620 | -0.046075 |
| 16 | 0.532444 | 0.493151 | 0.636620 | -0.104176 |

The observed-signal crossing occurs at s approximately **9.52985**; among the tested feasible integer sizes, the nuisance competitor wins from s=10 onward. The formula here assumes sqrt(s)<=L. It must not be extrapolated unchanged beyond the L1-feasible range.

For the latent partition Y, the numerator is `a²=2.25`, not m². Those labels have score `a²*sqrt(s)/(s+a²)`, but Y is not a deterministic assignment function of the overlapping observations. Comparing only latent-label BCSS would incorrectly suggest the same conflict already at s=8; the observed Bayes-direction split actually exceeds the nuisance competitor there.

For the Bayes-direction rule, the population classification error relative to Y is `Phi(-1.5)=0.0668072`. The limiting ARI under balanced symmetric errors is `(1-2*error)²=0.750624`. This is an asymptotic descriptive reference, not a finite-sample expected ARI or a guarantee for a fitted panel.

## Scope: concentrated weak signal can also win

At s=12, even the feasible rule using just one signal feature with weight 1 has population score **0.63964653**, slightly above the Gaussian nuisance competitor. Its limiting ARI with Y is only **0.11222129**. The full signal direction has substantially better group recovery but a lower objective.

This example follows by replacing a with `a/sqrt(s)` in the absolute-normal moment and dividing by that coordinate's total variance. Other signal coordinates have nonzero conditional means under this one-coordinate partition, so optimizing weights for that fixed partition can increase its score further. That conditional weight optimum need not preserve its boundary on a subsequent centroid update; it is not being claimed as a fitted native solution here.

Both the full signal split and the nuisance split are population Lloyd/weight-update fixed points with their respective weights: their conditional centroids reproduce their assignments, and their optimal feature weights remain unchanged. Their ordering illustrates why adding favorable starts and then selecting the largest native objective can still favor poorer group recovery. The comparison requires only one nuisance feature. Increasing p from 50 to 200 is not the source of this population effect, although it can increase finite-sample search opportunities for accidental splits. The current n=800 four-block design has only 200 observations per discovery fit, where those finite-sample effects also matter.

## Most decisive next ablation

Separate fixed-partition ranking from optimization, using identical discovery rows, scaling, weight constraints and reporting units.

1. **Score three frozen partitions on each existing discovery block:** the saved native labels; the observed oracle-direction labels; and a prespecified nuisance-coordinate sign split. Optimize only the weights for each frozen partition, and report weighted BCSS/n, weight norms and group sizes. The oracle and nuisance identities are privileged diagnostic information, never autonomous discovery inputs. If examining many nuisance coordinates, report both the prespecified comparator and the training-selected maximum explicitly.
2. **Then compare initializations of the same learner:** its ordinary starts, an oracle-panel/signal-direction start, and a prespecified nuisance start. Keep the same weight bound and iteration budget. Save objective and panel/partition changes after each update, and evaluate frozen assignments on fresh rows. Report every arm before any maximum-objective aggregation. Distinguish the conditional optimum in step 1 from the final deployed objective after reclustering.
3. **Interpret the two axes separately.** A substantially better oracle-start objective that ordinary starts miss supports an optimization problem. A higher-scoring low-ARI solution, despite a good oracle candidate being available, supports an objective problem. Both can occur in the same dataset. An objective increase accompanied by an ARI decrease is particularly direct evidence of conflicting targets; an unexplained objective decrease should first trigger an implementation check.

The present derivation already answers the population comparison. Larger synthetic discovery samples can test convergence toward it, but are secondary to this small, paired ablation. Existing inspected results remain development evidence; new seeds or sample sizes chosen after this diagnosis should be reported as a followup, not retroactive confirmation of the earlier protocol.

## A useful alternative diagnostic, with a counterexample of its own

One possible diagnostic changes the model from a diagonal feature metric to a sparse signed projection `t=v^T x`, retaining its native one-dimensional threshold as an interpretable rule. For the correct mean-shift direction, the between/total variance ratio in that projection is

\[
R_{\rm projection}=\frac{m^2}{1+a^2}=0.747469635452,
\]

independent of how many coordinates share the signal. A fixed projection of any multivariate Gaussian remains Gaussian; its population optimal two-means ratio is 2/pi after normalization, regardless of covariance anisotropy. This removes the particular dimension penalty in the calculation above. By contrast, merely dividing the current feature-weighted BCSS by its weighted total variance gives **0.1704755** for the s=12 signal partition versus **0.6366198** for nuisance, making this comparison worse.

However, projected two-means ratio is **not a general solution for cluster validity**: a single uniform population on `[-sqrt(3),sqrt(3)]` has variance 1 and a symmetric-split ratio **0.75**, which exceeds even the desired Gaussian-mixture direction's 0.74747. Thus this can be a useful Gaussian-family objective diagnostic, not a universal clustering fitness. Uniform, skewed and heavy-tailed one-population controls would be needed before broader claims.

Two-means cluster-index methods and Gaussian-null calibration already exist; [Huang et al., *Statistical Significance of Clustering using Soft Thresholding*](https://pmc.ncbi.nlm.nih.gov/articles/PMC4706235/) discusses the ratio and its Gaussian-null interpretation. Rejection of Gaussianity is not a general proof of multiple populations. Adaptive selection of projections adds another search layer that needs its own valid treatment. For a density-separated-cluster definition, directly optimizing and validating a valley or multimodal structure is the more relevant subsequent direction; [Minimum Density Hyperplanes](https://jmlr.org/papers/v17/15-307.html) provides established projection-pursuit prior art. No novelty or general validity claim follows from this proposed diagnostic.

Arithmetic was checked with SciPy's normal moments, and the existing `_sparse_weights` function reproduced the analytic optimum for s=5/8/12/16 with zero nuisance scores. No Monte Carlo fit, new learner, or change to historical code/results was performed. The audit distinguishes objective preference, optimizer limitations, finite-sample variation, privileged oracle information, annotation-based retrospective evaluation, adaptivity, model misspecification, cluster definition, multiple comparisons, benchmark scope and unproven generalization.
