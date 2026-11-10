# Fixed-panel readout comparison

Posthoc development check on the same observations. Centroid and identity-graph models use only discovery rows and fixed panels. All results are reported; no winner is selected. Exact rules describe the centroid model itself, not the original kernel assignment.

| Case | Seed | Panel source | Features | Native ARI | Centroid ARI | Identity ARI | Centroid/kernel disagreement |
|---|---:|---|---:|---:|---:|---:|---:|
| mean_shift | 26 | rank_preserved_pca | 16 | 0.545 | 0.591 | 0.575 | 0.035 |
| mean_shift | 26 | rank_preserved_optimized | 16 | 0.575 | 0.704 | 0.622 | 0.060 |
| grouped_moons | 26 | rank_preserved_pca | 16 | 0.545 | 0.502 | 0.502 | 0.015 |
| grouped_moons | 26 | rank_preserved_optimized | 16 | 0.560 | 0.516 | 0.516 | 0.015 |
| null_independent | 26 | rank_preserved_pca | 16 | — | — | — | 0.120 |
| null_independent | 26 | rank_preserved_optimized | 16 | — | — | — | 0.115 |
| null_correlated | 26 | rank_preserved_pca | 16 | — | — | — | 0.000 |
| null_correlated | 26 | rank_preserved_optimized | 16 | — | — | — | 0.175 |
| mean_shift | 27 | rank_preserved_pca | 16 | 0.545 | 0.591 | 0.531 | 0.025 |
| mean_shift | 27 | rank_preserved_optimized | 16 | 0.575 | 0.738 | 0.671 | 0.050 |
| grouped_moons | 27 | rank_preserved_pca | 16 | 0.687 | 0.575 | 0.591 | 0.035 |
| grouped_moons | 27 | rank_preserved_optimized | 16 | 0.654 | 0.575 | 0.575 | 0.035 |
| null_independent | 27 | rank_preserved_pca | 16 | — | — | — | 0.145 |
| null_independent | 27 | rank_preserved_optimized | 16 | — | — | — | 0.040 |
| null_correlated | 27 | rank_preserved_pca | 16 | — | — | — | 0.030 |
| null_correlated | 27 | rank_preserved_optimized | 16 | — | — | — | 0.045 |
| mean_shift | 28 | rank_preserved_pca | 16 | 0.671 | 0.622 | 0.704 | 0.035 |
| mean_shift | 28 | rank_preserved_optimized | 16 | 0.704 | 0.756 | 0.704 | 0.025 |
| grouped_moons | 28 | rank_preserved_pca | 16 | 0.446 | 0.420 | 0.407 | 0.010 |
| grouped_moons | 28 | rank_preserved_optimized | 16 | 0.433 | 0.420 | 0.407 | 0.035 |
| null_independent | 28 | rank_preserved_pca | 16 | — | — | — | 0.245 |
| null_independent | 28 | rank_preserved_optimized | 16 | — | — | — | 0.250 |
| null_correlated | 28 | rank_preserved_pca | 16 | — | — | — | 0.005 |
| null_correlated | 28 | rank_preserved_optimized | 16 | — | — | — | 0.035 |
