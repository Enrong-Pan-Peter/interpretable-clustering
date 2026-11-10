# exp-020 — Per-shape audit: what SUBCLU costs us, what flame costs us, and what the splitter costs us

**Date.** 2026-08-05. No new runs. Everything here is recomputed from
`results/method_baselines.csv` (old, leaky junk) and `results/method_baselines_structured.csv`
(repaired junk), each 6 shapes × 20 seeds × p = 12/20/40 = 11,880 rows.

**Why this exists.** The SUBCLU comparison is the project's cleanest win and had no experiment
write-up — it lived only in chat and in a memo. Writing it down surfaced three findings that were in
no document at all: flame is a selection failure rather than a scope boundary, the splitter matters
more than the selection on several shapes, and the repaired benchmark halves our measured advantage
over doing no selection at all. All three change what the paper can claim.

**How this connects to the goal.** The goal is a recursive tree whose every node names a few columns
and splits the rows, readable by a domain expert. Every number here is about **one node of that
tree**: can it name the right columns (selection), and does naming them buy anything (the split).
§1 says selection is the part nobody else does well. §2 says one shape defeats selection entirely
and we had been mis-recording why. §3 says the split that follows selection is not a solved
sub-problem either. §4 says how much of the final result is actually attributable to selection.

**Two measures, kept apart throughout.** *Rank-1 selection accuracy* — did the single top-scoring
subspace equal the planted pair. *ARI* — clustering quality once a subspace is fixed. A method can
pass one and fail the other.

---

## 1. SUBCLU finds the subspace; it cannot rank it. We can.

SUBCLU (Kailing, Kriegel & Kröger, SDM 2004) has no PyPI implementation, so this uses ours. It
returns a *set* of dense subspaces with no ordering, so any rule for making it name one is our
choice — see §5 on how that was pre-committed.

**Repaired benchmark, pooled over all 6 shapes × 20 seeds × 3 values of p:**

| method | true pair in returned list | rank-1 selection accuracy |
|---|---|---|
| SUBCLU, self-tuned density radius | 0.839 | 0.219 |
| SUBCLU + best add-on ranking rule (clump coverage) | 0.839 | 0.297 |
| SUBCLU, label-tuned radius, best entry from its own list *(oracle, not a competitor)* | 0.997 | 0.714 |
| **ours (graph-cut + density hybrid)** | — (enumerates all pairs) | **0.822** |

On the old leaky benchmark the same table reads: SUBCLU hit-any 0.872, self-tuned 0.186, clump
coverage **0.844**, oracle 0.833, ours **0.769**. So on the leaky data the clump rule *beat* us; on
the repaired data it collapses while we improve. That rule was living off the leak.

**Per shape, repaired, rank-1 selection accuracy:**

| | gauss2 | circles | moons | jain | spiral | flame |
|---|---|---|---|---|---|---|
| ours | 1.000 | 1.000 | 0.967 | 0.983 | 0.983 | 0.000 |
| SUBCLU + clump coverage | 1.000 | 0.000 | 0.000 | 0.783 | 0.000 | 0.000 |
| density term alone | 1.000 | 0.900 | 0.767 | 0.417 | 0.867 | 0.000 |
| graph-cut term alone | **0.000** | 1.000 | 0.917 | 0.917 | 0.300 | 0.000 |

Two things worth carrying:

- **The hybrid is not decoration.** It is at least as good as both single terms on every shape and
  much better than either on spiral (0.983 vs 0.867 and 0.300). The two terms fail on different
  shapes, which is the whole argument for summing them.
- **The graph-cut term is anti-correlated with truth on the convex control** — rank-1 0.000 on
  gauss2, i.e. it names the wrong pair every time. The density term is what rescues convex data. Any
  claim that we "work on convex data" rests on one term, on a dataset that needs no selection at
  all (§4).

**What this means for the goal.** Every node of the tree has to commit to one panel before it can
split. Finding candidate panels is close to solved by existing work; committing to one is not, and
that is where our contribution sits.

---

## 2. flame: a selection failure, not a scope boundary — and the docs had this wrong

Every document that mentions flame calls it unrecoverable in principle. It is not.

**Hand the true pair to a splitter (repaired benchmark, ARI on flame):**

| splitter, given the true pair | flame |
|---|---|
| spectral split | **0.665** |
| HDBSCAN | **0.612** |
| spectral | 0.491 |
| k-means | 0.430 |
| DBSCAN (eps 0.08) | 0.026 |
| persistence split | 0.033 |

Our end-to-end ARI on flame is **0.006–0.018** and our rank-1 selection accuracy is **0.000** at
every p on both benchmarks. So the entire gap between 0.02 and 0.665 is a failure to find the pair,
not an absence of structure to find. The old claim was true of persistence and DBSCAN only, which is
how it got generalised.

SUBCLU fails the same way and worse: its practical variants contain the true pair in their candidate
list only **3.3%** of the time on the repaired benchmark, while its label-tuned variant contains it
**98.3%** of the time. Nobody's ranking finds it.

flame is also the only shape where **our pipeline is net-negative**: clustering all features with no
selection reaches ARI 0.026, against our 0.018.

