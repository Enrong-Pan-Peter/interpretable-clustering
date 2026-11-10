# October radial work, frozen replication, and the November pivot

This chapter summarizes completed work and proposed directions separately. Detailed mathematics, protocols, audits and saved arrays are preserved in the repository snapshot. No experiment was rerun during packaging.

## October 4–14: make interpretability a testable requirement

The proposal and laboratory reviews distinguished five outputs: useful original measurements, an assignment rule, a shape assumption/display, evidence that fewer measurements suffice, and a reason to split or stop. Legacy tree code existed, but the newer research methods were binary root experiments rather than a validated complete hierarchy. An interface was a planned deliverable, not an implemented or scientifically validated system.

The lab suggested offline candidate discovery, browsing alternatives, and replacing branches. Two/three features were preferred for plots; the researcher explicitly allowed larger feature sets with explicit rules. The proposal's broad claim that no existing method could discover a readable unlabeled hierarchy was withdrawn. Comparing direct interpretable clustering, clustering followed by explanation, supervised gate transfer, and feature selection followed by clustering requires keeping their information inputs separate.

The October 14 novelty challenge identified close work on alternative feature sets, Cluster-Explorer, polyhedral explanations, TreeFARMS, x-PACS, Anchors, Learn then Test, multi-polytope clustering and inference for cluster labels. The trait-first plan therefore proposed one node, a declared model family, and independently checked assignment/feature evidence before building an entire interactive tree. These plans did not prove novelty.

Evidence: `docs/research/proposal-evolution-review-2026-10-04.md`, `interpretability-roadmap-2026-10-04.md`, `lab-meeting-design-review-2026-10-06.md`, `lab-meeting-benchmark-plan-2026-10-07.md`, `novelty-challenge-2026-10-14.md`, `trait-first-method-review-2026-10-14.md`, `trait-first-research-plan-2026-10-14.md`.

## The implemented radial model and fitness

`atomic_research/radial_panels.py` fits one- and two-band spatial densities on a chosen original-feature set. Fit-only centers/scales are saved. A shared component width yields an exact native rule:

`sum over selected j of ((x_j - center_j) / scale_j)^2 > threshold`.

This is the actual assignment, not a surrogate for an unrelated graph classifier. The spatial density includes dimension-dependent normalization and must be distinguished from the distribution of the radius itself: a radius histogram peak need not imply multiple spatial modes.

Comparing log likelihoods in different dimensions naively is invalid. The code uses one fixed joint Gaussian background, with the appropriate covariance marginal for each candidate. The full-space candidate is conceptually

`q_S(x_S) * q_0(x) / q_0,S(x_S)`.

Relative to the common background, the score reduces to a held-out mean of `log q_S(x_S) - log q_0,S(x_S)`. This permits a common observation-space comparison. It does not make positive gain equivalent to meaningful clusters; a non-Gaussian single population can improve the density fit.

The provisional flag separately checks positive gain over the background, positive two-band-versus-one-band gain, two spatial modes with an adequate valley, and sufficient assignment mass in both groups. These are heuristic conditions, not calibrated statistical error control. Predictions are still recorded for unflagged cases.

## Supplied-feature diagnostic, October 15–20

Protocol: 36 jobs, 24 available features, 600 rows each for fit/validation/test, three seeds, up to ten specified candidate sets. Candidates deliberately include the true support, partial sets, supersets and nuisance/random alternatives. This isolates representation and ranking; it is not autonomous discovery.

Population families include lognormal-thickness shells, an approximate quartic-family check, single shells, independent/correlated Gaussians, Student-t, shared-center scale mixtures, and mean-shift mixtures. Signal and nuisance coordinates have matched one-dimensional marginals. The shell feature map and population transform are shared across independent splits.

In the completed diagnostic, shell candidates were selected with test radial ARI 1.0 in the displayed dimensions 2, 3, 5 and 8; the quartic check also worked. Centroid rules failed on these concentric structures, illustrating why the native rule matters. The single-population/control candidates were unflagged. Mean-shift cases demonstrated the radial family's limitation. These are scoped mechanism results.

