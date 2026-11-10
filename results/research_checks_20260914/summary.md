# Feature-panel diagnostic results

These are prototype diagnostics. Search rows use no reference-panel seeds. Score-audit rows use a reference-augmented bank and must not be reported as discovery performance.

Test ARI below measures transferred discovery assignments. Search seconds include proposal optimization and panel scoring; shared reference setup and post-selection reporting are additional. Budgets do not imply equal compute.

| Case | Mode | p | s | Seed | Method / objective | Size → reduced | Best visited train ARI | Selected train ARI | Test ARI | Reduced test ARI | Search seconds |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| mean_shift | score-audit | 24 | 5 | 0 | consistent/consistent | 4 → 4 | — | 0.692 | 0.869 | 0.869 | — |
| mean_shift | score-audit | 24 | 5 | 0 | legacy/legacy | 4 → 4 | — | 0.692 | 0.869 | 0.869 | — |
| mean_shift | score-audit | 24 | 5 | 0 | graphcut/graphcut | 1 → 1 | — | 0.261 | 0.310 | 0.310 | — |
| mean_shift | score-audit | 24 | 5 | 0 | density/density | 4 → 4 | — | 0.692 | 0.869 | 0.869 | — |
| shells | score-audit | 24 | 5 | 0 | consistent/consistent | 4 → 4 | — | 0.024 | -0.017 | -0.017 | — |
| shells | score-audit | 24 | 5 | 0 | legacy/legacy | 1 → 1 | — | -0.004 | 0.001 | 0.001 | — |
| shells | score-audit | 24 | 5 | 0 | graphcut/graphcut | 1 → 1 | — | -0.001 | 0.001 | 0.001 | — |
| shells | score-audit | 24 | 5 | 0 | density/density | 8 → 8 | — | 0.001 | -0.013 | -0.013 | — |
| levine:cd4t_cd8t | search | 32 |  | 0 | random/consistent | 5 → 2 | 0.718 | 0.718 | 0.344 | 0.715 | 0.187 |
| levine:cd4t_cd8t | search | 32 |  | 0 | forward/consistent | 2 → 2 | 0.449 | 0.352 | 0.408 | 0.408 | 0.185 |
| levine:cd4t_cd8t | search | 32 |  | 0 | evolutionary/consistent | 1 → 1 | 0.950 | 0.950 | 1.000 | 1.000 | 0.196 |
| levine:cd4t_cd8t | search | 32 |  | 0 | soft_graph/consistent | 5 → 4 | 0.854 | 0.808 | 1.000 | 1.000 | 0.224 |
| levine:cd4t_cd8t | search | 32 |  | 0 | sparse_kmeans/consistent | 5 → 5 | 0.854 | 0.408 | 0.232 | 0.232 | 0.216 |
| metabric:lumA_lumB | search | 250 |  | 0 | random/consistent | 3 → 3 | 0.436 | 0.127 | 0.096 | 0.096 | 0.445 |
| metabric:lumA_lumB | search | 250 |  | 0 | forward/consistent | 4 → 4 | 0.082 | -0.004 | 0.001 | 0.001 | 0.464 |
| metabric:lumA_lumB | search | 250 |  | 0 | evolutionary/consistent | 2 → 2 | 0.459 | -0.009 | -0.016 | -0.016 | 0.442 |
| metabric:lumA_lumB | search | 250 |  | 0 | soft_graph/consistent | 7 → 3 | 0.396 | -0.009 | -0.013 | -0.013 | 0.542 |
| metabric:lumA_lumB | search | 250 |  | 0 | sparse_kmeans/consistent | 8 → 7 | 0.418 | -0.004 | 0.024 | 0.011 | 0.499 |

## Fixed-panel dependence controls

Both p-values concern independence, not the absence of clusters.

| Case | Seed | Graphcut independence p | Correlation independence p |
|---|---:|---:|---:|
| bimodal | 0 | 1.000 | 1.000 |
| null_correlated | 0 | 0.100 | 0.050 |
| null_independent | 0 | 0.350 | 0.500 |

Inspect each run's candidate records, reference diagnostics, rule fidelity and manifest before drawing conclusions. Seed-to-seed variation is not independent cohort replication.
