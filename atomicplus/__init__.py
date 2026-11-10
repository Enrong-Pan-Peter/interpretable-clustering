"""ATOMIC+ — a clean-room re-implementation of ATOMIC (Vandergrift & Hu, GECCO '24
Companion) plus the fair-evaluation harness for the follow-up project.

See architecture.md for the full map. Quick start:

    import numpy as np
    from atomicplus import atomic, AtomicConfig, preprocess

    Xp = preprocess(df)                      # 2-NN impute + [0,1] scale
    res = atomic(Xp.to_numpy(), AtomicConfig(seed=0))
    best = res.best()                        # highest-f, fewest-feature solution
    print(res.k_tilde, best.quality.size, best.quality.f)
"""
from .config import AtomicConfig
from .engine import AtomicResult, Individual, atomic
from .preprocessing import knn_impute, minmax01, preprocess

__all__ = [
    "atomic",
    "AtomicConfig",
    "AtomicResult",
    "Individual",
    "preprocess",
    "knn_impute",
    "minmax01",
]
