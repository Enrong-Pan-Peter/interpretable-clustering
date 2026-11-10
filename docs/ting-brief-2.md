# ATOMIC+ — update for Ting (talking outline)

> **SUPERSEDED (2026-08-05).** This is the outline used in the 2026-08-05 meeting. The outcome of
> that meeting — reframe the paper around interpretability rather than performance — is in
> `docs/ting-meeting-2026-08-05-interpretability-reframe.md`, and the per-shape numbers behind
> sections 4a/4c are now written up properly in
> `docs/experiments/exp-020-per-shape-audit-subclu-flame-splitter.md`. Two claims below need
> updating if this document is reused: flame is a **selection** failure, not an unrecoverable shape
> (it reaches ARI 0.665 once the true pair is known), and every end-to-end ARI quoted here silently
> takes the best of three splitters. See `docs/CORRECTIONS.md` C3 and C7.

Follows `docs/ting-brief.md` (mid-July). That memo said: I can't point to a contribution that is at
once novel, working and defensible. This is what happened when I went looking for one.

Everything below is organised around one question — **does it get us closer to an interpretable
topological clustering method?** Section 1 says what that means concretely, and every block in
section 4 ends with what it changed about our route there.

---

## 1. The goal, stated concretely

- **We are combining two separate ideas.**
  - **Topological clustering is about *what counts as a cluster*:** points linked to each other
    through chains of near neighbours, rather than points close to a common centre. Two concentric
    rings — k-means fails outright because both rings share the same centre, but following
    connectivity round each ring recovers them immediately.
  - **Subspace clustering is about *where you look*:** the clusters exist in only some of the
    features, and distances computed over all features drown them. A thousand gene measurements per
    patient where two disease subtypes are separated by three genes and the other 997 are noise —
    any method using all thousand dimensions sees nothing, while a subspace method finds the three
    genes and the split together.

- **What the method is meant to produce — a labelled tree.** One step is: pick a few columns, compute
  distances using only those columns, split the rows in two. Then recurse: at each of the two groups,
  pick a **new** few columns *from the full column set again*, and split again. Rows partition and get
  fewer down the tree; columns never shrink; the leaves add back up to the whole dataset. A column
  used at the top may be reused deeper or never again — the premise of subspace clustering is that
  different groups are separated by different features.

- **That tree is where "interpretable" lives.** Each split carries the small named panel that
  produced it: *"the first split separated the mice on pCREB and BDNF; inside the left group the
  next split was on pERK and Tau."* A biologist can read that. A single flat clustering in one
  subspace gives one explanation for the whole dataset, which is far weaker — and it is why the
  splits are binary, so each split gets its own small panel rather than one panel explaining k
  groups at once.

- **Two things have to work, and they are separate.** *Selection* — did it name the right columns.
  *Clustering* — did it group the right rows. A method can succeed at one and fail at the other, and
  most of what follows comes from measuring them apart.

- **Everything in this memo is about step one.** One subspace, one split. Not because the tree is
  unimportant, but because every level below inherits step one's error, so measuring a tree built on
  unreliable splits would tell us nothing. Step one is currently the bottleneck.

- **A constraint worth flagging early.** Both terms of our fitness need enough rows to estimate
  neighbourhoods. From 600 rows, three splits leaves ~75 rows a node and neither term means much.
  Depth is capped by sample size, and that caps how interpretable a tree we can honestly build.

---

## 2. Where we were two weeks ago

- **What held:** a precise diagnosis of why the original persistence fitness fails, and small,
  readable feature panels — the interpretability half of the goal was never the problem.

- **What had broken:** the fitness leading the search does not show any advantage for the
  evolutionary algorithm — random search matched or beat it everywhere, so **EA is currently no
  better than the other search algorithms we tried.** The topological objective named the wrong
  columns about half the time (rank-1 selection accuracy — did its single top-scoring panel match
  the planted one). The fix that *did* work looked like existing density-based subspace clustering
  (SUBCLU), so not novel.

- **The stated problem:** novel, working, defensible — I could get any two, never all three.

---

## 3. The current fitness, for reference

