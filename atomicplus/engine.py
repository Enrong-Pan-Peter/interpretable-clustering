"""The evolutionary loop: a clean-room (mu + lambda) NSLC/NSGA-II search.

Mirrors DEAP's `eaMuPlusLambda` + `varOr` (crossover OR mutation OR reproduction per
offspring), but with explicit RNG, no global state, and the fixes documented in
architecture.md. Entry point: `atomic(X, config)`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from . import fitness as fit
from . import genome as gm
from . import operators as ops
from . import topology
from .archive import NSLCArchive
from .config import AtomicConfig
from .selection import nondominated_indices, nsga2_select


@dataclass
class Individual:
    genome: np.ndarray
    quality: fit.SubsetEval
    novelty: float = 0.0
    competition: int = 0


@dataclass
class AtomicResult:
    k_tilde: int
    population: List[Individual]
    archive: NSLCArchive
    quality_front: List[Individual]  # non-dominated over (maximise f, minimise size)
    k_trace: List = field(default_factory=list)

    def best(self) -> Optional[Individual]:
        """Highest-f solution on the quality front, ties broken by fewest features."""
        if not self.quality_front:
            return None
        return sorted(self.quality_front, key=lambda i: (-i.quality.f, i.quality.size))[0]


def _dedup_individuals(archive: NSLCArchive, pop: List[Individual]) -> List[Individual]:
    seen = {}
    for g, ev in zip(archive.genomes, archive.evals):
        seen[gm.genome_key(g)] = Individual(g, ev)
    for ind in pop:
        seen.setdefault(gm.genome_key(ind.genome), ind)
    return list(seen.values())


def atomic(X, config: Optional[AtomicConfig] = None,
           rng: Optional[np.random.Generator] = None) -> AtomicResult:
    config = config or AtomicConfig()
    rng = rng if rng is not None else np.random.default_rng(config.seed)
    X = np.asarray(X, dtype=float)
    p = X.shape[1]

    # --- k̃ (stable-k), found once on the full data (or taken from config) ---
    k_trace: List = []
    if config.k_tilde is not None:
        k_tilde = int(config.k_tilde)
    else:
        k_tilde, k_trace = topology.choose_k(
            X, config.k_search_min, config.k_search_max, metric=config.metric, return_trace=True)

    archive = NSLCArchive(config.archive_neighbors, config.archive_add_prob,
                          config.archive_rebuild_every, config.outperform_rule)

    def quality(g) -> fit.SubsetEval:
        return fit.evaluate_subset(X, g, k_tilde, metric=config.metric,
                                   min_features=config.min_features,
                                   fitness_mode=config.fitness_mode,
                                   min_cluster_size=config.min_cluster_size,
                                   mutual_reachability=config.mutual_reachability,
                                   core_k=config.core_k, normalize=config.persistence_normalize)

    # --- pair-seed init (optional): guarantee jointly-informative PAIRS are evaluated ---
    seed_genomes: List[np.ndarray] = []
    if config.pair_seed_init:
        from itertools import combinations
        if p * (p - 1) // 2 <= config.pair_seed_max:
            cand = list(range(p))
        else:                                   # too many pairs -> restrict to top-variance dims
            m = int((1 + (1 + 8 * config.pair_seed_max) ** 0.5) / 2)
            cand = [int(d) for d in np.argsort(-X.var(0))[:m]]
        for i, j in combinations(cand, 2):
            g = np.zeros(p, dtype=np.int8)
            g[i] = 1
            g[j] = 1
            seed_genomes.append(g)

    # --- initial population; seed the archive with every initial genome (cf. custom_population) ---
    pop: List[Individual] = []
    init_genomes = seed_genomes + gm.random_population(
        max(0, config.pop_size - len(seed_genomes)), p, rng, config.min_features)
    evaluated = []
    for g in init_genomes:
        ev = quality(g)
        archive.add(g, ev)                      # every pair (and random) enters the archive
        evaluated.append((g, ev))
    pop = [Individual(g, ev) for (g, ev) in evaluated[:config.pop_size]]
    for ind in pop:
        ind.novelty, ind.competition = archive.novelty_and_competition(ind.genome, ind.quality)

    per_bit = config.resolved_per_bit_prob(p)
    if config.mutation_mode == "asymmetric":
        add_p = config.mutation_add_prob if config.mutation_add_prob is not None else 1.0 / p
        rem_p = config.mutation_remove_prob if config.mutation_remove_prob is not None else 3.0 / p
    else:
        add_p = rem_p = None

    # --- generational loop ---
    for _ in range(config.n_gen):
        offspring: List[np.ndarray] = []
        while len(offspring) < config.lam:
            r = rng.random()
            if r < config.cx_prob and len(pop) >= 2:
                i, j = rng.choice(len(pop), size=2, replace=False)
                c1, c2 = ops.crossover(pop[i].genome, pop[j].genome, rng,
                                       config.crossover_mode, min_features=config.min_features)
                offspring.append(c1)
                if len(offspring) < config.lam:
                    offspring.append(c2)
            elif r < config.cx_prob + config.mut_prob:
                i = int(rng.integers(len(pop)))
                offspring.append(ops.mutate(pop[i].genome, rng, per_bit,
                                            config.min_features, config.legacy_mutation,
                                            add_prob=add_p, remove_prob=rem_p))
            else:
                i = int(rng.integers(len(pop)))
                offspring.append(np.array(pop[i].genome, copy=True))
        offspring = offspring[:config.lam]

        off_inds: List[Individual] = []
        for g in offspring:
            ev = quality(g)
            archive.maybe_add(g, ev, rng)
            nov, comp = archive.novelty_and_competition(g, ev)
            off_inds.append(Individual(g, ev, nov, comp))

        combined = pop + off_inds
        M = np.array([[ind.novelty, ind.competition] for ind in combined], dtype=float)
        pop = [combined[i] for i in nsga2_select(M, config.mu)]

    # --- quality Pareto front over everything we evaluated ---
    all_inds = _dedup_individuals(archive, pop)
    qmat = np.array([[ind.quality.f, -ind.quality.size] for ind in all_inds], dtype=float)
    front = [all_inds[i] for i in nondominated_indices(qmat)]
    front.sort(key=lambda ind: (ind.quality.size, -ind.quality.f))
    return AtomicResult(k_tilde, pop, archive, front, k_trace)
