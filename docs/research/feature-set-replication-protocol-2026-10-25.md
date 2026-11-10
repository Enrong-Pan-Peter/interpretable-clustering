# Frozen feature-set search: replication and stress protocol

## Material Passport

- Origin Skill: academic-research-suite, experiment implementation
- Origin Date: 2026-10-25
- Version Label: feature_set_replication_v1
- Status at protocol creation: full replication not run; settings fixed before the separate smoke check
- Follow-up on 2026-10-31: the full run completed and passed its saved-state audit. See [findings and scope decision](feature-set-replication-assessment-2026-10-31.md); the prospective settings below are preserved.
- Basis: [ablation assessment and frozen candidate](feature-set-ablation-assessment-2026-10-25.md)
- Scope: one bounded synthetic replication/stress batch, not application validation or a novelty claim

## Fixed comparison

Compare `kernel_best` with `moment_best`. Each receives 256 distinct candidate fits, a maximum feature-set size of ten, and 600 rows in each of fitting, adaptive search, validation and test. The fitted radial model, predictive fitness, background model, local refinement and provisional split flags are unchanged. Both methods see the same observations for each population and use the same search seed.

The runner verifies SHA-256 identity of the four frozen scientific source files. The experiment adapter adds an optional data-generator argument and condition labels in reports. Its fitting, selection, oracle diagnostics and split-flag computations must retain the same parsed Python structure as the archived pipeline after removing that one generator hook. Source snapshots and the frozen candidate record accompany each run.

Use data seeds **5101, 5113, 5119**, crossed with search seeds **6101, 6113**. These differ from the inspected development and smoke seeds. Repeated search seeds reuse identical data; they measure algorithm variability, not additional independent population replicates.

| Condition | Cases | Features available | Data/search combinations | Jobs |
|---|---|---:|---:|---:|
| Baseline replication | Shells with 2, 3, 4, 5, 8 informative features; single shells with 2 and 5; independent Gaussian, correlated Gaussian, Student-t, common-center scale mixture with 5; mean shift with 3 | 24 | 3 x 2 | 72 |
| More nuisance measurements | Shells with 4, 5, 8 informative features | 72 | 3 x 2 | 18 |
| Weaker separation | Shells with 4, 5, 8 informative features | 24 | 3 x 2 | 18 |
| Dependent nuisance groups | Shells with 4, 5, 8 informative features | 24 | 3 x 2 | 18 |

Total: **126 jobs, 252 method runs, 64,512 search fits**, representing **63 distinct populations**, each searched twice. The three data seeds per condition remain a small replication sample.

## Stress definitions fixed before execution

Baseline and more-nuisance data use the original generator unchanged: shell radii 1.5 and 3.5 times the square root of informative dimension, log-radius standard deviation 0.06, and independently sampled nuisance coordinates with matched population marginals.

Weaker separation uses radii **2.0 and 3.0** times the square root of informative dimension and log-radius standard deviation **0.12**. Its independently sampled nuisance measurements match the revised signal marginals. This changes separation and thickness together as one declared harder condition; it does not identify their separate effects. The supplied-feature oracle is needed to distinguish overlap/model limits from discovery failure.

Dependent nuisance adds **two independent correlated Gaussian groups**, each with as many measurements as the informative feature set, pairwise correlation **0.7**, and coordinate variance matched to the standard shell population. These groups are independent of the signal and its labels. Remaining nuisance coordinates retain the original matched shell marginals. Signal observations and labels remain identical to the corresponding baseline condition. Gaussian distractors have different marginal shapes; matching their variance does not make the marginals identical. This condition challenges the assumption that the signal is the only dependent group; it is not an experiment with several equally valid planted clusterings.

No combined harder conditions or bandwidth, budget, fitness or threshold sweep is included. A shared feature permutation and population transform apply across each population's four observation blocks. Truth and distractor group membership are metadata for diagnostics only, never search inputs.

## Analysis and decision

Report each condition and informative dimension separately. Primary outcomes are exact planted-feature recovery and test ARI, paired between methods on each dataset/search seed. Show both search-seed outcomes within each data seed; do not treat 126 jobs as independent datasets. Also report precision/recall, selected size, validation gain, split flags, discovery timing, optimizer failures and preprocessing/runtime.

The baseline replication tests whether the d4/d5 recovery advantage recurs without losing d2/d3/d8 performance. If both methods reach a ceiling, report no demonstrated recovery advantage on those new samples. Controls and the out-of-scope mean-shift cases remain visible. The stress cases locate the method's limits; they are not a source of settings for retuning this frozen candidate.

For each failure, distinguish: (1) the true feature set was never proposed; (2) it was proposed but rejected by fitness; (3) even the supplied-feature oracle cannot recover the labels; (4) the selected partition works but feature recovery or split acceptance does not. Supply the oracle only after both searches. Report all outcomes, including refused numerical fits and control flags; current flags are not calibrated tests.

After this one batch, make the agreed retain/narrow/pivot decision. Retaining a scoped method leads to an application eligibility check and strong published comparators, not another broad synthetic tuning sweep. This protocol is an internal prospective plan, not an externally registered study.

## Run and recovery

From the repository folder in PowerShell:

```powershell
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_feature_set_replication.py"
```

Allow roughly **1–2 hours**, extrapolating from the preceding 35.64-minute batch and the additional 72-feature computations. This is an estimate, not a measured full-run duration. Results save under `results/research_feature_set_replication/` in a new timestamped directory. The runner prints progress and saves after each completed job.

Inspect the fixed plan with `--list-only`. Resume a stopped run with `--resume PATH_TO_RUN`; completed jobs are copied into a new run after configuration/source checks, and unfinished jobs restart. No scientific overrides are accepted. To audit saved results, use the existing `scripts/analyze_research_radial_search.py` with the completed run directory.

The engineering smoke suite (`--suite smoke`) uses data seed **5903**, search seed **6907**, 120 rows per block and 16 fits per method, with one four-feature case for each condition. It checks execution and auditability only. Its outcomes will not change the full protocol or select a method.

## Engineering verification completed before handoff

The focused checks passed: 47 generator tests, 33 new-runner tests and 114 existing search/pipeline/auditor regression tests (194 total). They cover unchanged baseline generation, stress geometry and nuisance independence, preservation of the scientific computation, paired configurations, source guards, saved results and interruption recovery.

The final smoke run `20261025T235417_772095Z` completed four jobs, eight method runs and 128 candidate fits. The independent saved-state audit passed **5,002 checks with zero errors**. An earlier smoke run is preserved; only receipt wording was corrected afterward so the smoke is explicitly described as four engineering datasets, not the full 63-population replication. No fitness, search or population settings changed. The full replication has not been launched by the assistant.
