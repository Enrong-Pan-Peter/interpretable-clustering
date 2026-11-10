# Kernel pilot: the objective often improves while the useful geometry deteriorates

Material passport: independent mathematical/results audit, 2026-09-27, under the ARS experiment-planning workflow. Source run: `results/research_kernel_panels/20260927T043314_711791Z`. This document reads saved results and performs short, posthoc reconstructions of the initial projection and frozen-map loss on other rows. It does not run a new optimizer, change a result, select a deployable winner, certify clusters, or establish novelty. Both annotations and the previously held-out test results have now informed development; a future confirmation experiment needs fresh cases.

The run is complete: 21 planned cases, 21 reports, seeds 26–28. All 46 recorded source hashes match the current files at this audit. Relevant SHA-256 values are:

| File | SHA-256 |
|---|---|
| `atomic_research/kernel_panels.py` | `5816e83490eabf1ff62a2d7e786ea534a49d3e9a7fa994bc1b8fc01876750149` |
| `atomic_research/kernel_benchmark.py` | `45e060d5ad172ce34eb616c692ae366d8d34520d7b189529e3eb8096fb801bc6` |
| `scripts/run_research_kernel_panels.py` | `f152a7c743d91e7694f56440512d897491ebc0b5290b7258d045ade8c5f20c20` |

The experiment used 400 discovery rows, including 200 optimization landmarks, 200 validation rows and 200 test rows. The support cap was 16, requested projection rank 2, 60 optimization steps, three restarts, and seven neighbors for local bandwidths. Current source uses no labels or held-out rows to choose a checkpoint; it chooses the lowest landmark loss satisfying its size/noncollapse gates. These gates do not test whether clusters exist. This audit checks source consistency, not every saved prediction replay.

## The starting representation was already useful

I reconstructed the first restart from the saved discovery rows, discovery-fitted scaler and exact landmark selection: centered SVD, keep the 16 rows with greatest energy in the first two right singular vectors, then normalize the matrix. Every reconstructed support and initial gap loss matched the saved trace; maximum allowed discrepancy was `1e-10`. Only the frozen native spectral assignment was evaluated. No optimization was repeated.

The table identifies runs by dataset and seed; their full directory names are `mean_shift_p200_s12_b16_seed{seed}` and `grouped_moons_p50_s10_b16_seed{seed}`. “Initial” is that exact PCA start; “final” is the saved winner across all three restarts, so these are not necessarily endpoints of the same trajectory. Loss is the gap-ratio objective plus the degree penalty. ARI is reported only after fitting.

| Case | Kernel | Initial loss → final loss | Initial test ARI → final test ARI | Initial signal recall → final |
|---|---|---:|---:|---:|
| Mean shift 26 | Local | .34520 → .11748 | .53039 → −.00095 | .750 → .000 |
| Mean shift 27 | Local | .34849 → .11350 | .48746 → .41956 | .750 → .750 |
| Mean shift 28 | Local | .27898 → .05059 | .67076 → .57548 | .833 → .750 |
| Grouped moons 26 | Local | .33336 → .00102 | .62226 → .62226 | 1.000 → 1.000 |
| Grouped moons 27 | Local | .30092 → .04858 | .63820 → .60647 | 1.000 → 1.000 |
| Grouped moons 28 | Local | .29721 → .03758 | .44619 → .27735 | 1.000 → .200 |
| Mean shift 26 | Global | .51196 → .28442 | .57526 → .27631 | .750 → .667 |
| Mean shift 27 | Global | .60415 → .28896 | .54535 → .57550 | .750 → .833 |
| Mean shift 28 | Global | .46358 → .20682 | .59085 → .70412 | .833 → .917 |
| Grouped moons 26 | Global | .29802 → .07940 | .54533 → .53055 | 1.000 → 1.000 |
| Grouped moons 27 | Global | .24018 → .08526 | .68733 → .62222 | 1.000 → 1.000 |
| Grouped moons 28 | Global | .28826 → .10792 | .44618 → .41965 | 1.000 → 1.000 |

Local training decreases test ARI in five of six cases and ties once, despite improving loss in all six. Global training decreases ARI in four of six cases and improves it twice. These six cases are a small, deliberately inspected development sample; the counts are diagnostic, not a significance claim.

