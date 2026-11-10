# Shell geometry and Gaussian controls: what the completed obstacle suite establishes

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validation of saved output and mathematical followup
- Origin Date: 2026-09-17
- Verification Status: ANALYZED; saved arithmetic, generator, protocol and source hashes checked; no clustering fits rerun
- Version Label: obstacle_geometry_controls_v1
- Source run: `results/research_obstacle_checks/20260916T145427_229536Z`
- Scope: nine geometry jobs, six Gaussian-control jobs, and the three autonomous shell-retention jobs

**The current shell failure is both a geometry problem and a feature-discovery problem.** Supplying the correct five-feature panel makes squared spectral clustering and a radius rule succeed perfectly. Squaring all features and asking the current sparse k-means learner to discover the panel does not. The controls establish a separate limitation: high transfer fidelity and even substantial fixed-panel replication can occur in a single Gaussian population.

The complete manifest records 33/33 jobs in 102.63 seconds. All 42 recorded source hashes match the files inspected for this audit. Relevant hashes are `run_research_obstacle_suite.py`: `2297f485618e78e87fd4e434a93b3c6eef05b3a20a1721b273411171be711d7e`; `obstacle_audits.py`: `554f323e723b024e40a1c9832199703958c267195cad4e7362473ab3d8bf207d`; `datasets.py`: `9142b7d7716be1bbc10a61f1dd5258c4a9d8cfb4f82a97b53897ab4d70a09b5e`. The manifest contains the remaining hashes. This verifies correspondence with saved sources, not an independent rerun.

## Oracle geometry works, but the neighborhood scale matters

The geometry jobs provide the planted panel to the learner. Each listed sample size is the total dataset size, with half used for discovery and one quarter each for validation and test. Spectral test predictions use a seven-neighbor assignment fitted to discovery labels. The squared representation squares discovery-standardized original features, then standardizes their squares using discovery rows. The radius representation sums the squares of the first standardized features. It has a supplied radial inductive bias.

The table averages test ARI over seeds 3, 4 and 5. Every configuration is reported; these are not test-selected winners.

| Total n / discovery n | Raw spectral k=5 | Raw spectral k=10 | Raw spectral k=20 | Squared spectral, each k=5/10/20 | Raw centroid | Squared centroid | Radius centroid |
|---|---:|---:|---:|---:|---:|---:|---:|
| 480 / 240 | 0.02794 | 0.00567 | 0.00448 | 1.00000 | 0.01004 | 0.54027 | 1.00000 |
| 960 / 480 | 0.02429 | 0.00607 | 0.00763 | 1.00000 | 0.00769 | 0.65397 | 1.00000 |
| 1920 / 960 | 0.88800 | 0.00368 | 0.00026 | 1.00000 | -0.00133 | 0.53923 | 1.00000 |

Supporting files are `geometry_shells_n{480,960,1920}_seed{3,4,5}/summary.json`. All **27** squared-spectral results and all **nine** radius-centroid results have both training and test ARI exactly 1. Raw k=5 becomes useful at the largest size: its three test ARIs are 0.92625, 0.78721 and 0.95052. It would therefore be incorrect to conclude that raw spectral clustering cannot recover the shells. It is sensitive to sample density and neighborhood scale here.

The directed raw ten-neighbor diagnostic helps explain the failure. Averaged across seeds, the fraction of an outer-shell point's neighbors coming from the inner shell is **0.49608, 0.37464 and 0.18799** at total n=480, 960 and 1920. Inner-shell cross-neighbor fractions are zero except 0.000877 in n480/seed3. Sparse outer-shell coverage leads many edges inward. Increasing n reduces this problem, but k=10/20 still gives poor partitions in these runs. This diagnostic uses generator labels after fitting; it is an explanation of benchmark behavior, not an available unsupervised selection criterion.

## Autonomous squaring does not discover the panel

The separate `retention_shells_seed{3,4,5}/comparisons.jsonl` files use n=480, p=50, five planted features, three fixed L1 bounds (1.25, sqrt(8), sqrt(50)), and three restarts per bound. Restart selection uses the native objective within each bound. The raw and squared native weighted models are retained, rather than automatically replaced by spectral clustering.

