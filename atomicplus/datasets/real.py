"""Real datasets: Madelon, UCI HAR, Mice Protein Expression.

WHY THESE THREE
---------------
Everything so far has been our own synthetic generator, and we already found once that a
generator can leak its answer in ways nobody noticed (see the benchmark-flaw finding: four of six
shapes gave up the planted pair to a one-column test). Real data cannot be flattered that way.

What we need from a real dataset: enough features that selection is a genuine problem, clusters
living in a subset of them, continuous values, enough rows for kNN density estimates, and labels.

| dataset | n     | p   | classes | full pair enumeration? | known panel |
|---------|-------|-----|---------|------------------------|-------------|
| madelon | 2000  | 500 | 2       | 124,750 pairs - no     | NOT shipped, see below |
| har     | 7352  | 561 | 6       | 157,080 pairs - no     | none |
| mice    | 1080  | 77  | 8       | 2,926 pairs - YES      | none |

`mice` is the only one where we can enumerate every pair, which makes it the natural first target.

MADELON AND ITS PANEL -- READ BEFORE CLAIMING ANYTHING
------------------------------------------------------
Madelon (NIPS 2003 feature-selection challenge, Guyon et al.) was built with 5 informative
features, 15 redundant linear combinations of them, and 480 pure distractors. The counts are
published; **the identities of those 20 columns are NOT in the distributed files.** So out of the
box Madelon scores clustering quality, not selection accuracy.

`madelon_derived_panel()` recovers a panel with random-forest importance against a permutation
null. That is standard practice for this dataset, but it is DERIVED, not ground truth, and it is
supervised -- we would be using labels to define the target that our unsupervised method is then
scored against. State that plainly wherever it is used, or use Madelon for clustering only.

Note also that a marginal (one-column) test CANNOT recover the panel here: Madelon's class is
XOR-like on hypercube vertices, so the informative features are individually near-useless. That
is exactly the jointly-necessary structure we care about, and it is why the recovery has to be
multivariate.

SUBSAMPLING
-----------
Our scores are O(n^2) in memory per candidate subset. HAR at n=7352 needs a 432 MB distance
matrix per subset, which is not workable. All loaders therefore subsample rows, stratified by
class, with a fixed seed. Default n=600. Pass n=None to get everything and accept the cost.
"""
from __future__ import annotations

import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from ..preprocessing import preprocess

RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uci", "raw")


