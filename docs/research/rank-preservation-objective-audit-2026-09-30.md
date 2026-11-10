# Rank preservation fixed a real defect; the remaining objective evidence is mixed

Material passport: independent results/mathematical audit, 2026-09-30, ARS experiment-planning workflow. Primary run: `results/research_rank_preservation/20260930T044157_487943Z`; earlier repeat: `20260930T034706_021919Z`. Read-only analysis of saved reports and source; no new fits or changes to results. Findings are exploratory development evidence, not confirmation or a novelty claim.

Both runs completed the same 24 jobs: four datasets × three seeds × two kernels. Their source hashes and parent-manifest hashes match. All 24 reports are exactly equal after removing timing fields; the Markdown summaries are byte-identical. These are repeated executions of one experiment, not six independent seeds. All 17 recorded source hashes match the files inspected. The runner hash is `561aa0fa939acb38ac2e3ada0cd8f3a3a5de311dd1ad3f5f77eb20f8aace59fc`; `rank_preserved_kernel.py` is `797a4357e59e67fb346c89a12ef721cd1b0e193e3419ef99f77e831259603b8a`.

## The constraint works, and the correct comparator matters

All 48 constrained models—24 frozen starts and 24 optimized models—satisfy `A.T @ A = I/2` to numerical precision. The largest Frobenius error is `7.99e-16`; the smallest second/first singular-value ratio is `0.9999999999999996`. All pass the implementation's noncollapse gate. This removes the previously demonstrated freedom to make a nominal rank-two projection effectively rank one.

The main paired comparator is `rank_preserved_pca`, not the old unconstrained optimized model. It isolates what optimization adds after the geometry constraint is imposed. Original PCA and saved unconstrained results remain useful secondary comparisons. Each row below averages only seeds 26, 27 and 28 for that dataset/kernel.

| Dataset / kernel | Original PCA ARI | Saved unconstrained ARI | Constrained frozen ARI | Constrained optimized ARI | Optimized vs constrained frozen |
|---|---:|---:|---:|---:|---|
| Mean shift / global | .57048 | .51864 | .58708 | **.61831** | All three improve |
| Mean shift / local | .56287 | .33136 | .58769 | .56073 | One improves, two worsen |
| Grouped moons / global | .55961 | .52414 | .55961 | .54916 | One improves, two worsen |
| Grouped moons / local | .56888 | .50203 | .56888 | .55239 | One improves, two worsen |

These are three small paired replications, not reliable estimates of universal superiority or inferiority. In particular, the two small average decreases on moons should not be exaggerated. But the direction is enough to withhold a claim that optimizing the current loss generally improves a useful starting representation.

Mean-shift/global is a real positive result. Its test ARIs improve from `.54514/.54535/.67076` to `.57531/.57550/.70412`. Signal recall improves from `9/12,9/12,10/12` to `11/12,12/12,11/12`. Validation graph loss improves in all three cases, from mean `.67113` to `.60710`. All three selected runs originate from the PCA start, with actual feature replacements. The result is not only a less distorted copy of the old support.

Mean-shift/local makes no feature entries in any of its nine restart trajectories. The selected support is exactly the constrained PCA support for each seed. Its ARI changes therefore mainly test changes to geometry/assignment within those supports, not improved panel discovery. For moons, the frozen starts already include every planted signal and all optimized constrained models retain them; the experiment mainly tests whether the representation becomes more useful.

The 16-feature cap is still an upper bound, not a minimal-panel certificate. Even the improved mean-shift/global models retain four or five nuisance features. Their depth-three tree disagreements are `.265/.320/.235` on test rows: high panel recall does not yet produce a faithful short rule.

## Apply the promised stopping rule by setting

The preceding audit said: “If the constrained optimizer still damages that baseline while improving both training and validation loss, reject this spectral score as the main selection objective for that setting.” This was an operational development rule, not a preregistered statistical test. It does not justify discarding every kernel and dataset because one branch fails.

The literal failure pattern still occurs, for example:

| Case | Constrained frozen → optimized test ARI | Training loss | Validation loss |
|---|---:|---:|---:|
| Mean shift 28 / local | .68734 → .59085 | .52389 → .24621 | .52174 → .50101 |
| Grouped moons 26 / local | .62226 → .59090 | .34757 → .00220 | .35502 → .32783 |
| Grouped moons 27 / global | .68733 → .65438 | .26088 → .14471 | .29101 → .24553 |
| Grouped moons 28 / global | .44618 → .43280 | .30940 → .16777 | .30745 → .24827 |

