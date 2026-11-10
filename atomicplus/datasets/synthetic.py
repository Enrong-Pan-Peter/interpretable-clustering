"""Synthetic generators with KNOWN ground truth (labels + defining features).

Two roles:
  * validation — we know the right answer, so a re-implementation bug cannot hide.
  * fairness demo — we know which dims separate the clusters, so we can show the
    silhouette/Davies-Bouldin space effect directly, without running the EA.

NOTE (audit M3): `two_cluster_subspace` / `subspace_gaussian` build axis-aligned
subspace Gaussians — exactly the structure ATOMIC is designed to find. That makes
them ideal for *fairness* (we know the truth) but circular for proving the method
is *good*. `nonconvex_projection` provides non-convex (jain/spiral/flame) structure
that centroid methods struggle with.
"""
from __future__ import annotations

import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def _cols(p: int) -> List[str]:
    return [f"f{i + 1}" for i in range(p)]


def two_cluster_subspace(n: int = 200, p: int = 10, informative=(0, 1),
                         frac: float = 0.4, sep: float = 0.5, std: float = 0.05,
                         rng: np.random.Generator = None, shuffle: bool = True
                         ) -> Tuple[pd.DataFrame, np.ndarray, List[int]]:
    """Two tight Gaussian clusters separated ONLY in `informative` dims.

    In the informative subspace the data is two dense balls (2 components); in any
    non-informative dim both clusters share center 0.5 (overlap, 1 component). The
    minimal separating subset is exactly `informative`.
    """
    rng = rng if rng is not None else np.random.default_rng()
    informative = list(informative)
    n1 = int(round(frac * n))
    n0 = n - n1
    labels = np.zeros(n, dtype=int)
    labels[:n1] = 1
    X = rng.normal(0.5, std, size=(n, p))
    for d in informative:
        X[:n1, d] = rng.normal(0.5 + sep / 2, std, size=n1)   # cluster 1
        X[n1:, d] = rng.normal(0.5 - sep / 2, std, size=n0)   # cluster 0
    if shuffle:
        perm = rng.permutation(n)
        X, labels = X[perm], labels[perm]
    return pd.DataFrame(X, columns=_cols(p)), labels, informative


def subspace_gaussian(n: int = 1000, p: int = 100, k: int = 3,
                      frac=(0.05, 0.20), sub_dims=(2, 4), sep: float = 6.0,
                      std: float = 0.5, rng: np.random.Generator = None
                      ) -> Tuple[pd.DataFrame, np.ndarray, Dict[int, List[int]]]:
    """One large Gaussian + (k-1) axis-aligned subspace clusters, each with its own
    defining dims. Clean re-implementation of `convex_synth_data.generate2`.
    Returns (df, labels, {cluster: [defining dims]})."""
    rng = rng if rng is not None else np.random.default_rng()
    X = rng.normal(0.0, 1.0, size=(n, p))
    labels = np.zeros(n, dtype=int)
    true_feats: Dict[int, List[int]] = {}
    for c in range(1, k):
        nd = int(rng.integers(sub_dims[0], sub_dims[1] + 1))
        dims = rng.choice(p, size=nd, replace=False)
        pool = np.flatnonzero(labels == 0)
        npts = int(rng.integers(int(n * frac[0]), max(int(n * frac[1]), int(n * frac[0]) + 1)))
        npts = min(npts, len(pool))
        pts = rng.choice(pool, size=npts, replace=False)
        for d in dims:
            X[pts, d] = rng.normal(sep * c, std, size=npts)
        labels[pts] = c
        true_feats[c] = sorted(int(d) for d in dims)
    return pd.DataFrame(X, columns=_cols(p)), labels, true_feats


