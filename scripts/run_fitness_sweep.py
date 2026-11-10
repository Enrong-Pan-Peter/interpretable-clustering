"""Overnight generality sweep for the graph-cut selection finding.

Two questions a small test cannot answer:
  (1) does graph-cut selection hold across MANY cluster shapes, not just the four we tried?
  (2) does it survive as dimensionality p grows (more noise features = harder selection)?

For each (shape, p, seed) we rank all feature pairs by each fitness and record how often the TRUE
pair is #1 (selection), plus recovery ARI of the graph-cut-selected pair under a spectral split and
under an HDBSCAN split (does a stronger split lift end-to-end?). Results saved incrementally.

    python scripts/run_fitness_sweep.py --seeds 20 --ps 12,20,40,80 moons circles jain flame spiral gauss2
"""
import os, sys, itertools, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.neighbors import kneighbors_graph
from sklearn.cluster import SpectralClustering, HDBSCAN
from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics
from atomicplus.persistence import persistence_split, core_distances
DATA2D = os.path.join(os.path.dirname(__file__), "..", "2d_data"); INF=[3,8]
FIT = ["gap_ratio","density","graphcut","hyb_gcut_dens"]

def load(name, p, seed):
    rng = np.random.default_rng(seed)
    if name in ("moons","circles"):
        g = syn.moons_subspace if name=="moons" else syn.circles_subspace
        X,y,_ = g(n=260,p=p,informative=INF,rng=rng); return preprocess(X).to_numpy(), y
    if name == "gauss2":                                   # convex control: answer should be easy
        X,y,_ = syn.two_cluster_subspace(n=260,p=p,informative=INF,sep=0.6,std=0.05,rng=rng)
        return preprocess(X).to_numpy(), y
    a = np.loadtxt(os.path.join(DATA2D,f"{name}.txt"),skiprows=1); xy=a[:,:2].astype(float); yy=a[:,2].astype(int)
    xy=(xy-xy.min(0))/(np.ptp(xy,0)+1e-12); X=rng.random((len(xy),p)); X[:,INF[0]],X[:,INF[1]]=xy[:,0],xy[:,1]
    return preprocess(pd.DataFrame(X)).to_numpy(), yy

def _mr(Z): c=core_distances(Z,5); D=squareform(pdist(Z)); M=np.maximum(D,np.maximum.outer(c,c)); np.fill_diagonal(M,0); return M
def base_scores(Z):
    r=persistence_split(Z,min_cluster_size=5,mutual_reachability=True,core_k=5,normalize="none"); lab=r.labels
    e_cut=r.cut_weight; gr=r.raw_gap; e_next=max(e_cut-gr,0.0); gap_ratio=(e_cut/e_next) if e_next>0 else (1.0+e_cut)
    density=-9.0
    if lab is not None and (lab==0).sum()>=2 and (lab==1).sum()>=2:
        M=_mr(Z); a=np.flatnonzero(lab==0); b=np.flatnonzero(lab==1); sep=M[np.ix_(a,b)].min()
        def me(idx): t=minimum_spanning_tree(csr_matrix(M[np.ix_(idx,idx)])); return t.data.max() if t.nnz else 0.0
        density=(sep-max(me(a),me(b)))/max(sep,me(a),me(b),1e-9)
    return gap_ratio, density, lab
def graphcut(Z,k=10):
    A=kneighbors_graph(Z,n_neighbors=k,mode="connectivity",include_self=False); A=0.5*(A+A.T).toarray()
    try: lab=SpectralClustering(n_clusters=2,affinity="precomputed",random_state=0).fit_predict(A)
    except Exception: return -9.0,None
    d=A.sum(1); a=lab==0; b=lab==1
    if a.sum()<2 or b.sum()<2: return -9.0,lab
    cut=A[np.ix_(a,b)].sum(); return -(cut/max(d[a].sum(),1e-9)+cut/max(d[b].sum(),1e-9)),lab

def main():
    args=list(sys.argv[1:]); seeds=20; ps=[12,20,40,80]
    if "--seeds" in args: i=args.index("--seeds"); seeds=int(args[i+1]); del args[i:i+2]
    if "--ps" in args: i=args.index("--ps"); ps=[int(x) for x in args[i+1].split(",")]; del args[i:i+2]
    datasets=args if args else ["moons","circles","jain","flame","spiral","gauss2"]
    outp="results/fitness_sweep.csv"; os.makedirs("results",exist_ok=True); rows=[]
    for name in datasets:
        for p in ps:
            for seed in range(seeds):
                Xp,y=load(name,p,seed); pairs=list(itertools.combinations(range(p),2))
                gr=[]; de=[]; gc=[]; plab={}; glab={}
                for pr in pairs:
                    Z=Xp[:,list(pr)]; a,b,pl=base_scores(Z); g,gl=graphcut(Z)
                    gr.append(a); de.append(b); gc.append(g); plab[pr]=pl; glab[pr]=gl
                def z(v): v=np.array(v,float); s=v.std(); return (v-v.mean())/(s if s>1e-9 else 1.0)
                comb={"gap_ratio":np.array(gr),"density":np.array(de),"graphcut":np.array(gc),
                      "hyb_gcut_dens":z(gc)+z(de)}
                ti=pairs.index(tuple(INF)); row=dict(dataset=name,p=p,seed=seed)
                for f in FIT:
                    order=np.argsort(-comb[f]); row[f+"_r1"]=int(order[0]==ti)
                # recovery: graphcut-selected pair, spectral vs HDBSCAN split
                gpair=pairs[int(np.argsort(-comb["graphcut"])[0])]; Zg=Xp[:,list(gpair)]
                row["gc_spectral_ari"]=metrics.ari(y,glab[gpair]) if glab[gpair] is not None else 0.0
                hl=HDBSCAN(min_cluster_size=10, copy=True).fit_predict(Zg); row["gc_hdbscan_ari"]=metrics.ari(y,hl)
                rows.append(row)
            pd.DataFrame(rows).to_csv(outp,index=False)          # incremental save
            print(f"  done {name} p={p}",flush=True)
    df=pd.DataFrame(rows)
    print("\n== rank-1 selection rate by shape x p (graphcut is the one to watch) ==")
    for f in FIT:
        print(f"\n[{f}]"); print(df.pivot_table(index="dataset",columns="p",values=f+"_r1",aggfunc="mean").round(2).to_string())
    print("\n== recovery ARI of graph-cut-selected pair: spectral split vs HDBSCAN split ==")
    print(df.groupby(["dataset","p"])[["gc_spectral_ari","gc_hdbscan_ari"]].mean().round(2).to_string())

if __name__=="__main__": main()
