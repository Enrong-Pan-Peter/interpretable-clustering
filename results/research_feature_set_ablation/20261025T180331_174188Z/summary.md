# Interpretable feature-set search

Controlled 2x2 development comparison: squared-correlation versus nonlinear kernel proposals, crossed with best-improvement versus first-improvement refinement. Every arm has the same unique-fit budget, model, fitness, size cap and initial random candidates. For a given dependence statistic, both refinement variants share all exploration candidates.

Raw data are copied byte-for-byte from the audited preceding pilot; their hashes and original metadata are retained. These previously inspected validation/test blocks are reused development evidence, not fresh confirmation. Kernel similarities use fitting observations only; the original-feature assignment rule is unchanged. Kernel preprocessing costs and optimizer status are recorded separately from unique fit counts.

Models fit on fit rows; adaptive search and final feature-set choice use search rows. Validation and test are excluded from this selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Feature set | Exact support | Oracle visited | Search gain | Val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| shells_d4_p24_seed2401_search3203 | moment_best | [0, 12] | False | False | 0.091 | 0.097 | 0.290 | True | 48 | 2.53 |
| shells_d4_p24_seed2401_search3203 | moment_first | [0, 12] | False | False | 0.091 | 0.097 | 0.290 | True | 48 | 2.56 |
| shells_d4_p24_seed2401_search3203 | kernel_best | [0, 1, 10] | False | False | 0.299 | 0.271 | 0.634 | True | 48 | 2.80 |
| shells_d4_p24_seed2401_search3203 | kernel_first | [0, 1, 10] | False | False | 0.299 | 0.271 | 0.634 | True | 48 | 2.85 |
| shells_d5_p24_seed2401_search3203 | moment_best | [0, 1, 7, 9, 10, 12, 17] | False | False | 0.194 | 0.160 | 0.745 | False | 48 | 2.52 |
| shells_d5_p24_seed2401_search3203 | moment_first | [0, 1, 7, 9, 12, 13, 14] | False | False | 0.037 | -0.011 | 0.480 | False | 48 | 2.57 |
| shells_d5_p24_seed2401_search3203 | kernel_best | [0, 1, 7, 9, 10, 12, 14] | False | False | 0.237 | 0.084 | 0.786 | False | 48 | 2.77 |
| shells_d5_p24_seed2401_search3203 | kernel_first | [0, 1, 7, 9, 10, 12, 14] | False | False | 0.237 | 0.084 | 0.786 | False | 48 | 2.76 |
| shells_d8_p24_seed2401_search3203 | moment_best | [0, 1, 2, 5, 9, 10, 12, 17, 23] | False | False | 0.804 | 0.631 | 0.967 | True | 48 | 2.31 |
| shells_d8_p24_seed2401_search3203 | moment_first | [0, 1, 2, 5, 9, 10, 12, 17, 23] | False | False | 0.804 | 0.631 | 0.967 | True | 48 | 2.38 |
| shells_d8_p24_seed2401_search3203 | kernel_best | [0, 2, 9, 12, 17, 23] | False | False | 0.475 | 0.358 | 0.768 | True | 48 | 2.56 |
| shells_d8_p24_seed2401_search3203 | kernel_first | [0, 2, 9, 12, 17, 23] | False | False | 0.475 | 0.358 | 0.768 | True | 48 | 2.55 |
| correlated_gaussian_d5_p24_seed2401_search3203 | moment_best | [3, 4, 5, 6, 14, 15, 17, 18, 20, 21] | False | False | 0.018 | -0.003 | — | False | 48 | 2.95 |
| correlated_gaussian_d5_p24_seed2401_search3203 | moment_first | [3, 4, 5, 6, 11, 12, 14, 16, 18, 22] | False | False | 0.024 | -0.003 | — | False | 48 | 2.89 |
| correlated_gaussian_d5_p24_seed2401_search3203 | kernel_best | [3, 4, 5, 6, 14, 15, 17, 18, 20, 21] | False | False | 0.018 | -0.003 | — | False | 48 | 3.21 |
| correlated_gaussian_d5_p24_seed2401_search3203 | kernel_first | [3, 4, 5, 6, 11, 12, 14, 16, 18, 22] | False | False | 0.024 | -0.003 | — | False | 48 | 3.17 |
