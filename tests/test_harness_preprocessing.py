"""The fairness harness (the core deliverable) + preprocessing."""
import numpy as np
import pandas as pd

from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import harness


def test_preprocess_imputes_and_scales_to_unit_range():
    df = pd.DataFrame({"a": [0.0, 1.0, np.nan, 3.0], "b": [10.0, 20.0, 30.0, 40.0]})
    out = preprocess(df, n_neighbors=2)
    assert not out.isna().any().any()               # NaN imputed
    assert out.to_numpy().min() >= -1e-9             # scaled to [0, 1]
    assert out.to_numpy().max() <= 1 + 1e-9


def test_subspace_parity_shows_metric_space_effect():
    """Same partition, two spaces: silhouette must be higher (and DB lower) in the
    low-dim informative subspace than in full space — the confound, isolated."""
    rng = np.random.default_rng(0)
    X, y, informative = syn.two_cluster_subspace(n=200, p=12, informative=[3, 7], rng=rng)
    tbl = harness.subspace_parity_demo(X.to_numpy(), informative, y)
    assert tbl.loc["subspace_V", "silhouette"] > tbl.loc["full_space", "silhouette"]
    assert tbl.loc["subspace_V", "davies_bouldin"] < tbl.loc["full_space", "davies_bouldin"]


def test_compare_returns_atomic_and_baselines():
    rng = np.random.default_rng(0)
    X, y, informative = syn.two_cluster_subspace(n=160, p=8, informative=[1, 4], rng=rng)
    # use the true labels as a stand-in ATOMIC partition for a fast harness smoke test
    tbl = harness.compare(X.to_numpy(), informative, y, y_true=y, rng=0)
    assert "ATOMIC" in tbl.index
    assert any("KMeans" in name for name in tbl.index)
    for col in ("sil_full", "sil_sub", "ari", "nmi"):
        assert col in tbl.columns