Full case names are `{dataset}_p{p}_s{signals}_b16_seed{seed}_{kernel}`; `p=200,signals=12` for mean shift and `p=50,signals=10` for grouped moons.

Thus rank preservation does not make a lower eigengap loss a dependable choice between representations, even when the preference persists on separate rows. Stop treating that loss as the sole authority for replacing an existing useful representation in these failing settings. The mean-shift/global branch does not meet this failure pattern and deserves further focused study. A blanket “kernel fitness failed” conclusion would throw away its observed support improvement.

## Negative controls explain what remains unresolved

| Negative control / kernel | Constrained frozen training → optimized | Constrained frozen validation → optimized | Old unconstrained validation |
|---|---:|---:|---:|
| Independent Gaussian / global | .94627 → .58296 | .94433 → .95808 | .66442 |
| Independent Gaussian / local | .86061 → .31657 | .85313 → .85327 | .32783 |
| Correlated Gaussian / global | .50381 → .34768 | .49426 → .51855 | .50755 |
| Correlated Gaussian / local | .31615 → .07582 | .31396 → .33048 | .33721 |

The spectacular transferable loss reduction on independent Gaussian noise largely disappears after preserving rank. Global validation loss worsens in all three seeds, although training loss improves strongly. This is consistent with the previous population calculation: the unconstrained score had rewarded flattening isotropic noise to a line. Now finite-sample optimization still exploits the discovery data, which independent-row evaluation exposes.

The correlated Gaussian control remains essential. Its optimized global validation loss `.51855` is lower than mean-shift/global `.60710`; its local validation loss `.33048` is lower than either positive dataset's local mean. Orthonormal columns do not make projected data isotropic when the original population covariance is anisotropic. A continuous elongated population can still receive an attractive spectral score. There is no universal absolute loss threshold warranted by these comparisons.

Every model still proposes two groups, and every constrained model passes the current gate. Negative-control test child counts remain nonempty and reasonably large; a balanced split of one population is still a split of one population. There is no acceptance rule here, hence no measured false-positive rate. Graph loss reconstructed on validation rows measures geometry there; it is distinct from the accuracy of the retained native assignment.

## Recommended direction: useful panels first, explicit shape evidence second

Keep the constrained global model as a **candidate panel generator**, with its frozen PCA comparator. The immediate research question should be narrower than another search over kernels, ranks and penalties: *does its support improvement lead to a simpler, independently defensible assignment rule?*

Freeze the discovered support and low-dimensional representation, then compare the retained spectral rule with an explicit low-dimensional shape model. A tightly scoped first branch is a one-Gaussian model versus a regularized two-component, shared-covariance Gaussian mixture in the fixed representation. Fit both on discovery rows; use a separate selection set for predictive log-density and complexity decisions; preserve a final evaluation set. Report the existing native spectral assignment alongside it, not retrospectively replaced by whichever has the best ARI. The one-Gaussian comparator must include covariance, so a correlated unimodal population is a serious alternative rather than being confused with two clusters. No change to the feature search is needed for this first comparison.

This is a proposed mean-shift branch, not a universal model for moons, shells or arbitrary shapes. A mixture can approximate a non-Gaussian single population, so improved mixture prediction is not alone a declaration that scientifically meaningful clusters exist. A single-shell control remains necessary before expanding the claim. For nonlinear shapes, explicitly testing density valleys/connected high-density regions is more faithful to the intended geometry than continuing to optimize spectral separation alone; that should be a separate representation study.

The relevant statistical distinction has established precedents: [SigClust](https://doi.org/10.1198/016214508000000454) explicitly evaluates a Gaussian null, and [Minimum Density Hyperplanes](https://www.jmlr.org/beta/papers/v17/15-307.html) targets low-density boundaries under a stated cluster definition. Neither source validates the proposed pipeline or makes its components novel. They illustrate why candidate discovery, shape assumptions and evidence for a split should be specified separately.

For the promising global branch, any subsequent claim of reproducible feature discovery should use fresh generated observations/seeds and the frozen comparator, with support recovery and assignment quality both reported. The two completed rank runs reuse all earlier development rows and cannot supply that confirmation.