Mean-shift seed 26 is a particularly clear selection failure. Local-gap chooses a random start containing no signal features. Its final loss `.117475` beats the PCA-start trajectory's final loss `.151569`. All three trajectories make zero support changes. The algorithm had a useful panel and still preferred a nuisance split under its own objective.

## Separate rows do not fully repair this preference

I recomputed the same gap loss on each 200-row validation set under the frozen discovery scaler and initial/final transformation matrices. The graph was reconstructed only for score evaluation, without using annotations or refitting the map. This is an independent-row geometry diagnostic, not a measure of transfer of the retained cluster assignment, and not a prespecified model selector.

| Case | Local validation loss, initial → final | Global validation loss, initial → final |
|---|---:|---:|
| Mean shift 26 | .32034 → .34082 | .53440 → .61063 |
| Mean shift 27 | .30005 → .29741 | .50843 → .50472 |
| Mean shift 28 | .29846 → .27030 | .54471 → .51013 |
| Grouped moons 26 | .34973 → .25102 | .25773 → .20329 |
| Grouped moons 27 | .31118 → .28212 | .26756 → .19049 |
| Grouped moons 28 | .48768 → .31143 | .28411 → .18555 |

A retrospective chooser using only these two validation losses would keep the initial map only on mean-shift seed 26, for both kernels. It would still choose four ARI-degrading local updates, and three ARI-degrading global updates. Thus an additional holdout protects against one major failure here but does not resolve the score's structural preference.

The independent-Gaussian negative control is more decisive: local validation loss decreases from `.85902/.84091/.78949` to `.32091/.31531/.34726`; global validation loss decreases from `.93544/.94411/.91273` to `.67746/.69068/.62513`. These improvements transfer to entirely separate rows even though the generating distribution contains no latent populations. Lower graph loss is not intrinsically evidence of clustering.

## The nominal rank-two global model becomes a line

All 21 global-gap models have final singular-value ratio `sigma_2 / sigma_1 <= .008609`; 20 of 21 have ratio at most `.000150`. Mean-shift ratios are approximately `.000033/.000061/.000054`; independent-Gaussian null ratios are `.000041/.000002/.000002`. Most matrices remain numerically rank two, so the existing numeric-rank diagnostic correctly reports rank two. Practically, their geometry is almost one-dimensional.

The Frobenius constraint fixes `sigma_1^2 + sigma_2^2 = 1`, not the two singular values individually. This allows the objective to change rank and anisotropy while apparently searching for a two-dimensional feature representation. All 21 diagonal-cut/local models likewise finish with exactly one original feature. Their losses are around `0.0005–0.0008` across signal and negative-control datasets. None fails the current child-size gate.

The local-gap maps do not show the same near-zero second singular value: independent-null ratios are `.446/.437/.507`, and mean-shift ratios `.436/.465/.504`. Local anisotropy, adaptive neighborhoods and finite-sample gap exploitation remain separate issues. Rank preservation can isolate one confound; it cannot be promised to repair these local results.

### A population calculation explains the global null improvement

Consider an independent standard Gaussian input and a fixed projection with squared singular values `t_1,t_2`, where `t_1+t_2=1`. The projected coordinates are independent normals with those variances. Ignore the negligible affinity floor and finite-sample self-loop contribution, and use the implemented global affinity `W(z,z') = exp(-||z-z'||^2/2)`.

The population row-normalized kernel sends coordinate `z_j` to a Gaussian transition with conditional mean `rho_j z_j`, where `rho_j=t_j/(1+t_j)`, and constant conditional variance. This is a reversible Gaussian autoregression. Its nonconstant eigenvalues are products of the coordinate eigenvalues `rho_j, rho_j^2, ...`; the symmetric normalized operator has the same eigenvalues. Consequently:

| Gaussian projection | Largest nonconstant adjacency eigenvalues | Laplacian `lambda_2,lambda_3` | Gap ratio |
|---|---|---|---:|
| Equal rank two: `t_1=t_2=1/2` | `1/3,1/3` | `2/3,2/3` | 1 |
| Rank-one limit: `t_1=1,t_2=0` | `1/2,1/4` | `1/2,3/4` | 2/3 |

There is a population reward of approximately one third for flattening a perfectly unimodal Gaussian to a line. It does not require overfitting, a bug, or a hidden cluster.

The population Jensen degree penalty is

`P(t) = (1/2) sum_j [log((1+t_j)/(1+2*t_j)) + t_j/(1+t_j)]`.

