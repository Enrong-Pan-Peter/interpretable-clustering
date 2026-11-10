"""Independent saved-state prediction replay on fresh queries and duplicate rows."""
import numpy as np
import pytest

from atomic_research.kernel_panels import fit_kernel_panel
from scripts.analyze_research_kernel_results import predict_saved


@pytest.mark.parametrize("kernel", ["local", "global"])
def test_independent_replay_matches_landmarks_and_unseen_queries(tmp_path, kernel):
    rng = np.random.default_rng(3)
    X = rng.normal(size=(50, 9))
    X[0, 2] = np.nan
    model = fit_kernel_panel(X, budget=6, steps=2, restarts=1, kernel=kernel, max_samples=30)
    path = tmp_path / "model.npz"
    model.save(path)
    with np.load(path, allow_pickle=False) as f:
        state = {k: f[k] for k in f.files}
    query = np.vstack((X, X[:2], rng.normal(size=(20, 9))))
    predicted, embedding = predict_saved(query, state)
    np.testing.assert_array_equal(predicted, model.predict(query))
    np.testing.assert_allclose(embedding, model.embed(query), atol=1e-9)
