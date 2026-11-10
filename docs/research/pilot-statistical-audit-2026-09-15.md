# Pilot statistical audit: what the saved runs establish

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validation of saved experimental output
- Origin Date: 2026-09-15
- Verification Status: ANALYZED; saved arithmetic and source consistency checked, clustering fits not rerun
- Version Label: pilot_statistical_audit_v1
- Inputs: `results/research_diagnostics/`; no code or result files changed

## Protocol integrity

All **19** expected manifests report completion: 3 fixed-panel null audits, 4 paired score audits, and 12 search runs with 5 methods each. Every recorded source hash matches the current local file, including the imported legacy code. Every run has disjoint discovery/validation/test indices with **240/120/120** rows. All 16 scoring/search reference banks contain **32/32 eligible panels**; graphcut and legacy-graphcut have identical calibration moments. Thus the reference-filtering confound identified during implementation is absent here.

Independently checked all **4,833** saved search candidates: all satisfy the declared common eligibility rule; their scalar values reproduce from the saved frozen moments. All **60** selected panels equal the score maximum under the implemented tie-breaking rule. All 60 retrospective best-visited training ARIs reproduce from the candidate records. No indication of external-label use in proposal, scalar selection or deletion decisions was found in the source.

This verifies internal reporting, not scientific validity. Real-data populations were deliberately filtered using annotations before the experiment. METABRIC uses a previously variance-filtered gene universe; Levine holds out cells within existing specimens. The three seeds reuse cohorts and vary samples/splits as well as optimization randomness. They are not three independent biological replications. The evolutionary arm is the new elite-parent add/drop/swap baseline, **not NSLC**.

## 1. Ranking remains a material bottleneck, but depends on the proposal family

Across the three METABRIC search runs, descriptive means are:

| Method | Best-visited minus selected training ARI | Selected transferred test ARI |
|---|---:|---:|
| Random | 0.4298 | 0.0193 |
| Forward | 0.2808 | -0.0021 |
| Evolutionary baseline | 0.3236 | 0.1454 |
| Smooth graph | 0.2421 | 0.1184 |
| Sparse k-means | 0.0264 | 0.3559 |

Source runs: `search_metabric_seed0_20260915T153605_077499Z`, `search_metabric_seed1_20260915T153710_941627Z`, `search_metabric_seed2_20260915T153814_416170Z`.

The strongest single example is seed 1: smooth graph visits a panel with training ARI **0.560679**, then selects training ARI **-0.003070** and test ARI **-0.007762**. This establishes an in-sample ranking failure relative to the supplied class target. It does not establish the held-out performance of the retrospectively best visited panel, which was not confirmed.

Better optimization of the present scalar is not reliably beneficial. On METABRIC seed 0, the evolutionary winner scores **2.535800** with test ARI **-0.001546**, while the sparse-k-means winner scores **2.344323** with test ARI **0.315710**. On seed 1, smooth graph scores **3.629855**, exceeding sparse k-means at **3.383244**, but their test ARIs are **-0.007762** and **0.334572**. Restricting proposals to a sensible model family may help by excluding attractive nuisance partitions; this is different from maximizing the current score more successfully.

Sparse k-means is the strongest METABRIC comparator in these three runs, but its independent re-clustering fidelity averages only **0.3926**. External-label transfer performance and reproducibility of the unsupervised partition remain separate requirements. No winner should yet be selected using a significance claim: the seed count is small, comparisons share data, and computation was not matched. Smooth graph scores 43–47 panels on METABRIC and sparse k-means 42–90, versus 100 for the discrete methods; optimizer work is additional and recorded.

## 2. Partition consistency helps in the paired banks; it does not remove size effects

The four fixed-bank comparisons give these selected **transferred test ARIs**:

| Case / run ID | Consistent hybrid | Legacy hybrid | Qualification |
|---|---:|---:|---|
| Levine / `score-audit_levine_seed0_20260915T153528_341309Z` | 0.966665 | 0.180939 | Both selected from the random portion |
| Mean shift / `score-audit_mean_shift_p50_s5_seed0_20260915T153507_387767Z` | 0.610298 | 0.584257 | Both selected planted-panel deletions |
| METABRIC / `score-audit_metabric_seed0_20260915T153518_028881Z` | 0.417655 | -0.007331 | Consistent selects 49 known reference genes |
| Shells / `score-audit_shells_p50_s5_seed0_20260915T153512_620764Z` | -0.005137 | -0.005987 | Consistent selects the true panel, but splits it incorrectly |

The masks, rows and emitted spectral partition are shared within each bank. The legacy hybrid changes its density partition and uses its own frozen density scale. These are controlled comparisons of the **two complete score profiles**, not a claim that only one numerical quantity changed. All 379 paired-bank panels are eligible; **378/379** have spectral-versus-MST partition ARI below 0.5. Median partition agreement is approximately zero in every bank. The historical partition inconsistency is substantial on these inputs.

The favorable METABRIC correlation for the consistent scalar also needs qualification: score-versus-training-ARI Spearman correlation is **0.7013** across its augmented bank, but only **0.0756** among the **63 random panels**, without recalibrating the objective. Mean shift changes from **0.2030** overall to **-0.0250** among 62 random panels. Reference augmentation makes useful structures available; those overall correlations are not evidence that arbitrary small masks can be ranked accurately.

