# September diagnostics, ablations, and kernel experiments

Prepared 2026-11-09 for the thesis-agent handoff. Coverage: research records dated September 14–30, including the fixed-feature-set readout diagnostic recorded in the September 30 assessment but timestamped October 1 in UTC. This is a synthesis of existing evidence, not a new experiment or fresh numerical audit. No original code or result was changed and no models were refitted while preparing it.

All paths below are relative to the repository root, originally `C:/Users/Peter/Desktop/Github/ATOMIC_Clustering`. Historical files and Python names use the old word “panel”; new discussion should use **feature set**. Keep historical paths intact for traceability.

The current decision is the **November 5 pivot**, described in `docs/research/thesis-direction-reassessment-2026-11-05.md`: preserve the restricted radial work, but reconsider the main thesis around compact original-feature sets, executable assignment, and independent-subject/sample generalization. No replacement method was implemented in that reassessment. The September recommendations below explain the route taken; they are not a queue of experiments the next agent should automatically execute.

## What this period established

The initial question was whether the main problem was fitness or evolutionary search. The answer became more specific: at least six separate mechanisms can fail.

1. **Candidate discovery:** useful feature sets may never be proposed.
2. **Ranking:** useful visited candidates may lose to irrelevant ones under the actual objective.
3. **Geometry and assignment:** a splitter can fail even with the correct features, or a replacement splitter can destroy a useful learned partition.
4. **Feature weighting:** finding all useful features does not help if the final metric concentrates on one weak or irrelevant coordinate.
5. **Compression:** a reduced rule can pass reused validation and fail to preserve its teacher on new observations; faithful compression can also preserve a bad teacher.
6. **Cluster interpretation:** repeatability, small feature sets, readable rules, and attractive scores can all occur in a single population. They do not by themselves prove meaningful clusters exist.

There was genuine non-enumerative progress. Learned proposals repeatedly reached a five-feature planted set; fixed-prefix native models could recover five or eight signals in easier settings; a constrained global-kernel proposer later recovered 11, 12, and 11 of 12 planted variables among 200. None of these results established a general nonlinear clustering method, a minimal feature set, biological novelty, or superiority to published feature-selection systems.

## Evidence ledger and study status

| Stage | Main saved evidence | Completed scope | Evidential status |
|---|---|---|---|
| September 14 implementation and short checks | `results/research_checks_20260914/summary.md`; `results/research_final_checks_20260914/score-audit_metabric_seed0_20260915T033708_467355Z/` | 57 targeted software checks; several short diagnostics; final 109-candidate reference-augmented smoke | Engineering and exploratory checks. Not the full pilot. |
| September 15 pilot | `results/research_diagnostics/` | 19 jobs: 3 null audits, 4 fixed-bank score audits, 12 searches × 5 proposal methods; 196.2 seconds recorded job time | Prescribed development comparison, three seeds. Not independent biological replication. |
| September 16 fixed-candidate ranking followup | `results/research_ranking_followup/20260916T025613_491524Z/` | 6 cases, 30 proposal banks, 4 policies; 45.47 seconds | Reanalysis of inspected pilot rows. New reference masks were not search candidates. |
| September 16 component/obstacle suite | `results/research_obstacle_checks/20260916T145427_229536Z/` | 33 cases: 9 retention, 9 compression, 9 geometry, 6 Gaussian controls; 102.63 seconds | Component ablations. Compression reused the pilot; other settings were prescribed development followups. |
| September 21 native-model replication | `results/research_panel_replication/20260921T202232_578177Z/` | 27 cases; 54 independently fitted A/B learners; 11.74 seconds | New development seeds, disjoint within-case discovery blocks; same real cohort. |
| September 23 sparse-objective audit | `docs/research/sparse-objective-math-audit-2026-09-23.md`; replication analysis below | Population derivation plus conditional scoring of saved partitions | Mathematical counterexample and retrospective diagnostics, not a new fitted method. |
| September 27 kernel prototype pilot | `results/research_kernel_panels/20260927T043314_711791Z/` | 21 cases; 5 autonomous variants plus all-feature graph; 186.4 seconds | Prespecified development variants on new development seeds; no external-method reproduction. |
| September 30 rank-preservation correction | `results/research_rank_preservation/20260930T034706_021919Z/` and `20260930T044157_487943Z/` | Same 24 jobs executed twice, 56.5 and 54.6 seconds | Same parent data, seeds, and configuration; identical arrays. Repeatable execution, not extra independent replications. |
| Fixed-feature-set readout comparison | `results/research_panel_readouts/20261001T024554_885812Z/` | 12 global-branch cases × 2 fixed supports; about 1.6 seconds | Explicitly posthoc diagnostic on the same inspected rows. |

These were not a frozen final pipeline evaluated on independent confirmation datasets. Individual policies, candidates, and splits were frozen within the stated comparisons, but the sequence was an adaptive development process. In particular, a file named “test” ceases to be untouched confirmation for a method redesigned after its results were inspected.

