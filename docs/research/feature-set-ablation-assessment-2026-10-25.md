# Feature-set search ablation: results and decision

## Material Passport

- Origin Skill: academic-research-suite, experiment validation
- Origin Date: 2026-10-25
- Version Label: feature_set_ablation_assessment_v1
- Verification Status: ANALYZED; independent saved-state audit passed, no independent refitting or fresh-data replication
- Run: `results/research_feature_set_ablation/20261025T184818_942365Z`
- Protocol: [feature-set search v2](feature-set-search-v2-2026-10-23.md)
- Evidence: [full run summary](../../results/research_feature_set_ablation/20261025T184818_942365Z/summary.md), [audit](../../results/research_feature_set_ablation/20261025T184818_942365Z/audit.json), [derived comparison](../../results/research_feature_set_ablation/20261025T184818_942365Z/comparison.json)
- Scope: descriptive development evidence for a restricted radial clustering model; previously inspected observations reused

## Main finding

Kernel-guided proposals resolved all five shell feature-set recovery failures of the original search in this batch, while retaining the same fitted model, fitness, assignment rule and 256-fit budget. First-improvement refinement alone resolved three of the five failures. Both kernel variants recovered every planted feature set and achieved test ARI 1.0 in all 15 shell cases.

| Variant | Exact feature-set recovery | Mean test ARI | Validation flags on controls |
|---|---:|---:|---:|
| Squared correlation + best improvement (`moment_best`) | 10/15 | 0.765 | 0/18 |
| Squared correlation + first improvement (`moment_first`) | 13/15 | 0.867 | 0/18 |
| Kernel + best improvement (`kernel_best`) | 15/15 | 1.000 | 0/18 |
| Kernel + first improvement (`kernel_first`) | 15/15 | 1.000 | 0/18 |

These averages describe five geometries with three data/search seed pairs each. They are not 15 identically distributed independent replications or estimates of universal success.

| Planted feature count | moment_best | moment_first | kernel_best | kernel_first |
|---|---:|---:|---:|---:|
| 2 | 3/3 | 3/3 | 3/3 | 3/3 |
| 3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 4 | 1/3 | 2/3 | 3/3 | 3/3 |
| 5 | 0/3 | 2/3 | 3/3 | 3/3 |
| 8 | 3/3 | 3/3 | 3/3 | 3/3 |

The earlier small-budget eight-feature regression did not persist at the planned 256-fit budget. These results are specific to that budget; the search schedule changes with the total budget, so a shorter run is not necessarily a prefix of a longer run.

## What the search records establish

Both kernel variants found every correct shell feature set in their identical exploration stage, through kernel-dependence-chain proposals, before local refinement. First discovery occurred at evaluations **9–103**, with median **31**. Thus this experiment provides no added shell recovery benefit for first-improvement once kernel proposals are used. It does not establish that refinement is unnecessary on other populations.

Across all four variants, the true feature set was visited in 53 of 60 shell method runs and selected in all 53. Every remaining failure omitted it from the candidates. In those seven failures its separately fitted diagnostic score exceeded the selected score by at least 0.517. This supports candidate discovery as the demonstrated obstacle in these cases. It does not establish a globally correct fitness landscape or alignment with scientific meaning on real data.

The kernel changes candidate proposals only. It is not a kernel clustering fitness or a latent representation in the final explanation. Assignment still uses an explicit threshold on the sum of squared standardized original measurements. Successful eight-feature recovery from 24 available measurements demonstrates search beyond three-feature sets here, using 256 distinct fitted candidates rather than enumerating the 4,540,385 allowed subsets of sizes one through ten. It does not demonstrate scalability to thousands of features.

The new `moment_best` arm selected the same feature sets as the historical dependence-guided baseline in all 36 cases. Search scores differed by at most 1.35e-15, consistent with floating reduction order after loading the saved arrays. This supports a controlled comparison with the prior implementation.

## Controls, limitations and verification

All 36 cases and 144 method runs completed, totaling 36,864 search fits in **35.64 minutes**. There were no recorded optimizer nonconvergences. The independent auditor passed **1,039,614 checks with zero errors**. It replays saved numerical state, kernel statistics, local moves, budgets, selection, rules, metrics and provenance; it does not refit every candidate or independently reconstruct every random proposal.

All 18 control cases per method remained unflagged on both validation and test observations. These include single shells, independent/correlated Gaussians, Student-t and common-center scale mixtures. The flags remain provisional; zero observed flags is not a calibrated false-split guarantee. The three mean-shift cases remain failures with near-zero test ARI, including when the correct feature set is supplied. This is a limitation of the radial model family, not a problem that better feature-set proposals alone can fix.

The signal generator contains one dependent informative block amid independently sampled nuisance measurements with matched marginals. This is favorable to dependence-guided discovery. Stronger nuisance dependence, competing structured blocks, weaker separation and higher nuisance counts remain untested here. No real-data utility, domain meaning, advantage over published methods or methodological novelty has been established.

## Decision and bounded next step

**Freeze `kernel_best` as the candidate for the previously agreed fresh-seed replication/stress batch, with `moment_best` as comparator.** It ties the other kernel variant on shell recovery while changing only the proposal mechanism from the original baseline. Keep fitness, 256-fit budget, size cap, assignment rule and provisional acceptance logic fixed. No additional prerequisite fitness redesign or broad parameter sweep is justified by these results.

The [frozen candidate record](../../results/research_feature_set_ablation/20261025T184818_942365Z/frozen_candidate.json) captures the algorithm choice and source hashes. The next batch's data design must be specified before execution: unseen data seeds, multiple search seeds per population, higher nuisance count and weaker separation as already planned. Add a predeclared competing dependent-nuisance-block condition within that same bounded batch to test the favorable dependence assumption. Its exact generator and settings remain to be specified; no such stress outcomes have been examined.

After this single replication/stress batch, make the agreed retain/narrow/pivot decision. Success would justify moving to an eligible application and strong established comparators. The potential thesis contribution remains an interpretable discovery-and-validation method for a declared geometry class; combining standard kernel dependence and local search is not itself established novelty.

## Interpretation checks: 11/11 reviewed

1. Simpson's paradox: report each signal dimension as well as the aggregate; kernel recovery does not regress in any tested dimension.
2. Ecological fallacy: no inference from synthetic recovery to biological feature meaning.
3. Berkson selection: all planned cases retained; the favorable generator structure is explicit.
4. Collider bias: no causal adjustment claim; no hierarchical conditioning tested.
5. Base rates: the designed mix of shells and controls is not an application prevalence estimate.
6. Regression to the mean: the design targeted known development failures; fresh replication remains necessary.
7. Survivorship: all 36 jobs and four variants completed; no failed cases excluded.
8. Look-elsewhere effect: candidate fits and audit checks are not independent scientific replications; no inferential p-values claimed.
9. Forking paths: the four-way comparison was written before execution; choosing the candidate now is development, not confirmation.
10. Causality: matched computational changes support scoped mechanism attribution, not causal claims about measured features.
11. Reverse causality: dependence proposals establish no direction of scientific causation.
