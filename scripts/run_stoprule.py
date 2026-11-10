"""exp-027 -- does one stopping rule get the panel SIZE right on datasets whose answers differ?

THE QUESTION
------------
Panel growth has over-run its target in every experiment: 35 of 39 nodes hit the size cap in the
cytometry tree (exp-024), and on the spherical shells the graph-cut term preferred a four-column
panel to the correct three-column one while clustering quality halved (exp-026). Two candidate
fixes came out of that, and this script decides between them.

WHY THIS DESIGN AND NOT AN END-TO-END RUN
-----------------------------------------
A rule that works on one dataset proves nothing -- if it needs different settings per dataset it is
tuning, not a fix. The only convincing evidence is ONE rule, with its settings fixed in advance,
landing on the right size across datasets whose right answers are DIFFERENT. So:

    shells            right answer is 3 columns   (radius needs all three coordinates)
    circles           right answer is 2 columns   (a planted non-convex pair)
    two-cluster       right answer is 2 columns   (a planted convex pair)
    Levine CD4T/CD8T  right answer is 2 columns   (the published CD4 x CD8 gate, real data)

A rule that stops at 3 on the first and 2 on the other three has generalised. A rule that stops at
the same size everywhere has just learned a habit.

GROWTH STARTS FROM THE TRUE PANEL MINUS ONE FEATURE, ON PURPOSE
---------------------------------------------------------------
This tests the stopping rule ALONE. Starting from a searched seed would mix in the separate question
of whether the search finds a good starting point, and a failure could not be attributed. So growth
starts from two of the true columns and the only question asked is: does it add what is missing and
then stop? On the size-2 datasets the seed is already the answer, so the test is purely whether the
rule correctly refuses to grow -- which is precisely the failure being investigated.

This is therefore NOT an end-to-end result and must not be reported as one. `--seed-mode search`
runs the honest end-to-end version once a rule has earned it.

THE FOUR RULES, FIXED BEFORE RUNNING
------------------------------------
    R1  graph-cut only, accept any gain      the current rule, the thing to beat
    R2  density only, accept any gain        the other term on its own
    R3  BOTH terms summed, accept any gain   proposal 1 -- no new parameter at all
    R4  both summed, gain > 1 standard error proposal 2 -- one parameter, fixed at 1 in advance

`min_gain_se = 1` is chosen because it is the plainest value, not because it was tried and worked.
`--min-gain-se` sweeps it if the effect of that choice needs reporting; a value picked after seeing
the results would be fitting to the answer key.

    python scripts/run_stoprule.py --quick            # small, a few minutes
    python scripts/run_stoprule.py --jobs 8
    python scripts/run_stoprule.py --jobs 8 --seed-mode search
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

from atomicplus.evaluation.stopping import grow_with_stop
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

#: Per-configuration output name. A fixed filename here destroyed two runs of this experiment:
#: the oracle-seeded and search-seeded runs both wrote to results/stoprule.csv and the second
#: silently overwrote the first, twice. Name outputs after the settings that produced them.
def outpath(mode, cfg):
    return f"results/stoprule_{mode}_n{cfg['n']}_B{cfg['B']}_s{cfg['seed']}.csv"

#: (name, scorers, n_reps, min_gain_se). Frozen before the first run -- see the module docstring.
RULES = [
    ("R1 graphcut, any gain",   [graphcut_term],               1, 0.0),
    ("R2 density, any gain",    [density_term],                1, 0.0),
    ("R3 combined, any gain",   [graphcut_term, density_term], 1, 0.0),
    ("R4 combined, gain>1 SE",  [graphcut_term, density_term], 3, 1.0),
]


def datasets(cfg):
    """(name, X, true panel columns, true size). Every entry states its own right answer."""
    from atomicplus.datasets.synthetic import circles_subspace, two_cluster_subspace
    out = []
    rng = np.random.default_rng(cfg["seed"])

    try:
        from atomicplus.datasets.synthetic import shells_subspace
        df, _, info = shells_subspace(n=cfg["n_shells_rows"], p=cfg["p"], n_shells=2,
                                      thickness=0.10, rng=np.random.default_rng(cfg["seed"]))
        out.append(("shells (answer 3)", df.to_numpy(), tuple(info), 3))
    except ImportError:
        print("  ! shells_subspace not found in atomicplus.datasets.synthetic -- skipping it.\n"
              "    That dataset is the only one here whose answer is 3, so without it this run\n"
              "    cannot distinguish a rule that generalises from one that always stops at 2.")

    df, _, info = circles_subspace(n=cfg["n"], p=cfg["p"], rng=rng)
    out.append(("circles (answer 2)", df.to_numpy(), tuple(info), 2))
    df, _, info = two_cluster_subspace(n=cfg["n"], p=cfg["p"], rng=rng)
    out.append(("two-cluster (answer 2)", df.to_numpy(), tuple(info), 2))

    try:
        from atomicplus.datasets.real import LEVINE_CONTRASTS, load_levine
        X, _, names = load_levine(n=cfg["n"], contrast="cd4t_cd8t")
        cols = tuple(names.index(m) for m in LEVINE_CONTRASTS["cd4t_cd8t"]["true_panel"])
        out.append(("Levine CD4T/CD8T (answer 2)", X, cols, 2))
    except Exception as e:  # noqa: BLE001
        print(f"  ! Levine unavailable ({type(e).__name__}), skipping the real-data case")
    return out


def seed_for(X, true_cols, mode, scorers, pool):
    """Where growth starts. `oracle` = two of the true columns, isolating the stopping rule."""
    if mode == "oracle":
        return tuple(sorted(true_cols[:2]))
    best, arg = -np.inf, (0, 1)
    for s in itertools.combinations(pool, 2):
        v = scorers[0](X[:, list(s)])[0]
        if np.isfinite(v) and v > best:
            best, arg = v, s
    return tuple(sorted(arg))


def main():
    a = list(sys.argv[1:])
    cfg = dict(n=300, p=12, n_shells_rows=800, B=15, jobs=1, seed=0, pool_cap=14,
               min_gain_se=-1.0)
    mode = "oracle"
    if "--seed-mode" in a:
        i = a.index("--seed-mode"); mode = a[i + 1]; del a[i:i + 2]
    if "--quick" in a:
        a.remove("--quick"); cfg.update(n=200, n_shells_rows=500, B=8)
    for k in list(cfg):
        for f in (f"--{k}", f"--{k.replace('_', '-')}"):
            if f in a:
                i = a.index(f)
                cfg[k] = float(a[i + 1]) if k == "min_gain_se" else int(a[i + 1])
                del a[i:i + 2]
                break
    if a:
        print(f"unrecognised arguments: {a}"); sys.exit(2)

    rules = RULES
    if cfg["min_gain_se"] >= 0:      # explicit override, for reporting sensitivity to that choice
        rules = [(f"combined, gain>{cfg['min_gain_se']} SE",
                  [graphcut_term, density_term], 3, cfg["min_gain_se"])]

    print(f"exp-027 -- one stopping rule, four datasets, answers of 3 and 2\n"
          f"seeding: {mode}   config {cfg}\n")
    rows = []
    for name, X, true_cols, true_k in datasets(cfg):
        # Growth pool: the true columns plus enough others to make the choice non-trivial, capped so
        # the run stays small. Recorded because a shortlist is a search decision, not a detail.
        rest = [j for j in range(X.shape[1]) if j not in true_cols]
        pool = sorted(set(true_cols) | set(rest[:max(0, cfg["pool_cap"] - len(true_cols))]))
        cap = true_k + 2
        print(f"### {name}   n={len(X)} p={X.shape[1]}  true panel {true_cols}  "
              f"pool {len(pool)} columns  cap {cap}")
        for rname, fns, n_reps, mgs in rules:
            t0 = time.time()
            s0 = seed_for(X, true_cols, mode, fns, pool)
            chosen, trace = grow_with_stop(fns, X, s0, max_size=cap, B=cfg["B"],
                                           shared_seed=cfg["seed"], pool=pool, n_reps=n_reps,
                                           min_gain_se=mgs, n_jobs=cfg["jobs"])
            stop = trace[-1] if not trace[-1]["accepted"] else None
            rows.append(dict(dataset=name, rule=rname, true_size=true_k, stopped_at=len(chosen),
                             correct_size=len(chosen) == true_k,
                             exact_panel=set(chosen) == set(true_cols),
                             hit_cap=len(chosen) >= cap, panel=str(tuple(chosen)),
                             rejected_gain=None if stop is None else round(stop["gain"], 3),
                             rejected_gain_se=None if stop is None else round(stop["gain_se"], 3),
                             seconds=round(time.time() - t0, 1)))
            r = rows[-1]
            print(f"  {rname:<26s} stopped at {r['stopped_at']} (true {true_k})  "
                  f"{'CORRECT SIZE' if r['correct_size'] else 'wrong size'}"
                  f"{', exact panel' if r['exact_panel'] else ''}"
                  f"{'  [HIT CAP, so it never chose to stop]' if r['hit_cap'] else ''}"
                  f"   {r['seconds']}s")
        print()

    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    out = outpath(mode, cfg)
    df.to_csv(out, index=False)
    pd.set_option("display.width", 200)
    print("=" * 96 + "\nexp-027 -- WHICH RULE GETS THE SIZE RIGHT EVERYWHERE?\n" + "=" * 96)
    piv = df.pivot_table(index="rule", columns="dataset", values="stopped_at", aggfunc="first")
    print("\nstopped at (true size in the column heading):")
    print(piv.to_string())
    summ = df.groupby("rule").agg(correct_size=("correct_size", "sum"),
                                  exact_panel=("exact_panel", "sum"),
                                  hit_cap=("hit_cap", "sum"), datasets=("rule", "size"))
    print("\n" + summ.to_string())
    win = summ[summ.correct_size == summ.datasets]
    print(f"\n  Rules correct on every dataset: "
          f"{list(win.index) if len(win) else 'none'}")
    print("  `hit_cap` counts runs that stopped only because the size cap was reached. Those did")
    print("  not exercise the stopping rule at all, so a rule with a high hit_cap has not been")
    print("  shown to stop -- it has been shown to be stopped.")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
