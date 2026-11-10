# ATOMIC+ — external review handoff

**Purpose.** A self-contained brief for the main ATOMIC working session. It carries over an
external review conducted 2026-08-01: what was measured, what the literature says, feedback on the
2026-08-01 supervisor discussion, a proposed search algorithm, and a second paper idea worth
parking for later.

**Provenance and status.** This came out of a session with read-only access to the repo.
**Nothing in `atomicplus/`, `scripts/`, `docs/` or any existing file was modified.** New artefacts
are prefixed `ec_` / `ec-`:

| file | what it is |
| --- | --- |
| `ec_diag_001_cliff_decomposition.py` | diagnostic script — reproduces the cliff, decomposes its cause, tests max-over-weights |
| `ec_diag_002_fixes.py` | tests two candidate fixes — search-matched calibration, cross-size comparability |
| `ec-findings-001-diagnosis-and-position.md` | full diagnosis + prior-art audit + paper positioning |
| `ec-findings-002-fixes.md` | fix testing results + implementable calibration shortlist |
| `ec_diag_001_full_e2.csv`, `ec_diag_00*_console.txt` | raw results and console logs |

Both scripts import the project's own `density_term`, `graphcut_term` and `load_structured`
read-only, so every number is on the same footing as `exp-018`.

**Reading order if short on time:** §1 (data bug), §2.2 (what actually causes the cliff), §3.1
(the fix that works), §6 (the proposed algorithm), §7 (feedback on the Ting discussion).

---

## 1. Fix first: the mice data is not what the docs assume

UCI Mice Protein Expression is **72 mice × 15 technical replicates = 1080 rows**, not 1080 mice.
Three replicates of a five-point dilution series per animal.

If the pipeline treats rows as independent samples, then part of the "cluster structure" the good
pairs are recovering is **mouse identity and dilution series**, not biology — and the effective n
for the 8 classes is 72, not 1080.

This directly affects `exp-019`'s headline ("65 of 2,926 pairs recover the label reasonably and the
best pair recovers it perfectly"). Either aggregate to 72 samples, or model the replicate structure
explicitly and report both. Do this before any further real-data claim; it lands the same way at a
workshop as at ICLR.

---

## 2. Diagnosis — what actually causes the 3.13 → 0.48 cliff

### 2.1 Why exp-018's explanation needed re-checking

`exp-018` attributes the collapse to dilution: distances are computed over every column, so each
junk column adds noise to every pairwise distance. That is a physical claim with a numerical
prediction — if junk adds the same expected amount to within- and between-cluster squared
distances, the mean gap is unchanged, only spread grows, so standardised separation should decay
like 1/√m in the junk count m. Anchoring at |S|=3 (m=1) against exp-018's own table:

| | predicted | exp-018 measured |
| --- | --- | --- |
| m=2 | 0.48/√2 = 0.34 | 0.31 |
| m=3 | 0.48/√3 = 0.28 | 0.26 |

The tail fits well. But the same law predicts the m=0 → m=1 step costs a factor of about 1, and
exp-018 measured **6.5**. Dilution explains the decay; it does not explain the cliff.

### 2.2 The experiment that isolates it — this is the load-bearing result

`ec_diag_001` holds the panel at |S|=3 = true pair + one added column, and varies what that third
column *is*. The critical control is a **constant column**: it adds a full dimension while
changing no pairwise distance whatsoever, separating "extra dimension" from "extra noise" exactly.

Reported as standardised margin (how many junk-pile SDs the true panel stands above the pile it
must be picked out of). Mean over moons / circles / jain, **6 seeds, 20 junk reference panels**,
structured benchmark, p=20. Percentages are retention relative to the constant-column anchor:

| third column is… | density | retained | graph-cut | retained |
| --- | --- | --- | --- | --- |
| *(none — \|S\|=2 anchor)* | 5.18 | — | 3.63 | — |
| **constant (junk × 0)** | **5.22** | 100% | **4.68** | 100% |
| junk × 0.05 | 5.22 | 100% | 4.68 | 100% |
| junk × 0.1 | 5.23 | 100% | 4.65 | 99% |
| junk × 0.2 | 4.30 | 82% | 4.49 | 96% |
| junk × 0.35 | 2.74 | 52% | 4.11 | 88% |
| junk × 0.5 | 1.88 | 36% | 3.37 | 72% |
| junk × 0.75 | 1.07 | 21% | 2.34 | 50% |
| **junk × 1 (real junk)** | **0.81** | **16%** | **1.65** | **35%** |
| duplicate of a true feature | 5.08 | 97% | 4.86 | 104% |
| permuted true feature | 2.15 | 41% | 0.63 | 14% |

The harness reproduces exp-018 first: density mean Cohen's d = 2.92 / 0.42 / 0.14 / 0.18 across
|S| = 2/3/4/5 against exp-018's 3.13 / 0.48 / 0.31 / 0.26; graph-cut 4.14 / 2.04 / 1.91 / 2.09
against 3.71 / 1.23 / 1.23 / 1.35. Same qualitative split — density collapses, graph-cut holds.

**Reading.** Adding a dimension is free (constant column: 5.22 vs the 5.18 anchor). Adding a
*duplicate of a real feature* is nearly free. The collapse is a smooth monotone function of the
added column's **scale**. And the permuted-informative row closes the argument: a column with the
identical marginal distribution to a real feature but no joint information collapses the score
like ordinary junk. So it is not dimensionality, not the density estimator, and not the marginal
shape of the column. It is the **magnitude of noise injected into the distance matrix, relative to
the between-cluster gap**.

### 2.3 What this changes about the fix

You do not need a score that ignores extra columns. You need one that keeps junk **below a
threshold that is now measured** — roughly 20% relative scale for the density term, 35–50% for
graph-cut. That is a far weaker requirement than selecting exactly the right columns, and it is a
concrete design target rather than a vague aspiration.

Two pieces of theory bracket this:

- **Durrant & Kabán, *Journal of Complexity* 25(4), 2009** — when the relevant components stay
  fixed while irrelevant dimensions grow, **any equal-weight distance must concentrate**. No choice
  of fixed metric escapes. Reweighting is the only available door.
