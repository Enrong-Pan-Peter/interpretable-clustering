# ATOMIC: separating panel discovery, ranking, and verification

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: experiment planning and user-authorized prototype implementation
- Origin Date: 2026-09-14
- Verification Status: 57 targeted checks passed; short diagnostics executed; efficacy, scaling, and novelty UNVERIFIED
- Version Label: panel_diagnostics_v1
- Evidence: saved local results, source audit, and primary papers linked below and in the companion research notes

## What we are trying to achieve

Discover a small set of original-feature panels that support useful, understandable clustering. A panel should have a demonstrable role: its partition survives new observations; deleting features has a measurable consequence; substitutes and redundant features are acknowledged; and biological interpretations can be checked against external knowledge. Shapes and readable assignment rules are valuable outputs. A large score, a familiar gene name, or a five-feature mask is insufficient by itself.

Panels larger than three must be reachable without initializing the search by enumerating all pairs or triples. They must also be useful: returning five features when one does the same work does not demonstrate a larger-panel capability. There is no requirement to invent every primitive. A contribution could be a specific, effective procedure for discovery and verification, with established components and explicit assumptions.

The previous source/result audit remains in `docs/research-assessment-2026-09-09.md`. Historical code and results were preserved. The new code lives separately in `atomic_research/`.

## Global research skill installation

Installed and enabled **ars-codex@ars-codex, version 0.1.28**, from `Imbad0202/academic-research-skills-codex`, ref `main`, in the user's global Codex configuration. Verified installation path:

`C:/Users/Peter/.codex/plugins/cache/ars-codex/ars-codex/0.1.28`

Its `academic-research-suite/SKILL.md` router and experiment-agent planning materials were read. A fresh Codex session can discover the installed skill normally; the files were used directly in this task. No executable research hooks or external-model services were enabled. The user's explicit authorization to build scripts governs this work.

Three agents independently contributed the scoring/statistics audit, smooth graph prototype, and mathematical alternatives plus sparse k-means comparator. Two also reviewed the integrated harness. Their findings were checked and incorporated.

## Is fitness the major problem?

**It is a demonstrated problem, but there are at least three independently testable failures.**

| Failure | Diagnostic | Appropriate response |
|---|---|---|
| Ranking | Useful visited panels receive a worse score than poor panels, on the same rows and same splitter | Change the objective's target, partition consistency, or selection procedure |
| Search | A useful panel has a better objective value, but optimization misses it | Change representation, initialization, proposals or search feedback |
| Splitting/geometry | The splitter fails even with the planted panel | Change geometry, splitter, model assumptions, or sample size before blaming feature search |

The old hybrid can add a graph score for a spectral partition to a density score for an MST partition. That combination need not describe the returned split. Its candidate-pool standardization can also change the relative weighting as the pool changes. The old EA experiment's raw score and the successful enumerative experiment's standardized score are not interchangeable comparisons.

Column permutations provide an **independence null**, not a no-clusters null. A correlated single Gaussian violates independence. A visibly bimodal singleton is invariant to shuffling its only column. Averaged or maximized z-scores do not become cluster probabilities. Increasing an optimizer's ability to maximize such a statistic cannot repair its target.

Even a coherent score can favor an unhelpful partition. A density valley and an overlapping mixture component are different targets. This matters for expression subtypes: external groups need not be separated by an empty Euclidean gap. A stable, predictable Gaussian partition can still be scientifically arbitrary.

## What is implemented

The harness tests a **single binary local split**, before adding hierarchy, automatic cluster count and recursive stopping. It does not claim a complete new clustering method or a calibrated split-existence decision.

### Proposal methods

1. Random masks, balanced approximately across requested sizes.
2. Budgeted forward growth with randomized extension shortlists. It does not consume the whole budget inspecting singletons when p is large. Unspent budget is filled randomly.
3. A simple add/drop/swap evolutionary baseline with elite parents and random immigrants. **This is not the repository's NSLC engine**, and results must not be attributed to that engine.
4. A smooth spectral proposal optimizer: jointly learn nonnegative feature weights, then submit ranked prefixes. It minimizes a normalized graph eigenvalue plus explicit degree and entropy penalties. No neural framework is required.
5. An established sparse k-means comparator: alternate weighted clustering and constrained sparse feature weighting, retaining candidate prefixes from several starts and sparsity settings.

All support a configurable maximum panel size beyond three. None enumerates all pairs/triples as search initialization. The smooth graph objective is not DUFS; sparse k-means is not CHIME. Ranked unweighted panels can lose structure from their learned weighted geometry. A future experiment must compare retaining the learned partition/metric with re-splitting the rounded panel.

See `soft-graph-notes.md` for equations and numerical caveats, and `math-search-directions.md` for the statistical alternatives and prior art.

### Common scoring and resource accounting

`score_panel` returns separate graphcut and density components for the **same returned partition**, alongside the old components and the agreement of their partitions. The density term is an explicitly identified DBCV-style surrogate, not full DBCV. The historical kNN graph/bridging convention is retained for comparison.

