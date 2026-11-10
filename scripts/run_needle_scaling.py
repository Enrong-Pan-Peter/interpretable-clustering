"""Does MORE COMPUTE recover the truth on a needle -- and does the EA beat random if so?

Nested-spheres-3D: the minimal panel is the exact triple {2,3,4} (any pair -> ARI ~0). This is a
needle with no marginal gradient. We scale the evaluation budget B and, at each B, ask: what fraction
of seeds does each method recover the triple (ARI>=0.9)? If the EA's curve tracks random's, the EA has
no search edge on needles (its recombination has no building blocks). If the EA pulls ahead, that IS
evidence for the EA -- report it.

    python scripts/run_needle_scaling.py                       # default sweep, 10 seeds
    python scripts/run_needle_scaling.py --seeds 20 --budgets 1000,4000,10000,20000
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from atomicplus import AtomicConfig, atomic, preprocess           # noqa: E402
from atomicplus import genome as gm                               # noqa: E402
from atomicplus.evaluation import metrics                         # noqa: E402
from atomicplus.evaluation.search_baselines import greedy_forward_persistence, random_search_persistence  # noqa: E402

def nested_spheres(n, p, inf, r_in, r_out, noise, rng):
    k=len(inf); half=n//2
    def shell(m,r):
        v=rng.normal(size=(m,k)); v/=np.linalg.norm(v,axis=1,keepdims=True); return v*r+rng.normal(0,noise,size=(m,k))
    core=np.vstack([shell(half,r_in),shell(n-half,r_out)]); y=np.array([0]*half+[1]*(n-half))
    X=rng.random((n,p))
    for j,d in enumerate(inf): X[:,d]=core[:,j]
    perm=rng.permutation(n); return X[perm],y[perm]

def main():
    args=list(sys.argv[1:]); seeds=10; budgets=[1000,3000,8000,20000]
    if "--seeds" in args: i=args.index("--seeds"); seeds=int(args[i+1]); del args[i:i+2]
    if "--budgets" in args: i=args.index("--budgets"); budgets=[int(x) for x in args[i+1].split(",")]; del args[i:i+2]
    inf=[2,3,4]; p=15; n=240
    base=dict(fitness_mode="persistence",k_tilde=5,min_cluster_size=5,crossover_mode="set_based",
              mutation_mode="asymmetric",archive_rebuild_every=25,pair_seed_init=False)
    rows=[]
    for B in budgets:
        pop=50; lam=50; n_gen=max(1,(B-pop)//lam)
        for seed in range(seeds):
            X,y=nested_spheres(n,p,inf,1.0,3.0,0.06,np.random.default_rng(seed)); Xp=preprocess(pd.DataFrame(X)).to_numpy()
            ea=atomic(Xp,AtomicConfig(pop_size=pop,mu=pop,lam=lam,n_gen=n_gen,**base),np.random.default_rng(seed)).best()
            ea_ari=metrics.ari(y,ea.quality.labels)
            _,_,rl=random_search_persistence(Xp,n_evals=B,min_cluster_size=5,rng=np.random.default_rng(seed))
            r_ari=metrics.ari(y,rl)
            _,_,gl=greedy_forward_persistence(Xp,min_cluster_size=5); g_ari=metrics.ari(y,gl)
            rows.append(dict(B=B,seed=seed,ea=ea_ari,rand=r_ari,greedy=g_ari))
        print(f"  done B={B}", flush=True)
    df=pd.DataFrame(rows)
    for path in ("results/needle_scaling.csv","/tmp/needle_scaling.csv"):
        try: os.makedirs(os.path.dirname(path) or ".",exist_ok=True); df.to_csv(path,index=False); print(f"saved {path}"); break
        except PermissionError: continue
    print("\n== recovery rate (fraction of seeds with ARI>=0.9) vs budget ==")
    rate=(df.assign(EA=df.ea>=0.9, random=df.rand>=0.9, greedy=df.greedy>=0.9)
            .groupby("B")[["EA","random","greedy"]].mean())
    print(rate.round(2).to_string())
    print("\nRead: if EA ~ random at every budget -> no EA edge on needles. If EA > random -> evidence FOR the EA.")

if __name__=="__main__":
    main()
