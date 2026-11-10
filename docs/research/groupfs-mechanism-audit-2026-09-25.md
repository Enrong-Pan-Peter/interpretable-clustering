# GroupFS mechanisms and a focused kernel-projection prototype

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: primary-source mechanism audit and implementation advice
- Origin Date: 2026-09-25
- Verification Status: READ/ANALYZED; paper equations and public author code inspected; GroupFS not installed, executed or reproduced
- Version Label: groupfs_mechanism_v1
- Primary paper: [arXiv 2511.09166v1](https://arxiv.org/html/2511.09166v1), with [AAAI 2026 publication](https://ojs.aaai.org/index.php/AAAI/article/view/39521)
- Author implementation: [ShiraLifshitz/GroupFS](https://github.com/ShiraLifshitz/GroupFS), `main` as returned by the web tool on this date. Its retrieved history shows head [b08d8b3fb5af697496caec9eda07fdcfbe0d693a](https://github.com/ShiraLifshitz/GroupFS/commit/b08d8b3fb5af697496caec9eda07fdcfbe0d693a), dated 2026-02-14. No local byte-for-byte checkout/hash verification was completed.
- Local comparison: `atomic_research/soft_graph.py`; no historical source/results changed

**A learned sparse sample projection is worth implementing, but it is not GroupFS's Q matrix.** The faithful inspiration is joint selection and graph reconstruction. Learning signed combinations of original features changes the representation beyond GroupFS and can directly address the distributed-signal failure of a diagonal feature metric. It should be described as a GroupFS-inspired sparse kernel-projection experiment, with spectral projection-pursuit prior art, rather than a reproduction or established new method.

## What GroupFS learns

Let X be N samples by d original features, and C the number of feature groups. Its soft feature-to-group matrix is M, of shape d by C. Stochastic group gates z give feature gates `g=M z`; sample data remain `X_tilde=X diag(g)`. The learned C-by-C matrix Q instead forms `F=M Q`, a **feature** embedding used for feature-graph regularization. It is not applied to samples as XQ. C is supplied or chosen by a separate spectral/Procrustes heuristic; the integer group count is not differentiated. D denotes a graph degree matrix, computed from affinities, not another freely learned embedding. The paper's sample loss is diffusion smoothness, not minimization of the second Laplacian eigenvalue. [Paper, §§3–5 and Appendix D](https://arxiv.org/html/2511.09166v1).

The public model names Q `W`. It samples Gumbel-softmax memberships, clips noisy group gates to [0,1], and implements:

\[
\mathcal L_s=-\operatorname{tr}(\widetilde X^T P^2\widetilde X)/(Bd),
\]

\[
\mathcal L_f=\operatorname{tr}(F^T L_{\rm feat}F)/(dC),\quad
\mathcal L_o=\|F^TF-I\|_F^2/(dC).
\]

It centers and column-normalizes F during loss evaluation. Its sparsity term weights each group's gate-on penalty by its soft fraction of features, then averages over C. Total loss combines sample smoothness, feature smoothness, orthogonality and sparsity. None of these terms directly estimates annotation ARI or establishes cluster existence. [Author `model.py`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/model.py).

## Kernel and graph construction in the author code

`affinity_mat` computes dense Euclidean distances and uses

\[
W_{ij}=\exp\{-\|x_i-x_j\|^2/(\gamma_i\gamma_j)\},\quad
P_{ij}=W_{ij}/\sum_k W_{ik}.
\]

Local scale gamma_i is the seventh-neighbor distance by default. Sorting includes the self-distance at index zero, so index seven means the seventh nonself neighbor absent distance ties. Scales are floored at 1e-5. The implementation retains self-affinities `W_ii=1` and does not sparsify to a binary kNN graph. The distance order statistics remain in the PyTorch gradient path; bandwidths are not detached. This still has a neighbor-count choice and becomes piecewise smooth around changes in nearest-neighbor identity. [Author `utils.py`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/utils.py).

The feature graph is constructed from `X.T` before training. For standardized columns, Euclidean column distance is closely connected to signed correlation: exactly `2N(1-r)` when both columns have mean zero and squared norm N. Thus this graph makes strongly positively correlated columns close; it does not automatically regard sign-reversed measurements as equivalent. The synthetic example consists of two blocks of noisy copies of the two moon coordinates plus independent Gaussian nuisance. [Author `data.py`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/data.py).

`training.py` freezes the resulting feature Laplacian and initializes memberships from its spectral clustering. The **sample** graph is rebuilt on the gated input in every batch. Batches drop their last incomplete block. Labels accompany batches but are not passed into the gradient loss; k-means annotation metrics are logged separately. These are distinct facts: the training objective is label-free, while subsequent benchmark reporting can use labels. [Author `training.py`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/training.py).

## Details that should not be copied without a decision

The public gate penalty has a concrete formula mismatch: its `regulaizer` returns `0.5*(1+erf(alpha/sigma*sqrt(2)))`, mathematically **Phi(2 alpha/sigma)**. For the implemented gate `clip(alpha+sigma*epsilon,0,1)`, the actual activation probability is **Phi(alpha/sigma)**. This changes regularization; its numerical impact was not measured here. Reproducing the public implementation and implementing the paper's probability are different choices. [Author `model.py`, `FeatureSelector.regulaizer`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/model.py).

A mathematical limitation of the orthogonality target also follows from the equations: rows of M sum to one, so after centering across features, `rank(M_centered)<=C-1`. Therefore centered `F=M Q` cannot have C exactly orthonormal columns. This is a soft diversity penalty with an unavoidable residual, not an exact orthogonality guarantee. This observation does not imply the method cannot work.

The author demo chooses the lowest final weighted loss across its parameter grid, then prints k-means accuracy/ARI as successive ranked groups are included. Those are original-feature subsets followed by new k-means fits, not an exported native kernel assignment. Comparing raw total losses across changing regularization coefficients is not automatically a comparable statistical validation criterion. [Author `mainGroupFS.py`](https://raw.githubusercontent.com/ShiraLifshitz/GroupFS/main/mainGroupFS.py).

The paper's fixed-budget description uses a local maximum of clustering accuracy to choose the GroupFS group budget; its adaptive-budget scenario explicitly uses accuracy-guided choice. That protocol is not an appropriate template for our label-blind panel-size selection. [Paper, §5.3](https://arxiv.org/html/2511.09166v1). Our frozen discovery/validation/test separation should remain.

## Why noise can still dominate: implications, not proven GroupFS failures

The following are deductions about the mechanism, not experimental claims about the published method:

- Local bandwidth adapts distance scale after neighbors have been determined. If many nuisance coordinates give the wrong neighbors, rescaling alone does not identify the missing informative panel.
- Fixed feature-graph regularization can encourage correlated nuisance groups. A coherent group of measurements is not necessarily a useful grouping of samples.
- Grouping reduces the number of gate parameters and can share evidence among related features. It does not guarantee discovery of features whose useful joint relation lacks strong column similarity. Our isotropic shell signal has zero raw pairwise correlations; its squared correlations can be almost cancelling. That weakens this particular grouping cue, without proving GroupFS must fail.
- Rebuilding a graph under the current mask permits improvement, but also creates a feedback loop in which a feature makes its own values smooth on the graph it helped create. A kernel does not supply an external truth signal.
- Two diffusion steps combine paths. They can smooth noise, but can also propagate bad cross-group edges; there is no universal guarantee that squaring P repairs a noise-dominated graph.

These qualify several older statements in `docs/ec-handoff-external-review.md`: self-tuning does not remove all tuning; Gaussian nuisance does not guarantee a correctly ranked initialization; and lack of redundant groups is not by itself a proof that GroupFS cannot work. No edits to that historical document were made.

## What our existing soft graph does and what the prototype should change

`atomic_research/soft_graph.py` already learns a diagonal metric through simplex feature weights and a dense RBF kernel. It minimizes the second normalized-Laplacian eigenvalue plus entropy and degree penalties, uses fixed bandwidths per restart, removes self-loops, and adds an affinity floor. It emits unweighted feature-prefix proposals for a separate evaluator. It does not learn M/Q, use feature-group gates, apply a two-step diffusion trace loss, or preserve an out-of-sample spectral model. Therefore merely adding the word “kernel” would not address the earlier failure.

A focused next model can learn a row-sparse matrix A and retain `Z=X A`, its kernel and its assignment rule. Nonzero rows identify the original-feature panel. Off-diagonal entries of `A A^T` permit feature combinations absent from the current diagonal metric. Directly learning projections by reducing spectral connectivity has close prior art: [Hofmeyr, Pavlidis and Eckley, *Minimum Spectral Connectivity Projection Pursuit*](https://arxiv.org/abs/1509.01546). Its existence makes an immediate novelty claim inappropriate, but does not make a useful prototype less worthwhile.

The smallest informative comparison is matched diagonal versus learned one-/two-dimensional projection, with the same support budget, discovery rows, initialization budget and kernel. Compare lambda_2 with `lambda_2/(lambda_3+epsilon)` as separate objective arms. The ratio can distinguish a two-way bottleneck from more fragmented geometry; it does not certify real clusters. Keep fixed-bandwidth RBF first so analytic gradients can be verified cleanly. Add self-tuning as a declared ablation, with derivatives through the local scales or an explicit approximation statement.

Implementation priorities:

1. **Constrain support during training and prevent collapse.** A row support cap and norm/orthogonality constraint control the transformation. Record actual rank and projected variance; nonzero coefficient norm alone does not exclude directions near a sample nullspace. At p near or above discovery n, dense projections have enough flexibility to fit accidental sample structure.
2. **Check the actual native partition.** Small eigenvalues can come from tiny islands. Record component/child sizes, minimum mass, spectral gaps, degree imbalance, scale floors and affinity-floor influence. A degree penalty is not a minimum-group-size guarantee.
3. **Retain the learned representation.** Save A, original-coordinate scaler, support, training projections, kernel parameters, training degrees/eigenvectors and the spectral readout. Compare its frozen transfer with an unweighted-panel refit explicitly rather than replacing the model silently.
4. **Make extension numerical conditions visible.** Nyström extension of normalized affinity divides by the affinity eigenvalue `mu_2=1-lambda_2`; guard values near zero. In a self-tuned kernel, compute each new point's scale against frozen projected discovery neighbors and retain training scales/degrees. Do not recluster the test set to assign its points.
5. **Start with a small paired experiment.** Use distributed mean-shift p=200/s=12, a curved positive control, and independent/correlated Gaussian plus uniform one-population controls. A linear projection can help mean-shift geometry; it does not by itself supply the squared/radial geometry required by shells. Keep a squared-feature extension as a separate subsequent arm with support counted in original features.

For the fixed-bandwidth metric, a useful derivative check is: if `H_ij=d(loss)/d(delta_ij²)` uses symmetric undirected-edge coefficients and `delta_ij²=||(x_i-x_j)A||²`, then `grad_A=2 X.T L_H X A`. Eigenvalue-ratio gradients additionally differentiate the denominator. Numerical finite-difference checks should avoid eigenvalue ties and support-switch boundaries, where classical gradients need not exist.

This is a concrete implementation direction, not a request for another broad audit. Success should mean improved native held-out clustering and useful original-feature support under a frozen comparison, with failure and null behavior visible. GroupFS's grouping machinery remains an optional later branch if correlated feature groups prove helpful. No source inspection here demonstrates that the new prototype works, controls false splits, or is novel.
