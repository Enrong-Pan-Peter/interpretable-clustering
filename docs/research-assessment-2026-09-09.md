# ATOMIC: assessment and a concrete research direction

Prepared 9 September 2026 from the original paper, implementation, experiment records, saved results, three independent agent reviews, and a targeted search of primary research sources.

## What I understand you want

You want a method that discovers a small set of useful feature panels, with evidence that those panels reveal meaningful clusters. Different clusters or levels of a hierarchy may need different panels. Cluster shapes and readable assignment rules would make the result stronger. The method must discover these panels without exhaustive subset enumeration, work beyond planted two-dimensional pictures, and contribute something identifiable beyond assembling an interface.

That is a coherent research objective. The strongest remaining idea in ATOMIC is **local, verifiable feature panels for clustering**. Evolutionary computation is one possible search tool. A recursive tree is one possible organization of the results. Neither needs to define the contribution before the discovery mechanism works.

The current evidence supports useful pieces of that objective, but does not establish a reliable end-to-end method. Several apparent limits on the project also come from experiments that do not isolate the cause they claim to isolate.

## What the project actually contains

The progression is recognizable:

1. Original ATOMIC searches Boolean feature masks for a kNN graph with two connected components, with novelty search and local competition.
2. ATOMIC+ replaces the flat component-count reward with an MST persistence statistic and adds recursive splitting and evaluation machinery.
3. Graph-cut and density-style scores improve panel ranking on the synthetic suite, particularly under exhaustive pair evaluation.
4. Per-panel column-permutation calibration attempts to compare panel sizes and stop growth.
5. Pair seeding, forward growth, combined stopping rules, and a cytometry tree attempt to turn ranking into a deployable discovery procedure.

These are not yet one consistent implementation. `atomicplus/tree.py` still forces persistence fitness, whereas the newer tree is implemented separately in `scripts/run_levine_tree.py`. Scores, splitters, and validation protocols also differ across scripts.

The corrected synthetic results are real evidence of an effective ranking signal in the tested regime. In `docs/CORRECTIONS.md`, exhaustive hybrid selection finds the true pair in 90–100% of repaired moons cases across p=12/20/40, and similarly performs strongly on circles, jain, and spiral. This establishes panel ranking on that generator. It does not establish search efficiency, recovery of unknown larger panels, or transfer to realistic nuisance structure.

## Findings that change the diagnosis

### 1. The latest tree uses the evaluation labels to decide when to stop

`scripts/run_levine_tree.py:257–269` computes the populations present using `y`, then stops if fewer than two remain. `scripts/run_stability.py` contains the same kind of stop. Consequently, the cytometry tree is partly oracle stopped. Its pure leaves cannot validate unsupervised abstention.

A lightweight control-flow diagnostic extracted the actual function: holding the same 100-by-2 feature matrix fixed, constant labels caused a `pure` leaf without calling search; balanced labels caused search to run. This isolates the label dependence without rerunning the costly clustering procedure.

The label-based capped sampling is disclosed in the script and can be useful for a diagnostic. It is a separate issue from labels determining fitted tree structure. Both must be removed from an ordinary unlabeled deployment evaluation. Labels may still be used afterward to assess the result.

### 2. Per-node purity is not final clustering quality

Reconstructing leaf-by-population contingency tables from the saved JSON outputs gives the following descriptive, in-sample results. These are **new calculations on existing outputs**, not new clustering runs:

| Saved configuration | Mean node purity | Final leaf-partition ARI |
|---|---:|---:|
| Graph-cut, cap60, maximum panel size 2, seed 0 | 0.980 | 0.638 |
| Density, cap60, maximum panel size 4, seed 0 | 0.982 | 0.167 |
| Graph-cut, cap60, maximum panel size 4, seed 0 | 0.877 | 0.761 |
| Combined, cap60, maximum panel size 4, seed 0 | 0.909 | 0.799 |

The density tree keeps populations together at many individual splits but leaves distinct populations merged. A purity measure rewards that behavior without requiring the tree to separate the populations. Conversely, a finer tree can have lower average node purity and higher final ARI. The builders allow label-based stopping, whose realized effect varies by run: cap60 graph-cut with panel size 2 and seed 0 records no pure leaves, whereas the density and combined runs do. These numbers cannot be treated as a fair ranking of deployable algorithms.

