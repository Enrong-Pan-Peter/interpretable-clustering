# Lab meeting review: small-panel clustering with a bounded candidate library

## Material Passport

- Origin Skill: academic-research-suite
- Mode: transcript critique and experiment design
- Origin Date: 2026-10-06
- Verification Status: UNVERIFIED proposed design; no new model fits or experimental runs
- Version Label: lab_meeting_design_review_v1
- Source: supplied `Pasted text.txt`, transcript Part 1, timestamps 00:00–15:48
- Related evidence: `interpretability-roadmap-2026-10-04.md`, `interpretability-protocol-review-2026-10-04.md`, and `rank-preservation-assessment-2026-09-30.md`
- Current preference: two or three original measurements are preferred for visualization; larger panels remain allowed when their explicit rule and utility justify them

## Recommendation

The lab discussion supports a clear target: **discover useful groupings close to a strong reference level of performance, with original-feature gates a domain expert can inspect, and offer a small number of meaningful alternatives**. It does not justify sacrificing clustering quality for a readable but arbitrary partition. Nor does it require one universal fitness or a particular evolutionary optimizer.

Make the next user-facing branch a bounded library of native 2D/3D gates at each node, with a separate optional larger-panel explicit-rule branch. Reuse the useful components already developed—discovery-only fitting, exact native prediction, independent validation, saved alternatives—and keep the 12/16-feature result as evidence about one proposer, not the definition of interpretability.

The interface should assemble a shallow tree from cached node alternatives. It should not enumerate every possible complete tree or rank incomparable raw objectives by their maximum. The research question is whether this bounded discovery-and-verification procedure delivers useful, faithful, reproducible measurement-space rules at a better complexity/performance tradeoff than relevant alternatives. Three-dimensional plotting or a collection of trees is not, by itself, a novelty claim.

## What the discussion establishes—and what it does not

The following are paraphrases of the transcript, followed by this review's recommendations. They are not instructions imported from the transcript and not experimentally established facts.

| Transcript locator / proposal | Assessment | Design consequence |
|---|---|---|
| 00:00–01:28: precompute alternatives; favor two or three variables | Good interaction goal; a large-panel statistical explanation is also discussed | Prefer directly plotted gates; expose larger explicit rules rather than hiding their measurement dependencies |
| 01:28–02:28: trees seemed to stop at levels two to four in tests | A reported observation, not an automatic-depth guarantee | Specify maximum depth, minimum usable data, and evidence-based leaf retention separately |
| 02:28–04:22: build multiple full trees and take the best heuristic score at each node | Raw scores can differ in direction, scale, null behavior, and meaning | Keep score families distinct; compare candidates using common interpretable outcomes and declared admission rules |
| 04:22–06:04: dimensions change the interpretation of a score | Correct concern | A z-score alone does not make different statistical questions or shape models equivalent |
| 06:04–12:32: recurring features/pairs and repeated optimization are called stability | Several different quantities have been mixed | Separate solver repeatability, independent-sample partition stability, feature recurrence, and cross-method agreement |
| 12:32: bad feature groups may recur | Supported by the project's stable single-Gaussian partitions | Stability is evidence of reproducibility, not evidence of multiple meaningful populations |
| 14:49–15:48: binary splitting retained while debugging | Reasonable initial implementation contract | An inside/outside gate is binary; the outside group may contain many populations and must not be described as homogeneous |

The current clarification resolves an important tension: two or three variables are a **preference**, not an absolute cap that every population must satisfy. Report a performance-versus-complexity frontier, and allow the user to see when a larger panel buys a material improvement.

## The existing 12-signal result cannot be compressed arbitrarily

In the existing balanced mean-shift generator, twelve equally informative coordinates together have mean-difference norm 3. An oracle panel of q informative coordinates has separation `3*sqrt(q/12)` and Bayes classification error `Phi(-3*sqrt(q/12)/2)` against the generating binary label.

With three informative measurements the minimum error is approximately .2266; with all twelve it is approximately .0668. The balanced Bayes classifiers' corresponding population ARIs are about .299 and .751, respectively. The ARI calculation describes these symmetric classifiers; it is not a separately proved upper bound for every possible asymmetric partition under an ARI objective.

