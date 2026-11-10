# ATOMIC+

**The idea:** take ATOMIC — a clustering method that finds the *minimal set of named features* that makes a group a distinct cluster — and give it a real objective, a fair evaluation, and a recursive tree. Target: a GECCO 2027 methods full paper.

---

## 1. What ATOMIC is

- Answers **"which few variables make this group its own cluster?"** — not just "what are the clusters" (k-means, DBSCAN).
- **Interpretable, not very explainable:** understand how the splits are made, the selected features *are* the explanation, but no idea what cluster 2 represents.
- Mechanism: a solution = a subset of features → build a nearest-neighbour graph in that subspace → a subset **isolates a cluster** when the graph splits into **exactly 2 components**. Fitness = hit 2 components with as few features as possible. An evolutionary search returns diverse splits.
- Published GECCO 2024 (4-page short paper); reported beating k-means / GMM / DBSCAN on silhouette & Davies–Bouldin on UCI data.

## 2. Problems with the original

- **Unfair evaluation.** Silhouette / Davies–Bouldin depend on the space they're measured in. ATOMIC scores itself in its own low-dim subspace, baselines in full space → the "win" may be a measurement artifact.
- **Flat objective.** `−(C−2)²` is integer — every clean 2-component split ties, so the search has no gradient.
- **Thin "topology."** Just connected components at one scale ≈ single-linkage → chaining and degenerate "isolate one outlier" splits.
- **Binary only.** One split at a time; no way to build a full hierarchy.
- **Operators fight parsimony.** Union crossover only grows feature sets.
- **Thin validation.** Single runs, no significance tests, all baselines non-interpretable.

## 3. What ATOMIC+ changes

- **Fair evaluation:** score all methods in the same space; add external metrics (ARI/NMI vs. labels); ~30 seeds + significance tests; a permutation null test.
- **Continuous persistence objective:** replace the flat count with a smooth "how wide is the gap between the clusters" score → gives the search a gradient. we form a MST in the feature subspace, use the difference of the largest weight edge and the second largest weight edge as a persistence score. Formula: `S = e₁ − e₂`, the gap between the two largest MST edge weights (cut `e₁` to get the two clusters; bigger gap = cleaner split).
- **Acceptance gate:** keep a split only if it beats the null (permutation shuffle of feature cols/rows) *and* reproduces under subsampling.
  - *Null permutation test:* shuffle each feature to destroy real structure, re-run the search on the scrambled data — if the split's score doesn't stand out from what the search finds on noise, it isn't real.
  - *Stability gate:* re-run on random subsamples of the data — a real split keeps giving the same partition; a lucky one doesn't.
- **Recursive tree (the product):** split → recurse → one hard-partition tree, each node labelled with its own features. Beam search (probe for next level splits) + gate guard against a bad early split. (if persistence drops below a threshold)
- **Better operators:** set/uniform crossover (different crossover + larget feature set) + asymmetric mutation (bias toward dropping features).
- **Diversity:** returns several equally-valid minimal feature panels per split — greedy can't.
- Validate on synthetic + UCI, plus a demo on an easier biomedical or suitable UCI dataset.

## 4. Findings so far

- **Metric-space suspicion confirmed.** Scored in the same space, ATOMIC no longer beats k-means/GMM; high silhouette often comes with ARI ≈ 0 (looks cohesive, doesn't match real structure). The paper's biggest win (Biodegradation) fails the null → artifact. Its one real success (Ceramic) ties k-means and wins only on interpretability.
- **Persistence fixes the flat-fitness failure.** Where the old objective picked pure noise (ARI 0.01), persistence recovers the true split (ARI 1.0).
- **Objective alone isn't enough** — it can still find clean-looking splits in shuffled data. The null + stability gate is mandatory. Two parts: objective *finds* structure, gate *certifies* it.
- **Recursive tree works.** Recovers a known 3-level hierarchy exactly (ARI 1.0); beam + gate beats greedy on deceptive cases.
- **The EA's edge is diversity, not raw quality.** On a simple split, greedy matches or beats it and is cheaper. The EA's real edge: many alternative panels per split (7 vs. greedy's 1).
- **Emerging niche: non-convex clusters hidden in noise.** On "moons" buried in noise dims, k-means/GMM fail; DBSCAN/HDBSCAN work only if handed the right features; ATOMIC finds the named features *and* clusters them (ARI 1.0).

## 5. Open problems

- **Justifying the EA over greedy** — rests on diversity, non-convex-in-noise, and the tree; the full benchmark has to confirm it.
- **Non-convex is fragile** — works only up to a noise ratio; salvaged with pair-seeded init (moons in noise: ARI 0 → 1.0), needs multi-seed confirmation.
- **Tree look-ahead blind spot** — a 1-step look-ahead can't fully overcome a high-persistence split that fragments real clusters.
- **Pending:** full 30-run benchmark + significance tests, null test on the rest of UCI, a scalable version of the objective.
