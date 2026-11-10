"""Is the harder benchmark actually harder? Check BEFORE spending hours on the full comparison.

Three checks, run side by side on the old junk columns and the new ones.

  CHECK 1  the one-column shortcut.  Score each column on its own by how unevenly its values are
           spread, take the two most uneven. If that finds the planted pair, the data gives away
           its answer without anyone looking at pairs -- which is what we discovered the ORIGINAL
           benchmark does on jain (100%), spiral (100%), gauss2 (65-80%) and circles (45-70%).
           On the new junk this should collapse toward chance, which is 1/C(p,2).

  CHECK 2  is the junk actually junk?  No junk column may predict the labels. Measured as the
           largest |AUC - 0.5| over all junk columns -- but compared against the SAME statistic
           with the labels shuffled, not against a fixed cutoff. With ~10 junk columns the
           maximum runs around 0.1 even under perfect independence, so a fixed threshold gives
           false alarms. Only an observed value ABOVE the shuffled range means real leakage.

  CHECK 3  the mass-concentration cue.  This is the crude rule that beat our signal on the old
           benchmark: for every pair, run DBSCAN at a small radius and count how many points land
           in a clump at all; pick the pair with the most. On the old junk this scores ~1.00
           because only the planted columns hold concentrated mass. The new junk is designed to
           defeat it. If it does NOT drop, the new generator has failed at its one job -- say so
           and fix it rather than proceeding.

WHAT A GOOD RESULT LOOKS LIKE: check 1 near chance, check 2 near zero, check 3 well down from
1.00. If check 3 drops but our own signal ALSO collapses, that is a real negative for our signal
and must be reported, not retried with different noise settings until it passes.

    python scripts/run_benchmark_validation.py                  # 20 seeds, p=12,20,40
    python scripts/run_benchmark_validation.py --seeds 5 --ps 20
"""
import itertools
import os
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scipy.stats import kstest
from sklearn.cluster import DBSCAN

from atomicplus.datasets.structured_noise import verify_noise_is_uninformative
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term, zscore
from run_method_baselines import INF, KNOWN_DATASETS, load, load_structured

SMALL_EPS = 0.03            # the radius SUBCLU actually chose on the original benchmark


def one_column_shortcut(X):
    ks = [kstest(X[:, j], "uniform").statistic for j in range(X.shape[1])]
    return set(np.argsort(ks)[-2:]) == set(INF)


def coverage_cue(X, pairs):
    """Rank pairs by how many points fall into a clump at all. Returns True if rank-1 is truth."""
    cov = [int(np.count_nonzero(DBSCAN(eps=SMALL_EPS, min_samples=5)
                                .fit_predict(X[:, list(pr)]) != -1)) for pr in pairs]
    return pairs[int(np.argmax(cov))] == tuple(INF)


def our_signal(X, pairs):
    gc, de = [], []
    for pr in pairs:
        g, _ = graphcut_term(X[:, list(pr)])
        d, _ = density_term(X[:, list(pr)])
        gc.append(g); de.append(d)
    return pairs[int(np.argmax(zscore(gc) + zscore(de)))] == tuple(INF)


def main():
    args = list(sys.argv[1:])
    seeds, ps, jobs = 20, [12, 20, 40], 1
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = int(args[i + 1]); del args[i:i + 2]
    if "--ps" in args:
        i = args.index("--ps"); ps = [int(x) for x in args[i + 1].split(",")]; del args[i:i + 2]
    if "--jobs" in args:
        i = args.index("--jobs"); jobs = int(args[i + 1]); del args[i:i + 2]
    datasets = args if args else list(KNOWN_DATASETS)

    rows = []
    for prof in ("uniform", "structured"):
        for name in datasets:
            for p in ps:
                pairs = list(itertools.combinations(range(p), 2))
                sc1 = sc2 = sc3 = 0
                leak = 0.0
                null = 0.0
                for seed in range(seeds):
                    X, y = (load(name, p, seed) if prof == "uniform"
                            else load_structured(name, p, seed, prof))
                    sc1 += one_column_shortcut(X)
                    sc3 += coverage_cue(X, pairs)
                    sc2 += our_signal(X, pairs)
                    junk = X[:, [j for j in range(p) if j not in INF]]
                    leak += verify_noise_is_uninformative(junk, y)["max_abs_auc_minus_half"]
                    # null: same statistic with the labels shuffled, so we know what "no
                    # relationship at all" looks like for this many columns and this n
                    rs = np.random.default_rng(777 + seed)
                    nd = [verify_noise_is_uninformative(junk, rs.permutation(y))
                          ["max_abs_auc_minus_half"] for _ in range(5)]
                    null += float(np.mean(nd))
                rows.append(dict(noise=prof, dataset=name, p=p, chance=1.0 / len(pairs),
                                 c1_one_column=sc1 / seeds, c3_mass_cue=sc3 / seeds,
                                 our_signal=sc2 / seeds, c2_worst_leak=leak / seeds, c2_null_leak=null / seeds))
                print(f"  {prof:11s} {name:8s} p={p:<3d} "
                      f"1col={sc1/seeds:.2f}  masscue={sc3/seeds:.2f}  ours={sc2/seeds:.2f}  "
                      f"leak={leak/seeds:.3f} (null {null/seeds:.3f})", flush=True)

    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/benchmark_validation.csv", index=False)
    pd.set_option("display.width", 200)

    print("\n" + "=" * 78)
    print("CHECK 1 -- one-column shortcut (want: collapses toward 'chance')")
    print("=" * 78)
    print(df.pivot_table(index=["dataset", "p"], columns="noise",
                         values="c1_one_column").round(2).to_string())
    print("\n  chance level by p:  " +
          "  ".join(f"p={p}: {1.0/len(list(itertools.combinations(range(p),2))):.3f}" for p in ps))

    print("\n" + "=" * 78)
    print("CHECK 2 -- is the junk actually junk? worst |AUC-0.5| over junk columns (want ~0)")
    print("=" * 78)
    print(df.pivot_table(index=["dataset", "p"], columns="noise",
                         values=["c2_worst_leak", "c2_null_leak"]).round(3).to_string())
    d = df[df.noise == "structured"]
    obs, nul = d.c2_worst_leak.mean(), d.c2_null_leak.mean()
    print(f"\n  new junk: observed {obs:.3f} vs shuffled-label null {nul:.3f}  ->  "
          + ("OK -- indistinguishable from pure independence" if obs <= nul * 1.25 else
             "PROBLEM: junk columns predict the labels, generator is broken"))
    print("  (junk is drawn from an RNG stream independent of the labels, so any gap here is")
    print("   estimator noise; both columns are averages over seeds, not maxima.)")

    print("\n" + "=" * 78)
    print("CHECK 3 -- mass-concentration cue (the rule that beat us) vs OUR signal")
    print("=" * 78)
    print(df.pivot_table(index=["dataset", "p"], columns="noise",
                         values=["c3_mass_cue", "our_signal"]).round(2).to_string())
    for prof in ("uniform", "structured"):
        d = df[df.noise == prof]
        print(f"\n  {prof:11s} mean:  mass-cue {d.c3_mass_cue.mean():.3f}   "
              f"ours {d.our_signal.mean():.3f}")
    print("\n  Read this honestly: if the mass cue drops and ours holds, the new benchmark is")
    print("  doing its job AND our signal is justified. If both drop, our signal was relying on")
    print("  the same easy cue -- report that, do NOT retune the noise until we pass.")


if __name__ == "__main__":
    main()
