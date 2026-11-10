## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan with targeted implementation checks
- Origin Date: 2026-09-14
- Verification Status: code checks reported below; proposed empirical improvements UNVERIFIED
- Version Label: partition_scoring_v1
- Scope: new `atomic_research/scoring.py`; historical implementation remains unchanged

## The question this implementation isolates

Is the score ranking the **partition actually returned**, and can it distinguish useful panels from plausible-looking nuisance? These are separate questions. Repairing the first is necessary bookkeeping. It does not establish the second, and cannot by itself rescue a search landscape with no useful intermediate signals.

The new interface returns all components without hiding them in one statistic:

- `graphcut` and `density` both evaluate exactly `labels` from the requested splitter.
- `legacy_graphcut` evaluates the spectral partition; `legacy_density` evaluates the historical MST partition.
- `legacy_partition_ari` measures agreement between those two unlabeled partitions. It uses no external classes.
- `valid` means numerical and minimum-size admissibility. It does **not** mean that two scientifically meaningful populations exist.
- `score_partition` evaluates frozen assignment labels on separate rows without fitting a new split. Those labels are algorithm outputs, not reference biological classes.

Preprocessing belongs outside the scorer and must be fitted on discovery data. No API in this module accepts reference class labels. All scores are conditional on the specified original features and the current preprocessing.

## Precisely what the two components mean

For two sets A and B in a panel S, the graph term is

`q_graph(S,A,B) = - cut(A,B) * [1 / vol(A) + 1 / vol(B)]`.

The implementation preserves the previous symmetric binary kNN graph and unit-weight connectivity bridges. This makes the legacy arm directly comparable on ordinary continuous data. It also preserves a limitation: a bridge weight of one does not encode how long a gap was crossed. Adding a connectivity bridge is a modeling choice, not a proof that the resulting score has a universal scale. The number of disconnected components before bridging is retained in the result.

Define `m(i,j) = max(distance(i,j), core_k(i), core_k(j))`, where the core radius uses all panel observations. Let `s` be the smallest m-distance between A and B; let `w` be the larger of the maximum within-A and within-B MST edge weights. Then

`q_density(S,A,B) = (s - w) / max(s,w)`.

The term lies in [-1,1]. It is positive precisely when the observed between-set bottleneck exceeds both observed within-set bottlenecks. It is a **DBCV-style surrogate**, not the full DBCV index. It does not implement DBCV's complete core-distance construction, internal-point restrictions, or weighted cluster aggregation. A worst-child bottleneck can be sensitive to a sparse tail or a single poorly connected observation; matching labels removes partition inconsistency but not this sensitivity.

When the returned partition cuts the largest admissible MST edge and no bigger edge remains in a child, the term reduces to `1 - e2/e1`. In that regime it is a monotone transform of the persistence ratio. Different names do not imply independent evidence. Graph and density terms can also be strongly dependent.

The corrected within-cluster bottleneck uses condensed single linkage, whose final merge height equals the largest complete-graph MST edge. This preserves legitimate zero-distance edges for duplicated or quantized observations. The legacy score deliberately retains the old implementation for comparison. All-identical panels, inadmissibly small children, and non-binary partitions are explicitly invalid. k and core_k are clipped to available neighbors, while the requested minimum child size is retained (at least two).

## What to freeze before comparing search methods

Compute component means and scales once on the **same prespecified reference masks** and discovery rows. Retain those constants for every search arm and every subsequent candidate. Record the reference masks and costs. Candidate-pool standardization changes the objective while search runs: altering one component's standard deviation changes its relative weight in the hybrid, even when none of an existing candidate's component values changed.

This frozen calibration supplies common units for a ranking experiment. It is not evidence that dimensions are scientifically comparable or that a weighted sum is optimal. Report raw components, panel size, selected score, and held-out evidence separately. Test weights as an explicitly declared sensitivity analysis instead of choosing the best weight from external ARI and reporting it as unlabeled discovery.

Compare search coverage and selection using the same scorer, splitter, rows, preprocessing, and unique-evaluation budget. If a search proposes good panels but does not select them, the objective is the bottleneck. If known useful panels rank well but are never proposed, the proposal mechanism is the bottleneck. If neither an oracle panel nor a richer unsupervised baseline separates the target on held-out rows, the chosen geometric target or data representation needs attention.

## Why the current permutation z cannot answer all three questions

Independent column permutations approximate a product-of-marginals null. They remove cross-feature dependence and retain marginal structure.

1. For one feature and any row-order-invariant statistic T, `T(permutation(x)) = T(x)` exactly. Even two widely separated marginal modes give a degenerate permutation null. A floor on the denominator cannot create the missing target information.
2. A bivariate Gaussian with nonzero correlation has one mode, but does not factor into independent marginals. A dependence statistic can reject the permutation null very strongly without supplying a reason to split.
3. Searching many panels and reporting the most extreme calibration on the same rows conditions on selection. A per-panel null ignores that event. Repeating the **entire search** on every null dataset can calibrate the selected statistic under that null, but still tests independence rather than cluster absence.

