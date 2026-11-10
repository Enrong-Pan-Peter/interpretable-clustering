# Ranking followup: correcting panel size does not fix the main failure

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validation of saved output
- Origin Date: 2026-09-16 (UTC run date; the local run began on September 15)
- Verification Status: ANALYZED; ranking arithmetic, replay and source hashes checked; clustering fits not rerun
- Version Label: ranking_assessment_v1
- Source: `results/research_ranking_followup/20260916T025613_491524Z`
- Reproduction: `.venv-research/Scripts/python.exe scripts/analyze_research_ranking_followup.py`

**Size-related score trends are real, but removing them is insufficient.** Size centering helps some mean-shift candidate banks. Neither tested size correction improves the aggregate METABRIC ranking or development-test performance. The next investigation should examine the proposed model/partition itself, transfer reliability and compression; another scalar normalization should not be the main research direction.

## What was verified

The saved manifest reports all six intended cases complete in **45.47 seconds**: `mean_shift_seed0/1/2` and `metabric_seed0/1/2`. All recorded followup hashes and all six source-pilot hash sets match the current files. Data protocols match the pilot exactly. The read-only audit independently reproduced:

- all **30** pilot-baseline selections and their training ARI, transferred test ARI and compression fidelity;
- all **120** policy winners and selected scalar values;
- best-visited training ARI and selection regret against **2,366** saved candidate records;
- calibration from **1,152** new reference records, with every observed size supported.

The four policies are: original pilot global calibration; a larger new global reference bank; size-specific centering with shared within-size residual scales; and size-specific centering and scaling. New reference panels never enter the candidate banks. Labels enter reporting after selection. The experiment isolates re-ranking existing candidates, **not how search would behave if trained on the new objectives**. The `size_centered` policy also changes common component scales from total variation to pooled within-size residual variation; its comparison with `new_global` is therefore not a means-only intervention. Comparing the two size policies isolates common versus size-specific scales while retaining the same size-specific means.

These are development reanalyses of already inspected splits. Their “test” numbers are useful diagnostics but are **not untouched confirmation** for the newly designed correction. Three resamplings of the same real cohort are not three independent biological replications. No p-values or universal superiority claim are warranted.

## Overall effects

Each row below averages 15 method/seed results within one dataset. These descriptive averages mix dependent candidate banks; they should be read alongside the per-method tables.

| Dataset | Ranking policy | Mean training selection regret ↓ | Mean development-test ARI ↑ | Mean selected size |
|---|---|---:|---:|---:|
| Mean shift | Pilot global | 0.1426 | 0.3923 | 7.13 |
| Mean shift | New global | 0.1426 | 0.3923 | 7.13 |
| Mean shift | Size centered | **0.0868** | **0.4401** | 6.47 |
| Mean shift | Size standardized | 0.1441 | 0.4057 | 5.87 |
| METABRIC | Pilot global | **0.2606** | **0.1274** | 6.00 |
| METABRIC | New global | 0.2786 | 0.0966 | 6.07 |
| METABRIC | Size centered | 0.2806 | 0.0926 | 6.53 |
| METABRIC | Size standardized | 0.2798 | 0.1064 | 3.87 |

“Selection regret” is the retrospectively best visited training ARI minus the selected training ARI. It uses external labels diagnostically, after the decision. The best visited panel is not an achievable label-free selector, and its held-out utility has not been established merely by this number.

Paired counts relative to the original pilot policy:

| Scope | Policy | Regret improved / worse / tied | Development-test ARI improved / worse / tied |
|---|---|---|---|
| Mean shift, 15 banks | New global | 0 / 0 / 15 | 0 / 0 / 15 |
| Mean shift, 15 banks | Size centered | 3 / 2 / 10 | 3 / 2 / 10 |
| Mean shift, 15 banks | Size standardized | 5 / 3 / 7 | 6 / 2 / 7 |
| METABRIC, 15 banks | New global | 0 / 2 / 13 | 0 / 2 / 13 |
| METABRIC, 15 banks | Size centered | 4 / 2 / 9 | **0 / 6 / 9** |
| METABRIC, 15 banks | Size standardized | 4 / 6 / 5 | 3 / 7 / 5 |
| Both datasets, 30 banks | New global | 0 / 2 / 28 | 0 / 2 / 28 |
| Both datasets, 30 banks | Size centered | 7 / 4 / 19 | 3 / 8 / 19 |
| Both datasets, 30 banks | Size standardized | 9 / 9 / 12 | 9 / 9 / 12 |

Ties use an absolute tolerance of 1e-9. Counts are not independent Bernoulli trials. In particular, “four METABRIC training regrets improve” does not imply improvement on new observations: every changed centered winner has lower development-test ARI here.

## Effects by proposal method

Mean **development-test ARI** over seeds 0, 1 and 2:

| Dataset | Proposal method | Pilot global | New global | Size centered | Size standardized |
|---|---|---:|---:|---:|---:|
| Mean shift | Random | 0.1520 | 0.1520 | 0.3385 | 0.2624 |
| Mean shift | Forward | 0.1619 | 0.1619 | 0.1619 | 0.0515 |
| Mean shift | Evolutionary baseline | 0.2680 | 0.2680 | 0.3394 | 0.2535 |
| Mean shift | Smooth graph | 0.7117 | 0.7117 | 0.6926 | 0.7207 |
| Mean shift | Sparse k-means | 0.6681 | 0.6681 | 0.6681 | 0.7403 |
| METABRIC | Random | 0.0193 | 0.0193 | 0.0166 | 0.0222 |
| METABRIC | Forward | -0.0021 | -0.0021 | -0.0041 | -0.0070 |
| METABRIC | Evolutionary baseline | 0.1454 | -0.0085 | 0.0422 | 0.0627 |
| METABRIC | Smooth graph | 0.1184 | 0.1184 | 0.1184 | 0.1294 |
| METABRIC | Sparse k-means | **0.3559** | **0.3559** | 0.2900 | 0.3244 |