def nonconvex_projection(data_dir: str, rng: np.random.Generator = None
                         ) -> Tuple[pd.DataFrame, np.ndarray, Dict[int, List[int]]]:
    """Project the 2-D jain / spiral / flame sets into 6-D, each occupying its own
    pair of dims with uniform noise elsewhere. Re-implements `nonconvex_data.convex_gen`
    but returns source labels and per-cluster defining dims. Each 2-D set is min-max
    normalised before embedding so the noise dims can't separate clusters by range.
    """
    rng = rng if rng is not None else np.random.default_rng()

    def load2d(name: str) -> np.ndarray:
        arr = np.loadtxt(os.path.join(data_dir, name), skiprows=1)
        xy = arr[:, :2].astype(float)
        xy = (xy - xy.min(0)) / (np.ptp(xy, axis=0) + 1e-12)  # -> [0,1] per axis
        return xy

    sets = {0: load2d("jain.txt"), 1: load2d("spiral.txt"), 2: load2d("flame.txt")}
    slot = {0: (0, 1), 1: (2, 3), 2: (4, 5)}
    blocks, labels = [], []
    for s, xy in sets.items():
        M = rng.random((xy.shape[0], 6))          # uniform noise in all 6 dims
        a, b = slot[s]
        M[:, a], M[:, b] = xy[:, 0], xy[:, 1]      # inject the real structure
        blocks.append(M)
        labels.extend([s] * xy.shape[0])
    X = np.vstack(blocks)
    true_feats = {s: list(slot[s]) for s in slot}
    return pd.DataFrame(X, columns=_cols(6)), np.asarray(labels), true_feats


def hierarchical_subspace(n: int = 300, p: int = 15, level1=(0, 1), level2=(2, 3),
                          std: float = 0.05, sep: float = 1.0,
                          rng: np.random.Generator = None, shuffle: bool = True):
    """Three clusters in a KNOWN hierarchy (for validating the recursive tree).

    Root splits {0} | {1,2} on the `level1` dims; the {1,2} branch then splits {1} | {2}
    on the `level2` dims. All other dims are noise. Returns (df, labels in {0,1,2},
    {"level1": dims, "level2": dims}).
    """
    rng = rng if rng is not None else np.random.default_rng()
    per = n // 3
    labels = np.array([0] * per + [1] * per + [2] * (n - 2 * per))
    X = rng.normal(0.5, std, size=(n, p))
    for d in level1:                        # cluster 0 high, clusters 1&2 low
        X[labels == 0, d] = rng.normal(0.5 + sep, std, size=int((labels == 0).sum()))
        X[labels != 0, d] = rng.normal(0.5 - sep, std, size=int((labels != 0).sum()))
    for d in level2:                        # within {1,2}: cluster 1 high, cluster 2 low; 0 stays mid
        X[labels == 1, d] = rng.normal(0.5 + sep, std, size=int((labels == 1).sum()))
        X[labels == 2, d] = rng.normal(0.5 - sep, std, size=int((labels == 2).sum()))
    if shuffle:
        perm = rng.permutation(n)
        X, labels = X[perm], labels[perm]
    return pd.DataFrame(X, columns=_cols(p)), labels, {"level1": list(level1), "level2": list(level2)}


def deceptive_hierarchy(n: int = 180, p: int = 12, sep: float = 3.0, trap: float = 8.0,
                        std: float = 0.08, rng: np.random.Generator = None, shuffle: bool = True):
    """Three clusters A,B,C recoverable as {A}|{B,C} on dim 0 then B|C on dim 1. A TRAP dim 2
    puts half of EVERY cluster at `trap` and half at 0 -> the single highest-persistence split,
    which FRAGMENTS all three clusters. A greedy tree that takes the trap mis-groups; the correct
    tree ignores dim 2. Used for the beam / gate ablation (error-compounding)."""
    rng = rng if rng is not None else np.random.default_rng()
    m = n // 3
    labels = np.array([0] * m + [1] * m + [2] * (n - 2 * m))
    X = rng.normal(0.5, std, size=(n, p))
    X[labels == 0, 0] = rng.normal(0.0, std, m)
    X[labels != 0, 0] = rng.normal(sep, std, int((labels != 0).sum()))
    X[labels == 1, 1] = rng.normal(0.0, std, int((labels == 1).sum()))
    X[labels == 2, 1] = rng.normal(sep, std, int((labels == 2).sum()))
    X[labels == 0, 1] = rng.normal(sep / 2, std, m)
    X[:, 2] = rng.normal(0.0, std, n)                       # TRAP dim
    half = rng.random(n) < 0.5
    X[half, 2] = rng.normal(trap, std, int(half.sum()))     # half of every cluster shoved out
    if shuffle:
        perm = rng.permutation(n)
        X, labels = X[perm], labels[perm]
    return pd.DataFrame(X, columns=_cols(p)), labels, {"correct_dims": [0, 1], "trap_dim": 2}