## 1. September 14: replace an opaque success claim with a diagnostic harness

Main sources: `docs/research/experiment-plan-2026-09-14.md` and `verification-2026-09-14.md`. New modules were placed in `atomic_research/`, separately from the historical implementation. The global research skill was installed and enabled as `ars-codex@ars-codex` version 0.1.28; installation itself was not research evidence.

The harness deliberately studied one binary local split, before recursion, automatic cluster count, or a stopping rule. It compared random masks, budgeted forward growth, a simple add/drop/swap evolutionary baseline, smooth spectral feature-weight proposals, and sparse-k-means proposals. All could propose sets larger than three without initializing from every pair or triple. **The evolutionary baseline was not the historical NSLC engine.** The smooth-graph prototype was not DUFS, and the sparse-k-means comparator was not CHIME.

Important repairs and accounting decisions:

- Graph and density terms were calculated for the same emitted partition. The historical hybrid could mix a spectral partition's graph score with an MST partition's density score.
- A discovery-only random reference bank fixed scaling units. All profiles used the same eligible intersection, avoiding a validity-policy confound. This made scores reproducible, not comparable probabilities or size-unbiased evidence.
- The density term was a DBCV-style surrogate, not full DBCV.
- Discrete searches had equal caps on unique candidate scores. Learned proposers also incurred recorded training work and could emit fewer candidates. This was **not matched total compute or wall time**.
- Discovery/validation/test splits were 50/25/25, label-blind and not retried for label balance. Imputation/scaling used discovery only. Reference labels entered reporting after decisions.
- Selected partitions were transferred by a distance-weighted 7-nearest-neighbor rule. Greedy deletion sought validation ARI at least .95 against that original frozen rule. A depth-three tree was an approximate explanation, with fidelity reported.

Short development diagnostics already separated failures. In a 240-patient METABRIC check, the simple EA visited training ARI .459 but selected -.009, with test ARI -.016. The supplied five-feature shell set gave spectral training ARI -.006 at 120 discovery observations. A bimodal singleton gave permutation p=1 because permuting its only column leaves its distribution unchanged. The correlated-Gaussian smoke had correlation p=.05 and graphcut p=.10 with 19 permutations. These were dependence comparisons, not tests of cluster existence. Do not confuse them with the later full-pilot permutation counts.

Software validation covered partition consistency, gradients, sparse weighting, label-blind preprocessing, candidate caps, external-label permutation invariance, and saved-rule prediction: 57 checks passed. Older smoke folders contain earlier hashes and must not be pooled with the final pilot.

## 2. September 15 pilot: useful feature sets were reached, then often mishandled

Sources: `pilot-assessment-2026-09-15.md`, `pilot-statistical-audit-2026-09-15.md`, `pilot-geometry-audit-2026-09-15.md`, `pilot-panel-interpretation-2026-09-15.md`, all under `docs/research/`.

All 19 jobs completed. Main searches used 480 observations, with 240/120/120 disjoint rows and seeds 0, 1, 2. Discrete methods scored 100 candidates; learned banks were often smaller, with their optimization cost recorded separately. The saved audit reproduced 4,833 candidate scores, all 60 selected candidates, and their retrospective best-visited training ARIs. This checked implementation/reporting consistency, not scientific truth.

Mean external-label test ARI after transfer:

| Proposal method | Five-feature mean shift, p=50 | METABRIC LumA/LumB | Levine CD4/CD8 |
|---|---:|---:|---:|
| Random | .152 | .019 | .956 |
| Forward | .162 | -.002 | .913 |
| Simple evolutionary | .268 | .145 | .956 |
| Smooth graph | .712 | .118 | .956 |
| Sparse k-means | .668 | .356 | .956 |

All methods were near zero on shells. Therefore “EA never helps” is too strong: this simple EA improved on random in mean shift and METABRIC, but learned proposals were stronger in important settings. These results do not evaluate every EA or the historical NSLC algorithm.

Both learned proposers **visited the exact five-feature mean-shift support in every seed**. They instead selected 6–8 features, keeping 1–3 nuisance variables, and the original compressor removed none. The exact support's objective values were 2.160, 1.877, 2.374; the winning larger sets had larger scores. That is a concrete ranking/compactness failure, not absence of the useful candidate. However, the mean shift is distributed low-order information, not a pure five-way interaction; fewer than five features can still be useful.

On METABRIC, sparse-k-means proposals selected 5, 5, and 8 genes with test ARIs .316, .335, .418. CEP55 and PTTG1 appeared in all three original sets; PAM50 overlaps were 5/5, 5/5, and 7/8. Smooth-graph sets had no pairwise gene overlap and test ARIs .316, -.008, .047. In one graph run a visited set had training ARI .561, but the selected set had -.003. These are plausible recurring features and a ranking warning, **not a new biomarker discovery**. The source universe was PAM50 enriched and previously variance-filtered using all patients; the benchmark is a label-defined LumA/LumB contrast. The three 480-patient samples overlapped by 194–196 patients. The contextual full-PAM50 ARI .352 was obtained through this project's spectral/kNN pipeline, not the published PAM50 classifier.

