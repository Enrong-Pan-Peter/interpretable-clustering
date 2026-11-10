"""Diversity of alternative panels -- the EA's contribution greedy cannot give.

Greedy / L1 / random each return ONE feature set. NSLC returns MANY: distinct minimal feature
panels that all induce (essentially) the SAME split. This counts them: among the archive's
2-component solutions whose partition matches the canonical (best) split within ARI >= agreement,
how many DISTINCT feature sets are there? (plan: "same membership, different features; ARI >= 0.98")
"""
from __future__ import annotations

from typing import List, Tuple

from .. import genome as gm
from . import metrics


def alternative_panels(res, agreement: float = 0.98, min_persistence: float = 1.1,
                       max_features: int = None) -> List[Tuple[int, ...]]:
    """Distinct feature panels inducing the canonical split (ARI >= agreement to it)."""
    best = res.best()
    if best is None or best.quality.labels is None:
        return []
    canon = best.quality.labels
    panels = {}
    for g, ev in zip(res.archive.genomes, res.archive.evals):
        if ev.labels is None or ev.n_components != 2 or ev.f < min_persistence:
            continue
        feats = tuple(sorted(int(i) for i in gm.selected_indices(g)))
        if max_features is not None and len(feats) > max_features:
            continue
        if metrics.ari(canon, ev.labels) >= agreement:
            panels[feats] = ev.f
    return sorted(panels.keys(), key=lambda f: (len(f), -panels[f]))


def n_alternative_panels(res, **kw) -> int:
    return len(alternative_panels(res, **kw))