- **Little, Maggioni & Murphy, *JMLR* 21, 2020, Thm 4.6** — the minimax-path (longest-leg path /
  LLPD) bound "depends only on the intrinsic dimension, not the ambient dimension." This explains,
  retroactively and cleanly, why **dc-dist behaved differently** and why ting-brief-2 §4e records
  it as not degrading as p grows. It also predicts the residual per-shape unevenness: LLPD success
  is governed by the inter-cluster gap versus the largest within-cluster nearest-neighbour leg,
  which is shape-dependent. That unevenness is expected behaviour, not a defect.

---

## 3. Fixes tested

### 3.1 What works — per-panel permutation calibration

**The idea in one sentence: score each panel against a scrambled copy of itself.**

For a panel S, permute each of its columns independently B times. This destroys any relationship
*between* columns (where clusters live) while preserving each column's own distribution, the
column count, and the row count. Score the scrambled versions. Then report

```
z(S) = (q(S) − mean_b q(S_b)) / sd_b q(S_b)
```

— how many standard deviations the real panel scores above its own no-structure version.

This is measured in units of "SDs above my own null," which means **a 2-column and a 5-column panel
are finally on the same scale.**

`exp-018` explicitly deferred the question this answers:

> "Whether the score peaks at the CORRECT panel size … is a cross-size comparison and raw scores
> are not comparable across sizes; it needs an absolute (scramble-calibrated) score. Separate
> experiment — do not infer it from these tables."

**Result** (density term, moons/circles/jain, B=20). True pair padded with 0/1/2/3 junk columns:

| quantity | k=2 | k=3 | k=4 | k=5 | peaks at |
| --- | --- | --- | --- | --- | --- |
| raw score of the true panel | −0.10 | −0.35 | −0.41 | −0.43 | k=2 |
| **calibrated z of the true panel** | **3.81** | **1.15** | **1.01** | **0.12** | **k=2** |
| raw margin over junk pile | 3.61 | 1.55 | 0.65 | 0.10 | k=2 |
| calibrated margin over junk pile | 3.65 | 0.87 | 1.07 | 0.04 | k=2 |

Per shape: moons k=2 (4.12), circles k=2 (5.30), jain k=3 (2.08 vs 2.00 — a tie).

The raw score technically peaks at k=2 too, but its values are all negative, sit on an arbitrary
scale, and cannot be thresholded or compared across sizes. The calibrated version separates
cleanly and is interpretable.

**Why this matters:** it gives a **stopping rule**. Grow the panel while calibrated z rises, stop
when it falls. Panel size becomes something the method discovers rather than something we tell it.
That is the single missing ingredient that forced pair enumeration.

**Novelty: none. Use it anyway.** This is DUSC / Vinh / UMC territory (§4.1). Cite it, implement
it, do not claim it. The value is that it unblocks the pipeline.

### 3.2 What does not work — max over weightings

Scoring each panel by its best weighting, q\*(S) = max over w of q(S, w), is monotone by
construction and looks like the obvious answer. `ec_diag_002` also tested whether **search-matched
calibration** rescues it (permute the panel's columns and re-run the *entire inner search* on each
replicate, so inflation appears on both sides and cancels).

Density term, standardised margin over the junk pile:

| scheme | k=2 | k=3 | k=4 |
| --- | --- | --- | --- |
| equal weights (baseline) | **4.36** | 1.72 | 0.37 |
| max over weights, uncalibrated | 1.08 | **4.25** | **1.48** |
| max over weights, calibrated | 2.24 | 3.47 | 0.17 |

Calibration recovers about a third of the k=2 damage but never beats plain equal weighting.

**The diagnostic that explains it** — max-gain, i.e. how much a panel gains from being *allowed*
to search over weightings (max over options minus mean over options):

| panel type | k=2 | k=3 | k=4 |
| --- | --- | --- | --- |
| true panel | 0.211 | 0.314 | 0.134 |
| junk panels | 0.326 | 0.155 | 0.111 |
| **junk gain ÷ true gain** | **1.55** | 0.49 | 0.83 |

At k=2, junk panels gain **55% more** from searching than the true panel. That is the inflation
measured directly: the true panel's weightings all see the same real structure so its options are
correlated and its max is close to any one of them, whereas a junk panel's options are
near-independent draws and its max is the maximum of many samples. **Verdict: drop this direction.
Keep the max-gain table as a figure** — it is a clean quantitative demonstration of a failure mode
that recurs throughout the project.

### 3.3 The general lesson about maxima — applies in three places

Three things this project does are the same statistical operation:

- max over C(p,2) candidate panels (the false-positive effect, HANDOFF §3b.4)
- max over the three candidate splits (prereg-001 Claim 3)
- max over weightings (§3.2)

All are maximally-selected statistics. And the trap: **a correction depending only on the number of
options searched cannot help.** Every panel searches the same nominal K, so Bonferroni, Šidák or
any fixed critical value applies the same constant to every panel and **leaves the ranking exactly
unchanged.** What differs between panels is the *effective* number of independent options, driven
by how correlated the option-scores are within that panel. Only a per-panel, search-matched null
captures it. (prereg-001 §4 already says the BH step cannot reorder Claim 1's ranking — that is
correct and it is the same point.)

### 3.4 The weighting method that suggests itself is already published

The natural design — given a bipartition, weight each column by its own separation-to-raggedness
ratio decomposed from the density criterion, then iterate — is anticipated in two pieces:

- **Tsai & Chiu, *CSDA* 52(10):4658–4672, 2008 (FWSA)** owns the ratio weight: separation over
  within-cluster dispersion, per feature, normalised, updated inside the clustering loop.
- **Chowdhury, Helian & de Amorim, "Feature weighting in DBSCAN using reverse nearest neighbours,"
  *Pattern Recognition* 137:109314, 2023** owns per-feature MST compactness inside a density-based
  clusterer with alternating reweighting. Their motivation is ours nearly verbatim: *"DBSCAN … is
  capable of recovering non-spherical clusters. One of its main weaknesses is that it treats all
  features equally."* Their future-work section names the extension.

