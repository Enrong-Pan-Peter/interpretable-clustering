# exp-010 — ATOMIC's genuine niche: non-convex clusters in a noisy subspace

> **CORRECTION NOTICE (2026-08-05).** 1-seed result; do not cite its table. Its "alternative panels
> (diversity)" differentiator was retracted by a fair test (HANDOFF §3b.3, and the 20-seed QD runs).
> Its "k-means/GMM fail outright" is softer on the repaired benchmark, where full-space k-means
> reaches moons 0.492 and jain 0.442. The DBSCAN/HDBSCAN-fail-in-full-space claim HOLDS strongly.
> See `docs/CORRECTIONS.md` C6.

**Status:** promising (1 seed; confirm multi-seed). **Phase:** 1 (positioning). **Datasets:** moons/circles/… in subspace.

## The question
Where does ATOMIC *actually* win? Hypothesis (from exp-009 + the UCI benchmark): ATOMIC targets
clusters that are **dense regions separated by a gap** (incl. non-convex/manifold shapes) living in
a **feature subspace among noise** — not compact/overlapping statistical categories (glass/ionosphere).

## Result — moons in a noisy 10-D subspace (informative dims [2,7])
ATOMIC (pair-seed) found V=[2,7], ARI=**1.00**, with 2 named features. Baselines, full space vs.
re-fit in ATOMIC's subspace:

| method | ARI full | ARI in V=[2,7] |
|---|---|---|
| **ATOMIC** | **1.00** | — |
| k-means | 0.47 | 0.19 |
| GMM | 0.48 | 0.34 |
| DBSCAN | 0.02 | 0.59 |
| spectral | 0.39 | 0.27 |
| HDBSCAN | 0.00 | **0.93** |

## Why this is the story
1. **k-means/GMM fail** (non-convex, compactness assumption wrong).
2. **DBSCAN/HDBSCAN fail in full space** — the noise dims drown the density signal.
3. **Given ATOMIC's subspace, HDBSCAN recovers (0.93)** — the density methods *can* cluster moons,
   but only if handed the 2 right features. **They cannot find those features themselves.**
4. **ATOMIC finds the 2 named features AND clusters them (ARI 1.0), interpretably**, plus offers
   alternative panels (diversity). That is a capability greedy / k-means / DBSCAN / spectral lack.

So ATOMIC's honest, defensible claim is **interpretable subspace selection for connectivity
clustering**: on non-convex structure buried in noise, it recovers *which* few named features
define the clusters — where black-box density methods need that subspace handed to them and never
name it, and centroid methods fail outright.

## Next
- Confirm multi-seed on moons + circles + spiral + flame (subspace-embedded), reporting ARI +
  #features + diversity, with DBSCAN/HDBSCAN/spectral scored full-space AND in-subspace.
- This is the connectivity benchmark that anchors the paper's "where ATOMIC wins" section; the UCI
  results become "connectivity clustering finds different structure than compactness labels" (fair-
  eval framing), not a loss.
