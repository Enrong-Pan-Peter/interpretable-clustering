# Next experiment: reproducible panels with exact native rules

## Material Passport

- Origin: independent experiment-design review
- Origin Skill: academic-research-suite
- Origin Date: 2026-10-04
- Origin Mode: plan / statistical protocol review
- Verification Status: UNVERIFIED (proposed); no new clustering fits or experimental results
- Version Label: interpretability_protocol_review_v1
- Inputs: the original project's recursive-panel/tree objectives; the September replication, kernel, and rank-preservation assessments; the October 1 fixed-panel readout results
- Deliverable: bounded specification for the next experiment, with explicit graduation and fallback decisions

## Recommendation

Test the surviving method component as **original-feature panel discovery followed by a declared native assignment model**. For the immediate mean-separation experiment, compare only frozen-PCA panels and rank-preserved global-search panels, using the same ordinary centroid readout. Independently rediscover each procedure, then select a shorter native rule from a discovery-fitted prefix ladder using independent fidelity certification.

This retains the project's central goals: named panels, automatic panel size, a readable assignment, reproducibility, a future recursive tree, and an interactive choice among meaningful alternatives. It does not turn the project into a claim that centroids solve nonlinear clustering. The existing nonconvex failures remain explicit, and a shape-specific branch must earn its own native rule and node-validation evidence.

The October 1 mean-shift ARI of about .733 is encouraging development evidence. It is neither independent confirmation nor an external-method comparison. Freeze the next configuration before generating new observations.

## 1. Deliverable and comparison

The immediate deliverable is one validated **candidate tree node**, not a fully grown hierarchy. Its saved object contains a feature panel, discovery preprocessing, a full native model, a frozen ordered list of candidate reduced models, certification results, and an exact rule. An evidence status separately states whether the node is merely a candidate partition or has passed a prespecified split-acceptance check.

Two primary procedures:

1. Frozen rank-preserved PCA support, budget 16, followed by unweighted two-means in discovery-standardized selected coordinates.
2. Global rank-preserved search, rank 2 and budget 16, followed by exactly the same centroid readout.

Freeze the existing optimizer settings rather than adding a kernel/rank/step grid: 60 steps, three starts, 200 discovery landmarks, and current preprocessing. Keep the original native graph prediction as a secondary geometry diagnostic, especially on the curved sentinel. It does not compete for a test-selected winner.

External GroupFS/DUFS/sparse-kernel comparisons remain necessary before a relative-performance claim. They are a later controlled comparison, not a prerequisite to this component-level decision.

## 2. Independent blocks from one feature population

For each of ten fresh population replicates, generate and save a population specification once: original feature identifiers, signal support, any synonym groups, loadings, nuisance law, and class proportions. Then draw independent blocks from that same specification:

| Block | Suggested rows | Permitted role |
|---|---:|---|
| Discovery A | 400 | Fit A's preprocessing, panel, full centroid model, and all reduced models |
| Discovery B | 400 | Independently fit the corresponding B pipeline |
| Certification C | 800 | Select among the already frozen prefix rules by fidelity to their own frozen full model |
| Test T | 2,000 | Report final utility, rule agreement, A/B rediscovery, and all failure denominators |

These are fresh observations, not a new split of the repeatedly inspected September pilot. Within a replicate, A and B share feature identities and population parameters; they do not independently reshuffle which columns are signals. Across replicates, a new saved population permutation is permitted. Use independent random streams for the population definition and each block. Labels and reference panels are inaccessible to fitting and certification.

Using 400 discovery rows preserves the existing discovery difficulty. Increasing C improves certification precision without improving the fitted teacher. A larger untouched T gives a clearer descriptive utility estimate without being used for selection. This remains a ten-replicate developmental comparison, not a basis for broad population claims.

The full A and B discovery fits are independent conditional on their common population specification. Their reduced-model choices share C, so the selected reduced pipelines are **not fully independent end-to-end replications**. Label these comparisons accordingly. For uncertainty summaries and graduation decisions, average A/B outcomes within each population replicate and compare the ten population-level results; do not count the twenty A/B fits as twenty independent populations.

## 3. Short prespecified matrix

All primary mean/Gaussian conditions use 200 available features. This avoids comparing a 200-feature signal task with easier 50-feature nulls.

