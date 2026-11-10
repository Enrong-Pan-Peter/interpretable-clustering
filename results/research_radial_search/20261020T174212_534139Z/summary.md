# Hidden-panel radial search

Development comparison: all arms have equal unique radial-panel fits, the same size cap, and no supplied support. Random/local and dependence/local use half their budget for proposals and the remainder for identical add/drop/swap refinement. The dependence proposal uses fit-only absolute squared-coordinate correlation; its extra preprocessing and wall time are recorded.

Shuffled-dependence local search permutes the feature identities of the dependence matrix before building the same chains. It preserves the matrix values and proposal procedure while breaking their association with the measurements. Evaluated size histograms are saved for every arm. The ordinary random/local comparison alone does not isolate the statistic from chain structure.

Models fit on fit rows; adaptive search and final panel choice use search rows. Validation and test are independent of panel selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Panel | Exact support | Oracle visited | Search gain | Fresh val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| shells_d2_p24_seed2401_search3203 | random | [6] | False | False | 0.151 | 0.094 | -0.002 | True | 256 | 17.54 |
| shells_d2_p24_seed2401_search3203 | random_local | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 14.33 |
| shells_d2_p24_seed2401_search3203 | dependence_local | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 14.72 |
| shells_d2_p24_seed2401_search3203 | shuffled_dependence_local | [0, 10] | True | True | 0.807 | 0.774 | 1.000 | True | 256 | 14.66 |
| shells_d3_p24_seed2401_search3203 | random | [17] | False | False | 0.048 | 0.031 | -0.001 | False | 256 | 14.96 |
| shells_d3_p24_seed2401_search3203 | random_local | [0, 1, 7, 10] | False | False | 0.220 | 0.184 | 0.804 | False | 256 | 14.21 |
| shells_d3_p24_seed2401_search3203 | dependence_local | [0, 1, 10] | True | True | 0.756 | 0.771 | 1.000 | True | 256 | 14.32 |
| shells_d3_p24_seed2401_search3203 | shuffled_dependence_local | [17] | False | False | 0.048 | 0.031 | -0.001 | False | 256 | 15.96 |
| shells_d4_p24_seed2401_search3203 | random | [1, 19] | False | False | 0.026 | -0.046 | 0.021 | False | 256 | 13.98 |
| shells_d4_p24_seed2401_search3203 | random_local | [0, 1, 10, 12] | True | True | 0.813 | 0.746 | 1.000 | True | 256 | 13.32 |
| shells_d4_p24_seed2401_search3203 | dependence_local | [1, 10, 12] | False | False | 0.271 | 0.300 | 0.661 | True | 256 | 13.75 |
| shells_d4_p24_seed2401_search3203 | shuffled_dependence_local | [0, 1, 10] | False | False | 0.299 | 0.271 | 0.634 | True | 256 | 13.93 |
| shells_d5_p24_seed2401_search3203 | random | [11, 13, 17] | False | False | -0.005 | -0.049 | -0.001 | False | 256 | 13.47 |
| shells_d5_p24_seed2401_search3203 | random_local | [0, 1, 10, 12] | False | False | 0.341 | 0.301 | 0.739 | True | 256 | 13.13 |
| shells_d5_p24_seed2401_search3203 | dependence_local | [0, 1, 9, 10] | False | False | 0.350 | 0.330 | 0.810 | True | 256 | 12.77 |
| shells_d5_p24_seed2401_search3203 | shuffled_dependence_local | [0, 1, 10, 12] | False | False | 0.341 | 0.301 | 0.739 | True | 256 | 13.31 |
| shells_d8_p24_seed2401_search3203 | random | [0, 1, 2, 4, 10, 17] | False | False | 0.096 | 0.072 | 0.522 | False | 256 | 12.99 |
| shells_d8_p24_seed2401_search3203 | random_local | [0, 1, 9, 12, 13, 17, 23] | False | False | 0.265 | 0.119 | 0.677 | True | 256 | 11.87 |
| shells_d8_p24_seed2401_search3203 | dependence_local | [0, 1, 2, 9, 10, 12, 17, 23] | True | True | 1.213 | 1.101 | 1.000 | True | 256 | 11.58 |
| shells_d8_p24_seed2401_search3203 | shuffled_dependence_local | [0, 1, 2, 4, 5, 10, 12, 17, 18, 23] | False | False | 0.228 | 0.088 | 0.666 | False | 256 | 12.57 |
| single_shell_d2_p24_seed2401_search3203 | random | [0, 10, 23] | False | False | 0.776 | 0.744 | — | False | 256 | 16.10 |
| single_shell_d2_p24_seed2401_search3203 | random_local | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 14.31 |
| single_shell_d2_p24_seed2401_search3203 | dependence_local | [0, 10] | True | True | 1.650 | 1.632 | — | False | 256 | 15.37 |
| single_shell_d2_p24_seed2401_search3203 | shuffled_dependence_local | [0, 2, 3, 10, 15, 17, 18, 19, 22] | False | False | 0.424 | 0.425 | — | False | 256 | 16.77 |
| single_shell_d5_p24_seed2401_search3203 | random | [0, 1, 4, 5, 8, 10, 12] | False | False | 0.189 | 0.179 | — | False | 256 | 19.31 |
| single_shell_d5_p24_seed2401_search3203 | random_local | [0, 1, 5, 8, 9, 10, 12] | False | False | 0.465 | 0.459 | — | False | 256 | 18.20 |
| single_shell_d5_p24_seed2401_search3203 | dependence_local | [0, 1, 9, 10, 12] | True | True | 1.137 | 1.104 | — | False | 256 | 17.58 |
| single_shell_d5_p24_seed2401_search3203 | shuffled_dependence_local | [0, 1, 6, 10, 12, 18, 19, 21] | False | False | 0.195 | 0.169 | — | False | 256 | 19.79 |
| independent_gaussian_d5_p24_seed2401_search3203 | random | [5, 18] | False | False | -0.005 | -0.012 | — | False | 256 | 14.17 |
| independent_gaussian_d5_p24_seed2401_search3203 | random_local | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 14.55 |
| independent_gaussian_d5_p24_seed2401_search3203 | dependence_local | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 14.74 |
| independent_gaussian_d5_p24_seed2401_search3203 | shuffled_dependence_local | [5, 9, 13, 18] | False | False | 0.002 | -0.035 | — | False | 256 | 14.76 |
| correlated_gaussian_d5_p24_seed2401_search3203 | random | [2, 3, 4, 5, 7, 10, 11, 13, 15, 19] | False | False | 0.038 | -0.011 | — | False | 256 | 14.17 |
| correlated_gaussian_d5_p24_seed2401_search3203 | random_local | [2, 3, 4, 5, 7, 10, 11, 13, 15, 21] | False | False | 0.055 | -0.010 | — | False | 256 | 14.26 |
| correlated_gaussian_d5_p24_seed2401_search3203 | dependence_local | [0, 2, 3, 4, 5, 16, 17, 18] | False | True | 0.031 | -0.023 | — | False | 256 | 14.88 |
| correlated_gaussian_d5_p24_seed2401_search3203 | shuffled_dependence_local | [2, 4, 7, 11, 12, 13, 15, 18, 23] | False | False | 0.042 | -0.006 | — | False | 256 | 14.69 |
| student_t_d5_p24_seed2401_search3203 | random | [3, 5, 7, 12, 13, 16, 17, 19, 20, 22] | False | False | -0.056 | -0.379 | — | False | 256 | 14.33 |
| student_t_d5_p24_seed2401_search3203 | random_local | [3, 5, 6, 7, 12, 13, 16, 17, 19, 22] | False | False | -0.032 | -0.372 | — | False | 256 | 14.87 |
| student_t_d5_p24_seed2401_search3203 | dependence_local | [2, 7, 10, 19] | False | True | -0.027 | -0.848 | — | False | 256 | 14.56 |
| student_t_d5_p24_seed2401_search3203 | shuffled_dependence_local | [2, 6, 7, 10, 11, 19, 20] | False | False | -0.022 | -0.808 | — | False | 256 | 15.07 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | random | [5, 7, 11, 13, 15] | False | False | -0.051 | -0.118 | — | False | 256 | 13.31 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | random_local | [5, 7, 9, 11, 13, 15] | False | False | -0.027 | -0.106 | — | False | 256 | 13.44 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | dependence_local | [2, 21] | False | True | -0.045 | -0.100 | — | False | 256 | 12.51 |
| common_center_scale_mixture_d5_p24_seed2401_search3203 | shuffled_dependence_local | [2, 21] | False | False | -0.045 | -0.100 | — | False | 256 | 13.27 |
| mean_shift_d3_p24_seed2401_search3203 | random | [2, 3, 4, 7, 8, 11, 15, 16, 17, 21] | False | False | 0.073 | 0.053 | -0.001 | False | 256 | 16.78 |
| mean_shift_d3_p24_seed2401_search3203 | random_local | [2, 3, 4, 5, 7, 8, 11, 15, 16, 17] | False | False | 0.097 | 0.041 | 0.002 | False | 256 | 17.84 |
| mean_shift_d3_p24_seed2401_search3203 | dependence_local | [10, 11, 14, 16, 17, 21, 22] | False | False | 0.062 | 0.048 | 0.000 | False | 256 | 16.75 |
| mean_shift_d3_p24_seed2401_search3203 | shuffled_dependence_local | [2, 7, 8, 11, 13] | False | False | 0.071 | 0.030 | 0.002 | False | 256 | 16.29 |
| shells_d2_p24_seed2411_search3217 | random | [15] | False | False | 0.145 | 0.113 | 0.007 | True | 256 | 16.45 |
| shells_d2_p24_seed2411_search3217 | random_local | [15] | False | False | 0.145 | 0.113 | 0.007 | True | 256 | 17.16 |
| shells_d2_p24_seed2411_search3217 | dependence_local | [8, 16] | True | True | 0.557 | 0.599 | 1.000 | True | 256 | 15.43 |
| shells_d2_p24_seed2411_search3217 | shuffled_dependence_local | [15] | False | False | 0.145 | 0.113 | 0.007 | True | 256 | 15.11 |
| shells_d3_p24_seed2411_search3217 | random | [12] | False | False | 0.045 | 0.040 | -0.001 | False | 256 | 14.24 |
| shells_d3_p24_seed2411_search3217 | random_local | [14, 17] | False | False | 0.043 | 0.035 | 0.003 | False | 256 | 14.53 |
| shells_d3_p24_seed2411_search3217 | dependence_local | [7, 8, 16] | True | True | 0.765 | 0.687 | 1.000 | True | 256 | 12.42 |
| shells_d3_p24_seed2411_search3217 | shuffled_dependence_local | [3, 19] | False | False | 0.036 | -0.014 | -0.001 | False | 256 | 14.84 |
| shells_d4_p24_seed2411_search3217 | random | [7, 8, 13, 20] | False | False | 0.046 | 0.047 | 0.508 | False | 256 | 13.31 |
| shells_d4_p24_seed2411_search3217 | random_local | [0, 11] | False | False | 0.027 | 0.001 | -0.001 | False | 256 | 13.62 |
| shells_d4_p24_seed2411_search3217 | dependence_local | [6, 18] | False | False | 0.029 | 0.006 | -0.002 | False | 256 | 13.88 |
| shells_d4_p24_seed2411_search3217 | shuffled_dependence_local | [0, 11] | False | False | 0.027 | 0.001 | -0.001 | False | 256 | 13.92 |
| shells_d5_p24_seed2411_search3217 | random | [6, 7, 8, 10, 13] | False | False | 0.094 | 0.079 | 0.677 | False | 256 | 13.15 |
| shells_d5_p24_seed2411_search3217 | random_local | [6, 7, 8, 13, 16, 23] | False | False | 0.347 | 0.277 | 0.816 | True | 256 | 12.65 |
| shells_d5_p24_seed2411_search3217 | dependence_local | [1, 2, 23] | False | False | 0.005 | -0.040 | -0.001 | False | 256 | 13.85 |
| shells_d5_p24_seed2411_search3217 | shuffled_dependence_local | [5, 19] | False | False | 0.007 | -0.042 | -0.001 | False | 256 | 13.34 |
| shells_d8_p24_seed2411_search3217 | random | [1, 2, 5, 6, 7, 8, 10, 16, 23] | False | False | 0.038 | 0.056 | 0.562 | False | 256 | 12.82 |
| shells_d8_p24_seed2411_search3217 | random_local | [2, 5, 6, 7, 8, 9, 10, 16, 23] | False | False | 0.263 | 0.183 | 0.751 | False | 256 | 12.04 |
| shells_d8_p24_seed2411_search3217 | dependence_local | [2, 5, 6, 7, 8, 9, 13, 16] | True | True | 1.130 | 1.191 | 1.000 | True | 256 | 12.02 |
| shells_d8_p24_seed2411_search3217 | shuffled_dependence_local | [2, 5, 6, 7, 8, 16] | False | False | 0.389 | 0.394 | 0.816 | True | 256 | 12.53 |
| single_shell_d2_p24_seed2411_search3217 | random | [3, 5, 8, 16, 22] | False | False | 0.499 | 0.458 | — | False | 256 | 15.91 |
| single_shell_d2_p24_seed2411_search3217 | random_local | [6, 8, 13, 16, 23] | False | False | 0.536 | 0.516 | — | False | 256 | 15.21 |
| single_shell_d2_p24_seed2411_search3217 | dependence_local | [8, 16] | True | True | 1.409 | 1.421 | — | False | 256 | 13.38 |
| single_shell_d2_p24_seed2411_search3217 | shuffled_dependence_local | [1, 8, 12, 16, 18, 20, 22] | False | False | 0.429 | 0.403 | — | False | 256 | 15.03 |
| single_shell_d5_p24_seed2411_search3217 | random | [6, 7, 8, 10, 13] | False | False | 0.266 | 0.326 | — | False | 256 | 18.93 |
| single_shell_d5_p24_seed2411_search3217 | random_local | [6, 7, 8, 13, 16, 23] | False | False | 0.648 | 0.653 | — | False | 256 | 18.89 |
| single_shell_d5_p24_seed2411_search3217 | dependence_local | [6, 7, 8, 13, 16] | True | True | 1.071 | 1.147 | — | False | 256 | 17.58 |
| single_shell_d5_p24_seed2411_search3217 | shuffled_dependence_local | [6, 8, 13, 16] | False | False | 0.504 | 0.485 | — | False | 256 | 17.53 |
| independent_gaussian_d5_p24_seed2411_search3217 | random | [1, 5, 8, 10] | False | False | 0.000 | -0.042 | — | False | 256 | 14.49 |
| independent_gaussian_d5_p24_seed2411_search3217 | random_local | [5, 8, 10, 12] | False | False | 0.006 | -0.057 | — | False | 256 | 13.84 |
| independent_gaussian_d5_p24_seed2411_search3217 | dependence_local | [3, 5, 6, 8, 9, 12, 16, 17, 20, 22] | False | False | 0.007 | -0.035 | — | False | 256 | 14.78 |
| independent_gaussian_d5_p24_seed2411_search3217 | shuffled_dependence_local | [5, 6, 7, 8, 9, 12, 16, 17, 20, 22] | False | False | 0.005 | -0.034 | — | False | 256 | 14.58 |
| correlated_gaussian_d5_p24_seed2411_search3217 | random | [0, 1, 3, 4, 5, 10, 16, 18, 19, 20] | False | False | 0.036 | -0.056 | — | False | 256 | 14.27 |
| correlated_gaussian_d5_p24_seed2411_search3217 | random_local | [0, 1, 3, 9, 10, 16, 17, 18, 19, 20] | False | False | 0.050 | -0.030 | — | False | 256 | 14.08 |
| correlated_gaussian_d5_p24_seed2411_search3217 | dependence_local | [2, 4, 6, 9, 14, 17, 20] | False | True | 0.035 | -0.020 | — | False | 256 | 14.35 |
| correlated_gaussian_d5_p24_seed2411_search3217 | shuffled_dependence_local | [1, 2, 5, 9, 10, 15, 17, 18, 19, 20] | False | False | 0.062 | -0.003 | — | False | 256 | 14.77 |
| student_t_d5_p24_seed2411_search3217 | random | [3, 4, 12] | False | False | -0.074 | -0.127 | — | False | 256 | 14.49 |
| student_t_d5_p24_seed2411_search3217 | random_local | [4, 16] | False | False | -0.043 | -0.361 | — | False | 256 | 13.44 |
| student_t_d5_p24_seed2411_search3217 | dependence_local | [4, 16] | False | True | -0.043 | -0.361 | — | False | 256 | 13.69 |
| student_t_d5_p24_seed2411_search3217 | shuffled_dependence_local | [4, 16] | False | False | -0.043 | -0.361 | — | False | 256 | 14.09 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | random | [0, 3, 4, 5, 11, 12, 16, 20, 21] | False | False | -0.056 | -0.111 | — | False | 256 | 13.29 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | random_local | [11, 15, 16, 20] | False | False | -0.039 | -0.070 | — | False | 256 | 13.00 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | dependence_local | [12, 15, 19, 20] | False | True | -0.028 | -0.124 | — | False | 256 | 13.72 |
| common_center_scale_mixture_d5_p24_seed2411_search3217 | shuffled_dependence_local | [3, 9, 12, 16] | False | False | -0.044 | -0.081 | — | False | 256 | 13.29 |
| mean_shift_d3_p24_seed2411_search3217 | random | [2, 6, 8, 10, 12, 13, 15, 19, 23] | False | False | 0.054 | 0.052 | -0.000 | False | 256 | 16.59 |
| mean_shift_d3_p24_seed2411_search3217 | random_local | [0, 2, 3, 4, 8, 9, 15, 18, 21] | False | False | 0.065 | 0.041 | -0.000 | False | 256 | 17.47 |
| mean_shift_d3_p24_seed2411_search3217 | dependence_local | [0, 2, 6, 8, 12, 13, 15, 17, 23] | False | False | 0.075 | 0.050 | -0.000 | False | 256 | 17.55 |
| mean_shift_d3_p24_seed2411_search3217 | shuffled_dependence_local | [1, 2, 3, 4, 6, 12, 13, 18] | False | False | 0.070 | 0.036 | -0.000 | False | 256 | 17.32 |
| shells_d2_p24_seed2423_search3221 | random | [10] | False | False | 0.145 | 0.125 | -0.001 | True | 256 | 16.32 |
| shells_d2_p24_seed2423_search3221 | random_local | [10] | False | False | 0.145 | 0.125 | -0.001 | True | 256 | 13.93 |
| shells_d2_p24_seed2423_search3221 | dependence_local | [2, 5] | True | True | 0.830 | 0.838 | 1.000 | True | 256 | 13.78 |
| shells_d2_p24_seed2423_search3221 | shuffled_dependence_local | [10] | False | False | 0.145 | 0.125 | -0.001 | True | 256 | 16.36 |
| shells_d3_p24_seed2423_search3221 | random | [9] | False | False | 0.035 | 0.030 | -0.000 | False | 256 | 14.76 |
| shells_d3_p24_seed2423_search3221 | random_local | [0, 12] | False | False | 0.035 | -0.001 | -0.002 | False | 256 | 15.25 |
| shells_d3_p24_seed2423_search3221 | dependence_local | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 14.29 |
| shells_d3_p24_seed2423_search3221 | shuffled_dependence_local | [2, 5, 10] | True | True | 0.631 | 0.672 | 1.000 | True | 256 | 13.35 |
| shells_d4_p24_seed2423_search3221 | random | [6, 8] | False | False | 0.023 | -0.012 | -0.001 | False | 256 | 13.66 |
| shells_d4_p24_seed2423_search3221 | random_local | [8, 9] | False | False | 0.029 | -0.001 | -0.001 | False | 256 | 13.85 |
| shells_d4_p24_seed2423_search3221 | dependence_local | [2, 5, 10, 18] | True | True | 0.736 | 0.794 | 1.000 | True | 256 | 13.18 |
| shells_d4_p24_seed2423_search3221 | shuffled_dependence_local | [2, 10, 18] | False | False | 0.262 | 0.275 | 0.629 | True | 256 | 13.67 |
| shells_d5_p24_seed2423_search3221 | random | [2, 7] | False | False | 0.019 | 0.033 | 0.195 | False | 256 | 13.22 |
| shells_d5_p24_seed2423_search3221 | random_local | [2, 5, 7, 9, 10, 13, 17, 18, 20, 21] | False | False | 0.041 | -0.006 | 0.466 | False | 256 | 14.95 |
| shells_d5_p24_seed2423_search3221 | dependence_local | [9, 14] | False | False | 0.007 | -0.074 | 0.001 | False | 256 | 16.85 |
| shells_d5_p24_seed2423_search3221 | shuffled_dependence_local | [2, 5, 7, 18] | False | False | 0.359 | 0.330 | 0.768 | True | 256 | 14.94 |
| shells_d8_p24_seed2423_search3221 | random | [0, 5, 7, 8, 10, 15] | False | False | 0.066 | 0.145 | 0.480 | False | 256 | 13.33 |
| shells_d8_p24_seed2423_search3221 | random_local | [2, 5, 7, 8, 15] | False | False | 0.234 | 0.227 | 0.645 | True | 256 | 14.41 |
| shells_d8_p24_seed2423_search3221 | dependence_local | [2, 5, 7, 8, 10, 12, 15, 18] | True | True | 1.142 | 1.226 | 1.000 | True | 256 | 12.48 |
| shells_d8_p24_seed2423_search3221 | shuffled_dependence_local | [2, 7, 12, 15] | False | False | 0.079 | 0.034 | 0.413 | False | 256 | 15.64 |
| single_shell_d2_p24_seed2423_search3221 | random | [0, 2, 5, 15] | False | False | 0.621 | 0.584 | — | False | 256 | 17.51 |
| single_shell_d2_p24_seed2423_search3221 | random_local | [2, 5, 6] | False | False | 0.821 | 0.799 | — | False | 256 | 14.26 |
| single_shell_d2_p24_seed2423_search3221 | dependence_local | [2, 5] | True | True | 1.685 | 1.696 | — | False | 256 | 14.98 |
| single_shell_d2_p24_seed2423_search3221 | shuffled_dependence_local | [1, 2, 3, 5, 7, 8, 9, 11, 12, 19] | False | False | 0.402 | 0.365 | — | False | 256 | 17.35 |
| single_shell_d5_p24_seed2423_search3221 | random | [2, 3, 5, 7, 9, 10, 17, 18, 20, 21] | False | False | 0.252 | 0.235 | — | False | 256 | 19.07 |
| single_shell_d5_p24_seed2423_search3221 | random_local | [2, 3, 5, 7, 10, 17, 18, 20, 21] | False | False | 0.293 | 0.286 | — | False | 256 | 16.85 |
| single_shell_d5_p24_seed2423_search3221 | dependence_local | [2, 5, 7, 10, 18] | True | True | 1.106 | 1.214 | — | False | 256 | 17.33 |
| single_shell_d5_p24_seed2423_search3221 | shuffled_dependence_local | [2, 3, 5, 16, 18, 19] | False | False | 0.149 | 0.081 | — | False | 256 | 19.40 |
| independent_gaussian_d5_p24_seed2423_search3221 | random | [10, 13] | False | False | 0.001 | -0.061 | — | False | 256 | 14.78 |
| independent_gaussian_d5_p24_seed2423_search3221 | random_local | [6, 10, 13] | False | False | 0.008 | -0.043 | — | False | 256 | 15.01 |
| independent_gaussian_d5_p24_seed2423_search3221 | dependence_local | [6, 7, 16, 20, 23] | False | False | 0.005 | -0.033 | — | False | 256 | 15.81 |
| independent_gaussian_d5_p24_seed2423_search3221 | shuffled_dependence_local | [5, 13, 18] | False | False | 0.001 | -0.029 | — | False | 256 | 15.27 |
| correlated_gaussian_d5_p24_seed2423_search3221 | random | [4, 9, 11, 13, 14, 19, 20, 21] | False | False | 0.024 | 0.005 | — | False | 256 | 14.34 |
| correlated_gaussian_d5_p24_seed2423_search3221 | random_local | [4, 6, 9, 11, 13, 14, 19, 20, 21] | False | False | 0.046 | 0.018 | — | False | 256 | 15.54 |
| correlated_gaussian_d5_p24_seed2423_search3221 | dependence_local | [3, 4, 6, 9, 13, 14, 16, 21] | False | True | 0.036 | 0.019 | — | False | 256 | 15.62 |
| correlated_gaussian_d5_p24_seed2423_search3221 | shuffled_dependence_local | [0, 11, 15, 17, 20, 22] | False | False | 0.023 | -0.008 | — | False | 256 | 15.14 |
| student_t_d5_p24_seed2423_search3221 | random | [0, 9, 11, 22] | False | False | -0.106 | -0.156 | — | False | 256 | 15.40 |
| student_t_d5_p24_seed2423_search3221 | random_local | [21, 23] | False | False | -0.094 | -0.601 | — | False | 256 | 13.79 |
| student_t_d5_p24_seed2423_search3221 | dependence_local | [21, 23] | False | True | -0.094 | -0.601 | — | False | 256 | 14.60 |
| student_t_d5_p24_seed2423_search3221 | shuffled_dependence_local | [6, 9, 19, 22] | False | False | -0.088 | -0.102 | — | False | 256 | 14.28 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | random | [0, 8, 18] | False | False | -0.058 | -0.143 | — | False | 256 | 13.67 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | random_local | [0, 2, 8, 18, 21] | False | False | -0.033 | -0.264 | — | False | 256 | 14.68 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | dependence_local | [0, 2, 8, 9, 11, 18, 21, 22] | False | True | -0.044 | -0.311 | — | False | 256 | 13.95 |
| common_center_scale_mixture_d5_p24_seed2423_search3221 | shuffled_dependence_local | [0, 2, 8, 14, 19, 20, 21] | False | False | -0.033 | -0.113 | — | False | 256 | 14.12 |
| mean_shift_d3_p24_seed2423_search3221 | random | [1, 2, 7, 12, 13, 15, 18, 19, 21, 23] | False | False | 0.087 | 0.068 | -0.002 | False | 256 | 17.54 |
| mean_shift_d3_p24_seed2423_search3221 | random_local | [1, 2, 7, 12, 13, 15, 16, 18, 19, 21] | False | False | 0.106 | 0.057 | -0.002 | False | 256 | 18.44 |
| mean_shift_d3_p24_seed2423_search3221 | dependence_local | [1, 2, 7, 12, 13, 15, 16, 18, 19, 21] | False | False | 0.106 | 0.057 | -0.002 | False | 256 | 18.21 |
| mean_shift_d3_p24_seed2423_search3221 | shuffled_dependence_local | [1, 2, 7, 12, 13, 15, 16, 18, 19, 21] | False | False | 0.106 | 0.057 | -0.002 | False | 256 | 18.35 |
