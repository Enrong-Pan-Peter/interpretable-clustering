# Panel replication results: compression improves; the learner's objective is now a central obstacle

## Material Passport

- Origin Skill: academic-research-suite / experiment validation
- Origin Date: 2026-09-24
- Verification Status: ANALYZED; saved predictions, native/oracle states, choices and arithmetic replayed without clustering refits
- Version Label: panel_replication_assessment_v1
- Source: `results/research_panel_replication/20260921T202232_578177Z`
- Reproducible audit: `scripts/analyze_research_panel_replication.py`
- Derived output: `results/research_panel_replication_analysis_20260923/analysis.json` and `analysis.md`

All 27 prescribed cases completed in 11.74 seconds. The 15,918 saved-state, source, prediction, metric and selection checks pass without discrepancies. Original experiments and results were not modified. These are development results, not independent external-cohort confirmation.

## What worked

The more conservative reduction rule preserves its teacher better. Among the **same 42 fitted learners** for which it returns a panel:

| Reduction policy | Mean test disagreement with full teacher | Observed test disagreement above 5% | Median panel size |
|---|---:|---:|---:|
| Empirical validation threshold | 3.92% | 12/42 | 4 |
| Simultaneous upper-bound threshold | 0.95% | 0/42 | 8 |

This costs compactness and availability: bounded selection returns **42/54** panels, versus 54/54 empirical panels. Missingness remains explicit. The bound concerns population disagreement with the frozen full model under its iid assumptions; it is not a guarantee about every finite test sample, group existence or biological correctness.

There is actual progress beyond triples. With 50 total features and five signals, all six bounded panels recover exactly the five planted features. With eight signals, all six retain all eight, with mean size 8.33. These are learned prefix panels, not exhaustive feature combinations. The result is limited to this controlled setting and does not establish a novel method.

## What fails before compression

Means over the two independently fitted learners and three seeds, using all six fits in every row:

| Total features | Planted signals | Full learned model test ARI | Supplied-feature oracle test ARI |
|---:|---:|---:|---:|
| 50 | 5 | .725 | .782 |
| 50 | 8 | .679 | .739 |
| 50 | 12 | .535 | .725 |
| 200 | 5 | .515 | .774 |
| 200 | 8 | .424 | .773 |
| 200 | 12 | **.165** | **.753** |

The oracle is ordinary two-means fitted on supplied planted features, never autonomous feature discovery. Its success shows that the data contain recoverable information in those features. Failure of the full autonomous model happens upstream of shortening the rule; faithful compression cannot correct a wrong teacher.

Feature ranking and weight allocation both matter. For example, the 200-feature/eight-signal seed-6 B model ranks all eight signals first, yet its full test ARI is only .369 versus oracle .773; its largest feature weight is .815. Finding promising features is not enough when the native objective concentrates the final rule on too little of their joint signal.

Exact positive-weight support is also a poor stability statistic for dense solutions. Many full models assign positive weights to every original feature, so full-support Jaccard 1 does not establish useful feature recovery. The prefix and prediction comparisons are more informative.

## A structural objective problem, not only insufficient search

This finding concerns the **sparse-k-means baseline objective used in this experiment**, not every topological fitness previously considered.

In the exact population version of the standardized mean-shift generator, with total mean separation 3 and 12 equally informative features, the intended Bayes-direction partition receives optimized weighted between-cluster sum of squares per observation **.590545**. A split at zero on one independent Gaussian nuisance coordinate receives **.636620**. Both satisfy the same feature-weight constraints and define valid native centroid boundaries.

Thus this objective can rank a low-information split above the desired distributed signal even with unlimited data. A single weak signal coordinate is another higher-scoring competitor; the derivation does not assert that every global optimum is pure noise, or that every useful partition loses. It does show why stronger optimization alone cannot guarantee the desired target.

The saved finite-sample evidence points in the same direction. For 200 features/12 signals, the saved native partition beats the supplied-feature oracle partition under this same weighted objective in **all six fits**, after optimizing weights for each fixed partition. Mean scores per observation are .677 versus .632, despite test ARIs .165 versus .753. This is an after-the-fact diagnostic using privileged oracle information, not a practical selector. Conditional weight optimization is kept distinct from a joint centroid refit.

The full derivation and its assumptions are in `sparse-objective-math-audit-2026-09-23.md`. This is stronger evidence than observing an optimizer perform poorly, but remains specific to the objective, scaling and target distribution being compared.

## Real data and nulls

METABRIC's full native models have mean external test ARI **.492** and mean A/B prediction-replication ARI **.847**. That supports continued investigation in this scoped contrast. Empirical panels average 3.67 genes with 5.17% teacher disagreement. Bounded panels are returned for only **3/6 learners**, and no seed has both bounded panels, so there is no completed bounded-panel A/B replication pair for METABRIC. The three same-cohort resamplings are not independent biological replications, and the existing feature-universe construction remains a limitation. These numbers are not a controlled improvement comparison with earlier suites, which used different splits/settings.

Correlated single-Gaussian controls still have full A/B prediction ARI **.773** despite containing no generated groups. The two available bounded A/B pairs average .757. Neither faithful compression nor rediscovery supplies the missing cluster-existence criterion.

## Next discriminating ablations

Do not spend the next round merely increasing EA generations or tuning the compression threshold. Preserve the bounded reduction procedure as a useful experimental component while investigating its teacher.

1. **Objective versus optimization:** hold discovery rows, scaling, weight constraint and update budget fixed. Compare ordinary initialization, a clearly marked oracle-direction initialization, and a prespecified nuisance-coordinate initialization. Save objective, weight concentration and partition changes at every update. Report each arm before selecting by objective. Improvement in objective accompanied by worse annotation agreement directly exposes the conflict; a better feasible objective missed by ordinary starts instead exposes optimization. Both can coexist. The fixed-partition part of this diagnosis is already computed in the new audit.
2. **Validation sample size:** freeze the discovery models and candidate ladders, then compare independent validation sizes 200 and 800 while reserving a separate final test set. This isolates confidence-bound power from model quality. Do not enlarge validation using the inspected test rows or rescue missing panels by consulting their test performance. At the present family size, n=200 permits at most one observed disagreement; larger validation can distinguish genuinely small errors more reliably.
3. **Geometry-specific learning remains separate:** the shell experiments require a learner that discovers useful joint mean/scale or quadratic structure. The current raw sparse model and its improved reduction are not that solution. Any replacement objective must be checked against single-population controls, including distributions beyond Gaussian; one-dimensional variance separation alone can favor a uniform population too.

A promising method direction remains a compact original-feature panel coupled to a learned joint score and its native assignment rule, with distinct checks for predictive utility, compression fidelity, rediscovery and evidence for separated groups. The present results identify which components can be retained and which need redesign; they do not yet establish novelty or a universally successful clustering method.

Statistical review: 11/11 scoped checks. Configuration-wise reporting addresses aggregation; no ecological, causal or reverse-causal claims; annotation filtering and cached feature selection remain disclosed; no diagnostic predictive-value claim; extreme-score selection and test reuse remain development risks; abstentions are retained; dependent comparisons and researcher degrees of freedom preclude a confirmatory superiority claim.
