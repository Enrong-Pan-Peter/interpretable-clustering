# Finding the remaining obstacles

## Material Passport

- Origin Skill: academic-research-suite / experiment planning and execution
- Origin Mode: diagnosis of saved results and prospective development experiments
- Origin Date: 2026-09-16
- Verification Status: ranking followup verified; new suite unit/integration tested and smoke tested; full 33-case suite not run by the assistant
- Version Label: obstacle_checks_v1
- Inputs: completed pilot and `results/research_ranking_followup/20260916T025613_491524Z`
- Entrypoint: `scripts/run_research_obstacle_suite.py`

## What the completed ranking run tells us

The fitness function remains a concern, but rescaling it is not a sufficient repair. All six cases completed; source hashes match; all 30 baseline replays and 120 ranking-policy winners were checked against the saved records. These are descriptive results on development data, not a statistical superiority test.

| Mean development-test ARI, averaging the five methods and three seeds | Original | Size-centered | Size-standardized |
|---|---:|---:|---:|
| Mean shift | 0.392 | 0.440 | 0.406 |
| METABRIC | 0.127 | 0.093 | 0.106 |

Sparse k-means remains the strongest existing METABRIC comparator in this pilot: original ranking averages 0.356, centering 0.290, size standardization 0.324. The larger global reference bank does not rescue it or the other methods. This does not prove all objective functions fail; it argues against spending the next round on scalar normalization alone.

The centered policy uses size-specific means **and common within-size residual scales**. Its comparison with the new global policy changes both centering and component weights; it is not a pure means-only intervention. See `ranking-assessment-2026-09-16.md` for all methods, paired gains and losses, and limitations.

## The four checks

### 1. Is useful structure discarded after feature proposal?

The earlier learned proposers supplied feature masks to another clustering procedure. A useful learned partition need not survive replacing its metric and splitting it again.

We now retain each sparse-k-means model, including its fitted transforms, weights, centroids and assignment rule. For each of three prescribed L1 bounds, select the restart with the largest native objective using discovery data only. Report all bounds; do not choose among them using annotations. The bounds are 1.25, square root of the prefix cap, and square root of the feature count, clipped/deduplicated by the fitter. Full native support can exceed the prefix cap.

For raw and centered-squared coordinates, report the full weighted model and every prefix of one through eight original features. The paired sequence compares:

1. Full weighted centroids, with both native nearest-centroid and kNN assignment.
2. The same stored centroids truncated to a feature prefix, retaining its weights.
3. Centroids refitted on that prefix with weights retained.
4. Centroids refitted with weights removed, with both nearest-centroid and kNN assignment.
5. Spectral clustering plus kNN in the same unweighted representation.
6. Spectral clustering plus kNN on the original raw standardized features.

Each step reports external ARI separately from fidelity to the full native rule. Discovery geometry is recorded in the original coordinates, the unweighted transformed coordinates, and the native weighted metric where applicable. Labels are used only for reporting, never native fitting, restart choice, or feature ranking.

Interpretation: a loss at truncation implicates support/weights; a loss when weights are removed implicates the metric; a loss when clustering changes implicates the partition model; a loss between centroid and kNN readouts implicates assignment. These are controlled comparisons conditional on fitted models, not a proof of one cause in every dataset. Some full models may also be poor or use too many features to be useful.

Default cases: mean shift, METABRIC, shells; seeds 3, 4, 5; 480 rows; 50 synthetic features; five planted features; eight-feature prefixes; 40 alternating iterations and three restarts per bound. METABRIC uses the existing 250-gene cached universe. Squaring follows discovery-fitted centering/scaling, then a second discovery-fitted scaling of the squared channels. A squared channel still counts as one original feature.

### 2. Does reduction preserve the right thing, and does that preservation transfer?

Replay the pilot's selected smooth-graph and sparse-k-means panels on mean shift, METABRIC and Levine, seeds 0, 1, 2. Verify source hashes, original feature data, preprocessing, row splits, teacher partition and full-panel test ARI before analyzing any deletions.

Compare four greedy deletion rules against the same frozen full-panel teacher:

- kNN assignment with validation ARI at least 0.95.
- kNN assignment with at most 5% changed validation assignments.
- kNN assignment with at most 5% changed assignments **in every one of three fixed validation folds**.
- Refit two-means with at most 5% changed validation assignments, with label orientation determined on discovery rows only.

