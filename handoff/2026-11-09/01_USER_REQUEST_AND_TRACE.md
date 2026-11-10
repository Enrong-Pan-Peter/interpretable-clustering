# Researcher priorities and conversation trace

This is a faithful summary of the visible user requests and documented project decisions. Exact dates are used only when recorded in an artifact or dated message. The raw laboratory transcript and original proposal are attached separately.

## Priorities that persist

- Build a useful and defensible thesis contribution. A novel method can combine established tools, but the actual difference and value must be demonstrated.
- Discover small feature sets whose usefulness can be checked against domain knowledge, known facts, reference populations, independent outcomes or credible external agreement.
- Prefer two or three variables where they support readable plots, but allow larger feature sets with explicit rules. Do not impose a hard three-feature limit.
- Ideally explain cluster shape and assign new points. Do not conflate a small feature set, an interpretable boundary and a low-dimensional plot.
- Use the words feature sets from the later search-design stage onward. Historical code identifiers remain unchanged.
- Be candid about failures and unsupported claims. The researcher repeatedly challenged claims that enumeration was an evolutionary-search success or that a single z-score could solve everything.
- The application can change. Cytometry and breast-cancer expression were initial examples, not compulsory datasets. Choose applications by scientific traits and then evaluate honestly; do not select datasets only after observing favorable scores.
- Deep learning, sparse encoders, transformers, graph/network methods, representation learning, weak/semi-supervision, concept methods and other clustering families are allowed when they address an actual problem.
- Multiple agents are welcome for literature, mathematics, statistics and code review. Their outputs are hypotheses/reviews, not independent experimental evidence.
- Prepare scripts and clear PowerShell commands for lengthy local runs. Store results in this repository so the agent can inspect them afterward. Many earlier experiments were run by the researcher this way.

## How the discussion moved

1. The researcher asked for a fresh inspection of the stalled ATOMIC-derived project. The central concern was whether the fitness was wrong, whether EA was helping, and whether the apparent successes were only exhaustive pair/triple enumeration.
2. The desired explanation was clarified: a small useful feature set comes first; seeing the cluster shape and having a readable new-point rule are additional goals.
3. The researcher requested the academic-research-suite skill globally. It is now present in the Codex skills catalog. This ZIP is self-contained research material; the recipient does not need that personal plugin installation to read it.
4. Repeated pilot, ranking and ablation runs were prepared and inspected. The analysis moved away from blaming one component toward separating proposal/search, score ranking, model geometry, compression and validation.
5. The researcher suggested kernels and dimensional transformations based on GroupFS. The ensuing mechanism audit distinguished GroupFS's feature embedding from a sample projection. Several kernel experiments followed; they are not reproductions of GroupFS.
6. Lab discussion emphasized interpretability and a bounded scope instead of promising arbitrary nonconvex clustering. The researcher wanted known benchmark structures and real examples with scientifically justified traits.
7. The original proposal was reviewed. Its main scientific aim survived, but claims that no existing method could build a readable unlabeled hierarchy were too broad. Several close tree/gating/feature-selection methods were identified.
8. The laboratory proposed precomputing candidate splits/trees, letting a person inspect alternatives and replace branches. Scores from different algorithms or dimensions were recognized as non-comparable without careful definitions. Stability was recognized as insufficient for quality. These are design ideas, not an implemented interactive product.
9. The trait-first plan narrowed to one node and explicit native rules before hierarchy/UI work. Radial models gave a tractable shape family and allowed feature-set likelihood comparisons on a common observation space.
10. A radial diagnostic run stopped in the single-shell case due to a floating-point lower-bound excursion. The fix preserved the scientific model and recovered completed work with provenance. It was not a scientific failure repaired by changing the data or objective.
11. The researcher asked how many more tests would precede algorithm design. The October 20 plan explicitly limited the remaining synthetic development to one targeted ablation and one frozen replication/stress batch. Those batches are complete.
12. The kernel proposal improved recovery in that restricted family, including sets larger than three variables. Higher nuisance dimension and weaker separation exposed limits. The evidence did not establish a general clustering algorithm or real-data usefulness.
13. In the latest discussion, the researcher explicitly invited a larger thesis pivot. The November 5 recommendation was to preserve radial results and investigate compact-feature prediction/transfer using existing models. A one-week proposal deadline was given. That new comparison has not been implemented yet.
14. The present request is a ZIP handoff that enables a new agent to keep the direction, change it, or propose a better method. Packaging is not authorization to claim any untested idea already works.

## Initial proposal and meeting context

The one-page proposal, `attachments/Enrong_CISC500_Proposal.pdf`, is titled **Interpretable Subspace Clustering for Biomedical Data**. It proposes recursive binary splits, feature-set size determined by the method, refusal of unsupported splits, biological marker/reference-population evaluation, and an interactive comparison interface. Its broad literature-gap wording is superseded by `docs/research/proposal-evolution-review-2026-10-04.md` and subsequent novelty audits.

The full supplied transcript is `attachments/lab_meeting_transcript.txt`. The user also supplied these pre-recording notes: the proposed tree resembles a decision tree and needs a clear distinction; understand how practitioners currently hand-pick clusters; automation plus interpretability could be a stronger contribution than inventing an entire clustering algorithm. The initial preference for at most three variables was later relaxed by the user to two/three preferred, larger sets allowed with explicit rules.

The transcript includes exploratory suggestions to rank nodes or trees using several clustering heuristics. Those suggestions are discussion material. They do not authorize treating incomparable numerical scores as a valid objective, or assuming a validated ranking procedure already exists.

## Practical working style

Use short, direct explanations. Lead with what a run established and what remains uncertain. Ask for missing information only when it materially affects the next action. Provide actual runnable Windows commands for expensive experiments. Do not make the researcher repeat completed batches because the new agent has not read the saved results.

The repository originally lived at `C:\Users\Peter\Desktop\Github\ATOMIC_Clustering`; an earlier conversation referred to `llm-faithfulness-evolution`. Use the current repository layout, not the old directory name. A previous command failed because `..venv-research` was mistyped; the executable is `& ".\.venv-research\Scripts\python.exe"` from the repository root.
