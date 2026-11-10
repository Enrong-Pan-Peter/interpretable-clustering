# Start the kernel fix, with bounded development comparisons

**Decision:** move from broad obstacle audits to a new, separate implementation. Keep a few matched comparisons inside it. The previous experiments already justify preserving the native model, avoiding a single pooled z-score, separating fidelity from cluster usefulness, and checking what the objective rewards. Further broad ablation before implementing would not resolve the representation problem.

Status: IMPLEMENTED DEVELOPMENT PROTOTYPE. Verified on 2026-09-27: 52 tests passed; the one-case, three-step smoke run completed; all 10 saved native models replayed successfully (46 prediction/embedding/metric checks). All 44 source hashes recorded by the preceding full panel-replication run remain unchanged. [Verification record](kernel-verification-2026-09-27.json). No full pilot results, GroupFS reproduction, independent-cohort validation, or SOTA claim yet.

The smoke run is an engineering check, not positive performance evidence: on its tiny held-out sample, learned mixing underperformed identity on the same selected support. Keep the prespecified paired comparisons; do not present the smoke as proof the proposed transformation helps.

## What is borrowed, and what is different

GroupFS jointly learns feature-group memberships and gates and rebuilds a sample graph from gated original features. Its Q matrix acts on feature memberships, not samples. Its sample objective rewards diffusion smoothness. Our prototype instead learns a sparse **sample** projection and optimizes spectral separation. See the [mechanism audit](groupfs-mechanism-audit-2026-09-25.md) for the distinction and source/code checks; [GroupFS paper](https://arxiv.org/html/2511.09166v1).

This is a deliberately small extension, not an attempted reimplementation of every GroupFS component. Group discovery, stochastic gates and the GroupFS diffusion loss are not implemented in this branch. No neural framework is needed for this first test.

Kernel variable selection and spectral projection learning have direct prior art: [Sparse kernel k-means](https://pmc.ncbi.nlm.nih.gov/articles/PMC11727190/) and [Minimum Spectral Connectivity Projection Pursuit](https://arxiv.org/abs/1509.01546). Adding a kernel or low-dimensional projection is not itself a novelty claim. The proposed research contribution to develop and test is a method that produces compact original-feature panels, retains their nonlinear assignment mechanism, and quantifies when a readable rule is faithful and when a panel is independently recoverable.

## Executable model

Discovery-only imputation/scaling maps original measurements to Z. Optimize A, with at most b nonzero rows and Frobenius norm one, then form U=ZA. The row support is the actual measurement panel. Signed combinations allow features to act jointly. A diagonal nonnegative metric is the paired no-mixing variant. The rank is an upper bound; no exact orthogonality or automatic rank determination is claimed.

On the projected discovery landmarks, construct either a locally scaled RBF affinity or a global RBF affinity. Local scales use the kth positive-distance neighbor; exact duplicates are omitted from neighbor counting. This is a dense affinity graph, not a sparse kNN graph or a claim of a Mercer kernel. Unit self-affinities plus a small floor are retained. Local-scale derivatives are included; there is no stop-gradient through bandwidths.

Two alternative spectral losses are compared, with the same mild degree-imbalance penalty:

- cut: lambda2 of the normalized Laplacian;
- gap ratio: lambda2/(lambda3+epsilon).

The latter asks for a relatively distinct binary split rather than several comparable fragments. It remains an unvalidated fitness surrogate. Neither loss is a likelihood, a test for clusters, or a universal solution to nonconvex clustering. A minimum child-size check rules out tiny landmark islands but does not establish cluster existence.

Optimization uses projected gradient steps with a hard support budget, local backtracking, multiple starts and discovery-only checkpoint selection. It does not enumerate feature combinations. The first start uses discovery PCA loadings; the paired diagonal version starts with the same support/row energies. Subsequent starts share their support and row energies across the mixing ablation. Log initial and final support and optimizer progress; local search can still get trapped or overfit noise.

Save the original feature support, scaler, A, landmark projections, affinity scales/degrees, graph eigenvectors and two spectral centers. New points use a frozen eigenfunction extension (Nyström-style) and nearest spectral center, without refitting their batch. A depth-3 tree in original measurement units is a separate approximation, with held-out disagreement reported. A small measurement panel does not automatically yield a simple decision boundary.

## Limited ablations built into the fix

Five autonomous fits per case: diagonal/cut/local, diagonal/gap/local, projection/cut/local, projection/gap/local, projection/gap/global. They have the same feature budget, landmark count, seeds and optimization limits. No variant is selected using labels or validation/test ARI. All results are reported.

For each projection fit, freeze its selected support and compare:

1. the retained learned projection and kernel assignment;
2. an unweighted identity representation with the same kernel family, landmarks and selected features;
3. ordinary centroid clustering on the same selected features.

This separates a representation/readout change from a change in feature selection. It is an ablation of learned mixing and weighting jointly; it does not isolate off-diagonal mixing from weights on identical support. The independent diagonal learner supplies a complementary end-to-end comparison, not a perfectly matched single-parameter treatment.

All-feature local spectral and ordinary k-means are simple controls. Supplied-planted-panel spectral assignment is an oracle geometry diagnostic. Shell radius and covariance-pair generator rules are additional explicitly non-autonomous references. None enters selection.

## First run and reporting boundaries

The pilot is 7 cases x 3 fresh development seeds (26,27,28), with n=800, 50/25/25 discovery/validation/test rows, budget16, rank2, at most200 discovery landmarks, 60 gradient steps and3 restarts. Validation is diagnostic in this pass: there is no panel-compression or teacher-fidelity certification decision. Test annotations appear only after fits freeze.

| Case | Purpose | What it does not show |
|---|---|---|
| mean shift, p200/s12 | Revisit the observed distributed-signal failure with joint mixing | Nonconvex geometry |
| grouped moons, p50/s10 | Correlated feature blocks plus curved sample geometry | Necessity of ten features; this is a redundant rank-two source |
| shells, p50/s5, radii1 and2 | Preserve the existing hard geometry/discovery problem | Universal success for shells or proof every useful panel needs five features |
| covariance regimes, p50/s8 | Joint information spread over four feature pairs | Separated density components: the populations overlap |
| independent Gaussian | No-population negative control | A formal false-positive rate without an acceptance rule |
| correlated Gaussian | Coherent features and stable splits can mislead | Domain relevance from correlation alone |
| one spherical population | Curved structure without two populations | Cluster existence from a nonlinear representation alone |

The covariance example has standard-normal one-dimensional marginals in both populations. At most three coordinates contain one informative pair, whereas eight coordinates contain four. Its known population likelihood rule provides a genuine larger-panel information advantage. This tests dependence recovery separately from density connectivity.

The optional geometry suite adds padded moons/rings/spirals, distributed noisy moons, and s12 shells. These are development diagnostics. The more tightly spaced shell construction and population lower bounds in the [benchmark scope report](kernel-benchmark-scope-2026-09-25.md) are proposed follow-ups, not the generator used by this executable pilot.

Every run creates a new timestamped directory under results/research_kernel_panels. It saves source hashes, package versions, configuration, per-case models and predictions, original data/splits, native embeddings, approximate tree rules and a summary. Failure/interruption remains explicit in the manifest. Old artifacts are not overwritten.

PowerShell, from this repository:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_kernel_panels.py --suite pilot
```

Optional later checks, only after reading the pilot:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_kernel_panels.py --suite geometry --budgets 8 16
.\.venv-research\Scripts\python.exe .\scripts\run_research_kernel_panels.py --suite real
```

These are local CPU runs using existing dependencies. Runtime depends on accepted gradient steps and line-search stalls; no GPU is assumed. Landmark count, total n and projection rank should be varied separately if sampling or projection loss is the apparent obstacle.

## How the pilot changes our next decision

- If the supplied-panel model fails, do not blame feature search: fix the geometric model or identify a sample-density limit. Rank-two linear compression may discard shell information; the RBF does not reconstruct discarded directions.
- If supplied-panel geometry works but autonomous supports fail, focus on discovery/initialization/fitness. Compare initial/final supports and native training versus held-out behavior before introducing EA or RL.
- If the learned native model beats same-panel identity/centroid fits, preserve the representation. Do not turn it back into an unweighted feature mask.
- If native assignment works but the tree has poor fidelity, retain its panel as measurement interpretation and report the rule as complex. Consider radial/energy or prototype rules appropriate to the supported geometry.
- If nulls receive attractive scores or stable splits, the existing no-cluster-acceptance limitation remains. Do not call the objective a validity test.

After the development choice is frozen, compare author implementations of GroupFS, DUFS and sparse kernel k-means, plus appropriate spectral/density clustering controls, under matched original-feature budgets, unsupervised tuning rules and runtime accounting. Evaluate a fresh, prespecified structural matrix and independent domain data where available. Competitive ARI is necessary context; possible improvement in panel size, fidelity, reproducibility or measured domain usefulness is a separate claim. No single favorable benchmark or oracle result establishes superiority.
