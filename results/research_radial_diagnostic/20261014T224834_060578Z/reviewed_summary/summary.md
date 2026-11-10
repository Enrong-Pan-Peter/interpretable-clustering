# Radial node diagnostic

Supplied-panel oracle diagnostics and fixed candidate ranking only. These results do not demonstrate autonomous feature discovery, statistical split certification, or a complete clustering hierarchy.

Candidate selection uses validation mean log-density gain on a common full-feature background; test rows only describe the frozen selection. Candidate lists deliberately contain the supplied true support, partial panels, supersets and random controls. Their ranking is an oracle-assisted diagnostic.

The heuristic split flag requires positive radial2-minus-background gain, positive radial2-minus-radial1 gain, two fitted spatial modes with valley/smaller-peak ratio <=0.5, and at least 10% native assignment mass in each group on the reported split. The validation flag is the frozen provisional decision. A test flag is only a descriptive recomputation and never changes that decision. These are not hypothesis tests, confidence guarantees, or calibrated acceptance rules. Both per-candidate and validation-selected control frequencies are reported below.

All models use fit-only scaling. Shell nuisance features have the same one-coordinate population marginals as signal features, drawn independently; the feature permutation and population transform are shared across independent splits. Labels never enter fitting or validation selection. The shells case uses off-model lognormal radii; quartic_shells approximates the model family with an explicitly recorded numerical inverse-CDF sampler.

| Job | Selected panel | Val gain | Test gain | Test 2-vs-1 | Oracle val rank | Test radial ARI | Test centroid ARI | Test GMM2 ARI | Val flag | Test flag |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| shells_d2_p12_seed811 | [8, 10] | 0.871 | 0.736 | 0.664 | 1 | 1.000 | -0.004 | 0.005 | True | True |
| shells_d5_p12_seed811 | [0, 3, 4, 8, 10] | 0.752 | 0.820 | 1.082 | 1 | 1.000 | -0.006 | 0.297 | True | True |
| correlated_gaussian_d3_p12_seed811 | [0] | 0.022 | -0.167 | -0.000 | 7 | — | — | — | False | False |
| student_t_d3_p12_seed811 | [0] | -0.105 | -0.102 | 0.000 | 4 | — | — | — | False | False |
| mean_shift_d3_p12_seed811 | [0] | -0.009 | 0.038 | -0.008 | 6 | -0.001 | 0.463 | 0.440 | False | False |

## Control flag frequencies

Frequencies below are descriptive. Candidates within a job are dependent; these are not independent trials or estimated inferential error guarantees. Common-center scale mixtures and Student-t populations are deliberate radial heavy-tail stress controls. A single-shell control specifies one connected band on the supplied panel. Its matched univariate nuisance marginals can create structured alternative subspaces, especially in two dimensions; flags on those other panels are not automatically false discoveries. Oracle-panel frequencies are reported separately.

| Control | Jobs | Candidates | Val candidate frequency | Test candidate frequency | Val selected frequency | Test selected frequency | Val oracle frequency | Test oracle frequency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| correlated_gaussian | 1 | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| student_t | 1 | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

Every job saves independent raw splits and labels, the fixed feature map, candidate supports, fitted model parameters, per-split predictions and radii, and incremental candidate JSON records. The manifest records configuration, source hashes, seeds, package versions and completion state.

The background comparison uses log q_S(x_S) + log q_0(x) - log q_{0,S}(x_S), so gains are evaluated on the same full feature space. A positive gain can reflect non-Gaussian dependence without two populations; the separate two-versus-one radial comparison and spatial profile are therefore reported. None of these diagnostics establishes semantic truth.
