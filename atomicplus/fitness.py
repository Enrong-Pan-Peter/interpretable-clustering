"""Subset evaluation (the quality objectives) and the NSLC out-performance rule.

A subset is scored by (f, size): f = -(C-2)^2 in the selected subspace, size = #features.
Out-performance is the paper's rule (f-greater, or f-equal and fewer features); the
original code's stricter "fewer than half" variant is reachable via rule="legacy".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from . import genome as gm
from . import topology

VERY_NEGATIVE = -1e9  # sentinel score for degenerate (<min_features) genomes


@dataclass
class SubsetEval:
    f: float                      # component fitness  -(C-2)^2  (maximise)
    size: int                     # number of selected features (minimise)
    n_components: int
    labels: Optional[np.ndarray]  # component labels in the selected subspace


def evaluate_subset(X: np.ndarray, g, k: int, metric: str = "euclidean",
                    min_features: int = 2, fitness_mode: str = "components",
                    min_cluster_size: int = 5, mutual_reachability: bool = True,
                    core_k: int = 5, normalize: str = "ratio") -> SubsetEval:
    idx = gm.selected_indices(g)
    size = int(len(idx))
    if size < min_features:
        return SubsetEval(VERY_NEGATIVE, size, -1, None)
    Xs = np.asarray(X, dtype=float)[:, idx]
    if fitness_mode == "persistence":
        from . import persistence as _P
        r = _P.persistence_split(Xs, min_cluster_size=min_cluster_size,
                                 mutual_reachability=mutual_reachability,
                                 core_k=core_k, normalize=normalize)
        return SubsetEval(r.score if r.valid else VERY_NEGATIVE, size,
                          2 if r.valid else 1, r.labels)
    n_comp, labels = topology.component_count(Xs, k, metric=metric)
    return SubsetEval(topology.component_fitness(n_comp), size, n_comp, labels)


def outperforms(a: SubsetEval, b: SubsetEval, rule: str = "paper") -> bool:
    """Does individual with eval `a` out-perform the one with eval `b`? (paper §2.3)"""
    if a.f > b.f:
        return True
    if a.f == b.f:
        if rule == "paper":
            return a.size < b.size
        if rule == "legacy":
            return a.size < (b.size // 2)
        raise ValueError(f"unknown outperform rule: {rule!r}")
    return False
