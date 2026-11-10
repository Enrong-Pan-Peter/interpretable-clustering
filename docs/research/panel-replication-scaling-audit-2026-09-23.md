# Native panel replication: scaling audit

Verification status: **ANALYZED**. This is a read-only analysis of the saved mean-shift cases in `results/research_panel_replication/20260921T202232_578177Z`. No model was fitted, no original output was changed, and no configuration was selected using test ARI. Source/result integrity and saved-prediction reconstruction are separate checks by the coordinating agent.

The main result is that preserving and compressing a learned rule works substantially better than discovering a useful rule at the harder settings. The bounded panels that were returned usually preserve their own teacher very closely. At 200 features and 12 planted signals, however, the full teachers are already poor: mean test ARI is 0.165 versus 0.753 for the supplied-panel oracle. A fidelity guarantee cannot repair this difference.

## Scope and denominators

The six configurations are all combinations of `p=50,200` and planted support size `s=5,8,12`, with generator seeds 6, 7, 8. Each case has 800 rows split into discovery A, discovery B, validation, and test blocks of 200 rows each. Both discovery fits use the same predeclared L1 upper bound of 4, three restarts, and at most 40 weight-update iterations. The native objective chooses the restart within its own discovery sample. Prefixes are frozen from discovery weights before validation.

Each configuration therefore has **six learner outcomes and three paired A/B comparisons**. The six outcomes are not six independent dataset replications: A and B share validation/test rows and the same generated dataset. Means below are descriptive, without confidence intervals, significance tests, or cross-case claims of simultaneous coverage.

The mean difference between generated classes has fixed Euclidean norm 3. Increasing `s` spreads this fixed separation across more coordinates; per-feature shifts become weaker. All planted coordinates are informative, but `s` is not guaranteed to be the unique minimum useful panel size. Exact support recovery and useful prediction are different targets.

The oracle receives the planted panel and fits ordinary unweighted two-means with 10 starts on the same learner's discovery rows. It is an ability benchmark; it neither discovers features nor uses the same optimizer. Its comparison with the native model does not isolate one causal implementation difference.

## Full models and feature discovery

ARI is against generated labels on the untouched test block. `Exact top-s` and `all signals in top-16` assess fixed, diagnostic ranks; they do not pick a size by test labels. Every denominator in these two columns is six.

| p | Planted s | Full native ARI | Supplied-panel oracle ARI | Oracle minus native | Exact top-s | All signals in top-16 |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 5 | 0.725 | 0.782 | 0.057 | 6/6 | 6/6 |
| 50 | 8 | 0.679 | 0.739 | 0.059 | 5/6 | 6/6 |
| 50 | 12 | 0.535 | 0.725 | 0.191 | 5/6 | 5/6 |
| 200 | 5 | 0.515 | 0.774 | 0.260 | 4/6 | 4/6 |
| 200 | 8 | 0.424 | 0.773 | 0.350 | 4/6 | 4/6 |
| 200 | 12 | 0.165 | 0.753 | 0.589 | 0/6 | 1/6 |

This method is computationally capable of proposing panels above three features, with no combination enumeration. It is not yet reliably discovering them. At `p=50,s=12`, five of six rankings contain the exact planted support in their first 12 positions. At `p=200,s=12`, none does. The supplied-panel oracle remains useful at every configuration, so the difficult cases cannot be dismissed as lacking recoverable signal in the supplied coordinates.

The failure is not solely a feature-ranking failure. At `p=200,s=8,seed=6`, learner B ranks all eight planted features first, but its full test ARI is only 0.369 versus oracle 0.773. Its largest weight is 0.815. At `p=200,s=12,seed=7`, A and B each rank 11 of 12 signals in their first 12 positions, yet full ARIs are 0.420 and 0.277; maximum weights are 0.725 and 0.920. The learned metric and resulting boundary matter after useful coordinates have been found.

There is also clear concentration on irrelevant coordinates. At `p=50,s=12,seed=8`, learner A places weight 0.9985 on one coordinate, has only one planted feature in its first 12 ranks, and has full test ARI -0.004 versus oracle 0.773. Its bounded singleton contains no planted feature but exactly reproduces the teacher on validation and test. This is a faithful explanation of an unsuccessful teacher, not successful discovery.

The positive-weight support is not bounded by 16. All 18 `p=50` teachers use all 50 coordinates. At `p=200`, 14 of 18 use all 200 coordinates, while four use 151, 155, or 157. Thus full-support recall is largely uninformative, and full-support Jaccard can be 1 even when two models make unrelated partitions.

## What compression selects

Sizes are in the fixed order **seed 6 A/B, seed 7 A/B, seed 8 A/B**; a dash means no bounded prefix was returned. Recall is planted overlap divided by `s`; precision is overlap divided by selected size. Means in a policy row use only its available outputs, and availability is shown explicitly. Exact recovery means equality with the whole planted set, not just containing it.

