# Small-panel interpretable clustering: comparator note

Prepared 2026-10-06. Focused primary-source scan; this is a comparison shortlist, not a systematic review or a claim that any method is universally best. No software was installed and no experiments were run for this note.

The requirement used here is **prefer two or three original features per displayed decision, but permit larger panels with explicit rules**. The primary application is cytometry; the broader high-dimensional feature-selection problem remains a separate evaluation setting.

## What counts as the same task

A tree's shape alone does not determine its learning problem:

| Training setup | Meaning | Essential evaluation |
|---|---|---|
| Tree trained on expert cell-type labels | Supervised classification or automated gating | Generalization to held-out donors and batches; it cannot establish label-free discovery |
| Tree trained on a clustering algorithm's assignments | Reference-dependent explanation or clustering approximation | Fidelity to the reference **and** independent biological validity; high fidelity can faithfully reproduce a poor reference |
| Tree and clusters learned from unlabeled measurements | Native interpretable clustering | Quality, reproducibility, null behavior, and complexity of the discovered partition |
| Feature selector followed by a clusterer | An unsupervised selection pipeline | Selected-panel sufficiency plus the downstream clusterer's quality; selection alone does not supply a gate hierarchy |

Terminology varies: an approximation tree can itself be an intrinsically interpretable *replacement model*, even though it was fitted after another clustering. Report whether the original assignments are retained, replaced, or jointly changed instead of relying on the phrase “post hoc.”

## Six focused general comparators

Each row distinguishes external labels from algorithm-generated assignments. “One feature per node” does not mean one feature per cluster or per tree.

