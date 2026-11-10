# exp-019 — Real data: the signals work when good subspaces are common and strong, and fail when they are rare and weak

> **CORRECTION NOTICE (2026-08-05). The mice half of this experiment is invalidated and must be
> re-run.** Mice Protein Expression is **72 animals × exactly 15 technical replicates**, not 1080
> independent samples, and all four labels are animal-level properties constant across an animal's
> 15 rows. Our 600-row subsample draws ~8 replicates per animal, so any clustering that separates
> *animals* scores well against any label without finding the biology. Effective n is 72, not 600.
> Every mice number below — 65 of 2,926 pairs above ARI 0.5, best pair ARI 1.00, graph-cut median
> rank 381, top-10 lift +0.296 — is affected, and so is the "works when good subspaces are common
> and strong" conclusion, since mice is the half that worked. Aggregate to 72 animals and re-run
> before quoting any of it. The HAR half is unaffected. See `docs/CORRECTIONS.md` C8; raised by
> `docs/ec-handoff-external-review.md` §1.

**Date.** 2026-07-31. Script: `scripts/run_real_data.py`. Loaders: `atomicplus/datasets/real.py`.
Data: `results/real_data_mice_behavior.csv` (mice, label = Behavior; byte-identical to
`results/real_data_postfix.csv`), `results/real_data_har_sitstand.csv` (har, label = sit_stand). Every "pairs above ARI 0.5" and every rank in this document is computed on
the `ari_spectral` column — the ARI of the graph-cut splitter — because that is the splitter the
selection score is paired with. The other two splitters are in the same files and reach lower ARI
everywhere (mice max: dcdist 0.93, hdbscan 0.86; har max: 0.25 and 0.24).

**Why.** Every selection number in this project so far comes from our own generator, and we already
caught that generator being wrong once (exp-018 follow-up: four of six shapes gave away the planted
pair to a single-column test, which invalidated every suite-averaged number up to that point). The
risk now is that we are tuning to a second set of quirks in the replacement generator. Two real
datasets, chosen and built by other people, cannot flatter us the same way.

---

## 1. Two things that must not be conflated

Both are measured here and they are different questions.

**Clustering quality — a property of the DATA.** For every possible pair of features, cluster using
only those two features and compare the result to the true labels with ARI. Mice gives 2,926 such
values (all pairs enumerated), HAR gives 6,000 (sampled from 157,080; the sample size is printed,
never silently truncated). This is the answer key. No selection is involved.

**Selection quality — a property of OUR METHOD.** Our score ranks those same pairs *without seeing
labels*. The question is whether the pairs it puts at the top are the ones with high ARI.

A method can fail at either independently. Reporting them together is how the field's evaluations
get muddled, and it is what this experiment is set up to separate.

---

## 2. The single-column check: does the dataset test what we claim?

Before scoring anything, ask whether one feature alone answers the question. Take each feature by
itself, split the data on that one number, compare to the labels. If any single feature succeeds,
the dataset cannot test us — the entire premise of this project is finding features that only mean
something *together*, and if one feature already suffices there is nothing to find.

Best single-column ARI (2-means on one column, n=600):

| dataset / label | best single column | columns above 0.5 | verdict |
|---|---|---|---|
| HAR moving (dynamic vs static) | **1.000** | 205 of 561 | **UNUSABLE** |
| HAR stand vs lay | 1.000 | 13 of 561 | unusable |
| HAR walk vs upstairs | 0.618 | 3 of 561 | leaky |
| HAR upstairs vs downstairs | 0.577 | 10 of 561 | leaky |
| **HAR sitting vs standing** | **0.409** | **0 of 561** | usable |
| **mice Behavior** | **0.537** | 1 of 77 | usable (best PAIR = 1.00) |
| mice Genotype | — | — | unusable: no PAIR exceeds 0.249 |

**The HAR failure is not a defect in HAR — it is a badly chosen question.** `fBodyAccJerk-entropy()-Y`
measures how erratic the phone's motion is. Walking shakes it; sitting and standing do not. A motion
sensor separating motion from stillness with one number is physics, not a data flaw. Sitting vs
standing is the opposite: both are motionless, so motion-erraticness is useless, and telling them
apart needs the direction of gravity relative to the phone, which no single measurement pins down.

Mice Genotype fails the opposite way: no single column *and* no pair works (best pair 0.249), so
there is nothing at pair level to find. Both failure modes produce confident-looking numbers that
mean nothing, so **run this check on every dataset before scoring anything on it.** It has now caught
the same problem twice — once on synthetic (jain, spiral) and once on real (HAR moving).

---

## 3. Results on the two usable datasets

| | mice / Behavior | HAR / sitting vs standing |
|---|---|---|
| pairs evaluated | 2,926 (all) | 6,000 of 157,080 (sampled) |
| **best achievable ARI** | **1.00** | **0.634** |
| mean ARI over pairs | 0.108 | 0.017 |
| pairs above ARI 0.5 | 65 = **2.2%** | 22 = **0.37%** |

So the two datasets differ in the answer key itself: mice has a reasonable supply of pairs that work
and a best pair that is perfect; HAR has a handful of pairs that half-work and no pair that solves it.

### Selection: where does our score put the good pairs?

