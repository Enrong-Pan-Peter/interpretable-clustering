# Blind-Spot Audit — ATOMIC Follow-Up

*A red-team / reviewer-adversarial pass over the codebase, `atomic_handoff_1.md`, and `literature_review.md`. Goal: surface **unknown-unknowns** — risks and decisions NOT already tracked in the 11 caveats or the 8-phase plan. Where a point sharpens an existing caveat rather than being wholly new, it says so.*

*Classification is by **cost-if-wrong × how-late-you'd-notice**, not by likelihood.*

---

## HIGH RISK — can change direction, architecture, or kill the paper

### H1. The fair evaluation you're championing could dissolve ATOMIC's advantage — and there's no plan for that branch
The entire plan is built as if ATOMIC's edge is real and the job is to *prove it fairly*. But Phase 1 (subspace parity + ARI/NMI) is precisely the test that could show the silhouette/DB wins were mostly a measurement artifact. The docs say "genuine strength AND/OR artifact" but every downstream phase assumes "strength." **If fair evaluation shows ATOMIC is not better than k-means/spectral in-subspace, the contribution must pivot entirely off performance and onto interpretability/diversity/capability — before you've built Phases 2–8 on the performance premise.** This is the single biggest unknown-unknown. You want to run the honest Phase 1 *first* and hold the rest loosely.

### H2. Two of your headline novelties fight each other: diversity-of-explanations vs. a single partition
NSLC exists to return *many competing* minimal splits. But ARI/NMI (Phase 1) and the recursive dendrogram (Phase 4) both need *one* partition. These pull opposite directions:
- If a patient can be split off by feature set A *or* by feature set B (two equally valid "explanations"), the recursive tree must pick one and **throws away exactly the diversity NSLC was built to produce.**
- **How do you even compute ARI for a one-vs-rest binary split against a K-class ground truth?** `combine.py` is a manual, heuristic assembly ("higher index wins"), user-supplied indices, no principled rule. That is not a publishable partition-construction method.

You have not decided whether the *product* is "a diverse set of local explanations" or "a global hierarchical partition." They need different evaluations, different framing, arguably different engines. **Architecture-defining; decide now.**

### H3. No null model / significance test — fatal for the biomedical claim
In high dimensions you will find *some* feature subset that "separates" patients **by chance** (garden of forking paths + a stochastic search explicitly hunting for splits). Stability selection (Phase 8) tests *reproducibility*, not *significance* — a chance split can be stable. There is no permutation/null anywhere in the plan: permute labels/data, re-run the full search, show your real separation score sits in the tail. **Without a null, "we found a 3-gene subset that splits patients" is a reviewer kill-shot in any biomarker venue.** New; not in the 11 caveats.

### H4. No greedy / L1 / random-search baseline — the EC reviewer's first question
The task "find a small feature subset that separates the data" is exactly what greedy forward selection and L1-sparse methods do cheaply. **A GECCO/TEVC reviewer will ask: does the evolutionary machinery beat greedy selection or random search?** If a greedy baseline matches ATOMIC, NSLC + NSGA-II + archive is unjustified complexity. Your planned baselines (ChameleoClust, spectral, exKMC) are the *clustering* competitors but miss the *"is the search even necessary"* ablation. New.

### H5. Venue and MVP are undecided, and that decision reorders every phase
"Journal-leaning" spans two incompatible audiences. An **EC journal** (Evol. Comput., IEEE TEVC) wants algorithmic novelty and ablations; biomedical validation reads as "an application." A **bioinformatics journal** wants survival/enrichment/stability and reads the EA as plumbing, asking "why not an established method?" These want the phases in *different priority orders*. Separately: **8 phases is plausibly two papers** (a methods paper: Phases 1–5; an application paper: Phases 6–8). Committing late lets scope sprawl into an unfocused single submission that satisfies neither reviewer pool. **Decide target venue + MVP scope before building.**

