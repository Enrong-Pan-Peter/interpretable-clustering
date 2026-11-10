# First executable node experiment: radial representation and panel ranking

## Material Passport

- Origin Skill: academic-research-suite, experiment implementation and verification
- Origin Date: 2026-10-15
- Verification Status: smoke verified; full 36-job pilot completed after the 2026-10-19 boundary repair, with 18,031 saved-state audit checks passed
- Version Label: radial_node_diagnostic_v1
- Scope: known-panel mechanism and fixed candidate-ranking diagnostic, not autonomous feature discovery, established novelty, calibrated cluster acceptance or a complete hierarchy
- Protocol basis: [trait-first plan](trait-first-research-plan-2026-10-14.md) and [mathematical design](trait-first-method-review-2026-10-14.md)

## Pilot completion update, 2026-10-19

The pilot is complete; no rerun is needed. See the [completed results](../../results/research_radial_diagnostic/20261020T021208_103657Z/summary.md), [audit](../../results/research_radial_diagnostic/20261020T021208_103657Z/audit.json), and [boundary repair and recovery record](radial-boundary-fix-2026-10-19.md). The results directory uses UTC, which was already October 20. Seventeen completed jobs from the failed run were copied unchanged, and the remaining nineteen jobs were completed with the numerical boundary repair. The original run is preserved.

## How to run a fresh pilot

Run this in PowerShell. It uses the existing research environment directly; activation is unnecessary.

```powershell
Set-Location "C:\Users\Peter\Desktop\Github\ATOMIC_Clustering"
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_radial_diagnostic.py" --suite pilot
```

The pilot has **36 jobs**: 12 population/dimension settings across seeds 1201, 1213 and 1229. Each job uses 24 available features and independent blocks of 600 fitting, 600 validation and 600 test observations. It evaluates up to 10 fixed candidate panels, including the supplied informative support, partial panels, supersets and random/nuisance alternatives. All candidates and outcomes are retained.

The seeds differ from the smoke run. This is still a development pilot, not a confirmatory study or a formal power calculation. The smoke run took about five seconds for five smaller jobs; the larger pilot may take minutes depending on the computer. Progress is printed after each candidate and job.

Results go into a new timestamped directory under `results/research_radial_diagnostic/`. Wait for the `Complete` message. The script saves `manifest.json`, `summary.md`, `summary.csv`, `summary.json`, per-job raw splits, model parameters and predictions. Source snapshots and hashes preserve the implementation used for each run. Existing results are not overwritten.

