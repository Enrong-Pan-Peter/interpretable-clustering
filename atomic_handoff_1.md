# Cowork Handoff — ATOMIC Follow-Up Research Project

> **Read this first.** This document is the single source of truth for the project. It captures everything agreed so far so a fresh Cowork session can pick up cold. It assumes you (Cowork) have been pointed at the local repo folder, which contains the original ATOMIC source code and the paper PDF (`ATOMIC-interpretable-clustering.pdf`).

> **⚠️ SUPERSEDED IN PARTS (2026-07-06).** Several decisions below have been updated by a blind-spot review — see **`blind-spot-audit.md`** (its "Decision log" and "risk triage" are now authoritative). Headlines: target is a **GECCO 2027 full paper, methods-first** (biomedical deferred to a later journal); the product is a **single recursive interpretable tree** (not a set of competing explanations); **reproduce-first is dropped** — we re-implement ATOMIC and own it. Where this doc and the audit disagree, the audit wins.

---

## 0. How this Cowork session will be used

- **Role split:** **Cowork** (you) = idea discussion, implementation-plan authoring, and editing findings docs. **Cursor** = executes the plans you write, does the actual coding. **The human (Enrong)** drives, decides, and runs experiments.
- **You do not need to write production code.** You produce plans, specs, and documentation that Cursor turns into code. When asked for a "plan for Cursor," write it as an explicit, ordered, file-and-function-level spec Cursor can follow with minimal ambiguity.
- Keep all durable project knowledge in repo markdown docs (see §7 for the proposed structure) so it survives across sessions.

---

## 1. Project context

- **Researcher:** Enrong — graduate student, **Ting Hu lab, Queen's University** (Kingston, Ontario).
- **Note:** Ting Hu is the **senior author of the anchor paper (ATOMIC)**, so the original code and lab resources are accessible. The repo is the lab's own.
- **Goal:** Improve the ATOMIC methodology *and* apply it to **biomedical data** (patient stratification — selecting the minimal features that separate patient subgroups), to publish a **follow-up paper**. Leaning toward a **journal** rather than another short conference paper (see §6).
- **Backstory that matters:** The original ATOMIC was intended as a *full* conference paper but became a **4-page short paper due to time/writing constraints** from the previous student. So the *idea may be stronger than the published artifact*, and the short-paper status is partly a writing artifact, not a ceiling on the method. Treat the existing code critically — it may carry the same rushed-ness.

---

## 2. What ATOMIC is (technical summary)

ATOMIC answers one question: **"Why does my data fit into distinct clusters?"** — by finding a **minimal subset of variables** that isolates a cluster from the rest. Key pieces:

- **Interpretable, not explainable** (Rudin's distinction): the model *is* the explanation, with no post-hoc approximation gap. (By the 2024 Interpretable Clustering survey's taxonomy, ATOMIC is an **"in-clustering"** method.)
- **Topology warping:** an individual is a **Boolean bit-string** of length *p* (one bit per variable, 1 = use it). Selecting a subset = viewing the points through only those dimensions, which **warps distances**. Different subsets break different groups off.
- **Connected components via k̃-NN graph:** for a given subset, build a nearest-neighbour graph in that subspace and count connected components. A subset **isolates a cluster** when there are exactly **two** components.
- **k̃ (k-tilde):** a single fixed neighbour count used in *every* subspace so fitness is comparable across subsets. Found once on the full data: grow k from 2 until the component count stops changing (the "stable k"). **Note:** k̃ is *not* 8 — the **8** in the paper is a *different* k, used for the k-NN graph over the *solution archive*.
- **Fitness:** `f = −(C − 2)²` (max = 0 at exactly two components) + minimize feature-set size.
- **Search = NSLC (Novelty Search with Local Competition)** under **NSGA-II** selection, to return a *diverse* set of splits:
  - **Novelty** = Hamming-distance sparseness to nearby solutions (explore different subsets).
  - **Local competition** = how many neighbours an individual out-performs, where I₁ out-performs I₂ iff `f(I₁) > f(I₂)` or (`f` tied and `|I₁| < |I₂|`).
