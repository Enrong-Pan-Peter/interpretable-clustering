# Decisions, tradeoffs and open obstacles

These are the documented reasons behind direction changes, expressed as research conclusions and hypotheses. They are not a verbatim internal reasoning transcript.

## A failure can occur at several stages

| Stage | Diagnostic question | What the project found |
|---|---|---|
| Target meaning | Is the desired population identifiable from these measurements and assumptions? | Different stable partitions may represent activity, identity, batch or another distinction. External labels are useful evidence but need not equal density groups. |
| Candidate search | Was a useful feature set ever evaluated? | Many radial failures, including higher-dimensional replication misses, never visited the known useful set. |
| Fitness/ranking | If evaluated, would the useful set win? | Early persistence and some sparse objectives preferred the wrong separation. One weak radial population exposed a search-score ordering failure that reversed on fresh blocks. |
| Geometry/assignment | Can the model represent the grouping given the right features? | Centroid rules cannot express concentric shells. The radial model fails on mean-shift cases. A good feature set does not guarantee a good readout. |
| Compression | Does the reduced set preserve the useful distinction? | Fidelity can fail out of sample; high fidelity can also preserve an arbitrary or scientifically irrelevant teacher. |
| Acceptance | Is a split supported at all? | A stable partition of a single population is possible. Independence rejection and density-model fit improvements are not generic cluster-existence tests. |
| Evaluation | Are the comparisons and sample units honest? | Metric-space mismatch, oracle stopping/splitter choice, mouse replicates, development reuse and changing result files all mattered. |

## Pivotal changes in thinking

**From one score to several decisions.** Separation, complexity, recurrence, cluster existence and scientific usefulness are different properties. A single normalized sum does not make them interchangeable. Use separate metrics and a declared tradeoff or constraint.

**From blaming EA to inspecting the exact objective and search budget.** Early operators were poor, but fixing them did not establish general advantage. A search cannot be expected to recover the researcher's preferred target when the reward favors something else. Fair baselines need equal evaluation budgets, honest initialization costs and the same objective.

**From pair-ranking success to genuine discovery.** Exhaustive pair evaluation showed useful ranking signals on several synthetic shapes. It did not answer how to find larger interacting sets. Oracle seeds and label-assisted upper bounds remain diagnostics, not deployable algorithms.

**From low-dimensional pictures to original-feature inputs.** A two-dimensional projection can depend on many original variables and can have a very complex boundary. Count original coordinates, rule complexity and computational input requirements separately.

**From post-hoc explanations to native assignment rules.** The radial family was attractive because the final equation exactly describes the prediction. The cost was a restricted geometry. For other shapes, accepting a surrogate with measured disagreement may be more useful than forcing a wrong simple shape.

**From null calibration to honest scope.** Independent-column scrambling addresses feature dependence. It preserves singleton distributions and rejects some one-population alternatives. Cross-dimensional normalization is established prior art and does not solve adaptive multiple testing or semantics.

**From endless diagnosis to a finite development sequence.** The October plan allowed one targeted ablation and one frozen replication/stress batch. Those are complete. The next useful work is application/comparator evidence or a justified pivot, not an automatic larger radial sweep.

**From keeping the original architecture to preserving the actual goal.** The user wants meaningful, checkable feature sets and a defensible contribution. Neither EA nor topology, a tree, cytometry or neural networks is inherently required. Preserve successful components and negative evidence without allowing sunk effort to dictate the thesis.

## Important tradeoffs

- Two/three original features are easy to plot, but a larger set may support a substantially better assignment. The user explicitly allows this.
- A fixed feature set is easy to audit at prediction time. Per-sample or per-cluster sets can be smaller locally, but the routing mechanism may require additional measurements. Count every input actually consulted.
- Sparse prediction of a fixed clustering is easier to validate than jointly learning the partition and feature set. Joint optimization needs a demonstrated benefit over that simple reduction.
- Flexible neural/graph models may model more shapes, but reconstruction can retain nuisance variation and self-training can reinforce an initially wrong partition. These are risks to measure, not reasons to ban neural methods.
- Small feature sets may be non-unique because correlated measurements are interchangeable. Exact planted-support recovery is appropriate on controlled synthetics but is not a complete definition of biological correctness.
- Independent-subject evaluation is stronger than random-row resampling for repeated observations. It also reduces effective sample size and can expose uncertainty hidden by many rows.
- Expert constraints can specify intended meaning. They change the problem to weak/semi-supervised clustering and require matched-information baselines.
- A stable batch effect can be reproducible and scientifically irrelevant. A useful rare population can be obscured by average ARI or consensus. Report per-population outcomes.
- A readable interface can help exploration; it does not replace a method evaluation. Repeated expert choices using held-out labels make subsequent outcomes exploratory.

## What remains open

1. Which real scientific question and sample unit should anchor the thesis?
2. Which existing comparator already comes closest to the practical goal?
3. Can compact original-feature inputs preserve its useful assignments on independent subjects?
4. If not, is the limiting mechanism feature selection, geometry, target ambiguity, scarce data, or transfer?
5. What precise new mechanism improves that limitation beyond existing sparse, neural, explanation, consensus and acquisition methods?
6. Is an explicit rule essential for every prediction, or is a compact-input model with measured interpretation sufficient for the revised proposal?
7. What evidence supports deciding not to split or not to assign a point? Current flags are not calibrated guarantees.
8. How should a root result extend to a hierarchy without error accumulation and changing sample sizes invalidating its evidence?

## Novelty boundaries and literature map

The package includes the complete dated literature reviews and an automatically extracted URL index. These were targeted reviews, not proof that all relevant work has been found; the links were not all rechecked during packaging.

- Sparse clustering and DUFS: small original-feature selection without enumeration already exists.
- GroupFS: feature-group discovery and selection already exists; its feature embedding is not the sample projection used in our prototype.
- IDC: deep clustering with sample/cluster feature explanations already exists.
- SpEx, polyhedral descriptions, Cluster-Explorer, CCAST, ConvexGating: explaining supplied clusterings or converting them into readable rules is already well developed.
- SCMER/PERSIST: preserving nonlinear geometry and transferring selected features are not standalone novelty claims.
- Consensus-guided feature selection: multiple reference partitions do not automatically create novelty.
- SUWR and active feature acquisition: preventing hidden use of unreported inputs is already a developed topic.
- Pairwise constrained sparse k-means and active constrained clustering: adding a few labels or queries is not itself new.
- Post-selection inference and cluster-tree inference: a guarantee for a fixed representation does not automatically apply after adaptive feature search.

A defensible novelty claim requires a concrete objective, selection procedure, acquisition rule, inference result or carefully established application contribution, plus the nearest appropriate comparators. A pipeline made of established pieces may be useful, but usefulness and methodological originality need separate evidence.
