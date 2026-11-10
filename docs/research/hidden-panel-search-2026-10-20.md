# Hidden-panel search: first controlled comparison

## Material Passport

- Origin Skill: academic-research-suite, experiment implementation and verification
- Origin Date: 2026-10-20
- Verification Status: smoke and 36-case pilot complete and independently audited; 181 related tests passed
- Version Label: hidden_panel_search_v1
- Scope: development experiment on synthetic radial geometries, not established novelty, real-data usefulness, or calibrated split inference
- Basis: [trait-first plan](trait-first-research-plan-2026-10-14.md), [completed supplied-panel pilot](../../results/research_radial_diagnostic/20261020T021208_103657Z/summary.md)

## Question and frozen comparison

The previous pilot established that the model can represent separated shells and rank the supplied informative panel above a few alternatives. It did not establish autonomous panel discovery. This experiment asks whether the same objective can recover useful panels without receiving their identities or size.

The model, likelihood comparison, fit-only centering/scaling, and numerical bounds are unchanged. We change panel proposals only. Each arm receives the fit and search matrices, a fixed feature-count cap, a budget and an independent random seed. It never receives the case name, true dimension, labels, support, feature map, validation block or test block.

Four arms use the same number of distinct two-band radial fits:

1. **Random:** uniformly sample a size from 1 to the cap, then a support of that size; reject duplicates.
2. **Random plus local:** use half the budget for random proposals, then add/drop/swap best-improvement neighborhoods. Restart randomly after a local optimum.
3. **Dependence plus local:** share the initial random proposals, replace the rest of the exploration half with chains built from absolute correlations of squared standardized features, then use the same local search.
4. **Shuffled dependence plus local:** perform the same dependence calculation and chain procedure, but permute which features the matrix refers to. Data are unchanged. This preserves the matrix values and proposal machinery while disrupting their association with the measurements.

All arms share their first `min(8, budget // 2)` random candidates (one when budget is one). Dependence chains are greedily grown from each feature and shuffled across roots and lengths; only scored panels consume the evaluation budget. Duplicate proposals never trigger a second fit. Each arm has a separate cache. A partial local neighborhood may exhaust the budget; this is recorded, not hidden by extra evaluations. The best score seen anywhere is retained. No search knows the true panel size; the common cap is 10.

The search uses an unchanged score: mean held-out two-band log density minus the covariance marginal of one fit-only joint Gaussian background. Maximize this score; break exact ties by fewer features, then evaluation order. No shape flag, annotation or test score changes the selected panel. A one-band comparison is fitted afterward for that selected panel. The supplied-support oracle is fitted after all search arms, outside their budgets, and cannot seed or steer them.

The dependence statistic is only a proposal heuristic. Squared-coordinate correlations may be negative or positive for shell populations, so absolute values are used. For the current radial distribution, pairwise squared-coordinate correlations nearly cancel around four signal dimensions. Dimension four is deliberately included as a stress case; failure there would not by itself invalidate the radial representation. This statistic is not guaranteed to detect general higher-order interactions.

## Data isolation and accounting

There are four nonoverlapping, independently drawn observation blocks from one fixed population map:

- **Fit:** fit every model, the background and the dependence statistic.
- **Search:** adapt proposals and choose the panel.
- **Validation:** check the frozen panel and compute the existing provisional flag, without reselection or refitting.
- **Test:** describe independent gains and external ARI after the panel is frozen.

The existing generator draws fit and search together as one independent stream, then splits its rows at the recorded boundary. Validation and test retain separate streams. In the pilot each block has 600 observations, so fitting itself uses the same number of rows as in the preceding pilot. Nuisance measurements retain matched one-dimensional marginals. Seeds differ from preceding experiments.

Equal fit counts are not equal wall time. Record preprocessing time, total search time, duplicate proposals, panel-size histograms, full best-score traces and nonconverged optimizer statuses. Finite nonconverged fits remain eligible exactly as in the existing fitter; these statuses are reported explicitly. Fatal exceptions stop the run and are saved in its manifest.

## Development suites fixed before execution

| Suite | Data/search seeds | Cases | Features | Rows per block | Unique fits per arm |
|---|---|---|---:|---:|---:|
| Smoke | 2309 / 3101 | Shells d=2,4,8; single shell d=5; correlated Gaussian d=5; mean shift d=3 | 14 | 160 | 48 |
| Pilot | 2401/3203, 2411/3217, 2423/3221 | Shells d=2,3,4,5,8; single shell d=2,5; independent Gaussian, correlated Gaussian, Student-t, common-center scale mixture d=5; mean shift d=3 | 24 | 600 | 256 |

The pilot has 36 population draws, four arms and 36,864 two-band search fits. It is a development comparison, not a power calculation or confirmatory study. Only one search seed is paired with each population draw; this does not separate optimizer-seed variability from data-sampling variability. If differences look useful, cross more search seeds with fixed populations before claiming robust superiority.

## Outcomes and decisions

Report per case and seed: support precision/recall/exact recovery, whether the oracle support was encountered naturally, selected panel size, search and fresh validation gains, test ARI, provisional flags and cost. Exact planted support is not a quality target for Gaussian or heavy-tail controls that have no privileged cluster panel. Assignment quality and feature identity can disagree, especially for substitutable or partially sufficient measurements.

