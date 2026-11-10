"""How many features does a real question actually need? The measurement that decides whether
METABRIC can carry a real-data section.

WHY THIS EXISTS
---------------
The one-column gate said LumA-vs-LumB has "no pair structure": best single gene ARI 0.392, best
pair 0.413. That verdict is misleading and this script is the correction. Two genes being too few
is not the same as the dataset having nothing in it -- PAM50 uses FIFTY genes to make that call,
and LumA/LumB is the hardest of the subtype boundaries. The honest question is not "is there a
pair?" but "how large does the panel have to be, and does a panel of that size exist at all?"

That question also happens to be the one our whole method is stuck on. Every result so far comes
from enumerating PAIRS, which only works because we told the method the answer is a pair. If
METABRIC needs 5 or 8 genes, it becomes the first real dataset where the panel size is genuinely
unknown and larger than two -- which is exactly what a stopping rule has to discover.

WHAT IT MEASURES, AND WHY EACH PIECE IS NEEDED
----------------------------------------------
  [1] THE PUBLISHED PANEL. Cluster on all 50 PAM50 genes. This is the answer key evaluating
      itself, and it is the single most informative number here. If the published 50-gene panel
      scores well on a contrast and our sampled pairs do not, the problem is panel SIZE. If the
      published panel also scores badly, the contrast is simply hard for unsupervised clustering
      and we should not use it, no matter how good the biology sounds.

  [2] NO SELECTION. Cluster on all 250 features. The floor that selection has to beat.

  [3] BEST OF RANDOM, at k = 1, 2, 3, 5, 8. What a blind search actually sees.
      READ THIS AS A LOWER BOUND ONLY. C(250, 8) is about 10^13, so sampling a few thousand
      subsets at k=8 tells you essentially nothing about the best one. A flat random curve is NOT
      evidence that large panels do not help -- it is evidence that random sampling cannot find
      them, which is a different and much less interesting fact.

  [4] GREEDY FORWARD SELECTION ON ARI -- the upper bound, and it USES LABELS.
      Add whichever feature most improves ARI, one at a time. This is an ORACLE: it is not a
      method, it cannot be run without the answer, and it must never be reported as a result of
      ours. It exists to separate "no panel of this size exists" from "we did not sample it",
      which [3] alone cannot do. Without it the whole experiment is uninterpretable.

  [5] THE SAME GREEDY, RESTRICTED TO THE 50 PAM50 GENES. If greedy inside the published panel
      does as well as greedy over all 250, then the panel really does contain the answer and
      selection is a search within it. If greedy over all 250 does much better, the published
      panel is not the ceiling and our "known answer key" claim needs softening.

  [6] TPR / FDR of the greedy panel against PAM50, following GroupFS (AAAI 2026), who use these
      on this exact dataset. TPR = fraction of the 50 panel genes selected; FDR = fraction of
      selections that are distractors. Rank-1 selection accuracy is useless when the answer is
      50 genes -- it is all-or-nothing and cannot tell 40-right from 0-right.

    python scripts/run_panel_size.py                                  # all four contrasts
    python scripts/run_panel_size.py --contrast lumA_lumB --jobs 8
    python scripts/run_panel_size.py --samples 4000 --max-greedy 12 --jobs 8
    python scripts/run_panel_size.py --analyze-only

HOW TO READ THE RESULT. If the greedy curve on LumA/LumB climbs materially from k=2 to k=5-8, the
contrast is in and it is the best real-data test of a stopping rule we could ask for. If it stays
flat near 0.41, the contrast is out and HER2-vs-luminal leads the section instead.
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

from sklearn.cluster import KMeans

from atomicplus.datasets.pam50 import PAM50, canonical
from atomicplus.datasets.real import load_metabric
from atomicplus.evaluation import metrics

OUT = "results/panel_size.csv"
CONTRASTS = ["lumA_lumB", "her2_luminal", "claudinlow_basal", "basal_luminal"]
KS = [1, 2, 3, 5, 8]


def ari(X, y, cols, seed=0):
    Z = X[:, list(cols)]
    return float(metrics.ari(y, KMeans(2, n_init=10, random_state=seed).fit_predict(Z)))


def greedy_oracle(X, y, pool, max_k, seed=0):
    """ORACLE upper bound -- uses the labels. Never report this as a method of ours.

    Answers "does a k-feature panel that separates these classes exist at all", which random
    sampling cannot answer at k >= 5 because the space is astronomically large.
    """
    chosen, trace, remaining = [], [], list(pool)
    for _ in range(max_k):
        best = max(((ari(X, y, chosen + [j], seed), j) for j in remaining), default=None)
        if best is None:
            break
        a, j = best
        chosen.append(j); remaining.remove(j)
        trace.append((len(chosen), a, tuple(chosen)))
    return trace


def run_contrast(contrast, n_rows, n_samples, max_greedy, seed):
    X, y, names = load_metabric(n=n_rows, seed=seed, contrast=contrast)
    p = X.shape[1]
    panel_syms = {canonical(g) for g in PAM50}
    panel = [j for j, nm in enumerate(names) if canonical(nm) in panel_syms]
    junk = [j for j in range(p) if j not in panel]
    rows, rng = [], np.random.default_rng(seed)
    base = dict(contrast=contrast, n=len(X), p=p, n_panel=len(panel), seed=seed)
    print(f"\n### {contrast}   n={len(X)}  p={p}   ({len(panel)} PAM50 genes, {len(junk)} distractors)",
          flush=True)

    # [1] the published panel, and [2] no selection at all
    a_panel, a_all = ari(X, y, panel), ari(X, y, list(range(p)))
    print(f"  [1] all {len(panel)} PAM50 genes        ARI {a_panel:.3f}   <- the published answer key")
    print(f"  [2] all {p} features, no selection  ARI {a_all:.3f}   <- the floor to beat")
    rows += [dict(kind="pam50_panel", k=len(panel), ari=a_panel, **base),
             dict(kind="no_selection", k=p, ari=a_all, **base)]

    # [3] best of random -- a LOWER bound; do not read a flat curve as "large panels don't help"
    print(f"  [3] best of {n_samples} random subsets per size (LOWER bound -- the space is huge):")
    for k in KS:
        space = itertools.combinations(range(p), k)
        subs = ([tuple(sorted(rng.choice(p, size=k, replace=False))) for _ in range(n_samples)]
                if k > 2 or p > 60 else list(space))
        vals = [ari(X, y, s) for s in subs]
        i = int(np.argmax(vals))
        print(f"        k={k:<2d} best {max(vals):.3f}   mean {np.mean(vals):.3f}   "
              f"({len(subs)} sampled)")
        rows.append(dict(kind="random", k=k, ari=float(max(vals)), mean_ari=float(np.mean(vals)),
                         n_sampled=len(subs), subset=str(subs[i]), **base))

    # [4]/[5] greedy oracle over everything, and restricted to the published panel
    for tag, pool in (("greedy_all", list(range(p))), ("greedy_pam50", panel)):
        trace = greedy_oracle(X, y, pool, max_greedy, seed)
        line = "  ".join(f"k={k}:{a:.3f}" for k, a, _ in trace)
        print(f"  [{4 if tag == 'greedy_all' else 5}] {tag:<13s} (ORACLE, uses labels)  {line}")
        for k, a, sub in trace:
            sel = set(sub)
            tpr = len(sel & set(panel)) / max(len(panel), 1)
            fdr = len(sel - set(panel)) / max(len(sel), 1)
            rows.append(dict(kind=tag, k=k, ari=a, subset=str(tuple(names[j] for j in sub)),
                             tpr=tpr, fdr=fdr, **base))
        if tag == "greedy_all" and trace:
            k, a, sub = trace[-1]
            inside = [names[j] for j in sub if j in set(panel)]
            print(f"      [6] at k={k}: TPR {len(set(sub) & set(panel)) / len(panel):.3f}  "
                  f"FDR {len(set(sub) - set(panel)) / len(sub):.3f}   "
                  f"in-panel genes chosen: {inside}")
    return rows


def analyze(df):
    pd.set_option("display.width", 200)
    print("\n" + "=" * 78)
    print("PANEL SIZE ON METABRIC -- how many genes does each contrast need?")
    print("=" * 78)
    for c, g in df.groupby("contrast"):
        pan = g[g.kind == "pam50_panel"].ari.max()
        allf = g[g["kind"] == "no_selection"].ari.max()
        print(f"\n### {c}   published 50-gene panel {pan:.3f} | no selection {allf:.3f}")
        piv = g[g.kind.isin(["random", "greedy_all", "greedy_pam50"])].pivot_table(
            index="kind", columns="k", values="ari")
        print(piv.round(3).to_string())
        gr = g[g.kind == "greedy_all"]
        if len(gr):
            climb = gr[gr.k <= 8].ari.max() - gr[gr.k == 2].ari.max()
            verdict = ("panel size IS the issue; this contrast is IN" if climb > 0.15
                       else "flat; larger panels do not rescue this contrast")
            print(f"  greedy gain from k=2 to k<=8: {climb:+.3f}   <- {verdict}")
    print("\n  greedy_* rows are ORACLE upper bounds computed WITH labels. They say what a panel")
    print("  of that size could achieve, never what our method achieves. random rows are lower")
    print("  bounds -- at k>=5 the subset space is far larger than any sample.")


def main():
    args = list(sys.argv[1:])
    if "--analyze-only" in args:
        analyze(pd.read_csv(OUT)); return
    contrasts, n_rows, n_samples, max_greedy, seed, jobs = CONTRASTS, 600, 2000, 10, 0, 1
    if "--quick" in args:
        args.remove("--quick"); contrasts, n_samples, max_greedy = ["lumA_lumB"], 200, 5
    if "--contrast" in args:
        i = args.index("--contrast"); contrasts = [args[i + 1]]; del args[i:i + 2]
    for flag in ("--n", "--samples", "--max-greedy", "--seed", "--jobs"):
        if flag in args:
            i = args.index(flag); v = int(args[i + 1]); del args[i:i + 2]
            n_rows = v if flag == "--n" else n_rows
            n_samples = v if flag == "--samples" else n_samples
            max_greedy = v if flag == "--max-greedy" else max_greedy
            seed = v if flag == "--seed" else seed
            jobs = v if flag == "--jobs" else jobs

    os.makedirs("results", exist_ok=True)
    t0 = time.time()
    if jobs == 1:
        rows = [r for c in contrasts for r in run_contrast(c, n_rows, n_samples, max_greedy, seed)]
    else:
        from joblib import Parallel, delayed
        rows = [r for blk in Parallel(n_jobs=min(jobs, len(contrasts)))(
            delayed(run_contrast)(c, n_rows, n_samples, max_greedy, seed) for c in contrasts)
            for r in blk]
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {OUT} ({len(df)} rows, {time.time() - t0:.0f}s)")
    analyze(df)


if __name__ == "__main__":
    main()
