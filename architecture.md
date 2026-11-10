# ATOMIC+ — Architecture

> **What this is.** The reference map for the ATOMIC follow-up project ("ATOMIC+"). Part 1 documents the **original** codebase (`atomic.py` and helpers) exactly as it stands — the EA loop, where fitness / connected-components / k̃ live, data + preprocessing, dependencies, and every bug/discrepancy found by reading the code against the paper. Part 2 specifies the **clean-room re-implementation** we are building and own. Companions: `atomic_handoff_1.md` (plan), `literature_review.md` (novelty fence), `blind-spot-audit.md` (authoritative decision log & risk triage).
>
> **Status (2026-07-07):** Phase 0 in progress — faithful re-implementation + fair-comparison harness. Engine = **clean-room NumPy/scikit-learn** (not DEAP), so the fitness, operators, and search loop can be swapped for Phases 2–5. Repo branch: `reproduction`.

---

## Part 1 — The original ATOMIC codebase

### 1.1 Repository layout (current)

| File | Role | Runs as-is? |
|---|---|---|
| `atomic.py` | The whole algorithm: k̃ selection, topology fitness, NSLC, DEAP EA loop, result display. | **No** — imports a missing module (`true_ex_convex`). |
| `convex_synth_data.py` | `generate2(n, p, k)` — one large Gaussian blob + (k−1) small **axis-aligned subspace** Gaussian blobs. Returns `(df, labels, true_explanations)`. Used for the poster figures. | Yes. |
| `nonconvex_data.py` | `convex_gen()` *(misnamed — it builds **non-convex** data)* — projects the 2-D jain/spiral/flame sets into 6-D with uniform-noise dims. | Yes (but see naming bug). |
| `synthetic_baseline.py` | `generate(k, mu, d, N)` — projected-clustering generator (Aggarwal-style), tracks which features define which cluster. Unused by `atomic.py`. | Yes. |
| `combine.py` | Manually stacks several one-vs-rest label files (`myarray*.txt`) into a global partition; "higher index wins". Produces the poster plot. | **No** — imports `nonconvex_gen` which does not exist. |
| `2d_data/{jain,spiral,flame}.txt` | Tab-separated 2-D non-convex benchmark sets (`X Y Label`) consumed by `nonconvex_data.py`. | Data. |
| `ATOMIC-interpretable-clustering.pdf` | The 4-page GECCO '24 Companion paper (anchor). | Doc. |
| `README.md` | One-paragraph overview + paper link. | Doc. |
| `atomic_handoff_1.md`, `literature_review.md`, `blind-spot-audit.md` | Project planning docs. | Doc. |

**Missing / never-committed artifacts** (confirmed unavailable — see `blind-spot-audit.md` M6):

- `compare_atomic.py` — the **baseline scorer** (silhouette / Davies–Bouldin). *This is the crux of the fairness question: it is the code that would reveal in which space each metric was computed.* Gone.
- `true_ex_convex.py` — imported by `atomic.py` (`from true_ex_convex import generate`); not in the repo, so `atomic.py` does not import cleanly.
- Preprocessed UCI CSVs and the exact EA config used for the published tables.

### 1.2 Data flow (original)

```
                        full data (all p variables, scaled to [0,1])
                                     │
                    init_mode: grow k = 2,3,…  → choose_k()  →  k̃      (atomic.py:188, 206-216)
                                     │
          ┌──────────────────────────────────────────────────────────────┐
          │  EA loop  (DEAP eaMuPlusLambda, 100 generations)              │
          │                                                               │
          │   individual = Boolean bit-string of length p  (1 = use var)  │
          │        │                                                      │
          │        ▼                                                      │
          │   tda_eval:  select cols where bit=1  →  kNN connectivity     │
          │   graph (k = k̃, include_self)  →  connected_components  →     │
          │   f = −(C−2)²   and   size = #selected           (l.52-72)    │
          │        │                                                      │
          │        ▼                                                      │
          │   nslc_eval:  novelty = mean Hamming dist to 8 nearest        │
          │   archive members;  local-competition = #of those 8 it        │
          │   out-performs;  stochastically add indiv to archive (l.84)   │
          │        │                                                      │
          │        ▼                                                      │
          │   NSGA-II selection on (novelty, local-competition)           │
          │   variation: bitwise-OR crossover + bit-flip mutation         │
          └──────────────────────────────────────────────────────────────┘
                                     │
                       ParetoFront (hof) + archive (bank)
                                     │
        __main__: keep archived solutions with <30 features, sort by size,
        display each (UMAP), dump labels to myarray*.txt  →  combine.py stitches
        chosen indices into a global partition ("higher index wins")
```

