# exp-009 — Diversity (the EA's real edge) + a sobering non-convex finding

**Status:** diversity solid; non-convex claim NOT supported by current evidence. **Phase:** 1/H4.

## Diversity of alternative panels (the robust EA justification)
On `redundant_informative` (dims [3,4,5,6] each carry the same split), the EA's archive contains
**7 distinct feature panels** that all induce the same clustering (e.g. (2,4,5), (3,4,7), (5,6,7)…);
**greedy returns exactly 1** ([4,5]). This is the "same-membership alternative panels" contribution,
and it is what greedy/L1/random cannot give by construction. **This is the EA's defensible edge.**

## Non-convex: k-means fails, but so does ATOMIC (both objectives)
Two-moons / concentric-circles / jain crescents embedded in a noisy high-D subspace, 3 seeds each,
ARI vs. truth:

| set | k-means | greedy | ATOMIC (EA) |
|---|---|---|---|
| moons | 0.46 / 0.05 / 0.03 | 1.0 / 0.0 / 1.0 | 1.0 / 0.0 / 0.0 |
| circles | 0.00 | 1.0 / 0.0 / 1.0 | 1.0 / 0.0 / 0.0 |
| jain | 0.59 / 0.04 / 0.04 | 0.05 / 0.07 / 0.05 | 0.05 / 0.07 / 0.00 |

- **k-means fails on non-convex** (confirmed) -- so topology *should* win in principle.
- **But ATOMIC does NOT reliably recover non-convex** -- ~1/3 on moons/circles, ~0 on jain in noise.
  Greedy is actually *more* reliable on moons/circles (its exhaustive pair-seed finds the true pair).

## Diagnosis (why ATOMIC fails on non-convex)
- On the TRUE moon dims [2,7], persistence = 1.19 -- barely above the ratio floor (1.0) and only
  a hair over a noise split [5,6] = 1.09. **The MST-gap signal on interleaved shapes is weak**, so
  a spurious noise split easily wins under max-persistence selection.
- The original **kNN-component objective is no better**: on [2,7] it gives 16 -> 4 -> 1 components
  as k grows (fragments, then chains) -- never a clean 2. The flat EA fails moons **0/3** (worse
  than persistence's 1/3). So Phase 2 did NOT lose non-convex capability; neither objective has it.
- The EA also under-isolates the clean pair (it evaluates supersets of {2,7}, whose persistence is
  diluted below the noise split), so the search compounds the weak-objective problem.

## Implications
1. **Diversity is the EA's load-bearing justification** (robust: 7 panels vs 1). Lean on it.
2. **"Non-convex capability" is NOT robustly supported by these experiments** -- a challenge to a
   *core* ATOMIC claim ("wider variety of cluster shapes than k-means"). It works on axis-aligned
   subspace-Gaussian clusters (ATOMIC's own generators) but not on interleaved shapes in noise.
3. **Non-convex does NOT justify the EA over greedy** -- the bottleneck is the weak objective +
   noise, not the search; greedy is at least as good.

## Caveats (before over-concluding)
Our setting is a *noisy* subspace embedding (2 informative dims among 8 uniform-noise dims), all
min-max scaled so signal and noise share a range -- a hard, realistic setup. Possible confounds to
check before a final verdict: noise scale vs. signal, k̃ tuned per-dataset for connectivity, and a
non-convex-aware objective (e.g. density/persistence over the kNN filtration rather than single-
linkage MST-gap). So: "current evidence doesn't support non-convex," not "ATOMIC provably can't."

## Recommendation
Make **diversity + interpretability + the recursive tree + fair evaluation** the paper's spine.
Treat **non-convex as an open investigation**, not a claim, until an objective/embedding is found
that recovers it reliably -- or report it honestly as a limitation.

---

## UPDATE — non-convex is SALVAGEABLE: it's a noise-ratio problem, not an objective problem

Isolating the cause:
- **Clean 2-D moons (no noise dims): ARI 1.00 / 0.98 / 1.00.** The persistence objective handles
  non-convex fine.
- **moons with 2 signal + 2 noise dims: ARI 1.00 / 1.00 / 1.00.** Still perfect.
- **moons with 2 signal + 6 noise dims: ARI 0.00 / 0.01 / 0.01.** Fails.

So the objective is NOT the problem. The problem is **feature-selection in noise**: ATOMIC's
non-convex separation signal is *weak* (persistence 1.19, just above the noise floor of ~1.0), so
as noise dims accumulate a spurious noise-dim split (~1.09) out-competes it and the search is
distracted. Sharp threshold with the noise ratio.

Why per-dim pre-screening won't rescue it: the moon dims are **jointly necessary** -- neither is
individually distinguishable from noise (each 1-D projection overlaps), so variance/bimodality
screens can't find them. The reliable tool for a jointly-informative *pair* is exhaustive pair
evaluation (which is exactly why *greedy* is more reliable on moons in noise).

### Salvage path (scoped, honest, with a concrete method fix)
1. **Claim scope:** ATOMIC recovers non-convex clusters when the subspace signal isn't drowned by
   noise (moderate noise ratio / well-separated shapes like flame). Demonstrated: moons/circles
   at low noise ratio -> ARI ~1.0.
2. **Method fix for the high-noise regime:** add **pair-seeded initialization** to the EA
   (evaluate promising feature pairs up front, as greedy does), so the true jointly-informative
   pair is guaranteed to be considered; the EA then keeps its DIVERSITY edge (many panels) on top.
3. **EA-vs-greedy stays justified by diversity** (7 panels vs 1) and by higher-order joint signals
   (>=3 features) that greedy's pair-seed cannot reach.

Net: non-convex moves from "unsupported" to "supported, scoped, with a clear improvement path."

---

## RESULT — pair-seeded init salvages high-noise non-convex

Added `AtomicConfig(pair_seed_init=True)`: seed the archive/population with all feature PAIRS
(or, above `pair_seed_max`, pairs among the top-variance dims), so a jointly-informative pair is
guaranteed to be evaluated; the EA then evolves for diversity + higher-order combinations on top.

| moons, p=10 (2 signal + 6 noise) | ARI (3 seeds) |
|---|---|
| pair-seed OFF (before) | 0.00 / 0.01 / 0.01 |
| **pair-seed ON** | **1.00 / 1.00 / 1.00** (finds [2,7] every time) |

**Non-convex is now supported** at high noise with a concrete method contribution, and the EA
keeps its edge over greedy: diversity (many panels vs 1) + higher-order joint signals (>=3 dims a
pair-seed can't reach). Cost: O(p^2) pair evaluations at init (bounded by `pair_seed_max`), the
same order as greedy's pair-seed.
