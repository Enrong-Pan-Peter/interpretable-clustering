"""exp-028 -- does a multi-objective search find better panels than greedy growth?

THE QUESTION, AND WHY IT IS NOT THE ONE I FIRST THOUGHT
-------------------------------------------------------
exp-024 through exp-027 left one thing unresolved: the tree grows a panel until a stopping rule says
halt, and nothing in that rule prefers a SMALL panel when a large one scores the same. On Levine the
published two-marker gate and a four-marker panel cluster the cells equally well (spectral ARI 0.934
against 0.947), so no scalar score can choose between them without an arbitrary weight. Two
objectives -- score and panel size -- is the standard way out, and NSGA-II is the standard method.

I initially argued this was ceremony, on the grounds that the Pareto front at p=32 is just the best
panel at each size and is therefore enumerable. That was wrong, and the error matters. Enumerating
the SIZES is trivial; finding the BEST PANEL OF EACH SIZE is a combinatorial search:

    size 2      496 panels    enumerable in minutes
    size 3    4,960 panels    enumerable, but hours at full settings
    size 4   35,960 panels    not enumerable here
    size 5  201,376 panels    no

So the front reported in exp-027 (0.99 at size 2, 3.41 at size 3, 4.85 at size 4) is what GREEDY
GROWTH found at each cap, not the best that exists. Whether a population-based search finds better
panels at the same sizes is an open, answerable question, and this script answers it.

THREE METHODS, ONE SCORE, ONE DATASET
-------------------------------------
  EXHAUSTIVE at size 2   all 496 pairs. Ground truth for one point on the front -- the only size
                         where "did the search find the best panel?" can be checked rather than
                         assumed. Both other methods are measured against it.
  GREEDY per size        what the tree does today: seed on the best raw pair, grow with the combined
                         calibrated stopping rule, capped at 2, 3, 4, 5 in turn.
  NSGA-II                population of bit-strings over the 32 markers, reusing this repo's existing
                         `fast_nondominated_sort` / `crowding_distance` / `nsga2_select` -- the same
                         implementation the original ATOMIC used, so only the OBJECTIVES differ.

OBJECTIVES, BOTH MAXIMISED (the convention `selection.py` expects)
------------------------------------------------------------------
  1. the combined shuffle-calibrated score, AVERAGED over the two terms. It must be the calibrated
     one: the original hybrid fitness standardises each term against other candidates OF THE SAME
     SIZE, which makes it a within-size ranking that cannot compare a 2-marker panel to a 4-marker
     one. In a problem whose second axis IS size, that would be measured on a different scale at
     every point along the front.
  2. minus the panel size.

THREE IMPLEMENTATION CHOICES THAT WOULD OTHERWISE QUIETLY BIAS THE RESULT
-------------------------------------------------------------------------
1. UNIFORM CROSSOVER, not the OR-crossover the original ATOMIC used. OR makes both children the
   union of their parents, so panels only ever grow. With size as an explicit objective that biases
   precisely the quantity being measured.
2. AN EVALUATION CACHE keyed on the bit-string. Populations revisit panels constantly and every
   evaluation costs two terms times B+1 shuffles. `genome.genome_key` exists for this.
3. EVALUATIONS SPENT IS REPORTED PER METHOD. Greedy is far cheaper than a population search, so
   "NSGA-II found something better" means little without the price beside it. Omitting that column
   would flatter the expensive method.

WHAT WOULD COUNT AS WHICH RESULT
--------------------------------
  NSGA-II beats greedy at size 3+   a finding; the tree's search is leaving panels on the table
  NSGA-II matches greedy            the validation result; greedy already reaches the front, which
                                    justifies the cheap method and is worth stating plainly
  either misses the exhaustive
  optimum at size 2                 that method is not searching well, and the size-3+ numbers from
                                    it should be read as lower bounds rather than as the front

Labels are used ONLY afterwards, to describe what each method returned. No search sees them.

    python scripts/run_nsga2.py --quick --jobs 4          # tiny, a few minutes
    python scripts/run_nsga2.py --jobs 8                  # the real run
    python scripts/run_nsga2.py --analyze-only results/nsga2_n400_B10_s0.csv
"""
from __future__ import annotations

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

