# Feature-panel diagnostic results

These are prototype diagnostics. Search rows use no reference-panel seeds. Score-audit rows use a reference-augmented bank and must not be reported as discovery performance.

Test ARI below measures transferred discovery assignments. Search seconds include proposal optimization and panel scoring; shared reference setup and post-selection reporting are additional. Budgets do not imply equal compute.

| Case | Mode | p | s | Seed | Method / objective | Size → reduced | Best visited train ARI | Selected train ARI | Test ARI | Reduced test ARI | Search seconds |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| levine:cd4t_cd8t | score-audit | 32 |  | 0 | consistent/consistent | 5 → 3 | — | 0.967 | 0.967 | 0.967 | — |
| levine:cd4t_cd8t | score-audit | 32 |  | 0 | legacy/legacy | 1 → 1 | — | 0.021 | 0.181 | 0.181 | — |
| levine:cd4t_cd8t | score-audit | 32 |  | 0 | graphcut/graphcut | 1 → 1 | — | -0.005 | -0.008 | -0.008 | — |
| levine:cd4t_cd8t | score-audit | 32 |  | 0 | density/density | 5 → 4 | — | 0.870 | 0.934 | 0.870 | — |
| mean_shift | score-audit | 50 | 5 | 0 | consistent/consistent | 4 → 4 | — | 0.750 | 0.610 | 0.610 | — |
| mean_shift | score-audit | 50 | 5 | 0 | legacy/legacy | 4 → 4 | — | 0.693 | 0.584 | 0.584 | — |
| mean_shift | score-audit | 50 | 5 | 0 | graphcut/graphcut | 1 → 1 | — | 0.309 | 0.227 | 0.227 | — |
| mean_shift | score-audit | 50 | 5 | 0 | density/density | 8 → 8 | — | -0.004 | -0.007 | -0.007 | — |
| metabric:lumA_lumB | score-audit | 250 |  | 0 | consistent/consistent | 49 → 38 | — | 0.399 | 0.418 | 0.510 | — |
| metabric:lumA_lumB | score-audit | 250 |  | 0 | legacy/legacy | 1 → 1 | — | -0.005 | -0.007 | -0.007 | — |
| metabric:lumA_lumB | score-audit | 250 |  | 0 | graphcut/graphcut | 1 → 1 | — | 0.239 | 0.227 | 0.227 | — |
| metabric:lumA_lumB | score-audit | 250 |  | 0 | density/density | 49 → 38 | — | 0.399 | 0.418 | 0.510 | — |
| shells | score-audit | 50 | 5 | 0 | consistent/consistent | 5 → 5 | — | -0.001 | -0.005 | -0.005 | — |
| shells | score-audit | 50 | 5 | 0 | legacy/legacy | 1 → 1 | — | -0.003 | -0.006 | -0.006 | — |
| shells | score-audit | 50 | 5 | 0 | graphcut/graphcut | 1 → 1 | — | 0.002 | -0.008 | -0.008 | — |
| shells | score-audit | 50 | 5 | 0 | density/density | 8 → 8 | — | -0.004 | -0.011 | -0.011 | — |
| levine:cd4t_cd8t | search | 32 |  | 0 | random/consistent | 4 → 2 | 0.934 | 0.934 | 0.934 | 0.934 | 2.887 |
| levine:cd4t_cd8t | search | 32 |  | 0 | forward/consistent | 8 → 3 | 1.000 | 0.902 | 0.839 | 0.934 | 2.829 |
| levine:cd4t_cd8t | search | 32 |  | 0 | evolutionary/consistent | 5 → 3 | 0.967 | 0.967 | 0.967 | 1.000 | 2.812 |
| levine:cd4t_cd8t | search | 32 |  | 0 | soft_graph/consistent | 4 → 2 | 0.983 | 0.967 | 0.967 | 0.967 | 1.144 |
| levine:cd4t_cd8t | search | 32 |  | 0 | sparse_kmeans/consistent | 4 → 2 | 1.000 | 0.967 | 0.967 | 0.967 | 2.353 |
| levine:cd4t_cd8t | search | 32 |  | 1 | random/consistent | 1 → 1 | 0.983 | 0.983 | 0.967 | 0.967 | 2.893 |
| levine:cd4t_cd8t | search | 32 |  | 1 | forward/consistent | 7 → 1 | 0.967 | 0.950 | 0.967 | 0.967 | 2.806 |
| levine:cd4t_cd8t | search | 32 |  | 1 | evolutionary/consistent | 7 → 1 | 0.934 | 0.886 | 0.967 | 0.870 | 2.891 |
| levine:cd4t_cd8t | search | 32 |  | 1 | soft_graph/consistent | 1 → 1 | 0.983 | 0.983 | 0.967 | 0.967 | 1.223 |
| levine:cd4t_cd8t | search | 32 |  | 1 | sparse_kmeans/consistent | 1 → 1 | 0.983 | 0.983 | 0.967 | 0.967 | 1.486 |
| levine:cd4t_cd8t | search | 32 |  | 2 | random/consistent | 6 → 1 | 0.967 | 0.950 | 0.967 | 0.967 | 2.889 |
| levine:cd4t_cd8t | search | 32 |  | 2 | forward/consistent | 6 → 2 | 0.983 | 0.950 | 0.934 | 0.967 | 2.801 |
| levine:cd4t_cd8t | search | 32 |  | 2 | evolutionary/consistent | 1 → 1 | 0.983 | 0.967 | 0.934 | 0.934 | 2.802 |
| levine:cd4t_cd8t | search | 32 |  | 2 | soft_graph/consistent | 1 → 1 | 0.983 | 0.967 | 0.934 | 0.934 | 1.153 |
| levine:cd4t_cd8t | search | 32 |  | 2 | sparse_kmeans/consistent | 1 → 1 | 0.983 | 0.967 | 0.934 | 0.934 | 1.508 |
| mean_shift | search | 50 | 5 | 0 | random/consistent | 8 → 8 | 0.442 | 0.028 | 0.015 | 0.015 | 2.879 |
| mean_shift | search | 50 | 5 | 0 | forward/consistent | 8 → 8 | 0.347 | -0.007 | -0.009 | -0.009 | 2.877 |
| mean_shift | search | 50 | 5 | 0 | evolutionary/consistent | 8 → 8 | 0.638 | 0.586 | 0.396 | 0.396 | 2.880 |
| mean_shift | search | 50 | 5 | 0 | soft_graph/consistent | 8 → 8 | 0.779 | 0.765 | 0.749 | 0.749 | 1.331 |
| mean_shift | search | 50 | 5 | 0 | sparse_kmeans/consistent | 6 → 6 | 0.794 | 0.765 | 0.692 | 0.692 | 1.117 |
| mean_shift | search | 50 | 5 | 1 | random/consistent | 8 → 7 | 0.442 | 0.000 | 0.023 | 0.018 | 2.896 |
| mean_shift | search | 50 | 5 | 1 | forward/consistent | 8 → 8 | 0.488 | 0.199 | 0.140 | 0.140 | 2.896 |
| mean_shift | search | 50 | 5 | 1 | evolutionary/consistent | 6 → 6 | 0.536 | 0.309 | 0.227 | 0.227 | 2.957 |
| mean_shift | search | 50 | 5 | 1 | soft_graph/consistent | 7 → 7 | 0.721 | 0.693 | 0.749 | 0.749 | 1.175 |
| mean_shift | search | 50 | 5 | 1 | sparse_kmeans/consistent | 8 → 8 | 0.750 | 0.693 | 0.778 | 0.778 | 1.731 |
| mean_shift | search | 50 | 5 | 2 | random/consistent | 4 → 4 | 0.612 | 0.599 | 0.418 | 0.418 | 2.884 |
| mean_shift | search | 50 | 5 | 2 | forward/consistent | 8 → 8 | 0.420 | 0.347 | 0.355 | 0.355 | 2.913 |
| mean_shift | search | 50 | 5 | 2 | evolutionary/consistent | 4 → 4 | 0.524 | 0.465 | 0.181 | 0.181 | 2.838 |
| mean_shift | search | 50 | 5 | 2 | soft_graph/consistent | 8 → 8 | 0.779 | 0.750 | 0.637 | 0.637 | 1.374 |
| mean_shift | search | 50 | 5 | 2 | sparse_kmeans/consistent | 8 → 8 | 0.765 | 0.707 | 0.534 | 0.534 | 1.097 |
| metabric:lumA_lumB | search | 250 |  | 0 | random/consistent | 5 → 1 | 0.396 | -0.014 | -0.001 | -0.001 | 2.936 |
| metabric:lumA_lumB | search | 250 |  | 0 | forward/consistent | 6 → 4 | 0.192 | -0.023 | 0.005 | 0.005 | 2.924 |
| metabric:lumA_lumB | search | 250 |  | 0 | evolutionary/consistent | 7 → 7 | 0.378 | -0.008 | -0.002 | -0.002 | 2.914 |
| metabric:lumA_lumB | search | 250 |  | 0 | soft_graph/consistent | 7 → 5 | 0.431 | 0.357 | 0.316 | 0.279 | 1.641 |
| metabric:lumA_lumB | search | 250 |  | 0 | sparse_kmeans/consistent | 5 → 4 | 0.453 | 0.409 | 0.316 | 0.297 | 2.028 |
| metabric:lumA_lumB | search | 250 |  | 1 | random/consistent | 8 → 4 | 0.465 | -0.017 | 0.001 | 0.001 | 2.905 |
| metabric:lumA_lumB | search | 250 |  | 1 | forward/consistent | 7 → 4 | 0.290 | 0.021 | 0.007 | 0.006 | 2.921 |
| metabric:lumA_lumB | search | 250 |  | 1 | evolutionary/consistent | 6 → 6 | 0.453 | 0.091 | 0.244 | 0.244 | 2.931 |
| metabric:lumA_lumB | search | 250 |  | 1 | soft_graph/consistent | 8 → 8 | 0.561 | -0.003 | -0.008 | -0.008 | 1.594 |
| metabric:lumA_lumB | search | 250 |  | 1 | sparse_kmeans/consistent | 5 → 5 | 0.512 | 0.476 | 0.335 | 0.335 | 1.384 |
| metabric:lumA_lumB | search | 250 |  | 2 | random/consistent | 3 → 3 | 0.440 | 0.041 | 0.059 | 0.059 | 2.912 |
| metabric:lumA_lumB | search | 250 |  | 2 | forward/consistent | 8 → 8 | 0.357 | -0.002 | -0.018 | -0.018 | 2.928 |
| metabric:lumA_lumB | search | 250 |  | 2 | evolutionary/consistent | 2 → 2 | 0.406 | 0.182 | 0.194 | 0.194 | 2.890 |
| metabric:lumA_lumB | search | 250 |  | 2 | soft_graph/consistent | 5 → 5 | 0.095 | 0.005 | 0.047 | 0.047 | 1.754 |
| metabric:lumA_lumB | search | 250 |  | 2 | sparse_kmeans/consistent | 8 → 5 | 0.573 | 0.573 | 0.418 | 0.416 | 2.769 |
| shells | search | 50 | 5 | 0 | random/consistent | 1 → 1 | 0.023 | 0.023 | -0.004 | -0.004 | 2.906 |
| shells | search | 50 | 5 | 0 | forward/consistent | 6 → 6 | 0.023 | -0.008 | -0.005 | -0.005 | 2.886 |
| shells | search | 50 | 5 | 0 | evolutionary/consistent | 7 → 7 | 0.016 | 0.002 | 0.019 | 0.019 | 2.853 |
| shells | search | 50 | 5 | 0 | soft_graph/consistent | 2 → 2 | 0.011 | -0.004 | -0.008 | -0.008 | 1.253 |
| shells | search | 50 | 5 | 0 | sparse_kmeans/consistent | 7 → 7 | 0.021 | -0.005 | 0.000 | 0.000 | 2.929 |
| shells | search | 50 | 5 | 1 | random/consistent | 7 → 7 | 0.021 | 0.001 | -0.007 | -0.007 | 2.885 |
| shells | search | 50 | 5 | 1 | forward/consistent | 7 → 7 | 0.016 | -0.004 | -0.004 | -0.004 | 2.868 |
| shells | search | 50 | 5 | 1 | evolutionary/consistent | 6 → 6 | 0.032 | -0.005 | -0.005 | -0.005 | 2.835 |
| shells | search | 50 | 5 | 1 | soft_graph/consistent | 6 → 6 | 0.016 | -0.002 | -0.002 | -0.002 | 1.177 |
| shells | search | 50 | 5 | 1 | sparse_kmeans/consistent | 2 → 2 | 0.010 | 0.006 | -0.006 | -0.006 | 2.952 |
| shells | search | 50 | 5 | 2 | random/consistent | 4 → 4 | 0.037 | -0.003 | -0.000 | -0.000 | 2.894 |
| shells | search | 50 | 5 | 2 | forward/consistent | 1 → 1 | 0.036 | -0.004 | -0.004 | -0.004 | 2.895 |
| shells | search | 50 | 5 | 2 | evolutionary/consistent | 2 → 2 | 0.037 | 0.000 | -0.008 | -0.008 | 2.911 |
| shells | search | 50 | 5 | 2 | soft_graph/consistent | 5 → 5 | 0.031 | -0.001 | 0.006 | 0.006 | 1.194 |
| shells | search | 50 | 5 | 2 | sparse_kmeans/consistent | 4 → 4 | 0.039 | -0.003 | -0.006 | -0.006 | 2.956 |

## Fixed-panel dependence controls

Both p-values concern independence, not the absence of clusters.

| Case | Seed | Graphcut independence p | Correlation independence p |
|---|---:|---:|---:|
| bimodal | 0 | 1.000 | 1.000 |
| null_correlated | 0 | 0.100 | 0.025 |
| null_independent | 0 | 0.700 | 0.350 |

Inspect each run's candidate records, reference diagnostics, rule fidelity and manifest before drawing conclusions. Seed-to-seed variation is not independent cohort replication.
