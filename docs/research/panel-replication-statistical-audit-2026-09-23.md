# Statistical audit of native panel replication

## Material Passport

- Origin: independent statistical review of the panel-replication experiment
- Origin Date: 2026-09-23
- Mode: analysis of saved outputs; no fits or experiment reruns
- Verification Status: ANALYZED
- Version Label: panel_replication_statistical_audit_v1
- Inputs: `results/research_panel_replication/20260921T202232_578177Z/summary.json`, case-level `data_protocol.json`, and the experiment/selection code for interpreting recorded quantities
- New calculations: matched-policy descriptive summaries, unavailable-panel counts, METABRIC sample overlaps, and binomial probabilities/thresholds
- Scope: compression, denominator effects, null controls, and METABRIC independent rediscovery. Mean-shift scaling and source/prediction integrity have separate reviewers.

## Conclusion

The bounded selector shows a useful improvement in fidelity to the already fitted model, at the cost of larger panels and explicit abstention. Among the same 42 learners for which it returns a panel, average test disagreement falls from 3.92% under empirical selection to 0.95% under bounded selection; median panel size increases from four to eight. The remaining 12 of 54 learners have no bounded panel within the 16-feature ladder. Missing outputs must remain part of the result.

This is progress in faithful compression, not evidence that the returned panels describe real clusters. Independent Gaussian noise yields compact, faithful panels with no independent partition replication. Correlated single-Gaussian data yield both faithful compression and substantial independent partition agreement. METABRIC full models reproduce reasonably well within the cached cohort, but **none of its three runs produces both bounded panels**, so this experiment has not demonstrated independent rediscovery of a bounded METABRIC panel.

## Scope and targets

There are 27 cases and 54 native sparse-two-means learners. Each case uses 800 observations divided into discovery A, discovery B, validation, and test blocks of 200 each. Each learner has its own discovery-fitted preprocessing, full native classifier, and fixed prefix ladder of at most 16 features. Both policies select from exactly those frozen ladders; neither refits a selected prefix. Their error target is disagreement with that learner's own full model, not external labels.

The empirical selector requires observed validation error at most .05. The bounded selector requires a one-sided Clopper–Pearson upper bound at most .05, using alpha=.05/32 per candidate to cover the two 16-prefix ladders within the case. All recorded prefix-validity flags are true, so unavailable bounded panels are caused by the bound threshold within the cap, not collapsed-group rejection.

The full model's positive-weight support is not capped at 16. It ranges from 20 to 200 features in this suite. Every selected prefix is smaller than its own full positive-weight support. Thus panel-size reduction is real, while raw full-support Jaccard can be uninformative when both models retain nearly all features.

## Compression: retain denominators and match policies

Test exceedance below means observed test disagreement greater than 5%. It is a descriptive finite-test event, not proof that a population bound failed.

| Case family | Learners | Empirical available | Empirical test exceedances | Bounded available | Bounded test exceedances | Median empirical / bounded size among each policy's outputs |
|---|---:|---:|---:|---:|---:|---:|
| Mean shift | 36 | 36 | 8 / 36 | 32 | 0 / 32 | 4 / 8 |
| METABRIC | 6 | 6 | 2 / 6 | 3 | 0 / 3 | 3.5 / 10 |
| Independent Gaussian null | 6 | 6 | 0 / 6 | 3 | 0 / 3 | 1 / 2 |
| Correlated Gaussian null | 6 | 6 | 3 / 6 | 4 | 0 / 4 | 5 / 12.5 |
| All cases | 54 | 54 | 13 / 54 | 42 | 0 / 42 | 4 / 8 |

The matched comparison uses the same 42 learners with a bounded output:

| Quantity | Empirical | Bounded |
|---|---:|---:|
| Mean test disagreement | 3.9167% | 0.9524% |
| Test changes, summed across 42 panels × 200 rows | 329 | 80 |
| Test exceedances | 12 / 42 | 0 / 42 |
| Mean panel size | 4.1667 | 7.7381 |
| Median panel size | 4 | 8 |

Bounded selection gives lower test disagreement in 37 matched learners, equal disagreement in four, and higher disagreement in one. It selects a larger panel in 38 and the same panel in four. This comparison supports a fidelity/size tradeoff; it does not isolate a benefit of confidence machinery from the direct benefit of retaining more features.

The 12 learners with no bounded output have mean empirical test disagreement 3.5417%, with only one test exceedance. Therefore the favorable matched comparison is not simply explained by discarding empirically poor test cases. Nevertheless, it would be wrong to write “bounded compression succeeds in all 54 cases” or to substitute a test-favored panel for a missing result.