- Across nine raw native configurations, test ARI ranges from **-0.00844 to -0.00121**.
- Across nine squared native configurations, test ARI ranges from **-0.00849 to 0.13955**. The maximum is seed3, bound sqrt(50); it is a retrospective descriptive maximum, not a selected model.
- Every top-five and top-eight panel from either representation contains **at most two of the five** planted features. Squared top-eight overlap counts, ordered by bound within each seed, are seed3: **0, 0, 2**; seed4: **0, 0, 0**; seed5: **1, 0, 2**.

This evidence supports changing the discovery objective/model family for shells. It does not establish that larger search budgets would never help. Full native support can exceed eight, and tiny positive weights can inflate the active-feature count; neither the raw positive count nor a post-hoc prefix is automatically an interpretable selected panel.

The benchmark is deliberately resistant to marginal feature screening: each nuisance feature is independently drawn from the same population marginal as each signal coordinate. Proper signal subsets can nevertheless retain information; this is not a parity benchmark or a claim that all five features are uniquely necessary.

There is also a useful mathematical warning about squared-covariance screening. For the idealized noiseless, balanced five-dimensional shells, write X=RU, with U uniform on the unit sphere and R in {1,2}. For distinct coordinates,

\[
\operatorname{Cov}(X_j^2,X_k^2)
=\frac{\mathbb E R^4}{d(d+2)}-\frac{(\mathbb E R^2)^2}{d^2}
=\frac{8.5}{35}-\frac{6.25}{25}=-\frac1{140}.
\]

The corresponding correlation is -1/67, approximately -0.01493, while the joint sum of squares is exactly 1 or 4. Thus powerful radial information can coexist with almost cancelling pairwise squared correlations. This is a derivation for the idealized population, not an estimate from the saved noisy/scaled samples. It argues against relying on squared PCA or pairwise screening alone; it does not prove their impossibility in every setting.

## Single-population controls can be repeatable

The controls are independent Gaussian features or a single equicorrelated Gaussian generated as `sqrt(.8)*common_normal + sqrt(.2)*independent_normal`. Neither has latent groups. External ARI is intentionally absent. The following descriptive averages span three seeds and three fixed sparsity bounds; these dependent configurations are not nine independent replications.

| Population / representation | Mean full native kNN-to-teacher ARI | Mean prefix-eight independent-centroid agreement | Range of prefix-eight agreement |
|---|---:|---:|---:|
| Independent Gaussian / raw | 0.90255 | 0.04507 | -0.00570 to 0.27841 |
| Independent Gaussian / squared | 0.89539 | 0.30548 | -0.04519 to 0.76586 |
| Correlated Gaussian / raw | 0.92408 | 0.78579 | 0.58431 to 0.90167 |
| Correlated Gaussian / squared | 0.81392 | 0.68028 | 0.43278 to 0.94819 |

The first agreement column measures a readout's fidelity to a learned teacher. The second compares transferred centroid labels with a centroid model reclustered on test rows **using the same discovered panel**. It does not independently rediscover features and is not test annotation ARI.

An instructive saved example is `controls_null_correlated_seed5/comparisons.jsonl`, squared representation, bound sqrt(8), prefix eight, `refit_unweighted_centroid` (`prediction_key=row0246`). Its training sizes are 198/42. Test predictions have sizes 106/14, versus 107/13 after test reclustering, with **ARI 0.94819 and disagreement 1/120**. This is a highly repeatable center-versus-tail partition of a one-population control.

For the correlated Gaussian, all nine raw native weighted density surrogates are negative (range **-0.87448 to -0.45491**), as are all nine squared native surrogates (**-0.89576 to -0.59873**). Raw native graphcut ranges from -0.09240 to -0.04751. Neither these numbers nor a standardized version is a calibrated acceptance test. The negative density values also make clear that good fidelity need not imply a density-separated partition under this surrogate.