- **EA params (Table 1):** Boolean genome length *p*; mutation = flip random bit (60%); crossover = **bitwise-OR** (40%); population 100, offspring 60 (a **(μ+λ)** scheme — pop stays 100 each generation); NSGA-II survivor selection; 100 generations; archive add prob listed as 0.05%.
- **Results:** 7 UCI datasets (all >10 dims), 2-NN imputation + scale to [0,1]. Beats k-means/GMM/DBSCAN on silhouette (5/7) and Davies–Bouldin (6/7). Interpretability reported as **% feature reduction**; performance correlates with reduction (>60% reduction → ATOMIC wins).
- **Showcase:** Ceramic dataset — ATOMIC isolates a cluster with 3 named variables (MgO, CaO, P₂O₅), plottable on real axes; contrasted with exKMC whose explaining tree lists its own mistakes (the approximation gap).

**Not PCA:** ATOMIC *selects* original variables (interpretable, named); PCA *transforms* into weighted blends of all variables (uninterpretable). This distinction is the whole value proposition for the biomedical application.

---

## 3. Identified caveats in ATOMIC (verify against the code; some may be typos/omissions)

Ordered by importance. **Phase 0 must check these against the actual code, especially #1.**

1. **Metric-space confound (highest priority).** Silhouette & Davies–Bouldin are **space-dependent**. ATOMIC chooses its own (low-dim) subspace; the baselines are scored in full space. High-dim silhouette collapses via **distance concentration**, so ATOMIC's biggest wins land exactly on the highest-reduction datasets — consistent with a *genuine strength AND/OR a measurement artifact*. **The code must reveal in which space each metric is computed.** This is the make-or-break audit.
2. **Flat fitness landscape.** `f = −(C−2)²` is integer-valued and mostly flat: most mutations don't change the component count, and all clean 2-component splits tie at 0. Almost certainly why NSLC was needed. → Phase 2 fixes this with a continuous score.
3. **"Topology" is currently a metaphor.** Only β₀ (connected components) at a *single* scale k̃. This is effectively **single-linkage clustering** → chaining (one bridge point fuses groups) and degenerate splits (isolate one outlier to score a perfect C=2). The fixed *global* k̃ is also questionable since subspaces have different geometry.
4. **Binary cuts only / no multi-cluster composition.** `f` targets exactly 2 components; multiple clusters emerge only as diverse one-vs-rest splits with no defined way to assemble them into a coherent global partition. → Phase 4 (recursive dendrogram).
5. **Bitwise-OR crossover** takes the *union* of parents → monotonically **grows** feature sets, fighting the parsimony goal. → Phase 5.
6. **Archive add-probability ~0.05%** looks suspicious: over ~16k evaluations that adds ~8 solutions, making novelty/local-competition (computed against the archive) nearly meaningless. Likely a typo (5%? 0.5%?) or genuine under-exploration. **Verify in code.**
7. **"Best solution" selection unspecified.** How the single reported solution (Table 4) is picked from the final Pareto front is never stated. Reproducibility hole. **Find it in code.**
8. **Thin evaluation.** Single runs (no mean±std for a stochastic EA), no statistical testing across datasets, and the baselines are all **non-interpretable full-space clusterers** — the honest competitors are other *interpretable/explainable* methods and the *evolutionary subspace* family (ChameleoClust/KymeroClust), plus spectral clustering. → Phase 1.
9. **Interpretability = feature count is too crude.** Conflates "few" with "understandable" (the Ozone result uses 37/72 variables yet is reported as a success). Showcase only works at ≤3 features (literally plottable).
10. **No out-of-sample rule.** ATOMIC names *which* variables separate a group but gives no threshold/rule and no way to assign a new point without rebuilding the graph. → Phase 7.
11. **Scalability wall for biomedical.** Sells itself as high-dimensional but tops out at 72 dims; gene expression is 10³–10⁴. A length-*p* bit-string with single-bit mutation + union crossover won't move at that scale. No complexity/runtime analysis. → Phase 6.

