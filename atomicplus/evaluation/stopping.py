"""Stopping rules for panel growth -- deciding when a panel is the right SIZE.

WHY THIS IS A SEPARATE MODULE
-----------------------------
Growing a panel needs two different decisions and they have been tangled together:

    WHICH feature to add next   -> a comparison between candidates of the same size
    WHETHER to add it at all    -> a comparison ACROSS sizes

Only the second is a stopping rule, and it is the one that failed in every experiment. exp-024
(cytometry tree): 35 of 39 nodes grew until they hit the size cap rather than stopping. exp-026
(spherical shells, where the answer is known to be exactly three columns): the graph-cut term scored
a four-column panel above the correct three-column one while clustering quality halved.

WHAT WAS RULED OUT FIRST
------------------------
The obvious suspect is that the calibrated score simply grows with panel size, which would make
every "improvement" an artefact. Measured on pure junk columns at sizes 1 through 6:

    density    0.00  1.60  -1.22  -0.27  -0.17   0.87
    graph-cut  0.00  0.04   0.44  -2.33  -0.44  -0.17

No upward trend. The calibration does make sizes comparable, so over-growing is NOT a size bias.

THE RULE THAT WORKED, AND THE EVIDENCE FOR IT
---------------------------------------------
COMBINE THE TERMS. The project always summed its two scoring terms, but the original sum
standardises each against the OTHER CANDIDATES OF THE SAME SIZE -- a relative ranking that cannot
compare a 2-column panel to a 3-column one. Summing the SHUFFLE-CALIBRATED versions can. On the
shells, where the answer is three columns:

    size   density   graph-cut   sum
      2       1.08       -0.29    0.78
      3       9.71        8.87   18.58   <- correct
      4       4.75       10.64   15.38

Graph-cut alone peaks at the wrong size; the sum peaks at the right one because density's collapse
outweighs graph-cut's rise. exp-027 then tested this properly, one configuration fixed in advance,
on datasets whose right answers DIFFER (3 for the shells, 2 for circles / two-cluster):

    graph-cut only   over-grew on the shells        2 of 4 exactly right
    density only     over-grew on two-cluster       2 of 4 exactly right
    BOTH SUMMED      correct on all three synthetics 3 of 4 exactly right

Each term fails where the other holds. That is why the sum generalises rather than being tuned.

THE SECOND RULE, KEPT BUT NOT DEFAULT
-------------------------------------
`min_gain_se` requires the gain to exceed that many standard errors of its own Monte-Carlo noise.
The motivation was real -- graph-cut's fatal step in exp-026 was a gain of 0.25 against a
shuffle-to-shuffle spread of 1.59 -- but exp-027 found it changed no outcome at three to five times
the cost, so it defaults to 0. Keep it for deep tree nodes where few cells make the score noisier.

The gain's error is estimated PAIRED: the same shuffle seeds score the current panel and the
candidate, and the spread is taken over the differences. The permutations are synchronised, so the
two estimates share most of their noise, and treating them separately would double-count it.

WHAT THIS MODULE DOES NOT DO, AND WHY IT MATTERS
------------------------------------------------
None of these rules prefers a SMALLER panel at equal quality. On Levine, growth from the published
(CD4, CD8) gate ran on to four markers -- and the four-marker panel clusters the cells as well or
slightly better (spectral ARI 0.947 against 0.934; k-means 0.987 either way). The score is not
wrong; the extra markers carry real information. But two markers are a scatter plot an immunologist
can read and four are not, so parsimony is a preference from OUTSIDE the data and has to be added
deliberately -- as a second objective, or by fixing the panel size for that application. Do not
expect a stopping rule to supply it.
"""
from __future__ import annotations

import itertools
from typing import Dict, Sequence, Tuple

import numpy as np

from atomicplus.evaluation.calibration import Scorer, calibrate


