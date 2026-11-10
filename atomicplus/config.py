"""Configuration for the ATOMIC+ re-implementation.

All parameters live here (not scattered literals). Defaults follow the paper's
Table 1 *intent*; where the original `atomic.py` diverged from the paper, the
divergence is noted and reachable via a flag so we can measure what it changes.
See `architecture.md` Part 1.4 (parameter table) and 1.5 (bug ledger).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AtomicConfig:
    # --- k̃ (stable-k) selection ---
    k_tilde: Optional[int] = None      # if set, use directly and skip the search
    k_search_min: int = 2
    k_search_max: int = 30

    # --- evolutionary algorithm ---
    pop_size: int = 100                # paper: population size 100
    mu: int = 100                      # survivors kept per generation (paper: 100; code used 50)
    lam: int = 60                      # offspring per generation (paper Table 1: 60)
    n_gen: int = 100                   # paper: 100 generations
    cx_prob: float = 0.40              # paper Table 1: 40% (original code used 0.10)
    mut_prob: float = 0.60             # prob an offspring is produced by mutation (paper: 60%)
    per_bit_mut_prob: float = 0.45     # per-bit flip rate inside mutation (original code value)
    min_features: int = 2              # every genome must keep >= this many features

    # --- NSLC archive ---
    archive_neighbors: int = 8         # k for the archive k-NN graph (paper & code: 8)
    archive_add_prob: float = 0.05     # code value = 5%; paper says "0.05%" (a typo; see ledger #4)
    archive_rebuild_every: int = 1     # 1 = faithful (rebuild NN index each eval); >1 = faster (audit M2)
    outperform_rule: str = "paper"     # "paper": |I1|<|I2| ; "legacy": |I1| < |I2|//2 (code)

    # --- operators ---
    crossover_mode: str = "or"         # "or" (faithful union) | "uniform" | "set_based"
    legacy_mutation: bool = False      # True reproduces the i1[1] bit-1 mutation bug (ledger #1)
    mutation_mode: str = "symmetric"   # "symmetric" (flip) | "asymmetric" (bias to removal, Phase 5)
    mutation_add_prob: Optional[float] = None     # asymmetric add rate    (default 1/p)
    mutation_remove_prob: Optional[float] = None  # asymmetric remove rate (default 4/p)

    # --- misc ---
    metric: str = "euclidean"
    seed: Optional[int] = None         # master seed; None -> nondeterministic

    # --- Phase 2: continuous persistence fitness (MST edge-gap) ---
    fitness_mode: str = "components"       # "components" = flat -(C-2)^2 ; "persistence" = MST gap
    min_cluster_size: int = 5              # both sides of a persistence split must have >= this
    mutual_reachability: bool = True       # edge weight = max(core_k(a), core_k(b), d(a,b))
    core_k: int = 5                        # k for core distances (mutual reachability)
    persistence_normalize: str = "ratio"   # "ratio" (e1/e2) | "median" | "none"

    # --- Phase 5b: pair-seeded initialization (for jointly-necessary features, e.g. non-convex) ---
    pair_seed_init: bool = False           # seed the archive/pop with all feature PAIRS
    pair_seed_max: int = 2000              # cap on #pairs (else restrict to top-variance dims)

    def resolved_per_bit_prob(self, p: int) -> float:
        """Per-bit mutation probability, allowing a 1/p convention if set to None-like <=0."""
        return (1.0 / p) if self.per_bit_mut_prob is None or self.per_bit_mut_prob <= 0 else self.per_bit_mut_prob