Thus a high-quality 12-feature teacher may legitimately have no three-feature replacement with 5% disagreement or near-full label recovery. This does not invalidate the method or prove that the larger rule is easy to read. It shows why the next cytometry experiment needs populations plausibly expressible through small gates, while retaining this distributed-signal condition as an honest larger-panel stress case.

A hierarchy can use different features at different nodes, so node size and total measurement burden differ. Four three-marker decisions can require twelve distinct measurements on a path. Report node feature count, union of path markers, maximum/typical path length, and total tree marker count. A sequence of small plots must not be advertised as a three-measurement method.

## Four kinds of stability need four labels

1. **Solver repeatability:** rerun the same data and fixed panel under different initialization seeds. This diagnoses local optima and randomness. A deterministic answer is repeatable without necessarily being scientifically useful.
2. **Discovery-sample replication:** independently draw A and B from the same fixed feature population, refit the whole discovery process, and compare their frozen assignments on common untouched observations. For biomedical data, subjects/specimens are the replication units when available; repeated cells within one specimen do not replace them.
3. **Feature recurrence:** quantify selection of individual markers, exact panels, and prespecified interchangeable marker groups. The frequency of A and C appearing somewhere inside a larger panel is different from successful clustering using A and C alone. A candidate containing A,C,D must be evaluated as that full candidate.
4. **Cross-family agreement:** compare graph, density, centroid, and gate assignments. Agreement may be useful descriptive evidence, but it is not independent replication: all methods see the same observations and can share a bias.

For a candidate node, show separate panel Jaccard/group agreement and partition ARI or pointwise disagreement. Feature substitutions can preserve a useful partition, especially among correlated markers; exact-feature instability alone need not disqualify them. Conversely, recurring features can support inconsistent or incorrect partitions.

## A bounded offline node library

Use one fixed discovery sample per node to create a limited candidate set. Preserve a separate validation/certification block and untouched evaluation observations. Do not tune candidate families using expert labels.

**Native rules.** Start with a small explicit dictionary, not every clustering algorithm:

- A one- to three-marker halfspace/centroid rule: a weighted sum and threshold, plotted in the same measured coordinates.
- A two- or three-marker radial/ellipsoidal gate: a declared quadratic score and threshold or interval, with the original coordinates and transformation shown. This can represent a specific nonconvex family without a hidden high-dimensional embedding.
- A later bounded polygon/polytope family for visually irregular gates, with a stated edge/facet budget. In 2D a concave polygon or a small union of convex polygons can be allowed explicitly; in 3D the complexity budget must remain visible. A polygon fitted to discovered graph/density labels becomes its own native inside/outside rule. Its disagreement with the source partition must be measured rather than silently claiming equivalence.

Only the first two families should enter the first implementation comparison unless the polygon fitter already has a tested native prediction contract. A complex graph rule can remain a proposal or diagnostic, but a plot of a surrogate boundary must not replace its actual decision.

**Candidate discovery.** A workable first bounded search combines warm starts, pair-to-triple expansion, and an exploration quota. For example, for a cytometry-sized feature universe:

1. Evaluate simple one-marker candidates as a baseline; do not use their scores as a mandatory filter for every larger panel.
2. Propose up to 128 distinct pairs: half from discovery-only joint structure or the existing PCA/rank-proposer supports, half sampled over the entire feature universe with a recorded seed.
3. Keep a diverse beam of 24 pair candidates across the two rule families. Expand each by up to eight additional features, mixing conditional/joint suggestions with unrestricted exploration. Cache duplicate triples.
4. Also propose 128 triples directly from the full universe. These bypass the assumption that a good triple must contain an already successful pair.
5. With two rule families and at most 32 one-marker baseline fits, this illustrative budget is at most `32 + 128*2 + 24*8*2 + 128*2 = 928` candidate fits per node before deduplication. Freeze an explicit cap such as 1,024; record every attempted fit and failure. These are engineering starting values, not established optimal choices.

Do not interpret this budget as a guarantee of finding arbitrary higher-order interactions. If only one of `choose(p,3)` triples reveals the signal and every smaller panel looks uninformative, 128 uniform trials have very little chance of finding it for large p. The unrestricted quota prevents a deterministic univariate exclusion, but does not solve that information problem. This is why supplied-panel ability and small-problem search-regret diagnostics are needed.