### 1.3 Component reference (file:line → what it does)

**Representation.** `creator.Individual = list` of 0/1, length *p* (`atomic.py:32-33`). Encoded to/from an integer (`int("".join(bits), 2)`) to key the archive hash-table (`bank`). Decoding pads with leading zeros back to length *p* (`l.91-96`). A global `bank: dict[int → (f, size)]` is the NSLC archive.

**Topology core — `tda_eval(indiv, data_pd, k_s)`** (`l.52-72`). Slices the columns whose bit is 1; if ≥2 features, builds `kneighbors_graph(..., n_neighbors=k_s, mode='connectivity', include_self=True)`, takes `connected_components`, returns `f1 = -1*(n_components-2)**2` and `size`. If <2 features it returns the **string `"ERROR"`** (not a tuple) — a latent type bug relied upon never firing because init/mutation force ≥2 bits.

**k̃ selection — `choose_k(seen_tuples)`** (`l.188-197`) + the loop in `atomic()` (`l.206-216`). Builds a full-data kNN graph for k = 2…29, records `(k, n_components)`, and `choose_k` returns the **first** k whose component count equals the previous k's ("stable k"). Two problems: it picks the *smallest* stabilizing k (sparsest graph → maximal single-linkage chaining), and if the count never repeats it returns `seen_tuples[-1]`, a **tuple**, which then propagates as `k_use`.

**Out-performance — `tuple_eval(first, next)`** (`l.75-81`). Returns `True` if `first[0] > next[0]`, **or** if `first[0] == next[0]` **and `first[1] < next[1]//2`**. The paper (§2.3) defines out-performance as f-greater, or f-equal and `|I₁| < |I₂|`. The code requires the winner to use **fewer than half** the loser's features — stricter than the paper.

**NSLC — `nslc_eval(indiv, …)`** (`l.84-122`). (1) Rebuilds a `NearestNeighbors(n_neighbors=8)` over the **entire current archive**, decoding every key to a bit-list, on **every evaluation** (the real runtime bottleneck — audit M2). (2) Novelty = mean Hamming distance to the 8 nearest archive members. (3) Local competition = how many of those 8 the individual out-performs (via `tuple_eval`). (4) Adds the individual to the archive with probability `percent_bank`. Returns `(novelty, local_competition)` — both maximized.

**Operators.** `custom_mutate(i1, prob)` (`l.125-135`): **BUG** — `i1[i] = (i1[1] + 1) % 2` toggles from bit **1** every time instead of `i1[i]`; it does not implement a per-bit flip. Then forces ≥2 set bits. `custom_mate(i1, i2)` (`l.138-144`): bitwise-**OR** — at positions where the parents differ, sets **both** to 1, i.e. both children become the union → feature sets only ever grow.

**EA driver — `atomic(dataset)`** (`l.200-254`). Seeds (`np.random.seed(3)`, `random.seed(64)`), optionally finds k̃, registers the DEAP toolbox, builds a 100-individual population, and runs `eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, …)` returning the Pareto front and k̃.

**Result assembly.** `__main__` (`l.257-303`) keeps archived solutions with <30 features, sorts by size, renders each with `tda_display` (UMAP embed, `random_state=1`), and writes `myarray{i}.txt`. `combine.py` then loads user-chosen indices and stacks them ("higher index wins") into one partition — a manual, non-reproducible step (audit H2).

