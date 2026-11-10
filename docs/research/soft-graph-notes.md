# Smooth spectral panel proposals: prototype and mathematical audit

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: authorized prototype implementation with a numerical validation plan
- Origin Date: 2026-09-14
- Verification Status: NUMERICAL CHECKS PASSED; discovery performance unverified
- Version Label: soft_spectral_proposals_v1
- Scope: mathematical derivation and implementation checks, not a performance or novelty claim

## The question this prototype can answer

Does a continuous feature geometry produce useful candidate panels, including
panels larger than three, more efficiently than random subsets or the existing
discrete search under a common evaluation protocol?

`atomic_research/soft_graph.py` supplies only **candidate proposals**. It does
not choose the final panel, fit a recursive tree, accept a split, access known
population labels, or establish biological usefulness. The root experiment
harness must evaluate its proposals with the same panel scorer used for other
search methods. Candidate labels, when required by that scorer, must be fitted
from the candidate's features rather than copied from this relaxation.

## Objective

Let `Z` contain the discovery rows after centering and optional unit-variance
scaling. Optimization uses a uniformly sampled subset of at most 128 rows by
default. This sample is the same across restarts. Fit scaling on discovery data
only, and never pass validation or confirmation rows to `propose_panels`.

For logits `a`, define positive feature weights `w = softmax(a)`, so
`sum(w) = 1`. The squared distance is

```text
r_ik(w) = sum_j w_j (Z_ij - Z_kj)^2.
```

For distinct observations,

```text
A_ik(w) = exp(-r_ik(w) / tau) + epsilon,
tau = 2 bandwidth^2,
A_ii = 0.
```

The default floor is `epsilon=1e-6`. It prevents a kernel that has underflowed
from appearing to have a perfect disconnected split. This is a numerical
regularizer that changes the graph and must be disclosed. A recorded
`floor_fraction_of_affinity` measures how much total affinity comes from this
floor. Values above 0.1 are counted in the final diagnostics; no hidden clipping
or acceptance rule treats such evaluations as meaningful separation evidence.

Let `D = diag(A 1)` and `Lsym = I - D^(-1/2) A D^(-1/2)`. The minimized loss is

```text
J(w) = lambda_2(Lsym)
       + beta [log(mean(d)) - mean(log(d))]
       + alpha H(w) / log(p),
H(w) = -sum_j w_j log(w_j).
```

For one variable feature, the entropy term is zero. The degree penalty is
nonnegative and discourages highly unequal degrees, including isolated
observations. It does **not** enforce a minimum cluster size, ensure two
populations, or exclude a stable nuisance split. Its default coefficient is
`beta=0.02`; ablation with zero is supported.

An L1 penalty on these nonnegative simplex weights would always be one and
could not select features. Positive entropy penalization instead encourages
weight concentration. It is a search device, not a principled estimator of the
true feature count. All-zero weights and global shrinking of every distance
are unavailable because the weights sum to one. This scale constraint does not
prevent concentrating on an unhelpful feature.

The entropy coefficient starts at zero for the first third of each run, then
ramps linearly to the requested value, `alpha=0.02` by default. The hope is that
geometry can develop before concentration becomes stronger. This is a
**hypothesis**, not an established convergence mechanism. Setting
`entropy_strength=0` gives the no-explicit-sparsity control. The spectral term
itself may still produce concentrated weights.

## Analytic gradient and what the tests establish

For a simple second eigenvalue, take the generalized eigenvector `v` satisfying

```text
(D-A)v = lambda Dv,   v' D v = 1.
```

Symmetric perturbation of one undirected affinity gives

```text
d lambda / d A_ik = (v_i-v_k)^2 - lambda(v_i^2 + v_k^2),  i < k.
```

The second term is essential: it differentiates the changing degree
normalization. Omitting it differentiates a different objective. This equation
follows by differentiating the generalized Rayleigh quotient at its normalized
stationary eigenvector.

For the degree penalty `R`,

```text
dR/dd_i = [1/mean(d) - 1/d_i] / n,
dR/dA_ik = dR/dd_i + dR/dd_k.
```

