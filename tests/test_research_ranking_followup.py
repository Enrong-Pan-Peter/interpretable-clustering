"""Checks for a ranking-only experiment with unchanged candidate banks."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ranking_followup", ROOT / "scripts/run_research_ranking_followup.py")
followup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(followup)


def test_reference_masks_are_unique_balanced_and_reproducible():
    panels = followup.reference_panels(20, {1, 2, 5, 8}, 12, 71)
    assert panels == followup.reference_panels(20, {1, 2, 5, 8}, 12, 71)
    assert len(panels) == len(set(panels)) == 48
    for size in (1, 2, 5, 8):
        assert sum(len(panel) == size for panel in panels) == 12
    assert all(len(set(panel)) == len(panel) for panel in panels)
    assert len(followup.reference_panels(3, {1, 2, 3}, 12, 0)) == 7


def test_winner_selection_does_not_use_annotations_or_add_candidates():
    rows = [{"panel": [1, 3], "valid": True, "legacy_valid": True, "objective": 2., "diagnostic_train_ari": .01},
            {"panel": [2], "valid": True, "legacy_valid": True, "objective": 1., "diagnostic_train_ari": 1.0},
            {"panel": [4], "valid": False, "legacy_valid": True, "objective": 100., "diagnostic_train_ari": 1.0}]
    before = deepcopy(rows)
    winner = followup.pick(rows, lambda r: r["objective"])
    assert winner["panel"] == [1, 3]
    assert rows == before
    for row in rows:
        row["diagnostic_train_ari"] = -row["diagnostic_train_ari"]
    assert followup.pick(rows, lambda r: r["objective"])["panel"] == [1, 3]
    assert len(rows) == 3


def test_tie_breaking_matches_original_cache_order():
    rows = [{"panel": p, "valid": True, "legacy_valid": True, "objective": 1.}
            for p in ([3, 4], [7], [2], [1, 2])]
    assert followup.pick(rows, lambda r: r["objective"])["panel"] == [2]
    assert followup.pick([], lambda r: r["objective"]) is None
