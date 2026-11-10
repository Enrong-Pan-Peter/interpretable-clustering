# Obstacle diagnostics

All configurations are prescribed and reported; no test-ARI winner is selected. Fresh seeds on real data are resamples of the same cohort. Compression reuses the inspected pilot. These are development diagnostics, not evidence of a novel validated method.

Full native support can exceed the feature-prefix cap. Squared coordinates are squared discovery-standardized original features, then standardized again on discovery rows. Each original feature is counted once.

The compact table shows the largest prescribed prefix and the full models. Every smaller prefix, feature name, assignment and geometry score is retained in case files. Showing a prefix here does not select it as best.

## Model retention and single-population controls

ARI compares to external annotations, when available. Fidelity compares test assignments to the full native model, which itself may be wrong. Invalid discovery partitions have blank external ARI. Controls have no external ARI or accepted/rejected status: the procedure always proposes a split.

| Case | Seed | Mapping | L1 bound | Prefix size | Full support | Assignment | Test ARI | Fidelity ARI |
|---|---:|---|---:|---:|---:|---|---:|---:|
| mean_shift | 17 | raw | 1.250 | full | 2 | full_native_centroid | 0.461 | 1.000 |
| mean_shift | 17 | raw | 1.250 | full | 2 | full_native_knn_readout | 0.325 | 0.799 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | truncated_native_centroid | 0.461 | 1.000 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | refit_weighted_centroid | 0.461 | 1.000 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | refit_unweighted_centroid | 0.461 | 0.616 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | refit_unweighted_centroid_knn | 0.620 | 0.461 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | representation_spectral_knn | 0.620 | 0.461 |
| mean_shift | 17 | raw | 1.250 | 4 | 2 | raw_spectral_knn | 0.620 | 0.461 |
| mean_shift | 17 | raw | 2.000 | full | 6 | full_native_centroid | 0.620 | 1.000 |
| mean_shift | 17 | raw | 2.000 | full | 6 | full_native_knn_readout | 0.620 | 1.000 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | truncated_native_centroid | 0.620 | 1.000 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | refit_weighted_centroid | 0.620 | 1.000 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | refit_unweighted_centroid | 0.463 | 0.800 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | refit_unweighted_centroid_knn | 0.463 | 0.800 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | representation_spectral_knn | 0.463 | 0.800 |
| mean_shift | 17 | raw | 2.000 | 4 | 6 | raw_spectral_knn | 0.463 | 0.800 |
| mean_shift | 17 | raw | 2.828 | full | 8 | full_native_centroid | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | full | 8 | full_native_knn_readout | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | truncated_native_centroid | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | refit_weighted_centroid | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | refit_unweighted_centroid | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | refit_unweighted_centroid_knn | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | representation_spectral_knn | 0.463 | 1.000 |
| mean_shift | 17 | raw | 2.828 | 4 | 8 | raw_spectral_knn | 0.463 | 1.000 |
| mean_shift | 17 | squared | 1.250 | full | 8 | full_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 1.250 | full | 8 | full_native_knn_readout | — | 0.000 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | truncated_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | refit_weighted_centroid | — | 1.000 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | refit_unweighted_centroid | -0.062 | 0.190 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | refit_unweighted_centroid_knn | -0.074 | -0.070 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | representation_spectral_knn | -0.062 | 0.190 |
| mean_shift | 17 | squared | 1.250 | 4 | 8 | raw_spectral_knn | -0.055 | 0.085 |
| mean_shift | 17 | squared | 2.000 | full | 8 | full_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.000 | full | 8 | full_native_knn_readout | — | 0.000 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | truncated_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | refit_weighted_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | refit_unweighted_centroid | -0.062 | 0.190 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | refit_unweighted_centroid_knn | -0.074 | -0.070 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | representation_spectral_knn | -0.062 | 0.190 |
| mean_shift | 17 | squared | 2.000 | 4 | 8 | raw_spectral_knn | -0.055 | 0.085 |
| mean_shift | 17 | squared | 2.828 | full | 8 | full_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.828 | full | 8 | full_native_knn_readout | — | 0.000 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | truncated_native_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | refit_weighted_centroid | — | 1.000 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | refit_unweighted_centroid | -0.062 | 0.190 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | refit_unweighted_centroid_knn | -0.074 | -0.070 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | representation_spectral_knn | -0.062 | 0.190 |
| mean_shift | 17 | squared | 2.828 | 4 | 8 | raw_spectral_knn | -0.055 | 0.085 |

Test-only centroid refitting on fixed panels is reported in case files. It checks replication of a fixed panel, not independent rediscovery of its features. Stability of this forced split is not a cluster-existence test.