| Condition | Fixed structure | What it decides |
|---|---|---|
| Distributed mean separation | 12 signals; total mean difference norm 3; independent unit-variance residuals | Whether the improved proposer still contributes beyond PCA with the same native readout |
| Covariance-matched single Gaussian | Same mean and covariance as the preceding mixture, but one Gaussian population | Whether covariance structure alone produces misleadingly credible splits |
| Independent Gaussian | 200 independent normal coordinates | Basic absence-of-signal control |
| Mean separation with correlated substitute measurements | Twelve informative measurement groups with prespecified noisy synonyms; total columns 200 | Whether prediction and group-level explanations reproduce even when individual feature choices differ |
| Strongly correlated single Gaussian | One shared continuous Gaussian factor plus residual noise | Whether stable, compact, readable partitions are incorrectly interpreted as multiple populations |
| Grouped-moons sentinel | Existing noisy two-coordinate groups, 10 signals among 50 features | Preserve a visible nonconvex failure check; do not claim that all ten variables are necessary |

An exact covariance-matched Gaussian construction is available. For the mean-mixture generator `X = Y * mu + epsilon`, with balanced `Y in {-1,+1}`, `||2*mu||=3`, and `epsilon ~ N(0,I)`, its covariance is `I + mu*mu.T`. The null can use `X = g*mu + epsilon`, where `g ~ N(0,1)`. Both use the same support and covariance; only the former has the two generated mean populations. Reference columns in the null are covariance-generating measurements, not true cluster markers.

For synonyms, draw a fixed latent measurement and several noisy observations of it rather than copying columns exactly. Save the equivalence groups in the population specification. Report both strict feature recovery and group recovery, without treating every substitute as uniquely necessary. A single small supplement can later vary redundancy strength; do not introduce that grid into the first run.

## 4. Automatic size means certification among fixed native models

For each proposer and discovery block, fit the full 16-feature centroid model. Rank its selected features by absolute centroid contrast in discovery-standardized units, `|c1_j-c0_j|`, with deterministic feature-index ties. Do not rank original-unit coefficients directly, because changing a measurement's units would change that ordering.

Before opening C, fit a native centroid model separately for every ordered prefix of lengths 1 through 15 using the same discovery block. Length 16 reuses the exact full model. Fix each reduced model's label orientation by agreement with the full model on discovery rows. Freeze preprocessing, prefixes, centers, random seeds, and orientation. No refit occurs after C selects a prefix. A/B models remain separate; do not refit their selected supports on A+B and transfer the old certificate to the new rules.

For candidate `h_k` and its own frozen teacher `h_full`, count disagreement on C. The target is

`P_X[h_k(X) != h_full(X)] <= .05`.

Use the existing one-sided Clopper–Pearson bound, with family size

`M = 2 proposers * 2 independent discovery fits * 16 planned prefixes = 64`.

Use alpha .05/64 for each bound and choose the shortest prefix whose upper bound is at most .05. Count invalid, duplicate, and unreturned planned candidates in this fixed family rather than reducing the multiplicity after seeing their results. If new assignment families are allowed to participate in the selection, enlarge M before certification. This is a per-replicate simultaneous fidelity statement conditional on discovery and iid certification rows, not a simultaneous guarantee over every future dataset or an assertion of biological correctness.

At n=800, zero errors gives an upper bound .008903; at most 21 errors pass the 5% target. At n=200, the corresponding upper bound is .035141 and at most one error passes. These calculations explain the proposed certification sample size. They do not promise that a particular prefix will pass. A finite test sample can exceed 5% disagreement even when population disagreement satisfies the bound.

Also report the shortest prefix passing the empirical 5% threshold on exactly the same ladder. That is a descriptive comparator, not the recommended guarantee-bearing selector.

**Important denominator:** the exact full teacher has zero disagreement, so a valid length-16 fallback will pass with this sample size. “A certified panel was returned” is consequently a weak success criterion. Report the complete size–coverage curve for k=1,...,16, shortest certified size, reduction from 16, coverage at sizes <=8 and <=12, and retention of the full 16-feature rule. Eight and twelve are reporting conventions, not evidence that humans find those sizes readable. Twelve is a reasonable first practical target here because the generator deliberately distributes signal over twelve measurements; failure to compress to eight is not automatically a methodological failure.

## 5. Exactness, readability, and stability are distinct metrics

The centroid rule is exactly expressible in original units. With `z_j=(imputed x_j-mean_j)/scale_j`, assign group 1 when

