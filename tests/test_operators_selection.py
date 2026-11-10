"""Operators + clean-room NSGA-II (verified once against DEAP, then DEAP-free)."""
import numpy as np

from atomicplus import operators, selection


def test_mutation_preserves_min_features():
    rng = np.random.default_rng(0)
    g = np.zeros(12, dtype=np.int8)
    g[0] = g[1] = 1
    for _ in range(20):
        m = operators.mutate(g, rng, per_bit_prob=1.0, min_features=2)
        assert m.sum() >= 2


def test_legacy_mutation_runs_and_repairs():
    rng = np.random.default_rng(0)
    g = np.array([0, 1, 0, 0, 0, 0], dtype=np.int8)
    m = operators.mutate(g, rng, per_bit_prob=1.0, min_features=2, legacy=True)
    assert m.sum() >= 2


def test_crossover_or_is_union():
    a = np.array([1, 0, 1, 0], dtype=np.int8)
    b = np.array([0, 0, 1, 1], dtype=np.int8)
    c1, c2 = operators.crossover(a, b, np.random.default_rng(0), mode="or")
    assert list(c1) == [1, 0, 1, 1]
    assert list(c2) == [1, 0, 1, 1]


def test_uniform_crossover_keeps_shared_bits():
    a = np.array([1, 1, 0, 0], dtype=np.int8)
    b = np.array([1, 0, 1, 0], dtype=np.int8)
    c1, c2 = operators.crossover(a, b, np.random.default_rng(1), mode="uniform")
    assert c1[0] == 1 and c2[0] == 1


def _bruteforce_front0(M):
    n = len(M)
    front = set()
    for i in range(n):
        dominated = any(
            i != j and np.all(M[j] >= M[i]) and np.any(M[j] > M[i]) for j in range(n)
        )
        if not dominated:
            front.add(i)
    return front


def _bruteforce_fronts(M):
    remaining = set(range(len(M)))
    fronts = []
    while remaining:
        front = {
            i for i in remaining
            if not any(j != i and np.all(M[j] >= M[i]) and np.any(M[j] > M[i])
                       for j in remaining)
        }
        fronts.append(front)
        remaining -= front
    return fronts


def test_nondominated_front_matches_bruteforce():
    M = np.random.default_rng(0).random((40, 2))
    assert set(selection.fast_nondominated_sort(M)[0]) == _bruteforce_front0(M)


def test_nsga2_select_returns_exactly_mu_unique():
    M = np.random.default_rng(1).random((60, 2))
    sel = selection.nsga2_select(M, 25)
    assert len(sel) == 25 and len(set(sel)) == 25


def test_full_front_partition_matches_reference():
    M = np.random.default_rng(7).integers(0, 6, size=(30, 2)).astype(float)
    mine = [set(f) for f in selection.fast_nondominated_sort(M)]
    assert mine == _bruteforce_fronts(M)


def test_asymmetric_mutation_biases_towards_removal():
    rng = np.random.default_rng(0)
    g = np.ones(20, dtype=np.int8)                       # all features on
    out = operators.mutate(g, rng, per_bit_prob=0.0, min_features=2,
                           add_prob=0.02, remove_prob=0.5)
    assert out.sum() < g.sum()                           # removal-biased -> trims bits
    assert out.sum() >= 2                                # but respects the floor
