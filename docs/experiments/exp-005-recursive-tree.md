# exp-005 — Phase 4: recursive interpretable tree (the product)

**Status:** greedy core built + validated. **Module:** `atomicplus/tree.py`.

## What it is
The single unique hard-partition tree. At each node: run the persistence search on that
node's points, take the canonical split (highest persistence), and commit it only if it
passes the acceptance gate (persistence >= threshold AND both sides >= min_cluster_size);
else the node is a leaf. Each internal node records **its own** responsible feature subset +
persistence. Recurse on each child independently.

## Validation — known 3-cluster hierarchy
`hierarchical_subspace(n=300, p=15, level1=[0,1], level2=[2,3])`: root should split {0}|{1,2}
on the level-1 dims, then {1,2} splits {1}|{2} on the level-2 dims.

```
[split on f0, f1, f7, f8, f14]  persistence=2.59  n=300      <- true level-1 dims [0,1] present
  |- [split on f0, f2, f9, f12]  persistence=2.76  n=200     <- true level-2 dim [2] present
  |-   |- * leaf #0  (n=100, low_persistence)
  |-   |- * leaf #1  (n=100, low_persistence)
  |- * leaf #2  (n=100, low_persistence)
```

**n_leaves = 3, ARI(leaves vs. truth) = 1.000.** The tree recovers the hierarchy exactly, each
internal node carrying the responsible feature set, and stops at pure leaves (low_persistence).

## Findings
1. The recursive persistence tree produces a **single hard partition** that recovers a known
   hierarchy perfectly, with **per-split feature sets** — the core product of the paper.
2. The true defining dims appear at the right level (level-1 at root, level-2 in the child).
   Feature sets also carry a few filler dims (weak parsimony -> Phase 5 operators will prune).
3. The min-persistence gate stops at pure leaves without over-splitting.

## Next
- **Beam search (b>1) + null/stability gate**, and the headline **b=1-vs-b / gate on-off
  ablation** on this synthetic truth (task #13). The gate should become the null + stability
  gate from exp-004 (commit only if the split also beats the permutation null and reproduces).
- Real-data demo (e.g. Glass, 6 classes) and per-node threshold rules (Phase 7).

## Caveats
- `min_persistence` is on the ratio scale, so it needs per-dataset calibration; the null gate
  (scale-free) is the principled replacement but costs a permutation test per node.
- Greedy (no beam yet) can compound an early wrong split; beam + look-ahead is the defense.
- O(n^2) per node x many nodes: fine for small n; needs the kNN-sparse MST for large n.

---

## Acceptance gate (task #13, part 1) — 2026-07-08

`atomicplus/gate.py`: a node commits its best split only if it clears
persistence >= threshold, **partition stability** (re-run on subsamples; split reproduces),
and optionally the **permutation null** (mode="none" | "stability" | "null").

| check | REAL 2-cluster node | PURE NOISE node |
|---|---|---|
| persistence | 1.80 | 1.04 |
| stability (mean ARI vs. node split) | **1.00** | **0.00** |
| gate verdict | **pass** | **reject (unstable)** |

Gated tree (stability) on the 3-cluster hierarchy still recovers it perfectly (n_leaves=3,
ARI=1.000; root persistence 3.22, stability 1.00). The stability layer catches cohesive-but-
spurious splits the persistence threshold alone would pass — the exp-004 credibility mechanism,
now enforced per node. **Still to do:** beam search (b>1) + the b=1-vs-b / gate on-off ablation.

---

## Beam + gate ablation (task #13, part 2) — 2026-07-08

Beam draws the top-`b` DISTINCT-partition candidates from the archive (not just the front,
so a correct-but-lower-persistence split isn't hidden behind a high-persistence trap); the gate
filters them; among passers, pick by a 1-ply look-ahead (candidate persistence + best child
persistences). b=1 = greedy.

**Clean 3-cluster hierarchy:** every config recovers it (ARI 1.000) — separable structure is
found regardless of split order, so the clean case can't separate the methods.

**Deceptive case** (`deceptive_hierarchy`: a trap dim that is the single highest-persistence
split and fragments all three clusters):

| beam | gate | n_leaves | ARI | behaviour |
|---|---|---|---|---|
| 1 | none | 8 | 0.520 | greedy takes the trap -> over-fragments |
| 3 | none | 7 | 0.556 | beam alone barely helps (look-ahead dominated by trap persistence) |
| 1 | stability | 1 | 0.000 | gate kills the trap, greedy has no alternative -> gives up |
| 3 | stability | 6 | **0.585** | **best** -- gate removes the trap, beam supplies the alternative |
| 5, 8 | stability | 6 | 0.585 | wider beam plateaus -- width is not the bottleneck |

## Findings
1. **The design thesis holds directionally:** beam+gate > beam-only > greedy > greedy+gate.
   Both matter and are best together -- the gate removes the unstable trap, and beam supplies
   the correct alternative the Pareto front hides.
2. **But a 1-ply total-persistence look-ahead does NOT fully overcome a high-persistence,
   cluster-fragmenting trap** (best ARI 0.585, still fragmented); wider beam does not help,
   so the bottleneck is the look-ahead CRITERION (dominated by the trap's raw persistence),
   not the candidate pool.
3. This delineates a real limitation and motivates: a **fragmentation-aware / min-child
   look-ahead** (don't sum persistence; penalise splits whose children don't cleanly recover),
   and the plan's **global prune-and-regraft refinement (future work)**.

Honest framing: the deceptive case is an adversarial stress test; on clean/real separable
structure the greedy tree already recovers (this doc's main result). The ablation's value is
mapping exactly where beam+gate help and where they don't -- the kind of limit a methods paper
must state rather than hide.

---

## Tree calibration fix (2026-07-08): data-adaptive acceptance

The tree collapsed to a single leaf on real data because the fixed `min_persistence=1.4` was
tuned to synthetic (good splits 5-28) but real splits score ~1.1-1.9. A *fixed* threshold can't
work for both (glass needs ~1.02, synthetic over-splits at 1.02). Fix: **low validity floor
(1.02) + the scale-free STABILITY gate** as the real acceptance criterion (reject splits that
don't reproduce under subsampling, regardless of magnitude).

| hier3 (true 3 clusters), floor=1.02 | n_leaves | ARI |
|---|---|---|
| gate=none | 10 (over-split) | 0.621 |
| **gate=stability** | **4** | **0.954** |

New tree defaults: `min_persistence=1.02`, `gate_mode="stability"`. On glass the tree now splits
(no collapse) but ARI stays low (~0.12) -- expected, since glass labels aren't connectivity
structure. The tree's value is on connectivity/hierarchical data, judged by the null/stability
evidence, not by beating k-means on compactness labels.
