"""Per-panel permutation calibration -- score each panel against a scrambled copy of ITSELF.

THE PROBLEM THIS SOLVES, AND WHY IT IS THE ONE BLOCKING THE PROJECT
-------------------------------------------------------------------
Everything the pipeline does today is ENUMERATION over pairs, and it only works because we told
the method the answer is a pair. A tree has to choose a panel at every node without being told its
size, and it cannot, because our scores are not comparable across panel sizes: the hybrid z-scores
each term against the pool of candidates of the SAME size, so a 2-column score and a 4-column score
sit on different scales. exp-018 measured the consequence and then explicitly deferred the cause:

    "Whether the score peaks at the CORRECT panel size ... is a cross-size comparison and raw
     scores are not comparable across sizes; it needs an absolute (scramble-calibrated) score.
     Separate experiment -- do not infer it from these tables."

This module is that scramble-calibrated score.

HOW IT WORKS
------------
For a panel S, permute each of its columns INDEPENDENTLY, B times. That destroys any relationship
*between* the columns -- which is exactly where clusters live -- while preserving each column's own
distribution, the number of columns, and the number of rows. Score the scrambled panels, then
report

    z(S) = (q(S) - mean_b q(S_b)) / sd_b q(S_b)

i.e. how many standard deviations the real panel scores above its own no-structure version. The
units are "SDs above my own null", so a 2-column panel and a 5-column panel are finally on the same
scale, and the number can be thresholded rather than only ranked.

WHAT THAT BUYS
--------------
  * A STOPPING RULE. Grow the panel while calibrated z rises; stop when it falls. Panel size
    becomes something the method discovers instead of something we tell it.
  * ABSTENTION. A node whose best panel does not clear threshold can decline to split and say so,
    rather than emitting a confident-looking arbitrary split. An interpretable tree whose first
    split may be arbitrary is worse than no tree.
  * PER-NODE CONFIDENCE, reportable: "3.8 SDs above what this panel produces with no structure".

NOVELTY: NONE. CITE IT, DO NOT CLAIM IT.
----------------------------------------
This is the standard fix for what the literature calls DIMENSIONALITY UNBIASEDNESS. Vinh, Chan,
Romano, Bailey, Leckie, Ramamohanarao & Pei, Data Mining and Knowledge Discovery 30:1520-1555
(2016) formalise the property and prove z-score normalisation achieves it; UMC (Wang et al., AAAI
2017) calibrates against the same independent-column permutation model, computed analytically for
speed; DUSC (Assent et al., ICDM 2007) divides by the expected value. Our earlier claim that
nothing had been done here since 2008 was wrong and is retracted in docs/CORRECTIONS.md C9. The
value of this module is that it unblocks our pipeline, not that it is new.

THE ONE PLACE OUR VERSION MIGHT ADD SOMETHING is narrow and should be stated narrowly: nobody has
established dimensionality unbiasedness for normalized graph cut or DBCV-style validity indices
specifically, and nobody couples per-subspace calibration with FDR control across the candidate set.

TWO IMPLEMENTATION CHOICES THAT MATTER
--------------------------------------
1. SYNCHRONISED PERMUTATIONS. Every panel is permuted with the same sequence of row orderings
   (`shared_seed`). Monte-Carlo noise then becomes common-mode across panels, so the RANKING is far
   more stable than B alone would suggest, even though each panel's individual z still carries
   O(1/sqrt(B)) error. Do not remove this to "make the nulls independent" -- independence across
   panels is what we are trying to avoid.
2. A FLOOR ON THE NULL SD. When a panel's null scores are near-identical the denominator collapses
   and z explodes, which manufactures spurious winners. `sd_floor` caps that, and `n_degenerate`
   counts how often it fired so the problem cannot hide.
"""
from __future__ import annotations

import itertools
from typing import Callable, Dict, Sequence, Tuple

import numpy as np

#: A scorer takes the panel's data (n x |S|) and returns (score, labels-or-None).
Scorer = Callable[[np.ndarray], Tuple[float, np.ndarray | None]]


def _raw_only(score_fn: Scorer, X: np.ndarray, s: Sequence[int]) -> float:
    """Top-level so joblib can pickle it when the pair sweep runs in parallel."""
    return float(score_fn(X[:, list(s)])[0])


