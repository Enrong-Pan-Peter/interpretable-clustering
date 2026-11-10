# exp-011 — Why the connectivity niche is narrow (three distinct mechanisms)

> **CORRECTION NOTICE (2026-08-05).** Three of this document's four regime conclusions are
> falsified by the 20-seed runs. moons is not a coin-flip (repaired end-to-end ARI 0.962); jain's
> "even the oracle pair reaches only 0.29-0.35, no search or fitness change can fix this" is wrong
> (HDBSCAN given the true pair reaches 0.902, DBSCAN 0.973 — a *splitter* change fixed it); the
> circles "clean win vs baseline 0.48" understates the baseline by about half; and the flame
> "true subspace yields ARI 0.95" is reproduced by no result file (best is 0.665). This document
> analyses the **persistence** fitness at p=10 and its conclusions do not transfer to the
> graph-cut + density hybrid. See `docs/CORRECTIONS.md` C4.

**Question.** The 10-seed connectivity batch gave circles 0.70 (7/10), moons 0.50 (5/10),
jain 0.115 (0/10, loses to DBSCAN-sub 0.32), flame -0.01 (0/10). Is this seed luck, a
fitness bug, or a model limit? Diagnosed by *enumerating all C(10,2)=45 feature pairs*
and scoring each with `persistence_split` — removing the EA/search from the question.

Config: fitness=persistence, min_cluster_size=8, core_k=5, mutual_reachability=True,
normalize=ratio; true informative dims = {2,7}; p=10 (8 uniform-noise dims).

## Finding: the batch is fully explained by the *fitness landscape*, not the search.
"ARI of the argmax-persistence pair" = what a perfect EA maximising fitness would get:

| dataset | argmax-score ARI | truth {2,7} ARI | oracle (best-ARI any pair) | mechanism |
|---|---|---|---|---|
| circles | 1.00 (rank 1/45) | 1.00 | 1.00 | **works** — true gap is salient |
| moons | 0.67 (rank 1 on 2/3 seeds) | ~1.00 | ~1.00 | **coin-flip** — true gap borderline vs noise |
| flame | ~0.00 (rank ~28/45) | **0.95** | 0.95 | **fitness misranks** — see below |
| jain | ~0.08 | 0.26 | 0.35 | **model wrong** — see below |

## Mechanism 1 — flame: the fitness actively prefers noise over a correct answer.
The true subspace {2,7} yields a split with **ARI 0.95** (the cut is in the right place),
but its persistence score is exactly 1.000 and it ranks ~28/45. A {signal, noise} pair
scores higher because a high-variance uniform-noise dimension manufactures a *larger*
MST top-edge gap than flame's compact (small-gap) crescent separation. So maximising raw
persistence picks noise → ARI 0. **This is a describable methodological weakness, not a bug:
a single MST edge-gap in a subspace containing a noise dim is noise-gameable.**

## Mechanism 2 — jain: single-cut model is wrong for unequal-density crescents.
Even the *oracle* pair reaches only ARI 0.29–0.35; truth {2,7} = 0.26. A single top-edge
cut cannot carve jain's two unequal-density crescents (single-linkage chaining). No search
or fitness change can fix this — the signal isn't recoverable by one persistence cut.
DBSCAN-in-subspace (0.32) wins because density tracing follows the crescent. Honest scope limit.

## The "obvious" fixes DON'T work (tested — guarding against benchmark-hacking).
- **Normalization** (ratio→median→raw gap, ±mutual-reachability): flame argmax-pair stays
  ARI≈0 under all four. The true gap is genuinely *smaller* than noise outlier gaps; no
  monotone rescaling reorders them (diag_norm.py).
- **Subsample stability** (rank pairs by reproducibility instead of score): ALSO gameable.
  Noise is *fixed per dataset*, so its spurious split reproduces under subsampling
  (stability 0.79–0.91, ARI≈0). Stability rescued moons-seed-1 but BROKE both circles seeds
  and did not fix flame (diag_stab.py). Neither raw persistence nor stability alone is a
  clean selector.
- Only a **column-permutation null** (permute each column independently → destroys the joint
  2-D crescent while preserving marginals) is principled: a noise "split" survives permutation
  (marginal outliers), a real crescent does not. But it's expensive (a null estimate per
  candidate) and would be a substantial, pre-registered architecture change — not a quiet patch.

## Takeaway
The connectivity niche is real but narrow: **circles = clean win** (0.70 vs best in-subspace
baseline 0.48), **moons = coin-flip** (ceiling ~0.67), **flame = fitness-misrank**,
**jain = out-of-model**. This is a complete, honest "operating-regime" characterisation of when
persistence-based subspace clustering works. Scripts: diag_landscape.py, diag_norm.py, diag_stab.py.
