# Fresh feature-set replication: findings and scope decision

## Material Passport

- Origin Skill: academic-research-suite, experiment validation
- Origin Date: 2026-10-31
- Version Label: feature_set_replication_assessment_v1
- Verification Status: ANALYZED; secondary provenance review and independent saved-state numerical audit passed; no independent refitting
- Run: `results/research_feature_set_replication/20261027T163415_226880Z`
- Protocol: [frozen replication/stress plan](feature-set-replication-protocol-2026-10-25.md)
- Evidence: [run summary](../../results/research_feature_set_replication/20261027T163415_226880Z/summary.md), [derived comparison and case details](../../results/research_feature_set_replication/20261027T163415_226880Z/comparison.json), [independent audit](../../results/research_feature_set_replication/20261027T163415_226880Z/audit.json)
- Scope: fresh-seed replication of the frozen synthetic method; no real-data or novelty claim

## Decision

**Retain the frozen kernel-guided method and narrow its supported claim.** The improvement replicates for clearly separated radial groups in the tested 24-feature setting, including competing dependent Gaussian nuisance groups. Higher feature counts expose search variability; weaker separation exposes model, acceptance and finite-sample ranking limitations. The planned ablation and replication stages are complete. Proceed to application eligibility, established comparators and interpretable reporting rather than another broad synthetic tuning sweep.

## Completion and primary results

All 126 jobs and 252 method runs completed, totaling 64,512 candidate fits in **60.93 minutes**. No optimizer nonconvergence was recorded. There are **63 distinct data blocks searched twice**, not 126 independent datasets. Conditions intentionally share seeds and, in some cases, signal observations; inference within a condition/dimension still has only three independent data-seed replicates.

The table reports shell cases only; each numerator counts exact planted-feature recovery over data/search seed combinations.

| Condition | Original exact recovery | Kernel exact recovery | Original mean test ARI | Kernel mean test ARI |
|---|---:|---:|---:|---:|
| Baseline, 24 available features | 22/30 | **30/30** | 0.869 | **1.000** |
| Two dependent Gaussian nuisance groups | 8/18 | **18/18** | 0.714 | **1.000** |
| 72 available features | 3/18 | **12/18** | 0.254 | **0.926** |
| Weaker separation and thicker shells | **12/18** | 10/18 | 0.398 | 0.398 |

The baseline improvement is concentrated in the expected difficult dimensions: four-feature exact recovery rises from 1/6 to 6/6, and five-feature recovery from 3/6 to 6/6. Both methods recover all two-, three- and eight-feature baseline cases. Kernel recovery succeeds under both search seeds on all 15 baseline datasets and all nine dependent-nuisance datasets. The dependent-nuisance result challenges the prior favorable assumption that the informative group is the only dependent group, but covers only the specified Gaussian distractors.

## Higher feature count: good partitions do not guarantee reliable explanations

At 72 features, kernel exact recovery is 3/6 for four informative features, 5/6 for five, and 4/6 for eight. All six kernel misses omit the true set from evaluated candidates. The separately fitted true-set model has test ARI 1.0 and a search-score advantage of 0.347–0.591 over each selected set. Candidate discovery remains the demonstrated obstacle in this condition.

The selected sets are often close: three add one nuisance feature, two omit one informative feature, and one replaces an informative feature. Their individual test ARIs range from 0.475 to 0.967. Therefore the overall mean ARI of 0.926 must not be presented as equally reliable feature identification.

Only **3/9 datasets** recover the true set under both search seeds, although every dataset recovers it under at least one. This is descriptive evidence of search-seed sensitivity. The retrospective either-seed count is not a new ensemble result or a matched-budget improvement. We have not changed the 256-fit budget or selection procedure after seeing these outcomes.

## Weak separation: several distinct obstacles

Four-feature recovery is 6/6 for both methods; five-feature recovery is 6/6 for the original and 4/6 for the kernel method; eight-feature recovery is 0/6 for both. Even when given the exact features, the current fitted model obtains test ARI only **0.503–0.716**, mean **0.612**. This is a current-model diagnostic, not a theoretical limit on recoverability by other methods.

