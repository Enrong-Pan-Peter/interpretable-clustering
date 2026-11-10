# How the project has evolved from the one-page proposal

Material passport: independent read-only proposal/code/literature review, 2026-10-04. Source proposal: `C:/Users/Peter/Downloads/Enrong_CISC500_Proposal.pdf`, one page, titled **Interpretable Subspace Clustering for Biomedical Data**. The complete page was extracted with pypdf; its headings supply the locators below. The PDF was preserved. Current-project evidence comes from the research modules and the September 30 assessment/interpretability audits, including their reported October 1 fixed-panel readout diagnostic. No new experiments were run for this review. Literature checks use the primary sources linked below and are targeted, not a systematic search establishing absence of competitors.

## The central aim survives

The proposal's **Background**, **Research question** and **Evaluation** concern unlabeled clustering supported by a small, understandable set of measured variables, with groupings and markers that can be checked against domain knowledge. That remains the project. Exploring evolutionary search, sparse weighting, kernels and constrained projections changes the mechanism, not that aim. None of those particular optimizers is required by the proposal.

The main scientific change is that one optimized score has become several decisions that need separate evidence. Current results distinguish finding a promising panel, choosing an assignment model, shortening its rule, checking reproducibility, and deciding whether to split at all. This is a defensible answer to the proposal's question about conflicting quality and interpretability objectives. Its **Deliverable** already anticipates showing alternatives to a domain expert instead of silently deciding every tradeoff with one number.

The current mean-shift result is useful but narrower than the thesis deliverable: rank-preserved global search recovers 11/12, 12/12 and 11/12 planted features among 200 columns, using a 16-feature cap. Applying the same centroid readout to those supports gives reported test ARIs around .704, .738 and .756. This supports continuing a panel-discovery component. It is not a completed biomedical hierarchy, a minimal-panel result, or evidence that the method handles general nonconvex shapes.

## Promise-by-promise comparison

| Proposal locator | Intended outcome | Current evidence and remaining gap |
|---|---|---|
| **Background**: gates in named marker coordinates | A person can see what defines a population | Original-feature panels are retained; centroid readouts have exact rules in original measurement units. A 16-term linear boundary is still more demanding than a two-marker gate. A graph embedding is not the measured panel's geometry. |
| **Research question**: separation, compactness and resampling | Useful, small, reproducible panels | The project now demonstrates why these properties need separate assessment. Support recall, rule fidelity, assignment ARI and split evidence are different quantities. Good recall alone did not protect moons from nuisance loading or worse assignment. |
| **Proposed work**: recursive tree | Different panels at different nodes, forming one readable hierarchy | Legacy `atomicplus/tree.py` implements recursion and gates. The verified new kernel/rank/readout branch evaluates binary root problems and has not integrated those components into a validated recursive predictor. Say “not integrated/validated,” not “no tree code exists.” |
| **Proposed work**: panel size decided by the method | A justified number of variables, rather than a user-selected answer | Latest results use a cap of 16 and retain 16 features. Earlier stopping/compression code exists; `replicated_panels.py` can validate frozen prefixes for fidelity. This does not yet demonstrate automatic compactness for the successful kernel-generated panels, much less a globally minimal panel. |
| **Proposed work**: decline an unconvincing split | A node can remain a leaf for an evidential reason | The current research branch forces two groups. Minimum child-size and numerical-validity checks do not establish multiple populations. Legacy stability/permutation gates exist, but the observed stable Gaussian splits prevent treating those gates as a solved acceptance rule. |
| **Evaluation**: reference populations and expert markers | Biological usefulness of the selected panel itself | Earlier Levine/METABRIC work exists, but the latest successful result is synthetic. Planted shuffled feature recovery is not a domain marker check. A new method needs documented marker identities, population-level interpretation, and held-out subjects/batches where possible. |
| **Evaluation**: resampling and comparisons | Reliable rediscovery and fair baselines | Earlier replication machinery exists. The two completed rank runs repeat the same data/seeds and therefore establish repeatable execution, not independent rediscovery. The complete proposed method has not yet been compared with the full intended cytometry/tree baseline set. |
| **Deliverable**: interactive candidate comparison | Load data, inspect alternative panels/splits, choose with domain knowledge | Saved reports, models, predictions and rules support such a product. This review did not find a demonstrated interactive interface integrated with the successful research branch. An interface alone would not validate its panels or splits. |
| **Timeline**: tree first, broader validation/interface later | A complete end-to-end method | Work has shifted toward diagnosing single-node failures before growing a tree. That is reasonable risk reduction, but the schedule should explicitly acknowledge integration, subject-level evaluation and interface work still ahead. |

