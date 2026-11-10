# Early ATOMIC and ATOMIC+ attempts, including corrections

This chapter reconstructs the early work from the 23 saved experiment reports, `docs/CORRECTIONS.md`, the older handoff, and the September 9 code/results audit. It does not rerun those experiments. All original reports and available outputs are included, including reports with conclusions that were later overturned.

## Starting point

Original ATOMIC uses Boolean feature subsets, a k-nearest-neighbor graph, and a reward based on proximity to two connected components: `-(components - 2)^2`. Many very different splits tie at the best value. The legacy `atomic.py` and original ATOMIC PDF are preserved. The clean-room `atomicplus/` package implements evolutionary search, NSGA-II, novelty/local competition, a persistence objective, trees and evaluation tools. These are distinct code generations.

## Attempt-by-attempt record

The experiment number identifies the complete report in `docs/experiments/`; each report contains commands and result paths. Figures below describe the recorded configuration, not universal behavior.

| Attempt | What was tried and learned | Present interpretation |
|---|---|---|
| 001: subspace parity | Compare internal clustering metrics in full space and the selected subspace. | A silhouette or Davies–Bouldin advantage can result from evaluating different measurement spaces. Compare like with like and separately use external evidence. |
| 002: seven UCI datasets | Reimplement ATOMIC and compare full-space/subspace metrics and ARI. Reported examples: Glass ARI about -0.01 versus best baseline 0.24; Ionosphere about 0.01 versus 0.40; Ceramic 1.0 for both. | High subspace separation did not consistently match labels. The full historical table is in the report, but today's `uci_comparison.csv` does not retain all those datasets. Low label agreement alone also does not prove a partition is meaningless. |
| 003: null and stability | Shuffle columns independently, rerun search, and use subsampling to assess feature/partition recurrence. | Useful machinery for checking search artifacts and recurrence. Later audits clarified that this null destroys dependence, not all possible clustering. Stable partitions can still be arbitrary or irrelevant. |
| 004: persistence fitness | Replace flat component count with an admissible MST edge ratio, often using mutual-reachability distances. On an easy synthetic example the informative set scores 5.89 with ARI 1, versus a noise set near 1.02. | More informative than the flat reward in that setting, but not adequate for all nonconvex shapes or varying densities. Ratio is the default, not raw edge difference. |
| 005: recursive tree | Search and accept a split at each node, then recurse. An easy three-group hierarchy reached leaf ARI 1. | Tree code exists. This does not validate later radial/kernel methods in a full hierarchy, nor prove automatic scientific stopping. |
| 006: EA versus greedy | On an easy two-feature problem, greedy/random reached the clean optimum while EA retained extra variables. OR crossover and high mutation were suspected. | An operator problem was demonstrated in the tested configuration; this was not the only obstacle. |
| 007: operator repair | Replace union crossover and disruptive symmetric mutation with set/uniform crossover and asymmetric mutation. Improved recovery at p=12. | More generations alone did not repair the original behavior. Improvement at one dimension did not establish robust EA superiority. |
| 008: broader benchmark | At p=20, greedy remained strong and the tuned EA again had extra variables or missed useful ones. | Stop tuning per problem merely to produce an EA win. Operator repair was too narrow to justify the original claim. |
| 009: alternative feature sets | An archive appeared to offer multiple feature sets describing the same clustering; nonconvex tests remained unreliable. | The claimed unique diversity advantage was later retracted after equal-budget counting and removal of exhaustive pair initialization. |
| 010: connectivity niche | One-seed noisy-subspace examples suggested topology could recover nonconvex groups when full-space methods struggled. | Preliminary only. Its table is explicitly marked not for citation; baseline and diversity claims were corrected. |
| 011: isolate persistence ranking | Enumerate 45 pairs at p=10, separating search from objective behavior on circles/moons/jain/flame. | A useful diagnostic idea, but several broad shape-level conclusions were contradicted by later splitters and repaired data. Do not reuse its purported performance ceilings. |
| 012: fair diversity test | Equal budgets and identical clean-pair counting, with exhaustive pair initialization off. EA found approximately zero clean pairs while random found several. | Earlier diversity mostly came from enumeration and permissive counting. Distinct noise-padded masks are not automatically distinct useful explanations. |
| 013: larger interacting sets | Additive Gaussian, redundant features, and a jointly necessary three-dimensional shell example. Some shell cases worked only at the correct support and failed when noise was added. | Demonstrated hard search landscapes for these models. The report's general claim that every useful set larger than two is necessarily an impossible needle is too broad. |
| 014: deceptive hierarchy | A different, scientifically undesired split often had the highest persistence score. | A better optimizer should select that higher score. Occasional failure to find it is not evidence that EA understands intended meaning. The proposed null/stability cure was not a general solution. |
| 015: multiobjective front | Try EA as a convenient quality/feature-count tradeoff generator. | It can expose alternatives, but greedy already found the best small set in the example; larger-set fronts were not necessarily optimal. No demonstrated EA advantage. |
| 016: graph-cut plus density | Ryan's suggestion led to graph normalized-cut and a DBCV-style density surrogate. Candidate-standardized combination ranked true pairs well on several shapes. | Strong scoped ranking result, largely established by exhaustive pairs. Corrected benchmark results replace old headline figures. The two terms can evaluate different partitions. |
| 017: search with new scores | Compare EA, random, sequential forward selection and CVT-MAP-Elites with a matched search budget. | No demonstrated EA advantage in that configuration. Important correction: the search experiment used a raw sum of terms, whereas the successful enumeration used candidate-standardized terms; these are not identical objectives. |
| 018: signal landscape | Examine subsets by size and number of true features; study nuisance dilution, multiple terms and multivariance-style alternatives. | Partial signal can be weak and vanish when irrelevant variables are added. Strong pair rankings do not establish an easy path through larger sets. Raw within-size comparisons cannot alone establish a cross-size stopping rule. |
| 019: real-data transfer | Pair sweeps on mouse protein and activity data; compare score ranks with attainable label agreement. | The original mouse result was invalidated: 1,080 rows were 72 animals with 15 replicates each. Activity results remain a separate historical diagnostic, not a new subject-transfer evaluation. |
| 020: SUBCLU/shape/splitter audit | Recompute old and repaired benchmarks and compare candidate availability, pair ranking, and different splitters. | Returning the true pair, ranking it first and assigning its clusters are different tasks. A best splitter chosen per shape using labels is an oracle comparison. Flame remains a ranking failure despite moderate recoverability on the true pair. |
| 021: per-set calibration | Independent-column permutations and z-scores attempt to compare different feature counts and guide stopping. | Size calibration is established prior art, not a new invention. It does not turn the null into a no-cluster test or make post-search thresholds statistically valid. |
| 022: expression-data search | Calibrated singleton screening, seeding and forward growth on reduced METABRIC contrasts; compare with label-assisted feature selection. | Historical search did not recover the strong label-assisted examples. Later claims that this isolates search alone changed sample size and splitter. Current result CSVs do not reproduce the historical METABRIC table. |
| 023: basin size | Random pair starts followed by growth; estimate the fraction reaching a label-defined performance bar. | Growth did not reliably enlarge the useful basin in the tested settings. Thirty probes give wide uncertainty. Label-based basin estimates are retrospective diagnostics, not an unlabeled eligibility test or a proof of exponential necessity. |

