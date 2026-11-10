# Interpretation of panels from the 15 September pilot

## Material Passport

- Origin: independent panel interpretation within the ATOMIC research review
- Origin Date: 2026-09-15
- Mode: analysis of saved experimental outputs
- Verification Status: ANALYZED; no clustering reruns or new performance experiment
- Version Label: pilot_panel_interpretation_v1
- Inputs: `results/research_diagnostics/search_*/summary.json`, `data_protocol.json`, candidate JSONL files, manifests, and saved assignment matrices
- New calculations: descriptive means, set overlaps/Jaccards, selected-panel training correlations and candidate ranks from existing files
- Scope: sparse-k-means and smooth-graph proposal arms; METABRIC, Levine and the five-feature mean-shift benchmark

## What the pilot establishes

The results support a narrower, useful conclusion: **data-informed proposal methods can discover panels containing five informative variables without exhaustive subset enumeration.** In this pilot, both proposal methods contain the exact planted support in their candidate pools in every mean-shift seed. The remaining problems include choosing a compact panel, transferring its partition reliably, and handling other geometries.

The strongest real-data lead is the sparse-k-means proposal arm on METABRIC: it repeatedly returns small, overlapping sets of mostly PAM50 genes and moderate held-out subtype agreement. The smooth-graph arm is much less consistent there. Levine is a successful recovery check for both, but largely reduces to finding CD8 in an already restricted CD4/CD8 T-cell contrast. It is not the hard larger-panel case needed to establish the eventual method's scope.

These names refer to **proposal arms in a common pipeline**. Their feature prefixes are reclustered with the common spectral splitter, selected by the discovery objective, and transferred by a distance-weighted 7-nearest-neighbor rule. They are not end-to-end evaluations of native sparse k-means or native weighted spectral clustering. Validation rows choose feature deletions; they do not choose among all proposed panels.

## Experimental scope and meaning of the measurements

Each run uses 480 observations, divided into 240 discovery, 120 validation and 120 test rows. The recorded real-data cases are METABRIC **LumA versus LumB**, with 250 preselected genes, and Levine **CD4T versus CD8T**, with 32 markers. The population filters use existing labels; subsequent sampling, feature search and score selection do not use those labels.

- **Transfer ARI:** agreement between external labels and the frozen discovery partition assigned to test observations by the kNN rule.
- **Reclustered ARI:** agreement with external labels when the test observations are independently split in the same selected panel.
- **Replication fidelity:** ARI between these two test partitions. It measures whether the discovery partition recurs under this splitter, not whether a biological population exists.
- **Compression fidelity:** ARI between the full-panel and reduced-panel kNN assignments on test rows. This is not the percentage of observations assigned identically.

All runs explicitly report `candidate_only_no_split_acceptance_test`. Numerical validity and high ARI against existing labels should not be reported as a formal test that clusters exist.

The METABRIC matrix is PAM50 enriched and was previously variance filtered using all patients before the new splits. It is a development dataset, not a clean independent discovery cohort. The three sampled patient sets share 194–196 of their 480 observations pairwise; their test sets share 8–13 observations. The runs therefore provide sensitivity checks, not three independent cohorts. Levine's sampled cell sets share only 4–5 cells pairwise and its test sets are disjoint, but all are drawn from the existing specimen pool. Cell holdout is not donor replication.

## METABRIC: a repeatable candidate family, incomplete verification

Numbers below are the saved test results, rounded to three decimals. The arrow reports the accepted validation-based reduction; an unchanged panel is marked “same.”

