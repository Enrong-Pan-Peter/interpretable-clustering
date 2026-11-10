# Fixed-candidate ranking followup

Development reanalysis of inspected pilot data. Candidate banks and clustering partitions are held fixed for ranking; new random reference panels never enter the candidate bank. Labels enter only reporting. Test-split results below are no longer independent confirmation of this newly designed strategy.

pilot_global: original pilot score; new_global: larger common reference bank; size_centered: size-specific means with common within-size scales; size_standardized: size-specific means and scales. None is a cluster-existence test.

| Dataset | Seed | Proposals | Ranking | Size | Train ARI | Training selection regret | Development test ARI |
|---|---:|---|---|---:|---:|---:|---:|
| metabric | 0 | random | pilot_global | 5 | -0.014 | 0.410 | -0.001 |
| metabric | 0 | random | new_global | 5 | -0.014 | 0.410 | -0.001 |
| metabric | 0 | random | size_centered | 5 | -0.014 | 0.410 | -0.001 |
| metabric | 0 | random | size_standardized | 7 | -0.029 | 0.425 | 0.001 |
| metabric | 0 | forward | pilot_global | 6 | -0.023 | 0.215 | 0.005 |
| metabric | 0 | forward | new_global | 6 | -0.023 | 0.215 | 0.005 |
| metabric | 0 | forward | size_centered | 8 | -0.003 | 0.195 | -0.001 |
| metabric | 0 | forward | size_standardized | 6 | -0.023 | 0.215 | 0.005 |
| metabric | 0 | evolutionary | pilot_global | 7 | -0.008 | 0.385 | -0.002 |
| metabric | 0 | evolutionary | new_global | 7 | -0.008 | 0.385 | -0.002 |
| metabric | 0 | evolutionary | size_centered | 7 | -0.008 | 0.385 | -0.002 |
| metabric | 0 | evolutionary | size_standardized | 1 | -0.004 | 0.381 | -0.008 |
| metabric | 0 | soft_graph | pilot_global | 7 | 0.357 | 0.073 | 0.316 |
| metabric | 0 | soft_graph | new_global | 7 | 0.357 | 0.073 | 0.316 |
| metabric | 0 | soft_graph | size_centered | 8 | 0.357 | 0.073 | 0.261 |
| metabric | 0 | soft_graph | size_standardized | 7 | 0.378 | 0.053 | 0.297 |
| metabric | 0 | sparse_kmeans | pilot_global | 5 | 0.409 | 0.044 | 0.316 |
| metabric | 0 | sparse_kmeans | new_global | 5 | 0.409 | 0.044 | 0.316 |
| metabric | 0 | sparse_kmeans | size_centered | 8 | 0.016 | 0.437 | 0.118 |
| metabric | 0 | sparse_kmeans | size_standardized | 7 | 0.300 | 0.153 | 0.335 |
