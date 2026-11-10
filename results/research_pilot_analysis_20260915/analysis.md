# Pilot audit and aggregates

Completed jobs: 19; source hash configurations: 1; summed job time: 196.2s.

All numbers below are descriptive across three seeds. Same-method test ARI means transferred discovery labels. Candidate generation and scalar selection had no access to reference labels. Best-visited ARI is retrospective and training-only.

| Dataset | Method | Mean test ARI [range] | Mean best-visited train ARI | Mean selected train ARI | Mean panel size | Mean candidates | Mean search seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| levine | evolutionary | 0.956 [0.934, 0.967] | 0.961 | 0.940 | 4.3 | 100.0 | 2.83 |
| levine | forward | 0.913 [0.839, 0.967] | 0.983 | 0.934 | 7.0 | 100.0 | 2.81 |
| levine | random | 0.956 [0.934, 0.967] | 0.961 | 0.956 | 3.7 | 100.0 | 2.89 |
| levine | soft_graph | 0.956 [0.934, 0.967] | 0.983 | 0.972 | 2.0 | 31.3 | 1.17 |
| levine | sparse_kmeans | 0.956 [0.934, 0.967] | 0.989 | 0.972 | 2.0 | 59.7 | 1.78 |
| mean_shift | evolutionary | 0.268 [0.181, 0.396] | 0.566 | 0.453 | 6.0 | 100.0 | 2.89 |
| mean_shift | forward | 0.162 [-0.009, 0.355] | 0.418 | 0.180 | 8.0 | 100.0 | 2.90 |
| mean_shift | random | 0.152 [0.015, 0.418] | 0.499 | 0.209 | 6.7 | 100.0 | 2.89 |
| mean_shift | soft_graph | 0.712 [0.637, 0.749] | 0.760 | 0.736 | 7.7 | 35.0 | 1.29 |
| mean_shift | sparse_kmeans | 0.668 [0.534, 0.778] | 0.770 | 0.722 | 7.3 | 43.3 | 1.32 |
| metabric | evolutionary | 0.145 [-0.002, 0.244] | 0.412 | 0.089 | 5.0 | 100.0 | 2.91 |
| metabric | forward | -0.002 [-0.018, 0.007] | 0.280 | -0.001 | 7.0 | 100.0 | 2.92 |
| metabric | random | 0.019 [-0.001, 0.059] | 0.433 | 0.003 | 5.3 | 100.0 | 2.92 |
| metabric | soft_graph | 0.118 [-0.008, 0.316] | 0.362 | 0.120 | 6.7 | 44.7 | 1.66 |
| metabric | sparse_kmeans | 0.356 [0.316, 0.418] | 0.513 | 0.486 | 6.0 | 65.7 | 2.06 |
| shells | evolutionary | 0.002 [-0.008, 0.019] | 0.028 | -0.001 | 5.0 | 100.0 | 2.87 |
| shells | forward | -0.004 [-0.005, -0.004] | 0.025 | -0.005 | 4.7 | 100.0 | 2.88 |
| shells | random | -0.004 [-0.007, -0.000] | 0.027 | 0.007 | 4.0 | 100.0 | 2.90 |
| shells | soft_graph | -0.001 [-0.008, 0.006] | 0.020 | -0.002 | 4.3 | 31.3 | 1.21 |
| shells | sparse_kmeans | -0.004 [-0.006, 0.000] | 0.023 | -0.001 | 4.3 | 100.0 | 2.95 |

## Compression failures on confirmation rows

Validation required ARI >= .95 to the full-panel rule. The following accepted reductions fell below .95 on test rows; this is not a 95% point-agreement requirement.

| Dataset | Method | Seed | Test compression fidelity | Full → reduced test label ARI |
|---|---|---:|---:|---:|
| levine | evolutionary | 1 | 0.839 | 0.967 → 0.870 |
| levine | forward | 0 | 0.902 | 0.839 → 0.934 |
| levine | forward | 1 | 0.934 | 0.967 → 0.967 |
| levine | forward | 2 | 0.902 | 0.934 → 0.967 |
| levine | random | 2 | 0.934 | 0.967 → 0.967 |
| mean_shift | random | 1 | 0.616 | 0.023 → 0.018 |
| metabric | forward | 0 | 0.570 | 0.005 → 0.005 |
| metabric | forward | 1 | 0.448 | 0.007 → 0.006 |
| metabric | random | 1 | 0.647 | 0.001 → 0.001 |
| metabric | soft_graph | 0 | 0.808 | 0.316 → 0.279 |
| metabric | sparse_kmeans | 0 | 0.839 | 0.316 → 0.297 |
| metabric | sparse_kmeans | 2 | 0.808 | 0.418 → 0.416 |

## Integrity

Missing default pilot cases: []
Duplicate cases: []
Failed or incomplete: []
Runs with current source mismatches: 0

The JSON includes per-run manifests and source checks. New analysis modules are not part of the historical manifest; edits to recorded modules would be reported as mismatches.
