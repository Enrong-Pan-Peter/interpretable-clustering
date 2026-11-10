# Compression audit of the 16 September obstacle suite

## Material Passport

- Origin: independent compression-stage review in the ATOMIC research investigation
- Origin Date: 2026-09-17
- Mode: statistical interpretation of saved results
- Verification Status: ANALYZED; descriptive calculations repeated from saved JSON, no clustering refits
- Version Label: obstacle_compression_review_v1
- Inputs: `results/research_obstacle_checks/20260916T145427_229536Z/compression_{mean_shift,metabric,levine}_seed{0,1,2}/{summary.json,data_protocol.json,soft_graph_deletions.json,sparse_kmeans_deletions.json}`
- Scope: nine dataset/seed cases, two proposal arms, four compression policies, and individual deletion diagnostics
- Limitation: development reanalysis of previously inspected pilot splits; the original test rows are not a fresh final confirmation set

## Main finding

Compression is a real unresolved bottleneck, but it is not the only bottleneck. The original ARI-fidelity rule makes no deletions in any of the six mean-shift panels, although all six contain nuisance features. Changing to 5% point disagreement makes deletions in all six, but five of the six final reductions disagree with the teacher on more than 5% of test observations. Requiring the threshold within each validation fold helps, but does not solve generalization or preserve every planted feature.

The k-means arm must be interpreted as two interventions: replacing the original spectral-partition/kNN assignment model, then deleting features under a k-means model. A gain over the original teacher can arise entirely from the first intervention. These results do not establish that k-means compression improves the clustering, and preserving a weak teacher does not establish a useful panel.

## What was actually measured

Each case has 240 discovery, 120 validation, and 120 test observations. The reference teacher is the original distance-weighted 7-nearest-neighbor classifier trained on the selected panel and the discovery partition. Candidate models are fitted on discovery only. Validation chooses a greedy deletion path; test predictions are evaluated afterward.

The four policies are:

1. **ARI:** keep a deletion if validation ARI against the original teacher is at least .95.
2. **Disagreement:** keep a deletion if at most 5% of validation assignments differ from the original teacher.
3. **Foldwise:** require at most 5% disagreement in every one of three fixed validation folds. This is a conservative sensitivity check, not a confidence bound. Each fold has 40 observations, allowing at most two changed assignments.
4. **Refit k-means:** independently refit two-means on the candidate reduced panel, orient labels using discovery teacher labels, and require at most 5% disagreement with the original teacher on validation. This checks a different model family; it does not approximate arbitrary nonlinear clustering.

ARI .95 and point disagreement .05 are different requirements. For these roughly balanced binary partitions, one changed validation assignment often gives ARI about .967, whereas six changed assignments often give ARI about .808. Their numerical thresholds cannot be substituted for one another.

There are 18 method-panel instances, but only 14 have more than one original feature. Four Levine instances are already singletons. The two proposal methods return the same teacher in each Levine seed, so the duplicated rows are not independent successes. Real-data cases also reuse the earlier development populations. No confidence intervals or significance claims are attached to the following frequencies.

## Accepted reductions and failures on test rows

| Policy | Final panels reduced / 14 eligible | Features removed over all instances | Reduced final panels failing their test criterion |
|---|---:|---:|---:|
| ARI | 5 / 14 | 10 | 3 / 5 |
| Disagreement | 14 / 14 | 45 | 9 / 14 |
| Foldwise | 13 / 14 | 34 | 6 / 13 |
| Refit k-means | 12 / 14 | 41 | 9 / 12 |

For ARI, test failure means ARI below .95. For the other policies, it means aggregate test disagreement above .05. We do not claim the foldwise policy passed a simultaneous test-fold condition. Unchanged frozen-teacher panels have zero disagreement by construction and should not inflate a success rate for compression.

All 72 final outputs are below. A cell is **original size → final size; validation changes / test changes**, with both change counts out of 120. An asterisk means failure of the relevant test criterion. The two k-means cells marked `no pass` made no deletion and their same-panel replacement also failed the validation fidelity threshold; they are not accepted fidelity-preserving outputs.

### Mean-shift control

| Seed / proposal arm | ARI | Disagreement | Foldwise | Refit k-means |
|---|---|---|---|---|
| 0 soft_graph | 8 → 8; 0/0 | 8 → 4; 6/12 * | 8 → 5; 5/5 | 8 → 5; 5/6 |
| 0 sparse_kmeans | 6 → 6; 0/0 | 6 → 3; 6/9 * | 6 → 4; 2/4 | 6 → 6; 10/5; no pass |
| 1 soft_graph | 7 → 7; 0/0 | 7 → 5; 3/2 | 7 → 5; 3/2 | 7 → 4; 5/11 * |
| 1 sparse_kmeans | 8 → 8; 0/0 | 8 → 5; 5/12 * | 8 → 6; 4/11 * | 8 → 4; 6/10 * |
| 2 soft_graph | 8 → 8; 0/0 | 8 → 5; 4/11 * | 8 → 6; 5/5 | 8 → 5; 6/8 * |
| 2 sparse_kmeans | 8 → 8; 0/0 | 8 → 4; 3/13 * | 8 → 6; 4/12 * | 8 → 6; 5/12 * |

