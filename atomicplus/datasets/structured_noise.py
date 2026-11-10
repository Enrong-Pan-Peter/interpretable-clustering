"""Harder junk columns, so the benchmark tests what we claim it tests.

THE PROBLEM THIS FIXES
----------------------
In the original benchmark the informative columns hold a real 2-D picture (crescents, rings, a
spiral) while every junk column is spread evenly across its range. That difference is visible ONE
COLUMN AT A TIME: a single-column "how uneven is this?" test finds both informative columns 100%
of the time on jain and spiral, 65-80% on gauss2 and 45-70% on circles. Only moons and flame
resist it. So four of six shapes never tested the premise of the project -- that the informative
features can only be found by looking at them TOGETHER.

Cause: planting a picture makes those columns lumpy as a side-effect. Evenly-spread junk is then
trivially distinguishable. The fix is junk that is also lumpy.

THE DESIGN RULE (this is what keeps it a fair test rather than a rigged one)
---------------------------------------------------------------------------
Junk columns get CONCENTRATED MASS but NO CLEAN GAP.

  * concentrated mass -> defeats crude "which subspace has the most points in clumps?" cues,
    which is exactly the rule that beat our signal on the old benchmark.
  * no clean gap -> a genuine separation signal remains detectable, so the task stays answerable.

We deliberately do NOT plant separable cluster structure in junk columns in the default profile.
If a junk pair contained real, well-separated clusters unrelated to the labels, then NO label-free
method could be expected to prefer the true pair -- the task would be ill-posed, and beating it
would prove nothing. That case is available as profile="decoy" and must be reported as a SCOPE
BOUNDARY, never as part of the main comparison.

Every junk column is drawn independently of the labels. `verify_noise_is_uninformative` checks it.
"""
from __future__ import annotations

import numpy as np

PROFILES = ("uniform", "structured", "decoy")


def _multimodal(n, rng):
    """Lumpy but with OVERLAPPING modes -- looks non-uniform, offers no clean cut."""
    k = rng.integers(2, 4)
    means = rng.uniform(0.25, 0.75, size=k)
    # sd chosen relative to mode spacing so the lumps blend into each other
    sd = rng.uniform(0.12, 0.20)
    which = rng.integers(0, k, size=n)
    return means[which] + rng.normal(0, sd, size=n)


def _skewed(n, rng):
    """Heavily one-sided. Very far from evenly spread, still a single connected mass."""
    a, b = rng.uniform(0.6, 1.2), rng.uniform(2.5, 6.0)
    if rng.random() < 0.5:
        a, b = b, a
    return rng.beta(a, b, size=n)


def _blob_pair(n, rng, separable=False):
    """Two columns holding overlapping 2-D lumps: concentrated mass, no clean gap.

    This is the column type that specifically defeats a mass-concentration cue. With
    separable=True the lumps are pulled apart into genuine clusters -- the ill-posed decoy case.
    """
    k = rng.integers(2, 4)
    centres = rng.uniform(0.2, 0.8, size=(k, 2))
    sd = rng.uniform(0.05, 0.08) if separable else rng.uniform(0.18, 0.26)
    which = rng.integers(0, k, size=n)
    return centres[which] + rng.normal(0, sd, size=(n, 2))


def make_noise_matrix(n: int, m: int, rng: np.random.Generator,
                      profile: str = "structured") -> np.ndarray:
    """(n, m) matrix of junk columns, independent of any labels.

    profile="uniform"    the original benchmark's evenly-spread junk (kept for comparison).
    profile="structured" the harder junk: a mix of even, lumpy, skewed, and paired-lump columns.
    profile="decoy"      as structured, but the paired columns hold genuinely separable clusters.
                         ILL-POSED ON PURPOSE -- scope boundary only.
    """
    if profile not in PROFILES:
        raise ValueError(f"profile must be one of {PROFILES}, got {profile!r}")
    if profile == "uniform":
        return rng.random((n, m))

    X = np.empty((n, m), dtype=float)
    # Fixed allocation, so the composition is a documented property of the benchmark rather
    # than something that drifts between runs: ~20% paired-lump, rest split evenly three ways.
    n_pair_cols = 2 * (m // 10)
    rest = m - n_pair_cols
    n_even = rest // 3
    n_multi = rest // 3
    n_skew = rest - n_even - n_multi

    c = 0
    for _ in range(n_pair_cols // 2):
        X[:, c:c + 2] = _blob_pair(n, rng, separable=(profile == "decoy"))
        c += 2
    for _ in range(n_even):
        X[:, c] = rng.random(n); c += 1
    for _ in range(n_multi):
        X[:, c] = _multimodal(n, rng); c += 1
    for _ in range(n_skew):
        X[:, c] = _skewed(n, rng); c += 1

    # Shuffle column order so the informative dims aren't identifiable by position, and so no
    # method can benefit from junk types appearing in a fixed arrangement.
    return X[:, rng.permutation(m)]


def verify_noise_is_uninformative(noise: np.ndarray, y: np.ndarray) -> dict:
    """Sanity check: no junk column should predict the labels.

    Returns the best single-column AUC-like separation achieved by any junk column. Anything
    near 0.5 means the junk really is junk. If this comes back high, the generator is broken and
    every downstream number is meaningless -- fail loudly rather than quietly.
    """
    from sklearn.metrics import roc_auc_score
    y = np.asarray(y)
    classes = np.unique(y)
    if len(classes) < 2:
        return {"max_abs_auc_minus_half": float("nan"), "worst_col": -1}
    binary = (y == classes[0]).astype(int)
    worst, col = 0.0, -1
    for j in range(noise.shape[1]):
        try:
            a = abs(roc_auc_score(binary, noise[:, j]) - 0.5)
        except Exception:  # noqa: BLE001
            continue
        if a > worst:
            worst, col = a, j
    return {"max_abs_auc_minus_half": float(worst), "worst_col": int(col)}