### 1.4 Parameters — Table 1 (paper) vs. code

| Parameter | Paper (Table 1 / §2) | Code (`atomic.py`) | Note |
|---|---|---|---|
| Representation | Boolean list length *p* | same | — |
| Mutation | flip random entry, **60%** | `MUTPB=0.6`; per-bit prob `0.45` inside `custom_mutate` | 60% = prob individual is mutated; 0.45 = per-bit rate. **Mutation is buggy** (toggles bit 1). |
| Crossover | bitwise-OR, **40%** | `CXPB=0.1` (**10%**) | **Discrepancy** — code uses 10%, not 40%. |
| Survivor selection | NSGA-II | `tools.selNSGA2` | — |
| Population size | **100** | init 100, but `MU=50` kept per generation | **Discrepancy** — steady-state pop is 50. |
| Offspring (λ) | 60 | `LAMBDA=60` | matches |
| Generations | 100 | `NGEN=100` | matches |
| Archive k-NN | k = 8 | `num_neighbours=8` | matches |
| Archive add prob | "**0.05%**" | `percent_bank=0.05` → **5%** | **Resolves open Q3:** the paper's "0.05%" is a typo; the code adds at **5%**. |
| Objectives | novelty (sparseness) + local competition | `weights=(1.0, 1.0)` | both maximized |
| k̃ | "stable k", found once on full data | `choose_k`, range 2–29 | smallest-stabilizing (chaining risk) |

### 1.5 Bug & discrepancy ledger (things Part 2 fixes and documents)

1. **Mutation** `i1[i] = (i1[1]+1)%2` — toggles bit 1, not bit *i*. Not a real per-bit flip. *(Fix; keep the buggy variant behind a flag to reproduce old behaviour if ever needed.)*
2. **`choose_k`** returns the smallest stabilizing k (max chaining) and can return a **tuple** if the count never stabilizes. *(Fix + make k̃ explicit/overridable per dataset.)*
3. **Out-performance** uses `next[1]//2` (fewer-than-half) instead of the paper's `|I₁| < |I₂|`. *(Match the paper; make the rule pluggable.)*
4. **Archive add-probability** is 5% in code vs "0.05%" in the paper. *(Document; expose as a parameter.)*
5. **Crossover probability** 10% in code vs 40% in the paper. *(Document; expose.)*
6. **Population** steady-states at 50, not 100. *(Document; expose.)*
7. **Bitwise-OR crossover** monotonically grows feature sets (fights parsimony). *(Keep as baseline; add uniform/set-based in Phase 5.)*
8. **Novelty recomputed over the whole growing archive every eval** — super-linear cost. *(Fix with an incremental/rebuilt-every-N index.)*
9. **`tda_eval` returns `"ERROR"` string** for <2 features. *(Return a sentinel score; never rely on it not firing.)*
10. **Naming/import breakage:** `nonconvex_data.convex_gen` builds non-convex data; `combine.py` imports the non-existent `nonconvex_gen`; `atomic.py` imports the missing `true_ex_convex`. *(Clean names in the re-implementation.)*

### 1.6 External dependencies (original)

`deap` (EA), `numpy`, `scikit-learn` (`kneighbors_graph`, `NearestNeighbors`), `scipy` (`csr_matrix`, `connected_components`, `distance.hamming`), `pandas`, `matplotlib`, `umap-learn` (display only). The baseline metrics (silhouette, DB) lived in the **missing** `compare_atomic.py`.

---

## Part 2 — The re-implementation ("ATOMIC+")

### 2.1 Design principles

