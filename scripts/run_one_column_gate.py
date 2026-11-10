"""THE GATE. Run this on any dataset BEFORE scoring anything on it.

THE QUESTION IT ASKS
--------------------
Can you get the right answer from ONE feature on its own? If yes, the dataset cannot test us. The
entire premise of this project is finding features that only mean something TOGETHER, so if a
single column already suffices there is nothing joint to find, and the correct tool is a univariate
filter -- score each column separately, sort, take the best. Cheap, well understood, and not what
we are building.

There is a second, sharper reason. A dataset where many single columns work hands out free marks:
if 205 of 561 columns individually reach ARI 0.5, then roughly 60% of all pairs contain a column
that already answers the question, so almost any pair we pick scores well and the test cannot
separate a working selection method from a coin flip.

WHAT IT HAS ALREADY CAUGHT
--------------------------
  * our own synthetic generator -- jain and spiral gave up the planted pair 100% of the time, and
    every suite-averaged number up to that point was inflated (docs/CORRECTIONS.md C2)
  * UCI HAR "moving vs still" -- best single column ARI 1.000, 205 of 561 columns above 0.5. Not a
    defect in HAR; a motion sensor telling motion from stillness with one number is physics. It is
    a badly chosen QUESTION, and we switched to sitting-vs-standing (best single column 0.409).

Both times the gate was the difference between a real result and a confident-looking meaningless
one. Run it on prestigious datasets too.

HOW TO READ THE OUTPUT
----------------------
  best single-column ARI  >= 0.9   UNUSABLE. Pick another contrast.
                          0.5-0.9  LEAKY. Usable only if the best PAIR is far better; report both.
                          <  0.5   usable.
  columns above ARI 0.5   any number above a handful is the free-marks problem, independent of the
                          best value.

Also reported: the best PAIR over a random sample of pairs. A dataset is interesting to us exactly
when pairs beat singles by a wide margin -- that gap IS the joint structure we claim to find.

    python scripts/run_one_column_gate.py metabric
    python scripts/run_one_column_gate.py metabric --contrast basal_luminal
    python scripts/run_one_column_gate.py mice --label Behavior
    python scripts/run_one_column_gate.py har mice metabric --pairs 3000
"""
from __future__ import annotations

import itertools
import os
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.cluster import KMeans

from atomicplus.datasets.real import LOADERS
from atomicplus.evaluation import metrics

OUT = "results/one_column_gate.csv"


def ari_2means(Z: np.ndarray, y: np.ndarray, seed: int = 0) -> float:
    return metrics.ari(y, KMeans(2, n_init=10, random_state=seed).fit_predict(Z))


def gate(name: str, X: np.ndarray, y: np.ndarray, names, n_pairs: int, seed: int) -> dict:
    p = X.shape[1]
    singles = np.array([ari_2means(X[:, [j]], y) for j in range(p)])
    order = np.argsort(-singles)

    all_pairs = list(itertools.combinations(range(p), 2))
    rng = np.random.default_rng(seed)
    if len(all_pairs) > n_pairs:
        idx = rng.choice(len(all_pairs), size=n_pairs, replace=False)
        pairs = [all_pairs[i] for i in sorted(idx)]
        note = f"sampled {len(pairs)} of {len(all_pairs)}"
    else:
        pairs, note = all_pairs, f"all {len(all_pairs)}"
    pair_ari = np.array([ari_2means(X[:, list(s)], y) for s in pairs])
    best_pair = pairs[int(np.argmax(pair_ari))]

    best1, n_over = float(singles.max()), int((singles > 0.5).sum())
    # Four outcomes, and the third one is easy to miss: a dataset can pass the leak check simply
    # by having no structure at all. That produces an AMBIGUOUS NULL -- our score will look bad on
    # it, but the dataset never had a pair to find, so the result says nothing about our method.
    # exp-019 hit exactly this with mice/Genotype and it has to be caught here, not afterwards.
    verdict = ("UNUSABLE" if best1 >= 0.9 else
               "NO PAIR STRUCTURE" if pair_ari.max() < 0.5 else
               "LEAKY" if best1 >= 0.5 or n_over > 3 else "usable")
    print(f"\n### {name}   n={len(X)}  p={p}   ({note} pairs)")
    print(f"  best single-column ARI  {best1:.3f}   ({names[int(order[0])]})")
    print(f"  columns above ARI 0.5   {n_over} of {p}")
    print(f"  top 5 single columns    " +
          ", ".join(f"{names[j]} {singles[j]:.2f}" for j in order[:5]))
    print(f"  best PAIR ARI           {pair_ari.max():.3f}   "
          f"({names[best_pair[0]]}, {names[best_pair[1]]})")
    print(f"  pairs above ARI 0.5     {int((pair_ari > 0.5).sum())} of {len(pairs)}")
    print(f"  pair minus single       {pair_ari.max() - best1:+.3f}   "
          f"<- the joint structure we claim to find; want this large")
    print(f"  VERDICT                 {verdict}")
    if verdict == "UNUSABLE":
        print("  -> one feature answers the question. This dataset/contrast cannot test us.")
    elif verdict == "NO PAIR STRUCTURE":
        print("  -> no pair reaches ARI 0.5, so there is nothing at pair level to find. Any score")
        print("     measured here is an AMBIGUOUS NULL: it says the dataset is unsuitable, NOT")
        print("     that our method failed. Try another contrast or a larger panel size.")
    elif verdict == "LEAKY":
        print("  -> usable only if the pair margin above is large. Report both numbers.")
    return dict(dataset=name, n=len(X), p=p, best_single=best1, n_cols_over_half=n_over,
                best_single_feature=names[int(order[0])], best_pair_ari=float(pair_ari.max()),
                best_pair=str(tuple(names[j] for j in best_pair)),
                n_pairs_scored=len(pairs), n_pairs_total=len(all_pairs),
                pairs_over_half=int((pair_ari > 0.5).sum()),
                pair_minus_single=float(pair_ari.max() - best1), verdict=verdict)


def main() -> None:
    args = list(sys.argv[1:])
    kw, n_pairs, n_rows, seed = {}, 4000, 600, 0
    for flag, cast in (("--contrast", str), ("--label", str), ("--pairs", int),
                       ("--n", int), ("--seed", int)):
        if flag in args:
            i = args.index(flag); v = cast(args[i + 1]); del args[i:i + 2]
            if flag == "--pairs": n_pairs = v
            elif flag == "--n": n_rows = None if v <= 0 else v   # --n 0 means "use every row"
            elif flag == "--seed": seed = v
            else: kw[flag[2:]] = v
    datasets = args or ["metabric"]
    bad = [d for d in datasets if d not in LOADERS]
    if bad:
        sys.exit(f"ERROR: unknown dataset(s) {bad}; valid: {' '.join(LOADERS)}")

    os.makedirs("results", exist_ok=True)
    rows = []
    for ds in datasets:
        import inspect
        sig = inspect.signature(LOADERS[ds]).parameters
        kws = {k: v for k, v in kw.items() if k in sig}
        X, y, names = LOADERS[ds](n=n_rows, seed=seed, **kws)
        rows.append(gate(f"{ds} {kws or ''}".strip(), X, y, names, n_pairs, seed))
    df = pd.DataFrame(rows)
    df.to_csv(OUT, mode="a", header=not os.path.exists(OUT), index=False)
    print(f"\nappended to {OUT}")


if __name__ == "__main__":
    main()
