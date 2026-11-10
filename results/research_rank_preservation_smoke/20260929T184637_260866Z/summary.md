# Rank-preservation development followup

This reuses the kernel pilot rows and labels for diagnostic reporting. It is not independent confirmation. No winner is chosen and no cluster-existence test is implemented. Native prediction, panel size and tree fidelity stay separate.

| Dataset | Seed | Kernel | Variant | Status | Test ARI | Val graph loss | Sigma2/sigma1 | Features | Tree error |
|---|---:|---|---|---|---:|---:|---:|---:|---:|
| mean_shift | 26 | local | original_pca | complete | 0.530 | 0.320 | 0.615 | 16 | 0.190 |
| mean_shift | 26 | local | saved_unconstrained | complete | -0.001 | 0.341 | 0.436 | 16 | 0.260 |
| mean_shift | 26 | local | rank_preserved_pca | complete | 0.530 | 0.404 | 1.000 | 16 | 0.190 |
| mean_shift | 26 | local | rank_preserved_optimized | complete | 0.516 | 0.422 | 1.000 | 16 | 0.190 |
| mean_shift | 26 | global | original_pca | complete | 0.575 | 0.534 | 0.615 | 16 | 0.195 |
| mean_shift | 26 | global | saved_unconstrained | complete | 0.276 | 0.611 | 0.000 | 16 | 0.290 |
| mean_shift | 26 | global | rank_preserved_pca | complete | 0.545 | 0.669 | 1.000 | 16 | 0.195 |
| mean_shift | 26 | global | rank_preserved_optimized | complete | 0.545 | 0.662 | 1.000 | 16 | 0.205 |