Levine was largely an easy singleton recovery check. CD8 alone was selected in two seeds; both learned proposers had the same outputs. Random search also averaged .956. Cells came from existing specimens, so cell holdout was not donor transfer. This did not demonstrate difficult larger-feature-set discovery or full unfiltered population hierarchy recovery.

The paired score audit did show that partition consistency mattered. Consistent versus legacy selected test ARI was .967 versus .181 on Levine and .418 versus -.007 on METABRIC. But the METABRIC winner was a supplied reference deletion containing 49 genes, not autonomous small-set discovery. Spectral/MST partitions had ARI below .5 in 378/379 paired-bank candidates. Across ordinary random masks, graphcut and density had opposing size trends; for mean shift their size correlations were -.963 and +.954. Graphcut alone selected a singleton in all four score audits. Reference augmentation inflated apparent score/quality association: METABRIC correlation fell from .701 across the augmented bank to .076 among random candidates.

Compression also failed its intended held-out target: 17 outputs deleted features, and 12/17 ended below ARI .95 fidelity on test despite passing validation. ARI .95 does not mean 95% point agreement; around balanced groups of 120, two changed assignments can yield ARI about .934. Preserving a noisy kNN boundary can also preserve nuisance dependence.

The shell oracle diagnosis was decisive. On the supplied five features, raw spectral clustering had training ARIs approximately -.001, .001, .004; about 47–51% of outer-shell ten-nearest-neighbor edges went inward. The graphcut score favored a directional split over the generating radial split. Squaring the supplied discovery-centered/scaled coordinates made spectral training, transfer, and independent test reclustering all reach ARI 1.0. But autonomous squared-feature sparse k-means over all 50 features still missed the full support. **Expressing the answer with an oracle transformation did not solve discovery.**

The full null audit used 39 permutations: correlated-Gaussian correlation p=.025, graphcut p=.10; bimodal-singleton p=1 for both. Column permutation tests independence, not “no clusters.” There was no acceptance test, hence no false-split rate.

## 3. Fixed-candidate ranking: size correction was not the cure

Source: `docs/research/ranking-assessment-2026-09-16.md`; run `results/research_ranking_followup/20260916T025613_491524Z/`. Six mean-shift/METABRIC cases reused their pilot candidate banks. The runner added 24 random references per represented size, never as selectable candidates, and compared original global scaling, a larger global reference bank, size centering with common within-size scales, and size-specific means/scales.

The audit reproduced 30 original selections, 120 policy winners, 2,366 saved candidates, and calibration from 1,152 new reference records. Crucial correction: **size centering also replaced component scales with pooled within-size residual scales**. Comparing it with the global policy is not a pure centering-only intervention.

Each row below averages five methods × three seeds, so these are dependent descriptive outcomes:

| Dataset/policy | Training selection regret | Development-test ARI | Selected size |
|---|---:|---:|---:|
| Mean shift/original | .1426 | .3923 | 7.13 |
| Mean shift/new global | .1426 | .3923 | 7.13 |
| Mean shift/centered | .0868 | .4401 | 6.47 |
| Mean shift/standardized | .1441 | .4057 | 5.87 |
| METABRIC/original | .2606 | .1274 | 6.00 |
| METABRIC/new global | .2786 | .0966 | 6.07 |
| METABRIC/centered | .2806 | .0926 | 6.53 |
| METABRIC/standardized | .2798 | .1064 | 3.87 |

Regret means retrospective best-visited training ARI minus chosen training ARI. It uses privileged labels after selection and is not an available unsupervised selection policy. The larger reference bank changed only 2/30 winners, both worse METABRIC EA outcomes. Size centering improved METABRIC training regret in four banks but worsened test ARI in every one of its six changed winners. Sparse-k-means METABRIC means were .356 original, .290 centered, .324 standardized. Smaller selected sets were not necessarily more useful.

Decision at the time: stop assuming another global normalization solves ranking; inspect native model retention, assignment, and compression. This experiment did not test how search would behave if trained under the alternative objectives.

## 4. The 33-case obstacle suite: actual component ablations

Plans and findings: `obstacle-checks-2026-09-16.md`, `obstacle-compression-audit-2026-09-17.md`, `obstacle-geometry-controls-audit-2026-09-17.md`, `next-ablation-plan-2026-09-21.md`. Main run: `results/research_obstacle_checks/20260916T145427_229536Z/`.

Retention compared full weighted centroids, truncated stored centroids, refitted weighted/unweighted centroids, centroid versus kNN readout, and spectral replacement on the same features. Raw and centered-squared representations used three prescribed L1 bounds, three starts per bound, and 40 iterations; eight-feature prefixes were reported, but full positive-weight support could exceed eight. Seeds 3–5 were used for retention/geometry/controls; compression replayed pilot seeds 0–2.

