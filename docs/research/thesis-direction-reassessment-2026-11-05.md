# Thesis direction reassessment and one-week decision plan

## Material Passport

- Origin skill: academic-research-suite, research question refinement.
- Date: 2026-11-05; deadline supplied by the researcher: settle the revised proposal within one week.
- Version: direction_reassessment_v1.
- Evidence status: existing local results reviewed; targeted primary-source literature scan and two completed parallel reviews. This is not a systematic review or a verified novelty claim.
- Execution status: no replacement method implemented or trained in this reassessment. Local activity-data subject identifiers were checked read-only.
- Terminology: feature sets. Historical filenames retain earlier terminology.

## Decision

Pivot the main thesis away from a mandatory radial geometry and a universal clustering fitness. Preserve the frozen radial method, its tests and its failures as a completed research component. Do not launch another broad synthetic fitness or search sweep.

The preferred research direction is **clustering with compact original-feature sets that support assignment of new observations and generalize across independent subjects or samples**. Existing sparse or neural clustering models are starting points. A readable tree is optional; a genuinely executable small-feature assignment procedure is the immediate requirement.

This preserves the scientific aim of finding useful feature sets while relaxing the requirement that a particular geometry or a two/three-dimensional visualization must generate every cluster. Larger sets are allowed when measured quality requires them.

The fallback is explicitly weakly supervised feature selection and clustering if the desired grouping cannot be distinguished from other plausible groupings without domain information. It is a change in the information available to the method, not merely a stronger optimizer.

## What the completed work establishes

The [replication assessment](feature-set-replication-assessment-2026-10-31.md) supports the frozen method on clearly separated radial synthetic groups. Kernel-guided search recovered the planted features in 30/30 baseline searches with 24 available features. At 72 features, recovery fell to 12/18; only 3/9 underlying datasets succeeded under both search seeds. Under weaker separation, mean test ARI was 0.398 for both search methods, and even models supplied with the true features averaged 0.612. These are current-model results, not limits on what other models can recover.

Thus there are separate obstacles in candidate discovery, geometry/model fit, and finite-sample objective ranking. The evidence does not show that sparse clustering generally is a dead end. It also does not establish a real application or novelty for the radial method. Keeping radial geometry central requires a defensible application mechanism; finding a favorable score alone would be insufficient.

## Closest prior art and implications

