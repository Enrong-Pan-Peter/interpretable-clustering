# Interpretable feature-set search

Frozen candidate replication/stress comparison: moment_best versus kernel_best, with identical predictive fitness, original-feature rules and unique-fit budgets. Data seeds are separate from development and smoke seeds. Each full-run population is searched with two independently specified search seeds.

Conditions are baseline replication, more nuisance measurements, weaker shell separation, and two dependent Gaussian nuisance blocks. Repeated search seeds reuse the same observations and are not independent data replications. Report each condition separately. The smoke suite checks execution only and uses a reduced budget on separate seeds.

Models fit on fit rows; adaptive search and final feature-set choice use search rows. Validation and test are excluded from this selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Feature set | Exact support | Oracle visited | Search gain | Val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| baseline_shells_d2_p24_seed5101_search6101 | moment_best | [0, 5] | True | True | 0.720 | 0.665 | 1.000 | True | 256 | 16.49 |
| baseline_shells_d2_p24_seed5101_search6101 | kernel_best | [0, 5] | True | True | 0.720 | 0.665 | 1.000 | True | 256 | 15.45 |
| baseline_shells_d2_p24_seed5101_search6113 | moment_best | [0, 5] | True | True | 0.720 | 0.665 | 1.000 | True | 256 | 15.12 |
| baseline_shells_d2_p24_seed5101_search6113 | kernel_best | [0, 5] | True | True | 0.720 | 0.665 | 1.000 | True | 256 | 15.54 |
| baseline_shells_d2_p24_seed5113_search6101 | moment_best | [9, 17] | True | True | 0.812 | 0.717 | 1.000 | True | 256 | 17.29 |
| baseline_shells_d2_p24_seed5113_search6101 | kernel_best | [9, 17] | True | True | 0.812 | 0.717 | 1.000 | True | 256 | 18.30 |
| baseline_shells_d2_p24_seed5113_search6113 | moment_best | [9, 17] | True | True | 0.812 | 0.717 | 1.000 | True | 256 | 15.53 |
| baseline_shells_d2_p24_seed5113_search6113 | kernel_best | [9, 17] | True | True | 0.812 | 0.717 | 1.000 | True | 256 | 16.63 |
| baseline_shells_d2_p24_seed5119_search6101 | moment_best | [7, 15] | True | True | 0.731 | 0.767 | 1.000 | True | 256 | 16.41 |
| baseline_shells_d2_p24_seed5119_search6101 | kernel_best | [7, 15] | True | True | 0.731 | 0.767 | 1.000 | True | 256 | 15.87 |
| baseline_shells_d2_p24_seed5119_search6113 | moment_best | [7, 15] | True | True | 0.731 | 0.767 | 1.000 | True | 256 | 16.43 |
| baseline_shells_d2_p24_seed5119_search6113 | kernel_best | [7, 15] | True | True | 0.731 | 0.767 | 1.000 | True | 256 | 16.39 |
| baseline_shells_d3_p24_seed5101_search6101 | moment_best | [0, 5, 23] | True | True | 0.734 | 0.642 | 1.000 | True | 256 | 13.82 |
| baseline_shells_d3_p24_seed5101_search6101 | kernel_best | [0, 5, 23] | True | True | 0.734 | 0.642 | 1.000 | True | 256 | 12.85 |
| baseline_shells_d3_p24_seed5101_search6113 | moment_best | [0, 5, 23] | True | True | 0.734 | 0.642 | 1.000 | True | 256 | 13.78 |
| baseline_shells_d3_p24_seed5101_search6113 | kernel_best | [0, 5, 23] | True | True | 0.734 | 0.642 | 1.000 | True | 256 | 13.43 |
| baseline_shells_d3_p24_seed5113_search6101 | moment_best | [9, 17, 23] | True | True | 0.684 | 0.746 | 1.000 | True | 256 | 13.72 |
| baseline_shells_d3_p24_seed5113_search6101 | kernel_best | [9, 17, 23] | True | True | 0.684 | 0.746 | 1.000 | True | 256 | 13.39 |
| baseline_shells_d3_p24_seed5113_search6113 | moment_best | [9, 17, 23] | True | True | 0.684 | 0.746 | 1.000 | True | 256 | 14.06 |
| baseline_shells_d3_p24_seed5113_search6113 | kernel_best | [9, 17, 23] | True | True | 0.684 | 0.746 | 1.000 | True | 256 | 13.44 |
| baseline_shells_d3_p24_seed5119_search6101 | moment_best | [7, 9, 15] | True | True | 0.701 | 0.707 | 1.000 | True | 256 | 13.53 |
| baseline_shells_d3_p24_seed5119_search6101 | kernel_best | [7, 9, 15] | True | True | 0.701 | 0.707 | 1.000 | True | 256 | 12.92 |
| baseline_shells_d3_p24_seed5119_search6113 | moment_best | [7, 9, 15] | True | True | 0.701 | 0.707 | 1.000 | True | 256 | 13.62 |
| baseline_shells_d3_p24_seed5119_search6113 | kernel_best | [7, 9, 15] | True | True | 0.701 | 0.707 | 1.000 | True | 256 | 13.17 |
| baseline_shells_d4_p24_seed5101_search6101 | moment_best | [9, 12] | False | False | 0.032 | -0.016 | 0.077 | False | 256 | 14.21 |
| baseline_shells_d4_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 23] | True | True | 0.784 | 0.768 | 1.000 | True | 256 | 12.28 |
| baseline_shells_d4_p24_seed5101_search6113 | moment_best | [9, 12] | False | False | 0.032 | -0.016 | 0.077 | False | 256 | 14.21 |
| baseline_shells_d4_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 23] | True | True | 0.784 | 0.768 | 1.000 | True | 256 | 12.14 |
| baseline_shells_d4_p24_seed5113_search6101 | moment_best | [5, 9, 17, 23] | True | True | 0.695 | 0.739 | 1.000 | True | 256 | 13.04 |
| baseline_shells_d4_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 23] | True | True | 0.695 | 0.739 | 1.000 | True | 256 | 12.67 |
| baseline_shells_d4_p24_seed5113_search6113 | moment_best | [5, 7, 9, 17, 23] | False | False | 0.296 | 0.291 | 0.822 | True | 256 | 13.11 |
| baseline_shells_d4_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 23] | True | True | 0.695 | 0.739 | 1.000 | True | 256 | 12.87 |
| baseline_shells_d4_p24_seed5119_search6101 | moment_best | [9, 16] | False | False | 0.083 | 0.085 | 0.298 | False | 256 | 14.60 |
| baseline_shells_d4_p24_seed5119_search6101 | kernel_best | [7, 9, 15, 16] | True | True | 0.689 | 0.686 | 1.000 | True | 256 | 12.56 |
| baseline_shells_d4_p24_seed5119_search6113 | moment_best | [7, 16] | False | False | 0.083 | 0.090 | 0.312 | True | 256 | 14.32 |
| baseline_shells_d4_p24_seed5119_search6113 | kernel_best | [7, 9, 15, 16] | True | True | 0.689 | 0.686 | 1.000 | True | 256 | 12.73 |
| baseline_shells_d5_p24_seed5101_search6101 | moment_best | [5, 12, 16, 23] | False | False | 0.307 | 0.324 | 0.834 | True | 256 | 13.31 |
| baseline_shells_d5_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.767 | 0.803 | 1.000 | True | 256 | 11.68 |
| baseline_shells_d5_p24_seed5101_search6113 | moment_best | [5, 12, 16, 23] | False | False | 0.307 | 0.324 | 0.834 | True | 256 | 13.22 |
| baseline_shells_d5_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.767 | 0.803 | 1.000 | True | 256 | 11.78 |
| baseline_shells_d5_p24_seed5113_search6101 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.827 | 0.852 | 1.000 | True | 256 | 12.22 |
| baseline_shells_d5_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.827 | 0.852 | 1.000 | True | 256 | 11.99 |
| baseline_shells_d5_p24_seed5113_search6113 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.827 | 0.852 | 1.000 | True | 256 | 12.46 |
| baseline_shells_d5_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.827 | 0.852 | 1.000 | True | 256 | 12.03 |
| baseline_shells_d5_p24_seed5119_search6101 | moment_best | [5, 9, 15, 16] | False | False | 0.337 | 0.308 | 0.804 | True | 256 | 12.59 |
| baseline_shells_d5_p24_seed5119_search6101 | kernel_best | [5, 7, 9, 15, 16] | True | True | 0.732 | 0.775 | 1.000 | True | 256 | 11.60 |
| baseline_shells_d5_p24_seed5119_search6113 | moment_best | [5, 7, 9, 15, 16] | True | True | 0.732 | 0.775 | 1.000 | True | 256 | 12.70 |
| baseline_shells_d5_p24_seed5119_search6113 | kernel_best | [5, 7, 9, 15, 16] | True | True | 0.732 | 0.775 | 1.000 | True | 256 | 11.71 |
| baseline_shells_d8_p24_seed5101_search6101 | moment_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.173 | 1.202 | 1.000 | True | 256 | 11.75 |
| baseline_shells_d8_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.173 | 1.202 | 1.000 | True | 256 | 11.74 |
| baseline_shells_d8_p24_seed5101_search6113 | moment_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.173 | 1.202 | 1.000 | True | 256 | 11.74 |
| baseline_shells_d8_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.173 | 1.202 | 1.000 | True | 256 | 11.79 |
| baseline_shells_d8_p24_seed5113_search6101 | moment_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 11.55 |
| baseline_shells_d8_p24_seed5113_search6101 | kernel_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 11.94 |
| baseline_shells_d8_p24_seed5113_search6113 | moment_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 11.67 |
| baseline_shells_d8_p24_seed5113_search6113 | kernel_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 12.05 |
| baseline_shells_d8_p24_seed5119_search6101 | moment_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 11.73 |
| baseline_shells_d8_p24_seed5119_search6101 | kernel_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 11.84 |
| baseline_shells_d8_p24_seed5119_search6113 | moment_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 11.84 |
| baseline_shells_d8_p24_seed5119_search6113 | kernel_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 11.86 |
| baseline_single_shell_d2_p24_seed5101_search6101 | moment_best | [0, 5] | True | True | 1.490 | 1.551 | — | False | 256 | 14.70 |
| baseline_single_shell_d2_p24_seed5101_search6101 | kernel_best | [0, 5] | True | True | 1.490 | 1.551 | — | False | 256 | 15.54 |
| baseline_single_shell_d2_p24_seed5101_search6113 | moment_best | [0, 5] | True | True | 1.490 | 1.551 | — | False | 256 | 15.16 |
| baseline_single_shell_d2_p24_seed5101_search6113 | kernel_best | [0, 5] | True | True | 1.490 | 1.551 | — | False | 256 | 15.89 |
| baseline_single_shell_d2_p24_seed5113_search6101 | moment_best | [9, 17] | True | True | 1.530 | 1.600 | — | False | 256 | 14.84 |
| baseline_single_shell_d2_p24_seed5113_search6101 | kernel_best | [9, 17] | True | True | 1.530 | 1.600 | — | False | 256 | 16.45 |
| baseline_single_shell_d2_p24_seed5113_search6113 | moment_best | [9, 17] | True | True | 1.530 | 1.600 | — | False | 256 | 15.15 |
| baseline_single_shell_d2_p24_seed5113_search6113 | kernel_best | [9, 17] | True | True | 1.530 | 1.600 | — | False | 256 | 14.83 |
| baseline_single_shell_d2_p24_seed5119_search6101 | moment_best | [7, 15] | True | True | 1.627 | 1.624 | — | False | 256 | 14.99 |
| baseline_single_shell_d2_p24_seed5119_search6101 | kernel_best | [7, 15] | True | True | 1.627 | 1.624 | — | False | 256 | 16.09 |
| baseline_single_shell_d2_p24_seed5119_search6113 | moment_best | [7, 15] | True | True | 1.627 | 1.624 | — | False | 256 | 14.93 |
| baseline_single_shell_d2_p24_seed5119_search6113 | kernel_best | [7, 15] | True | True | 1.627 | 1.624 | — | False | 256 | 16.04 |
| baseline_single_shell_d5_p24_seed5101_search6101 | moment_best | [0, 5, 12, 16, 23] | True | True | 1.100 | 1.170 | — | False | 256 | 17.38 |
| baseline_single_shell_d5_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 16, 23] | True | True | 1.100 | 1.170 | — | False | 256 | 17.72 |
| baseline_single_shell_d5_p24_seed5101_search6113 | moment_best | [0, 5, 12, 16, 23] | True | True | 1.100 | 1.170 | — | False | 256 | 17.19 |
| baseline_single_shell_d5_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 16, 23] | True | True | 1.100 | 1.170 | — | False | 256 | 17.54 |
| baseline_single_shell_d5_p24_seed5113_search6101 | moment_best | [5, 9, 17, 18, 23] | True | True | 1.124 | 1.140 | — | False | 256 | 17.43 |
| baseline_single_shell_d5_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 18, 23] | True | True | 1.124 | 1.140 | — | False | 256 | 18.09 |
| baseline_single_shell_d5_p24_seed5113_search6113 | moment_best | [5, 9, 17, 18, 23] | True | True | 1.124 | 1.140 | — | False | 256 | 17.91 |
| baseline_single_shell_d5_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 18, 23] | True | True | 1.124 | 1.140 | — | False | 256 | 18.03 |
| baseline_single_shell_d5_p24_seed5119_search6101 | moment_best | [5, 7, 9, 15, 16] | True | True | 1.056 | 1.020 | — | False | 256 | 17.19 |
| baseline_single_shell_d5_p24_seed5119_search6101 | kernel_best | [5, 7, 9, 15, 16] | True | True | 1.056 | 1.020 | — | False | 256 | 18.04 |
| baseline_single_shell_d5_p24_seed5119_search6113 | moment_best | [5, 7, 9, 15, 16] | True | True | 1.056 | 1.020 | — | False | 256 | 18.07 |
| baseline_single_shell_d5_p24_seed5119_search6113 | kernel_best | [5, 7, 9, 15, 16] | True | True | 1.056 | 1.020 | — | False | 256 | 18.62 |
| baseline_independent_gaussian_d5_p24_seed5101_search6101 | moment_best | [0, 1, 2, 6, 11, 13, 18, 21, 22] | False | False | 0.001 | -0.015 | — | False | 256 | 15.55 |
| baseline_independent_gaussian_d5_p24_seed5101_search6101 | kernel_best | [9, 12, 13, 17] | False | False | 0.005 | -0.016 | — | False | 256 | 15.56 |
| baseline_independent_gaussian_d5_p24_seed5101_search6113 | moment_best | [0, 1, 2, 6, 11, 18, 21, 22, 23] | False | False | 0.000 | -0.022 | — | False | 256 | 15.70 |
| baseline_independent_gaussian_d5_p24_seed5101_search6113 | kernel_best | [9, 12, 13, 17] | False | False | 0.005 | -0.016 | — | False | 256 | 15.68 |
| baseline_independent_gaussian_d5_p24_seed5113_search6101 | moment_best | [2, 4, 5, 14, 20] | False | False | 0.008 | -0.015 | — | False | 256 | 14.73 |
| baseline_independent_gaussian_d5_p24_seed5113_search6101 | kernel_best | [2, 5, 6, 7, 10, 14, 17, 19, 23] | False | False | 0.005 | -0.024 | — | False | 256 | 14.94 |
| baseline_independent_gaussian_d5_p24_seed5113_search6113 | moment_best | [2, 4, 5, 14, 20] | False | False | 0.008 | -0.015 | — | False | 256 | 14.98 |
| baseline_independent_gaussian_d5_p24_seed5113_search6113 | kernel_best | [2, 5, 6, 7, 10, 14, 17, 19, 23] | False | False | 0.005 | -0.024 | — | False | 256 | 15.21 |
| baseline_independent_gaussian_d5_p24_seed5119_search6101 | moment_best | [4, 10, 15, 22] | False | False | -0.001 | -0.085 | — | False | 256 | 14.96 |
| baseline_independent_gaussian_d5_p24_seed5119_search6101 | kernel_best | [4, 6, 7, 16, 21, 23] | False | False | 0.003 | -0.032 | — | False | 256 | 14.95 |
| baseline_independent_gaussian_d5_p24_seed5119_search6113 | moment_best | [0, 4, 7, 13, 16, 19, 23] | False | False | 0.010 | -0.024 | — | False | 256 | 14.90 |
| baseline_independent_gaussian_d5_p24_seed5119_search6113 | kernel_best | [4, 6, 7, 16, 21, 23] | False | False | 0.003 | -0.032 | — | False | 256 | 15.05 |
| baseline_correlated_gaussian_d5_p24_seed5101_search6101 | moment_best | [3, 13, 17, 22] | False | True | 0.005 | -0.020 | — | False | 256 | 15.03 |
| baseline_correlated_gaussian_d5_p24_seed5101_search6101 | kernel_best | [1, 2, 3, 7, 8, 17, 19, 21, 22] | False | True | 0.019 | 0.009 | — | False | 256 | 14.96 |
| baseline_correlated_gaussian_d5_p24_seed5101_search6113 | moment_best | [3, 13, 17, 22] | False | True | 0.005 | -0.020 | — | False | 256 | 14.97 |
| baseline_correlated_gaussian_d5_p24_seed5101_search6113 | kernel_best | [1, 2, 3, 4, 7, 8, 17, 19, 21, 22] | False | True | 0.022 | 0.010 | — | False | 256 | 14.95 |
| baseline_correlated_gaussian_d5_p24_seed5113_search6101 | moment_best | [0, 1, 6, 8, 11, 13, 16, 18, 21] | False | True | 0.031 | 0.007 | — | False | 256 | 14.75 |
| baseline_correlated_gaussian_d5_p24_seed5113_search6101 | kernel_best | [0, 1, 5, 6, 21] | False | True | 0.012 | -0.033 | — | False | 256 | 14.53 |
| baseline_correlated_gaussian_d5_p24_seed5113_search6113 | moment_best | [3, 5, 6, 7, 8, 11, 12, 13, 14] | False | True | 0.029 | 0.008 | — | False | 256 | 14.62 |
| baseline_correlated_gaussian_d5_p24_seed5113_search6113 | kernel_best | [0, 1, 5, 6, 11, 16] | False | True | 0.012 | -0.006 | — | False | 256 | 14.68 |
| baseline_correlated_gaussian_d5_p24_seed5119_search6101 | moment_best | [0, 1, 4, 8, 13, 18, 20, 23] | False | True | 0.039 | 0.010 | — | False | 256 | 14.66 |
| baseline_correlated_gaussian_d5_p24_seed5119_search6101 | kernel_best | [0, 2, 4, 12, 13, 17, 18, 20, 21, 23] | False | True | 0.053 | 0.010 | — | False | 256 | 14.81 |
| baseline_correlated_gaussian_d5_p24_seed5119_search6113 | moment_best | [0, 1, 4, 6, 8, 13, 18, 20, 23] | False | True | 0.037 | 0.005 | — | False | 256 | 14.58 |
| baseline_correlated_gaussian_d5_p24_seed5119_search6113 | kernel_best | [0, 2, 4, 6, 12, 13, 17, 18, 21, 23] | False | True | 0.052 | 0.020 | — | False | 256 | 14.76 |
| baseline_student_t_d5_p24_seed5101_search6101 | moment_best | [13, 14, 15, 22] | False | True | -0.067 | -0.211 | — | False | 256 | 13.85 |
| baseline_student_t_d5_p24_seed5101_search6101 | kernel_best | [13, 14, 22] | False | True | -0.069 | -0.131 | — | False | 256 | 13.92 |
| baseline_student_t_d5_p24_seed5101_search6113 | moment_best | [13, 14, 15, 22] | False | True | -0.067 | -0.211 | — | False | 256 | 13.72 |
| baseline_student_t_d5_p24_seed5101_search6113 | kernel_best | [13, 14, 22] | False | True | -0.069 | -0.131 | — | False | 256 | 13.97 |
| baseline_student_t_d5_p24_seed5113_search6101 | moment_best | [1, 3, 9, 20] | False | True | -0.064 | -0.244 | — | False | 256 | 14.57 |
| baseline_student_t_d5_p24_seed5113_search6101 | kernel_best | [8, 9, 20] | False | True | -0.037 | -0.260 | — | False | 256 | 14.10 |
| baseline_student_t_d5_p24_seed5113_search6113 | moment_best | [1, 3, 7, 9, 11] | False | True | -0.060 | -0.175 | — | False | 256 | 14.71 |
| baseline_student_t_d5_p24_seed5113_search6113 | kernel_best | [8, 9, 20] | False | True | -0.037 | -0.260 | — | False | 256 | 14.28 |
| baseline_student_t_d5_p24_seed5119_search6101 | moment_best | [1, 9] | False | True | -0.058 | -0.298 | — | False | 256 | 13.44 |
| baseline_student_t_d5_p24_seed5119_search6101 | kernel_best | [1, 16] | False | True | -0.073 | -0.392 | — | False | 256 | 14.87 |
| baseline_student_t_d5_p24_seed5119_search6113 | moment_best | [1, 10] | False | True | -0.063 | -0.235 | — | False | 256 | 13.45 |
| baseline_student_t_d5_p24_seed5119_search6113 | kernel_best | [1, 16] | False | True | -0.073 | -0.392 | — | False | 256 | 14.92 |
| baseline_common_center_scale_mixture_d5_p24_seed5101_search6101 | moment_best | [1, 5, 17, 20] | False | True | -0.018 | -0.158 | — | False | 256 | 14.34 |
| baseline_common_center_scale_mixture_d5_p24_seed5101_search6101 | kernel_best | [5, 20] | False | True | -0.025 | -0.085 | — | False | 256 | 14.59 |
| baseline_common_center_scale_mixture_d5_p24_seed5101_search6113 | moment_best | [0, 4, 7, 11, 13, 14, 16, 17, 20, 23] | False | True | -0.020 | -0.144 | — | False | 256 | 13.81 |
| baseline_common_center_scale_mixture_d5_p24_seed5101_search6113 | kernel_best | [0, 4, 7, 11, 13, 14, 16, 17, 20, 23] | False | True | -0.020 | -0.144 | — | False | 256 | 14.00 |
| baseline_common_center_scale_mixture_d5_p24_seed5113_search6101 | moment_best | [9, 14] | False | True | -0.037 | -0.161 | — | False | 256 | 12.97 |
| baseline_common_center_scale_mixture_d5_p24_seed5113_search6101 | kernel_best | [8, 9, 11, 15, 16] | False | True | 0.006 | -0.117 | — | False | 256 | 14.37 |
| baseline_common_center_scale_mixture_d5_p24_seed5113_search6113 | moment_best | [2, 3, 7, 10, 13, 22] | False | True | -0.020 | -0.100 | — | False | 256 | 14.15 |
| baseline_common_center_scale_mixture_d5_p24_seed5113_search6113 | kernel_best | [8, 9, 11, 15, 16] | False | True | 0.006 | -0.117 | — | False | 256 | 14.44 |
| baseline_common_center_scale_mixture_d5_p24_seed5119_search6101 | moment_best | [13, 14, 20] | False | True | -0.047 | -0.086 | — | False | 256 | 14.53 |
| baseline_common_center_scale_mixture_d5_p24_seed5119_search6101 | kernel_best | [5, 6, 9, 10, 11, 14, 15, 16, 18, 21] | False | True | -0.033 | -0.207 | — | False | 256 | 13.74 |
| baseline_common_center_scale_mixture_d5_p24_seed5119_search6113 | moment_best | [2, 3, 5, 7, 11, 12, 13, 14, 19] | False | True | -0.020 | -0.148 | — | False | 256 | 14.26 |
| baseline_common_center_scale_mixture_d5_p24_seed5119_search6113 | kernel_best | [2, 3, 5, 7, 11, 12, 13, 14, 19] | False | True | -0.020 | -0.148 | — | False | 256 | 14.32 |
| baseline_mean_shift_d3_p24_seed5101_search6101 | moment_best | [6, 8, 10, 13, 15, 23] | False | False | 0.070 | 0.044 | 0.004 | False | 256 | 16.25 |
| baseline_mean_shift_d3_p24_seed5101_search6101 | kernel_best | [1, 3, 5, 8, 12, 14, 19, 20, 21, 22] | False | False | 0.077 | 0.042 | -0.000 | False | 256 | 17.72 |
| baseline_mean_shift_d3_p24_seed5101_search6113 | moment_best | [9, 11, 13, 15, 18, 22] | False | False | 0.065 | 0.033 | -0.004 | False | 256 | 16.57 |
| baseline_mean_shift_d3_p24_seed5101_search6113 | kernel_best | [1, 3, 5, 8, 12, 14, 19, 20, 21, 22] | False | False | 0.077 | 0.042 | -0.000 | False | 256 | 17.53 |
| baseline_mean_shift_d3_p24_seed5113_search6101 | moment_best | [2, 3, 4, 5, 6, 7, 10, 11, 17, 19] | False | False | 0.079 | 0.061 | -0.000 | False | 256 | 17.84 |
| baseline_mean_shift_d3_p24_seed5113_search6101 | kernel_best | [2, 4, 6, 8, 10, 12, 17, 18, 19, 21] | False | False | 0.076 | 0.050 | 0.000 | False | 256 | 17.77 |
| baseline_mean_shift_d3_p24_seed5113_search6113 | moment_best | [2, 3, 4, 5, 6, 7, 10, 17, 19, 22] | False | False | 0.078 | 0.067 | -0.000 | False | 256 | 17.90 |
| baseline_mean_shift_d3_p24_seed5113_search6113 | kernel_best | [2, 4, 6, 8, 10, 12, 17, 18, 19, 21] | False | False | 0.076 | 0.050 | 0.000 | False | 256 | 18.01 |
| baseline_mean_shift_d3_p24_seed5119_search6101 | moment_best | [1, 2, 4, 10, 14, 15, 17, 22] | False | False | 0.068 | 0.045 | -0.000 | False | 256 | 18.24 |
| baseline_mean_shift_d3_p24_seed5119_search6101 | kernel_best | [1, 4, 6, 7, 10, 13, 14, 16, 22] | False | False | 0.081 | 0.060 | 0.001 | False | 256 | 18.19 |
| baseline_mean_shift_d3_p24_seed5119_search6113 | moment_best | [1, 2, 4, 10, 14, 15, 17, 22] | False | False | 0.068 | 0.045 | -0.000 | False | 256 | 18.40 |
| baseline_mean_shift_d3_p24_seed5119_search6113 | kernel_best | [1, 4, 6, 7, 10, 13, 14, 16, 22] | False | False | 0.081 | 0.060 | 0.001 | False | 256 | 18.22 |
| more_nuisance_shells_d4_p72_seed5101_search6101 | moment_best | [16, 30, 54] | False | False | 0.023 | -0.018 | -0.001 | False | 256 | 14.44 |
| more_nuisance_shells_d4_p72_seed5101_search6101 | kernel_best | [12, 52, 53, 61] | True | True | 0.784 | 0.768 | 1.000 | True | 256 | 12.65 |
| more_nuisance_shells_d4_p72_seed5101_search6113 | moment_best | [5, 40] | False | False | 0.021 | -0.017 | 0.000 | False | 256 | 14.26 |
| more_nuisance_shells_d4_p72_seed5101_search6113 | kernel_best | [12, 43, 52, 53, 61] | False | False | 0.287 | 0.234 | 0.846 | True | 256 | 13.24 |
| more_nuisance_shells_d4_p72_seed5113_search6101 | moment_best | [31, 71] | False | False | 0.018 | -0.011 | 0.003 | False | 256 | 14.32 |
| more_nuisance_shells_d4_p72_seed5113_search6101 | kernel_best | [27, 46, 50, 67] | False | False | 0.104 | 0.069 | 0.475 | False | 256 | 13.55 |
| more_nuisance_shells_d4_p72_seed5113_search6113 | moment_best | [10, 12] | False | False | 0.024 | -0.019 | 0.010 | False | 256 | 14.29 |
| more_nuisance_shells_d4_p72_seed5113_search6113 | kernel_best | [29, 46, 50, 67] | True | True | 0.695 | 0.739 | 1.000 | True | 256 | 12.82 |
| more_nuisance_shells_d4_p72_seed5119_search6101 | moment_best | [28, 56] | False | False | 0.018 | -0.003 | 0.000 | False | 256 | 13.97 |
| more_nuisance_shells_d4_p72_seed5119_search6101 | kernel_best | [9, 22, 57, 59] | True | True | 0.689 | 0.686 | 1.000 | True | 256 | 12.84 |
| more_nuisance_shells_d4_p72_seed5119_search6113 | moment_best | [23, 31] | False | False | 0.013 | -0.047 | -0.001 | False | 256 | 14.03 |
| more_nuisance_shells_d4_p72_seed5119_search6113 | kernel_best | [9, 57, 59] | False | False | 0.265 | 0.220 | 0.582 | True | 256 | 13.77 |
| more_nuisance_shells_d5_p72_seed5101_search6101 | moment_best | [19, 61] | False | False | 0.011 | -0.023 | 0.059 | False | 256 | 13.68 |
| more_nuisance_shells_d5_p72_seed5101_search6101 | kernel_best | [4, 12, 52, 53, 61] | True | True | 0.766 | 0.803 | 1.000 | True | 256 | 12.57 |
| more_nuisance_shells_d5_p72_seed5101_search6113 | moment_best | [31, 35] | False | False | 0.011 | -0.020 | -0.003 | False | 256 | 13.58 |
| more_nuisance_shells_d5_p72_seed5101_search6113 | kernel_best | [4, 12, 52, 53, 61] | True | True | 0.766 | 0.803 | 1.000 | True | 256 | 12.61 |
| more_nuisance_shells_d5_p72_seed5113_search6101 | moment_best | [28, 32, 49] | False | False | 0.015 | -0.011 | -0.000 | False | 256 | 13.81 |
| more_nuisance_shells_d5_p72_seed5113_search6101 | kernel_best | [29, 46, 50, 51, 56, 67] | False | False | 0.385 | 0.333 | 0.915 | True | 256 | 13.41 |
| more_nuisance_shells_d5_p72_seed5113_search6113 | moment_best | [0, 4] | False | False | 0.011 | 0.000 | -0.000 | False | 256 | 13.75 |
| more_nuisance_shells_d5_p72_seed5113_search6113 | kernel_best | [29, 46, 50, 51, 67] | True | True | 0.827 | 0.852 | 1.000 | True | 256 | 12.79 |
| more_nuisance_shells_d5_p72_seed5119_search6101 | moment_best | [28, 30] | False | False | 0.013 | -0.003 | -0.001 | False | 256 | 13.46 |
| more_nuisance_shells_d5_p72_seed5119_search6101 | kernel_best | [9, 22, 55, 57, 59] | True | True | 0.732 | 0.775 | 1.000 | True | 256 | 12.44 |
| more_nuisance_shells_d5_p72_seed5119_search6113 | moment_best | [13, 27] | False | False | 0.009 | -0.052 | -0.001 | False | 256 | 13.52 |
| more_nuisance_shells_d5_p72_seed5119_search6113 | kernel_best | [9, 22, 55, 57, 59] | True | True | 0.732 | 0.775 | 1.000 | True | 256 | 12.55 |
| more_nuisance_shells_d8_p72_seed5101_search6101 | moment_best | [4, 52, 53, 61] | False | False | 0.110 | 0.092 | 0.328 | False | 256 | 14.50 |
| more_nuisance_shells_d8_p72_seed5101_search6101 | kernel_best | [4, 12, 16, 29, 30, 52, 53, 61] | True | True | 1.173 | 1.202 | 1.000 | True | 256 | 12.95 |
| more_nuisance_shells_d8_p72_seed5101_search6113 | moment_best | [29, 53, 61] | False | False | 0.042 | 0.025 | 0.233 | False | 256 | 13.40 |
| more_nuisance_shells_d8_p72_seed5101_search6113 | kernel_best | [12, 16, 29, 30, 52, 53, 61] | False | False | 0.706 | 0.707 | 0.883 | True | 256 | 13.05 |
| more_nuisance_shells_d8_p72_seed5113_search6101 | moment_best | [1, 3, 20, 29, 46, 50, 51, 67] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 12.37 |
| more_nuisance_shells_d8_p72_seed5113_search6101 | kernel_best | [1, 3, 20, 29, 46, 50, 51, 67] | True | True | 1.137 | 1.126 | 1.000 | True | 256 | 13.15 |
| more_nuisance_shells_d8_p72_seed5113_search6113 | moment_best | [1, 3, 20, 29, 32, 46, 50, 51, 67] | False | False | 0.750 | 0.779 | 0.947 | True | 256 | 12.69 |
| more_nuisance_shells_d8_p72_seed5113_search6113 | kernel_best | [1, 3, 16, 20, 29, 46, 50, 51, 67] | False | False | 0.790 | 0.711 | 0.967 | True | 256 | 13.38 |
| more_nuisance_shells_d8_p72_seed5119_search6101 | moment_best | [9, 13, 22, 25, 26, 55, 57, 59] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 12.81 |
| more_nuisance_shells_d8_p72_seed5119_search6101 | kernel_best | [9, 13, 22, 25, 26, 55, 57, 59] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 13.44 |
| more_nuisance_shells_d8_p72_seed5119_search6113 | moment_best | [9, 13, 22, 25, 26, 55, 57, 59] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 12.41 |
| more_nuisance_shells_d8_p72_seed5119_search6113 | kernel_best | [9, 13, 22, 25, 26, 55, 57, 59] | True | True | 1.084 | 1.126 | 1.000 | True | 256 | 13.11 |
| weak_separation_shells_d4_p24_seed5101_search6101 | moment_best | [0, 5, 12, 23] | True | True | 0.162 | 0.164 | 0.666 | False | 256 | 15.36 |
| weak_separation_shells_d4_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 23] | True | True | 0.162 | 0.164 | 0.666 | False | 256 | 15.51 |
| weak_separation_shells_d4_p24_seed5101_search6113 | moment_best | [0, 5, 12, 23] | True | True | 0.162 | 0.164 | 0.666 | False | 256 | 15.91 |
| weak_separation_shells_d4_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 23] | True | True | 0.162 | 0.164 | 0.666 | False | 256 | 16.79 |
| weak_separation_shells_d4_p24_seed5113_search6101 | moment_best | [5, 9, 17, 23] | True | True | 0.155 | 0.155 | 0.608 | False | 256 | 16.69 |
| weak_separation_shells_d4_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 23] | True | True | 0.155 | 0.155 | 0.608 | False | 256 | 15.61 |
| weak_separation_shells_d4_p24_seed5113_search6113 | moment_best | [5, 9, 17, 23] | True | True | 0.155 | 0.155 | 0.608 | False | 256 | 16.57 |
| weak_separation_shells_d4_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 23] | True | True | 0.155 | 0.155 | 0.608 | False | 256 | 16.18 |
| weak_separation_shells_d4_p24_seed5119_search6101 | moment_best | [7, 9, 15, 16] | True | True | 0.146 | 0.123 | 0.542 | False | 256 | 15.80 |
| weak_separation_shells_d4_p24_seed5119_search6101 | kernel_best | [7, 9, 15, 16] | True | True | 0.146 | 0.123 | 0.542 | False | 256 | 16.49 |
| weak_separation_shells_d4_p24_seed5119_search6113 | moment_best | [7, 9, 15, 16] | True | True | 0.146 | 0.123 | 0.542 | False | 256 | 16.34 |
| weak_separation_shells_d4_p24_seed5119_search6113 | kernel_best | [7, 9, 15, 16] | True | True | 0.146 | 0.123 | 0.542 | False | 256 | 16.13 |
| weak_separation_shells_d5_p24_seed5101_search6101 | moment_best | [0, 5, 12, 16, 23] | True | True | 0.083 | 0.089 | 0.582 | False | 256 | 15.09 |
| weak_separation_shells_d5_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.083 | 0.089 | 0.582 | False | 256 | 15.56 |
| weak_separation_shells_d5_p24_seed5101_search6113 | moment_best | [0, 5, 12, 16, 23] | True | True | 0.083 | 0.089 | 0.582 | False | 256 | 15.28 |
| weak_separation_shells_d5_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.083 | 0.089 | 0.582 | False | 256 | 15.67 |
| weak_separation_shells_d5_p24_seed5113_search6101 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.097 | 0.112 | 0.562 | False | 256 | 15.74 |
| weak_separation_shells_d5_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.097 | 0.112 | 0.562 | False | 256 | 15.60 |
| weak_separation_shells_d5_p24_seed5113_search6113 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.097 | 0.112 | 0.562 | False | 256 | 15.81 |
| weak_separation_shells_d5_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.097 | 0.112 | 0.562 | False | 256 | 15.86 |
| weak_separation_shells_d5_p24_seed5119_search6101 | moment_best | [5, 7, 9, 15, 16] | True | True | 0.074 | 0.081 | 0.503 | False | 256 | 14.95 |
| weak_separation_shells_d5_p24_seed5119_search6101 | kernel_best | [5, 7, 9, 15, 16, 19] | False | False | 0.059 | 0.058 | 0.331 | False | 256 | 16.30 |
| weak_separation_shells_d5_p24_seed5119_search6113 | moment_best | [5, 7, 9, 15, 16] | True | True | 0.074 | 0.081 | 0.503 | False | 256 | 15.12 |
| weak_separation_shells_d5_p24_seed5119_search6113 | kernel_best | [5, 7, 9, 15, 16, 19] | False | False | 0.059 | 0.058 | 0.331 | False | 256 | 16.39 |
| weak_separation_shells_d8_p24_seed5101_search6101 | moment_best | [5, 6, 8, 14, 17, 22, 23] | False | False | 0.007 | -0.010 | 0.027 | False | 256 | 14.46 |
| weak_separation_shells_d8_p24_seed5101_search6101 | kernel_best | [5, 7, 10, 15, 17, 21] | False | False | 0.011 | -0.014 | 0.133 | False | 256 | 14.43 |
| weak_separation_shells_d8_p24_seed5101_search6113 | moment_best | [5, 6, 8, 14, 17, 22, 23] | False | False | 0.007 | -0.010 | 0.027 | False | 256 | 14.47 |
| weak_separation_shells_d8_p24_seed5101_search6113 | kernel_best | [5, 7, 10, 15, 17, 21] | False | False | 0.011 | -0.014 | 0.133 | False | 256 | 14.42 |
| weak_separation_shells_d8_p24_seed5113_search6101 | moment_best | [6, 17, 18, 21] | False | False | 0.012 | -0.021 | 0.063 | False | 256 | 14.12 |
| weak_separation_shells_d8_p24_seed5113_search6101 | kernel_best | [1, 3, 5, 9, 13, 15, 17, 18, 23] | False | False | 0.023 | 0.007 | 0.159 | False | 256 | 15.62 |
| weak_separation_shells_d8_p24_seed5113_search6113 | moment_best | [6, 17, 18, 21] | False | False | 0.012 | -0.021 | 0.063 | False | 256 | 14.26 |
| weak_separation_shells_d8_p24_seed5113_search6113 | kernel_best | [1, 3, 5, 9, 15, 16, 17, 18, 23] | False | False | 0.024 | 0.003 | 0.089 | False | 256 | 15.45 |
| weak_separation_shells_d8_p24_seed5119_search6101 | moment_best | [2, 6, 9, 13, 19, 22] | False | False | 0.016 | -0.017 | 0.028 | False | 256 | 14.26 |
| weak_separation_shells_d8_p24_seed5119_search6101 | kernel_best | [4, 16, 17] | False | False | 0.008 | -0.026 | 0.038 | False | 256 | 15.27 |
| weak_separation_shells_d8_p24_seed5119_search6113 | moment_best | [2, 6, 9, 13, 19, 22] | False | False | 0.016 | -0.017 | 0.028 | False | 256 | 14.23 |
| weak_separation_shells_d8_p24_seed5119_search6113 | kernel_best | [4, 16, 17] | False | False | 0.008 | -0.026 | 0.038 | False | 256 | 15.23 |
| dependent_nuisance_shells_d4_p24_seed5101_search6101 | moment_best | [0, 12, 23] | False | False | 0.300 | 0.222 | 0.666 | True | 256 | 13.67 |
| dependent_nuisance_shells_d4_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 23] | True | True | 0.783 | 0.768 | 1.000 | True | 256 | 12.39 |
| dependent_nuisance_shells_d4_p24_seed5101_search6113 | moment_best | [0, 12, 23] | False | False | 0.300 | 0.222 | 0.666 | True | 256 | 13.76 |
| dependent_nuisance_shells_d4_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 23] | True | True | 0.783 | 0.768 | 1.000 | True | 256 | 12.44 |
| dependent_nuisance_shells_d4_p24_seed5113_search6101 | moment_best | [4, 6, 7, 11, 16, 19, 22, 23] | False | False | 0.024 | -0.025 | 0.014 | False | 256 | 13.80 |
| dependent_nuisance_shells_d4_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 23] | True | True | 0.705 | 0.747 | 1.000 | True | 256 | 12.54 |
| dependent_nuisance_shells_d4_p24_seed5113_search6113 | moment_best | [4, 6, 7, 11, 16, 19, 22, 23] | False | False | 0.024 | -0.025 | 0.014 | False | 256 | 13.93 |
| dependent_nuisance_shells_d4_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 23] | True | True | 0.705 | 0.747 | 1.000 | True | 256 | 12.46 |
| dependent_nuisance_shells_d4_p24_seed5119_search6101 | moment_best | [7, 16] | False | False | 0.084 | 0.091 | 0.312 | True | 256 | 14.38 |
| dependent_nuisance_shells_d4_p24_seed5119_search6101 | kernel_best | [7, 9, 15, 16] | True | True | 0.696 | 0.684 | 1.000 | True | 256 | 12.54 |
| dependent_nuisance_shells_d4_p24_seed5119_search6113 | moment_best | [6, 7, 8, 9, 17, 18, 19, 20] | False | False | 0.033 | -0.007 | 0.030 | False | 256 | 13.80 |
| dependent_nuisance_shells_d4_p24_seed5119_search6113 | kernel_best | [7, 9, 15, 16] | True | True | 0.696 | 0.684 | 1.000 | True | 256 | 12.56 |
| dependent_nuisance_shells_d5_p24_seed5101_search6101 | moment_best | [5, 12, 16, 23] | False | False | 0.310 | 0.324 | 0.834 | True | 256 | 13.65 |
| dependent_nuisance_shells_d5_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.781 | 0.808 | 1.000 | True | 256 | 12.03 |
| dependent_nuisance_shells_d5_p24_seed5101_search6113 | moment_best | [5, 12, 16, 23] | False | False | 0.310 | 0.324 | 0.834 | True | 256 | 13.63 |
| dependent_nuisance_shells_d5_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 16, 23] | True | True | 0.781 | 0.808 | 1.000 | True | 256 | 12.29 |
| dependent_nuisance_shells_d5_p24_seed5113_search6101 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.839 | 0.860 | 1.000 | True | 256 | 12.37 |
| dependent_nuisance_shells_d5_p24_seed5113_search6101 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.839 | 0.860 | 1.000 | True | 256 | 12.13 |
| dependent_nuisance_shells_d5_p24_seed5113_search6113 | moment_best | [5, 9, 17, 18, 23] | True | True | 0.839 | 0.860 | 1.000 | True | 256 | 12.45 |
| dependent_nuisance_shells_d5_p24_seed5113_search6113 | kernel_best | [5, 9, 17, 18, 23] | True | True | 0.839 | 0.860 | 1.000 | True | 256 | 12.09 |
| dependent_nuisance_shells_d5_p24_seed5119_search6101 | moment_best | [5, 7, 9, 15, 16] | True | True | 0.741 | 0.781 | 1.000 | True | 256 | 12.69 |
| dependent_nuisance_shells_d5_p24_seed5119_search6101 | kernel_best | [5, 7, 9, 15, 16] | True | True | 0.741 | 0.781 | 1.000 | True | 256 | 11.96 |
| dependent_nuisance_shells_d5_p24_seed5119_search6113 | moment_best | [5, 7, 9, 15, 16] | True | True | 0.741 | 0.781 | 1.000 | True | 256 | 12.68 |
| dependent_nuisance_shells_d5_p24_seed5119_search6113 | kernel_best | [5, 7, 9, 15, 16] | True | True | 0.741 | 0.781 | 1.000 | True | 256 | 11.90 |
| dependent_nuisance_shells_d8_p24_seed5101_search6101 | moment_best | [0, 5, 12, 15, 17, 23] | False | False | 0.422 | 0.377 | 0.739 | True | 256 | 12.47 |
| dependent_nuisance_shells_d8_p24_seed5101_search6101 | kernel_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.194 | 1.209 | 1.000 | True | 256 | 12.49 |
| dependent_nuisance_shells_d8_p24_seed5101_search6113 | moment_best | [0, 5, 12, 15, 16, 23] | False | False | 0.419 | 0.397 | 0.733 | True | 256 | 12.53 |
| dependent_nuisance_shells_d8_p24_seed5101_search6113 | kernel_best | [0, 5, 12, 15, 16, 17, 21, 23] | True | True | 1.194 | 1.209 | 1.000 | True | 256 | 12.56 |
| dependent_nuisance_shells_d8_p24_seed5113_search6101 | moment_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.170 | 1.155 | 1.000 | True | 256 | 12.24 |
| dependent_nuisance_shells_d8_p24_seed5113_search6101 | kernel_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.170 | 1.155 | 1.000 | True | 256 | 12.69 |
| dependent_nuisance_shells_d8_p24_seed5113_search6113 | moment_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.170 | 1.155 | 1.000 | True | 256 | 12.26 |
| dependent_nuisance_shells_d8_p24_seed5113_search6113 | kernel_best | [1, 5, 9, 17, 18, 20, 21, 23] | True | True | 1.170 | 1.155 | 1.000 | True | 256 | 12.56 |
| dependent_nuisance_shells_d8_p24_seed5119_search6101 | moment_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.129 | 1.167 | 1.000 | True | 256 | 12.03 |
| dependent_nuisance_shells_d8_p24_seed5119_search6101 | kernel_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.129 | 1.167 | 1.000 | True | 256 | 12.28 |
| dependent_nuisance_shells_d8_p24_seed5119_search6113 | moment_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.129 | 1.167 | 1.000 | True | 256 | 12.01 |
| dependent_nuisance_shells_d8_p24_seed5119_search6113 | kernel_best | [4, 5, 7, 9, 14, 15, 16, 22] | True | True | 1.129 | 1.167 | 1.000 | True | 256 | 12.36 |
