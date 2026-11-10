"""Null-model + stability machinery (fast, no EA)."""
import numpy as np

from atomicplus.evaluation import significance as sig


def test_column_permute_preserves_marginals_changes_order():
    X = np.arange(30, dtype=float).reshape(10, 3)
    Xp = sig.column_permute(X, np.random.default_rng(0))
    assert np.allclose(np.sort(X, axis=0), np.sort(Xp, axis=0))  # marginals kept
    assert not np.allclose(X, Xp)                                # order changed


def test_nogueira_identical_is_one():
    assert abs(sig.nogueira_stability([[1, 1, 0, 0]] * 6) - 1.0) < 1e-9


def test_nogueira_random_near_zero():
    rng = np.random.default_rng(0)
    rand = [(rng.random(20) < 0.5).astype(int) for _ in range(40)]
    assert abs(sig.nogueira_stability(rand)) < 0.15


def test_nogueira_handles_degenerate_input():
    assert np.isnan(sig.nogueira_stability([[1, 0, 1]]))  # <2 runs -> nan
