"""Compare fitness signals for SELECTING the informative subspace (Ryan's ideas).

Signals scored for every feature pair; we report how often each ranks the TRUE pair #1
(rank-1 rate, the key selection metric) and the recovery ARI of the top-ranked pair.
  gap_ratio   current fitness, e1/e2
  gap_raw     e1 - e2 (original design)
  median_gap  gap divided by the median edge (uses more of the edge distribution)
  cutwithin   between-cluster gap over the median within-cluster edge (uses more edges)
  density     DBCV-style density validity of the split
  graphcut    normalized cut on the kNN graph, not the tree (Ryan's graph idea)
  hyb_gap_dens, hyb_gcut_dens   z-score combinations (Ryan's hybrid idea)

    python scripts/run_fitness.py --seeds 30 moons circles jain flame
"""
import os, sys, itertools, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.neighbors import kneighbors_graph
from sklearn.cluster import SpectralClustering
from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics
from atomicplus.persistence import persistence_split, core_distances
DATA2D = os.path.join(os.path.dirname(__file__), "..", "2d_data"); INF=[3,8]; P=12
FIT = ["gap_ratio","gap_raw","median_gap","cutwithin","density","graphcut","hyb_gap_dens","hyb_gcut_dens"]

def load(name, seed):
    rng = np.random.default_rng(seed)
    if name in ("moons","circles"):
        g = syn.moons_subspace if name=="moons" else syn.circles_subspace
        X,y,_ = g(n=240,p=P,informative=INF,rng=rng); return preprocess(X).to_numpy(), y
    a = np.loadtxt(os.path.join(DATA2D,f"{name}.txt"),skiprows=1); xy=a[:,:2].astype(float); yy=a[:,2].astype(int)
    xy=(xy-xy.min(0))/(np.ptp(xy,0)+1e-12); X=rng.random((len(xy),P)); X[:,INF[0]],X[:,INF[1]]=xy[:,0],xy[:,1]
    return preprocess(pd.DataFrame(X)).to_numpy(), yy

def _mr(Z): c=core_distances(Z,5); D=squareform(pdist(Z)); M=np.maximum(D,np.maximum.outer(c,c)); np.fill_diagonal(M,0); return M
def base_scores(Z):
    r=persistence_split(Z,min_cluster_size=5,mutual_reachability=True,core_k=5,normalize="none")
    lab=r.labels; e_cut=r.cut_weight; gap_raw=r.raw_gap; e_next=max(e_cut-gap_raw,0.0)
    gap_ratio=(e_cut/e_next) if e_next>0 else (1.0+e_cut)
    M=_mr(Z); mstw=minimum_spanning_tree(csr_matrix(M)).tocoo().data
    med=float(np.median(mstw)) if len(mstw) else 1.0
    median_gap=gap_raw/med if med>0 else gap_raw
    density=-9.0; cutwithin=-9.0
    if lab is not None and (lab==0).sum()>=2 and (lab==1).sum()>=2:
        a=np.flatnonzero(lab==0); b=np.flatnonzero(lab==1); sep=M[np.ix_(a,b)].min()
        def me(idx): t=minimum_spanning_tree(csr_matrix(M[np.ix_(idx,idx)])); return t.data.max() if t.nnz else 0.0
        spa=max(me(a),me(b)); density=(sep-spa)/max(sep,spa,1e-9)
        w=np.concatenate([M[np.ix_(a,a)][np.triu_indices(len(a),1)],M[np.ix_(b,b)][np.triu_indices(len(b),1)]])
        cutwithin=sep/(float(np.median(w))+1e-9)
    return dict(gap_ratio=gap_ratio,gap_raw=gap_raw,median_gap=median_gap,cutwithin=cutwithin,density=density), lab
def graphcut(Z,k=10):
    A=kneighbors_graph(Z,n_neighbors=k,mode="connectivity",include_self=False); A=0.5*(A+A.T).toarray()
    try: lab=SpectralClustering(n_clusters=2,affinity="precomputed",random_state=0).fit_predict(A)
    except Exception: return -9.0,None
    d=A.sum(1); a=lab==0; b=lab==1
    if a.sum()<2 or b.sum()<2: return -9.0,lab
    cut=A[np.ix_(a,b)].sum(); return -(cut/max(d[a].sum(),1e-9)+cut/max(d[b].sum(),1e-9)),lab

def main():
    args=list(sys.argv[1:]); seeds=30
    if "--seeds" in args: i=args.index("--seeds"); seeds=int(args[i+1]); del args[i:i+2]
    datasets=args if args else ["moons","circles","jain","flame"]
    rows=[]
    for name in datasets:
        for seed in range(seeds):
            Xp,y=load(name,seed); pairs=list(itertools.combinations(range(P),2))
            raw={k:[] for k in ["gap_ratio","gap_raw","median_gap","cutwithin","density","graphcut"]}
            plab={}; glab={}
            for pr in pairs:
                Z=Xp[:,list(pr)]; d,pl=base_scores(Z); gcs,gl=graphcut(Z)
                for k in d: raw[k].append(d[k])
                raw["graphcut"].append(gcs); plab[pr]=pl; glab[pr]=gl
            def z(a): a=np.array(a,float); s=a.std(); return (a-a.mean())/(s if s>1e-9 else 1.0)
            Zc={k:z(raw[k]) for k in raw}
            comb={**{k:np.array(raw[k],float) for k in raw},
                  "hyb_gap_dens":Zc["gap_ratio"]+Zc["density"], "hyb_gcut_dens":Zc["graphcut"]+Zc["density"]}
            ti=pairs.index(tuple(INF)); row=dict(dataset=name,seed=seed)
            for f in FIT:
                order=np.argsort(-comb[f]); amax=pairs[int(order[0])]
                lab=glab[amax] if f in ("graphcut","hyb_gcut_dens") else plab[amax]
                row[f+"_r1"]=int(order[0]==ti); row[f+"_ari"]=metrics.ari(y,lab) if lab is not None else 0.0
            rows.append(row)
        print(f"  done {name}",flush=True)
    df=pd.DataFrame(rows)
    for path in ("results/fitness.csv","/tmp/fitness.csv"):
        try: os.makedirs(os.path.dirname(path) or ".",exist_ok=True); df.to_csv(path,index=False); print("saved",path); break
        except PermissionError: continue
    print("\n== rank-1 rate: how often each fitness ranks the TRUE pair #1 (higher = better selection) ==")
    print(df.groupby("dataset")[[f+"_r1" for f in FIT]].mean().round(2).rename(columns=lambda c:c[:-3]).to_string())
    print("\n== recovery ARI of the top-ranked pair ==")
    print(df.groupby("dataset")[[f+"_ari" for f in FIT]].mean().round(2).rename(columns=lambda c:c[:-4]).to_string())
if __name__=="__main__": main()
