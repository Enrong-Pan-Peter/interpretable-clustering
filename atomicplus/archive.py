"""NSLC archive ("the bank"): novelty (Hamming sparseness) + local competition.

Replaces the global `bank` dict and the per-eval `NearestNeighbors.fit(all_in_bank)`
in `atomic.py`. The costly rebuild-every-eval behaviour (audit M2) is preserved by
default (`rebuild_every=1`) but can be relaxed for speed.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors

from . import fitness as fit
from . import genome as gm


class NSLCArchive:
    def __init__(self, n_neighbors: int = 8, add_prob: float = 0.05,
                 rebuild_every: int = 1, outperform_rule: str = "paper"):
        self.n_neighbors = n_neighbors
        self.add_prob = add_prob
        self.rebuild_every = max(1, int(rebuild_every))
        self.rule = outperform_rule
        self.genomes: List[np.ndarray] = []
        self.evals: List[fit.SubsetEval] = []
        self._keys = set()
        self._nn = None
        self._built_size = 0

    def __len__(self) -> int:
        return len(self.genomes)

    def add(self, g, ev: fit.SubsetEval) -> bool:
        key = gm.genome_key(g)
        if key in self._keys:
            return False
        self._keys.add(key)
        self.genomes.append(np.asarray(g, dtype=np.int8))
        self.evals.append(ev)
        return True

    def maybe_add(self, g, ev: fit.SubsetEval, rng: np.random.Generator) -> bool:
        if rng.random() <= self.add_prob:
            return self.add(g, ev)
        return False

    def _ensure_index(self) -> None:
        if len(self.genomes) == 0:
            self._nn = None
            return
        grew = len(self.genomes) - self._built_size
        if self._nn is None or grew >= self.rebuild_every:
            M = np.vstack(self.genomes)
            k = min(self.n_neighbors, len(self.genomes))
            self._nn = NearestNeighbors(n_neighbors=k, metric="hamming").fit(M)
            self._built_size = len(self.genomes)

    def novelty_and_competition(self, g, ev: fit.SubsetEval) -> Tuple[float, int]:
        """Novelty = mean Hamming distance to the k nearest archive members;
        local competition = how many of those the individual out-performs."""
        self._ensure_index()
        if self._nn is None:
            return 0.0, 0
        gq = np.asarray(g, dtype=np.int8).reshape(1, -1)
        k = min(self.n_neighbors, len(self.genomes))
        dist, idx = self._nn.kneighbors(gq, n_neighbors=k)
        novelty = float(np.mean(dist))
        comp = 0
        for j in idx[0]:
            if fit.outperforms(ev, self.evals[int(j)], self.rule):
                comp += 1
        return novelty, comp
