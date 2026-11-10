"""Fit-only nonlinear proposals for interpretable feature-set discovery.

This normalized kernel similarity is an exploration heuristic, not a p-value,
cluster validity score, or learned representation used by the assignment rule.
"""
from __future__ import annotations

import numpy as np

from .radial_panels import _matrix


def kernel_dependence(X, *, max_bytes=536870912):
    """Centered Gaussian-kernel alignment of squared standardized features.

    Bandwidth is the median strictly positive absolute pairwise difference in
    each squared coordinate. All fitting rows are used, with no labels, search
    rows, random subsampling, or bandwidth sweep. Raw constant columns fail;
    constant squared coordinates contribute zero similarity. The explicit
    allocation guard prevents an accidental dense high-dimensional run.
    """
    X = _matrix(X)
    n, p = X.shape
    if n < 3:
        raise ValueError("at least three fitting observations required")
    scale = X.std(axis=0)
    if np.any(scale <= np.finfo(float).eps):
        raise ValueError("constant features are not supported")
    # Cached flattened kernels plus bounded working matrices/index arrays.
    estimated_bytes = 8 * (p + 8) * n * n
    if not isinstance(max_bytes, int) or max_bytes < 1 or estimated_bytes > max_bytes:
        raise ValueError(f"dense kernel proposals need about {estimated_bytes} bytes; "
                         "use an explicitly evaluated approximation for larger inputs")
    squared = ((X - X.mean(axis=0)) / scale) ** 2
    kernels = np.zeros((p, n * n), dtype=float)
    upper = np.triu_indices(n, 1)
    bandwidths, degenerate = [], []
    for j in range(p):
        differences = np.abs(squared[:, j, None] - squared[None, :, j])
        pair_distances = differences[upper]
        positive = pair_distances[pair_distances > 0.]
        if not len(positive):
            bandwidths.append(None)
            degenerate.append(j)
            continue
        sigma = float(np.median(positive))
        bandwidths.append(sigma)
        with np.errstate(over="ignore", under="ignore"):
            gram = np.exp(-0.5 * (differences / sigma) ** 2)
        means = gram.mean(axis=0)
        centered = gram - means[:, None] - means[None, :] + float(gram.mean())
        norm = float(np.linalg.norm(centered))
        if norm == 0.:
            degenerate.append(j)
        else:
            kernels[j] = centered.ravel() / norm
    dependence = np.clip(kernels @ kernels.T, 0., 1.)
    np.fill_diagonal(dependence, 0.)
    metadata = {"kind": "normalized_centered_rbf_squared", "bandwidths": bandwidths,
                "bandwidth_rule": "median strictly positive absolute pairwise squared-coordinate difference",
                "kernel": "exp(-0.5 * ((u_i-u_j)/bandwidth)^2)",
                "centering": "H K H; H=I-11'/n", "fit_rows": n,
                "degenerate_features": degenerate, "estimated_working_bytes": estimated_bytes,
                "maximum_working_bytes": max_bytes, "subsampled": False,
                "scope": "feature-set proposal similarity only; not an independence test"}
    return dependence, metadata
