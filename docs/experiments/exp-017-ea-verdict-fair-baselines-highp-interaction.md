# exp-017 — EA still does not earn its keep with a good signal; fair baselines; the high-p problem

> **CORRECTION NOTICE (2026-08-05).** Source `results/ea_newfit.csv` has no `noise` column, so this
> was run on the pre-repair benchmark. Its `enum2_ceil` is also a different configuration from the
> ceiling in `method_baselines*.csv` (circles 0.64 here vs ARI 1.000 there), so do not quote it as
> "the ceiling". The EA-vs-random comparison itself is internally consistent and its conclusion
> stands: **the fitness leading the search shows no advantage for the EA; EA is no better than the
> other search algorithms, and at low p it is worse than random.** Phrase it that way, not as
> "the EA doesn't earn its keep". See `docs/CORRECTIONS.md` C5.

**Setup.** With the working graph-cut+density signal (exp-016), we re-asked the question that had been
confounded by the weak old signal: does an evolutionary search now beat simple baselines?

## Fair-baseline corrections (important, do not undo)
- **"Greedy" must be Sequential Forward Selection** (start from best single feature, add one at a time),
  NOT exhaustive pair enumeration. Enumerating all pairs bakes in the knowledge that the answer is
  size-2 and is really the ceiling, not a search. Fair SFS greedy FAILS on jointly-necessary shapes,
  because no single feature gives a signal to start the climb.
- **"Random search" = sample B subsets, keep the best by fitness, same budget as the EA.** That is the
  standard, strong, fair baseline. Weakening it to a single draw would be sandbagging.

## EA vs CVT-MAP-Elites vs greedy(SFS) vs random on the new fitness (20 seeds, fixed budget 400)
Recovery ARI at p = 12/20/40:
- **fair greedy (SFS):** 0.00 on ALL non-convex shapes at every p (works only on convex gauss2).
- **random:** strong at low p, fades sharply as p grows (moons 0.68/0.34/0.05).
- **plain EA:** worse than random at low p (it bloats to 4-feature panels), a faint bit better at p=40
  on jain (0.16 vs random 0.04) and moons (0.10 vs 0.05), but far below the ceiling. Does NOT beat random.
- **CVT-MAP-Elites:** does not clearly beat random either.
- **enum2 ceiling** (check every pair): holds on moons/circles (~0.6–0.8 at p=40) but fades on jain.

**Conclusion.** Even with a good signal the EA is essentially indistinguishable from random here: a
jointly-necessary needle offers no gradient to follow and no partial building blocks to recombine, so
the EA's operators degenerate to sampling. This REFUTES the hypothesis that the weak old signal was the
only thing holding the EA back. A good signal helps everyone equally; the EA still adds nothing.

## Why high-dimensional selection is hard (two effects, both grow with p)
1. **Coverage (the needle):** the true pair is one of C(p,2) pairs, and a budget-limited search may
   never evaluate it. This hurts moons — the ceiling still finds it, but budget-search does not.
2. **False positives:** with many noise pairs, one overtakes the true pair by luck even under full
   enumeration. This hurts jain/spiral — the ceiling itself fades as p grows.
See `docs/needle.png` and `docs/needle_highp.png` for the graphical version.

## Reframing (for paper positioning)
This is **unsupervised feature-INTERACTION / epistasis detection**: features that matter jointly but not
individually. For pairs the standard solution is an exhaustive O(p^2) scan, not an EA; higher-order is a
genuinely open hard problem. On real data with any marginal signal, plain greedy/forward selection
works. So the EA has no clear home in this problem. This framing likely aligns with the lab's epistasis
expertise. Full context in `docs/HANDOFF.md`.

Scripts: `run_ea_newfit.py` (fair SFS greedy + enum2 ceiling), `run_fitness_sweep.py`.