| Comparator and verified source | Input and labels | Feature budget and output | Why test it; limitations |
|---|---|---|---|
| **IMM / ExKMC** — Moshkovitz et al., ICML **2020**; Frost et al., **2020** preprint. [IMM](https://proceedings.mlr.press/v119/moshkovitz20a.html), [ExKMC](https://arxiv.org/abs/2006.02399), [authors' implementation](https://github.com/navefr/ExKMC) | Numeric measurements, a requested cluster count, and a reference k-means solution; no biological labels required. | Axis-aligned binary rules use one original feature per node. IMM uses k leaves; ExKMC permits k′ ≥ k leaves labeled with k clusters. There is no two/three-feature global panel constraint. | Practical reference-dependent tree baseline. Match leaf budgets and measure clustering cost plus held-out reference fidelity. Its objective inherits the reference geometry; simple rules are already part of its design. |
| **Sparse oblique joint clustering / TAO** — Gabidolla & Carreira-Perpiñán, KDD **2022**. [Paper](https://faculty.ucmerced.edu/mcarreira-perpinan/papers/kdd22.pdf), [DOI](https://doi.org/10.1145/3534678.3539361) | Measurements and a clustering cost; demonstrated with Euclidean and spherical k-means. Assignments and tree are coadapted without biological labels. | Original-feature linear inequalities; an L1 penalty sparsifies each node and can prune nodes. Sparsity is tunable, not an exact two/three-feature cap. Multiple leaves can represent one cluster. | Closest direct comparator for a sparse oblique hierarchy. Compare equal complexity and the entire quality–complexity curve. “Optimal” in the title must not be presented as a guarantee of finding the global optimum. This scan did not validate a runnable authors' package. |
| **Kauri** — Ohl et al., **2024**, retrieved as an arXiv preprint. [Paper](https://arxiv.org/pdf/2402.12232), [record](https://arxiv.org/abs/2402.12232) | Measurements and a kernel; no reference partition or external labels required. Greedily optimizes a kernel k-means criterion. | One original feature per split. Separate maxima for clusters and leaves; leaves may share cluster labels. Stops when further gains are unavailable. | Direct native-tree baseline for nonlinear cluster geometry. Its paper reports generally similar linear-kernel performance to competitors, with advantages depending on the kernel. The full kernel matrix makes large-cell-count memory a test item. Pseudocode is available; this scan did not verify an authors' package or later journal publication. |
| **SpEx** — Argov & Wagner, NeurIPS **2025**. [Proceedings](https://papers.neurips.cc/paper_files/paper/2025/hash/20aa64395b2d43d2a32825660f566f6c-Abstract-Conference.html), [paper](https://papers.neurips.cc/paper_files/paper/2025/file/20aa64395b2d43d2a32825660f566f6c-Paper-Conference.pdf), [authors' code](https://github.com/talargv/SpEx) | SpEx-Clique accepts arbitrary reference assignments; SpEx-kNN builds from the data graph without a reference clustering. Neither needs expert labels. | Coordinate-threshold binary tree with a requested leaf count; one feature per node, no global marker-count constraint. | Strong modern graph-based comparator, in both modes. Check sensitivity to nuisance features and graph construction. The paper acknowledges objective-specific methods can be better for k-means; reported advantages are not universal dominance. |
| **CLTree** — Liu, Xia & Yu, CIKM **2000**. [DOI](https://doi.org/10.1145/354756.354775), [author-uploaded report](https://www.researchgate.net/publication/2805324_Clustering_Through_Decision_Tree_Construction) | Unlabeled observations. Contrasts observed data with virtual background points; the resulting artificial classes are not biological supervision. | Single-feature splits identify dense and sparse regions. Pruning yields hyperrectangular cluster descriptions, potentially using different feature subsets. No explicit two/three-feature cap. | Historical native-tree and subspace comparator: interpretable cluster discovery is not new. Test on axis-aligned subspace clusters and noise, including pruning sensitivity. A maintained reference implementation was not verified, so use as conceptual prior art unless reproduction is independently validated. |
| **Sparse k-means** — Witten & Tibshirani, JASA **2010**. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2930825/), [authors' sparcl package](https://stat.ethz.ch/CRAN/web/packages/sparcl/index.html) | Unlabeled measurements and k; alternates feature weighting and clustering. | A global nonnegative feature-weight vector with L1/L2 constraints; yields clusters and selected original features, not a rule tree. L1 tuning does not directly specify an exact feature count. | Essential baseline for “small original panel discovers meaningful clusters,” particularly mean-shift data. Compare achieved nonzero-feature counts and held-out assignments. It does not establish node-specific panels, visible two-dimensional gates, or a biological hierarchy. |

These six were selected for methodological proximity, including strong alternatives, rather than because they are expected to lose. Published benchmark rankings are not comparable across different datasets, feature representations, budgets, and tuning procedures.

## Adjacent work that changes the interpretation

**Nonlinear reference explanations already exist.** Fleissner, Vankadara & Ghoshdastidar's [*Explaining Kernel Clustering via Decision Trees*](https://openreview.net/pdf?id=FAGtjl7HOw), ICLR **2024**, extends tree approximation to kernel k-means. For its supported feature constructions, splits can be translated into one-feature intervals in the original space. It belongs in a nonlinear ablation if computationally practical; “kernel geometry with original-feature explanations” alone is not a novelty claim.

**Native trees predate the modern explainable-k-means literature.** Fraiman, Ghattas & Svarc's [*Interpretable Clustering using Unsupervised Binary Trees*](https://arxiv.org/abs/1103.5339), preprint **2011**, uses recursive heterogeneity reduction, pruning, and joining. CLTree is not the only historical example. Conversely, the term “predictive clustering tree” often includes supervised tasks; it should not be treated as synonymous with unsupervised discovery.

**Cytometry-facing discovery and visible gates are distinct comparisons.** [SCAMP](https://arxiv.org/abs/1807.10328) (Greene, Finak & Gottardo, **2018** preprint) searches for candidate populations obeying coordinate-wise shape constraints, then selects them using preference scores and supplies annotations. Cluster count is not an input parameter, but this is not a prescribed global two/three-marker panel. The [authors' repository](https://github.com/RGLab/scamp) distinguishes the manuscript-reproduction branch from the branch used with FAUST. This is relevant exploratory prior art, with source/version choice needing care.

[UNITO](https://www.nature.com/articles/s41467-025-56622-2) (Chen et al., Nature Communications **2025**) produces hierarchical bivariate gates through image segmentation learned from annotated gating examples. It is an excellent comparison for gate usability and transfer on a known panel, but a supervised gating comparator, not evidence of unsupervised novel-population discovery. Its authors explicitly distinguish production annotation from exploratory clustering. Do not compare against it under the same “no labels” claim while allowing labeled training only for one method.

**Feature selectors are component controls.** [DUFS](https://proceedings.neurips.cc/paper/2021/hash/0bc10d8a74dbafbf242e30433e83aa56-Abstract.html), NeurIPS **2021**, learns feature gates while recomputing graph structure on gated inputs; its algorithm can return a requested top-s feature set. [GroupFS](https://ojs.aaai.org/index.php/AAAI/article/view/39521), AAAI **2026** (2025 preprint), jointly learns latent feature groups and their selection without fixed group definitions or labels. Neither source establishes a cytometry gating-tree gold standard. Pair either selector with an explicitly named downstream clusterer and charge its full selection and tuning cost.

**Short trees have genuine limits.** Deng et al.'s [depth-reduction result](https://arxiv.org/abs/2305.02850), **2023** preprint / [Information and Computation **2026**](https://doi.org/10.1016/j.ic.2026.105430), constructs planar cases where reducing an axis-aligned explanation's depth below k−1 yields unbounded relative clustering cost. This is a worst-case result about that model, not a prediction of cytometry performance or a theorem covering every sparse oblique tree. It supports evaluating a tradeoff rather than promising universally tiny rules without loss.

## Budgets to report separately

These are proposed reporting definitions, not claims from a comparator paper:

1. **Node panel:** number of original measurements actually used by a split, including every term of a linear inequality or nonlinear rule.
2. **Path panel:** union of measurements used from root to leaf; also report path length and repeated tests.
3. **Whole-tree panel:** union of measurements used anywhere, which determines the assay panel if every sample must support every path.
4. **Rule complexity:** number of thresholds, coefficients, intervals, or polygon vertices, plus leaves per cluster. A three-feature rule can still be difficult to understand.
5. **Discovery inputs:** measurements used to choose the tree, reference clustering, graph, preprocessing, and tuning. A small inference panel does not imply a small discovery panel.

For a binary tree with L leaves and at most q features at each internal node, the union contains at most min(p, q(L−1)) features; a path of depth h uses at most min(p, qh). These are counting bounds, not actual achieved panel sizes. Axis-aligned trees use q=1 but may require many leaves to represent diagonal boundaries.

Interpret the user's two/three-feature preference as an explanation target: show the complete two/three-dimensional decision where possible. If a larger rule is selected, expose every measurement, coefficient/threshold and the reason for expansion. Projecting a larger rule onto two axes without showing the hidden terms is not a faithful two-feature explanation.

## Usable comparison plan — proposed, not executed

| Test | Concrete comparison | What would be learned |
|---|---|---|
| Global-panel sufficiency | Existing method versus sparse k-means and DUFS/GroupFS + the same downstream clusterer at achieved budgets 2, 3, 5, 8, 16 | Whether local gains require a tree at all; avoid attributing a better clusterer to feature selection |
| Rule discovery | Native proposed tree versus sparse oblique TAO, Kauri, and SpEx-kNN; retain CLTree/CUBT as historical controls when reproducible | Whether the new split/search objective adds value beyond established native trees |
| Explanation only | Freeze a common reference; compare CART, IMM/ExKMC when applicable, and SpEx-Clique at equal leaf/depth budgets | Whether improvement is explanation fidelity rather than better discovery; evaluate the reference itself separately |
| Geometry and noise | Axis-aligned means, rotated sparse boundaries, curved populations, correlated redundant markers, nuisance features and outliers | Which assumptions drive wins and failures; include cases favorable to each comparator |
| Cytometry transfer | Freeze preprocessing and fitted rules on training donors; apply to untouched donors/batches; match populations without using test labels to tune | Donor-level reproducibility, rare-population recall and precision, frequency error, and external biological concordance |
| Stability and nulls | Donor/bootstrap refits, seed variation, null datasets and marker perturbations | Stability of memberships **and** selected rules; propensity to invent unsupported splits |
| Scale | Increase cells and features separately; record peak memory, total tuning time and prediction time | Whether graph/kernel discovery is viable at cytometry scale, even if final prediction is cheap |

Use two prespecified tracks: a strict q≤3 node ablation and the preferred-small/adaptive-larger version. For the latter, define the maximum allowed size, minimum population support and expansion/stopping rule before inspecting final evaluation labels. Select larger rules only with a reproducible improvement under the declared selection procedure; report the fraction of nodes that expand and the quality lost when they are restricted. A complexity penalty or Pareto curve is clearer than quietly changing the budget.

Report independent biological agreement alongside unsupervised objectives and reference fidelity. Expert labels are a useful evaluation reference, not perfect truth about undiscovered biology. For rare populations, aggregate ARI can hide failure. Split data by donor or batch before fitting transformations, feature selection, cluster discovery or hyperparameters; cell-level random splits alone do not assess cross-donor transfer.

## What a defensible contribution could be

The published work already covers tree-shaped clustering, sparse oblique rules, original-feature explanations, joint clustering/tree fitting, and graph-based native trees. The proposed system needs a more specific claim: for example, **more stable biologically useful populations with a smaller achieved path/assay panel, a transparent rule for exceeding the two/three-feature preference, or an efficient search that preserves quality at larger scales**. Those are candidate contributions to test, not findings established here.

The existing local rank-fixed global-projection result selected 16 features, recovered 11/12, 12/12 and 11/12 planted features among 200 across three seeds, and obtained mean centroid ARI about 0.733 on synthetic mean shifts. That result is relevant to global selection only. It does not yet establish a native hierarchical method, two/three-feature decisions, held-out biomedical validity, or superiority to the comparators above. The numerical result is documented in `rank-preservation-assessment-2026-09-30.md` and was not rerun in this literature subtask.

## Search and evidence limits

Search performed 2026-10-06 using primary paper titles and combinations of explainable/interpretable clustering, sparse/oblique/unsupervised trees, kernel trees, feature selection and cytometry gating; forward searches explicitly included 2025–2026 and a 2026-10-06 cutoff. Core sources were conference proceedings, author PDFs, original preprints, the original JASA manuscript, author code, and the author-uploaded CLTree report. Search snippets were used for discovery; technical descriptions were checked against accessible original text. CLTree's direct PDF retrieval failed, so its author-uploaded original report text was used. Kauri and SCAMP publication upgrades were not verified. No systematic database coverage, citation-count completeness or “latest best method” certification is implied.

Critical checks: no labels were silently reclassified as unsupervised; regularization was not called an exact feature cap; native clustering was not conflated with reference fidelity; favorable author benchmarks were not promoted to universal superiority; the comparison includes methods that already provide interpretability.
