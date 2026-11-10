# Paper claims and evidence — what we will assert, and what would establish it

**Created 2026-08-05.** Written before committing to more experiments, so that an experiment has to
earn its place by supporting a claim. Anything with no claim above it does not get run.

**Framing** (from `ting-meeting-2026-08-05-interpretability-reframe.md` plus the external review's
§7.3): *an interpretable recursive clustering tree where every split names a small feature panel,
carries a calibrated confidence, and the method can decline to split.* Interpretability first, no
requirement to beat the state of the art, established metrics reused with no novelty pressure.

**Status key.** HAVE = measured, 20 seeds, on the repaired benchmark or real data.
PARTIAL = measured but on stale data or needing a re-run to quote. BLOCKED = waiting on a run.
NOT BUILT = no implementation yet.

---

## The claims

### C1 — the contribution. A tree whose every split is named, scored and refusable.
*What establishes it:* a working implementation, plus C4 (the confidence means something) and C5
(it really does decline), plus C6 (one real tree a domain reader can evaluate).
**Status: NOT BUILT.** `calibration.py` exists and `tree.py` exists; they are not connected.
*Run:* after exp-021 reports. Do not build the tree before we know the confidence is meaningful —
a tree with a meaningless confidence is the exact failure mode this framing exists to avoid.

### C2 — subspace selection is *necessary*, not a refinement.
*What establishes it:* per shape, our best result against the best method that uses every column.
**Status: HAVE.** Repaired benchmark, 20 seeds, p = 12/20/40:

| | circles | spiral | moons | jain | gauss2 | flame |
|---|---|---|---|---|---|---|
| ours, best splitter (ARI) | 1.000 | 0.553 | 0.962 | 0.887 | 1.000 | 0.018 |
| best full-space method (ARI) | 0.000 | 0.001 | 0.492 | 0.452 | 1.000 | 0.026 |
| **gain from selection** | **+1.000** | **+0.552** | **+0.470** | **+0.435** | 0.000 | −0.008 |

*Run: none. This is ready to write.* Lead with circles and spiral, where full-space methods are at
chance. The moons and jain gains halved when the benchmark leak was repaired, so they are the
weaker half of the argument. gauss2 shows selection buys nothing on convex data, which is the
cleanest possible scope sentence.

### C3 — existing subspace methods find the panel but cannot rank it. We can rank it.
*What establishes it:* SUBCLU's recall of the true panel versus its rank-1 accuracy, reported both
as retrieval (no invented ranking) and under the tie-break most favourable to it.
**Status: PARTIAL.** Have the tie-break view: true pair in SUBCLU's returned list 84–87% of the
time, rank-1 accuracy 22% (self-tuned) / 30% (best add-on rule), against our 82%; even a
label-tuned pick from its own list reaches only 71%. The retrieval columns (precision, random-pick)
were added to the harness today and need a re-run.
*Run:* `run_method_baselines.py`, both noise profiles.

### C4 — calibration makes panel size *discoverable*. The stopping rule.
*What establishes it:* calibrated z peaks at the true panel size, where the raw score cannot be
compared across sizes at all; and growing a panel from a seed stops at the right size on a majority
of shapes at 20 seeds.
**Status: BLOCKED, not measured.** A 2-seed / B=5 smoke test is consistent with it and is not
evidence.
*Run:* `run_calibration.py --seeds 20`. **This is the experiment the paper hinges on** — without it
C1 has no mechanism and we are back to enumerating pairs because we told the method the answer is a
pair.

### C5 — the method can abstain, and that is a capability no baseline has.
*What establishes it:* on panels with no planted structure, calibrated z stays below a pre-set bar
at a controlled rate, while true panels clear it. Plus a statement that SUBCLU, oblique clustering
trees, HTC and DUFS have no mechanism to say "I don't know".
**Status: BLOCKED, not measured.** Same run as C4, question [3].
*Run:* same. This is the answer to Ting's own objection — that there is no guarantee the recursive
algorithm is right even at the first level. It converts the flaw into the feature.

### C6 — a real-data case study with a *published* answer key.
*What establishes it:* METABRIC passes the one-column gate on at least one contrast; our top-ranked
panel overlaps PAM50 above chance; the resulting tree's named genes are readable.
**Status: BLOCKED on the gate.** Data is in place. Every dataset before this had labels but no
published panel, so we could only ever score clustering, never selection.
*Run:* `reduce_metabric.py`, then the gate, then the pair sweep. **The gate is a genuine decision
point, not a formality** — if a single gene solves LumA vs LumB we pick another contrast, and if
none of the four survive, the real-data section is mice alone and this is a different paper.

