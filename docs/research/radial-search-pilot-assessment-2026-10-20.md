# Pilot assessment and bounded transition to method design

## Material Passport

- Origin Skill: academic-research-suite, experimental validation and method design
- Origin Date: 2026-10-20
- Verification Status: saved-state numerical audit passed; descriptive interpretation; next design proposed, not yet implemented or evaluated
- Version Label: radial_search_pilot_assessment_v1
- Evidence: [completed pilot](../../results/research_radial_search/20261020T174212_534139Z/summary.md), [audit](../../results/research_radial_search/20261020T174212_534139Z/audit.json), [frozen development protocol](hidden-panel-search-2026-10-20.md)
- Scope: synthetic development evidence for a restricted radial rule family; no novelty, semantic-validity, minimum-panel or calibrated error-rate claim

## Decision

**Start the next algorithm design now. No additional prerequisite diagnostic suite is needed.** We already have a native model, a defined predictive fitness, and executable support-search algorithms. The pilot identifies two concrete weaknesses to redesign. Further tests should evaluate those changes, not postpone design.

Bound the next synthetic development phase to **one targeted ablation batch followed by one frozen replication/stress batch**. If the targeted design fails, permit at most one explicit repair and repeat of the same development batch; report the reuse as development. If that still fails, narrow or replace this search mechanism instead of adding another open-ended sweep. This is a development decision rule, not a claim that two batches can complete all thesis validation. Real-data comparison, interpretable-panel verification and strong published baselines will still be needed afterward.

## Verified findings

The run completed all **36 cases, 144 method runs and 36,864 two-band panel evaluations** in **36.12 minutes**. Each method received 256 unique fits per case. The independent auditor passed **793,616 checks with zero errors**. No optimizer nonconvergence was recorded. This audit replays saved numerical computation; it is not an independent rerun or proof of scientific validity.

The 15 shell cases span five signal dimensions and three data/search seed pairs:

| Search method | Exact planted panels recovered | Mean test ARI |
|---|---:|---:|
| Random | 0/15 | 0.198 |
| Random initialization + local search | 2/15 | 0.460 |
| Squared-dependence initialization + local search | 10/15 | 0.765 |
| Shuffled-dependence initialization + local search | 2/15 | 0.444 |

These are descriptive averages over heterogeneous geometries, not 15 independent identically distributed replicates or estimates of universal performance. The per-dimension results matter more than the aggregate:

| Signal dimension | Dependence-guided exact recovery | Test ARIs by seed |
|---|---:|---|
| 2 | 3/3 | 1.000, 1.000, 1.000 |
| 3 | 3/3 | 1.000, 1.000, 1.000 |
| 4 | 1/3 | 0.661, -0.002, 1.000 |
| 5 | 0/3 | 0.810, -0.001, 0.001 |
| 8 | 3/3 | 1.000, 1.000, 1.000 |

The supplied diagnostic panel achieved test ARI 1.0 in all 15 shell cases. Across the four methods, every one of the 14 visits to the exact panel selected it; all 46 failures to recover it omitted it from the evaluated candidates. In those failures its post-search diagnostic score was higher than the selected score. This is evidence of a support-discovery obstacle in these runs, rather than a demonstrated rejection of the useful panel by the final ranking score. It does not prove that all useful panels have an accessible local objective landscape or that the score always agrees with scientific meaning.

All **18 single-population/control cases per method** remained unflagged, including independent/correlated Gaussians, Student-t, single shells and common-center scale mixtures. This is encouraging behavior under this limited generator family, not a calibrated false-split guarantee. Some unsuccessful two-feature shell searches flagged unrelated singleton measurements with near-zero ARI to the intended labels. Matched nuisance marginals can support different structure; a density flag is not semantic validation. The mean-shift case remains outside this radial rule family's successful scope.

## Two specific design changes

### 1. Replace a single moment with a nonlinear dependence proposal

The present proposal statistic is `abs(corr(z_j^2, z_k^2))`, using fit-only standardized measurements. Pairwise second-moment effects nearly cancel around dimension four for this generator and are weak at dimension five. The observed difficult regimes agree with that predeclared concern; this agreement is a mechanism hypothesis, not a proof that it is the sole cause of every failure.

The first replacement will use **normalized, centered Gaussian-kernel dependence between squared coordinates**, with bandwidth determined from fitting observations only. For squared measurements `u_j`, let `K_j` be their Gaussian Gram matrix, `H` the centering matrix and `A_j = H K_j H`. Define the proposal similarity

`D_jk = trace(A_j A_k) / sqrt(trace(A_j A_j) trace(A_k A_k))`.