Run: `results/research_radial_diagnostic/20261020T021208_103657Z`. All 36 jobs and 360 candidates completed. The saved-state audit reports 18,031 checks with zero errors.

### Numerical interruption and repair

Original failed run: `results/research_radial_diagnostic/20261016T150124_340504Z`. During the single-shell five-dimensional job, L-BFGS-B proposed a location of `-6.938893903907228e-18` despite a zero bound. The strict normalizer correctly rejected it.

The adapter now projects only bound excursions within 64 machine epsilons times the bound scale; it still rejects material violations and nonfinite values. The public normalizer stays strict. The failed candidate replay used three tiny corrections. This did not change the data, scientific model, objective or candidate list.

Recovery copied 17 completed jobs unchanged and completed the other 19, restarting the incomplete job. Both predecessor and recovery provenance are retained. The associated 78 software tests and recovery audit passed as documented in `docs/research/radial-boundary-fix-2026-10-19.md`. This repair is completed; do not rerun recovery as an outstanding task.

## Autonomous hidden-feature search, October 20

The next experiment removes the true support from search proposals. Four methods share a 256-distinct-fit budget: random; random starts plus local search; squared-dependence starts plus local search; and shuffled-dependence starts plus local search. Sets up to size ten are allowed. Add/drop/swap refinement and a fit cache avoid exhaustive enumeration. Fit/search/validation/test blocks each contain 600 rows.

Fitness for search is held-out search-block predictive gain. The true set is fitted separately afterward as a diagnostic; it does not guide proposals. The run completed 36 cases, 144 method runs and 36,864 fits in 36.12 minutes. A saved-state audit passed 793,616 checks.

| Method | Exact recovery across 15 shell cases | Mean test ARI |
|---|---:|---:|
| Random | 0/15 | .198 |
| Random starts + local search | 2/15 | .460 |
| Squared-dependence + local search | 10/15 | .765 |
| Shuffled-dependence + local search | 2/15 | .444 |

The supplied true set achieved ARI 1.0 in every shell case. Every searched visit to that set selected it; failures omitted it. The difficult dimensions were four and five: squared dependence could cancel or weaken, and complete-neighborhood refinement could spend its remaining budget before exploiting a promising near-correct set. This supported a specific search intervention, not another wholesale fitness rewrite.

Run: `results/research_radial_search/20261020T174212_534139Z`. Plan/assessment: `docs/research/hidden-panel-search-2026-10-20.md` and `radial-search-pilot-assessment-2026-10-20.md`.

The researcher asked when design would start. The explicit agreement was one targeted development ablation, then one frozen replication/stress batch. Both are now complete.

## Search v2 and the 2 by 2 ablation, October 23–25

Two changes were separated:

- Proposal similarity: absolute correlation between squared standardized features versus normalized centered Gaussian-kernel similarity on those squared values. The latter is an HSIC-related statistic, not an independence-test p-value.
- Refinement: finish a neighborhood and follow its best improvement versus move immediately after the first improvement.

All four variants use the same radial model, fitness, set-size cap and unique-fit budget. The kernel changes proposals only. It does not replace the final rule with a latent embedding or change the clustering fitness.

Run: `results/research_feature_set_ablation/20261025T184818_942365Z`. The original development populations were intentionally reused, so this is not fresh replication.

| Variant | Exact shell recovery | Mean test ARI |
|---|---:|---:|
| moment_best | 10/15 | .765 |
| moment_first | 13/15 | .867 |
| kernel_best | 15/15 | 1.000 |
| kernel_first | 15/15 | 1.000 |

Both kernel variants found every true set during their identical exploration phase, at evaluations 9–103 (median 31). The ablation therefore showed no extra recovery benefit from first-improvement after kernel proposals. The old moment/best arm reproduced its historical choices across all 36 cases. All 18 control cases per method were unflagged, while mean-shift cases still failed.