A discovery-only random reference bank fixes the comparison units once. Every scalar profile uses the **same eligible reference intersection** (`valid` and `legacy_valid`), and the same eligibility intersection is used for selection. This isolates objective changes from validity-policy and graph-weight changes. It is a diagnostic restriction, not an optimal production rule. If too few reference panels are eligible, the saved count exposes that; the implementation uses declared fallback scales rather than estimating significance.

Discrete methods receive equal caps on unique panel scores. Smooth graph and sparse k-means receive that cap **plus separately recorded training work**. Their candidate banks can be smaller than the cap; they are not padded with random candidates. Optimizer steps/eigensolves, k-means fits, proposal time, scoring time and total search time are saved. A common reference bank is additional shared setup cost. Post-selection validation/reporting is additional work. **These are not matched-wall-time or matched-total-compute comparisons.**

### Discovery, compression and confirmation

Rows are split 50/25/25 without labels or stratified retries. Median imputation and standardization are fit on discovery rows only. Panel proposals and scoring see only discovery X. External annotations are used after selection, for reporting.

The selected discovery partition defines a distance-weighted 7-nearest-neighbour assignment rule. Backward deletion removes a feature only if the reduced rule retains at least 0.95 ARI agreement with the original rule on validation rows. All deletions are judged against the frozen original rule. This produces a locally irreducible panel at that tolerance, not a globally minimum panel.

The untouched test split reports external-label ARI, compression fidelity, independently re-fitted clustering agreement, and geometry of the transferred partition. Invalid independent fits retain their failure reason and do not produce replication ARIs. Compression fidelity measures preservation of a discovered partition, not its scientific truth.

Each selected panel also gets a depth-three tree surrogate and its test fidelity. Thresholds are in standardized units. A low-fidelity surrogate must not be described as an exact explanation. Saved assignment data and preprocessing support predicting new observations; this remains an exploratory candidate rule.

### Dataset controls

- **Distributed mean shift:** 5 or 8 informative features, fixed total mean separation. Each feature has a weaker contribution as the signal is distributed. Smaller subsets retain some information; indispensability is measured, not assumed.
- **Concentric shells:** 5 or 8 radial coordinates with independently generated nuisance features having the same univariate marginal distributions. The model is not secretly given informative column names. This does not assert that every smaller subset is uninformative.
- **Negative controls:** independent and correlated Gaussian populations; a bimodal singleton distinguishes cluster separation from dependence testing. These runs do not measure a false split rate because no split-acceptance rule exists yet.
- **METABRIC:** the existing PAM50-plus-200 matrix, LumA/LumB by default. PAM50 is contextual reference information, not a uniquely correct minimal panel. The cached gene universe already used an all-patient variance filter; only the new imputation/scaling is discovery-fitted. This is a development dataset, not pristine external confirmation.
- **Levine:** CD4/CD8 contrast by default, using the existing FCS and arcsinh(count/5). Population naming is repository-derived. Cell holdout within existing specimens is not independent donor replication. Marker lists are contextual references, not proof that every named marker is necessary.
- **Mice:** available as an optional 72-animal, replicate-aggregated diagnostic. Small held-out groups limit what its geometry can establish.

Real-data contrasts are predeclared using annotations to define a scoped benchmark population. The algorithms then receive only its X. This does not demonstrate discovery of the whole unfiltered hierarchy.

## Short checks already completed

The result index is `results/research_checks_20260914/summary.md`. These are small, single-seed development checks, not efficacy estimates.

**METABRIC:** 240 sampled patients, 250 genes, 120 discovery rows, 32 scored panels per method. The same consistent score was used across methods.

| Proposal method | Best eligible visited training ARI | Selected training ARI | Selected transferred test ARI |
|---|---:|---:|---:|
| Random | 0.436 | 0.127 | 0.096 |
| Simple evolutionary | 0.459 | -0.009 | -0.016 |
| Smooth graph | 0.396 | -0.009 | -0.013 |
| Sparse k-means | 0.418 | -0.004 | 0.024 |

This is a ranking warning on discovery rows. The retrospective best-visited ARI is label-informed diagnostic information, not an achievable unsupervised selection rule or independently confirmed performance. The separate full-PAM50 diagnostic reached transferred test ARI 0.481 in this run; it was not injected into search and exceeds the search size cap.

**Mean shift:** in a reference-augmented bank, the true five-feature panel had training ARI 0.749. A four-feature panel selected by the combined score had test transfer ARI 0.869. Because the candidate bank explicitly includes the reference panel and its deletions, this diagnoses scoring and sample variation; it is not a discovery success.

**Five-dimensional shells:** the spectral splitter's training ARI on the true panel was -0.006 at 120 discovery observations. This immediately prevents interpreting every failed search as a feature-finding failure. A radial model, another graph, or more data needs investigation.

**Null target:** the bimodal singleton had permutation p=1 for both tested statistics, exactly as the invariance argument predicts. With only 19 permutations, the correlated Gaussian's correlation statistic had p=0.05 and graphcut p=0.10. These are dependence comparisons; neither result validates a no-clusters test.