### C7 — a disagreement with established labels can be meaningful, and here is the test.
*What establishes it:* a split that disagrees with the primary label but aligns with a variable
that never entered the clustering.
**Status: PLAN CHANGED — mice cannot do this.** The gate at 72 animals shows Genotype (best pair
ARI 0.437) and Treatment (0.186) have no pair-level structure at all, so there is nothing for a
disagreeing split to align *with*. All of mice's pair-level structure is in Behavior.
*Run:* moves to METABRIC, which is a better home anyway — it ships survival, NPI, chemotherapy,
hormone therapy, INTCLUST and the 3-gene classifier as genuinely independent held-out variables. A
split that disagrees with PAM50 but tracks survival is a much stronger version of this argument
than anything mice could have given us.

### C8 — negatives worth publishing.
1. **The fitness leading the search shows no advantage for the evolutionary algorithm; EA is no
   better than the other search algorithms, and at low p it is worse than random.** HAVE, but
   measured pre-repair — the direction stands, the absolute numbers need a re-run before quoting.
2. **flame defeats every subspace-selection method we tested**, ours and SUBCLU's alike, on data
   whose clusters separate at ARI 0.665 once the right pair is known. HAVE. Sharper and more useful
   than the old "flame is unrecoverable", which was wrong. Whether it goes in the paper is a
   writing decision to take with Ting.
3. **The raw score's ability to tell a better panel from a worse one shrinks as the panel grows**
   (density term, Cohen's d 3.13 at size 2 → 0.48 at size 3), and one of its two terms inverts at
   larger panels. HAVE, exp-018. This is the motivation for C4.

### C9 — mice, restated honestly.
**Status: gate done, pair sweep needs re-running.** At 72 animals (not 1080 rows): best pair
ARI 1.000, 102 of 2,926 pairs above 0.5, best single column 0.690 with 1 of 77 above 0.5. The
signal survives aggregation — more pairs clear 0.5 than before, because averaging replicates
removes noise. The caveat becomes the single-column leak, not the sample size.
*Run:* `run_real_data.py mice --label Behavior`.

---

## Claims we are NOT making

Stated here so nobody drifts into them.

- Beating existing methods on clustering quality (ARI). We do not, except where selection is the
  whole difference (C2), and that is a different claim.
- Novelty in the clustering primitives. Normalized graph cut and the density validity index are
  established, and Ting has explicitly said reusing them is fine.
- **Novelty in the calibration.** This is the standard fix for what the literature calls
  dimensionality unbiasedness (Vinh et al., DMKD 2016; UMC, AAAI 2017; DUSC, ICDM 2007). We cite
  it and use it. Our earlier claim that nothing had been done here since 2008 was wrong and is
  retracted in `CORRECTIONS.md` C9. The narrow thing that may be ours: nobody has established it
  for normalized graph cut or DBCV-style indices specifically.
- Fair evaluation as a contribution. Every paper is supposed to do it.

---

## What this cuts, and what it keeps as supporting material

**Cut for now** — good ideas with no claim above them, and not deliverable by late August:
- The δ / marginal-signal sweep. It would turn "it fails" into a curve and revive the EA question,
  which is genuinely attractive, but it supports no claim in this paper. Park it for the follow-up.
- The benchmarking paper (Gaussian-nuisance critique). A second paper, explicitly parked.
- Higher-order dependence measures beyond what is already measured.

**Keep as supporting, not central:**
- DUFS. Not a claim, but a *threat* — a reviewer who knows it will ask, and the external review's
  point is right that our one-column gate does not protect against it (it assumes graph smoothness,
  not marginal separability). One run, one paragraph.
- Distance multivariance and the density-connectivity distance. Already measured. They become at
  most a paragraph explaining what we tried and why the deployed method does not use them.

---

## Open decisions

1. **Which venue.** The NeurIPS workshop deadline (29 Aug, non-archival) is 24 days out and would
   fit C1–C5 plus one real dataset. ICLR 2027 (25 Sept) needs C6 and C7 as well. Decide after the
   METABRIC gate reports, because that is what determines whether C6 exists.
2. **Whether flame goes in the table.** With Ting, at writing time.
3. **Which SUBCLU view leads** — retrieval or best-case tie-break. Both are recorded; choose at
   writing time.

## Ordering that follows from the above

C4 and C5 come from one run and gate the whole framing. C6 comes from one run and determines
whether there is a real-data section. Everything else is either already in hand (C2, C8) or a
re-run for numbers we can already predict the shape of (C3, C9). So: the calibration run and the
METABRIC gate are the two things that matter this week, and they are independent of each other.
