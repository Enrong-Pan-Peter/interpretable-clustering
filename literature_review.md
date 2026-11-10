# Literature Review — ATOMIC Follow-Up Project

**Topic:** Interpretable subspace clustering via evolutionary search over feature subsets, extended with a topological (persistence-based) separation objective and applied to biomedical patient stratification.

**Purpose of this document:** Map the direct prior art, record what each paper does and does *not* cover, and stake out the white space our follow-up paper occupies. Use this as the basis for the manuscript's *Related Work* section and to keep the novelty claim narrow and defensible.

> **⚠️ Plan updated 2026-07-06** (see `blind-spot-audit.md` for the authoritative decision log). Target = **GECCO 2027 full paper, methods-first**; biomedical validation (Phase 8) is deferred to a follow-on **journal** paper. The product is a **single recursive interpretable tree**; **diversity** is scoped as **same-membership alternative panels** per split. **Reproduce-first is dropped** — we re-implement ATOMIC and own it. The prior-art map below is unchanged and still governs the novelty fence.

**Legend for coverage of our planned ingredients:** ✅ present · ⚠️ partial / adjacent · ❌ absent

---

## Primary prior art (direct comparison)

| Paper | Year / Venue | What they covered / contributed | What's NOT in theirs but is in our plan |
|---|---|---|---|
| **ATOMIC** — Vandergrift & Hu, *ATOMIC: an Interpretable Clustering Method Based on Data Topology* | 2024 · GECCO '24 Companion (Melbourne) — 4-page short paper | Anchor paper. Evolutionary algorithm (NSLC + NSGA-II) that searches **feature subsets** ("topology warping") for a subset that splits the data into **two connected components** of a fixed-k̃ nearest-neighbour graph. Interpretability = the variables *responsible* for isolating a cluster (interpretable, not explainable, per Rudin). Bit-string genome; fitness `f = −(C−2)²`; novelty = Hamming sparseness, local competition = out-performance. Beats k-means/GMM/DBSCAN on silhouette & Davies–Bouldin on 7 UCI sets; reports % feature reduction as interpretability. | Fair evaluation (subspace parity, ARI/NMI vs ground truth, statistical tests); **continuous persistence fitness** replacing the flat integer count; robustness to single-linkage/outlier failure and to fixed-k̃; **multi-cluster composition** (recursive dendrogram with per-split feature sets); better operators; **scalability** to biomedical dimensionality; **out-of-sample rule**; **biomedical validation** (survival, subtype recovery, pathway enrichment, stability). |
| **ChameleoClust / ChameleoClust+** — Peignier, Rigotti & Beslon | 2015 · GECCO · *(journal: Computational Intelligence, Wiley, 2020)* | Evolutionary **subspace clustering** with an *evolvable, variable-length genome* (functional + non-functional elements, large rearrangements). Phenotype = core points placed in **distinct subspaces**; clusters formed by grouping data around core points. Detects varying numbers of clusters of differing dimensionality; minimal parameter tuning. Benchmarked on the standard subspace-clustering evaluation framework. **This is the closest *engine* prior art.** | Assigns points by **centroid/core-point proximity** (presumes locally convex structure) — we use **topological connectivity / persistence** to catch non-convex & chained separations. No interpretability framing, no causal variable→cluster claim, no comparison to explainable methods. No **diversity of competing explanations** (novelty search). No biomedical layer, survival, or deployable rule. |
| **KymeroClust** — Peignier (et al.) | 2017 · PhD thesis, INSA Lyon · *(applied in EvoMove, ECAL 2017)* | Leaner, faster successor to ChameleoClust using more abstract evolutionary mechanics; same core-point-in-subspace phenotype; sets core-point coordinates from data objects to approximate cluster **medians** (extends k-medians). Adapts cluster count + subspace dimensionality; suited to streaming/on-the-fly clustering. | Same gaps as ChameleoClust (median/centroid-based, not topological; no interpretability framing; no persistence; no diversity-of-explanations; no biomedical validation). Trades capability for speed → even further from a topology-rich interpretable method. |
| **Interpretable Clustering: A Survey** — Hu, Jiang, Dong, Liu & He | 2024 · arXiv:2409.00743 (preprint) | Master taxonomy of the field: **pre-clustering** (feature selection/extraction), **in-clustering** (interpretability embedded in the clustering process), **post-clustering** (explain a black box). Codifies "good interpretable clustering": *minimal* evidence per cluster + evidence *unique* to each cluster. Enumerates interpretable model families: decision tree, rules, prototype, convex-polyhedral, description. **ATOMIC is an "in-clustering" method by this taxonomy.** | It is a survey, not a competing method — but it shows our *goals* are the field's standard desiderata (so novelty can't live there) and our *interpretable-vs-explainable* pitch is the standard in- vs post-clustering distinction. Our differentiator is the **mechanism**: a topology/persistence-driven in-clustering model returning minimal *causal* feature sets + a *diversity* of them — a sparsely populated cell of their taxonomy. Use its reference list to pick the in-clustering baselines to benchmark against. |
| **Robust Topology-Based Algorithm for Gene Expression Profiling** — Seemann, Shulman & Gunaratne | 2012 · ISRN / International Scholarly Research Notices · DOI 10.5402/2012/381023 | **Closest *biomedical* prior art.** Persistent homology + statistical invariants on gene expression. Pre-selects a **compact, bimodally-expressed gene panel** (non-dimensionalized std-dev for bimodality + PH for coherent co-expression), then **partitions patients hierarchically** using 0-dim homology (connected components). Recovers **classical/mesenchymal/proneural GBM subtypes** from 202 TCGA tumors; finds neural subtype is fragmented. Derives a **59-gene subtype prediction model** (deployable classifier). | Uses **one global gene panel** pre-filtered up front and **does not search subspaces** — it does *not* tie a specific minimal feature set to a *specific* split. We discover **different, independent feature sets per cluster** via evolutionary search (per-split causal evidence). No evolutionary/multi-objective search; no **diversity of alternative stratifications**; PH used to *build* the panel & partition, **not as a continuous fitness a search optimizes**. Predates modern interpretable-clustering framing, fair protocols (ARI/NMI), and exKMC-style comparison. |

