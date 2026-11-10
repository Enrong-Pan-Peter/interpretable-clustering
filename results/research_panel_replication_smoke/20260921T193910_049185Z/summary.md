# Native panel replication

Sparse two-means is an established baseline. This experiment preserves its assignment rule, independently fits two discovery samples, and shortens each rule using a training-only prefix ladder. It does not test whether clusters exist or establish novelty.

Empirical: observed validation disagreement <= the prescribed tolerance. Bounded: one-sided Clopper–Pearson upper disagreement <= tolerance, with Bonferroni across at most 2*cap prefixes in a case. Conditional on fixed discovery fits and independent identically distributed validation rows, this controls the family of fidelity bounds; it does not cover cluster truth, independent cohorts, all suite cases jointly, or future tuning.

## Each learner and selected panel

Missing bounded panels are reported, not replaced with a favorable candidate. Test error can exceed the tolerance by sampling variation even when a population-risk bound holds; a single test exceedance is not proof of bound failure.

| Case | p | Planted | Seed | Learner | Policy | Full support | Selected size | Val error | Val upper | Test error | Full test ARI | Selected test ARI | Supplied-panel oracle ARI |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| null_independent | 200 | — | 19 | A | empirical | 200 | 1 | 0.000 | 0.032 | 0.010 | — | — | — |
| null_independent | 200 | — | 19 | A | bounded | 200 | 1 | 0.000 | 0.032 | 0.010 | — | — | — |
| null_independent | 200 | — | 19 | B | empirical | 200 | 1 | 0.010 | 0.052 | 0.015 | — | — | — |
| null_independent | 200 | — | 19 | B | bounded | 200 | 2 | 0.005 | 0.043 | 0.015 | — | — | — |
| null_correlated | 200 | — | 19 | A | empirical | 31 | 3 | 0.050 | 0.113 | 0.075 | — | — | — |
| null_correlated | 200 | — | 19 | A | bounded | 31 | 16 | 0.005 | 0.043 | 0.015 | — | — | — |
| null_correlated | 200 | — | 19 | B | empirical | 30 | 5 | 0.035 | 0.092 | 0.040 | — | — | — |
| null_correlated | 200 | — | 19 | B | bounded | 30 | 11 | 0.005 | 0.043 | 0.015 | — | — | — |

## Independent rediscovery

Each A/B model has its own feature panel and scaler. Label orientation is aligned on validation only for this comparison; that alignment never changes the prefix-vs-teacher fidelity calculation or selected rules. Jaccard measures exact feature overlap; equivalent biological substitutes may differ.

| Case | p | Planted | Seed | Policy | Val agreement ARI | Test agreement ARI | Test disagreement | Feature Jaccard | Both val groups >=5 | Both test groups >=5 |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| null_independent | 200 | — | 19 | full | -0.004 | -0.005 | 0.505 | 1.000 | True | True |
| null_independent | 200 | — | 19 | empirical | -0.002 | -0.005 | 0.500 | 0.000 | True | True |
| null_independent | 200 | — | 19 | bounded | -0.003 | -0.005 | 0.500 | 0.000 | True | True |
| null_correlated | 200 | — | 19 | full | 0.791 | 0.704 | 0.080 | 0.017 | True | True |
| null_correlated | 200 | — | 19 | empirical | 0.606 | 0.531 | 0.135 | 0.000 | True | True |
| null_correlated | 200 | — | 19 | bounded | 0.791 | 0.704 | 0.080 | 0.000 | True | True |

Full prefix curves, cluster sizes, source hashes, prediction arrays and exact linear rules in original feature units are saved per case. Every rule applies its recorded discovery-median imputation first. Rule coefficients are not calibrated class probabilities.

Real-data results reuse the same cached cohort and feature universe. The iid assumption is a model assumption, not a donor/external-cohort validation. Planted signal count is not guaranteed to be the minimum useful panel size. Correlated Gaussian controls may be highly stable despite containing only one generated population.

The mean-shift oracle fits ordinary unweighted two-means after being supplied the planted panel, on each learner's own discovery rows. It is an ability benchmark, not autonomous feature discovery or the same optimizer. Oracle results never enter model or prefix selection.