The METABRIC prefix-eight centroid-kNN versus spectral-kNN ARIs were .442/.296, .467/.276, .475/.259 across the three sparsity bounds. Holding features, unweighted coordinates, and kNN readout fixed exposed harm from replacing the partition family. In mean shift at moderate sparsity, native .779 became weighted-prefix .779, unweighted centroid .749, centroid-kNN .711, spectral-kNN .711: weight removal and assignment mattered, but spectral replacement added no aggregate loss in that comparison. There is no universal “centroids always win” conclusion.

Compression compared four greedy policies against the same original teacher:

| Policy | Reduced outputs / 14 non-singleton instances | Features removed | Reduced outputs failing the corresponding test criterion |
|---|---:|---:|---:|
| Validation ARI at least .95 | 5/14 | 10 | 3/5 |
| At most 5% validation disagreement | 14/14 | 45 | 9/14 |
| At most 5% disagreement in each of 3 validation folds | 13/14 | 34 | 6/13 |
| Refit k-means, then at most 5% disagreement | 12/14 | 41 | 9/12 |

The foldwise rule was a sensitivity check, not a confidence bound. There were 18 method/set instances, but four were already Levine singletons, and Levine duplicates were not independent evidence. The refit arm changed the model before deleting variables; two unchanged refits did not even pass validation fidelity and must not count as accepted compression. In one mean-shift example, replacing the teacher raised external ARI .534→.778, then deletion lowered it to .584. Reporting only .534→.584 would misattribute the gain to deletion.

At the individual-deletion level, frozen-kNN tests allowed 14/15 nuisance deletions on validation but only 6/30 planted deletions; 12/15 nuisance and 1/30 planted deletions passed both validation and test. Greedy adaptive reuse nevertheless accumulated errors. Planted support is not automatically the unique smallest useful set under a nonzero prediction tolerance.

Geometry removed feature search entirely by supplying the five shell coordinates:

| Total n (discovery half) | Raw spectral k=5 | Raw k=10 | Raw k=20 | Squared spectral, all three k | Radius rule |
|---:|---:|---:|---:|---:|---:|
| 480 | .028 | .006 | .004 | 1.000 | 1.000 |
| 960 | .024 | .006 | .008 | 1.000 | 1.000 |
| 1920 | .888 | .004 | .000 | 1.000 | 1.000 |

All 27 squared-spectral and nine radius outputs had training/test ARI 1.0. Raw k=5 succeeded better only with more observations; raw spectral is not impossible in principle. Autonomous squared native fits still achieved at most .140 ARI; all top-five/top-eight sets contained at most 2/5 signals.

A separate population calculation explained why pairwise squared-correlation screening is weak for ideal five-dimensional shells: covariance of distinct squared coordinates is -1/140, correlation -1/67, while the complete squared radius perfectly identifies shell. This is not a parity claim or a measured noisy-sample correlation.

Single-Gaussian controls undermined simplistic stability claims. A correlated squared-Gaussian fixed-set centroid refit reached ARI .948, with only one changed assignment among 120, despite one generated population. That test refitted the partition on an already discovered set; it did not independently rediscover features. No acceptance rule was implemented.

The later read-only audit passed 62,004 checks (`results/research_obstacle_analysis_20260921/analysis.md`). An earlier verifier failed because its contingency table omitted trailing empty cells; the verifier was corrected and regression tested. Do not report this as an experimental clustering failure. Geometry predictions and independent test-only centroid labels were not saved, limiting independent replay of those particular metrics.

## 5. Native-model replication and conservative compression

Sources: `next-ablation-plan-2026-09-21.md`, `panel-replication-assessment-2026-09-24.md`, `panel-replication-scaling-audit-2026-09-23.md`, `panel-replication-statistical-audit-2026-09-23.md`. Run: `results/research_panel_replication/20260921T202232_578177Z/`. Audit: `results/research_panel_replication_analysis_20260923/analysis.json` and `.md` (15,918 checks).

Each 800-row case had four disjoint blocks of 200: discovery A, discovery B, validation, test. A/B separately fitted preprocessing and native sparse two-means. The L1 bound was 4, with three starts and 40 iterations. From each native ranking, prefixes 1–16 were frozen before validation, retaining stored weights and centroids. Empirical selection required at most 5% observed disagreement with its own teacher. Bounded selection required a one-sided Clopper–Pearson upper bound at most 5%, with Bonferroni over both 16-prefix ladders (32 candidates). Missing results were explicit, without a favorable fallback. Exact linear native rules in original units were exported.

The bound is conditional on fixed discovery models and iid independent validation observations. It concerns teacher disagreement within one case's candidate family, not cluster truth, independent-cohort validity, global minimum size, or simultaneous performance over every future experiment. At n=200, the upper bounds for 0/1/2 disagreements were .031791/.042852/.052320, so only zero or one error could pass. Observed finite test error exceeding 5% would not by itself disprove a valid population-risk bound.

