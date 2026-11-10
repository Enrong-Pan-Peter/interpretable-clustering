"""Significance & stability: is an ATOMIC split REAL structure or a search artifact?

Ting's point (2026-07-08): clusters need not match the label/causal features, so a low
ARI does not prove a split is meaningless. But the search hunts for *any* 2-way split, so
"it looks separated in the subspace I selected to look separated" is partly circular. These
two tests settle real-vs-artifact WITHOUT relying on labels:

  * null_separation_test  -- per-feature permutation destroys joint structure but keeps each
    marginal; re-run the FULL search on permuted data. If ATOMIC finds equally-separated
    splits on structureless data, the real split is a garden-of-forking-paths artifact.
    Empirical p = P(null separation >= real separation).
  * subsample_stability   -- re-run on random subsamples; a real structure reproduces the
    same features (Nogueira stability + selection frequency) and the same partition (mean
    ARI vs a reference run); a spurious one does not.

Both re-run the search, so cost ~ (n_runs+1) x one ATOMIC run. Statistic = silhouette of the
best 2-component front solution in ITS OWN subspace (the quantity the search optimises); we
also report feature counts, since silhouette is dimension-sensitive (Phase 2's persistence
will be the cleaner, dimension-robust statistic).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .. import genome as gm
from ..config import AtomicConfig
from ..engine import atomic
from . import metrics


def column_permute(X, rng: np.random.Generator) -> np.ndarray:
    """Shuffle each column independently: keeps every marginal, destroys joint structure."""
    X = np.asarray(X, dtype=float).copy()
    for j in range(X.shape[1]):
        rng.shuffle(X[:, j])
    return X


def best_shot(res, X):
    """Front's 2-component solution with the best silhouette in its own subspace."""
    cands = [i for i in res.quality_front
             if i.quality.labels is not None and i.quality.n_components == 2]
    if not cands:
        return None
    Xf = np.asarray(X, dtype=float)
    return max(cands, key=lambda i: metrics.silhouette(Xf[:, gm.selected_indices(i.genome)],
                                                       i.quality.labels))


def separation_statistic(res, X):
    ind = best_shot(res, X)
    if ind is None:
        return float("-inf"), 0
    V = gm.selected_indices(ind.genome)
    return metrics.silhouette(np.asarray(X, dtype=float)[:, V], ind.quality.labels), int(len(V))


@dataclass
class NullResult:
    real: float
    real_nfeat: int
    null: List[float]
    null_nfeat: List[int]
    p_value: float

    def summary(self) -> str:
        arr = np.array([s for s in self.null if np.isfinite(s)])
        n = len(self.null)
        ge = sum(1 for s in self.null if s >= self.real)
        floor = 1.0 / (1 + n)
        if ge == 0:
            verdict = (f"real exceeds ALL {n} permutations (p<={floor:.3f}; "
                       f"need >=19 perms to formally cross 0.05)")
        elif self.p_value <= 0.05:
            verdict = "REAL structure (p<=0.05)"
        else:
            verdict = "NOT distinguishable from noise"
        return (f"real sil={self.real:+.3f} ({self.real_nfeat} feats) | "
                f"null sil={arr.mean():+.3f}±{arr.std():.3f} (mean {np.mean(self.null_nfeat):.1f} feats) | "
                f"{ge}/{n} null>=real, p={self.p_value:.3f}  ->  {verdict}")


def null_separation_test(X, config: Optional[AtomicConfig] = None,
                         n_permutations: int = 20, base_seed: int = 0) -> NullResult:
    config = config or AtomicConfig()
    X = np.asarray(X, dtype=float)
    real, real_nf = separation_statistic(atomic(X, config, np.random.default_rng(base_seed)), X)
    null, null_nf = [], []
    for i in range(n_permutations):
        Xp = column_permute(X, np.random.default_rng(base_seed + 1000 + i))
        s, nf = separation_statistic(atomic(Xp, config, np.random.default_rng(base_seed + 2000 + i)), Xp)
        null.append(s)
        null_nf.append(nf)
    ge = sum(1 for s in null if s >= real)
    p = (1 + ge) / (1 + n_permutations)          # conservative empirical p-value
    return NullResult(real, real_nf, null, null_nf, p)


def nogueira_stability(selection_vectors) -> float:
    """Nogueira et al. (2018) stability in (-inf, 1]; 1 = identical feature sets every run."""
    Z = np.asarray(selection_vectors, dtype=float)
    if Z.ndim != 2 or Z.shape[0] < 2:
        return float("nan")
    B, p = Z.shape
    pf = Z.mean(axis=0)
    kbar = Z.sum(axis=1).mean()
    denom = (kbar / p) * (1 - kbar / p)
    if denom == 0:
        return float("nan")
    num = ((B / (B - 1.0)) * pf * (1 - pf)).mean()
    return float(1 - num / denom)


@dataclass
class StabilityResult:
    nogueira: float
    mean_partition_ari: float
    n_runs: int
    feature_frequency: Dict[int, float] = field(default_factory=dict)

    def top_features(self, k: int = 8):
        return sorted(self.feature_frequency.items(), key=lambda kv: -kv[1])[:k]

    def summary(self) -> str:
        top = ", ".join(f"f{f}:{v:.2f}" for f, v in self.top_features(6))
        return (f"Nogueira feature-stability={self.nogueira:+.3f} | "
                f"partition reproducibility (mean ARI vs ref)={self.mean_partition_ari:+.3f} | "
                f"n_runs={self.n_runs}\n    top selection freq: {top}")


def subsample_stability(X, config: Optional[AtomicConfig] = None, n_runs: int = 20,
                        frac: float = 0.8, base_seed: int = 0) -> StabilityResult:
    config = config or AtomicConfig()
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    ref = best_shot(atomic(X, config, np.random.default_rng(base_seed)), X)
    ref_labels = ref.quality.labels if ref is not None else None
    vectors, aris = [], []
    for r in range(n_runs):
        idx = np.random.default_rng(base_seed + 100 + r).choice(n, size=max(3, int(round(frac * n))),
                                                                replace=False)
        ind = best_shot(atomic(X[idx], config, np.random.default_rng(base_seed + 300 + r)), X[idx])
        if ind is None:
            continue
        v = np.zeros(p, dtype=int)
        v[gm.selected_indices(ind.genome)] = 1
        vectors.append(v)
        if ref_labels is not None:
            aris.append(metrics.ari(ref_labels[idx], ind.quality.labels))
    freq = {int(f): float(np.mean([v[f] for v in vectors])) for f in range(p)} if vectors else {}
    return StabilityResult(
        nogueira=nogueira_stability(vectors) if len(vectors) >= 2 else float("nan"),
        mean_partition_ari=float(np.mean(aris)) if aris else float("nan"),
        n_runs=len(vectors),
        feature_frequency=freq,
    )
