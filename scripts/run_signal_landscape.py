"""exp-018 phase 1 -- does the fitness give a search anything to climb?  (Ryan's test)

THE QUESTION
------------
Everything we do right now is ENUMERATION: score all C(p,2) pairs, take the best. That works
only because we told the method the answer is a pair. On real data we would not know the panel
size, the space is 2^p, and enumeration is impossible. A search is only possible if the fitness
rises as a panel gets CLOSER to the true one -- not just when it is exactly right.

So, within each panel size k, sort every candidate subset into three groups by how many of the
true features it contains:

    t=0   contains neither true feature      "pure junk"
    t=1   contains exactly one               "halfway there"
    t=2   contains both                      "has the answer"

and compare their fitness distributions.

    t=1 clearly above t=0  ->  there is a gradient. A search can follow it. The method can
                               generalise to panels of unknown size.
    t=1 sitting on top of t=0 -> the landscape is a CLIFF. Partial panels look exactly like
                               junk, nothing can climb, enumeration is the only option and we
                               are capped at pairs forever.

WHY RAW TERMS, NOT THE z-SCORED HYBRID
--------------------------------------
The hybrid z-scores each term across whatever pool of subsets it is comparing. Here the pool IS
the thing under study, so z-scoring inside a group would erase the differences we are measuring,
and z-scoring across a mixed pool would make the answer depend on how we composed the pool.
We therefore report the RAW graph-cut and RAW density terms separately. Separately also matters
on its own: if one term has a gradient and the other does not, that is directly actionable.

Every comparison here is WITHIN a panel size, which sidesteps the fact that raw scores are not
comparable across sizes. The separate question "does the score peak at the RIGHT size" needs an
absolute score and is deliberately NOT answered here -- see the note at the end of the output.

SAMPLING
--------
k=1 and k=2 are enumerated. Above that we sample, and the sampling MUST be stratified: at k=3
with p=40 a uniformly drawn subset contains both true features only 0.4% of the time, so uniform
sampling would give us almost no t=2 examples. We draw `--per-group` subsets per (k, t) instead.

    python scripts/run_signal_landscape.py --quick                       # ~2 min
    python scripts/run_signal_landscape.py --seeds 10 --jobs 8           # the real run
    python scripts/run_signal_landscape.py --analyze-only

Saves incrementally to results/signal_landscape.csv.
"""
import itertools
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atomicplus.evaluation.multivariance import (
    centred_distance_matrices, multivariance, total_multivariance,
)
from atomicplus.evaluation.subspace_baselines import (
    density_term, graphcut_term, graphcut_term_dcdist,
)
from run_method_baselines import INF, KNOWN_DATASETS, load, load_structured

OUT = "results/signal_landscape.csv"
# All four scores, computed on the SAME subsets so they are directly comparable.
#   graphcut / density        -- our current two terms
#   multivariance             -- non-total M^2. Provably 0 if any feature is independent of the
#                                rest, so predicted to be a perfect cliff: superb at k=2, dead after.
#   total_multivariance       -- M-bar^2, retains all sub-multiplets, so {true pair + junk} keeps
#                                its pairwise term. Resists dilution, but ONLY on jain/moons --
#                                it is blind on circles/spiral (see exp-018 follow-up).
#   graphcut_dcdist           -- the SAME -NCut statistic, but with the kNN graph built in
#                                density-connectivity (minimax-path) space rather than Euclidean.
#                                Only the metric differs, so any change is attributable to it.
#                                Expected to trade peak strength for tolerance to junk columns.
TERMS = ["graphcut", "density", "multivariance", "total_multivariance", "graphcut_dcdist"]
# flame excluded by default: nothing recovers it, so it contributes noise rather than signal.
SHAPES = ["moons", "circles", "jain", "spiral", "gauss2"]
SIZES = [1, 2, 3, 4, 5]


