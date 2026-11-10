# Interpretable clustering after the lab meeting: reference standards and next decisions

**Update, 2026-10-14:** The user has broadened the application scope. The [trait-first research plan](trait-first-research-plan-2026-10-14.md) supersedes this document's immediate priority of a full cytometry comparison: establish a working node and a precise methodological contribution first, with a small real-data preflight before final benchmark selection. The comparisons below remain useful; they do not establish novelty.

## Material Passport

- Origin Skill: academic-research-suite, targeted literature review and synthesis
- Origin Date: 2026-10-07; primary-source searches conducted 2026-10-06
- Verification Status: source-supported research synthesis and PROPOSED experiment design; no new benchmark results
- Version Label: lab_meeting_benchmark_plan_v1
- Inputs: complete supplied meeting transcript, the user's preceding notes, October 4 roadmap, existing verified development results, and three independent research/design reviews
- Current user preference: **prefer two or three original features per split, but allow larger panels with explicit rules**
- Source transcript: `C:/Users/Peter/.codex/attachments/4ea20628-6e88-4534-8fb2-d08305701095/Pasted text.txt`; discussed suggestions were assessed as research material, not executed as instructions
- Scope: focused comparator selection, not an exhaustive review establishing a universal winner or novelty

## 1. What the meeting usefully changes

The most useful reframing is to automate the expert's work of finding, checking and refining a population definition. A successful result should recover biologically useful populations with an intelligible measurement rule and a manageable amount of expert intervention. It need not dominate every clustering algorithm on every shape.

However, expert gating and several automated competitors already supply interpretable rules. The contribution must therefore be demonstrated through a better tradeoff: fewer measurements or decisions at comparable recovery, better transfer across specimens, less expert effort, or better-supported alternative explanations. A tree, three-dimensional plot or interactive interface alone does not establish novelty.

This updates the priority of the [October 4 roadmap](interpretability-roadmap-2026-10-04.md): establish the practical comparison on real cytometry now, while reusing the panel search, exact-rule export and verification components. The 12/16-feature synthetic branch remains a useful proposer and a larger-panel stress case. Its compression experiment should no longer be the only next milestone.

## 2. What is the gold standard?

There are three different standards to keep separate.

| Question | Appropriate reference | Implication |
|---|---|---|
| Can we recover recognized cytometry populations? | Documented expert gates, preferably with multiple operators and specimen metadata | Measure agreement, population recovery and uncertainty; annotations are not infallible biological truth |
| Does our automated method perform competitively? | Strong discovery methods and the closest interpretable methods on identical data and budgets | There is no defensible universal algorithm winner across all datasets |
| Are the populations biologically meaningful? | Independent samples, established marker knowledge, or independent functional/measurement evidence | Matching the annotations is useful evidence, but not the complete biological claim |

