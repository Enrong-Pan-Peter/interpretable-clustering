# exp-004 — Continuous persistence fitness (Phase 2): before / after

**Status:** core built + wired + validated (synthetic + Ceramic). **Phase:** 2 (the linchpin).
**Module:** `atomicplus/persistence.py`; enabled via `AtomicConfig(fitness_mode="persistence")`.

## What changed
Flat `f = −(C−2)²` → continuous **MST edge-gap**. For a feature subset V: build the MST over
the *data points* using distances in the subspace V (mutual-reachability by default), sort edge
weights e₁≥e₂≥…, and score the split by the gap at the largest **min-cluster-size-admissible**
edge, `S = e_cut / e_next` (ratio normalization). Cutting that edge gives the two clusters.
Defaults: `min_cluster_size=5`, `mutual_reachability=True`, `core_k=5`, `normalize="ratio"`.

## Core validation (no EA — just the objective)
On `two_cluster_subspace(p=12, informative=[3,7])`:

| subspace | persistence S | ARI of induced split |
|---|---|---|
| informative [3,7] | **5.89** | **1.000** |
| noise [0,1] | 1.02 (≈ ratio floor) | 0.008 |

The flat objective scored **both** of these `f=0` (a tie); persistence separates them 5.89 vs 1.02.
Min-cluster-size correctly refuses to isolate a lone outlier.

## End-to-end EA: flat vs. persistence

| dataset | mode | best features | ARI |
|---|---|---|---|
| synthetic (true dims [4,11]) | flat (`components`) | [2,5,9,16] (all noise) | **0.011** |
| synthetic (true dims [4,11]) | **persistence** | [**4**,6,**11**,15,19] (both true dims) | **1.000** |
| ceramic (Body/Glaze) | flat | [0,5,11,14] | 1.000 |
| ceramic (Body/Glaze) | persistence | [0,2,5,10,12,13,16] | 1.000 |

## Findings
1. **Persistence fixes the failure flat fitness caused.** On the synthetic set where the flat
   objective picked a spurious noise split (ARI 0.01), persistence selects both true dims and
   recovers the split at **ARI 1.0** — because the continuous score (f=1.35 vs a flat 0) gives
   the search a gradient toward the real structure. This directly answers the low-ARI concern:
   the low ARI was largely the flat objective, not an inability to find real structure.
2. **It preserves the genuinely-separable case** (Ceramic 1.0 in both modes).
3. k̃ is no longer used in persistence mode (Phase 3 dissolves), and degenerate outlier cuts
   are blocked by min-cluster-size.

## Next (the Phase-2 success criterion, from exp-003)
Run the **permutation null test with `fitness_mode="persistence"`**:
  * on synthetic / Ceramic, persistence's split must **beat** the null (real structure);
  * on **Biodegradation**, persistence should **still fail** the null (it must not manufacture
    structure the flat objective hallucinated). If persistence beats the null on more real
    datasets while still rejecting Biodeg, Phase 2 has done its job.

## Caveats
- Persistence carries extra filler features (weak parsimony pressure → Phase 5 operators).
- Per-eval cost O(n²) (pdist + MST): fine for small-n biomedical; heavy for large n (Ozone
  n=5070). Add a kNN-sparse MST approximation before large runs.
- `ratio` normalization can be large when e_next→0; that's a genuinely clean split, but watch
  the dynamic range when comparing across subspaces.

---

## Persistence vs. the null (Phase-2 success criterion) — partial (2026-07-08)

Same permutation-null + subsample-stability as exp-003, now with `fitness_mode`:

| dataset | fitness | real sep | null sep | null≥real | partition stability |
|---|---|---|---|---|---|
| synthetic [4,11] | persistence | 0.488 | 0.383 ± 0.044 | 0/8 (~2.4σ) | — |
| Ceramic | flat | 0.383 | 0.19 ± 0.12 | 0/15 | 0.78 |
| **Ceramic** | **persistence** | **0.556** | **0.257 ± 0.08** | **0/8 (~3.7σ)** | **1.000** |
| Biodeg (full, 99 perms) | flat | 0.579 | 0.503 ± 0.118 | 12/99, p=0.13 | 0.50 |
| Biodeg (full, 99 perms) | persistence | 0.579 | 0.541 +/- 0.036 | 15/99, p=0.16 | 0.63 |

## Conclusion (2026-07-08) -- Phase 2 validated

Persistence **beats the null on real structure** (synthetic ~2.4 sigma; Ceramic ~3.7 sigma,
partition stability 1.00) and **still rejects the artifact** (Biodeg full: real 0.579 sits
inside its null 0.541 +/- 0.036, 15/99 perms match, p=0.16 -> not significant, like the flat
objective's Biodeg p=0.13). Best-case outcome.

**Key nuance:** persistence is *better* at finding gaps, so it reports a cohesive split
(silhouette 0.58) on Biodeg even after permutation (null mean rises 0.503 -> 0.541, tightens to
+/- 0.036). The real value does not stand out from that null. So **the continuous objective
alone does NOT distinguish real structure from an artifact** -- the permutation-null + partition-
stability gate is *mandatory*, not optional.

**The method is two parts:**
1. **Search objective** = continuous MST persistence (the gradient; recovers real structure the
   flat objective missed -- synthetic ARI 0.01 -> 1.00).
2. **Acceptance gate** = permutation-null significance + partition stability (rejects the
   cohesive-but-spurious splits either objective can manufacture -- Biodeg).

Maps onto the planned Phase-4 "stability gate", now a **null + stability gate**: commit a split
only if it (a) has top persistence, (b) beats the permutation null, (c) reproduces under
subsampling. Phase 2 is done; the gate becomes part of Phase 4 recursion.
