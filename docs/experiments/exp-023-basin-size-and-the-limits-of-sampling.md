# exp-023 — How many pairs must we look at? The basin is small, and growth does not enlarge it

**Date.** 2026-08-07. Script: `scripts/run_basin.py`. Method: `basin_fraction` and
`two_resolution_scan` in `atomicplus/evaluation/calibration.py`. Data: `results/basin.csv`.

**Why.** Every selection result in this project came from enumerating all C(p,2) pairs. That does
not scale, and it is the reason we cannot move to higher-dimensional data or to panels of more than
two features. exp-022 showed pair-seeded search works where singleton-seeded search fails, which
raised an obvious follow-up: if growth can climb from a merely-decent pair to a good panel, we never
needed the *best* pair — only *a* pair in the basin — and then sampling replaces enumeration.

**How this connects to the goal.** The goal is a recursive tree, and every node of it must choose a
panel. If each node has to enumerate C(p,2) pairs, the tree is unbuildable above small p no matter
how good the score is. So this experiment is not about speed; it is about whether the architecture
can exist at all on realistic data.

**The measurement.** Draw pairs uniformly at random, grow each with the real unsupervised search,
count how many reach 80% of the label-using pair ceiling. That hit rate is the basin fraction f.
Sampling s pairs then succeeds with probability 1 − (1−f)^s. The ceiling and the ARI of grown
panels use labels; they are instruments, and the search never sees them.

---

## 1. The result, and it refutes the claim that prompted the experiment

Graph-cut term, 30 probes each.

| dataset | pairs already above the bar (no growth) | **basin f after growth** | draws for 95% | mean grown ARI |
|---|---|---|---|---|
| Levine CD4T vs CD8T (p=32, n=300) | 6.25% | **6.67%** (2/30, CI 1.8–21.3%) | 44 of 496 | 0.100 |
| mice Behavior (p=77, n=72) | 0.27% | **3.33%** (1/30, CI 0.6–16.7%) | 89 of 2,926 | 0.193 |

**On Levine, growth adds nothing.** 6.25% of pairs are usable before growth and 6.67% after — inside
sampling noise of each other. On mice it multiplies the base by 12× (0.27% → 3.33%), which is real
but starts from almost nothing.

**So the claim that motivated this experiment is wrong and is retracted here.** After exp-022 the
working hypothesis was "the search needs any pair in the basin, and growth does the rest, therefore
sampling replaces enumeration." Growth mostly does *not* do the rest. The pair-seeded successes in
exp-022 — Levine CD4T/CD8T reaching 0.952–1.000 from all five seeds — happened because the raw score
put genuinely good pairs in the top five, not because growth rescued mediocre ones.

**What survives is weaker and still useful.** You must *sample* about 44 of 496 pairs on Levine and
89 of 2,926 on mice for 95% success, so sampling does beat enumeration by roughly 11× and 33×. That
is a real saving and it is measurable per dataset. It is not the order-of-magnitude scaling story
that would carry us to p in the thousands: at p = 20,000 a basin of a few percent still means
sampling thousands of pairs, and if f falls with p — untested — it means more.

---

## 2. Madelon: the case where seed-and-grow provably cannot start

Attempted at p=500 and abandoned after roughly 55 hours, but it produced its finding in the first
five minutes:

```
pair ceiling ARI 0.068       <- the BEST possible two-feature clustering
pairs above the bar: 0.45%   <- and the bar itself is 0.054, i.e. noise
```

No pair of Madelon's 500 features clusters the data at all. That is not a defect: the class is
XOR-like on a five-dimensional hypercube, so nothing appears until roughly five features are present
together. Seeding from 5-subsets would mean C(500,5) ≈ 2.5×10¹¹ candidates.

This is the k-junta case that Beretta (APPROX/RANDOM 2025) shows is computationally equivalent to
learning parity with noise. Our architecture requires *some* low-order signal to seed from, and
Madelon has none by construction. **That is a scope boundary with a proof attached, not an
engineering problem**, and it is worth a paragraph in the paper rather than another month.

`basin_fraction` now aborts when the pair ceiling is below 0.15 and says so, so this costs minutes
rather than days.

---

## 3. Two-resolution screening works on one dataset and not the other

Scoring is O(n²) per candidate, so screening on a row subsample and paying full price only for the
survivors is the obvious speed-up. It is only legitimate if the subsample preserves the ranking.

| dataset | Spearman, screen vs full | full winner survives the screen's top 2%? |
|---|---|---|
| mice (n 150 vs 72) | **+1.000** | yes |
| Levine (n 150 vs 300) | **+0.532** | **no** |

On Levine the screen loses the eventual winner. So this cannot be switched on globally; it has to be
checked per dataset, which is why `run_basin.py` reports it rather than assuming it. Where it holds
it is a free order of magnitude; where it does not, it silently discards the answer.

---

## 4. What this settles about the search

Combining this with exp-021 and exp-022, the picture is consistent across five datasets and it has a
mechanism rather than a shrug.

**The search works when two conditions hold**, and both are measurable *before* running it:

1. **Low-order signal exists to seed from** — the pair ceiling is well above zero. Levine 0.987,
   mice 1.000, METABRIC HER2 0.624, Madelon 0.068.
2. **The populations separate rather than overlap** — our terms score gaps, so shifted-but-
   overlapping distributions rank a coincidentally-bimodal junk pair above the real answer
   (exp-022 §3).

Levine satisfies both, and pair-seeded search reaches ARI 0.952–1.000. Mice Behavior satisfies both
and reaches 0.644 against a singleton-seeded 0.332. METABRIC satisfies the first and fails the
second. Madelon fails the first.

**The honest contribution is therefore not "our search works" but:**

> Seed-and-grow finds interpretable panels when the data has low-order signal to seed from and
> populations that separate rather than overlap. Both conditions are measurable in advance from the
> pair ceiling and the basin fraction, so the method can tell a user whether it will help with their
> data before they commit to it.

That is a scope statement with a test and three positive cases, and it does not require solving a
problem that has a hardness result attached.

## 5. Caveats

- **f rests on 30 probes.** The Wilson intervals are wide (1.8–21.3% and 0.6–16.7%). The ordering
  between datasets is not established; only the fact that both are small.
- **One term.** Everything here is graph-cut. Density behaved differently in exp-021 and was worse
  on every real dataset in exp-022, but its basin has not been measured.
- **f may depend on p, and that is the question this cannot answer.** Both datasets are p ≤ 77.
  Whether the basin shrinks as p grows is precisely what decides whether sampling scales, and it
  needs a dataset with mid-range p, real pair-level signal, and a known answer — which we do not
  currently have. METABRIC at p=250 is the nearest candidate.
- **The first Levine run and the smoke test disagree** (basin 6.67% vs 0.0% at 6 probes with a
  12-feature shortlist). Small-probe estimates of f are extremely noisy; do not quote a single run.