The study contained 18 mean-shift cases (p=50/200, signals=5/8/12, seeds 6–8), three METABRIC cases, and six independent/correlated Gaussian controls. It completed all 27 in 11.74 seconds.

On the **same 42 learners with a bounded output**, empirical versus bounded mean test disagreement was 3.92% versus .95%; exceedances above 5% were 12/42 versus 0/42; median size was 4 versus 8. Over all learners, empirical availability was 54/54 with 13/54 exceedances, while bounded availability was 42/54 with 0/42. This is a fidelity/size/availability trade-off; it does not isolate confidence-bound machinery from retaining more features. Twelve missing outputs must remain visible.

At p=50/s=5 all six bounded outputs exactly recovered the planted support; at p=50/s=8 all six retained every signal with mean size 8.33. These were learned prefixes, not enumerated combinations. Harder full models failed before compression:

| Available p | Signals s | Full native test ARI | Supplied-feature two-means oracle ARI | Exact top-s ranking |
|---:|---:|---:|---:|---:|
| 50 | 5 | .725 | .782 | 6/6 |
| 50 | 8 | .679 | .739 | 5/6 |
| 50 | 12 | .535 | .725 | 5/6 |
| 200 | 5 | .515 | .774 | 4/6 |
| 200 | 8 | .424 | .773 | 4/6 |
| 200 | 12 | .165 | .753 | 0/6 |

The six learners per row are not six independent datasets: A/B share evaluation rows and a generated population. The oracle used supplied features and a different ordinary two-means fitting routine. It establishes recoverable information, not an autonomous baseline or a one-factor causal comparison.

Good rankings did not guarantee good weights. At p=200/s=8/seed6/B, all eight signals ranked first, yet full ARI was .369 versus oracle .773; the largest feature weight was .815. Some failed teachers were faithfully compressed to irrelevant singletons. Conversely, p=200/s=5/seed8/A had ARI .846 and exact top-five recovery but no bounded output: that missingness concerned certification/cap limits, not failed discovery.

METABRIC full native mean ARI was .492 and full A/B test agreement .847. Bounded sets existed for only 3/6 learners, with sizes 10, 15, 8; **no seed had both bounded outputs**, so there was no completed bounded-set A/B replication pair. The three 800-patient samples overlapped by 547–551 patients, from the same 1,175-patient contrast. Correlated-Gaussian controls had full A/B ARI .773 and two bounded pairs averaging .757, despite no latent groups. Exact selected-feature overlap could be zero while assignments agreed, because correlated features substitute for each other. Full positive-weight-support Jaccard was often misleadingly one because nearly every coordinate received some weight.

## 6. A mathematical objective counterexample

Full derivation: `docs/research/sparse-objective-math-audit-2026-09-23.md`. This concerns the **standardized sparse-k-means weighted between-cluster sum-of-squares objective**, not every fitness ever tried in ATOMIC.

For equally weighted Gaussian mean-shift signal with total mean separation 3, let a=1.5 and s be the signal count. The Bayes observed-data direction has optimized population objective per observation

`J_signal(s) = m^2 * sqrt(s) / (s + a^2)`, where `m = 2*phi(a) + a*(2*Phi(a)-1)`.

A feasible split on one independent Gaussian nuisance coordinate has `J_noise = 2/pi = .636620`. Both obey the nonnegative L2/L1 weight constraints and correspond to actual centroid assignment boundaries. At s=5/8/12, signal objectives are .749245/.670344/.590545. Therefore at s=12 the intended informative split loses to a nuisance split even in the population limit. A weak one-signal-coordinate split can also score higher (.639647) while its limiting label ARI is only .112, versus about .751 for the full Bayes direction.

Important correction: compare the observable Bayes-direction split, not inaccessible latent labels. The latent-label formula would incorrectly suggest this ordering already at s=8. The signal/noise crossing is about s=9.53 under the stated feasible range, not an unrestricted statement for arbitrary s or sparsity bounds.

In saved p=200/s=12 cases, optimizing weights conditionally for each fixed partition gave the native partition a larger score than the supplied-feature oracle partition in all six fits: mean .677 versus .632, while external test ARI was .165 versus .753. Conditional weight optimization is not a joint centroid refit and not an available unsupervised oracle.

Consequences: better optimization alone cannot guarantee the desired partition under this objective. It does not prove every global optimum is pure noise, every useful partition loses, or every observed failure is only fitness. Dividing weighted BCSS by weighted total variance worsened this counterexample. A signed-projection ratio removed the specific dimension penalty, but a single uniform distribution scored .75, above the intended mixture's .74747. That alternative was not a universal cluster-validity solution either.

Proposed followups included fixed-partition comparisons, ordinary/oracle/nuisance initializations, a 30-start comparison, a carefully solved weight-concentration constraint, and fresh validation sizes 200 versus 800. These were recommendations in September documents, **not completed experiments evidenced by this review**. Do not represent them as ablations already run.

