# Radial node diagnostic

Supplied-panel oracle diagnostics and fixed candidate ranking only. These results do not demonstrate autonomous feature discovery, statistical split certification, or a complete clustering hierarchy.

Candidate selection uses validation mean log-density gain on a common full-feature background; test rows only describe the frozen selection. Candidate lists deliberately contain the supplied true support, partial panels, supersets and random controls. Their ranking is an oracle-assisted diagnostic.

The heuristic split flag requires positive radial2-minus-background gain, positive radial2-minus-radial1 gain, two fitted spatial modes with valley/smaller-peak ratio <=0.5, and at least 10% native assignment mass in each group on the reported split. The validation flag is the frozen provisional decision. A test flag is only a descriptive recomputation and never changes that decision. These are not hypothesis tests, confidence guarantees, or calibrated acceptance rules. Both per-candidate and validation-selected control frequencies are reported below.

All models use fit-only scaling. Shell nuisance features have the same one-coordinate population marginals as signal features, drawn independently; the feature permutation and population transform are shared across independent splits. Labels never enter fitting or validation selection. The shells case uses off-model lognormal radii; quartic_shells approximates the model family with an explicitly recorded numerical inverse-CDF sampler.

| Job | Selected panel | Val gain | Test gain | Test 2-vs-1 | Oracle val rank | Test radial ARI | Test centroid ARI | Test GMM2 ARI | Val flag | Test flag |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| shells_d2_p24_seed1201 | [5, 9] | 0.720 | 0.719 | 0.640 | 1 | 1.000 | 0.002 | 0.001 | True | True |
| shells_d3_p24_seed1201 | [1, 5, 9] | 0.645 | 0.713 | 0.709 | 1 | 1.000 | 0.002 | -0.000 | True | True |
| shells_d5_p24_seed1201 | [1, 5, 6, 9, 18] | 0.859 | 0.766 | 1.002 | 1 | 1.000 | 0.001 | 0.013 | True | True |
| shells_d8_p24_seed1201 | [1, 5, 6, 8, 9, 18, 20, 21] | 1.070 | 1.132 | 1.630 | 1 | 1.000 | 0.001 | 1.000 | True | True |
| single_shell_d2_p24_seed1201 | [5, 9] | 1.483 | 1.518 | 0.022 | 1 | — | — | — | False | False |
| single_shell_d5_p24_seed1201 | [1, 5, 6, 9, 18] | 1.141 | 1.067 | 0.003 | 1 | — | — | — | False | False |
| independent_gaussian_d5_p24_seed1201 | [0, 1, 16, 19] | -0.016 | -0.024 | 0.083 | 6 | — | — | — | False | False |
| correlated_gaussian_d5_p24_seed1201 | [1, 7, 8, 10, 12, 16, 17] | 0.005 | -0.021 | 0.115 | 10 | — | — | — | False | False |
| student_t_d5_p24_seed1201 | [1, 5] | -0.125 | -0.131 | 0.212 | 5 | — | — | — | False | False |
| common_center_scale_mixture_d5_p24_seed1201 | [0, 1, 16, 19] | -0.080 | -0.124 | 0.185 | 9 | — | — | — | False | False |
| mean_shift_d3_p24_seed1201 | [2, 17] | 0.050 | 0.023 | 0.006 | 8 | -0.001 | -0.002 | -0.002 | False | False |
| quartic_shells_d3_p24_seed1201 | [1, 5, 9] | 1.049 | 1.109 | 1.087 | 1 | 1.000 | 0.004 | 0.001 | True | True |
| shells_d2_p24_seed1213 | [3, 12] | 0.710 | 0.737 | 0.670 | 1 | 1.000 | -0.002 | -0.001 | True | True |
| shells_d3_p24_seed1213 | [3, 12, 22] | 0.740 | 0.726 | 0.759 | 1 | 1.000 | -0.002 | -0.001 | True | True |
| shells_d5_p24_seed1213 | [3, 12, 17, 18, 22] | 0.891 | 0.852 | 1.034 | 1 | 1.000 | 0.002 | 1.000 | True | True |
| shells_d8_p24_seed1213 | [3, 8, 9, 12, 17, 18, 20, 22] | 1.060 | 1.158 | 1.628 | 1 | 1.000 | 0.002 | 1.000 | True | True |
| single_shell_d2_p24_seed1213 | [3, 12] | 1.559 | 1.593 | 0.007 | 1 | — | — | — | False | False |

## Control flag frequencies

Frequencies below are descriptive. Candidates within a job are dependent; these are not independent trials or estimated inferential error guarantees. Common-center scale mixtures and Student-t populations are deliberate radial heavy-tail stress controls. A single-shell control specifies one connected band on the supplied panel. Its matched univariate nuisance marginals can create structured alternative subspaces, especially in two dimensions; flags on those other panels are not automatically false discoveries. Oracle-panel frequencies are reported separately.

| Control | Jobs | Candidates | Val candidate frequency | Test candidate frequency | Val selected frequency | Test selected frequency | Val oracle frequency | Test oracle frequency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| common_center_scale_mixture | 1 | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| correlated_gaussian | 1 | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| independent_gaussian | 1 | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| single_shell | 3 | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| student_t | 1 | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

Every job saves independent raw splits and labels, the fixed feature map, candidate supports, fitted model parameters, per-split predictions and radii, and incremental candidate JSON records. The manifest records configuration, source hashes, seeds, package versions and completion state.

The background comparison uses log q_S(x_S) + log q_0(x) - log q_{0,S}(x_S), so gains are evaluated on the same full feature space. A positive gain can reflect non-Gaussian dependence without two populations; the separate two-versus-one radial comparison and spatial profile are therefore reported. None of these diagnostics establishes semantic truth.
