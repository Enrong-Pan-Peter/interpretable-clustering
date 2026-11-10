# Obstacle diagnostics

All configurations are prescribed and reported; no test-ARI winner is selected. Fresh seeds on real data are resamples of the same cohort. Compression reuses the inspected pilot. These are development diagnostics, not evidence of a novel validated method.

Full native support can exceed the feature-prefix cap. Squared coordinates are squared discovery-standardized original features, then standardized again on discovery rows. Each original feature is counted once.

The compact table shows the largest prescribed prefix and the full models. Every smaller prefix, feature name, assignment and geometry score is retained in case files. Showing a prefix here does not select it as best.

## Model retention and single-population controls

ARI compares to external annotations, when available. Fidelity compares test assignments to the full native model, which itself may be wrong. Invalid discovery partitions have blank external ARI. Controls have no external ARI or accepted/rejected status: the procedure always proposes a split.

| Case | Seed | Mapping | L1 bound | Prefix size | Full support | Assignment | Test ARI | Fidelity ARI |
|---|---:|---|---:|---:|---:|---|---:|---:|
| mean_shift | 3 | raw | 1.250 | full | 5 | full_native_centroid | 0.297 | 1.000 |
| mean_shift | 3 | raw | 1.250 | full | 5 | full_native_knn_readout | 0.418 | 0.749 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | truncated_native_centroid | 0.297 | 1.000 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | refit_weighted_centroid | 0.297 | 1.000 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | refit_unweighted_centroid | 0.778 | 0.355 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | refit_unweighted_centroid_knn | 0.749 | 0.297 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | representation_spectral_knn | 0.720 | 0.278 |
| mean_shift | 3 | raw | 1.250 | 8 | 5 | raw_spectral_knn | 0.720 | 0.278 |
| mean_shift | 3 | raw | 2.828 | full | 50 | full_native_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 2.828 | full | 50 | full_native_knn_readout | 0.749 | 0.934 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | truncated_native_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.720 | 0.902 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.749 | 0.870 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | representation_spectral_knn | 0.720 | 0.839 |
| mean_shift | 3 | raw | 2.828 | 8 | 50 | raw_spectral_knn | 0.720 | 0.839 |
| mean_shift | 3 | raw | 7.071 | full | 50 | full_native_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 7.071 | full | 50 | full_native_knn_readout | 0.749 | 0.934 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | truncated_native_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | 0.749 | 1.000 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.720 | 0.902 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.749 | 0.870 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | representation_spectral_knn | 0.720 | 0.839 |
| mean_shift | 3 | raw | 7.071 | 8 | 50 | raw_spectral_knn | 0.720 | 0.839 |
| mean_shift | 3 | squared | 1.250 | full | 38 | full_native_centroid | -0.001 | 1.000 |
| mean_shift | 3 | squared | 1.250 | full | 38 | full_native_knn_readout | -0.016 | 0.737 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | truncated_native_centroid | -0.001 | 1.000 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | refit_weighted_centroid | -0.001 | 1.000 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | refit_unweighted_centroid | -0.016 | 0.126 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | refit_unweighted_centroid_knn | -0.020 | 0.238 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | representation_spectral_knn | 0.024 | -0.040 |
| mean_shift | 3 | squared | 1.250 | 8 | 38 | raw_spectral_knn | -0.014 | -0.018 |
| mean_shift | 3 | squared | 2.828 | full | 50 | full_native_centroid | 0.020 | 1.000 |
| mean_shift | 3 | squared | 2.828 | full | 50 | full_native_knn_readout | 0.020 | 1.000 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | truncated_native_centroid | 0.020 | 1.000 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | 0.020 | 1.000 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.018 | 0.426 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.014 | 0.377 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | representation_spectral_knn | 0.014 | -0.002 |
| mean_shift | 3 | squared | 2.828 | 8 | 50 | raw_spectral_knn | 0.000 | -0.016 |
| mean_shift | 3 | squared | 7.071 | full | 50 | full_native_centroid | 0.009 | 1.000 |
| mean_shift | 3 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.014 | 0.818 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.009 | 1.000 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | 0.022 | 0.882 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | -0.005 | 0.315 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | -0.010 | 0.239 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | representation_spectral_knn | -0.014 | -0.022 |
| mean_shift | 3 | squared | 7.071 | 8 | 50 | raw_spectral_knn | -0.006 | 0.001 |
| mean_shift | 4 | raw | 1.250 | full | 4 | full_native_centroid | 0.418 | 1.000 |
| mean_shift | 4 | raw | 1.250 | full | 4 | full_native_knn_readout | 0.486 | 0.839 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | truncated_native_centroid | 0.418 | 1.000 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | refit_weighted_centroid | 0.418 | 1.000 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | refit_unweighted_centroid | 0.749 | 0.375 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | refit_unweighted_centroid_knn | 0.534 | 0.296 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | representation_spectral_knn | 0.463 | 0.243 |
| mean_shift | 4 | raw | 1.250 | 8 | 4 | raw_spectral_knn | 0.463 | 0.243 |
| mean_shift | 4 | raw | 2.828 | full | 50 | full_native_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 2.828 | full | 50 | full_native_knn_readout | 0.637 | 0.870 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | truncated_native_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.749 | 0.934 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.664 | 0.839 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | representation_spectral_knn | 0.692 | 0.870 |
| mean_shift | 4 | raw | 2.828 | 8 | 50 | raw_spectral_knn | 0.692 | 0.870 |
| mean_shift | 4 | raw | 7.071 | full | 50 | full_native_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 7.071 | full | 50 | full_native_knn_readout | 0.720 | 0.967 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | truncated_native_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | 0.749 | 1.000 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.808 | 0.870 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.692 | 0.808 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | representation_spectral_knn | 0.637 | 0.808 |
| mean_shift | 4 | raw | 7.071 | 8 | 50 | raw_spectral_knn | 0.637 | 0.808 |
| mean_shift | 4 | squared | 1.250 | full | 28 | full_native_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 1.250 | full | 28 | full_native_knn_readout | -0.006 | 0.918 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | truncated_native_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | refit_weighted_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | refit_unweighted_centroid | -0.006 | 0.482 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | refit_unweighted_centroid_knn | -0.006 | 0.458 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | representation_spectral_knn | 0.001 | -0.105 |
| mean_shift | 4 | squared | 1.250 | 8 | 28 | raw_spectral_knn | -0.001 | -0.013 |
| mean_shift | 4 | squared | 2.828 | full | 50 | full_native_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 2.828 | full | 50 | full_native_knn_readout | -0.006 | 0.918 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | truncated_native_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | -0.006 | 1.000 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | -0.006 | 0.482 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | -0.006 | 0.458 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | representation_spectral_knn | 0.001 | -0.105 |
| mean_shift | 4 | squared | 2.828 | 8 | 50 | raw_spectral_knn | -0.001 | -0.013 |
| mean_shift | 4 | squared | 7.071 | full | 50 | full_native_centroid | 0.008 | 1.000 |
| mean_shift | 4 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.008 | 0.882 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.008 | 1.000 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | 0.008 | 1.000 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | -0.007 | 0.210 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.008 | 0.203 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | representation_spectral_knn | -0.005 | 0.072 |
| mean_shift | 4 | squared | 7.071 | 8 | 50 | raw_spectral_knn | 0.211 | -0.006 |
| mean_shift | 5 | raw | 1.250 | full | 5 | full_native_centroid | 0.261 | 1.000 |
| mean_shift | 5 | raw | 1.250 | full | 5 | full_native_knn_readout | 0.297 | 0.934 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | truncated_native_centroid | 0.261 | 1.000 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | refit_weighted_centroid | 0.261 | 1.000 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | refit_unweighted_centroid | 0.870 | 0.297 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | refit_unweighted_centroid_knn | 0.839 | 0.278 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | representation_spectral_knn | 0.839 | 0.278 |
| mean_shift | 5 | raw | 1.250 | 8 | 5 | raw_spectral_knn | 0.839 | 0.278 |
| mean_shift | 5 | raw | 2.828 | full | 50 | full_native_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 2.828 | full | 50 | full_native_knn_readout | 0.902 | 0.934 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | truncated_native_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.778 | 0.870 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.720 | 0.749 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | representation_spectral_knn | 0.720 | 0.749 |
| mean_shift | 5 | raw | 2.828 | 8 | 50 | raw_spectral_knn | 0.720 | 0.749 |
| mean_shift | 5 | raw | 7.071 | full | 50 | full_native_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 7.071 | full | 50 | full_native_knn_readout | 0.902 | 0.934 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | truncated_native_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | 0.839 | 1.000 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.664 | 0.749 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.778 | 0.808 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | representation_spectral_knn | 0.808 | 0.839 |
| mean_shift | 5 | raw | 7.071 | 8 | 50 | raw_spectral_knn | 0.808 | 0.839 |
| mean_shift | 5 | squared | 1.250 | full | 17 | full_native_centroid | -0.012 | 1.000 |
| mean_shift | 5 | squared | 1.250 | full | 17 | full_native_knn_readout | -0.011 | 0.877 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | truncated_native_centroid | -0.012 | 1.000 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | refit_weighted_centroid | -0.012 | 1.000 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | refit_unweighted_centroid | -0.010 | 0.132 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | refit_unweighted_centroid_knn | -0.007 | 0.032 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | representation_spectral_knn | -0.002 | -0.053 |
| mean_shift | 5 | squared | 1.250 | 8 | 17 | raw_spectral_knn | -0.006 | -0.035 |
| mean_shift | 5 | squared | 2.828 | full | 50 | full_native_centroid | -0.009 | 1.000 |
| mean_shift | 5 | squared | 2.828 | full | 50 | full_native_knn_readout | -0.007 | 0.951 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | truncated_native_centroid | -0.009 | 1.000 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | -0.009 | 1.000 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.006 | 0.656 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | -0.006 | 0.373 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | representation_spectral_knn | -0.010 | 0.065 |
| mean_shift | 5 | squared | 2.828 | 8 | 50 | raw_spectral_knn | -0.004 | 0.002 |
| mean_shift | 5 | squared | 7.071 | full | 50 | full_native_centroid | 0.037 | 1.000 |
| mean_shift | 5 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.030 | 0.885 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.037 | 1.000 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | 0.037 | 1.000 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.018 | 0.233 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.016 | 0.183 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | representation_spectral_knn | -0.005 | -0.019 |
| mean_shift | 5 | squared | 7.071 | 8 | 50 | raw_spectral_knn | 0.584 | 0.024 |
| metabric | 3 | raw | 1.250 | full | 3 | full_native_centroid | 0.418 | 1.000 |
| metabric | 3 | raw | 1.250 | full | 3 | full_native_knn_readout | 0.418 | 0.934 |
| metabric | 3 | raw | 1.250 | 8 | 3 | truncated_native_centroid | 0.418 | 1.000 |
| metabric | 3 | raw | 1.250 | 8 | 3 | refit_weighted_centroid | 0.418 | 1.000 |
| metabric | 3 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid | 0.335 | 0.534 |
| metabric | 3 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid_knn | 0.396 | 0.559 |
| metabric | 3 | raw | 1.250 | 8 | 3 | representation_spectral_knn | 0.178 | 0.462 |
| metabric | 3 | raw | 1.250 | 8 | 3 | raw_spectral_knn | 0.178 | 0.462 |
| metabric | 3 | raw | 2.828 | full | 10 | full_native_centroid | 0.396 | 1.000 |
| metabric | 3 | raw | 2.828 | full | 10 | full_native_knn_readout | 0.396 | 0.934 |
| metabric | 3 | raw | 2.828 | 8 | 10 | truncated_native_centroid | 0.335 | 0.902 |
| metabric | 3 | raw | 2.828 | 8 | 10 | refit_weighted_centroid | 0.355 | 0.934 |
| metabric | 3 | raw | 2.828 | 8 | 10 | refit_unweighted_centroid | 0.335 | 0.902 |
| metabric | 3 | raw | 2.828 | 8 | 10 | refit_unweighted_centroid_knn | 0.396 | 0.934 |
| metabric | 3 | raw | 2.828 | 8 | 10 | representation_spectral_knn | 0.178 | 0.486 |
| metabric | 3 | raw | 2.828 | 8 | 10 | raw_spectral_knn | 0.178 | 0.486 |
| metabric | 3 | raw | 15.811 | full | 250 | full_native_centroid | 0.463 | 1.000 |
| metabric | 3 | raw | 15.811 | full | 250 | full_native_knn_readout | 0.510 | 0.870 |
| metabric | 3 | raw | 15.811 | 8 | 250 | truncated_native_centroid | 0.418 | 0.808 |
| metabric | 3 | raw | 15.811 | 8 | 250 | refit_weighted_centroid | 0.440 | 0.839 |
| metabric | 3 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.418 | 0.808 |
| metabric | 3 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.396 | 0.720 |
| metabric | 3 | raw | 15.811 | 8 | 250 | representation_spectral_knn | 0.147 | 0.463 |
| metabric | 3 | raw | 15.811 | 8 | 250 | raw_spectral_knn | 0.147 | 0.463 |
| metabric | 3 | squared | 1.250 | full | 2 | full_native_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | full | 2 | full_native_knn_readout | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | 8 | 2 | truncated_native_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | 8 | 2 | refit_weighted_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | 8 | 2 | refit_unweighted_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | 8 | 2 | refit_unweighted_centroid_knn | 0.014 | 1.000 |
| metabric | 3 | squared | 1.250 | 8 | 2 | representation_spectral_knn | 0.017 | -0.014 |
| metabric | 3 | squared | 1.250 | 8 | 2 | raw_spectral_knn | 0.058 | 0.012 |
| metabric | 3 | squared | 2.828 | full | 77 | full_native_centroid | — | 1.000 |
| metabric | 3 | squared | 2.828 | full | 77 | full_native_knn_readout | — | 1.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | truncated_native_centroid | — | 1.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | refit_weighted_centroid | — | 1.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | refit_unweighted_centroid | — | 1.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | refit_unweighted_centroid_knn | — | 1.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | representation_spectral_knn | 0.022 | 0.000 |
| metabric | 3 | squared | 2.828 | 8 | 77 | raw_spectral_knn | -0.008 | 0.000 |
| metabric | 3 | squared | 15.811 | full | 250 | full_native_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | full | 250 | full_native_knn_readout | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | 8 | 250 | truncated_native_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | 8 | 250 | refit_weighted_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.014 | 1.000 |
| metabric | 3 | squared | 15.811 | 8 | 250 | representation_spectral_knn | 0.017 | -0.014 |
| metabric | 3 | squared | 15.811 | 8 | 250 | raw_spectral_knn | 0.058 | 0.012 |
| metabric | 4 | raw | 1.250 | full | 3 | full_native_centroid | 0.610 | 1.000 |
| metabric | 4 | raw | 1.250 | full | 3 | full_native_knn_readout | 0.610 | 0.934 |
| metabric | 4 | raw | 1.250 | 8 | 3 | truncated_native_centroid | 0.610 | 1.000 |
| metabric | 4 | raw | 1.250 | 8 | 3 | refit_weighted_centroid | 0.610 | 1.000 |
| metabric | 4 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid | 0.440 | 0.720 |
| metabric | 4 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid_knn | 0.534 | 0.839 |
| metabric | 4 | raw | 1.250 | 8 | 3 | representation_spectral_knn | 0.315 | 0.375 |
| metabric | 4 | raw | 1.250 | 8 | 3 | raw_spectral_knn | 0.315 | 0.375 |
| metabric | 4 | raw | 2.828 | full | 10 | full_native_centroid | 0.559 | 1.000 |
| metabric | 4 | raw | 2.828 | full | 10 | full_native_knn_readout | 0.559 | 0.870 |
| metabric | 4 | raw | 2.828 | 8 | 10 | truncated_native_centroid | 0.584 | 0.967 |
| metabric | 4 | raw | 2.828 | 8 | 10 | refit_weighted_centroid | 0.584 | 0.967 |
| metabric | 4 | raw | 2.828 | 8 | 10 | refit_unweighted_centroid | 0.534 | 0.967 |
| metabric | 4 | raw | 2.828 | 8 | 10 | refit_unweighted_centroid_knn | 0.610 | 0.870 |
| metabric | 4 | raw | 2.828 | 8 | 10 | representation_spectral_knn | 0.296 | 0.396 |
| metabric | 4 | raw | 2.828 | 8 | 10 | raw_spectral_knn | 0.296 | 0.396 |
| metabric | 4 | raw | 15.811 | full | 250 | full_native_centroid | 0.534 | 1.000 |
| metabric | 4 | raw | 15.811 | full | 250 | full_native_knn_readout | 0.637 | 0.808 |
| metabric | 4 | raw | 15.811 | 8 | 250 | truncated_native_centroid | 0.559 | 0.902 |
| metabric | 4 | raw | 15.811 | 8 | 250 | refit_weighted_centroid | 0.534 | 0.870 |
| metabric | 4 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.534 | 0.870 |
| metabric | 4 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.610 | 0.778 |
| metabric | 4 | raw | 15.811 | 8 | 250 | representation_spectral_knn | 0.296 | 0.463 |
| metabric | 4 | raw | 15.811 | 8 | 250 | raw_spectral_knn | 0.296 | 0.463 |
| metabric | 4 | squared | 1.250 | full | 4 | full_native_centroid | 0.078 | 1.000 |
| metabric | 4 | squared | 1.250 | full | 4 | full_native_knn_readout | 0.068 | 0.956 |
| metabric | 4 | squared | 1.250 | 8 | 4 | truncated_native_centroid | 0.078 | 1.000 |
| metabric | 4 | squared | 1.250 | 8 | 4 | refit_weighted_centroid | 0.078 | 1.000 |
| metabric | 4 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid | 0.042 | 0.681 |
| metabric | 4 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid_knn | 0.020 | 0.539 |
| metabric | 4 | squared | 1.250 | 8 | 4 | representation_spectral_knn | 0.102 | 0.436 |
| metabric | 4 | squared | 1.250 | 8 | 4 | raw_spectral_knn | 0.090 | -0.005 |
| metabric | 4 | squared | 2.828 | full | 19 | full_native_centroid | — | 1.000 |
| metabric | 4 | squared | 2.828 | full | 19 | full_native_knn_readout | — | 1.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | truncated_native_centroid | — | 1.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | refit_weighted_centroid | — | 1.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | refit_unweighted_centroid | — | 1.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | refit_unweighted_centroid_knn | — | 1.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | representation_spectral_knn | 0.002 | 0.000 |
| metabric | 4 | squared | 2.828 | 8 | 19 | raw_spectral_knn | 0.005 | 0.000 |
| metabric | 4 | squared | 15.811 | full | 250 | full_native_centroid | 0.059 | 1.000 |
| metabric | 4 | squared | 15.811 | full | 250 | full_native_knn_readout | 0.025 | 0.459 |
| metabric | 4 | squared | 15.811 | 8 | 250 | truncated_native_centroid | 0.068 | 0.958 |
| metabric | 4 | squared | 15.811 | 8 | 250 | refit_weighted_centroid | 0.051 | 0.959 |
| metabric | 4 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.059 | 0.918 |
| metabric | 4 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.034 | 0.786 |
| metabric | 4 | squared | 15.811 | 8 | 250 | representation_spectral_knn | 0.102 | 0.655 |
| metabric | 4 | squared | 15.811 | 8 | 250 | raw_spectral_knn | 0.260 | -0.012 |
| metabric | 5 | raw | 1.250 | full | 2 | full_native_centroid | 0.355 | 1.000 |
| metabric | 5 | raw | 1.250 | full | 2 | full_native_knn_readout | 0.355 | 0.934 |
| metabric | 5 | raw | 1.250 | 8 | 2 | truncated_native_centroid | 0.355 | 1.000 |
| metabric | 5 | raw | 1.250 | 8 | 2 | refit_weighted_centroid | 0.355 | 1.000 |
| metabric | 5 | raw | 1.250 | 8 | 2 | refit_unweighted_centroid | 0.418 | 0.664 |
| metabric | 5 | raw | 1.250 | 8 | 2 | refit_unweighted_centroid_knn | 0.396 | 0.637 |
| metabric | 5 | raw | 1.250 | 8 | 2 | representation_spectral_knn | 0.396 | 0.637 |
| metabric | 5 | raw | 1.250 | 8 | 2 | raw_spectral_knn | 0.396 | 0.637 |
| metabric | 5 | raw | 2.828 | full | 12 | full_native_centroid | 0.335 | 1.000 |
| metabric | 5 | raw | 2.828 | full | 12 | full_native_knn_readout | 0.355 | 0.902 |
| metabric | 5 | raw | 2.828 | 8 | 12 | truncated_native_centroid | 0.335 | 1.000 |
| metabric | 5 | raw | 2.828 | 8 | 12 | refit_weighted_centroid | 0.355 | 0.967 |
| metabric | 5 | raw | 2.828 | 8 | 12 | refit_unweighted_centroid | 0.315 | 0.902 |
| metabric | 5 | raw | 2.828 | 8 | 12 | refit_unweighted_centroid_knn | 0.396 | 0.778 |
| metabric | 5 | raw | 2.828 | 8 | 12 | representation_spectral_knn | 0.355 | 0.839 |
| metabric | 5 | raw | 2.828 | 8 | 12 | raw_spectral_knn | 0.355 | 0.839 |
| metabric | 5 | raw | 15.811 | full | 250 | full_native_centroid | 0.440 | 1.000 |
| metabric | 5 | raw | 15.811 | full | 250 | full_native_knn_readout | 0.486 | 0.870 |
| metabric | 5 | raw | 15.811 | 8 | 250 | truncated_native_centroid | 0.418 | 0.902 |
| metabric | 5 | raw | 15.811 | 8 | 250 | refit_weighted_centroid | 0.396 | 0.870 |
| metabric | 5 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.396 | 0.870 |
| metabric | 5 | raw | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.418 | 0.839 |
| metabric | 5 | raw | 15.811 | 8 | 250 | representation_spectral_knn | 0.335 | 0.720 |
| metabric | 5 | raw | 15.811 | 8 | 250 | raw_spectral_knn | 0.335 | 0.720 |
| metabric | 5 | squared | 1.250 | full | 3 | full_native_centroid | 0.030 | 1.000 |
| metabric | 5 | squared | 1.250 | full | 3 | full_native_knn_readout | 0.024 | 0.958 |
| metabric | 5 | squared | 1.250 | 8 | 3 | truncated_native_centroid | 0.030 | 1.000 |
| metabric | 5 | squared | 1.250 | 8 | 3 | refit_weighted_centroid | 0.030 | 1.000 |
| metabric | 5 | squared | 1.250 | 8 | 3 | refit_unweighted_centroid | 0.003 | 0.665 |
| metabric | 5 | squared | 1.250 | 8 | 3 | refit_unweighted_centroid_knn | 0.003 | 0.665 |
| metabric | 5 | squared | 1.250 | 8 | 3 | representation_spectral_knn | -0.006 | 0.536 |
| metabric | 5 | squared | 1.250 | 8 | 3 | raw_spectral_knn | 0.335 | -0.000 |
| metabric | 5 | squared | 2.828 | full | 18 | full_native_centroid | -0.011 | 1.000 |
| metabric | 5 | squared | 2.828 | full | 18 | full_native_knn_readout | -0.016 | 0.877 |
| metabric | 5 | squared | 2.828 | 8 | 18 | truncated_native_centroid | -0.014 | 0.896 |
| metabric | 5 | squared | 2.828 | 8 | 18 | refit_weighted_centroid | -0.014 | 0.896 |
| metabric | 5 | squared | 2.828 | 8 | 18 | refit_unweighted_centroid | — | 0.546 |
| metabric | 5 | squared | 2.828 | 8 | 18 | refit_unweighted_centroid_knn | — | 0.000 |
| metabric | 5 | squared | 2.828 | 8 | 18 | representation_spectral_knn | -0.012 | 0.137 |
| metabric | 5 | squared | 2.828 | 8 | 18 | raw_spectral_knn | -0.006 | 0.087 |
| metabric | 5 | squared | 15.811 | full | 250 | full_native_centroid | 0.007 | 1.000 |
| metabric | 5 | squared | 15.811 | full | 250 | full_native_knn_readout | 0.001 | 0.882 |
| metabric | 5 | squared | 15.811 | 8 | 250 | truncated_native_centroid | 0.013 | 0.962 |
| metabric | 5 | squared | 15.811 | 8 | 250 | refit_weighted_centroid | 0.013 | 0.962 |
| metabric | 5 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid | 0.024 | 0.885 |
| metabric | 5 | squared | 15.811 | 8 | 250 | refit_unweighted_centroid_knn | 0.011 | 0.807 |
| metabric | 5 | squared | 15.811 | 8 | 250 | representation_spectral_knn | -0.010 | 0.667 |
| metabric | 5 | squared | 15.811 | 8 | 250 | raw_spectral_knn | 0.355 | -0.005 |
| shells | 3 | raw | 1.250 | full | 50 | full_native_centroid | -0.001 | 1.000 |
| shells | 3 | raw | 1.250 | full | 50 | full_native_knn_readout | 0.002 | 0.902 |
| shells | 3 | raw | 1.250 | 8 | 50 | truncated_native_centroid | -0.001 | 1.000 |
| shells | 3 | raw | 1.250 | 8 | 50 | refit_weighted_centroid | -0.001 | 0.934 |
| shells | 3 | raw | 1.250 | 8 | 50 | refit_unweighted_centroid | 0.005 | 0.082 |
| shells | 3 | raw | 1.250 | 8 | 50 | refit_unweighted_centroid_knn | -0.004 | 0.093 |
| shells | 3 | raw | 1.250 | 8 | 50 | representation_spectral_knn | -0.008 | 0.046 |
| shells | 3 | raw | 1.250 | 8 | 50 | raw_spectral_knn | -0.008 | 0.046 |
| shells | 3 | raw | 2.828 | full | 50 | full_native_centroid | -0.001 | 1.000 |
| shells | 3 | raw | 2.828 | full | 50 | full_native_knn_readout | -0.002 | 0.934 |
| shells | 3 | raw | 2.828 | 8 | 50 | truncated_native_centroid | -0.001 | 1.000 |
| shells | 3 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | -0.001 | 1.000 |
| shells | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.032 | 0.140 |
| shells | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.037 | 0.127 |
| shells | 3 | raw | 2.828 | 8 | 50 | representation_spectral_knn | 0.006 | 0.093 |
| shells | 3 | raw | 2.828 | 8 | 50 | raw_spectral_knn | 0.006 | 0.093 |
| shells | 3 | raw | 7.071 | full | 50 | full_native_centroid | -0.008 | 1.000 |
| shells | 3 | raw | 7.071 | full | 50 | full_native_knn_readout | -0.008 | 0.902 |
| shells | 3 | raw | 7.071 | 8 | 50 | truncated_native_centroid | -0.008 | 1.000 |
| shells | 3 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | -0.008 | 1.000 |
| shells | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.000 | 0.180 |
| shells | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.025 | 0.100 |
| shells | 3 | raw | 7.071 | 8 | 50 | representation_spectral_knn | 0.079 | 0.065 |
| shells | 3 | raw | 7.071 | 8 | 50 | raw_spectral_knn | 0.079 | 0.065 |
| shells | 3 | squared | 1.250 | full | 50 | full_native_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 1.250 | full | 50 | full_native_knn_readout | -0.002 | 0.942 |
| shells | 3 | squared | 1.250 | 8 | 50 | truncated_native_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 1.250 | 8 | 50 | refit_weighted_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 1.250 | 8 | 50 | refit_unweighted_centroid | -0.011 | 0.127 |
| shells | 3 | squared | 1.250 | 8 | 50 | refit_unweighted_centroid_knn | -0.015 | 0.164 |
| shells | 3 | squared | 1.250 | 8 | 50 | representation_spectral_knn | -0.008 | 0.256 |
| shells | 3 | squared | 1.250 | 8 | 50 | raw_spectral_knn | -0.001 | 0.004 |
| shells | 3 | squared | 2.828 | full | 50 | full_native_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 2.828 | full | 50 | full_native_knn_readout | -0.002 | 0.942 |
| shells | 3 | squared | 2.828 | 8 | 50 | truncated_native_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | 0.003 | 1.000 |
| shells | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | -0.011 | 0.127 |
| shells | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | -0.015 | 0.164 |
| shells | 3 | squared | 2.828 | 8 | 50 | representation_spectral_knn | -0.008 | 0.256 |
| shells | 3 | squared | 2.828 | 8 | 50 | raw_spectral_knn | -0.001 | 0.004 |
| shells | 3 | squared | 7.071 | full | 50 | full_native_centroid | 0.140 | 1.000 |
| shells | 3 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.140 | 1.000 |
| shells | 3 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.140 | 1.000 |
| shells | 3 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | 0.140 | 1.000 |
| shells | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.105 | -0.056 |
| shells | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.080 | -0.097 |
| shells | 3 | squared | 7.071 | 8 | 50 | representation_spectral_knn | 0.081 | 0.446 |
| shells | 3 | squared | 7.071 | 8 | 50 | raw_spectral_knn | 0.072 | 0.020 |
| shells | 4 | raw | 1.250 | full | 27 | full_native_centroid | -0.001 | 1.000 |
| shells | 4 | raw | 1.250 | full | 27 | full_native_knn_readout | -0.001 | 0.870 |
| shells | 4 | raw | 1.250 | 8 | 27 | truncated_native_centroid | -0.001 | 1.000 |
| shells | 4 | raw | 1.250 | 8 | 27 | refit_weighted_centroid | -0.001 | 1.000 |
| shells | 4 | raw | 1.250 | 8 | 27 | refit_unweighted_centroid | 0.010 | 0.093 |
| shells | 4 | raw | 1.250 | 8 | 27 | refit_unweighted_centroid_knn | 0.020 | 0.140 |
| shells | 4 | raw | 1.250 | 8 | 27 | representation_spectral_knn | 0.020 | 0.196 |
| shells | 4 | raw | 1.250 | 8 | 27 | raw_spectral_knn | 0.020 | 0.196 |
| shells | 4 | raw | 2.828 | full | 50 | full_native_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 2.828 | full | 50 | full_native_knn_readout | -0.008 | 0.967 |
| shells | 4 | raw | 2.828 | 8 | 50 | truncated_native_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | -0.001 | 0.140 |
| shells | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | -0.008 | 0.073 |
| shells | 4 | raw | 2.828 | 8 | 50 | representation_spectral_knn | -0.003 | 0.034 |
| shells | 4 | raw | 2.828 | 8 | 50 | raw_spectral_knn | -0.003 | 0.034 |
| shells | 4 | raw | 7.071 | full | 50 | full_native_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 7.071 | full | 50 | full_native_knn_readout | -0.008 | 1.000 |
| shells | 4 | raw | 7.071 | 8 | 50 | truncated_native_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | -0.008 | 1.000 |
| shells | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | -0.001 | 0.140 |
| shells | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | -0.008 | 0.073 |
| shells | 4 | raw | 7.071 | 8 | 50 | representation_spectral_knn | -0.003 | 0.034 |
| shells | 4 | raw | 7.071 | 8 | 50 | raw_spectral_knn | -0.003 | 0.034 |
| shells | 4 | squared | 1.250 | full | 28 | full_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 1.250 | full | 28 | full_native_knn_readout | 0.011 | 0.961 |
| shells | 4 | squared | 1.250 | 8 | 28 | truncated_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 1.250 | 8 | 28 | refit_weighted_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 1.250 | 8 | 28 | refit_unweighted_centroid | 0.015 | 0.258 |
| shells | 4 | squared | 1.250 | 8 | 28 | refit_unweighted_centroid_knn | 0.033 | 0.277 |
| shells | 4 | squared | 1.250 | 8 | 28 | representation_spectral_knn | -0.003 | -0.068 |
| shells | 4 | squared | 1.250 | 8 | 28 | raw_spectral_knn | -0.001 | -0.017 |
| shells | 4 | squared | 2.828 | full | 50 | full_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 2.828 | full | 50 | full_native_knn_readout | 0.011 | 0.961 |
| shells | 4 | squared | 2.828 | 8 | 50 | truncated_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.015 | 0.258 |
| shells | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.033 | 0.277 |
| shells | 4 | squared | 2.828 | 8 | 50 | representation_spectral_knn | -0.003 | -0.068 |
| shells | 4 | squared | 2.828 | 8 | 50 | raw_spectral_knn | -0.001 | -0.017 |
| shells | 4 | squared | 7.071 | full | 50 | full_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.011 | 0.961 |
| shells | 4 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | 0.007 | 1.000 |
| shells | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.015 | 0.258 |
| shells | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.033 | 0.277 |
| shells | 4 | squared | 7.071 | 8 | 50 | representation_spectral_knn | -0.003 | -0.068 |
| shells | 4 | squared | 7.071 | 8 | 50 | raw_spectral_knn | -0.001 | -0.017 |
| shells | 5 | raw | 1.250 | full | 19 | full_native_centroid | -0.001 | 1.000 |
| shells | 5 | raw | 1.250 | full | 19 | full_native_knn_readout | 0.002 | 0.902 |
| shells | 5 | raw | 1.250 | 8 | 19 | truncated_native_centroid | -0.001 | 1.000 |
| shells | 5 | raw | 1.250 | 8 | 19 | refit_weighted_centroid | -0.001 | 1.000 |
| shells | 5 | raw | 1.250 | 8 | 19 | refit_unweighted_centroid | 0.002 | 0.375 |
| shells | 5 | raw | 1.250 | 8 | 19 | refit_unweighted_centroid_knn | -0.007 | 0.261 |
| shells | 5 | raw | 1.250 | 8 | 19 | representation_spectral_knn | 0.001 | 0.039 |
| shells | 5 | raw | 1.250 | 8 | 19 | raw_spectral_knn | 0.001 | 0.039 |
| shells | 5 | raw | 2.828 | full | 50 | full_native_centroid | -0.006 | 1.000 |
| shells | 5 | raw | 2.828 | full | 50 | full_native_knn_readout | -0.006 | 0.934 |
| shells | 5 | raw | 2.828 | 8 | 50 | truncated_native_centroid | -0.006 | 1.000 |
| shells | 5 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | -0.006 | 1.000 |
| shells | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | -0.007 | 0.297 |
| shells | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | -0.008 | 0.297 |
| shells | 5 | raw | 2.828 | 8 | 50 | representation_spectral_knn | -0.008 | 0.355 |
| shells | 5 | raw | 2.828 | 8 | 50 | raw_spectral_knn | -0.008 | 0.355 |
| shells | 5 | raw | 7.071 | full | 50 | full_native_centroid | -0.007 | 1.000 |
| shells | 5 | raw | 7.071 | full | 50 | full_native_knn_readout | -0.008 | 0.778 |
| shells | 5 | raw | 7.071 | 8 | 50 | truncated_native_centroid | -0.007 | 1.000 |
| shells | 5 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | -0.007 | 1.000 |
| shells | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | -0.008 | 0.261 |
| shells | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.014 | 0.167 |
| shells | 5 | raw | 7.071 | 8 | 50 | representation_spectral_knn | 0.005 | 0.026 |
| shells | 5 | raw | 7.071 | 8 | 50 | raw_spectral_knn | 0.005 | 0.026 |
| shells | 5 | squared | 1.250 | full | 32 | full_native_centroid | -0.008 | 1.000 |
| shells | 5 | squared | 1.250 | full | 32 | full_native_knn_readout | -0.001 | 0.865 |
| shells | 5 | squared | 1.250 | 8 | 32 | truncated_native_centroid | -0.008 | 1.000 |
| shells | 5 | squared | 1.250 | 8 | 32 | refit_weighted_centroid | -0.008 | 1.000 |
| shells | 5 | squared | 1.250 | 8 | 32 | refit_unweighted_centroid | -0.010 | 0.579 |
| shells | 5 | squared | 1.250 | 8 | 32 | refit_unweighted_centroid_knn | -0.001 | 0.628 |
| shells | 5 | squared | 1.250 | 8 | 32 | representation_spectral_knn | 0.053 | -0.054 |
| shells | 5 | squared | 1.250 | 8 | 32 | raw_spectral_knn | -0.006 | 0.068 |
| shells | 5 | squared | 2.828 | full | 50 | full_native_centroid | 0.029 | 1.000 |
| shells | 5 | squared | 2.828 | full | 50 | full_native_knn_readout | 0.029 | 1.000 |
| shells | 5 | squared | 2.828 | 8 | 50 | truncated_native_centroid | 0.029 | 1.000 |
| shells | 5 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | 0.029 | 1.000 |
| shells | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | 0.008 | 0.367 |
| shells | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | 0.006 | 0.484 |
| shells | 5 | squared | 2.828 | 8 | 50 | representation_spectral_knn | 0.029 | -0.095 |
| shells | 5 | squared | 2.828 | 8 | 50 | raw_spectral_knn | 0.002 | -0.015 |
| shells | 5 | squared | 7.071 | full | 50 | full_native_centroid | 0.002 | 1.000 |
| shells | 5 | squared | 7.071 | full | 50 | full_native_knn_readout | 0.002 | 1.000 |
| shells | 5 | squared | 7.071 | 8 | 50 | truncated_native_centroid | 0.002 | 1.000 |
| shells | 5 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | -0.001 | 0.951 |
| shells | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | 0.036 | 0.552 |
| shells | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | 0.001 | 0.452 |
| shells | 5 | squared | 7.071 | 8 | 50 | representation_spectral_knn | 0.011 | -0.040 |
| shells | 5 | squared | 7.071 | 8 | 50 | raw_spectral_knn | -0.007 | 0.058 |
| null_independent | 3 | raw | 1.250 | full | 17 | full_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 1.250 | full | 17 | full_native_knn_readout | — | 0.967 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | truncated_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | refit_weighted_centroid | — | 1.000 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | refit_unweighted_centroid | — | 0.153 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | refit_unweighted_centroid_knn | — | 0.140 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | representation_spectral_knn | — | 0.181 |
| null_independent | 3 | raw | 1.250 | 8 | 17 | raw_spectral_knn | — | 0.181 |
| null_independent | 3 | raw | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 2.828 | full | 50 | full_native_knn_readout | — | 0.839 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.181 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.227 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | representation_spectral_knn | — | 0.227 |
| null_independent | 3 | raw | 2.828 | 8 | 50 | raw_spectral_knn | — | 0.227 |
| null_independent | 3 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.839 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.181 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.227 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.227 |
| null_independent | 3 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.227 |
| null_independent | 3 | squared | 1.250 | full | 34 | full_native_centroid | — | 1.000 |
| null_independent | 3 | squared | 1.250 | full | 34 | full_native_knn_readout | — | 0.678 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | truncated_native_centroid | — | 0.951 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | refit_weighted_centroid | — | 0.951 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | refit_unweighted_centroid | — | 0.097 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | refit_unweighted_centroid_knn | — | 0.171 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | representation_spectral_knn | — | -0.037 |
| null_independent | 3 | squared | 1.250 | 8 | 34 | raw_spectral_knn | — | 0.011 |
| null_independent | 3 | squared | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 3 | squared | 2.828 | full | 50 | full_native_knn_readout | — | 1.000 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.305 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.300 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | representation_spectral_knn | — | -0.021 |
| null_independent | 3 | squared | 2.828 | 8 | 50 | raw_spectral_knn | — | -0.004 |
| null_independent | 3 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 3 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.830 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.830 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.369 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.315 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.069 |
| null_independent | 3 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | -0.005 |
| null_independent | 4 | raw | 1.250 | full | 30 | full_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 1.250 | full | 30 | full_native_knn_readout | — | 0.934 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | refit_unweighted_centroid | — | 0.181 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | refit_unweighted_centroid_knn | — | 0.093 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | representation_spectral_knn | — | 0.063 |
| null_independent | 4 | raw | 1.250 | 8 | 30 | raw_spectral_knn | — | 0.063 |
| null_independent | 4 | raw | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 2.828 | full | 50 | full_native_knn_readout | — | 0.934 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.244 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.261 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | representation_spectral_knn | — | 0.355 |
| null_independent | 4 | raw | 2.828 | 8 | 50 | raw_spectral_knn | — | 0.355 |
| null_independent | 4 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.934 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.244 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.211 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.103 |
| null_independent | 4 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.103 |
| null_independent | 4 | squared | 1.250 | full | 25 | full_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 1.250 | full | 25 | full_native_knn_readout | — | 0.918 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | refit_unweighted_centroid | — | 0.482 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | refit_unweighted_centroid_knn | — | 0.458 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | representation_spectral_knn | — | -0.105 |
| null_independent | 4 | squared | 1.250 | 8 | 25 | raw_spectral_knn | — | -0.013 |
| null_independent | 4 | squared | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 2.828 | full | 50 | full_native_knn_readout | — | 1.000 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.174 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.265 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | representation_spectral_knn | — | 0.020 |
| null_independent | 4 | squared | 2.828 | 8 | 50 | raw_spectral_knn | — | -0.016 |
| null_independent | 4 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.843 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.171 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.112 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.039 |
| null_independent | 4 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | -0.004 |
| null_independent | 5 | raw | 1.250 | full | 23 | full_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 1.250 | full | 23 | full_native_knn_readout | — | 0.902 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | refit_weighted_centroid | — | 1.000 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | refit_unweighted_centroid | — | 0.140 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | refit_unweighted_centroid_knn | — | 0.115 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | representation_spectral_knn | — | 0.197 |
| null_independent | 5 | raw | 1.250 | 8 | 23 | raw_spectral_knn | — | 0.197 |
| null_independent | 5 | raw | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 2.828 | full | 50 | full_native_knn_readout | — | 0.808 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.063 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.140 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | representation_spectral_knn | — | 0.127 |
| null_independent | 5 | raw | 2.828 | 8 | 50 | raw_spectral_knn | — | 0.127 |
| null_independent | 5 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.967 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 1.000 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.039 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.073 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.128 |
| null_independent | 5 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.128 |
| null_independent | 5 | squared | 1.250 | full | 35 | full_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 1.250 | full | 35 | full_native_knn_readout | — | 0.963 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | refit_weighted_centroid | — | 1.000 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | refit_unweighted_centroid | — | 0.501 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | refit_unweighted_centroid_knn | — | 0.426 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | representation_spectral_knn | — | 0.031 |
| null_independent | 5 | squared | 1.250 | 8 | 35 | raw_spectral_knn | — | 0.070 |
| null_independent | 5 | squared | 2.828 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 2.828 | full | 50 | full_native_knn_readout | — | 0.930 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | refit_weighted_centroid | — | 0.965 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid | — | 0.588 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.511 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | representation_spectral_knn | — | 0.212 |
| null_independent | 5 | squared | 2.828 | 8 | 50 | raw_spectral_knn | — | -0.006 |
| null_independent | 5 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.896 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 1.000 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.965 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.588 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.511 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.212 |
| null_independent | 5 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | -0.006 |
| null_correlated | 3 | raw | 1.250 | full | 4 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | raw | 1.250 | full | 4 | full_native_knn_readout | — | 0.967 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | truncated_native_centroid | — | 1.000 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | refit_unweighted_centroid | — | 0.584 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | refit_unweighted_centroid_knn | — | 0.584 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | representation_spectral_knn | — | 0.584 |
| null_correlated | 3 | raw | 1.250 | 8 | 4 | raw_spectral_knn | — | 0.584 |
| null_correlated | 3 | raw | 2.828 | full | 13 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | raw | 2.828 | full | 13 | full_native_knn_readout | — | 0.934 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | truncated_native_centroid | — | 0.902 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | refit_weighted_centroid | — | 0.902 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | refit_unweighted_centroid | — | 0.839 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | refit_unweighted_centroid_knn | — | 0.778 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | representation_spectral_knn | — | 0.808 |
| null_correlated | 3 | raw | 2.828 | 8 | 13 | raw_spectral_knn | — | 0.808 |
| null_correlated | 3 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.839 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.870 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.839 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.839 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.870 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.870 |
| null_correlated | 3 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.870 |
| null_correlated | 3 | squared | 1.250 | full | 4 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | squared | 1.250 | full | 4 | full_native_knn_readout | — | 0.822 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | truncated_native_centroid | — | 1.000 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid | — | 0.658 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid_knn | — | 0.648 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | representation_spectral_knn | — | 0.501 |
| null_correlated | 3 | squared | 1.250 | 8 | 4 | raw_spectral_knn | — | -0.004 |
| null_correlated | 3 | squared | 2.828 | full | 15 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | squared | 2.828 | full | 15 | full_native_knn_readout | — | 0.769 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | truncated_native_centroid | — | 0.888 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | refit_weighted_centroid | — | 0.888 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | refit_unweighted_centroid | — | 0.962 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | refit_unweighted_centroid_knn | — | 0.807 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | representation_spectral_knn | — | 0.781 |
| null_correlated | 3 | squared | 2.828 | 8 | 15 | raw_spectral_knn | — | -0.006 |
| null_correlated | 3 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 3 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.745 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.653 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.683 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.683 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.709 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.749 |
| null_correlated | 3 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | -0.005 |
| null_correlated | 4 | raw | 1.250 | full | 3 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | raw | 1.250 | full | 3 | full_native_knn_readout | — | 0.967 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | truncated_native_centroid | — | 1.000 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid | — | 0.610 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | refit_unweighted_centroid_knn | — | 0.692 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | representation_spectral_knn | — | 0.637 |
| null_correlated | 4 | raw | 1.250 | 8 | 3 | raw_spectral_knn | — | 0.637 |
| null_correlated | 4 | raw | 2.828 | full | 13 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | raw | 2.828 | full | 13 | full_native_knn_readout | — | 0.934 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | truncated_native_centroid | — | 0.967 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | refit_weighted_centroid | — | 0.967 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | refit_unweighted_centroid | — | 0.967 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | refit_unweighted_centroid_knn | — | 0.934 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | representation_spectral_knn | — | 0.902 |
| null_correlated | 4 | raw | 2.828 | 8 | 13 | raw_spectral_knn | — | 0.902 |
| null_correlated | 4 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.967 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.778 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.778 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.778 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.720 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.692 |
| null_correlated | 4 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.692 |
| null_correlated | 4 | squared | 1.250 | full | 3 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | squared | 1.250 | full | 3 | full_native_knn_readout | — | 0.843 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | truncated_native_centroid | — | 1.000 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | refit_unweighted_centroid | — | 0.627 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | refit_unweighted_centroid_knn | — | 0.474 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | representation_spectral_knn | — | 0.532 |
| null_correlated | 4 | squared | 1.250 | 8 | 3 | raw_spectral_knn | — | 0.007 |
| null_correlated | 4 | squared | 2.828 | full | 12 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | squared | 2.828 | full | 12 | full_native_knn_readout | — | 0.889 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | truncated_native_centroid | — | 0.895 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | refit_weighted_centroid | — | 0.895 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | refit_unweighted_centroid | — | 0.847 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | refit_unweighted_centroid_knn | — | 0.889 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | representation_spectral_knn | — | 0.403 |
| null_correlated | 4 | squared | 2.828 | 8 | 12 | raw_spectral_knn | — | -0.002 |
| null_correlated | 4 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 4 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.589 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.706 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.706 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.706 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.686 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.696 |
| null_correlated | 4 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.001 |
| null_correlated | 5 | raw | 1.250 | full | 2 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | raw | 1.250 | full | 2 | full_native_knn_readout | — | 1.000 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | truncated_native_centroid | — | 1.000 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | refit_unweighted_centroid | — | 0.534 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | refit_unweighted_centroid_knn | — | 0.559 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | representation_spectral_knn | — | 0.559 |
| null_correlated | 5 | raw | 1.250 | 8 | 2 | raw_spectral_knn | — | 0.559 |
| null_correlated | 5 | raw | 2.828 | full | 14 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | raw | 2.828 | full | 14 | full_native_knn_readout | — | 0.902 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | truncated_native_centroid | — | 1.000 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | refit_unweighted_centroid | — | 0.902 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | refit_unweighted_centroid_knn | — | 0.902 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | representation_spectral_knn | — | 0.902 |
| null_correlated | 5 | raw | 2.828 | 8 | 14 | raw_spectral_knn | — | 0.902 |
| null_correlated | 5 | raw | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | raw | 7.071 | full | 50 | full_native_knn_readout | — | 0.808 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.839 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.839 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.839 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.808 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.808 |
| null_correlated | 5 | raw | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.808 |
| null_correlated | 5 | squared | 1.250 | full | 4 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | squared | 1.250 | full | 4 | full_native_knn_readout | — | 1.000 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | truncated_native_centroid | — | 1.000 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | refit_weighted_centroid | — | 1.000 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid | — | 0.736 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | refit_unweighted_centroid_knn | — | 0.781 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | representation_spectral_knn | — | 0.619 |
| null_correlated | 5 | squared | 1.250 | 8 | 4 | raw_spectral_knn | — | 0.006 |
| null_correlated | 5 | squared | 2.828 | full | 12 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | squared | 2.828 | full | 12 | full_native_knn_readout | — | 0.839 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | truncated_native_centroid | — | 0.951 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | refit_weighted_centroid | — | 0.951 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | refit_unweighted_centroid | — | 0.900 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | refit_unweighted_centroid_knn | — | 0.854 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | representation_spectral_knn | — | 0.819 |
| null_correlated | 5 | squared | 2.828 | 8 | 12 | raw_spectral_knn | — | 0.077 |
| null_correlated | 5 | squared | 7.071 | full | 50 | full_native_centroid | — | 1.000 |
| null_correlated | 5 | squared | 7.071 | full | 50 | full_native_knn_readout | — | 0.830 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | truncated_native_centroid | — | 0.656 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | refit_weighted_centroid | — | 0.656 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid | — | 0.656 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | refit_unweighted_centroid_knn | — | 0.695 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | representation_spectral_knn | — | 0.811 |
| null_correlated | 5 | squared | 7.071 | 8 | 50 | raw_spectral_knn | — | 0.070 |