1. **Own every operator.** Framework-free core (NumPy + scikit-learn primitives only) so fitness, selection, and variation are transparent and modifiable — required for the GECCO methods paper and for Phases 2–5. NSGA-II selection is cross-checked once against DEAP's `selNSGA2` to prove faithfulness.
2. **Faithful-but-fixed.** Default behaviour reproduces the paper's intent (paper's out-performance rule, k̃ procedure). Each original bug is fixed, with the legacy behaviour reachable via a config flag so we can measure what each fix changes.
3. **Pure functions, injected RNG.** No global `bank`, no module-level seeds, no `creator.create` global state. Every stochastic function takes an explicit `numpy.random.Generator`, so runs are independently seedable (the 30-run protocol needs this) and recursion/beam (later) can spawn sub-searches safely.
4. **Space is explicit everywhere.** Every metric call names the feature space it is computed in. Nothing is scored in an implicit space — this is the whole point of the fairness work.
5. **Config over constants.** All parameters (Table 1 + the fixes) live in a dataclass, not scattered literals.

### 2.2 Module map (new)

```
atomicplus/
  config.py          # AtomicConfig, EvalConfig dataclasses (all Table-1 params + fix flags)
  genome.py          # bit-string <-> index-set <-> int; random init with >=2 set bits
  topology.py        # kNN connectivity graph, connected_components, f=-(C-2)^2, choose_k (fixed)
  fitness.py         # tda_eval (component score + size); out-performance rule (paper | legacy)
  archive.py         # NSLC archive: novelty (Hamming sparseness) + local competition; add policy
  selection.py       # clean-room NSGA-II: fast non-dominated sort + crowding distance; Pareto front
  operators.py       # mutation (fixed per-bit flip | legacy) ; crossover (OR | uniform | set-based)
  engine.py          # mu+lambda loop; atomic(data, config) -> (pareto_front, archive, k̃)
  preprocessing.py   # knn_impute(2) + minmax_scale([0,1])
  datasets/
    synthetic.py     # subspace_gaussian(...) ; nonconvex_projection(...) ; known labels+features
    uci.py           # load_uci(name) via ucimlrepo (+ local-CSV fallback); paper's 7 sets
  evaluation/
    metrics.py       # silhouette, davies_bouldin, ari, nmi  (each takes an explicit space)
    baselines.py     # kmeans / gmm / dbscan wrappers with the paper's model-selection rules
    harness.py       # subspace-parity comparison table (full space vs selected subspace) + external metrics
tests/               # pytest: topology, operators, selection, synthetic recovery, harness, k̃
```

**Old → new mapping.** `tda_eval` → `topology.py` + `fitness.py`; `choose_k` → `topology.choose_k` (fixed); `nslc_eval` + `bank` → `archive.py`; `custom_mutate`/`custom_mate` → `operators.py`; `selNSGA2` → `selection.py`; `atomic()` → `engine.atomic()`; `custom_population` → `genome.random_population`; the missing `compare_atomic.py` → `evaluation/`.

### 2.3 The fair-comparison harness (`evaluation/harness.py`) — the point of this session

The open question is *"is ATOMIC actually better than the baselines, or is the win a metric-space artifact?"* Internal metrics (silhouette, Davies–Bouldin) are **space-dependent**: in high dimensions they collapse toward 0 via distance concentration, and ATOMIC scores itself in a low-dim **selected** subspace while the baselines were (probably) scored in full space. The harness settles this by construction:

For each dataset and each ATOMIC solution (feature subset `V`, partition `P`):

| Method | Full-space score | In-subspace score (restricted to `V`) | External (space-invariant) |
|---|---|---|---|
| ATOMIC | silhouette / DB in ℝᵖ on `P` | silhouette / DB in ℝ^|V| on `P` | ARI, NMI of `P` vs. labels |
| KMeans / GMM / DBSCAN | silhouette / DB in ℝᵖ on their partition | **their partition re-scored in `V`** and the baseline **re-fit inside `V`** | ARI, NMI vs. labels |

Reading it: if ATOMIC's advantage **shrinks when every method is scored in the same subspace `V`**, the original gap was largely the space, not the method (the confound is real). If ATOMIC **still leads in-subspace and on ARI/NMI**, the advantage is genuine. External metrics (ARI/NMI vs. ground truth) are the tie-breaker because no choice of subspace can inflate them. *(Caveat M1: UCI labels are classification labels, not guaranteed geometric clusters — so we report internal and external side by side and never let ARI alone adjudicate.)*

