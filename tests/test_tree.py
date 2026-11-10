"""Phase 4 recursive tree: data structure (fast) + one hierarchy-recovery integration test."""
import numpy as np

from atomicplus import AtomicConfig, preprocess
from atomicplus import tree as T
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics


def test_tree_labels_and_leaves_from_hand_built_tree():
    leafA = T.TreeNode(indices=np.array([0, 1]), depth=2, reason="min_size", leaf_id=0)
    leafB = T.TreeNode(indices=np.array([2]), depth=2, reason="min_size", leaf_id=1)
    leafC = T.TreeNode(indices=np.array([3, 4, 5]), depth=1, reason="min_size", leaf_id=2)
    left = T.TreeNode(indices=np.array([0, 1, 2]), depth=1, features=[0], persistence=2.0,
                      children=[leafA, leafB])
    root = T.TreeNode(indices=np.array([0, 1, 2, 3, 4, 5]), depth=0, features=[1],
                      persistence=3.0, children=[left, leafC])
    tree = T.Tree(root, 6)
    assert tree.n_leaves() == 3
    assert list(tree.labels()) == [0, 0, 1, 2, 2, 2]
    assert "split on f1" in tree.pretty()


def test_build_tree_recovers_known_hierarchy():
    rng = np.random.default_rng(0)
    X, y, info = syn.hierarchical_subspace(n=150, p=10, level1=[0, 1], level2=[2, 3], rng=rng)
    cfg = AtomicConfig(fitness_mode="persistence", k_tilde=5, pop_size=30, mu=30, lam=18,
                       n_gen=10, archive_rebuild_every=20, min_cluster_size=4)
    tree = T.build_tree(preprocess(X).to_numpy(), config=cfg, min_persistence=1.5, max_depth=4)
    assert 3 <= tree.n_leaves() <= 5            # ~3 true clusters (allow mild over-split)
    assert metrics.ari(y, tree.labels()) >= 0.9
    assert (tree.labels() >= 0).all()           # every point lands in a leaf


def test_gate_passes_real_split_rejects_noise():
    from atomicplus import atomic, gate as G
    cfg = AtomicConfig(fitness_mode="persistence", k_tilde=5, pop_size=20, mu=20, lam=12,
                       n_gen=8, archive_rebuild_every=20, min_cluster_size=4)
    Xr, _, _ = syn.two_cluster_subspace(n=90, p=8, informative=[2, 5], rng=np.random.default_rng(1))
    Xr = preprocess(Xr).to_numpy()
    br = atomic(Xr, cfg, np.random.default_rng(0)).best()
    gr = G.evaluate_gate(Xr, br, cfg, mode="stability", min_persistence=1.2,
                         stability_min=0.5, n_sub=4)
    assert gr.passed and gr.stability >= 0.8         # real split reproduces

    Xn = np.random.default_rng(7).random((90, 8))
    bn = atomic(Xn, cfg, np.random.default_rng(0)).best()
    gn = G.evaluate_gate(Xn, bn, cfg, mode="stability", min_persistence=1.0,
                         stability_min=0.5, n_sub=4)
    assert not gn.passed                             # spurious split is rejected


def test_deceptive_generator_shape():
    X, y, info = syn.deceptive_hierarchy(n=120, p=8, rng=np.random.default_rng(0))
    assert X.shape == (120, 8)
    assert set(np.unique(y)) == {0, 1, 2}
    assert info["trap_dim"] == 2


def test_beam_tree_runs_and_recovers_clean_hierarchy():
    rng = np.random.default_rng(0)
    X, y, _ = syn.hierarchical_subspace(n=120, p=8, level1=[0, 1], level2=[2, 3], rng=rng)
    cfg = AtomicConfig(fitness_mode="persistence", k_tilde=5, pop_size=24, mu=24, lam=14,
                       n_gen=8, archive_rebuild_every=20, min_cluster_size=4)
    tr = T.build_tree(preprocess(X).to_numpy(), config=cfg, min_persistence=1.4,
                      max_depth=4, beam=2, gate_mode="none")
    assert metrics.ari(y, tr.labels()) >= 0.9


def test_nonconvex_and_redundant_generators_shape():
    Xm, ym, im = syn.moons_subspace(n=120, p=8, informative=[2, 5], rng=np.random.default_rng(0))
    assert Xm.shape == (120, 8) and set(np.unique(ym)) == {0, 1} and im == [2, 5]
    Xr, yr, ir = syn.redundant_informative(n=120, p=10, informative=[3, 4, 5], rng=np.random.default_rng(0))
    assert Xr.shape == (120, 10) and ir == [3, 4, 5]
