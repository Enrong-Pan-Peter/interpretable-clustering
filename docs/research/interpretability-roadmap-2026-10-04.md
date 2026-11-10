# From promising feature panels to interpretable clustering

**Update, 2026-10-14:** The [trait-first research plan](trait-first-research-plan-2026-10-14.md) now sets the sequence: one working node, a specific novelty test, application preflight, then full benchmarking. Cytometry is optional; the preference for small original-feature panels with explicit larger-panel rules is retained.

**Update, 2026-10-07:** The [lab-meeting benchmark plan](lab-meeting-benchmark-plan-2026-10-07.md) updates the immediate priorities and comparators. The user prefers two or three features per split while allowing larger explicit rules. This October 4 document remains the record of the earlier design; the cytometry extension needs per-population recovery checks in addition to global fidelity.

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-10-04
- Verification Status: UNVERIFIED proposed design; existing findings are identified separately
- Version Label: interpretability_roadmap_v1
- Source proposal: `C:/Users/Peter/Downloads/Enrong_CISC500_Proposal.pdf`, complete one-page text and rendered page inspected; original preserved
- Proposal SHA256: `39ee32cb9c3eac3fce76ddff3580b7840c2c652600d9e12a86e3c3a15862ad1f`
- Evidence: [verified development assessment](rank-preservation-assessment-2026-09-30.md), [proposal comparison](proposal-evolution-review-2026-10-04.md), and [new experiment specification](interpretability-protocol-review-2026-10-04.md)
- Scope: design and proposal comparison; no new clustering experiment or completed-method claim

## 1. The proposal's aim remains the right one

The original proposal already made interpretability central: discover small sets of biomedical measurements without using expert labels, form a readable hierarchy, choose panel size, refuse unsupported splits, and show alternatives to a domain expert. It also explicitly acknowledged conflict between separation and small panels. We should preserve those commitments.

What changes is the proposed mechanism and the order of work. The experiments show that optimizing separation, finding relevant measurements, assigning observations, explaining assignments, and establishing evidence for a split are different tasks. One score did not reliably align them. A better proposal makes those tasks explicit and tests their connections.

Neither an evolutionary optimizer nor a particular topological score is a requirement of the original one-page proposal. They can remain candidate mechanisms. The work should be judged by its interpretable output and the evidence for it.

| Original element | Recommended revision | Current status |
|---|---|---|
| An objective combining quality, small panels and stability | Candidate discovery followed by explicit assignment, constrained simplification and independent checks | Component evidence exists; combined method proposed |
| Small panels a person can plot | Named measurements plus an exact rule; direct marker plots where applicable, transparent summaries for larger panels | Exact centroid rules exist, but still use 16 features |
| Panel size chosen by the method | Smallest panel meeting stated requirements among a frozen candidate set | Fidelity machinery exists; integration with the promising proposer remains |
| Recursive binary tree | Validate a useful node, then integrate a shallow hierarchy and its stopping rule | Legacy tree code exists; the new branch is not validated as a hierarchy |
| Refuse an unconvincing split | Distinguish insufficient data, inadequate explanation and lack of evidence under a stated population model | Current promising branch still forces two groups |
| Agreement with expert populations and markers | Preserve these tests; add donor-level transfer where possible, alternative valid marker groups and direct usability checks | Latest positive result is synthetic, not biological validation |
| Interactive candidate comparison | Show a small verified shortlist and the consequences of choosing each panel | Evidence reports exist; integrated interface remains a deliverable |

Moving from two-marker plots to panels larger than three is a meaningful extension of the original explanation format. A two-dimensional embedding that depends on many measurements is not a two-marker gate. The interface must show that dependency honestly.

## 2. Updated research question and potential contribution

**Research question:** Can a method discover compact panels of original measurements and explicit assignment rules that produce useful, reproducible groupings, while exposing the limits of their explanations and declining splits unsupported by its stated assumptions?

The hierarchical version asks whether different nodes can use different panels without accumulating arbitrary splits or an unreadable decision path.

A potential contribution is a method that makes interpretability an admission requirement for candidate partitions: a candidate must supply an executable rule, pass a declared simplification check, and expose its evidence for splitting. It can then present the surviving size/utility tradeoffs to an expert. This is a hypothesis about a useful method, not an established novelty claim.

The first centroid experiment alone is insufficient to demonstrate this contribution. It tests whether a promising panel generator can support that design. Later comparisons must show what is gained over both direct interpretable clustering and clustering followed by gate reconstruction. Merely assembling a kernel, feature selection and a report would not establish novelty.

