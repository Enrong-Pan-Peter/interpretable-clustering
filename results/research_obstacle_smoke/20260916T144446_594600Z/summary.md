# Obstacle diagnostics

All configurations are prescribed and reported; no test-ARI winner is selected. Fresh seeds on real data are resamples of the same cohort. Compression reuses the inspected pilot. These are development diagnostics, not evidence of a novel validated method.

Full native support can exceed the feature-prefix cap. Squared coordinates are squared discovery-standardized original features, then standardized again on discovery rows. Each original feature is counted once.

The compact table shows the largest prescribed prefix and the full models. Every smaller prefix, feature name, assignment and geometry score is retained in case files. Showing a prefix here does not select it as best.

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
| metabric | 0 | soft_graph | frozen_knn_ari | 7 → 5 | 0.316 | 0.316 | 0.279 | 0.008 | 0.050 | 0.808 |
| metabric | 0 | soft_graph | frozen_knn_disagreement | 7 → 3 | 0.316 | 0.316 | 0.297 | 0.025 | 0.042 | 0.839 |
| metabric | 0 | soft_graph | frozen_knn_foldwise_disagreement | 7 → 3 | 0.316 | 0.316 | 0.297 | 0.025 | 0.042 | 0.839 |
| metabric | 0 | soft_graph | refit_kmeans_disagreement | 7 → 2 | 0.316 | 0.355 | 0.315 | 0.033 | 0.100 | 0.637 |
| metabric | 0 | sparse_kmeans | frozen_knn_ari | 5 → 4 | 0.316 | 0.316 | 0.297 | 0.008 | 0.042 | 0.839 |
| metabric | 0 | sparse_kmeans | frozen_knn_disagreement | 5 → 2 | 0.316 | 0.316 | 0.127 | 0.042 | 0.183 | 0.396 |
| metabric | 0 | sparse_kmeans | frozen_knn_foldwise_disagreement | 5 → 3 | 0.316 | 0.316 | 0.227 | 0.017 | 0.092 | 0.663 |
| metabric | 0 | sparse_kmeans | refit_kmeans_disagreement | 5 → 2 | 0.316 | 0.316 | 0.244 | 0.042 | 0.150 | 0.486 |

Every single-feature deletion, validation trace, validity guard and cost is saved in each method's deletions file. External annotations never choose a deletion.

