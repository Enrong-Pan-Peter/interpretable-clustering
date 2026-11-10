"""Overnight: EA vs CVT-MAP-Elites vs greedy vs random, ALL optimizing the NEW hybrid fitness
(graph cut + density). Two questions:
  (1) with a good signal, do the evolutionary methods now MATCH or BEAT greedy/random?
  (2) does CVT-MAP-Elites beat plain EA? (If the signal is informative, illumination should help.)
All methods get the SAME evaluation budget. Metric: recovery ARI (HDBSCAN split of the selected
subset) and whether the true pair was found. Saves incrementally.
    python scripts/run_ea_newfit.py --seeds 20 --p 20 --budget 250 moons circles jain flame spiral gauss2
"""
import os, sys, itertools, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.neighbors import kneighbors_graph
from sklearn.cluster import SpectralClustering, HDBSCAN, KMeans
from scipy.spatial import cKDTree
from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.evaluation import metrics
from atomicplus.persistence import core_distances, persistence_split
DATA2D=os.path.join(os.path.dirname(__file__),"..","2d_data"); INF=[3,8]; CAP=4
def load(name,p,seed):
    rng=np.random.default_rng(seed)
    if name in("moons","circles"):
        g=syn.moons_subspace if name=="moons" else syn.circles_subspace
        X,y,_=g(n=260,p=p,informative=INF,rng=rng); return preprocess(X).to_numpy(),y
    if name=="gauss2":
        X,y,_=syn.two_cluster_subspace(n=260,p=p,informative=INF,sep=0.6,std=0.05,rng=rng); return preprocess(X).to_numpy(),y
    a=np.loadtxt(os.path.join(DATA2D,f"{name}.txt"),skiprows=1); xy=a[:,:2].astype(float); yy=a[:,2].astype(int)
    xy=(xy-xy.min(0))/(np.ptp(xy,0)+1e-12); X=rng.random((len(xy),p)); X[:,INF[0]],X[:,INF[1]]=xy[:,0],xy[:,1]
    return preprocess(pd.DataFrame(X)).to_numpy(),yy
def _gc(Z,k=10):
    A=kneighbors_graph(Z,n_neighbors=min(k,len(Z)-1),mode="connectivity",include_self=False); A=0.5*(A+A.T).toarray()
    try: lab=SpectralClustering(n_clusters=2,affinity="precomputed",random_state=0).fit_predict(A)
    except Exception: return -9.0
    d=A.sum(1); a=lab==0; b=lab==1
    if a.sum()<2 or b.sum()<2: return -9.0
    cut=A[np.ix_(a,b)].sum(); return -(cut/max(d[a].sum(),1e-9)+cut/max(d[b].sum(),1e-9))
def _dn(Z):
    r=persistence_split(Z,min_cluster_size=5,mutual_reachability=True,core_k=5,normalize="none"); lab=r.labels
    if lab is None or (lab==0).sum()<2 or (lab==1).sum()<2: return -9.0
    c=core_distances(Z,5); D=squareform(pdist(Z)); M=np.maximum(D,np.maximum.outer(c,c)); np.fill_diagonal(M,0)
    a=np.flatnonzero(lab==0); b=np.flatnonzero(lab==1); sep=M[np.ix_(a,b)].min()
    def me(i): t=minimum_spanning_tree(csr_matrix(M[np.ix_(i,i)])); return t.data.max() if t.nnz else 0.0
    return (sep-max(me(a),me(b)))/max(sep,me(a),me(b),1e-9)
def make_fit(Xp):
    cache={}
    def f(feats):
        key=tuple(sorted(int(x) for x in feats))
        if not(1<=len(key)<=CAP): return -9.0
        if key in cache: return cache[key]
        Z=Xp[:,list(key)]; v=_gc(Z)+_dn(Z); cache[key]=v; return v
    return f
def recover(Xp,feats,y): return metrics.ari(y,HDBSCAN(min_cluster_size=10, copy=True).fit_predict(Xp[:,list(feats)]))

def m_random(fit,p,B,rng):
    best=(-9,(0,1))
    for _ in range(B):
        k=int(rng.integers(2,CAP+1)); s=tuple(sorted(rng.choice(p,k,replace=False))); v=fit(s)
        if v>best[0]: best=(v,s)
    return best[1]
def m_greedy(fit,p,B,rng):                            # STANDARD Sequential Forward Selection (fair)
    used=0; sc=[]
    for f in range(p):                                # step 1: best single feature (1-D cluster)
        if used>=B: break
        sc.append((fit((f,)),f)); used+=1
    sel=[max(sc)[1]]; v=fit(tuple(sel)); best=(v,tuple(sorted(sel)))
    while len(sel)<CAP and used<B:                     # then add one feature at a time by improvement
        cand=None
        for d in range(p):
            if d in sel: continue
            vv=fit(tuple(sorted(sel+[d]))); used+=1
            if cand is None or vv>cand[0]: cand=(vv,d)
            if used>=B: break
        if cand and cand[0]>v+1e-9: sel=sel+[cand[1]]; v=cand[0]; best=(v,tuple(sorted(sel)))
        else: break
    return best[1]