## 7. GroupFS audit and the kernel prototype: what was actually borrowed

Sources: `groupfs-mechanism-audit-2026-09-25.md`, `kernel-benchmark-scope-2026-09-25.md`, `kernel-prototype-plan-2026-09-25.md`, `kernel-verification-2026-09-27.json`.

The GroupFS paper and public author code were inspected, not installed/reproduced. GroupFS's learned Q acts on feature memberships, producing a feature embedding; it is **not a learned sample projection XQ**. Its sample graph is rebuilt on gated original inputs, with a diffusion-smoothness objective. Its feature graph is frozen before training. Group count is supplied or chosen separately, not differentiated. Self-tuning local scale still requires a neighbor choice. The inspected public code also had a gate-activation regularizer formula differing from the probability implied by its implemented gates; no empirical impact was measured. The paper's accuracy-guided feature-budget choices cannot be adopted as label-free selection.

Our already existing smooth graph used a dense RBF kernel, so “add a kernel” alone was not a new mechanism. The new prototype instead learned a row-sparse **sample projection** A, with a hard original-feature budget and Frobenius norm one, then formed `U = standardized X @ A`. It compared diagonal/no-mixing and signed rank-two mixing, local/global affinities, and lambda2 versus lambda2/(lambda3+epsilon), with a mild degree penalty. It saved a native frozen Nyström-style extension and spectral-center readout, rather than silently handing its mask to an unrelated classifier. A depth-three tree remained an approximate explanation.

Five autonomous arms were prescribed: diagonal/cut/local; diagonal/gap/local; projection/cut/local; projection/gap/local; projection/gap/global. Same-support identity graphs and ordinary centroids isolated representation/readout effects. Local affinities were graph kernels, not a claimed positive-semidefinite Mercer kernel. The learned projection was explicitly GroupFS-inspired, not a reproduction; group memberships, stochastic gates, and GroupFS diffusion loss were absent.

The planned broader benchmark document included thick shells with s=6/12 and radius ratio 1.35, quantified three-coordinate Bayes-error bounds, covariance interactions, spirals, density imbalance, and surrogate features. **Those are not the completed pilot settings.** The executed pilot had s=5 shells with radii 1 and 2, grouped moons containing ten noisy measurements of two latent coordinates, and an eight-feature covariance-regime task. Its 21 cases used seeds 26–28, n=800 split 400/200/200, budget 16, rank at most two, 200 landmarks, 60 gradient steps, and three restarts. Optional `geometry` and `real` runner suites and external GroupFS/DUFS/sparse-kernel comparisons were prepared/proposed, not evidenced as completed here.

The 52 implementation tests and one-case three-step smoke verified engineering, not efficacy. Ten smoke native models replayed in 46 checks, and 44 preceding replication hashes were unchanged. The smoke itself showed learned mixing worse than identity on its selected set; it was not presented as a success.

## 8. Completed kernel pilot: fitness could improve while useful structure deteriorated

Sources: `kernel-pilot-assessment-2026-09-29.md`, `kernel-objective-results-2026-09-27.md`, `kernel-geometry-results-2026-09-27.md`. Run: `results/research_kernel_panels/20260927T043314_711791Z/`; read-only replay: `results/research_kernel_analysis_20260927/analysis.json` and `.md`. All 21 cases completed in 186.4 seconds. The analyzer replayed 201 saved native models and 6,966 checks, including 46 historical hashes. It did not reconstruct exported tree text or unsaved same-support centroid models.

Mean held-out external ARI over three seeds:

| Family | Local projection/gap | Global projection/gap | Supplied true-set local graph | Supplied generator rule |
|---|---:|---:|---:|---:|
| Mean shift, p200/s12 | .331 | .519 | .710 | — |
| Grouped moons, p50/s10 | .502 | .524 | .595 | — |
| Shells, p50/s5 | -.002 | .014 | .014 | 1.000 |
| Covariance pairs, p50/s8 | .002 | -.002 | .037 | .864 |

The true-set/rule columns were privileged ability checks. The covariance target was recovery of overlapping dependence regimes, not separated density components. A rank-two linear projection can discard high-dimensional radius information; a subsequent nonlinear kernel cannot reconstruct discarded information. But identity on the correct shell set also failed in this particular 200-landmark graph, so projection loss was not its sole problem.

The exact sparse-PCA initializer was reconstructed after the run. Local gap optimization reduced training loss in all six mean-shift/moons cases but decreased test ARI in five and tied once. Independent-row validation loss still favored four harmful local changes. Global optimization reduced ARI in four of six. Final winners could come from different restarts than the PCA start: this diagnosed optimization plus selection, not always a single trajectory. Mean-shift seed26/local selected a no-signal random-start set with better loss than the useful PCA-start trajectory.

