"""Subspace-clustering baselines and the shared selection-signal terms.

WHY THIS FILE EXISTS
--------------------
The strongest pessimistic claim against the project is "the fix that works isn't novel --
it's just density-based subspace clustering (SUBCLU)". That claim has never been measured.
This module provides the machinery to measure it:

  * `subclu`   - a faithful re-implementation of SUBCLU (Kailing, Kriegel & Kroger, SDM 2004).
                 There is no SUBCLU on PyPI, so we implement it ourselves; doing so also lets us
                 control and document the fairness of the comparison.
  * `graphcut_term` / `density_term` - the two halves of the graph-cut+density selection signal,
                 lifted verbatim from scripts/run_fitness_sweep.py so the numbers reproduce.
                 (This also starts HANDOFF next-step #4: the signal living in the package, not
                 only in experiment scripts.)

FAIRNESS NOTES (read before quoting any number this produces)
-------------------------------------------------------------
* SUBCLU uses ONE global eps across all subspaces. That is the published algorithm, and it is a
  known weakness of it. We do NOT hide that: we sweep eps and report SUBCLU under both a
  self-tuned rule and an ORACLE rule (the eps that maximises its ARI). The oracle column is an
  upper bound the real algorithm cannot reach, and exists so we cannot be accused of
  sandbagging the baseline.
* SUBCLU has no intrinsic ranking over the subspaces it returns. We therefore report BOTH
  `hit_any` (was the true subspace returned at all -- generous to SUBCLU) and a rank-1 number
  under an explicitly stated tie-break. Quote `hit_any` when asking "can SUBCLU find it";
  quote rank-1 only when comparing like-for-like against a method that must commit to one answer.
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN, SpectralClustering
from sklearn.neighbors import kneighbors_graph

from ..persistence import core_distances, persistence_split

# --------------------------------------------------------------------------------------------
# Shared selection-signal terms (verbatim from run_fitness_sweep.py -- do not "improve" silently)
# --------------------------------------------------------------------------------------------

DEFAULT_KNN_K = 10      # kNN graph degree.   CONVENTIONAL DEFAULT, NOT TUNED.
DEFAULT_CORE_K = 5      # core distance = distance to 5th neighbour. NOT TUNED.


def mutual_reach(Z: np.ndarray, core_k: int = DEFAULT_CORE_K) -> np.ndarray:
    """Mutual-reachability distance matrix (HDBSCAN's metric)."""
    c = core_distances(Z, core_k)
    D = squareform(pdist(Z))
    M = np.maximum(D, np.maximum.outer(c, c))
    np.fill_diagonal(M, 0.0)
    return M


def _connect_graph(A: np.ndarray, D: np.ndarray) -> Tuple[np.ndarray, int]:
    """Ensure the kNN graph is connected, and report how many components it had.

    WHY THIS IS NOT COSMETIC. A disconnected kNN graph has cut = 0 exactly, so NCut = 0 and our
    score -NCut = 0, which is the MAXIMUM attainable value. Disconnected subspaces therefore float
    to the top of the ranking and tie there. On the mice data 39% of pairs came out disconnected
    under dc-dist and ALL of the top 20 were degenerate ties -- the ranking was meaningless.
    Volume normalisation cannot save us here, because 0 / anything is still 0.

    Fix: join the components with the lightest available edges (MST edges of the underlying
    distance whose endpoints straddle components). This is standard practice for spectral
    clustering on kNN graphs, it makes cut > 0 so the score is well defined, and it makes scores
    comparable across candidate subspaces. It also removes sklearn's "Graph is not fully
    connected" warning by removing its cause rather than silencing it.
    """
    n_comp, lab = connected_components(csr_matrix(A), directed=False)
    if n_comp == 1:
        return A, 1
    A = A.copy()
    mst = minimum_spanning_tree(csr_matrix(D)).tocoo()
    for i, j in zip(mst.row, mst.col):
        if lab[i] != lab[j]:
            A[i, j] = A[j, i] = 1.0
    n2, _ = connected_components(csr_matrix(A), directed=False)
    if n2 > 1:                      # MST edges alone did not suffice; close the rest greedily
        for c in range(1, n2):
            idx = np.flatnonzero(_relabel(A) == c)
            if len(idx):
                A[idx[0], 0] = A[0, idx[0]] = 1.0
    return A, n_comp


def _relabel(A: np.ndarray) -> np.ndarray:
    return connected_components(csr_matrix(A), directed=False)[1]


def density_term(Z: np.ndarray, core_k: int = DEFAULT_CORE_K,
                 min_cluster_size: int = 5) -> Tuple[float, np.ndarray | None]:
    """DBCV-style validity of the single-linkage bipartition of Z.

    (min between-cluster mutual reach - max within-cluster MST edge) / max(those).
    Returns (score, labels); score -9.0 marks a degenerate split.
    """
    r = persistence_split(Z, min_cluster_size=min_cluster_size, mutual_reachability=True,
                          core_k=core_k, normalize="none")
    lab = r.labels
    if lab is None or (lab == 0).sum() < 2 or (lab == 1).sum() < 2:
        return -9.0, lab
    M = mutual_reach(Z, core_k)
    a = np.flatnonzero(lab == 0)
    b = np.flatnonzero(lab == 1)
    sep = M[np.ix_(a, b)].min()

    def max_mst_edge(idx: np.ndarray) -> float:
        t = minimum_spanning_tree(csr_matrix(M[np.ix_(idx, idx)]))
        return float(t.data.max()) if t.nnz else 0.0

    wa, wb = max_mst_edge(a), max_mst_edge(b)
    return float((sep - max(wa, wb)) / max(sep, wa, wb, 1e-9)), lab


def selftuning_affinity(D: np.ndarray, k: int = DEFAULT_KNN_K) -> np.ndarray:
    """Zelnik-Manor & Perona (NIPS 2004) locally-scaled affinity: exp(-d_ij^2 / (s_i * s_j)),
    with s_i the distance from point i to its k-th nearest neighbour.

    WHY THIS IS OFFERED AS AN OPTION. Our default graph is binary kNN connectivity with a fixed
    k=10, and HANDOFF flags k=10 and core_k=5 as untuned defaults whose sensitivity was never
    tested. A fixed global neighbourhood judges density on an absolute scale, so where two groups
    overlap with shifted means -- METABRIC's subtypes, HAR sitting-vs-standing -- the neighbourhood
    is wide enough to smooth away the density saddle between the two modes and the graph sees one
    blob. A per-point bandwidth judges density RELATIVE TO LOCAL SCALE, which is where a saddle
    between overlapping modes should become visible.

    It also REMOVES a hyper-parameter rather than adding one: the bandwidth is read off the data
    instead of being set. Adopted by GroupFS (AAAI 2026) across all their graph-based baselines
    for exactly that reason -- "to avoid manual bandwidth tuning".

    DEFAULT OFF. It changes the geometry, so any result computed with it is not comparable to the
    existing tables; run it as an arm alongside the default, never as a silent replacement.
    """
    n = len(D)
    kk = min(k, n - 1)
    sigma = np.sort(D, axis=1)[:, kk]                    # distance to the k-th neighbour
    sigma = np.maximum(sigma, 1e-12)
    W = np.exp(-(D ** 2) / np.outer(sigma, sigma))
    np.fill_diagonal(W, 0.0)
    return W


def graphcut_term(Z: np.ndarray, k: int = DEFAULT_KNN_K,
                  rng: int = 0, affinity: str = "knn") -> Tuple[float, np.ndarray | None]:
    """-NCut of the spectral bipartition of the neighbourhood graph. Returns (score, labels).

    `affinity="knn"` (default) is the binary k-nearest-neighbour graph every existing result in
    this project was computed with. `affinity="selftuning"` swaps in the locally-scaled Gaussian
    of `selftuning_affinity` -- an ARM to compare against, not a replacement. See that function
    for why it might help on data whose groups overlap rather than separate.
    """
    if affinity == "selftuning":
        D = squareform(pdist(Z))
        A = selftuning_affinity(D, k)
        A, _ = _connect_graph(A, D)
    elif affinity == "knn":
        A = kneighbors_graph(Z, n_neighbors=min(k, len(Z) - 1), mode="connectivity",
                             include_self=False)
        A = 0.5 * (A + A.T).toarray()
        A, _ = _connect_graph(A, squareform(pdist(Z)))
    else:
        raise ValueError('affinity must be "knn" or "selftuning"')
    try:
        lab = SpectralClustering(n_clusters=2, affinity="precomputed",
                                 random_state=rng).fit_predict(A)
    except Exception:  # noqa: BLE001
        return -9.0, None
    d = A.sum(1)
    a, b = lab == 0, lab == 1
    if a.sum() < 2 or b.sum() < 2:
        return -9.0, lab
    cut = A[np.ix_(a, b)].sum()
    ncut = cut / max(d[a].sum(), 1e-9) + cut / max(d[b].sum(), 1e-9)
    return float(-ncut), lab


def zscore(v: Sequence[float]) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    s = v.std()
    return (v - v.mean()) / (s if s > 1e-9 else 1.0)


# --------------------------------------------------------------------------------------------
# SUBCLU (Kailing, Kriegel & Kroger, "Density-Connected Subspace Clustering for
# High-Dimensional Data", SDM 2004)
# --------------------------------------------------------------------------------------------

def _dbscan_clusters(Z: np.ndarray, eps: float, min_pts: int) -> List[np.ndarray]:
    """DBSCAN on Z; returns a list of index arrays, one per cluster (noise dropped)."""
    if len(Z) < min_pts:
        return []
    lab = DBSCAN(eps=eps, min_samples=min_pts).fit_predict(Z)
    return [np.flatnonzero(lab == c) for c in np.unique(lab) if c != -1]


def _join_candidates(keys: Sequence[Tuple[int, ...]], k: int) -> List[Tuple[int, ...]]:
    """Apriori join: merge two k-dim subspaces sharing their first k-1 dimensions."""
    out = set()
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if a[:k - 1] == b[:k - 1] and a[k - 1] < b[k - 1]:
                out.add(tuple(sorted(set(a) | set(b))))
    return sorted(out)


def subclu(X: np.ndarray, eps: float, min_pts: int = 5,
           max_dim: int = 2) -> Dict[Tuple[int, ...], List[np.ndarray]]:
    """Bottom-up density-connected subspace clustering.

    Exploits the monotonicity of density-connectivity: if a subspace S contains a cluster,
    every subspace of S does too. So we build dense subspaces bottom-up and prune any
    candidate with a non-dense (k-1)-subset.

    `max_dim` caps the subspace dimensionality. Default 2 because every experiment in this
    project plants the signal in a 2-D subspace, so capping at 2 makes SUBCLU's search space
    identical to ours -- that is the fair setting. Raise it to let SUBCLU roam, which is
    *harder* for it, not easier.

    Returns {subspace_tuple: [cluster_index_array, ...]} for every dense subspace found.
    """
    X = np.asarray(X, dtype=float)
    n, p = X.shape

    current: Dict[Tuple[int, ...], List[np.ndarray]] = {}
    for j in range(p):                                        # k = 1
        cl = _dbscan_clusters(X[:, [j]], eps, min_pts)
        if cl:
            current[(j,)] = cl
    found: Dict[Tuple[int, ...], List[np.ndarray]] = dict(current)

    k = 1
    while current and k < max_dim:
        candidates = _join_candidates(sorted(current.keys()), k)
        nxt: Dict[Tuple[int, ...], List[np.ndarray]] = {}
        for cand in candidates:
            subs = [s for s in itertools.combinations(cand, k) if s in current]
            if len(subs) < k + 1:            # apriori prune: ALL k-subsets must be dense
                continue
            # SUBCLU heuristic: run DBSCAN only inside the clusters of the cheapest subspace
            best = min(subs, key=lambda s: sum(len(a) for a in current[s]))
            clusters: List[np.ndarray] = []
            for idx in current[best]:
                if len(idx) < min_pts:
                    continue
                for sub in _dbscan_clusters(X[np.ix_(idx, list(cand))], eps, min_pts):
                    clusters.append(idx[sub])
            if clusters:
                nxt[cand] = clusters
        current = nxt
        found.update(current)
        k += 1
    return found


def clusters_to_labels(n: int, clusters: List[np.ndarray]) -> np.ndarray:
    """Index-arrays -> label vector (-1 = not in any cluster). Later clusters win overlaps."""
    lab = np.full(n, -1, dtype=int)
    for cid, idx in enumerate(clusters):
        lab[idx] = cid
    return lab


def subclu_candidates(X: np.ndarray, eps: float, min_pts: int = 5, max_dim: int = 2,
                      dim: int = 2) -> Dict[Tuple[int, ...], np.ndarray]:
    """Every `dim`-dimensional subspace SUBCLU returns, with its labelling.

    Use this rather than `subclu_select` when you want to apply several different tie-breaks to
    the SAME SUBCLU output -- including a best-possible (oracle) tie-break. SUBCLU itself has no
    ranking over the subspaces it returns, so WHICH tie-break we impose is our choice, not the
    algorithm's, and imposing a poor one would silently handicap the baseline.
    """
    found = subclu(X, eps=eps, min_pts=min_pts, max_dim=max_dim)
    return {s: clusters_to_labels(len(X), found[s]) for s in sorted(found) if len(s) == dim}


def subclu_select(X: np.ndarray, eps: float, min_pts: int = 5, max_dim: int = 2,
                  dim: int = 2) -> Tuple[Tuple[int, ...] | None, np.ndarray | None,
                                         List[Tuple[int, ...]]]:
    """Run SUBCLU and commit to ONE subspace of dimensionality `dim`.

    Tie-break (stated explicitly so it can be criticised): among returned `dim`-dimensional
    subspaces, take the one whose SUBCLU labelling has the highest density validity, computed
    with the SAME density_term used by our own signal. Ties broken by lexicographic order for
    determinism.

    Returns (selected_subspace, labels, all_returned_subspaces_of_that_dim).
    """
    found = subclu(X, eps=eps, min_pts=min_pts, max_dim=max_dim)
    cands = sorted(s for s in found if len(s) == dim)
    if not cands:
        return None, None, []
    best = None
    for s in cands:
        lab = clusters_to_labels(len(X), found[s])
        keep = lab >= 0
        score = -9.0
        if keep.sum() >= 4 and len(np.unique(lab[keep])) >= 2:
            score, _ = density_term(X[np.ix_(np.flatnonzero(keep), list(s))])
        if best is None or score > best[0]:
            best = (score, s, lab)
    return best[1], best[2], cands


def subclu_retrieval_stats(returned: Sequence[Tuple[int, ...]],
                           truth: Tuple[int, ...]) -> Dict[str, float]:
    """Score SUBCLU's OUTPUT AS A LIST, without making it commit to one answer.

    WHY BOTH THIS AND A TIE-BREAK
    -----------------------------
    SUBCLU returns a SET of dense subspaces with no ordering over them. Scoring it by rank-1
    accuracy therefore measures a tie-break WE bolted on, not the algorithm. Two honest views
    exist and they answer different questions, so we record both on every run and choose at
    writing time (HANDOFF section 4 item 6):

      * RETRIEVAL (this function) -- treat the returned set as a retrieval result. Recall = did
        the true panel come back at all. Precision = how much of what came back was the answer.
        This is the view that does not require inventing a ranking, and it is the fairer one to
        the baseline.
      * BEST-CASE tie-break (`subclu_select`, plus the ORACLE columns) -- give SUBCLU the most
        favourable rule we can, and compare rank-1 accuracy against ours.

    They tell different stories and both are true. On the repaired benchmark recall is high
    (the true pair is usually in the list) while rank-1 is low, and that gap IS our claim: the
    contribution is the ranking signal, not the ability to find candidates.

    Precision is reported two ways because a set of one and a set of two hundred both containing
    the answer are not the same result:
      `precision`  = 1/len(returned) when the truth is present -- how concentrated the output is.
      `n_returned` = the raw size, so precision can be read in context rather than as a bare ratio.
    """
    ret = [tuple(sorted(s)) for s in returned]
    t = tuple(sorted(truth))
    hit = float(t in ret)
    n = len(ret)
    prec = hit / n if n else 0.0
    return {"subclu_recall": hit, "subclu_precision": prec,
            "subclu_f1": (2 * prec * hit / (prec + hit)) if (prec + hit) > 0 else 0.0,
            "subclu_n_returned": float(n),
            # 1 = the answer was the only thing returned; 0 = it was not returned at all.
            # A random pick from the returned list would be right this often, which is the
            # fairest single number for "SUBCLU with no tie-break at all".
            "subclu_random_pick": prec}


# --------------------------------------------------------------------------------------------
# IMM -- the explainable-k-means threshold tree (Moshkovitz, Dasgupta, Rashtchian & Frost,
# "Explainable k-Means and k-Medians Clustering", ICML 2020; also the base tree of ExKMC,
# Frost, Moshkovitz & Rashtchian 2020).
#
# WHY WE RE-IMPLEMENT IT: the `ExKMC` PyPI package ships only pre-generated Cython C that was
# built against Python <= 3.8 headers (`longintrepr.h`), so it does not compile on Python 3.11+
# and no .pyx is shipped to regenerate from. This is OUR implementation of IMM, and must be
# labelled as such in any writeup -- it is not the authors' code.
#
# SCOPE: this is the IMM base tree (exactly k leaves). ExKMC's extra-leaves extension is NOT
# implemented; it lowers k-means cost but does not change which features the tree splits on,
# and with max_leaves = k there are no extra leaves anyway. Since our comparison is about WHICH
# FEATURES an interpretable tree uses, that is the relevant part.
#
# WHAT IT IS A STAND-IN FOR: the interpretable-clustering-tree family. It is axis-aligned, so it
# is NOT the KDD 2022 oblique (sparse-hyperplane) method, which is strictly more expressive.
# A failure of IMM is therefore weaker evidence than a failure of the oblique method would be.
# Say that in the paper rather than letting the reader assume otherwise.
# --------------------------------------------------------------------------------------------

def _imm_build(X, assign, centers, pt_idx, center_ids, used):
    """Recursively split until one centre remains. Returns a nested (feature, theta, l, r) tree."""
    if len(center_ids) == 1:
        return ("leaf", int(center_ids[0]))
    best = None
    for i in range(X.shape[1]):
        cv = np.sort(np.unique(centers[center_ids, i]))
        if len(cv) < 2:
            continue
        for a, b in zip(cv[:-1], cv[1:]):
            theta = 0.5 * (a + b)
            # a "mistake" = a point that lands on the opposite side from its own k-means centre
            left_pt = X[pt_idx, i] <= theta
            left_ct = centers[assign[pt_idx], i] <= theta
            m = int(np.count_nonzero(left_pt != left_ct))
            if best is None or m < best[0]:
                best = (m, i, theta)
    if best is None:
        return ("leaf", int(center_ids[0]))
    _, feat, theta = best
    used.add(int(feat))
    lc = np.array([c for c in center_ids if centers[c, feat] <= theta])
    rc = np.array([c for c in center_ids if centers[c, feat] > theta])
    if len(lc) == 0 or len(rc) == 0:                       # degenerate: stop rather than loop
        return ("leaf", int(center_ids[0]))
    lp = pt_idx[X[pt_idx, feat] <= theta]
    rp = pt_idx[X[pt_idx, feat] > theta]
    return ("node", feat, theta,
            _imm_build(X, assign, centers, lp, lc, used),
            _imm_build(X, assign, centers, rp, rc, used))


def _imm_apply(tree, X):
    lab = np.zeros(len(X), dtype=int)
    def walk(node, idx):
        if node[0] == "leaf":
            lab[idx] = node[1]; return
        _, feat, theta, l, r = node
        m = X[idx, feat] <= theta
        walk(l, idx[m]); walk(r, idx[~m])
    walk(tree, np.arange(len(X)))
    return lab


def imm_tree(X: np.ndarray, k: int = 2, rng: int = 0) -> Tuple[np.ndarray, List[int]]:
    """Fit k-means then explain it with an axis-aligned threshold tree of exactly k leaves.

    Returns (labels, sorted list of features the tree splits on). That feature list is this
    family's answer to "which features matter", and is what we compare against our panels.
    """
    from sklearn.cluster import KMeans
    X = np.asarray(X, dtype=float)
    km = KMeans(n_clusters=k, n_init=10, random_state=rng).fit(X)
    used: set[int] = set()
    tree = _imm_build(X, km.labels_, km.cluster_centers_, np.arange(len(X)),
                      np.arange(k), used)
    return _imm_apply(tree, X), sorted(used)


def cart_on_kmeans(X: np.ndarray, k: int = 2, rng: int = 0) -> Tuple[np.ndarray, List[int]]:
    """The cruder interpretable-tree baseline practitioners actually use: fit k-means, then a
    decision tree on its labels. Included because it is the obvious thing to try, so a reviewer
    will ask whether it already suffices."""
    from sklearn.cluster import KMeans
    from sklearn.tree import DecisionTreeClassifier
    X = np.asarray(X, dtype=float)
    km = KMeans(n_clusters=k, n_init=10, random_state=rng).fit(X)
    dt = DecisionTreeClassifier(max_leaf_nodes=k, random_state=rng).fit(X, km.labels_)
    used = sorted({int(f) for f in dt.tree_.feature if f >= 0})
    return dt.predict(X), used


# --------------------------------------------------------------------------------------------
# Density-connectivity distance (dc-dist) -- Beer, Draganov, Hohma, Jahn, Frey & Assent,
# "Connecting the Dots -- Density-Connectivity Distance unifies DBSCAN, k-Center and Spectral
# Clustering", KDD 2023. Successor: Draganov, Weber, Jorgensen, Beer, Plant & Assent,
# "Ultrametric Cluster Hierarchies", NeurIPS 2025 (pip install SHiP-framework).
#
# WHY WE WANT IT: exp-018 showed our scores collapse when a junk column is added, because every
# junk column inflates every Euclidean distance. dc-dist is a MINIMAX-PATH ultrametric -- the
# distance between two points is the largest edge on the best path between them through the
# mutual-reachability graph. It therefore depends only on WHICH edge is the bottleneck, not on
# the magnitude of the distances along the path. A junk column that inflates all distances
# roughly uniformly does not change the bottleneck, so the score should be far more tolerant of
# irrelevant columns. That is a principled reason to expect it to help, not a guess.
#
# FIRST MEASUREMENT (4 seeds, p=20 -- indicative only, NOT evidence), d(t2 vs t1):
#            euclidean Ncut        dc-dist Ncut
#   circles   4.62 -> -1.07         1.78 -> 1.14
#   spiral    2.56 -> -0.40         1.03 -> 2.36
#   moons     4.21 ->  3.34         1.61 -> 1.54
# Lower peak at k=2, but FLAT-OR-RISING under dilution on all three, where Euclidean inverts on
# two of them. It trades peak strength for tolerance -- which is the trade we want.
#
# Implemented directly rather than via SHiP: the minimax-path ultrametric is exactly the
# cophenetic distance of single linkage on the mutual-reachability graph, which is transparent,
# dependency-free and matches the paper's definition.
# --------------------------------------------------------------------------------------------

def dc_distance(Z: np.ndarray, core_k: int = DEFAULT_CORE_K) -> np.ndarray:
    """Density-connectivity (minimax-path) ultrametric on the mutual-reachability graph."""
    from scipy.cluster.hierarchy import cophenet, linkage
    from scipy.spatial.distance import squareform as _sq
    M = mutual_reach(Z, core_k)
    return _sq(cophenet(linkage(_sq(M, checks=False), method="single")))


def graphcut_term_dcdist(Z: np.ndarray, k: int = DEFAULT_KNN_K,
                         core_k: int = DEFAULT_CORE_K,
                         rng: int = 0) -> Tuple[float, np.ndarray | None]:
    """Our -NCut term, but with the kNN graph built in dc-dist space instead of Euclidean.

    Same statistic, different metric -- so any difference is attributable to the metric alone.
    """
    D = dc_distance(Z, core_k)
    n = len(D)
    kk = min(k, n - 1)
    idx = np.argsort(D, axis=1)[:, 1:kk + 1]
    A = np.zeros((n, n))
    A[np.repeat(np.arange(n), kk), idx.ravel()] = 1.0
    A = 0.5 * (A + A.T)
    A, _ = _connect_graph(A, D)
    try:
        lab = SpectralClustering(n_clusters=2, affinity="precomputed",
                                 random_state=rng).fit_predict(A)
    except Exception:  # noqa: BLE001
        return -9.0, None
    d = A.sum(1)
    a, b = lab == 0, lab == 1
    if a.sum() < 2 or b.sum() < 2:
        return -9.0, lab
    cut = A[np.ix_(a, b)].sum()
    return float(-(cut / max(d[a].sum(), 1e-9) + cut / max(d[b].sum(), 1e-9))), lab