def z_reps(score_fns: Sequence[Scorer], X: np.ndarray, subset: Sequence[int],
           B: int = 20, shared_seed: int = 0, n_reps: int = 1) -> np.ndarray:
    """Combined calibrated z for `subset`, once per repeat, so the caller can see the spread.

    Each entry AVERAGES that panel's calibrated z over the terms under one shuffle seed. All-NaN if
    any term is unscorable or its null collapsed -- a panel whose null has no spread has a z that is
    a ratio to an arbitrary constant, and letting that into a comparison manufactures winners.

    MEAN RATHER THAN SUM, AND THIS IS NOT COSMETIC. The tree's abstention threshold (BAR = 2.0, from
    exp-021) was measured on a SINGLE term's z. A sum of two terms sits on roughly twice that scale,
    so pairing it with the same bar compares a number against a threshold never meant for it. The
    first combined run at max_size=2 abstained at the root on z = 1.99 against a bar of 2.0 -- a
    decision made by a scale mismatch rather than by the data, and the whole tree was one node.

    Averaging returns the combined score to the single-term scale, so one bar and every z printed
    across this project stay mutually comparable. It changes no growth decision: dividing every z by
    a constant scales gains and their standard errors identically, leaving both `gain > 0` and
    `gain > min_gain_se * se` untouched. Only the abstention comparison moves, which is the one that
    was wrong.
    """
    out = np.empty(n_reps, dtype=float)
    for r in range(n_reps):
        total = 0.0
        for fn in score_fns:
            c = calibrate(fn, X, subset, B=B, shared_seed=shared_seed + 1000 * r)
            if not np.isfinite(c["z"]) or c.get("degenerate", 0.0):
                return np.full(n_reps, np.nan)
            total += c["z"]
        out[r] = total / len(score_fns)      # MEAN, not sum -- see the note above
    return out


def paired_gain(cur: np.ndarray, cand: np.ndarray) -> Tuple[float, float]:
    """(mean gain, standard error of the gain) on the PAIRED differences. See module docstring."""
    d = cand - cur
    if len(d) < 2 or not np.all(np.isfinite(d)):
        return (float(np.mean(d)) if np.all(np.isfinite(d)) else float("nan"), 0.0)
    return float(np.mean(d)), float(np.std(d, ddof=1) / np.sqrt(len(d)))


def grow_with_stop(score_fns: Sequence[Scorer], X: np.ndarray, seed_subset: Sequence[int],
                   max_size: int = 6, B: int = 20, shared_seed: int = 0,
                   pool: Sequence[int] | None = None, n_reps: int = 1,
                   min_gain_se: float = 0.0, n_jobs: int = 1,
                   ) -> Tuple[Tuple[int, ...], list[Dict[str, object]]]:
    """Add the best remaining feature while the combined calibrated z rises convincingly.

    Returns (chosen panel, trace). The trace records every step including the rejected one, with the
    gain and its standard error, so a stop can be audited rather than taken on trust.
    """
    cur = tuple(sorted(seed_subset))
    cur_r = z_reps(score_fns, X, cur, B=B, shared_seed=shared_seed, n_reps=n_reps)
    trace = [dict(subset=cur, size=len(cur), accepted=True, z=float(np.mean(cur_r)),
                  gain=float("nan"), gain_se=float("nan"),
                  degenerate=float(not np.all(np.isfinite(cur_r))))]
    candidates = range(X.shape[1]) if pool is None else pool
    remaining = [j for j in candidates if j not in cur]

    while len(cur) < max_size and remaining:
        subsets = [tuple(sorted(cur + (j,))) for j in remaining]
        if n_jobs != 1 and len(subsets) > 1:
            from joblib import Parallel, delayed
            reps = Parallel(n_jobs=n_jobs)(
                delayed(z_reps)(score_fns, X, s, B, shared_seed, n_reps) for s in subsets)
        else:
            reps = [z_reps(score_fns, X, s, B=B, shared_seed=shared_seed, n_reps=n_reps)
                    for s in subsets]

        scored = []
        for s, j, r in zip(subsets, remaining, reps):
            if not np.all(np.isfinite(r)):
                continue
            g, se = paired_gain(cur_r, r)
            scored.append((g, se, s, j, r))
        if not scored:
            break

        g, se, s, j, r = max(scored, key=lambda t: t[0])
        accepted = bool(g > min_gain_se * se) and g > 0
        trace.append(dict(subset=s, size=len(s), accepted=accepted, z=float(np.mean(r)),
                          gain=g, gain_se=se, degenerate=0.0))
        if not accepted:
            break
        cur, cur_r = s, r
        remaining.remove(j)
    return cur, trace


