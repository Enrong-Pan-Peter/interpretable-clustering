# Triage of the external review (`ec-handoff-external-review.md`)

**Date.** 2026-08-05. The review was written 2026-08-01, so it predates the audit that produced
`docs/CORRECTIONS.md` and `exp-020`. This note says what we take, what we reject, what conflicts,
and what I verified myself rather than taking on trust.

**Verified here, independently:** the mice replicate structure (§1), the Vinh et al. 2016 citation
that retracts our cross-size gap claim (§4.1), and the existence of the Beretta hardness result
(§5). Everything else below is reported as the review states it and is marked unverified.

---

## Take, and it changes the plan

### T1. The mice replicate bug (review §1) — CONFIRMED, worse than the review states

72 animals × exactly 15 replicates, all four labels constant within an animal. Full detail and what
it invalidates: `docs/CORRECTIONS.md` C8, and exp-019 now carries a banner. This is the highest
priority item in the whole document. It invalidates our strongest real-data result and it blocks the
meaningful-disagreement test that the reframe depends on.

### T2. Per-panel permutation calibration (review §3.1) — the most valuable idea here

**Score each panel against permuted copies of itself.** Permute each of the panel's columns
independently B times: that destroys the relationship *between* columns, which is where clusters
live, while preserving each column's own distribution, the column count and the row count. Report
how many standard deviations the real panel scores above its own scrambled version.

Why it matters to us specifically: the units become "SDs above my own null", so **a 2-column panel
and a 5-column panel are finally on the same scale**. That gives a stopping rule — grow the panel
while calibrated z rises, stop when it falls — and panel size becomes something the method discovers
rather than something we tell it. That is the exact missing ingredient that forced us into pair
enumeration, and it is the question exp-018 explicitly deferred:

> "Whether the score peaks at the CORRECT panel size … needs an absolute (scramble-calibrated)
> score. Separate experiment — do not infer it from these tables."

Their result (density term, moons/circles/jain, B=20, *unverified by us*): calibrated z of the true
panel 3.81 / 1.15 / 1.01 / 0.12 at k=2/3/4/5, peaking at the correct size, where the raw score is
negative at every size and cannot be thresholded at all.

**Novelty: none.** DUSC / Vinh / UMC territory. Cite it, implement it, do not claim it. The value is
that it unblocks the pipeline.

Related and cheap: review §4.3 points out our `z(gc) + z(de)` z-scores **across the candidate pool**,
not within a panel. I had recorded the pool-relativity as a limitation in ting-brief-2 §3; the
review's stronger point is that it is the *cause* of the cross-size problem, and that it means we do
not get the Vinh et al. Theorem 3 guarantee — a reviewer who knows that paper will ask why. Changing
the z to be against a per-panel null instead of the pool is roughly 20 lines plus B× score cost.

### T3. The fix to the interpretability reframe (review §7.2–7.3) — sharper than what we had

The review names the flaw in Ting's own words: *"fitness is not showing partial signal either way,
so there is no guarantee the recursive algorithm is correct even at the first level."* Their reading:
that is fatal to the interpretability framing as stated, because **an interpretable tree whose first
split may be arbitrary is worse than no tree — it is confidently misleading.** A faithful explanation
of an unreliable decision is not a contribution.

We reached the same place independently in exp-019 §4 ("noise dressed up as an explanation"). The
review goes one step further and supplies the fix, which we did not have:

> An interpretable recursive clustering tree where every split carries a **calibrated confidence**
> and the method can **decline to split**.

Every node reports "this split is 3.8 SDs above what this panel would produce with no structure"
versus "0.2 SDs — indistinguishable from noise", and when nothing clears threshold the tree refuses
to split and says so. "No guarantee at level 1" becomes measured and disclosed per node.

**This is a capability no baseline has.** SUBCLU cannot say "I don't know". Neither can oblique
trees, HTC, or DUFS. prereg-001 already spotted this ("a capability claim, not a performance claim")
without connecting it to the tree.

It satisfies everything Ting asked for — interpretability first, established metrics reused with no
novelty pressure, no need to beat the state of the art — and adds a technical contribution that is
not the tree structure or the interface, both of which are probably too thin to carry a paper alone.
**Recommend adopting this as the paper's framing** and taking it to her.

---

## Take when convenient

### T4. The δ dial (review §7.5)

Keep the shapes planted in two columns but add a small class-dependent shift δ to each, so each
column alone carries a weak marginal signal while the joint structure remains. At δ=0 this is exactly
our current setup. Sweep δ.

Every result we have is measured at one point — marginal signal exactly zero — which is why
everything reads as "it fails". A single point is hard to publish; a curve is a paper. It also
revives the EA question in a form that can be answered: *at what marginal strength does evolutionary
search start to beat random?* All the infrastructure exists (`run_ea_newfit.py`, fair SFS greedy,
matched-budget random, 20-seed protocol).

The review notes GroupFS already has this dial as ρ ∈ [0.6, 1] with Gaussian nuisance, so we would be
extending their axis in two directions they did not go — a more comfortable position than "we beat
GroupFS". *Unverified.*

### T5. Better instruments than rank-1 selection accuracy (review §8)

RG_sim (Jaccard overlap between discovered and true panels, so partial recovery scores partially),
TPR and FDR. Rank-1 is all-or-nothing and throws away the difference between "named one of the two
true features" and "named neither" — which is exactly the distinction exp-018 spends its whole length
measuring by other means. Also worth taking: the self-tuning kernel (per-point bandwidth from the
K-th nearest neighbour), which removes our untuned `k=10` / `core_k=5` defaults rather than tuning
them. *Unverified.*

