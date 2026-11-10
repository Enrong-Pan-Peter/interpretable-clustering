# A method-first, trait-defined research target

## Material Passport

- Origin Skill: academic-research-suite, targeted research-question and novelty review
- Origin Date: 2026-10-14
- Verification Status: source-supported prior-art assessment; PROPOSED method and experiments; no new experimental results
- Version Label: trait_first_plan_v1
- Inputs: user's application-scope correction; verified September/October development results; lab-meeting transcript and original proposal previously reviewed; three parallel literature/mathematical reviews
- Scope: targeted novelty challenge, not an exhaustive search or a guarantee of novelty
- Preference retained: prefer two or three original measurements per decision; permit larger panels with explicit rules

## 1. Decision

Develop one reliable, interpretable node before committing to a full FlowCAP or other application benchmark. The October 7 plan moved the real-data comparison too far forward as the immediate development priority. A small data inspection remains useful now to check measurement semantics, independent sampling units and plausible structure; a large leaderboard exercise is not the next milestone.

Cytometry and breast cancer are possible applications, not constraints on the method. Define the intended data properties first, then select datasets using those properties and an independent source of validation. Record exclusions before looking at final comparative results. This permits a specialized method without making the evaluation a search for datasets on which it happens to win.

The present broad target is a credible research question, but **it is not yet an established novel method**. The useful change from this review is a stricter test of what could count as the contribution.

## 2. What the novelty audit rules out