Two terms, because they fail on different things: the graph-cut term handles convex blobs well but
not non-convex shapes; the density term alone mishandles unequal-density crescents like jain.
**Neither term uses a centre point** — both score connectivity between neighbours, which is what
makes the objective topological rather than centroid-based.

- **Term 1 — normalized graph cut.** Connect each point to its 10 nearest neighbours, split the
  graph in two, and score the split as `NCut = cut/vol(A) + cut/vol(B)`. `cut` is the number of
  edges crossing between the halves; low means the halves are barely connected, which is what a good
  split looks like. `vol(A)` is the total edge-endpoints inside half A, a measure of its size. The
  division matters: raw `cut` alone is minimised by shaving off a single isolated point, a terrible
  split, whereas dividing by volume punishes lopsidedness — if A is tiny, vol(A) is tiny and the
  ratio explodes. So NCut rewards splits that are both weakly connected and reasonably balanced. We
  use `−NCut` so that bigger is better.

- **Term 2 — density validity.** Split the points by single linkage, then measure
  `(gap between the two groups − biggest gap inside either group) / whichever is largest`. Positive
  means the separation between clusters genuinely exceeds the internal raggedness. Distances use
  mutual reachability — each point's distance is inflated to at least the distance to its 5th
  neighbour — which stops one isolated point in a sparse region from bridging two clusters. The
  division makes it scale-free, roughly −1 to 1.

The two are z-scored against the pool of candidate subspaces of the same size and summed. **That
standardisation is also a limitation** — it makes panels of the same size comparable and panels of
different sizes not, which comes back in 4d.

---

## 4. What we tried since the last memo

### 4a. Measured the "isn't this just SUBCLU?" objection instead of assuming it

- **Why, and how it serves the goal.** If an existing method already selects the subspace, the
  selection half of our goal is solved and we have nothing to add. That was the strongest
  pessimistic claim in the last memo, and nobody had ever run it. No SUBCLU exists on PyPI, so I
  implemented it.
- **Result.** SUBCLU, tuning its own density radius, *returns* a candidate list containing the true
  pair **84–87%** of the time — so finding it is close to solved. But it has no way to rank its own
  output, and when forced to name one it is right only **22%** (its self-tuned rule) or **30%** (the
  best add-on rule we could give it) on the repaired benchmark, against **82%** for us. That is
  rank-1 selection accuracy: did the single top-scoring panel match the planted one, averaged over
  6 shapes × 20 seeds × p = 12/20/40.
- **Even with oracle help it trails us.** If we let SUBCLU pick the best entry from its own returned
  list using the labels, it reaches 71% — still below our 82%. This is a diagnostic upper bound, not
  a competitor; it is here to show the gap is in the ranking step and not in the candidate list.
- **What it means for the goal.** The gap in the field is not *finding* candidate subspaces, it is
  *choosing among them* — and choosing is precisely what a tree needs at every node, since each node
  must commit to one panel before it can split. So the honest claim is narrow and defensible: **the
  contribution is the ranking signal, not the ability to find the subspace.**
- **A methods lesson worth sharing.** My first version made us look twice as good as we are, because
  I had picked a poor rule for making SUBCLU commit to one answer. SUBCLU has no native ranking, so
  whatever rule you bolt on is *your* choice — you can build a strawman out of entirely reasonable
  decisions. Fixed by committing in advance to whichever rule is best *for the baseline*.

### 4b. Found that our own test data was giving away its answer

- **Why, and how it serves the goal.** Our goal is features that only mean something *together*. So:
  can you get the right answer from one feature on its own? If yes, the dataset is not testing the
  thing we claim, and every selection number measured on it is meaningless for our purposes.
- **Result.** On jain and spiral the one-column shortcut recovered the planted pair **100% of the
  time**; gauss2 65–80%, circles 45–70%. Moons was the only shape close to clean, and even there it
  succeeded 25% of the time against a chance rate of 1.5%. **Four of six shapes were handing out
  free marks**, so every ARI and selection-accuracy number averaged across the suite was flattering
  us.