def m_enum2(fit,p,B,rng):                             # CEILING ONLY: exhaustive over pairs (assumes size-2)
    return max(((fit(pr),pr) for pr in itertools.combinations(range(p),2)),key=lambda z:z[0])[1]
def _vary(a,keys,p,rng):
    if rng.random()<0.5 and len(keys)>1:
        b=set(keys[rng.integers(len(keys))]); c=set(a)|b
        while len(c)>CAP: c.discard(list(c)[rng.integers(len(c))])
    else:
        c=set(a)
        if rng.random()<0.5 and len(c)>2: c.discard(list(c)[rng.integers(len(c))])
        else:
            cand=[d for d in range(p) if d not in c]
            if cand: c.add(int(cand[rng.integers(len(cand))]))
    return tuple(sorted(c)) if len(c)>=2 else tuple(sorted(rng.choice(p,2,replace=False)))
def m_ea(fit,p,B,rng,pop=20):
    S=[tuple(sorted(rng.choice(p,2,replace=False))) for _ in range(pop)]; sc=[(fit(s),s) for s in S]; used=pop
    while used<B:
        kids=[]
        for _ in range(pop):
            if used+len(kids)>=B: break
            a=sc[rng.integers(len(sc))][1]; kids.append(_vary(a,[t for _,t in sc],p,rng))
        sc=sorted(sc+[(fit(k),k) for k in kids],key=lambda z:(z[0],-len(z[1])),reverse=True)[:pop]; used+=len(kids)
    return max(sc,key=lambda z:z[0])[1]
def m_cvt(fit,p,B,rng,kn=64):
    kk=min(kn,max(12,B//4)); samp=(rng.random((2000,p))<(3.0/p)).astype(float)
    cent=KMeans(n_clusters=kk,n_init=1,random_state=0).fit(samp).cluster_centers_; tree=cKDTree(cent); niche={}
    def desc(f): v=np.zeros(p); v[list(f)]=1.0; return v
    def add(f):
        f=tuple(sorted(set(int(x) for x in f)))
        if not(2<=len(f)<=CAP): return
        v=fit(f); nid=int(tree.query(desc(f))[1]); cur=niche.get(nid)
        if cur is None or v>cur[0]: niche[nid]=(v,f)
    used=0
    while used<B:
        if len(niche)<12 or rng.random()<0.25:
            k=int(rng.integers(2,4)); add(rng.choice(p,k,replace=False)); used+=1; continue
        el=[v[1] for v in niche.values()]; add(_vary(el[rng.integers(len(el))],el,p,rng)); used+=1
    return max(niche.values(),key=lambda z:z[0])[1] if niche else (0,1)
METHODS={"random":m_random,"greedy":m_greedy,"EA":m_ea,"CVT":m_cvt,"enum2_ceil":m_enum2}
def main():
    args=list(sys.argv[1:]); seeds=20; ps=[20]; B=400
    if "--seeds" in args: i=args.index("--seeds"); seeds=int(args[i+1]); del args[i:i+2]
    if "--ps" in args: i=args.index("--ps"); ps=[int(x) for x in args[i+1].split(",")]; del args[i:i+2]
    if "--budget" in args: i=args.index("--budget"); B=int(args[i+1]); del args[i:i+2]
    datasets=args if args else ["moons","circles","jain","flame","spiral","gauss2"]
    print(f"ps={ps} budget={B} seeds={seeds}",flush=True); rows=[]; os.makedirs("results",exist_ok=True)
    for name in datasets:
        for p in ps:
            for seed in range(seeds):
                Xp,y=load(name,p,seed); row=dict(dataset=name,p=p,seed=seed)
                for mn,mf in METHODS.items():
                    fit=make_fit(Xp); sel=mf(fit,p,B,np.random.default_rng(seed*17+hash(mn)%1000))
                    row[mn+"_ari"]=recover(Xp,sel,y); row[mn+"_found"]=int(set(INF)<=set(sel) and len(sel)<=3)
                rows.append(row)
            pd.DataFrame(rows).to_csv("results/ea_newfit.csv",index=False); print(f"  done {name} p={p}",flush=True)
    df=pd.DataFrame(rows)
    print("\n== recovery ARI by shape x p (fixed budget; watch random fade and CVT/EA hold as p grows) ==")
    for m in METHODS:
        print(f"\n[{m}]"); print(df.pivot_table(index="dataset",columns="p",values=m+"_ari",aggfunc="mean").round(2).to_string())
if __name__=="__main__": main()