Median rank of the above-0.5 pairs, under each score (rank 1 = top; random ≈ half the total):

| score | mice (of 2,926) | HAR (of 6,000) |
|---|---|---|
| graph-cut | **381** (best pick: rank 1) | 2,684 (best 230) |
| graph-cut in dc-dist space | 793 (best 3) | 2,195 (best 154) |
| density | 1,330 (best 31) | 1,926 (best 35) |
| total multivariance | 1,174 | **4,909 — worse than random** |

On mice, graph-cut pushes the good pairs into the top 13%, and its single highest-scoring pair is the
genuinely best pair in the dataset. On HAR every score leaves them near the middle of the pile, which
is where they would sit if we ranked at random.

Supporting numbers, mice — mean ARI of the 10 highest-scoring pairs, minus the mean over all pairs
(so 0 means the top ten are no better than average): graph-cut **+0.296**, dc-dist **+0.304**,
density −0.02, multivariance +0.13. On HAR every one of these is within ±0.05 of zero.

**The top ten is a mix, not a clean sweep, and the lift number hides that.** Graph-cut's ten
highest-scoring mice pairs have ARI `1.00, 0.01, 0.01, 1.00, 1.00, 0.01, 0.01, 0.98, 0.01, 0.01` —
four excellent, six worthless. Against a base rate of 2.2% that is a large enrichment (a shuffled
null puts the good pairs at median ~1,463; observed 381, p < 0.0001), but a reader told only
"+0.296 lift" would picture something smoother than this. On HAR the same list is all noise
(max 0.023), and the median rank of 2,684 is inside the null distribution (p = 0.30) — that is the
basis for calling it no better than random, rather than eyeballing "about half of 6,000".

---

## 4. The finding

**The selection signals work when good subspaces are reasonably common and strong. They fail when
good subspaces are rare and weak.** Mice: 2.2% of pairs work, best reaches 1.00 → selection succeeds.
HAR sitting-vs-standing: 0.37% of pairs half-work, best reaches 0.634 → selection is no better than
chance.

This is a statement about which data the method suits, not about the algorithm, which is what makes
it useful: a reader can check which situation their own data is in before trying any of this.

**How this connects to the goal.** The project is trying to produce an *interpretable topological
clustering* — a tree whose every node names a few columns and splits the rows, so a domain expert
can read the explanation off it. Every node of that tree performs exactly the operation measured
here: pick a subspace, then split. So this result is not a side observation about two UCI files, it
is a statement about whether the tree is buildable at all on a given dataset. Where good subspaces
are common and strong (mice), a node will pick a usable panel and the split beneath it means
something. Where they are rare and weak (HAR sitting-vs-standing), a node picks essentially at
random and everything below it is noise dressed up as an explanation — which is worse than no tree,
because the output still *looks* interpretable. Being able to tell those two situations apart before
building anything is therefore a prerequisite for the whole design, not just a result about these
two datasets.

It is also consistent with the needle results in the handoff (exp-013, exp-017), where nothing —
EA, greedy or random — could find a target that gave no partial signal. Here we see the same wall on
real data and can now say where it sits in terms the data itself supplies.

---

## 5. Two things this changes

**The synthetic ordering does not transfer.** On our six shapes, dc-dist had the best gradient and
Euclidean graph-cut went *negative* on circles and spiral. On mice, Euclidean graph-cut is the
strongest term on every measure — best rank placement, tied-best top-10 lift, best resistance to
added junk columns (2.12 vs dc-dist's 1.07). Any ranking established on the synthetic suite is
provisional until re-checked on real data.

**Drop total multivariance as a general term.** It ranked HAR's good pairs *worse than random*
(median 4,909 of 6,000; Spearman −0.29). On mice it is mildly positive, not negative — median rank
1,174 against a random expectation of ~1,463, Spearman +0.045, top-10 lift +0.13 — so the honest
statement is "no use on one dataset, mildly helpful on the other", not "wrong sign everywhere". Its
spectacular synthetic numbers were confined to jain and moons, where it also has no gradient at all
(d(t1 vs t0) between −0.06 and −0.10 on every shape): it can confirm an arrival, never guide a
search. It stays interesting as a shape-specific detector; it is not a component of a general
method.

---

## 6. Caveats

- **HAR's two failures are entangled.** When the best available answer is only 0.634, telling a good
  pair from a mediocre one is intrinsically harder. "Our score failed" and "there was nothing clean
  to find" cannot be fully separated on this dataset.
- **HAR is sampled, mice is not.** 6,000 of 157,080 pairs is 3.8%. The 22 good pairs found imply
  roughly 575 exist overall; our score was ranked only over the sample.
- **Neither dataset has a known informative feature panel**, so selection is scored against
  clustering quality rather than against a true answer. Madelon is the one dataset with a recoverable
  panel (see `atomicplus/datasets/real.py`) and it has not been run yet.
- **Two datasets, one label each.** The "synthetic doesn't transfer" claim currently rests on a single
  comparison. mice/Treatment, HAR/up-vs-down and madelon are the obvious next runs.
- **Whole-field rank correlations are weak everywhere** (≤0.32) even where the top of the ranking is
  good. These scores order the whole field badly and the top well. Since a method only ever acts on
  the top, report the top; a low correlation beside a strong top-10 result is not a contradiction.
