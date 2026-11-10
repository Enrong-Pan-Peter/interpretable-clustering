# Pre-registration 001 — null-calibrated subspace selection

**Status:** DRAFT, awaiting Enrong's sign-off. No code to be written until this is approved.
**Date drafted:** 2026-07-27
**Why a pre-registration at all:** this is the item the project notes flag as carrying the largest
overfitting-risk surface. Deciding the null, the correction, the success threshold and the
abandonment conditions *before* seeing results is what separates "we found a fix" from
"we tuned until the number went up". Everything below is binding once signed.

---

## 1. The specific failure being targeted

As `p` grows, the graph-cut+density hybrid degrades: rank-1 selection on jain falls 1.0 → 0.65
and spiral 1.0 → 0.60 between p=12 and p=40 (20 seeds). The mechanism is not that the true
subspace gets worse — the enumerate-all-pairs ceiling holds — it is that with C(p,2) candidates,
some *noise* subspace eventually scores higher by luck. This is a multiple-comparisons problem,
and every selection signal tried so far scores subspaces on an **absolute** validity scale where
that luck is invisible.

## 2. What was already tried, and why this is not a repeat

A permutation-null selection criterion was tried before and gave coin-flip (0.50) on
moons/circles. That was null-calibration applied to the **persistence** signal, which has since
been shown to be intrinsically too weak — calibrating a weak signal cannot rescue it. This
proposal applies calibration to the **graph-cut+density** signal, which demonstrably works.
That is a real difference, but it is a *reason to retry*, not a reason to expect success.
The prior negative is recorded here so nobody later mistakes this for an untried idea.

## 3. Null model (H0)

For a candidate subspace `S`, H0 is: *the columns of `S` carry no joint structure, but have the
observed marginal distributions.*

Realisation: independently permute each column of `X[:, S]` with its own random permutation.
This destroys joint structure exactly and preserves each marginal exactly. It is the right null
because a noise subspace's apparent clusters arise from marginal density fluctuations, and this
null keeps those — so a noise subspace gets no credit for them.

Rejected alternatives, and why: *Gaussian parametric null* (wrong — our noise columns are
uniform, and marginals matter); *resampling rows* (wrong — destroys marginal shape too);
*rotating the subspace* (wrong — not a null for feature selection).

## 4. Statistic and correction

