# Corrections register — claims in this repo that the data does not support

**Created 2026-08-05.** Every number below was recomputed directly from `results/*.csv` on the lab
machine, not copied from another document. Where a document is affected it now carries a banner at
the top pointing here.

Two things caused most of this:

1. **The old benchmark leaked.** Junk columns were spread evenly, so planting a picture into two
   columns made those two columns visibly lumpy. Four of six shapes could be solved one column at a
   time. Everything measured before the repair is suspect, and the repaired numbers are almost
   always *better* for us, not worse.
2. **Numbers were copied between documents rather than recomputed.** Three figures in the exp-016
   headline line were wrong even against the benchmark they claimed to come from.

Notation: **rank-1 selection accuracy** = did the single top-scoring subspace equal the planted
pair. **ARI** = clustering quality once a subspace is fixed. They are different questions and most
of the confusion below comes from mixing them.

---

## C1. "Works on convex data, not on non-convex data" — RETRACTED, it is backwards

**Where it appears.** `docs/ting-brief.md` ("Lean on where ATOMIC+ genuinely partially works:
convex / redundant subspace structure"; "no selection signal reliably picks the informative
subspace on non-convex data"; "end-to-end still collapses"). It is also what Ting was told verbally
in the 2026-08-05 meeting.

**What the data says.** Rank-1 selection accuracy, `atomicplus_hybrid`, 20 seeds, p = 12/20/40.
Selection is identical across splitters, so it is reported once.

| shape | OLD (leaky) | REPAIRED |
|---|---|---|
| circles | 1.00 / 1.00 / 0.90 | **1.00 / 1.00 / 1.00** |
| moons | 0.90 / 0.90 / 0.85 | **1.00 / 1.00 / 0.90** |
| jain | 1.00 / 0.90 / 0.70 | **1.00 / 1.00 / 0.95** |
| spiral | 1.00 / 0.95 / 0.75 | **1.00 / 0.95 / 1.00** |
| gauss2 (convex control) | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| flame | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 |

Selection works on all four non-convex shapes and fails only on flame. It is *stronger* after the
repair, not weaker.

**And the convex control is the weakest case, not the strongest.** On gauss2 the graph-cut term
alone has rank-1 accuracy **0.000** — it names the wrong pair every single time — and the whole
dataset is solved by `kmeans_full` at ARI 1.000 with no subspace selection at all. Subspace
selection buys exactly nothing there. The correct statement is the opposite of the retracted one:
**the selection signal is a non-convex-structure detector, and on convex data it is carried entirely
by the density term on a dataset that needs no selection.**

**Why the wrong belief formed.** It predates the graph-cut + density hybrid (exp-016) and predates
the benchmark repair. It was true of the *persistence* fitness on the *leaky* benchmark.

---

## C2. exp-016's headline sweep line — stale, and three figures wrong even on its own benchmark

**Quoted claim.** "circles 1.0/1.0/0.9 · gauss2 1.0/1.0/1.0 · moons 0.90/0.90/0.80 ·
jain 1.0/0.90/0.65 · spiral 1.0/0.95/0.60 · flame 0.0/0.0/0.0" (also repeated in `HANDOFF.md` §3.2).

**Against the old benchmark it claims to describe:** moons p=40 is **0.85**, not 0.80; jain p=40 is
**0.70**, not 0.65; spiral p=40 is **0.75**, not 0.60. **Against the repaired benchmark** the whole
line should read: circles 1.0/1.0/1.0 · gauss2 1.0/1.0/1.0 · moons 1.0/1.0/0.90 · jain 1.0/1.0/0.95
· spiral 1.0/0.95/1.0 · flame 0/0/0.

**"Degrades gracefully with p"** (exp-016, HANDOFF §3.2) — the degradation was mostly the leak.
After the repair the largest drop from p=12 to p=40 on any non-flame shape is 0.10.

**"Largely solves the selection problem"** (exp-016) — this one HOLDS, and is understated. It is the
one place where repairing the benchmark helped our case.

**"The hybrid beats graph-cut alone"** (exp-016, HANDOFF §3.2) — HOLDS on the repaired data. Rank-1
by shape: hybrid 1.00 / 0.97 / 0.98 / 0.98 on circles / moons / jain / spiral, against graph-cut
alone 1.00 / 0.92 / 0.92 / 0.30 and density alone 0.90 / 0.77 / 0.42 / 0.87. The hybrid is at least
as good as both single terms on every shape, and much better than either on spiral.

---

## C3. "flame is unrecoverable for any gap/connectivity method" — CONTRADICTED, and this matters

**Where it appears.** `HANDOFF.md` §3b.5, `exp-016`. Also `exp-011` claims the true subspace on
flame yields ARI 0.95, which no result file reproduces.

**What the data says.** Hand the true pair to a splitter (tier C, repaired benchmark), ARI on flame:

| given the true pair | flame ARI |
|---|---|
| spectral split | **0.665** |
| HDBSCAN | **0.612** |
| spectral (non-split variant) | 0.491 |
| k-means | 0.430 |
| DBSCAN (eps 0.08) | 0.026 |
| persistence split | 0.033 |

Flame's clusters *are* recoverable at ARI 0.665 once you know which two features to use. The claim
is true only of persistence and DBSCAN, which is almost certainly how the overgeneralisation got in.

**So flame is not a free limitation.** Our end-to-end ARI on flame is 0.006–0.018 and our rank-1
selection accuracy is 0.000. The whole gap between 0.02 and 0.665 is a **selection** failure — ours
and SUBCLU's alike (SUBCLU's practical rules find the true pair in their candidate list only 3.3% of
the time on the repaired benchmark, though its label-tuned variant finds it 98.3% of the time). It
is also the one shape where our pipeline is net-negative: `spectral_full` with no selection at all
gets 0.026 against our 0.018.

