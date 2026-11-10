# Native panel replication

Sparse two-means is an established baseline. This experiment preserves its assignment rule, independently fits two discovery samples, and shortens each rule using a training-only prefix ladder. It does not test whether clusters exist or establish novelty.

Empirical: observed validation disagreement <= the prescribed tolerance. Bounded: one-sided Clopper–Pearson upper disagreement <= tolerance, with Bonferroni across at most 2*cap prefixes in a case. Conditional on fixed discovery fits and independent identically distributed validation rows, this controls the family of fidelity bounds; it does not cover cluster truth, independent cohorts, all suite cases jointly, or future tuning.

## Each learner and selected panel

Missing bounded panels are reported, not replaced with a favorable candidate. Test error can exceed the tolerance by sampling variation even when a population-risk bound holds; a single test exceedance is not proof of bound failure.

| Case | p | Planted | Seed | Learner | Policy | Full support | Selected size | Val error | Val upper | Test error | Full test ARI | Selected test ARI | Supplied-panel oracle ARI |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mean_shift | 50 | 5 | 6 | A | empirical | 50 | 4 | 0.025 | 0.077 | 0.005 | 0.773 | 0.756 | 0.791 |
| mean_shift | 50 | 5 | 6 | A | bounded | 50 | 5 | 0.005 | 0.043 | 0.000 | 0.773 | 0.773 | 0.791 |
| mean_shift | 50 | 5 | 6 | B | empirical | 50 | 4 | 0.030 | 0.085 | 0.020 | 0.773 | 0.704 | 0.791 |
| mean_shift | 50 | 5 | 6 | B | bounded | 50 | 5 | 0.000 | 0.032 | 0.000 | 0.773 | 0.773 | 0.791 |
| mean_shift | 50 | 8 | 6 | A | empirical | 50 | 5 | 0.035 | 0.092 | 0.030 | 0.704 | 0.638 | 0.756 |
| mean_shift | 50 | 8 | 6 | A | bounded | 50 | 9 | 0.000 | 0.032 | 0.010 | 0.704 | 0.704 | 0.756 |
| mean_shift | 50 | 8 | 6 | B | empirical | 50 | 6 | 0.015 | 0.061 | 0.040 | 0.622 | 0.591 | 0.756 |
| mean_shift | 50 | 8 | 6 | B | bounded | 50 | 8 | 0.000 | 0.032 | 0.000 | 0.622 | 0.622 | 0.756 |
| mean_shift | 50 | 12 | 6 | A | empirical | 50 | 7 | 0.035 | 0.092 | 0.050 | 0.560 | 0.473 | 0.721 |
| mean_shift | 50 | 12 | 6 | A | bounded | 50 | 11 | 0.000 | 0.032 | 0.000 | 0.560 | 0.560 | 0.721 |
| mean_shift | 50 | 12 | 6 | B | empirical | 50 | 7 | 0.050 | 0.113 | 0.050 | 0.591 | 0.560 | 0.654 |
| mean_shift | 50 | 12 | 6 | B | bounded | 50 | 16 | 0.005 | 0.043 | 0.010 | 0.591 | 0.622 | 0.654 |
| mean_shift | 200 | 5 | 6 | A | empirical | 200 | 1 | 0.020 | 0.069 | 0.030 | -0.003 | -0.005 | 0.791 |
| mean_shift | 200 | 5 | 6 | A | bounded | 200 | 6 | 0.005 | 0.043 | 0.015 | -0.003 | -0.004 | 0.791 |
| mean_shift | 200 | 5 | 6 | B | empirical | 200 | 4 | 0.020 | 0.069 | 0.065 | 0.756 | 0.606 | 0.773 |
| mean_shift | 200 | 5 | 6 | B | bounded | 200 | 7 | 0.005 | 0.043 | 0.000 | 0.756 | 0.756 | 0.773 |
| mean_shift | 200 | 8 | 6 | A | empirical | 200 | 1 | 0.045 | 0.106 | 0.040 | -0.004 | -0.004 | 0.791 |
| mean_shift | 200 | 8 | 6 | A | bounded | 200 | none | — | — | — | -0.004 | — | 0.791 |
| mean_shift | 200 | 8 | 6 | B | empirical | 200 | 3 | 0.030 | 0.085 | 0.060 | 0.369 | 0.256 | 0.773 |
| mean_shift | 200 | 8 | 6 | B | bounded | 200 | 6 | 0.005 | 0.043 | 0.015 | 0.369 | 0.333 | 0.773 |
| mean_shift | 200 | 12 | 6 | A | empirical | 200 | 1 | 0.010 | 0.052 | 0.010 | 0.001 | -0.001 | 0.704 |
| mean_shift | 200 | 12 | 6 | A | bounded | 200 | none | — | — | — | 0.001 | — | 0.704 |
| mean_shift | 200 | 12 | 6 | B | empirical | 200 | 1 | 0.020 | 0.069 | 0.020 | 0.085 | 0.063 | 0.704 |
| mean_shift | 200 | 12 | 6 | B | bounded | 200 | 2 | 0.005 | 0.043 | 0.015 | 0.085 | 0.092 | 0.704 |
| metabric | 250 | — | 6 | A | empirical | 20 | 2 | 0.035 | 0.092 | 0.085 | 0.487 | 0.419 | — |
| metabric | 250 | — | 6 | A | bounded | 20 | 10 | 0.005 | 0.043 | 0.040 | 0.487 | 0.406 | — |
| metabric | 250 | — | 6 | B | empirical | 20 | 3 | 0.040 | 0.099 | 0.045 | 0.473 | 0.459 | — |
| metabric | 250 | — | 6 | B | bounded | 20 | none | — | — | — | 0.473 | — | — |
| null_independent | 200 | — | 6 | A | empirical | 200 | 1 | 0.040 | 0.099 | 0.045 | — | — | — |
| null_independent | 200 | — | 6 | A | bounded | 200 | none | — | — | — | — | — | — |
| null_independent | 200 | — | 6 | B | empirical | 200 | 1 | 0.020 | 0.069 | 0.025 | — | — | — |
| null_independent | 200 | — | 6 | B | bounded | 200 | 2 | 0.005 | 0.043 | 0.030 | — | — | — |
| null_correlated | 200 | — | 6 | A | empirical | 32 | 3 | 0.050 | 0.113 | 0.090 | — | — | — |
| null_correlated | 200 | — | 6 | A | bounded | 32 | 16 | 0.000 | 0.032 | 0.005 | — | — | — |
| null_correlated | 200 | — | 6 | B | empirical | 26 | 6 | 0.045 | 0.106 | 0.025 | — | — | — |
| null_correlated | 200 | — | 6 | B | bounded | 26 | 13 | 0.005 | 0.043 | 0.010 | — | — | — |
| mean_shift | 50 | 5 | 7 | A | empirical | 50 | 3 | 0.030 | 0.085 | 0.070 | 0.638 | 0.545 | 0.773 |
| mean_shift | 50 | 5 | 7 | A | bounded | 50 | 5 | 0.000 | 0.032 | 0.010 | 0.638 | 0.671 | 0.773 |
| mean_shift | 50 | 5 | 7 | B | empirical | 50 | 5 | 0.000 | 0.032 | 0.015 | 0.671 | 0.687 | 0.791 |
| mean_shift | 50 | 5 | 7 | B | bounded | 50 | 5 | 0.000 | 0.032 | 0.015 | 0.671 | 0.687 | 0.791 |
| mean_shift | 50 | 8 | 7 | A | empirical | 50 | 6 | 0.035 | 0.092 | 0.035 | 0.721 | 0.606 | 0.756 |
| mean_shift | 50 | 8 | 7 | A | bounded | 50 | 8 | 0.000 | 0.032 | 0.005 | 0.721 | 0.704 | 0.756 |
| mean_shift | 50 | 8 | 7 | B | empirical | 50 | 6 | 0.025 | 0.077 | 0.045 | 0.687 | 0.575 | 0.791 |
| mean_shift | 50 | 8 | 7 | B | bounded | 50 | 8 | 0.000 | 0.032 | 0.005 | 0.687 | 0.704 | 0.791 |
| mean_shift | 50 | 12 | 7 | A | empirical | 50 | 10 | 0.030 | 0.085 | 0.020 | 0.846 | 0.773 | 0.791 |
| mean_shift | 50 | 12 | 7 | A | bounded | 50 | 11 | 0.005 | 0.043 | 0.010 | 0.846 | 0.809 | 0.791 |
| mean_shift | 50 | 12 | 7 | B | empirical | 50 | 7 | 0.050 | 0.113 | 0.035 | 0.560 | 0.460 | 0.638 |
| mean_shift | 50 | 12 | 7 | B | bounded | 50 | 10 | 0.000 | 0.032 | 0.015 | 0.560 | 0.516 | 0.638 |
| mean_shift | 200 | 5 | 7 | A | empirical | 200 | 1 | 0.015 | 0.061 | 0.010 | -0.003 | -0.003 | 0.704 |
| mean_shift | 200 | 5 | 7 | A | bounded | 200 | 4 | 0.005 | 0.043 | 0.005 | -0.003 | -0.003 | 0.704 |
| mean_shift | 200 | 5 | 7 | B | empirical | 200 | 4 | 0.050 | 0.113 | 0.030 | 0.773 | 0.773 | 0.721 |
| mean_shift | 200 | 5 | 7 | B | bounded | 200 | 12 | 0.000 | 0.032 | 0.000 | 0.773 | 0.773 | 0.721 |
| mean_shift | 200 | 8 | 7 | A | empirical | 157 | 7 | 0.025 | 0.077 | 0.010 | 0.721 | 0.687 | 0.721 |
| mean_shift | 200 | 8 | 7 | A | bounded | 157 | 8 | 0.000 | 0.032 | 0.005 | 0.721 | 0.704 | 0.721 |
| mean_shift | 200 | 8 | 7 | B | empirical | 155 | 5 | 0.045 | 0.106 | 0.060 | 0.671 | 0.516 | 0.773 |
| mean_shift | 200 | 8 | 7 | B | bounded | 155 | 8 | 0.005 | 0.043 | 0.000 | 0.671 | 0.671 | 0.773 |
| mean_shift | 200 | 12 | 7 | A | empirical | 157 | 5 | 0.045 | 0.106 | 0.030 | 0.420 | 0.345 | 0.756 |
| mean_shift | 200 | 12 | 7 | A | bounded | 157 | 10 | 0.005 | 0.043 | 0.010 | 0.420 | 0.420 | 0.756 |
| mean_shift | 200 | 12 | 7 | B | empirical | 200 | 2 | 0.030 | 0.085 | 0.050 | 0.277 | 0.181 | 0.809 |
| mean_shift | 200 | 12 | 7 | B | bounded | 200 | 5 | 0.005 | 0.043 | 0.020 | 0.277 | 0.236 | 0.809 |
| metabric | 250 | — | 7 | A | empirical | 20 | 5 | 0.045 | 0.106 | 0.035 | 0.545 | 0.531 | — |
| metabric | 250 | — | 7 | A | bounded | 20 | none | — | — | — | 0.545 | — | — |
| metabric | 250 | — | 7 | B | empirical | 20 | 6 | 0.040 | 0.099 | 0.045 | 0.671 | 0.560 | — |
| metabric | 250 | — | 7 | B | bounded | 20 | 15 | 0.005 | 0.043 | 0.015 | 0.671 | 0.654 | — |
| null_independent | 200 | — | 7 | A | empirical | 200 | 1 | 0.010 | 0.052 | 0.030 | — | — | — |
| null_independent | 200 | — | 7 | A | bounded | 200 | 3 | 0.005 | 0.043 | 0.010 | — | — | — |
| null_independent | 200 | — | 7 | B | empirical | 200 | 1 | 0.025 | 0.077 | 0.050 | — | — | — |
| null_independent | 200 | — | 7 | B | bounded | 200 | none | — | — | — | — | — | — |
| null_correlated | 200 | — | 7 | A | empirical | 23 | 4 | 0.035 | 0.092 | 0.065 | — | — | — |
| null_correlated | 200 | — | 7 | A | bounded | 23 | 12 | 0.005 | 0.043 | 0.010 | — | — | — |
| null_correlated | 200 | — | 7 | B | empirical | 27 | 4 | 0.040 | 0.099 | 0.080 | — | — | — |
| null_correlated | 200 | — | 7 | B | bounded | 27 | 12 | 0.005 | 0.043 | 0.010 | — | — | — |
| mean_shift | 50 | 5 | 8 | A | empirical | 50 | 4 | 0.025 | 0.077 | 0.035 | 0.773 | 0.756 | 0.773 |
| mean_shift | 50 | 5 | 8 | A | bounded | 50 | 5 | 0.000 | 0.032 | 0.000 | 0.773 | 0.773 | 0.773 |
| mean_shift | 50 | 5 | 8 | B | empirical | 50 | 4 | 0.045 | 0.106 | 0.055 | 0.721 | 0.704 | 0.773 |
| mean_shift | 50 | 5 | 8 | B | bounded | 50 | 5 | 0.000 | 0.032 | 0.010 | 0.721 | 0.756 | 0.773 |
| mean_shift | 50 | 8 | 8 | A | empirical | 50 | 6 | 0.040 | 0.099 | 0.015 | 0.654 | 0.638 | 0.687 |
| mean_shift | 50 | 8 | 8 | A | bounded | 50 | 9 | 0.000 | 0.032 | 0.000 | 0.654 | 0.654 | 0.687 |
| mean_shift | 50 | 8 | 8 | B | empirical | 50 | 5 | 0.050 | 0.113 | 0.050 | 0.687 | 0.591 | 0.687 |
| mean_shift | 50 | 8 | 8 | B | bounded | 50 | 8 | 0.005 | 0.043 | 0.000 | 0.687 | 0.687 | 0.687 |
| mean_shift | 50 | 12 | 8 | A | empirical | 50 | 1 | 0.000 | 0.032 | 0.000 | -0.004 | -0.004 | 0.773 |
| mean_shift | 50 | 12 | 8 | A | bounded | 50 | 1 | 0.000 | 0.032 | 0.000 | -0.004 | -0.004 | 0.773 |
| mean_shift | 50 | 12 | 8 | B | empirical | 50 | 8 | 0.040 | 0.099 | 0.060 | 0.654 | 0.531 | 0.773 |
| mean_shift | 50 | 12 | 8 | B | bounded | 50 | 12 | 0.005 | 0.043 | 0.000 | 0.654 | 0.654 | 0.773 |
| mean_shift | 200 | 5 | 8 | A | empirical | 200 | 4 | 0.040 | 0.099 | 0.085 | 0.846 | 0.560 | 0.883 |
| mean_shift | 200 | 5 | 8 | A | bounded | 200 | none | — | — | — | 0.846 | — | 0.883 |
| mean_shift | 200 | 5 | 8 | B | empirical | 200 | 4 | 0.025 | 0.077 | 0.020 | 0.721 | 0.721 | 0.773 |
| mean_shift | 200 | 5 | 8 | B | bounded | 200 | 5 | 0.000 | 0.032 | 0.005 | 0.721 | 0.738 | 0.773 |
| mean_shift | 200 | 8 | 8 | A | empirical | 151 | 5 | 0.045 | 0.106 | 0.075 | 0.791 | 0.606 | 0.773 |
| mean_shift | 200 | 8 | 8 | A | bounded | 151 | 8 | 0.005 | 0.043 | 0.010 | 0.791 | 0.791 | 0.773 |
| mean_shift | 200 | 8 | 8 | B | empirical | 200 | 1 | 0.000 | 0.032 | 0.005 | -0.004 | -0.005 | 0.809 |
| mean_shift | 200 | 8 | 8 | B | bounded | 200 | 1 | 0.000 | 0.032 | 0.005 | -0.004 | -0.005 | 0.809 |
| mean_shift | 200 | 12 | 8 | A | empirical | 200 | 1 | 0.035 | 0.092 | 0.005 | 0.024 | 0.021 | 0.791 |
| mean_shift | 200 | 12 | 8 | A | bounded | 200 | none | — | — | — | 0.024 | — | 0.791 |
| mean_shift | 200 | 12 | 8 | B | empirical | 200 | 4 | 0.050 | 0.113 | 0.025 | 0.180 | 0.172 | 0.756 |
| mean_shift | 200 | 12 | 8 | B | bounded | 200 | 10 | 0.005 | 0.043 | 0.010 | 0.180 | 0.180 | 0.756 |
| metabric | 250 | — | 8 | A | empirical | 20 | 2 | 0.040 | 0.099 | 0.055 | 0.407 | 0.394 | — |
| metabric | 250 | — | 8 | A | bounded | 20 | 8 | 0.000 | 0.032 | 0.040 | 0.407 | 0.407 | — |
| metabric | 250 | — | 8 | B | empirical | 21 | 4 | 0.030 | 0.085 | 0.045 | 0.369 | 0.381 | — |
| metabric | 250 | — | 8 | B | bounded | 21 | none | — | — | — | 0.369 | — | — |
| null_independent | 200 | — | 8 | A | empirical | 200 | 1 | 0.050 | 0.113 | 0.025 | — | — | — |
| null_independent | 200 | — | 8 | A | bounded | 200 | none | — | — | — | — | — | — |
| null_independent | 200 | — | 8 | B | empirical | 200 | 1 | 0.005 | 0.043 | 0.025 | — | — | — |
| null_independent | 200 | — | 8 | B | bounded | 200 | 1 | 0.005 | 0.043 | 0.025 | — | — | — |
| null_correlated | 200 | — | 8 | A | empirical | 29 | 10 | 0.040 | 0.099 | 0.025 | — | — | — |
| null_correlated | 200 | — | 8 | A | bounded | 29 | none | — | — | — | — | — | — |
| null_correlated | 200 | — | 8 | B | empirical | 31 | 9 | 0.050 | 0.113 | 0.015 | — | — | — |
| null_correlated | 200 | — | 8 | B | bounded | 31 | none | — | — | — | — | — | — |