| Primary source | Established capability relevant to the proposal | Consequence |
|---|---|---|
| [Sparse clustering, Witten and Tibshirani, 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2930825/) | Joint clustering and sparse feature weighting. | Small feature sets and avoiding exhaustive enumeration are established goals. |
| [DUFS, NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/0bc10d8a74dbafbf242e30433e83aa56-Abstract.html) | Differentiable feature gates and graph geometry computed on gated inputs. | Nonlinear feature selection need not enumerate subsets; graph quality still matters. |
| [GroupFS, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/download/39521/43482) | Joint latent feature-group discovery and selection. | Borrowing a kernel or adding feature groups is not enough novelty. Reproduce the actual method when using it as a comparator. |
| [IDC, ICML 2024](https://proceedings.mlr.press/v235/svirsky24a.html) | Neural tabular clustering with instance-level and cluster-level feature gates. | Deep clustering plus feature selection is already directly covered. |
| [Cluster Explanation via Polyhedral Descriptions, ICML 2023](https://proceedings.mlr.press/v202/lawless23a.html) and [SpEx, NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/20aa64395b2d43d2a32825660f566f6c-Abstract-Conference.html) | Sparse descriptions or explanation trees for supplied clusterings. | Learning a partition and subsequently explaining it is a strong baseline, not a novelty claim. |
| [SCMER, Nature Computational Science 2021](https://www.nature.com/articles/s43588-021-00070-7) and [PERSIST, Nature Communications 2023](https://www.nature.com/articles/s41467-023-37392-1) | Original-feature selection preserving nonlinear structure; neural selection including transfer across technologies. | Preserving geometry or testing transfer alone is also established. |
| [Consensus Guided Unsupervised Feature Selection, AAAI 2016](https://ojs.aaai.org/index.php/AAAI/article/view/10221) | Consensus cluster information guiding sparse feature selection. | Multiple reference clusterings plus feature selection is insufficient novelty by itself. |
| [SUWR, ICML 2024](https://proceedings.mlr.press/v235/oosterhuis24a.html) | Formal conditions against information leakage through local selections, and sequential selection using revealed values. | Honest feature acquisition is an existing foundation; direct distillation of cluster labels with this method is a required comparator if developing adaptive acquisition. |
| [Pairwise constrained sparse k-means, 2021](https://doi.org/10.1016/j.patrec.2020.11.015) and [active constrained clustering, SDM 2004](https://www.cs.utexas.edu/~ml/papers/semi-sdm-04.pdf) | Sparse clustering with pairwise constraints; actively selecting constraints. | Adding expert feedback or active queries is not automatically novel. |
| [DIVI, Computational Statistics, September 2026](https://link.springer.com/article/10.1007/s00180-026-01807-6) | Joint feature gates, mixture clustering and adaptive component growth. | Another close recent comparator for a joint gated-mixture proposal. Abstract and accessible technical material inspected; the subscription main text was not fully reviewed. |

This table is a novelty challenge, not a performance ranking. No universal gold standard has been established for the user's combined objective. The comparison must distinguish scientific cluster validity, prediction from a restricted feature set, and explanation quality.

## A concrete candidate research question

> Can we learn a compact original-feature assignment procedure that preserves reproducible cluster distinctions on new subjects, and recognizes when its feature budget cannot support a reliable assignment?

The potential contribution concerns the interaction between feature sufficiency, uncertainty in the discovered partition, and transfer. Each ingredient already has prior art. We must identify a repeatable failure of a strong existing baseline and improve it with a specific mechanism before claiming novelty.

An architectural distinction worth testing is that a model may highlight few features while using additional values to choose those features. In [IDC's method description](https://arxiv.org/html/2306.04785v2), local gates depend on the full input, and the cluster-specific global gate is selected using the predicted cluster. Therefore its gate count is not automatically the measurement cost of a standalone predictor. This is an inference about the input contract, not evidence that IDC's reported results are incorrect.

For our proposed output, either:

1. A fixed feature set is selected during training and the predictor accepts only those coordinates; or
2. A sequential procedure chooses the next coordinate using only values already observed, and all coordinates consulted along the path are counted.

Start with the first option. Sequential acquisition, abstention, cluster coarsening and interactive feedback should not all enter the first prototype.

Three outcomes remain separate: agreement with a frozen discovery model; reproducibility across training runs or subjects; and independent scientific validity. A model can score well on one and fail another. Sparse hidden representations also do not by themselves establish a small original-feature input requirement.

## Initial method hypothesis, subject to the feasibility result

Use an existing discovery model and a learned original-feature gate or selector. Compare an ordinary selector trained to reproduce one fitted partition against a selector trained to preserve distinctions that recur across training subjects and discovery refits. Use held-out training subjects to evaluate candidate feature sets. Do not treat inconsistent reference partitions as a single unquestioned ground truth.

The objective should expose a feature-budget/assignment-quality trade-off, rather than mix arbitrary cluster scores into one normalized number. Set a feature budget explicitly; evaluate prediction loss and per-cluster preservation separately. If useful distinctions require more features, report that cost. Prevent trivial solutions that merge everything or omit difficult populations from evaluation.

This sketch is not yet an original algorithm. Consensus feature selection, robust optimization, domain generalization and sparse distillation all threaten its novelty. The one-week decision must either locate a concrete gap and specify the new mechanism, or choose the weak-supervision fallback. A small generic stability penalty would not, by itself, justify a methodological novelty claim.

## One-week plan

### Days 1–2: data contract and reproducible baselines

Use UCI Human Activity Recognition as the first engineering pilot. It offers named sensor-derived features, independently recorded activity annotations, and subject identifiers. Its [official documentation](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones) describes 561 engineered features and a split by volunteers. The local archive contains 7,352 training observations from 21 subjects and 2,947 test observations from 9 different subjects; the subject sets do not overlap. The full archive includes the training subject identifiers even though the current extraction is incomplete.

This dataset is already in the project, so do not assume it is untouched confirmatory evidence. Use it for feasibility and explicitly record historical exposure. Its feature budget counts engineered variables, not necessarily physical sensors or raw-signal acquisition cost. Activity classes are an external reference, not proof that every activity should form one density mode.

Freeze preprocessing using training subjects. Reserve a fixed subset of those subjects for development validation; use the official test subjects for the fixed pilot report. Do not randomly split overlapping windows across training and validation. A subsequent thesis evaluation needs a prospectively chosen independent dataset or cohort with compatible scientific traits.

Limit the initial portfolio to:

- K-means and a regularized GMM as inexpensive full-feature references, with a fixed preprocessing/configuration budget.
- IDC as the primary neural comparator, using the authors' implementation and recording the exact version and required adaptations.
- A fixed feature selector plus a predictor trained on training cluster assignments, and a shallow tree surrogate. These intentionally strong simple reductions test whether a complicated joint method is necessary.

DUFS or GroupFS is the next feature-selection comparator. If neural setup prevents a runnable IDC baseline within the first two days, use an existing DUFS implementation for the feasibility phase and record the substitution. Do not spend the whole week building a new framework. Do not label the existing local kernel prototype a GroupFS reproduction.

### Days 3–4: feature sufficiency and transfer

Evaluate fixed feature budgets of 3, 5, 10 and 20, alongside full features. Use a small declared seed/configuration budget; report all scheduled runs and failures. If a method cannot hit a budget exactly, report its actual count rather than silently changing the protocol.

For each fitted discovery model, separately measure:

- External agreement with activity annotations, including per-activity quality.
- Fidelity of restricted-input predictions to that frozen model on new subjects.
- Variation across training seeds and subject splits.
- Actual input coordinates required at prediction time, including routing and gate computation.
- Feature count, runtime, and any loss of small populations.

Predictions on test subjects must use a defined frozen assignment mechanism. Re-clustering the test data is a different, transductive task and must be reported separately. If the cluster count is supplied from benchmark metadata, state that prior information. Labels used for tuning or constraints constitute supervision; final test labels must not be reused for those purposes.

### Days 5–6: one intervention or one fallback

If full-feature clusters are credible but restricted-input models lose important distinctions or fail on new subjects, prototype one change addressing the observed mechanism. Compare it to the strong simple reduction under the same information and feature budget. Test its one relevant ablation; do not open another large parameter sweep.

If several reproducible partitions correspond to different meanings and the desired one requires domain information, switch to a declared small feedback budget. Compare an established constrained sparse-clustering baseline with random versus targeted feedback at equal budgets. Simulated feedback drawn from training annotations must be identified as simulated supervision, not an expert study. A few pairwise constraints are not equivalent to the same number of independent labeled examples.

If ordinary sparse prediction already solves the practical problem, record that success honestly. A useful application or careful evaluation contribution may remain, but a new clustering algorithm has not been justified.

### Day 7: settle the proposal

Produce one research question, one methodological hypothesis, its nearest competing methods, a prespecified application scope, preliminary feasibility evidence and explicit failure criteria. The one-week goal is a defensible proposal and working baseline, not a demonstrated state-of-the-art replacement.

## Decision gates

- Continue with compact-feature assignment when at least one credible reference partition can be preserved reasonably well with substantially fewer features on independent subjects. Assess per-group losses as well as average quality. Define any numerical acceptance margins before viewing the pilot results.
- Pursue a new joint clustering objective only if simple fixed-partition feature selection has a reproducible deficiency that the joint objective addresses.
- Use neural representation learning only when the matched comparison supports it. A transformer, graph network or reinforcement-learning policy needs a specific structural reason, not simply greater model capacity.
- Add weak supervision when it supplies missing task meaning. If even a modest supervised diagnostic cannot predict the chosen target on new subjects, reconsider the measurements or target before inventing a more elaborate unsupervised model.
- Keep radial discovery central only if an application independently motivates its geometry and comparative results support its utility.
- Do not claim novelty merely from gates, consensus, feedback, stability, transfer testing, or an explanation tree. The exact proposed mechanism still needs a focused comparison against its closest literature.

## Confidence and unresolved work

Confidence is high that the current radial results justify narrowing or changing the model family, and that exhaustive subset enumeration is not mandatory. Confidence is moderate that the compact-feature transfer question is a feasible thesis direction. Confidence in a novel successful replacement is currently unestablished: the candidate gap has not been tested, and the closest implementations have not yet been reproduced here.

The immediate next build is the subject-aware data/evaluation adapter and small comparator runner. Long-running experiments should save configurations, fitted states, restricted-input predictions and per-subject results locally, and be supplied as commands for the researcher to run. No further radial command is prescribed by this reassessment.
