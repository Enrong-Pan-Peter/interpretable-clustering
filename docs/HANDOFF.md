# ATOMIC+ — Project Handoff (self-contained)

> **CORRECTION NOTICE (2026-08-05).** Parts of this handoff are superseded. Its selection numbers
> in §3.2/§3.3/§7 were measured on the benchmark that leaked (junk columns spread evenly, so four of
> six shapes gave away the planted pair one column at a time); the repaired-benchmark figures are
> uniformly better. Three of the §3.2 p=40 figures were also wrong against the old benchmark itself.
> §3b.5's "flame is unrecoverable for any gap/connectivity method" is contradicted — flame reaches
> ARI 0.665 once the true pair is known. Read `docs/CORRECTIONS.md` (C2, C3, C7) and
> `docs/experiments/exp-020-per-shape-audit-subclu-flame-splitter.md` before quoting anything here.
> The paper framing is also superseded by
> `docs/ting-meeting-2026-08-05-interpretability-reframe.md`.

This is a cold-start guide. Read it fully before doing anything. It covers what the project is, what
we tried, what worked and did not, the mistakes to avoid, how the repo is laid out, and next steps.

--------------------------------------------------------------------------------
## 0. One-paragraph state of the project
ATOMIC+ set out to be an interpretable clustering method: search over feature subsets to find the few
features ("panels") that separate clusters, judge separation topologically, arrange splits in a
recursive interpretable tree, and evaluate fairly. After extensive testing the honest state is: the
evolutionary algorithm does NOT earn its keep (random/greedy match or beat it), and the original
topological gap fitness was too weak. The breakthrough was a new SELECTION signal (a graph normalized
cut combined with a density-validity term, suggested by lab-mate Ryan) that reliably finds the
informative features on most non-convex shapes at low-to-moderate dimensionality. The open hard part
is high-dimensional selection of jointly-necessary features, which is essentially an unsupervised
feature-interaction / epistasis detection problem. No paper has been written yet; direction is under
discussion (see docs/ting-brief.md).

