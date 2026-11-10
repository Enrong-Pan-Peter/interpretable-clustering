# Pilot assessment and the next controlled experiment

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: results interpretation and authorized experiment preparation
- Origin Date: 2026-09-15
- Verification Status: 19 pilot jobs audited; follow-up code passed 22 checks and two bounded replay checks; effectiveness and novelty remain unverified
- Version Label: pilot_assessment_v1
- Inputs: `results/research_diagnostics/`, independent agent audits, and `results/research_pilot_analysis_20260915/analysis.json`
- Scope: single-node development experiments, not a finished clustering algorithm or publication claim

## Decision

The project now has evidence that it can discover five-feature signal without enumeration. It has not yet solved choosing a compact explanation or handling different cluster geometries.

Use **sparse k-means proposals as the strongest current real-data baseline**, retain smooth graph proposals as a comparison, and prioritize three separable changes:

1. Test panel-size effects on ranking while keeping all candidate panels fixed.
2. Preserve and evaluate the learned representation and partition, rather than automatically replacing them with an unweighted raw-space spectral split.
3. Redesign reduction to assess the usefulness of a refitted smaller model, alongside fidelity to the original rule. A noisy original rule should not make nuisance features appear necessary.

More EA generations are not the first priority. The simple evolutionary baseline did outperform random masks on average in mean shift and METABRIC, so saying "EA never helps" would also be wrong. It was substantially weaker than the learned proposal methods on mean shift, and weaker than sparse k-means on METABRIC. This baseline is not the original NSLC engine.

## What completed

All **19 expected jobs** completed with no missing or duplicate cases. They share one saved source configuration; all recorded hashes match the files at review time. Discovery, validation and test row indices are disjoint within every run (240/120/120). The summed recorded job time is **196.2 seconds**, excluding interpreter startup and suite overhead.

Independent checks reproduced all 60 search selections and 4,833 candidate objective values. The reference banks used the same eligibility intersection for all scoring profiles. These checks support implementation consistency; they do not establish that the chosen objectives capture meaningful populations.

The three seeds are sensitivity checks. METABRIC patient samples overlap across runs and originate from the same PAM50-enriched, previously variance-filtered matrix. Levine cells come from the existing specimen pool. Neither is independent cohort replication.

## Results that change the plan

Mean transferred test ARI across the three seeds:

| Proposal method | Five-feature mean shift | METABRIC LumA/LumB | Levine CD4/CD8 |
|---|---:|---:|---:|
| Random | .152 | .019 | .956 |
| Forward | .162 | -.002 | .913 |
| Simple evolutionary | .268 | .145 | .956 |
| Smooth graph | .712 | .118 | .956 |
| Sparse k-means | .668 | .356 | .956 |

Every method scored approximately zero ARI on the shells. Proposal learning costs are recorded; these are not matched-total-compute experiments. Learned proposal banks often contain fewer than the 100 candidates scored by discrete methods.

### Discovery beyond three: a concrete success, with a remaining selection failure

Both learned methods scored the **exact planted five-feature panel in every mean-shift seed**. They selected 6–8 features instead, retaining all five signal coordinates plus 1–3 nuisance coordinates. None of those selected learned-method panels was reduced.

This moves the diagnosis beyond "search never reaches a useful larger panel." On this generator, search does reach it. The compact panel loses to larger panels under the current objective, and the current reduction rule does not repair that choice.

Five planted coordinates do not prove five indispensable coordinates. This generator distributes a mean shift across features; a four-feature subset can still be useful. Minimality must be defined relative to a declared quality tolerance and checked on new data.

### METABRIC: a plausible, repeatable feature family

Sparse k-means proposal panels have transferred test ARIs **.316, .335 and .418**, using **5, 5 and 8 genes**. CEP55 and PTTG1 occur in all three original panels. Those panels contain 5/5, 5/5 and 7/8 PAM50 genes. Smooth-graph selected panels share no genes across seeds and have test ARIs **.316, -.008 and .047**.

The pattern favors sparse k-means as a development baseline. It does not show that the selected genes are uniquely necessary, that they constitute a new biomarker, or that the method beats a published classifier. The contextual full-PAM50 panel averaged .352 through **our spectral-plus-kNN pipeline**; that number is not the published PAM50 classifier's performance.

The [panel interpretation report](pilot-panel-interpretation-2026-09-15.md) lists every panel, its overlaps, training correlations, and the existing proliferation-index connection supported by primary literature. The METABRIC feature universe and annotations already favor recovering parts of this established signature, so new biological claims need a stronger external evaluation.

### Fitness: partition consistency helps, but global scaling is still problematic

In the paired banks, consistent scoring substantially improves over the legacy hybrid on Levine and METABRIC. Those banks include contextual reference panels; their performance cannot be described as autonomous discovery. METABRIC's winning 49-gene panel is explicitly a reference-panel deletion, not a panel found by the bounded search.

Among the random panels, graphcut strongly decreases with size while consistent density increases. For mean shift, their Spearman correlations with size are **-.963 and +.954**; for shells, **-.970 and +.945**. Graphcut alone selects a singleton in all four paired audits. A fixed global scale makes the score reproducible but does not eliminate these trends.

