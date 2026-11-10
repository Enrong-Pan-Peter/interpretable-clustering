# Sparse kernel projection development experiment

All prespecified variants are reported. No annotation-based choice of panels, restarts, kernel, rank or winner. Every model proposes two groups; even valid/stable negative-control splits are not evidence of clusters. A local affinity is a graph kernel here, not a claim of a positive-semidefinite Mercer kernel.

The rank-two sample projection is an experimental extension, NOT a reproduction of GroupFS's feature embedding. Tree rules are approximations; fidelity is separate from ARI. Support budgets are upper bounds, not certified minimal sizes.

| Case | Seed | Budget | Variant | Status | Features | Test ARI | Same-panel identity ARI | Tree disagreement | Planted recall |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| grouped_moons | 91 | 6 | diagonal_cut_local | complete | 6 | 0.522 | — | 0.033 | 1.000 |
| grouped_moons | 91 | 6 | diagonal_gap_local | complete | 6 | 0.522 | — | 0.000 | 0.667 |
| grouped_moons | 91 | 6 | projection_cut_local | complete | 6 | 0.427 | 0.627 | 0.067 | 1.000 |
| grouped_moons | 91 | 6 | projection_gap_local | complete | 6 | 0.341 | 0.627 | 0.100 | 1.000 |
| grouped_moons | 91 | 6 | projection_gap_global | complete | 6 | 0.521 | 0.627 | 0.033 | 1.000 |
| grouped_moons | 91 | 6 | all_features_local | complete | 12 | 0.521 | — | 0.067 | 1.000 |

Per-case reports also include supplied-panel geometry diagnostics and ordinary k-means. Oracles must never be counted as autonomous performance. Full model files, split indices, native/tree predictions, test embeddings and readable approximate rules are retained. No numerical SOTA claim is supported by this suite.