The global map nearly collapsed to a line: all 21 global-gap transforms had second/first singular-value ratio at most .008609; 20 were at most .000150. Frobenius norm one does not constrain each singular value. A population calculation on a single independent Gaussian explained the incentive: with the implemented global affinity, the gap ratio falls from 1 for an equal rank-two projection to 2/3 in the rank-one limit. The degree-penalty change was only about .000032 after weighting, too small to offset this. This was an objective preference possible without hidden clusters or finite-sample overfit; exact finite-sample constants have additional assumptions.

Feature selection could be better than the learned map. Global mean-shift supports recovered 8, 10, 11 of 12 signals in sets of 16. On those identical sets, mean identity-graph ARI was .607 and ordinary-centroid ARI .651, versus native projection .519. These were all-reported diagnostics, not permission to choose the best test readout. On grouped moons, diagonal-gap was competitive and mixing was not established as necessary.

No projection tree among 63 had at most 5% disagreement on both validation and test. Global mean-shift test disagreement averaged 25.7%. Thus these trees were not the actual classifier's rule. All 21 diagonal-cut fits shrank to one feature and were easy to approximate, but often wrong. All 54 outputs across three null families were numerically valid; forced two-way assignments did not constitute accepted clusters or false positives.

## 9. Rank preservation: a successful numerical repair with a narrow scientific benefit

Sources: `rank-preservation-assessment-2026-09-30.md`, `rank-preservation-objective-audit-2026-09-30.md`, `rank-preservation-interpretability-audit-2026-09-30.md`. Primary run: `results/research_rank_preservation/20260930T044157_487943Z/`; earlier repeat: `20260930T034706_021919Z`. Audit outputs: `results/research_rank_analysis_20260930/analysis.json` and `.md`.

The new constraint `A.T @ A = I/2` was imposed by a scaled polar factor within retained support, rejecting rank-deficient supports. It preserved coefficient rank, not isotropy or multimodality of observations. The 24 jobs were mean shift, grouped moons, independent Gaussian, correlated Gaussian × three old seeds × local/global kernels. Shells and covariance regimes were excluded because their earlier geometry tests failed. Four objects were kept distinct: original frozen sparse-PCA; saved unconstrained optimum; frozen constrained PCA; optimized constrained model. The main baseline for the effect of optimization was **frozen constrained PCA**.

Both completed runs had identical model arrays/predictions/metrics (2,112 comparisons). The audit passed 19,013 checks across both runs' 192 model outputs; this was not six generating seeds. All constrained transforms satisfied the intended condition to numerical precision, maximum error about 8e-16.

| Family/kernel | Old unconstrained test ARI | Frozen constrained PCA | Optimized constrained |
|---|---:|---:|---:|
| Mean shift/global | .519 | .587 | .618 |
| Mean shift/local | .331 | .588 | .561 |
| Grouped moons/global | .524 | .560 | .549 |
| Grouped moons/local | .502 | .569 | .552 |

Global mean shift improved in each seed and changed support from 9/9/10 planted features to 11/12/11, gaining six signal occurrences and losing none. Recall was 34/36, but precision only 34/48 because each set still contained 16 features. This justified retaining it as a **candidate feature-set proposer**, not a general accepted fitness or a novel complete method.

Local mean shift and both moons variants still included cases where training and validation loss improved while test ARI worsened. Apply that stopping rule by setting; do not discard the positive global mean-shift result or generalize it to the failures. All moons signals could be retained while useful loading was lost: global signal loading fell from about 94% to 56–64%, with nuisance allocation rising accordingly. Perfect support recall did not ensure good geometry.

Rank preservation largely removed transferable independent-Gaussian loss gains: global validation loss worsened after optimization despite training improvement. Correlated-Gaussian validation loss could still be lower than mean-shift loss. A full-rank transform does not whiten correlated data, and a thin continuous population can still be split stably. None of the 24 optimized depth-three trees passed 5% disagreement on both validation and test.

## 10. Posthoc fixed-set readouts: exact rules without claiming graph fidelity

Evidence: `results/research_panel_readouts/20261001T024554_885812Z/summary.md` and case artifacts; described in the September 30 assessment. Each global branch's frozen and optimized support was held fixed, and identity-kernel and ordinary-centroid models were fitted on the same discovery rows. All outputs were reported, including controls; no new feature search or test-based winner selection occurred. Choosing to perform this diagnostic was itself posthoc.

| Family/support source | Native projection | Identity kernel | Ordinary centroids |
|---|---:|---:|---:|
| Mean shift/frozen PCA support | .587 | .603 | .601 |
| Mean shift/optimized support | .618 | .666 | .733 |
| Grouped moons/frozen PCA support | .560 | .500 | .499 |
| Grouped moons/optimized support | .549 | .499 | .504 |

For optimized mean-shift sets the centroid test ARIs were .704, .738, .756, each better than centroid readout on its starting set. Holding the readout family fixed provided evidence that the support change contributed value. Centroids hurt moons relative to the graph, so this was a mean-separation lead, not a universal nonlinear replacement.