def chosen_from_trace(trace: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """The record of the panel actually chosen -- never `trace[-1]`, which may be the rejected one."""
    acc = [t for t in trace if t.get("accepted")]
    return dict(acc[-1]) if acc else {}


# ------------------------------------------------------------------------------------------------
# Drop-in replacement for calibration.grow_from_pairs
# ------------------------------------------------------------------------------------------------

def grow_from_pairs_stop(score_fns: Sequence[Scorer], X: np.ndarray, seed_score_fn: Scorer = None,
                         n_seeds: int = 10, max_size: int = 6, B: int = 30, shared_seed: int = 0,
                         pool: Sequence[int] | None = None,
                         pair_pool: Sequence[Tuple[int, int]] | None = None,
                         n_reps: int = 1, min_gain_se: float = 0.0, n_jobs: int = 1,
                         ) -> list[Dict[str, object]]:
    """Pair-seeded search whose STOPPING decision uses the combined calibrated score.

    Returns the same record shape as `calibration.grow_from_pairs` -- seed_pair, seed_raw_rank,
    seed_raw, panel, size, z, degenerate, z_last, trace -- so callers swap one for the other without
    touching anything downstream.

    TWO SCORES DOING TWO JOBS, AND THEY ARE NOT THE SAME JOB
    --------------------------------------------------------
    Seeds are ranked by the RAW score of `seed_score_fn` (graph-cut by default), because exp-022
    measured that raw graph-cut puts good pairs at median rank 38 of 496 on this data while the
    calibrated score is worse at ranking and sometimes inverts. Growth then stops on the COMBINED
    CALIBRATED score, because that is the only statistic comparable across panel sizes and the only
    one exp-027 found correct on datasets with different right answers.

    Raw scores from the two terms are NOT summed for seeding -- they live on different scales, and
    adding them would silently weight whichever has the larger spread.
    """
    seed_score_fn = seed_score_fn or score_fns[0]
    p = X.shape[1]
    cand = list(pair_pool) if pair_pool is not None else list(itertools.combinations(range(p), 2))
    if n_jobs != 1 and len(cand) > 1:
        from joblib import Parallel, delayed
        raw = np.array(Parallel(n_jobs=n_jobs)(
            delayed(_raw)(seed_score_fn, X, s) for s in cand), dtype=float)
    else:
        raw = np.array([_raw(seed_score_fn, X, s) for s in cand], dtype=float)
    order = np.argsort(-np.nan_to_num(raw, nan=-np.inf))
    seeds = [cand[i] for i in order[:n_seeds]]

    out = []
    for rank0, s0 in enumerate(seeds, 1):
        chosen, trace = grow_with_stop(score_fns, X, s0, max_size=max_size, B=B,
                                       shared_seed=shared_seed, pool=pool, n_reps=n_reps,
                                       min_gain_se=min_gain_se, n_jobs=n_jobs)
        e = chosen_from_trace(trace)
        out.append(dict(seed_pair=tuple(s0), seed_raw_rank=rank0,
                        seed_raw=float(raw[order[rank0 - 1]]),
                        panel=tuple(chosen), size=len(chosen),
                        z=float(e.get("z", float("nan"))),
                        degenerate=float(e.get("degenerate", 0.0)),
                        z_last=float(trace[-1]["z"]) if trace else float("nan"),
                        trace=trace))
    return out


def _raw(score_fn: Scorer, X: np.ndarray, s: Sequence[int]) -> float:
    """Top-level so joblib can pickle it when the pair sweep runs in parallel."""
    v = score_fn(X[:, list(s)])[0]
    return float(v)
