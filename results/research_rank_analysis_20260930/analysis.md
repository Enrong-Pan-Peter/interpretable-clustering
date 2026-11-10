# Rank-preservation audit

Descriptive paired development results, three seeds. Repeated execution is not new data. Verification replays native assignment and saved tree metrics; it does not verify exported tree text. No clustering fits.

19013 checks, 0 discrepancies, 192 saved models.

| Case | Kernel | Model | Test ARI | Validation loss | Recall | Tree error | Sizes |
|---|---|---|---:|---:|---:|---:|---|
| mean_shift | local | original_pca | 0.563 | 0.306 | 0.778 | 0.238 | [16, 16, 16] |
| mean_shift | local | saved_unconstrained | 0.331 | 0.303 | 0.500 | 0.263 | [16, 16, 16] |
| mean_shift | local | rank_preserved_pca | 0.588 | 0.434 | 0.778 | 0.263 | [16, 16, 16] |
| mean_shift | local | rank_preserved_optimized | 0.561 | 0.427 | 0.778 | 0.205 | [16, 16, 16] |
| mean_shift | global | original_pca | 0.570 | 0.529 | 0.778 | 0.242 | [16, 16, 16] |
| mean_shift | global | saved_unconstrained | 0.519 | 0.542 | 0.806 | 0.257 | [16, 16, 16] |
| mean_shift | global | rank_preserved_pca | 0.587 | 0.671 | 0.778 | 0.243 | [16, 16, 16] |
| mean_shift | global | rank_preserved_optimized | 0.618 | 0.607 | 0.944 | 0.273 | [16, 16, 16] |
| grouped_moons | local | original_pca | 0.569 | 0.383 | 1.000 | 0.053 | [16, 16, 16] |
| grouped_moons | local | saved_unconstrained | 0.502 | 0.282 | 0.733 | 0.087 | [16, 16, 16] |
| grouped_moons | local | rank_preserved_pca | 0.569 | 0.399 | 1.000 | 0.060 | [16, 16, 16] |
| grouped_moons | local | rank_preserved_optimized | 0.552 | 0.358 | 1.000 | 0.053 | [16, 16, 16] |
| grouped_moons | global | original_pca | 0.560 | 0.270 | 1.000 | 0.065 | [16, 16, 16] |
| grouped_moons | global | saved_unconstrained | 0.524 | 0.193 | 1.000 | 0.060 | [16, 16, 16] |
| grouped_moons | global | rank_preserved_pca | 0.560 | 0.289 | 1.000 | 0.057 | [16, 16, 16] |
| grouped_moons | global | rank_preserved_optimized | 0.549 | 0.254 | 1.000 | 0.060 | [16, 16, 16] |
| null_independent | local | original_pca | — | 0.830 | — | 0.360 | [16, 16, 16] |
| null_independent | local | saved_unconstrained | — | 0.328 | — | 0.350 | [16, 16, 16] |
| null_independent | local | rank_preserved_pca | — | 0.853 | — | 0.342 | [16, 16, 16] |
| null_independent | local | rank_preserved_optimized | — | 0.853 | — | 0.312 | [16, 16, 16] |
| null_independent | global | original_pca | — | 0.931 | — | 0.313 | [16, 16, 16] |
| null_independent | global | saved_unconstrained | — | 0.664 | — | 0.377 | [16, 16, 16] |
| null_independent | global | rank_preserved_pca | — | 0.944 | — | 0.310 | [16, 16, 16] |
| null_independent | global | rank_preserved_optimized | — | 0.958 | — | 0.308 | [16, 16, 16] |
| null_correlated | local | original_pca | — | 0.311 | — | 0.083 | [16, 16, 16] |
| null_correlated | local | saved_unconstrained | — | 0.337 | — | 0.107 | [16, 16, 16] |
| null_correlated | local | rank_preserved_pca | — | 0.314 | — | 0.082 | [16, 16, 16] |
| null_correlated | local | rank_preserved_optimized | — | 0.330 | — | 0.105 | [16, 16, 16] |
| null_correlated | global | original_pca | — | 0.520 | — | 0.085 | [16, 16, 16] |
| null_correlated | global | saved_unconstrained | — | 0.508 | — | 0.100 | [16, 16, 16] |
| null_correlated | global | rank_preserved_pca | — | 0.494 | — | 0.102 | [16, 16, 16] |
| null_correlated | global | rank_preserved_optimized | — | 0.519 | — | 0.112 | [16, 16, 16] |
