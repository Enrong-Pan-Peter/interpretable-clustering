# Native panel replication: saved-results audit

## Material Passport

- Origin: academic-research-suite experiment validation
- Date: 2026-09-23
- Status: ANALYZED; saved arithmetic/states verified; no clustering fits rerun
- Cases: 27; checks: 15918; discrepancies: 0

No clustering refits; saved native/oracle states, exported rules, predictions, metrics and choices replayed. Objective probe uses post-hoc oracle labels; no new model or annotation-selected winner.

Development evidence, not independent cohort confirmation. Bounds concern population disagreement under iid sampling; test exceedances are descriptive, not confidence-bound violations. No cluster-existence rule.

## All prescribed groups

Means use available outputs; denominators differ and must remain visible. Full-support overlap is not informative when almost every feature has a positive weight.

| Dataset | p | Signals | Policy | Available | Mean size | Test ARI | Test disagreement | Complete A/B pairs | A/B test ARI | Oracle ARI |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| mean_shift | 50 | 5 | full | 6/6 | 50.000 | 0.725 | — | 3 | 0.768 | 0.782 |
| mean_shift | 50 | 5 | empirical | 6/6 | 4.000 | 0.692 | 0.033 | 3 | 0.613 | 0.782 |
| mean_shift | 50 | 5 | bounded | 6/6 | 5.000 | 0.739 | 0.006 | 3 | 0.762 | 0.782 |
| mean_shift | 50 | 8 | full | 6/6 | 50.000 | 0.679 | — | 3 | 0.768 | 0.739 |
| mean_shift | 50 | 8 | empirical | 6/6 | 5.667 | 0.607 | 0.036 | 3 | 0.576 | 0.739 |
| mean_shift | 50 | 8 | bounded | 6/6 | 8.333 | 0.679 | 0.003 | 3 | 0.768 | 0.739 |
| mean_shift | 50 | 12 | full | 6/6 | 50.000 | 0.535 | — | 3 | 0.420 | 0.725 |
| mean_shift | 50 | 12 | empirical | 6/6 | 6.667 | 0.465 | 0.036 | 3 | 0.324 | 0.725 |
| mean_shift | 50 | 12 | bounded | 6/6 | 10.167 | 0.526 | 0.006 | 3 | 0.414 | 0.725 |
| mean_shift | 200 | 5 | full | 6/6 | 200.000 | 0.515 | — | 3 | 0.249 | 0.774 |
| mean_shift | 200 | 5 | empirical | 6/6 | 3.000 | 0.442 | 0.040 | 3 | 0.142 | 0.774 |
| mean_shift | 200 | 5 | bounded | 5/6 | 6.800 | 0.452 | 0.005 | 2 | -0.004 | 0.774 |
| mean_shift | 200 | 8 | full | 6/6 | 177.167 | 0.424 | — | 3 | 0.237 | 0.773 |
| mean_shift | 200 | 8 | empirical | 6/6 | 3.667 | 0.343 | 0.042 | 3 | 0.184 | 0.773 |
| mean_shift | 200 | 8 | bounded | 5/6 | 6.200 | 0.499 | 0.007 | 2 | 0.367 | 0.773 |
| mean_shift | 200 | 12 | full | 6/6 | 192.833 | 0.165 | — | 3 | 0.037 | 0.753 |
| mean_shift | 200 | 12 | empirical | 6/6 | 2.333 | 0.130 | 0.023 | 3 | 0.020 | 0.753 |
| mean_shift | 200 | 12 | bounded | 4/6 | 6.750 | 0.232 | 0.014 | 1 | 0.085 | 0.753 |
| metabric | 250 | — | full | 6/6 | 20.167 | 0.492 | — | 3 | 0.847 | — |
| metabric | 250 | — | empirical | 6/6 | 3.667 | 0.457 | 0.052 | 3 | 0.739 | — |
| metabric | 250 | — | bounded | 3/6 | 11.000 | 0.489 | 0.032 | 0 | — | — |
| null_independent | 200 | — | full | 6/6 | 200.000 | — | — | 3 | 0.004 | — |
| null_independent | 200 | — | empirical | 6/6 | 1.000 | — | 0.033 | 3 | 0.000 | — |
| null_independent | 200 | — | bounded | 3/6 | 2.000 | — | 0.022 | 0 | — | — |
| null_correlated | 200 | — | full | 6/6 | 28.000 | — | — | 3 | 0.773 | — |
| null_correlated | 200 | — | empirical | 6/6 | 6.000 | — | 0.050 | 3 | 0.600 | — |
| null_correlated | 200 | — | bounded | 4/6 | 13.250 | — | 0.009 | 2 | 0.757 | — |

## Matched compression comparison

On the same 42 learners where bounded selection returns a panel:

- Empirical mean test disagreement: 0.039; above 5% on 12 outputs.
- Bounded mean test disagreement: 0.010; above 5% on 0 outputs.
- Missing bounded panels are not silently replaced. See the per-group denominators and statistical audit for the abstention cost.

## Objective probe

Known-support oracle partitions and latent generating labels enter only this diagnostic. Each fixed partition receives its optimal nonnegative L1/L2 feature weights under the same bound as the native model. This is not a feasible label-free selector or a new fitted clustering solution.

| p | Signals | Native score / row | Oracle-partition score / row | Native score higher / 6 | Mean largest squared weight |
|---:|---:|---:|---:|---:|---:|
| 50 | 5 | 0.782 | 0.777 | 5/6 | 0.309 |
| 50 | 8 | 0.715 | 0.707 | 6/6 | 0.239 |
| 50 | 12 | 0.687 | 0.665 | 6/6 | 0.376 |
| 200 | 5 | 0.752 | 0.778 | 2/6 | 0.500 |
| 200 | 8 | 0.705 | 0.702 | 4/6 | 0.568 |
| 200 | 12 | 0.677 | 0.632 | 6/6 | 0.814 |

Statistical review: 11/11 scoped checks. Dataset/configuration effects are separated; no ecological, causal or reverse-causal claims; annotation-filtered cohorts and cached feature selection remain limits; no prevalence/diagnostic probabilities claimed; selection/extreme-score regression, missingness, multiplicity, and researcher degrees of freedom are disclosed. These dependent fits and reused cohorts do not justify a universal superiority or novelty claim.
