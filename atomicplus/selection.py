"""Clean-room NSGA-II: fast non-dominated sort + crowding distance.

Replaces DEAP's `tools.selNSGA2`. Objectives are given as an (N, d) matrix and are
all **maximised** (callers negate anything to be minimised). Cross-checked once
against DEAP in the test suite to prove faithfulness.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np


def _dominates(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.all(a >= b) and np.any(a > b))


def fast_nondominated_sort(M: np.ndarray) -> List[List[int]]:
    """Partition rows of M into Pareto fronts (front 0 = non-dominated)."""
    M = np.asarray(M, dtype=float)
    n = M.shape[0]
    dominated: List[List[int]] = [[] for _ in range(n)]
    dom_count = np.zeros(n, dtype=int)
    fronts: List[List[int]] = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if _dominates(M[p], M[q]):
                dominated[p].append(q)
            elif _dominates(M[q], M[p]):
                dom_count[p] += 1
        if dom_count[p] == 0:
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        nxt: List[int] = []
        for p in fronts[i]:
            for q in dominated[p]:
                dom_count[q] -= 1
                if dom_count[q] == 0:
                    nxt.append(q)
        i += 1
        fronts.append(nxt)
    fronts.pop()
    return fronts


def crowding_distance(M: np.ndarray, front: List[int]) -> Dict[int, float]:
    M = np.asarray(M, dtype=float)
    dist = {i: 0.0 for i in front}
    l = len(front)
    if l == 0:
        return dist
    Mf = M[front]
    for m in range(M.shape[1]):
        order = np.argsort(Mf[:, m], kind="mergesort")
        sorted_idx = [front[o] for o in order]
        dist[sorted_idx[0]] = np.inf
        dist[sorted_idx[-1]] = np.inf
        span = Mf[order[-1], m] - Mf[order[0], m]
        if span == 0:
            continue
        for r in range(1, l - 1):
            dist[sorted_idx[r]] += (Mf[order[r + 1], m] - Mf[order[r - 1], m]) / span
    return dist


def nsga2_select(M: np.ndarray, mu: int) -> List[int]:
    """Select `mu` row indices by NSGA-II (fronts, then crowding within the last front)."""
    fronts = fast_nondominated_sort(M)
    selected: List[int] = []
    for front in fronts:
        if len(selected) + len(front) <= mu:
            selected.extend(front)
        else:
            cd = crowding_distance(M, front)
            remaining = mu - len(selected)
            ordered = sorted(front, key=lambda i: cd[i], reverse=True)
            selected.extend(ordered[:remaining])
            break
    return selected


def nondominated_indices(M: np.ndarray) -> List[int]:
    """Indices on the first Pareto front."""
    if np.asarray(M).shape[0] == 0:
        return []
    return fast_nondominated_sort(M)[0]