| Proposal arm / seed | Original panel → reduced panel | Transfer ARI, original → reduced | Independent test reclustering ARI, original → reduced | Test compression fidelity |
|---|---|---:|---:|---:|
| Sparse k-means / 0 | ANLN, CEP55, EXO1, PTTG1, UBE2C → CEP55, EXO1, PTTG1, UBE2C | .316 → .297 | .118 → .130 | .839 |
| Sparse k-means / 1 | CEP55, EXO1, MELK, PTTG1, UBE2C → same | .335 → .335 | .296 → .296 | 1.000 |
| Sparse k-means / 2 | ANLN, CEP55, MELK, PTTG1, RRM2, TYMS, UBE2T, PCLAF → ANLN, CEP55, MELK, RRM2, UBE2T | .418 → .416 | .177 → .162 | .808 |
| Smooth graph / 0 | EXO1, FOXC1, MELK, PTTG1, UBE2C, UBE2T, PCLAF → EXO1, FOXC1, MELK, PTTG1, PCLAF | .316 → .279 | .245 → .213 | .808 |
| Smooth graph / 1 | ESR1, BCORL1, GPNMB, HEATR5B, MOGS, RASGRF2, RNASE6, WDR86 → same | −.008 → −.008 | .014 → .014 | 1.000 |
| Smooth graph / 2 | BTNL8, HS3ST3A1, NAV2, SCGB2A2, UBE2Q1 → same | .047 → .047 | .054 → .054 | 1.000 |

### What is stable

Sparse-k-means original panels contain **CEP55 and PTTG1 in all three seeds**. ANLN, EXO1, MELK and UBE2C occur in two. Original-panel Jaccards are .667, .300 and .300 for seed pairs (0,1), (0,2) and (1,2); their mean is .422. Reduced-panel Jaccards are .800, .125 and .250, mean .392. The exact gene list is therefore only partly stable; reduction does not clearly increase its consistency. CEP55 is the sole gene in every reduced panel.

The selected smooth-graph panels have **zero gene overlap between every pair of seeds**, both before and after reduction. Their average test transfer ARI is .118, compared with .356 for the sparse-k-means arm. The latter's three transfer ARIs remain positive and moderately sized, whereas the graph result is concentrated in seed 0. With only three runs and unequal proposal costs, this is a development signal, not a statistical superiority claim.

The original sparse-k-means panels contain 5/5, 5/5 and 7/8 PAM50 genes. All reduced sparse-k-means panels contain only PAM50 genes. Smooth-graph original panels contain 6/7, 1/8 and 0/5 PAM50 genes. These are overlaps with a contextual reference, not precision/recall against a complete ground-truth list. Only 50 of the 250 available genes belong to that reference, but no enrichment p-value is justified by treating the adaptively selected genes as independent random draws.

### What is biologically plausible

CEP55, PTTG1, UBE2C, RRM2 and TYMS appear in the published PAM50 proliferation index. This gives a specific existing biological connection for part of the recurring sparse-k-means panels. It does not require assigning a function to every selected gene. The source's index and its intended role are documented in [Nielsen et al. (2010), supplementary Table M1](https://unclineberger.org/peroulab/wp-content/uploads/sites/1008/2019/06/Nov-1-TAM-series-PAM50-Nielsen-et-al-CCR-2010.pdf).

The selected sparse-k-means discovery matrices also show strong positive within-panel association: mean pairwise Pearson correlations are .809, .824 and .670 for seeds 0–2; the corresponding ranges are .736–.889, .774–.882 and .489–.823. These are new descriptive calculations from the saved training matrices. They are consistent with finding correlated measurements of a shared expression pattern. Correlation itself does not verify proliferation, subtype discrimination or a density valley.

It would be premature to call these minimal biomarker panels, a biological discovery, or independent verification of PAM50. The feature universe and subtype annotations are already closely connected to the PAM50 context. Demonstrating recovery is useful, but a new scientific claim needs evidence beyond recovering part of this existing signature.

### What is not yet reliable

Sparse-k-means replication fidelities are only .361, .354 and .462, despite transfer ARIs of .316–.418. The test reclustering ARIs are lower than transfer ARI in all three seeds. The result therefore supports a transferred predictive partition more strongly than it supports independently reproduced spectral clusters.

The full 50-gene contextual reference achieves test transfer ARIs .418, .243 and .396, mean .352. Sparse-k-means averages .356 using 5–8 genes. Similar three-seed means suggest a compactness opportunity; they do **not** establish equivalence, noninferiority, or consistent improvement. The reference itself is being passed through the same spectral/kNN pipeline, not the published PAM50 classifier, and is not a performance ceiling.