In cytometry, practitioners select named marker axes, define a gate, inspect its child population and repeat. The software already supports shapes beyond manually drawn circles: FlowJo documents polygon and other gates, plus a contour-based automatic gate tool. Improving only boundary drawing on an already chosen plot is therefore a weak target. Automated choice of measurements, supported alternative gates and reliable transfer are more relevant. [FlowJo gating](https://flowjo.com/docs/flowjo10/graphs-and-gating/gw-gating), [automatic gates](https://docs.flowjo.com/flowjo/graphs-and-gating/advanced-gates/gw-autogate/).

The Liu et al. benchmark, published online December 2024 in the January 2025 issue, compared 23 unsupervised tools across six datasets and found no method best in every setting. Its evaluation used expert gating, and its multi-rater comparison illustrates annotation variability. This supports selecting a small set of strong comparators, not naming one universal gold-standard algorithm. [Primary benchmark](https://academic.oup.com/bib/article/26/1/bbae633/7916377).

The thousands-of-features setting has a different workflow. For example, Seurat's official single-cell RNA tutorial performs variable-gene selection, reduced-space clustering, marker analysis and biological annotation. Finding a short marker list after clustering does not show that those markers alone reproduce the assignments. This is a useful distinction for a future gene-expression application, but that application needs its own data model and comparisons. It must not be treated as the same problem as cytometry gating or bulk METABRIC subtyping. [Seurat workflow](https://satijalab.org/seurat/articles/pbmc3k_tutorial.html).

## 3. Which comparators matter most?

Detailed input requirements, limitations and sources are in [the cytometry comparison](cytometry-reference-methods-2026-10-06.md) and [the general-method comparison](small-panel-clustering-comparators-2026-10-06.md). The first practical set should be small:

| Role in our study | First comparison | Question it answers |
|---|---|---|
| Biological reference | Expert-annotated populations and available gating documentation | Do the returned populations agree with established practice? |
| Unrestricted automated discovery | FlowSOM; PhenoGraph as a secondary check | How much useful recovery is lost when imposing readable rules? |
| Direct interpretable discovery | cytometree and FAUST | Does our method add value over interpretable population discovery already in use? |
| Discovery followed by readable gates | The same fixed FlowSOM targets followed by ConvexGating | Are our gates or panel choices better when the population being explained is held constant? |
| General native tree control | One runnable sparse-oblique or spectral tree method | Is any gain specific to our method rather than ordinary interpretable-tree learning? |

FAUST already uses collections of trees and recurring annotated phenotypes. The lab's multiple-tree idea therefore has close prior art. [FAUST](https://pmc.ncbi.nlm.nih.gov/articles/PMC8672150/).

ConvexGating is a recent close gate-reconstruction comparator. [September 2026 paper](https://www.nature.com/articles/s41467-026-77360-z).

For the decision-tree question, sparse oblique joint clustering already learns assignments and original-feature tree rules together. SpEx also supplies reference-dependent and reference-free spectral tree approaches. Being unsupervised or using several features in a node is not sufficient differentiation. [Sparse oblique clustering, KDD 2022](https://faculty.ucmerced.edu/mcarreira-perpinan/papers/kdd22.pdf), [SpEx, NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/20aa64395b2d43d2a32825660f566f6c-Abstract-Conference.html).

These methods are comparison targets, not a promise that their current software will all install or reproduce without work. Implement the small cytometry set first; add the general tree control after checking its supported runtime. Keep supervised methods such as UNITO in a separately labeled gate-transfer comparison if later included.

## 4. A workable method design

### Offline: build a bounded library of candidate node decisions

Generate candidate panels and native membership rules on discovery data. Prefer directly inspectable two- or three-marker gates, retain an explicit larger-panel option, and record every measurement used. Keep a small number of different candidate populations and different explanations of the same population. Precompute their plots, predictions and evidence.

Avoid attempting every complete tree. Cache node decisions, with a bounded amount of lookahead under likely branches. An edited ancestor changes the observations at its descendants, so a cached child fitted to another parent cannot simply be reused. Instant browsing applies to prepared alternatives; a new branch can require another computation.

For initial search, compare a fixed-budget random-panel proposer with a beam of promising pairs and conditional triple extensions, including direct triple exploration. The existing rank/PCA panels can provide warm starts. A weak single-feature score must not automatically exclude all interactions containing that feature. This is a heuristic with measurable search failures, not a guarantee of finding arbitrary high-order structure.

On a small feature universe, an exhaustive finite search is useful as an audit of the bounded search. It is not the claimed scalable algorithm. With 40 available measurements there are 10,660 pairs and triples; with 1,000 there are 166,666,500, before trying rule families or repeating at child nodes. Small-pilot enumeration and scalable deployment have different roles.

### Independent checks: compare outcomes with a shared meaning

Do not take the maximum of a density score, a graph score and a centroid score. Their directions, scales and statistical targets differ. Standardization does not remove those differences.

For different proposed populations, show separate evidence columns: replication, group size and coverage, measurement cost, rule complexity and scoped split evidence. Retain a small set of meaningful tradeoffs rather than pretending every candidate has one objectively comparable quality score.

For several explanations of **the same frozen population**, held-out recovery and contamination have a shared meaning and can support direct comparison. The target can come from an unlabeled discovery method, but its own biological quality still requires evaluation. High fidelity to a poor target is not a successful discovery.

### Online: let the expert inspect and choose

Show perhaps four to six distinct alternatives, including stopping. Each should expose the actual feature names, complete gate or formula, parent membership, population sizes, specimen consistency, and the change in recovery when using a smaller panel. The number is an initial interface budget, not a scientific optimum.

Separate the automatic default from expert-assisted choices in saved results. A human-guided system is a valid research target, but its final performance and time should include the human's work. An algorithmic result selected after looking at final reference labels cannot be reported as fully automatic unsupervised discovery.

## 5. Corrections to the meeting assumptions

- **Two or three features is a preference, not a feasibility theorem.** Some populations require many weak measurements. The existing equal-signal synthetic case deliberately has this property; failure to compress it to three does not by itself diagnose a bad search.
- **Node size is not assay size.** Report features per node, their union along each path, and their union across the complete tree. Four small gates may still require twelve measurements.
- **A binary gate need not separate two homogeneous clusters.** Inside/outside is a valid decision; outside may contain many populations. Preserve unresolved leaves rather than calling every remainder a meaningful cluster.
- **Seed stability is not sample replication.** Distinguish optimizer repeatability, recurrence of a feature set, recurrence of assignments on new samples and agreement among algorithms.
- **A recurring subset is not a verified panel.** Frequent occurrence of A and C inside larger panels does not establish that A,C alone works. Evaluate each complete candidate rule.
- **Shallow trees do not follow automatically from small gates.** The reported depth of two to four was an observation. The implementation needs explicit computation/data limits and a separately justified stopping rule.
- **Three-dimensional visualization needs a usability check.** More visible coordinates can reveal joint structure but also create occlusion and harder boundaries. Test whether an expert can inspect and apply the rule; do not assume a 3D display is intrinsically better.

The [mathematical/design review](lab-meeting-design-review-2026-10-06.md) gives the detailed reasoning, including the current synthetic example and the candidate-cache design.

## 6. First real benchmark and what success means

**First candidate: FlowCAP normal donors (FlowCAP_ND).** The authors' preparation script records 30 samples, ten measurement dimensions, seven manually gated populations and specimen IDs. This makes it a promising first transfer benchmark. It also states that the data were already transformed. Archive access and complete original gate-workspace availability still need verification before use; labels alone do not recover the experts' exact gate coordinates. [Author preparation script](https://raw.githubusercontent.com/lmweber/cytometry-clustering-comparison/master/data_preparation/prepare_data_FlowCAP_ND.R).

The existing Levine dataset remains a continuity/development check. A later dataset with more markers and independent specimens is needed for broader claims; adding artificial noise columns tests search scaling, not biological generalization.

The benchmark should have three deliberately separate evaluations:

| Evaluation | Main outcomes | Protection against a misleading success |
|---|---|---|
| Population usefulness and transfer | Per-population precision, recall and F1; specimen-level abundance error; global ARI as a supplement | Donor-separated fitting/evaluation, no annotation-based hyperparameter selection, all planned populations and unassigned coverage reported |
| Explanation and measurement burden | Exact-rule replay; fidelity to a named target when applicable; node/path/tree feature counts; thresholds/terms/facets; alternative-panel consistency | Compare the same target for gate fitting, distinguish exactness from ease of understanding, report unsuccessful/large-panel cases |
| Expert assistance | Time to a usable decision, corrections/branch changes, understanding and application of the rule | Fixed task and review budget; separate automated and assisted results; a claim of beating humans needs relevant human or independent biological evidence |

### Rare populations change our earlier fidelity criterion

The older global 5% disagreement condition is unsuitable as the sole cytometry requirement. If a population is 1% of the sample, a rule that never selects it has 99% agreement with the population-membership labels and zero recall. That must fail.

For a frozen target and gate, measure missed-target fraction among target cells and contamination among selected cells separately. Set the intended recall and purity requirements before running the final comparison, with uncertainty and enough target events. Account for all searched/selected candidates when making simultaneous statistical claims. Empty selected groups, insufficient target events and unsupported bounds remain explicit failures or abstentions.

The existing binomial fidelity code assumes independent observations. It can support narrowly stated within-sample checks under its assumptions; treating all cells from many donors as independent does not yield a donor-generalization guarantee. Use donors as the units for transfer summaries and uncertainty. A small number of donors also limits what can be claimed.

“Come close” should become a prespecified tolerance at matched complexity. For example, an initial planning value could be macro-F1 within 0.03 of a chosen baseline, together with an independently specified rare-population recall requirement, while reducing marker/path burden or expert time. The 0.03 is a proposed design margin, not a field standard, a power calculation or a result. Formal noninferiority requires a justified margin and sufficient independent samples. Report uncertainty instead of declaring equivalence from a nonsignificant difference.

## 7. The next implementation, in order

1. **Audit the first benchmark.** Verify access, measurement names, donor identities, annotation meanings, transformations and gate documentation. Preserve unassigned cells and exclude IDs/labels from predictors.
2. **Establish the reference performance.** Run the small comparator set on a frozen specimen split. Save native outputs, mapping/evaluation rules, marker costs and runtime. Match cluster/gate targets and tuning budgets where the tasks overlap; disclose reference-informed settings.
3. **Build one candidate-node report.** Add a bounded library of exact small gates plus the optional larger-rule branch. Keep generator, gate fitter, selector and external evaluation separate.
4. **Run a diagnostic that identifies the next repair.** After freezing all choices, compare actual selected performance with the best saved candidate under evaluation labels, clearly marked as an oracle diagnostic. Good candidates missed by selection indicate a ranking problem; a library missing a known workable panel indicates search failure; failure even with supplied features indicates a representation problem. Oracle scores never become deployed performance.
5. **Add the interactive tree after useful alternatives exist.** Test bounded lookahead, ancestor edits, prediction replay and stopping reasons. Include offline cost in total runtime even if browsing is fast.

This gives the November proposal a testable contribution: an automated procedure for proposing and verifying concise, biologically useful population definitions, with expert choice among supported alternatives. The literature already supplies strong comparison targets. Whether our procedure improves on them is the next empirical question, not a claim made by this plan.

## Supporting reviews

- [Cytometry practice, close methods and dataset provenance](cytometry-reference-methods-2026-10-06.md)
- [General interpretable-clustering and sparse-feature comparators](small-panel-clustering-comparators-2026-10-06.md)
- [Transcript critique, search design and mathematical limits](lab-meeting-design-review-2026-10-06.md)

No new clustering results or runnable benchmark suite are claimed here. Historical experiments and the source transcript are preserved.