| p | s | Policy | Available | Selected sizes | Mean recall | Mean precision | Exact recovery |
|---:|---:|---|---:|---|---:|---:|---:|
| 50 | 5 | Empirical | 6/6 | 4, 4, 3, 5, 4, 4 | 0.800 | 1.000 | 1/6 |
| 50 | 5 | Bounded | 6/6 | 5, 5, 5, 5, 5, 5 | 1.000 | 1.000 | 6/6 |
| 50 | 8 | Empirical | 6/6 | 5, 6, 6, 6, 6, 5 | 0.708 | 1.000 | 0/6 |
| 50 | 8 | Bounded | 6/6 | 9, 8, 8, 8, 9, 8 | 1.000 | 0.963 | 4/6 |
| 50 | 12 | Empirical | 6/6 | 7, 7, 10, 7, 1, 8 | 0.542 | 0.833 | 0/6 |
| 50 | 12 | Bounded | 6/6 | 11, 16, 11, 10, 1, 12 | 0.778 | 0.792 | 1/6 |
| 200 | 5 | Empirical | 6/6 | 1, 4, 1, 4, 4, 4 | 0.533 | 0.667 | 0/6 |
| 200 | 5 | Bounded | 5/6 | 6, 7, 4, 12, —, 5 | 0.600 | 0.426 | 1/5 |
| 200 | 8 | Empirical | 6/6 | 1, 3, 7, 5, 5, 1 | 0.417 | 0.667 | 0/6 |
| 200 | 8 | Bounded | 5/6 | —, 6, 8, 8, 8, 1 | 0.750 | 0.800 | 3/5 |
| 200 | 12 | Empirical | 6/6 | 1, 1, 5, 2, 1, 4 | 0.167 | 0.667 | 0/6 |
| 200 | 12 | Bounded | 4/6 | —, 2, 10, 5, —, 10 | 0.521 | 0.950 | 0/4 |

Bounded selection returns 32 of 36 panels. All 32 have observed test disagreement with their own teacher at most 0.02; 8 of 36 empirical selections exceed 0.05. These are observed test errors, not estimates of simultaneous population coverage. The bounded policy measures fidelity to the frozen native rule, not recovery of planted labels or features.

For comparisons below, native ARI is averaged over **the same learners for which that policy returned a panel**. This avoids making missingness look like an improvement or deterioration.

| p | s | Empirical ARI | Empirical teacher disagreement | Bounded available | Native ARI on available learners | Bounded ARI | Bounded minus native | Bounded teacher disagreement |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 5 | 0.692 | 0.0333 | 6/6 | 0.725 | 0.739 | +0.0140 | 0.0058 |
| 50 | 8 | 0.607 | 0.0358 | 6/6 | 0.679 | 0.679 | -0.0000 | 0.0033 |
| 50 | 12 | 0.465 | 0.0358 | 6/6 | 0.535 | 0.526 | -0.0083 | 0.0058 |
| 200 | 5 | 0.442 | 0.0400 | 5/6 | 0.449 | 0.452 | +0.0035 | 0.0050 |
| 200 | 8 | 0.343 | 0.0417 | 5/6 | 0.510 | 0.499 | -0.0107 | 0.0070 |
| 200 | 12 | 0.130 | 0.0233 | 4/6 | 0.241 | 0.232 | -0.0087 | 0.0138 |

The observed compression loss under the bounded rule is small relative to the native-versus-oracle gap. The compact empirical panels trade away more teacher fidelity and sometimes label ARI, which is consistent with their weaker acceptance rule. Neither policy optimizes support recovery.

Missingness is a separate obstacle. The four unavailable bounded panels are:

| p | s | Seed/learner | Full ARI | Oracle ARI | Exact top-s? |
|---:|---:|---|---:|---:|---|
| 200 | 5 | 8/A | 0.846 | 0.883 | Yes |
| 200 | 8 | 6/A | -0.004 | 0.791 | No |
| 200 | 12 | 6/A | 0.001 | 0.704 | No |
| 200 | 12 | 8/A | 0.024 | 0.791 | No |

The first of these has a useful teacher and exactly recovered ranking at size five. Its unavailable bounded panel is a fidelity-certification/cap limitation, not evidence of discovery failure. Conversely, some unsuccessful teachers obtain bounded panels. Raising the cap or validation sample size could change availability; it would not by itself fix the bad teachers.

## Independent A/B rediscovery

These ARIs compare A's and B's test assignments with each other, not with generated labels. Label orientation for the reported disagreement was aligned on validation only. Missing pairs remain missing. Full-support Jaccard is deliberately omitted because its near-universal inclusion of all features is misleading as a compact-panel replication measure.