`column_permutation_calibration` exposes the actual null target and marks selection adjustment false. It uses the finite Monte Carlo count `(1 + number of null scores at least as large) / (B + 1)`. Its descriptive z is absent when the null is degenerate. It requires a deterministic row-order-invariant scalar statistic; numerical splitters with row-order dependence need additional care.

`dependence_permutation_diagnostic` uses the sum of squared Pearson correlations as a cheap illustration. This statistic only detects linear dependence; it is not an omnibus test. The unit tests contrast a strongly correlated **single Gaussian population** with a **gapped singleton**. Their opposite behavior is a target mismatch, not an optimizer failure. These tests establish what a permutation test asks; they do not estimate real-data performance.

## Statistical direction worth investigating

An interpretable target is a reproducible pair of connected high-density regions separated by a valley in the selected panel. Density cluster-tree inference supplies an explicit population object and confidence-set/pruning machinery. Kim et al. construct uncertainty sets for density cluster trees and prune insignificant features. An extension to adaptively learned panels must justify selection, density-estimation error, and recursive conditioning; their fixed-space framework does not automatically supply those guarantees. [Kim et al., Statistical Inference for Cluster Trees, NeurIPS 2016](https://papers.nips.cc/paper_files/paper/2016/hash/a9b7ba70783b617e9998dc4dd82eb3c5-Abstract.html).

A first experiment can measure independent rediscovery without claiming a probability that clusters exist. Prediction strength compares test-set co-memberships with assignments induced by a training clustering. The proposed project can preserve that separation of discovery and replication, replacing centroid assignment when nonconvex shapes require a neighborhood or prototype rule. Report collapse to one predicted cluster and minimum group size as well as agreement; one-sided co-membership scores alone can reward collapse. [Tibshirani and Walther, Cluster Validation by Prediction Strength, 2005](https://www.tandfonline.com/doi/abs/10.1198/106186005X59243).

Stability must remain one evidence axis. A stable optimizer can reproducibly partition a single population. Ben-David, von Luxburg, and Pál show that stability can be determined by uniqueness of the objective's optimum and can behave counterintuitively as a choice-of-k criterion. [A Sober Look at Clustering Stability, COLT 2006](https://www.tml.cs.uni-tuebingen.de/team/luxburg/publications/BenLuxPal06.pdf).

Recommended sequence: discover proposals on one sample; choose among a small frozen set on validation rows; reserve independent confirmation for the final panel and rule. Repeat by independent patient, animal, or donor where the design supports it. With too few independent units, use grouped repeated resampling descriptively and avoid claiming a formal confirmation result. Test whether candidates split correlated Gaussian, anisotropic unimodal, curved single-population, and batch-effect controls as search budget grows.

## Mathematical traps in feature-panel discovery beyond three dimensions

**Explaining a partition is easier than discovering its scientific meaning.** Once a partition P has been generated from S, optimizing its predictability from the very same S is circular. For a deterministic assignment `P=f(X_S)`, conditional entropy `H(P|X_S)=0`, so mutual information `I(P;X_S)=H(P)`. This cannot independently verify that S contains meaningful clusters. Predictability becomes useful for compression when P is frozen from a different discovery procedure and tested on independent rows; even then it verifies fidelity to P, not truth.

**Sufficiency is different from uniqueness.** If two features are interchangeable measurements of one latent variable, either may support the same separation. Exact feature recovery penalizes valid substitutes. Report deletion loss, successful replacements, and the equivalence of induced partitions. A locally irreducible panel is a concrete attainable output; global minimality generally requires much stronger structure or search.

**Some high-order signals have no low-order clues.** No choice of EA can guarantee scalable discovery for an unrestricted family in which every proper feature subset is uninformative. The project needs an explicit recoverability regime: useful features change neighborhoods, support a low-dimensional smooth weighted metric, or become informative conditional on a reasonably accessible provisional partition. Higher-order stress tests should expose violations of these assumptions, not silently redefine the target as a two-dimensional projection.

**A conditional signal offers a way forward.** Joint feature weighting and partition/graph updates can evaluate many features against a provisional structure at once; backward deletion can then establish which features preserve it. This is a plausible proposal-and-compression mechanism. Its failure modes are self-reinforcement of nuisance structure, arbitrary initial geometry, and selection of easy-to-predict artifacts. The diagnostic harness should retain proposed-but-unselected panels so these causes can be distinguished.

## Checks and limits

The companion tests check label-name invariance, exact agreement of corrected terms with the returned partition, legacy score reproduction on continuous data, rejection of constant/tiny panels, zero-distance geometry, deterministic fitting, and the two null-target examples. Executed on 2026-09-14 with `.venv-research/Scripts/python.exe -m pytest tests/test_research_scoring.py -q`: **19 passed**. No end-to-end clustering result is claimed by this module.

This is experiment planning, not a clinical, causal, or confirmatory statistical analysis. The relevant recurring interpretation risks are selection over panels and seeds, researcher choices tuned against external labels, pseudoreplication, and interpreting reproducible geometric separation as established biological fact. The new module addresses objective coherence and makes null targets explicit. It leaves scientific corroboration and final inference to the study design.