Test-only centroid refitting on fixed panels is reported in case files. It checks replication of a fixed panel, not independent rediscovery of its features. Stability of this forced split is not a cluster-existence test.

## Compression

Teacher = original spectral partition with frozen kNN assignment. Same-panel family = the policy's full-panel model before deletion. The refit policy replaces the model family before deleting anything; that change and deletion must be judged separately. ARI 0.95 is not 95% assignment agreement. The foldwise criterion is a sensitivity check, not a confidence bound.

| Case | Seed | Method | Deletion policy | Size before → after | Teacher test ARI | Same-panel family ARI | Reduced test ARI | Val disagreements | Test disagreements | Test fidelity ARI |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| levine | 0 | soft_graph | frozen_knn_ari | 4 → 2 | 0.967 | 0.967 | 0.967 | 0.008 | 0.000 | 1.000 |
| levine | 0 | soft_graph | frozen_knn_disagreement | 4 → 1 | 0.967 | 0.967 | 0.967 | 0.025 | 0.000 | 1.000 |
| levine | 0 | soft_graph | frozen_knn_foldwise_disagreement | 4 → 1 | 0.967 | 0.967 | 0.967 | 0.025 | 0.000 | 1.000 |
| levine | 0 | soft_graph | refit_kmeans_disagreement | 4 → 1 | 0.967 | 0.934 | 1.000 | 0.017 | 0.008 | 0.967 |
| levine | 0 | sparse_kmeans | frozen_knn_ari | 4 → 2 | 0.967 | 0.967 | 0.967 | 0.008 | 0.000 | 1.000 |
| levine | 0 | sparse_kmeans | frozen_knn_disagreement | 4 → 1 | 0.967 | 0.967 | 0.967 | 0.025 | 0.000 | 1.000 |
| levine | 0 | sparse_kmeans | frozen_knn_foldwise_disagreement | 4 → 1 | 0.967 | 0.967 | 0.967 | 0.025 | 0.000 | 1.000 |
| levine | 0 | sparse_kmeans | refit_kmeans_disagreement | 4 → 1 | 0.967 | 0.934 | 1.000 | 0.017 | 0.008 | 0.967 |
| levine | 1 | soft_graph | frozen_knn_ari | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | soft_graph | frozen_knn_disagreement | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | soft_graph | frozen_knn_foldwise_disagreement | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | soft_graph | refit_kmeans_disagreement | 1 → 1 | 0.967 | 0.934 | 0.934 | 0.008 | 0.025 | 0.902 |
| levine | 1 | sparse_kmeans | frozen_knn_ari | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | sparse_kmeans | frozen_knn_disagreement | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | sparse_kmeans | frozen_knn_foldwise_disagreement | 1 → 1 | 0.967 | 0.967 | 0.967 | 0.000 | 0.000 | 1.000 |
| levine | 1 | sparse_kmeans | refit_kmeans_disagreement | 1 → 1 | 0.967 | 0.934 | 0.934 | 0.008 | 0.025 | 0.902 |
| levine | 2 | soft_graph | frozen_knn_ari | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | soft_graph | frozen_knn_disagreement | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | soft_graph | frozen_knn_foldwise_disagreement | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | soft_graph | refit_kmeans_disagreement | 1 → 1 | 0.934 | 0.870 | 0.870 | 0.008 | 0.017 | 0.934 |
| levine | 2 | sparse_kmeans | frozen_knn_ari | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | sparse_kmeans | frozen_knn_disagreement | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | sparse_kmeans | frozen_knn_foldwise_disagreement | 1 → 1 | 0.934 | 0.934 | 0.934 | 0.000 | 0.000 | 1.000 |
| levine | 2 | sparse_kmeans | refit_kmeans_disagreement | 1 → 1 | 0.934 | 0.870 | 0.870 | 0.008 | 0.017 | 0.934 |
| mean_shift | 0 | soft_graph | frozen_knn_ari | 8 → 8 | 0.749 | 0.749 | 0.749 | 0.000 | 0.000 | 1.000 |
| mean_shift | 0 | soft_graph | frozen_knn_disagreement | 8 → 4 | 0.749 | 0.749 | 0.584 | 0.050 | 0.100 | 0.637 |
| mean_shift | 0 | soft_graph | frozen_knn_foldwise_disagreement | 8 → 5 | 0.749 | 0.749 | 0.720 | 0.042 | 0.042 | 0.839 |
| mean_shift | 0 | soft_graph | refit_kmeans_disagreement | 8 → 5 | 0.749 | 0.778 | 0.808 | 0.042 | 0.050 | 0.808 |
| mean_shift | 0 | sparse_kmeans | frozen_knn_ari | 6 → 6 | 0.692 | 0.692 | 0.692 | 0.000 | 0.000 | 1.000 |
| mean_shift | 0 | sparse_kmeans | frozen_knn_disagreement | 6 → 3 | 0.692 | 0.692 | 0.559 | 0.050 | 0.075 | 0.720 |
| mean_shift | 0 | sparse_kmeans | frozen_knn_foldwise_disagreement | 6 → 4 | 0.692 | 0.692 | 0.584 | 0.017 | 0.033 | 0.870 |
| mean_shift | 0 | sparse_kmeans | refit_kmeans_disagreement | 6 → 6 | 0.692 | 0.778 | 0.778 | 0.083 | 0.042 | 0.839 |
| mean_shift | 1 | soft_graph | frozen_knn_ari | 7 → 7 | 0.749 | 0.749 | 0.749 | 0.000 | 0.000 | 1.000 |
| mean_shift | 1 | soft_graph | frozen_knn_disagreement | 7 → 5 | 0.749 | 0.749 | 0.808 | 0.025 | 0.017 | 0.934 |
| mean_shift | 1 | soft_graph | frozen_knn_foldwise_disagreement | 7 → 5 | 0.749 | 0.749 | 0.808 | 0.025 | 0.017 | 0.934 |
| mean_shift | 1 | soft_graph | refit_kmeans_disagreement | 7 → 4 | 0.749 | 0.808 | 0.720 | 0.042 | 0.092 | 0.664 |
| mean_shift | 1 | sparse_kmeans | frozen_knn_ari | 8 → 8 | 0.778 | 0.778 | 0.778 | 0.000 | 0.000 | 1.000 |
| mean_shift | 1 | sparse_kmeans | frozen_knn_disagreement | 8 → 5 | 0.778 | 0.778 | 0.664 | 0.042 | 0.100 | 0.637 |
| mean_shift | 1 | sparse_kmeans | frozen_knn_foldwise_disagreement | 8 → 6 | 0.778 | 0.778 | 0.637 | 0.033 | 0.092 | 0.664 |
| mean_shift | 1 | sparse_kmeans | refit_kmeans_disagreement | 8 → 4 | 0.778 | 0.870 | 0.720 | 0.050 | 0.083 | 0.692 |
| mean_shift | 2 | soft_graph | frozen_knn_ari | 8 → 8 | 0.637 | 0.637 | 0.637 | 0.000 | 0.000 | 1.000 |
| mean_shift | 2 | soft_graph | frozen_knn_disagreement | 8 → 5 | 0.637 | 0.637 | 0.510 | 0.033 | 0.092 | 0.664 |
| mean_shift | 2 | soft_graph | frozen_knn_foldwise_disagreement | 8 → 6 | 0.637 | 0.637 | 0.610 | 0.042 | 0.042 | 0.839 |
| mean_shift | 2 | soft_graph | refit_kmeans_disagreement | 8 → 5 | 0.637 | 0.808 | 0.808 | 0.050 | 0.067 | 0.749 |
| mean_shift | 2 | sparse_kmeans | frozen_knn_ari | 8 → 8 | 0.534 | 0.534 | 0.534 | 0.000 | 0.000 | 1.000 |
| mean_shift | 2 | sparse_kmeans | frozen_knn_disagreement | 8 → 4 | 0.534 | 0.534 | 0.720 | 0.025 | 0.108 | 0.610 |
| mean_shift | 2 | sparse_kmeans | frozen_knn_foldwise_disagreement | 8 → 6 | 0.534 | 0.534 | 0.486 | 0.033 | 0.100 | 0.637 |
| mean_shift | 2 | sparse_kmeans | refit_kmeans_disagreement | 8 → 6 | 0.534 | 0.778 | 0.584 | 0.042 | 0.100 | 0.637 |
| metabric | 0 | soft_graph | frozen_knn_ari | 7 → 5 | 0.316 | 0.316 | 0.279 | 0.008 | 0.050 | 0.808 |
| metabric | 0 | soft_graph | frozen_knn_disagreement | 7 → 3 | 0.316 | 0.316 | 0.297 | 0.025 | 0.042 | 0.839 |
| metabric | 0 | soft_graph | frozen_knn_foldwise_disagreement | 7 → 3 | 0.316 | 0.316 | 0.297 | 0.025 | 0.042 | 0.839 |
| metabric | 0 | soft_graph | refit_kmeans_disagreement | 7 → 2 | 0.316 | 0.355 | 0.315 | 0.033 | 0.100 | 0.637 |
| metabric | 0 | sparse_kmeans | frozen_knn_ari | 5 → 4 | 0.316 | 0.316 | 0.297 | 0.008 | 0.042 | 0.839 |
| metabric | 0 | sparse_kmeans | frozen_knn_disagreement | 5 → 2 | 0.316 | 0.316 | 0.127 | 0.042 | 0.183 | 0.396 |
| metabric | 0 | sparse_kmeans | frozen_knn_foldwise_disagreement | 5 → 3 | 0.316 | 0.316 | 0.227 | 0.017 | 0.092 | 0.663 |
| metabric | 0 | sparse_kmeans | refit_kmeans_disagreement | 5 → 2 | 0.316 | 0.316 | 0.244 | 0.042 | 0.150 | 0.486 |
| metabric | 1 | soft_graph | frozen_knn_ari | 8 → 8 | -0.008 | -0.008 | -0.008 | 0.000 | 0.000 | 1.000 |
| metabric | 1 | soft_graph | frozen_knn_disagreement | 8 → 7 | -0.008 | -0.008 | -0.009 | 0.042 | 0.042 | 0.832 |
| metabric | 1 | soft_graph | frozen_knn_foldwise_disagreement | 8 → 8 | -0.008 | -0.008 | -0.008 | 0.000 | 0.000 | 1.000 |
| metabric | 1 | soft_graph | refit_kmeans_disagreement | 8 → 8 | -0.008 | -0.002 | -0.002 | 0.183 | 0.150 | 0.484 |
| metabric | 1 | sparse_kmeans | frozen_knn_ari | 5 → 5 | 0.335 | 0.335 | 0.335 | 0.000 | 0.000 | 1.000 |
| metabric | 1 | sparse_kmeans | frozen_knn_disagreement | 5 → 2 | 0.335 | 0.335 | 0.486 | 0.033 | 0.075 | 0.720 |
| metabric | 1 | sparse_kmeans | frozen_knn_foldwise_disagreement | 5 → 2 | 0.335 | 0.335 | 0.486 | 0.033 | 0.075 | 0.720 |
| metabric | 1 | sparse_kmeans | refit_kmeans_disagreement | 5 → 2 | 0.335 | 0.354 | 0.375 | 0.042 | 0.083 | 0.692 |
| metabric | 2 | soft_graph | frozen_knn_ari | 5 → 5 | 0.047 | 0.047 | 0.047 | 0.000 | 0.000 | 1.000 |
| metabric | 2 | soft_graph | frozen_knn_disagreement | 5 → 1 | 0.047 | 0.047 | 0.020 | 0.050 | 0.117 | 0.584 |
| metabric | 2 | soft_graph | frozen_knn_foldwise_disagreement | 5 → 4 | 0.047 | 0.047 | 0.026 | 0.025 | 0.058 | 0.778 |
| metabric | 2 | soft_graph | refit_kmeans_disagreement | 5 → 2 | 0.047 | 0.040 | 0.055 | 0.042 | 0.058 | 0.778 |
| metabric | 2 | sparse_kmeans | frozen_knn_ari | 8 → 5 | 0.418 | 0.418 | 0.416 | 0.008 | 0.050 | 0.808 |
| metabric | 2 | sparse_kmeans | frozen_knn_disagreement | 8 → 3 | 0.418 | 0.418 | 0.316 | 0.033 | 0.075 | 0.720 |
| metabric | 2 | sparse_kmeans | frozen_knn_foldwise_disagreement | 8 → 3 | 0.418 | 0.418 | 0.316 | 0.033 | 0.075 | 0.720 |
| metabric | 2 | sparse_kmeans | refit_kmeans_disagreement | 8 → 2 | 0.418 | 0.375 | 0.417 | 0.042 | 0.067 | 0.749 |