from atomicplus import genome as gm
from atomicplus import operators as ops
from atomicplus.evaluation.stopping import grow_from_pairs_stop, z_reps
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term
from atomicplus.selection import nsga2_select
from run_levine_tree import (LEVINE_POPULATIONS, load_capped, majority_sides, name_boundary,
                             present, purity)

TERMS = [graphcut_term, density_term]


# ------------------------------------------------------------------------------------------------
# Shared, cached fitness -- every method pays the same price per panel
# ------------------------------------------------------------------------------------------------

class Fitness:
    """Combined calibrated score with memoisation, so the three methods are compared on equal terms.

    `n_evals` counts DISTINCT panels scored, which is the honest cost measure: a method that
    revisits the same panel a hundred times has not done a hundred units of work.
    """

    def __init__(self, X, B=10, shared_seed=0):
        self.X, self.B, self.seed = X, B, shared_seed
        self.cache, self.n_evals = {}, 0

    def __call__(self, cols) -> float:
        key = tuple(sorted(int(c) for c in cols))
        if key in self.cache:
            return self.cache[key]
        v = float(z_reps(TERMS, self.X, key, B=self.B, shared_seed=self.seed, n_reps=1)[0])
        if not np.isfinite(v):
            v = -1e9                      # unscorable panels are dominated, never selected
        self.cache[key] = v
        self.n_evals += 1
        return v


# ------------------------------------------------------------------------------------------------
# Method A: exhaustive at size 2 -- the only place the true optimum is checkable
# ------------------------------------------------------------------------------------------------

def exhaustive_pairs(fit: Fitness, p: int, jobs: int) -> tuple:
    pairs = list(itertools.combinations(range(p), 2))
    if jobs != 1:
        from joblib import Parallel, delayed
        vals = Parallel(n_jobs=jobs)(
            delayed(_score_one)(fit.X, s, fit.B, fit.seed) for s in pairs)
        for s, v in zip(pairs, vals):
            fit.cache[tuple(s)] = v
        fit.n_evals += len(pairs)
    else:
        vals = [fit(s) for s in pairs]
    i = int(np.argmax(vals))
    return list(pairs[i]), float(vals[i]), len(pairs)


def _score_one(X, cols, B, seed):
    """Top level so joblib can pickle it."""
    v = float(z_reps(TERMS, X, tuple(sorted(cols)), B=B, shared_seed=seed, n_reps=1)[0])
    return v if np.isfinite(v) else -1e9


# ------------------------------------------------------------------------------------------------
# Method C: NSGA-II over bit-strings, reusing the repo's selection machinery unchanged
# ------------------------------------------------------------------------------------------------

def objectives(pop, fit: Fitness) -> np.ndarray:
    """(N, 2) all-maximised: [combined score, -panel size]."""
    M = np.empty((len(pop), 2), dtype=float)
    for i, g in enumerate(pop):
        cols = gm.selected_indices(g)
        M[i, 0] = fit(cols)
        M[i, 1] = -float(len(cols))
    return M


def crowded_tournament(M, rng, k=2):
    """Binary tournament on (front rank, then crowding distance) -- the classical NSGA-II operator."""
    from atomicplus.selection import crowding_distance, fast_nondominated_sort
    fronts = fast_nondominated_sort(M)
    rank = np.empty(len(M), dtype=int)
    cd = np.zeros(len(M))
    for r, f in enumerate(fronts):
        d = crowding_distance(M, f)
        for i in f:
            rank[i] = r
            cd[i] = d[i]

    def pick():
        a, b = rng.integers(0, len(M), size=2)
        if rank[a] != rank[b]:
            return int(a if rank[a] < rank[b] else b)
        return int(a if cd[a] > cd[b] else b)
    return [pick() for _ in range(k)]