### METABRIC, LumA versus LumB

| Seed / proposal arm | ARI | Disagreement | Foldwise | Refit k-means |
|---|---|---|---|---|
| 0 soft_graph | 7 → 5; 1/6 * | 7 → 3; 3/5 | 7 → 3; 3/5 | 7 → 2; 4/12 * |
| 0 sparse_kmeans | 5 → 4; 1/5 * | 5 → 2; 5/22 * | 5 → 3; 2/11 * | 5 → 2; 5/18 * |
| 1 soft_graph | 8 → 8; 0/0 | 8 → 7; 5/5 | 8 → 8; 0/0 | 8 → 8; 22/18 *; no pass |
| 1 sparse_kmeans | 5 → 5; 0/0 | 5 → 2; 4/9 * | 5 → 2; 4/9 * | 5 → 2; 5/10 * |
| 2 soft_graph | 5 → 5; 0/0 | 5 → 1; 6/14 * | 5 → 4; 3/7 * | 5 → 2; 5/7 * |
| 2 sparse_kmeans | 8 → 5; 1/6 * | 8 → 3; 4/9 * | 8 → 3; 4/9 * | 8 → 2; 5/8 * |

Even the ARI policy's three accepted METABRIC reductions fail the same ARI requirement on test rows: test ARIs are .808, .839, and .808. These change only six, five, and six test assignments, respectively. Describing all three as failing 5% point agreement would therefore also be incorrect.

### Levine, CD4T versus CD8T

| Seed / proposal arm | ARI | Disagreement | Foldwise | Refit k-means |
|---|---|---|---|---|
| 0 soft_graph | 4 → 2; 1/0 | 4 → 1; 3/0 | 4 → 1; 3/0 | 4 → 1; 2/1 |
| 0 sparse_kmeans | 4 → 2; 1/0 | 4 → 1; 3/0 | 4 → 1; 2/1 |
| 1 soft_graph | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 1/3 |
| 1 sparse_kmeans | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 1/3 |
| 2 soft_graph | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 1/2 |
| 2 sparse_kmeans | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 0/0 | 1 → 1; 1/2 |

Both seed-0 teachers use CD4, CD8, CXCR4, and CD47. ARI compression retains CD8 and CXCR4; the other policies retain CD8. The other seeds already use CD8 alone. This is a successful simple redundancy check in a restricted population contrast, not evidence for difficult higher-dimensional compression.

## What the individual feature deletions reveal

All six original mean-shift panels contain all five planted features, plus 15 nuisance-feature occurrences across those panels. Original-panel one-feature deletion diagnostics contain 30 planted deletions and 15 nuisance deletions per model family:

| Model family / removed type | Candidates | Pass 5% validation | Pass both validation and test |
|---|---:|---:|---:|
| Frozen kNN / planted | 30 | 6 | 1 |
| Frozen kNN / nuisance | 15 | 14 | 12 |
| Refit k-means / planted | 30 | 7 | 1 |
| Refit k-means / nuisance | 15 | 11 | 5 |

This is useful separation: the original frozen-kNN deletion test usually permits nuisance deletion and usually rejects planted deletion. But its false passes accumulate when the same small validation sample guides several choices. The table is descriptive; overlapping candidates and reused observations prevent treating these counts as independent Bernoulli trials.

The final greedy paths remove the following feature occurrences in mean-shift:

| Policy | Planted removed | Nuisance removed | Final panels equal planted support / 6 |
|---|---:|---:|---:|
| ARI | 0 | 0 | 0 |
| Disagreement | 6 | 13 | 1 |
| Foldwise | 3 | 10 | 2 |
| Refit k-means | 3 | 12 | 2 |

Two traces show why a final panel alone is insufficient:

- Mean-shift, graph seed 0: disagreement compression deletes nuisance features 4, 15, and 39, then planted feature 8. The successive validation/test change counts are 2/6, 4/7, 5/5, and 6/12. The foldwise policy stops before the planted deletion, retaining exactly the five planted features. Test fidelity is not monotone along this path.
- Mean-shift, sparse-k-means seed 0: the disagreement policy deletes nuisance 38, then planted 3, then planted 21, giving validation/test changes 2/3, 2/4, and 6/9. Foldwise stops after deleting planted 3: it passes test fidelity with four changes but external ARI falls from .692 to .584. Passing a teacher-fidelity tolerance does not imply preserving generating support or external performance.

The planted set is the known generating support, not a proven unique minimal predictive panel under a nonzero error tolerance. A smaller subset can still carry signal. Losing a planted variable is a failure of exact support recovery, but not automatically failure of every useful-panel objective.

For METABRIC, ARI/disagreement/foldwise/k-means policies delete respectively 5/13/12/15 PAM50-reference occurrences and 1/7/3/5 other occurrences. PAM50 membership is contextual, not a deletion correctness label. These data cannot establish that a removed PAM50 gene was necessary, or that a retained non-PAM50 gene is useful. Likewise, deleting CD4 while retaining CD8 can work in the restricted Levine contrast. Functional plausibility must remain separate from independent predictive or replication evidence.

