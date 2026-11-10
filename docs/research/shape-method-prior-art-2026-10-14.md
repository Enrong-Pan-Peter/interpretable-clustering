# Shape-aware panel discovery: prior art and a falsifiable next step

**Material passport.** Focused primary-source review, 14 October 2026. Sources below are author manuscripts, original journal articles, or dataset-provider documentation. No new fits, downloads of datasets, installations, or changes to existing results. Mathematical statements marked as derivations are this audit's deductions. This is a bounded overlap check, not an exhaustive novelty search or a state-of-the-art comparison.

## What should happen before a working method exists?

Small diagnostic experiments are part of building the method. A full application benchmark is premature. We need enough comparison now to distinguish an implementation failure from a wrong objective or an unsuitable model family: a known-support oracle, an existing sparse mean model, an existing sparse mean-and-variance model, and the proposed change on a few prespecified mechanisms. Run the broad benchmark after a coherent discovery procedure, native assignment rule, and stopping behavior exist.

An early dataset audit is still useful: establish the observation unit, available feature meanings, dependence between observations, annotation provenance, and which claimed traits the data actually exhibit. Cytometry or breast cancer can later test usefulness. Neither should silently define what a cluster or an interpretable rule must be.

## The proposed ingredients already have substantial prior art

| Primary source | Relevant mechanism and consequence for this project |
|---|---|
| [Pan and Shen, 2007, *Penalized Model-Based Clustering with Application to Variable Selection*](https://www.jmlr.org/papers/v8/pan07a.html) | Penalized Gaussian mixtures select variables through component means under a common diagonal covariance. This is a useful mean-sensitive baseline, not a model for every variance-only distinction. |
| [Xie, Pan and Shen, 2008, *Penalized model-based clustering with cluster-specific diagonal covariance matrices and grouped variables*](https://arxiv.org/abs/0802.3125) | Joint shrinkage of means and variances supports variable selection with component-specific diagonal covariance; grouped variables and EM updates are included. This directly anticipates a sparse mean-plus-scale mixture. Adding variance sensitivity or grouped sparsity is not, by itself, a new method. |
| [Maugis, Celeux and Martin-Magniette, 2009, *A general variable role modeling*](https://www.math.univ-toulouse.fr/~maugis/publication/2009-01-01_maugis09csda/) | Separates clustering variables, redundant variables dependent on relevant variables, and independent irrelevant variables. Relevant to correlated nuisance and interchangeable panels: selecting the originally planted feature is a different target from finding an equally informative substitute. |
| [Scrucca et al., 2016, *mclust 5*](https://journal.r-project.org/articles/RJ-2016-021/) | Established Gaussian covariance families separate volume, shape and orientation; model selection spans covariance structures and component counts. Geometry adaptation and likelihood-based component selection are established. They do not automatically yield small original-feature panels or a density-cluster interpretation. |
| [Jiang, Wang and Leng, 2018, *A Direct Approach for Sparse Quadratic Discriminant Analysis*](https://www.jmlr.org/papers/v19/17-285.html) | Estimates sparse quadratic interactions and a linear discriminant term. Explicit sparse quadratic assignment is established. This method uses class labels; it is prior art for the rule family, not a label-free discovery comparator. |
| [Friedman and Meulman, 2004, COSA](https://academic.oup.com/jrsssb/article/66/4/815/7109385) | Different clusters can have different, overlapping attribute subsets; the work also develops a dissimilarity suitable for hierarchical clustering. Local panels and a hierarchy are not a sufficient novelty claim. A dendrogram is not automatically a deployable tree of compact assignment rules. |
| [Hofmeyr, Pavlidis and Eckley, 2019, minimum spectral connectivity projection pursuit](https://eprints.lancs.ac.uk/id/eprint/124926/) | Learns projections for binary separation and recursively constructs a divisive hierarchy with different local subspaces. This is a direct general-domain neighbor of the project's spectral branch; original-feature sparsity and reliable stopping remain separate questions. |

Also, [Yau and Holmes, 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3121559/) explicitly allow cluster-specific variable relevance. Their Bayesian hierarchy describes a prior/model; it should not be confused with an interpretable recursive routing tree. These sources establish prior art for the individual ingredients and several combinations of unsupervised discovery, local feature relevance, shape information, and hierarchical organization. A novelty claim about a precise joint formulation needs further comparison; this review does not establish one.

## What the mean-and-scale rule actually is

**Derivation.** For two diagonal Gaussian components, with variances \(v_{kj}\), posterior log odds are

\[
\log\frac{P(1\mid x)}{P(0\mid x)}
=c+\sum_j (a_jx_j^2+b_jx_j),
\quad a_j=\tfrac12(v_{0j}^{-1}-v_{1j}^{-1}),
\quad b_j=\mu_{1j}/v_{1j}-\mu_{0j}/v_{0j}.
\]

A variable whose mean and variance are identical in both components contributes nothing. A shared center gives a weighted sum of squared deviations. Proportional diagonal covariances give a threshold in a weighted radius. Therefore a sparse radial or additive quadratic rule is a native mixture assignment rule, not a new construction merely because it is readable. Arbitrary additive quadratics also need not be ellipsoids: mixed-sign coefficients produce different shapes. Off-diagonal covariance differences require cross-products.

**The crucial distinction: scale components are not necessarily density-separated clusters.** Let every Gaussian component have the same center \(\mu\), with positive definite covariance \(\Sigma_k\). Along any nonzero direction \(v\),

\[
\frac{d}{dr}f(\mu+rv)
=-r\sum_k\pi_k c_k(v^\top\Sigma_k^{-1}v)
\exp[-r^2v^\top\Sigma_k^{-1}v/2]<0\qquad(r>0).
\]

The mixture has one density mode at the center and connected, star-shaped superlevel sets. A successful scale-component classifier may therefore discover overlapping latent regimes without discovering multiple density clusters. Thin separated shells are a different distribution. A radial histogram is also not the original-space density: in an isotropic \(d\)-dimensional model the radial density contains an \(r^{d-1}\) volume factor. A ring-shaped histogram alone does not establish a density valley in feature space.

## A narrower contribution worth testing

The most useful next hypothesis is **nuisance-resistant discovery of a small original-feature panel supporting an explicit radial or mean gate, with a stated distinction between a latent-component explanation and separated geometry**. This targets the observed failure on shells beyond a known-support oracle. It is narrower than claiming a general new interpretable clustering framework.

Begin with one node. Compare a sparse mean model with the established sparse heteroscedastic mixture family and a deliberately constrained radial proposal. Preserve their native rules. Test whether the new discovery formulation recovers useful panels when individual features are uninformative or misleading, without merely isolating extreme observations. Prefer two or three features when adequate; report the necessary larger support honestly. A hierarchy should follow only after the root-level discovery mechanism works.

Potential contribution lies in a demonstrably useful formulation for **joint panel and radial-separation discovery under nuisance**, including a specified rejection/alternative-explanation mechanism. It does not lie in EM, squared features, a radius threshold, or better ARI alone. This review has not established that such a formulation is absent from the literature. If an existing sparse mixture solves the same cases at comparable panel complexity, adopt it as a component and move the contribution elsewhere.

Use a small mechanism suite, not an open-ended search for favorable data:

| Trait | Decisive question |
|---|---|
| Distributed mean signal, many irrelevant features | Does adding the scale branch preserve the already useful mean solution? |
| Equal means, differing scales; separately, thin separated shells with matched-marginal nuisance | Does the method find the relevant panel autonomously? Does it distinguish component membership from density separation? |
| Identical univariate marginals, different correlations | Is failure correctly attributed to a missing interaction rule? For opposite correlations, the Bayes rule involves \(x_1x_2\), outside a centered sum-of-squares rule. |
| Different informative panels in different branches | After the one-node test succeeds, does local discovery improve on a single global panel? |
| One Gaussian, one correlated Gaussian, one heavy-tailed elliptical population, one shell | Does a declared stopping procedure reject artificial subdivisions under its stated null? Forced splits cannot answer this question. |

Vary signal strength and nuisance dimension before seeing results; preserve failed cases. Record assignment quality, selected support, optimization sensitivity, and whether a split was accepted. For overlapping mixtures, the known latent labels are not perfectly recoverable: use oracle achievable risk as context. Any false-split claim needs a defined null and actual acceptance procedure; stability, BIC, and teacher fidelity alone are insufficient.

## Two real-data families to audit later

These are candidates chosen for observable traits, not claimed successes or ground-truth geometric clusters.

* **Chemical sensor responses:** [UCI Gas Sensor Array Drift at Different Concentrations](https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations) provides 13,910 measurements, 128 descriptors from 16 sensors, six gases, concentration information, and ten temporal batches. Useful questions concern grouped/redundant measurements and nuisance drift. Define batch-aware evaluation before fitting; gas identity is an external reference, while concentration and time can induce other genuine structure. A two-feature panel can still involve one or two physical sensors, so report both counts.
* **Industrial condition monitoring:** [UCI hydraulic systems](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems) provides 2,205 cycles, raw sensor time series, four component-condition annotations and a stability flag. This supports a trait audit of location, variability and multiple condition axes. Any cycle summaries must have fixed physical meanings and be declared before label inspection. The repository lists 43,680 raw time-point features; these are not 43,680 independently interpretable sensors. Audit cycle dependence and recording order before proposing a split; do not promise independent test rigs from this dataset.

Neither dataset establishes that a variance-only or radial method is appropriate. First verify metadata and traits; include both if they meet the prespecified eligibility criteria, regardless of initial scores. Keep labels out of panel discovery and method selection. Full comparative benchmarking comes after the mechanism and target are settled.
