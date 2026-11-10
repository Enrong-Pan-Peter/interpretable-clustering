"""Phase 2 - continuous persistence fitness (MST edge-gap).

Replaces the flat f = -(C-2)^2 with a smooth 2-cluster separation score. Per the plan
(atomic_handoff_1.md Phase 2):

  * nodes = the DATA POINTS; edges = point-to-point distance in the SELECTED subspace;
  * build the MST, sort edge weights e1 >= e2 >= ...;
  * persistence S = e1 - e2  (the two clusters are the two subtrees left after cutting e1).

Refinements (all from the plan):
  * mutual-reachability distance  max(core_k(a), core_k(b), d(a,b))  -- outlier-robust;
  * minimum cluster size          both sides of the cut must have >= minPts points;
  * normalization                 e1/e2 (default, scale-free) or gap / median edge.

When the largest MST edge would isolate < minPts points, we take the largest edge whose
removal yields two admissible sides (the min-size-aware version of "cut e1"); the gap is
that edge minus the next edge in the sorted order. Invalid (no admissible cut) -> score 0.
Per-eval cost O(n^2 d): fine for small-n/large-d biomedical data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors


@dataclass
class PersistenceResult:
    score: float                    # normalized persistence (higher = cleaner split); 0 if invalid
    raw_gap: float                  # e_cut - e_next (unnormalized)
    labels: Optional[np.ndarray]    # 0/1 two-cluster assignment
    cut_weight: float               # e_cut
    valid: bool                     # a min-size-admissible cut existed


def core_distances(X: np.ndarray, k: int) -> np.ndarray:
    """Distance from each point to its k-th nearest neighbour (excluding itself)."""
    X = np.asarray(X, dtype=float)
    n = len(X)
    if n <= 1:
        return np.zeros(n)
    k_eff = int(min(k, n - 1))
    nn = NearestNeighbors(n_neighbors=k_eff + 1).fit(X)   # +1: first neighbour is self (dist 0)
    d, _ = nn.kneighbors(X)
    return d[:, -1]


def _distance_matrix(X, mutual_reachability, core_k):
    D = squareform(pdist(np.asarray(X, dtype=float)))
    if mutual_reachability:
        core = core_distances(X, core_k)
        D = np.maximum(D, np.maximum.outer(core, core))
        np.fill_diagonal(D, 0.0)
    return D


def _mst_edges(D) -> List[Tuple[int, int, float]]:
    T = minimum_spanning_tree(csr_matrix(D)).tocoo()
    return list(zip(T.row.tolist(), T.col.tolist(), T.data.tolist()))


def _root_and_sizes(n, edges):
    """Root the tree at 0; return, per edge, the 'child' endpoint and its subtree size."""
    adj = [[] for _ in range(n)]
    for eid, (i, j, _w) in enumerate(edges):
        adj[i].append((j, eid))
        adj[j].append((i, eid))
    parent_eid = [-1] * n
    visited = [False] * n
    order = []
    stack = [0]
    visited[0] = True
    while stack:
        u = stack.pop()
        order.append(u)
        for v, eid in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent_eid[v] = eid
                stack.append(v)
    size = [1] * n
    for u in reversed(order):
        # add u's subtree to its parent via the edge that entered u
        eid = parent_eid[u]
        if eid >= 0:
            i, j, _w = edges[eid]
            p = j if i == u else i
            size[p] += size[u]
    edge_child = [None] * len(edges)
    for v in range(n):
        if parent_eid[v] >= 0:
            edge_child[parent_eid[v]] = v
    return edge_child, size


def _labels_after_cut(start, cut_eid, edges, n):
    adj = [[] for _ in range(n)]
    for eid, (i, j, _w) in enumerate(edges):
        if eid == cut_eid:
            continue
        adj[i].append(j)
        adj[j].append(i)
    seen = np.zeros(n, dtype=bool)
    seen[start] = True
    stack = [start]
    comp = [start]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
                comp.append(v)
    labels = np.zeros(n, dtype=int)
    labels[comp] = 1
    return labels


def persistence_split(X_sub, min_cluster_size: int = 5, mutual_reachability: bool = True,
                      core_k: int = 5, normalize: str = "ratio") -> PersistenceResult:
    X_sub = np.asarray(X_sub, dtype=float)
    n = X_sub.shape[0]
    if n < 2 * min_cluster_size or X_sub.ndim != 2 or X_sub.shape[1] < 1:
        return PersistenceResult(0.0, 0.0, None, 0.0, False)

    D = _distance_matrix(X_sub, mutual_reachability, core_k)
    edges = _mst_edges(D)
    if len(edges) < 1:
        return PersistenceResult(0.0, 0.0, None, 0.0, False)

    edge_child, size = _root_and_sizes(n, edges)
    order_by_w = sorted(range(len(edges)), key=lambda e: edges[e][2], reverse=True)
    weights_desc = [edges[e][2] for e in order_by_w]

    cut_pos = None
    cut_eid = None
    for rank, e in enumerate(order_by_w):
        c = edge_child[e]
        if c is None:
            continue
        s = size[c]
        if s >= min_cluster_size and (n - s) >= min_cluster_size:
            cut_pos, cut_eid = rank, e
            break
    if cut_pos is None:
        return PersistenceResult(0.0, 0.0, None, 0.0, False)

    e_cut = weights_desc[cut_pos]
    e_next = weights_desc[cut_pos + 1] if cut_pos + 1 < len(weights_desc) else 0.0
    raw_gap = e_cut - e_next

    if normalize == "ratio":
        score = (e_cut / e_next) if e_next > 0 else (1.0 + e_cut)
    elif normalize == "median":
        med = float(np.median([w for (_i, _j, w) in edges]))
        score = raw_gap / med if med > 0 else raw_gap
    else:
        score = raw_gap

    labels = _labels_after_cut(edge_child[cut_eid], cut_eid, edges, n)
    return PersistenceResult(float(score), float(raw_gap), labels, float(e_cut), True)