Independent A/B comparison has a stricter availability requirement: both outputs must exist. Bounded pairs are available in only 16 of 27 cases: 14/18 mean-shift, 0/3 METABRIC, 0/3 independent-null, and 2/3 correlated-null. Comparing average bounded replication across these 16 with average empirical replication across all 27 confounds policy and case availability. On the same 16 cases, mean test agreement ARI is .5157 for full models, .3894 for empirical prefixes, and .5098 for bounded prefixes. This is consistent with preservation of the full model's replication behavior, not an improvement over full-model rediscovery. These pooled means mix different regimes and are descriptive only.

## What missing bounded outputs mean

At n=200 and 32 candidates, zero errors gives an upper bound .031791; one gives .042852; two gives .052320. The bounded selector therefore permits only zero or one observed error, although the empirical rule permits ten.

Every missing case below has a valid 16-feature prefix. The final two columns evaluate that *fixed endpoint*, not a newly selected best test panel:

| Case | Seed / learner | Minimum errors anywhere in ladder | 16-feature validation errors / 200 | 16-feature test errors / 200 |
|---|---|---:|---:|---:|
| Mean shift, p=200, s=8 | 6 / A | 4 | 6 | 2 |
| Mean shift, p=200, s=12 | 6 / A | 2 | 3 | 2 |
| METABRIC | 6 / B | 2 | 2 | 3 |
| Independent null | 6 / A | 3 | 5 | 3 |
| METABRIC | 7 / A | 2 | 2 | 0 |
| Independent null | 7 / B | 5 | 6 | 1 |
| Mean shift, p=200, s=5 | 8 / A | 2 | 2 | 2 |
| Mean shift, p=200, s=12 | 8 / A | 2 | 2 | 2 |
| METABRIC | 8 / B | 3 | 3 | 0 |
| Independent null | 8 / A | 2 | 2 | 1 |
| Correlated null | 8 / A | 4 | 4 | 3 |
| Correlated null | 8 / B | 4 | 4 | 2 |

All these fixed endpoint test errors are 0–1.5%. The immediate explanation for abstention is insufficient validation evidence at this simultaneous threshold, not an observed absence of faithful candidates. This observation motivates a validation-size ablation; it must not be used to rescue the original selections using test outcomes. It also does not prove that each candidate's true error is below 5%.

## Population bounds are not test-sample ceilings

The Clopper–Pearson construction bounds a binomial probability; the established exact method is documented in the [SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html). The implementation uses its one-sided form. Conditional on frozen training fits and iid validation observations, simultaneous coverage over M fixed candidates follows from the union bound: each upper-bound failure has probability at most alpha/M, so any failure in that family has probability at most alpha. Dependence between candidate predictions does not invalidate that argument.

The bound concerns population disagreement with the fixed full teacher. It does not promise that every future test sample has empirical error below the upper bound. There is an actual example: METABRIC seed 8 learner A has validation upper bound .031791 but test error .04. That is not itself a statistical contradiction. For scale, if a fixed classifier's true disagreement probability is exactly .05, a fresh 200-row test sample exceeds 5% error with probability `P[Binomial(200,.05)>10] = .416933`. This number was calculated directly from the binomial distribution, not inferred from the experiment.

Conversely, zero observed exceedances among the 42 bounded outputs does not prove that all population risks are below .05, or that the assumptions hold. The selected outputs are dependent within cases, and several conditions share seeds and generated structure. Treating the 42 outcomes as independent trials to obtain a success-rate confidence interval would overstate precision.

The guarantee is within each counted case, not across all 27 cases or future tuning. It concerns the chance that the selection procedure returns a candidate whose population error exceeds the threshold; it is not a posterior statement that 95% of the returned panels are true clusters. Conditioning only on favorable returned outputs can change the interpretation further. Validation-based label alignment is used only for separate A/B reporting, and must remain outside the frozen prefix-vs-teacher error calculation.

## Null controls expose two different failure modes

All null external ARIs are correctly unavailable because the generator has a single population; forced two-way partitions cannot establish two true classes.

| Null / seed | Full A/B test ARI | Empirical A/B test ARI | Bounded A/B test ARI | Full feature Jaccard | Empirical / bounded Jaccard |
|---|---:|---:|---:|---:|---:|
| Independent / 6 | .0050 | .0050 | unavailable | 1.0000 | 0 / unavailable |
| Independent / 7 | .0014 | -.0014 | unavailable | 1.0000 | 0 / unavailable |
| Independent / 8 | .0049 | -.0033 | unavailable | 1.0000 | 0 / unavailable |
| Correlated / 6 | .8090 | .5908 | .8272 | .0357 | 0 / 0 |
| Correlated / 7 | .7557 | .4874 | .6873 | 0 | 0 / 0 |
| Correlated / 8 | .7557 | .7211 | unavailable | .0345 | 0 / unavailable |

On independent Gaussian noise, the empirical selector returns one feature for all six learners, with 2.5–5% test disagreement from the full teacher. Three learners even receive a bounded 1–3-feature panel. Yet the two independently trained models have essentially zero partition agreement. This shows that a compact faithful explanation of an arbitrary split is possible. Full support Jaccard equals one only because both full supports include all 200 columns; it is not meaningful feature rediscovery.

