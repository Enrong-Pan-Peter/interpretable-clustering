# Kernel pilot: verified descriptive results

Descriptive development audit; no clustering refits; three seeds do not establish superiority. Independent replay verifies native predictions and saved tree metrics, not exported tree text or unsaved same-panel centroid models.

6966 checks; 0 discrepancies; 201 saved models.

| Case | Variant | Test ARI | Same-panel identity ARI | Recall | Tree disagreement | Sizes |
|---|---|---:|---:|---:|---:|---|
| mean_shift | diagonal_cut_local | 0.144 | — | 0.083 | 0.000 | [1, 1, 1] |
| mean_shift | diagonal_gap_local | 0.046 | — | 0.083 | 0.013 | [16, 15, 16] |
| mean_shift | projection_cut_local | 0.268 | 0.426 | 0.472 | 0.303 | [16, 16, 16] |
| mean_shift | projection_gap_local | 0.331 | 0.374 | 0.500 | 0.263 | [16, 16, 16] |
| mean_shift | projection_gap_global | 0.519 | 0.607 | 0.806 | 0.257 | [16, 16, 16] |
| mean_shift | all_features_local | 0.478 | — | 1.000 | 0.277 | [200, 200, 200] |
| grouped_moons | diagonal_cut_local | 0.076 | — | 0.033 | 0.002 | [1, 1, 1] |
| grouped_moons | diagonal_gap_local | 0.532 | — | 0.933 | 0.057 | [16, 16, 16] |
| grouped_moons | projection_cut_local | 0.277 | 0.288 | 0.400 | 0.197 | [16, 16, 16] |
| grouped_moons | projection_gap_local | 0.502 | 0.477 | 0.733 | 0.087 | [16, 16, 16] |
| grouped_moons | projection_gap_global | 0.524 | 0.509 | 1.000 | 0.060 | [16, 16, 16] |
| grouped_moons | all_features_local | 0.486 | — | 1.000 | 0.065 | [50, 50, 50] |
| shells | diagonal_cut_local | -0.004 | — | 0.000 | 0.003 | [1, 1, 1] |
| shells | diagonal_gap_local | 0.004 | — | 0.133 | 0.018 | [13, 10, 11] |
| shells | projection_cut_local | -0.001 | -0.003 | 0.267 | 0.290 | [16, 16, 16] |
| shells | projection_gap_local | -0.002 | -0.003 | 0.133 | 0.357 | [16, 16, 16] |
| shells | projection_gap_global | 0.014 | 0.011 | 0.200 | 0.272 | [16, 16, 16] |
| shells | all_features_local | 0.005 | — | 1.000 | 0.395 | [50, 50, 50] |
| covariance_pairs | diagonal_cut_local | -0.002 | — | 0.083 | 0.007 | [1, 1, 1] |
| covariance_pairs | diagonal_gap_local | 0.001 | — | 0.250 | 0.023 | [3, 11, 16] |
| covariance_pairs | projection_cut_local | 0.003 | 0.003 | 0.333 | 0.208 | [16, 16, 16] |
| covariance_pairs | projection_gap_local | 0.002 | 0.000 | 0.333 | 0.308 | [16, 16, 16] |
| covariance_pairs | projection_gap_global | -0.002 | -0.000 | 0.333 | 0.293 | [16, 16, 16] |
| covariance_pairs | all_features_local | -0.001 | — | 1.000 | 0.425 | [50, 50, 50] |
| null_independent | diagonal_cut_local | — | — | — | 0.000 | [1, 1, 1] |
| null_independent | diagonal_gap_local | — | — | — | 0.013 | [16, 16, 13] |
| null_independent | projection_cut_local | — | — | — | 0.180 | [16, 16, 16] |
| null_independent | projection_gap_local | — | — | — | 0.350 | [16, 16, 16] |
| null_independent | projection_gap_global | — | — | — | 0.377 | [16, 16, 16] |
| null_independent | all_features_local | — | — | — | 0.363 | [50, 50, 50] |
| null_correlated | diagonal_cut_local | — | — | — | 0.005 | [1, 1, 1] |
| null_correlated | diagonal_gap_local | — | — | — | 0.088 | [11, 16, 16] |
| null_correlated | projection_cut_local | — | — | — | 0.077 | [16, 16, 16] |
| null_correlated | projection_gap_local | — | — | — | 0.107 | [16, 16, 16] |
| null_correlated | projection_gap_global | — | — | — | 0.100 | [16, 16, 16] |
| null_correlated | all_features_local | — | — | — | 0.112 | [50, 50, 50] |
| single_shell | diagonal_cut_local | — | — | — | 0.000 | [1, 1, 1] |
| single_shell | diagonal_gap_local | — | — | — | 0.012 | [14, 12, 12] |
| single_shell | projection_cut_local | — | — | — | 0.302 | [16, 16, 16] |
| single_shell | projection_gap_local | — | — | — | 0.327 | [16, 16, 16] |
| single_shell | projection_gap_global | — | — | — | 0.342 | [16, 16, 16] |
| single_shell | all_features_local | — | — | — | 0.372 | [50, 50, 50] |
