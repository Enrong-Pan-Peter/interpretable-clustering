# exp-018 — Does the fitness give a search anything to climb? No: the blocker is dilution, not gradient

**Date.** 2026-07-30. Script: `scripts/run_signal_landscape.py` (Ryan's test).
Data: `results/signal_landscape.csv` (373,600 subsets; 5 shapes, p=20/40, k=1..5, 10 seeds, both
the old and new junk-column benchmarks).

**Test.** Everything the pipeline currently does is ENUMERATION: score all C(p,2) pairs, take the
best. That only works because we told the method the answer is a pair. A real search needs the
fitness to rise as a panel gets CLOSER to the truth, not just when it is exactly right. So within
each panel size k, group subsets by how many of the two true features they hold — t=0 (junk),
t=1 (halfway), t=2 (has both) — and compare their score distributions. Cohen's d throughout.

Uses the RAW graph-cut and density terms, NOT the z-scored hybrid: the z-score is relative to
whatever pool it compares, so it would erase the very differences under study. All comparisons
are WITHIN a panel size (raw scores are not comparable across sizes). Stratified sampling is
mandatory — at k=3, p=40 a uniform draw holds both true features only 0.4% of the time.

## 1. The gradient is real but too shallow, and lives in only one term
Non-convex shapes only (gauss2 excluded, see §3), new benchmark, d(t=1 vs t=0):

| term | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| density | **0.41** | 0.25 | 0.22 | 0.17 |
| graph-cut | 0.22 | 0.12 | **-0.06** | **-0.20** |

Pre-registered bar was d > 0.5 = "a slope a search could follow". Density peaks at 0.41 and
decays. **It fails the bar we set in advance.**

Graph-cut goes NEGATIVE at larger panels — a subset holding one true feature scores *worse* than
pure junk. Per shape it is stark: moons runs 0.06 / -0.19 / -0.31 / -0.38 as k grows, spiral
similar. A search following graph-cut on those shapes is pushed AWAY from the answer. Only jain
(0.39/0.44/0.22/0.06) and circles get positive signal from it, and only at small k.

Top-10% enrichment (closer to what a search exploits) agrees but is kinder: density beats its
base rate by +0.12 to +0.18 consistently, graph-cut by ~0 (-0.03 to +0.05).

## 2. THE FINDING: the blocker is dilution, not gradient
d(t=2 vs t=1) — what the exact true panel buys over a partial one:

| term | k=2 (exact pair) | k=3 (pair + ONE junk column) | k=4 | k=5 |
|---|---|---|---|---|
| density | **3.13** | **0.48** | 0.31 | 0.26 |
| graph-cut | 3.71 | 1.23 | 1.23 | 1.35 |

The exact pair produces an enormous signal. Add **one** junk column and density drops 85%. The
correct answer carrying a single irrelevant feature is nearly indistinguishable from a panel with
only one true feature.

So the problem was never "no gradient toward the truth". It is **no tolerance for extra
features.** The fitness fires only when the panel is exactly right. That is exactly why
enumerating exact pairs works and search does not: any search passes through panels carrying
junk, and there the signal has already evaporated.

Mechanism is mundane — distances are computed over every column in the panel, so each junk column
adds noise to every pairwise distance. Curse of dimensionality operating INSIDE the panel.

## 2b. Does COMBINING the two terms help? Only for detection, not for guidance
Each term standardised against the junk (t=0) group within each cell, then summed. (Standardising
against junk rather than the whole pool keeps the weighting independent of how we sampled the
other groups -- the pipeline's usual z-score is pool-relative and would not be safe here.)

**One true feature vs none — the gradient a search would climb**

| | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| graph-cut | 0.22 | 0.11 | -0.06 | -0.21 |
| density | 0.41 | 0.25 | **0.22** | **0.18** |
| combined | **0.46** | **0.28** | 0.12 | -0.01 |

**Both true features vs one — detecting that you have arrived**

| | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| graph-cut | 3.70 | **1.22** | **1.21** | **1.30** |
| density | 3.12 | 0.48 | 0.31 | 0.26 |
| combined | **5.10** | 1.22 | 1.06 | 1.08 |

Clean division of labour, and it settles how to use the two terms:
- For **guidance**, combining beats either term at k=2 (0.46) but is WORSE than density alone by
  k=4/5 (0.12 and -0.01 vs 0.22 and 0.18) — graph-cut's negative gradient drags the sum down.
- For **detection**, combining is best at k=2 (5.10, better than either alone: the terms are
  genuinely complementary there) and at k>=3 the combination just tracks graph-cut, which carries
  it entirely.

So: **search on density, confirm with graph-cut.** The equally-weighted hybrid is the wrong object
for a search even though it is the right object for ranking exact pairs.

Per shape, combined, both-vs-one: circles 6.03 -> -0.08, spiral 4.62 -> 0.25 (both collapse the
moment a junk column is added); jain 4.64 -> 2.23 and moons 5.13 -> 2.49 hold up better. So the
dilution problem is worst exactly on the shapes where the graph term matters most.

## 3. Two controls worth recording
- **Convex control.** gauss2 averages d = **+7.3** where the non-convex shapes average +0.3. Both
  terms have an enormous gradient on convex data. The gradient problem is specific to non-convex
  structure — a clean scope statement. (This also caused a reporting bug: the script's first
  verdict block averaged gauss2 in and made everything look like a pass. Fixed; the verdict now
  excludes it and reports it separately. Do not average the convex control into anything.)
- **The old benchmark reverses the signs.** On uniform junk, density's gradient is NEGATIVE
  (-0.34) and graph-cut's is POSITIVE (+0.07 to +0.20) — the exact opposite of the fixed
  benchmark. Yet another reason nothing measured on the old junk carries forward (see exp-017
  and the benchmark flaw).

## Verdict
- Phase 2 as planned (SFS / backward elimination / random at matched budget on this fitness) is
  **NOT justified** by the pre-registered thresholds. It would fail, and we can now predict why,
  so running it would only confirm what we already know.
- The next experiment is upstream: **make the score tolerant of irrelevant columns inside the
  panel.** If the 3.13 -> 0.48 collapse can be flattened, search becomes viable and phase 2
  becomes worth running. Candidates: within-panel dimension weighting, distances robust to
  irrelevant dimensions, subspace-local metrics.
- For search purposes the equally-weighted hybrid is half anti-signal. Any search should be
  driven by the DENSITY term, with graph-cut used only to confirm on arrival.
- **Do NOT "fix" this with a panel-size penalty.** It works by baking in "the answer is small",
  which is the same knowing-the-answer we criticised in the enumeration setup. It would improve
  the benchmark numbers without making the method able to handle a real panel of unknown size.

## Not answered here
Whether the score peaks at the CORRECT panel size. That is a cross-size comparison and raw scores
are not comparable across sizes; it needs an absolute (scramble-calibrated) score. Separate
experiment — do not infer it from these tables.
