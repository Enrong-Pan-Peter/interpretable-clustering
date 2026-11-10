"""exp-024 -- can we recover a PUBLISHED biological hierarchy as an interpretable tree?

WHY THIS IS THE PAPER'S CENTREPIECE
-----------------------------------
Every experiment so far has measured ONE split: pick a panel, cut the rows in two, score it. The
actual claim of the project is a RECURSIVE TREE whose every node names a few columns, and no
experiment has ever tested the tree. This one does, which is why it is the interpretability paper's
centrepiece rather than another table.

Levine_32dim is the right place for it. Its 14 gated populations are not a flat list -- they are the
hematopoietic lineage, and immunologists already navigate that lineage exactly the way we propose
to: a recursive hierarchy of low-dimensional gates on named surface markers, drawn by hand. So there
is a published structure to compare against, the output format is the one the field already uses,
and it runs at p=32 where C(32,2)=496 is enumerable, which keeps the search question (exp-023) out
of the way of the interpretability question asked here.

WHAT IS BEING ASKED
-------------------
  [1] SPLIT PURITY. At each node, does the split keep populations intact rather than cutting through
      them? A split that sends ~all of every population present to one side respects the biology
      whatever we then call the two sides. Reported per node two ways: UNWEIGHTED, the mean over
      populations of max(fraction left, fraction right), which counts a 60-cell population and a
      600-cell one equally; and WEIGHTED, the fraction of all cells at the node landing on their own
      population's majority side. 0.5 is chance for a balanced population, 1.0 is perfect.

  [2] DID IT NAME THE RIGHT MARKERS? Where a split corresponds to a lineage boundary an immunologist
      would recognise, the textbook markers are known -- CD3/CD7 for T, CD19/CD22/CD20 for B, CD34
      /CD117 for progenitors, CD4 vs CD8 within T. Reported as the overlap between the panel our
      search chose and that marker set. This is the interpretability claim, and it is the only place
      in the project where a panel-level answer key exists for a MULTI-LEVEL structure.

  [3] WHERE DOES IT ABSTAIN? A node whose best panel does not clear the calibrated-z bar refuses to
      split. Abstaining at a leaf that really is one population is a success; abstaining at the root
      is a failure; splitting confidently through the middle of a population is the worst outcome
      and the reason the calibration machinery exists at all.

TWO MODELLING CHOICES, STATED RATHER THAN BURIED
------------------------------------------------
1. CAPPED SAMPLING (`--cap`, default 60 cells per population). Levine's gated populations run from
   304 cells (HSPC_CD123pos) to 26,366 (CD4 T), an 87x range. Under proportional sampling at any
   tractable n the small populations get 2-3 cells and the question "does the tree find them"
   becomes unaskable. Capping equalises them. It is not neutral -- NCut is sensitive to group
   volume, so equal-sized groups are an easier target than a 0.3% rarity -- and the write-up says
   so. `--proportional` runs the other way for contrast.
2. GLOBAL SCALING, NOT PER-NODE. Columns are min-max scaled once over all 104,184 gated cells and
   never rescaled inside a node. A marker that is already uniform at a node therefore contributes
   almost no distance and the search naturally ignores it, which is the behaviour we want.
   Rescaling per node would inflate whatever noise remained.

THE REFERENCE HIERARCHY IS NOT SCORED AGAINST
----------------------------------------------
Other orderings of the lineage are defensible (myeloid/lymphoid before or after progenitor/mature,
for instance), so nothing here scores "did the tree match our drawing". Purity does not depend on
any reference topology, and the marker check is applied only at boundaries an immunologist would
name without argument.

    python scripts/run_levine_tree.py --quick --jobs 8            # depth 2, cap 40, ~2 min
    python scripts/run_levine_tree.py --jobs 8                    # the real run, ~30 min
    python scripts/run_levine_tree.py --jobs 8 --seed 1           # same, different capped sample
    python scripts/run_levine_tree.py --jobs 8 --proportional     # rare populations left rare
    python scripts/run_levine_tree.py --analyze-only results/levine_tree_cap60_d6_k4_s0.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from functools import partial

from atomicplus.datasets.real import LEVINE_POPULATIONS, load_levine
from atomicplus.evaluation.calibration import grow_from_pairs
from atomicplus.evaluation.stopping import grow_from_pairs_stop
from atomicplus.evaluation.subspace_baselines import density_term, graphcut_term

#: Which term drives the search. `partial` rather than a lambda so joblib can pickle it under
#: --jobs. exp-021 measured that these two behave DIFFERENTLY as stopping rules: the calibrated z of
#: the density term peaks at the true panel size in 80% of cells, graph-cut in only 52%, and on jain
#: graph-cut's z rises monotonically as junk columns are added -- it prefers a padded panel. The
#: first full run of this experiment reproduced that: 35 of 39 nodes grew to max_size instead of
#: stopping. So the term is a flag, not a constant.
TERMS = {"graphcut": graphcut_term,
         "density": density_term,
         "graphcut_st": partial(graphcut_term, affinity="selftuning")}

#: Per-configuration output name. A fixed filename here is how two METABRIC runs were destroyed in
#: exp-022 -- a second run with different settings silently overwrote the first.
def outpath(cfg, proportional):
    tag = f"prop{cfg['n_prop']}" if proportional else f"cap{cfg['cap']}"
    return (f"results/levine_tree_{cfg['term']}_{tag}_d{cfg['depth']}"
            f"_k{cfg['max_size']}_s{cfg['seed']}.json")
BAR = 2.0          # calibrated-z threshold below which a node declines to split (exp-021)
MIN_CELLS = 60     # below this, k=10 neighbours is too large a fraction of the node to score

#: REFERENCE COMPARTMENTS -- the answer key for measurement [2]. Each entry is a set of populations
#: that an immunologist would draw a single gate around, the ONE marker that gate is drawn on, and
#: the other markers that would be accepted as naming the same boundary.
#:
#: Memberships follow the phenotype, not convenience, and the two that look surprising are correct:
#: pro-B cells are CD34+ and so belong in the progenitor compartment (verified in the data: median
#: CD34 is 0.512 in pro_B, above HSPC_CD123pos at 0.483, while every mature population is <0.07);
#: and basophils group with pDCs because both are CD123-high (0.707 and 0.733 against <0.10 for
#: everything else once the CD123+ progenitors are gone).
#:
#: A boundary is only checked when the split draws it EXACTLY, so this table cannot flatter a split
#: that half-drew something. Where several entries describe the same partition at a node, the most
#: specific one is graded and the ties are recorded.
REFERENCE = [
    # (name,                populations,                                        primary, also)
    ("CD34+ progenitor",    {"HSC", "HSPC_CD123neg", "HSPC_CD123pos", "pro_B"}, "CD34", {"CD117", "CD133", "Flt3"}),
    ("HSC (CD38-low)",      {"HSC"},                                            "CD38", {"CD34", "CD45RA"}),
    ("CD123-high",          {"basophil", "pDC"},                                "CD123", {"HLA-DR"}),
    ("pDC",                 {"pDC"},                                            "HLA-DR", {"CD123"}),
    ("basophil",            {"basophil"},                                       "CD123", {"HLA-DR"}),
    ("T cell",              {"CD4_T", "CD8_T"},                                 "CD3", {"CD7", "CD4", "CD8"}),
    ("CD4 T",               {"CD4_T"},                                          "CD4", {"CD3"}),
    ("CD8 T",               {"CD8_T"},                                          "CD8", {"CD3"}),
    ("NK",                  {"NK_CD16neg", "NK_CD16pos"},                       "CD7", {"CD16"}),
    ("CD16+ NK",            {"NK_CD16pos"},                                     "CD16", {"CD7"}),
    ("B lineage",           {"mature_B", "plasma_B", "pre_B", "pro_B"},         "CD19", {"CD22", "CD20"}),
    ("mature B",            {"mature_B", "plasma_B"},                           "CD20", {"CD19", "CD22"}),
    ("plasma B",            {"plasma_B"},                                       "CD38", {"CD20"}),
    ("pre-B",               {"pre_B"},                                          "CD19", {"CD38"}),
    ("monocyte",            {"monocyte"},                                       "CD14", {"CD33", "CD11b", "CD64"}),
    ("myeloid",             {"monocyte", "basophil", "pDC"},                    "CD11c", {"CD11b", "CD33", "CD64", "CD14"}),
    ("lymphoid",            {"CD4_T", "CD8_T", "NK_CD16neg", "NK_CD16pos",
                             "mature_B", "plasma_B", "pre_B"},                  "CD3", {"CD19", "CD7"}),
]


# ------------------------------------------------------------------------------------------------
# Measurements
# ------------------------------------------------------------------------------------------------

MIN_POP = 3        # a population represented by fewer cells than this is not present at a node
MIN_POP_FRAC = 0.02


def present(y_node: np.ndarray) -> list[int]:
    """Population codes genuinely present at a node, i.e. not a handful of cells left behind.

    Splits are never perfectly clean, so a node routinely inherits one or two cells of a population
    that went the other way. Counting those as "present" would corrupt both measurements in the same
    direction: a 1-cell population has purity 1.0 by construction, which inflates the mean, and it
    blocks exact-set boundary naming, which deflates the marker hit rate. Excluding them makes both
    numbers harder to reach, not easier.
    """
    n = len(y_node)
    thr = max(MIN_POP, int(np.ceil(MIN_POP_FRAC * n)))
    return [int(c) for c in np.unique(y_node) if (y_node == c).sum() >= thr]


def purity(y_node: np.ndarray, side: np.ndarray) -> tuple[float, float]:
    """(unweighted, weighted) fraction of each population landing on its own majority side.

    Independent of any reference topology: it asks only whether the split cut THROUGH a population,
    which is the failure mode that makes a tree biologically unreadable. Unweighted treats every
    population as one vote, so a rare one cannot be ignored; weighted is over cells. Both are
    computed over `present` populations only.
    """
    per, kept, tot = [], 0, 0
    for c in present(y_node):
        m = y_node == c
        f = side[m].mean()
        per.append(max(f, 1 - f))
        kept += max(f, 1 - f) * m.sum()
        tot += m.sum()
    if not per:
        return float("nan"), float("nan")
    return float(np.mean(per)), float(kept / max(tot, 1))


def majority_sides(y_node: np.ndarray, side: np.ndarray) -> tuple[set, set]:
    """Population names assigned to each side by majority vote -- the input to boundary naming."""
    left, right = set(), set()
    for c in present(y_node):
        m = y_node == c
        (right if side[m].mean() >= 0.5 else left).add(LEVINE_POPULATIONS[int(c)])
    return left, right


def name_boundary(left: set, right: set) -> dict | None:
    """Which textbook boundary, if any, this split drew. None if it did not draw a clean one.

    A split matches compartment `g` when one side is EXACTLY the populations of `g` present at this
    node and the other side is exactly the rest. Nothing partial counts -- we are not grading a
    split against a boundary it only half-drew. When several compartments describe the same
    partition (separating monocytes from CD4 T is both "monocyte" and "myeloid"), the most specific
    is graded and the others recorded, because grading against the union would inflate the hit rate.
    """
    pops = left | right
    hits = []
    for name, members, primary, also in REFERENCE:
        here = members & pops
        if here and here != pops and (left == here or right == here):
            hits.append((len(members), name, primary, also))
    if not hits:
        return None
    hits.sort()
    _, name, primary, also = hits[0]
    return {"name": name, "primary": primary, "also": sorted(also),
            "ties": [h[1] for h in hits[1:]]}


def minimality(fn, sub: np.ndarray, y_node: np.ndarray, panel: list, names: list) -> dict:
    """Does every marker in the chosen panel earn its place, or is the tail a passenger?

    Re-splits on every (k-1)-subset of the chosen panel and reports the best purity any of them
    reaches. If dropping a marker costs nothing, the stopping rule kept a marker that adds no
    biology -- which matters here more than usual, because a 2-marker gate is a scatter plot an
    immunologist can read and a 4-marker one is not.
    """
    if len(panel) < 3:
        return {}
    full = purity(y_node, fn(sub[:, panel])[1].astype(bool))[0]
    best, drop = -1.0, None
    for j in panel:
        keep = [c for c in panel if c != j]
        lab = fn(sub[:, keep])[1]
        if lab is None or lab.sum() in (0, len(lab)):
            continue
        p = purity(y_node, lab.astype(bool))[0]
        if p > best:
            best, drop = p, j
    return {"purity_full": round(full, 4), "purity_best_drop_one": round(best, 4),
            "droppable": names[drop] if drop is not None else None,
            "cost_of_dropping": round(full - best, 4)}


def describe(y_node: np.ndarray, side: np.ndarray) -> dict:
    """Which populations went which way, by name and count, so a node reads without decoding."""
    left, right = {}, {}
    for c in np.unique(y_node):
        m = y_node == c
        n_r = int(side[m].sum()); n_l = int(m.sum()) - n_r
        nm = LEVINE_POPULATIONS[int(c)]
        if n_l:
            left[nm] = n_l
        if n_r:
            right[nm] = n_r
    return {"left": left, "right": right}


# ------------------------------------------------------------------------------------------------
# The tree
# ------------------------------------------------------------------------------------------------

def split_node(X, y, idx, names, depth, node_id, cfg, log):
    """One node: pair-seeded search for a panel, split on it, recurse. Returns the node dict."""
    sub = X[idx]
    pops = sorted({LEVINE_POPULATIONS[int(c)] for c in y[idx]})
    here = sorted(LEVINE_POPULATIONS[c] for c in present(y[idx]))   # ignoring stragglers
    node = {"id": node_id, "depth": depth, "n": int(len(idx)), "populations": pops,
            "populations_present": here}
    pad = "  " * depth

    if len(idx) < MIN_CELLS or len(here) < 2 or depth >= cfg["depth"]:
        node["leaf"] = True
        node["reason"] = ("too few cells" if len(idx) < MIN_CELLS else
                          "pure" if len(here) < 2 else "depth limit")
        log(f"{pad}[{node_id}] LEAF n={len(idx)} ({node['reason']}) {here}")
        return node

    t0 = time.time()
    # TWO JOBS, TWO TERMS, AND CONFLATING THEM WOULD CONFOUND THE EXPERIMENT.
    #   the SCORING terms decide WHICH panel        (--term)
    #   the SPLIT term decides HOW to cut on it     (--split-term)
    # The two terms cut the same panel differently -- graph-cut takes a spectral bipartition,
    # density a single-linkage one -- so something still has to choose how the cells divide.
    # Keeping graph-cut for the cut leaves this tree comparable with the exp-024 trees, so any
    # difference is attributable to the stopping rule rather than to a different kind of cut.
    fn = TERMS[cfg["split_term"]]
    if cfg["term"] == "combined":
        # exp-027: summing the two SHUFFLE-CALIBRATED terms was the only rule correct on
        # datasets whose right answers differ (3 on the shells, 2 on circles/two-cluster).
        # Each term alone over-grew on one of them; the sum over-grew on neither.
        res = grow_from_pairs_stop([TERMS["graphcut"], TERMS["density"]], sub,
                                   seed_score_fn=TERMS["graphcut"], n_seeds=cfg["seeds"],
                                   max_size=cfg["max_size"], B=cfg["B"], shared_seed=0,
                                   n_reps=cfg["n_reps"], min_gain_se=cfg["min_gain_se"],
                                   n_jobs=cfg["jobs"])
    else:
        res = grow_from_pairs(TERMS[cfg["term"]], sub, n_seeds=cfg["seeds"],
                              max_size=cfg["max_size"], B=cfg["B"], shared_seed=0,
                              n_jobs=cfg["jobs"])
    # Drop panels whose null SD collapsed: sd_floor was substituted, so their z is a ratio to an
    # arbitrary constant and can be arbitrarily large. Thresholding it would manufacture splits.
    n_degen = sum(int(r["degenerate"]) for r in res)
    res = [r for r in res if np.isfinite(r["z"]) and not r["degenerate"]]
    if not res:
        node["leaf"] = True; node["reason"] = f"no scorable panel ({n_degen} degenerate nulls)"
        log(f"{pad}[{node_id}] LEAF n={len(idx)} ({node['reason']})")
        return node
    res.sort(key=lambda r: -r["z"])
    best = res[0]
    panel, z = list(best["panel"]), float(best["z"])
    node["n_degenerate_seeds"] = n_degen

    # The runners-up are kept because an interface should offer them: exp-022 showed the raw score's
    # top-1 pair can be junk while rank 5 is the answer, so a node that shows five panels is honest
    # about the ranking's reliability instead of hiding it.
    node["alternatives"] = [dict(panel=[names[j] for j in r["panel"]], z=round(float(r["z"]), 2),
                                 seed_rank=r["seed_raw_rank"]) for r in res[:5]]

    if z < BAR:
        node["leaf"] = True
        node["reason"] = f"ABSTAIN (z={z:.2f} < {BAR})"
        node["z"] = z
        log(f"{pad}[{node_id}] ABSTAIN n={len(idx)} z={z:.2f} best={[names[j] for j in panel]} {here}")
        return node

    lab = fn(sub[:, panel])[1]
    if lab is None or lab.sum() in (0, len(lab)):
        node["leaf"] = True; node["reason"] = "degenerate split"
        log(f"{pad}[{node_id}] LEAF n={len(idx)} (degenerate split)")
        return node
    side = lab.astype(bool)

    pur_u, pur_w = purity(y[idx], side)
    left, right = majority_sides(y[idx], side)
    bnd = name_boundary(left, right)
    pnames = [names[j] for j in panel]
    node.update(panel=pnames, z=z, z_last=round(float(best["z_last"]), 2),
                purity=pur_u, purity_weighted=pur_w,
                boundary=bnd["name"] if bnd else None, boundary_ties=bnd["ties"] if bnd else [],
                seed_pair=[names[j] for j in best["seed_pair"]],
                seed_raw_rank=best["seed_raw_rank"], went=describe(y[idx], side),
                minimality=minimality(fn, sub, y[idx], panel, names),
                hit_cap=bool(len(panel) >= cfg["max_size"]),
                seconds=round(time.time() - t0, 1), leaf=False)

    # [2] marker check -- only where the split drew a boundary the textbook names
    if bnd:
        node["canonical_primary"] = bnd["primary"]
        node["canonical_also"] = bnd["also"]
        node["primary_hit"] = bnd["primary"] in pnames
        node["any_hit"] = bool(({bnd["primary"]} | set(bnd["also"])) & set(pnames))
    log(f"{pad}[{node_id}] n={len(idx)} panel={pnames} z={z:.1f} purity={pur_u:.3f}/{pur_w:.3f}" +
        (f"  -> {bnd['name']}: primary {bnd['primary']} "
         f"{'NAMED' if node['primary_hit'] else 'MISSED'}" if bnd else "  (no textbook boundary)"))

    node["children"] = [
        split_node(X, y, idx[~side], names, depth + 1, node_id + "L", cfg, log),
        split_node(X, y, idx[side], names, depth + 1, node_id + "R", cfg, log)]
    return node


# ------------------------------------------------------------------------------------------------
# Reporting
# ------------------------------------------------------------------------------------------------

def summarise(tree):
    rows = []

    def walk(n):
        if not n.get("leaf"):
            m = n.get("minimality") or {}
            rows.append(dict(id=n["id"], depth=n["depth"], n=n["n"], purity=n["purity"],
                             pur_w=n["purity_weighted"], z=round(n["z"], 2), k=len(n["panel"]),
                             cap=int(bool(n.get("hit_cap"))),
                             panel=",".join(n["panel"]), boundary=n.get("boundary") or "",
                             primary=n.get("canonical_primary", ""),
                             hit="" if not n.get("boundary") else
                                 ("PRIMARY" if n.get("primary_hit") else
                                  "related" if n.get("any_hit") else "miss"),
                             drop_cost=m.get("cost_of_dropping", np.nan),
                             droppable=m.get("droppable") or ""))
            for c in n["children"]:
                walk(c)
        else:
            rows.append(dict(id=n["id"], depth=n["depth"], n=n["n"], purity=np.nan, pur_w=np.nan,
                             z=round(n["z"], 2) if n.get("z") is not None else np.nan, k=0,
                             cap=0, panel="LEAF: " + n["reason"], boundary="", primary="", hit="",
                             drop_cost=np.nan, droppable=""))
    walk(tree)
    df = pd.DataFrame(rows)
    pd.set_option("display.width", 240)
    print("\n" + "=" * 108 + "\nexp-024 -- LEVINE LINEAGE TREE\n" + "=" * 108)
    print(df.to_string(index=False))

    internal = df[df.purity.notna()]
    print(f"\n[1] SPLIT PURITY -- did splits keep populations intact?")
    print(f"    internal nodes {len(internal)}   leaves {len(df) - len(internal)}")
    if len(internal):
        print(f"    mean purity  unweighted {internal.purity.mean():.3f} | weighted "
              f"{internal.pur_w.mean():.3f}   (0.5 = cuts a population in half, 1.0 = intact)")
        print(f"    worst node   {internal.purity.min():.3f} at "
              f"{internal.loc[internal.purity.idxmin(), 'id']}")
        # BY DEPTH. The first full run showed the tree is excellent at the top and decays with
        # depth, which a single pooled mean hides completely -- so it is printed by default.
        by = internal.groupby("depth").agg(
            nodes=("id", "size"), mean_purity=("purity", "mean"), worst=("purity", "min"),
            median_n=("n", "median"), frac_at_cap=("cap", "mean"))
        ck = internal[internal.boundary != ""]
        if len(ck):
            by = by.join(ck.groupby("depth").agg(
                checkable=("hit", "size"), primary=("hit", lambda s: (s == "PRIMARY").sum()),
                missed=("hit", lambda s: (s == "miss").sum())))
        print("\n    by depth:")
        print("      " + by.to_string().replace("\n", "\n      "))

    chk = internal[internal.boundary != ""]
    print(f"\n[2] DID IT NAME THE RIGHT MARKER? (only at boundaries the textbook names outright)")
    if len(chk):
        for _, r in chk.iterrows():
            print(f"    {r.id:<8s} {r.boundary:<18s} panel {r.panel:<26s} "
                  f"primary {r.primary:<7s} {r.hit}")
        nprim = int((chk.hit == "PRIMARY").sum()); nany = int((chk.hit != "miss").sum())
        # Chance baseline: a panel of k markers drawn at random from p contains the one primary
        # marker with probability k/p. Stated so the hit count is not read as impressive by itself.
        p_tot = 32
        exp_chance = float(sum(r.k / p_tot for _, r in chk.iterrows()))
        print(f"    -> primary marker named at {nprim} of {len(chk)} checkable splits "
              f"({nany} named the primary or a related marker)")
        print(f"       chance expectation for random panels of the same sizes: "
              f"{exp_chance:.2f} of {len(chk)}")
    else:
        print("    no split drew a boundary the textbook names -- nothing checkable.")

    print(f"\n[3] ABSTENTION -- where did it refuse to split?")
    print(f"    abstained {int(df.panel.str.contains('ABSTAIN').sum())}   "
          f"pure leaves {int(df.panel.str.contains('pure').sum())}   "
          f"too few cells {int(df.panel.str.contains('too few').sum())}   "
          f"depth limit {int(df.panel.str.contains('depth limit').sum())}")
    # THE TEST THE ABSTENTION RULE HAS TO PASS: is there any z threshold that separates the splits
    # that cut through populations from the ones that did not? If the two z ranges overlap, no bar
    # can work and abstention is decoration. Printed whether or not it passes.
    bad, good = internal[internal.purity < 0.90], internal[internal.purity >= 0.99]
    if len(bad) and len(good):
        print(f"    splits that cut through a population (purity<0.90): {len(bad)} of "
              f"{len(internal)}; z range {bad.z.min():.2f}-{bad.z.max():.2f}")
        print(f"    clean splits (purity>=0.99): {len(good)}; z range "
              f"{good.z.min():.2f}-{good.z.max():.2f}")
        sep = bad.z.max() < good.z.min()
        print(f"    -> the two z ranges {'SEPARATE' if sep else 'OVERLAP'}, so a z bar "
              f"{'can' if sep else 'CANNOT'} tell them apart"
              f"   (Spearman z vs purity {internal.z.corr(internal.purity, method='spearman'):+.3f})")
    print(f"    panels that grew to max_size instead of stopping: "
          f"{int(internal.cap.sum())} of {len(internal)} -- a stopping rule that always hits the "
          f"cap is a cap, not a stopping rule")

    mini = internal[internal.drop_cost.notna()]
    if len(mini):
        free = mini[mini.drop_cost <= 0.005]
        print(f"\n[4] PANEL MINIMALITY -- did every marker earn its place?")
        print(f"    panels of size>=3: {len(mini)};  {len(free)} lose <=0.005 purity when their "
              f"most droppable marker is removed")
        for _, r in mini.iterrows():
            print(f"    {r.id:<8s} {r.panel:<26s} drop {r.droppable:<8s} costs "
                  f"{r.drop_cost:+.4f} purity")

    print("\n  Purity needs no reference topology; it only asks whether a split cut THROUGH a")
    print("  population. The marker check uses labels and canonical immunology. The search sees")
    print("  neither: it gets 32 unlabelled columns and the calibrated-z stopping rule.")
    return df


# ------------------------------------------------------------------------------------------------

def load_capped(cap: int, seed: int, proportional: bool, n_prop: int):
    """Full gated Levine, min-max scaled globally, then `cap` cells per population (or stratified).

    Scaling happens on all 104,184 cells inside `load_levine`, before the cap, so the column ranges
    are the population-level ones and do not shift with the sample.
    """
    X, y, names = load_levine(n=None, pops="all")
    rng = np.random.default_rng(seed)
    if proportional:
        keep = []
        for c in np.unique(y):
            i = np.flatnonzero(y == c)
            take = max(2, int(round(n_prop * len(i) / len(y))))
            keep.extend(rng.choice(i, size=min(take, len(i)), replace=False))
    else:
        keep = []
        for c in np.unique(y):
            i = np.flatnonzero(y == c)
            keep.extend(rng.choice(i, size=min(cap, len(i)), replace=False))
    keep = np.sort(np.array(keep))
    return X[keep], y[keep], names


def main():
    a = list(sys.argv[1:])
    # min_gain_se defaults to 0 (off): exp-027 measured the noise threshold changing no outcome
    # at three to five times the cost. Kept for deep nodes where few cells make z noisier.
    cfg = dict(depth=6, cap=60, seeds=5, max_size=4, B=15, jobs=1, seed=0, n_prop=800,
               term="graphcut", split_term="graphcut", n_reps=1, min_gain_se=0.0)
    if "--analyze-only" in a:
        i = a.index("--analyze-only")
        if i + 1 >= len(a):
            print("--analyze-only needs a results/levine_tree_*.json path"); sys.exit(2)
        summarise(json.load(open(a[i + 1]))); return
    proportional = "--proportional" in a
    if proportional:
        a.remove("--proportional")
    if "--quick" in a:
        a.remove("--quick"); cfg.update(depth=2, cap=40, seeds=3, max_size=3, B=6)
    for k in list(cfg):
        # accept both --max-size and --max_size; other scripts in this repo use the hyphen
        for f in (f"--{k}", f"--{k.replace('_', '-')}"):
            if f in a:
                i = a.index(f)
                cfg[k] = (a[i + 1] if k in ("term", "split_term")
                          else float(a[i + 1]) if k == "min_gain_se" else int(a[i + 1]))
                del a[i:i + 2]
                break
    if cfg["term"] not in set(TERMS) | {"combined"}:
        print("--term must be one of: " + ", ".join(sorted(set(TERMS) | {"combined"})))
        sys.exit(2)
    if cfg["split_term"] not in TERMS:
        print("--split-term must be one of: " + ", ".join(sorted(TERMS)))
        sys.exit(2)
    if a:
        print(f"unrecognised arguments: {a}"); sys.exit(2)

    X, y, names = load_capped(cfg["cap"], cfg["seed"], proportional, cfg["n_prop"])
    counts = {LEVINE_POPULATIONS[int(c)]: int((y == c).sum()) for c in np.unique(y)}
    print(f"Levine, all gated populations: {X.shape[0]} cells x {X.shape[1]} markers, "
          f"{len(counts)} populations")
    how = "proportional" if proportional else f"capped at {cfg['cap']} per population"
    print(f"  sampling: {how}   {counts}")
    print(f"  config {cfg}\n", flush=True)

    log = lambda s: print(s, flush=True)  # noqa: E731
    t0 = time.time()
    tree = split_node(X, y, np.arange(len(X)), names, 0, "root", cfg, log)
    os.makedirs("results", exist_ok=True)
    tree["_config"] = {**cfg, "proportional": proportional, "bar": BAR, "min_cells": MIN_CELLS}
    out = outpath(cfg, proportional)
    json.dump(tree, open(out, "w"), indent=1)
    print(f"\nwrote {out}  ({time.time() - t0:.0f}s)")
    summarise(tree)


if __name__ == "__main__":
    main()