### T6. The hardness result (review §5)

Our target class — structure present in k features jointly with no signal in any proper subset — is
**k-junta distributions**, and Beretta (*New Statistical and Computational Results for Learning Junta
Distributions*, LIPIcs APPROX/RANDOM 2025 art. 31, arXiv:2505.05819 — **existence verified**) proves
learning them is computationally equivalent to learning parity with noise.

What it does *not* mean is "unsolvable": the exponent is n^k, and k=2 at p=77 is 2,926 pairs. The
barrier bites at k≥4 and large p. Useful interpretable panels are 2–5 features, so the practical goal
sits inside the tractable region. The honest scoping sentence the review offers is good: *solvable for
small panels by paying the full exhaustive cost, and that cost is affordable; what is blocked is
scaling to arbitrary panel size.*

The value for us is that it recasts every negative result — "the EA does not show an advantage",
"random matches or beats it", "no budget-limited search reaches the enumeration ceiling" — as located
points on a known landscape rather than as engineering failures.

### T7. Run DUFS on our benchmark (review §4.5)

DUFS (NeurIPS 2021) demos on n=100, p=20, two moons plus 18 i.i.d. Gaussian nuisance — our benchmark,
five years earlier. The review's correction is the important part and it sounds right: **our
one-column gate does not protect us**, because DUFS does not assume informative features are
marginally separable, it assumes they are individually smooth along the graph, and graph smoothness
is a much weaker requirement. Their predicted failure mode on structured junk (a lumpy column pulls
its own clump together in the metric and then scores as smooth on the graph it helped build) is
plausible and is exactly what our repaired benchmark tests. *Unverified; worth running.*

---

## Do not take

- **The max-over-weightings direction (review §3.2).** Their own numbers kill it: junk panels gain
  55% more from being allowed to search over weightings than the true panel does. Keep their
  max-gain table as a figure; it is a clean demonstration of a failure mode that recurs in this
  project.
- **An EA over the choice of scoring term** (review §7.4, and Ting's suggestion). Three or four
  options — evaluate all of them. Same conclusion I reached independently.
- **The feature-weighting method that suggests itself (review §3.4).** Already published in two
  pieces (FWSA 2008 for the ratio weight; Chowdhury et al. *Pattern Recognition* 2023 for per-feature
  MST compactness in a density clusterer), and the review flags a likely convergence failure. The
  genuinely open ground they identify — **learned feature weights combined with a minimax-path /
  density-connectivity distance** — is real and sits exactly where our dc-dist result was best, but
  they are right that it is paper-sized, not an August task.

---

## Conflicts with what we now know

The review predates today's audit, so three of its premises are out of date.

1. **Its §7.1 worked example is moot.** "Running moons, seeing it fail, and omitting it" — moons does
   not fail. Repaired-benchmark rank-1 selection accuracy on moons is **0.967**. See
   `docs/CORRECTIONS.md` C1.
2. **It does not know exp-020.** flame is a *selection* failure, not an unrecoverable shape (ARI
   0.665 once the true pair is known); the splitter swings ARI by 0.84 on jain with identical
   selection; and selection buys +1.000 on circles and +0.552 on spiral against full-space methods at
   chance. That last table is a better motivating figure than anything in the review.
3. **A real tension to resolve before either claim goes in a paper.** Review §5 argues that every
   bottom-up subspace method prunes by downward closure, that our benchmark makes downward closure
   false by construction, and therefore that CLIQUE / ENCLUS / MAFIA / SUBCLU "cannot find our
   structure at any parameter setting". But exp-020 §1 measures SUBCLU's candidate list as containing
   the true pair **84–87%** of the time. Both cannot be fully right. Either our SUBCLU's candidate
   generation is less strictly downward-closed than the theory assumes, or the structured junk leaves
   enough one-dimensional density for the pruning to survive. These are central to two different
   sections — the hardness argument and the SUBCLU comparison — so it needs settling.

One thing to read carefully rather than act on: review §2.3 concludes we need junk kept below roughly
20% relative scale for the density term. Our preprocessing z-scores every column to unit variance, so
junk sits at 100% scale by construction and there is no knob. The actionable reading is the one they
give in §3.4 — **reweighting is the only door** (Durrant & Kabán, *J. Complexity* 2009: with relevant
components fixed and irrelevant dimensions growing, any equal-weight distance must concentrate). The
threshold is a design target for a weighting scheme, not something we can set directly.

---

## Revised order of work

1. **Fix the mice replicates.** Aggregate to 72 animals, re-run exp-019's mice half, report both.
   Blocks every real-data claim and the disagreement test.
2. **Per-panel null calibration** (T2). Small change, confirmed by them to work, answers exp-018's
   deferred question, and is the prerequisite for the framing in T3.
3. **Take T3 to Ting** as the paper framing before building anything further.
4. **METABRIC acquisition** continues in parallel — it is unaffected by all of the above and it is
   the one dataset with a published feature panel.
5. Then: DUFS on the structured benchmark (T7), the δ sweep (T4), prereg-001 Stage 0 with UMC
   recorded as prior art first.

**Dates, from the review §10 and not re-verified:** NeurIPS 2026 workshop deadlines all 29 Aug
(non-archival, list was still unpublished on 1 Aug); ICLR 2027 abstract 18 Sept, paper 25 Sept.
The 29 Aug date is 24 days from now. Confirm both before planning around them.
