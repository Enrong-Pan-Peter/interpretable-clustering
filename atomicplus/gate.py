"""Phase 4 acceptance gate: commit a split only if it is CREDIBLE, not just high-scoring.

From exp-004: the continuous persistence objective alone can't tell a real split from a
cohesive-but-spurious one (it manufactured a high-silhouette split on Biodegradation that sat
inside the permutation null). So each node commits its best split only if it clears:

  1. persistence >= min_persistence   -- cheap threshold;
  2. partition stability              -- re-run the search on subsamples; the split must
                                         reproduce (mean ARI vs. the node split >= stability_min);
  3. [optional] permutation null       -- beat column-permuted data (p <= null_alpha); expensive.

mode="none" applies only (1); "stability" adds (2); "null" adds (2)+(3). Each check re-runs the
search, so the gate costs several searches per node.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .config import AtomicConfig
from .engine import atomic
from .evaluation import metrics
from .evaluation.significance import column_permute


@dataclass
class GateReport:
    passed: bool
    reason: str
    persistence: float
    stability: float = float("nan")
    null_p: float = float("nan")


def _best(X, config: AtomicConfig, seed: int):
    return atomic(np.asarray(X, dtype=float), config, np.random.default_rng(seed)).best()


def partition_stability(X_node, split_labels, config: AtomicConfig,
                        n_sub: int = 5, frac: float = 0.8, base_seed: int = 0) -> float:
    """Mean ARI between the node's split and the split re-found on 80% subsamples."""
    X_node = np.asarray(X_node, dtype=float)
    split_labels = np.asarray(split_labels)
    n = len(X_node)
    aris = []
    for r in range(n_sub):
        idx = np.random.default_rng(base_seed + r).choice(n, size=max(4, int(frac * n)),
                                                          replace=False)
        b = _best(X_node[idx], config, base_seed + 100 + r)
        if b is None or b.quality.labels is None or b.quality.n_components != 2:
            continue
        aris.append(metrics.ari(split_labels[idx], b.quality.labels))
    return float(np.mean(aris)) if aris else float("nan")


def permutation_null_p(X_node, real_score: float, config: AtomicConfig,
                       n_perm: int = 19, base_seed: int = 0) -> float:
    """Empirical p = P(best persistence on column-permuted data >= real persistence)."""
    X_node = np.asarray(X_node, dtype=float)
    ge = 0
    for i in range(n_perm):
        Xp = column_permute(X_node, np.random.default_rng(base_seed + 1000 + i))
        b = _best(Xp, config, base_seed + 2000 + i)
        s = b.quality.f if b is not None else float("-inf")
        if s >= real_score:
            ge += 1
    return (1 + ge) / (1 + n_perm)


def evaluate_gate(X_node, best_split, config: AtomicConfig, mode: str = "none",
                  min_persistence: float = 1.5, stability_min: float = 0.5,
                  null_alpha: float = 0.05, n_sub: int = 5, n_perm: int = 19,
                  base_seed: int = 0) -> GateReport:
    S = float(best_split.quality.f)
    if S < min_persistence:
        return GateReport(False, "low_persistence", S)
    stab = float("nan")
    p = float("nan")
    if mode in ("stability", "null"):
        stab = partition_stability(X_node, best_split.quality.labels, config,
                                   n_sub=n_sub, base_seed=base_seed)
        if not (stab >= stability_min):
            return GateReport(False, f"unstable({stab:.2f})", S, stab, p)
    if mode == "null":
        p = permutation_null_p(X_node, S, config, n_perm=n_perm, base_seed=base_seed)
        if p > null_alpha:
            return GateReport(False, f"null(p={p:.2f})", S, stab, p)
    return GateReport(True, "ok", S, stab, p)
