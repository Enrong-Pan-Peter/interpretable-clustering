"""Distance multivariance as a subspace score.

WHY
---
exp-018 found that our score only fires when the panel is EXACTLY right: the exact true pair
gives Cohen's d = 3.13, and adding ONE irrelevant column drops it to 0.48. We need a score whose
behaviour under an added irrelevant column is understood rather than accidental.

Distance multivariance (Boettcher, Keller-Ressel & Schilling, "Distance multivariance: new
dependence measures for random vectors", Annals of Statistics 47(5):2757-2789, 2019) has exactly
such a property, and it is PROVEN rather than empirical:

    M^2(X_1, ..., X_n) = 0   whenever ANY single X_j is independent of the others.

READ THAT CAREFULLY BEFORE GETTING EXCITED. It cuts both ways:

  * As a RANKER it is close to ideal -- it rejects any panel containing an irrelevant feature,
    which is a stronger and more principled version of the peakedness our current score has by
    accident.
  * As a SEARCH GUIDE it is the WORST POSSIBLE case. {true pair} scores high; {true pair + junk}
    scores ZERO; {one true + junk} scores ZERO. Both sit at the floor, so there is no gradient at
    all -- a perfect cliff. It would make the exp-018 problem worse, not better.

So this module implements BOTH variants, because the contrast between them IS the experiment:

  * `multivariance`        non-total M^2 -- the pure higher-order term. Zeroes on any independent
                           feature. Predicted: superb detector, zero gradient.
  * `total_multivariance`  M-bar^2 -- sums over ALL sub-multiplets of size >= 2, so a panel of
                           {true pair + junk} RETAINS its (true, true) pairwise term. Predicted:
                           weaker detector, but it should have a gradient. This is the one that
                           could actually help a search.

DEFINITIONS (sample estimators)
-------------------------------
For each feature i, B_i is the N x N matrix of absolute differences, and A_i = -C B_i C is its
double-centred version with C = I - (1/N) 11^T. Then

    M^2      = (1/N^2) sum_{j,k}  prod_i (A_i)_{jk}
    M-bar^2  = (1/N^2) sum_{j,k} [ prod_i (1 + (A_i)_{jk}) - 1 - sum_i (A_i)_{jk} ]

The second identity holds because prod_i (1 + a_i) expands to the sum over ALL subsets of
prod_{i in S} a_i; subtracting 1 (empty set) and sum_i a_i (singletons) leaves exactly the sum
over subsets of size >= 2. That avoids enumerating 2^n subsets.

NORMALISATION -- ours, not the paper's. Say so if we publish it.
Boettcher (2020, Open Statistics) defines a "multicorrelation"; we did not have the exact form
to hand, so we normalise each centred matrix by its own L^n norm:

    Ahat_i = A_i / ( (1/N^2) sum_{jk} |(A_i)_{jk}|^n )^(1/n)

By Hoelder's inequality the resulting M^2 then lies in [-1, 1], and for n = 2 it reduces exactly
to the squared distance correlation of Szekely, Rizzo & Bakirov (Ann. Statist. 35(6), 2007).
That is a defensible normalisation with a stated bound, but it is OURS -- do not attribute it.

IMPORTANT CAVEAT, and it is not small: multivariance measures DEPENDENCE, not CLUSTERABILITY.
Two features lying on a noisy sine curve are strongly dependent and contain no clusters at all,
and multivariance will score them highly. It cannot replace a validity term; at best it gates one.

COST: one N x N matrix per feature (cache these -- `centred_distance_matrices`), then an
elementwise product per candidate subset. O(|S| N^2) per subset once the cache is built.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


def centred_distance_matrices(X: np.ndarray) -> np.ndarray:
    """(p, N, N) stack of double-centred per-feature distance matrices A_i = -C B_i C.

    Build this ONCE per dataset and index into it for every candidate subset.
    """
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    out = np.empty((p, n, n), dtype=float)
    for i in range(p):
        col = X[:, i]
        B = np.abs(col[:, None] - col[None, :])
        rm = B.mean(axis=1, keepdims=True)
        cm = B.mean(axis=0, keepdims=True)
        out[i] = -(B - rm - cm + B.mean())
    return out


def _normalise(A: np.ndarray, order: int) -> np.ndarray:
    """Scale a centred matrix by its L^order norm so the Hoelder bound gives |M^2| <= 1."""
    nrm = (np.abs(A) ** order).mean() ** (1.0 / order)
    return A / nrm if nrm > 1e-12 else A


def multivariance(A_stack: np.ndarray, subset: Sequence[int],
                  normalise: bool = True) -> float:
    """Non-total distance multivariance M^2 of the features in `subset`.

    ZERO (up to sampling error) if any one feature is independent of the rest. Excellent
    detector, no gradient -- see the module docstring before using this to drive a search.
    """
    idx = list(subset)
    if len(idx) < 2:
        return 0.0
    n = len(idx)
    prod = np.ones_like(A_stack[idx[0]])
    for i in idx:
        Ai = _normalise(A_stack[i], n) if normalise else A_stack[i]
        prod = prod * Ai
    return float(prod.mean())


def total_multivariance(A_stack: np.ndarray, subset: Sequence[int],
                        normalise: bool = True) -> float:
    """Total distance multivariance M-bar^2: sums ALL sub-multiplets of size >= 2.

    Because it retains the lower-order terms, a panel of {true pair + junk} keeps its
    (true, true) pairwise contribution. That is exactly the graded behaviour a search needs,
    and the reason this variant is worth testing alongside the non-total one.
    """
    idx = list(subset)
    if len(idx) < 2:
        return 0.0
    n = len(idx)
    mats = [_normalise(A_stack[i], n) if normalise else A_stack[i] for i in idx]
    prod = np.ones_like(mats[0])
    ssum = np.zeros_like(mats[0])
    for A in mats:
        prod = prod * (1.0 + A)
        ssum = ssum + A
    return float((prod - 1.0 - ssum).mean())