**How to write it.** "Every subspace-selection method we tested, including ours and SUBCLU's, fails
to find flame's informative pair, on a dataset whose clusters separate at ARI 0.67 once that pair is
known." That is a sharper and more useful sentence than "flame is unrecoverable", and it is true.

---

## C4. exp-011's four-way regime characterisation — three of four regimes falsified

`exp-011` is a landscape analysis of the **persistence** fitness at p=10. Its conclusions were
written as scope limits on the project and are quoted downstream as such.

| exp-011 claim | verdict | correct number |
|---|---|---|
| "circles = clean win (0.70 vs best in-subspace baseline 0.48)" | CONTRADICTED | best in-subspace baseline on circles is spectral-split at **1.000**, DBSCAN 0.727, HDBSCAN 0.677 — the 0.48 understates it |
| "moons = coin-flip (ceiling ~0.67)" | CONTRADICTED | repaired end-to-end moons ARI **0.962** (persistence splitter), **0.935** (HDBSCAN) |
| "jain: even the oracle pair reaches only ARI 0.29–0.35 … no search or fitness change can fix this … honest scope limit" | CONTRADICTED | HDBSCAN given the true pair on jain = **0.902**; DBSCAN = **0.973**. A *splitter* change fixed exactly what the doc says nothing can fix |
| "flame: the true subspace yields ARI 0.95" | UNSUPPORTED | no file reproduces this; the best oracle-subspace number on flame anywhere is 0.665 |
| "DBSCAN-in-subspace (0.32) wins on jain" | CONTRADICTED | DBSCAN in the true subspace on jain = **0.973**, roughly 3× the quoted figure |

Only the flame-misranking regime survives, and its mechanism is misattributed (see C3).

---

## C5. exp-017's EA verdict — measured on the leaky benchmark, and its "ceiling" is a different configuration