def run_nsga2(fit: Fitness, p: int, cfg, log) -> list:
    rng = np.random.default_rng(cfg["seed"])
    pop = gm.random_population(cfg["mu"], p, rng, min_features=2)
    for g in pop:
        ops._enforce_cap(g, rng, cfg["max_size"])
        gm.ensure_min_features(g, rng, 2)
    M = objectives(pop, fit)

    for gen in range(cfg["gens"]):
        offspring = []
        while len(offspring) < cfg["lam"]:
            i, j = crowded_tournament(M, rng)
            c1, c2 = ops.crossover(pop[i], pop[j], rng, mode="uniform", min_features=2)
            for c in (c1, c2):
                c = ops.mutate(c, rng, per_bit_prob=cfg["mut"], min_features=2)
                ops._enforce_cap(c, rng, cfg["max_size"])
                gm.ensure_min_features(c, rng, 2)
                offspring.append(c)
        offspring = offspring[:cfg["lam"]]
        combined = list(pop) + offspring
        Mc = objectives(combined, fit)
        keep = nsga2_select(Mc, cfg["mu"])
        pop = [combined[i] for i in keep]
        M = Mc[keep]
        if gen % 5 == 0 or gen == cfg["gens"] - 1:
            best = {}
            for g in pop:
                c = tuple(gm.selected_indices(g))
                best[len(c)] = max(best.get(len(c), -np.inf), fit(c))
            log(f"    gen {gen:>3}  evals {fit.n_evals:>5}  best by size "
                f"{ {k: round(v, 2) for k, v in sorted(best.items())} }")
    return pop


# ------------------------------------------------------------------------------------------------
# Post-hoc description -- labels enter here and nowhere else
# ------------------------------------------------------------------------------------------------

def describe_panel(X, y, cols, names):
    lab = graphcut_term(X[:, list(cols)])[1]
    if lab is None or lab.sum() in (0, len(lab)):
        return dict(purity=np.nan, boundary="", primary="", hit="degenerate")
    side = lab.astype(bool)
    pu, _ = purity(y, side)
    b = name_boundary(*majority_sides(y, side))
    pn = [names[j] for j in cols]
    return dict(purity=round(pu, 3), boundary=b["name"] if b else "",
                primary=b["primary"] if b else "",
                hit="" if not b else ("PRIMARY" if b["primary"] in pn else
                                      "related" if ({b["primary"]} | set(b["also"])) & set(pn)
                                      else "miss"))