Mean **training selection regret** for those same cells:

| Dataset | Proposal method | Pilot global | New global | Size centered | Size standardized |
|---|---|---:|---:|---:|---:|
| Mean shift | Random | 0.2895 | 0.2895 | 0.0770 | 0.1672 |
| Mean shift | Forward | 0.2386 | 0.2386 | 0.2386 | 0.3399 |
| Mean shift | Evolutionary baseline | 0.1128 | 0.1128 | 0.0414 | 0.1322 |
| Mean shift | Smooth graph | 0.0241 | 0.0241 | 0.0289 | 0.0384 |
| Mean shift | Sparse k-means | 0.0480 | 0.0480 | 0.0480 | 0.0431 |
| METABRIC | Random | 0.4298 | 0.4298 | 0.4214 | 0.4253 |
| METABRIC | Forward | 0.2808 | 0.2808 | 0.2742 | 0.2882 |
| METABRIC | Evolutionary baseline | 0.3236 | 0.4140 | 0.3156 | 0.3491 |
| METABRIC | Smooth graph | 0.2421 | 0.2421 | 0.2421 | 0.2345 |
| METABRIC | Sparse k-means | **0.0264** | **0.0264** | 0.1496 | 0.1018 |

The larger global bank changes only two of 30 winners, both METABRIC evolutionary cases, and both changes worsen training and development-test ARI. Thus insufficient reference-bank size is not supported as the dominant explanation for the failures. This single bank draw does not establish calibration robustness, however.

The dramatic mean-shift centering gain is concentrated: random seed 1 rises from test ARI **0.0234 to 0.3546**, and evolutionary seed 1 from **0.2272 to 0.4624**. A useful existing panel can sometimes be rescued. The harm is also concrete: in `metabric_seed0`, sparse k-means changes from a five-feature panel with test ARI **0.3157** to an eight-feature centered winner with **0.1180**; standardization gives **0.2619**. In `metabric_seed1`, standardization improves the smooth-graph failure from **-0.0078 to 0.2111**, but that is not a general cure across methods or seeds.

The strongest existing comparator on METABRIC remains sparse k-means with original/global ranking. These results do not yet justify calling its panels novel or biologically established. They do support keeping it as a serious baseline rather than assuming an EA or differentiable graph must be superior.

## Next decisive checks

1. **Preserve the proposal's model, then measure what rounding discards.** On the same data and feature prefixes, compare the learned weighted partition/assignment with the current unweighted spectral re-split. A mean-shift model can propose useful features and still lose its partition when the evaluator replaces its geometry. This comparison identifies that loss without another normalization sweep. Keep all annotations outside fitting and model selection.
2. **Separate reliable assignment from reliable rediscovery.** Train independently on disjoint or grouped samples, transfer both rules to common evaluation rows, and compare their partitions, sizes and non-collapse. Reproduction of a fixed chosen rule and rediscovery of a partition are different targets. Include external ARI only as an additional retrospective outcome.
3. **Audit compression over fresh resampling, not just its accepted validation score.** Compare the current greedy deletion procedure with repeated split or nested validation and a conservative preservation threshold. Report achieved held-out fidelity and feature substitutions. Fewer selected features after size standardization are not evidence that those retained are sufficient; an easy but wrong partition may also be compact.
4. **Diagnose geometry before feature search on shells.** Compare a radial/quadratic model with current spectral clustering on both all features and a clearly marked oracle panel. Then test whether the model can discover the panel without access to its identity. This separates representational ability, proposal discovery and ranking.
5. **Run the complete procedure on negative controls.** Include independent and correlated unimodal populations, anisotropic or curved single populations, and nuisance/batch structure. Study candidate-evidence distributions as search budget increases. A false-split rate is meaningful only after an explicit acceptance rule is defined; the current methods always produce candidates.

These checks can be staged in a single local suite with early summaries: original-space model retention first, then replication/compression, then broader geometry and negative controls. Keep separate evidence for each obstacle, and reserve new datasets/splits for confirmation after development decisions. Reusing the current followup to select a new winner and calling its displayed test ARI independent would overstate the evidence.

## Statistical limits

Neither reference normalization nor dependence permutation tests decide whether clusters exist. A stable optimizer can repeatedly select an arbitrary partition of a single population. A high-fidelity rule can preserve that arbitrary partition. A sparse biological panel requires evidence about the particular scientific target and plausible alternative explanations, not just a large standardized score.

The new analysis script is read-only and reports all four policies, including deteriorations. It does not rerun fits, correct multiple comparisons, or estimate population-level effect uncertainty. Statistical fallacy coverage (11/11): aggregation/Simpson risk is addressed by dataset/method tables; ecological inference is not claimed; annotation filtering and possible selection/Berkson effects remain disclosed; no causal conditioning or collider model is asserted; no predictive-value/base-rate claim is made; selecting extreme scores can regress under reuse/holdout; all planned cases are present; look-elsewhere and forking paths remain development risks; no causal or reverse-causal interpretation is claimed.