Baseline model-selection follows the paper (§3.3): k-means over k=2…20 minimizing within-cluster SSE; GMM over all covariance types and 2…20 components keeping the best score; DBSCAN with the authors'-suggested heuristic.

### 2.4 Validation strategy (how we tell a re-implementation bug from a finding)

With no reference numbers to match (M6), correctness is pinned by tests, not by reproducing tables:

- **Tiny hand-checkable inputs** — e.g. two well-separated 2-point blobs → exactly 2 components at small k; a single bridge point fuses them → 1 component (documents the chaining failure). k̃ on a hand-built graph returns the known stable k.
- **Synthetic known-answer recovery** — `subspace_gaussian` embeds a blob in known dims; ATOMIC should select (a superset of) those dims and induce the known 2-way split; measured by ARI vs. true labels and Jaccard vs. true feature set.
- **Selection cross-check** — our NSGA-II front equals DEAP's `selNSGA2` on random fitness populations (one-time faithfulness proof).
- **Subspace-parity demonstration** — on synthetic data with *known* separating dims, score baselines full-space vs. in-subspace to exhibit the silhouette inflation mechanism directly, independent of the EA.

### 2.5 Extension points (later phases, not built yet)

`fitness.py` is where **Phase 2** continuous persistence (MST-gap `S = e₁ − e₂`, mutual-reachability distance, min-cluster-size) replaces `f = −(C−2)²`. `engine.py` is where **Phase 4** recursion + beam search + stability gate wrap the single-split search into the tree. `genome.py`/`operators.py` hold the **Phase 5/6** sparse index-set representation and uniform/set-based operators. All are isolated behind the config so the Phase-0 baseline stays runnable for comparison.

---

## Part 3 — Repo structure & conventions

Current planning docs live at the repo root (`atomic_handoff_1.md`, `literature_review.md`, `blind-spot-audit.md`, this file). As code lands, migrate documentation into `/docs` per `atomic_handoff_1.md` §7:

```
architecture.md            # this file (root for now; discoverable next to the other docs)
atomicplus/                # the re-implementation package (Part 2)
tests/                     # pytest suite
docs/
  caveats-audit.md         # findings on the 11 caveats (esp. the metric-space confound)
  method-extensions.md     # living spec of Phases 2–7
  decisions.md             # ADR-style log
  experiments/             # one file per experiment: hypothesis → setup → command → result → conclusion
legacy/                    # original atomic.py + helpers, preserved read-only (proposed; not yet moved)
```

Conventions: one experiment = one doc; log decisions as they're made; keep the original files untouched under version control (`git tag` a pristine baseline before refactoring); branch per extension.

### Build order & status

| # | Item | Phase | Status |
|---|---|---|---|
| 1 | `architecture.md` | — | **done (this doc)** |
| 2 | Topology core + fixed k̃ (`topology.py`) | 0 | **done** |
| 3 | Clean-room EA — NSLC + NSGA-II (`engine.py`, verified vs DEAP) | 0 | **done** |
| 4 | Preprocessing + datasets (synthetic + UCI) | 0/1 | **done** |
| 5 | Fair-comparison harness (`evaluation/harness.py`) | 1 | **done** |
| 6 | Validation + tests (`tests/`, 18 passing) | 0 | **done** |
| 7 | Continuous persistence fitness | 2 | not started (linchpin, next) |
| 8 | Recursion + beam + stability gate | 4 | not started |

**First result:** `docs/experiments/exp-001-subspace-parity.md` — on controlled synthetic
data, once every method is scored in a common space ATOMIC ties k-means/GMM (ARI=1.0 all
round); the paper's silhouette/DB gap is a metric-space effect. Also surfaced ATOMIC's k̃
fragility (smallest-stable-k + flat fitness → spurious splits). Dataset setup: `DATASETS.md`.
Run the demo: `python scripts/demo_fairness.py`.
