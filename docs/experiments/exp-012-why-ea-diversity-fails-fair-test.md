# exp-012 — The "why EA?" diversity claim does NOT survive a fair test

**Question.** Is the evolutionary search (NSLC + NSGA-II + archive) justified by returning many
distinct interpretable panels, vs. greedy / random under EQUAL budget?

**Setup.** `redundant_informative` (each informative dim independently carries the 2-cluster
split), p=15, informative R in {4,6}. The minimal interpretable panels are therefore the C(R,2)
informative PAIRS. Equal budget B = pop + n_gen*lam for the EA, random-subset search, and
multi-start greedy. Identical counting rule for all: distinct valid (ARI>=0.98 vs truth)
informative pairs. **EA run with `pair_seed_init` OFF** to measure the SEARCH itself (pair-seed
is brute pair enumeration, not evolution). Script: `scripts/run_diversity.py`.

**Result (mean over seeds):**

| ceiling | ea_search (no pair-seed) | random | greedy |
|---|---|---|---|
| 6  (R=4) | **0** | 2.0 | 0.5 |
| 15 (R=6) | **0** | 7.0 | 1.5 |

Confirmed mechanism (inline check): the un-seeded EA reaches best ARI 1.0 but its archive has
**median size 6–7 and no size-2 genomes** — it solves the problem with bloated, noise-padded
panels and never compresses to clean pairs. Cause: persistence is noise-gameable (5 informative +
1 noise scores as well as a clean pair), and NSLC selection rewards novelty, not parsimony.

**Where the diversity actually comes from.** With `pair_seed_init` ON, the archive holds exactly
the C(R,2) informative pairs (= ceiling); with it OFF, zero. So the "41 vs 1" diversity is
**brute-force pair enumeration**, not the EA. Random even blankets the valid space better than the
un-seeded EA (149 vs 2 total valid panels; 7 vs 0 clean pairs).

**Implication.** On benchmarks whose minimal panels are pairs, brute force covers them and the
evolutionary machinery is not justified by diversity. The EA's advantage — if any — can only appear
where enumeration fails: **minimal panels of size >=3 (jointly-necessary features) at higher p**,
where crossover must ASSEMBLE a panel that no pair, no greedy step, and no feasible random draw
reveals. That is the pre-registered test that would honestly settle "why EA." If the EA loses there
too, the paper must NOT claim the search earns its cost, and the contribution reframes around the
fair-evaluation methodology + persistence fitness (EA as one interchangeable backend).
