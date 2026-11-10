# exp-021 — Per-panel calibration gives a stopping rule, on the density term only

**Date.** 2026-08-06. Script: `scripts/run_calibration.py`. Method:
`atomicplus/evaluation/calibration.py`. Data: `results/calibration.csv` — 200 cells
(4 non-convex shapes + gauss2 control) × p = 20/40 × 20 seeds, B = 30 permutations per panel,
27,035 rows, 7,369 s at `--jobs 8`.

**Why.** The goal is a recursive tree whose every node names a few columns and splits the rows.
Every node must choose a panel of unknown size, and until now we could not: exp-018 showed our
scores are z-scored against a pool of same-size candidates, so a 2-column score and a 4-column
score sit on different scales and "should I add another feature?" has no answer. That is why every
result in this project came from enumerating pairs, which only works because we told the method the
answer was a pair. exp-018 named the fix and deferred it:

> "Whether the score peaks at the CORRECT panel size … is a cross-size comparison and raw scores
> are not comparable across sizes; it needs an absolute (scramble-calibrated) score."

**Method.** For a panel S, permute each of its columns independently B times. That destroys the
relationship *between* columns — where clusters live — while preserving each column's own
distribution, the column count and the row count. Report `z = (q(S) − mean q(S_b)) / sd q(S_b)`:
how many standard deviations the real panel beats its own scrambled version by. The units are "SDs
above my own null", so panels of different sizes are finally comparable.

**Novelty: none, and it must not be claimed.** This is the standard fix for what the literature
calls dimensionality unbiasedness — Vinh et al., DMKD 30:1520–1555 (2016) formalise the property and
prove z-score normalisation achieves it; UMC (AAAI 2017) calibrates against the same
independent-column permutation model; DUSC (ICDM 2007) divides by the expected value. Our earlier
"nothing since 2008" claim is retracted in `CORRECTIONS.md` C9. The value here is that it unblocks
our pipeline.

---

## 1. Does calibrated z peak at the true panel size? Density yes, graph-cut no.

True pair padded with 0–3 junk columns. Pre-registered bar: peaks at k=2 in a majority of cells.

**density** — mean calibrated z

| shape | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| circles | **5.03** | 0.45 | 0.58 | 0.22 |
| spiral | **3.45** | 0.35 | 0.41 | 0.01 |
| moons | **2.70** | −0.09 | 0.22 | −0.14 |
| jain | **1.99** | 0.54 | 0.25 | 0.14 |

Peaks at k=2 in **80%** of (shape, seed) cells. **Passes.**

**graph-cut** — mean calibrated z

| shape | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| circles | **4.55** | −0.09 | −0.21 | 0.10 |
| spiral | **2.46** | 0.12 | 0.20 | 0.19 |
| moons | 4.01 | **4.30** | 3.68 | 3.63 |
| jain | 3.56 | 3.92 | 4.40 | **4.62** |

Peaks at k=2 in **52%** of cells. **Fails**, and the failure is not a near miss: on jain the
calibrated z *rises monotonically as junk is added*, so the term actively prefers a five-feature
panel carrying three junk columns over the exact right pair. On moons it peaks at k=3.

**The raw scores answer none of this.** They are negative at every size on every shape and decrease
monotonically with k (density: −0.05 → −0.44 on moons; graph-cut: −0.01 → −0.14), which is an
artefact of scale rather than a preference. That contrast — calibrated z separates cleanly where the
raw score cannot even be compared — is the result of this section.

This agrees with exp-018, which found density is the slope and graph-cut the cliff. Same division of
labour, now with a stopping rule attached to it.

---

## 2. End-to-end: growing a panel from one feature, with no target size given

Start from one of the two true features, add the feature that most raises calibrated z, stop when
nothing raises it. **This is the first search this project has run.** Everything prior enumerated.

| shape | exact pair found (density / graph-cut) | contains both true features | mean size stopped at |
|---|---|---|---|
| circles | **0.90 / 1.00** | 0.95 / 1.00 | 2.05 / 2.00 |
| spiral | 0.60 / 0.30 | 0.75 / 0.45 | 2.35 / 2.60 |
| moons | 0.55 / 0.00 | 0.65 / 1.00 | 2.45 / 3.75 |
| jain | 0.00 / 0.00 | 0.35 / **1.00** | 3.10 / 4.60 |

Density recovers the exact planted pair 90% of the time on circles, 55–60% on moons and spiral,
never on jain. Graph-cut *contains* both true features on jain and moons in every run but will not
stop, padding to 4.60 and 3.75 features — the same inverted preference as §1, now costing it the
answer.

So: **panel size is discoverable, about half the time, on the density term.** That is a real
capability and a modest one. It should be reported as both.

---

## 3. Abstention: safe, and under-sensitive

Panels drawn entirely from junk columns, against the pre-registered bar of z > 2.

| | false-split rate |
|---|---|
| circles | 0.039 / 0.031 (density / graph-cut) |
| jain | 0.045 / 0.034 |
| moons | 0.039 / 0.031 |
| spiral | 0.035 / 0.040 |
| **overall** | **0.037** |

3.7% of structureless panels would be declared a split. Tight and consistent. But only **43.2%** of
genuine panels clear the same bar, so a tree using this threshold would refuse to split more than
half the time when it should.

That is high specificity with low sensitivity, and it fails on the safe side — a tree that declines
is honest; a tree that emits a confident arbitrary split is the failure mode this whole mechanism
exists to prevent. It should be reported as a threshold curve rather than one number, because the
operating point is a choice and 2.0 was fixed before the run rather than after.

---

## 4. Convex control, reported separately and never pooled

| term | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| density | **28.13** | 17.50 | 9.35 | 6.56 |
| graph-cut | **−2.66** | −1.70 | −0.32 | 0.04 |

Density's signal on gauss2 is an order of magnitude above anything on the non-convex shapes, and it
peaks correctly. Graph-cut is negative at the true pair and *increases* with junk — completely
inverted. That matches exp-020, where graph-cut alone had rank-1 selection accuracy 0.000 on gauss2.
Any claim that this method "works on convex data" rests entirely on the density term, on a dataset
that plain k-means already solves at ARI 1.000 with no selection at all.

The null-sd floor fired on 1.6% of panels at B=30, down from 5.6% at B=5.

---

## 5. What this means for the goal

The goal is an interpretable recursive tree. Two things were missing and this experiment supplies
one and a half of them.

**Supplied:** panel size can be discovered rather than assumed, using the density term, at roughly
50% exact-recovery and 90% on the easiest shape. Without this the tree cannot exist, because every
node must commit to a panel of unknown size and enumeration only works when someone has told the
method the answer is a pair.

**Half supplied:** per-node confidence and the ability to decline. The mechanism works and errs
safely, but at the pre-registered threshold it declines on more than half of genuine panels.

**Not supplied, and this is the caveat that matters:** none of this says the confidence is
*calibrated to correctness*. z measures "structure versus no structure in these columns", not
"agreement with the labels a domain expert cares about". On synthetic data those coincide because we
planted the structure. exp-022 tests whether they coincide on real data. They do not.

## 6. Not answered here

- Whether the stopping rule finds the right size when the true panel is **larger than two**. Every
  planted truth in this suite is a pair, so a pass here only shows it stops correctly at 2.
- Whether B = 30 is enough. The null-sd floor firing at all means some panels have degenerate nulls,
  and the 43% sensitivity may be partly Monte-Carlo noise rather than a property of the score.
- flame is absent from this suite, as it is from exp-018 (see `CORRECTIONS.md`).
