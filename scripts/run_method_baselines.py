"""Tier A/B/C method comparison -- the experiment that decides whether there is a paper.

THE QUESTION
------------
Our own notes say the working fix "isn't novel, it's just density-based subspace clustering".
That has never been measured. This script measures it, and separates the two things most
clustering evaluations conflate:

    TIER A  full task: the method must FIND a subspace and CLUSTER in it.
            -> atomicplus (graph-cut + density hybrid), density-only, graphcut-only, SUBCLU.
    TIER B  clustering only, FULL space, no selection: k-means, spectral, HDBSCAN, and a
            full-space single-linkage persistence split standing in for HTC.
            -> A vs B answers "does subspace selection actually buy anything?"
    TIER C  clustering only, given the ORACLE subspace (the true informative dims).
            -> B vs C answers "was the failure in selection or in the split?"  This is the
               ceiling; no realistic method can beat it.

FAIRNESS PROTOCOL (identical for every method -- change it here, not per-method)
-------------------------------------------------------------------------------
1. Every method sees the SAME preprocessed matrix and the same candidate space (2-D subspaces).
2. Where a method has its own unsupervised model-selection rule, it uses it (k-means/spectral
   pick k by silhouette; SUBCLU picks eps by density validity of its own output).
3. Where a rule does not exist, we ALSO report an ORACLE-tuned column (the hyperparameter that
   maximises that method's ARI). Oracle columns are upper bounds the method cannot reach in
   practice. They exist so we cannot be accused of sandbagging a baseline. If atomicplus only
   wins against self-tuned baselines and not oracle-tuned ones, SAY SO in the writeup.
4. k (kNN graph) = 10 and core_k = 5 are CONVENTIONAL DEFAULTS, NOT TUNED, for our method.
   Their sensitivity is the separate run_sensitivity.py experiment. Do not quote this table as
   evidence our defaults are good.

WHICH SUBCLU TIE-BREAK IS THE HEADLINE (decision rule, fixed in advance)
------------------------------------------------------------------------
SUBCLU has NO native ranking over the subspaces it returns, so every tie-break here is OUR
addition, not SUBCLU's own ability. There is therefore no "unboosted SUBCLU" to protect -- the
only question is which addition gives the STRONGEST REASONABLE baseline.

RULE: the headline number uses whichever label-free tie-break scores highest ON SUBCLU'S OWN
mean rank-1 across all shapes. That choice is made from SUBCLU's numbers alone and NEVER by
which one leaves the largest gap in our favour. All four columns are reported regardless.

Choosing among defensible tie-breaks by which makes us look best would be benchmark-hacking even
though each tie-break is individually legitimate. Note also the symmetry: our own hybrid is a
combination rule WE picked after seeing that it beat graph-cut alone. Denying SUBCLU a tuned
ranking rule while keeping our own tuned combination would be a double standard.

`ORACLEtiebreak` and `ORACLEall` use ground truth and are NOT candidates for the headline; they
are upper bounds that quantify how much of SUBCLU's gap is ranking rather than finding.

KNOWN NON-EQUIVALENCE (state this in the paper; do not pretend it away)
-----------------------------------------------------------------------
SUBCLU searches subspaces of any dimensionality and returns a SET of them; we cap it at 2-D so
its search space matches ours, and we report both `hit_any` (true subspace returned at all --
generous) and rank-1 (committed to one answer -- like-for-like). The full-space persistence run
is a STAND-IN for HTC, not HTC: HTC does persistent-homology H0 in the full space, which is the
property we are probing, but it is not the same code. Label it as a stand-in.

RUN
---
    # smoke test (~1 min)
    python scripts/run_method_baselines.py --quick

    # the real run -- do this in your own terminal, it is long
    python scripts/run_method_baselines.py --seeds 20 --ps 12,20,40 \
        moons circles jain flame spiral gauss2

Results append incrementally to results/method_baselines.csv, so an interrupted run is not lost.
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

from sklearn.cluster import HDBSCAN

from atomicplus import preprocess
from atomicplus.datasets import synthetic as syn
from atomicplus.datasets.structured_noise import make_noise_matrix, verify_noise_is_uninformative
from atomicplus.evaluation import baselines as bl
from atomicplus.evaluation import metrics
from atomicplus.evaluation.subspace_baselines import (
    cart_on_kmeans, density_term, graphcut_term, imm_tree, subclu_candidates,
    subclu_retrieval_stats, zscore,
)
from atomicplus.persistence import persistence_split

DATA2D = os.path.join(os.path.dirname(__file__), "..", "2d_data")
KNOWN_DATASETS = ["moons", "circles", "jain", "flame", "spiral", "gauss2"]
INF = [3, 8]                       # the planted informative dimensions (same as every other script)
EPS_GRID = [0.03, 0.05, 0.08, 0.12, 0.18, 0.25]
MIN_PTS = 5                        # matches core_k=5; conventional, not tuned


# ------------------------------------------------------------------------------------------
# data (identical to run_fitness_sweep.py so numbers are comparable across experiments)
# ------------------------------------------------------------------------------------------
def load(name, p, seed):
    rng = np.random.default_rng(seed)
    if name in ("moons", "circles"):
        g = syn.moons_subspace if name == "moons" else syn.circles_subspace
        X, y, _ = g(n=260, p=p, informative=INF, rng=rng)
        return preprocess(X).to_numpy(), y
    if name == "gauss2":                       # convex control: this one should be easy
        X, y, _ = syn.two_cluster_subspace(n=260, p=p, informative=INF, sep=0.6,
                                           std=0.05, rng=rng)
        return preprocess(X).to_numpy(), y
    a = np.loadtxt(os.path.join(DATA2D, f"{name}.txt"), skiprows=1)
    xy = a[:, :2].astype(float)
    yy = a[:, 2].astype(int)
    xy = (xy - xy.min(0)) / (np.ptp(xy, 0) + 1e-12)
    X = rng.random((len(xy), p))
    X[:, INF[0]], X[:, INF[1]] = xy[:, 0], xy[:, 1]
    return preprocess(pd.DataFrame(X)).to_numpy(), yy


def picture_2d(name, seed):
    """The bare 2-D picture (n,2) plus labels, before any junk columns are added."""
    rng = np.random.default_rng(seed)
    if name in ("moons", "circles"):
        g = syn.moons_subspace if name == "moons" else syn.circles_subspace
        X, y, _ = g(n=260, p=2, informative=[0, 1], rng=rng)
        return np.asarray(X, dtype=float), y
    if name == "gauss2":
        X, y, _ = syn.two_cluster_subspace(n=260, p=2, informative=[0, 1], sep=0.6,
                                           std=0.05, rng=rng)
        return np.asarray(X, dtype=float), y
    a = np.loadtxt(os.path.join(DATA2D, f"{name}.txt"), skiprows=1)
    xy = a[:, :2].astype(float)
    xy = (xy - xy.min(0)) / (np.ptp(xy, 0) + 1e-12)
    return xy, a[:, 2].astype(int)


def load_structured(name, p, seed, profile="structured"):
    """Same pictures, harder junk columns. See atomicplus/datasets/structured_noise.py.

    NOTE this deliberately does NOT reproduce `load()` bit-for-bit even at profile="uniform":
    the random draws happen in a different order. Compare distributions over seeds between the
    two benchmarks, not individual seeds.
    """
    xy, y = picture_2d(name, seed)
    n = len(xy)
    rng = np.random.default_rng(50_000 + seed)
    noise = make_noise_matrix(n, p - 2, rng, profile=profile)
    X = np.empty((n, p), dtype=float)
    others = [j for j in range(p) if j not in INF]
    X[:, INF[0]], X[:, INF[1]] = xy[:, 0], xy[:, 1]
    X[:, others] = noise
    return preprocess(pd.DataFrame(X)).to_numpy(), y


def split_labels(Z, how):
    """The three split criteria, applied to an already-chosen subspace."""
    if how == "spectral":
        _, lab = graphcut_term(Z)
        return lab
    if how == "hdbscan":
        return HDBSCAN(min_cluster_size=10, copy=True).fit_predict(Z)
    if how == "persistence":
        return persistence_split(Z, min_cluster_size=5, mutual_reachability=True,
                                 core_k=5, normalize="none").labels
    raise ValueError(how)


def score(y, lab):
    if lab is None:
        return 0.0, 0.0
    return metrics.ari(y, lab), metrics.nmi(y, lab)


# ------------------------------------------------------------------------------------------
def evaluate_one(name, p, seed, noise="uniform"):
    """Returns a list of result rows for one (dataset, p, seed) cell."""
    rows = []
    Xp, y = load(name, p, seed) if noise == "uniform" else load_structured(name, p, seed, noise)
    pairs = list(itertools.combinations(range(p), 2))
    true_idx = pairs.index(tuple(INF))

    def add(tier, method, ari, nmi, **kw):
        rows.append(dict(dataset=name, p=p, seed=seed, noise=noise, tier=tier, method=method,
                         ari=ari, nmi=nmi, **kw))

    # ---------------- TIER A: selection + clustering ----------------
    # One pass over all pairs; every enumeration-based selector reuses these scores.
    gc, de = [], []
    gc_lab = {}
    for pr in pairs:
        Z = Xp[:, list(pr)]
        g, gl = graphcut_term(Z)
        d, _ = density_term(Z)
        gc.append(g)
        de.append(d)
        gc_lab[pr] = gl
    gc = np.asarray(gc)
    de = np.asarray(de)
    signals = {
        "atomicplus_hybrid": zscore(gc) + zscore(de),   # Ryan's graph-cut + density
        "density_only": de,                             # pure DBCV-style = SUBCLU-family signal
        "graphcut_only": gc,
    }

    for sig_name, sig in signals.items():
        order = np.argsort(-sig)
        sel = pairs[int(order[0])]
        rank1 = int(order[0] == true_idx)
        true_rank = int(np.flatnonzero(order == true_idx)[0]) + 1
        Zs = Xp[:, list(sel)]
        # No single split wins every shape (HANDOFF 3.3). Report each split separately rather
        # than silently picking the best -- picking the best per shape IS the cherry-pick we
        # are trying not to commit. The null-calibrated meta-chooser is the intended fix.
        for how in ("spectral", "hdbscan", "persistence"):
            lab = gc_lab[sel] if how == "spectral" else split_labels(Zs, how)
            a, nm = score(y, lab)
            add("A", f"{sig_name}+{how}", a, nm, sel_rank1=rank1, sel_true_rank=true_rank,
                sel_subspace=str(sel), n_candidates=len(pairs))

    # ---------------- TIER A: SUBCLU, under four tie-breaks ----------------
    # SUBCLU returns a SET of subspaces and provides no way to rank them. Which tie-break we
    # impose is OUR choice, so a single tie-break invites the objection that we handicapped the
    # baseline. We therefore report four, two realistic and two unreachable:
    #   selftuned      eps by density validity, subspace by density validity   (realistic)
    #   tb_coverage    eps by density validity, subspace by points covered     (realistic, alt)
    #   ORACLEtiebreak eps by density validity, subspace by best ARI  <- the key column: this is
    #                  "SUBCLU picks the best subspace it actually returned", i.e. exactly how
    #                  much of the gap is ranking rather than finding.
    #   ORACLEall      eps by best ARI, subspace by best ARI          (absolute upper bound)
    per_eps = []
    for eps in EPS_GRID:
        try:
            cands = subclu_candidates(Xp, eps=eps, min_pts=MIN_PTS, max_dim=2, dim=2)
        except Exception:                                  # noqa: BLE001
            continue
        if not cands:
            continue
        info = {}
        for s, lab in cands.items():
            keep = np.flatnonzero(lab >= 0)
            v = -9.0
            if len(keep) >= 4 and len(np.unique(lab[keep])) >= 2:
                v, _ = density_term(Xp[np.ix_(keep, list(s))])
            a, nm = score(y, lab)
            info[s] = dict(validity=v, coverage=len(keep), ari=a, nmi=nm)
        picks = {
            "density": max(info, key=lambda s: info[s]["validity"]),
            "coverage": max(info, key=lambda s: info[s]["coverage"]),
            "oracle": max(info, key=lambda s: info[s]["ari"]),
        }
        per_eps.append(dict(eps=eps, info=info, picks=picks,
                            hit_any=int(tuple(INF) in cands), n=len(cands),
                            self_score=info[picks["density"]]["validity"],
                            oracle_ari=info[picks["oracle"]]["ari"]))

    # BOTH VIEWS ARE RECORDED, EVERY RUN. SUBCLU returns an unordered SET, so rank-1 accuracy
    # measures a tie-break we bolted on rather than the algorithm. The retrieval view (recall /
    # precision / random-pick over the returned list) needs no invented ranking and is the fairer
    # one to the baseline; the best-case tie-break view answers "even at its best, can it commit
    # to the right answer". They tell different stories and both are true. Which one goes in the
    # paper is a writing decision -- see HANDOFF section 4 item 6. Do not drop either here.
    if not per_eps:
        for tag in ("subclu_selftuned", "subclu_tb_coverage", "subclu_ORACLEtiebreak",
                    "subclu_ORACLEall"):
            add("A", tag, 0.0, 0.0, sel_rank1=0, sel_hit_any=0, eps=np.nan, n_subspaces=0,
                **{k: 0.0 for k in ("subclu_recall", "subclu_precision", "subclu_f1",
                                    "subclu_n_returned", "subclu_random_pick")})
    else:
        e_self = max(per_eps, key=lambda d: d["self_score"])
        e_orac = max(per_eps, key=lambda d: d["oracle_ari"])
        for tag, blk, tb in (("subclu_selftuned", e_self, "density"),
                             ("subclu_tb_coverage", e_self, "coverage"),
                             ("subclu_ORACLEtiebreak", e_self, "oracle"),
                             ("subclu_ORACLEall", e_orac, "oracle")):
            s = blk["picks"][tb]
            add("A", tag, blk["info"][s]["ari"], blk["info"][s]["nmi"],
                sel_rank1=int(tuple(s) == tuple(INF)), sel_hit_any=blk["hit_any"],
                eps=blk["eps"], n_subspaces=blk["n"], sel_subspace=str(s),
                **subclu_retrieval_stats(list(blk["info"]), tuple(INF)))

    # ---------------- TIER A: interpretable trees (IMM / CART-on-kmeans) ----------------
    # These pick features via tree splits rather than by scoring subspaces, so rank-1 on a PAIR
    # is not a meaningful measure for them (IMM with k=2 makes one split and so uses exactly one
    # feature -- it CANNOT return a pair). We record how many features the tree used and how many
    # of those were informative, which is the like-for-like interpretability comparison.
    k_true = len(np.unique(y[y >= 0])) if (y >= 0).any() else 2
    for fn, tag in ((imm_tree, "imm_tree"), (cart_on_kmeans, "cart_on_kmeans")):
        try:
            lab, used = fn(Xp, k=k_true)
        except Exception:                                  # noqa: BLE001
            continue
        a, nm = score(y, lab)
        add("A", tag, a, nm, n_feats_used=len(used),
            n_informative_used=len(set(used) & set(INF)),
            only_informative=int(bool(used) and set(used) <= set(INF)),
            sel_subspace=str(tuple(used)))

    # ---------------- TIER B: full space, no selection ----------------
    # Two groups: (i) standard off-the-shelf clusterers, (ii) OUR OWN three split criteria run
    # on the full space. Group (ii) is what makes B comparable to A method-for-method -- the
    # only difference from Tier A is that no subspace was selected.
    lab, _ = bl.kmeans_best(Xp); add("B", "kmeans_full", *score(y, lab))
    lab, _ = bl.spectral_best(Xp); add("B", "spectral_full", *score(y, lab))
    lab, _ = bl.hdbscan_best(Xp); add("B", "hdbscan_full", *score(y, lab))
    for how in ("spectral", "hdbscan", "persistence"):
        tag = "persistence_full_HTCstandin" if how == "persistence" else f"split_{how}_full"
        add("B", tag, *score(y, split_labels(Xp, how)))

    # ---------------- TIER C: oracle subspace ----------------
    # NOT a global ceiling -- it is the ceiling FOR THESE CLUSTERERS. A Tier-A method using a
    # split not represented here can legitimately exceed a Tier-C number, so the matched
    # `split_*_oracle` rows below are the ones to compare Tier A against.
    Zt = Xp[:, INF]
    lab, _ = bl.kmeans_best(Zt); add("C", "kmeans_oracle", *score(y, lab))
    lab, _ = bl.spectral_best(Zt); add("C", "spectral_oracle", *score(y, lab))
    lab, _ = bl.hdbscan_best(Zt); add("C", "hdbscan_oracle", *score(y, lab))
    for how in ("spectral", "hdbscan", "persistence"):
        add("C", f"split_{how}_oracle", *score(y, split_labels(Zt, how)))
    # DBSCAN on the oracle subspace: this is the row that bounds SUBCLU, whose split IS DBSCAN.
    # Without it SUBCLU can appear to beat "the ceiling" simply because its split criterion was
    # absent from Tier C (this happened on spiral in the first full run).
    for eps in EPS_GRID:
        from sklearn.cluster import DBSCAN
        add("C", f"dbscan_oracle_eps{eps}", *score(y, DBSCAN(eps=eps,
                                                             min_samples=MIN_PTS).fit_predict(Zt)))
    return rows


# ------------------------------------------------------------------------------------------
def main():
    args = list(sys.argv[1:])
    seeds, ps, quick, jobs, noise = 20, [12, 20, 40], False, 1, "uniform"
    if "--quick" in args:
        args.remove("--quick"); quick = True; seeds, ps = 2, [12]
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = int(args[i + 1]); del args[i:i + 2]
    if "--ps" in args:
        i = args.index("--ps"); ps = [int(x) for x in args[i + 1].split(",")]; del args[i:i + 2]
    if "--jobs" in args:
        i = args.index("--jobs"); jobs = int(args[i + 1]); del args[i:i + 2]
    if "--noise" in args:
        i = args.index("--noise"); noise = args[i + 1]; del args[i:i + 2]
    datasets = args if args else (["moons", "circles"] if quick else list(KNOWN_DATASETS))

    # Fail fast and legibly on a bad dataset name. Without this a typo dies deep inside a joblib
    # worker as an unrelated-looking FileNotFoundError. The backslash case is called out because
    # PowerShell does NOT accept `\` as a line continuation (it uses a backtick), so a pasted
    # bash-style multi-line command silently turns `\` into an argument.
    bad = [d for d in datasets if d not in KNOWN_DATASETS]
    if bad:
        print(f"ERROR: unknown dataset name(s): {bad}", file=sys.stderr)
        print(f"       valid names: {' '.join(KNOWN_DATASETS)}", file=sys.stderr)
        if any(set(b) <= {"\\", "`", "/"} for b in bad):
            print("\n       That looks like a line-continuation character that reached Python as an\n"
                  "       argument. PowerShell uses a backtick (`), not a backslash (\\). Simplest\n"
                  "       fix is to put the whole command on one line.", file=sys.stderr)
        sys.exit(2)

    os.makedirs("results", exist_ok=True)
    outp = "results/method_baselines.csv" if noise == "uniform" else f"results/method_baselines_{noise}.csv"
    rows = []
    t0 = time.time()
    for name in datasets:
        for p in ps:
            if jobs == 1:
                for seed in range(seeds):
                    rows.extend(evaluate_one(name, p, seed, noise))
            else:
                # Parallel over SEEDS only -- seeds are independent, and every method is
                # deterministic given (dataset, p, seed), so results are identical to --jobs 1.
                from joblib import Parallel, delayed
                for chunk in Parallel(n_jobs=jobs)(
                        delayed(evaluate_one)(name, p, s, noise) for s in range(seeds)):
                    rows.extend(chunk)
            pd.DataFrame(rows).to_csv(outp, index=False)        # incremental save
            print(f"  done {name} p={p}   ({time.time() - t0:.0f}s elapsed)", flush=True)

    df = pd.DataFrame(rows)
    print(f"\nwrote {outp}  ({len(df)} rows)")
    print("\n== mean ARI by tier x method x p ==")
    print(df.pivot_table(index=["tier", "method"], columns="p", values="ari",
                         aggfunc="mean").round(2).to_string())
    print("\n== TIER A selection accuracy (rank-1 = committed to the true subspace) ==")
    a = df[df.tier == "A"]
    print(a.pivot_table(index="method", columns="p", values="sel_rank1",
                        aggfunc="mean").round(2).to_string())
    if "sel_hit_any" in a.columns:
        h = a.dropna(subset=["sel_hit_any"])
        if len(h):
            print("\n== SUBCLU hit_any (true subspace returned at all -- generous to SUBCLU) ==")
            print(h.pivot_table(index="method", columns="p", values="sel_hit_any",
                                aggfunc="mean").round(2).to_string())
    print("\n== headline: does selection buy anything? ==")
    print("   A = found its own subspace | B = full space, no selection | C = given the oracle")
    print("   NOTE C is the ceiling for THESE clusterers, not a global ceiling; compare A to the")
    print("   matched split_*_oracle rows, not to max(C).")
    # Best METHOD per tier by MEAN ari over seeds. Do NOT use .max() over raw rows here: that
    # maxes over seeds too, which reports a best-case run rather than typical behaviour and can
    # make a Tier-A method look like it beat the oracle ceiling.
    per = df.groupby(["dataset", "p", "tier", "method"])["ari"].mean().reset_index()
    print(per.groupby(["dataset", "p", "tier"])["ari"].max().unstack().round(2).to_string())
    print("\n== matched comparison: same split criterion, three levels of subspace knowledge ==")
    mt = df[df.method.str.contains("split_|atomicplus_hybrid|persistence_full|persistence_oracle")]
    print(mt.pivot_table(index="dataset", columns="method", values="ari",
                         aggfunc="mean").round(2).to_string())


if __name__ == "__main__":
    main()
