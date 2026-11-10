# exp-001 — Subspace parity: is ATOMIC's silhouette/DB win a metric-space artifact?

**Status:** first result (synthetic, controlled). **Phase:** 1 (fair evaluation).
**Owner:** Enrong. **Depends on:** the Phase-0 re-implementation (`atomicplus/`).

## Hypothesis
ATOMIC scores silhouette / Davies–Bouldin in its **selected low-dim subspace**; the
paper's baselines were (probably) scored in **full space**, where those metrics collapse
via distance concentration. If so, ATOMIC's reported advantage is partly a *measurement*
effect, not a clustering-quality effect (caveat #1 / audit H1).

## Setup
- Data: `synthetic.two_cluster_subspace(n=200, p=20, informative=[4,11])` — two tight
  Gaussian clusters separated **only** in dims 4 and 11; the other 18 dims are noise.
  Ground-truth labels and defining features known.
- Preprocess: 2-NN impute + [0,1] scale (paper §3.1).
- Metric spaces compared: full ℝ²⁰ vs. the true informative subspace ℝ²={4,11}.
- Harness: `evaluation/harness.py` (`subspace_parity_demo`, `compare`).

## Command
```
python scripts/demo_fairness.py
```

## Result
**(1) Subspace parity — the SAME true partition, scored in two spaces:**

| space | dims | silhouette | Davies–Bouldin |
|---|---|---|---|
| full | 20 | 0.240 | 1.633 |
| subspace {4,11} | 2 | **0.873** | **0.182** |

Nothing changed but the space, yet silhouette jumped 3.6× and DB fell 9×. That gap is
pure measurement.

**(2) Comparison — every method scored in full space vs. the subspace:**

| method | sil_full | db_full | sil_sub | db_sub | ARI | NMI |
|---|---|---|---|---|---|---|
| ATOMIC | 0.240 | 1.633 | 0.873 | 0.182 | 1.000 | 1.000 |
| KMeans (fit=full) | 0.240 | 1.633 | 0.873 | 0.182 | 1.000 | 1.000 |
| GMM (fit=full) | 0.240 | 1.633 | 0.873 | 0.182 | 1.000 | 1.000 |

k-means and GMM recover the **same** true partition (ARI=1.0) in full space, so once all
three are scored in the same space their silhouette/DB are **identical**. The only thing
that ever differed in the paper's tables was the scoring space.

**Side finding (k̃ fragility).** With the auto-selected k̃ (the *smallest* stable k = 3
here — the sparsest graph, max single-linkage chaining), ATOMIC's own `best()` selected
spurious **noise** dims [2,5,9,16] with ARI≈0.01, and the true split was not even on the
Pareto front. At a larger fixed k̃=8 it recovers the true split (ARI=1.0). The flat
fitness `-(C-2)²` cannot rank the many subsets that all hit C=2, so the choice of k̃ and
tie-breaking decide everything (caveats #2, #3, #7; audit M5).

## Conclusion
On this controlled case ATOMIC is **not better** than k-means/GMM once compared in a
common space — the paper's silhouette/DB advantage is explained by scoring ATOMIC
in-subspace and baselines in full space. External metrics (ARI/NMI), which are
space-invariant, put all three level. This supports Phase 1's design: report internal
metrics in a *shared* space **and** external metrics, never internal-only across
different-dimensional spaces.

Two consequences for the plan:
1. The contribution must lean on **interpretability + recursive capability + diversity**,
   not raw silhouette dominance (audit H1 — already the locked framing).
2. **Continuous persistence fitness (Phase 2)** and **k̃ robustness (Phase 3)** are
   necessary: the flat objective + smallest-stable-k is what makes ATOMIC's own
   selection fragile here.

## Caveats
- The generator encodes ATOMIC's own inductive bias (axis-aligned subspace Gaussians;
  audit M3), so this shows the *mechanism*, not a general verdict. **Re-run on the UCI
  sets** (where baselines may genuinely lose in-subspace) before drawing conclusions.
- UCI labels are classification labels, not guaranteed geometric clusters (audit M1):
  read ARI/NMI alongside internal metrics.
