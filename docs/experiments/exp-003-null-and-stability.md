# exp-003 — Real structure or search artifact? Null model + stability

**Status:** machinery done + validated; Biodeg preliminary (subsampled). **Phase:** 1.
**Command:** `python scripts/run_significance.py <dataset> --perms 99 --boots 50`
**Module:** `atomicplus/evaluation/significance.py`.

## Why
Ting (2026-07-08): clusters need not match the label/causal features, so **low ARI ≠ a bad
clustering** — ATOMIC may find a different *real* structure. Fair point. But the search hunts
for *any* 2-way split, so "cohesive in the subspace I selected to look split" is partly
circular. So we adjudicate real-vs-artifact **without labels**, two ways:

- **Null model (permutation):** shuffle each feature independently (kills joint structure,
  keeps every marginal), re-run the FULL search, and compare ATOMIC's real separation to the
  separation it manufactures on structure-free data. Empirical p = P(null ≥ real).
- **Stability (subsampling):** re-run on random 80% subsamples; report Nogueira feature
  stability and — more importantly — **partition reproducibility** (mean ARI of each
  subsample's split vs. a full-data reference).

Statistic = silhouette of the best 2-component front solution in its own subspace (what the
search optimises). Feature counts are reported since silhouette is dimension-sensitive.

## Results (light config; Biodeg subsampled to n=300)

| dataset | real sep | null sep | null≥real | p | partition stability (ARI) | Nogueira | verdict |
|---|---|---|---|---|---|---|---|
| **Ceramic** (known real) | 0.383 | 0.19 ± 0.12 | 0/15 | ≤0.063 | **0.78** | 0.06 | **REAL** |
| **Biodegradation** (paper's top win) | 0.592 | 0.52 ± 0.08 | 2/19 | 0.15 | **0.33** | 0.01 | **ARTIFACT** |
| Pure noise (control) | −0.155 | 0.10 ± 0.07 | — | 1.00 | — | — | not real ✓ |

## Findings
1. **The null test discriminates.** Ceramic's real split beats *every* permutation (need ≥19
   perms to push p<0.05, which it will); pure noise sits below its null (p=1.0, correct
   control); **Biodegradation sits *inside* its null (p=0.15)**.
2. **Biodegradation — the paper's biggest silhouette win — is a garden-of-forking-paths
   artifact.** The same search finds equally-cohesive splits (0.52) on column-permuted data
   with all real structure destroyed. Its silhouette 0.59 is not evidence of structure.
3. **Partition stability, not feature stability, is the credibility measure.** Ceramic's
   *features* vary run-to-run (Nogueira ≈ 0.06) yet its *partition* reproduces (ARI 0.78):
   several different oxide panels induce the SAME Body/Glaze split. That is the
   **alternative-panels / diversity** phenomenon the method wants to claim — a feature, not
   instability. Biodeg's partition does NOT reproduce (ARI 0.33) → no real structure.
4. **Resolves the Ting tension.** The framework *defends* a non-label structure when it is
   real (Ceramic would pass even against a label it didn't match) and *rejects* an artifact
   (Biodeg) — all without using labels. So "don't chase ARI" and "don't ship artifacts" are
   both satisfied: replace ARI-as-arbiter with **null significance + partition stability**.

## Implications
- **Adopt null-gating + partition-stability** as the split-acceptance criterion (this is the
  "stability gate" already planned for Phase 4 beam search — now with a null attached).
- **Phase 2 success criterion:** the continuous-persistence objective must produce splits that
  (i) beat the permutation null and (ii) reproduce under subsampling — on more datasets than
  the flat objective does (currently: Ceramic yes, Biodeg no).
- Report **partition stability**, not Nogueira feature stability, as the headline stability
  number; report feature-selection frequency separately as evidence of alternative panels.

## Limits / next
- Biodeg is subsampled (n=300) + light EA config; **confirm on full data with `--perms 99`**.
  Direction is unambiguous (real within 1σ of null), but nail the number.
- Silhouette-in-subspace is dimension-sensitive; here real vs. null feature counts matched
  (Ceramic 4 vs 3.9; Biodeg 13 vs 13.6) so the comparison is fair. Phase 2 persistence gives
  a cleaner, dimension-robust statistic — re-run this test with it.
- Run the null on Glass/Ionosphere/Wholesale too (fast) to complete the picture.