def main():
    a = list(sys.argv[1:])
    cfg = dict(n=400, cap=60, B=10, mu=40, lam=40, gens=25, mut=0.06, max_size=5, jobs=1, seed=0)
    if "--analyze-only" in a:
        i = a.index("--analyze-only")
        d = pd.read_csv(a[i + 1]); pd.set_option("display.width", 220)
        print(d.to_string(index=False)); return
    if "--quick" in a:
        a.remove("--quick"); cfg.update(n=250, B=6, mu=16, lam=16, gens=6)
    for k in list(cfg):
        for f in (f"--{k}", f"--{k.replace('_', '-')}"):
            if f in a:
                i = a.index(f)
                cfg[k] = float(a[i + 1]) if k == "mut" else int(a[i + 1])
                del a[i:i + 2]
                break
    if a:
        print(f"unrecognised arguments: {a}"); sys.exit(2)

    log = lambda s: print(s, flush=True)  # noqa: E731
    X, y, names = load_capped(cfg["cap"], cfg["seed"], False, 800)
    if cfg["n"] and cfg["n"] < len(X):
        rng = np.random.default_rng(cfg["seed"])
        idx = np.sort(rng.choice(len(X), size=cfg["n"], replace=False))
        X, y = X[idx], y[idx]
    p = X.shape[1]
    log(f"exp-028 -- NSGA-II vs greedy vs exhaustive, at the tree's ROOT node\n"
        f"{len(X)} cells x {p} markers, {len(set(y.tolist()))} populations\nconfig {cfg}\n")

    rows = []

    log("[A] EXHAUSTIVE at size 2 -- ground truth where it is computable")
    t0 = time.time()
    f_ex = Fitness(X, B=cfg["B"], shared_seed=cfg["seed"])
    best2, z2, n_ex = exhaustive_pairs(f_ex, p, cfg["jobs"])
    log(f"    best pair {[names[j] for j in best2]}  z={z2:.3f}  ({n_ex} panels, "
        f"{time.time() - t0:.0f}s)")
    rows.append(dict(method="exhaustive", size=2, z=round(z2, 3),
                     panel=",".join(names[j] for j in best2), evals=n_ex,
                     seconds=round(time.time() - t0, 1), **describe_panel(X, y, best2, names)))

    log("\n[B] GREEDY per size -- what the tree does today")
    f_gr = Fitness(X, B=cfg["B"], shared_seed=cfg["seed"])
    for K in range(2, cfg["max_size"] + 1):
        t0, before = time.time(), f_gr.n_evals
        res = grow_from_pairs_stop(TERMS, X, seed_score_fn=graphcut_term, n_seeds=5, max_size=K,
                                   B=cfg["B"], shared_seed=cfg["seed"], n_jobs=cfg["jobs"])
        res = [r for r in res if np.isfinite(r["z"])]
        if not res:
            continue
        b = max(res, key=lambda r: r["z"])
        cols = list(b["panel"])
        rows.append(dict(method="greedy", size=len(cols), z=round(float(b["z"]), 3),
                         panel=",".join(names[j] for j in cols),
                         evals=np.nan, seconds=round(time.time() - t0, 1),
                         **describe_panel(X, y, cols, names)))
        log(f"    cap {K}: {[names[j] for j in cols]}  z={b['z']:.3f}  "
            f"({time.time() - t0:.0f}s)")

    log("\n[C] NSGA-II")
    t0 = time.time()
    f_ea = Fitness(X, B=cfg["B"], shared_seed=cfg["seed"])
    pop = run_nsga2(f_ea, p, cfg, log)
    seen = {}
    for g in pop:
        cols = tuple(gm.selected_indices(g))
        v = f_ea(cols)
        if v > seen.get(len(cols), (-np.inf, None))[0]:
            seen[len(cols)] = (v, cols)
    for k in sorted(seen):
        v, cols = seen[k]
        rows.append(dict(method="nsga2", size=k, z=round(v, 3),
                         panel=",".join(names[j] for j in cols), evals=f_ea.n_evals,
                         seconds=round(time.time() - t0, 1),
                         **describe_panel(X, y, list(cols), names)))
        log(f"    size {k}: {[names[j] for j in cols]}  z={v:.3f}")

    # Greedy can return the same panel at two different caps (at cap 5 the rule stopped at 4), so
    # keep the best row per (method, size) rather than printing the duplicate.
    df = pd.DataFrame(rows).sort_values("z", ascending=False)
    df = df.drop_duplicates(subset=["method", "size"], keep="first").sort_values(["method", "size"])
    os.makedirs("results", exist_ok=True)
    out = f"results/nsga2_n{len(X)}_B{cfg['B']}_s{cfg['seed']}.csv"
    df.to_csv(out, index=False)
    pd.set_option("display.width", 220)
    print("\n" + "=" * 104 + "\nexp-028 -- BEST COMBINED SCORE AT EACH PANEL SIZE\n" + "=" * 104)
    print(df.to_string(index=False))

    piv = df.pivot_table(index="size", columns="method", values="z", aggfunc="max")
    print("\nbest score by size (higher is better):")
    print(piv.to_string())
    if {"greedy", "nsga2"} <= set(df.method):
        for k in sorted(set(df[df.method == "nsga2"]["size"]) & set(df[df.method == "greedy"]["size"])):
            g = df[(df.method == "greedy") & (df["size"] == k)].z.max()
            e = df[(df.method == "nsga2") & (df["size"] == k)].z.max()
            print(f"  size {k}: NSGA-II {e:+.3f} vs greedy {g:+.3f}  ->  "
                  f"{'NSGA-II better' if e > g + 1e-9 else 'greedy better' if g > e + 1e-9 else 'tie'}")
    if "exhaustive" in set(df.method):
        ez = df[df.method == "exhaustive"].z.max()
        for m in ("greedy", "nsga2"):
            sub = df[(df.method == m) & (df["size"] == 2)]
            if len(sub):
                print(f"  size 2 check: {m} reached {sub.z.max():.3f} against the true optimum "
                      f"{ez:.3f}" + ("  -- FOUND IT" if abs(sub.z.max() - ez) < 1e-6 else "  -- MISSED"))
    print(f"\n  Evaluations spent: exhaustive {n_ex}, NSGA-II {f_ea.n_evals} distinct panels.")
    print("  Greedy's count is not comparable -- it spends most of its budget on raw pair scores,")
    print("  which are far cheaper than a calibrated one. Read the seconds column instead.")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
