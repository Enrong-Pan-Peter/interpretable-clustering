# exp-002 — UCI comparison: does ATOMIC actually beat the baselines?

**Status:** complete for all 7 paper datasets (Cervical has no usable label → internal only).
**Phase:** 1. **Command:** `python scripts/run_uci_comparison.py` (+ `build_raw_uci.py` for biodeg/ceramic).

## Setup
2-NN impute + [0,1] scale. ATOMIC: clean-room re-impl, auto k̃, pop=60/μ=60/λ=40/gen=25.
Flat fitness ties every 2-component split and the paper never states how it picks its one
reported solution (caveat #2,#7), so ATOMIC gets its **best shot**: the front's 2-component
solution with the best silhouette in its own subspace. All methods scored in full space AND
ATOMIC's subspace V; ARI/NMI vs. labels are space-invariant. Baselines use silhouette
model-selection (fairer than the paper's WCSS rule, which degenerates to k=20).

## Results (ATOMIC best-shot vs. baselines)

| dataset | p | ATOMIC feats (reduction) | ATOMIC sil_sub | k-means sil (full) | k-means sil (re-fit in V) | ATOMIC ARI | best baseline ARI |
|---|---|---|---|---|---|---|---|
| Glass | 9 | 2 (78%) | 0.64 | 0.53 | 0.51 | **−0.01** | **0.24** (kmeans) |
| Wholesale | 7 | 2 (71%) | 0.76 | 0.80 | 0.73 | 0.02 | 0.05 |
| Ionosphere | 34 | 9 (74%) | 0.39 | 0.31 | 0.32 | **0.01** | **0.40** (dbscan-sub) |
| Ozone (n=600) | 72 | 29 (60%) | 0.03 | 0.33 | 0.38 | 0.04 | ~0 |
| Ceramic | 17 | 4 (76%) | 0.38 | 0.36 | 0.38 | **1.00** | **1.00** (kmeans) |
| Biodegradation | 41 | 13 (68%) | 0.58 | 0.39 | 0.22 | **−0.02** | 0.07 |

## Findings
1. **ATOMIC often does win on silhouette — reproducing the paper's headline.** On Glass,
   Ionosphere, and Biodegradation its silhouette exceeds every baseline (Biodeg: 0.58 vs
   k-means 0.22 in the same subspace). On Ozone it loses badly (matching the paper's own
   weak Ozone number 0.03 ≈ 0.0297 — a re-implementation sanity check).
2. **...but those silhouette wins are not real clustering.** ATOMIC's ARI ≈ 0 on 5 of 6
   sets (−0.02 to 0.04). Its high-silhouette splits are cohesive-looking geometry in a
   self-chosen low-D subspace that does NOT match the classes. Meanwhile k-means/DBSCAN
   reach ARI 0.24–0.40 on Glass/Ionosphere. High silhouette + ~0 ARI = the tell.
3. **The silhouette edge is largely the measurement space.** Re-fitting baselines inside
   ATOMIC's subspace shrinks or erases the gap (Ceramic 0.38 vs 0.38; Wholesale 0.73 vs
   0.76). The paper's big margins came from scoring ATOMIC in-subspace vs. baselines in
   full space (caveat #1 / audit H1) — plus a WCSS-crippled k-means baseline (finding #4, exp).
4. **Where structure is genuinely strong, ATOMIC ties, not beats.** Ceramic (Body/Glaze):
   ATOMIC recovers it perfectly (ARI=1.0) with 4 of 17 oxides — including PbO₂, the
   lead-glaze marker — but k-means in full space also gets ARI=1.0 with identical silhouette.
   ATOMIC's only advantage there is **interpretability** (4 named oxides vs. 17), not quality.

## Verdict
On all datasets tested, **ATOMIC does not deliver a genuine, ground-truth-validated
performance advantage.** Its silhouette wins are (a) inflated by in-subspace scoring and a
handicapped baseline, and (b) decoupled from real structure (ARI≈0). Its one clear success
(Ceramic) is a tie on quality, won only on interpretability. This is strong empirical support
for the locked reframing: the contribution is fair evaluation + a better objective +
interpretability/capability — never raw cluster-quality dominance.

## Implication for the proposal (see chat 2026-07-08)
Not a threat to novelty (which is the *synthesis* + mechanism, per literature_review.md), and
it is the **motivating gap**: the flat component-count objective finds cohesive-but-meaningless
splits. It DOES set the bar for Phase 2: the persistence objective must lift ARI/NMI (recover
real structure) while keeping interpretability — "interpretable but ARI≈0" is not publishable.
Add a null model (audit H3) to show current ATOMIC splits are noise-level, and adopt "beats
the ATOMIC baseline's ARI and is competitive with strong baselines, at higher interpretability"
as the success criterion.

## Limits / next
- Modest EA budget + auto k̃ (smallest-stable-k = max chaining); a longer run would find the
  paper's more-reduced solutions (e.g. Biodeg 2-feat, sil≈0.9) — which would push silhouette
  UP and, predictably, keep ARI≈0 (the extreme of the confound). Worth confirming once.
- Add 30-run mean±std + Friedman/Nemenyi; add the null-model permutation test.