def _embed_2d(xy, y, p, informative, rng):
    xy = (xy - xy.min(0)) / (np.ptp(xy, axis=0) + 1e-12)   # -> [0,1] per axis
    X = rng.random((xy.shape[0], p))                        # uniform noise in the other dims
    X[:, informative[0]] = xy[:, 0]
    X[:, informative[1]] = xy[:, 1]
    return pd.DataFrame(X, columns=_cols(p)), np.asarray(y), list(informative)


def moons_subspace(n: int = 300, p: int = 12, informative=(0, 1), noise: float = 0.08,
                   rng: np.random.Generator = None):
    """Two interleaving half-moons (a canonical NON-CONVEX set k-means fails on) placed in
    `informative` dims, uniform noise elsewhere. Returns (df, labels, informative dims)."""
    from sklearn.datasets import make_moons
    rng = rng if rng is not None else np.random.default_rng()
    xy, y = make_moons(n_samples=n, noise=noise, random_state=int(rng.integers(0, 2**31 - 1)))
    return _embed_2d(xy, y, p, informative, rng)


def circles_subspace(n: int = 300, p: int = 12, informative=(0, 1), noise: float = 0.06,
                     factor: float = 0.5, rng: np.random.Generator = None):
    """Two concentric circles (non-convex; k-means fails) in `informative` dims, noise elsewhere."""
    from sklearn.datasets import make_circles
    rng = rng if rng is not None else np.random.default_rng()
    xy, y = make_circles(n_samples=n, noise=noise, factor=factor,
                         random_state=int(rng.integers(0, 2**31 - 1)))
    return _embed_2d(xy, y, p, informative, rng)


def redundant_informative(n: int = 200, p: int = 12, informative=(3, 4, 5, 6), frac: float = 0.4,
                          sep: float = 0.6, std: float = 0.05, rng: np.random.Generator = None,
                          shuffle: bool = True):
    """Two clusters separated REDUNDANTLY in several dims (each `informative` dim carries the same
    split). So many different small feature panels induce the SAME clustering -> a controlled test
    of the 'alternative panels' diversity the EA should find and greedy cannot."""
    rng = rng if rng is not None else np.random.default_rng()
    informative = list(informative)
    n1 = int(round(frac * n)); n0 = n - n1
    labels = np.zeros(n, dtype=int); labels[:n1] = 1
    X = rng.normal(0.5, std, size=(n, p))
    for d in informative:
        X[:n1, d] = rng.normal(0.5 + sep / 2, std, size=n1)
        X[n1:, d] = rng.normal(0.5 - sep / 2, std, size=n0)
    if shuffle:
        perm = rng.permutation(n); X, labels = X[perm], labels[perm]
    return pd.DataFrame(X, columns=_cols(p)), labels, informative