Handle a degenerate zero denominator as zero dependence. Use a fixed median positive pair-distance bandwidth convention; do not tune bandwidths using support labels or held-out ARI. This is an HSIC-related normalized kernel statistic used only to rank proposals. It is not an independence-test p-value or a clustering fitness. The original HSIC work establishes the kernel-dependence framework; the suggestion that it improves these failed panel searches is our untested inference. [Gretton et al., A Kernel Statistical Test of Independence](https://proceedings.neurips.cc/paper/2007/file/d5cfead94f5350c12c322b5b664544c1-Paper.pdf).

The model still predicts from named original measurements through the same explicit squared-radius rule. No latent embedding becomes the user-facing explanation. Pairwise kernel dependence can still miss purely higher-order dependencies, and its dense computation has nontrivial cost. First measure it at p=24; use bounded fitting-row subsampling or an explicitly tested approximation before claiming scalability to thousands of features. This is a replacement for exhaustive subset proposals, not a claim that pairwise computation itself is free.

### 2. Exploit a promising partial panel before spending the whole neighborhood budget

The current refinement evaluates a full shuffled neighborhood of one anchor before moving to the best improvement. In `shells_d4_p24_seed2401_search3203`, dependence-guided search found a panel missing only one correct feature at the **241st** evaluation. In `shells_d5_p24_seed2401_search3203`, it found such a panel at the **199th** evaluation. The exact panel was never evaluated before the 256-fit budget expired. Other failed runs never got comparably close, so scheduling alone is not sufficient.

Use **first-improvement refinement** as the next minimal scheduling change: after an evaluated add/drop/swap move improves the incumbent under the same deterministic ranking, immediately begin proposals around that improved panel. Keep the existing random restarts and evaluation cache. Preserve the best panel seen globally. Previously evaluated neighbors do not consume more fits; strict improvement/tie ordering prevents cycling. Record parent support and move type so the traversal can be checked. The expensive panel-fit budget, starting candidates, allowed sizes and objective must remain matched to the original refinement.

A small diverse beam is a later option only if this simpler change exposes a specific need. Do not add first-improvement, a beam, a new kernel, a new score and a new population generator in one unexplained change.

## What we are designing about the fitness now

The current fitness is a real predictive objective:

`G(S) = mean_search[log g_2,S(x_S) - log q_0,S(x_S)]`.

It compares models on a common full observation space through the fixed-background cancellation. Keep it unchanged in the next search comparison because the pilot supports its ranking when the planted panels are reached. Replacing it simply because it is not novel would discard a useful control.

The broader method should retain **separate quantities**, with distinct roles:

| Quantity | Role |
|---|---|
| Predictive gain G(S) | Guide support exploration and select a density model |
| Two-band versus one-band gain C(S) | Ask whether two bands add predictive value, distinct from non-Gaussianity |
| Fitted spatial valley and group occupancy | Describe the proposed split and reject obvious degenerate candidates |
| Number of measurements and rule terms | Expose explanation cost and guide a separately evaluated compression step |
| Fresh-sample behavior | Check that a frozen rule and its claimed usefulness generalize |

Do not combine these into an arbitrary normalized z-score. Record the quality-versus-feature-count frontier rather than claiming a globally minimum panel. Compression requires its own explicit predictive-loss/recovery tolerance and an untouched final evaluation; those tolerances are not established by this pilot. The existing provisional flag is not yet a statistically calibrated acceptance rule. None of these components validates biological or domain meaning without independent evidence.

This is the fitness architecture for the thesis method. Its implementation order is deliberate: fix the demonstrated search weaknesses first while retaining a stable score, then change score/acceptance/compression only for an observed failure that those components can address.

## Finite experiment sequence and decision gates

**Before implementation: zero additional diagnostic batches.**

**Batch 1 — one targeted 2x2 ablation after implementation.** Cross old/new dependence proposals with old/new refinement; four variants, all other ingredients fixed. Reuse the saved development populations for attribution and explicitly label that reuse. Prioritize dimensions four and five, retain two/three/eight as regression cases, and retain the existing controls. Assess paired changes in recovery, oracle visitation, feature count, fresh validation gains, flags and time at the same 256-fit budget. Candidate comparisons here are development, not independent confirmation. Unit tests and the numerical audit are software checks, not additional scientific parameter sweeps.

For the first decision, ask whether the new proposal raises useful-panel visitation in the difficult cases, whether prompt refinement improves exploitation at the same budget, and whether improvements survive fresh validation without sacrificing the already successful regimes. If the revised mechanism still misses panels with a large known score advantage, diagnose its recorded proposal path once; permit at most one documented repair and repeat. If that fails again, narrow the supported regime or replace the search approach. Do not respond by automatically increasing the budget through another broad sweep.

**Batch 2 — one frozen replication/stress batch if Batch 1 succeeds.** Freeze the chosen search, objective, budgets and thresholds. Use previously unseen data seeds, cross multiple search seeds per population to separate algorithm variability from data variability, and include a higher nuisance-feature count and a harder separation condition chosen before looking at those outcomes. Compare the frozen old and new versions. This is the evidence gate for investing in an application benchmark; it does not replace comparison with strong published methods.

After that, make an explicit retain/narrow/pivot decision. A real-data eligibility preflight can proceed alongside implementation, using measurement semantics and expected geometry rather than screening datasets for favorable final scores. The thesis still needs an application, credible comparator methods and interpretable-panel verification. Improving a standard HSIC-plus-local-search construction alone is not established novelty.

## Interpretation checks: 11/11 reviewed

1. **Simpson's paradox:** report each dimension; aggregate improvements conceal d4/d5 failures.
2. **Ecological fallacy:** no inference from synthetic groups to individual biological measurements.
3. **Berkson selection:** generators and exclusions are fixed; successful regimes must not erase failures.
4. **Collider bias:** no causal adjustment claim; future hierarchy conditioning would require separate treatment.
5. **Base rates:** controls and shell cases have designed proportions, not real-world cluster prevalence.
6. **Regression to the mean:** development influenced the next design; freeze it before fresh replication.
7. **Survivorship:** all 36 jobs and all four arms completed; zero recorded optimizer nonconvergence; no failed configurations excluded.
8. **Look-elsewhere effect:** 36,864 searched supports do not create that many independent validation trials; flags are heuristic.
9. **Forking paths:** next method is informed by these results; preserve this record and distinguish development from replication.
10. **Causality:** the matched comparison supports scoped computational mechanism checks, not a causal claim about real scientific populations.
11. **Reverse causality:** no causal direction is inferred from feature dependence; it proposes panels only.