All 144 method runs and 36,864 fits completed in 35.64 minutes; the audit passed 1,039,614 checks. Successful eight-feature recovery among 24 available features used 256 fits rather than enumerating 4,540,385 allowed sets of sizes one through ten. This is evidence beyond triples in a restricted setting, not a claim of scalable general feature discovery.

`kernel_best` was frozen as the candidate, with `moment_best` as comparator. Evidence: `docs/research/feature-set-search-v2-2026-10-23.md`, `feature-set-ablation-assessment-2026-10-25.md`, and the run's frozen candidate record.

## Fresh replication and stress conditions, October 27–31

Run: `results/research_feature_set_replication/20261027T163415_226880Z`. Protocol: `docs/research/feature-set-replication-protocol-2026-10-25.md`. Assessment: `docs/research/feature-set-replication-assessment-2026-10-31.md`.

There are 126 jobs, 252 method runs, 64,512 fits and 60.93 minutes of recorded execution. No optimizer nonconvergence was recorded. There are 63 data blocks searched twice; conditions intentionally share some signal observations/seeds, and each condition/dimension has only three data-seed replicates.

| Shell condition | moment_best exact | kernel_best exact | moment_best mean test ARI | kernel_best mean test ARI |
|---|---:|---:|---:|---:|
| Baseline, 24 features | 22/30 | 30/30 | .869 | 1.000 |
| Dependent Gaussian nuisance groups | 8/18 | 18/18 | .714 | 1.000 |
| 72 available features | 3/18 | 12/18 | .254 | .926 |
| Weaker separation/thicker shells | 12/18 | 10/18 | .398 | .398 |

At 72 features, all six kernel misses failed to visit the true set; its separate fit scored better and had ARI 1. Only 3/9 datasets recovered it under both search seeds. Every dataset succeeding under at least one seed is a retrospective observation, not a validated ensemble method. The high average ARI masks imperfect feature identification.

For weak separation, even true-set fits achieve only .503–.716 ARI, mean .612. This is a limitation of the fitted model in those cases, not a theoretical ceiling. All true-set fits have one spatial mode and fail the provisional split flag. One eight-feature population has selected sets with higher search gain despite much worse ARI; ordering reverses on validation/test. This introduces finite-sample/adaptive ranking as an issue alongside search. It is one population observed through multiple searches, not four independent counterexamples.

Controls remained unflagged; this does not calibrate a false-split probability. The saved-state audit reports 1,811,652 checks with zero errors. It checks numerical consistency, rules, selection, budgets and provenance; it does not refit every model or establish scientific meaning.

## November 5: larger pivot is allowed

The latest user explicitly allowed a change of clustering family, data domain and proposal. The preferred assistant recommendation is now a limited real-data comparison of existing methods, concentrating on compact original-feature prediction across independent subjects. IDC, DUFS/GroupFS, sparse clustering and simple cluster-label distillation are starting points, not claimed new components. Weak supervision is a fallback if it supplies missing meaning.

A candidate question is whether a small feature set can support executable new-point assignments and preserve reproducible distinctions across subjects, with visible evidence when the budget is insufficient. This is not a verified novelty claim. Existing work already covers deep gates, sparse clustering, cluster explanations, manifold-preserving selection, consensus selection, transfer and honest sequential acquisition.

The activity archive contains 21 official training subjects and 9 disjoint test subjects. It is useful for a first subject-aware pilot, but it has been used historically in the project, so it is not untouched confirmation. Its 561 variables are engineered sensor features; fewer such variables do not automatically mean fewer physical sensors.

The seven-day plan was to establish a small comparator set, test restricted-input sufficiency at budgets 3/5/10/20/all, then implement one targeted change or use declared limited supervision. No new comparison runner or neural method was implemented during the reassessment. The new agent should decide whether this remains the best use of the remaining proposal time, without repeating the completed radial batches by default.
