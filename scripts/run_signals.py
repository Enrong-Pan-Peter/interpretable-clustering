"""Subspace-selection SIGNAL comparison: which criterion reliably picks the informative subspace
for non-convex structure hidden in noise? Diagnosis (session): raw MST-persistence scores a CORRECT
non-convex split as "no gap" ~half the time, so noise pairs with tiny spurious gaps win. Test whether
a partition-QUALITY signal (density validity) fixes it.

Signals scored per candidate feature pair (same persistence_split partition, different SCORING):
  * persist    -- current e_cut/e_next ratio (baseline).
  * dbcv_lite  -- (min between-cluster mutual-reach - max within-cluster MST edge)/max(...)  [DBCV core].
  * cut_within -- between-cluster gap / median within-cluster edge.
Report, per dataset/signal: mean recovery-ARI (ARI of the argmax-signal pair) and how often the TRUE
pair is ranked #1; compare to the ORACLE (true pair handed in). Higher recovery-ARI = better selection.

    python scripts/run_signals.py --seeds 30 moons circles jain flame
"""
import os, sys, itertools, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics
from atomicplus.persistence import persistence_split, core_distances

DATA2D = os.path.join(os.path.dirname(__file__), "..", "2d_data"); INF = [3, 8]; P = 12
def load(name, seed):
    rng = np.random.default_rng(seed)
    if name == "moons": return (lambda X, y, _: (preprocess(X).to_numpy(), y))(*syn.moons_subspace(n=240, p=P, informative=INF, rng=rng))
    if name == "circles": return (lambda X, y, _: (preprocess(X).to_numpy(), y))(*syn.circles_subspace(n=240, p=P, informative=INF, rng=rng))
    arr = np.loadtxt(os.path.join(DATA2D, f"{name}.txt"), skiprows=1); xy = arr[:, :2].astype(float); y = arr[:, 2].astype(int)
    xy = (xy - xy.min(0)) / (np.ptp(xy, 0) + 1e-12); X = rng.random((len(xy), P)); X[:, INF[0]], X[:, INF[1]] = xy[:, 0], xy[:, 1]
    return preprocess(pd.DataFrame(X)).to_numpy(), y

def split(Z):
    r = persistence_split(Z, min_cluster_size=5, mutual_reachability=True, core_k=5); return (r.score if r.valid else -1.0), r.labels
def _mr(Z):
    c = core_distances(Z, 5); D = squareform(pdist(Z)); M = np.maximum(D, np.maximum.outer(c, c)); np.fill_diagonal(M, 0); return M
def dbcv_lite(Z, lab):
    if lab is None: return -9.0
    a = np.flatnonzero(lab == 0); b = np.flatnonzero(lab == 1)
    if len(a) < 2 or len(b) < 2: return -9.0
    M = _mr(Z); sep = M[np.ix_(a, b)].min()
    def me(idx):
        t = minimum_spanning_tree(csr_matrix(M[np.ix_(idx, idx)])); return t.data.max() if t.nnz else 0.0
    spa = max(me(a), me(b)); return (sep - spa) / max(sep, spa, 1e-9)
def cut_within(Z, lab):
    if lab is None: return -9.0
    a = np.flatnonzero(lab == 0); b = np.flatnonzero(lab == 1)
    if len(a) < 2 or len(b) < 2: return -9.0
    M = _mr(Z); sep = M[np.ix_(a, b)].min()
    w = np.concatenate([M[np.ix_(a, a)][np.triu_indices(len(a), 1)], M[np.ix_(b, b)][np.triu_indices(len(b), 1)]])
    return sep / (np.median(w) + 1e-9)

def main():
    args = list(sys.argv[1:]); seeds = 30
    if "--seeds" in args: i = args.index("--seeds"); seeds = int(args[i+1]); del args[i:i+2]
    datasets = args if args else ["moons", "circles", "jain", "flame"]
    rows = []
    for name in datasets:
        for seed in range(seeds):
            Xp, y = load(name, seed)
            recs = []
            for pr in itertools.combinations(range(P), 2):
                Z = Xp[:, list(pr)]; s, lab = split(Z); a = metrics.ari(y, lab) if lab is not None else 0.0
                recs.append((pr, s, dbcv_lite(Z, lab), cut_within(Z, lab), a))
            def pick(k): return max(recs, key=lambda t: t[k])
            truth = next(t for t in recs if set(t[0]) == set(INF))
            rank = lambda k: 1 + sorted(recs, key=lambda t: -t[k]).index(truth)
            rows.append(dict(dataset=name, seed=seed,
                persist=pick(1)[4], dbcv=pick(2)[4], cut=pick(3)[4], oracle=truth[4],
                persist_rank1=int(rank(1) == 1), dbcv_rank1=int(rank(2) == 1)))
        print(f"  done {name}", flush=True)
    df = pd.DataFrame(rows)
    for path in ("results/signals.csv", "/tmp/signals.csv"):
        try: os.makedirs(os.path.dirname(path) or ".", exist_ok=True); df.to_csv(path, index=False); print(f"saved {path}"); break
        except PermissionError: continue
    print("\n== mean recovery-ARI (ARI of the argmax-signal pair); higher=better selection ==")
    print(df.groupby("dataset")[["persist", "dbcv", "cut", "oracle"]].mean().round(2).to_string())
    print("\n== how often the TRUE pair is ranked #1 (selection accuracy) ==")
    print(df.groupby("dataset")[["persist_rank1", "dbcv_rank1"]].mean().round(2).to_string())

if __name__ == "__main__":
    main()
