# Pilot geometry audit: learning useful panels and keeping the right partition

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: saved-result inspection plus bounded diagnostic calculations
- Origin Date: 2026-09-15
- Verification Status: saved results inspected; listed small diagnostics executed
- Version Label: pilot_geometry_audit_v1
- Scope: three synthetic seeds; descriptive findings, not a general performance or novelty claim

## Main conclusions

1. The learned proposal methods outperform these discrete mask-search baselines
   on the pilot's mean-shift case. Both propose the exact planted five-feature
   panel in every seed. The final selector then prefers six to eight features.
   Discovery improved; compact-panel selection remains unsolved.
2. The shells failure cannot be attributed only to search. Supplying the exact
   five-feature panel to the current raw-space spectral splitter still gives
   ARI approximately zero. Its graph connects outer-shell observations to the
   inner shell and prefers a directional division.
3. A simple interpretable representation changes that fixed-panel result:
   square discovery-centered/scaled coordinates. With the true panel supplied,
   spectral clustering and transfer both reach ARI 1.0 for all three seeds.
   This is an **oracle-panel diagnostic**, not autonomous panel discovery.
4. The same representation does not automatically fix feature search. A small
   squared-feature sparse-k-means proposal check still failed to find the full
   panel. Representation, proposal search, partition retention, and panel
   reduction need separate controls.

## What the mean-shift runs establish

Source runs: the three `search_mean_shift_p50_s5_seed*` directories under
`results/research_diagnostics`. Each has 480 observations, 50 features, five
planted mean-shift features, and fixed discovery/validation/test splits.

| Method | Mean test transfer ARI | Three-seed range | Mean selected size | Mean scored candidates | Mean search seconds |
|---|---:|---:|---:|---:|---:|
| Random masks | 0.152 | 0.015–0.418 | 6.67 | 100 | 2.89 |
| Forward | 0.162 | -0.009–0.355 | 8.00 | 100 | 2.90 |
| Evolutionary | 0.268 | 0.181–0.396 | 6.00 | 100 | 2.89 |
| Soft graph | 0.712 | 0.637–0.749 | 7.67 | 35.0 | 1.29 |
| Sparse k-means | 0.668 | 0.534–0.778 | 7.33 | 43.3 | 1.32 |

These elapsed times include proposal work and candidate scoring, but exclude
shared reference setup and subsequent reporting/compression. They are measured
pilot timings, not matched-compute estimates or scaling guarantees. The EA is
the new bounded add/drop/swap baseline, not the original ATOMIC NSLC engine.

Both learned methods score the exact planted panel in all three runs. Their
chosen panels also contain all five signal features, plus nuisance features:

| Seed | Exact five-feature objective | Soft-graph selected size / objective | Sparse-k-means selected size / objective |
|---|---:|---:|---:|
| 0 | 2.160 | 8 / 2.526 | 6 / 2.612 |
| 1 | 1.877 | 7 / 2.298 | 8 / 2.462 |
| 2 | 2.374 | 8 / 2.584 | 8 / 2.616 |

The same fixed panel scorer generated each row. The larger panels therefore
win because of its actual ranking, not because search failed to expose the
compact alternative. Backward rule compression did not remove these extra
features from the learned methods' selected panels. Preserving an original
noisy kNN rule at ARI 0.95 is a different objective from finding a small panel
with similarly useful clustering.

The saved soft-graph optimizer traces are also informative. At the final
0.7-bandwidth restart, all five highest-ranked weights correspond to planted
features in every mean-shift seed, while the effective feature count has
fallen to approximately 1.035, 1.034, and 1.049. Thus a useful ranking survives
even though the final continuous metric has nearly concentrated on one
feature. The other bandwidth restarts are much less reliable. Prefixes across
the optimization path are contributing useful candidates; these results do
not show that the final continuous geometry has learned five necessary weights.

### Five planted features are not automatically five necessary features

