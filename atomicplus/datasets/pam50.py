"""The PAM50 gene panel -- our first real dataset with a PUBLISHED answer key for SELECTION.

WHY THIS FILE MATTERS MORE THAN IT LOOKS
----------------------------------------
Every dataset used in this project so far (the six synthetic shapes, Mice Protein Expression, UCI
HAR) has labels but no published feature panel. That capped everything: we could score whether the
CLUSTERING was right, never whether the SELECTION was right on real data. PAM50 is 50 named genes
published as the panel for the breast-cancer intrinsic subtypes, so for the first time "did the
method name the right features?" has an answer somebody else wrote down.

SOURCE. Parker et al., "Supervised risk predictor of breast cancer based on intrinsic subtypes",
J Clin Oncol 27(8):1160-1167, 2009. The symbol list below was taken from a public implementation
(github.com/elswob/BASALT, R/subtype_functions.R) and cross-checked to be exactly 50 symbols; it
matches the list shipped in the Bioconductor `genefu` package. If a reviewer asks, cite Parker 2009.

LEGACY SYMBOLS. Three entries are pre-HGNC-rename names and expression matrices vary in which they
use. ALIASES maps old <-> new so a match is found either way. Always report how many of the 50 were
actually located in the matrix -- a silent 43/50 match would quietly change the answer key.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Set

PAM50: List[str] = [
    "ACTR3B", "ANLN", "BAG1", "BCL2", "BIRC5", "BLVRA", "CCNB1", "CCNE1", "CDC20", "CDC6",
    "CDCA1", "CDH3", "CENPF", "CEP55", "CXXC5", "EGFR", "ERBB2", "ESR1", "EXO1", "FGFR4",
    "FOXA1", "FOXC1", "GPR160", "GRB7", "KIF2C", "KNTC2", "KRT14", "KRT17", "KRT5", "MAPT",
    "MDM2", "MELK", "MIA", "MKI67", "MLPH", "MMP11", "MYBL2", "MYC", "NAT1", "ORC6L",
    "PGR", "PHGDH", "PTTG1", "RRM2", "SFRP1", "SLC39A6", "TMEM45B", "TYMS", "UBE2C", "UBE2T",
]
assert len(PAM50) == 50 and len(set(PAM50)) == 50, "PAM50 list must be exactly 50 unique symbols"

#: old symbol -> current HGNC symbol. Applied in both directions by `expand_aliases`.
ALIASES: Dict[str, str] = {"CDCA1": "NUF2", "KNTC2": "NDC80", "ORC6L": "ORC6"}


def expand_aliases(symbols: Sequence[str] = tuple(PAM50)) -> Set[str]:
    """Every spelling of every panel gene, so a match is found whichever convention a matrix uses."""
    out: Set[str] = set()
    for s in symbols:
        out.add(s)
        if s in ALIASES:
            out.add(ALIASES[s])
        for old, new in ALIASES.items():
            if s == new:
                out.add(old)
    return out


def canonical(symbol: str) -> str:
    """Fold a symbol onto its current HGNC name so the two spellings never count as two genes."""
    return ALIASES.get(symbol, symbol)
