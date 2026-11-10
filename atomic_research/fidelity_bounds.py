"""Simultaneous validation bounds for a fixed family of panel predictors.

Each error is disagreement with a frozen full-panel model, not an external
class label. Conditional on discovery data, validation rows must be iid and
independent of training; all candidate masks, fitted rules, label orientations,
and the teacher must be frozen before seeing validation. Bonferroni does not
require independence between candidates, but it does require counting the
entire prespecified family (including invalid or unselected candidates).

These bounds concern fidelity to a particular learned model. They establish
neither cluster existence nor biological usefulness nor feature recovery.
There is deliberately no test-data argument and no fitting in this module.
"""

from __future__ import annotations

import math
from numbers import Integral, Real

from scipy.stats import beta


def _integer(value: object, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    result = int(value)
    if result < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return result


def _probability(value: object, name: str, *, open_interval: bool) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real probability")
    result = float(value)
    permitted = 0 < result < 1 if open_interval else 0 <= result <= 1
    if not math.isfinite(result) or not permitted:
        interval = "(0, 1)" if open_interval else "[0, 1]"
        raise ValueError(f"{name} must be finite and in {interval}")
    return result


def binomial_upper_bound(errors: int, n: int, alpha: float = .05) -> float:
    """One-sided (1-alpha) Clopper-Pearson upper bound on error probability.

    For k < n the bound is Beta(k+1, n-k)'s upper-alpha quantile;
    all n errors gives 1. The zero-error formula uses expm1 for accuracy.
    Counts must be integers (booleans and integral-valued floats are rejected).
    """
    count = _integer(errors, "errors")
    total = _integer(n, "n", minimum=1)
    level = _probability(alpha, "alpha", open_interval=True)
    if count > total:
        raise ValueError("errors must not exceed n")
    if count == total:
        return 1.0
    if count == 0:
        return -math.expm1(math.log(level) / total)
    # isf avoids rounding 1-alpha to 1 for small Bonferroni-adjusted alpha.
    result = float(beta.isf(level, count + 1, total - count))
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise ValueError("binomial upper bound could not be computed finitely")
    return result


def select_prefix(
    records: list[dict],
    max_error: float = .05,
    alpha: float = .05,
    family_size: int | None = None,
) -> dict:
    """Select the smallest valid frozen panel under empirical/bounded error.

    Each record contains panel (a nonempty list of unique nonnegative integer
    indices), errors, n, and valid (a bool). All records use the same positive
    validation n. Records must be nonempty; no eligible panel is represented by
    None. Panel order is preserved and breaks equal-size ties lexicographically.

    family_size defaults to len(records), and must be at least len(records).
    When separate calls share a validation set, supply the total number of
    prespecified candidates across calls for a joint Bonferroni guarantee.
    Annotations are returned on copies; neither records nor panels are changed.
    The caller is responsible for fixed, training-only prefix construction.
    """
    level = _probability(alpha, "alpha", open_interval=True)
    threshold = _probability(max_error, "max_error", open_interval=False)
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a nonempty list")
    count = _integer(
        len(records) if family_size is None else family_size,
        "family_size", minimum=1,
    )
    if count < len(records):
        raise ValueError("family_size must be at least len(records)")
    try:
        adjusted_alpha = level / count
    except OverflowError as exc:
        raise ValueError("family_size is too large for a finite adjustment") from exc
    if adjusted_alpha == 0:
        raise ValueError("alpha/family_size underflows to zero")

    annotated = []
    common_n = None
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"records[{index}] must be a dict")
        required = {"panel", "errors", "n", "valid"}
        if not required.issubset(record):
            raise ValueError(f"records[{index}] must contain {sorted(required)}")
        panel = record["panel"]
        if not isinstance(panel, list) or not panel:
            raise ValueError(f"records[{index}].panel must be a nonempty list")
        panel = [_integer(feature, "panel feature") for feature in panel]
        if len(set(panel)) != len(panel):
            raise ValueError(f"records[{index}].panel must contain unique features")
        if not isinstance(record["valid"], bool):
            raise ValueError(f"records[{index}].valid must be a bool")
        total = _integer(record["n"], "n", minimum=1)
        errors = _integer(record["errors"], "errors")
        if errors > total:
            raise ValueError("errors must not exceed n")
        if common_n is None:
            common_n = total
        elif common_n != total:
            raise ValueError("all records must have the same validation n")
        annotated.append({
            **record,
            "panel": panel,
            "errors": errors,
            "n": total,
            "point_error": errors / total,
            "upper_error": binomial_upper_bound(errors, total, adjusted_alpha),
        })

    def choose(metric: str) -> list[int] | None:
        candidates = [
            row for row in annotated
            if row["valid"] and row[metric] <= threshold
        ]
        if not candidates:
            return None
        winner = min(candidates, key=lambda row: (len(row["panel"]), row["panel"]))
        return list(winner["panel"])

    return {
        "records": annotated,
        "empirical_panel": choose("point_error"),
        "bounded_panel": choose("upper_error"),
        "family_size": count,
        "alpha": level,
        "max_error": threshold,
    }