On correlated Gaussian noise, different panels can encode the same continuous common variation. Independent full-model test agreement ARIs reach .756–.809, and bounded prefixes in seeds 6 and 7 have ARIs .827 and .687 despite zero selected-feature overlap. Thus requiring partition stability as well as fidelity would still not establish cluster existence. Conversely, zero feature Jaccard need not mean that the two rules describe unrelated geometry when variables are substitutes.

These controls distinguish rule fidelity, feature identity, geometric reproducibility, and cluster existence. No single one replaces the others. A future cluster-acceptance rule needs an explicit notion of a meaningful split and corresponding null model; this suite has deliberately not implemented such a rule.

## METABRIC: a reproducible full model, incomplete compact rediscovery

| Seed / learner | Full support / external test ARI | Empirical size / external ARI / teacher error | Bounded size / external ARI / teacher error |
|---|---|---|---|
| 6 / A | 20 / .4872 | 2 / .4186 / 8.5% | 10 / .4059 / 4% |
| 6 / B | 20 / .4732 | 3 / .4593 / 4.5% | unavailable |
| 7 / A | 20 / .5453 | 5 / .5306 / 3.5% | unavailable |
| 7 / B | 20 / .6707 | 6 / .5603 / 4.5% | 15 / .6544 / 1.5% |
| 8 / A | 20 / .4066 | 2 / .3939 / 5.5% | 8 / .4066 / 4% |
| 8 / B | 21 / .3686 | 4 / .3810 / 4.5% | unavailable |

The full independent pairs have test agreement ARIs .9406, .7733, and .8272, with feature Jaccards 1, 1, and .9524. Their empirical prefixes reduce pair ARI to .7209 and .6874 in seeds 6 and 8, while seed 7 increases to .8090. This is promising evidence of a reproducible partition within this development population, with incomplete preservation under aggressive shortening.

The empirical panels contain CEP55 in five of six fits, PTTG1 in five, and MELK and UBE2C in four each. All 22 empirical feature occurrences are PAM50-reference members. Bounded panels have reference overlap 9/10, 13/15, and 7/8. These are contextual matches, not proof of necessity, unique recovery, or independent biological validation; the available feature universe is itself PAM50 enriched.

Each A/B training pair is disjoint within its run, but the three 800-patient samples come from the same 1,175-patient contrast. Between seeds 6/7, 6/8, and 7/8, they share 551, 548, and 547 patients; their 200-patient test sets share 34, 27, and 37 patients. Repeated seeds therefore are not three independent cohorts. The cached matrix also used an all-patient variance filter before this experiment. Discovery-fitted scaling alone cannot undo that development-data limitation.

## Focused next ablation

Before changing the fidelity threshold or introducing another search optimizer, isolate the cost of certifying a fixed ladder: retain the same trained model, feature order, coefficients, and cap, and compare **prespecified fresh validation sizes 200 versus 800**, using a separate large test draw for the synthetic regimes. No refitting, feature substitutions, new stopping rule, or test-guided choice should accompany this ablation. Repeat over fresh discovery seeds and retain all abstentions.

For alpha=.05 and the same 32-candidate family, n=200 permits at most 1 validation error; n=400 permits 7; n=800 permits 22. More observations allow a bound to certify error rates nearer the intended 5% target without relaxing that target. Use independent fresh observations for validation and evaluation, and do not keep extending validation until a preferred panel passes. If choosing across multiple validation schedules rather than reporting a fixed experimental comparison, account for that additional selection.

Report availability, selected size, population-risk approximation on the large independent synthetic test sample, external performance, and full-versus-prefix replication separately. Include a fixed 16-feature endpoint as a descriptive comparator to distinguish selector conservatism from poor prefix fidelity. The current results predict that more validation may reduce abstentions, but they do not establish the outcome in advance.

This ablation addresses certification power, not the quality of the original discovered partition or the correlated-null problem. Those remain separate targets. An eventual method may combine discovery, interpretable native rules, compression, and split verification, but neither the established sparse-k-means model nor adding a standard confidence bound alone supports a novelty claim.

## Interpretation checklist

ARS statistical fallacies reviewed: 11/11 categories. Stratified and matched summaries address aggregation/Simpson concerns; learner-level results are not converted into cohort-level claims (ecological concern). The prefiltered real-data contrast and enriched feature universe limit generalization (selection/Berkson concern). No causal adjustment or causal-direction claim is made (collider, causation, reverse-causality concerns). Null controls prevent equating apparent accuracy/stability with meaningful populations (base-rate concern). Full-model baselines are retained, avoiding claims of improvement based only on extreme selected outcomes (regression-to-mean concern). All missing panels remain explicit (survivorship concern). Multiplicity is scoped to fixed within-case candidate families, and new ablations require fresh data with fixed rules (look-elsewhere and forking-path concerns). This is a descriptive audit, not a new confirmatory biological study.