`results/ea_newfit.csv` (exp-017's source) has 360 rows, 6 shapes, p = 12/20/40, 12 seeds, and **no
`noise` column** — so it was run before the structured-junk repair and cannot be re-attributed.

Its `enum2_ceil_ari` is also not the same object as the ceiling in `method_baselines*.csv`. On
circles exp-017's ceiling is 0.64 while `atomicplus_hybrid+spectral` reaches ARI **1.000** on the
repaired benchmark; the exp-017 run used one fixed splitter. So the sentence "the ceiling holds on
moons/circles (~0.6–0.8 at p=40) but fades on jain" describes that configuration on that benchmark,
not the pipeline as it now stands, and should not be quoted as a general ceiling.

**What is unaffected.** The EA-vs-random comparison is internally consistent (same benchmark, same
budget for all four searchers), and its direction is unchanged: EA 0.25/0.39/0.36/0.28 against
random 0.53/0.68/0.46/0.45 at p=12 on circles/moons/jain/spiral. **The fitness leading the search
shows no advantage for the EA; EA is no better than the other search algorithms, and at low p it is
worse than random.** That conclusion stands. Only the absolute ceiling numbers need re-running on
the repaired benchmark before they are quoted.

---

## C6. exp-010's "alternative panels (diversity)" differentiator — retracted elsewhere, still asserted here

`exp-010` lists "offers alternative panels (diversity) — a capability greedy / k-means / DBSCAN /
spectral lack" as the differentiator. `HANDOFF.md` §3b.3 already retracts this ("the diversity of
alternative panels claim collapsed under a fair test… do not revive without new evidence"), and the
20-seed QD runs confirmed random search beats MAP-Elites and CVT-MAP-Elites at every p. exp-010 also
self-flags as a 1-seed result. Do not cite its table.

`exp-010`'s other claim — that DBSCAN/HDBSCAN fail in the full space — HOLDS strongly
(`hdbscan_full` = 0.000 on every non-convex shape, both benchmarks, all p). But its "k-means/GMM
fail outright" is softer than stated on the repaired benchmark: `kmeans_full` reaches moons 0.492
and jain 0.442 there, against 0.248 and 0.059 on the leaky one. Structured junk makes the
no-selection baselines meaningfully stronger, which halves our measured advantage on those two
shapes (see exp-020).

---

## C7. Reported end-to-end ARI silently maximises over the splitter

Every "best end-to-end" number in `HANDOFF.md` §3.3/§7 and `exp-016` takes the best of three
splitters per shape. No document says so. The spread is large — on jain, ARI runs 0.887 (HDBSCAN),
0.559 (spectral), 0.048 (persistence) from *identical* selection. Choosing the splitter per shape
after seeing the answer is an oracle choice and has to be labelled as one. See exp-020 §3.

---

## C8. Mice Protein Expression is 72 animals × 15 replicates, not 1080 independent samples — exp-019's mice result is invalidated

**Raised by the external review (`docs/ec-handoff-external-review.md` §1). Verified here.**

```
rows                                    1080
distinct MouseID strings                1080   (e.g. 309_1 … 309_15, J3295_1 … J3295_15)
distinct ANIMALS after stripping _<n>     72
replicates per animal                     15   (exactly, for every animal)
animals whose replicates disagree on any label   0
```

Every one of the four labels — Genotype, Treatment, Behavior, class — is an **animal-level**
property, constant across all 15 rows of that animal. So 15 rows always carry the same answer, and
they are near-duplicates of one another in feature space.

**What that does to our numbers.** Our loader takes a 600-row subsample stratified by class, which
draws roughly 8 replicates per animal. Any clustering that separates *animals* therefore scores well
against any animal-level label without having found the biology at all. The effective sample size
for the class question is **72, not 600**.

Directly affected: exp-019's headline ("65 of 2,926 pairs reach ARI above 0.5 and the best pair
reaches ARI 1.00"), the graph-cut median-rank figure of 381, the top-10 lift of +0.296, and the
whole "selection works when good subspaces are common and strong" statement, since mice is the half
of that comparison that worked. Also affected: `docs/ting-brief-2.md` §4f and §5.

**Do not quote any mice number until this is fixed.** The fix is to aggregate to 72 animals (mean or
median over replicates) or to model the replicate structure explicitly, and to report both. At n=72
our density and graph-cut terms may not have enough rows to mean much, which is itself a finding.

This also blocks the meaningful-disagreement test (`ting-meeting-2026-08-05` §4b), which is built on
mice's four labels. The test is still the right test; it needs the aggregated data.

---

## C9. "Nothing since 2008 on making subspace scores comparable across panel sizes" — RETRACTED

**Where it appears.** `docs/ting-brief-2.md` §4d and §4g (one of three "gaps confirmed empty"), and
it was said to Ting verbally.

The problem has a formal name — **dimensionality unbiasedness** — a formal definition, and several
published correction mechanisms. Verified directly: **Vinh, Chan, Romano, Bailey, Leckie,
Ramamohanarao & Pei, *Data Mining and Knowledge Discovery* 30:1520–1555, 2016**, whose abstract
states the goal as "how to design effective scoring functions that are unbiased with respect to
dimensionality and yet being computationally efficient", formalises the concept, and proves Z-score
normalisation achieves it.

The external review lists six more (Dy & Brodley JMLR 2004; SURFING ICDM 2004; DUSC ICDM 2007; HiCS
ICDE 2012; UMC AAAI 2017; MCDE SSDBM 2019). Those are **not independently verified here** — check
before citing.

**The narrowed claim that may survive:** nobody has established dimensionality unbiasedness
specifically for normalized graph cut or DBCV-style validity indices, and nobody couples per-subspace
calibration with FDR control across the candidate set. That is a much smaller delta and should be
stated as one.

Related: `prereg-001`'s permutation null is also largely pre-empted by UMC (AAAI 2017). Record it in
prereg §2 before running Stage 0, so the result is read against the right baseline.

---

## C10. The reported calibrated z was the z of a panel the search REFUSED — exp-022's `z` and `abstain` columns are wrong

**Found** 2026-08-08 while wiring exp-024, whose abstention rule reads that number at every node.

**The bug.** `grow_panel` stops in one of three ways, and only two of them leave the chosen panel as
the last trace entry:

```python
trace.append(dict(subset=s, size=len(s), accepted=accepted, **top))
if not accepted:
    break                      # <- trace[-1] is now the REJECTED extension
```

Both `grow_from_pairs` and `run_real_calibration.py` then read `trace[-1]["z"]`. When growth stopped
because the best extension scored worse — which is the *principled* stop, the one the stopping rule
exists to make — the number reported is the rejected extension's z, and that is by construction
**below** the chosen panel's. When growth instead ran to `max_size` or exhausted the features, the
read happens to be correct.

**What it corrupts, and in which direction.** Every effect is one-sided:

| quantity | affected? | direction |
|---|---|---|
| ARI, chosen panel, stopped-at size | **no** | these come from `chosen`, not the trace |
| exp-022's `z` column | **yes** | too low, only on runs that stopped by rejection |
| exp-022's `abstain` column and counts | **yes** | too many abstentions |
| exp-021 stopping-rule results | no | reads the whole trace, not `trace[-1]` |
| exp-023 basin fractions | no | scored by ARI of the grown panel |

So no conclusion about *where the search lands* changes. What changes is the reported confidence in
those landings and how often the method is said to refuse — and since "it knows when to abstain" is
part of the pitch, the number has to be right before it goes in the paper.

**The fix.** `calibration.chosen_z` / `chosen_entry` return the last *accepted* entry. Both callers
now use it and additionally record `z_last`, the old number, so the two can be compared without a
re-run. Any abstention count quoted from a `real_calibration.csv` written before 2026-08-08 should
be recomputed.

**Also fixed alongside.** `chosen_entry` carries the `degenerate` flag. When a panel's null SD
collapses, `sd_floor` is substituted and z becomes a ratio to an arbitrary constant, so it can be
arbitrarily large — thresholding it manufactures splits. exp-024 now discards degenerate panels
rather than ranking them; `run_real_calibration.py` records the flag.

---

## Open gaps, recorded so they are not forgotten

- `results/benchmark_validation.csv` only tested moons, spiral and jain, at p=12. circles, flame
  and gauss2 were never checked for the one-column leak after the repair.
- `results/signal_landscape.csv` (exp-018, exp-019's dilution figures) has no flame, no p=12, and
  10 seeds where `prereg-001` specifies 20.
- The mass-concentration shortcut still recovers the planted pair 75% of the time on jain after the
  repair (0% on moons and spiral).