## Separate model replacement from deletion

External test ARIs for the mean-shift k-means arm are:

| Seed / proposal arm | Original teacher | K-means, original panel | K-means, selected panel |
|---|---:|---:|---:|
| 0 soft_graph | .749012 | .778394 | .808377 |
| 0 sparse_kmeans | .691813 | .778408 | .778408 |
| 1 soft_graph | .749012 | .808392 | .720156 |
| 1 sparse_kmeans | .778429 | .870020 | .720156 |
| 2 soft_graph | .636972 | .808394 | .808394 |
| 2 sparse_kmeans | .533908 | .778422 | .584310 |

For graph seed 2, the apparent increase from .637 to .808 comes entirely from same-panel model replacement; deletion adds no external ARI gain. For sparse-k-means seed 2, reporting only the teacher-to-final increase from .534 to .584 hides the deletion-associated drop from .778 to .584. For sparse-k-means seed 0, no feature was deleted and the replacement disagrees on 10/120 validation observations, so its improvement is not evidence of accepted faithful compression.

The issue is also visible on real data. METABRIC graph seed 1 has unchanged size 8 and validation disagreement 22/120 under the replacement model; its external ARI remains near zero. In Levine seed 1 the unchanged CD8 panel goes from teacher external ARI .966666 to k-means .933894, and seed 2 goes from .933889 to .870010. A returned valid fitted model is not necessarily an accepted fidelity-preserving replacement.

## The next discriminating test

The next experiment should separate native model reproducibility from compression, and replace adaptive validation-guided deletion with a fixed training-only prefix family as an experimental arm. This does not require another search optimizer yet.

Use two disjoint discovery samples to fit each learner independently, including preprocessing, feature ranking, panel masks, full model, and prefix models. Freeze every prefix predictor and its orientation relative to its own full model before reading validation. Compare an empirical 5% selector with a simultaneous one-sided binomial upper-bound selector. Choose the smallest eligible prefix, then evaluate the frozen choices on untouched test rows. Report full-to-reduced fidelity separately from agreement between the two independently discovered models. External labels and reference membership enter only after selection.

For a prespecified family of M frozen candidates and k disagreements among n iid validation observations, use the one-sided Clopper–Pearson bound

`U(k,n,alpha/M) = BetaInverseSurvival(alpha/M; k+1, n-k)` for `k<n`, and `U=1` for `k=n`.

When `k=0`, `U = 1 - (alpha/M)^(1/n)`. Select a prefix only if `U <= .05`. At n=200, M=32, and alpha=.05, upper bounds for 0, 1, and 2 errors are .031791, .042852, and .052320. Thus zero or one validation disagreement can certify this threshold; two cannot. An empirical .05 rule would allow ten errors in 200 observations. The difference in operating behavior must be reported, not hidden.

Conditional on frozen training data and iid independent validation rows, Bonferroni gives simultaneous upper coverage across that prespecified family without requiring candidates to be independent. Include invalid and unselected candidates in M. Two calls sharing validation must count both learners' full candidate family. Label orientation learned using validation is permissible for a separate replication diagnostic, but it must not alter the fidelity classifiers unless both orientations were included in the counted frozen family.

This guarantee concerns disagreement with the learner's own full model. It neither proves clusters exist nor guarantees fidelity to biological truth. It applies within the counted run/family, not automatically across all future experiments. Real-data donor dependence, prior feature-universe selection, and repeated use of development observations limit population claims. The synthetic independent-observation case is the cleanest initial check.

The decisive outcomes are: does native rediscovery recur between independent discovery samples; does bounded prefix selection reduce test fidelity failures compared with empirical selection; and how much panel reduction remains possible? Record same-family full-to-reduced external ARI deltas and planted-feature retention as post-selection diagnostics. A full panel always agreeing with itself is a fallback, not evidence that compression succeeded. Failure to reproduce the full model points upstream; stable full models that admit no compact faithful prefix point to either feature ranking or the chosen compression target.

The supporting bound/selector implementation is isolated in `atomic_research/fidelity_bounds.py`. Its 53 tests pass, including enumerated binomial coverage at boundary probabilities, analytic zero-error values, monotonicity, deterministic selection, no test-data interface, and malformed-input rejection. This verifies the numerical helper, not the entire proposed experiment or its sampling assumptions.

## Interpretation checks

The ARS statistical fallacy checklist was reviewed, 11/11 categories. Dataset-specific results are shown rather than only pooled averages; duplicated method outputs and overlapping cohorts are not independent replications (aggregation/ecological concerns). Population filtering limits generalization (selection/Berkson concerns); no causal adjustment or causal direction claim is made (collider, causation, reverse causality). Accuracy does not establish population prevalence or usefulness (base-rate concern). Same-panel baselines separate model replacement from deletion, and poor original teachers are not silently excluded (regression-to-mean and survivorship concerns). All policies and unchanged outputs are reported, and this is explicitly a development reanalysis (look-elsewhere and forking-path concerns). No p-values, significance declarations, causal conclusions, or novel-method claims are warranted by this audit.