- If the oracle works but searches never encounter it, inspect proposal coverage and local barriers.
- If the oracle is encountered but loses by search score, inspect scoring and search-split overfitting rather than simply increasing optimizer effort.
- If search gains improve while fresh validation gains deteriorate, investigate adaptive overfitting.
- If dependence proposals outperform both random/local and shuffled-dependence/local, test the mechanism on more seeds and harder conditions; this alone does not establish novelty.
- If all methods work similarly, prefer the simpler search and reassess what methodological contribution remains.
- If control flags increase after search, the next task includes a scoped acceptance procedure. Current flags remain heuristic.

This experiment does not establish the smallest sufficient panel, a real application, a hierarchy, or superiority over established sparse-clustering methods. Forward/backward baselines, strong published comparators, and a real-data preflight remain later checks before a contribution claim.

## Commands

The smoke and larger pilot are complete; **do not rerun the pilot as the next step**. The pilot took 36.12 minutes and passed 793,616 saved-state audit checks. See the [pilot assessment and bounded next design](radial-search-pilot-assessment-2026-10-20.md). The command below is retained for reproducibility.

Run from PowerShell using the existing environment; activation is unnecessary:

```powershell
Set-Location "C:\Users\Peter\Desktop\Github\ATOMIC_Clustering"
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_radial_search.py" --suite pilot
```

Every invocation creates a new timestamped directory under `results/research_radial_search`. Raw splits, generator metadata, every evaluated support and fitted model, selected rules, predictions, summaries, package versions and source snapshots are saved. Progress is printed per case and arm.

For a failed or interrupted run with unchanged source, `--resume` copies completed jobs into a new directory and restarts incomplete jobs while preserving the parent. It rejects configuration overrides and changed source. Use the path printed by the failed run:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_radial_search.py" --resume ".\results\research_radial_search\REPLACE_WITH_RUN_DIRECTORY"
```

For independent saved-state verification:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\analyze_research_radial_search.py" ".\results\research_radial_search\REPLACE_WITH_RUN_DIRECTORY"
```

The audit verifies saved calculations and bookkeeping; it does not certify scientific cluster validity.

## Completed smoke findings

Saved run: [20261020T142817_892315Z](../../results/research_radial_search/20261020T142817_892315Z/summary.md).

Six cases, four arms, 48 unique fits per arm: **1,152 search fits**, with zero recorded optimizer nonconvergence statuses. No supplied panel was injected into any search. The supplied diagnostic panel was fitted afterward, on the same fit rows.

| Shell dimension | Supplied-panel test ARI | Random | Random + local | Dependence + local | Shuffled dependence + local |
|---|---:|---:|---:|---:|---:|
| 2 | 1.000 | -0.004 | -0.004 | 0.209 | 0.001 |
| 4 | 1.000 | 0.003 | 0.003 | 0.003 | 0.003 |
| 8 | 1.000 | 0.809 | 0.926 | 0.721 | 0.950 |

None of these twelve shell searches evaluated the exact planted panel. In all three shell cases, its post-search diagnostic score exceeded every arm's best search score. At this small budget, the missed panel therefore reflects proposal coverage, before a potential question of rejecting it by score. This does not prove that the fitness is universally adequate.

On the eight-feature case, ordinary local search selected seven true features, with test ARI 0.926. Shuffled dependence selected all eight true features plus one nuisance feature and reached 0.950. These observations illustrate why feature count, purity, support recall and recovery must be reported separately. They provide no advantage claim for the unshuffled dependence heuristic, which selected five true features and performed worse here.

The single-shell and correlated-Gaussian controls were unflagged for every arm. On the two-feature shell case, random and random/local selected an unrelated singleton and flagged it, despite near-zero ARI to the intended shell labels. Its matched marginal can contain another structured partition; a flag is not evidence of the intended population or scientific meaning. The radial method continued to fail on mean-separated labels, the deliberately out-of-scope geometry.

Only one population/search seed pair and 160 observations per block were used. This smoke verifies execution and reveals obstacles; it cannot establish comparative reliability or a false-positive rate. The larger pilot keeps the planned four arms, introduces fresh seeds, and raises both sample count and search budget. It does not retune the fitness to this result.

Verification:

- **173 tests passed** across the existing radial model/pipeline/recovery and the new four-arm search, data-isolation and recovery tests; **8 additional auditor tests passed**. Total: **181**.
- The [independent saved-state audit](../../results/research_radial_search/20261020T142817_892315Z/audit.json) passed **27,657 checks**, zero errors, covering all 24 method runs and 1,152 evaluated panels. Every saved search score was replayed; independent normalization integration was performed for selected/oracle models.
- Metamorphic tests change labels, true support, feature metadata and validation/test observations without changing the saved search trajectory or fitted models.
- The runner's resume validation was strengthened after the smoke snapshots were taken. The audit checks the archived source identity and reports that difference. Search and model calculations for the smoke are preserved.

Next decision: run the planned pilot before introducing another proposal mechanism. If the supplied panels retain a clear score advantage but remain unvisited, prioritize a stronger proposal/search mechanism. If visited panels lose, investigate objective behavior or selection noise. If search scores fail to carry over to fresh validation, investigate overfitting. Stronger comparison methods and real-data validation remain necessary before a thesis contribution claim.
