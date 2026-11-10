"""Topology core: k-NN connectivity graph -> connected components -> fitness,
plus the stable-k (k̃) procedure.

Faithful to `atomic.py` (kneighbors_graph connectivity + scipy connected_components),
with two fixes vs. the original `choose_k` (see architecture.md ledger #2):
  * the no-stable-k fallback returns an int (the original returned a tuple);
  * k is clamped to n-1 so a small subspace can't crash kneighbors_graph.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from scipy.sparse.csgraph import connected_components
from sklearn.neighbors import kneighbors_graph


def component_count(X: np.ndarray, k: int, metric: str = "euclidean") -> Tuple[int, np.ndarray]:
    """Number of connected components of the k-NN connectivity graph, and node labels."""
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    if n < 2:
        return 1, np.zeros(n, dtype=int)
    k_eff = int(min(max(k, 1), n - 1))
    G = kneighbors_graph(X, n_neighbors=k_eff, mode="connectivity",
                         metric=metric, include_self=True)
    n_comp, labels = connected_components(G, directed=False, return_labels=True)
    return int(n_comp), labels


def component_fitness(n_components: int) -> float:
    """ATOMIC fitness: f = -(C - 2)^2, maximised (=0) at exactly two components."""
    return -1.0 * (n_components - 2) ** 2


def stable_k_from_trace(trace: List[Tuple[int, int]], fallback: int = None) -> int:
    """Given [(k, n_components), ...], return the smaller k of the first consecutive
    pair with an unchanged component count (the paper's stable-k). Falls back to the
    last k as an **int** if none is found (fixes the original tuple-return bug, #2)."""
    prev = None
    for (k, c) in trace:
        if prev is not None and c == prev[1]:
            return prev[0]
        prev = (k, c)
    return fallback if fallback is not None else trace[-1][0]


def choose_k(X: np.ndarray, k_min: int = 2, k_max: int = 30, metric: str = "euclidean",
             return_trace: bool = False):
    """Stable-k (k̃): the smallest k for which the component count is unchanged when k -> k+1.

    Matches the original's smallest-stable-k behaviour (a chaining risk we KEEP for a
    faithful baseline; overridable via AtomicConfig.k_tilde). Fixes the tuple-return bug.
    """
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    k_hi = int(min(k_max, n - 1))
    trace: List[Tuple[int, int]] = []
    for k in range(k_min, k_hi + 1):
        c, _ = component_count(X, k, metric=metric)
        trace.append((k, c))
    stable = stable_k_from_trace(trace, fallback=k_hi)
    return (stable, trace) if return_trace else stable