The literature-gap paragraph needs revision. In particular, [ConvexGating](https://www.nature.com/articles/s41467-026-77360-z), published 18 September 2026, learns marker-pair gating hierarchies from supplied cluster assignments. It is a close comparator. Distinguish discovering a partition from reconstructing gates for one; neither distinction alone proves novelty. The companion [proposal comparison](proposal-evolution-review-2026-10-04.md) also corrects the treatment of CCAST and covers spectral projection pursuit.

## 3. Define the output before adding more fitness terms

Every proposed node should produce the following inspectable record. These are separate columns, not ingredients silently collapsed into one score.

| Requirement | Evidence the node should provide | What it does not establish |
|---|---|---|
| Measurable panel | Original feature names, units, preprocessing and measurement count | That these are causal or uniquely correct markers |
| Executable explanation | Exact assignment rule, parameters, missing-value policy and numerical replay | That a long equation is easy for a human to use |
| Shape description | Declared rule family and faithful boundary/score display | That a convenient projection preserves every cluster shape |
| Justified compactness | Size versus disagreement curve; smallest tested panel passing the fixed requirement | Global minimality over all feature subsets |
| Rediscovery | Independently fitted panels and assignments; separate exact-feature and substitute-group agreement | Transfer to new donors if only cells were resampled |
| Useful grouping | Reference-population agreement and prespecified domain facts on evaluation data | Universal correctness of annotation labels |
| Split or stop | Stated reference model, evidence status and reason to retain a leaf | A distribution-free proof that biological clusters exist |

For the current centroid family, the executable rule is a weighted sum of measured values compared with a threshold. It describes that centroid model exactly. It must not be advertised as a faithful explanation of the different kernel classifier. For transformed cytometry values, name the transformation in the rule; a linear formula after an arcsinh transform is not linear in raw instrument intensity.

The first report should show marker names and coefficient directions, full versus reduced rule predictions, the entire size curve, independent-sample agreement, and the split-evidence status. Plots of marker pairs are supporting views; when the decision uses additional measurements, they must not show a single unconditional two-dimensional boundary as though it were the full rule.

## 4. Immediate experiment: useful panels that can earn their size

The surviving development result is specific. For three mean-shift seeds, optimized supports recover 11/12, 12/12 and 11/12 planted variables among 200 candidates under a 16-feature cap. With the same centroid readout, mean ARI improves from approximately .601 on the PCA supports to .733 on optimized supports. These are posthoc development findings, and nuisance variables remain. The nonconvex results do not show a comparable success.

The next implementation should answer one bounded question: **Does the improved panel generator reproduce on fresh observations, and can its native rule be shortened while retaining useful assignments?**

Use the exact [protocol specification](interpretability-protocol-review-2026-10-04.md):

1. Compare only PCA-generated panels and rank-preserved global-search panels, with the same centroid fitting procedure and a maximum of 16 measurements. Keep optimizer settings fixed.
2. Draw two independent discovery samples from each saved feature population. Keep feature identities fixed between them. Fit preprocessing, panels, complete centroid rules and all shorter candidate rules using discovery data only.
3. Use a separate sample to choose the shortest already-fitted rule whose simultaneous upper bound on disagreement with its own full rule is at most 5%. The first candidate set is a fixed sequence of prefixes, not enumeration of every possible subset.
4. Use untouched observations to report utility, feature recovery, independent-discovery agreement, rule fidelity and failures. Report all planned fits, including unsuccessful ones.

The proposed block sizes are 400 + 400 discovery, 800 certification and 2,000 test observations per population replicate, with ten fresh replicates per condition. These are engineering defaults, not a power guarantee. The short matrix has a distributed-mean condition, a substitute-measurement condition, three Gaussian controls with different covariance structures, and a grouped-moons boundary case. There is no hyperparameter grid.

Report the full panel-size curve, with <=8 and <=12 as readable summaries rather than universal definitions of interpretability. A model built from 12 weakly informative measurements may legitimately need more than eight. The full 16-feature rule has zero disagreement with itself, so retaining it cannot count as successful compression.

Fidelity means preserving a specified fitted model's decisions. A small rule that faithfully reproduces a poor model remains poor. Therefore the optimized-minus-PCA comparison and external utility must be reported alongside every compression claim. Use a common untouched evaluation set to compare independently discovered partitions, without choosing the best model using its annotations.

This experiment contains the remaining necessary component ablations: proposal improvement with assignment held fixed; full versus shortened rules; empirical versus confidence-bounded shortening; independent rediscovery; and single-population controls. It moves implementation forward rather than reopening a broad search over fitness formulas.

## 5. Sequence after that experiment

### Milestone A: finish the node's explanation

Implement the frozen protocol and a report containing the seven evidence fields above. Replay exact rules and verify that certification never fits a new candidate. If optimized panels no longer improve on the PCA baseline, revise or replace the proposer. If rules cannot be shortened, report the required measurements and the failed compactness target without loosening the tolerance after inspecting results.

The useful output is a reproducible candidate node, not yet permission to grow a tree.

### Milestone B: implement a scoped reason to split or stop

The current Gaussian failures rule out using stability or low graph loss alone as acceptance. A concrete next prototype can compare a discovery-fitted alternative density with a single-Gaussian reference on a separate acceptance sample, using the established split-likelihood method from [Universal Inference](https://arxiv.org/abs/1912.11436). Its assumptions and multiplicity handling are specified in the protocol.

This tests a particular population model. A heavy-tailed single population can also violate Gaussianity, so rejection cannot be named proof of two biological types. Report reference-model departure, minimum group sizes and explanation adequacy separately. Add a heavy-tailed control before interpreting acceptance more broadly.

At descendants, ancestor routing truncates the data distribution. A fresh sample alone does not justify reusing an ordinary Gaussian null there. Hierarchical acceptance needs a reference model accounting for the route or an explicitly exploratory status. This is a substantive research issue to resolve before treating recursive growth as validated.

### Milestone C: return to a biomedical case early

Cytometry remains the primary application because it matches the original proposal's named-marker and gating goals. First audit feature names, transformations, expert-label provenance and usable specimen identifiers. The present Levine loader excludes an `individual` field from predictors but does not preserve donor groupings in its output; its existence does not establish enough independently sampled donors for the proposed design.

A known two-population contrast can debug rules and marker recovery. It is not evidence that the method independently found that contrast in the full population, because its input cells were selected using annotations. The end-to-end case study should use a prespecified parent population or complete quality-controlled sample, with annotation labels reserved for evaluation.

Have a domain expert inspect a small, consistently formatted shortlist: identify what the rule means, assign a few held-out examples using it, identify unnecessary or surprising markers, and suggest biologically equivalent alternatives. Record correctness, time and specific objections. This is an initial usability exercise, not a statistically established human-factors result. Formal expert-study design follows if feasible.

METABRIC remains secondary development evidence: the current feature universe is PAM50-enriched and was partly chosen using all patients. Repeated splits of that matrix cannot turn familiar-gene recovery into independent biological validation. Known facts are valuable evidence, but need provenance and a comparison against alternative panels rather than a posthoc plausibility story.

### Milestone D: support one explicit nonlinear family

Preserve the nonconvex ambition with a scoped branch. A candidate is a sparse radial or shared-scale rule: selected measurements contribute weighted squared deviations from a learned centre, and a radial interval or threshold defines membership. This would give a native nonlinear explanation for suitable shell-like populations. It remains a design hypothesis, distinct from the previously unsuccessful squared sparse-k-means baseline.

First test the rule on supplied informative features, then test autonomous panel discovery. If the rule fails even with the correct measurements, improve the shape model before investing in search. If supplied features work but discovered ones do not, search is the obstacle. Keep a curved-manifold failure case visible. Do not select favorable final benchmarks after viewing outcomes and then describe those results as confirmation; define the intended shape family and comparison set before the next test.

A radial success would justify a family-specific contribution. It would not resolve arbitrary moons, covariance-defined groups or all nonconvex clusters. The tree and panel-verification machinery can be shared while assignment assumptions remain explicit.

### Milestone E: integrate a small hierarchy and candidate chooser

Start with a depth-two tree once node explanation and acceptance are usable. Validate routing, reduced sample counts, path complexity, per-node panels, stopping reasons and complete held-out assignments. Reuse suitable legacy tree code, but do not inherit its validation claims automatically.

Then present a frozen shortlist in an interface. A person should see what changes when choosing a smaller panel: measurements saved, assignments changed, uncertainty and independent-sample agreement. Choosing among already-certified candidates differs from editing a panel and fitting a new rule; the latter needs new validation.

Benchmark the complete method against direct tree clustering and cluster-then-gate methods, as well as the simple PCA-panel baseline. Compare usefulness at matched measurement/rule budgets and compactness at comparable utility, with runtime and failures included. For the original cytometry scale, separately measure discovery cost on representative samples and batched assignment to all cells. A 200-feature simulation does not establish scalability to hundreds of thousands of cells.

## 6. Implementation handoff

- Working directory: `C:/Users/Peter/Desktop/Github/ATOMIC_Clustering`.
- Environment: existing `.venv-research`; preserve the recorded dependency versions.
- Reusable components: `atomic_research/rank_preserved_kernel.py`, `fidelity_bounds.py`, centroid-rule export and replay, and existing dataset/result conventions.
- New work: saved fixed-population generator, A/B/C/T runner, discovery-only prefix builder, and a compact evidence report. Use new files/results so historical experiments retain their source identity.
- Required artifacts: frozen configuration, feature-population manifest, row splits, preprocessing, every candidate model, exact rules, certification counts/bounds, all test outcomes, runtimes and fit-failure reasons.
- Entry command: not supplied yet because this protocol's runner has not been implemented. Do not run an earlier suite expecting it to execute this design.
- Execution: perform a short integration check first; provide the full local command once it exists. Save progress after each completed replicate so longer manual runs are inspectable and resumable.

The first implementation target is Milestone A. The other milestones make the original proposal's remaining obligations visible without requiring all of them to be solved before the next useful experiment.