`2 * sum_j (c1_j-c0_j) * z_j > ||c1||^2 - ||c0||^2`.

Save full-precision coefficients, intercept, discovery imputation, and tie behavior. A display rounded to two decimal places is not the exact implementation; either show it as an approximation or replay its rounded predictions and report the rounding error. The rule explains its own centroid model, not the separate graph model. Sixteen weighted terms may be exact but still cumbersome for a domain expert.

Primary result table, retaining every planned fit:

- **Utility:** full and chosen-prefix test ARI against synthetic labels; paired optimized-minus-PCA ARI with the readout held fixed. Report fit failures and coverage beside conditional means.
- **Panel quality:** precision, recall, nuisance count, selected size, and synonym-group recovery. A correct reference feature is not automatically essential.
- **Rediscovery:** A/B panel Jaccard, synonym-group Jaccard, and A/B prediction ARI on the same T. Partition ARI is invariant to label swapping. If pointwise agreement is displayed, fix A/B orientation using C first and do not quietly optimize it on T.
- **Fidelity:** C errors and upper bound, T disagreement with the own full teacher, and certification/size coverage. Keep cases lacking both A and B reduced rules in the denominator of paired-availability summaries.
- **Practical readability:** number of measured variables, number of arithmetic terms, rule family, missing-value policy, and a prespecified expert readability rubric later on real data.
- **Resources:** all proposal, full-model, prefix-fit, and certification costs; report PCA and optimized costs separately.

No single combined z-score replaces this table. In particular, a faithful but incorrect teacher must not score as a successful discovery. Alongside conditional ARI, report failure-aware counts such as “number of planned fits returning a <=12-feature certified rule with test ARI >=.65.” The .65 threshold is a proposed engineering checkpoint for this mean-shift benchmark, not a universal clustering standard; freeze it before running.

## 6. Split acceptance is a separate next stage

Stage 1 can establish a reproducible useful **candidate partition**. It cannot by itself authorize a recursive split on an unlabeled population. Independent and correlated Gaussian controls must remain visible even when their rules are perfectly stable and compressible.

A scoped acceptance prototype can ask whether the selected measurements are consistent with one multivariate Gaussian. A concrete option is a split likelihood-ratio test: fit a proper alternative density q on discovery, then on a fresh acceptance block G calculate `E = product_i q(x_i) / sup_{mu,Sigma} product_i phi(x_i;mu,Sigma)`. Under the Gaussian null, the denominator dominates the true likelihood, giving `E[E] <= 1`; a multiplicity-adjusted threshold follows by Markov's inequality. The fitted alternative may be a regularized two-Gaussian density tied to the native discovery partition. This is an application of the established split-likelihood approach, not a novel test. [Wasserman, Ramdas and Balakrishnan, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7382245/).

Do this only as a subsequent scoped module with its own independent G, predeclared candidate family, and finite-density/covariance checks. If four already-selected A/B/proposer rules reach G, adjust for all four; if a shape-family chooser or every prefix can win there, count that larger family instead. Certification C and acceptance G have different purposes. Gaussian covariance must be unrestricted enough to include the matched and strongly correlated controls. Ordinary Gaussian MLE needs sufficient independent rows and nonsingular panel covariance; numerical regularization of the denominator is not automatically a valid substitute for its likelihood supremum.

The score can be conservative, particularly when estimating a flexible Gaussian denominator in a 16-dimensional panel. Lack of rejection is insufficient split evidence under this test, not proof of one population. Check power first on the frozen mean-shift model and its covariance-matched null. If power is inadequate, a prespecified one-dimensional native-score version is a possible next refinement because a frozen linear score of a Gaussian is Gaussian; its claim concerns that score. Do not try both and keep the favorable answer without including both tests in the family. The auxiliary density must be normalized and discovery-fitted; a graph eigengap, a silhouette, or an unnormalized fitness cannot replace its numerator.