The audit also found sensitivity to sampling: graph-cut with panel size 2 has final ARI about 0.398 at cap120. A proportional-sampling run reaches ARI about 0.899 while its mean best-cluster F1 across the 14 populations is about 0.529. Report population-level recovery alongside global ARI; rare populations can be poorly recovered despite a strong aggregate score.

Reproduction: `scripts/audit_saved_tree_results.py`; output: `results/audit_saved_tree_results_2026-09-09.json`.

### 3. The score used to test the EA differs from the successful hybrid

`scripts/run_fitness.py:77–80` combines candidate-standardized terms, `z(graphcut) + z(density)`. `scripts/run_ea_newfit.py:47–54` instead uses the raw sum `_gc + _dn`, also comparing different panel sizes.

The EA, random search, and greedy search were compared internally on the same raw objective, so that comparison remains informative. It does not establish that the EA failed on the exact objective responsible for the successful enumeration result. This is a reason to narrow the conclusion, not a reason to assume the EA will win after correction.

Candidate-standardized scoring itself is unsuitable as a fixed adaptive-search objective: adding candidates changes each term's standard deviation and hence the relative weight of graph cut and density. Existing candidates can change order when unrelated candidates are added.

### 4. The hybrid scores two potentially different splits

In `atomicplus/evaluation/subspace_baselines.py:96–118`, density evaluates a persistence/MST partition. In lines 149–180, graph cut evaluates a spectral partition. Their sum can reward two different separations in the same panel. The tree then emits the partition from its configured splitter.

This is not an invalid panel-ranking heuristic by definition. It is, however, weak evidence about the quality of the particular split the method returns. A new objective should score the **same panel-and-partition pair** throughout, or explicitly justify why a panel-level ensemble predicts the chosen split's quality.

A related mathematical observation: when the largest positive MST edge is an admissible cut, the implemented density statistic is `1 - e2/e1`, a monotone transform of the original persistence ratio `e1/e2`. It differs more substantially when minimum-size constraints force the algorithm to cut a smaller edge while retaining a larger within-child edge. It is a DBCV-style surrogate, not the full DBCV index. This follows from the MST cut property and the code in `persistence.py:131–165`; zero-distance degeneracies require separate handling.

### 5. The permutation null does not mean “no clusters”

`atomicplus/evaluation/calibration.py:80–107` independently shuffles each column. This destroys dependence between columns while preserving their marginal distributions.

Two examples expose the mismatch:

- One correlated Gaussian population differs from the independent-column null, although it has one density mode. Rejecting independence need not justify a split.
- Two obvious clusters in one feature are unchanged by a permutation of its rows. Any row-order-invariant clustering statistic has an identical singleton permutation null. Singleton calibrated screening cannot detect that univariate cluster structure.

Standardizing by a null mean and standard deviation also does not make the statistic Gaussian. Selecting the maximum over panels, growth steps, seeds, and tree nodes makes a fixed `z > 2` threshold more problematic. Averaging two standardized terms does not restore a standard-normal scale: if their null correlation is rho, the average has variance `(1 + rho)/2` when each has unit variance.

The older `evaluation/significance.py` reruns the old search on each null realization. That is a useful existing example of accounting for search, but it is not the inference procedure used by the current calibrated tree. Neither approach turns an independence null into a general test of clustering.

### 6. Growth success and useful initialization are still being conflated

The saved shells experiment makes the distinction concrete. The true panel is `(0,1,2)`. The combined rule recovers it in the oracle-initialized result, but autonomous search returns `(0,1,2,8,11)` and reaches size 5. Graph-cut search returns a size-3 panel `(2,8,10)` containing the wrong features.

Sources: `results/stoprule_oracle_n300_B15_s0.csv` and `results/stoprule_search_n300_B15_s0.csv`. Correct panel size is not correct panel recovery. Stopping correctly after being given useful features is not discovering them.

The METABRIC “same data, same score, therefore search alone is responsible” interpretation is also not isolated: the raw pair sweep uses n=600 and spectral evaluation, whereas the documented search uses n=300 and `run_real_calibration.py:91–93` evaluates KMeans. The current `real_calibration.csv` contains mice and Levine rows, so it does not reproduce the historical METABRIC table. Search may be a major problem, but that comparison does not identify it as the sole cause.

