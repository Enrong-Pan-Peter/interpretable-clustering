# Research prototype verification record

Local date: 14 September 2026. This records implementation checks, not scientific efficacy or novelty.

Final targeted command (isolated Python environment):

```powershell
.\.venv-research\Scripts\python.exe -m pytest tests/test_research_scoring.py tests/test_research_soft_graph.py tests/test_research_sparse_kmeans.py tests/test_research_harness.py -q --basetemp=C:/Users/Peter/Desktop/Github/ATOMIC_Clustering/results/research_test_tmp_20260914_4
```

Result: **57 passed in 6.08 seconds**. The temporary directory was absent before this run. Use a new scratch directory when repeating; pytest can clear an existing basetemp.

Checks cover score/partition agreement, zero-distance handling, legacy reproduction on continuous inputs, independence-null counterexamples, analytic eigenvalue gradients, sparse-weight optimization, label-blind splits/preprocessing, fixed reference units, shared eligibility, bounded search, panels above three features, matched shell marginals, external-label permutation invariance of selection/compression, invalid test partition reporting, incremental score records, and saved-rule prediction through the command line.

Final integration smoke:

```powershell
.\.venv-research\Scripts\python.exe scripts/run_research_diagnostics.py score-audit --dataset metabric --n 160 --budget 8 --reference-budget 8 --output results/research_final_checks_20260914
```

Completed in **3.9 seconds**, scoring 109 diagnostic panels: eight random panels plus contextual full-PAM50, singleton and leave-one-out panels. This is an explicitly reference-augmented score audit, not unsupervised panel discovery. Manifest and results:

`results/research_final_checks_20260914/score-audit_metabric_seed0_20260915T033708_467355Z/`

The folder timestamp is UTC; the local experiment date is still 14 September.

Earlier short empirical diagnostics are indexed at `results/research_checks_20260914/summary.md`. The main experiment plan reports their configurations and limitations. The smoke directories `results/research_smoke/` and `results/research_review_smoke/` contain earlier code versions, whose manifests identify their hashes. Do not merge them into a performance table without checking versions.

The complete 19-job pilot and the 40-job larger-panel sweep were prepared and listed, but **not executed**. Original ATOMIC implementation/tests were not broadly revalidated by this new-module check; historical code was not changed. No commit was created.
