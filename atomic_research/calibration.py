"""Frozen size-specific reference units for controlled panel-ranking experiments.

These moments describe a reference mask bank. They are not permutation nulls,
cluster-existence tests, confidence levels, or guarantees of dimension fairness.
No annotation labels are accepted. The historical scorer is left unchanged.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy

import numpy as np

from .search import FrozenObjective

COMPONENTS = ("graphcut", "density")
INVALID_OBJECTIVE = -1e12


class UnsupportedPanelSizeError(ValueError):
    """A panel size lacks enough eligible reference masks for calibration."""


def _panel_key(record: Mapping) -> tuple[int, ...]:
    try:
        panel = tuple(record["panel"])
        if not panel or any(isinstance(j, (bool, np.bool_)) or int(j) != j or j < 0 for j in panel):
            raise ValueError
        panel = tuple(sorted(int(j) for j in panel))
        if len(set(panel)) != len(panel):
            raise ValueError
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Every record needs a nonempty panel of unique nonnegative integer indices") from exc
    return panel


def _finite_components(record: Mapping) -> bool:
    try:
        return bool(all(np.isfinite(float(record[key])) for key in COMPONENTS))
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


class SizeReferenceObjective:
    """Center scores by panel size, with within-size or pooled residual scales.

    Each size must have ``min_count`` reference records satisfying
    ``FrozenObjective.eligible`` and finite graphcut/density values. Reference
    panels must be unique. Unobserved or undersupported sizes are rejected;
    no neighboring-size interpolation or global fallback is performed.

    ``scale_mode='within'`` uses a separate mean and population SD (ddof=0)
    for each size/component. ``'pooled'`` retains those size-specific means,
    but uses the sample-count-weighted within-size residual RMS for each
    component across supported sizes. Between-size mean differences do not
    enter the pooled scale. Both modes floor each scale at ``scale_floor``.
    With one supported size, both equal FrozenObjective's consistent score
    when it receives that same eligible bank and the default scale floor.

    This object never learns from subsequent candidates. ``diagnostics`` and
    ``moments`` return copies, so inspecting them cannot change fitted units.
    """

    def __init__(self, records: Sequence[Mapping], scale_mode: str = "within",
                 min_count: int = 8, scale_floor: float = .001):
        if scale_mode not in ("within", "pooled"):
            raise ValueError("scale_mode must be 'within' or 'pooled'")
        if (isinstance(min_count, (bool, np.bool_))
                or not isinstance(min_count, (int, np.integer)) or min_count < 1):
            raise ValueError("min_count must be a positive integer")
        if not np.isfinite(scale_floor) or scale_floor <= 0:
            raise ValueError("scale_floor must be positive and finite")
        self.scale_mode = scale_mode
        self.min_count = int(min_count)
        self.scale_floor = float(scale_floor)
        counts, values, seen = {}, {}, set()
        for record in records:
            panel = _panel_key(record)
            if panel in seen:
                raise ValueError(f"Duplicate reference panel: {panel}")
            seen.add(panel)
            size = len(panel)
            count = counts.setdefault(size, {"total": 0, "common_eligible": 0, "finite_eligible": 0})
            count["total"] += 1
            if not FrozenObjective.eligible(record):
                continue
            count["common_eligible"] += 1
            if not _finite_components(record):
                continue
            count["finite_eligible"] += 1
            values.setdefault(size, []).append([float(record[key]) for key in COMPONENTS])

        supported = sorted(size for size, count in counts.items() if count["finite_eligible"] >= self.min_count)
        unsupported = sorted(set(counts) - set(supported))
        self._moments = {}
        raw_moments = {}
        squared_residual_sum = np.zeros(len(COMPONENTS))
        supported_count = 0
        for size in supported:
            array = np.asarray(values[size], dtype=float)
            with np.errstate(over="ignore", invalid="ignore"):
                means, stds = array.mean(axis=0), array.std(axis=0, ddof=0)
                residual_sum = np.square(array - means).sum(axis=0)
            if not np.isfinite(np.r_[means, stds, residual_sum]).all():
                raise ValueError("Reference moments overflowed; rescale the component values")
            raw_moments[size] = {key: (float(means[j]), float(stds[j]))
                                 for j, key in enumerate(COMPONENTS)}
            squared_residual_sum += residual_sum
            supported_count += len(array)

        pooled_scales = (np.sqrt(squared_residual_sum / supported_count)
                         if supported_count else np.zeros(len(COMPONENTS)))
        if not np.isfinite(pooled_scales).all():
            raise ValueError("Pooled reference moments overflowed; rescale the component values")
        for size in supported:
            self._moments[size] = {}
            for j, key in enumerate(COMPONENTS):
                mean, within_std = raw_moments[size][key]
                raw_scale = within_std if scale_mode == "within" else float(pooled_scales[j])
                self._moments[size][key] = (mean, max(raw_scale, self.scale_floor))

        self._diagnostics = {
            "scale_mode": self.scale_mode, "min_count": self.min_count,
            "scale_floor": self.scale_floor, "ddof": 0,
            "reference_total": len(seen), "supported_reference_count": supported_count,
            "counts": counts, "supported_sizes": supported,
            "unsupported_sizes": unsupported, "unseen_sizes_unsupported": True,
            "raw_within_moments": raw_moments, "moments": self._moments,
            "raw_pooled_scales": dict(zip(COMPONENTS, map(float, pooled_scales))),
            "pooled_weighting": "reference-count weighted within-size residual RMS; supported sizes only",
            "eligibility": "FrozenObjective.eligible AND finite graphcut/density AND supported size",
            "interpretation": "frozen reference comparison units; not significance or cluster validity",
        }

    @property
    def diagnostics(self) -> dict:
        return deepcopy(self._diagnostics)

    @property
    def moments(self) -> dict:
        return deepcopy(self._moments)

    def eligible(self, record: Mapping) -> bool:
        """Whether this record can be ranked under the fitted reference units."""
        size = len(_panel_key(record))
        return bool(size in self._moments and FrozenObjective.eligible(record)
                    and _finite_components(record))

    def __call__(self, record: Mapping) -> float:
        size = len(_panel_key(record))
        if size not in self._moments:
            count = self._diagnostics["counts"].get(size, {}).get("finite_eligible", 0)
            raise UnsupportedPanelSizeError(
                f"Panel size {size} has {count} eligible reference masks; require {self.min_count}")
        if not self.eligible(record):
            return INVALID_OBJECTIVE
        with np.errstate(over="ignore", invalid="ignore"):
            score = sum((float(record[key]) - self._moments[size][key][0]) /
                        self._moments[size][key][1] for key in COMPONENTS)
        if not np.isfinite(score):
            raise ValueError("Candidate score overflowed; rescale the component values")
        return float(score)
