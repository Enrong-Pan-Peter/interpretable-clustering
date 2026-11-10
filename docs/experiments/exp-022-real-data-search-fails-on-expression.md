# exp-022 — The unsupervised search does not beat doing nothing on breast cancer expression data

> **READ §2d FIRST.** After this was written, the two re-run exp-019 sweeps showed that raw
> graph-cut ranks the good METABRIC pairs in the top 7% and its top pick scores ARI 0.482 against
> the search's 0.190. The failure is in the SEARCH, not in the score. §1 and §3 were written before
> that was known and overstate the score's culpability.

**Date.** 2026-08-06. Script: `scripts/run_real_calibration.py`. Data:
`results/real_calibration.csv` — 4 METABRIC contrasts × 2 terms × 6 seeds = 48 runs, n = 300
patients, p = 250 genes (50 PAM50 + 200 random distractors), B = 20, growth shortlist 70 features
from a Stage-0 screen at B = 5.

**Why.** exp-021 showed the stopping rule works on our synthetic shapes. `run_panel_size.py` showed
that on METABRIC a small panel genuinely exists: on HER2-vs-luminal an eight-gene panel reaches
ARI 0.744 against 0.213 for all 250 features and 0.181 for the published 50-gene PAM50 panel. So the
data has an answer worth +0.53 ARI. This experiment asks the only question that is about our method:
**starting from nothing, with no labels, does the search find it?**

**Design.** Stage 0 screens every singleton by calibrated z. Stage 1 seeds from the top-scoring
singletons (Channel A) and from a sample of the low-scoring ones (Channel B, the only place a
jointly-necessary panel could live). Stage 2 grows each seed while calibrated z rises and stops when
it falls. Each stopped panel's ARI is reported against two references: the no-selection **floor**
(cluster on all 250 genes) and the label-using greedy **oracle** at the same panel size. The oracle
is a diagnostic, never a competitor — it cannot run without the answer.

---

## 1. The result

Best stopped panel per contrast and term, against the floor.

| contrast | floor (all 250) | oracle at that size | ours, density | ours, graph-cut |
|---|---|---|---|---|
| HER2 vs luminal | 0.184 | 0.75–0.79 | **0.044** | **0.190** |
| claudin-low vs basal | 0.268 | 0.63 | **0.179** | **0.311** |
| LumA vs LumB | 0.517 | 0.60 | 0.214 | 0.390 |
| basal vs luminal | 1.000 | 1.000 | 0.211 | 0.635 |

**On every contrast the search lands at or below the no-selection floor.** The single exception is
claudin-low vs basal under graph-cut, at +0.04 above the floor, which is about 12% of the achievable
gain.

On HER2-vs-luminal — where an eight-gene panel reaches 0.744 — all twelve seeds fall between −0.067
and 0.190. Selection bought nothing. This is not "partway to the ceiling"; it is at the floor.

Channel B (seeding from low-scoring singletons) produced the best panel on basal-vs-luminal (0.635
vs 0.195 for Channel A) and on HER2-vs-luminal under graph-cut (0.190 vs 0.010). So the channel we
included on principle is the one that occasionally works, which is worth keeping — but it is
outperforming a Channel A that is itself at the floor.

## 2. Three findings that follow

### 2a. Density loses to graph-cut on every real contrast — the synthetic ordering inverted again