### 7. Some supposed impossibility results overstate what is known

Madelon has 32 geometric clusters at hypercube vertices, assigned random binary class labels, plus redundant features. Recovering the supplied two classes is not the same task as recovering those geometric clusters. Low binary ARI is therefore not proof that no unsupervised geometric signal exists. This construction is documented by the [UCI dataset source](https://archive-beta.ics.uci.edu/dataset/171/madelon).

[Beretta's junta-distribution result](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.APPROX/RANDOM.2025.31) concerns distributions on a Boolean hypercube and reductions to noisy parity learning. It supports caution about unrestricted high-order interaction discovery. It is not a proof that this continuous dataset, this clustering target, or all alternative representations require enumeration.

Exp-023's label-based pair ceiling and basin fraction are diagnostic instruments, not checks available before unlabeled use. Also, if a useful basin fraction stayed at 3%, about 99 independent random draws would give 95% coverage regardless of p. The unresolved scaling question is how the basin fraction changes with dimensionality.

## The method I would investigate first

**Learn a sparse local geometry, then identify and verify the smallest panels that preserve its useful separation.**

This is a research candidate, not a claimed new algorithm or an established solution. It addresses your main objective directly: verifiable panels. An executable assignment rule is an additional output when it can represent the discovered shape faithfully.

### A. Replace Boolean panel enumeration with smooth, sparse proposals

Use continuous or stochastic feature gates to learn a weighted distance and its neighborhood structure together. Recompute the graph as the weights change. Begin with several initializations and sparsity levels; a graph built once in the full noisy space should not be the only starting point.

For example, weighted squared distance can be written as `d_w(i,k)^2 = sum_j w_j (x_ij - x_kj)^2`, with nonnegative feature weights, an explicit scale constraint, and a sparsity mechanism. Use a mathematically compatible penalty: an L1 penalty is constant if nonnegative weights are constrained to sum to one. Stochastic gates with an expected active-feature penalty are an established alternative.

The affinity must vary smoothly with distance. Simply replacing masks with real weights while keeping a binary kNN adjacency leaves broad flat regions whenever neighbor ordering does not change. Smooth kernels, refreshed candidate neighborhoods, or a differentiable graph surrogate are necessary for useful gradient-based proposals.

An anchor approximation can reduce a dense pairwise distance stage from O(n^2 p) to roughly O(n a p) per pass for a fixed number a of anchors. This is a computational design target, not a total-runtime guarantee: iterations, restarts, anchor quality, and rare-population coverage still matter.

The reason to test this is concrete: a tentative partition or neighborhood graph can provide conditional information about many features simultaneously. Current singleton/pair growth must first encounter a useful low-order seed. Joint learning may supply better feedback, although it can also reinforce an incorrect initial graph.

### B. Optimize partition quality and panel complexity as separate quantities

For a proposed panel S and partition P, evaluate topology/density evidence **for P in S**, plus reproducibility across independent samples. Search across panel complexity and keep the simplest candidate within a prespecified quality tolerance of a better-supported candidate.

A useful conceptual formulation is:

`minimize panel complexity, subject to reproducible separation and bounded loss of partition fidelity`.

This is preferable to hoping that one z-score will also discover the preferred panel size. More features may contain real information while adding little practical value. Parsimony is a chosen preference that needs an explicit tolerance or tradeoff.

The initial implementation should be modest: sparse graph proposals followed by backward deletion and small replacement moves. After every deletion, recompute the partition and compare it on validation rows. Delete a feature only when the measured loss stays within the chosen tolerance. The result is locally irreducible under those moves, not a proven globally smallest panel.

Highly correlated features can produce several equally useful panels. Report interchangeable alternatives when supported, rather than treating failure to recover one exact feature list as automatic failure. Distinguish a different panel explaining the same partition from a panel revealing a different valid partition.

### C. Verify panel usefulness with several independent questions

Each returned panel should carry an evidence record:

| Question | Evidence |
|---|---|
| Is there a separation in these features? | Density/topology analysis matched to a stated cluster definition; controls with a single correlated population |
| Does it recur? | Rediscovery on independent subjects or samples, compared on common evaluation points |
| Are all features needed? | Deletion and substitution tests with reclustering, reported with uncertainty |
| Does it match something meaningful? | Prespecified external labels, known markers, unused metadata, or independent expert assessment |
| Can new points be assigned? | A frozen assignment function and measured agreement with independently reproduced clusters |

These questions are not interchangeable. A simple rule can predict an arbitrary split of a Gaussian cloud very well. A stable batch effect can be biologically uninteresting. Agreement with labels derived from the same assay is useful validation of recovery, but weaker than independent scientific corroboration. PAM50 membership is not a complete answer key for a uniquely correct small gene panel.

### D. Keep topology, but use it for a precise target

A defensible target is reproducible high-density components separated by a density valley in a selected low-dimensional panel. This permits nonconvex clusters and relates directly to ATOMIC's origin.

Use discovery data for panel and partition search, separate validation data for choosing among proposals, and untouched confirmation data for final evidence. If using formal inference, freeze the proposed tree before confirmation and account for the tested nodes. Do not repeatedly adapt the tree to confirmation outcomes. The conditioning imposed by parent regions and density estimation near their boundaries also needs to be included in the procedure.

Confidence sets and pruning for density cluster trees already exist in [Kim et al., NeurIPS 2016](https://papers.neurips.cc/paper/6508-statistical-inference-for-cluster-trees.pdf). Extending appropriate guarantees to learned local panels would require actual statistical work. A fixed-panel theorem does not automatically validate adaptive feature search. For a first prototype, honest replication metrics are preferable to an unsupported probability-of-correctness claim.

At n=72 animals, a three-way split may be underpowered. Repeated grouped resampling can diagnose stability, while a formal confidence claim should wait for a design with adequate independent data.

### E. Add plots and assignment rules without forcing the wrong geometry

For panels with two or three features, show the data in those original coordinates. For larger panels, show carefully labeled projections and avoid claiming one picture captures the whole clustering geometry.

Fit a threshold, sparse oblique rule, quadratic rule, small rule set, or compact prototype model if useful. Report its fidelity and complexity. Concentric rings can have a short radius rule; a spiral may need a much more complex boundary despite using only two features. If the readable rule is poor, preserve the panel result and state the limitation. A black-box rule using only a few features is still a different level of interpretability from a short formula.

## Where novelty could be, and where it already is not

The literature is close enough that a generic “sparse graph plus tree” claim would be weak:

| Existing work | Relevant overlap | Implication for this project |
|---|---|---|
| [DUFS, NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/0bc10d8a74dbafbf242e30433e83aa56-Abstract.html) | Differentiable feature gates coupled to graph construction | Use as a proposal baseline; continuous feature selection alone is not new |
| [GroupFS, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/39521) | Joint discovery and selection of feature groups without labels | Learning interacting feature groups is already an active, directly relevant problem |
| [Minimum Spectral Connectivity Projection Pursuit](https://arxiv.org/abs/1509.01546) | Optimizing low-dimensional projections for graph separation, divisive hierarchies, microcluster approximation | Topology-oriented projection search and hierarchy are established |
| [SpEx, NeurIPS 2025](https://arxiv.org/abs/2511.00885) | Explanation trees from arbitrary clusterings or directly from the data | A spectral clustering explanation tree is not sufficient novelty |
| [Feature weighting in DBSCAN using reverse nearest neighbours, 2023](https://repository.essex.ac.uk/34583/1/1-s2.0-S0031320323000158-main.pdf) | Cluster-specific feature weights and density connectivity | Feature weighting plus nonconvex density clustering is not sufficient novelty |
| [SigDT, Information Sciences 2025](https://www.sciencedirect.com/science/article/abs/pii/S0020025524015020) | Significance-based interpretable categorical clustering, automatic stopping and cluster count | “No baseline can decline to split” is false; its categorical setting differs from ours |

The potential contribution is a **specific mechanism for finding compact local panels, preserving a demonstrated separation while reducing them, and verifying the resulting panels after search**. Its value must be demonstrated against straightforward combinations of the existing methods above. The search performed here does not establish that this mechanism is absent from all prior work.

A possible future claim, conditional on evidence, is: “The method discovers compact feature panels for local nonconvex clusters without exhaustive panel enumeration, and reports reproducibility and feature-removal evidence for each panel.” That would be a useful methods contribution even if some datasets favor an established full-space clusterer.

## Three experiments that would determine whether to pursue it

### First checkpoint: repair the measurement and isolate the objective

Create one label-free fitting interface: `fit(X)` produces panels, partitions, and optional assignment models; evaluation receives labels separately. Verify that changing y cannot change any fitted output with X and the seed fixed.

Use identical rows, preprocessing, candidate panels, and splitters to compare the current hybrid with scores computed on the same partition. Separate oracle panels, proposed panels, selected panels, and confirmed panels in the output. Include final ARI, population-level recovery, panel complexity, false splitting on negative controls, and wall time.

This step determines whether the current ranking signal can support a consistent objective. It should precede another large evolutionary sweep.

### Second checkpoint: determine whether a good panel can be compressed once a split is found

On Levine and one METABRIC contrast, generate a small set of partitions without labels using current sampling and established sparse graph proposals. Compare forward growth with backward panel reduction starting from the same candidates. Include oracle partitions only as clearly labeled diagnostic ceilings.

If compression reliably produces smaller panels with preserved held-out separation, but discovery seldom finds the starting partition, proposal generation is the main bottleneck. If compression fails even for useful unsupervised partitions, the desired small explanation may be absent or the fidelity criterion may be wrong.

This is a much more informative experiment than testing another optimizer on the same scalar fitness.

### Third checkpoint: test scalable discovery before adding recursion

Compare random masks, current seed-and-grow, DUFS-style proposals, and proposals plus reduction at matched wall time and with unique evaluations recorded. Use exhaustive search only as a diagnostic ceiling where feasible.

Include unknown true panel sizes 1, 2, 3, and 5; realistic correlated nuisance; disconnected and overlapping groups; rare groups; and one curved single-population negative control. Vary dimension and sample size separately. Use real-data cases during development, then reserve untouched cases for the final evaluation. Distinguish strict high-order interaction stress tests from typical recoverable problems.

For real data, aggregate mice at the animal level, use patients as independent METABRIC units, and disclose Levine's within-specimen limitations unless independent donor data are available. Fit preprocessing on discovery data. A label-selected biological contrast is a scoped benchmark, not a demonstration that the full unlabeled population was discovered automatically.

Continue to a recursive method only if the single-node prototype shows a useful quality-versus-cost tradeoff, retains useful three-or-more-feature panels, and avoids accepting arbitrary single-population splits as the search budget increases. If it fails, inspect candidate coverage, score ranking, compression loss, and confirmation power separately. Each failure points to a different repair.

## What I would do with evolutionary computation

I would pause generic Boolean-mask EA tuning. I would keep the existing implementations as baselines and reconsider evolutionary computation only after a representation and score provide usable partial feedback.

A meaningful later role is a population of distinct panel-and-partition solutions, with local sparse optimization inside each candidate and novelty measured by partition disagreement rather than Hamming distance alone. Another is evolving compact nonlinear assignment rules after useful panels exist. Both require an equal-cost random-plus-local-search baseline. Neither is automatically novel, and neither should be used to rescue an objective that does not recognize useful intermediate solutions.

## What this review delivered and did not establish

This review inspected the paper, corrected experimental history, current implementation, and saved results; reconstructed final clustering metrics from existing trees; checked the label-dependent stopping path; and verified close prior art through primary sources. It adds an independent saved-output audit and this assessment. It does not replace the existing method or silently revise historical experiment records.

No new end-to-end clustering benchmark or full test-suite run was performed. The available bundled Python has NumPy and pandas but lacks SciPy, scikit-learn, and pytest. The lightweight saved-output audit uses NumPy and does not need those packages. Proposed mechanisms and expected advantages above are hypotheses to test, not reported performance improvements.

My recommendation is to invest next in **a single-node prototype that learns sparse geometry and returns verifiable, reducible panels**, alongside a corrected evaluation harness. That offers a concrete route toward your intended method and gives early evidence about whether the proposed contribution is worth a full implementation.