This is consistent with the theoretical distinction between stable objective minimizers and meaningful groups in [Ben-David, von Luxburg and Pál, *A Sober Look at Clustering Stability*](https://www.tml.cs.uni-tuebingen.de/team/luxburg/publications/BenLuxPal06.pdf). Stability is useful evidence about reproducibility, but cannot substitute for a stated cluster definition. No false-split rate can be computed from this suite because no cluster-acceptance rule was applied.

## Recommended next step and the separate shell branch

The planned raw-model preservation, independent-discovery and compression experiment is a sensible next check for the mean-shift/real-data branch. Independent discovery on two disjoint halves and comparison on a common unused sample addresses a stronger question than fixed-panel reclustering. For synthetic observations, independent draws have a clear meaning. Two subsets or resamplings of METABRIC still do not create an independent cohort. The Gaussian controls must remain in that experiment because independent rediscovery can also reproduce an arbitrary partition of a correlated population.

A finite-sample upper bound on compression disagreement answers whether a smaller rule preserves its **own frozen teacher**. It does not establish that the teacher represents true clusters, or that the panel is minimal or biologically necessary. For a Clopper–Pearson/Bonferroni implementation, fit the full candidate ladder before validation, include all selectable candidates in the family, and fix label orientation on training rows or account for both orientations. Choosing the lower of the two validation errors and treating it as a prespecified binomial count requires that extra care.

For shells, the next meaningful experiment should change the learner, not normalize the old scalar again. Two small, established families offer useful diagnostics:

1. **Sparse native mean/scale mixtures.** Fit a shared latent group model allowing selected original features to change means and variances, with assignment retained as its native likelihood rule. Mean-only sparse clustering excludes the mechanism needed for concentric shells. Penalizing both means and component-specific variances already exists in [Xie, Pan and Shen (2008)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2777718/); it is an appropriate baseline, not a novelty claim. Under known ideal shell parameters, even an isotropic two-Gaussian likelihood ratio is a threshold on radius squared, so this family can express the desired assignment. Autonomous sparse estimation remains the question.
2. **Sparse additive quadratic projection with a density-valley target.** Learn an interpretable score `t(x)=sum_j [a_j*z_j + b_j*z_j^2]`, where `z_j` uses discovery-fitted centering/scaling. Enforce sparsity by original feature groups, then learn a boundary in this one-dimensional score. This preserves a named panel and a readable curved decision rule. The radius oracle is one member of this family. Low-density projection pursuit has an established foundation in [Pavlidis, Hofmeyr and Tasoulis (2016)](https://jmlr.org/papers/v17/15-307.html); their published linear method does not by itself provide this sparse quadratic extension or its guarantees. Dip-based feature extraction is also prior art, as in [Schelling et al., *Utilizing Structure-rich Features to Improve Clustering*](https://ecmlpkdd-storage.s3.eu-central-1.amazonaws.com/preprints/2020/lncs12457/lncs12457091.pdf). This is a research proposal to test, not a demonstrated solution.

Prefer the mean/scale mixture as the cheaper established-model diagnostic; retain the quadratic valley learner as a focused geometry-development direction if mixture discovery remains inadequate. Both require an honest nuisance model: the shell noise features themselves have non-Gaussian marginals. Comparing a mixture to an independent Gaussian background can reward fitting those marginals rather than recovering their shared latent structure. Compare likelihoods over the same original variables, allow a flexible independent-marginal nuisance baseline, and retain a correlated one-population baseline. Diagonal mixture components are misspecified for both within-shell dependence and the correlated Gaussian control; extra components can approximate such dependence without establishing clusters.

A decisive shell pilot would first verify each family's ability on the supplied panel, then discover among p=50 and p=200 with planted sizes 5/8/12, preserving the native assignment. Freeze a small configuration grid, report all configurations and matched nulls, and use new simulated draws for confirmation. Report panel recovery, native transferred ARI, rediscovery, and a directly inspectable score distribution separately. Optimization success and cluster existence remain different claims. Learned nonlinear transformations can change modality, so a transformed-space valley alone does not certify original-space populations; any eventual acceptance calibration must include the complete search under its explicitly stated null family.

No additional clustering fits or new learner implementations were performed for this audit. Its conclusions support a staged investigation, not superiority or novelty claims. Statistical review covered selection after seeing results, multiplicity, dependent configurations, test reuse, oracle information, estimand changes, null misspecification, absence of an acceptance rule, surrogate-versus-clinical relevance, benchmark scope, and uncertainty from only three seeds.