This test rejects a stated Gaussian model. It does **not** distinguish every multimodal distribution from every unimodal heavy-tailed or curved distribution. Add a one-population heavy-tailed control before interpreting its decisions broadly. The older SigClust literature also uses an explicit Gaussian cluster definition rather than a universal definition of cluster existence. [Liu et al., 2008](https://doi.org/10.1198/016214508000000454).

Do not label a significant Gaussian departure as a proven biological subtype. Operational node acceptance should display the evidence scope and also require a valid, adequately populated native split and the chosen readability policy. Fidelity failure, insufficient data, and lack of evidence against the one-population reference are distinct abstention reasons.

## 7. Graduation and fallback decisions

Prespecify these as engineering decisions, not posthoc significance tests:

1. **Advance the proposer** if the paired centroid comparison shows a practically useful optimized-panel gain on fresh mean-shift populations, rather than a gain confined to one inspected seed. A suggested target is mean paired ARI improvement >=.03 and positive replicate-averaged differences in at least 8/10 replicates. Also inspect nuisance retention and runtime. If it fails, keep frozen PCA as the mean-separation proposer while revising the optimizer; the native-rule framework is still usable.
2. **Advance automatic panel sizing** if it often removes nuisance variables while maintaining certified fidelity. Report <=8 and <=12 coverage, not just returned-panel averages. If the selected rules remain large, retain the full exact rule and label the compactness objective unmet; do not relax the fidelity threshold after viewing T.
3. **Advance a depth-two tree only after a scoped node-acceptance prototype is usable.** Freeze the candidate tree on discovery, then certify frozen node rules on held-out observations routed through frozen ancestors. Enlarge the family for all planned node/rule candidates, count the smaller per-node sample sizes, and stop a node when data are inadequate. If training or topology changes after certification, recertify.
4. **Keep nonlinear work explicit.** The moons sentinel cannot be rescued by relabeling centroid success as nonlinear clustering. The next shape branch should supply a native nonlinear rule with an interpretable form, for example a sparse shared-scale/radial score for shells, and pass its own supplied-panel ability and autonomous-discovery controls. This is distinct from rerunning the failed squared sparse-k-means baseline. The framework can share feature-panel, certification, and interface machinery without claiming a universal fitness.

There is a further hierarchy-specific obstacle: conditioning a single Gaussian population on an ancestor's split generally produces a truncated Gaussian. Applying an ordinary untruncated Gaussian null independently at every child can therefore produce misleading recursive rejections, even with fresh rows. Depth-two acceptance needs a route-aware null or an explicitly narrower exploratory interpretation. A root-level Gaussian certificate must not silently become a whole-tree cluster-existence theorem.

## 8. Biomedical evaluation and the interactive panel chooser

After the single-node protocol is frozen, use one real-data contrast with a prespecified feature universe, sampling unit, annotation target, and domain-review form. A small real case study should test whether the rule can be read and challenged by a domain expert, not merely whether familiar markers appear in a list.

The cached METABRIC matrix is PAM50-enriched and its extra features were variance-filtered across patients before the newer split. PAM50 overlap is contextual plausibility in that selected universe, not independent validation or a unique correct panel. New patient splits cannot undo that earlier feature-universe construction. A stronger study requires a train-only or externally specified universe and, eventually, an independent cohort. Select a small set of external facts or unused annotations before examining the new panels; retain contradictory findings and account for multiple tests. Marker sign, scale, correlated alternatives, and assignment behavior matter in addition to gene names.

For Levine, random held-out cells do not constitute donor replication. Use donor/specimen-separated discovery and evaluation when sufficient donors exist, with preprocessing fitted only on discovery donors. If the available cache cannot support that split, report within-specimen reproducibility and defer the independent-biological-replication claim. Known gating markers can validate recovery of an existing contrast but may partly define its reference labels.

The interface should offer a small **frozen shortlist** with each panel's exact native rule, certified fidelity/size, A/B prediction agreement, evidence scope, and abstention reason. Group interchangeable correlated measurements when justified, while preserving the actual chosen columns and coefficients. A domain expert may choose a biologically preferable candidate from this shortlist. If every displayed candidate was included in simultaneous certification, that selection retains the stated fidelity coverage to its own teacher. It does not establish its biological validity. Editing panels, fitting new rules, or choosing new families after seeing held-out results creates a new exploratory candidate requiring new certification.

## Claims this experiment can and cannot support

It can show that a fixed proposal procedure improves useful feature recovery over its PCA initializer under a declared mean-separation population, that independent samples rediscover related assignments, and that an automatically chosen original-feature rule preserves its own full teacher within a specified error bound.

It cannot establish SOTA performance, method novelty, causal biomarkers, universal cluster existence, essential higher-order nonlinear panels, or independent biomedical validation. It also cannot turn the successful centroid branch into evidence that shells or curved manifolds are solved. Those remain concrete next branches of the same interpretable-node design.