---

## Supporting / context references (cite for grounding, not head-to-head competitors)

| Paper | Year / Venue | Relevance |
|---|---|---|
| **ToMATo** — Chazal, Guibas, Oudot & Skraba, *Persistence-Based Clustering* | 2011/2013 · SoCG / JACM | Establishes **persistence as a cluster-separation criterion** (mode-seeking + persistence-guided merging). Our persistence fitness is an instantiation of this principle — cite to show it's borrowed, not invented. |
| **Accelerated Hierarchical Density Clustering (topological HDBSCAN)** — McInnes & Healy | 2017 · IEEE ICDMW | Frames HDBSCAN's objective as **maximizing total cluster persistence subject to non-overlap** — the conceptual parent of our MST-gap stability score, mutual-reachability distance, and min-cluster-size guard. |
| **Nicolau, Levine & Carlsson** — Topology-based identification of a breast-cancer subgroup | 2011 · PNAS | Second biomedical-TDA precedent (Mapper). Cite alongside Seemann so the biomedical-TDA prior art doesn't look cherry-picked. |
| **Multi-objective evolutionary subspace clustering** (e.g., Expert Systems w/ Applications 2020; Pattern Recognition Letters 2021) | 2019–2021 | Shows simultaneous optimization of compactness + per-cluster feature sets, incl. **overlapping** variants and gene-expression biclustering. Confirms "different features per cluster" is established; differentiate on topology + interpretability-first + diversity. |
| **PHEATPRUNER** — Pham et al. | 2024 | Interpretable **feature selection via persistent homology** (for time-series classification). Shows TDA-driven interpretable feature selection exists; we differ by doing it inside an evolutionary clustering search with per-split feature sets. |