def permute_columns(Z: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Independently permute the rows of every column -- kills joint structure, keeps marginals."""
    out = np.empty_like(Z)
    for j in range(Z.shape[1]):
        out[:, j] = Z[rng.permutation(Z.shape[0]), j]
    return out


def calibrate(score_fn: Scorer, X: np.ndarray, subset: Sequence[int], B: int = 20,
              shared_seed: int = 0, sd_floor: float = 1e-6) -> Dict[str, float]:
    """Calibrated z for one panel: how many SDs it beats its own scrambled version by.

    `shared_seed` must be the SAME for every panel in a comparison -- see note 2 in the module
    docstring. Returns raw, null mean/sd, z, and a `degenerate` flag when the sd floor fired.
    """
    Z = X[:, list(subset)]
    raw, _ = score_fn(Z)
    null = np.empty(B, dtype=float)
    for b in range(B):
        # Seeded per (shared_seed, b) and NOT per panel, so all panels see the same permutations.
        null[b] = score_fn(permute_columns(Z, np.random.default_rng((shared_seed, b))))[0]
    finite = null[np.isfinite(null)]
    if len(finite) < 2:
        return dict(raw=float(raw), null_mean=np.nan, null_sd=np.nan, z=np.nan, degenerate=1.0)
    mu, sd = float(finite.mean()), float(finite.std(ddof=1))
    degenerate = float(sd < sd_floor)
    return dict(raw=float(raw), null_mean=mu, null_sd=sd,
                z=float((raw - mu) / max(sd, sd_floor)), degenerate=degenerate)


def calibrate_many(score_fn: Scorer, X: np.ndarray, subsets: Sequence[Sequence[int]],
                   B: int = 20, shared_seed: int = 0) -> list[Dict[str, float]]:
    """Calibrate a list of panels of possibly DIFFERENT sizes. That is the whole point."""
    return [dict(subset=tuple(s), size=len(s),
                 **calibrate(score_fn, X, s, B=B, shared_seed=shared_seed)) for s in subsets]


def two_stage(score_fn: Scorer, X: np.ndarray, subsets: Sequence[Sequence[int]],
              b_screen: int = 10, b_final: int = 200, keep: int = 50,
              shared_seed: int = 0) -> list[Dict[str, float]]:
    """Cheap screen at low B, then a proper null for the finalists only.

    Calibration multiplies every score evaluation by B, which is the whole cost story: at p=77
    (mice) all 2,926 pairs at B=30 is roughly 90k evaluations. Screening at B=10 and only paying
    B=200 for the top `keep` cuts that by an order of magnitude while leaving the numbers we
    actually report at full precision. Rows keep a `stage` field so a screen-quality z is never
    mistaken for a final one.
    """
    screened = calibrate_many(score_fn, X, subsets, B=b_screen, shared_seed=shared_seed)
    for r in screened:
        r["stage"] = "screen"
    order = sorted(range(len(screened)),
                   key=lambda i: (-np.inf if not np.isfinite(screened[i]["z"]) else screened[i]["z"]),
                   reverse=True)[:keep]
    finals = calibrate_many(score_fn, X, [screened[i]["subset"] for i in order],
                            B=b_final, shared_seed=shared_seed)
    for i, r in zip(order, finals):
        r["stage"] = "final"
        screened[i] = r
    return screened


def chosen_z(trace: Sequence[Dict[str, float]]) -> float:
    """The calibrated z OF THE PANEL THAT WAS ACTUALLY CHOSEN. Do not read ``trace[-1]["z"]``.

    A `grow_panel` trace ends one of three ways and only two put the chosen panel last:

      * stopped because the best extension SCORED WORSE -- that rejected extension is appended with
        ``accepted=False`` and *then* the loop breaks, so ``trace[-1]`` describes a panel the search
        REFUSED, and its z is by construction below the chosen panel's;
      * hit ``max_size``, or ran out of features -- last entry is accepted, so it is correct.

    Reading ``trace[-1]["z"]`` therefore under-reports z on exactly the runs that stopped for the
    principled reason, which biases any THRESHOLD applied to it towards over-abstention. Found while
    wiring exp-024. `run_real_calibration.py` had the same read, so exp-022's `z` and `abstain`
    columns are affected; its ARI columns are not, because those come from `chosen`.
    """
    e = chosen_entry(trace)
    return float(e["z"]) if e else float("nan")


def chosen_entry(trace: Sequence[Dict[str, float]]) -> Dict[str, float] | None:
    """The full trace record of the chosen panel -- carries `degenerate`, which callers need.

    `degenerate=1` means the null SD collapsed and `sd_floor` was substituted, so z is a ratio to an
    arbitrary constant rather than to a measured spread. Thresholding such a z is meaningless, so
    anything that abstains on z must look at this flag too.
    """
    acc = [t for t in trace if t.get("accepted")]
    return dict(acc[-1]) if acc else None


def grow_panel(score_fn: Scorer, X: np.ndarray, seed_subset: Sequence[int],
               max_size: int = 6, B: int = 50, shared_seed: int = 0,
               pool: Sequence[int] | None = None, n_jobs: int = 1,
               ) -> Tuple[Tuple[int, ...], list[Dict[str, float]]]:
    """THE STOPPING RULE. Add the best feature while calibrated z rises; stop when it falls.

    This is the piece that raw scores could never do, because raw scores of different-sized panels
    are not comparable, so "did adding a feature help?" had no answer. Returns the chosen panel and
    the full trace, because the trace is the evidence that the stop was principled rather than a
    hyper-parameter.

    Deliberately simple: steepest ascent, forward only, no removals or swaps yet. Add those once
    the forward-only version is shown to stop in the right place -- a more elaborate search that
    stops in the wrong place teaches us nothing.

    `pool` restricts which features may be added. This is not a shortcut, it is Stage 0 of the
    search doing its job: at p=250 with B=20, trying every remaining feature costs 5,000 scored
    panels PER STEP, which is hours. Screening singletons first and growing only over a shortlist
    is the design. Pass None to consider everything (fine at small p). Whatever is passed must be
    RECORDED in the write-up -- a shortlist is a search decision, not an implementation detail.
    """
    cur = tuple(sorted(seed_subset))
    best = calibrate(score_fn, X, cur, B=B, shared_seed=shared_seed)
    trace = [dict(subset=cur, size=len(cur), accepted=True, **best)]
    candidates = range(X.shape[1]) if pool is None else pool
    remaining = [j for j in candidates if j not in cur]
    while len(cur) < max_size and remaining:
        cands = [(tuple(sorted(cur + (j,))), j) for j in remaining]
        if n_jobs != 1 and len(cands) > 1:
            from joblib import Parallel, delayed
            vals = Parallel(n_jobs=n_jobs)(
                delayed(calibrate)(score_fn, X, s, B=B, shared_seed=shared_seed) for s, _ in cands)
        else:
            vals = [calibrate(score_fn, X, s, B=B, shared_seed=shared_seed) for s, _ in cands]
        scored = [(v, s, j) for v, (s, j) in zip(vals, cands)]
        scored = [t for t in scored if np.isfinite(t[0]["z"])]
        if not scored:
            break
        top, s, j = max(scored, key=lambda t: t[0]["z"])
        accepted = top["z"] > best["z"]
        trace.append(dict(subset=s, size=len(s), accepted=accepted, **top))
        if not accepted:
            break
        cur, best = s, top
        remaining.remove(j)
    return cur, trace


def grow_from_pairs(score_fn: Scorer, X: np.ndarray, n_seeds: int = 10, max_size: int = 6,
                    B: int = 30, shared_seed: int = 0, pool: Sequence[int] | None = None,
                    pair_pool: Sequence[Tuple[int, int]] | None = None, n_jobs: int = 1,
                    ) -> list[Dict[str, object]]:
    """Seed the search from PAIRS ranked by the RAW score, then grow with the calibrated stop.

    WHY THIS REPLACES SINGLETON SEEDING
    -----------------------------------
    The previous design screened single features and grew from the best ones. That is a bet that a
    good panel contains a good single feature -- which is the downward-closure assumption we spent
    the whole project criticising bottom-up methods (CLIQUE, SUBCLU) for making. We built it into
    our own Stage 0 by accident, and it is measurably what breaks the search: on Levine
    CD4T-vs-CD8T, raw graph-cut ranks the true gate (CD4, CD8) at **5 of 496 pairs**, yet neither
    CD4 nor CD8 alone is a standout singleton, so no singleton seed ever starts there and the
    search lands on (CD19, CD41) at ARI 0.012 while enumeration finds ARI 0.987.

    THE DIVISION OF LABOUR, AND IT IS THE POINT
    -------------------------------------------
    Two different jobs, two different statistics, each used only where it was measured to work:

      * RANKING candidates of the SAME size -> the RAW score. Measured: raw graph-cut puts the
        good pairs at median rank 38/496 on Levine CD4T/CD8T and 26/496 on basophil/pDC.
        Calibrated z is worse at this and sometimes inverts (exp-022 2b: z=6.65 on an ARI-0.087
        panel beat z=4.74 on an ARI-1.000 panel).
      * DECIDING WHEN TO STOP GROWING, a comparison ACROSS sizes -> CALIBRATED z, which is the one
        thing raw scores cannot do at all and the one thing exp-021 validated calibration for
        (peaks at the true size in 80% of cells on the density term).

    We were previously using calibrated z for both. It only works for the second.

    COST. p*(p-1)/2 raw pair scores, then n_seeds * (|pool| * B) per growth step -- so
    O(p^2 + k*p*B), NOT O(p^k). At p=250 that is 31k pair scores; at p=2000, 2M, which is a
    screening problem rather than a wall. Panels of size 5 cost five more sweeps of p, not p^5.

    RETURNS THE TOP `n_seeds` FINISHED PANELS, NOT ONE. Committing to the argmax is what fails --
    graph-cut's top-1 pair on Levine is CD11b/HLA-DR at ARI -0.007 while rank 5 is the answer.
    A tree node can show the user several candidate panels; an interface makes that a feature.
    """
    p = X.shape[1]
    cand = list(pair_pool) if pair_pool is not None else list(itertools.combinations(range(p), 2))
    if n_jobs != 1 and len(cand) > 1:
        from joblib import Parallel, delayed
        raw = np.array(Parallel(n_jobs=n_jobs)(
            delayed(_raw_only)(score_fn, X, s) for s in cand), dtype=float)
    else:
        raw = np.array([score_fn(X[:, list(s)])[0] for s in cand], dtype=float)
    order = np.argsort(-np.nan_to_num(raw, nan=-np.inf))
    seeds = [cand[i] for i in order[:n_seeds]]

    out = []
    for rank0, s0 in enumerate(seeds, 1):
        chosen, trace = grow_panel(score_fn, X, s0, max_size=max_size, B=B,
                                   shared_seed=shared_seed, pool=pool, n_jobs=n_jobs)
        e = chosen_entry(trace) or {}
        out.append(dict(seed_pair=tuple(s0), seed_raw_rank=rank0, seed_raw=float(raw[order[rank0 - 1]]),
                        panel=tuple(chosen), size=len(chosen),
                        z=float(e.get("z", float("nan"))),
                        degenerate=float(e.get("degenerate", 0.0)),
                        z_last=trace[-1]["z"] if trace else float("nan"),
                        trace=trace))
    return out


# ------------------------------------------------------------------------------------------------
# SCALING. Two mechanisms, and only the first is an argument -- the second is engineering.
# ------------------------------------------------------------------------------------------------

def two_resolution_scan(score_fn: Scorer, X: np.ndarray, candidates: Sequence[Sequence[int]],
                        n_screen: int = 150, keep_frac: float = 0.02, keep_min: int = 20,
                        seed: int = 0) -> list[Dict[str, object]]:
    """Score every candidate on a ROW SUBSAMPLE, then rescore the survivors on all rows.

    Our score is O(n^2) per candidate, so screening at n=150 instead of n=600 is ~16x cheaper per
    candidate. Screening wide and cheap, then paying full price only for the top `keep_frac`, is
    what makes p=500 (Madelon: 124,750 pairs) comfortable rather than an overnight job.

    This is engineering, not a claim. The screen must never be the reported number -- rows carry
    `stage` so a screen-quality score cannot be mistaken for a final one, and the returned list is
    ordered by the FULL-resolution score for the survivors.

    The assumption it rests on, stated so it can be checked: a subsample preserves the ORDERING of
    candidates well enough that the true winner survives the cut. That is testable -- run with
    keep_frac=1.0 on a small dataset and compare the screen ranking to the full ranking. Do that
    once per new dataset rather than assuming it.
    """
    rng = np.random.default_rng(seed)
    idx = (np.sort(rng.choice(len(X), size=n_screen, replace=False))
           if n_screen < len(X) else np.arange(len(X)))
    Xs = X[idx]
    screen = np.array([score_fn(Xs[:, list(c)])[0] for c in candidates], dtype=float)
    order = np.argsort(-np.nan_to_num(screen, nan=-np.inf))
    n_keep = max(keep_min, int(round(keep_frac * len(candidates))))
    keep = set(int(i) for i in order[:n_keep])
    out = []
    for i, c in enumerate(candidates):
        full = float(score_fn(X[:, list(c)])[0]) if i in keep else np.nan
        out.append(dict(subset=tuple(c), screen=float(screen[i]), full=full,
                        stage="final" if i in keep else "screen"))
    out.sort(key=lambda r: (-np.inf if not np.isfinite(r["full"]) else r["full"]), reverse=True)
    return out


def basin_fraction(grow_fn, ari_fn, candidates: Sequence[Sequence[int]], n_probe: int = 30,
                   success: float = 0.8, ceiling: float = 1.0, seed: int = 0,
                   min_ceiling: float = 0.15) -> Dict[str, float]:
    """How many pairs is it enough to SAMPLE? Measures the size of the basin growth can climb out of.

    THIS IS THE SCALING ARGUMENT, not a speed trick. Enumerating C(p,2) pairs is unnecessary,
    because seed-and-grow does not need the BEST pair -- it needs ANY pair from which growth
    reaches a good panel. On Levine CD4T-vs-CD8T, growth from each of the top five raw-scored pairs
    reached ARI >= 0.952, and 32 of 496 pairs already exceed ARI 0.5 on their own.

    If a fraction f of pairs lie in that basin, sampling s of them at random finds one with
    probability 1 - (1-f)^s. At f = 0.065, fifty draws give 96%. So the cost of search is set by
    1/f, not by p^2 -- and f is a measurable property of a dataset that we can report alongside
    every result rather than assume.

    `grow_fn(pair) -> panel` runs the growth step. `ari_fn(panel) -> float` scores the result
    against labels; it USES LABELS and exists only to measure f, never inside the search.
    Returns f, its Wilson interval, and the number of draws needed for 95% and 99% success.
    """
    # GUARD. If no pair clusters the data at all, the "bar" is a fraction of noise and every probe
    # measures nothing. Madelon burned ~55 hours before we noticed: its pair ceiling is ARI 0.068,
    # because the class is XOR-like on a 5-D hypercube so pairs genuinely carry no signal. Refuse
    # rather than produce a confident-looking number about an empty question.
    if ceiling < min_ceiling:
        return dict(basin_fraction=float("nan"), n_probe=0, hits=0, ci_low=float("nan"),
                    ci_high=float("nan"), draws_for_95pct=-1, draws_for_99pct=-1,
                    mean_grown_ari=float("nan"), success_bar=success * ceiling,
                    aborted=f"pair ceiling {ceiling:.3f} < {min_ceiling}: no pair-level signal "
                            f"exists, so the basin is undefined. Seed-and-grow cannot start here.")
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(candidates), size=min(n_probe, len(candidates)), replace=False)
    hits, scores = 0, []
    for i in pick:
        a = ari_fn(grow_fn(candidates[int(i)]))
        scores.append(a)
        hits += int(a >= success * ceiling)
    n = len(pick)
    f = hits / n
    # Wilson score interval -- honest at small n_probe, unlike the normal approximation.
    z2 = 1.96 ** 2
    denom = 1 + z2 / n
    centre = (f + z2 / (2 * n)) / denom
    half = (1.96 * np.sqrt(f * (1 - f) / n + z2 / (4 * n * n))) / denom
    need = (lambda q: (int(np.ceil(np.log(1 - q) / np.log(1 - f))) if 0 < f < 1
                       else (1 if f >= 1 else -1)))
    return dict(basin_fraction=f, n_probe=n, hits=hits,
                ci_low=max(0.0, centre - half), ci_high=min(1.0, centre + half),
                draws_for_95pct=need(0.95), draws_for_99pct=need(0.99),
                mean_grown_ari=float(np.mean(scores)), success_bar=success * ceiling, aborted="")