exp-021 measured density as the term that can drive a calibrated search (80% peak-at-truth against
graph-cut's 52%) and the defaults were changed on that basis. On real data graph-cut wins every
contrast, by 0.15 (HER2), 0.13 (claudin-low), 0.18 (LumA/LumB) and 0.42 (basal) ARI.

This is the **third** time an ordering established on the synthetic suite has failed to transfer —
after exp-019 (dc-dist looked best on our shapes, plain graph-cut was best on mice) and the
dc-dist/multivariance results. The pattern is now consistent enough to state as a methodological
finding in its own right: **rankings of candidate scores established on our generator do not
survive contact with real data, and should never be reported without a real-data check.**

### 2b. Confidence is high where the answer is wrong

Only **2 of 48** seeds abstained at the pre-registered bar, and calibrated z reaches **18.9** on
panels scoring ARI 0.31. The mechanism that exp-021 showed declining on 96% of structureless
synthetic panels declines almost never here, on panels that recover nothing.

There is a defensible reading and it must not be assumed. Calibrated z measures "structure versus no
structure in these columns", not "agreement with this particular label". A confident split that
disagrees with HER2 status could be real structure orthogonal to it — which is the meaningful-
disagreement case. But we have not run that test, and until we do, "high z" means only "found some
structure", which is materially weaker than the confidence claim the interpretability framing needs.
**This is the single biggest open risk to that framing.**

### 2c. The genes are right even when the clustering is not

On LumA-vs-LumB, graph-cut stops on **ANLN, BIRC5, CDC20** — the proliferation signature that
clinically distinguishes those two subtypes. On HER2-vs-luminal it stops on **MYC, NDC80, SLC39A6**;
on claudin-low vs basal, **BCL2, CDC20, CDH3, PHGDH, TYMS**. These are PAM50 genes and they are
biologically coherent for the contrast in question.

So the method names plausible genes and still does not beat clustering on all 250. That is worth
something for an interpretability argument and it must not be oversold: naming the right genes while
producing a worse partition is not a working method, it is a suggestive failure.

---

## 2d. UPDATE (same day): the score CAN see the answer — it is the SEARCH that cannot reach it

The two destroyed exp-019 sweeps were re-run. Scoring 4,000 sampled METABRIC pairs directly, with
no search involved:

| HER2 vs luminal, 4,000 pairs | median rank of the 22 good pairs | top-10 lift | ARI of top pick |
|---|---|---|---|
| graph-cut | **278 / 4000** | +0.181 | **0.482** |
| graph-cut in dc-dist space | **227 / 4000** | +0.231 | 0.152 |
| density | 2,762 / 4000 (worse than random) | −0.006 | 0.001 |
| random expectation | 2,000 | 0 | — |

Raw graph-cut puts the good pairs in the **top 7%** and its single top-scoring pair reaches
ARI 0.482 against a best-available 0.624. The search using the same term reached only 0.190, at the
floor. **So enumeration beats search by a wide margin on the same data with the same score.**

That reverses the §4 open question and it invalidates the framing of §1: the correct statement is
not "the score cannot see the answer on expression data" but "**the score can see it and our search
cannot reach it**". Three candidate causes, none yet tested: calibration may be destroying a signal
the raw score has; greedy forward growth may not be able to reach the good pairs from any good
singleton; or the 70-feature growth shortlist from the Stage-0 screen may simply have excluded the
right genes. That is the next diagnostic and it is cheap, because at 496 pairs Levine_32dim allows
exhaustive enumeration and search side by side.

Density is worse than random here (median 2,762), consistent with the search result and with
exp-021's finding reversing on real data (2a).

claudin-low vs basal is an **ambiguous null**: zero of 4,000 pairs exceed ARI 0.5 and the maximum is
0.450, so nothing there measures our method. Total multivariance shows the highest whole-field
Spearman we have recorded anywhere (+0.389) while its top pick scores 0.203 — ordering noise
tidily. Do not quote that correlation.

## 3. Why it fails, and why it is the same failure as before

Our two terms both reward **gaps** — the graph cut wants two halves that are barely connected, the
density term wants a between-cluster separation exceeding the within-cluster raggedness. Breast
cancer subtypes as defined by PAM50 are **overlapping distributions with shifted means**, not
separated populations. LumA versus LumB is explicitly a proliferation gradient with a threshold
drawn through it. There is no gap to find, so a gap-seeking score ranks a random pair that happens
to look bimodal above the pair that actually separates the classes.

That mechanism also explains the two earlier real-data failures, which had been recorded without
one:

- **HAR sitting-vs-standing** (exp-019): selection no better than random. Two static postures
  differing in the direction of gravity — overlapping, no gap.
- **mice Genotype** (exp-020 / gate): no pair exceeds ARI 0.44. Control versus trisomic is a
  continuous shift in protein levels.
- **mice Behavior**, which *works* (best pair ARI 1.000, graph-cut top pick 1.000, top-10 lift
  +0.455 at 72 animals): two experimental protocols producing genuinely distinct protein states.

The scope statement this supports: **the method finds structure that is separated, and fails on
structure that is shifted.** That is checkable in advance on any dataset, which makes it useful
rather than merely apologetic.

---

## 4. Caveats

- n = 300 patients and a 70-feature growth shortlist. A larger n or a wider shortlist could change
  the numbers, though not plausibly by the +0.5 ARI that would be needed.
- The floors here differ from `run_panel_size.py` because that ran at n = 600. basal-vs-luminal
  reaches ARI 1.000 with no selection at n = 300, so nothing can be added there and its
  `frac_of_ceiling` column is meaningless.
- **Reporting bug:** `frac_of_ceiling` divides by (oracle − floor) and blows up to −10⁹ when those
  coincide. The guard uses a minimum absolute value where it needs a minimum spread. Read the raw
  ARI columns, not that one, until it is fixed.
- The direct test of the score without the search — Spearman(score, ARI) over sampled METABRIC
  pairs, the exp-019 machinery — has **not** been run on METABRIC yet. Two runs were destroyed by an
  output-filename collision. The search could be failing for its own reasons, and that test would
  separate "the score cannot see the answer" from "the search cannot reach it". It is the next run.

## 5. What this changes

- **The real-data section of an interpretability paper cannot rest on METABRIC as a success.** It
  can rest on mice Behavior, and METABRIC becomes the honest negative that defines the scope.
- **The confidence claim needs the disagreement test** before it can be made, not after.
- **Do not quote any term ordering from synthetic data** without the real-data check (2a).
- The two candidate repairs — retuning the neighbourhood graph so a density saddle between
  overlapping modes becomes visible, and moving to biomedical data whose populations are genuinely
  discrete (single-cell RNA-seq, flow and mass cytometry) — are recorded in
  `docs/paper-claims-table.md` rather than here, because they are decisions and not results.
