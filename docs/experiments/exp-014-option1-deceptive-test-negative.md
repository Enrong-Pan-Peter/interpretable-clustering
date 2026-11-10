# exp-014 — Option 1 (deceptive test): the EA does NOT beat greedy; deception traps the OBJECTIVE

**Pre-registered test** (existing `deceptive_hierarchy` generator, not built for this): does the EA's
population escape a trap that greedy-forward falls into? Trap = dim 2, a clean ORTHOGONAL bimodal
split (spurious, ARI~0); truth = dim 0 split {0}|{1,2}. Swept trap in {8,12}, seeds 0-3.

## Result: the trap is the GLOBAL persistence maximum, so every maximizer should take it.
Enumerating all pairs (score = persistence, ARItop vs the correct {0}|{1,2}):

| seed | global-max pair | ARItop | best TRUTH pair (score) | best TRAP pair (score) |
|---|---|---|---|---|
| 0 | (0,11) | 1.00 | (0,11) **4.64** | (2,11) 3.98 |
| 1 | (2,11) | 0.00 | (0,11) 3.92 | (2,11) **4.42** |
| 2 | (2,10) | 0.00 | (0,5)  4.59 | (2,10) **5.84** |
| 3 | (2,5)  | 0.00 | (0,6)  4.13 | (2,5)  **4.14** |

On 3/4 seeds the TRAP outscores the best truth panel -> a persistence-maximizer SHOULD take it.
Greedy, random, and the EA (pair-seed on) all take the trap when it is the global max. The un-seeded
EA occasionally "escapes" (seed 2 -> dim 0) but ONLY because its incomplete search never evaluated
the higher-scoring trap pair (2,10) (5.84 > 4.59). That is incomplete-search LUCK, erased by more
compute or pair-seed -- a bug, not an advantage.

## Conclusion (Option 1 = negative)
Deception traps persistence-MAXIMISATION itself, independent of the search algorithm. The correct fix
is the ACCEPTANCE GATE (stability / column-permutation null rejects the spurious trap; ties to
exp-004/exp-005), which is orthogonal to EA-vs-greedy. So a deceptive landscape provides NO
justification for the EA over greedy. Combined with exp-012 (easy=pair-seed does the work) and
exp-013 (hard=needle defeats everyone), there is no tested regime where the EA's search earns its cost.
