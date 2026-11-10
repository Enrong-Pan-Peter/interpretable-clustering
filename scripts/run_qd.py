"""Quality-Diversity (MAP-Elites variants) vs random vs greedy at recovering clean minimal panels.

Tests whether modern QD + the fixes Enrong proposed (sparse init #1, reward-small #2, CVT-MAP-Elites
for high dimensions #3) make the EA family MORE SAMPLE-EFFICIENT than random -- especially at HIGH p,
where informative pairs are sparse among C(p,2) and random wastes budget on noise pairs.

  MAP-Elites     -- sparse init + breed-from-elites; niche = exact feature set; best-per-niche.
  CVT-MAP-Elites -- Vassiliades/Chatzilygeroudis/Mouret 2017: fixed k well-spread niches via a
                    centroidal Voronoi tessellation (k-means on random descriptors); scales to
                    high-dimensional feature spaces where grid MAP-Elites cannot.
  random, greedy(multi-start) -- baselines, same budget.

WIN for the EA family = QD recovers clean pairs at LOWER budget than random, gap GROWING with p.
TIE with random everywhere = no EA edge even at its best. (Neither can beat random on a NEEDLE --
that is a property of the threshold-shaped objective, not the search. This tests efficiency only.)

    python scripts/run_qd.py --seeds 20 --ps 15,40,80 --budgets 500,1500,4000
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from atomicplus import preprocess                                  # noqa: E402
from atomicplus.datasets import synthetic as syn                   # noqa: E402
from atomicplus.evaluation import metrics                          # noqa: E402
from atomicplus.persistence import persistence_split               # noqa: E402

MCS, MR, CK, CAP, AGREE = 5, True, 5, 4, 0.98
INF = [2, 3, 4, 5, 6, 7]           # 6 informative dims -> ceiling = C(6,2) = 15 clean pairs

def sc(Xp, feats):
    r = persistence_split(Xp[:, list(feats)], min_cluster_size=MCS, mutual_reachability=MR, core_k=CK)
    return (r.score if r.valid else -1.0), (r.labels if r.valid else None)

def _vary(a, keys, p, rng):
    if rng.random() < 0.5 and len(keys) > 1:
        b = set(keys[rng.integers(len(keys))]); child = set(a) | b
        while len(child) > CAP: child.discard(list(child)[rng.integers(len(child))])
    else:
        child = set(a)
        if rng.random() < 0.5 and len(child) > 2: child.discard(list(child)[rng.integers(len(child))])
        else:
            cand = [d for d in range(p) if d not in child]
            if cand: child.add(int(cand[rng.integers(len(cand))]))
    return child

def map_elites(Xp, y, B, p, rng):
    arch = {}
    def ev(feats):
        feats = tuple(sorted(set(int(f) for f in feats)))
        if not (2 <= len(feats) <= CAP): return
        s, lab = sc(Xp, feats); cur = arch.get(feats)
        if cur is None or s > cur[0]: arch[feats] = (s, lab)
    used = 0
    while used < B:
        if len(arch) < 20 or rng.random() < 0.25:
            k = int(rng.integers(2, 4)); ev(rng.choice(p, size=k, replace=False)); used += 1; continue
        keys = list(arch); ev(_vary(keys[rng.integers(len(keys))], keys, p, rng)); used += 1
    return arch

def cvt_map_elites(Xp, y, B, p, rng, k_niches=256, n_cvt=4000):
    from sklearn.cluster import KMeans
    from scipy.spatial import cKDTree
    kk = min(k_niches, max(16, B // 4))
    samples = (rng.random((n_cvt, p)) < (3.0 / p)).astype(float)
    cent = KMeans(n_clusters=kk, n_init=1, random_state=0).fit(samples).cluster_centers_
    tree = cKDTree(cent); niche = {}
    def desc(feats):
        v = np.zeros(p); v[list(feats)] = 1.0; return v
    def ev(feats):
        feats = tuple(sorted(set(int(f) for f in feats)))
        if not (2 <= len(feats) <= CAP): return
        s, lab = sc(Xp, feats); nid = int(tree.query(desc(feats))[1]); cur = niche.get(nid)
        if cur is None or s > cur[0]: niche[nid] = (s, feats, lab)
    used = 0
    while used < B:
        if len(niche) < 20 or rng.random() < 0.25:
            k = int(rng.integers(2, 4)); ev(rng.choice(p, size=k, replace=False)); used += 1; continue
        el = [v[1] for v in niche.values()]; ev(_vary(el[rng.integers(len(el))], el, p, rng)); used += 1
    return {feats: (s, lab) for (s, feats, lab) in niche.values()}

def random_panels(Xp, y, B, p, rng):
    out = {}
    for _ in range(B):
        k = int(rng.integers(2, CAP + 1)); f = tuple(sorted(int(x) for x in rng.choice(p, size=k, replace=False)))
        if f in out: continue
        s, lab = sc(Xp, f); out[f] = (s, lab)
    return out

def greedy_panels(Xp, y, B, p, rng):
    out = {}; used = 0
    while used < B:
        sel = [int(f) for f in rng.choice(p, size=2, replace=False)]; used += 1
        s, lab = sc(Xp, sel)
        if lab is not None: out[tuple(sorted(sel))] = (s, lab)
        moved = True
        while moved and len(sel) < CAP and used < B:
            moved = False; best = None
            for f in range(p):
                if f in sel: continue
                s2, lab2 = sc(Xp, sel + [f]); used += 1
                if best is None or s2 > best[0]: best = (s2, f, lab2)
                if used >= B: break
            if best and best[0] > s + 1e-9:
                sel = sel + [best[1]]; s = best[0]; out[tuple(sorted(sel))] = (best[0], best[2]); moved = True
    return out

def count_clean(panels, y):
    return sum(1 for f, (s, lab) in panels.items()
               if len(f) == 2 and set(f) <= set(INF) and lab is not None and metrics.ari(y, lab) >= AGREE)

def main():
    args = list(sys.argv[1:]); seeds = 10; ps = [15, 40, 80]; budgets = [500, 1500, 4000]
    if "--seeds" in args: i = args.index("--seeds"); seeds = int(args[i+1]); del args[i:i+2]
    if "--ps" in args: i = args.index("--ps"); ps = [int(x) for x in args[i+1].split(",")]; del args[i:i+2]
    if "--budgets" in args: i = args.index("--budgets"); budgets = [int(x) for x in args[i+1].split(",")]; del args[i:i+2]
    print(f"ceiling = C(6,2) = 15 clean pairs; seeds={seeds}; ps={ps}; budgets={budgets}", flush=True)
    rows = []
    for p in ps:
        for B in budgets:
            for seed in range(seeds):
                X, y, _ = syn.redundant_informative(n=200, p=p, informative=INF, sep=0.6, rng=np.random.default_rng(seed))
                Xp = preprocess(X).to_numpy()
                rows.append(dict(p=p, B=B, seed=seed,
                    MAPElites=count_clean(map_elites(Xp, y, B, p, np.random.default_rng(100+seed)), y),
                    CVT=count_clean(cvt_map_elites(Xp, y, B, p, np.random.default_rng(150+seed)), y),
                    random=count_clean(random_panels(Xp, y, B, p, np.random.default_rng(200+seed)), y),
                    greedy=count_clean(greedy_panels(Xp, y, B, p, np.random.default_rng(300+seed)), y)))
            print(f"  done p={p} B={B}", flush=True)
    df = pd.DataFrame(rows)
    for path in ("results/qd.csv", "/tmp/qd.csv"):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True); df.to_csv(path, index=False); print(f"saved {path}"); break
        except PermissionError: continue
    print("\n== clean pairs recovered (mean over seeds), ceiling=15 ==")
    print(df.groupby(["p", "B"])[["MAPElites", "CVT", "random", "greedy"]].mean().round(1).to_string())
    print("\nWIN for EA family = MAPElites/CVT > random, gap growing with p. TIE = no EA edge.")

if __name__ == "__main__":
    main()
