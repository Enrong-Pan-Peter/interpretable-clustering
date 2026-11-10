"""Known-answer validation: on data where we know the truth, ATOMIC must recover the
correct bipartition with a small feature set (so a re-implementation bug can't hide)."""
import numpy as np

from atomicplus import AtomicConfig, atomic
from atomicplus import genome as gm
from atomicplus import topology
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics


def test_informative_subspace_splits_noise_does_not():
    rng = np.random.default_rng(0)
    X, y, informative = syn.two_cluster_subspace(n=200, p=10, informative=[2, 5], rng=rng)
    Xn = X.to_numpy()
    assert topology.component_count(Xn[:, informative], k=5)[0] == 2   # informative -> 2
    assert topology.component_count(Xn[:, [0, 1]], k=5)[0] == 1        # pure noise -> 1


def test_atomic_recovers_correct_split_with_few_features():
    rng = np.random.default_rng(0)
    X, y, informative = syn.two_cluster_subspace(n=200, p=10, informative=[2, 5], rng=rng)
    cfg = AtomicConfig(seed=1, k_tilde=5, pop_size=50, mu=50, lam=40,
                       n_gen=20, archive_rebuild_every=10)
    res = atomic(X.to_numpy(), cfg)
    best = res.best()
    selected = set(int(i) for i in gm.selected_indices(best.genome))
    assert best.quality.n_components == 2                 # found a clean 2-way split
    assert best.quality.size <= 4                         # and it is small
    assert metrics.ari(y, best.quality.labels) >= 0.9     # matching the true clusters
    assert selected & set(informative)                    # using >=1 truly informative dim


def test_k_tilde_is_int_and_reasonable():
    rng = np.random.default_rng(1)
    X, _, _ = syn.two_cluster_subspace(n=150, p=6, informative=[0, 3], rng=rng)
    k = topology.choose_k(X.to_numpy(), 2, 20)
    assert isinstance(k, int) and 2 <= k <= 20
