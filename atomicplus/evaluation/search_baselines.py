"""Non-evolutionary search baselines for the 'does the EA earn its cost?' ablation (audit H4).

Both optimise the SAME continuous persistence objective the EA does, so the comparison is
apples-to-apples: if greedy forward-selection or random search matches the EA, the NSLC +
NSGA-II + archive machinery is unjustified complexity.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np

from ..persistence import persistence_split


def _score(X, feats, mcs, mr, ck):
    r = persistence_split(X[:, list(feats)], min_cluster_size=mcs,
                          mutual_reachability=mr, core_k=ck)
    return (r.score if r.valid else -1.0), r


def greedy_forward_persistence(X, min_cluster_size: int = 5, max_features: int = 8,
                               mutual_reachability: bool = True, core_k: int = 5,
                               rng=None):
    """Seed with the best feature pair, then greedily add the feature that most raises
    persistence; stop when nothing improves or max_features is reached."""
    X = np.asarray(X, dtype=float)
    p = X.shape[1]
    if p <= 14:
        pairs = list(combinations(range(p), 2))
    else:                                   # seed from pairs among the top-variance features
        topv = list(np.argsort(-X.var(0))[:10])
        pairs = list(combinations(topv, 2))
    best = None
    for pr in pairs:
        s, r = _score(X, pr, min_cluster_size, mutual_reachability, core_k)
        if best is None or s > best[0]:
            best = (s, list(pr), r)
    score, selected, res = best
    improved = True
    while improved and len(selected) < max_features:
        improved = False
        cand = None
        for f in range(p):
            if f in selected:
                continue
            s, r = _score(X, selected + [f], min_cluster_size, mutual_reachability, core_k)
            if s > score + 1e-9 and (cand is None or s > cand[0]):
                cand = (s, f, r)
        if cand is not None:
            score, selected, res = cand[0], selected + [cand[1]], cand[2]
            improved = True
    return sorted(int(f) for f in selected), float(score), res.labels


def random_search_persistence(X, n_evals: int = 600, min_cluster_size: int = 5,
                              max_features: int = 8, mutual_reachability: bool = True,
                              core_k: int = 5, rng=None):
    """Sample `n_evals` random feature subsets (size 2..max_features); keep the best
    persistence. Set n_evals to the EA's evaluation budget (pop*gen) for a fair fight."""
    rng = rng if rng is not None else np.random.default_rng()
    X = np.asarray(X, dtype=float)
    p = X.shape[1]
    best = (-np.inf, [0, 1], None)
    for _ in range(n_evals):
        k = int(rng.integers(2, max_features + 1))
        feats = rng.choice(p, size=min(k, p), replace=False)
        s, r = _score(X, feats, min_cluster_size, mutual_reachability, core_k)
        if s > best[0]:
            best = (s, sorted(int(f) for f in feats), r.labels)
    return best[1], float(best[0]), best[2]
