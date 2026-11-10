"""Fair-evaluation harness: internal metrics (silhouette, Davies-Bouldin) scored in
BOTH the full space and the selected subspace, plus space-invariant external metrics
(ARI, NMI). This is the machinery that answers "is ATOMIC's advantage real or a
metric-space artifact?" See architecture.md Part 2.3.
"""
from . import baselines, harness, metrics  # noqa: F401

__all__ = ["metrics", "baselines", "harness"]