--------------------------------------------------------------------------------
## 1. What the project is
- Follow-up to ATOMIC (Vandergrift & Hu, GECCO '24), from Ting Hu's lab, Queen's University. Enrong is
  the student. Target was a GECCO 2027 methods-first paper (now in question).
- Original ATOMIC: an evolutionary algorithm (NSLC + NSGA-II) over boolean feature-subset genomes;
  clusters = connected components of a kNN graph; fitness = -(components-2)^2; interpretability = the
  few features responsible for a split. Reported wins on silhouette/Davies-Bouldin over k-means/GMM/DBSCAN.
- ATOMIC+ intended additions: a continuous "persistence" (topological gap) fitness, a recursive
  interpretable tree with per-split panels, and a fair evaluation protocol.
- Enrong values HONESTY and avoiding overfitting/benchmark-hacking. Keep that bar.

--------------------------------------------------------------------------------
## 2. How to use this repo
- `atomicplus/` is the clean-room package (no DEAP): `engine.py` (EA loop), `fitness.py`, `persistence.py`
  (MST edge-gap split), `tree.py` (recursive tree + gate), `operators.py`, `selection.py` (NSGA-II),
  `archive.py` (NSLC), `genome.py`, `topology.py`, plus `evaluation/` (metrics, baselines, harness,
  significance, diversity, search_baselines) and `datasets/` (synthetic generators, uci loader).
- `scripts/` holds the experiments (see the index in section 8). Run with `python scripts/NAME.py ...`.
- `docs/experiments/exp-001..exp-015` are dated findings write-ups. `docs/ting-brief.md` is the advisor
  memo. `docs/shapes.png`, `failures.png`, `needle.png`, `needle_highp.png` are explanatory figures.
- `2d_data/` has the non-convex benchmark shapes: jain.txt, flame.txt, spiral.txt.
- Tests: `python -m pytest -q -p no:cacheprovider` (32 tests, all passing).

### Gotchas (these WILL bite you)
- The sandbox shell has a ~44s timeout. Heavy runs (multi-seed, graph cut over many pairs) must be run
  by the user in their own terminal. Build+validate small in the sandbox, then hand off a command.
- Windows/Linux mount can corrupt files written by the Edit/Write tools mid-session. Prefer writing
  repo files via bash heredocs (`cat > file <<'EOF' ...`). Clear stale bytecode with
  `find . -name __pycache__ -exec rm -rf {} +` before running tests.
- The persistence fitness default is `normalize="ratio"` (e1/e2), NOT the raw gap e1-e2. This matters.
- `k=10` (kNN graph) and `core_k=5` (core distance = distance to 5th neighbour) are conventional
  defaults, NOT tuned. Their sensitivity is untested. Flag this in any writeup.

--------------------------------------------------------------------------------
## 3. Findings: what WORKED
1. **Fair-evaluation diagnosis.** Silhouette/Davies-Bouldin are computed in the low-dim subspace the
   method itself selects, which flatters it. Fix: score every method in the SAME subspace, use external
   metrics (ARI/NMI), add a column-permutation null and subsample stability. (Caveat: the confound is
   known in the literature; not novel by itself.)
2. **The graph-cut + density SELECTION signal (Ryan's idea) is the breakthrough.** For a candidate
   feature subset, score = z(graph term) + z(density term):
   - graph term g = -NCut(spectral bipartition of the kNN graph),  NCut = cut/vol(A) + cut/vol(B).
   - density term d = (min between-cluster mutual-reach - max within-cluster MST edge)/max(those) [DBCV-style].
   Overnight sweep (20 seeds, p in {12,20,40}) rank-1 selection rate: circles 1.0, gauss2 1.0,
   moons 0.90->0.80, jain 1.0->0.65, spiral 1.0->0.60, flame 0.0. Near-perfect at low p on 5/6 shapes,
   degrades gracefully with p. The hybrid beats graph-cut-alone (which fails the convex control and spiral).
3. **The split criterion is fixable with graph/density methods.** Single-linkage persistence fails on
   unequal-density (jain) and touching (flame) clusters; HDBSCAN recovers jain (0.90) and spectral
   recovers circles (1.0). Best end-to-end (graph-cut selection + the right split): circles 1.0,
   gauss2 1.0, moons 0.92, jain 0.90 at low-to-moderate p. NOTE: best split is shape-dependent
   (HDBSCAN for jain/moons, spectral for circles); no single split wins all.
4. **Interpretability**: the method returns small named panels; the recursive tree recovers known
   hierarchies on easier synthetic data.

## 3b. Findings: what did NOT work
1. **The EA does not earn its keep.** Tested exhaustively (plain search, diversity, deceptive landscapes,
   needle, MAP-Elites, CVT-MAP-Elites) AND re-tested with the good new fitness. Random search and greedy
   match or beat it everywhere. Structural reason: the landscape is threshold-shaped (a cliff, not a
   slope); jointly-necessary features give no gradient and no partial "building blocks" to recombine, so
   the EA degenerates to random-like sampling. CVT-MAP-Elites did not beat plain random either.
2. **The original persistence gap fitness (e1/e2) is too weak for non-convex.** It scores a CORRECT
   non-convex split as "no gap" about half the time (within-cluster edges are as long as the
   between-cluster bridge), so noise pairs with tiny spurious gaps outrank the true pair. The gap is
   tiny in both raw and ratio form (true pair ~0.008 raw vs best noise pair ~0.003). Switching ratio to
   raw difference does not help; the fix is a partition-quality signal (the graph-cut+density above).
3. **The "diversity of alternative panels" claim collapsed under a fair test.** It was the review's
   central novelty. With equal budget and honest counting, the un-seeded EA found ~0 clean panels;
   the diversity came entirely from brute-force pair-seed enumeration, and random blanketed the space
   better. Do not revive this claim without new evidence.
4. **High-dimensional selection of jointly-necessary features is unsolved.** Two effects grow with p:
   (a) coverage - the true pair is a needle among C(p,2) pairs and a budget-limited search may never
   evaluate it; (b) false positives - with many noise pairs, one overtakes the true pair by luck even
   under full enumeration (hurts jain/spiral). The check-everything ceiling holds on moons/circles but
   no budget-limited search reaches it.
5. **flame is unrecoverable** for any gap/connectivity method (its clusters touch; the ground-truth
   labels do not correspond to a visible separation). Keep it as a scope-boundary example, do not drop it.

--------------------------------------------------------------------------------
## 4. Mistakes NOT to repeat (methodological pitfalls we hit)
1. **Never trust 2-5 seeds.** A 2-seed run once "showed" the EA winning at high p; 20 seeds reversed it.
   Use >= 15-20 seeds before believing any trend.
2. **"Greedy" must be Sequential Forward Selection (add one feature at a time), NOT exhaustive pair
   enumeration.** Enumerating all pairs bakes in the knowledge that the answer is size-2 and is
   unfairly strong (it is really the ceiling). Fair greedy FAILS on jointly-necessary shapes because no
   single feature gives a signal to start from. `run_ea_newfit.py` now uses fair SFS; keep it that way.
3. **Do not weaken random search to a single draw.** "Random search" = sample B subsets, keep the best
   by fitness, SAME budget as the EA. That is the standard, strong, fair baseline. A single draw would
   be sandbagging it to make our method look good.
4. **Two different baseline questions - do not conflate them.** (i) search baselines (random/greedy on
   OUR fitness) answer "does the EA earn its cost". (ii) method baselines (k-means, spectral, HDBSCAN,
   SUBCLU, HTC, oblique trees) answer "do we beat prior work". The paper needs to win (ii), not (i);
   nobody beats random search.
5. **Check prior art before claiming novelty.** Each ingredient is largely covered: HTC (2026, topological
   hierarchical clustering), oblique clustering trees (KDD 2022, interpretable per-node feature splits),
   ChameleoClust (evolutionary subspace clustering), SUBCLU (density-based subspace clustering, the
   family the working fix falls into), OpenSubspace (VLDB 2009, the existing subspace benchmark).
6. **Keep the repo's record complete; decide separately what the paper reports.** *(Revised
   2026-08-05 on Enrong's instruction, confirmed with Ting. The previous version of this item told
   the reader not to drop datasets from the paper — that is no longer the project's position.)*
   What goes in a paper is a writing decision: reporting the settings where the method works, with
   a limitations section, is normal practice and is the plan here. That call is made at writing
   time, not in this file. What does not change is the **internal** record — every run into
   `results/`, every finding into an `exp-0XX` doc, including the ones that went against us. That
   is not about the paper; it is the only way we can tell what is actually true. The two biggest
   findings in this project came from the record being complete: the benchmark leak (four of six
   shapes gave the answer away one column at a time) and the mice replicate structure (72 animals,
   not 1080 samples). Both were caught because unfavourable numbers had been written down.
   Separately, the tie-break rules in `run_method_baselines.py` are a different question — those
   govern how a *baseline* was configured, not which of our results we show, and a reviewer who
   reimplements SUBCLU with the natural rule would find the difference. Keep those. Current
   practice there is to record both the precision/recall view and the best-case tie-break, and
   choose at writing time.
7. **Internal metrics are space-dependent.** Always confirm findings with external metrics (ARI/NMI).

--------------------------------------------------------------------------------
## 5. Novelty / prior-art map (read before positioning any paper)
- Non-convex clustering itself is NOT novel (spectral, HDBSCAN do it). Our defensible angle is narrower:
  finding the few informative features that reveal non-convex clusters hidden in noise, interpretably.
- The winning signal's parts (normalized cut, density validity) are established, so novelty is in the
  assembly + interpretable-subspace framing, not the clustering primitives.
- Strongest honest framing that emerged: this is **unsupervised feature-INTERACTION / epistasis
  detection** for clustering (features that matter jointly but not individually). For pairs the standard
  solution is an exhaustive O(p^2) scan; higher-order is genuinely open. This framing likely aligns with
  the lab's expertise and does not oversell.
- See docs/ting-brief.md for the three paper options (benchmark/characterization, scoped method,
  methodology) and their trade-offs.

--------------------------------------------------------------------------------
## 6. Next steps (in rough priority)
1. **Prototype a multiple-comparison-aware / null-calibrated signal.** Score each pair by how surprising
   its fitness is vs a null distribution of noise pairs, corrected for the number of pairs tested. This
   is the one untried lever for the false-positive effect (making the true pair stand out among many).
2. **Run the established-method comparison** (our full pipeline vs k-means, spectral, HDBSCAN, SUBCLU,
   HTC, oblique trees / exKMC) under the fair protocol. This is the comparison that decides the paper.
   Note: exKMC would not pip-install in the sandbox; may need the user's environment or a proxy.
3. **Sensitivity analysis** on k (kNN graph) and core_k (density) - currently untuned defaults.
4. **Wire the graph-cut+density signal into the main pipeline** - it currently lives only in the
   experiment scripts (run_fitness*.py, run_ea_newfit.py), not in atomicplus/.
5. **Decide the paper framing with Ting** (traveling as of last update) using docs/ting-brief.md.
6. Only if pursuing higher-order interactions: acknowledge it as an open hard problem, do not expect the
   EA to crack it.

--------------------------------------------------------------------------------
## 7. Key numbers to remember
- graph-cut+density selection (20 seeds): reliable on circles/moons/jain/spiral at low p; degrades to
  ~0.6-0.8 by p=40 on jain/spiral; flame ~0 always.
- Best end-to-end recovery with the right split: circles 1.0, moons 0.92, jain 0.90, gauss2 1.0 (low-mod p).
- EA vs random on the good fitness (fixed budget 400): essentially tied; both fade as p grows
  (moons random 0.68->0.34->0.05 at p=12/20/40); fair greedy = 0 on all non-convex; ceiling holds on
  moons/circles (~0.6-0.8 at p=40) but fades on jain.

--------------------------------------------------------------------------------
## 8. Experiment / script index
- `scripts/run_fitness_sweep.py` - the KEY positive result: graph-cut selection across shapes x p. Run:
  `python scripts/run_fitness_sweep.py --seeds 20 --ps 12,20,40 moons circles jain flame spiral gauss2`
- `scripts/run_fitness.py` - compares selection signals (gap, density, graphcut, hybrids) by rank-1 rate.
- `scripts/run_ea_newfit.py` - EA vs CVT-MAP-Elites vs (fair SFS) greedy vs random vs enum2-ceiling, all
  on the graph-cut+density fitness, sweeping p. Shows the EA does not beat random even with a good signal.
- `scripts/run_signals.py` - earlier signal comparison (persistence vs density vs cut/within) diagnosing
  why persistence fails.
- `scripts/run_diversity.py` (`--big`) - the fair "why EA / diversity" test (negative result).
- `scripts/run_qd.py` - MAP-Elites / CVT-MAP-Elites diversity test (negative result).
- `scripts/run_needle_scaling.py` - needle budget-scaling (EA vs random vs greedy on nested spheres).
- `scripts/run_connectivity.py`, `scripts/run_benchmark.py`, `scripts/demo_fairness.py` - earlier
  connectivity-niche and fair-benchmark harnesses.
- `docs/experiments/exp-001..exp-015` - narrative findings, in order. exp-011..015 cover the connectivity
  diagnosis, the failed EA/diversity claim, and the split/selection isolation.

--------------------------------------------------------------------------------
## 9. People / process
- Enrong (student), Ting Hu (advisor, PI), Ryan Zhou (lab PhD; proposed the graph-cut + density hybrid,
  which is the current best signal). Enrong runs the heavy multi-seed batches manually; the cowork
  session builds and validates small, then hands off commands. Always be honest about limitations; the
  lab explicitly wants to avoid making baselines look artificially bad OR artificially good.