Accepted reductions in sparse-k-means seeds 0 and 2, and graph seed 0, fall below the validation target ARI .95 on the untouched test rows: their test fidelities are .839, .808 and .808. Validation fidelity was .967 or better at each accepted final reduction. This is direct evidence that the current small-sample reduction decision does not reliably preserve its stated tolerance out of sample. Similar external ARI before and after reduction does not repair that fidelity claim; they are different measurements.

The graph failure has different causes by seed. In seed 1 it visited a five-gene panel — BIRC5, CCNB1, MELK, UBE2T, KIF11 — with diagnostic training ARI .561, but ranked it 13th and selected a panel with training ARI −.003. This is a clear **training candidate-ranking failure relative to the supplied subtype labels**. It does not show how that unselected panel would perform on test data. In seed 2 the graph arm's best visited training ARI was only .095, indicating poor candidate coverage as well. One diagnosis cannot explain every seed.

## Levine: strong local recovery, largely a singleton task

Both proposal arms select exactly the same panel and make the same reduction in each seed.

| Seed | Selected panel → reduced panel | Test transfer ARI | Independent test reclustering ARI | Replication fidelity | Compression fidelity |
|---|---|---:|---:|---:|---:|
| 0 | CD4, CD8, CXCR4, CD47 → CD8, CXCR4 | .967 | .967 | 1.000 | 1.000 |
| 1 | CD8 → same | .967 | .934 | .902 | 1.000 |
| 2 | CD8 → same | .934 | 1.000 | .934 | 1.000 |

CD8 is present in every original and reduced panel. Original set Jaccards are .25, .25 and 1.00; reduction raises them to .50, .50 and 1.00. The variable panel sizes coexist with a stable core feature and strong partition recovery. Requiring exact recovery of the contextual pair CD4/CD8 would incorrectly penalize a useful singleton in this restricted contrast.

The seed-0 reduction drops CD47 and then CD4; dropping CXCR4 afterward would give validation fidelity .902 and is rejected. This supports CXCR4's role in approximating that seed's particular frozen rule at the specified tolerance. It does not establish that CXCR4 is biologically necessary for distinguishing these populations; the other two seeds succeed with CD8 alone.

The contextual CD4/CD8 reference also shows a splitter/assignment issue: in seed 0 its test transfer ARI is .559 while independent test reclustering ARI is .967. A biologically sensible reference panel is therefore not sufficient to guarantee a good trained split. Panel, splitter and assignment quality need separate diagnostics.