Multiplying the combined edge derivative by
`-exp(-r_ik/tau)(Z_ij-Z_kj)^2/tau` and summing over `i<k` produces the feature
gradient. The entropy derivative adds `-alpha(log(w_j)+1)/log(p)`.
Finally, the softmax chain rule gives

```text
dJ/da_j = w_j [dJ/dw_j - sum_l w_l dJ/dw_l].
```

For a symmetric matrix `B`, the implementation uses the identity

```text
sum_(i<k) B_ik (Z_ij-Z_kj)^2
  = sum_i Z_ij^2 sum_k B_ik - sum_i Z_ij (BZ)_ij.
```

Thus it does not allocate a feature-by-observation-by-observation tensor.
Dense work per objective evaluation is approximately `O(m^2 p + m^3)`, where
`m <= max_samples`; the cubic term conservatively describes the dense
eigensolver. Working memory is `O(mp + m^2 + p)` in addition to the supplied
input and its initial conversion. This is a bounded-row prototype, not an
anchor-graph implementation or a large-sample scalability claim.

At repeated second eigenvalues the eigenvalue objective is nonsmooth. The
selected eigenvector need not provide a unique derivative. Every evaluation
records the second-to-third eigenvalue gap, and diagnostics count gaps below
`1e-8`. The finite-difference tests deliberately check simple-eigenvalue cases;
they do not assert differentiability at multiplicity.

The numerical tests cover the full gradient, including entropy and degree
normalization, at two bandwidths; the matrix contraction against an explicit
pair sum; feature permutation and logit-offset invariance; reproducibility;
constant features; finite-data checks; and the affinity-underflow case. A
uniform-start proposal run must commute with a feature permutation away from
ranking ties. Random restarts have this property **in distribution**, because
using the same seed after permuting columns assigns its random perturbations
to different features. Exact ties can depend on column order.

On 2026-09-14, running
`.venv-research/Scripts/python.exe -m pytest tests/test_research_soft_graph.py -q`
passed all 20 tests in 14.91 seconds (including initial imports). These are
numerical and interface checks, not successful clustering experiments.

A separate bounded smoke diagnostic used 180 observations, 24 features,
five planted concentric-shell coordinates, and 19 independent Gaussian
nuisance coordinates. Directions were uniform on the unit sphere in five
dimensions; the two equiprobable radii were 1 and 2.5. Data seed was 314,
signal indices `(1,4,8,13,19)`, proposal seed 5, 30 steps, three restarts,
and 80 sampled rows. It completed 93 objective evaluations, produced 37
panels covering sizes one through eight, and **did not propose the planted
five-feature panel**. The best five-feature proposal overlapped three of the
five signal coordinates. All gradients were finite. Measured proposal time
on this machine was approximately 0.064 seconds; that timing is not a
large-dataset speed claim. This single exploratory failure shows why larger
panel support in an interface is not evidence of high-order panel recovery.
No clustering ARI was measured in that check, and the planted panel need
not be the only or smallest useful explanation.

A second exploratory check was deliberately easier: 180 observations, 24
features, with feature 8 generated at means -3 and +3 and within-group standard
deviation 0.15; all other features were independent standard Gaussian noise.
The data seed remained 314, proposal seed 5. The default 80-step, three-restart,
128-row run **also failed to propose the singleton `(8,)`**, although feature
8 appeared in some larger prefixes. It completed 243 objective evaluations
and returned 33 distinct panels in approximately 0.247 seconds.

For diagnosis only, evaluating weights concentrated on the known true singleton
on the exact optimization sample gave these final-coefficient objectives:

| Bandwidth | Learned final objective | Oracle singleton objective |
|---|---:|---:|
| 0.7 | 0.317244 | 0.0342614 |
| 0.35 | 0.103580 | 0.00000457 |
| 1.4 | 0.629583 | 0.533538 |

Lower is better here. The oracle weights were **not supplied to the optimizer**.
This isolates a search failure on this particular example: a much better
solution exists for the implemented objective, but the three local runs did
not reach it. A wide initial geometry can amplify accidental nuisance
directions. These results argue against assuming that differentiability alone
resolves ATOMIC's search problem. They do not establish that all continuous
methods fail, and no hyperparameters were tuned to make these controls pass.

