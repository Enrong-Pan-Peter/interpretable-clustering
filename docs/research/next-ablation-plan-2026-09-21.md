# What the ablations establish, and the next discriminating experiment

## Material Passport

- Origin Skill: academic-research-suite / experiment validation and planning
- Origin Date: 2026-09-21
- Verification Status: ANALYZED; saved obstacle arithmetic and frozen states independently checked, with no clustering refits; new replication experiment tested and smoke tested only
- Version Label: native_panel_replication_v1
- Completed experiment: `results/research_obstacle_checks/20260916T145427_229536Z`
- Current audit: `results/research_obstacle_analysis_20260921/analysis.md`
- Next entrypoint: `scripts/run_research_panel_replication.py`

## Yes, these are ablation studies

The 33-case obstacle suite changes individual components while holding the panel or other parts of the pipeline fixed. This differs from a software unit test or a comparison of unrelated end-to-end algorithms. A supplied-feature oracle is an additional ability benchmark: it removes the need to discover features, but must not be described as autonomous success.

The run completed all 33 cases in 102.63 seconds. A read-only audit now passes 62,004 arithmetic, coverage, state and provenance checks without discrepancies. The original experimental results are unchanged. An earlier incomplete audit failed because its contingency-table implementation omitted trailing empty cells; that verifier bug was corrected and regression tested. Geometry predictions and independent test-only centroid labels were not saved by the old suite, so their fits/metrics were not independently replayed. They are reported from the saved summaries with that narrower verification scope.

| Question / intervention | What was held fixed | Evidence | Interpretation and limit |
|---|---|---|---|
| Does scalar size adjustment repair ranking? | The visited candidate banks | METABRIC mean test ARI .127 original, .093 centered, .106 standardized | The tried corrections are insufficient; this does not rule out a better objective. Centering also changes component scales. |
| Does spectral replacement discard useful partitions? | Same selected features, unweighted coordinates, same kNN assignment | METABRIC prefix-eight centroid-kNN vs spectral-kNN mean ARI: .442 vs .296, .467 vs .276, .475 vs .259 across the three prescribed sparsity bounds | Partition replacement is damaging here. These are paired software interventions on a scoped benchmark, not a claim that centroids always win. |
| Is the same loss present in mean shift? | Moderate sparsity, prefix eight | Native .779; weighted prefix .779; unweighted centroid .749; centroid-kNN .711; spectral-kNN .711 | Weight removal and assignment contribute here; replacing the partition adds no aggregate loss in this particular comparison. |
| Is shell failure purely the search engine? | Supply the correct five features | Squared spectral: 27/27 test ARI=1; radius rule: 9/9=1. Raw spectral improves only at the largest sample with k=5 | Geometry and sampling matter. Autonomous squared native models still reach at most .140 ARI, with top-eight masks finding at most 2/5 planted features. Discovery remains unsolved. |
| Is reduction reliable after passing validation? | Same pilot teacher and panel | Empirical 5% disagreement reduces 14/14 reducible panels, but 9/14 exceed 5% test disagreement; foldwise: 6/13 | Passing reused validation is not enough. These counts are descriptive and dependent; this alone does not distinguish every source of uncertainty or establish a population failure rate. |
| Does repeatability imply groups exist? | Run prescribed fits on one Gaussian population | Correlated-null fixed-panel refitting reaches ARI .948 | It does not. Fidelity, independent rediscovery and cluster existence need separate evidence. |

The fitness function is therefore not the only demonstrated problem. More powerful search cannot by itself repair a representation that hides the target, a replacement partition that discards useful structure, or unreliable validation. Conversely, these results do not prove the current search is adequate at larger dimensions.

## Next experiment: native panels, independent rediscovery, controlled compression

We retain the raw sparse-k-means metric and nearest-centroid rule. This is an established baseline, not a claim of a new clustering algorithm: [Witten and Tibshirani, 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2930825/). The purpose is to test whether a defensible panel method can be built around a useful fitted model before comparing more search engines.

Each case uses four disjoint, label-blind row blocks: discovery A, discovery B, validation, and test. At the default 800 observations each block contains 200. Each discovery block independently fits its own imputation, scaling, native model and feature ranking. The L1 bound is fixed at the square root of the smaller of the prefix cap and variable-feature count; the discovery objective chooses among three restarts at that one bound. Models may have more positive weights than the cap.

Freeze the top-one through top-sixteen prefixes from positive-weight features before reading validation. Keep the same stored centroids and weights; do not refit, flip labels, substitute features or adaptively delete based on validation. Then apply two policies to the identical candidate ladder:

1. **Empirical:** choose the smallest valid prefix with observed validation disagreement at most 5% relative to its own full native teacher.
2. **Bounded:** choose the smallest valid prefix whose simultaneous one-sided upper bound on that disagreement is at most 5%.