---

## 4. The plan (extensions, dependency-ordered)

> Full version with rationale is in `literature_review.md` (§"Outline of our plan"). Condensed here with the technical specifics Cursor will need.

### Phase 0 — Re-implement and own the baseline *(do first)* — **UPDATED**
**Reproduce-first is dropped.** Matthew's baseline scorer (`compare_atomic.py`), preprocessed CSVs, and exact EA config are unavailable, so bit-for-bit reproduction of the published tables is not possible — and matching them would only validate a possibly-confounded setup. Instead:
- **Re-implement ATOMIC faithfully** from the paper + the repo EA (`atomic.py`), fixing/documenting the known bugs (mutation `i1[1]` typo, `choose_k` chaining/tuple, novelty recompute).
- **Validate the re-implementation** on tiny hand-checkable inputs and a synthetic set with known answer (so a re-implementation bug can't masquerade as a finding).
- No dependency on Matthew: the 7 UCI sets are public, preprocessing (2-NN impute + [0,1] scale) is fully specified in the paper, and baselines/metrics are stock scikit-learn.
- On the fairness question: what's *confirmed* is that ATOMIC scores itself in its selected subspace; whether the baselines were scored in full space is unknown. Don't claim "they were unfair" — internal metrics (silhouette/DB) simply aren't comparable across different-dimensional spaces, so adopt a protocol that's valid either way (Phase 1) and let the numbers fall where they fall. Frame as *putting the evaluation on a fair footing*, not a correction.

### Phase 1 — Fair evaluation protocol *(highest-stakes)*
- **Subspace parity:** score baselines on ATOMIC's selected subset (same space for all).
- **External metrics:** ARI + NMI vs ground-truth labels (space-invariant). The UCI sets have labels (Ionosphere, Glass, Biodegradation, Cervical Cancer, Ceramic era).
- **Statistics:** ~30 runs, mean±std; Friedman + Nemenyi across datasets.

### Phase 2 — Continuous persistence fitness *(core upgrade)*
- Build **MST** in the selected subspace; sort edge weights `e₁ ≥ e₂ ≥ …`; **S = e₁ − e₂** (maximize) = persistence of the 2-cluster split. The two clusters are the two subtrees after cutting `e₁`. Multi-cluster: `S = e_{m−1} − e_m` after cutting the top `m−1` edges.
- Normalize: `e₁/e₂` or divide by median edge weight (cross-subspace comparability).
- **Mutual-reachability distance:** replace `d(a,b)` with `max(core_k(a), core_k(b), d(a,b))` (outlier-robust; HDBSCAN's idea).
- **Minimum cluster size:** a split only counts if both sides ≥ minPts (kills "isolate one outlier" degenerate wins).
- Plug into out-performance: I₁ beats I₂ if `S(I₁) > S(I₂)`, tie-broken by fewer features.
- **Cost note:** per-eval is `O(n²d)` — cheap for biomedical small-n/large-d.

### Phase 3 — k̃ robustness
Mostly dissolved by Phase 2 (filtration over scales). If keeping a single-scale graph: **mutual-kNN** graph + min-cluster-size; report a k̃/minPts sensitivity ablation.

### Phase 4 — Recursive interpretable dendrogram *(cleanest new capability)* — **UPDATED (this is now THE product)**
1. Run on full data → best split (group A | rest) with feature set V_A and score S_A.
2. Recurse on each child *independently* (each split finds its own minimal feature set — minimality is a **soft per-split preference for interpretability, never enforced, not depth-coupled**).
3. Stop when best persistence < threshold or subset < minPts.
- Output: **a single unique binary tree**, every internal node annotated with (responsible variables, persistence, threshold rule).
- **Canonical split selection** (resolves "which of several equal-size panels?"): highest **continuous persistence** → tie-break by **stability** (bootstrap reproducibility) → then **balance**. Interpretability is a *reported* property, not a selection criterion. *Requires Phase 2 continuous fitness to exist first, or every split ties.*
- **Diversity = same-membership alternative panels.** Multiple minimal sets that induce the *same* bipartition are kept as alternative *descriptions* of one split (a human picks the most measurable/plausible); admit a panel only if its split matches the canonical one within ε (e.g., ARI ≥ 0.98). This keeps the tree unique while preserving the diversity contribution.
- **Error-compounding defense:** **beam search** (keep top-*b* splits per node, expand, keep best subtree; *b*=1 ↔ greedy) + a **stability gate** (commit a split only if it clears persistence AND bootstrap-reproduces). The **b=1-vs-b / gate on–off** ablation on synthetic truth is a headline result. Global prune-and-regraft refinement = future work.
- **Hard partition, no overlap by construction.** Soft assignment only if the biology later demands it.
- **vs decision tree:** unsupervised; splits on a **jointly-selected feature subset** (not one feature/threshold); rule fit *afterward* to reproduce a geometrically-found split.

### Phase 5 — Operators
- **Crossover:** replace bitwise-OR with **uniform** (each bit from either parent ½) or **set-based** (keep shared features, sample symmetric difference under a size cap).
- **Mutation:** per-bit, **asymmetric** — remove rate ≈ 3–5× add rate (add ≈ 1/p) to counter bloat in sparse genomes.
- **Archive:** standard **novelty-threshold** add (+ small random trickle), not 0.05%.
- **Init:** seed from features with univariate separation signal (Phase 6 screen).

### Phase 6 — Scalability (biomedical)
- **Sparse representation:** variable-length **set of selected indices**, not a length-*p* bit-string; operators act on sets.
- **Pre-screen:** variance filter + **bimodality screen** (**Hartigan's dip test**, or Seemann's non-dimensionalized std-dev) → shrink 10³–10⁴ genes to a few hundred candidates; reuse as init seeds.
- **Group units:** select **pathways / gene sets (MSigDB)** instead of single genes (lower dim + better interpretability).
- **Correlation-awareness:** cluster genes into **co-expression modules (design-time)**, select representatives, to fight collinearity-driven instability.

### Phase 7 — Out-of-sample rule + richer interpretability
- After each split, fit a **minimal rule on the selected features to reproduce that split** (depth-1/2 tree or linear boundary), fit to ATOMIC's *own* partition → small, **measured** approximation gap. Yields thresholds → human-readable rule + deployable classifier for new patients.
- Report interpretability beyond feature count: selection stability, nameable/grouped features, rule simplicity.

### Phase 8 — Biomedical validation *(earns the bio venue)*
- Datasets: TCGA (e.g., **BRCA / PAM50**), METABRIC, GEO. Pre-correct **batch effects (ComBat)**; check class imbalance.
- **External agreement:** ARI/NMI vs known molecular subtypes.
- **Clinical meaning:** per-cluster **Kaplan–Meier** curves + **log-rank** test ("do discovered clusters separate survival?" — i.e., do cluster patients' time-to-event curves pull apart).
- **Biological plausibility:** pathway enrichment (**GSEA / hypergeometric**) on selected genes.
- **Stability selection (credibility linchpin):** bootstrap patients, re-run, report selection frequency + a formal stability score (**Nogueira's**).
- **Framing:** "to what extent does it recover known biology," NOT "it recovers known biology." Partial recovery + survival separation is publishable; full recovery of supervised subtypes (e.g., PAM50) is a high bar and not expected.

### Optional later experiment
- **MAP-Elites** (quality-diversity) as an alternative engine to NSLC for diversity — comparison/ablation, not baseline; build only if NSLC underperforms on diversity.

---

## 5. Novelty positioning (what makes this publishable)

The space is **crowded** — most of our broad ideas exist somewhere. The contribution is the **synthesis**, framed narrowly. (Full map in `literature_review.md`.)

Each neighbour owns one ingredient; **no single work combines all four:**
1. evolutionary subspace search (Peignier: ChameleoClust/KymeroClust),
2. a **continuous topological separation objective** the search optimizes (ToMATo / topological HDBSCAN provide the criterion, not the search),
3. a **diversity** of minimal feature-defined separations (novelty search) — scoped as **same-membership alternative panels per split** (feature-space diversity; the tree stays unique),
4. a **recursive interpretable hierarchy** with per-split feature sets + deployable rules — validated under a fair protocol (biomedical validation deferred to the follow-on journal paper).

**Must cite & differentiate up front:**
- **Peignier (engine):** we differ via topology/persistence (non-convex capability) + interpretability-first + diversity. Their methods are centroid/median-proximity, performance-framed, single-solution.
- **Seemann 2012 (biomedical):** *the* closest biomedical prior art — persistence + compact genes + hierarchical + GBM subtype recovery + 59-gene predictor + bimodality pre-screen. We differ via **per-split independent feature sets discovered by search** (they use one global panel for all subtypes), evolutionary search, diversity, and modern fair evaluation.
- **Interpretable Clustering Survey 2024:** our *goals* (minimal, unique per-cluster evidence) are the field's standard desiderata, and our interpretable-vs-explainable pitch is the standard in- vs post-clustering distinction — so novelty lives in the *mechanism*, not the framing.

A drafted *Related Work* positioning section already exists (in our discussion) and should be dropped into the manuscript early to pre-empt reviewers. **Sentences that are promissory** ("captures non-convex separations that elude centroid models"; "each separation defined by its own minimal feature set") **must be backed by experiments** before they go in.

---

## 6. Decisions & working agreements already made

- **Get the repo, don't reproduce from scratch** (done). Opus/Cursor can *write* a clean ATOMIC, but matching the paper's exact numbers from a 4-page paper is unreliable; the repo is ground truth, especially for the underspecified bits (metric space, k̃, archive prob, best-solution selection).
- **Repo hygiene:** `git clone` (NOT fork — no upstream merge is happening). Keep original history as provenance; `git tag atomic-baseline` the pristine commit; optionally keep theirs as a read-only `upstream` remote and push your own `origin`. **Branch per extension.**
- **Reproduce-first, scoped tight:** run their code → match their tables → read metric code → tag → move on. Do *not* sink weeks re-implementing from the paper.
- **Cursor codes, Cowork plans/interprets.** (This split.)
- **Journal-leaning** follow-up (the short-paper status was partly a writing artifact; the fuller method + biomedical validation is journal-sized).
- **Hard partition first** (no overlap by construction in the recursive method); add soft assignment only if biology demands it.
- **Realistic biomedical framing** (partial recovery + survival separation is the win; don't promise full subtype recovery).

### Updated decisions (2026-07-06 blind-spot session) — these supersede conflicts above
- **Target = GECCO 2027 full paper, methods-first.** Biomedical (Phases 6–8) → follow-on **journal** paper. *(Supersedes the earlier "journal-leaning" ambiguity.)*
- **Product = a single recursive interpretable tree**, not a set of competing explanations.
- **Diversity kept**, scoped as **same-membership alternative panels** per split (feature-space only).
- **EA justified** by multi-objective (separation vs. minimal size) **+** the diversity of panels — this is the answer to "why not greedy?" (with a greedy/L1 + b=1 ablation to prove it).
- **Canonical split** = persistence → stability → balance; interpretability reported, not selected on.
- **Error-compounding** handled by **beam search + stability gate**; global refinement = future work.
- **Baseline = re-implement and own** (reproduce-first dropped; Matthew's code/data unavailable — see Phase 0).
- **Continuous persistence fitness (Phase 2) is the linchpin — build it first;** recursion, canonical selection, and beam scoring all depend on it.
- Full rationale + risk triage: **`blind-spot-audit.md`**.

---

## 7. Proposed repo documentation structure (one of your first tasks is to finalize this)

The human wants to decide which docs to create for findings/experiments. Proposed layout (adjust as needed):

```
/docs
  architecture.md          # Cursor-generated map of the codebase (Task 1)
  baseline-reproduction.md # env setup, exact repro results, any discrepancies vs paper
  caveats-audit.md         # findings on the 11 caveats, esp. the metric-space confound
  method-extensions.md     # living spec of the planned method changes (Phases 2–7)
  literature.md            # the literature review / novelty positioning (port from literature_review.md)
  decisions.md             # ADR-style log: each decision, date, rationale
  /experiments
    exp-001-subspace-parity.md
    exp-002-external-metrics-ari-nmi.md
    exp-003-persistence-fitness.md
    ...                    # one file per experiment: hypothesis, setup, command, result, conclusion
  biomed-validation.md     # datasets, protocols (KM/log-rank, enrichment, stability), results
README.md                  # project overview + how to run + pointer to /docs
```

Principles: one experiment = one doc (hypothesis → setup → exact command → result → conclusion); log decisions as you go; keep `method-extensions.md` as the canonical spec Cursor implements against.

---

## 8. Immediate Cowork task queue (what the human will start with)

*Reordered 2026-07-06: Phase-2-first, no reproduction step.*
1. **`architecture.md`** — Cursor maps the codebase: the EA loop, where fitness/connected-components/k̃ live, data loading/preprocessing, external deps. Reference map for later work.
2. **Re-implement + validate ATOMIC** (Phase 0, updated): faithful re-implementation, bugs fixed/documented, checked on tiny + synthetic-with-known-answer inputs. No reproduction of the published tables.
3. **Continuous persistence fitness (Phase 2) — build first.** The linchpin; canonical selection, tie-breaks, and beam scoring all depend on it. Without it every clean split ties (caveat #2).
4. **Recursion + canonical selection + stability gate + beam** (Phase 4). Produces the single tree; add the same-membership alternative-panels layer once the spine is solid.
5. **Fair evaluation (Phase 1) + null + adversarial synthetic benchmark + greedy/L1 & b=1 ablation.** Score baselines *both* in full space and in-subspace to show the space effect empirically. Report internal *and* external (ARI/NMI) metrics (watch M1).
6. **Operators (Phase 5)** as needed; **decide `/docs` structure** (§7) alongside.

When writing any "plan for Cursor," make it file-and-function-level explicit, list the exact files to touch, and state the acceptance check (e.g., "reproduces Table 2 silhouette within ±0.01" or "ARI computed against `y_true` in full space").

---

## 9. Key references (URLs)

- **ATOMIC** (anchor, in repo): Vandergrift & Hu, GECCO '24 Companion. DOI 10.1145/3638530.3654271
- **ChameleoClust:** https://inria.hal.science/hal-01252793 · Peignier PhD thesis (incl. KymeroClust): https://hal.archives-ouvertes.fr/tel-01697499
- **Interpretable Clustering: A Survey (2024):** https://arxiv.org/pdf/2409.00743
- **Seemann et al. 2012** (closest biomedical prior art): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4393071/
- **Context:** ToMATo (Chazal et al.); topological HDBSCAN (McInnes & Healy, arXiv 1705.07321); Nicolau et al. PNAS 2011; multi-objective evolutionary subspace clustering (Expert Systems w/ Applications 2020); PHEATPRUNER (2024).

---

## 10. Open questions to resolve from the code (carry into the audit)

- In which feature space are silhouette & Davies–Bouldin computed for **ATOMIC**? For the **baselines**? (The confound.)
- What are the actual **k̃** values per dataset, and how stable are they?
- What is the **real archive add-probability** (is 0.05% a typo)?
- How is the **single reported solution** chosen from the final population?
- Is there any **runtime/complexity** instrumentation, or must we add it?
- How are **ties at C=2** currently broken (feature count only)?
- Does the implementation already handle **multi-cluster** in any way, or strictly one-vs-rest?

---

*Companion: `literature_review.md` — the prior-art comparison table and the plan outline.*