## Independent rediscovery

Each A/B model has its own feature panel and scaler. Label orientation is aligned on validation only for this comparison; that alignment never changes the prefix-vs-teacher fidelity calculation or selected rules. Jaccard measures exact feature overlap; equivalent biological substitutes may differ.

| Case | p | Planted | Seed | Policy | Val agreement ARI | Test agreement ARI | Test disagreement | Feature Jaccard | Both val groups >=5 | Both test groups >=5 |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| mean_shift | 50 | 5 | 6 | full | 0.773 | 0.738 | 0.070 | 1.000 | True | True |
| mean_shift | 50 | 5 | 6 | empirical | 0.622 | 0.687 | 0.085 | 0.600 | True | True |
| mean_shift | 50 | 5 | 6 | bounded | 0.756 | 0.738 | 0.070 | 1.000 | True | True |
| mean_shift | 50 | 8 | 6 | full | 0.721 | 0.756 | 0.065 | 1.000 | True | True |
| mean_shift | 50 | 8 | 6 | empirical | 0.560 | 0.560 | 0.125 | 0.375 | True | True |
| mean_shift | 50 | 8 | 6 | bounded | 0.721 | 0.756 | 0.065 | 0.889 | True | True |
| mean_shift | 50 | 12 | 6 | full | 0.575 | 0.606 | 0.110 | 1.000 | True | True |
| mean_shift | 50 | 12 | 6 | empirical | 0.473 | 0.433 | 0.170 | 0.400 | True | True |
| mean_shift | 50 | 12 | 6 | bounded | 0.591 | 0.606 | 0.110 | 0.688 | True | True |
| mean_shift | 200 | 5 | 6 | full | 0.012 | -0.004 | 0.485 | 1.000 | True | True |
| mean_shift | 200 | 5 | 6 | empirical | 0.007 | -0.005 | 0.490 | 0.000 | True | True |
| mean_shift | 200 | 5 | 6 | bounded | 0.007 | -0.005 | 0.490 | 0.000 | True | True |
| mean_shift | 200 | 8 | 6 | full | 0.005 | -0.005 | 0.500 | 1.000 | True | True |
| mean_shift | 200 | 8 | 6 | empirical | 0.003 | -0.005 | 0.510 | 0.000 | True | True |
| mean_shift | 200 | 8 | 6 | bounded | — | — | — | — | — | — |
| mean_shift | 200 | 12 | 6 | full | -0.003 | -0.001 | 0.530 | 1.000 | True | True |
| mean_shift | 200 | 12 | 6 | empirical | -0.004 | -0.003 | 0.520 | 0.000 | True | True |
| mean_shift | 200 | 12 | 6 | bounded | — | — | — | — | — | — |
| metabric | 250 | — | 6 | full | 0.941 | 0.941 | 0.015 | 1.000 | True | True |
| metabric | 250 | — | 6 | empirical | 0.773 | 0.721 | 0.075 | 0.250 | True | True |
| metabric | 250 | — | 6 | bounded | — | — | — | — | — | — |
| null_independent | 200 | — | 6 | full | -0.005 | 0.005 | 0.450 | 1.000 | True | True |
| null_independent | 200 | — | 6 | empirical | -0.003 | 0.005 | 0.450 | 0.000 | True | True |
| null_independent | 200 | — | 6 | bounded | — | — | — | — | — | — |
| null_correlated | 200 | — | 6 | full | 0.791 | 0.809 | 0.050 | 0.036 | True | True |
| null_correlated | 200 | — | 6 | empirical | 0.638 | 0.591 | 0.115 | 0.000 | True | True |
| null_correlated | 200 | — | 6 | bounded | 0.773 | 0.827 | 0.045 | 0.000 | True | True |
| mean_shift | 50 | 5 | 7 | full | 0.809 | 0.738 | 0.070 | 1.000 | True | True |
| mean_shift | 50 | 5 | 7 | empirical | 0.704 | 0.531 | 0.135 | 0.600 | True | True |
| mean_shift | 50 | 5 | 7 | bounded | 0.809 | 0.721 | 0.075 | 1.000 | True | True |
| mean_shift | 50 | 8 | 7 | full | 0.902 | 0.809 | 0.050 | 1.000 | True | True |
| mean_shift | 50 | 8 | 7 | empirical | 0.721 | 0.638 | 0.100 | 0.714 | True | True |
| mean_shift | 50 | 8 | 7 | bounded | 0.902 | 0.809 | 0.050 | 1.000 | True | True |
| mean_shift | 50 | 12 | 7 | full | 0.738 | 0.654 | 0.095 | 1.000 | True | True |
| mean_shift | 50 | 12 | 7 | empirical | 0.487 | 0.545 | 0.130 | 0.545 | True | True |
| mean_shift | 50 | 12 | 7 | bounded | 0.721 | 0.638 | 0.100 | 0.909 | True | True |
| mean_shift | 200 | 5 | 7 | full | -0.005 | -0.003 | 0.520 | 1.000 | True | True |
| mean_shift | 200 | 5 | 7 | empirical | -0.004 | -0.003 | 0.480 | 0.000 | True | True |
| mean_shift | 200 | 5 | 7 | bounded | -0.004 | -0.004 | 0.515 | 0.000 | True | True |
| mean_shift | 200 | 8 | 7 | full | 0.575 | 0.721 | 0.075 | 0.668 | True | True |
| mean_shift | 200 | 8 | 7 | empirical | 0.460 | 0.560 | 0.125 | 0.500 | True | True |
| mean_shift | 200 | 8 | 7 | bounded | 0.560 | 0.738 | 0.070 | 1.000 | True | True |
| mean_shift | 200 | 12 | 7 | full | 0.063 | 0.111 | 0.330 | 0.785 | True | True |
| mean_shift | 200 | 12 | 7 | empirical | 0.058 | 0.063 | 0.370 | 0.167 | True | True |
| mean_shift | 200 | 12 | 7 | bounded | 0.063 | 0.085 | 0.350 | 0.500 | True | True |
| metabric | 250 | — | 7 | full | 0.827 | 0.773 | 0.060 | 1.000 | True | True |
| metabric | 250 | — | 7 | empirical | 0.809 | 0.809 | 0.050 | 0.571 | True | True |
| metabric | 250 | — | 7 | bounded | — | — | — | — | — | — |
| null_independent | 200 | — | 7 | full | -0.005 | 0.001 | 0.540 | 1.000 | True | True |
| null_independent | 200 | — | 7 | empirical | -0.003 | -0.001 | 0.530 | 0.000 | True | True |
| null_independent | 200 | — | 7 | bounded | — | — | — | — | — | — |
| null_correlated | 200 | — | 7 | full | 0.704 | 0.756 | 0.065 | 0.000 | True | True |
| null_correlated | 200 | — | 7 | empirical | 0.654 | 0.487 | 0.150 | 0.000 | True | True |
| null_correlated | 200 | — | 7 | bounded | 0.738 | 0.687 | 0.085 | 0.000 | True | True |
| mean_shift | 50 | 5 | 8 | full | 0.809 | 0.827 | 0.045 | 1.000 | True | True |
| mean_shift | 50 | 5 | 8 | empirical | 0.575 | 0.622 | 0.105 | 0.600 | True | True |
| mean_shift | 50 | 5 | 8 | bounded | 0.809 | 0.827 | 0.045 | 1.000 | True | True |
| mean_shift | 50 | 8 | 8 | full | 0.721 | 0.738 | 0.070 | 1.000 | True | True |
| mean_shift | 50 | 8 | 8 | empirical | 0.473 | 0.530 | 0.135 | 0.375 | True | True |
| mean_shift | 50 | 8 | 8 | bounded | 0.738 | 0.738 | 0.070 | 0.889 | True | True |
| mean_shift | 50 | 12 | 8 | full | -0.005 | -0.001 | 0.530 | 1.000 | True | True |
| mean_shift | 50 | 12 | 8 | empirical | -0.005 | -0.005 | 0.500 | 0.000 | True | True |
| mean_shift | 50 | 12 | 8 | bounded | -0.005 | -0.001 | 0.530 | 0.000 | True | True |
| mean_shift | 200 | 5 | 8 | full | 0.671 | 0.756 | 0.065 | 1.000 | True | True |
| mean_shift | 200 | 5 | 8 | empirical | 0.531 | 0.433 | 0.170 | 0.600 | True | True |
| mean_shift | 200 | 5 | 8 | bounded | — | — | — | — | — | — |
| mean_shift | 200 | 8 | 8 | full | -0.005 | -0.005 | 0.490 | 0.755 | True | True |
| mean_shift | 200 | 8 | 8 | empirical | -0.005 | -0.005 | 0.490 | 0.000 | True | True |
| mean_shift | 200 | 8 | 8 | bounded | -0.005 | -0.005 | 0.495 | 0.000 | True | True |
| mean_shift | 200 | 12 | 8 | full | 0.021 | 0.002 | 0.540 | 1.000 | True | True |
| mean_shift | 200 | 12 | 8 | empirical | 0.012 | 0.002 | 0.540 | 0.000 | True | True |
| mean_shift | 200 | 12 | 8 | bounded | — | — | — | — | — | — |
| metabric | 250 | — | 8 | full | 0.809 | 0.827 | 0.045 | 0.952 | True | True |
| metabric | 250 | — | 8 | empirical | 0.738 | 0.687 | 0.085 | 0.500 | True | True |
| metabric | 250 | — | 8 | bounded | — | — | — | — | — | — |
| null_independent | 200 | — | 8 | full | -0.003 | 0.005 | 0.550 | 1.000 | True | True |
| null_independent | 200 | — | 8 | empirical | -0.005 | -0.003 | 0.520 | 0.000 | True | True |
| null_independent | 200 | — | 8 | bounded | — | — | — | — | — | — |
| null_correlated | 200 | — | 8 | full | 0.756 | 0.756 | 0.065 | 0.034 | True | True |
| null_correlated | 200 | — | 8 | empirical | 0.654 | 0.721 | 0.075 | 0.000 | True | True |
| null_correlated | 200 | — | 8 | bounded | — | — | — | — | — | — |

Full prefix curves, cluster sizes, source hashes, prediction arrays and exact linear rules in original feature units are saved per case. Every rule applies its recorded discovery-median imputation first. Rule coefficients are not calibrated class probabilities.

Real-data results reuse the same cached cohort and feature universe. The iid assumption is a model assumption, not a donor/external-cohort validation. Planted signal count is not guaranteed to be the minimum useful panel size. Correlated Gaussian controls may be highly stable despite containing only one generated population.

The mean-shift oracle fits ordinary unweighted two-means after being supplied the planted panel, on each learner's own discovery rows. It is an ability benchmark, not autonomous feature discovery or the same optimizer. Oracle results never enter model or prefix selection.
