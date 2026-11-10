# ATOMIC+: status and a request for direction

> **CORRECTION NOTICE (2026-08-05).** Historical record only. Its central scope claim — "lean on
> where ATOMIC+ genuinely partially works: convex / redundant subspace structure", and "no selection
> signal reliably picks the informative subspace on non-convex data" — is **backwards**. On the
> repaired benchmark, rank-1 selection accuracy is 0.97-1.00 on all four non-convex shapes and the
> convex control is the case where selection buys nothing. See `docs/CORRECTIONS.md` C1. The paper
> framing is superseded by `docs/ting-meeting-2026-08-05-interpretability-reframe.md`.

## The short version
I've built and stress-tested the ATOMIC+ ideas fairly thoroughly, and I've run into a wall on the
*core* novelty. A lot of solid, honest results came out of the process, but I can't currently point
to a single contribution that is at once **novel, working, and defensible**, and I'd value your read on
how to frame this or which direction to take. Both the useful findings and the problems are below.

## What we set out to do
Extend ATOMIC (evolutionary search over feature subsets + topological/connectivity clustering) with a
continuous **persistence fitness**, a **recursive interpretable tree** with per-split feature panels,
and a **fair evaluation** protocol.

*A note on the test data:* throughout, I test on standard 2D non-convex clustering shapes, embedded in
extra noise features so the method has to find the two informative dimensions among many. The shapes are
**moons** (two interleaving crescents), **circles** (two concentric rings), **jain** (two crescents of
unequal density), and **flame** (two clusters that nearly touch).

## What holds
- **Fair-evaluation finding.** ATOMIC's original wins lean partly on a metric-space confound:
  silhouette / Davies–Bouldin are computed in the low-dim subspace ATOMIC itself selects, which
  flatters it. Scoring every method in the *same* subspace (plus a permutation null and subsample
  stability) neutralizes this. 
- **A precise diagnosis.** I can show *why* the natural topological objective (MST edge-gap
  persistence) fails when used to *select* a subspace: it scores a **correct** non-convex split as
  "no gap" about half the time (within-cluster edges are as long as the between-cluster bridge), so
  noise features with tiny spurious gaps win. 
- **Interpretability.** The method returns small, named feature panels, and on synthetic data the
  recursive tree recovers the known hierarchies (partially, not on all synthetic data but some easier ones). The panels are interpretable because they're small, 
  though on real data we can't confirm they're the *right* features, since there's no ground truth to check against.
- **An existing density-based approach is the most promising fix.** A density-based validity picks the
  right subspace better than our persistence signal on clear-gap cases (e.g. circles), and HDBSCAN-style
  splitting handles shapes single-linkage can't (e.g. jain). Two caveats, expanded below: it doesn't
  generalize across all cluster shapes, and it isn't *ours*; it's essentially existing density-based subspace clustering.

## Where it breaks
- **The evolutionary search doesn't obviously help.** We tested plain search, diversity of
  panels, deceptive landscapes, high-dimensional recovery, and modern quality-diversity (MAP-Elites,
  CVT-MAP-Elites). Random search and greedy **match or beat** the EA everywhere. The reason is structural:
  the persistence landscape is a cliff, not a slope, so there are no partial-progress "building blocks"
  for evolution to recombine. For example, if the true panel needs 3 features, 1 feature gives ARI ≈ 0.01
  and 2 features still ≈ 0.01, but 3 features jump to ≈ 0.99 (ARI: 1 = perfect, 0 = chance). With no
  gradient to climb toward, the EA is no better than random search. (the persistence score does not rise gradually as the search adds or removes one feature at a time. On jointly necessary structure, every subset that is missing even one required feature sits near the floor, and the score only jumps once all the required features are present together. So there is no partial signal for the search to climb.)
- **The topological objective is unreliable for its target.** On non-convex data it picks the wrong
  subspace ~half the time, and no criterion I tried (persistence, permutation-null, stability) fixes it.
- **The split is fixable, and fixing it isolated the *real* crux: subspace selection.** Swapping the
  single-linkage persistence cut for HDBSCAN-style density stability rescues the split (jain 0.90,
  moons 0.97, circles/flame partial) *given the true features*. But end-to-end still collapses,
  because **no selection signal reliably picks the informative subspace on non-convex data**. I
  tried persistence, permutation-null, subsample-stability, HDBSCAN-score, and DBCV, and each works
  on some cluster shapes and fails on others. This looks like a genuinely hard problem: unsupervised
  cluster-validity is unreliable, noise subspaces produce apparent clusters, and beating all C(p,2)
  of them is a multiple-comparisons problem that worsens with dimensionality.
- **The fix that works isn't novel.** The reliable signal is density-based validity, which is exactly
  what density-based *subspace* clustering already does: **SUBCLU** (Kailing, Kriegel & Kröger, 2004)
  and successors find arbitrary-shaped clusters in feature subspaces via density-connectivity.
- **Novelty is narrower than we thought.** Each ingredient is largely covered: **HTC** (2026) does
  topological hierarchical clustering; **oblique clustering trees** (KDD 2022) do interpretable
  per-node feature-subset splits; **ChameleoClust** does evolutionary subspace clustering; **SUBCLU**
  does density subspace clustering. Our "novel synthesis" sits in the gaps between these. Originally if ATOMIC+ works, we have this method as our novelty, but now the algorithm does not seem to work as we'd expect, I am a bit uncertain. 

## Where I'm stuck
The core method/novelty claims (evolutionary + topological) doesn't work; the version that works (density validity)
isn't novel; and each remaining asset (fair evaluation, interpretable tree) has prior art. I can't
currently locate a contribution that is simultaneously novel, working, and defensible, hence this memo.

## Possible directions 
- **A benchmark and analysis paper, instead of a new method.** If framing towards benchmark, we could build on the synthetic datasets I
  made, where we know exactly which features carry the clusters and how many are truly needed. Because we
  know the answer, we can measure two things that most evaluations mix together: whether a method can
  *find* the right features, and whether it can *separate* the clusters once it has them. The main finding
  would be that finding the right features is the harder, still unsolved step, so the negative results
  become the point of the paper rather than a weakness. I would need to read up on how benchmark papers
  are structured, and show clearly how ours differs from OpenSubspace, the existing benchmark in this area.
- **A scoped method paper.** Lean on where ATOMIC+ genuinely partially works: convex / redundant subspace
  structure, with the small interpretable panels, the recursive tree, and fair evaluation, and present
  the non-convex difficulty as an analyzed limitation. Maybe we could also try it on the real patients data to see how it performs, although we may not be able to clearly rate how well are the features it gives, but worth a try. 
- **Any other directions I cannot think of now** 

I'm genuinely unsure which of these is worth pursuing, or whether there's a stronger angle I'm not
seeing, that's the main thing I'd value your read on.