For raw score `q(S)` and `B` null draws `q_1..q_B`, the empirical p-value with the standard
add-one correction:

    p̂(S) = (1 + #{ q_b ≥ q(S) }) / (B + 1)

Multiple-comparison correction across the `m = C(p,2)` candidates: Benjamini–Hochberg for the
*acceptance* decision (§6, Claim 2). For *ranking* (Claim 1), BH is monotone in p̂ and therefore
does not reorder — ranking uses p̂ directly. This is stated explicitly because it is the trap in
the whole idea, see next section.

## 5. STAGE 0 — the go/no-go diagnostic (run this FIRST, before building anything)

**The trap:** if the null distribution is *identical* across all noise subspaces, then calibrating
is a monotone transform of the raw score, the ranking is unchanged, and Claim 1 buys **nothing**.
Calibration can only improve selection if the null distribution *varies* across subspaces.

So the first experiment is not the method, it is the diagnostic:

> Draw 200 noise-only subspaces from a p=40 instance. For each, estimate the null distribution of
> the hybrid score with B=200 permutations. Test whether the null mean and null sd differ across
> subspaces by more than Monte-Carlo error (Levene / Kruskal–Wallis on the draws, plus the
> practical effect size: sd of the per-subspace null means, divided by the mean null sd).

**Gate:** if the ratio (between-subspace sd of null means) / (within-subspace null sd) is
**< 0.25**, nulls are effectively homogeneous → **Claim 1 is declared dead on arrival**, we do NOT
build the calibrated ranker, and we proceed to Claims 2 and 3 only. This gate exists to stop us
spending two weeks on something arithmetic can rule out in an afternoon.

## 6. The three claims, stated separately

They have very different prior odds and must not be reported as one result.

**Claim 1 (selection ranking) — the gamble.** Calibrated ranking beats raw ranking at high p.
Gated by Stage 0.

**Claim 2 (abstention) — valid regardless of Stage 0.** With BH control at q=0.10, the method can
output "no structure found" instead of forcing a split. Measured on planted-null datasets (all
columns noise, no clusters): the false-discovery rate should be ≤ 0.10. None of the neighbouring
methods (SUBCLU, HTC, oblique trees) can abstain, so this is a capability claim, not a
performance claim, and should be written up as such.

**Claim 3 (split meta-choice) — the most likely to work, and the one Enrong asked for.** Run each
candidate split (persistence / HDBSCAN / spectral) through the *same* calibration and pick the
(subspace, split) pair with the smallest p̂. Calibration is exactly the tool for this, because raw
HDBSCAN-stability and raw NCut are not on a common scale and cannot otherwise be compared. If
this works it converts "no single split wins all shapes" from a weakness into a designed
component — the unsupervised model-selection rule.

## 7. Pre-specified success criteria (fixed now, not after seeing results)

All at 20 seeds, on the standard six shapes.

* **Claim 1 PASSES** iff mean rank-1 selection at p=40 over {moons, jain, spiral} improves by
  **≥ 0.15 absolute** over the uncalibrated hybrid, **AND** drops by **≤ 0.05** on
  {circles, gauss2} (no-harm constraint on the shapes already at 1.0).
* **Claim 2 PASSES** iff empirical FDR on planted-null data is **≤ 0.10** at q=0.10, and power
  (detecting real structure at p=12 on the four shapes where the hybrid already achieves rank-1)
  is **≥ 0.80**.
* **Claim 3 PASSES** iff the meta-chooser picks the oracle-best split on **≥ 0.70** of
  (shape, seed) cells where a unique oracle-best split exists.

Anything short of these is a FAIL and gets written up as a negative result in
`docs/experiments/`, in the same detail as a positive one.

## 8. Abandonment conditions and the iteration cap

* Stage 0 gate fails → Claim 1 abandoned, no further work on calibrated ranking.
* **At most 3 design iterations**, and every one of them happens on the **development seed block
  (seeds 100–119) only.** The evaluation block (seeds 0–19) is touched **once**, at the end.
  After the third iteration, whatever exists goes to evaluation and is reported as-is.
* If Claims 1 and 3 both fail, null-calibration is closed as a direction and recorded as such;
  we do not go looking for a fourth framing of it.

## 9. Anti-rigging guards

1. Dev/eval seed separation as above. This is the main guard — it is what makes the reported
   number an out-of-sample number.
2. `flame` stays in every table. It is a known scope boundary, not a dataset to drop.
3. The uncalibrated hybrid is reported **alongside** the calibrated version in every table.
4. Per-shape numbers always reported; no averaging a failure away inside a mean.
5. The exchangeability shortcut (§10) is an *assumption*, and §10's validation is mandatory,
   not optional.
6. `k=10` and `core_k=5` remain at their untuned defaults throughout this experiment, so that
   any improvement is attributable to calibration and not to incidental retuning.

## 10. Compute plan, and the assumption it rests on

Exact per-subspace nulls are infeasible: at p=40 that is 780 subspaces × B=200 permutations ×
~30 ms ≈ 78 minutes for a *single* (shape, seed) cell.

Shortcut: if noise columns are exchangeable, the null depends only on `(n, |S|)`, so it can be
fitted **once per cell** with B=500 draws (~15 s) and reused for every subspace.

Note the tension, which is deliberate and is the interesting part of this design: the shortcut is
valid exactly when Stage 0 says nulls are homogeneous — which is exactly when Claim 1 is dead.
So the two live paths are:

* Stage 0 homogeneous → cheap shortcut valid → Claims 2 and 3 only.
* Stage 0 heterogeneous → Claim 1 alive, shortcut invalid → we need the middle option:
  a **regression-calibrated null**, modelling null mean and sd as a function of cheap
  per-subspace covariates (marginal skew, kurtosis, effective density) fitted on a sample of
  subspaces. That is tractable, and its adequacy is itself checked against exact nulls on a
  held-out sample of 50 subspaces before it is used anywhere.

## 11. What gets reported regardless of outcome

A `docs/experiments/exp-016-null-calibration.md` write-up containing: the Stage 0 diagnostic
number, all three claims with their pass/fail against the thresholds in §7, the per-shape tables,
and the dev-block iteration history (what was changed and why). A failed pre-registration is a
publishable finding for the characterization framing; a quietly abandoned one is not.

---

**Sign-off:** _______________________  (Enrong)   Date: ____________