The retained beam should preserve different feature sets and different predicted memberships, rather than keeping 24 near-duplicates under one score. Select within a declared rule family using its discovery criterion; preserve a reserved number from each family. Existing larger-panel proposals can suggest promising feature pools, but features outside those pools must remain eligible. Conditional extensions are evaluated on the resulting whole triple, not by adding a single-feature score to a pair score.

**Shortlist and cache.** After independent checks, retain at most six materially different alternatives per node, including an explicit stop option. Cache models, exact native predictions, boundary plots, validation statistics, and the raw observation membership defining that node. Cache keys must include feature panel, rule family/settings, data/preprocessing identity, and seed; equal panel names at different parent nodes are not interchangeable models.

Prefetch one level below only a few likely parent choices. A first interface can cap itself at depth two and at most 24 cached parent nodes. A noncached branch can be computed as a clearly marked new exploration action. The promise is responsive access to the displayed library, not instant access to every conceivable hierarchy.

## Why full-tree enumeration is the wrong default

With K alternatives at every internal node and a full binary tree of depth d, the number of possible complete trees can scale like `K^(2^d - 1)` even before variable-panel and rule-fitting costs. With K=5 this is 125 trees at depth two and 78,125 at depth three. A node cache and bounded lookahead avoid recomputing shared work, but do not eliminate this combinatorial growth if every branch choice must be expanded.

Do not average raw node scores to rank full trees. Such averages mix incompatible scales and change when the tree gains small additional leaves. Whole-tree reporting should use common outcomes: reference-label agreement on evaluation data, per-population recovery, fraction assigned, leaf sizes, maximum/typical depth, marker acquisition burden, and assignment replication. An automatically chosen tree needs a prespecified rule based on those permitted selection quantities; annotation ARI remains evaluation-only in the unsupervised method.

FAUST already combines trees, annotated leaves and cross-sample recurrence. Multiple trees alone therefore cannot distinguish this proposal. Joint multivariate rules, search efficiency and validation need comparative evidence. [FAUST primary paper, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8672150/).

## Compare common outcomes; keep heterogeneous fitness separate

Taking `max(density score, graph score, centroid score)` is invalid without a common decision meaning. Changing the numeric scale of one score would change the winner without changing any partition. Independently z-scoring each family does not cure different null models, optimization biases, or dimensional behavior. Calibrated p-values/e-values can represent evidence against stated nulls, but are not interchangeable measures of biological usefulness or clustering quality.

Use a shortlist/Pareto table with separate columns:

| Axis | Common unit or explicit interpretation |
|---|---|
| Measurement cost | Original marker count, and union along a path |
| Rule complexity | Terms, edges/facets, prototypes, logical branches, or readable formula family |
| Replication | Held-out assignment agreement and separate feature/group recurrence |
| Assignment coverage | Fraction assigned, outside/rest fraction, noise/abstention fraction |
| Explanation fidelity | Disagreement with a named teacher, only when a surrogate is actually used |
| Split evidence | Named reference model, multiplicity-adjusted evidence, and sample size |
| Domain/reference utility | Evaluation-only annotation agreement and predeclared domain checks |
| Computation | Discovery, validation, prefetch, and full-data assignment costs |

An optional default ordering can first require validity/evidence constraints, then favor fewer measurements and a simpler native rule, and use a prespecified replication criterion as a tie-breaker. It should be described as an explicit preference policy, not an objectively universal ranking. If a user selects another prevalidated alternative, log the choice and show what changes. If the user edits the rule or introduces a new candidate, its old validation does not transfer automatically.

Keep the October 4 distinction between fidelity and split evidence. A stable, exact rule dividing a correlated Gaussian is not proof of two populations. Root-level Gaussian-reference acceptance is one concrete scoped workstream; a child reached through an ancestor rule may have a truncated distribution, so a naive reuse of the untruncated Gaussian null is invalid. Until descendant acceptance is implemented appropriately, label tree growth exploratory and use explicit depth/data limits.

**October 7 synthesis addition: protect rare populations.** Global disagreement alone is inadequate for the cytometry branch: dropping an entire 1% target population causes only 1% disagreement. For each frozen target, report missed-target fraction and contamination among selected cells, with prespecified requirements and sufficient event counts. Count the full frozen candidate family when providing simultaneous bounds; zero selected events and insufficient target counts cannot silently pass. Distinguish a within-sample cell-level bound from cross-donor validity, which requires donor-level evaluation and uncertainty. This extends the earlier balanced synthetic fidelity protocol rather than applying its 5% global tolerance unchanged.