Each mean-shift coordinate carries some population information on its own.
For the generator's equal-prior, spherical Gaussian populations, retaining
`k` of the five signal features gives mean separation
`3 sqrt(k/5)` and Bayes classification error `Phi(-1.5 sqrt(k/5))`.
Using four rather than five therefore changes idealized error from about
6.7% to 9.0%; it does not make the problem unidentifiable.

Consequently, distinguish:

- **Support recovery:** did the proposal recover the generator's five indices?
- **Compact useful explanation:** what is the smallest panel meeting a stated,
  independently assessed quality tolerance?
- **Necessary high-order signal:** do all smaller panels fail that tolerance,
  after allowing an appropriate partitioner?

The pilot establishes the first for these learned proposal pools. It has not
established the second or third. Merely returning eight coordinates establishes
none of them.

## Why raw-space shells fail

The generator places observations near radii 1 and 2 in a five-dimensional
signal subspace. Each nuisance coordinate has the same univariate marginal as
a signal coordinate, generated independently. This removes a univariate
distribution shortcut. It does not assert that all proper signal subsets carry
zero information.

In the supplied true panel, the saved raw-space spectral discovery ARIs are
`-0.00124`, `0.00121`, and `0.00424`. The held-out transfer ARIs are likewise
near zero. Therefore even a perfect feature search would fail with that
unchanged partitioning pipeline.

I reconstructed each saved dataset and split using its manifest, then measured
the directed ten-nearest-neighbor graph in the standardized true panel:

| Seed | Inner-shell neighbors from the other shell | Outer-shell neighbors from the other shell |
|---|---:|---:|
| 0 | 0.0% | 47.2% |
| 1 | 0.09% | 48.6% |
| 2 | 0.0% | 51.2% |

At this sample size, the outer surface is sparsely covered: observations on
that surface frequently have nearby inner-shell observations. The binary kNN
graph is not representing the desired two density components faithfully.
Symmetrizing the graph retains these cross-shell connections.

Directly scoring the known radial partition diagnoses the mismatch:

| Seed | Raw graphcut for radial truth | Raw graphcut for returned spectral split | Density for radial truth | Density for spectral split |
|---|---:|---:|---:|---:|
| 0 | -0.533 | -0.259 | -0.294 | -0.526 |
| 1 | -0.557 | -0.279 | -0.337 | -0.584 |
| 2 | -0.542 | -0.286 | -0.338 | -0.559 |

Larger is better for these scores. Graphcut favors the wrong partition by a
large margin. The density surrogate prefers the radial partition relative to
this competitor, but remains negative because finite-sample within-surface
connectivity is costly. A mixture of these terms is not guaranteed to recover
the radial partition, and the current panel scorer never offers that partition
as an alternative to begin with.

## Executed representation diagnostics

These are new small calculations on the same saved discovery/test rows, not
new independent confirmation data. No previous result files were changed.

Let `Z` use the saved discovery-fitted centering and scaling. Two oracle-panel
checks were performed:

1. Fit two-means to `sum(Z_j^2)` over the five supplied signal coordinates and
   predict the test radii with the frozen scalar model.
2. Run the existing spectral splitter on the five supplied coordinates after
   mapping each to `Z_j^2`; transfer labels by the existing seven-neighbor rule
   in that transformed space, and also recluster the test rows independently.

Both checks obtained ARI **1.0 on discovery and test for seeds 0, 1, and 2**.
The squared-coordinate spectral check also obtained test reclustering ARI 1.0.
Each command completed in under three seconds on this machine.

This interpretable transformation folds together sign-related positions around
the estimated center. It changes which observations are neighbors. A displayed
rule can refer to squared deviations or radius, so interpretability need not
mean using only untransformed Euclidean distance.

Crucially, the oracle supplied the panel. Running sparse-k-means proposals on
all 50 squared coordinates, with 20 steps, three restarts, and maximum size
eight, did **not** propose the exact panel in any seed. Best five-coordinate
proposals recovered one, two, and two of the five signal features respectively.
This run used approximately 0.07 seconds of proposal time per seed; it was a
bounded check, not an exhaustive tuning exercise.