The source benchmark uses manually gated populations, so success here is recovery of an existing annotation within a prefiltered pair of populations. The benchmark preparation documentation describes the manually gated structure and source specimens: [Levine-32 benchmark repository](https://github.com/lmweber/benchmark-data-Levine-32-dim). These runs do not establish automatic discovery of those populations inside the full unlabeled cell pool, donor transfer, or a new marker relationship.

Also, the random arm has the same mean test transfer ARI, .956, in this pilot. Levine confirms that several methods can recover this local contrast; it does not distinguish the proposed search mechanisms by that endpoint.

## Mean-shift: discovery beyond three succeeds; minimality does not

Every seed independently generates five shifted coordinates among 50. Their numeric feature positions are permuted anew, so Jaccards of names such as `f0008` across seeds would be meaningless support-stability measurements. The correct comparisons are with each seed's own planted set.

| Arm / seed | Selected size | Planted features recovered | Noise features retained | Exact five-feature support's rank in the scored candidate pool | Test transfer ARI |
|---|---:|---:|---:|---:|---:|
| Sparse k-means / 0 | 6 | 5/5 | 1 | 11 | .692 |
| Sparse k-means / 1 | 8 | 5/5 | 3 | 10 | .778 |
| Sparse k-means / 2 | 8 | 5/5 | 3 | 7 | .534 |
| Smooth graph / 0 | 8 | 5/5 | 3 | 4 | .749 |
| Smooth graph / 1 | 7 | 5/5 | 2 | 4 | .749 |
| Smooth graph / 2 | 8 | 5/5 | 3 | 5 | .637 |

The exact planted support was **proposed and scored in all six runs**. It was not used as a search seed. Both methods therefore solve the candidate-coverage problem in this particular five-feature setting. Selected panels contain all planted variables, but none equals the planted set. None loses any feature during backward reduction.

Mean test transfer ARI is .668 for sparse-k-means proposals and .712 for graph proposals, versus .152 for random, .162 for forward and .268 for evolutionary search. These observations support more informative proposal feedback; the budgets do not establish equal-computation superiority, and three seeds cannot support a general ranking.

The problem is a **distributed mean-shift mixture**, not a pure higher-order interaction. The population mean difference has norm 3, spread equally across five variables. Each individual mean difference is `3/sqrt(5)` and is nonzero; the latent grouping also produces covariance structure. Simultaneous feature methods have available low-order statistical clues. Success cannot be extrapolated to signals whose smaller subsets reveal no information.

The compression failure is also informative. The best one-feature deletion fidelities are .934, .934 and .902 for sparse-k-means, and .934, .902 and .870 for graph, all below .95. Some rejected deletions remove known noise coordinates. This shows that preserving the exact fitted kNN behavior can preserve noise-sensitive details of its boundary.

The threshold is stringent on 120 validation observations: for a roughly balanced binary split, changing two assignments can already reduce ARI to about .934, even though pointwise agreement is about 98.3%. This numerical example explains the scale; it is not a claim that every recorded .934 corresponds to exactly two errors. A fixed ARI threshold should not be described as allowing 5% assignment disagreement.

The present reduction procedure **does not recluster each reduced panel**; it retrains kNN on the same frozen discovery labels. Its “locally irreducible” status therefore means irreducible for this assignment-fidelity objective and observed validation set, not a proof that every retained feature contains clustering signal. The untouched test comparison is useful, but cannot turn that target into minimum signal support.

## Next stage indicated by these panels

1. **Keep sparse-k-means as the primary real-data proposal baseline.** Its recurring METABRIC panels justify testing sparse discriminant mixture proposals or a native mean-shift readout. Measure native assignments and the common spectral/kNN assignments separately. Otherwise a good feature proposal can be judged through an unsuitable splitter.
2. **Test selection and reduction on the saved candidate families before increasing search complexity.** Both exact mean-shift supports already exist in the pools. A predeclared compactness-versus-replication rule should be tested on new seeds, with true labels used only for final diagnostics. Increasing restarts cannot fix a preference for extra features when the desired panel was already found.
3. **Replace a single fidelity number with an explicit reduction target.** Compare fidelity to the frozen discovery rule, independent reclustering stability, pointwise disagreement after label alignment, and loss of original-space separation. Distinguish preserving a useful population pattern from preserving individual kNN boundary decisions. Set tolerances prospectively; do not lower the threshold merely until this pilot's known noise features disappear.
4. **Retain the METABRIC recurring genes as hypotheses, not a fixed winning panel.** On a new development split, ask whether interchangeable subsets recover the same pattern. Later check a separate cohort or unused metadata; existing PAM50 labels and PAM50 membership are related validation axes, not independent biological discoveries.
5. **Keep the easy Levine contrast as a regression test and add a harder scope check.** Use donor grouping where feasible, or test discovery in a broader unlabeled population. Do not use these singleton successes to claim larger-panel capability.
6. **Diagnose shell splitting separately before adding neural/RL machinery.** The saved shell reference panels also have near-zero ARI under the common spectral pipeline. Failure there does not isolate panel search. Establish a working original-panel partition/readout first, then test whether discovery can recover its features.

The next productive question is therefore: **can we retain the candidate coverage already achieved, select smaller panels, and reproduce the same useful partition on new observations?** The pilot provides positive evidence for five-feature proposal discovery and a promising METABRIC panel family. It does not yet provide a validated minimal-panel clustering method.

## Interpretation checks

The analysis keeps selection on labels separate from after-the-fact label diagnostics; distinguishes training from test results; discloses overlapping resamples and specimen-level limitations; treats multiple candidate/seed comparisons descriptively; does not convert nonsignificance into equivalence; does not infer causality from marker selection or correlations; distinguishes fidelity from external validity; does not treat a contextual reference as unique ground truth; does not claim a method's runtime advantage from unequal computational budgets; and does not interpret no reduction as evidence of minimum signal support. No hypothesis tests, biological enrichment tests, confidence intervals, or new model performance estimates were added.
