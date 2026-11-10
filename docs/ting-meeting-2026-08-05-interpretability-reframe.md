# Meeting with Ting, 2026-08-05 — reframe the paper around interpretability

Supersedes the framing in `docs/ting-brief.md` and `docs/ting-brief-2.md`. Those remain as a record
of what was believed at the time; several of their claims are now corrected in
`docs/CORRECTIONS.md`.

---

## 1. The decision

**The paper is no longer about performance. It is about interpretability.**

The novelty is *the recursive tree with a named feature panel at every split, plus an interactive
tool for exploring it* — not beating the state of the art. Ting's position, in her words as relayed:
it is very hard to invent a new methodology that outperforms established distance-based and
density-based clustering, and we do not need to. If we beat a baseline in some setting, report it.
If we do not, that comparison simply is not the paper's argument.

Three consequences she stated explicitly:

- **Using established components is fine.** The density validity index and the normalized graph cut
  do not need to be novel. The tree and the interface carry the novelty.
- **Not matching established labels is acceptable.** Our clusters often disagree with the labels
  shipped with a dataset. That is not automatically a failure.
- **Report where the method works; put the rest in limitations.** Her framing: this is not dataset
  hacking, it is reporting our advantages. Enrong's position, stated in the same conversation: not
  fabricating or altering data, and not dataset hacking.

A dissent was recorded and is noted here for completeness rather than as an open dispute, since this
is the supervisor's call: omitting a *dataset you ran* or a *baseline that beat you* after seeing
the result is the one move a reviewer probes for. A search of venue policies (IJCAI 2025's
reproducibility policy, for one) did not turn up a rule requiring authors to report everything they
ran, so this is a judgement call about risk, not a rule being broken. In our specific case it is
also largely moot — see §3.

---

## 2. The interactive tool

Ting's idea, and it is now a first-class deliverable rather than a nice-to-have.

- User supplies a table. The algorithm runs and returns the recursive tree.
- Possibly **several trees**, from different splits and different feature panels at each split.
- The user reads the tree as the explanation: which few named columns separated which rows.
- Open source, on GitHub.

This has a consequence nobody has written down yet, and it is the most useful thing to come out of
the meeting. **Enumerating all pairs is defensible at depth 1 and only breaks when a search has to
guess panel size at deeper nodes.** If the user drives the deeper exploration through the interface,
the search problem stops being a blocker and becomes a design choice. That is a real answer to the
thing that has blocked this project for two weeks (exp-018: the fitness's ability to distinguish good
panels from bad shrinks as the panel grows, so no search can follow it).

---

## 3. Correction to carry into the next conversation

Ting's current understanding is *"works on circles, not on the harder moons; convex yes, non-convex
mostly no."* **The data says the opposite** and she should be told. Full detail in
`docs/CORRECTIONS.md` C1; the short version, rank-1 selection accuracy on the repaired benchmark,
20 seeds, p = 12/20/40:

| | gauss2 | circles | moons | jain | spiral | flame |
|---|---|---|---|---|---|---|
| ours | 1.000 | 1.000 | **0.967** | 0.983 | 0.983 | 0.000 |

Selection works on all four non-convex shapes and fails only on flame. On the **convex** control the
graph-cut term alone has rank-1 accuracy 0.000, and the dataset is solved at ARI 1.000 by plain
k-means with no selection at all — subspace selection buys literally nothing there.

Three further points that change what "report where we work" costs us:

- **We do not currently have a baseline that beat us on selection.** Ours 0.822 against SUBCLU's
  best realistic rule at 0.297 on the repaired benchmark. So the awkward case has not arisen.
- **flame is not a free limitation.** It is recoverable at ARI 0.665 once the right pair is known;
  our failure there is a selection failure, and it is the one shape where doing no selection at all
  beats our pipeline. See exp-020 §2. Reporting it costs little because *every* method fails it,
  and omitting it invites "where is flame?" in review.
- **The strongest table for an interpretability paper is the value-of-selection table**, not a
  head-to-head: on circles and spiral, methods that use every column are at chance (ARI 0.000 and
  0.001) while ours reach 1.000 and 0.553. See exp-020 §4.

---

## 4. Ting's three open questions, and where we stand on them

### 4a. "Would it be easier to frame this as actual unsupervised learning?"