Raw components have opposing size trends among the random panels:

| Case | Spearman(size, graphcut) | Spearman(size, consistent density) |
|---|---:|---:|
| Mean shift | -0.9629 | +0.9544 |
| Shells | -0.9698 | +0.9454 |
| METABRIC | -0.9195 | +0.6072 |
| Levine | -0.9159 | +0.6183 |

For mean shift, median graphcut changes from **-0.01977** at size 1 to **-0.40087** at size 8, while density changes from **-0.96277** to **-0.57453**. Graphcut alone selects a singleton in all four paired audits. Density alone selects an uninformative eight-feature panel in mean shift (training ARI **-0.004159**). Frozen global standardization makes the objective reproducible; it does **not** make it size-unbiased. These correlations are descriptive and the masks overlap, so no independence-based p-values are attached. Within-size ranking and feature-removal studies are needed before attributing the trends entirely to irrelevant dimensions.

## 3. Validation-only compression often fails to preserve its tolerance on test rows

Among the 60 selected search results, **17** actually delete features. Every accepted deletion meets the configured validation threshold. **12 of those 17** final reductions have test full-versus-reduced ARI below **0.95**. This is a descriptive failure count, not a binomial inference: methods and seeds share observations and sometimes the same panels.

Examples, showing final accepted validation fidelity and independent test fidelity:

| Run / method | Size change | Validation | Test |
|---|---:|---:|---:|
| `search_metabric_seed0_20260915T153605_077499Z` / sparse k-means | 5 → 4 | 0.966665 | 0.838525 |
| `search_metabric_seed1_20260915T153710_941627Z` / forward | 7 → 4 | 1.000000 | 0.447763 |
| `search_metabric_seed2_20260915T153814_416170Z` / sparse k-means | 8 → 5 | 0.966657 | 0.808397 |
| `search_levine_seed1_20260915T153727_561448Z` / evolutionary | 7 → 1 | 0.966640 | 0.838932 |

The Levine example decreases external-label test ARI from **0.966666 to 0.870026**. More broadly, good ARI can survive even when the original partition changes, and a bad partition can be preserved perfectly. Both measurements must remain visible. The implemented compression is a greedy explanation of frozen assignments, not reclustering-based proof of feature necessity. The test split has now been inspected for development; future claims about an improved compressor require new confirmation data or a properly nested evaluation design.

## 4. Higher-dimensional recovery and cluster acceptance remain unestablished

The mean-shift learned proposals are promising: mean test ARI is **0.7117** for smooth graph and **0.6681** for sparse k-means, versus **0.1520** for random masks. Their selected panels have 6–8 features and retain those sizes after compression. This establishes useful multi-feature **outputs** on this generator, not that every retained feature is needed or that the method scales well. The three underlying runs are `search_mean_shift_p50_s5_seed0_20260915T153533_581854Z`, `search_mean_shift_p50_s5_seed1_20260915T153638_932155Z`, and `search_mean_shift_p50_s5_seed2_20260915T153742_882674Z`.

For shells, the true-panel training ARIs are **-0.001244, 0.001213, 0.004240** across seeds 0–2. The failure therefore survives supplying the correct features. Conversely, the shell seed-1 sparse-k-means candidate has re-clustering fidelity **0.749049**, yet external-label test ARI **-0.005942** (`search_shells_p50_s5_seed1_20260915T153654_397054Z`). Reproducibility can concern the wrong separation.

The null audits only test fixed-panel independence. The correlated Gaussian yields graphcut p=**0.100** and correlation p=**0.025**, while the bimodal singleton gives both p=**1.000** at 39 permutations. Source runs: `null-audit_null_correlated_p50_s5_seed0_20260915T153502_811108Z` and `null-audit_bimodal_p50_s5_seed0_20260915T153505_112216Z`. No full search on negative controls or split-acceptance rule is present, so there is **no false-split-rate estimate**.

## Consequences for the next experiment

Prioritize a small **proposal-family × selection-policy** comparison, retaining separate density, graph, reproduction and complexity measurements. Inspect within-size ranking before adding another global scalar. Use sparse k-means as a serious baseline for overlapping mean-shift populations; treat smooth graph as a proposal hypothesis with local-optimum and ranking failures. For shells, test a geometry capable of expressing radius before more feature-search tuning. Evaluate compression under repeated independent validation or nested splits, including its realized held-out fidelity rather than only the acceptance threshold. Do not advance to recursive split acceptance until its statistical target has been defined.

Statistical fallacy scan, 11/11 addressed: aggregation/Simpson effects require case-specific reporting; no ecological individual-level claim is made; annotation-defined filtering is disclosed (Berkson/selection risk); no collider adjustment or causal model is asserted; no predictive-value/base-rate claim is made; extreme candidate scores can regress under holdout; all expected runs completed, limiting run-survivorship concerns; look-elsewhere and forking-path risks remain for post-pilot model choices; no causal or reverse-causal interpretation is claimed. These observations guide interpretation and do not turn this small pilot into confirmatory evidence.
