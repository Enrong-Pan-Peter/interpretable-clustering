"""Phase 2 MST persistence core."""
import numpy as np

from atomicplus import persistence as P
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics


def test_persistence_ranks_informative_over_noise_and_recovers_split():
    rng = np.random.default_rng(0)
    X, y, info = syn.two_cluster_subspace(n=200, p=12, informative=[3, 7], rng=rng)
    X = X.to_numpy()
    r_inf = P.persistence_split(X[:, info], min_cluster_size=5)
    r_noise = P.persistence_split(X[:, [0, 1]], min_cluster_size=5)
    assert r_inf.valid and r_inf.score > 3 * r_noise.score      # strong gradient (flat had a tie)
    assert metrics.ari(y, r_inf.labels) >= 0.95                 # recovers the true split


def test_min_cluster_size_blocks_lone_outlier_cut():
    rng = np.random.default_rng(0)
    blob = rng.normal(0.0, 0.05, (40, 2))
    Xo = np.vstack([blob, [[9.0, 9.0]]])
    unguarded = P.persistence_split(Xo, min_cluster_size=1)
    guarded = P.persistence_split(Xo, min_cluster_size=5)
    assert int(min(np.bincount(unguarded.labels))) == 1        # would isolate the outlier
    assert (not guarded.valid) or int(min(np.bincount(guarded.labels))) >= 5


def test_core_distances_kth_neighbour():
    X = np.array([[0.0], [1.0], [2.0], [10.0]])
    c = P.core_distances(X, k=1)     # nearest-neighbour distance
    assert np.allclose(c, [1.0, 1.0, 1.0, 8.0])