There is a reason not to assume that a linear covariance method on squared
coordinates must solve this example. For `X=R U`, with `U` uniform on the
five-dimensional unit sphere and distinct coordinates `i,j`,

```text
Cov(X_i^2, X_j^2) = E[R^4] / (5*7) - E[R^2]^2 / 25.
```

Ignoring the tiny radial jitter, the generator has `E[R^2]=2.5` and
`E[R^4]=8.5`, giving covariance approximately `-0.00714`: radial dependence
almost cancels the negative dependence caused by the spherical constraint.
Strong useful joint geometry can coexist with weak pairwise covariance.
This calculation explains a potential weakness of covariance-only proposals;
it is not a computational impossibility result.

## The next experiment should retain representations and partitions

The current proposal interface returns masks. It discards the optimized
partition and metric, then asks raw-space spectral clustering to invent a new
partition for each mask. That is a legitimate way to benchmark mask proposals,
but it cannot show whether a useful learned partition was lost during rounding.

A precise next experiment is a small factorial ablation on newly generated
seeds, keeping existing pilot results exploratory:

1. **Representations:** raw standardized coordinates and squared standardized
   coordinates. Fit all transformation parameters on discovery data; retain a
   mapping from transformed coordinates back to original feature names. Report
   both channels, since squaring can destroy a sign-based mean shift.
2. **Candidate:** store `(original panel, transformation, weights, discovery
   partition, frozen assignment rule)` instead of only a mask. Count a feature
   once if multiple transformations of it are used.
3. **Partition-retention comparison:** evaluate the native learned partition,
   a refit using the same representation/weights, and the current hard-mask
   raw-space spectral partition. Compare ARI/fidelity between them on shared
   evaluation points and external labels only after selection.
4. **Compression:** compare preservation of the original assignment rule with
   deleting a feature and refitting a partition in the retained representation.
   A smaller useful cluster solution need not reproduce every nuisance-dependent
   decision made by the original kNN rule. Choose a tolerance before examining
   confirmation results.
5. **Selection:** preserve separation, replication, and complexity as separate
   reported quantities. If comparing score scales across representations, fix
   reference calibration independently for each and check whether that choice
   changes rankings. Do not silently compare raw spectral loss with transformed
   graphcut or treat either as a cluster-existence test.

First include the fixed oracle panel to verify that each representation can
express the intended split. Then evaluate autonomous discovery with the oracle
records excluded from candidate generation and selection. Failure at the first
stage identifies a representation/partition problem; failure only at the second
identifies search or panel ranking.

For sparse k-means, refit labels once using final weights before retaining a
candidate: an alternating iteration's label update precedes its weight update.
For soft graph, retain the actual weighted affinity and an explicit split of
its spectral vector; the relaxation's eigenvalue alone is not an assignment
rule. Apply minimum-size conditions without using population labels.

This experiment is justified by the observed failure modes. It does not yet
claim a new algorithm, guaranteed recovery beyond three features, or a complete
statistical stopping rule.

## Provenance and reproduction

Saved-run evidence comes from each relevant directory's `manifest.json`,
`data_protocol.json`, `summary.json`, per-method `*_candidates.jsonl`, and
`*_proposal_trace.json`. The extra checks used `prepare()` with each manifest's
configuration to recover the exact data and row split, `score_partition()` on
the planted labels as an explicitly marked diagnostic, and `score_panel()` on
the fixed transformed oracle panel. Labels did not enter proposal routines.

The relevant implementation files are `atomic_research/datasets.py`,
`experiment.py`, `scoring.py`, `soft_graph.py`, and `sparse_kmeans.py`. All new
numbers above are either directly aggregated from saved runs or explicitly
identified as bounded post-pilot diagnostic calculations. None should be
presented as independent confirmatory evidence.