def subsets_for(k, t, p, rng, per_group):
    """Subsets of size k containing exactly t of the true features. Enumerate if small."""
    true = list(INF)
    junk = [j for j in range(p) if j not in INF]
    if t > min(k, len(true)) or (k - t) > len(junk):
        return []
    all_t = list(itertools.combinations(true, t))
    n_total = len(all_t) * len(list(itertools.combinations(range(len(junk)), k - t))) \
        if k - t <= 6 else 10 ** 9
    if n_total <= per_group:                       # small enough to enumerate exactly
        return [tuple(sorted(a + b)) for a in all_t
                for b in itertools.combinations(junk, k - t)]
    out = set()
    guard = 0
    while len(out) < per_group and guard < per_group * 40:
        guard += 1
        a = all_t[rng.integers(len(all_t))]
        b = tuple(rng.choice(junk, size=k - t, replace=False)) if k - t else ()
        out.add(tuple(sorted(a + b)))
    return sorted(out)


def one_cell(name, p, seed, noise, per_group):
    X, y = (load(name, p, seed) if noise == "uniform"
            else load_structured(name, p, seed, noise))
    rng = np.random.default_rng(90_000 + seed)
    # One centred distance matrix per feature, built once and reused for every candidate subset.
    A = centred_distance_matrices(X)
    rows = []
    for k in SIZES:
        if k > p:
            continue
        for t in (0, 1, 2):
            for S in subsets_for(k, t, p, rng, per_group):
                Z = X[:, list(S)]
                g, _ = graphcut_term(Z)
                d, _ = density_term(Z)
                rows.append(dict(dataset=name, p=p, seed=seed, noise=noise, k=k, t=t,
                                 subset=str(S), graphcut=g, density=d,
                                 multivariance=multivariance(A, S),
                                 total_multivariance=total_multivariance(A, S),
                                 graphcut_dcdist=graphcut_term_dcdist(Z)[0]))
    return rows