It is approximately `.045651` for equal rank two and `.047267` for the rank-one limit. Multiplication by `.02` changes the total loss by only about `.000032`, far too little to cancel the spectral reward. The implemented `1e-6` denominator term also has negligible effect on this comparison. This is a derivation for a fixed projection and population Gaussian operator; finite-sample optimization, discovery scaling, the positive affinity floor and correlated inputs change exact values. It nevertheless explains why the observed independent-null global validation losses approach roughly two thirds.

## What the other comparisons establish

Mean test ARIs across the three seeds are:

| Variant | Mean shift | Grouped moons | Shells | Covariance pairs |
|---|---:|---:|---:|---:|
| Diagonal cut, local | .14358 | .07578 | −.00398 | −.00240 |
| Diagonal gap, local | .04580 | .53165 | .00433 | .00054 |
| Projection cut, local | .26828 | .27711 | −.00071 | .00264 |
| Projection gap, local | .33136 | .50203 | −.00221 | .00207 |
| Projection gap, global | .51864 | .52414 | .01409 | −.00198 |
| All-feature local affinity | .47842 | .48561 | .00462 | −.00091 |

Diagonal gap performs competitively on grouped moons, so mixing is not established as necessary there. On mean shift the global model's discovered support is more useful than its learned map: replacing only that map by equal-weight identity on the same support gives test ARIs `.50119/.54535/.77327` (mean `.60660`), compared with native `.27631/.57550/.70412` (mean `.51864`). This is a diagnostic comparison, not permission to retrospectively declare identity the chosen method.

Optimization is not purely frozen support: local-gap makes no feature entries in 49/63 restart trajectories, but global-gap makes entries in all 63. The latter still produces nearly rank-one maps. Extending all runs or adding random restarts alone does not address the identified loss preference. Affinity-floor fractions stay below `3.2e-7` in the learned models; their projected variances exceed `.90`. The results are not explained by all-zero projected data or affinity-floor domination.

The correlated-Gaussian negative control has mean local-gap training loss `.021475`, below the mean-shift `.093853` and grouped-moons `.029059` means. This directly forbids interpreting an uncalibrated low loss as a cluster-acceptance score. The experiment has no such acceptance rule and does not estimate a false-split rate.

For shells, even the supplied true panel with the same raw local graph has test ARIs `.03428/.01200/−.00463`, while the supplied generator radius rule gets `1.0` in all three cases. For covariance pairs, supplied-panel local graph ARIs are `.07523/.02069/.01467`, while the supplied interaction rule gets about `.86422`. These are failures of the evaluated representation/assignment as well as discovery, not evidence that the signal is unknowable. The supplied generator rules are oracles, never autonomous results.

## One bounded next fix

Implement a matched sparse projection constrained to `A.T @ A = I/r`. A polar/QR step inside the retained feature support can preserve that support while preventing silent singular-value collapse. Keep explicit rank-one models separate from this fixed-rank comparison. This is a targeted rank-preservation ablation, not a novel algorithm or a cluster-existence test.

Use the same prespecified initial supports and data splits, and report four distinct objects: original frozen sparse-PCA map, its frozen rank-preserved version, optimized rank-preserved map, and saved unconstrained final map. Separating the two frozen maps matters because hard row truncation already changes the PCA column geometry. Report initial/final supports, singular values, independent-row losses, assignment ARI, and negative controls without choosing a retrospective winner. Retain the useful frozen baseline explicitly.

If the constrained optimizer still damages that baseline while improving both training and validation loss, reject this spectral score as the main selection objective for that setting. More optimization would pursue the wrong target more effectively. Shell and covariance-interaction representation work should remain a separate branch; neither outcome is settled by fixing rank on mean-shift/moons.

Sparse sample projection followed by spectral connectivity optimization has direct prior art in [Hofmeyr, Pavlidis and Eckley, Minimum Spectral Connectivity Projection Pursuit](https://arxiv.org/abs/1509.01546). Local bandwidths also come from established work, [Zelnik-Manor and Perona, Self-Tuning Spectral Clustering](https://papers.nips.cc/paper_files/paper/2004/hash/40173ea48d9567f1f393b20c855bb40b-Abstract.html). The proposed constraint test should be described as a controlled diagnostic of this implementation, without a novelty or superiority claim.