## Corrected benchmark findings

The old nuisance generator used comparatively uniform noise; some planted features revealed themselves through their marginal distributions. Four of six shapes could be detected one column at a time. The repaired structured-noise benchmark made single-column screening less informative. Some method scores improved after this repair, while full-space baselines also became stronger. Do not label every old number as a result on the repaired generator.

For corrected hybrid rank-one pair recovery at p=12/20/40, `docs/CORRECTIONS.md` reports circles 1/1/1, moons 1/1/.90, jain 1/1/.95, spiral 1/.95/1, and flame 0/0/0. These are pair-ranking figures, not end-to-end clustering quality or search efficiency.

Flame is not universally unrecoverable. Given its true pair, the recorded spectral split reaches ARI .665 and HDBSCAN .612. The near-zero end-to-end result is therefore a serious feature-selection failure relative to these diagnostics. For jain, alternative splitters can perform much better than the persistence splitter; the old claim that nothing could fix it was wrong. Choosing the strongest splitter retrospectively by shape is an oracle, not a deployed automatic selection rule.

## September 9 audit: issues that change the story

Read `docs/research-assessment-2026-09-09.md` before accepting the older `docs/HANDOFF.md` as current truth.

1. `scripts/run_levine_tree.py` and related stability code use evaluation labels to identify pure populations and stop. Those runs cannot validate fully unlabeled tree stopping. Label-stratified sampling is a separate disclosed source of information.
2. Mean node purity and final leaf clustering can disagree sharply. Saved density-tree node purity near .982 corresponded to final leaf ARI about .167; a combined example had .909 node purity and .799 leaf ARI. These are descriptive in-sample audits of partly label-assisted trees, not a fair ranking of deployable methods.
3. Candidate-pool z-scoring changes the relative weights when unrelated candidates are added. The normalized hybrid is not a fixed adaptive objective unless its reference distribution is frozen.
4. Graph-cut and density terms can score different partitions within the same feature set; the emitted splitter can be different again.
5. The density term is a DBCV-style surrogate, not full DBCV. Under particular admissible MST conditions it is a monotone transform of an edge ratio.
6. Column permutations preserve singleton data distributions. They cannot detect a univariate two-mode structure through a row-order-invariant statistic. Conversely, one correlated Gaussian can reject independence without having multiple modes.
7. Known-support initialization and successful stopping do not establish autonomous discovery. A saved three-feature shell example grows correctly from the supplied support but autonomous search returns extra or wrong features.
8. A sparse score cannot be assumed to represent every intended scientific category. Madelon's binary labels are not simply its geometric cluster identities. Hardness results for Boolean distributions do not prove this continuous thesis problem requires enumeration.

## Current-file gaps and drift

The packaging inventory records the current CSV headers and row counts. Historical writeups remain included even when the corresponding original table is missing.

- The current `results/uci_comparison.csv` contains only Ozone rows rather than the full seven-dataset history.
- The current `results/real_calibration.csv` contains a smaller mouse-only result set rather than the historical METABRIC table; even the September audit's description of its then-current contents is historical.
- The current EA result contains seeds 0–19; an older correction refers to 12 seeds. Use the stored rows for current coverage.
- `results/benchmark_validation.csv` now covers six shapes, three feature counts and both noise types; an older recorded coverage gap is no longer an accurate file inventory.
- `results/fitness_sweep.csv` denied read access during packaging, even with shared-read access. Its related code and written findings are included; the file is explicitly recorded as unreadable rather than reconstructed.
- Some very early experiments were reported from inline commands without a complete standalone run directory. Their reports are evidence of the historical reasoning, not a substitute for unavailable raw data.

## Why this history matters

The useful surviving lesson is to diagnose the exact failing stage. An optimization failure, an objective mismatch, a bad assignment model and an evaluation mistake require different repairs. The project made progress whenever it separated them. It lost time when it treated a better internal number, an oracle-assisted result or an attractive explanation as evidence that the whole method worked.
