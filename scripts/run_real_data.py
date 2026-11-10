"""exp-019 -- do the selection signals behave on REAL data the way they do on our synthetic shapes?

WHY THIS EXISTS
---------------
We have iterated on our own generator for a long time, and we already caught it being wrong once:
four of six shapes gave up the planted pair to a one-column test, which invalidated every
suite-averaged selection number up to that point. The honest risk now is that we are tuning to a
second set of quirks in the replacement generator. Real data cannot flatter us that way.

THE MEASUREMENT PROBLEM, AND HOW WE GET AROUND IT
--------------------------------------------------
None of these datasets ships a ground-truth feature panel, so `rank-1 selection` and the
`t=0/1/2` grouping from exp-018 are simply not computable. Asking for them anyway would mean
inventing a panel, which is circular.

Instead we ask the question that IS answerable and is not circular:

    Does the unsupervised score rank subspaces the same way ground-truth ARI does?

For every candidate pair we compute (a) each unsupervised score and (b) the ARI of the clustering
in that pair's subspace against the real labels. If a score is a good selection signal, the two
should correlate. That is a direct test of "does this score know which subspaces are informative",
it uses labels only for scoring and never for selection, and nothing about it is circular.

Three outputs:

  [1] SPEARMAN(score, ARI) over all pairs -- the primary number. A score that ranks subspaces
      well has high positive rank correlation. Reported per split criterion, because ARI depends
      on which splitter you use and it would be dishonest to quietly pick the flattering one.

  [2] TOP-10 LIFT -- mean ARI of the 10 highest-scoring pairs minus the mean ARI over all pairs.
      Closer to what a method actually delivers than a correlation over the whole range, since in
      practice we only ever act on the top of the ranking.

  [3] DILUTION ON REAL DATA -- the exp-018 t2-vs-t1 test, with the "true pair" taken to be the
      highest-ARI pair. We are NOT claiming that pair is the biological answer; we are asking
      whether each score can still recognise the best AVAILABLE subspace once an irrelevant
      column is mixed in. That is exactly the property that failed on synthetic data.

SCOPE
-----
mice has 77 features, so all 2,926 pairs are enumerated -- no sampling, no search confound.
madelon (500) and har (561) have ~125k and ~157k pairs, so those are randomly sampled; the number
sampled is printed and recorded, never silently truncated.

Label choice is deliberate: for mice the 8-way `class` is a 2x2x2 design whose groups need not be
geometrically separable in ANY 2-D subspace, so the default target is the binary Genotype factor.
For har the 6 activities collapse to the standard dynamic-vs-static bipartition. Asking a 2-way
splitter to recover 6 or 8 groups would be a rigged failure. See atomicplus/datasets/real.py.

    python scripts/run_real_data.py --quick                 # mice, 300 pairs, ~2 min
    python scripts/run_real_data.py mice --jobs 8           # full enumeration
    python scripts/run_real_data.py mice har madelon --jobs 8 --max-pairs 4000
    python scripts/run_real_data.py mice --jobs 8 --label Behavior
    python scripts/run_real_data.py metabric --label her2_luminal --jobs 8 --max-pairs 4000
    python scripts/run_real_data.py --analyze-only        # reads every results/real_data_*.csv

IF max achievable ARI comes back near zero, STOP AND READ THIS. It means no pair of features
carries the labelled structure at all, so every correlation below is measuring noise. That is an
AMBIGUOUS null -- it says nothing about whether our score is good, only that this dataset+label
has no 2-feature panel to find. Report it as "dataset unsuitable", never as "method failed", and
try the other labels or a larger panel size before drawing any conclusion.
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

from scipy.stats import spearmanr
from sklearn.cluster import HDBSCAN

from atomicplus.datasets.real import LOADERS
from atomicplus.evaluation import metrics
from atomicplus.evaluation.multivariance import (
    centred_distance_matrices, multivariance, total_multivariance,
)
from atomicplus.evaluation.subspace_baselines import (
    density_term, graphcut_term, graphcut_term_dcdist,
)

# One file PER (dataset, label). A single fixed filename silently destroyed two METABRIC runs on
# 2026-08-06 -- three sequential invocations each overwrote the last, and only the final one
# survived. Results files are cheap; re-running an overnight sweep is not.
OUT_DIR = "results"


def out_path(ds: str, lbl: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(lbl))
    return os.path.join(OUT_DIR, f"real_data_{ds}_{safe}.csv")


def load_all_results() -> "pd.DataFrame":
    """Every real_data_*.csv, concatenated, for --analyze-only."""
    import glob
    paths = sorted(glob.glob(os.path.join(OUT_DIR, "real_data_*.csv")))
    if not paths:
        raise SystemExit(f"no {OUT_DIR}/real_data_*.csv found -- run a sweep first")
    print("reading:\n  " + "\n  ".join(paths))
    return pd.concat([pd.read_csv(f) for f in paths], ignore_index=True)


TERMS = ["graphcut", "graphcut_st", "graphcut_dcdist", "density", "multivariance",
         "total_multivariance"]
SPLITS = ["spectral", "dcdist", "hdbscan"]


def score_pair(X, A, S):
    """All five unsupervised scores for one candidate subspace."""
    Z = X[:, list(S)]
    g, glab = graphcut_term(Z)
    # ARM, not a replacement: same statistic on a locally-scaled affinity instead of binary kNN.
    # Reported side by side so the comparison is like-for-like on identical candidates.
    gs, gslab = graphcut_term(Z, affinity="selftuning")
    gd, gdlab = graphcut_term_dcdist(Z)
    d, _ = density_term(Z)
    return (dict(graphcut=g, graphcut_st=gs, graphcut_dcdist=gd, density=d,
                 multivariance=multivariance(A, S),
                 total_multivariance=total_multivariance(A, S)),
            {"spectral": glab, "spectral_st": gslab, "dcdist": gdlab,
             "hdbscan": HDBSCAN(min_cluster_size=10, copy=True).fit_predict(Z)})


def one_pair(X, y, A, S):
    sc, labs = score_pair(X, A, S)
    row = dict(subset=str(tuple(S)), **sc)
    for nm, lab in labs.items():
        row[f"ari_{nm}"] = metrics.ari(y, lab) if lab is not None else 0.0
    return row


def analyze(df):
    pd.set_option("display.width", 210)
    print("\n" + "=" * 78)
    print("exp-019 -- SELECTION SIGNALS ON REAL DATA")
    print("=" * 78)
    for (ds, lbl), g in df.groupby(["dataset", "label"]):
        print(f"\n### {ds} / {lbl}  ({len(g)} pairs scored)")
        acols = [c for c in g.columns if c.startswith("ari_")]
        print("\n  achievable ARI by split criterion (max over pairs / mean over pairs):")
        for a in acols:
            print(f"    {a:16s} max {g[a].max():.3f}   mean {g[a].mean():.3f}")

        print("\n  [1] SPEARMAN(score, ARI) -- does the score rank subspaces like ARI does?")
        rows = []
        for t in TERMS:
            r = {"term": t}
            for a in acols:
                v = g[[t, a]].replace(-9.0, np.nan).dropna()
                r[a.replace("ari_", "")] = (spearmanr(v[t], v[a]).statistic
                                            if len(v) > 10 else np.nan)
            rows.append(r)
        print(pd.DataFrame(rows).set_index("term").round(3).to_string())

        print("\n  [2] TOP-10 LIFT -- mean ARI of the 10 best-scoring pairs, minus overall mean")
        rows = []
        for t in TERMS:
            r = {"term": t}
            for a in acols:
                v = g[[t, a]].replace(-9.0, np.nan).dropna()
                r[a.replace("ari_", "")] = (v.nlargest(10, t)[a].mean() - v[a].mean()
                                            if len(v) > 10 else np.nan)
            rows.append(r)
        print(pd.DataFrame(rows).set_index("term").round(3).to_string())
        print("    (a score that picks nothing useful scores ~0 here, by construction)")

    print("\n  [3] DILUTION on real data is in the *_dilution rows of the CSV; see below.")
    dl = df[df.get("kind", "pair") == "dilution"] if "kind" in df.columns else pd.DataFrame()
    if len(dl):
        print(dl.pivot_table(index="term", columns=["dataset", "k"], values="d21").round(2).to_string())


def cohens_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan
    s = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                / max(len(a) + len(b) - 2, 1))
    return float((a.mean() - b.mean()) / s) if s > 1e-12 else np.nan


def dilution_test(X, A, best_pair, p, rng, n_draw=120):
    """exp-018's t2-vs-t1 test with the highest-ARI pair standing in for the true pair.

    NOT a claim that this pair is the biological answer -- it is the best subspace available, and
    the question is whether each score still recognises it once a junk column is mixed in.
    """
    others = [j for j in range(p) if j not in best_pair]
    out = []
    for k in (3, 4):
        t2, t1 = [], []
        for _ in range(n_draw):
            extra = tuple(rng.choice(others, size=k - 2, replace=False))
            t2.append(score_pair(X, A, tuple(sorted(best_pair + extra)))[0])
            half = (best_pair[rng.integers(2)],)
            extra1 = tuple(rng.choice(others, size=k - 1, replace=False))
            t1.append(score_pair(X, A, tuple(sorted(half + extra1)))[0])
        for t in TERMS:
            out.append(dict(kind="dilution", k=k, term=t,
                            d21=cohens_d([r[t] for r in t2], [r[t] for r in t1])))
    return out


def main():
    args = list(sys.argv[1:])
    jobs, max_pairs, n_rows, quick, label = 1, 4000, 600, False, None
    if "--analyze-only" in args:
        analyze(load_all_results()); return
    if "--quick" in args:
        args.remove("--quick"); quick = True; max_pairs = 300
    if "--label" in args:
        i = args.index("--label"); label = args[i + 1]; del args[i:i + 2]
    for flag in ("--jobs", "--max-pairs", "--n"):
        if flag in args:
            i = args.index(flag); v = int(args[i + 1]); del args[i:i + 2]
            jobs = v if flag == "--jobs" else jobs
            max_pairs = v if flag == "--max-pairs" else max_pairs
            n_rows = v if flag == "--n" else n_rows
    datasets = args if args else (["mice"] if quick else ["mice"])
    bad = [d for d in datasets if d not in LOADERS]
    if bad:
        print(f"ERROR: unknown dataset(s) {bad}; valid: {' '.join(LOADERS)}", file=sys.stderr)
        sys.exit(2)

    os.makedirs(OUT_DIR, exist_ok=True)
    allrows, t0 = [], time.time()
    for ds in datasets:
        dsrows = []
        kw = {"n": n_rows}
        # metabric takes `contrast`, mice/har take `label`; pass whichever the loader accepts.
        import inspect as _i
        _params = _i.signature(LOADERS[ds]).parameters
        if label:
            if "label" in _params:
                kw["label"] = label
            elif "contrast" in _params:
                kw["contrast"] = label
        X, y, names = LOADERS[ds](**kw)
        p = X.shape[1]
        pairs = list(itertools.combinations(range(p), 2))
        rng = np.random.default_rng(0)
        n_all = len(pairs)
        if len(pairs) > max_pairs:
            sel = rng.choice(len(pairs), size=max_pairs, replace=False)
            pairs = [pairs[i] for i in sorted(sel)]
            print(f"  {ds}: SAMPLED {len(pairs)} of {n_all} pairs (not silent truncation)",
                  flush=True)
        else:
            print(f"  {ds}: enumerating all {len(pairs)} pairs", flush=True)
        A = centred_distance_matrices(X)
        if jobs == 1:
            rows = [one_pair(X, y, A, S) for S in pairs]
        else:
            from joblib import Parallel, delayed
            rows = Parallel(n_jobs=jobs)(delayed(one_pair)(X, y, A, S) for S in pairs)
        # Record the label ACTUALLY used, read off the loader's own default. Hardcoding a guess
        # here once wrote label="moving" into a har run that was really sitting-vs-standing, which
        # is the kind of provenance error that silently misreads a results file months later.
        import inspect
        _p = (inspect.signature(LOADERS[ds]).parameters.get("label")
              or inspect.signature(LOADERS[ds]).parameters.get("contrast"))
        lbl = label or (_p.default if _p is not None else "class")  # madelon has no label choice
        for r in rows:
            r.update(dataset=ds, label=lbl, kind="pair", n=len(X), p=p,
                     n_pairs_scored=len(pairs), n_pairs_total=n_all)
        allrows.extend(rows); dsrows.extend(rows)
        path = out_path(ds, lbl)
        pd.DataFrame(dsrows).to_csv(path, index=False)
        print(f"    scored ({time.time() - t0:.0f}s) -> {path}", flush=True)

        best = eval(max(rows, key=lambda r: max(r[c] for c in r if c.startswith("ari_")))["subset"])
        print(f"    best pair by ARI: {best} = {names[best[0]][:20]} , {names[best[1]][:20]}",
              flush=True)
        for d in dilution_test(X, A, tuple(best), p, rng):
            d.update(dataset=ds, label=lbl, n=len(X), p=p)
            allrows.append(d); dsrows.append(d)
        pd.DataFrame(dsrows).to_csv(path, index=False)
        print(f"    dilution done ({time.time() - t0:.0f}s) -> {path}", flush=True)

    analyze(pd.DataFrame(allrows))


if __name__ == "__main__":
    main()