For k disagreements out of n validation observations and M=2*cap candidates, the upper bound is the Beta(k+1,n-k) upper alpha/M quantile, with the all-errors boundary set to one. This is a one-sided Clopper–Pearson bound with Bonferroni coverage over both fixed ladders. With no observed errors, n=200 and M=32, the upper bound is .031791. The construction is conservative; [Brown, Cai and DasGupta, 2001](https://www.stat.cmu.edu/~brian/720/week01/Binomial-StatSci.pdf) discusses the coverage/conservatism of exact binomial intervals. The familywise extension follows the union bound; dependence between candidate rules does not require independence across their bounds.

The guarantee is conditional on frozen discovery fits and iid validation observations, concerns fidelity to each learned teacher, and is per case. It does not establish biological truth, feature necessity, cluster existence, or simultaneous coverage across all future experiments. It does not guarantee that a finite test sample's observed error will always be below 5%. Under real-cohort sampling, the iid interpretation remains a modeling assumption.

No acceptable prefix means an explicit missing result, with no favorable fallback. Group-size checks reject collapsed/tiny discovery and validation partitions. Test group sizes and noncollapse flags remain visible in the summary. A and B label orientation is aligned on validation only for reporting their agreement; that alignment never changes compression errors, selected models or exported rules.

Report separately:

- Full-to-prefix validation bound and test fidelity.
- A-versus-B prediction agreement on a common untouched test set.
- Exact feature overlap, feature names and reference overlap where meaningful.
- External test ARI, after all decisions are frozen.
- Full model support and selected support, including missing bounded panels.
- Every fixed prefix curve, not just selected outputs.
- Exact linear assignment rules in original feature units, with recorded missing-value imputation.

For synthetic mean shift, add an explicitly supplied-support benchmark: ordinary two-means on the planted features, independently fitted on each learner's discovery block. This is an ability comparison, not feature discovery or an identical optimizer. It is fitted only after autonomous choices are fixed and never seeds or selects them.

## The prescribed 27 cases

| Population | Settings | Seeds | Cases |
|---|---|---|---:|
| Mean shift | p=50/200; planted features=5/8/12; total separation norm fixed at 3 | 6,7,8 | 18 |
| METABRIC LumA/LumB | Existing 250-gene cached universe | 6,7,8 | 3 |
| Independent / correlated single Gaussian | p=200 | 6,7,8 | 6 |

Default n=800, cap=16, 40 alternating iterations, three starts per learner. No feature-combination enumeration is used. The fitted prefixes are candidates from a learned ranking. The known generating support is not asserted to be the unique minimum useful panel at nonzero tolerance.

This is still development evidence. New real-data seeds resample the same cohort; METABRIC's existing all-patient feature-universe filter remains a limitation. Independent external validation and domain interpretation remain necessary later.

## How to interpret the next outputs

| Result pattern | What it directs us to examine |
|---|---|
| Supplied support succeeds, autonomous full model fails as p grows | Feature-learning objective or optimization/sample requirements. Inspect support recovery and initialization sensitivity before adding an EA. |
| Both full models work, but independently discovered feature sets differ | Feature redundancy/substitution; compare predictions and biological groupings before demanding identical genes. |
| Full A/B assignments disagree strongly | The native model/feature learning is not reproducible at this sample size; compression cannot fix that. |
| Full model works, empirical prefixes fail, bounded prefixes transfer better | Validation uncertainty was a material compression problem. Report coverage, sizes and missing outputs, not just successes. |
| Even sixteen features cannot preserve the teacher reliably | Teacher complexity/noise sensitivity or insufficient validation evidence. Do not force a small panel. |
| Gaussian controls pass fidelity and rediscovery | A separate acceptance criterion is still needed. Compactness and stability are not cluster tests. |

These are diagnostic interpretations, not precommitted causal conclusions about the scientific population. Comparisons within a case change one component; comparing this new suite wholesale with the earlier pilot also changes seeds, sample allocation and fitting settings, so it would not isolate a single factor.

## Run locally

```powershell
Set-Location 'C:\Users\Peter\Desktop\Github\ATOMIC_Clustering'
.\.venv-research\Scripts\python.exe -u .\scripts\run_research_panel_replication.py --suite all
```

Outputs: `results/research_panel_replication/<timestamp>/summary.md`, a JSON summary, source/runtime manifest, per-case predictions and preprocessing, and `A/B_empirical/bounded_rule.json/.txt` when those panels exist. Completed cases survive interruption; automatic resume is not implemented. To inspect only the planned jobs, add `--list-only`.

69 targeted tests passed. Short execution checks cover synthetic scaling, METABRIC, both controls, rule export and the report. The full 27-case study has not been run by the assistant. The short checks use seed 19 and reduced optimization effort and must not be presented as evidence that the method works.

## Ablations still needed after this round

The shell branch remains open. A raw mean-separation model does not solve that problem. The geometry audit proposes sparse mean/scale mixtures as an established baseline, and sparse additive quadratic projections targeting a density valley as a separate research direction. Both must discover features autonomously, preserve their native assignment and confront matched-marginal nuisance features and correlated nulls. See `obstacle-geometry-controls-audit-2026-09-17.md`.

An optimizer comparison should then hold the model, objective, initialization access, candidate admissibility and evaluation/time budgets fixed, comparing random/local/evolutionary proposals. Existing results do not constitute a decisive test of every EA or the original NSLC implementation. We should first settle the object and evidence being optimized. Acceptance calibration must include the complete search procedure under explicitly stated null models.

Novelty is not established by these combinations. A potential method contribution would be a coherent approach to discovering interpretable original-feature panels, retaining their geometry and assignment, and separately validating compactness, reproducibility, usefulness and group evidence. Each part needs evidence rather than being hidden in one score.