To inspect the job list without running it:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_radial_diagnostic.py" --suite pilot --list-only
```

An interrupted or failed run preserves completed candidates and a manifest status. A fresh invocation makes a new directory. To recover a compatible run, use `--resume` with its directory; the runner verifies configuration and source compatibility, records provenance, copies completed jobs unchanged into a new directory, and restarts unfinished jobs. Do not manually combine partial results. The repair record contains the recovery command used for this pilot.

## What is actually implemented

`atomic_research/radial_panels.py` fits one- and two-band densities on a supplied original-feature panel. Preprocessing is estimated only on fitting observations. The two-band model shares a width, allowing an exact rule of the form

`sum_j ((x_j - center_j) / scale_j)^2 > threshold`.

The selected measurements, centres, scales and threshold are saved in original measurement units. No fitted latent embedding is required for prediction. The equation defines the native assignment, rather than approximating a separate graph classifier.

The spatial density is normalized in the selected dimension, including the sphere-area factor. The plotted/computed spatial profile is kept distinct from the radius probability density. A joint Gaussian background is fitted once on discovery-standardized measurements; candidate scoring uses its covariance marginal, with the appropriate change-of-units factor. Thus likelihood gains have a common full-observation-space interpretation despite different support sizes.

The runner fits centroids and one-/two-component diagonal Gaussian mixtures on the same candidate panel. These are basic mechanism comparators, not a complete set of sparse-clustering or interpretable-clustering competitors. It selects the radial candidate using validation gain only. Test outcomes describe that frozen selection. It also reports the supplied panel separately so a poor selected panel cannot conceal whether the correct panel was representable.

The candidate list deliberately includes the true support. This is an **oracle-assisted ranking experiment**. Neither its best ARI nor its ranking success establishes autonomous support search. The five-/eight-feature cases establish that the model and evaluation can operate beyond triples; they do not prove that every one of those features is necessary.

## Locked pilot cases

| Case | Dimensions of supplied panel | Purpose |
|---|---|---|
| Two noisy radial bands, lognormal radial thickness | 2, 3, 5, 8 | Test a restricted nonlinear geometry with an off-model generator |
| Two bands from the proposed quartic spatial family | 3 | Approximate on-model numerical check; inverse-CDF grid details recorded |
| One noisy band | 2, 5 | Check whether a single supplied population is subdivided |
| Independent Gaussian | 5 | Simple one-population reference |
| Correlated Gaussian | 5 | Test whether dependence is confused with radial populations |
| Elliptical Student-t | 5 | Heavy-tail stress control |
| Shared-centre Gaussian scale mixture | 5 | Latent scale groups without separate spatial density modes |
| Mean-separated mixture | 3 | Show whether a different native rule family is necessary |

Every nuisance coordinate is an independent draw from the same one-coordinate marginal as a signal coordinate. This removes the easy shortcut of identifying the supplied panel from variance alone. It also introduces an interpretation limit: a projected single ring, especially in two dimensions, can have a multimodal marginal. Its independently generated nuisance features can therefore support other structured partitions. Report **control flag frequencies**, with supplied-panel results separate from other-panel results; do not call all such alternatives false clusters.

Labels enter external evaluation. Support truth enters construction of the diagnostic candidates. Neither labels nor test observations enter model fitting or validation selection. Within a job, the population transform and feature permutation are identical across independently generated blocks.

## Provisional split diagnostics

The experimental flag requires:

1. Positive validation predictive gain over the shared Gaussian background.
2. Positive validation gain over the one-band model on the same support.
3. Two modes in the fitted spatial profile, with valley height no greater than half the smaller peak.
4. At least 10% of validation observations assigned to each group.

These thresholds are fixed prototype diagnostics, not established optimal cutoffs. They do not provide a p-value, a false-discovery guarantee or proof that two scientific populations exist. The corresponding flag recomputed on test data is descriptive and cannot change the frozen validation decision. The native two-band model can still output two labels when the diagnostic flag is false.

Fitting is bounded deterministic multistart optimization. Convergence, bound hits and actual group occupancy are recorded. Mixing-weight bounds alone do not ensure both predicted groups have useful mass. Inspect these diagnostics before treating a fitted result as a useful candidate.

## Completed smoke evidence

Saved run: `results/research_radial_diagnostic/20261014T224834_060578Z`.

It contains five jobs, eight candidates per job, 120 observations in each block, and seed 811. On both two- and five-dimensional shell cases, the supplied informative panel ranked first by validation gain and its native rule obtained test ARI 1.000. These deliberately well-separated synthetic cases are a representation/ranking sanity check.

The correlated-Gaussian and Student-t cases each had zero flagged candidates out of eight on validation and test. Two small control jobs cannot establish a false-positive rate. The mean-shift case was poorly represented by the radial family, supporting retention of the existing linear branch rather than a universal radial objective.

Verification completed:

- **67 tests passed**, including independent adaptive integration, closed-form normalizers, derivatives, change-of-units invariance, Gaussian marginal cancellation and exported-rule replay.
- A pipeline isolation test changed all annotations and the entire test feature block; fitted radial parameters and validation selection stayed unchanged.
- An independent saved-state audit passed **2,033 checks with zero discrepancies** for all 40 candidates. It replayed native and comparator predictions, normalization, gains, reported ARIs and validation selection without importing the radial implementation.
- Historical source files were archived only after matching their recorded hashes. Subsequent changes affect reporting terminology, future pilot seeds and automatic source archiving, not the completed smoke fit.

The smoke evidence above is historical. The full pilot was subsequently completed as recorded in the update above. Neither experiment establishes a new algorithm or superiority to state-of-the-art clustering.

## How the pilot determines the following step

| Outcome | Next development action |
|---|---|
| Supplied-panel rule fails on clear separated bands | Repair the model or numerical implementation before feature search |
| Supplied panel works, but its objective loses to unsuitable candidates | Repair the comparison/selection objective; a stronger optimizer would pursue the wrong target |
| Useful panel ranks well across dimensions and controls remain acceptable | Implement bounded add/drop/swap and block-support exploration, compared at equal budget with random search |
| Single-population controls frequently pass the provisional flag | Develop a scoped acceptance procedure; do not present stable assignments as cluster evidence |
| Established comparator achieves the same capability and complexity | Reassess the proposed distinguishing mechanism before making a novelty claim |

We do not need another general fitness sweep before inspecting this experiment. Its purpose is to locate the next repair. The full application benchmark and the hierarchy remain later milestones.

For a completed run, an independent audit is available:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\analyze_research_radial_diagnostic.py" ".\results\research_radial_diagnostic\REPLACE_WITH_RUN_DIRECTORY"
```

The audit writes `audit.json` beside that run. It verifies saved computation, not biological validity or independent experimental replication.