Every single-feature deletion, validation trace, validity guard and cost is saved in each method's deletions file. External annotations never choose a deletion.

## Oracle geometry ability check

The true features are supplied here. This is a representation/splitter check, not feature discovery. The radius rule receives a radial inductive bias. Compare the separate autonomous squared-model retention results before claiming discoverability.

| Rows | Seed | Mapping | Splitter | Graph neighbors | Train ARI | Test ARI |
|---:|---:|---|---|---:|---:|---:|
| 480 | 3 | raw | spectral | 5 | 0.003 | 0.027 |
| 480 | 3 | raw | spectral | 10 | 0.021 | -0.007 |
| 480 | 3 | raw | spectral | 20 | 0.004 | -0.012 |
| 480 | 3 | squared | spectral | 5 | 1.000 | 1.000 |
| 480 | 3 | squared | spectral | 10 | 1.000 | 1.000 |
| 480 | 3 | squared | spectral | 20 | 1.000 | 1.000 |
| 480 | 3 | raw | centroid | — | 0.018 | -0.007 |
| 480 | 3 | squared | centroid | — | 0.750 | 0.808 |
| 480 | 3 | radius_squared | centroid | — | 1.000 | 1.000 |
| 480 | 4 | raw | spectral | 5 | -0.004 | 0.064 |
| 480 | 4 | raw | spectral | 10 | 0.000 | 0.026 |
| 480 | 4 | raw | spectral | 20 | 0.009 | 0.032 |
| 480 | 4 | squared | spectral | 5 | 1.000 | 1.000 |
| 480 | 4 | squared | spectral | 10 | 1.000 | 1.000 |
| 480 | 4 | squared | spectral | 20 | 1.000 | 1.000 |
| 480 | 4 | raw | centroid | — | 0.006 | 0.032 |
| 480 | 4 | squared | centroid | — | 0.299 | 0.279 |
| 480 | 4 | radius_squared | centroid | — | 1.000 | 1.000 |
| 480 | 5 | raw | spectral | 5 | -0.004 | -0.007 |
| 480 | 5 | raw | spectral | 10 | -0.003 | -0.002 |
| 480 | 5 | raw | spectral | 20 | -0.003 | -0.007 |
| 480 | 5 | squared | spectral | 5 | 1.000 | 1.000 |
| 480 | 5 | squared | spectral | 10 | 1.000 | 1.000 |
| 480 | 5 | squared | spectral | 20 | 1.000 | 1.000 |
| 480 | 5 | raw | centroid | — | 0.003 | 0.005 |
| 480 | 5 | squared | centroid | — | 0.511 | 0.534 |
| 480 | 5 | radius_squared | centroid | — | 1.000 | 1.000 |
| 960 | 3 | raw | spectral | 5 | 0.002 | 0.036 |
| 960 | 3 | raw | spectral | 10 | -0.002 | 0.014 |
| 960 | 3 | raw | spectral | 20 | 0.001 | 0.006 |
| 960 | 3 | squared | spectral | 5 | 1.000 | 1.000 |
| 960 | 3 | squared | spectral | 10 | 1.000 | 1.000 |
| 960 | 3 | squared | spectral | 20 | 1.000 | 1.000 |
| 960 | 3 | raw | centroid | — | -0.001 | 0.003 |
| 960 | 3 | squared | centroid | — | 0.736 | 0.736 |
| 960 | 3 | radius_squared | centroid | — | 1.000 | 1.000 |
| 960 | 4 | raw | spectral | 5 | -0.002 | -0.003 |
| 960 | 4 | raw | spectral | 10 | 0.001 | -0.000 |
| 960 | 4 | raw | spectral | 20 | -0.002 | -0.004 |
| 960 | 4 | squared | spectral | 5 | 1.000 | 1.000 |
| 960 | 4 | squared | spectral | 10 | 1.000 | 1.000 |
| 960 | 4 | squared | spectral | 20 | 1.000 | 1.000 |
| 960 | 4 | raw | centroid | — | 0.000 | -0.003 |
| 960 | 4 | squared | centroid | — | 0.606 | 0.561 |
| 960 | 4 | radius_squared | centroid | — | 1.000 | 1.000 |
| 960 | 5 | raw | spectral | 5 | 0.000 | 0.040 |
| 960 | 5 | raw | spectral | 10 | -0.002 | 0.004 |
| 960 | 5 | raw | spectral | 20 | 0.001 | 0.021 |
| 960 | 5 | squared | spectral | 5 | 1.000 | 1.000 |
| 960 | 5 | squared | spectral | 10 | 1.000 | 1.000 |
| 960 | 5 | squared | spectral | 20 | 1.000 | 1.000 |
| 960 | 5 | raw | centroid | — | 0.004 | 0.024 |
| 960 | 5 | squared | centroid | — | 0.626 | 0.666 |
| 960 | 5 | radius_squared | centroid | — | 1.000 | 1.000 |
| 1920 | 3 | raw | spectral | 5 | 0.930 | 0.926 |
| 1920 | 3 | raw | spectral | 10 | -0.001 | -0.002 |
| 1920 | 3 | raw | spectral | 20 | 0.000 | -0.001 |
| 1920 | 3 | squared | spectral | 5 | 1.000 | 1.000 |
| 1920 | 3 | squared | spectral | 10 | 1.000 | 1.000 |
| 1920 | 3 | squared | spectral | 20 | 1.000 | 1.000 |
| 1920 | 3 | raw | centroid | — | -0.001 | -0.002 |
| 1920 | 3 | squared | centroid | — | 0.684 | 0.680 |
| 1920 | 3 | radius_squared | centroid | — | 1.000 | 1.000 |
| 1920 | 4 | raw | spectral | 5 | 0.875 | 0.787 |
| 1920 | 4 | raw | spectral | 10 | 0.006 | -0.002 |
| 1920 | 4 | raw | spectral | 20 | 0.005 | -0.002 |
| 1920 | 4 | squared | spectral | 5 | 1.000 | 1.000 |
| 1920 | 4 | squared | spectral | 10 | 1.000 | 1.000 |
| 1920 | 4 | squared | spectral | 20 | 1.000 | 1.000 |
| 1920 | 4 | raw | centroid | — | 0.002 | -0.001 |
| 1920 | 4 | squared | centroid | — | 0.519 | 0.543 |
| 1920 | 4 | radius_squared | centroid | — | 1.000 | 1.000 |
| 1920 | 5 | raw | spectral | 5 | 0.963 | 0.951 |
| 1920 | 5 | raw | spectral | 10 | 0.021 | 0.015 |
| 1920 | 5 | raw | spectral | 20 | 0.009 | 0.004 |
| 1920 | 5 | squared | spectral | 5 | 1.000 | 1.000 |
| 1920 | 5 | squared | spectral | 10 | 1.000 | 1.000 |
| 1920 | 5 | squared | spectral | 20 | 1.000 | 1.000 |
| 1920 | 5 | raw | centroid | — | 0.002 | -0.001 |
| 1920 | 5 | squared | centroid | — | 0.367 | 0.395 |
| 1920 | 5 | radius_squared | centroid | — | 1.000 | 1.000 |