- **Cause.** Planting a picture into two columns makes those columns lumpy as a side effect, while
  the junk columns were evenly spread — visible one column at a time. Fixed by making the junk
  columns lumpy too. After the fix the one-column shortcut works 0% of the time on the three shapes
  re-run (moons, spiral, jain, at p=12); gauss2, circles and flame have not been re-run, so "fixed
  everywhere" is not yet earned.
- **One residual leak, worth saying out loud.** A second shortcut — "pick the pair where the most
  points fall into clumps" — still recovers the planted pair **75% of the time on jain** after the
  repair (0% on moons and spiral). Jain's two crescents differ in density by construction, so mass
  concentration really is informative there. The repaired benchmark is honest on two of the three
  shapes tested, not three.
- **What it means for the goal.** We now have a benchmark that mostly requires joint structure,
  which is the only kind that can tell us whether we are moving toward the goal. It also became a
  reusable gate: run it on any dataset before scoring anything on it (used again in 4f).

### 4c. Re-ran the SUBCLU comparison on the repaired data

- **Why, and how it serves the goal.** Any claim about our ranking signal — the piece 4a identified
  as the contribution — was measured on data that leaked, so it had to be remeasured.
- **Result — this one went our way.** A simple rule ("pick the pair where the most points fall into
  clumps") had been beating us **0.844 to 0.769** on rank-1 selection accuracy on the old data. On
  the repaired data it drops to **0.297** while ours *rises* to **0.822**. That rule was living
  almost entirely off the flaw we removed.
- **Per shape, because the average hides where.** On the repaired benchmark the clump rule survives
  only on jain (0.783) and on gauss2 (1.000 — the convex control, which nothing struggles with). It
  is **exactly 0.000** on circles, moons and spiral. Ours is 1.000 / 0.983 / 0.967 / 0.983 on
  circles / jain / moons / spiral.
- **The number I would not want Ting to hear from someone else first: flame is 0.000.** On flame,
  *every* method scores zero rank-1 accuracy on both benchmarks — ours, both SUBCLU rules, and the
  oracle variant. So our headline 0.822 is an average that includes one shape where the entire field
  fails. Excluding flame it is 0.987; over the four non-convex shapes excluding flame, 0.983. Flame
  is a known scope boundary for this whole family of methods rather than a bug of ours, but the
  honest headline is "0.822 over six shapes, one of which nobody can do."
- **What it means for the goal.** The ranking claim — the piece 4a identified as the actual
  contribution — survives the only test we have that mostly requires joint structure, and it is the
  step every node of the tree depends on. This is the one result in the memo that strengthened
  rather than qualified the story.

### 4d. Ryan's test: does the fitness give a search anything to climb?

- **Why, and how it serves the goal.** A tree needs to choose a panel at *every node*, on data where
  nobody tells you the panel size. Everything we do today is *enumeration* — score all pairs, take
  the best — which only works because we told the method the answer is a pair. Without a working
  search, the recursive tree in section 1 cannot be built at all. So this test is a direct check on
  whether the goal is reachable with the current fitness.
- **Result.** Measured as Cohen's d on the raw density term, comparing panels *of the same size*
  (the two terms are not comparable across sizes — see below):
  - a panel holding one of the two true features beats a panel of pure junk by only **d = 0.41** at
    panel size 2, falling to 0.17 at size 5 — against a bar of d = 0.5 written into the test script
    before the run;
  - a panel holding *both* true features beats one holding one by **d = 3.13** at size 2, but by
    only **0.48** once a single junk column is added.
- **The graph-cut term is worse than shallow — it points the wrong way.** Its d(one-true vs junk) is
  **−0.06 at panel size 4 and −0.20 at size 5**: a panel containing one true feature scores *lower*
  than pure junk. Per shape it is starker — moons runs 0.06 / −0.19 / −0.31 / −0.38 as the panel
  grows. So a search driven by the deployed hybrid is actively pushed away from the answer on those
  shapes. Only the density term has a slope at all, and it fails the bar.
- **The single sentence.** *The fitness's ability to tell a better panel from a worse one shrinks as
  the panel grows, and one of its two terms inverts.* Ryan asked whether there was a slope to climb;
  on the density term there is one and it is too shallow to follow, and on the graph-cut term it
  runs downhill.
- **And a third gap on top of that.** Because the two terms are z-scored within a pool of same-size
  candidates (section 3), fitness values at different panel sizes are not comparable at all. Even a
  perfect within-size signal would not tell a search *when to stop adding features*. The 2025–26
  literature search found nothing on this since 2008.
- **Mechanism.** Distances are computed over every column in the panel, so each junk column adds
  noise to every distance.
- **What it means for the goal.** This is the blocker on the route to the tree. Enumerating pairs is
  not a method — it is a demonstration that a signal exists when you already know the answer. A tree
  node must choose a panel of unknown size from scratch, and a search doing that walks through
  panels carrying junk, where the signal has already faded. Until the fitness tolerates irrelevant
  columns *and* becomes comparable across panel sizes, there is no route from "we can rank exact
  pairs" to "we can build the tree."

### 4e. Two attempts to remove that blocker

- **Distance multivariance** — a dependence measure from the statistics literature, chosen because
  it provably penalises a panel that contains an irrelevant feature, which is exactly the tolerance
  problem in 4d. *Result: shape-specific, and only one of its two variants works.* On jain and moons
  its Cohen's d on the "have I arrived" measurement is roughly an order of magnitude above the next
  best term (jain 67, moons 39 at panel size 2; 19× and 9× the runner-up), and the **total** variant
  survives added junk columns better than anything else we have (jain 67 → 33, moons 39 → 20 at size
  3) — the plain variant collapses to −0.2 and −0.6 at size 3. On circles and spiral both variants
  fail completely, detecting nothing even with the exact right pair (−0.1 and −0.3). And neither
  variant has any slope at all: d(one-true vs junk) is between −0.06 and −0.10 on every shape, so it
  can never guide a search, only confirm an arrival. A shape-specific detector, not a general fix —
  and 4f found it ranks HAR's good pairs worse than random.

- **Density-connectivity distance** (a "minimax path" distance from a KDD 2023 paper). *What it is:*
  instead of measuring A to B in a straight line, walk from A to B hopping point to nearby point;
  every route has one longest hop; take the route that makes that longest hop smallest, and that hop
  is the distance. So two points at opposite ends of a long curved chain come out **close** (every
  hop is short) while two points across an empty gap come out **far** (some hop must jump it).
  - *Why it is the natural thing to try:* that is our own definition of a cluster — linked through
    chains of near neighbours — promoted from something we score to the distance itself. It is not a
    bolt-on; it makes the geometry topological from the ground up.
  - *Why we hoped it fixes 4d:* junk columns inflate all raw distances. This distance only cares
    about the single worst hop on the best route, so if everything inflates by about the same
    amount, the best route and the ranking of what-is-close-to-what should not move. Straight-line
    distance has no such protection.
  - *Result — the most encouraging term we have, and still not enough.* On the "have I arrived"
    measurement it does **not** collapse when a junk column is added, unlike the density term
    (3.13 → 0.48): it runs 0.80–1.33 at panel size 2 and 0.91–1.57 at size 3. That resistance is
    exactly the property 4d says we need — though it does fade further out (circles 0.07 by size 4;
    at size 5, circles 0.03, spiral 0.31, moons 0.51, only jain still at 0.85). And on the "is there
    a slope to climb" measurement it clears the 0.5 bar on **3 of the 4 non-convex shapes only when
    the panel is exactly 2 features** (jain 1.04, spiral 0.85, moons 0.55; circles 0.34 fails), and
    at size 3 or more **only jain still clears it**.
- **What it means for the goal.** Half the blocker is removable and we know which half. A distance
  built on our own notion of connectivity survives extra columns; what it still lacks is a slope
  pointing toward the answer from far away. That is a sharper open problem than we had two weeks
  ago, and it is stated in terms of the goal rather than in terms of a benchmark score.

### 4f. Moved off our own generator onto real data

- **Why, and how it serves the goal.** We caught the generator leaking once already (4b).
  Continuing to tune against it risks fitting a second set of quirks nobody has spotted — and the
  goal is a method that works on somebody's real table, not on our shapes.
- **What we used.** Mice Protein Expression (77 proteins, 1080 mice; question = which of two
  behaviour protocols the mouse went through) and UCI Human Activity Recognition (561 sensor
  features). Both went through 4b's one-column gate first. HAR's obvious question (moving vs still)
  had to be thrown out: a single column reaches **ARI 1.00** on it and 205 of 561 columns reach
  ARI 0.5, so about 60% of all pairs contain a column that already answers the question and the
  dataset cannot separate a working selection method from a coin flip. That is physics, not a data
  flaw — a motion sensor telling motion from stillness with one number is what you would expect.
  Switched to sitting vs standing, where both
  postures are motionless and the best single column reaches only **ARI 0.41**. Mice is not perfectly clean
  either — one of the 77 proteins reaches **ARI 0.54** alone — but the best *pair* reaches
  **ARI 1.00**, so pairs add a great deal over the best single column, which is what we need.
  Both are scored on a stratified 600-row subsample — our terms need an n×n distance matrix per
  candidate, and HAR at 7,352 rows needs 432 MB of it per candidate.
- **Result — the clearest finding of the two weeks.**
  - On **mice** (all 2,926 protein pairs enumerated), 65 pairs reach **ARI above 0.5** and the best
    pair reaches **ARI 1.00**. Our graph-cut term ranks those 65 at median 381st of 2,926, and its
    single highest-scoring pair does achieve ARI 1.00. Its top ten are a mix, not a clean sweep:
    four of them are at ARI ≥ 0.98 and the other six are near zero. Against a base rate of 2.2%,
    getting 4 in 10 is a large enrichment, and a random ranking would land the good pairs at median
    ~1,463 (p < 0.0001 against a shuffled null).
  - On **HAR sitting-vs-standing** (6,000 pairs, a 3.8% sample of the 157,080 possible), only 22
    exceed **ARI 0.5** and the best pair only reaches **ARI 0.63**. Our graph-cut term ranks the good
    ones at median 2,684th of 6,000 — indistinguishable from random (p = 0.30 against the same
    shuffled null).
  - **So: selection works when good subspaces are reasonably common and strong, and fails when they
    are rare and weak.**
  - *Honest caveat on HAR:* when the best available answer is only ARI 0.63, telling a good pair
    from a mediocre one is intrinsically harder, so "our term failed" and "there was nothing clean
    to find" cannot be fully separated on this dataset.
- **What it means for the goal.** This is the first statement we have about *which real data the
  method suits*, and it is directly a statement about whether the tree is buildable: a node whose
  rows contain no strong 2-feature structure will pick a panel at random, and everything below it is
  noise. It also gives a reader something they can check on their own data before trying any of
  this, which a bare performance number does not.

### 4g. Checked the 2025–2026 literature

- **Why, and how it serves the goal.** To know which of the gaps blocking us are genuinely open —
  i.e. which parts of the goal are ours to solve and which are already solved by someone else.
- **Result — gaps.** ~~Nothing since 2008 on making subspace scores comparable across different panel
  sizes~~ **RETRACTED, see `docs/CORRECTIONS.md` C9** — the problem has a formal name
  (dimensionality unbiasedness), a formal definition and several published fixes; Vinh et al., DMKD
  30:1520–1555 (2016) proves Z-score normalisation achieves it. What survives is narrower: nobody has
  established it for normalized graph cut or DBCV-style indices specifically. The other two hold: no
  successor to the 2009 subspace-clustering benchmark (the problem in 4b is the field's problem too),
  and nobody has applied higher-order dependence measures to unsupervised feature selection (4e's
  first attempt).
- **Result — new work we must cite or beat.** DISCO (ICLR 2026) supersedes the validity index our
  density term is based on. SpEx (NeurIPS 2025) and GroupFS (AAAI 2026) are close neighbours — on
  interpretable trees and on feature "panels" respectively, which is to say on both halves of our
  goal.
- **One uncomfortable finding.** The two-stage design I was about to propose — cheap monotone filter
  to generate candidates, then a better score to rank them — is the founding architecture of this
  field (CLIQUE 1998) and has been reinvented at least five times, once by the SUBCLU authors
  themselves a year *before* SUBCLU.

---

## 5. Where that leaves the paper

- **What is now defensible.**
  - **A precise statement of when subspace selection works and when it doesn't**, measured on both
    synthetic and real data, in terms a reader can check against their own dataset. This is the
    piece that has actually grown, and it speaks directly to whether the tree in section 1 is
    buildable on given data.
  - The narrow SUBCLU claim: it finds the subspace (true pair in its candidate list 84–87% of the
    time) but cannot rank it (22–30% rank-1 selection accuracy on the repaired benchmark, vs our
    82%); ranking is what every node of the tree needs. Stated with the flame caveat: on one of the
    six shapes every method including ours scores zero, so this is a claim about five shapes.
  - Two negatives worth publishing: **the fitness leading the search does not show any advantage for
    the evolutionary algorithm, so EA is currently no better than the other search algorithms**; and
    the fitness's ability to distinguish good panels from bad shrinks as the panel grows, which is
    why enumeration works and search does not.

- **What is not defensible.** Beating existing methods on clustering quality (ARI). Any novelty in
  the clustering primitives — they are all established. And **fair evaluation is not a contribution**
  — comparing methods in a subspace the method did not choose for itself is something every paper is
  supposed to do. We do it; we don't claim credit for it.

- **A caution I would state out loud.** Our synthetic ranking of candidate terms did **not** survive
  contact with real data. The term that looked best on our shapes (density-connectivity distance)
  was not the best on mice: plain graph-cut placed the high-ARI pairs better (median 381 vs 793) and
  resisted added junk columns better (2.12 vs 1.07), though the two are effectively tied on top-10
  lift (+0.296 vs +0.304, if anything dc-dist is marginally ahead). Any ordering of terms
  established only on our generator should be treated as provisional.

- **What the "when does it work" claim currently rests on.** Two datasets, one question each. That
  is thin, and mice/Treatment, HAR/upstairs-vs-downstairs and Madelon are the obvious next runs.

---

## 6. What I would like your view on

- **Is "when does this work" a paper?** The strongest thing we now have is a characterisation with
  real-data evidence, not a method that wins. Is that a GECCO paper, a benchmark paper elsewhere, or
  a section of something larger?
- **GECCO fit.** If the evolutionary search shows no advantage under this fitness, is there enough
  left for that venue, or does this belong somewhere like ECML PKDD or a journal?
- **Real data.** Mice and HAR have labels but no known "correct" feature panel, so we can only test
  the clustering half of the claim, never selection against a true answer. Is there a biomedical
  dataset where the literature already reports a panel? Bryant suggested stability across reruns as
  an additional angle worth pursuing.
- **Scope.** Is it acceptable to define the contribution as "we can rank subspaces, we cannot search
  them", and leave the search problem — and therefore the full recursive tree — explicitly open?

---

## Appendix — provenance of every number above

Not for the meeting; for me, before any of this goes into a draft.

- **4a, 4c** — `results/method_baselines.csv` (old junk) and `results/method_baselines_structured.csv`
  (repaired junk). Full factorial: 6 shapes × 20 seeds × p = 12/20/40 = 360 runs per method.
- **4b** — `results/benchmark_validation.csv`. Covers moons, spiral and jain at p=12 only. gauss2
  and circles were measured *before* the repair but never re-run after it, so "the one-column
  shortcut now works 0% of the time" is verified on three shapes, not six. flame was never run.
- **4d, 4e** — `results/signal_landscape.csv`. 5 shapes (no flame), p = 20/40, 10 seeds. The
  pre-registration asks for 20 seeds, so this is half the intended power.
- **4f** — `results/real_data_mice_behavior.csv` (= `real_data_postfix.csv`, identical file) and
  `results/real_data_har_sitstand.csv`. Both scored on a stratified 600-row subsample.
- **Two gaps against our own pre-registration**, both worth closing before a draft: flame is missing
  from 4b/4d/4e (the pre-registration says it stays in every table as a known scope boundary, and
  4c shows exactly why — it is where everything scores zero), and signal_landscape ran 10 seeds
  where 20 were specified.
