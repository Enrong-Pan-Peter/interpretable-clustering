# exp-013 — Is there ANY dataset where the EA's SEARCH beats greedy? (structural answer)

**Motivation.** exp-012 killed the diversity/why-EA claim on easy (pair-minimal) data. Enrong's
hypothesis: the EA may win on HARDER data where minimal panels are size >=3, which defeats pair
enumeration and forces the search to work. Tested three structural regimes.

## 1. Additive Gaussian (diagonal): means differ by delta in each of R informative dims.
Never separates cleanly under persistence: size-4 ARI <= 0.58 even at delta=2. For additive
isotropic structure, per-dim SNR = joint SNR / sqrt(k) -> the separability RATIO is constant in k
-> there is no clean "need exactly k dims" threshold. Persistence needs a density GAP; Gaussians
lack one. So Gaussian redundancy cannot make a size-3-minimal panel.

## 2. Jointly-necessary non-convex (nested hyperspheres, 3 dims): CLEAN size-3, but a NEEDLE.
Inner sphere r=1 inside outer shell r=3 in dims {2,3,4}, uniform noise elsewhere.
- size-1 ARI ~0.03, size-2 ~0.02, **size-3 ARI 0.97** -> a genuine jointly-necessary triple.
- BUT: {2,3,4}+1 noise dim -> ARI 0.00; every subset -> 0.00. The valid region is the SINGLE point
  {2,3,4} in the subset lattice (no marginal signal from any direction).
- No method finds it: EA (no-seed, B=1260), greedy, and random (B=1500) all land at ARI ~0.

## 3. Easy redundant (exp-012): panels are pairs -> pair-seed ENUMERATES them; search adds nothing.

## Structural conclusion (the important part)
"Minimal panel > pairs" REQUIRES jointly-necessary features == NO marginal signal == a NEEDLE with
no gradient and no building blocks. Needles defeat every search equally, so the EA's recombination
advantage has nothing to exploit. Conversely, any structure WITH marginal signal (a gradient) is
solved by plain greedy. Across the natural spectrum the EA therefore never has a search edge:

    gradient-rich  -> greedy solves it (EA not needed)
    needle         -> nobody solves it (EA not special)

The theoretical home of an EA advantage is DECEPTIVE-but-decomposable landscapes (greedy gets
trapped, a population escapes). That does not arise naturally in connectivity subspace selection;
constructing one carries a rigging risk and may not reflect real data.

## Implication for the paper
Do NOT stake the contribution on "the EA earns its keep via search." Honest routes:
(A) methodology-first paper — fair-evaluation confound + persistence fitness + interpretability —
    with the EA reported as ONE search backend that is competitive-with (not superior-to) greedy;
(B) ONE pre-registered test of deceptive-but-decomposable structure — the only principled shot at a
    real EA-beats-greedy result — with explicit anti-rigging guards;
(C) reframe the EA's value as multi-objective convenience (quality / parsimony / novelty in a single
    run and Pareto front), which is honest but not a search-superiority claim.

Scripts: inline probes this session; run_diversity.py (exp-012).