Two further warnings before investing in it:

- **The decomposition is not really a DBCV decomposition.** DSC is a *max* over within-cluster MST
  edges, DSPC a *min* over between-cluster links. Extremal statistics have no additive
  per-coordinate decomposition, so a per-column version quietly replaces them with means. Say so,
  or a reviewer will.
- **Convergence probably breaks.** The ratio update is not a descent step on any single objective —
  FWSA's known weakness relative to EWKM. Chowdhury et al. inherit EWKM's guarantee *precisely
  because* they kept only the denominator. Adding a numerator likely destroys it. That may be why
  nobody has published the combination.

**The genuinely open ground:** no work combines **learned feature weights with a minimax-path /
density-connectivity / ultrametric distance** (dc-dist, LLPD). Every method in that family uses an
unweighted base metric. It is open because it is hard — weights change which edges are in the MST,
which changes the ultrametric, which changes the clustering. And it sits exactly where ting-brief-2
§4e already measured the best gradient. Paper-sized idea, not an August task.

Also unclaimed: a per-feature *separation* statistic on mutual-reachability links. Chowdhury has
compactness; nobody has the separation half.

---

## 4. Prior-art corrections — claims that should be retired before submission

### 4.1 "Nothing since 2008 on making subspace scores comparable across panel sizes" — false

The problem has a formal name (**dimensionality unbiasedness**), a formal definition with theorems,
and multiple correction mechanisms:

| Year | Work | Mechanism |
| --- | --- | --- |
| 2004 | Dy & Brodley, *JMLR* 5:845–889 | States the problem almost verbatim in the same setting; cross-projection normalisation; proves the ML criterion prefers lower dimensions |
| 2004 | SURFING (Baumgartner et al., ICDM) | Ranks subspaces across dimensionalities *(characterised from a secondary source — primary unreachable)* |
| 2007 | **DUSC** (Assent, Krieger, Müller, Seidl, ICDM) | The formal definition: dimensionality unbiased iff E[φ_S₁] = E[φ_S₂] for all subspaces; fixed by dividing by expected value |
| 2012 | **HiCS** (Keller, Müller, Böhm, ICDE) | Monte-Carlo subspace slices with α₁ = α^(1/\|C\|), holding expected slice count constant across dimensionality |
| 2016 | **Vinh et al.**, *DMKD* 30:1520–1555 | Formalises unbiasedness and **proves Z-score normalisation achieves it** (Thm 3) |
| 2017 | **UMC** (Wang, Romano, Nguyen, Bailey, Ma, Xia, AAAI) | Subtracts expected value under the **permutation model**; names "Comparability" as an explicit design criterion |
| 2019 | **MCDE** (Fouché & Böhm, SSDBM) | Dimensionality-aware slicing; its Requirement R6 is a precise statement of our complaint |

**The narrowed version that survives:** nobody has established dimensionality unbiasedness
specifically for normalised graph cut or DBCV-style validity indices, and nobody couples per-subspace
calibration with FDR control over the search lattice. Workshop-sized delta, honestly stated.

### 4.2 prereg-001's null calibration is largely pre-empted

UMC (AAAI 2017) already calibrates a subspace score against a **permutation model that permutes
columns independently, preserving marginals and destroying dependence** — prereg-001 §3's null,
adopted for prereg-001's purpose. UMC computes it analytically for speed, which makes Monte-Carlo
the signposted alternative rather than a new idea. Per-subspace hypothesis testing also exists
(Müller, Schiffer & Seidl, ICDE 2011).

What could not be found anywhere: an *empirical Monte-Carlo permutation p-value per subspace*
followed by *Benjamini–Hochberg across the candidate set*. Real, but thin.

**Still run prereg-001 Stage 0** — it is cheap and decides the question in an afternoon. But update
prereg §2 to record UMC as prior art first, so the result is interpreted against the right baseline.

### 4.3 The z-score may be a bug, not a research gap — check this first

`scripts/run_fitness_sweep.py:72` and `atomicplus/evaluation/subspace_baselines.py:142`:

```python
def z(v): v = np.array(v, float); s = v.std(); return (v - v.mean()) / (s if s > 1e-9 else 1.0)
comb = {..., "hyb_gcut_dens": z(gc) + z(de)}
```

`gc` and `de` are vectors **over the pool of candidate pairs**. So the z-score is taken *across
panels*, not against a per-panel reference distribution. Three consequences:

- **No cross-|S| comparability anywhere in the path.** The inability to compare |S|=2 against
  |S|=3 that blocks search is a direct consequence of this, not a property of the signals.
- **It is not the Vinh et al. construction**, whose Z is taken against the score's own null
  *within* a subspace. So the project does not currently get the Theorem 3 guarantee. A reviewer
  who knows that paper will ask why `z(gc)+z(de)` is not simply Theorem 3.
- **Term weighting is pool-dependent** — how much graph-cut counts relative to density depends on
  the spread of whatever pool happened to be compared.

`exp-018` already spotted the pool-relativity and worked around it by standardising against the
junk group. The step not yet taken: **z against a per-panel permutation null instead of the pool**,
which delivers cross-size comparability and per-panel variance removal in one change. ~20 lines
plus B× score cost. Try it before designing any new method.

### 4.4 Smaller corrections

- **"No successor benchmark to OpenSubspace" survives but must be narrowed** to *axis-parallel
  subspace clustering on static data*. Threats to the broad phrasing: Moise, Zimek, Kröger,
  Kriegel, Sander (*KAIS*, 2009) — independent same-year evaluation, different group; Subspace MOA
  / Hassani et al. (*JIIS* 45(3), 2014) — a genuine post-2009 framework, for streams; Günnemann et
  al. (CIKM 2011) — external measures. Non-threats, checked: CLUBench (2026), ClusBench (2026),
  clustbench (*SoftwareX* 2022), ClustPy.