---

## The white space we occupy (novelty fence)

Each neighbour supplies **one** ingredient:

- the **interpretability desiderata** (minimal, unique per-cluster evidence) → *Interpretable Clustering Survey, 2024*
- the **evolution of per-cluster feature subspaces** → *ChameleoClust / KymeroClust (Peignier)*
- a **persistence-based separation criterion** → *ToMATo / topological HDBSCAN*, and its **biomedical instantiation** → *Seemann 2012*

**To our knowledge, no single work combines all of:** (1) an evolutionary subspace search, (2) a *continuous topological separation objective* the search optimizes directly, (3) a *diversity* of minimal feature-defined separations (novelty search) — scoped as **same-membership alternative panels per split**, and (4) a *recursive interpretable hierarchy* with per-split feature sets and deployable out-of-sample rules, validated under a fair protocol. *(For GECCO 2027: (1)–(4) on synthetic + UCI; biomedical validation is the follow-on journal paper.)*

The contribution is this **synthesis**. The load-bearing novelty is the *topology-warping + diversity + interpretability-first* combination (distinguishes us from Peignier) and the *per-cluster independent feature sets discovered by search* (distinguishes us from Seemann). **Framing it as "a new interpretable clustering method" invites rejection on these references; framing it as this narrow synthesis is defensible.**

---

## Outline of our plan for this paper

Ordered by dependency (earlier items de-risk or enable later ones).

### Phase 0 — Re-implement and own the baseline (do first) — **UPDATED**
- **Reproduce-first dropped.** Matthew's baseline scorer, preprocessed CSVs, and exact config are unavailable, so bit-for-bit reproduction is impossible and low-value. Instead re-implement ATOMIC faithfully from the paper + `atomic.py`, fix/document the known bugs, and validate on tiny + known-answer synthetic inputs.
- Fully doable without Matthew: UCI data is public, preprocessing (2-NN impute + [0,1] scale) is specified in the paper, baselines/metrics are stock scikit-learn.
- The suspected metric-space confound can't be settled from the lost code — so we neutralize it by design in Phase 1 rather than proving it.

### Phase 1 — Fair evaluation protocol *(highest-stakes contribution)*
The headline ATOMIC result may be partly an artifact: silhouette/Davies–Bouldin are space-dependent, ATOMIC chooses its own (low-dim) space, and high-dim silhouette collapses via distance concentration. Fixes:
- **Subspace parity:** run k-means/GMM/DBSCAN on ATOMIC's selected feature subset so all methods are scored in the same space.
- **External metrics:** Adjusted Rand Index + NMI against ground-truth labels (space-invariant, ungameable).
- **Statistics:** ~30 stochastic runs, mean ± std; Friedman + Nemenyi post-hoc across datasets.

### Phase 2 — Continuous persistence-based fitness *(core mechanism upgrade)*
Replace flat `f = −(C−2)²` with a smooth separation score:
- In the selected subspace, build the **MST**; sort edge weights descending `e₁ ≥ e₂ ≥ …`; persistence of the 2-cluster split = **S = e₁ − e₂** (maximize). Generalizes to m clusters: `S = e_{m−1} − e_m`.
- Refinements: normalize (`e₁/e₂` or divide by median edge); use **mutual-reachability distance** `max(core_k(a), core_k(b), d(a,b))` for outlier-robustness; enforce a **minimum cluster size** so splits can't win by amputating an outlier.
- Net effect: gives the search a gradient, ranks ties at C=2, and earns the "topology" branding.

### Phase 3 — k̃ robustness
- Largely dissolved by Phase 2 (filtration over scales rather than one fixed k̃). If a single-scale graph is retained, use a **mutual-kNN** graph + min-cluster-size, and report a k̃ / minPts sensitivity ablation.

