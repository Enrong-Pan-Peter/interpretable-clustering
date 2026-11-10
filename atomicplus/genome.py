"""Genome representation: a Boolean bit-string of length p (1 = use that variable).

Framework-free replacement for DEAP's `creator.Individual = list`. No global state;
all randomness comes from an injected `numpy.random.Generator`.
"""
from __future__ import annotations

import numpy as np


def random_genome(p: int, rng: np.random.Generator, min_features: int = 2) -> np.ndarray:
    g = (rng.random(p) < 0.5).astype(np.int8)
    ensure_min_features(g, rng, min_features)
    return g


def ensure_min_features(g: np.ndarray, rng: np.random.Generator, min_features: int = 2) -> np.ndarray:
    """Set additional random bits until at least `min_features` are on (in place)."""
    deficit = min_features - int(g.sum())
    if deficit > 0:
        zeros = np.flatnonzero(g == 0)
        if len(zeros):
            pick = rng.choice(zeros, size=min(deficit, len(zeros)), replace=False)
            g[pick] = 1
    return g


def random_population(n: int, p: int, rng: np.random.Generator, min_features: int = 2):
    return [random_genome(p, rng, min_features) for _ in range(n)]


def n_features(g) -> int:
    return int(np.sum(g))


def selected_indices(g) -> np.ndarray:
    return np.flatnonzero(np.asarray(g) == 1)


def genome_key(g) -> bytes:
    """Hashable key for archive de-duplication (p is fixed within a run)."""
    return np.asarray(g, dtype=np.uint8).tobytes()
