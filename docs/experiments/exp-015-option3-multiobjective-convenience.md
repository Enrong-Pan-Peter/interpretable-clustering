# exp-015 — Option 3 (EA as multi-objective convenience): honest but weak

**Test.** Does the EA deliver, in ONE run, a useful quality-vs-#features Pareto front that beats what
greedy already gives? Dataset: synthetic2 (p=20, truth minimal panel {4,11}).

## EA quality/parsimony front (one run)
| size | persistence | ARI | panel |
|---|---|---|---|
| 2 | **4.63** | 1.00 | [4,11]  (true minimal panel; the peak) |
| 3 | 2.39 | 1.00 | [0,4,11] |
| 4 | 1.94 | 1.00 | [0,4,7,11] |
| 5-7 | ~1.0-1.4 | 1.00 | (larger, diluted) |

Persistence PEAKS at the minimal panel and DECREASES as features are added (dilution); ARI is 1.0 at
every size (the extra features don't break the clustering, they just dilute the gap).

## Baselines
- **greedy-forward**: finds {4,11} and STOPS at the peak (size 2) -- its halting point already tells
  you "2 features is optimal."
- **enumeration oracle**: size-2 {4,11}=4.63 (= EA); size-3 {4,7,11}=3.02, but the EA's size-3
  {0,4,11}=2.39 is SUBOPTIMAL -- the EA's per-size front is not even accurate above the peak.

## Verdict
- The front is a genuine deliverable and the compression / "few features vs many" story HOLDS
  (2 of 20 features, ARI 1.0, highest persistence) -- this is the honest interpretability win.
- BUT greedy finds the same minimal panel, its stop already signals the optimal size, and the EA's
  front is suboptimal above the peak. So the front's UNIQUE value reduces to "multiple equivalent
  panels per level" (diversity) -- which exp-012 showed is pair-seed enumeration on easy data, and
  which random blankets.
- Net: Option 3 is defensible ONLY as a convenience/usability claim (one run -> a quality/parsimony
  curve + a menu of interpretable panels), NOT a superiority claim.

## Combined verdict (Options 1 + 3)
No tested regime shows the EA as a superior search (exp-012 easy=pair-seed does it; exp-013 hard=needle
defeats all; exp-014 deceptive=objective is trapped not the algorithm; exp-015 front=convenience only).
The defensible contributions are the fair-evaluation methodology + persistence fitness + interpretability,
with the EA as a convenient vehicle. -> take to Ting for the Option-2 (methodology-first) framing.
