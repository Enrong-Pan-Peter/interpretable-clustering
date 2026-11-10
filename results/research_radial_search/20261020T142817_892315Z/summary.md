# Hidden-panel radial search

Development comparison: all arms have equal unique radial-panel fits, the same size cap, and no supplied support. Random/local and dependence/local use half their budget for proposals and the remainder for identical add/drop/swap refinement. The dependence proposal uses fit-only absolute squared-coordinate correlation; its extra preprocessing and wall time are recorded.

Shuffled-dependence local search permutes the feature identities of the dependence matrix before building the same chains. It preserves the matrix values and proposal procedure while breaking their association with the measurements. Evaluated size histograms are saved for every arm. The ordinary random/local comparison alone does not isolate the statistic from chain structure.

Models fit on fit rows; adaptive search and final panel choice use search rows. Validation and test are independent of panel selection. The supplied-support oracle is fitted afterward as a diagnostic, outside the search budget. Flags are provisional, not calibrated tests. Exact support recovery is not meaningful for control cases with no special planted cluster support. This is not a comparison with established sparse-clustering methods or evidence of novelty.

| Job | Method | Panel | Exact support | Oracle visited | Search gain | Fresh val gain | Test ARI | Val flag | Fits | Seconds |
|---|---|---|---|---|---|---|---|---|---:|---:|
| shells_d2_p14_seed2309_search3101 | random | [7] | False | False | 0.182 | 0.067 | -0.004 | True | 48 | 2.65 |
| shells_d2_p14_seed2309_search3101 | random_local | [7] | False | False | 0.182 | 0.067 | -0.004 | True | 48 | 2.35 |
| shells_d2_p14_seed2309_search3101 | dependence_local | [1, 3, 6, 8, 9, 11, 12] | False | False | 0.070 | 0.049 | 0.209 | False | 48 | 2.67 |
| shells_d2_p14_seed2309_search3101 | shuffled_dependence_local | [2, 3, 6, 9, 10, 13] | False | False | 0.080 | 0.038 | 0.001 | False | 48 | 2.67 |
| shells_d4_p14_seed2309_search3101 | random | [0, 13] | False | False | 0.030 | -0.057 | 0.003 | False | 48 | 2.40 |
| shells_d4_p14_seed2309_search3101 | random_local | [0, 13] | False | False | 0.030 | -0.057 | 0.003 | False | 48 | 2.17 |
| shells_d4_p14_seed2309_search3101 | dependence_local | [0, 13] | False | False | 0.030 | -0.057 | 0.003 | False | 48 | 2.32 |
| shells_d4_p14_seed2309_search3101 | shuffled_dependence_local | [0, 13] | False | False | 0.030 | -0.057 | 0.003 | False | 48 | 2.23 |
| shells_d8_p14_seed2309_search3101 | random | [0, 1, 2, 3, 4, 6, 7, 8, 11, 12] | False | False | 0.091 | 0.164 | 0.809 | False | 48 | 2.04 |
| shells_d8_p14_seed2309_search3101 | random_local | [1, 3, 4, 6, 8, 11, 12] | False | False | 0.705 | 0.587 | 0.926 | True | 48 | 1.92 |
| shells_d8_p14_seed2309_search3101 | dependence_local | [3, 4, 6, 9, 12] | False | False | 0.243 | 0.217 | 0.721 | True | 48 | 2.17 |
| shells_d8_p14_seed2309_search3101 | shuffled_dependence_local | [1, 2, 3, 4, 6, 8, 9, 11, 12] | False | False | 0.636 | 0.696 | 0.950 | True | 48 | 1.97 |
| single_shell_d5_p14_seed2309_search3101 | random | [1, 3, 5, 6, 8, 11, 12] | False | False | 0.225 | 0.198 | — | False | 48 | 2.80 |
| single_shell_d5_p14_seed2309_search3101 | random_local | [1, 3, 5, 6, 8, 9, 12] | False | False | 0.457 | 0.288 | — | False | 48 | 2.87 |
| single_shell_d5_p14_seed2309_search3101 | dependence_local | [1, 6, 8, 9, 12] | True | True | 0.993 | 1.036 | — | False | 48 | 2.81 |
| single_shell_d5_p14_seed2309_search3101 | shuffled_dependence_local | [0, 1, 4, 6, 7, 8, 9, 10, 11, 12] | False | False | 0.308 | 0.277 | — | False | 48 | 2.97 |
| correlated_gaussian_d5_p14_seed2309_search3101 | random | [0, 3, 5, 7, 9, 10, 11, 13] | False | False | 0.058 | 0.099 | — | False | 48 | 2.42 |
| correlated_gaussian_d5_p14_seed2309_search3101 | random_local | [0, 2, 3, 5, 7, 9, 10, 11] | False | False | 0.112 | 0.075 | — | False | 48 | 2.41 |
| correlated_gaussian_d5_p14_seed2309_search3101 | dependence_local | [2, 3, 5, 7, 9, 10, 11] | False | True | 0.081 | 0.061 | — | False | 48 | 2.54 |
| correlated_gaussian_d5_p14_seed2309_search3101 | shuffled_dependence_local | [3, 5, 7, 8] | False | False | 0.035 | 0.059 | — | False | 48 | 2.51 |
| mean_shift_d3_p14_seed2309_search3101 | random | [2, 4, 7, 9, 10, 12, 13] | False | False | 0.074 | 0.044 | 0.017 | False | 48 | 2.67 |
| mean_shift_d3_p14_seed2309_search3101 | random_local | [2, 3, 4, 5, 7, 8, 9, 10, 11, 13] | False | False | 0.089 | 0.028 | -0.003 | False | 48 | 2.86 |
| mean_shift_d3_p14_seed2309_search3101 | dependence_local | [3, 4, 5, 7, 8, 9, 10, 11, 13] | False | False | 0.078 | 0.037 | -0.002 | False | 48 | 2.80 |
| mean_shift_d3_p14_seed2309_search3101 | shuffled_dependence_local | [1, 2, 3, 4, 5, 7, 8, 11, 13] | False | False | 0.109 | 0.042 | 0.002 | False | 48 | 2.83 |