def shells_subspace(n: int = 1500, p: int = 12, n_shells: int = 3, informative=(0, 1, 2),
                    radii=None, thickness: float = 0.10,
                    noise: str = "matched", rng: np.random.Generator = None):
    """Concentric spherical shells in THREE dims -- a structure no PAIR of features resolves.

    WHY THIS GENERATOR EXISTS
    -------------------------
    Every testbed in this project has a two-feature answer. The synthetic shapes plant pairs, and
    Levine's reference gates are two-marker. So the question "can the method choose a panel bigger
    than two when that is the right answer?" has never actually been asked -- not asked and failed,
    never asked. This is the missing testbed.

    Three concentric spherical shells separate perfectly by radius, and radius needs all three
    coordinates. Drop to any two of them and you are looking at the shells' shadow.

    WHAT A TWO-FEATURE VIEW ACTUALLY SHOWS, AND WHY IT IS NOT ZERO
    --------------------------------------------------------------
    Be careful with the claim. Projecting a uniform sphere of radius r onto a plane gives a filled
    disc whose density diverges at the rim (proportional to 1/sqrt(r^2 - rho^2)), so the shadow of
    three shells is three bright rings on overlapping filled backgrounds -- structure, just badly
    degraded. A point near a shell's pole lands at the centre of the shadow, on top of the inner
    shell, so the classes genuinely mix.

    That partial leak is not a flaw in the construction, it is unavoidable: a structure whose
    two-dimensional views carry NO information at all is a parity function, and that family has a
    hardness proof attached (exp-023 sec. 2, Madelon). Any purely geometric three-dimensional
    structure leaks something into its shadows. So the right test is not "the pair scores zero" but
    "the gap between the best pair and the true triple is large, and the method takes the triple."
    `thickness` tunes the leak: thicker shells overlap more in projection, which shrinks the pair's
    score and the triple's together.

    NOISE COLUMNS ARE MARGINAL-MATCHED BY DEFAULT
    ---------------------------------------------
    `noise="matched"` draws each junk column by resampling the pooled informative coordinates, so
    every column has an identical one-dimensional distribution and no single feature can be told
    from junk by its histogram alone. This repo has been bitten before by a generator whose
    informative columns were identifiable one at a time (`run_one_column_gate.py`), which lets a
    method look good without ever using joint structure. `noise="uniform"` reproduces the older
    `_embed_2d` behaviour for comparability with the existing shape benchmarks.

    Returns (df, labels, informative dims).
    """
    rng = rng if rng is not None else np.random.default_rng()
    informative = list(informative)
    if len(informative) != 3:
        raise ValueError("shells live in exactly three dimensions")
    # SAMPLING DENSITY IS THE BINDING CONSTRAINT, and getting it wrong produces a dataset that
    # fails in THREE dimensions, which looks like a method failure and is not one. A sphere of
    # radius r carrying m points has nearest-neighbour spacing about 2r*sqrt(pi/m); the shells only
    # read as separate objects when that spacing is comfortably below the radial gap between them.
    # Measured: radii (1,2,3) needs n=3000 before the true three-column view reaches ARI 1.0, while
    # the wider spacing below gets there at n=1500 and two shells manage at n=600. Defaults are set
    # from those measurements, and `run_shells.py` refuses to draw conclusions if the true panel
    # scores low, because that means undersampling rather than anything about the method.
    radii = list(radii) if radii is not None else [1.0 + 2.0 * i for i in range(n_shells)]
    radii = radii[:n_shells]
    per = [n // n_shells] * n_shells
    for i in range(n - sum(per)):
        per[i] += 1

    xyz, labels = [], []
    for c, (r, m) in enumerate(zip(radii, per)):
        v = rng.normal(size=(m, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)      # uniform on the unit sphere
        rad = r + rng.normal(0.0, thickness, size=(m, 1))  # give the shell some thickness
        xyz.append(v * rad)
        labels.append(np.full(m, c))
    xyz = np.vstack(xyz)
    y = np.concatenate(labels)

    xyz = (xyz - xyz.min(0)) / (np.ptp(xyz, axis=0) + 1e-12)   # -> [0,1] per axis, as _embed_2d
    if noise == "matched":
        pool = xyz.ravel()
        X = rng.choice(pool, size=(len(xyz), p), replace=True)
    elif noise == "uniform":
        X = rng.random((len(xyz), p))
    else:
        raise ValueError('noise must be "matched" or "uniform"')
    for j, d in enumerate(informative):
        X[:, d] = xyz[:, j]

    perm = rng.permutation(len(X))
    return pd.DataFrame(X[perm], columns=_cols(p)), y[perm], informative