- **Citation error.** "OpenSubspace, VLDB 2009" conflates two papers: the evaluation study is
  Müller, Günnemann, Assent, Seidl, *PVLDB* 2(1):1270–1281, 2009; the WEKA toolkit is Müller,
  Assent, Günnemann, Seidl, OSDM workshop @ PAKDD 2009.
- **ATOMIC (Vandergrift & Hu, GECCO '24, pp. 319–322) is a 4-page poster.** Fine to build on, weak
  as load-bearing related work.
- **DISCO's** ICLR 2026 camera-ready title is "Internal Evaluation of Density-Based Clusterings
  with Noise" — DISCO is the method name.
- **GroupFS** *discovers* latent feature groups; it does not consume predefined panels. See §8.

### 4.5 DUFS is the biggest single threat, and I owe a correction

**Lindenbaum, Shaham, Peterfreund, Svirsky, Casey, Kluger, "Differentiable Unsupervised Feature
Selection based on a Gated Laplacian," NeurIPS 2021.** Their demo notebook is **n=100, p=20, two
moons + 18 i.i.d. Gaussian nuisance** — our benchmark, five years ago, with public code at
`github.com/Ofirlin/DUFS` (TF 1.x era, unmaintained; core is ~100 lines, easier to reimplement in
PyTorch than resurrect).

**Correction to an assumption made earlier in this review:** the single-column check (0% recovery)
does *not* protect us. DUFS does not assume informative features are marginally separable — it
assumes they are **individually smooth along the graph**. Neither moons coordinate is marginally
bimodal, yet each varies smoothly along the moon manifold, which is why DUFS solves it. Graph
smoothness is a much weaker requirement than marginal separability.

**But there is a specific, mechanistic reason to expect it fails on the structured benchmark.** Its
per-feature score is essentially a within-neighbourhood vs total variance ratio, and an open
feature *contributes to the metric that defines its own neighbourhoods*. A z-scored
multimodal/skewed column has most of its variance *between* lumps and little *within* them, so it
pulls same-lump points together in the metric and then scores as highly smooth on the graph it just
helped build. Self-confirmation. A two-moons coordinate, marginally unimodal and spread out, scores
worse by comparison. **The ordering can invert.** Gaussian nuisance is the best possible case for
DUFS precisely because structureless columns cannot systematically fake smoothness.

Also worth knowing: DUFS's objective is **additively separable across features given the graph** —
there is no pairwise or interaction term anywhere in the loss. It gets two moons right by a lucky
property of that dataset, not by any joint-selection capability.

**Action:** run their own notebook, swap N(0,1) nuisance for the structured junk at matched
variance, and watch their Fig. 5 precision/recall curve. Highest-priority experiment in this
document after the mice fix.

**Free idea from it:** the parameter-free variant divides the objective by the expected number of
open gates, making it **scale-free in panel size**. Cheap thing to try against the panel-size
problem.

### 4.6 Correlation Detective publishes our motivating sentence

**Minartz, d'Hondt & Papapetrou, *PVLDB* 15(6):1266–1278, 2022**: *"groups with low pairwise
correlations can still be strongly correlated as a whole, and these are arguably the most
interesting cases."* Its saving grace: both supported measures are **linear and Pearson-based**, so
it cannot see two moons or concentric circles. That is the cleanest available statement of where
our gap actually is.

---

## 5. The hardness result — what it does and does not mean

The target class — *structure present in k features jointly, with no signal in any proper subset* —
has a formal name: **k-junta distributions** (Aliakbarpour, Blais & Rubinfeld, COLT 2016, PMLR
49:19–46), framed literally as "learning distributions in the presence of irrelevant features."

**Beretta (APPROX/RANDOM 2025, LIPIcs 353, art. 31)** proves learning k-junta distributions is
**computationally equivalent to learning k-parity with noise (LPN)**. Beating the n^k scan would
be an LPN breakthrough. Supporting this from another direction, Diakonikolas, Kane, Ren & Sun
(NeurIPS 2023) give near-optimal statistical-query lower bounds for hidden non-Gaussian subspace
structure under a moment-matching condition alone — and SQ covers essentially every spectral
method, moment method, EM variant and gradient-based learner one would try.

**What it does not mean.** Not "unsolvable." Read the exponent: n^k with k=2 is C(p,2) — 190 at
p=20, 2,926 at p=77, 500k at p=1000. Trivial to affordable. k=3 at p=100 is 162k triples; fine.
**The barrier bites at k≥4 and large p.** Clinically useful interpretable panels are 2–5 features,
so the practical goal sits inside the tractable region. The honest scoping statement:

> Solvable for small panels by paying the full exhaustive cost, and that cost is affordable. What
> is blocked is scaling to arbitrary panel size.

**The structural version, no complexity theory required.** Every bottom-up subspace method —
CLIQUE, ENCLUS, MAFIA, SUBCLU — prunes using **downward closure**: dense units in k dimensions
imply dense units in all (k−1)-dimensional projections. Our benchmark makes that false by
construction, so the pruning rule is *invalid* on our data. Those methods cannot find our structure
at any parameter setting. One sentence, no conjecture needed.

**Reading the project's negatives against this.** "The EA does not earn its keep." "Random matches
or beats it everywhere." "No budget-limited search reaches the enumeration ceiling." "The landscape
is a cliff, not a slope." These are not engineering failures — they are what a conditional lower
bound looks like from the inside. The EA was asked to exploit partial progress in a problem class
*defined by the absence of partial progress*.

**The detail to raise with Ting.** Hu, Andrew, Karagas & Moore (*Pacific Symposium on Biocomputing*,
2013) reduce a 3-locus search from 5.3M candidates to 391 by traversing a pairwise information-gain
network, justified explicitly by:

> "it is much less likely for a higher-order interaction to exist without showing any lower-order
> interactions than without showing any main effects."

Our synthetic benchmark is precisely the case where that heuristic does not hold. Not a
contradiction to apologise for — it is the natural way to connect this work to the lab's existing
line, and the generalisable question is *how much lower-order signal is needed before search
becomes possible.* §7.5's dial is the beginning of an answer.

---

## 6. Proposed search algorithm — calibrated seed-and-grow with abstention

This is the constructive proposal. It handles the relaxation agreed in discussion — panels may
contain individually-useful features *or* jointly-necessary ones — which makes it easier, not
harder.

**Design principle: one mechanism gates every stage.** Cross-size comparison, method selection,
abstention and confidence reporting all come from the same per-panel permutation calibration (§3.1).
That is what makes it an architecture rather than a pile of tricks.

**Stage 0 — screen singletons.** Calibrated z for every single feature. Cost: p evaluations. Maps
which features carry individual signal without committing to them.

**Stage 1 — seed on two channels.** The key design decision, and it exists precisely because both
regimes are now in scope:

- *Channel A* — pairs among the top-scoring singletons. Cheap; catches everything where individual
  signal exists.
- *Channel B* — a stratified sample of pairs among the **low**-scoring singletons. The only place
  jointly-necessary panels can live, and Channel A will never look there.

Split the budget between them. Channel B is exactly what the bottom-up methods silently drop (§5),
and having it is a defensible design contribution.

**Stage 2 — grow, with the stopping rule.** From each surviving seed, try adding each remaining
feature; accept only if calibrated z **increases**. Also try removals and swaps (steepest-ascent
local search). Stop when nothing improves. This is what §3.1 showed is possible and raw scores
could never do. **Panel size becomes discovered rather than assumed.**

**Stage 3 — abstain or commit.** If the best panel fails significance after correcting for the
search performed, output *"no structure found at this node"* rather than forcing a split. This is
prereg-001 Claim 2.

**Stage 4 — choose the split method by the same calibration.** Run persistence / HDBSCAN /
spectral / dc-dist through the *same* null and take the best calibrated. Raw HDBSCAN stability and
raw NCut are not on a common scale; calibrated they are. This is prereg-001 Claim 3, which the
prereg already calls "the most likely to work."

**Stage 5 — recurse** on each child.

**Stage 6 — retain alternatives.** Keep the top-K *distinct* high-confidence panels per node, not
just the argmax. This is what generates multiple alternative trees for the interface (§7.4).

**Cost.** Calibration multiplies every evaluation by B. Use a two-stage budget — cheap screen at
B≈10, then B≈200 for finalists — and **synchronised permutation seeds across panels**, so Monte
Carlo noise is common-mode and the *ranking* is far more stable than B alone suggests. Stage 1
dominates: at p=77 (mice), ~2,900 pairs × 30 nulls ≈ 90 minutes. At p=561 you must sample or lean
on the Stage 0 screen to prune.

**Calibration schemes worth implementing, in order** (from a focused search on maximally-selected
statistics):

1. **Freeze-argmax with held-out scoring.** Split the rows. Run the full inner search on half A,
   record only the *argmax* (winning weights/split/structure). Evaluate that frozen configuration
   on half B. The reported score contains no maximum, so inflation is identically zero. ~30 lines,
   ~2× one inner search. Gives an unimpeachable reference ranking to validate everything else
   against. *One trap:* Gao, Bien & Witten (*JASA* 119(545), 2024) show sample splitting does not
   rescue post-clustering inference — but that does not apply here. Their hypothesis is about
   cluster membership of test points chosen using test points; ours is fixed in advance, and only
   a *configuration* is selected on A and applied to B as a fixed function. Keep the held-out
   evaluation strictly non-adaptive and it is valid.
2. **Per-panel search-matched permutation gap.** §3.1 extended so the whole inner search re-runs on
   each replicate. This is the sparse-k-means permutation gap (Witten & Tibshirani, *JASA*
   105(490):713–726, 2010), itself an instance of the gap statistic (Tibshirani, Walther & Hastie,
   *JRSS-B* 63(2):411–423, 2001) — and sparse k-means *is* a max over feature weightings, so the
   template is not an analogy.
3. **Beta fit on the null minimum-p → effective search size.** Nearly free given (2). Under
   independence the min-p over K options is Beta(1, K); fit Beta(a,b) by MLE to the
   permutation-derived null min-p values, and the fitted **b estimates that panel's effective
   number of independent options** (Ongen et al., *Bioinformatics* 32(10):1479–1485, 2016 —
   FastQTL). Turns §3.2's max-gain table into a principled measurement and a strong figure.
4. *Optional diagnostic* — option-correlation matrix, effective test count from its eigenvalues
   (Li & Ji, *Heredity* 95(3):221–227, 2005). Good for explanation, not for quoting p-values.

**Do not build:** PoSI (Berk et al., *AoS* 41(2), 2013 — needs a response variable); polyhedral
selective inference (Lee, Sun, Sun & Taylor, *AoS* 44(3), 2016 — needs Gaussian response and a
polyhedral selection event); classical maximally-selected closed forms (Miller & Siegmund 1982;
Lausen & Schumacher 1992 — assume an *ordered, nested* family so the statistic converges to a
Brownian bridge; 20 arbitrary weight vectors are not that); any nominal-K correction (§3.3); a
single shared reference null for all panels.

Cite but do not build: Chen & Witten (*JMLR* 24(152), 2023) do selective inference for k-means by
conditioning on all intermediate cluster assignments — the philosophically correct version — but
the estimand is a difference in cluster means under a known isotropic Gaussian model.

---

## 7. Feedback on the 2026-08-01 supervisor discussion

### 7.1 On reporting

There is a legitimate version of "report our advantages, mention limitations briefly" and a risky
version, and the practical rule is:

> **Choose what you claim; do not choose what you report within what you claim.**

Scoping to "convex and moderately non-convex structure" is entirely legitimate — every paper
scopes. Running moons, seeing it fail, and omitting it from a suite that reports jain and spiral is
the risky version, specifically because jain/flame/spiral/moons is *the* standard non-convex set;
the omission is more conspicuous than the failure would be. This also matters because HANDOFF §4.6
already commits the project to not doing it.

**Ting's reframe mostly dissolves the tension.** If the contribution is the tree and the interface
rather than clustering accuracy, moons failing is a limitation rather than a refutation. It can be
reported at near-zero cost, which is a far more comfortable position than hoping nobody asks.

Useful precedent to show her: **GroupFS (AAAI 2026) reports all nine datasets including two —
Yale and NMNIST — where the "use all features" baseline beats it**, states so in the text, reports
its C=2 failure case in Fig. 3, and has a genuine limitations paragraph. Strong venue, strong
group, failures reported. Honesty and publishability are not in tension here.

### 7.2 The interpretability pivot is right, but it has one flaw that must be fixed

Ting identified it herself: *"fitness is not showing partial signal either way, so there is no
guarantee the recursive algorithm is correct even at the first level."*

That is fatal to the interpretability framing **as stated**. An interpretable tree whose first
split may be arbitrary is worse than no tree — it is confidently misleading, and a reviewer in the
interpretability community will ask "interpretable, but is it *right*?" A faithful explanation of
an unreliable decision is not a contribution.

### 7.3 The fix — and it is already in prereg-001

Calibration (§3.1) turns the flaw into the feature:

- Every node carries **its own confidence**: "this split is 3.8 SDs above what this panel would
  produce with no structure" versus "0.2 SDs — indistinguishable from noise."
- When nothing clears threshold, the tree **refuses to split** and says so.
- "No guarantee at level 1" becomes *measured and disclosed per node*, with the option to decline.

**This is a genuine capability claim no baseline has.** prereg-001 already spotted it: *"None of the
neighbouring methods (SUBCLU, HTC, oblique trees) can abstain, so this is a capability claim, not a
performance claim."* SUBCLU cannot say "I don't know." Neither can oblique trees, HTC, or DUFS.

**Proposed framing:**

> An interpretable recursive clustering tree where every split carries a calibrated confidence and
> the method can decline to split.

Interpretability-first ✓. Established metrics reused with no novelty pressure ✓. No need to beat
SOTA ✓. And a real technical contribution that is *not* the tree structure or the interface, both
of which are individually too weak to carry a paper.

### 7.4 Ting's EA suggestion — right instinct, wrong tool, plus a better EC angle

Using an EA to choose between density / graph-cut / hybrid at each node: **skip it.** That is a
choice among 3–4 options; evaluate all four. An EA over four options is machinery without benefit
and a reviewer will say so. But her underlying instinct — *the method choice should be automatic,
not hand-set* — is right, and calibration delivers it (Stage 4). Worth presenting to her that way:
her goal, achieved more simply.

**The EC angle that does survive.** Every negative result tested EC at finding the *single best*
panel, where random matched or beat it. The tool Ting describes needs something different: **a
diverse set of equally-valid alternative trees.** That is quality-diversity, which is what NSLC and
MAP-Elites are actually for, and it is the lab's home turf. The earlier diversity claim collapsed
because it was framed as "the EA finds better panels"; reframed as "the user needs several distinct
valid explanations, here is how we populate that archive," the archive *is* the deliverable.

*Caution so exp-009 does not repeat:* random sampling plus a calibrated validity filter may
populate the archive just as densely. Test it. If random wins again, report that the generator can
be simple because the **calibration** is doing the work — a perfectly good finding for a tool paper.

### 7.5 On the relaxation, and a dial that already exists in the literature

Allowing panels to contain individually-useful features is a good move, and stronger than it looks.
Every current result is measured at **one point** — marginal signal exactly zero — which is why
everything reads as "it fails." A single dot is hard to sell; a curve is a paper.

Concretely: keep the moons/circles planted in two columns, but add to each a small class-dependent
shift of size δ. At δ=0 this is exactly the current setup; as δ grows each column alone carries a
weak signal while the joint structure remains. Sweep δ.

What that buys:

- **A gradient exists again**, so search is not doomed by construction. The "cliff, not a slope"
  finding was true *because a cliff was built*.
- **The EA work returns.** *At what marginal strength does evolutionary search start to earn its
  keep over random?* All the infrastructure exists — `run_ea_newfit.py`, fair SFS greedy,
  matched-budget random, 20-seed protocols. Nobody has measured it, and it is directly relevant to
  the lab.
- **The problem stops being LPN-hard**, since cheap search becomes valid again.
- **It aligns with Ting's PSB line rather than falsifying it** — you are measuring how much
  lower-order trace her heuristic needs.

**The dial already exists in the literature.** GroupFS's ρ generates informative features as
x′ = √ρ·x + √(1−ρ)·ε with ρ ∈ [0.6, 1], where x is a moons coordinate. At ρ=0.95 (their default) a
feature is 95% the raw coordinate — very strong individual signal. Their range stops well short of
zero. So: **GroupFS occupies (high ρ, Gaussian nuisance); we occupy (ρ→0, structured nuisance).**
Extending their axis in two directions they did not go is a far more comfortable position than
"we beat GroupFS," and it makes our benchmark immediately legible to anyone who knows their paper.

**The one thing that must be shown** for the relaxation to be a contribution: a regime where
marginal-only selection fails but marginal-plus-joint succeeds, and that it is **wide, not a
knife-edge**. Concrete experiment: run a pure marginal filter (Laplacian Score, variance ranking)
alongside the joint score across the δ sweep and find the band where they diverge.

### 7.6 "What would count as evidence that a disagreement is meaningful?"

Four bars. A disagreement with established labels is meaningful when:

1. **It is real** — high calibrated z. Structure, not noise. Without this, disagreement is failure.
2. **It is stable** — reproduces across subsamples and reruns (Bryant's suggestion).
3. **They cannot find it either** — the established method, *given our panel*, still does not
   recover our split. Rules out "they just weren't looking there."
4. **It predicts something not used** — cluster on one set of variables, show the split aligns with
   a **held-out** variable that never entered the clustering.

Bar 4 is the gold standard and it is directly runnable: **Mice Protein has Genotype, Treatment,
Behavior and the composite class.** Cluster on proteins, disagree with Behavior, align with
Treatment → a meaningful disagreement with external evidence. exp-019 already shows Genotype
behaves differently from Behavior at pair level. **Fix the replicate issue (§1) first**, or the
alignment numbers will be inflated by replicate structure.

### 7.7 "What would a minimum publishable result look like?"

**Workshop (4–8pp, 29 Aug):** the calibrated tree with abstention; a demonstration that it
correctly abstains on planted-null data at a controlled false-discovery rate; that it finds panels
of the right size where they exist; one real dataset with the §7.6 disagreement analysis; the
dose-response curve (§2.2) as the motivating figure. Achievable, mostly from existing code.

**ICLR (9pp, 25 Sept):** the above, plus a **capability comparison** rather than a performance one
— can SUBCLU / oblique trees / HTC / DUFS choose their own panel size? report per-split confidence?
abstain? (no, no, no) — plus performance wherever we win, honest limitations, and the released tool.

**Odds, honestly: 20–25% at ICLR** for this framing. Lower than the §9 benchmarking story, but far
more deliverable by September, much better aligned with Ting, and it uses the code that exists. The
abstention capability is what keeps it above a pure tool paper. Note the two are not exclusive —
§9's findings become the *motivation* section: existing selection is unreliable in this regime,
*therefore* per-node confidence is necessary.

---

## 8. What to borrow from GroupFS (AAAI 2026)

Full paper attached separately. The methodology is the least borrowable part; the experimental
design is the most.

**Borrow — the experimental protocol.** Two scenarios rather than one: *fixed budget* (every method
gets the same number of features) and *adaptive budget* (every method picks its own from
{50,100,200,400} and reports its best). Running both closes the "you handicapped the baselines"
objection from both directions. Plus: *"hyper-parameters are set based on the lowest loss, without
supervision"* and *"ground-truth groups are used only to compute evaluation metrics; the model is
trained without access to this information."* They also standardise the kernel across all
graph-based baselines "to avoid manual bandwidth tuning" — a fairness move worth copying. This is
exactly the territory where our fair-evaluation finding lives.

**Borrow — their metrics, which are better instruments than rank-1 selection rate.**
**RG_sim** (Jaccard overlap between discovered and true groups, so partial recovery scores
partially), **TPR** (fraction of informative features selected), **FDR** (fraction of selected
features from the noise set). Caveat: RG_sim first discards predicted groups that don't overlap
any informative group, so it doesn't penalise spurious pure-noise groups — FDR covers that, which
is presumably why they report both. Report both.

**Borrow — the self-tuning kernel** (their eq. 1, from Zelnik-Manor & Perona 2004):
W_ij = exp(−‖x_i−x_j‖²/(γ_i γ_j)) with γ_i the distance from point i to its K-th nearest neighbour.
Per-point adaptive bandwidth. HANDOFF flags `k=10` and `core_k=5` as untuned defaults with untested
sensitivity — this removes the bandwidth choice rather than tuning it.

**Borrow — the diffusion power** P^t with t=2 rather than a single-step random walk. Suppresses
spurious single edges in a noisy kNN graph. Two-line change, worth an ablation.

**Borrow — group-level gating, for one specific use.** Their trick cuts learnable gating parameters
from d to C. Our features are not redundant so their grouping engine will not work on our data, but
the idea transfers to *seeding*: at p=1000, C(1000,2)=500k pairs; pre-group correlated features into
~50 clusters and the seed scan drops to C(50,2)=1225. A legitimate way to make Stage 1 affordable
at clinical scale.

**Do not borrow the differentiable machinery.** Gumbel-Softmax with temperature annealing,
stochastic gates, two Laplacians, an orthogonality penalty, a trainable projection Q, plus λ₁, λ₂,
β, C, t, p_main and an annealing schedule, tuned by grid search over λ₁/λ₂ on lowest loss. Large
tuning surface for a project that explicitly worries about benchmark-hacking. And their own
Conclusion states: *"the sample and feature graphs rely on Euclidean distances, which can
misrepresent data on curved, non-Euclidean manifolds"* — which is precisely our setting.

**Related-work paragraph, which writes itself:**

> Group feature selection discovers sets of features that are **redundant** with one another — the
> feature-similarity graph rewards high mutual affinity, and the synthetic groups are five noisy
> copies of the same coordinate. We study sets that are **jointly necessary**: individually
> uninformative, informative only in combination. These are opposite selection pressures, and a
> method built for one does not transfer to the other.

Their framing sentence — *"Jointly discovering groups, selecting which ones are informative and
rejecting the rest, without labels, remains an open problem"* — is a useful citation that this
problem area is live in 2026.

---

## 9. Parked for later: the benchmarking paper

Worth writing down because it is a genuinely strong idea and the evidence keeps accumulating, but
it is a *second* paper, not the September one.

**The claim.** Unsupervised feature selection is validated almost exclusively on Gaussian nuisance,
and Gaussian nuisance is the single easiest case.

**The mechanism.** These methods all work the same way: guess which columns matter → build a
distance/graph using the guess → see which columns agree with the resulting structure → update →
repeat. At step one the guess is "all columns," so the graph is noise-dominated. The loop only
reaches the right answer if the informative features have a **correctly-signed advantage at
initialisation**. The feedback is an *amplifier*, not a safety mechanism — it amplifies whichever
ordering it starts with, and none of these papers proves the dynamics escape a bad start.

Under i.i.d. Gaussian nuisance the initial ordering is *guaranteed* correct, because structureless
columns cannot systematically fake graph-smoothness. Under **structured** nuisance — lumpy, skewed,
multimodal, i.e. what real tabular and clinical data look like — a junk column pulls its own
clump-members together in the metric and then scores as smooth on the graph it helped build. The
ordering inverts and the loop locks into the wrong basin with high confidence.

**Evidence already in hand:**

- **DUFS (NeurIPS 2021)**: demo notebook is 2 moons + 18 i.i.d. Gaussian nuisance.
- **GroupFS (AAAI 2026)**, §5.2 verbatim: *"The remaining features (11-20) are i.i.d. Gaussian noise
  with zero mean and unit variance."* Their robustness study (Fig. 2D) varies the **sample-level**
  additive noise std, not the nuisance distribution. Nuisance is Gaussian at every setting.

If LS, MCFS, CAE and MGAGR show the same pattern — likely — this stops being speculation and
becomes a documented fact with citations.

**Why our benchmark repair is the instrument.** Making junk columns lumpy to close the
single-column leak was recorded as a bug fix. It is actually the first benchmark in this area that
violates the field's unexamined assumption.

**The full shape: a two-axis phase diagram.**

- axis 1 — δ (or ρ): how much individual signal the true features carry (§7.5)
- axis 2 — noise structure: Gaussian → lumpy

Run the grid with 5–8 published methods, scored with GroupFS's own RG_sim / TPR / FDR so the
comparison is on their terms. The output is a map of which regions are solvable by which methods
and where each breaks. GroupFS sits at one corner, our current setup at the other, and every prior
negative result becomes a located point rather than a failure.

**Honest status: a hypothesis with a good mechanism, not a finding.** It has not been run. What
would make it a paper: **breadth** (5–8 methods across families, so it indicts a practice rather
than a method), **mechanism** (we can explain, predict which methods suffer, and predict when),
and **actionability** (it tells the field to change its synthetic benchmarks). What would kill it:
if the effect needs extreme lumpiness, reviewers call it contrived — though our structured noise is
gentle (overlapping modes, no clean gaps), which helps.

**Estimated odds if executed well: 25–35% at ICLR** — higher than the interpretability framing, but
it needs a broad method sweep that will not be ready by September. Best target: **NeurIPS 2027
Evaluations & Datasets**, whose call explicitly welcomes "critiques of existing benchmarks,"
"negative results and audits," "stress-testing of prior work," and states *"submissions need not
introduce a new model or outperform prior work."* That track closed 6 May 2026 for this cycle. It
is the single best-matched venue in the ecosystem for this idea.

---

## 10. Venues and dates

- **NeurIPS 2026 main track and Evaluations & Datasets** — both closed **6 May 2026**.
- **AAAI-27** — closed **28 July 2026**.
- **NeurIPS 2026 workshops** — all deadlines **29 Aug**, notification **29 Sept**, all non-archival.
  The official list was still unpublished as of 1 Aug (organisers notified 11 July; individual sites
  live). **Wait for the list before committing.** Of what is confirmed, **New In ML** is the best
  practical fit (all ML topics, 2–8pp, Paris; eligibility: no prior NeurIPS/ICML/ICLR paper). There
  is currently **no NeurIPS 2026 workshop on unsupervised learning, clustering, dimensionality
  reduction or benchmarking methodology.**
  - **ICBINB-BIO: do not submit.** Themed editions track their theme closely, the reviewer rubric's
    first criterion is *"Is the biological task, modeling approach, and claimed failure mode clearly
    stated?"*, and the organisers are single-cell/regulatory-genomics people. One UCI tabular file
    will not clear it, and the replicate issue (§1) would be spotted immediately. Flips to a strong
    fit if a real single-cell dataset is ever added.
  - **Interpretability for Discovery: skip.** It is a mechanistic-interpretability workshop; our
    failure is not about interpretability of a trained model. Acceptance likely, audience wrong.
- **ICLR 2027** — abstract **18 Sept**, paper **25 Sept**, 9 pages. Note workshop notification
  (29 Sept) lands *after* the ICLR paper deadline, so the workshop is visibility, not a review cycle.
- **TMLR** — rolling; its criteria explicitly protect this kind of work (evidence quality plus
  "would some individuals be interested"; lack of SOTA is *not* grounds for rejection). **Caveat:**
  author submission quotas enforced from 1 July 2026, roughly 2/year solo, and withdrawn or
  desk-rejected submissions still count.
- **AISTATS 2027** — unannounced; historically early-to-mid October; strong topical fit. Monitor
  aistats.org directly, as the deadline aggregators are currently contradictory.

---

## 11. Recommended order of work

1. **Fix the mice replicate issue** (§1). Blocks every real-data claim.
2. **The per-panel-null z change** (§4.3, §3.1). ~20 lines. Confirmed to work; gives cross-size
   comparability and a stopping rule; answers exp-018's deferred question.
3. **Run DUFS on the structured benchmark** (§4.5). Biggest single threat, and a pip install.
   Also the first data point for §9.
4. **Prototype the search algorithm** (§6) — Stages 0–3 first; Stages 4–6 after.
5. **The mice held-out-label disagreement test** (§7.6). Answers Ting's question with data.
6. **Firm up §2 and §3 to publication strength** — full seeds, all six shapes, both terms, plus the
   graph-cut arm of the calibration test which had not finished at handoff.
7. **prereg-001 Stage 0**, with §3.3 folded into interpretation and §4.2's UMC prior art recorded
   in prereg §2 first.
8. **Write the workshop paper** against the §7.3 framing.

---

## 12. Verification caveats

Stated so nothing here is trusted more than it should be.

- **E3 (§3.2)** used a crude 20-vector random weight bank rather than a real optimiser, on two
  shapes. The direction held between a 12-vector and a 20-vector run and the mechanism is
  understood, but magnitudes are indicative.
- **The graph-cut arm** of the §3.1 calibration test had not finished at handoff (spectral
  clustering on permuted data is slow). All §3.1 numbers are the **density** term, which exp-018
  identified as the search-relevant one.
- **§9 is a hypothesis, not a result.** It has not been run.
- **SURFING's** internal normalisation is characterised from a secondary source (KISS, EDBT 2021);
  every primary mirror redirected. **RIS's** (PKDD 2003) mechanism could not be verified beyond the
  abstract.
- **ATOMIC's** algorithm could not be verified — ACM DL returned 403, no open copy found. Existence,
  authors, venue and pages are confirmed; the mechanism description comes from the project's own
  notes. Get the PDF from the lab before citing the mechanism.
- Page numbers for CMI (SDM 2013) and several others rest on publisher tables of contents rather
  than structured metadata. Semantic Scholar, the arXiv API and OpenAlex were blocked or
  rate-limited during this review.