All 24 centroid models exported exact original-unit linear assignment rules, including discovery imputation and threshold conventions. Those rules reproduced predictions on all three blocks in 72 checks; a separate saved-state review passed 521 checks and three relevant tests. Numerical JSON coefficients, rather than rounded display text, retain exact precision. The rule was exact **for the centroid model**, not a faithful explanation of the different graph classifier. Up to 16 features remained, so mathematical exactness did not establish adequate human readability or minimality.

## What was only proposed, not established by these September results

- The initial 40-job larger-feature-set scaling sweep was prepared; do not infer completion from its command in the September 14 plan. The later 27-case native replication was a different experiment.
- More starts, a concentration-constrained sparse-k-means update, oracle/nuisance initialization trajectories, and larger independent validation blocks were recommendations, not completed followups in the reviewed evidence.
- GroupFS, DUFS, CHIME, and sparse kernel k-means were discussed as comparators; none was reproduced in these completed September suites. The prototypes are not substitutes for author-implementation comparisons.
- The broader geometry/real kernel suites, thick-shell radius-ratio-1.35 information benchmark, and substantial benchmark matrices were plans. The executed pilot's shell settings were different.
- Sparse shared-scale mixtures, original-feature quadratic rules, a matched independent-marginal nuisance model, and a one-Gaussian versus two-component comparison were proposed directions. Some radial ideas were developed later in October, outside this chapter. They must not be credited as implemented by September.
- There was no recursive end-to-end interpretable hierarchy, calibrated decision that clusters exist, independent donor/cohort validation, demonstrated useful feature necessity, or verified novelty/SOTA claim.

## Corrections the next agent must retain

1. Do not equate the new simple evolutionary baseline with historical NSLC, or conclude all EAs fail from these comparisons.
2. Do not call a supplied-support or supplied-generator-rule result autonomous discovery.
3. Do not interpret best-visited ARI as an available label-free selector or independently verified test utility.
4. Do not combine graph and density measurements from different partitions and call them evidence for the emitted split.
5. Do not call size centering a means-only intervention in the actual ranking followup.
6. Do not equate ARI .95 with 95% unchanged assignments.
7. Do not attribute a same-set model-replacement gain to compression or feature discovery.
8. Do not equate fidelity, rediscovery, selected-feature identity, external-label agreement, and evidence of multiple populations.
9. Do not pool repeated executions, A/B learners sharing test rows, overlapping cohort resamples, or many candidate checks as independent replications.
10. Do not infer necessary high-order information from noisy copies of a two-coordinate moons source, or from the size of an output set.
11. Do not confuse GroupFS's feature embedding with our sample projection, a local affinity with a guaranteed Mercer kernel, or coefficient rank with projected-data isotropy.
12. Do not present shallow trees with substantial disagreement as the native classifier. Exact centroid rules changed the classifier family.
13. Do not turn the sparse-BCSS population counterexample into a claim that every objective or every dataset is impossible.
14. Do not use “test” filenames to conceal adaptive reuse. This development sequence requires fresh, frozen evaluation for any subsequent confirmatory claim.

## File map for deeper inspection

The narrative sources listed above contain full tables and qualifications. Start with the stage assessment, then use its audit and result directory. Every result directory's `manifest.json`, saved configurations, hashes, data protocol, predictions, and case reports are more precise than an abbreviated conversation summary.

Relevant implementation/entrypoint families:

- Initial proposal/scoring harness: `atomic_research/experiment.py`, `scoring.py`, `datasets.py`, `soft_graph.py`, `sparse_kmeans.py`; `scripts/run_research_suite.py`, `run_research_diagnostics.py`.
- Fixed-bank ranking: `scripts/run_research_ranking_followup.py`, `analyze_research_ranking_followup.py`.
- Component ablations: `atomic_research/retained_models.py`, `obstacle_audits.py`; `scripts/run_research_obstacle_suite.py`.
- Native replication/compression: `atomic_research/replicated_panels.py`, `fidelity_bounds.py`; `scripts/run_research_panel_replication.py`, `analyze_research_panel_replication.py`.
- Kernel models: `atomic_research/kernel_panels.py`, `kernel_benchmark.py`; `scripts/run_research_kernel_panels.py`, `analyze_research_kernel_results.py`.
- Rank constraint: `atomic_research/rank_preserved_kernel.py`; `scripts/run_research_rank_preservation.py`.
- Historical implementation verification: `docs/research/verification-2026-09-14.md`, `kernel-verification-2026-09-27.json`; exact dependencies in `requirements-research-lock.txt`.

For handoff packaging, preserve the assessment/audit documents and the referenced manifests, summaries, case records and prediction/model artifacts when space permits. A count of thousands of passed replay checks means saved-state consistency, not thousands of independent successful experiments. This chapter did not recompute any of those historical audits or re-verify today's source bytes against historical hashes.

Coverage gaps are intentional: the pre-September-14 legacy-source audit, October radial-model development and feature-set search, October frozen replication, and November proposal pivot need their own chapters. This chapter supplies the diagnostic chain that explains why those later decisions were made.