Overall score-versus-ARI correlations can also exaggerate success by mixing reference panels with ordinary random panels. On METABRIC the consistent score's overall training correlation is .701, but it is .076 within the random panels without recalibration. On mean shift it changes from .203 overall to -.025 within random panels. See the [statistical audit](pilot-statistical-audit-2026-09-15.md) for exact definitions and run IDs.

These are reasons for a targeted scaling experiment, not a reason to claim that size-normalized scores will solve clustering. Reference masks are not a no-clusters null, and rare high scores do not establish cluster existence.

### Shells: representation and discovery are separate obstacles

Raw-space spectral clustering fails even when given the true five features in every seed. Approximately half of each outer-shell point's ten neighbors belong to the inner shell. The raw graphcut score actually prefers the returned directional split over the known radial split.

A bounded post-pilot diagnostic applied squaring to the standardized coordinates of the supplied true panel. Spectral clustering then reached ARI **1.0** for training, transferred test assignments and independent test reclustering in all three seeds. This proves that a suitable representation can express the separation on these samples.

It does **not** solve feature discovery: sparse-k-means proposals on all 50 squared features still missed the full planted panel. The transformed true-panel result is an oracle ability check, not unsupervised recovery. The [geometry audit](pilot-geometry-audit-2026-09-15.md) records the construction and next representation/partition-retention comparison.

### Reduction needs its own evaluation

Of the 17 search outputs that deleted features, **12 failed to retain the .95 ARI fidelity threshold on test rows**, although their accepted deletions passed validation. These dependent cases do not support a binomial inference, but they expose an engineering and statistical weakness.

Conversely, none of the extra features in the learned mean-shift panels was deleted. The procedure preserves the original noisy kNN rule, rather than asking whether a smaller refitted model captures the useful separation. These are different targets.

ARI .95 also does not mean 95% point agreement. With approximately balanced groups on 120 rows, only two changed assignments can lower ARI to about .934. Future reduction experiments should report aligned assignment disagreement, partition ARI, external-label agreement and uncertainty separately, with thresholds fixed before evaluating confirmation data.

## Prepared next run: keep the candidate bank fixed

`scripts/run_research_ranking_followup.py` replays the six mean-shift and METABRIC search runs. It verifies source hashes, data reconstruction, preprocessing and baseline selections before comparison.

For each case it scores 24 additional random reference panels at each represented size, then applies four policies to the **unchanged pilot candidates**:

1. Original pilot global units.
2. Global units from the larger new reference bank, controlling for bank precision/composition.
3. Size-specific means with common within-size scales, isolating removal of average size offsets.
4. Size-specific means and scales, additionally adjusting within-size variability.

The new reference masks never become candidates. Labels enter only reporting. Unsupported sizes are rejected explicitly instead of receiving unstable fallback scales. The original scoring implementation and pilot outputs remain unchanged.

This is **development reanalysis of already inspected splits**. Any apparent gain needs later confirmation on fresh data under a fixed method. It is neither a new significance test nor a proposed final fitness. The bounded 12-references-per-size seed-0 checks replayed both mean-shift and METABRIC successfully; the mean-shift check did not produce a general recovery/minimality fix.

Run in PowerShell:

```powershell
Set-Location "C:\Users\Peter\Desktop\Github\ATOMIC_Clustering"
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_ranking_followup.py"
```

The full six-case, 24-per-size comparison is prepared and **not yet run**. It writes a new timestamped folder under `results/research_ranking_followup/`, including the reference bank, calibration diagnostics, replayed winners, assignment rules, manifests and `summary.md`. Completed case outputs survive interruption. Old pilot files are never overwritten.

The 19 calibration checks and three follow-up selection/reference checks passed together (**22 passed**). Two bounded integration runs successfully replayed the saved baseline panels and metrics before evaluating alternative scaling. Their folders are under `results/research_ranking_followup_smoke/` and are development checks, not the full follow-up.

## What follows from each outcome

- If size adjustment improves compact selection while preserving useful assignments, confirm that mechanism on fresh seeds before combining it with other changes.
- If candidate quality remains poorly ranked within a size, stop treating score scaling as the main explanation. Test objectives matching the target population structure, and retain multiple distinct candidate partitions during development.
- If native learned assignments outperform hard-mask spectral refits, preserve the model's representation, weights and assignment rule as part of the method. A feature panel alone is not the whole learned object.
- For nonlinear cases, test whether a limited original-feature dictionary can express and autonomously discover the structure. The successful oracle transform must remain excluded from discovery claims.
- Redesign compression independently, allowing a smaller model to refit while measuring both preserved structure and useful predictive assignment. Do not force every smaller panel to reproduce incidental errors of the original rule.

The novelty opportunity is a concrete procedure for **local panel discovery, preservation of its learned partition, and verifiable reduction with interchangeable features**. Sparse weighting, projection pursuit, multiobjective scoring and stability are already established ideas. The contribution must be the particular mechanism and its demonstrated benefit, not their renaming or assembly alone.