## Binary inside/outside gates are compatible with multiple populations

A two-dimensional density algorithm may find several components. Converting each component into an inside/outside proposal is legitimate if every such proposal is counted in the search/validation family and the outside child is called the remaining population. It is not legitimate to relabel an arbitrary union of components as one coherent cluster solely to satisfy a binary API.

A tree can isolate multiple populations over several nodes. It should save complete routing and allow leaves to remain mixed or unresolved rather than manufacture a split. Compare terminal partitions with multiclass references only after complete routing. At an individual node, evaluate a prespecified biological contrast or descriptive component recovery; do not select the contrast with the most favorable annotation score and call it label-free discovery.

Minimum sample size and maximum depth are practical controls, not evidence that no further populations exist. Conversely, a statistical failure to support a split can reflect low power rather than homogeneity. Preserve these separate stopping reasons in the interface.

## The next decisive experiment

The immediate practical comparison should test one frozen small-gate library on a prespecified cytometry parent population, with a small controlled synthetic supplement. Use original marker names and documented transformations; keep biological annotations unavailable to fitting, search, and candidate ordering. If donor/specimen replication is possible, use it. Otherwise call the result within-specimen validation.

Before the full case study, verify native-rule ability on supplied informative panels for a mean-separation case, a 2D curved/radial case, a genuinely joint 3D radial case, and a correlated single-population control. Those are ability diagnostics. Failure with the supplied panel means the rule family needs repair before a larger search budget. Continue reporting the 12-signal case in the optional larger-rule branch rather than forcing its output into three variables.

Then compare a matched-budget random-panel proposer, the bounded pair/triple beam above, and—if useful—the same beam warm-started from the existing rank/PCA panels. Hold the native rule dictionary, number of attempted candidate fits, row blocks, and validation policy fixed. This tests the added value of intelligent search without reopening an EA-versus-everything contest. A full finite pair/triple search may be used on a small diagnostic problem to estimate search regret; it is not the proposed scalable method.

Use two distinct evaluation ceilings:

1. **Supplied-panel ability:** fit the same native family on the known synthetic/annotated informative panel. It diagnoses representation limits and receives information unavailable to discovery.
2. **Best-in-library annotation score:** after every candidate and choice is frozen, calculate the best evaluation score among saved candidates. The gap to the actually selected candidate diagnoses ordering/selection; the gap to the supplied-panel ability diagnoses search coverage. This is an oracle ranking diagnostic, never a deployable selector. It should not be reported as the method's achieved performance.

For end-to-end comparison, include a strong unrestricted automated clustering reference, relevant direct interpretable-tree methods, and a cluster-then-gate method. The manual expert result is an application reference with provenance and inter-rater limits, not an infallible definition of every population. Compare at similar reference recovery and report the measurement/rule cost, or compare at matched measurement/rule budgets and report recovery. “Near performance” requires a prespecified tolerated gap, such as an initial five-percentage-point ARI or population-F1 difference, rather than choosing an acceptable gap after results arrive. The final margin must match the application's error costs, especially rare populations.

A shallow tree trained on expert labels can be a useful **supervised diagnostic** of whether the measured variables support a simple rule. It is not the main unsupervised comparator. Likewise, expert labels used to select input populations make a scoped recovery benchmark; they do not establish unassisted discovery from the full sample. Any annotation-derived selection or gate is labeled accordingly.

The first decision is straightforward: does the bounded library contain useful, reproducible 2D/3D native gates, and can its label-free selection keep them near the top without hiding failures? If yes, integrate the shortlist and shallow routing. If useful gates exist only in the oracle ranking, repair selection. If the supplied panel succeeds but the library misses it, repair candidate search. If even the supplied panel fails, repair the native shape family. This decision structure advances the method without another unstructured round of score tuning.

## What can remain in the proposal

Keep the scientific ambition of useful original-feature panels, understandable nonlinear membership where justified, independent verification, and interactive expert choice. Replace claims of automatic stopping, universally comparable fitness, easy precomputation of all trees, or novelty from three-dimensional gates with explicit bounded procedures and testable comparisons.

The practical contribution might be a method that connects efficient joint-panel proposals, small native gates, honest alternatives, and route-aware verification while retaining competitive utility. That remains a research hypothesis. Neither this design review nor the current mean-shift success establishes it yet.