def _subsample(X: np.ndarray, y: np.ndarray, n: int | None, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Stratified row subsample, so class proportions survive."""
    if n is None or n >= len(X):
        return X, y
    rng = np.random.default_rng(seed)
    keep: List[int] = []
    for c in np.unique(y):
        idx = np.flatnonzero(y == c)
        take = max(2, int(round(n * len(idx) / len(y))))
        keep.extend(rng.choice(idx, size=min(take, len(idx)), replace=False))
    keep = np.sort(np.array(keep))
    return X[keep], y[keep]


def load_madelon(n: int | None = 600, seed: int = 0) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """2000 x 500, 2 balanced classes. 20 real features among 480 distractors (identities unknown)."""
    d = os.path.join(RAW, "madelon", "MADELON")
    X = np.loadtxt(os.path.join(d, "madelon_train.data"))
    y = np.loadtxt(os.path.join(d, "madelon_train.labels")).astype(int)
    X, y = _subsample(X, y, n, seed)
    return preprocess(pd.DataFrame(X)).to_numpy(), y, [f"f{i}" for i in range(X.shape[1])]


def load_har(n: int | None = 600, seed: int = 0,
             label: str = "sit_stand") -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """7352 x 561 engineered accelerometer/gyroscope features.

    LABEL CHOICE DECIDES WHETHER THIS DATASET TESTS ANYTHING. Measured one-column
    recoverability (best ARI from 2-means on a SINGLE column, n=600):

        moving        (dynamic vs static)   1.000   -- 205 of 561 columns beat ARI 0.5
        stand_vs_lay                        1.000   -- 13 columns beat 0.5
        walk_vs_up                          0.618
        up_vs_down                          0.577
        sit_stand     (sitting vs standing) 0.409   -- ZERO columns beat 0.5

    "moving" is therefore USELESS for us: the answer is available one column at a time, which is
    exactly the flaw we found and fixed in the synthetic benchmark. It would hand out free marks
    and test nothing about joint necessity. DEFAULT IS sit_stand, the classic hard HAR contrast
    (both postures are static with near-identical accelerometer signatures), which no single
    column solves.

    Options: "sit_stand" (default), "up_down", "moving" (trivial, kept only for comparison),
    "activity" (all 6 -- but a 2-way splitter cannot fairly be asked to recover 6 groups).
    """
    d = os.path.join(RAW, "human+activity+recognition+using+smartphones", "har_files")
    X = np.loadtxt(os.path.join(d, "X_train.txt"))
    y = np.loadtxt(os.path.join(d, "y_train.txt")).astype(int)
    names = [ln.split(None, 1)[1].strip() for ln in open(os.path.join(d, "features.txt"))]
    # 1 WALKING  2 WALKING_UPSTAIRS  3 WALKING_DOWNSTAIRS  4 SITTING  5 STANDING  6 LAYING
    if label == "moving":
        y = (y <= 3).astype(int)
    elif label in ("sit_stand", "up_down"):
        a, b = (4, 5) if label == "sit_stand" else (2, 3)
        m = np.isin(y, [a, b])
        X, y = X[m], (y[m] == a).astype(int)
    elif label != "activity":
        raise ValueError("label must be sit_stand | up_down | moving | activity")
    X, y = _subsample(X, y, n, seed)
    return preprocess(pd.DataFrame(X)).to_numpy(), y, names


def load_mice(n: int | None = 600, seed: int = 0, label: str = "Genotype",
              aggregate: str = "animal") -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """72 animals x 15 technical replicates x 77 proteins. Has missing values.

    *** READ THIS BEFORE USING THE DEFAULT n=600 WITH aggregate="none". ***

    The file has 1080 ROWS but only **72 ANIMALS**. MouseIDs run `309_1 ... 309_15`: fifteen
    technical replicates per animal. All four labels (Genotype, Treatment, Behavior, class) are
    ANIMAL-level properties, constant across an animal's fifteen rows, and the replicates are near
    duplicates of one another in feature space.

    Treating rows as independent samples is pseudo-replication: any clustering that separates
    ANIMALS scores well against any label without having found the biology, and the effective
    sample size is 72, not 1080. This invalidated exp-019's mice results (see docs/CORRECTIONS.md
    C8), which is why `aggregate="animal"` is now the DEFAULT.

      aggregate="animal"  median over each animal's replicates -> 72 rows. Correct, and small.
      aggregate="none"    the raw 1080 rows. ONLY for reproducing the old, invalid numbers.

    At 72 rows the density and graph-cut terms have few neighbours to work with; if they stop
    separating anything, that is a finding about the dataset's usable size, not a bug.

    LABEL CHOICE MATTERS AND IS NOT COSMETIC. The 8-way `class` is a 2x2x2 design
    (Genotype x Treatment x Behavior), so those eight groups need not be geometrically separable
    in any 2-D subspace at all -- asking a 2-way splitter to recover them is unfair to the method
    and uninformative about it. The three binary factors are the honest targets for a bipartition:
      Genotype  control vs trisomic (the Down-syndrome model) -- default, most biologically real
      Treatment saline vs memantine
      Behavior  context-shock vs shock-context
    Pass label="class" for the 8-way version, but read the caveat above before quoting it.

    The 1396 missing cells go through our standard 2-NN imputation inside `preprocess`.
    """
    f = os.path.join(RAW, "mice+protein+expression", "Data_Cortex_Nuclear.xls")
    # Legacy .xls needs xlrd, which pandas does not pull in by default. Convert once to CSV and
    # cache it, so xlrd is needed only on the first run and never again on this machine.
    cache = f.replace(".xls", ".cached.csv")
    if os.path.exists(cache):
        m = pd.read_csv(cache)
    else:
        try:
            m = pd.read_excel(f)
        except ImportError as e:
            raise ImportError(
                "Reading Data_Cortex_Nuclear.xls needs the `xlrd` package (legacy .xls format).\n"
                "    pip install xlrd\n"
                "After the first successful read this file is cached as CSV and xlrd is no longer "
                "needed."
            ) from e
        m.to_csv(cache, index=False)
    if label not in m.columns:
        raise ValueError(f"label must be one of {[c for c in m.columns if m[c].dtype == object]}")
    if aggregate not in ("animal", "none"):
        raise ValueError('aggregate must be "animal" or "none"')

    if aggregate == "animal":
        # MouseID is "<animal>_<replicate>"; strip the replicate suffix and collapse.
        animal = m["MouseID"].astype(str).str.rsplit("_", n=1).str[0]
        n_before, n_animals = len(m), animal.nunique()
        num = m.select_dtypes("number").groupby(animal).median()
        lab = m.groupby(animal)[label].agg(lambda s: s.iloc[0])
        # A label that varies within an animal would mean the ID parse is wrong -- fail loudly.
        bad = m.groupby(animal)[label].nunique()
        if (bad > 1).any():
            raise ValueError(f"{int((bad > 1).sum())} animals have inconsistent {label}; "
                             f"the MouseID parse is wrong, do not silently average over this")
        y = pd.Categorical(lab.loc[num.index]).codes.astype(int)
        print(f"    mice: collapsed {n_before} replicate rows -> {n_animals} animals "
              f"(median over replicates). Effective n is {n_animals}.")
    else:
        num = m.select_dtypes("number")
        y = pd.Categorical(m[label]).codes.astype(int)

    X, y = _subsample(num.to_numpy(dtype=float), y, n, seed)
    return preprocess(pd.DataFrame(X)).to_numpy(), y, list(num.columns)


def load_metabric(n: int | None = 600, seed: int = 0, contrast: str = "lumA_lumB",
                  reduced: str | None = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """METABRIC breast cancer expression -- the first dataset here with a PUBLISHED feature panel.

    Reads the cached matrix written by `scripts/reduce_metabric.py`; it does NOT touch the 689 MB
    raw file. Run the reduction once first.

    THE POINT. PAM50 (Parker et al., JCO 2009) is 50 published genes for the intrinsic subtypes,
    so selection accuracy is scorable against somebody else's answer key rather than proxied by
    clustering quality. The reduced matrix is those 50 genes plus randomly-chosen non-PAM50 genes
    as distractors -- our synthetic design, on real data.

    CONTRAST CHOICE DECIDES WHETHER THIS DATASET TESTS ANYTHING. Our splitter is binary; PAM50 is
    five-way. Subtype counts in the full cohort:
        LumA 700 | LumB 475 | Her2 224 | claudin-low 218 | Basal 209 | Normal 148 | NC 6

      "lumA_lumB"       (1175) DEFAULT. The clinically hard one: both luminal, separated mainly by
                        proliferation, and no single gene is expected to solve it. This is the
                        breast-cancer analogue of HAR's sitting-vs-standing.
      "basal_luminal"   (1384) Expected to FAIL the one-column gate -- ESR1 alone should separate
                        these. Kept for comparison, the same way HAR's "moving" is.
      "her2_luminal"    (1399) Middle case; ERBB2/GRB7 may carry it alone.
      "claudinlow_basal" (427) The free second contrast METABRIC gives us over TCGA.

    RUN `scripts/run_one_column_gate.py metabric` BEFORE SCORING ANYTHING. That check has already
    caught two unusable dataset/label pairs (jain+spiral on our own generator, HAR moving-vs-still).
    A prestigious dataset is not exempt.
    """
    d = os.path.join(RAW, "..", "..", "brca_metabric")
    if reduced is None:
        cands = sorted(f for f in os.listdir(d) if f.startswith("reduced_") and f.endswith(".csv"))
        if not cands:
            raise FileNotFoundError(
                "No reduced METABRIC matrix found. Run:\n"
                "    python scripts/reduce_metabric.py\n"
                "once; it turns the 689 MB expression file into a small cached CSV.")
        reduced = cands[-1]
    m = pd.read_csv(os.path.join(d, reduced), index_col=0)
    sub = m.pop("CLAUDIN_SUBTYPE")

    groups = {"lumA_lumB": (["LumA"], ["LumB"]),
              "basal_luminal": (["Basal"], ["LumA", "LumB"]),
              "her2_luminal": (["Her2"], ["LumA", "LumB"]),
              "claudinlow_basal": (["claudin-low"], ["Basal"])}
    if contrast not in groups:
        raise ValueError(f"contrast must be one of {sorted(groups)}")
    a, b = groups[contrast]
    keep = sub.isin(a + b).to_numpy()
    X, y = m.to_numpy(dtype=float)[keep], sub[keep].isin(a).to_numpy().astype(int)
    X, y = _subsample(X, y, n, seed)
    return preprocess(pd.DataFrame(X)).to_numpy(), y, list(m.columns)


LOADERS = {"madelon": load_madelon, "har": load_har, "mice": load_mice,
           "metabric": load_metabric}


def madelon_derived_panel(n_estimators: int = 500, n_perm: int = 20,
                          seed: int = 0) -> List[int]:
    """Recover Madelon's ~20 real features by random-forest importance vs a permutation null.

    DERIVED, NOT GROUND TRUTH, AND SUPERVISED. The real identities were never released. We keep a
    feature if its importance exceeds the maximum importance seen across `n_perm` runs with the
    labels shuffled -- i.e. above anything pure chance produced for this many features and rows.

    Circularity warning: this uses labels to define the target an unsupervised method is then
    scored against. It is the standard approach for Madelon and it is defensible, but it must be
    labelled as derived in any writeup, and the panel it returns should be sanity-checked against
    the published counts (5 informative + 15 redundant = 20).
    """
    from sklearn.ensemble import RandomForestClassifier
    X, y, _ = load_madelon(n=None)
    rf = RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1)
    imp = rf.fit(X, y).feature_importances_
    rng = np.random.default_rng(seed)
    null = 0.0
    for _ in range(n_perm):
        r = RandomForestClassifier(n_estimators=max(100, n_estimators // 5),
                                   random_state=seed, n_jobs=-1)
        null = max(null, r.fit(X, rng.permutation(y)).feature_importances_.max())
    return sorted(int(i) for i in np.flatnonzero(imp > null))


# ------------------------------------------------------------------------------------------------
# Levine_32dim -- mass cytometry. The best-matched dataset in this project, for four reasons:
#   1. 32 markers => C(32,2) = 496 pairs, FULLY ENUMERABLE. For the first time we can score every
#      pair exhaustively AND run the search on the same data, so "did the search find what
#      enumeration would have found" is directly measurable. On METABRIC (250 features) a search
#      failure and a sampling failure were indistinguishable.
#   2. The 14 population labels come from MANUAL GATING by the original authors -- an answer key
#      produced independently of any clustering of this data.
#   3. Gating strategies are published and mostly TWO MARKERS per split (CD4 T vs CD8 T is CD4/CD8;
#      B vs T is CD19/CD3), so a true PAIR exists and TPR/FDR against it are computable. That is
#      what we wanted from PAM50 and did not get -- PAM50 is a 50-gene 5-way classifier, not a gate.
#   4. Immunologists already analyse this as a recursive hierarchy of 2-D gates on named markers,
#      by hand. That IS our interpretable tree; the domain invented the output format.
#
# Levine, Simonds, Bendall et al., "Data-Driven Phenotypic Dissection of AML Reveals
# Progenitor-like Cells that Correlate with Prognosis", Cell 162(1):184-197, 2015. Benchmark
# preparation: github.com/lmweber/benchmark-data-Levine-32-dim.
#
# 265,627 cells from two healthy donors; 104,184 carry a gate label, 161,443 are "unassigned".
# Unassigned cells are DROPPED by default -- they are cells the human gater could not place, so
# including them would score us against an absence of ground truth rather than against ground truth.

#: Non-protein columns in the FCS. Everything else is one of the 32 surface markers.
_LEVINE_NON_MARKER = {"Time", "Cell_length", "DNA1", "DNA2", "Viability",
                      "file_number", "event_number", "label", "individual"}

#: Cell counts per label code, from the file itself. Used only as a sanity check on load.
LEVINE_COUNTS = {1: 1207, 2: 3905, 3: 2248, 4: 3295, 5: 304, 6: 916, 7: 26366,
                 8: 20108, 9: 16520, 10: 21099, 11: 1238, 12: 330, 13: 6135, 14: 513}

#: Code -> population name. The FCS ships numeric codes only, so this mapping was DERIVED FROM THE
#: DATA by `levine_population_profile()` rather than guessed: each code's marker fingerprint was
#: matched to the canonical immunophenotype. Every assignment below is unambiguous and the cell
#: counts agree with expectation (CD4 T largest, plasma B smallest). Re-derive with
#: `levine_population_profile()` if anything upstream changes.
#:     1  CD123+ HLA-DR-           -> basophils (HLA-DR is what separates them from pDCs)
#:     2  CD7+ CD16-               -> CD16- NK
#:     3  CD16+ CD7+               -> CD16+ NK
#:     4  CD34+ CD38+ CD117+ HLA-DR+ -> CD34+CD38+CD123- HSPC
#:     5  CD123+ CD34+ HLA-DR+     -> CD34+CD38+CD123+ HSPC
#:     6  CD34+ CD117+ CD38-lo     -> CD34+CD38lo HSC
#:     7  CD3+ CD4+                -> CD4 T
#:     8  CD8+ CD3+                -> CD8 T
#:     9  CD19+ CD22+ CD20+ HLA-DR+ -> mature B
#:    10  CD64+ CD11c+ CD11b+      -> monocytes
#:    11  CD123+ HLA-DR+           -> pDC
#:    12  CD38-hi CD19+ CD20-      -> plasma B
#:    13  CD38+ CD19+ HLA-DR+      -> pre-B
#:    14  CD38+ CD34+ CD19+        -> pro-B (CD34 separates pro- from pre-)
LEVINE_POPULATIONS = {1: "basophil", 2: "NK_CD16neg", 3: "NK_CD16pos", 4: "HSPC_CD123neg",
                      5: "HSPC_CD123pos", 6: "HSC", 7: "CD4_T", 8: "CD8_T", 9: "mature_B",
                      10: "monocyte", 11: "pDC", 12: "plasma_B", 13: "pre_B", 14: "pro_B"}

#: Named contrasts, each with the PUBLISHED GATING MARKERS that define it -- the first true
#: answer key at PANEL level this project has had. `true_panel` is what a correct selection should
#: name, so TPR/FDR against it are computable (PAM50 could not give us this: it is a 50-gene 5-way
#: classifier, not a two-marker gate).
LEVINE_CONTRASTS = {
    # Both populations are CD3+ T cells, so CD3 is useless and CD4/CD8 is the whole answer.
    # The two largest populations, and the cleanest 2-marker gate in the panel.
    "cd4t_cd8t":      dict(pops=(7, 8),   true_panel=("CD4", "CD8")),
    # Both are CD123+, so CD123 alone cannot separate them; HLA-DR is the discriminator.
    # A deliberately hard case where the obvious single marker fails.
    "basophil_pdc":   dict(pops=(1, 11),  true_panel=("HLA-DR", "CD123")),
    "nk16neg_nk16pos": dict(pops=(2, 3),  true_panel=("CD16", "CD7")),
    # Pro-B are CD34+, pre-B are not; both CD19+CD38+.
    "preb_prob":      dict(pops=(13, 14), true_panel=("CD34", "CD19")),
    # Easy control, expected to fall to a single marker -- the analogue of HAR "moving".
    "monocyte_bcell": dict(pops=(10, 9),  true_panel=("CD19", "CD64")),
}


def levine_population_profile(top: int = 4, n_per_pop: int | None = 2000, seed: int = 0):
    """Marker fingerprint per label code, so populations can be NAMED FROM THE DATA.

    For each gated population, returns the markers whose mean expression is furthest above the
    mean over all other gated cells. This is how we assign biological names without guessing a
    mapping, and it doubles as a check that the file parsed correctly: if the population with the
    highest CD3 and CD4 is not one of the two largest, something is wrong upstream.
    """
    X, y, names = load_levine(n=None, pops="all", seed=seed)
    out = {}
    for c in np.unique(y):
        m = y == c
        d = X[m].mean(0) - X[~m].mean(0)
        idx = np.argsort(-d)[:top]
        out[int(c)] = [(names[i], round(float(d[i]), 3)) for i in idx]
    return out


def load_levine(n: int | None = 600, seed: int = 0, pops=(7, 8), contrast: str | None = None,
                path: str | None = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Levine_32dim mass cytometry, as a binary (or multi-class) contrast between gated populations.

    `pops` is a pair of LABEL CODES, e.g. (7, 8) for the two largest populations, or "all" to keep
    every gated cell. Codes rather than names because the code->name mapping is not in the file;
    see `levine_population_profile()`.

    TRANSFORM. Mass cytometry counts are arcsinh-transformed with cofactor 5 before anything else.
    That is the field standard, not a preference -- raw ion counts are heavily right-skewed and
    every published analysis of this data applies it. Our usual min-max scaling runs afterwards so
    the columns match every other loader.

    Needs `flowio` (pip install flowio). Do NOT use `fcsparser`: it pins numpy<2 and tries to build
    numpy 1.26 from source, which fails on Python 3.13+ without a C compiler.
    """
    try:
        import flowio
    except ImportError as e:                                        # noqa: F841
        raise ImportError("Reading Levine_32dim.fcs needs flowio:\n    pip install flowio") from e
    f = os.path.join(RAW, "..", "..", "Levine_32dim.fcs") if path is None else path
    if not os.path.exists(f):
        raise FileNotFoundError(
            f"{f} not found. Get it with:\n"
            "    git clone https://github.com/lmweber/benchmark-data-Levine-32-dim\n"
            "and put data/Levine_32dim.fcs under data/.")
    if contrast is not None:
        if contrast not in LEVINE_CONTRASTS:
            raise ValueError(f"contrast must be one of {sorted(LEVINE_CONTRASTS)}")
        pops = LEVINE_CONTRASTS[contrast]["pops"]
    fd = flowio.FlowData(f)
    A = np.reshape(fd.events, (-1, fd.channel_count))
    cols = [fd.text[f"p{i}n"] for i in range(1, fd.channel_count + 1)]
    markers = [c for c in cols if c not in _LEVINE_NON_MARKER]
    lab = A[:, cols.index("label")]

    keep = ~np.isnan(lab)                                   # drop the 161,443 ungated cells
    if pops != "all":
        a, b = pops
        for c in (a, b):
            if c not in LEVINE_COUNTS:
                raise ValueError(f"label code {c} not in {sorted(LEVINE_COUNTS)}")
        keep &= np.isin(lab, [a, b])
    Xm = A[np.ix_(np.flatnonzero(keep), [cols.index(m) for m in markers])]
    y = lab[keep].astype(int)
    if pops != "all":
        y = (y == pops[0]).astype(int)

    Xm = np.arcsinh(Xm / 5.0)                               # mass-cytometry standard, cofactor 5
    Xm, y = _subsample(Xm, y, n, seed)
    return preprocess(pd.DataFrame(Xm)).to_numpy(), y, markers


LOADERS["levine"] = load_levine