Probably yes for honesty, but it raises the evidence bar, because you then have to say what makes a
split meaningful without labels — which is her next question. The workable shape is a hybrid: use
labelled data to validate the machinery (normal in clustering papers) and present unlabelled use as
the application.

### 4b. "What would count as evidence that a disagreement is meaningful?"

Four kinds, weakest to strongest:

1. **It reappears.** The same panel and split recur under resampling. Noise does not. This is
   Bryant's stability suggestion and it is cheap.
2. **It predicts something neither method used.** The strongest, and *runnable on data we already
   have*. Mice Protein Expression carries four labels — Genotype, Treatment, Behavior, and an 8-way
   class. Our best pair reaches **ARI 1.00 against Behavior** while **no pair exceeds 0.249 against
   Genotype**. So a split that "disagrees with the labels" can be perfectly explaining a different
   real factor in the same data. Scoring our top-ranked pairs against all four labels turns that into
   a demonstration, using labels only to check and never to select.
3. **It survives a fair internal check.** With the caveat we already identified: an internal score
   computed in the subspace the method chose flatters it, so this has to be against a null with the
   same features and shuffled rows.
4. **A domain expert can read it.** Which is what the tool is for.

### 4c. "What would a minimum publishable result look like?"

Proposed answer, to be agreed with Ting:

1. The recursive tree, defined and implemented, with named panels at each node.
2. Evidence that selection is *necessary*: full-space clustering at chance where we succeed
   (exp-020 §4).
3. One clean baseline win on a well-defined task: SUBCLU finds but cannot rank (exp-020 §1).
4. A real-data case study where the tree tells a domain story, with 4b's multi-label test as the
   evidence that a disagreement can be meaningful.
5. The open-source tool.
6. Limitations: flame, enumeration-only search, behaviour on unlabelled data.

---

## 5. Her suggestion: use the EA to choose the metric

The idea: rather than searching feature panels, let the evolutionary algorithm decide *which*
criterion to use at each split — density, graph cut, hybrid, density-connectivity distance — and
which direction to prune. She flagged it as a suggestion, fine to drop.

**Honest read.** Two problems and one opportunity.

- The configuration space is roughly a dozen combinations (four scoring terms × three splitters).
  That is enumerable; an EA over twelve options will not survive review.
- Choosing a criterion without labels is the same selection problem one level up. Making the chooser
  an EA does not manufacture a signal that is not there. Our own 20-seed runs already showed NSLC,
  MAP-Elites and CVT-MAP-Elites all losing to random search, with the gap growing in p
  (`why-ea-diversity-unsupported` memory; exp-012, exp-013, exp-017).
- **But** the reframe rescues a different angle we already have evidence for. If the deliverable is
  *several* trees rather than one best tree, the multi-objective front from **exp-015** — quality,
  parsimony and novelty in a single run — becomes the natural way to generate the portfolio. That
  result was filed as a weak "convenience claim" because it was judged against performance. Under an
  interpretability paper it is the right shape. **This is the one place the reframe upgrades an
  existing negative result into a positive one.**

Also worth noting for the venue question: exp-020 §3 shows the splitter choice swings ARI by up to
0.84 on jain with identical selection, and no splitter wins everywhere. Under a performance framing
that is an unfixed hole; under the tool framing it is a feature — show the user the tree each
splitter produces.

---

## 6. Next data: public cancer expression data

Ting's suggestion, and it closes the single biggest gap in our evaluation. Every dataset so far —
our shapes, mice, HAR — has labels but **no published feature panel**, so we have only ever been able
to test whether the clustering was right, never whether the *selection* was right on real data.
Breast cancer has PAM50, a published gene panel for the intrinsic subtypes.

Full plan, download routes and design constraints: `docs/data-plan-cancer-expression.md`.

---

## 7. Actions

| | action | state |
|---|---|---|
| 1 | Correct the mis-documented findings in the repo | done — `docs/CORRECTIONS.md`, exp-020 |
| 2 | Tell Ting the convex/non-convex reading is backwards | pending, next conversation |
| 3 | Acquire cancer expression data | pending — see the data plan |
| 4 | Mice multi-label run (evidence for 4b) | pending, cheap |
| 5 | Re-run the EA comparison on the repaired benchmark before quoting exp-017's ceiling | pending |
| 6 | Agree the minimum publishable result in §4c with Ting | pending |
| 7 | Design the tool | not started |
