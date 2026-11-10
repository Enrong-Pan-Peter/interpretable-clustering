# Fixed-candidate ranking followup

Development reanalysis of inspected pilot data. Candidate banks and clustering partitions are held fixed for ranking; new random reference panels never enter the candidate bank. Labels enter only reporting. Test-split results below are no longer independent confirmation of this newly designed strategy.

pilot_global: original pilot score; new_global: larger common reference bank; size_centered: size-specific means with common within-size scales; size_standardized: size-specific means and scales. None is a cluster-existence test.

| Dataset | Seed | Proposals | Ranking | Size | Train ARI | Training selection regret | Development test ARI |
|---|---:|---|---|---:|---:|---:|---:|
| mean_shift | 0 | random | pilot_global | 8 | 0.028 | 0.414 | 0.015 |
| mean_shift | 0 | random | new_global | 8 | 0.028 | 0.414 | 0.015 |
| mean_shift | 0 | random | size_centered | 8 | 0.028 | 0.414 | 0.015 |
| mean_shift | 0 | random | size_standardized | 8 | 0.028 | 0.414 | 0.015 |
| mean_shift | 0 | forward | pilot_global | 8 | -0.007 | 0.354 | -0.009 |
| mean_shift | 0 | forward | new_global | 8 | -0.007 | 0.354 | -0.009 |
| mean_shift | 0 | forward | size_centered | 8 | -0.007 | 0.354 | -0.009 |
| mean_shift | 0 | forward | size_standardized | 8 | -0.007 | 0.354 | -0.009 |
| mean_shift | 0 | evolutionary | pilot_global | 8 | 0.586 | 0.052 | 0.396 |
| mean_shift | 0 | evolutionary | new_global | 8 | 0.586 | 0.052 | 0.396 |
| mean_shift | 0 | evolutionary | size_centered | 8 | 0.586 | 0.052 | 0.396 |
| mean_shift | 0 | evolutionary | size_standardized | 8 | 0.586 | 0.052 | 0.396 |
| mean_shift | 0 | soft_graph | pilot_global | 8 | 0.765 | 0.015 | 0.749 |
| mean_shift | 0 | soft_graph | new_global | 8 | 0.765 | 0.015 | 0.749 |
| mean_shift | 0 | soft_graph | size_centered | 8 | 0.765 | 0.015 | 0.749 |
| mean_shift | 0 | soft_graph | size_standardized | 7 | 0.765 | 0.015 | 0.637 |
| mean_shift | 0 | sparse_kmeans | pilot_global | 6 | 0.765 | 0.030 | 0.692 |
| mean_shift | 0 | sparse_kmeans | new_global | 6 | 0.765 | 0.030 | 0.692 |
| mean_shift | 0 | sparse_kmeans | size_centered | 6 | 0.765 | 0.030 | 0.692 |
| mean_shift | 0 | sparse_kmeans | size_standardized | 7 | 0.779 | 0.015 | 0.692 |
