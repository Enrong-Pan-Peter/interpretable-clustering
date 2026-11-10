# Native panel replication

Sparse two-means is an established baseline. This experiment preserves its assignment rule, independently fits two discovery samples, and shortens each rule using a training-only prefix ladder. It does not test whether clusters exist or establish novelty.

Empirical: observed validation disagreement <= the prescribed tolerance. Bounded: one-sided Clopper–Pearson upper disagreement <= tolerance, with Bonferroni across at most 2*cap prefixes in a case. Conditional on fixed discovery fits and independent identically distributed validation rows, this controls the family of fidelity bounds; it does not cover cluster truth, independent cohorts, all suite cases jointly, or future tuning.

## Each learner and selected panel

Missing bounded panels are reported, not replaced with a favorable candidate. Test error can exceed the tolerance by sampling variation even when a population-risk bound holds; a single test exceedance is not proof of bound failure.

| Case | p | Planted | Seed | Learner | Policy | Full support | Selected size | Val error | Val upper | Test error | Full test ARI | Selected test ARI |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| mean_shift | 12 | 5 | 19 | A | empirical | 12 | 2 | 0.050 | 0.223 | 0.050 | 0.139 | 0.139 |
| mean_shift | 12 | 5 | 19 | A | bounded | 12 | none | — | — | — | 0.139 | — |
| mean_shift | 12 | 5 | 19 | B | empirical | 12 | 3 | 0.050 | 0.223 | 0.125 | -0.016 | -0.023 |
| mean_shift | 12 | 5 | 19 | B | bounded | 12 | none | — | — | — | -0.016 | — |

## Independent rediscovery

Each A/B model has its own feature panel and scaler. Label orientation is aligned on validation only for this comparison; that alignment never changes the prefix-vs-teacher fidelity calculation or selected rules. Jaccard measures exact feature overlap; equivalent biological substitutes may differ.

| Case | p | Planted | Seed | Policy | Val agreement ARI | Test agreement ARI | Test disagreement | Feature Jaccard |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| mean_shift | 12 | 5 | 19 | full | -0.026 | 0.016 | 0.400 | 1.000 |
| mean_shift | 12 | 5 | 19 | empirical | -0.027 | 0.183 | 0.275 | 0.250 |
| mean_shift | 12 | 5 | 19 | bounded | — | — | — | — |

Full prefix curves, cluster sizes, source hashes, prediction arrays and exact linear rules in original feature units are saved per case. Every rule applies its recorded discovery-median imputation first. Rule coefficients are not calibrated class probabilities.

Real-data results reuse the same cached cohort and feature universe. The iid assumption is a model assumption, not a donor/external-cohort validation. Planted signal count is not guaranteed to be the minimum useful panel size. Correlated Gaussian controls may be highly stable despite containing only one generated population.
