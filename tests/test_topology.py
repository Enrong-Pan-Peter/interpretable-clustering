"""Hand-checkable topology + the stable-k (k̃) logic."""
import numpy as np

from atomicplus import topology


def test_two_separated_blobs_give_two_components():
    rng = np.random.default_rng(0)
    A = rng.normal(0.0, 0.02, size=(15, 2))
    B = rng.normal(10.0, 0.02, size=(15, 2))
    X = np.vstack([A, B])
    n_comp, _ = topology.component_count(X, k=3)
    assert n_comp == 2


def test_chaining_bridge_fuses_groups():
    """A chain of bridge points fuses two blobs under single-linkage kNN (caveat #3).

    Uses evenly-spaced (deterministic) blobs so each blob is one connected component;
    the point is the *bridge* effect, not blob density.
    """
    A = np.linspace(0.0, 1.0, 20).reshape(-1, 1)
    B = np.linspace(10.0, 11.0, 20).reshape(-1, 1)
    assert topology.component_count(np.vstack([A, B]), k=3)[0] == 2
    bridges = np.array([[3.0], [5.0], [7.0], [9.0]])
    fused = np.vstack([A, B, bridges])
    assert topology.component_count(fused, k=3)[0] == 1


def test_component_fitness_peaks_at_two():
    assert topology.component_fitness(2) == 0.0
    assert topology.component_fitness(1) == -1.0
    assert topology.component_fitness(3) == -1.0
    assert topology.component_fitness(5) == -9.0


def test_k_clamped_to_n_minus_one():
    X = np.random.default_rng(0).normal(size=(4, 2))
    # k far larger than n-1 must not crash; still returns a valid count.
    n_comp, labels = topology.component_count(X, k=99)
    assert n_comp >= 1 and len(labels) == 4


def test_stable_k_from_trace():
    # first unchanged consecutive pair is (2->5, 3->5) => stable k = 2
    assert topology.stable_k_from_trace([(2, 5), (3, 5), (4, 3)]) == 2
    # first unchanged pair is (3->4, 4->4) => stable k = 3
    assert topology.stable_k_from_trace([(2, 5), (3, 4), (4, 4)]) == 3
    # never stabilises => int fallback (last k), NOT a tuple (bug #2 fixed