**How to state it.** "Every subspace-selection method we tested, ours and SUBCLU's alike, fails to
find flame's informative pair, on a dataset whose clusters separate at ARI 0.67 once that pair is
known." That is honest, it is a sharper finding than the old wording, and it is the one shape where
the goal is currently out of reach for reasons we can name.

---

## 3. The splitter matters more than the selection on three of five shapes

Selection is identical across these three rows — same subspace, same seeds. Only the splitter that
runs inside the chosen subspace differs. Repaired benchmark, mean ARI:

| shape | HDBSCAN | persistence | spectral | spread | best |
|---|---|---|---|---|---|
| jain | **0.887** | 0.048 | 0.559 | **0.839** | HDBSCAN |
| spiral | **0.553** | 0.550 | 0.137 | 0.416 | HDBSCAN |
| circles | 0.677 | 0.947 | **1.000** | 0.323 | spectral |
| moons | 0.935 | **0.962** | 0.821 | 0.141 | persistence |
| gauss2 | 1.000 | 1.000 | 1.000 | 0.000 | tie |
| flame | 0.018 | −0.002 | 0.006 | 0.020 | HDBSCAN |

No splitter wins everywhere: HDBSCAN takes jain and spiral, spectral takes circles, persistence
takes moons. On jain the choice swings ARI by 0.84, which is larger than everything selection buys
on that shape (§4).

**Two consequences.** First, every "best end-to-end ARI" figure previously reported takes the best
of three splitters per shape without saying so — that is an oracle choice and has to be labelled
(recorded as C7 in `docs/CORRECTIONS.md`). Committing blind to one splitter costs circles 0.32 if you
pick HDBSCAN, or jain 0.33 and spiral 0.42 if you pick spectral.

Second, and more useful: this *is* the "which criterion should we use?" question, already measured.
Under an interactive-tool framing it stops being an embarrassment and becomes a feature — the tool
can show the user the tree each splitter produces and let them compare. Under a performance framing
it is an unfixed hole.

---

## 4. What subspace selection actually buys, per shape

Best of our three splitters, minus the best method that clusters **all** features with no selection:

| shape | ours (best splitter) | no selection, all features | **gain from selection** |
|---|---|---|---|
| circles | 1.000 | 0.000 | **+1.000** |
| spiral | 0.553 | 0.001 | **+0.552** |
| moons | 0.962 | 0.492 | **+0.470** |
| jain | 0.887 | 0.452 | **+0.435** |
| gauss2 | 1.000 | 1.000 | **0.000** |
| flame | 0.018 | 0.026 | **−0.008** |

This is the strongest single table we have for an interpretability-framed paper: on circles and
spiral, methods that use every column are at chance, and finding the right two columns is the
difference between recovering the structure and not.

**But note what the benchmark repair did to it.** On the leaky benchmark the same gains were +0.632
(moons) and +0.639 (jain), because full-space k-means and spectral were much weaker there
(moons 0.248, jain 0.144). Structured junk makes the no-selection baselines genuinely stronger, so
our measured advantage on those two shapes roughly halves. The +1.000 on circles and +0.552 on
spiral survive intact, and those are the ones to lead with.

**Selection buys exactly zero on the convex control**, which is the cleanest possible statement of
where this method is and is not for.

---

## 5. Methods note on the SUBCLU tie-break

SUBCLU has no native ranking, so whatever rule makes it commit to one subspace is our design choice
and a strawman can be built out of entirely reasonable-looking decisions. The first version of this
comparison made us look twice as good as we are for exactly that reason. The rule was therefore
pre-committed in the script docstring before the run: *use whichever tie-break is best for the
baseline*. On the old benchmark that is clump coverage at 0.844 (which beat us); on the repaired
benchmark it is still clump coverage, at 0.297. Both are reported.

The label-tuned SUBCLU variants are diagnostics and upper bounds, never competitors. They are here
to show the gap sits in the ranking step and not in the candidate list.

---

## 6. What this changes

- **Write the SUBCLU claim narrowly and it is solid:** SUBCLU finds the subspace (true pair in its
  list 84–87% of the time) but cannot rank it (22–30% rank-1); we rank it at 82%. Even given
  label-tuned help choosing among its own candidates it reaches 71%, below us.
- **Retract "flame is unrecoverable."** Replace with the selection-failure statement in §2.
- **Label the splitter choice** wherever an end-to-end ARI is quoted, or fix one splitter and take
  the loss honestly.
- **Lead the value-of-selection argument with circles and spiral** (+1.000 and +0.552 against
  full-space methods at chance), not with moons and jain, whose gains halved after the repair.
- **Stop quoting the "works on convex, not non-convex" scope.** See `docs/CORRECTIONS.md` C1; it is
  backwards.

## 7. Not answered here

- Whether flame's pair is findable by *any* ranking criterion, or whether it is a genuine needle.
  Worth one targeted run: score all C(p,2) pairs on flame and see where the true pair lands under
  each term. If it ranks near the top under some term, this is fixable; if it is mid-field
  everywhere, it is a needle and belongs in limitations permanently.
- Whether the splitter can be chosen without labels. Currently it cannot, which is why §3 matters.