| Proposed differentiator | Close prior art | Consequence |
|---|---|---|
| Cluster descriptions using few original features | [Lawless and Gunluk, ICML 2023](https://proceedings.mlr.press/v202/lawless23a.html) optimizes feature count or polyhedral complexity | Small panels plus readable boundaries alone are insufficient |
| Discover clusters and readable sparse rules jointly | [Multi-Polytope Machines, AAAI 2022](https://ojs.aaai.org/index.php/AAAI/article/view/20693) jointly constructs partitions and constrained polytopes | Being unsupervised or avoiding a fixed teacher is insufficient |
| Several concise descriptions of a discovered population | [Cluster-Explorer, PVLDB 2025](https://www.vldb.org/pvldb/vol18/p1495-somech.pdf) searches feature predicates using coverage and separation criteria | Alternative descriptions and a browsing interface are insufficient |
| Multiple good, different feature panels | [Bach and Bohm, 2024](https://link.springer.com/article/10.1007/s41060-024-00527-8) formalizes alternative feature selection | Changing the target to frozen cluster labels is a straightforward baseline, not an automatic novelty claim |
| Feature selection sensitive to both means and variances | [Xie, Pan and Shen, 2008](https://arxiv.org/abs/0802.3125) selects variables with cluster-specific diagonal covariance models | A sparse variance-sensitive mixture or quadratic assignment rule alone is insufficient |
| Joint feature relevance, clustering and adaptive component growth | [DIVI, September 2026](https://link.springer.com/article/10.1007/s00180-026-01807-6) is a new, particularly relevant competitor | Inspect its full method and implementation before claiming this combination; abstract and accessible appendix reviewed here |

The earlier comparison also identified sparse oblique clustering trees, Kauri, SpEx, FAUST and ConvexGating. These remain relevant when their inputs and outputs match the experiment. A kernel, a tree, resampling and a few features do not collectively establish novelty just because the exact software package is different.

Independent calibration is useful, but attaching a standard held-out error bound to an existing learner is not by itself a substantial methodological contribution. Recent [conformal cluster-label inference](https://arxiv.org/abs/2604.03488) also makes a blanket claim of novel clustering uncertainty inappropriate. Its latent-label target differs from agreement with our frozen prediction rule; these guarantees must not be conflated.

## 3. Recommended research question and scope

**Question:** Can we discover compact original-feature rules for populations with sparse, simple local geometry, while preserving recovery on independent observations and explicitly exposing when a smaller panel or a proposed split is unsupported?

The first scope is continuous tabular measurements with meaningful names and units. We hypothesize that useful local populations can be separated using a modest subset of measurements and a short rule. Many other measurements may be irrelevant or correlated substitutes. Different nodes may eventually use different panels. There must be enough independent observations to fit and evaluate the proposed population.

Initially consider two native rule families:

1. A sparse linear score for mean-separated populations, reusing the existing exact centroid-rule branch.
2. A sparse radial or ellipsoidal score for a deliberately narrow nonlinear case: separated inner and outer bands. The rule uses squared deviations of named measurements, rather than an opaque embedding.

An illustrative curved rule is `((x_a-c_a)/s_a)^2 + ((x_b-c_b)/s_b)^2 > t`. This is an executable two-measurement boundary. It is not a new mathematical idea and does not cover arbitrary moons, spirals or intersecting manifolds. Two or three measurements are preferred where the evidence supports them; they are not imposed on a signal that needs twelve.

Avoid treating every latent mixture component as a density cluster. In particular, Gaussians with a common center and different scales form a density that decreases away from that center. Their posterior assignments can separate inner and outer observations without there being two density modes. A genuinely separated-band model and a single heavy-tailed population are therefore different tests.

This scope is provisional. If real measurement domains do not support a useful curved-rule regime, do not manufacture an application to justify it. Retain the mean-separation component and revise the nonlinear scope using the data audit.

## 4. Where a methodological contribution would have to occur

The preferred research bet is **support search for native interpretable cluster rules**, with independently checked population recovery and a scoped split decision. The explanatory rule participates in the discovery problem. The algorithm must find useful original-feature supports without exhaustive combinations, including supports whose utility appears only jointly.

The unresolved question is whether we can devise a search or pruning mechanism that improves the recovery-versus-measurement-cost tradeoff over strong existing learners and straightforward combinations of them. This review has not established that mechanism, and novelty must remain conditional until it is specified and compared.

The contribution should survive these challenges:

- **Reduction challenge:** Could the proposed method be obtained by running an established sparse mixture or interpretable clustering learner, then applying ordinary pruning and a held-out check? If so, identify a substantive advance beyond that composition or weaken the novelty claim.
- **Search challenge:** At matched computation, does the proposed search find useful supports that random search, simple forward/backward selection and an established sparse learner miss? A small-dimensional exhaustive audit measures the search gap; it is not the deployment algorithm.
- **Coupling challenge:** Does incorporating rule simplicity during discovery improve the outcome over explaining a frozen partition afterward? Use the same rule family and data budgets to avoid attributing gains to an unfair comparator.
- **Statistical challenge:** Does the rule retain the advertised recovery, and does the split decision behave properly under its stated null? Feature recurrence and fidelity alone do not answer either question.
- **Claim challenge:** Call a panel the smallest *tested* sufficient panel unless a valid lower bound or global optimization certificate establishes more. A proof of near-minimality would strengthen the work, but is not assumed or promised.

A defensible thesis can contribute a new, well-tested method for a defined regime without a new optimizer or a universal clustering theorem. Merely assembling familiar modules and observing one favorable dataset would not meet the intended standard.

The companion adversarial review deliberately sets a demanding bar around minimality certificates and post-search inference. Those are possible contributions, not mandatory prerequisites for every useful methods thesis. The practical first bet remains a specific discovery mechanism with a demonstrated advantage over the corresponding standard construction; a guarantee should be claimed only if it is actually established.

## 5. Smallest experiment that changes our next decision

Use a two-arm node diagnostic: known informative panel versus unknown panel. Both arms fit the same rule family. Labels are reserved for evaluation, except that the known-panel arm deliberately receives the planted feature indices as an oracle diagnostic.

| Check | Controlled cases | Decision it supports |
|---|---|---|
| Representation | Mean separation; separated radial bands; known features supplied | If the rule fails even here, fix the family or implementation before changing the search |
| Search and ranking | Same populations, hidden among nuisance measurements; compare fixed budgets | A successful oracle and failed unknown-panel fit isolates the feature-discovery problem |
| Compression | True small support versus distributed 12-feature signal | Distinguish removing nuisance from discarding necessary information |
| Substitute measurements | Correlated alternative measurements supporting the same assignments | Evaluate assignment stability separately from exact-feature recurrence |
| Split acceptance | Independent and correlated single Gaussian; single heavy-tailed population; one radial band | Detect forced or model-misspecification splits; distinguish null validity from favorable power |
| Scope boundary | Curved shape outside the chosen rule family | Show the limit rather than retuning the rule after seeing final labels |

For the nonlinear diagnostic, the mathematical review proposes a properly normalized radial-band density. Test it first on supplied features with discovery-fitted preprocessing. Its likelihood calculation must be checked before support search is added.

When comparing different panel sizes, use a model on the same full observation space or a justified cancellation of a common nuisance model. Do not compare raw likelihoods of different-dimensional observations. A possible construction is `p_S(x) = q0(x_notS | x_S) g_S(x_S)`, with one fixed joint reference `q0`; the full-space log-likelihood ratio reduces to `log g_S(x_S) - log q0,S(x_S)`. This is a proposed modeling device, not a new result or a universal clustering-quality score. Its assumptions and normalization must be implemented faithfully.

Better predictive fit is still separate from evidence of multiple meaningful populations. Start with a root node and an explicitly scoped null. Do not transfer an untruncated Gaussian null to child nodes after routing; ancestor selection changes the distribution.

Use fresh development seeds and independent evaluation rows because previous development results have already influenced design. Preserve feature identities within a population when comparing independent rediscovery. For grouped data, reserve whole specimens or subjects where those are the claimed unit of generalization.

Report a small set of separate outcomes: population recovery, feature count, rule terms, search cost, independent assignment reproducibility, false splits and abstentions. Include per-population errors when rare groups matter. Set numerical success tolerances before a confirmatory run; none of the illustrative goals here is a field-standard threshold.

## 6. Order of work and dataset choice

1. **Establish the node:** retain the promising mean-separation branch as a control; implement and verify the supplied-panel curved-rule diagnostic and negative controls. This is mechanism development, not a novelty demonstration.
2. **Locate the search obstacle:** run the known-versus-hidden-panel ablation and matched-budget baselines. Extend beyond three selected features in at least one condition. Do not add another optimizer until this comparison identifies what it must improve.
3. **Specify the new mechanism:** write the exact difference from the closest existing method and test the ablation that removes that difference. If the difference has no effect or is already standard, revise the claim before expanding the benchmark.
4. **Run a real-data preflight:** inspect one candidate application for named measurements, relevant geometry, independent samples and external validation. Chemical assays, cell morphology, interpretable sensor measurements and cytometry are candidate families, not verified matches. Check dataset eligibility before final performance comparison.
5. **Freeze and benchmark:** use at least one trait-matched real dataset plus a stress case, with strong relevant comparators and a record of all tested datasets. FlowCAP is appropriate if cytometry remains the best match. Published class labels provide external validation; they need not coincide with all unsupervised structures.
6. **Add the hierarchy:** only after the root-node result, evaluate path complexity, measurement reuse, accumulated errors and appropriate stopping after conditioning. Then build the offline alternatives interface.

Do not wait until the entire tree and interface work to inspect any real data. Conversely, do not mistake a large collection of benchmark scores for evidence that the underlying mechanism is understood.

## 7. Effect on the proposal

Retain the original aim of interpretable population discovery, automatic measurement selection, explicit decisions and useful alternatives. Replace a biomedical-dataset commitment with a trait-defined scope and justify the final application after inspection. Replace a general combined-fitness promise with a specified native-rule family, a support-search hypothesis, separate validation and explicit limitations.

A suitable working title is **Feature-Efficient Clustering with Verifiable Rules for Structured Tabular Data**. This is a working research direction, not a claim of established novelty or a completed algorithm.

Current positive evidence remains the three-seed development result for mean-separated data and exact replay of the centroid rules. It does not establish sparse curved clustering, split control, global panel minimality, real-data usefulness or superiority to current methods. See the [verified development assessment](rank-preservation-assessment-2026-09-30.md).

## Supporting reviews

- [Adversarial novelty review](novelty-challenge-2026-10-14.md)
- [Mathematical node design](trait-first-method-review-2026-10-14.md)
- [Shape-model prior art and data scope](shape-method-prior-art-2026-10-14.md)

No new clustering runs were performed for this design review.
