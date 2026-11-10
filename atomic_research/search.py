"""Small label-blind, bounded search baselines using a common frozen scorer.

This evolutionary baseline is NOT a reimplementation of ATOMIC's NSLC engine.
No baseline enumerates all pairs or triples as initialization.
"""
from __future__ import annotations

from math import comb
from time import perf_counter
import numpy as np

from .scoring import score_panel

COMPONENTS = ("graphcut", "density", "legacy_graphcut", "legacy_density")


def random_panels(p, max_features, count, seed):
    rng = np.random.default_rng(seed)
    limit = min(max_features, p)
    total = sum(comb(p, k) for k in range(1, limit + 1))
    target = min(count, total)
    panels = {}
    # A bounded duplicate retry loop is essential for tiny finite spaces.
    for attempt in range(max(100, 50 * target)):
        if len(panels) >= target:
            break
        k = 1 + attempt % limit
        panel = tuple(sorted(rng.choice(p, k, replace=False).tolist()))
        panels[panel] = None
    return list(panels)


class FrozenObjective:
    """Reference moments never change with the search population.

    These are comparison units, NOT null z-scores or cluster probabilities.
    A common reference bank is scored once, recorded, and hidden from search.
    """
    def __init__(self, reference_records, mode="consistent"):
        if mode not in ("consistent", "legacy", "graphcut", "density"):
            raise ValueError("Unknown objective")
        self.mode = mode
        self.moments = {}
        # A common intersection isolates scoring changes from eligibility and
        # reference-weight changes. This is an audit policy, not a validity test.
        self.reference_total = len(reference_records)
        shared = [r for r in reference_records if self.eligible(r)]
        self.reference_eligible = len(shared)
        for key in COMPONENTS:
            values = [r[key] for r in shared]
            self.moments[key] = (float(np.mean(values)) if values else 0.0,
                                 max(float(np.std(values)), .001) if values else 1.0)

    @staticmethod
    def eligible(record):
        return bool(record["valid"] and record["legacy_valid"])

    def __call__(self, record):
        if not self.eligible(record):
            return -1e12
        keys = {"consistent": ("graphcut", "density"),
                "legacy": ("legacy_graphcut", "legacy_density"),
                "graphcut": ("graphcut",), "density": ("density",)}[self.mode]
        return float(sum((record[k] - self.moments[k][0]) / self.moments[k][1] for k in keys))


class ScoreCache:
    def __init__(self, X, objective, budget, *, seed=0, splitter="spectral", k=10, on_evaluation=None):
        self.X, self.objective, self.budget = X, objective, budget
        self.seed, self.splitter, self.k = seed, splitter, k
        self.records = {}
        self.requests = 0
        self.started = perf_counter()
        self.scoring_seconds = 0.0
        self.on_evaluation = on_evaluation

    @property
    def full(self):
        return len(self.records) >= self.budget

    def evaluate(self, panel):
        panel = tuple(sorted(panel))
        self.requests += 1
        if panel in self.records:
            return self.records[panel]
        if self.full:
            return None
        start = perf_counter()
        record = score_panel(self.X, panel, seed=self.seed, splitter=self.splitter, k=self.k)
        elapsed = perf_counter() - start
        self.scoring_seconds += elapsed
        record.update(objective=self.objective(record), evaluation=len(self.records) + 1,
                      scoring_seconds=elapsed, elapsed_seconds=perf_counter() - self.started)
        self.records[panel] = record
        if self.on_evaluation is not None:
            self.on_evaluation(record)
        return record

    def ranked(self):
        return sorted(self.records.values(), key=lambda r: (-r["objective"], len(r["panel"]), r["panel"]))


def search_discrete(method, cache, max_features=8, seed=0):
    """Same unique scoring budget for random, forward, and add/drop/swap EA.

    Forward has a bounded randomized extension shortlist per depth so p>budget
    cannot consume everything at singletons. EA keeps score-elite parents plus
    immigrants, with no oracle seeding, enumeration or biological supervision.
    """
    rng = np.random.default_rng(seed)
    p = cache.X.shape[1]
    limit = min(max_features, p)
    trace = []
    max_attempts = 50 * cache.budget + 100
    if method == "random":
        for panel in random_panels(p, limit, cache.budget, seed):
            cache.evaluate(panel)
    elif method == "forward":
        panel = ()
        per_depth = max(2, cache.budget // limit)
        for depth in range(limit):
            options = rng.permutation([j for j in range(p) if j not in panel])[:per_depth]
            proposals = []
            for j in options:
                record = cache.evaluate((*panel, int(j)))
                if record is not None:
                    proposals.append(record)
            if not proposals:
                break
            winner = max(proposals, key=lambda r: r["objective"])
            panel = winner["panel"]
            trace.append({"depth": depth + 1, "panel": panel, "objective": winner["objective"]})
            if cache.full:
                break
    elif method == "evolutionary":
        for panel in random_panels(p, limit, min(12, max(2, cache.budget // 4)), seed):
            cache.evaluate(panel)
        for _ in range(max_attempts):
            if cache.full:
                break
            ranked = cache.ranked()
            if rng.random() < .25 or not ranked:
                panel = set(rng.choice(p, int(rng.integers(1, limit + 1)), replace=False).tolist())
            else:
                parent = ranked[int(rng.integers(min(12, len(ranked))))]
                panel = set(parent["panel"])
                operation = rng.choice(["add", "drop", "swap"])
                if operation in ("drop", "swap") and len(panel) > 1:
                    panel.remove(int(rng.choice(sorted(panel))))
                if operation in ("add", "swap") and len(panel) < limit:
                    remaining = [j for j in range(p) if j not in panel]
                    if remaining:
                        panel.add(int(rng.choice(remaining)))
            cache.evaluate(tuple(panel))
    else:
        raise ValueError(f"Unknown discrete search: {method}")
    # Fill unused budget for forward and finite-space duplicate stalls equally.
    for panel in random_panels(p, limit, cache.budget, seed + 781):
        if cache.full:
            break
        cache.evaluate(panel)
    return {"method": method, "trace": trace, "unique_evaluations": len(cache.records),
            "requests": cache.requests, "scoring_seconds": cache.scoring_seconds,
            "total_seconds": perf_counter() - cache.started,
            "budget_kind": "unique panel scores; not equal wall time"}