## Optimization and candidate rounding

The implementation uses Adam on the logits. It performs `steps + 1` objective
evaluations per completed restart so the final update is evaluated. With the
defaults there are `81 * 3 = 243` eigensolve/gradient evaluations. All evaluation
losses, gradient norms, graph diagnostics, objective counts, and elapsed times
are recorded. Runtime includes preprocessing, optimization, and candidate
formation, not merely scoring the returned panels. A time cap is checked
between evaluations; it is a soft cap, not a hard process timeout.

The first restart starts at uniform weights. Later ones add independent
Gaussian logit perturbations. Default bandwidths cycle through `0.7, 0.35,
1.4`. These are intentionally different scale hypotheses. Report variability
across seeds and bandwidths rather than treating one successful restart as a
robust method. Set a one-element bandwidth tuple to isolate initialization
effects.

At roughly one third, two thirds, and the end of a run, sort the weights and
propose every prefix size from one to the supplied maximum. Remove duplicate
panels. This is at most `3 * restarts * max_features` panel occurrences, with
fewer distinct candidates. It is not exhaustive enumeration: no collection of
all pairs or all subsets is evaluated inside this module. For example,
`max_features=8` allows sizes one through eight; it does not tell the optimizer
that eight features are correct or that any panel should be accepted.

Ranked prefixes can be poor approximations to a useful weighted metric. They
can contain unnecessary features, and an informative feature with a modest
weight may be missed. Re-evaluation and backward reduction are essential;
they remain separate from this module. Do not interpret effective feature
count `exp(H(w))` as a discovered integer panel size.

## Controls and decision rules for the broader experiment

1. Compare with random subsets under both recorded runtime and scored-candidate
   budgets. Charging only the final candidate count would give this optimizer
   unreported computation. EA objective evaluations and calibration work also
   need to be counted.
2. Include a well-separated singleton and a redundant multi-marker case. The
   minimal useful panel in the latter may be one feature, even when several
   features are associated with the known population.
3. Include curved low-dimensional clusters, useful panels of size four to
   eight, correlated Gaussian nuisance, heavy tails, unequal populations, and
   row counts or dimensions that expose poor discovery neighborhoods. Do not
   choose all controls to favor spectral separation.
4. Separate proposal recall from the score's ranking. If a useful candidate is
   proposed but the evaluator rejects it, better optimization is not the
   immediate remedy. If only a label-informed oracle can propose it, the
   discovery stage has not succeeded. Label-informed diagnostics are never
   eligible methods in the unsupervised comparison.
5. Compare the same frozen panel across independent validation rows and after
   feature deletion. Use external labels only for evaluation. Neither a small
   training eigenvalue nor a stable Gaussian split is evidence of a real
   population.

No neural network is needed to test whether gradients carry useful information
in this problem. If this relaxation consistently fails because its graph
initialization cannot discover high-order interactions, a gate network or
different dependence representation may be worth testing. Adding a neural
network would not itself repair a mismatched clustering objective.

## Relation to published work and novelty limits

[DUFS (Lindenbaum et al., NeurIPS 2021)](https://proceedings.neurips.cc/paper/2021/hash/0bc10d8a74dbafbf242e30433e83aa56-Abstract.html)
learns relaxed Bernoulli feature gates with a gated Laplacian score favoring
low-frequency features. The present deterministic simplex-weighted
second-eigenvalue objective is **not a reproduction of DUFS**, and no DUFS
performance claim applies to it. A proper DUFS baseline would require the
published method and its training details.

[Minimum Spectral Connectivity Projection Pursuit (Hofmeyr, Pavlidis and Eckley)](https://arxiv.org/abs/1509.01546)
already optimizes graph spectral separation in learned low-dimensional
projections and discusses its nonconvex, nonsmooth nature. Therefore “optimize
a spectral eigenvalue” is also not a new contribution.

This module is a deliberately small diagnostic proposal mechanism. A future
ATOMIC contribution would need its own substantiated mechanism for local
panel discovery, reduction, and verification, with a clear distinction from
these established approaches. Performance and novelty remain unverified.
