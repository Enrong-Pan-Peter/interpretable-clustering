"""Independent verifier must handle empty contingency cells and label flips."""
import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score
from scripts.analyze_research_obstacle_results import ari


@pytest.mark.parametrize("a,b", [([0,0,1,1], [1,1,0,0]), ([0,0,1,1], [0,0,1,1]),
    ([0,0,0], [1,1,1]), ([0,0,0], [0,1,1]), ([0], [1]), ([0,1,2], [2,1,0])])
def test_contingency_ari_matches_reference_at_boundaries(a, b):
    assert ari(a,b) == pytest.approx(adjusted_rand_score(a,b))


def test_contingency_ari_matches_reference_for_multiclass_random_partitions():
    rng = np.random.default_rng(4)
    for n in (2, 7, 53):
        for _ in range(15):
            a, b = rng.integers(0, 4, n), rng.integers(0, 3, n)
            assert ari(a,b) == pytest.approx(adjusted_rand_score(a,b), abs=1e-12)