All one-feature deletions of the original panel are recorded, even when reduction stops immediately. The folds are a sensitivity check, not a confidence interval or independent nested validation. Validation rows remain reused across greedy decisions. Test rows only assess outcomes.

ARI 0.95 does not mean 95% of points keep their assignments. The refit policy changes the model family even before deleting a feature, so reports explicitly distinguish the original teacher, the full-panel refitted model, and the reduced model. A faithful rule can preserve a scientifically wrong partition; external agreement is reported separately. No policy is declared best by inspecting this reused test split.

Interpretation: if simpler disagreement limits remove nuisance variables with acceptable test fidelity, the old reduction criterion was obstructing compactness. If validation fidelity fails on test, adaptive reuse/sample uncertainty is an obstacle. If every deletion changes predictions but external ARI barely changes, the teacher may depend on details irrelevant to the annotation target. Known planted support is not automatically the unique smallest useful panel.

### 3. Can the clustering model recover a shape when feature search is removed?

Supply the known shell features and compare raw spectral clustering, squared-coordinate spectral clustering, raw/squared two-means, and a squared-radius rule. Sweep sample sizes 480, 960, 1920 and graph neighborhoods 5, 10, 20, using seeds 3, 4, 5. All configurations are reported. Save how often a raw-space neighbor crosses shells.

This is an **oracle ability check**, not discovery. The radius rule receives a radial inductive bias. Compare it with autonomous squared-coordinate feature learning in check 1. If the oracle succeeds while autonomous discovery fails, the representation can express the answer but feature search or its native objective cannot locate it. If raw geometry improves only with more observations, graph construction/sample density is part of the obstacle. Success here would not establish arbitrary-shape clustering.

### 4. Can the same method produce convincing partitions when no groups were generated?

Run the complete retained sparse-model procedure, including native restart selection, on independent and correlated single-Gaussian populations at seeds 3, 4, 5. Report the same prefixes, assignments and geometry diagnostics. This covers that retained-model procedure, not every legacy EA/search implementation.

Test-only centroid refits on fixed panels assess partition replication; they do **not** independently rediscover the features. A stable split of a single population is possible. There is currently no cluster-acceptance rule, so these outputs are not false-positive or false-split rates. Negative controls expose misleading evidence and help design a later acceptance test.

## Run locally

From PowerShell, these commands use the research environment explicitly, regardless of which environment is activated:

```powershell
Set-Location 'C:\Users\Peter\Desktop\Github\ATOMIC_Clustering'
.\.venv-research\Scripts\python.exe -u .\scripts\run_research_obstacle_suite.py --stage all
```

There are **33 cases**: nine model-retention, nine compression (two methods per case), nine geometry, and six controls. The full run may take minutes; precise time depends on the computer. Completed case files and a growing summary survive interruption. A new invocation creates a new timestamped directory; automatic resume is not implemented.

To run one stage, replace `all` with `retention`, `compression`, `geometry`, or `controls`. To inspect the planned cases without fitting, add `--list-only`. Avoid repeatedly rerunning the complete suite while tuning against its displayed test labels.

Outputs are under `results/research_obstacle_checks/<timestamp>/`:

- `manifest.json`: prescribed jobs, completion/failure, configuration, runtime versions and research/legacy source hashes.
- `summary.md` and `summary.json`: growing cross-case report; the compact model table shows the full model and largest prescribed prefix, without selecting it as best.
- Per-case `summary.json`, discovery/validation/test row protocol, and feature/preprocessing metadata.
- Model cases: every prefix/readout in `comparisons.jsonl`, fitted models and readout assignments in NPZ files.
- Compression cases: every original one-feature deletion, all subsequent validation trials, predictions and fit accounting.

## What follows the results

The immediate decision is which object to optimize and preserve: a feature mask alone, or a feature panel together with its metric, partition and assignment rule. We should choose that based on where the ablations lose agreement and reliability. We can then test a small number of targeted methods instead of adding an EA or neural network before establishing what its objective should reward.

Independent feature rediscovery on disjoint or grouped samples, more negative controls, external-cohort verification, a cluster-acceptance rule, and comparisons against stronger published baselines remain future checks. Same-cohort resampling is not biological replication; the METABRIC feature universe was constructed using all-patient variance information; Levine cell holdouts are not donor holdouts. These limitations are also retained in dataset metadata.

The proposed novelty remains unestablished. These diagnostics are intended to make the next method defensible: compact original-feature explanations, explicit geometry and a reproducible assignment rule, with separate evidence for utility, fidelity, replication and cluster existence.