def cohens_d(a, b):
    """Standardised gap between two groups. ~0 = indistinguishable; >0.5 = a real, usable slope."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan
    s = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                / max(len(a) + len(b) - 2, 1))
    return float((a.mean() - b.mean()) / s) if s > 1e-12 else np.nan


def analyze(df):
    pd.set_option("display.width", 220)
    print("\n" + "=" * 78)
    print("exp-018 PHASE 1 -- IS THERE A GRADIENT FOR A SEARCH TO CLIMB?")
    print("=" * 78)

    # Degenerate scores (-9.0) mark splits that could not be formed; drop rather than average in.
    for c in ("graphcut", "density", "graphcut_dcdist"):   # these use the -9.0 sentinel
        df.loc[df[c] <= -8.9, c] = np.nan

    print("\n[1] THE HEADLINE: gap between 'halfway there' (t=1) and 'pure junk' (t=0),")
    print("    in standard deviations. Near 0 = cliff, no search possible.")
    print("    >0.5 = a slope a search could actually follow.")
    rows = []
    for (nz, ds, p, k), g in df.groupby(["noise", "dataset", "p", "k"]):
        if k < 2:
            continue
        for term in TERMS:
            rows.append(dict(noise=nz, dataset=ds, p=p, k=k, term=term,
                             d_1v0=cohens_d(g[g.t == 1][term], g[g.t == 0][term]),
                             d_2v1=cohens_d(g[g.t == 2][term], g[g.t == 1][term])))
    h = pd.DataFrame(rows)
    for term in TERMS:
        print(f"\n  --- {term}: t=1 vs t=0 (the gradient that matters) ---")
        print(h[h.term == term].pivot_table(index=["noise", "dataset"], columns=["p", "k"],
                                            values="d_1v0").round(2).to_string())
    print("\n  --- for contrast, t=2 vs t=1 (the final step onto the answer) ---")
    print(h.pivot_table(index=["noise", "term"], columns="k", values="d_2v1").round(2).to_string())

    print("\n[2] SEARCH-RELEVANT VIEW: of the top 50 subsets of size k by score, what fraction")
    print("    contain at least one true feature? This is closer to what a search exploits.")
    rows = []
    for (nz, ds, p, k), g in df.groupby(["noise", "dataset", "p", "k"]):
        for term in TERMS:
            gg = g.dropna(subset=[term]).nlargest(min(50, len(g)), term)
            if len(gg):
                rows.append(dict(noise=nz, dataset=ds, p=p, k=k, term=term,
                                 frac_top50=float((gg.t >= 1).mean()),
                                 base_rate=float((g.t >= 1).mean())))
    tp = pd.DataFrame(rows)
    print(tp.pivot_table(index=["noise", "term"], columns="k",
                         values=["frac_top50", "base_rate"]).round(2).to_string())
    print("\n    NB base_rate is inflated by the stratified sampling (equal numbers per group),")
    print("    so read frac_top50 AGAINST base_rate, never on its own.")

    print("\n[3] VERDICT -- NON-CONVEX SHAPES ONLY")
    print("    gauss2 is EXCLUDED here on purpose: as a convex control its effect sizes run 4-15")
    print("    and swamp any average that includes it. Reported separately below.")
    nc = h[h.dataset != "gauss2"]
    for nz, g in nc.groupby("noise"):
        for term in TERMS:
            v = g[g.term == term]
            small = v[v.k <= 3].d_1v0.mean()
            large = v[v.k >= 4].d_1v0.mean()
            print(f"    {nz:11s} {term:9s}  mean d(t1 vs t0): small panels {small:+.2f}   "
                  f"large panels {large:+.2f}")
    cv = h[h.dataset == "gauss2"]
    if len(cv):
        print(f"\n    convex control (gauss2), for contrast: "
              f"d(t1 vs t0) = {cv.d_1v0.mean():+.1f} on average -- both terms have an enormous")
        print("    gradient on convex data, so the gradient problem is specific to non-convex.")
    print("\n    DILUTION -- d(t2 vs t1), i.e. what the exact true panel buys over a partial one.")
    print("    Watch how much it falls from k=2 (the exact pair) to k=3 (pair + one junk column):")
    print(nc.pivot_table(index=["noise", "term"], columns="k", values="d_2v1").round(2).to_string())
    print("    A large drop means the score only fires when the panel is EXACTLY right, which is")
    print("    fatal for search: any search passes through panels carrying junk.")
    print("\n    >0.5 everywhere        -> search viable; go to phase 2 (SFS / backward / random).")
    print("    strong at k=2, gone by k=4 -> method is capped at small panels; a scope statement.")
    print("    ~0 everywhere          -> cliff confirmed; enumeration only, fitness needs rework.")
    print("\n    NOT ANSWERED HERE: whether the score peaks at the CORRECT panel size. That is a")
    print("    cross-size comparison and raw scores are not comparable across sizes; it needs an")
    print("    absolute (scramble-calibrated) score. Separate experiment, do not infer it here.")


def main():
    args = list(sys.argv[1:])
    seeds, jobs, per_group, noises = 10, 1, 200, ["structured", "uniform"]
    ps = [20, 40]
    if "--analyze-only" in args:
        analyze(pd.read_csv(OUT)); return
    if "--quick" in args:
        args.remove("--quick"); seeds, ps, per_group, noises = 2, [12], 40, ["structured"]
    for flag in ("--seeds", "--jobs", "--per-group"):
        if flag in args:
            i = args.index(flag); v = int(args[i + 1]); del args[i:i + 2]
            if flag == "--seeds": seeds = v
            elif flag == "--jobs": jobs = v
            else: per_group = v
    if "--ps" in args:
        i = args.index("--ps"); ps = [int(x) for x in args[i + 1].split(",")]; del args[i:i + 2]
    if "--noise" in args:
        i = args.index("--noise"); noises = [args[i + 1]]; del args[i:i + 2]
    datasets = args if args else list(SHAPES)
    bad = [d for d in datasets if d not in KNOWN_DATASETS]
    if bad:
        print(f"ERROR: unknown dataset(s) {bad}; valid: {' '.join(KNOWN_DATASETS)}", file=sys.stderr)
        sys.exit(2)

    os.makedirs("results", exist_ok=True)
    rows, t0 = [], time.time()
    for nz in noises:
        for name in datasets:
            for p in ps:
                if jobs == 1:
                    for s in range(seeds):
                        rows.extend(one_cell(name, p, s, nz, per_group))
                else:
                    from joblib import Parallel, delayed
                    for chunk in Parallel(n_jobs=jobs)(
                            delayed(one_cell)(name, p, s, nz, per_group) for s in range(seeds)):
                        rows.extend(chunk)
                pd.DataFrame(rows).to_csv(OUT, index=False)
                print(f"  done {nz} {name} p={p}  ({time.time() - t0:.0f}s)", flush=True)
    analyze(pd.DataFrame(rows))


if __name__ == "__main__":
    main()
