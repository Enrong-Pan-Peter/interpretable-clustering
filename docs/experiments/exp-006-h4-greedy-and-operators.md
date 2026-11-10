# exp-006 — H4 (does the EA beat greedy?) + the operator diagnosis

**Status:** preliminary (easy synthetic); reorders the plan. **Phase:** 1/5.

## Setup
`two_cluster_subspace(p=12, informative=[4,9])` (true optimum = the 2 dims [4,9]). Compare, on
the SAME persistence objective: greedy forward-selection, random search, and the EA. Persistence
is ratio-normalized (higher = cleaner split); [4,9] alone scores 5.33, fillers dilute it.

## Result
| method | features | persistence | ARI |
|---|---|---|---|
| greedy forward-selection | **[4, 9]** | **5.33** | 1.000 |
| random search | [4, 9] | 5.33 | 1.000 |
| EA (OR crossover, current) | [0,1,4,7,9] etc. | ~1.9 (4 seeds) | 1.000 |

EA crossover ablation (mean over 4 seeds): OR = 1.94 (4.2 feats), uniform = 2.15 (3.2), set = 2.67 (3.8).

## Findings
1. **The current EA loses to greedy on its own objective** (persistence ~2.0 vs 5.33) AND on
   interpretability (4-5 feats vs 2), *systematically* across seeds. Everyone gets ARI 1.0 here
   (easy problem), so the separation is on persistence + parsimony, not partition quality.
2. **Cause = the operators, not the search idea.** OR-crossover (monotonic union -> bloat) plus
   an over-disruptive symmetric mutation (per-bit 0.45 ~= 5 flips on p=12) stop the EA from
   fine-tuning down to the clean [4,9]. Swapping crossover helps only modestly (1.94 -> 2.67);
   the mutation is the other half.
3. **This is the answer to "is parsimony important?"** -- it is not cosmetic: the bloat makes
   the EA uncompetitive with greedy. Parsimony (Phase 5) is a **prerequisite for a fair H4
   benchmark**, not an afterthought.

## Consequence for the plan (reorder)
Run **Phase 5 (operators: uniform/set crossover + asymmetric low-rate mutation, add ~1/p,
remove 3-5x)** BEFORE the full benchmark. A benchmark run now would show "EA loses to greedy"
as an operator artifact. After Phase 5, re-run H4 on real/harder data -- where greedy can get
trapped in local optima and the EA's diversity should pay off -- for the real verdict.

*(Experiments-first paid off: 4 quick runs surfaced that operators are load-bearing and reordered
the plan before we spent a full 30-run benchmark on a handicapped EA.)*

## Caveat
Easy synthetic (all ARI 1.0). Whether the *fixed* EA beats greedy on hard/real data (the actual
H4 question) needs the full benchmark, post-Phase-5. Greedy/random baselines + spectral are built
(`evaluation/search_baselines.py`, `baselines.spectral_best`); `scripts/run_benchmark.py` pending.
