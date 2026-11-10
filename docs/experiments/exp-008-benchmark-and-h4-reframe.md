# exp-008 — Benchmark harness + the H4 reframe (greedy is strong; the EA's real case)

**Status:** harness built + validated; a decision-changing preliminary finding. **Phase:** 1/H4.
**Script:** `scripts/run_benchmark.py` (H4 single-split track + partition track, multi-seed, Friedman).

## The finding (before the full run)
Comparing the EA to greedy forward-selection on the SAME persistence objective, on convex
subspace-cluster synthetics:

| problem | greedy persistence (#feat) | EA persistence (#feat), Phase-5 operators |
|---|---|---|
| p=12, dims [4,9] | 5.33 (2) | 4.11 (2.8)  -- close |
| p=20, dims [4,11] | 5.19 (2) | ~1.5 (6), or 3.15 (2.7) only with aggressive removal (drops a true dim 1/3) |

Two things:
1. **Greedy matches or beats the EA on the single split** for convex/axis-aligned clusters
   (which is what our generators and several UCI sets are). Greedy reliably climbs to the clean
   2-feature optimum; the EA gets close only with hand-tuned removal rates.
2. **The Phase-5 operator win was overfit to p=12.** The removal rate `3/p` weakens as p grows
   (0.25 at p=12 -> 0.15 at p=20), so the EA bloats again at p=20. Tuning the rate per-problem
   until the EA wins is benchmark-hacking (the overfitting risk flagged 2026-07-08).

## Honest conclusion
On convex single-split, **the evolutionary search is NOT justified by split quality** -- greedy
is as good or better and far cheaper. So we stop tuning operators to chase greedy, and justify
the EA (if at all) on what greedy structurally CANNOT do:

- **Diversity of alternative panels.** Greedy returns ONE panel; NSLC returns many equally-valid
  minimal panels for the same split (the "same-membership alternative panels" contribution).
  Measurable: count distinct valid panels; greedy = 1 by construction.
- **Non-convex / multi-optimum problems** where greedy is trapped in a local optimum and
  evolutionary exploration escapes. Untested -- all our synthetics are convex (favouring greedy).

## Recommended reframe (before the full 30-run benchmark)
1. **Add a diversity metric** to the H4 track: number of distinct valid panels (ARI >= 0.98 to
   the canonical split) each method yields. Greedy/random ~ 1; the EA should give several.
2. **Add a non-convex / multi-optimum benchmark** (e.g. the jain/spiral/flame projection, or a
   generator with a decoy local optimum) where greedy provably fails and the EA should win.
3. **Do NOT keep tuning operator rates on the convex synthetics.** Pick one robust setting and
   freeze it; let the benchmark judge.
Then run the full benchmark, and let it honestly report: greedy competitive on convex split; EA's
value = diversity + non-convex + the recursive tree.

## Note
This is the fair-benchmark infrastructure doing its job -- it caught the operator overfitting
before we built conclusions on it, and it reframes the EA's contribution onto defensible ground.
