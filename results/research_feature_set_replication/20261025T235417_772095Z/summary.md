# Interpretable feature-set search

Frozen candidate replication/stress comparison: moment_best versus kernel_best, with identical predictive fitness, original-feature rules and unique-fit budgets. Data seeds are separate from development and smoke seeds. Each full-run population is searched with two independently specified search seeds.

Conditions are baseline replication, more nuisance measurements, weaker shell separation, and two dependent Gaussian nuisance blocks. Repeated search seeds reuse the same observations and are not independent data replications. Report each condition separately. The smoke suite checks execution only and uses a reduced budget on separate seeds.

Models fit on fit rows; adaptive search and final feature-set choice use search rows. Validation and test are excluded from this selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Feature set | Exact support | Oracle visited | Search gain | Val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| baseline_shells_d4_p24_seed5903_search6907 | moment_best | [7, 11, 17] | False | False | 0.072 | -0.027 | 0.011 | False | 16 | 0.81 |
| baseline_shells_d4_p24_seed5903_search6907 | kernel_best | [7, 11, 17] | False | False | 0.072 | -0.027 | 0.011 | False | 16 | 0.82 |
| more_nuisance_shells_d4_p72_seed5903_search6907 | moment_best | [3, 5, 6, 38, 65] | False | False | 0.012 | -0.005 | 0.012 | False | 16 | 0.97 |
| more_nuisance_shells_d4_p72_seed5903_search6907 | kernel_best | [3, 5, 6, 38, 65] | False | False | 0.012 | -0.005 | 0.012 | False | 16 | 1.01 |
| weak_separation_shells_d4_p24_seed5903_search6907 | moment_best | [0, 2, 4, 5, 6, 7, 8, 19, 22] | False | False | 0.053 | 0.043 | -0.002 | False | 16 | 0.92 |
| weak_separation_shells_d4_p24_seed5903_search6907 | kernel_best | [0, 2, 4, 5, 6, 7, 8, 19, 22] | False | False | 0.053 | 0.043 | -0.002 | False | 16 | 0.93 |
| dependent_nuisance_shells_d4_p24_seed5903_search6907 | moment_best | [10, 13, 23] | False | False | 0.039 | -0.033 | 0.006 | False | 16 | 0.72 |
| dependent_nuisance_shells_d4_p24_seed5903_search6907 | kernel_best | [10, 13, 23] | False | False | 0.039 | -0.033 | 0.006 | False | 16 | 0.70 |