Every weak-separation true-set model has one fitted spatial mode. All selected and true-set models fail the existing split-acceptance check. Thus these results do not establish a clearly supported density-valley split even where a two-component assignment partially matches the simulated labels. The scripts still record predictions; an unflagged split is not an implemented abstention interface or a calibrated statistical decision.

One population, weak separation with eight informative features and data seed 5119, exposes a ranking issue in addition to a proposal miss. The true-set model has test ARI 0.645, while selected feature sets have ARI 0.028 (original) or 0.038 (kernel). Yet their search gains exceed the true-set model's by 0.0127 and 0.0055 respectively. This repeats under both search seeds, representing one population rather than four independent counterexamples. Simply adding the true set to those candidate lists would not make it win under the recorded fitness.

The ordering reverses on validation and test: the true-set model scores better there. Sampling noise and adaptive search may contribute, so this does not prove that the population-level predictive objective inherently prefers the wrong features. It does show that the earlier observation that every missed true set had a better score no longer holds universally. We should neither call every remaining problem search-only nor redesign all fitness components from this one weak case.

## Controls and verification

All 18 distinct control datasets, each searched twice per method, remain unflagged on validation and test: 0/36 searched control jobs for each method. These observations do not calibrate a false-split error rate. Mean-shift cases retain near-zero ARI and remain outside the successful radial model scope.

Secondary provenance review found no discrepancies: all planned jobs match the fixed protocol; all nine source snapshots and the four frozen scientific hashes agree; the experiment adapter retains the permitted AST equivalence; full-run seeds do not overlap development or smoke seeds. All 63 repeated-search pairs have byte-identical saved data. In all nine dependent-nuisance/baseline dataset pairs, signal columns, labels and non-distractor columns are exactly preserved across the four splits.

The independent numerical audit passed **1,811,652 checks with zero errors** across all 126 jobs, 252 method runs and 64,512 candidate fits. Saved-state auditing checks numerical consistency, native assignment rules, scores, selection, budgets, local moves and provenance. It does not refit candidates, reconstruct all random exploration choices or establish cluster validity.

## Next stage, without expanding the synthetic tuning cycle

Preserve `kernel_best` as the frozen candidate, including its current failures. The defensible working target is **automatic discovery of modest original-feature sets supporting explicit radial cluster rules when sufficiently separated radial structure is present**, with visible evidence about feature stability and split support. We cannot claim general nonconvex clustering, dependable recovery at arbitrary dimension, biological meaning or novelty from these results.

The next deliverables are an application eligibility/comparator plan and an interpretable result report. Define an application using measurement meaning and a plausible radial hypothesis before inspecting final benchmark scores. Compare with appropriate published methods under matched evaluation, with feature verification, prediction quality, explanation cost and stability reported separately. Each result report should expose the selected features, explicit assignment rule, shape diagnostic, held-out evidence and unsupported-split status; a high ARI alone cannot verify the claimed explanation.

If no defensible application fits the model family, that is a reason to change the model family explicitly rather than select favorable datasets after seeing their outcomes. Do not launch another broad synthetic budget, kernel or fitness sweep as the automatic next step.

## Interpretation checks: 11/11 reviewed

1. Simpson's paradox: condition- and dimension-specific results accompany aggregates, including the weak-separation regression.
2. Ecological fallacy: no synthetic feature recovery is treated as scientific feature meaning.
3. Berkson selection: all declared cases and failures remain visible; application selection must be prospectively justified.
4. Collider bias: no causal adjustment or hierarchical conditioning is claimed.
5. Base rates: designed control counts do not estimate application prevalence or calibrated false-split risk.
6. Regression to the mean: the method was frozen before these new seeds; no post-result retuning is included.
7. Survivorship: all 126 jobs completed, with no recorded nonconvergence or omitted condition.
8. Look-elsewhere effect: candidate evaluations and audit checks are not independent replication units; no p-values are inferred from them.
9. Forking paths: post hoc diagnostics are identified; either-seed success is not a new ensemble evaluation.
10. Causality: matched computational comparisons establish scoped behavior, not causal relevance of measurements.
11. Reverse causality: feature dependence implies no direction of scientific causation.
