"""The 'why EA?' keystone: alternative-panel recovery under EQUAL budget (fair version).

Object of interest (defined a priori): the set of MINIMAL, INTERPRETABLE equivalent panels =
distinct feature PAIRS drawn from the truly-informative dims whose persistence split recovers the
true clustering (ARI >= agree). On redundant data each informative dim carries the split, so many
such pairs exist and all induce the same partition -- the diversity greedy cannot enumerate.

FAIR rules a reviewer demands, all applied identically:
  * equal evaluation budget B = pop + n_gen*lam for EA, random, and multi-start greedy;
  * same validity + counting rule (valid informative pair) for every method;
  * EA runs with pair_seed_init=OFF, so we measure the NSLC SEARCH, not brute pair-enumeration.
    (Pair-seed as-shipped trivially evaluates all pairs; that's enumeration, not evolution -- so it
     would be dishonest to credit 'the EA' for it. We note it separately, analytically.)

    python scripts/run_diversity.py --quick
    python scripts/run_diversity.py --seeds 15          # full (run on your box)
"""
import os, sys, itertools
import numpy as np, pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from atomicplus import AtomicConfig, atomic, preprocess           # noqa: E402
from atomicplus import genome as gm                               # noqa: E402
from atomicplus.datasets import synthetic as syn                  # noqa: E402
from atomicplus.evaluation import metrics                         # noqa: E402
from atomicplus.persistence import persistence_split              # noqa: E402

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 30)
MCS, MR, CK = 5, True, 5
CAP = 4
AGREE = 0.98

def split_labels(X, feats):
    r = persistence_split(X[:, list(feats)], min_cluster_size=MCS, mutual_reachability=MR, core_k=CK)
    return (r.labels if r.valid else None)

def is_valid(X, y, feats):
    lab = split_labels(X, feats)
    return lab is not None and metrics.ari(y, lab) >= AGREE

def ceiling_pairs(X, y, inf):
    return {tuple(sorted(pr)) for pr in itertools.combinations(inf, 2) if is_valid(X, y, pr)}

def ea_valid_panels(res, X, y):
    out = set()
    for g, ev in zip(res.archive.genomes, res.archive.evals):
        feats = tuple(sorted(int(i) for i in gm.selected_indices(g)))
        if 2 <= len(feats) <= CAP and ev.labels is not None and ev.n_components == 2 \
           and metrics.ari(y, ev.labels) >= AGREE:
            out.add(feats)
    return out

def random_valid_panels(X, y, B, p, rng):
    out = set()
    for _ in range(B):
        k = int(rng.integers(2, CAP + 1))
        feats = tuple(sorted(int(f) for f in rng.choice(p, size=min(k, p), replace=False)))
        if feats not in out and is_valid(X, y, feats):
            out.add(feats)
    return out

def greedy_valid_panels(X, y, B, p, rng):
    out = set(); used = 0
    while used < B:
        sel = [int(f) for f in rng.choice(p, size=2, replace=False)]; used += 1
        if is_valid(X, y, sel): out.add(tuple(sorted(sel)))
        # then hill-climb by persistence (its native objective), recording valid panels en route
        r = persistence_split(X[:, sel], min_cluster_size=MCS, mutual_reachability=MR, core_k=CK)
        sc = r.score if r.valid else -1.0; moved = True
        while moved and len(sel) < CAP and used < B:
            moved = False; best = None
            for f in range(p):
                if f in sel: continue
                rr = persistence_split(X[:, sel + [f]], min_cluster_size=MCS, mutual_reachability=MR, core_k=CK)
                used += 1; s2 = rr.score if rr.valid else -1.0
                if best is None or s2 > best[0]: best = (s2, f)
                if used >= B: break
            if best and best[0] > sc + 1e-9:
                sel = sel + [best[1]]; sc = best[0]; moved = True
                if is_valid(X, y, sel): out.add(tuple(sorted(sel)))
    return out

def pairs_only(panels, inf):   # minimal, clean: informative pairs (ceiling-comparable)
    return {f for f in panels if len(f) == 2 and set(f) <= set(inf)}
def clean_any(panels, inf):    # generous: any-size subset of informative dims
    return {f for f in panels if set(f) <= set(inf)}

DSETS = {"redund4": ([2, 3, 4, 5], 15), "redund6": ([2, 3, 4, 5, 6, 7], 15)}

def main():
    args = list(sys.argv[1:]); quick = "--quick" in args; big = "--big" in args
    if quick: args.remove("--quick")
    if big: args.remove("--big")
    seeds = 2 if quick else 15
    if "--seeds" in args: i = args.index("--seeds"); seeds = int(args[i+1]); del args[i:i+2]
    base = dict(fitness_mode="persistence", k_tilde=5, min_cluster_size=MCS,
                crossover_mode="set_based", mutation_mode="asymmetric",
                archive_rebuild_every=25, pair_seed_init=False)   # OFF: measure the search
    if quick:   cfg = AtomicConfig(pop_size=30, mu=30, lam=18, n_gen=10, **base)
    elif big:   cfg = AtomicConfig(pop_size=100, mu=100, lam=60, n_gen=100, **base)  # paper-spec budget
    else:       cfg = AtomicConfig(pop_size=60, mu=60, lam=36, n_gen=25, **base)
    B = cfg.pop_size + cfg.n_gen * cfg.lam
    print(f"equal budget B={B}  seeds={seeds}  cap={CAP}  agree={AGREE}  (EA pair_seed OFF)")
    rows = []
    for name, (inf, p) in DSETS.items():
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            X, y, _ = syn.redundant_informative(n=200, p=p, informative=inf, sep=0.6, rng=rng)
            Xp = preprocess(X).to_numpy()
            ceil = ceiling_pairs(Xp, y, inf)
            ea = ea_valid_panels(atomic(Xp, cfg, np.random.default_rng(seed)), Xp, y)
            rd = random_valid_panels(Xp, y, B, p, np.random.default_rng(1000 + seed))
            gr = greedy_valid_panels(Xp, y, B, p, np.random.default_rng(2000 + seed))
            rows.append(dict(dataset=name, seed=seed, ceiling=len(ceil),
                ea_pairs=len(pairs_only(ea, inf)), rand_pairs=len(pairs_only(rd, inf)),
                greedy_pairs=len(pairs_only(gr, inf)),
                ea_clean=len(clean_any(ea, inf)), rand_clean=len(clean_any(rd, inf)),
                greedy_clean=len(clean_any(gr, inf)),
                ea_any=len(ea), rand_any=len(rd), greedy_any=len(gr)))
        print(f"  done {name}")
    df = pd.DataFrame(rows)
    for path in ("results/diversity.csv", "/tmp/diversity.csv"):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            df.to_csv(path, index=False); print(f"saved {path}"); break
        except PermissionError: continue
    g = df.groupby("dataset")
    print("\n== MINIMAL clean panels (informative PAIRS) recovered, mean over seeds [ceiling-bounded] ==")
    print(g[["ceiling", "ea_pairs", "rand_pairs", "greedy_pairs"]].mean().round(1).to_string())
    print("\n== generous: any-size subset of informative dims recovered ==")
    print(g[["ea_clean", "rand_clean", "greedy_clean"]].mean().round(1).to_string())
    print("\n== transparency: total valid panels incl. noise-padded (random blankets this) ==")
    print(g[["ea_any", "rand_any", "greedy_any"]].mean().round(1).to_string())

if __name__ == "__main__":
    main()
