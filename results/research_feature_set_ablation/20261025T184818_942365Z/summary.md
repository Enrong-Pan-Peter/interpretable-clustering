# Interpretable feature-set search

Controlled 2x2 development comparison: squared-correlation versus nonlinear kernel proposals, crossed with best-improvement versus first-improvement refinement. Every arm has the same unique-fit budget, model, fitness, size cap and initial random candidates. For a given dependence statistic, both refinement variants share all exploration candidates.

Raw data are copied byte-for-byte from the audited preceding pilot; their hashes and original metadata are retained. These previously inspected validation/test blocks are reused development evidence, not fresh confirmation. Kernel similarities use fitting observations only; the original-feature assignment rule is unchanged. Kernel preprocessing costs and optimizer status are recorded separately from unique fit counts.

Models fit on fit rows; adaptive search and final feature-set choice use search rows. Validation and test are excluded from this selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Feature set | Exact support | Oracle visited | Search gain | Val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| shells_d2_p24_seed2401_search3203 | moment_best | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 15.84 |
| shells_d2_p24_seed2401_search3203 | moment_first | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 15.87 |
| shells_d2_p24_seed2401_search3203 | kernel_best | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 15.97 |
| shells_d2_p24_seed2401_search3203 | kernel_first | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 16.42 |
| shells_d3_p24_seed2401_search3203 | moment_best | [0, 1, 10] | True | True | 0.756 | 0.771 | 1.000 | True | 256 | 14.00 |
| shells_d3_p24_seed2401_search3203 | moment_first | [0, 1, 10] | True | True | 0.756 | 0.771 | 1.000 | True | 256 | 13.88 |
| shells_d3_p24_seed2401_search3203 | kernel_best | [0, 1, 10] | True | True | 0.756 | 0.771 | 1.000 | True | 256 | 13.69 |
| shells_d3_p24_seed2401_search3203 | kernel_first | [0, 1, 10] | True | True | 0.756 | 0.771 | 1.000 | True | 256 | 14.02 |
| shells_d4_p24_seed2401_search3203 | moment_best | [1, 10, 12] | False | False | 0.271 | 0.300 | 0.661 | True | 256 | 13.71 |
| shells_d4_p24_seed2401_search3203 | moment_first | [0, 1, 10, 12] | True | True | 0.813 | 0.746 | 1.000 | True | 256 | 12.71 |
| shells_d4_p24_seed2401_search3203 | kernel_best | [0, 1, 10, 12] | True | True | 0.813 | 0.746 | 1.000 | True | 256 | 12.66 |
| shells_d4_p24_seed2401_search3203 | kernel_first | [0, 1, 10, 12] | True | True | 0.813 | 0.746 | 1.000 | True | 256 | 12.66 |
| shells_d5_p24_seed2401_search3203 | moment_best | [0, 1, 9, 10] | False | False | 0.350 | 0.330 | 0.810 | True | 256 | 12.94 |
| shells_d5_p24_seed2401_search3203 | moment_first | [0, 1, 9, 10, 12] | True | True | 0.867 | 0.869 | 1.000 | True | 256 | 12.20 |
| shells_d5_p24_seed2401_search3203 | kernel_best | [0, 1, 9, 10, 12] | True | True | 0.867 | 0.869 | 1.000 | True | 256 | 11.91 |
| shells_d5_p24_seed2401_search3203 | kernel_first | [0, 1, 9, 10, 12] | True | True | 0.867 | 0.869 | 1.000 | True | 256 | 11.83 |
| shells_d8_p24_seed2401_search3203 | moment_best | [0, 1, 2, 9, 10, 12, 17, 23] | True | True | 1.213 | 1.101 | 1.000 | True | 256 | 11.88 |
| shells_d8_p24_seed2401_search3203 | moment_first | [0, 1, 2, 9, 10, 12, 17, 23] | True | True | 1.213 | 1.101 | 1.000 | True | 256 | 11.80 |
| shells_d8_p24_seed2401_search3203 | kernel_best | [0, 1, 2, 9, 10, 12, 17, 23] | True | True | 1.213 | 1.101 | 1.000 | True | 256 | 12.15 |
| shells_d8_p24_seed2401_search3203 | kernel_first | [0, 1, 2, 9, 10, 12, 17, 23] | True | True | 1.213 | 1.101 | 1.000 | True | 256 | 12.20 |
| single_shell_d2_p24_seed2401_search3203 | moment_best | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 15.77 |
| single_shell_d2_p24_seed2401_search3203 | moment_first | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 16.32 |
| single_shell_d2_p24_seed2401_search3203 | kernel_best | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 16.38 |
| single_shell_d2_p24_seed2401_search3203 | kernel_first | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 15.95 |
| single_shell_d5_p24_seed2401_search3203 | moment_best | [0, 1, 9, 10, 12] | True | True | 1.137 | 1.104 | — | False | 256 | 18.05 |
| single_shell_d5_p24_seed2401_search3203 | moment_first | [0, 1, 9, 10, 12] | True | True | 1.137 | 1.104 | — | False | 256 | 17.89 |
| single_shell_d5_p24_seed2401_search3203 | kernel_best | [0, 1, 9, 10, 12] | True | True | 1.137 | 1.104 | — | False | 256 | 18.81 |
| single_shell_d5_p24_seed2401_search3203 | kernel_first | [0, 1, 9, 10, 12] | True | True | 1.137 | 1.104 | — | False | 256 | 18.69 |
| independent_gaussian_d5_p24_seed2401_search3203 | moment_best | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 15.04 |
| independent_gaussian_d5_p24_seed2401_search3203 | moment_first | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 15.12 |
| independent_gaussian_d5_p24_seed2401_search3203 | kernel_best | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 15.12 |
| independent_gaussian_d5_p24_seed2401_search3203 | kernel_first | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 15.06 |
| correlated_gaussian_d5_p24_seed2401_search3203 | moment_best | [0, 2, 3, 4, 5, 16, 17, 18] | False | True | 0.031 | -0.023 | — | False | 256 | 15.18 |
| correlated_gaussian_d5_p24_seed2401_search3203 | moment_first | [0, 4, 7, 11, 13, 15, 18, 20, 21] | False | True | 0.065 | 0.012 | — | False | 256 | 15.16 |
| correlated_gaussian_d5_p24_seed2401_search3203 | kernel_best | [0, 2, 4, 13, 18] | False | True | 0.022 | -0.040 | — | False | 256 | 15.42 |
| correlated_gaussian_d5_p24_seed2401_search3203 | kernel_first | [0, 2, 13, 16, 18, 19] | False | True | 0.027 | -0.022 | — | False | 256 | 15.24 |
| student_t_d5_p24_seed2401_search3203 | moment_best | [2, 7, 10, 19] | False | True | -0.027 | -0.848 | — | False | 256 | 14.91 |
| student_t_d5_p24_seed2401_search3203 | moment_first | [2, 7, 10, 19] | False | True | -0.027 | -0.848 | — | False | 256 | 14.99 |
| student_t_d5_p24_seed2401_search3203 | kernel_best | [2, 7, 10, 19] | False | True | -0.027 | -0.848 | — | False | 256 | 14.24 |
| student_t_d5_p24_seed2401_search3203 | kernel_first | [2, 7, 10, 19] | False | True | -0.027 | -0.848 | — | False | 256 | 15.10 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | moment_best | [2, 21] | False | True | -0.045 | -0.100 | — | False | 256 | 12.97 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | moment_first | [2, 21] | False | True | -0.045 | -0.100 | — | False | 256 | 13.81 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | kernel_best | [2, 21] | False | True | -0.045 | -0.100 | — | False | 256 | 13.22 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | kernel_first | [2, 21] | False | True | -0.045 | -0.100 | — | False | 256 | 14.04 |
| mean_shift_d3_p24_seed2401_search3203 | moment_best | [10, 11, 14, 16, 17, 21, 22] | False | False | 0.062 | 0.048 | 0.000 | False | 256 | 17.34 |
| mean_shift_d3_p24_seed2401_search3203 | moment_first | [2, 4, 5, 7, 8, 9, 11, 12, 17, 19] | False | False | 0.096 | 0.061 | 0.003 | False | 256 | 17.83 |
| mean_shift_d3_p24_seed2401_search3203 | kernel_best | [2, 5, 7, 9, 10, 11, 16, 17, 19, 21] | False | False | 0.073 | 0.052 | -0.001 | False | 256 | 18.48 |
| mean_shift_d3_p24_seed2401_search3203 | kernel_first | [2, 4, 5, 7, 8, 11, 13, 14, 16, 17] | False | False | 0.101 | 0.019 | -0.000 | False | 256 | 18.92 |
| shells_d2_p24_seed2411_search3217 | moment_best | [8, 16] | True | True | 0.557 | 0.599 | 1.000 | True | 256 | 15.79 |
| shells_d2_p24_seed2411_search3217 | moment_first | [8, 16] | True | True | 0.557 | 0.599 | 1.000 | True | 256 | 15.81 |
| shells_d2_p24_seed2411_search3217 | kernel_best | [8, 16] | True | True | 0.557 | 0.599 | 1.000 | True | 256 | 15.90 |
| shells_d2_p24_seed2411_search3217 | kernel_first | [8, 16] | True | True | 0.557 | 0.599 | 1.000 | True | 256 | 16.18 |
| shells_d3_p24_seed2411_search3217 | moment_best | [7, 8, 16] | True | True | 0.765 | 0.687 | 1.000 | True | 256 | 12.74 |
| shells_d3_p24_seed2411_search3217 | moment_first | [7, 8, 16] | True | True | 0.765 | 0.687 | 1.000 | True | 256 | 12.56 |
| shells_d3_p24_seed2411_search3217 | kernel_best | [7, 8, 16] | True | True | 0.765 | 0.687 | 1.000 | True | 256 | 13.57 |
| shells_d3_p24_seed2411_search3217 | kernel_first | [7, 8, 16] | True | True | 0.765 | 0.687 | 1.000 | True | 256 | 14.12 |
| shells_d4_p24_seed2411_search3217 | moment_best | [6, 18] | False | False | 0.029 | 0.006 | -0.002 | False | 256 | 14.21 |
| shells_d4_p24_seed2411_search3217 | moment_first | [6, 18] | False | False | 0.029 | 0.006 | -0.002 | False | 256 | 14.14 |
| shells_d4_p24_seed2411_search3217 | kernel_best | [7, 8, 13, 16] | True | True | 0.739 | 0.745 | 1.000 | True | 256 | 12.36 |
| shells_d4_p24_seed2411_search3217 | kernel_first | [7, 8, 13, 16] | True | True | 0.739 | 0.745 | 1.000 | True | 256 | 12.86 |
| shells_d5_p24_seed2411_search3217 | moment_best | [1, 2, 23] | False | False | 0.005 | -0.040 | -0.001 | False | 256 | 14.15 |
| shells_d5_p24_seed2411_search3217 | moment_first | [6, 7, 8, 13, 16] | True | True | 0.832 | 0.842 | 1.000 | True | 256 | 13.66 |
| shells_d5_p24_seed2411_search3217 | kernel_best | [6, 7, 8, 13, 16] | True | True | 0.832 | 0.842 | 1.000 | True | 256 | 12.18 |
| shells_d5_p24_seed2411_search3217 | kernel_first | [6, 7, 8, 13, 16] | True | True | 0.832 | 0.842 | 1.000 | True | 256 | 12.15 |
| shells_d8_p24_seed2411_search3217 | moment_best | [2, 5, 6, 7, 8, 9, 13, 16] | True | True | 1.130 | 1.191 | 1.000 | True | 256 | 12.09 |
| shells_d8_p24_seed2411_search3217 | moment_first | [2, 5, 6, 7, 8, 9, 13, 16] | True | True | 1.130 | 1.191 | 1.000 | True | 256 | 12.15 |
| shells_d8_p24_seed2411_search3217 | kernel_best | [2, 5, 6, 7, 8, 9, 13, 16] | True | True | 1.130 | 1.191 | 1.000 | True | 256 | 12.17 |
| shells_d8_p24_seed2411_search3217 | kernel_first | [2, 5, 6, 7, 8, 9, 13, 16] | True | True | 1.130 | 1.191 | 1.000 | True | 256 | 12.06 |
| single_shell_d2_p24_seed2411_search3217 | moment_best | [8, 16] | True | True | 1.409 | 1.421 | — | False | 256 | 14.03 |
| single_shell_d2_p24_seed2411_search3217 | moment_first | [8, 16] | True | True | 1.409 | 1.421 | — | False | 256 | 14.09 |
| single_shell_d2_p24_seed2411_search3217 | kernel_best | [8, 16] | True | True | 1.409 | 1.421 | — | False | 256 | 14.80 |
| single_shell_d2_p24_seed2411_search3217 | kernel_first | [8, 16] | True | True | 1.409 | 1.421 | — | False | 256 | 14.90 |
| single_shell_d5_p24_seed2411_search3217 | moment_best | [6, 7, 8, 13, 16] | True | True | 1.071 | 1.147 | — | False | 256 | 18.14 |
| single_shell_d5_p24_seed2411_search3217 | moment_first | [6, 7, 8, 13, 16] | True | True | 1.071 | 1.147 | — | False | 256 | 18.14 |
| single_shell_d5_p24_seed2411_search3217 | kernel_best | [6, 7, 8, 13, 16] | True | True | 1.071 | 1.147 | — | False | 256 | 18.48 |
| single_shell_d5_p24_seed2411_search3217 | kernel_first | [6, 7, 8, 13, 16] | True | True | 1.071 | 1.147 | — | False | 256 | 18.59 |
| independent_gaussian_d5_p24_seed2411_search3217 | moment_best | [3, 5, 6, 8, 9, 12, 16, 17, 20, 22] | False | False | 0.007 | -0.035 | — | False | 256 | 15.32 |
| independent_gaussian_d5_p24_seed2411_search3217 | moment_first | [0, 4, 5, 6, 7, 8, 9, 16, 17, 18] | False | False | 0.009 | -0.025 | — | False | 256 | 15.24 |
| independent_gaussian_d5_p24_seed2411_search3217 | kernel_best | [1, 8, 12, 16, 17, 20, 22, 23] | False | False | -0.005 | -0.035 | — | False | 256 | 15.35 |
| independent_gaussian_d5_p24_seed2411_search3217 | kernel_first | [4, 9, 12, 13, 16, 17, 18, 19, 20] | False | False | 0.012 | -0.020 | — | False | 256 | 15.45 |
| correlated_gaussian_d5_p24_seed2411_search3217 | moment_best | [2, 4, 6, 9, 14, 17, 20] | False | True | 0.035 | -0.020 | — | False | 256 | 14.88 |
| correlated_gaussian_d5_p24_seed2411_search3217 | moment_first | [0, 5, 6, 9, 14, 17, 20] | False | True | 0.041 | -0.065 | — | False | 256 | 14.82 |
| correlated_gaussian_d5_p24_seed2411_search3217 | kernel_best | [4, 5, 8, 9, 11, 12, 17, 18, 23] | False | True | 0.039 | -0.001 | — | False | 256 | 15.21 |
| correlated_gaussian_d5_p24_seed2411_search3217 | kernel_first | [0, 1, 2, 5, 12, 15, 17, 18, 19, 20] | False | True | 0.084 | -0.026 | — | False | 256 | 15.27 |
| student_t_d5_p24_seed2411_search3217 | moment_best | [4, 16] | False | True | -0.043 | -0.361 | — | False | 256 | 13.83 |
| student_t_d5_p24_seed2411_search3217 | moment_first | [5, 16, 19] | False | True | -0.050 | -0.109 | — | False | 256 | 14.48 |
| student_t_d5_p24_seed2411_search3217 | kernel_best | [4, 16] | False | True | -0.043 | -0.361 | — | False | 256 | 13.98 |
| student_t_d5_p24_seed2411_search3217 | kernel_first | [4, 16] | False | True | -0.043 | -0.361 | — | False | 256 | 14.59 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | moment_best | [12, 15, 19, 20] | False | True | -0.028 | -0.124 | — | False | 256 | 13.99 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | moment_first | [0, 3, 9, 12, 13, 19] | False | True | -0.013 | -0.158 | — | False | 256 | 13.89 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | kernel_best | [12, 15, 19, 20, 22] | False | True | -0.022 | -0.098 | — | False | 256 | 14.85 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | kernel_first | [3, 9, 11, 12, 13, 16, 19] | False | True | -0.011 | -0.201 | — | False | 256 | 14.14 |
| mean_shift_d3_p24_seed2411_search3217 | moment_best | [0, 2, 6, 8, 12, 13, 15, 17, 23] | False | False | 0.075 | 0.050 | -0.000 | False | 256 | 17.75 |
| mean_shift_d3_p24_seed2411_search3217 | moment_first | [2, 3, 6, 8, 12, 13, 15, 17, 22, 23] | False | False | 0.087 | 0.033 | -0.000 | False | 256 | 17.69 |
| mean_shift_d3_p24_seed2411_search3217 | kernel_best | [8, 12, 17, 23] | False | False | 0.060 | 0.023 | 0.000 | False | 256 | 16.66 |
| mean_shift_d3_p24_seed2411_search3217 | kernel_first | [2, 3, 6, 8, 13, 18, 22, 23] | False | False | 0.076 | 0.025 | -0.000 | False | 256 | 16.93 |
| shells_d2_p24_seed2423_search3221 | moment_best | [2, 5] | True | True | 0.830 | 0.838 | 1.000 | True | 256 | 13.92 |
| shells_d2_p24_seed2423_search3221 | moment_first | [2, 5] | True | True | 0.830 | 0.838 | 1.000 | True | 256 | 14.07 |
| shells_d2_p24_seed2423_search3221 | kernel_best | [2, 5] | True | True | 0.830 | 0.838 | 1.000 | True | 256 | 13.83 |
| shells_d2_p24_seed2423_search3221 | kernel_first | [2, 5] | True | True | 0.830 | 0.838 | 1.000 | True | 256 | 13.94 |
| shells_d3_p24_seed2423_search3221 | moment_best | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 13.17 |
| shells_d3_p24_seed2423_search3221 | moment_first | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 13.73 |
| shells_d3_p24_seed2423_search3221 | kernel_best | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 14.13 |
| shells_d3_p24_seed2423_search3221 | kernel_first | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 13.71 |
| shells_d4_p24_seed2423_search3221 | moment_best | [2, 5, 10, 18] | True | True | 0.736 | 0.794 | 1.000 | True | 256 | 13.14 |
| shells_d4_p24_seed2423_search3221 | moment_first | [2, 5, 10, 18] | True | True | 0.736 | 0.794 | 1.000 | True | 256 | 12.75 |
| shells_d4_p24_seed2423_search3221 | kernel_best | [2, 5, 10, 18] | True | True | 0.736 | 0.794 | 1.000 | True | 256 | 12.50 |
| shells_d4_p24_seed2423_search3221 | kernel_first | [2, 5, 10, 18] | True | True | 0.736 | 0.794 | 1.000 | True | 256 | 12.48 |
| shells_d5_p24_seed2423_search3221 | moment_best | [9, 14] | False | False | 0.007 | -0.074 | 0.001 | False | 256 | 13.39 |
| shells_d5_p24_seed2423_search3221 | moment_first | [9, 14] | False | False | 0.007 | -0.074 | 0.001 | False | 256 | 13.42 |
| shells_d5_p24_seed2423_search3221 | kernel_best | [2, 5, 7, 10, 18] | True | True | 0.878 | 0.842 | 1.000 | True | 256 | 11.96 |
| shells_d5_p24_seed2423_search3221 | kernel_first | [2, 5, 7, 10, 18] | True | True | 0.878 | 0.842 | 1.000 | True | 256 | 12.12 |
| shells_d8_p24_seed2423_search3221 | moment_best | [2, 5, 7, 8, 10, 12, 15, 18] | True | True | 1.142 | 1.226 | 1.000 | True | 256 | 11.91 |
| shells_d8_p24_seed2423_search3221 | moment_first | [2, 5, 7, 8, 10, 12, 15, 18] | True | True | 1.142 | 1.226 | 1.000 | True | 256 | 11.93 |
| shells_d8_p24_seed2423_search3221 | kernel_best | [2, 5, 7, 8, 10, 12, 15, 18] | True | True | 1.142 | 1.226 | 1.000 | True | 256 | 12.24 |
| shells_d8_p24_seed2423_search3221 | kernel_first | [2, 5, 7, 8, 10, 12, 15, 18] | True | True | 1.142 | 1.226 | 1.000 | True | 256 | 12.17 |
| single_shell_d2_p24_seed2423_search3221 | moment_best | [2, 5] | True | True | 1.685 | 1.696 | — | False | 256 | 15.07 |
| single_shell_d2_p24_seed2423_search3221 | moment_first | [2, 5] | True | True | 1.685 | 1.696 | — | False | 256 | 14.83 |
| single_shell_d2_p24_seed2423_search3221 | kernel_best | [2, 5] | True | True | 1.685 | 1.696 | — | False | 256 | 14.13 |
| single_shell_d2_p24_seed2423_search3221 | kernel_first | [2, 5] | True | True | 1.685 | 1.696 | — | False | 256 | 14.12 |
| single_shell_d5_p24_seed2423_search3221 | moment_best | [2, 5, 7, 10, 18] | True | True | 1.106 | 1.214 | — | False | 256 | 17.17 |
| single_shell_d5_p24_seed2423_search3221 | moment_first | [2, 5, 7, 10, 18] | True | True | 1.106 | 1.214 | — | False | 256 | 17.36 |
| single_shell_d5_p24_seed2423_search3221 | kernel_best | [2, 5, 7, 10, 18] | True | True | 1.106 | 1.214 | — | False | 256 | 18.11 |
| single_shell_d5_p24_seed2423_search3221 | kernel_first | [2, 5, 7, 10, 18] | True | True | 1.106 | 1.214 | — | False | 256 | 18.20 |
| independent_gaussian_d5_p24_seed2423_search3221 | moment_best | [6, 7, 16, 20, 23] | False | False | 0.005 | -0.033 | — | False | 256 | 14.88 |
| independent_gaussian_d5_p24_seed2423_search3221 | moment_first | [6, 7, 16, 18, 20, 23] | False | False | 0.005 | -0.016 | — | False | 256 | 14.90 |
| independent_gaussian_d5_p24_seed2423_search3221 | kernel_best | [0, 4, 7, 18] | False | False | -0.002 | -0.067 | — | False | 256 | 15.22 |
| independent_gaussian_d5_p24_seed2423_search3221 | kernel_first | [7, 10, 22] | False | False | -0.002 | -0.077 | — | False | 256 | 15.00 |
| correlated_gaussian_d5_p24_seed2423_search3221 | moment_best | [3, 4, 6, 9, 13, 14, 16, 21] | False | True | 0.036 | 0.019 | — | False | 256 | 14.90 |
| correlated_gaussian_d5_p24_seed2423_search3221 | moment_first | [4, 6, 8, 9, 11, 13, 14, 19, 21, 23] | False | True | 0.053 | 0.034 | — | False | 256 | 15.00 |
| correlated_gaussian_d5_p24_seed2423_search3221 | kernel_best | [9, 11, 12, 13, 14, 16, 17, 19, 22, 23] | False | True | 0.047 | 0.006 | — | False | 256 | 15.38 |
| correlated_gaussian_d5_p24_seed2423_search3221 | kernel_first | [9, 11, 12, 13, 14, 15, 17, 20, 22, 23] | False | True | 0.078 | 0.012 | — | False | 256 | 15.49 |
| student_t_d5_p24_seed2423_search3221 | moment_best | [21, 23] | False | True | -0.094 | -0.601 | — | False | 256 | 14.06 |
| student_t_d5_p24_seed2423_search3221 | moment_first | [5, 6, 19, 22] | False | True | -0.092 | -0.130 | — | False | 256 | 13.80 |
| student_t_d5_p24_seed2423_search3221 | kernel_best | [6, 9, 19, 22] | False | True | -0.088 | -0.102 | — | False | 256 | 14.04 |
| student_t_d5_p24_seed2423_search3221 | kernel_first | [5, 6, 9, 19, 22] | False | True | -0.083 | -0.103 | — | False | 256 | 15.19 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | moment_best | [0, 2, 8, 9, 11, 18, 21, 22] | False | True | -0.044 | -0.311 | — | False | 256 | 13.49 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | moment_first | [0, 2, 4, 8, 9, 16, 20, 22] | False | True | -0.024 | -0.162 | — | False | 256 | 13.70 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | kernel_best | [0, 2, 4, 8, 20] | False | True | -0.030 | -0.124 | — | False | 256 | 14.82 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | kernel_first | [0, 2, 8, 18, 20, 21] | False | True | -0.029 | -0.213 | — | False | 256 | 14.13 |
| mean_shift_d3_p24_seed2423_search3221 | moment_best | [1, 2, 7, 12, 13, 15, 16, 18, 19, 21] | False | False | 0.106 | 0.057 | -0.002 | False | 256 | 17.90 |
| mean_shift_d3_p24_seed2423_search3221 | moment_first | [1, 2, 4, 7, 12, 13, 16, 17, 20, 21] | False | False | 0.120 | 0.054 | -0.002 | False | 256 | 18.06 |
| mean_shift_d3_p24_seed2423_search3221 | kernel_best | [2, 3, 4, 7, 12, 13, 15, 19, 20] | False | False | 0.090 | 0.033 | -0.003 | False | 256 | 18.68 |
| mean_shift_d3_p24_seed2423_search3221 | kernel_first | [1, 2, 3, 9, 11, 12, 13, 18, 20, 22] | False | False | 0.096 | 0.065 | -0.002 | False | 256 | 19.13 |