### H6. The diversity mechanism degenerates at biomedical scale — distinct from the genome-length wall
Novelty = Hamming distance between bit-strings. At p≈10⁴, all *sparse* genomes share ~10⁴ zeros and are near-equidistant in Hamming — **novelty becomes uninformative exactly where you need it.** This is the diversity analog of distance concentration, and it is *separate* from caveat #11 ("single-bit mutation won't move a length-p string"). Switching to a sparse index-set representation (Phase 6) *also silently changes the novelty metric's semantics* (set distance on very different supports), which the plan doesn't acknowledge. If diversity-of-explanations is load-bearing (see H2), this threatens it in the target domain.

### H7. You are publicly correcting your own lab's prior result, under the same senior author
If Phase 1 shows the headline ATOMIC numbers were partly a metric-space artifact, the follow-up says so — with Ting Hu as senior author on *both* papers, and Matthew's code as the thing being audited. **This needs an explicit framing and buy-in strategy** ("we strengthen and correct the evaluation of our own method") agreed *before* you write it, or it becomes awkward late. New; a project/political risk, not technical.

---

## MEDIUM RISK — important, quietly wrong, expensive to retrofit

### M1. ARI-vs-class-label can penalize a *correct* clustering
UCI labels (Ionosphere good/bad, Glass type, …) are **classification** labels, not guaranteed to be the geometric cluster structure. A method can recover real structure that doesn't match the label and score low ARI. You're leaning on ARI/NMI (Phase 1) to escape the metric-space confound, but it has its own confound: **low ARI may mean "found different real structure," not "worse."** Report internal *and* external, and don't let ARI alone adjudicate.

### M2. The real runtime bottleneck is the novelty/archive bookkeeping, not the O(n²d) topology eval
`nslc_eval` rebuilds a `NearestNeighbors` over the *entire growing bank* on **every evaluation** (`neigh.fit(all_in_bank)`), decoding every bank key to a bit-list each time. That's roughly O(|bank|·p) per eval with |bank| growing — plausibly **super-linear in evaluations and dominant over the fitness cost** the plan budgeted (O(n²d)). The scalability wall (caveat #11) is framed as genome length; a bigger wall is in the search plumbing. New sharpening.

### M3. Your synthetic generators encode ATOMIC's own inductive bias — circular validation
`convex_synth_data.generate2` and `convex_synth_data.py` build **axis-aligned subspace Gaussians** (a subset of dims has a blob, the rest uniform) — literally the structure ATOMIC is designed to find. Method-development phases (2, 5) validated on self-matched synthetic data will look good for the wrong reason. **You need adversarial synthetic data**: non-axis-aligned, correlated-noise, and connectivity-*un*-separable clusters, plus cases where a bridge point should (not) fuse groups. New.

### M4. Survival separation is confounded by clinical covariates
Discovered clusters can separate Kaplan–Meier curves because they capture **stage/age/grade**, not novel biology. Plan has log-rank only. A bioinformatics reviewer wants **Cox with clinical covariates** (does the cluster add signal beyond known prognostics?). New; standard demand.

### M5. `choose_k` picks the *smallest* stabilizing k → maximizes chaining, and has a latent bug
`choose_k` returns the first k where the component count repeats once — for a connectivity kNN graph that's typically a *very small* k̃, i.e. the sparsest graph, i.e. **maximum single-linkage chaining risk** (the exact failure in caveat #3, now with a named mechanism). Also: if the count never stabilizes it returns `seen_tuples[-1]`, a **tuple**, so `k_use` becomes a tuple and downstream calls misbehave silently. Verify what k̃ actually was in the published runs (also open in request-to-matthew #4).

### M6. "Reproduce-first" is now largely infeasible — the baseline must be re-implemented and *owned* (UPDATED)
Confirmed by Enrong: assume **no further code/data from Matthew beyond the incomplete repo.** `compare_atomic.py` (the baseline scorer — the crux of the confound), the preprocessed CSVs, and the real EA config are gone. So **Phase 0 "match their published tables" is effectively dead** — you cannot reproduce numbers whose scoring code, data, and config no longer exist. Consequences:
- The baseline becomes a **clean re-implementation you own** (from paper + repo), *not* a bit-for-bit reproduction. This is exactly what the handoff wanted to avoid — the plan needs rewriting to drop the reproduce-first framing.
- **Silver lining on H7:** if you never reproduce their exact tables, you're not publicly declaring their specific numbers wrong; you're reporting what *your* fair protocol finds. Less political, cleaner story.
- **New risk:** without a reference implementation to check against, you can't tell a *re-implementation bug* from a *genuine finding*. Mitigate with unit tests on tiny hand-checkable inputs and at least one sanity dataset where the right answer is known.
- Separately, **METABRIC is EGA controlled-access** (application + weeks–months); if Phase 8 is the venue-earner, secure data access *now*, in parallel, not after the methods work.