### Phase 4 — Recursive interpretable dendrogram *(now THE product)* — **UPDATED**
- Isolate cluster → remove its points → re-run on remainder → repeat. Each split discovers **its own** minimal feature set (minimality is a soft per-split preference, never enforced, not depth-coupled).
- Output: **a single unique binary tree**; every internal node carries (responsible variables, persistence, threshold rule). **Hard partition**; soft assignment only if biology later demands it.
- **Canonical split** = highest continuous persistence → tie-break by stability → then balance (interpretability reported, not selected on). **Diversity** = same-membership alternative panels kept as alternative descriptions of one split.
- **Error-compounding** defended by **beam search + a stability gate** (a stopping threshold alone is insufficient); the b=1-vs-b / gate on–off ablation is a headline result. Requires Phase 2 continuous fitness first.
- Differs from a decision tree: **unsupervised**, splits on a **jointly-selected feature subset**, rule fit *afterward* to reproduce a geometrically-discovered split.

### Phase 5 — Improved genetic operators
- **Crossover:** drop bitwise-OR (monotonically grows feature sets) → uniform or set-based (keep shared features, sample the symmetric difference under a size cap).
- **Mutation:** per-bit, asymmetric — bias toward **removal** (remove rate ~3–5× add rate; add ~1/p) to counter bloat in sparse genomes.
- **Archive:** fix the suspicious ~0.05% add rule → standard novelty-threshold + small random trickle.
- **Initialization:** seed from features showing univariate separation signal (see Phase 6).

### Phase 6 — Scalability to biomedical dimensionality
- **Sparse representation:** variable-length set of selected indices (not a length-p bit string).
- **Pre-screening:** variance filter + **bimodality screen** (Hartigan's dip test, or Seemann's non-dimensionalized std-dev) to shrink ~10³–10⁴ genes to a few hundred candidates and seed initialization.
- **Group units:** select **pathways / gene sets (MSigDB)** rather than single genes (lower dim + stronger interpretability).
- **Correlation-awareness:** cluster genes into co-expression modules (design-time) and select representatives, to fight collinearity-driven instability.
- Note: per-evaluation cost is `O(n²d)`, cheap for biomedical small-n/large-d; the search-space size is the real cost.

### Phase 7 — Out-of-sample assignment rule + richer interpretability
- After each split, fit a **minimal rule on the selected features to reproduce that split** (depth-1/2 tree or linear boundary), fit to ATOMIC's *own* partition → small, *measured* approximation gap (exKMC's idea anchored to an interpretable base). Yields thresholds → human-readable rule + deployable classifier for new patients.
- Report interpretability beyond feature count: selection stability, nameable/grouped features, rule simplicity.

### Phase 8 — Biomedical validation *(the result that earns a bio venue)*
- Datasets: TCGA (e.g., BRCA / PAM50), METABRIC, public GEO; pre-correct batch effects (ComBat), check class imbalance.
- **External agreement:** ARI/NMI vs known molecular subtypes.
- **Clinical meaning:** Kaplan–Meier survival curves per cluster + log-rank test ("do discovered clusters separate survival?").
- **Biological plausibility:** pathway enrichment (GSEA / hypergeometric) on selected genes.
- **Stability selection:** bootstrap patients, re-run, report selection frequency + a formal stability score (e.g., Nogueira's). *Credibility linchpin for any biomarker claim.*
- **Realistic framing:** "to what extent does it recover known biology," not "it recovers known biology." Partial recovery + survival separation is publishable.

### Possible Phase-2(b) / later experiment
- **MAP-Elites** (quality-diversity) as an alternative engine to NSLC for the diversity goal — note as a comparison/ablation, not baseline. Build only if NSLC struggles with diversity.

---

*Companion document: `cowork_handoff.md` — full project state and the Cowork task queue.*
