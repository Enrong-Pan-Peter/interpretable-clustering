# exp-016 — A working selection signal: graph normalized-cut + density (Ryan's hybrid)

> **CORRECTION NOTICE (2026-08-05).** The headline sweep line is stale and three of its figures were
> wrong even against the benchmark it describes. Repaired-benchmark rank-1, p=12/20/40: circles
> 1.0/1.0/1.0, gauss2 1.0/1.0/1.0, moons 1.0/1.0/0.90, jain 1.0/1.0/0.95, spiral 1.0/0.95/1.0,
> flame 0/0/0. "Degrades gracefully with p" was mostly the leak. "flame is unrecoverable" is
> contradicted (0.665 given the true pair). The core conclusion — the hybrid largely solves
> selection, and beats either term alone — HOLDS and is understated by the old numbers.
> See `docs/CORRECTIONS.md` C2, C3 and `docs/experiments/exp-020-per-shape-audit-subclu-flame-splitter.md`.

**Motivation.** exp-011..015 concluded the crux is SUBSPACE SELECTION for non-convex structure, and
that the MST edge-gap persistence fitness is too weak (noise-gameable). Lab-mate Ryan Zhou suggested
three fixes: use more of the edge distribution, add a density term, and use the full neighbour GRAPH
(not the tree) with a graph cut. We tested all three.

## The persistence gap fitness is genuinely weak (confirmed)
On moons the true pair's raw gap e1-e2 is about 0.008 (ratio e1/e2 = 1.078); a random NOISE pair
already scores ~0.003 (ratio 1.027). Adding a single noise feature to the true pair drops its gap to
~0.002, i.e. below the noise level. So the signal barely clears noise in BOTH raw and ratio form, and
switching the ratio back to the raw difference does not help. The default is `normalize="ratio"`.

## What each of Ryan's ideas did — rank-1 selection rate (true pair scores highest)
- **More edges** (median-normalised gap; between-cluster gap / median within-cluster edge): each helps
  ONE shape but not both (median helps circles, cut/within helps moons). Shape-specific.
- **Density** (DBCV-style: (min between-cluster mutual-reach − max within-cluster MST edge)/max): helps
  circles, not moons.
- **Graph cut** (−NCut of the spectral bipartition of the kNN graph): the big winner.
- **Hybrid** z(graphcut) + z(density): best overall, and it beats graph-cut alone (which fails the
  convex control gauss2 and fails spiral at high p). The density term is what fixes those.

## Overnight sweep (20 seeds, p in {12,20,40}) — hybrid rank-1 selection rate
circles 1.0/1.0/0.9 · gauss2 1.0/1.0/1.0 · moons 0.90/0.90/0.80 · jain 1.0/0.90/0.65 ·
spiral 1.0/0.95/0.60 · flame 0.0/0.0/0.0. Near-perfect at low p on 5 of 6 shapes; degrades gracefully
with p; flame never. This is the first signal that reliably finds the informative features across most
non-convex shapes, and it largely SOLVES the selection problem we had called the unsolved crux.

## End-to-end recovery (graph-cut selection + best split)
The split is shape-dependent: HDBSCAN wins jain/moons, spectral wins circles. Best recovery ARI:
circles 1.0, gauss2 1.0, moons 0.92, jain 0.90 at low-to-moderate p. So there is now a WORKING pipeline
on most non-convex shapes, which we did not have before.

## Caveats (do not oversell)
- The primitives (normalized cut = spectral clustering; DBCV density validity) are established, so the
  novelty is in the assembly and the interpretable-subspace framing, not the clustering core (cf. SUBCLU).
- k (kNN graph = 10) and core_k (density = 5) are conventional defaults, untuned; sensitivity unknown.
- flame is unrecoverable for any gap/connectivity method (its clusters touch).

Scripts: `run_fitness.py`, `run_fitness_sweep.py`.