### M7. "Interpretable" is asserted, never tested
Interpretability is operationalized as feature *count* (you know it's crude) — but "small" ≠ "understandable to an oncologist." There's no rubric and no domain-expert check. Interpretable-ML reviewers increasingly demand one. Adding a human/expert evaluation is scope-expanding — a **resource decision** to make deliberately, not a thing to discover you're missing at submission.

---

## LOW RISK — real, cheap to fix if caught early, embarrassing if not

### L1. UMAP appears in figures; "clusters separate in UMAP" is not evidence
`atomic.py`/`combine.py` embed via UMAP (`random_state=1`) for display. Ensure no *claim* rests on UMAP separation; it's a nonlinear, parameterized transform. Figure-integrity only.

### L2. Preprocessing drives the graph and is part of the lost reproducibility
2-NN imputation + [0,1] scaling determine the kNN connectivity and thus the component count. Robustness to preprocessing choices is untested; and the exact preprocessing is among the missing artifacts (request-to-matthew #2). Pin it, then perturb it once as a robustness check.

### L3. k̃ instability contaminates the 30-run variance
k̃ is found once on full data. If `choose_k` is sensitive to seed/preprocessing, k̃ shifts between runs and your mean±std mixes two sources of variance. Fix k̃ per dataset explicitly, or fold its selection into each run and report it.

### L4. Hardcoded seeds mask variance
`np.random.seed(3)`, `random.seed(64)` — the current artifact is single-seed. The 30-run protocol must vary the EA seed *and* any preprocessing/k̃ seed, or "mean±std" understates true variability.

---

## Decision log (updated live in session, 2026-07-06)

**LOCKED**
- **Primary claim** = *interpretable clustering via a recursive hierarchy*, each split using a (preferably smaller) feature set. → De-prioritizes raw-performance framing; softens **H1**. *(was decision 1)*
- **Product shape** = *single global hierarchy*, not competing explanations. → **H2 resolved** in favor of one partition. *(was decision 2)*
- **Engine role** = EA justified by **both** (i) multi-objective per node — "minimal *and* best" = separation-vs-size Pareto — **and** (ii) **diversity of alternative panels per split** (Enrong: alternatives are valuable). Diversity is now a **claimed contribution, not optional.** → Resolves open item A. Greedy/L1 give neither natively, answering **H4**. **H6** (Hamming novelty at 10⁴ genes) deferred to the bio journal paper.
- **Venue + MVP** = **GECCO 2027 full paper**, **methods-first** (Phases 1–5, synthetic + UCI). Biomedical (Phases 6–8) = later **journal** paper. → **H5 resolved.** Runway ≈ 7 months.
- **Baseline** = re-implement and own; no reproduce-first (Matthew's code/data unavailable). → **M6.**
- **Alt-split semantics** = same membership, different features (single unique tree; agreement criterion e.g. ARI ≥ 0.98). → **F.**
- **Canonical split selection** = highest continuous **persistence**; ties → **stability** (bootstrap), then **balance**. **Interpretability is NOT a selection criterion** (too subjective — cf. **M7**); it's a *reported property*, applied post-hoc by a human choosing among same-membership panels. → **Hard prerequisite: Phase 2 (continuous fitness) must exist before recursion is built**, or every split ties (caveat #2).
- **Error-compounding defense** = **beam search** (keep top-*b* splits per node, expand, keep best subtree; *b*=1 ↔ greedy) + **stability gate** (commit a split only if it clears a persistence bar AND bootstrap-reproduces; else the node is a leaf). Headline experiment: **b=1-vs-b / gate on–off ablation** on synthetic data with known truth. Look-ahead = cheap fallback; global prune-and-regraft refinement = **future work**. Leans on the existing population/diversity as a robustness asset.

**OPEN — must resolve before building**
- **A. ~~EA justification~~ RESOLVED** — multi-objective + diversity (see locked list). *(H4)*
- **F. Diversity × recursion — RESOLVED:** alternatives must induce the **same membership** (feature-space diversity only). Output stays a single unique tree; panels are alternative *descriptions* of one split. **Implementation consequence:** needs an agreement criterion to admit a panel as an "alternative" (e.g., ARI ≥ 0.98 vs. the canonical bipartition), else near-misses get mislabeled as alternatives.
- **B. Set-size vs. depth — RESOLVED:** minimality is a **per-split soft objective** (the existing "minimize size" Pareto term), preferred for interpretability, **never mandatory and not depth-coupled**. Just observe/report whether sets shrink with depth.
- **C. Error-compounding — RESOLVED:** beam search + stability gate (see locked list).
- **D. Evaluation design for a *methods* paper — STILL LIVE (design work).** With biomedical deferred, synthetic + UCI must carry it. Needs adversarial (non-ATOMIC-biased) synthetic data (**M3**), a null model (**H3**), and the greedy/random ablation (**H4**).
- **E. Integrity guard for the later bio paper — DEFERRED.** "Find the easier dataset that awards the method / make it look good" is fine for a *demonstration* but is favorable-selection if framed as *validation*. Defense: pre-commit datasets, report the null + stability, frame as "to what extent does it recover known biology."

---

---

## Status after 2026-07-06 session — risk triage

**Resolved or softened by the decisions above**
- **H2** (diversity vs. partition) → single tree. **Resolved.**
- **H5** (venue) → GECCO 2027, methods-first. **Resolved.**
- **H4** (greedy baseline) → now a *required experiment* (b=1 ablation + explicit greedy/L1). **Owned.**
- **M6** (reproduce-first blocked) → decision to re-implement and own. **Resolved.**
- **H1** (performance edge dissolves) → **softened**: the claim is interpretability + recursive capability, not silhouette dominance — but the method still needs external validity (ARI/NMI) to look credible.
- **H7** (correcting the lab's own result) → **softened** by re-implement-and-own (no bit-for-bit numbers to contradict).
- **H6** (Hamming novelty degenerates at 10⁴ genes) → **deferred** to the biomedical journal paper.

**Still genuinely LIVE — must build for a credible GECCO paper**
1. **Continuous persistence fitness (Phase 2) — the linchpin.** Canonical selection, beam scoring, and tie-breaks all depend on it. **Build first.**
2. **Null model (H3).** Permutation test — does the method beat itself on shuffled data? Cheap; pre-empts "you found structure in noise."
3. **Adversarial synthetic benchmark (M3).** Current generators encode ATOMIC's own bias. Need data where k-means provably fails but your method wins (non-convex / non-axis-aligned) *and* a known hierarchical ground truth to score the tree.
4. **Greedy/L1 + b=1 ablation (H4).** Prove the EA and the beam earn their cost.
5. **Fair evaluation (Phase 1): subspace parity + ARI/NMI**, reported alongside internal metrics (M1: class labels ≠ cluster structure).

**Code-level fixes (not decisions, but real)**
- Mutation bug `i1[i] = (i1[1]+1)%2` — toggles bit 1, not bit i (request-to-matthew #6).
- `choose_k` picks the *smallest* stabilizing k (max chaining) and can return a tuple (M5).
- Novelty recomputes over the growing bank every eval (M2) — bites once beam multiplies evaluations.

**Suggested build order:** Phase 2 (continuous fitness) → canonical selection + stability gate → recursion + beam → Phase 1 (fair eval) + null + adversarial synthetic → operators (Phase 5) as needed. The alternative-panels/diversity layer goes on once the single-tree spine is solid.

---

*Companion to `atomic_handoff_1.md` (plan) and `literature_review.md` (novelty fence).*