**Other optimizer checks:** the soft-graph agent documented a separated-singleton example in which the oracle feature had a better objective but optimization missed it. Gradients were numerically correct. This demonstrates that making a score differentiable does not eliminate local optima.

The Levine smoke loaded and ran all five methods successfully. Some assignments had perfect agreement on its 40 held-out cells; that small scoped contrast is insufficient for any general biological performance claim.

## Run this next

Run from a PowerShell terminal in `C:/Users/Peter/Desktop/Github/ATOMIC_Clustering`. The isolated environment is already installed. No environment activation, GPU, API key or external service is required.

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_suite.py --suite pilot
```

This runs 19 serial jobs: three null-target diagnostics, four paired score audits, and four search cases across seeds 0, 1 and 2. Larger runs use 480 total rows, 100 scored panels per search method, and the declared optimizer settings. Allow several minutes; exact timing is printed. The full pilot has **not** been run in this task. Ctrl+C stops it; completed run folders remain. Re-running creates new timestamped folders and does not overwrite results.

The summary is written to `results/research_diagnostics/summary.md` and `summary.csv`. Each run includes configuration, source hashes (including imported legacy code), dependency versions, data split/preprocessing, candidate records, proposal traces, full/partial summaries, selected assignment data and readable rule approximations. A failed run's manifest records the error. Do not mix stale versions just because filenames are similar.

To inspect the exact planned jobs without running:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_suite.py --suite pilot --list-only
```

After inspecting the pilot, the larger-panel sweep is available:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\run_research_suite.py --suite scaling --seeds 0 1 2 3 4 --output results/research_scaling
```

It tests 5- and 8-feature signal, 50 and 200 total features, both synthetic regimes, 800 total rows and a search cap of 12 features. This is 40 runs and can take substantially longer. It is prepared, not executed. Keep success thresholds fixed before inspecting these results.

For a targeted diagnostic or alternative scalar, use `run_research_diagnostics.py --help`. For example, `search --dataset metabric --objective graphcut --seed 0` changes only the declared objective; it does not turn ARI into fitness. To regenerate a summary after interrupted or additional runs:

```powershell
.\.venv-research\Scripts\python.exe .\scripts\summarize_research_results.py --root results/research_diagnostics
```

The exact installed versions are recorded in `requirements-research-lock.txt`; `requirements-research.txt` describes the compatible dependency range. New-point use is documented by `predict_research_panel.py --help`; Levine inputs must already be arcsinh-transformed, and output cluster names are arbitrary algorithm labels.

## Decisions after the pilot

1. **If useful panels are visited but consistently ranked away:** stop spending effort on more EA generations. Compare selection that retains distinct partitions and separate quality components. For overlapping populations, test a model matching that target instead of requiring a density gap. Do not pick weights by the final test ARI.
2. **If the reference panel works but is absent from proposals:** change proposal information and representation. Compare retaining learned weighted geometry, better initialization, conditional feature updates and published implementations. Our current continuous relaxation has not earned a recommendation as the winner.
3. **If the reference panel fails the splitter:** test original-space geometry, sample size and alternative splitters first. For radial structure, grouped linear/quadratic projection pursuit can express a multi-feature radius without enumerating subsets.
4. **If performance is good but panels have passengers:** tighten or replace the compression procedure, examine feature substitutions, and compare to equally compact baselines. A five-feature output counts as evidence beyond three only when its additional features have reproducible value.
5. **If all controls are partitioned convincingly:** define a scientifically meaningful acceptance/null model before building a recursive hierarchy. Stability, surrogate fidelity and independence rejection are insufficient on their own.

The next serious statistical comparator is **CHIME-style sparse discriminant mixture fitting**, which estimates a sparse assignment direction rather than enumerating masks. Under shared covariance the relevant direction is `beta = inverse(Sigma) (mu1-mu0)`. A feature with no marginal mean shift can still help adjust correlated nuisance, so marker lists and assignment panels need not match exactly. [Cai, Ma and Zhang, 2019](https://drjingma.com/papers/cai-chime).

The nonlinear alternative is a small grouped dictionary of original features and their squared values, with a constrained projected valley/dip objective. It can express a radius involving five or more original features and return a readable rule. Projection pursuit for density separation is established; transformations can manufacture modes, so the proposed partition still needs checks in original coordinates. [Minimum Density Hyperplanes, 2016](https://www.jmlr.org/papers/v17/15-307.html).

Deep learning is optional when it supplies useful proposal information that these smaller models lack. RL receiving the same defective reward does not fix the target. Any learned policy must include its training cost and disclose external knowledge. Differentiable group discovery already has close prior art, including [GroupFS, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/39521).

A defensible novelty direction is a **specific local panel discovery-and-reduction procedure with explicit partition preservation, interchangeable-feature handling, and independent evidence**, supported by measurable gains over straightforward combinations of existing methods. Those general ingredients alone are not a novelty claim. The mathematical report identifies narrower theoretical targets and failure assumptions. We have built the tools to choose a direction on evidence; we have not yet established a novel effective method.