The original emphasis on panels small enough for a direct plot and the user's present requirement to work beyond three variables introduce a real design choice. Preserve named original features and verifiable assignment as requirements; treat one- or two-variable visual gates as one explanation form, not a limit on every useful panel. A larger panel must earn its complexity through measurable utility and a readable rule. Two plotted projection coordinates with hidden dependence on many measurements do not automatically satisfy the original gating promise.

## The literature-gap paragraph needs correction

The proposal's **The gap** ends with an unrestricted claim that no existing method discovers an unlabeled small-variable hierarchy. That wording is not established by the cited comparisons and should be removed. The following distinctions matter.

| Primary source and locator | What it supports | Consequence for this proposal |
|---|---|---|
| [CCAST, Anchang et al. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4117418/), **Abstract** and method overview | Clustering is followed by recursive classification to obtain a gating tree. | A univariate explanation tree does not imply the preceding cluster discovery only considers one variable at a time. Separate limits of discovering groups from limits of explaining them. |
| [cytometree, Commenges et al. 2018](https://onlinelibrary.wiley.com/doi/abs/10.1002/cyto.a.23601), **Methods / Principle** | At each node, marker-wise one- versus two-component models determine a split and a threshold controls stopping. | A single-marker limitation is a defensible statement about this particular node criterion. Unlabeled recursive trees and a stop option are already established components. |
| [UNITO, 2025](https://www.nature.com/articles/s41467-025-56622-2), **Cytometric gating structure** and **UNITO training and cell membership prediction** | Separately trained bivariate segmentation gates follow predefined marker-pair coordinates and a predefined hierarchy, using manual gate training targets. | It is a relevant supervised gate-transfer comparison, not evidence that all other methods lack multivariate discovery. Its scope differs from discovering a new split from unlabeled measurements. |
| [Minimum Spectral Connectivity Projection Pursuit](https://arxiv.org/abs/1509.01546), **Abstract** | Learns low-dimensional projections by spectral separation and combines binary partitions in a divisive hierarchy. | Unsupervised projection learning plus a spectral hierarchy is not itself a new contribution. Sparse original-feature support and verifiable explanations need their own comparison. |
| [ConvexGating, 18 September 2026](https://www.nature.com/articles/s41467-026-77360-z), **ConvexGating algorithm**, **Step 1** | Selects marker pairs and learns polygon gating hierarchies for supplied cluster assignments. | A close comparator: distinguish partition discovery from gate reconstruction, without assuming that distinction establishes novelty. |

Here, “without labels” needs care: cluster-derived targets need not be human annotations. Specify whether the contribution concerns discovering a partition, explaining one, or constraining both. Broadly dismissing reconstruction methods as supervised would obscure relevant comparisons.

The proposal's claim that a single-variable tree cannot find any structure visible only jointly is also too broad. It is a serious limitation for a purely marginal node-search criterion in some distributions; it is not a theorem covering multivariate clustering followed by tree approximation or all sequences of univariate splits.

## A defensible updated research question

One suitable replacement is:

> Can unlabeled node-level candidate discovery, explicit assignment models and independent verification produce a hierarchy whose feature panels are compact, reproducible and biologically useful, while making unsupported splits and inadequate explanations visible?

This is a research question, not a claim that the combination is unprecedented. A possible contribution would be a carefully tested method connecting these pieces under stated assumptions, particularly if it provides benefits over both direct tree clustering and clustering-followed-by-gate reconstruction. Establish that through comparison rather than a universal literature-negative sentence.

## What “interpretable” should require before the tree is extended

At a node, the stored result should make five things separately inspectable: the selected original measurements; the exact native assignment rule and preprocessing; the shape assumption or displayed measurement-space boundary; evidence that smaller panels retain adequate utility/fidelity; and the reason to split or stop. A surrogate tree should carry its measured disagreement, not silently replace the actual classifier. Exactness, compactness, biological validity and uncertainty remain separate properties.

The next plan should connect the surviving panel generator to those requirements before claiming that the old recursive wrapper completes the method. Recursive use changes sample sizes, selection and error accumulation; a root-only result does not validate every descendant. Repeated cell sampling within one donor also does not establish transfer across patients or batches.

The interactive interface can then present these concrete alternatives and their evidence. Human choices should be logged as exploratory choices; allowing a user to inspect labels or repeatedly inspect held-out outcomes cannot leave the result described as untouched confirmation.

The project has not departed from the proposal. It has learned that the proposed objective needs a clearer contract and that finding a panel is only one component of the interpretable clustering method. The remaining work should restore the full promise around that surviving component rather than equating the latest kernel score or a readable plot with completion.
