"""Variation operators: mutation and crossover.

Faithful defaults (bit-flip mutation, bitwise-OR crossover) plus the Phase-5
alternatives (uniform / set-based crossover). The original mutation bug
(`i1[i] = (i1[1]+1)%2`, toggling bit 1) is reproducible via `legacy=True`.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from . import genome as gm


def mutate(g, rng: np.random.Generator, per_bit_prob: float,
           min_features: int = 2, legacy: bool = False,
           add_prob=None, remove_prob=None) -> np.ndarray:
    g = np.array(g, dtype=np.int8, copy=True)
    if legacy:
        # Reproduce the original bug: mutated positions are set from bit index 1,
        # not flipped in place. Kept only to measure what the fix changes.
        bit1 = int(g[1]) if len(g) > 1 else int(g[0])
        draws = rng.random(len(g))
        g[draws < per_bit_prob] = (bit1 + 1) % 2
    elif add_prob is not None or remove_prob is not None:
        # Phase 5: ASYMMETRIC per-bit mutation -- bias toward REMOVING set bits to fight
        # the bloat that OR-crossover and symmetric flips create (add ~ 1/p, remove 3-5x).
        pa = per_bit_prob if add_prob is None else add_prob
        pr = per_bit_prob if remove_prob is None else remove_prob
        ones = g == 1
        rem = ones & (rng.random(len(g)) < pr)
        add = (~ones) & (rng.random(len(g)) < pa)
        g[rem] = 0
        g[add] = 1
    else:
        flips = rng.random(len(g)) < per_bit_prob
        g[flips] = 1 - g[flips]
    gm.ensure_min_features(g, rng, min_features)
    return g


def crossover(g1, g2, rng: np.random.Generator, mode: str = "or",
              size_cap: Optional[int] = None, min_features: int = 2) -> Tuple[np.ndarray, np.ndarray]:
    a = np.array(g1, dtype=np.int8, copy=True)
    b = np.array(g2, dtype=np.int8, copy=True)

    if mode == "or":
        # Faithful: both children become the union of parents (feature sets grow).
        u = (a | b).astype(np.int8)
        return u.copy(), u.copy()

    if mode == "uniform":
        mask = rng.random(len(a)) < 0.5
        c1 = np.where(mask, a, b).astype(np.int8)
        c2 = np.where(mask, b, a).astype(np.int8)
        gm.ensure_min_features(c1, rng, min_features)
        gm.ensure_min_features(c2, rng, min_features)
        return c1, c2

    if mode == "set_based":
        # Keep shared features; split the symmetric difference between the children.
        shared = (a & b).astype(np.int8)
        diff = np.flatnonzero(a != b)
        rng.shuffle(diff)
        c1 = shared.copy()
        c2 = shared.copy()
        half = len(diff) // 2
        c1[diff[:half]] = 1
        c2[diff[half:]] = 1
        if size_cap is not None:
            _enforce_cap(c1, rng, size_cap)
            _enforce_cap(c2, rng, size_cap)
        gm.ensure_min_features(c1, rng, min_features)
        gm.ensure_min_features(c2, rng, min_features)
        return c1, c2

    raise ValueError(f"unknown crossover mode: {mode!r}")


def _enforce_cap(g: np.ndarray, rng: np.random.Generator, cap: int) -> None:
    on = np.flatnonzero(g == 1)
    if len(on) > cap:
        drop = rng.choice(on, size=len(on) - cap, replace=False)
        g[drop] = 0