| p | s | Full A/B ARI, 3 pairs | Empirical A/B ARI, 3 pairs | Empirical feature Jaccard | Bounded pairs | Bounded A/B ARI | Bounded feature Jaccard |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 5 | 0.768 | 0.613 | 0.600 | 3/3 | 0.762 | 1.000 |
| 50 | 8 | 0.768 | 0.576 | 0.488 | 3/3 | 0.768 | 0.926 |
| 50 | 12 | 0.420 | 0.324 | 0.315 | 3/3 | 0.414 | 0.532 |
| 200 | 5 | 0.249 | 0.142 | 0.200 | 2/3 | -0.004 | 0.000 |
| 200 | 8 | 0.237 | 0.184 | 0.167 | 2/3 | 0.367 | 0.500 |
| 200 | 12 | 0.037 | 0.020 | 0.056 | 1/3 | 0.085 | 0.500 |

The poor replication at high dimension already exists in the full teachers. At `p=200,s=5`, the only pair with strong full-model agreement (seed 8, ARI 0.756) is absent from the bounded-pair calculation because A has no bounded panel. The bounded mean of -0.004 should therefore not be described as a within-pair decline from the all-case full mean of 0.249.

All saved full and selected A/B comparisons with available predictions meet the experiment's minimum-five-members rule in validation and test. The failures above are not an artifact of reporting tiny groups; that guard is nevertheless far weaker than evidence of meaningful clusters.

## Diagnosis and a targeted next experiment

Three mechanisms should remain separate:

1. **Discovery/metric failure:** the full native rule can concentrate on a nuisance coordinate, or overemphasize one weak planted coordinate even when other signals rank highly. At `p=200,s=12`, this dominates the result.
2. **Compression:** a selected prefix can change a useful teacher. The bounded policy makes this change small in these saved cases; the empirical policy sacrifices more fidelity. Faithfully compressing an unsuccessful teacher still leaves it unsuccessful.
3. **Certification and reproducibility:** a useful teacher can lack a certified prefix within the cap, while independent discovery can choose different rules. These have different denominators and remedies.

The objective is implicated, but these files alone do not prove that every failed fit reached the global optimum, or that all nonselected restarts had worse external ARI. Only the chosen model is saved in full; other restart traces contain objectives, not the complete predictions needed for that comparison. The separate population-objective audit examines why a diffuse mean direction can be outranked by a one-coordinate split under this weighted between-cluster objective.

A practical next ablation is a **predeclared comparison of optimizer effort and weight concentration**, retaining the present splits, cap, frozen assignment rule, and prefix validation:

- Keep the current three-start learner as the reference. Add a 30-start version with the same objective and a nested random-seed stream; preserve every restart's weights, centers, objective, and downstream predictions. This distinguishes missed objective maxima from an objective that favors unhelpful partitions. Select restarts using discovery objective only, and report the extra time.
- Add one explicitly experimental concentration constraint, for example `max_j w_j <= 0.5` under the existing nonnegative L2/L1 bounds. This fixed value is not supplied the true support size; equal weights on 5, 8, or 12 signals remain feasible. Compare it with the same declared optimizer budgets rather than picking a winner by test ARI. It may reduce one-coordinate domination, but may hurt genuinely one-feature clusters and does not establish cluster existence. Include the independent and correlated Gaussian controls plus a true one-feature positive control.

The concentration-constrained update is a new optimization problem and needs its own numerical validation before running the ablation; clipping and renormalizing current weights is not a justified exact update. This is a bounded diagnostic proposal, not an established solution or novelty claim. Do not tune the cap, concentration limit, initialization, or selector repeatedly against the present test labels. Use these cases as diagnosis and reserve fresh seeds for confirmation.

## Material passport and interpretation checks

Source material: the aggregate/per-case JSON reports, each selected model's NPZ weights, data-protocol reference panels, and the local runner/method implementation. Calculations: arithmetic means of all configured outcomes, overlaps at fixed ranks, saved maximum weights, and explicit conditional denominators. No external dataset, new cohort, refit, or test-label selection was introduced.

ARS interpretation checklist coverage (11/11): Simpson's paradox is addressed by keeping all six configurations separate; ecological fallacy by avoiding individual or biological inference; Berkson's paradox and collider bias by disclosing conditioning on panel availability rather than treating available panels as a random sample; base-rate neglect by distinguishing teacher fidelity from cluster validity; regression to the mean by treating unusual individual seeds as examples rather than promised improvements; survivorship bias by showing every missing panel; look-elsewhere effects by using fixed configurations and diagnostic ranks rather than a best-test winner; forking paths by declaring proposed changes prospective and requiring fresh confirmation; correlation/causation and reverse causality by making no causal biological claim and not attributing the native-oracle difference to one isolated change.

The present evidence supports improving the learned rule and its objective before further polishing fidelity selection. It does not yet support a general interpretable-clustering method for arbitrary shapes or a claim that the returned groups correspond to distinct populations.
