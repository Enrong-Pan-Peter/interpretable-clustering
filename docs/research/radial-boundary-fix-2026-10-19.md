# Radial pilot boundary repair and recovery

The 36-job pilot is complete. Its [summary](../../results/research_radial_diagnostic/20261020T021208_103657Z/summary.md) and [independent saved-state audit](../../results/research_radial_diagnostic/20261020T021208_103657Z/audit.json) are available locally. The directory timestamp is UTC, already October 20 at completion.

## Cause and repair

The original run failed in job 18, `single_shell_d5_p24_seed1213`, on its last candidate, `c09_random`. During L-BFGS-B line search, a component location reached `-6.938893903907228e-18` despite its zero lower bound. The normalizer correctly rejects negative locations, so this floating-point boundary excursion stopped the experiment.

The optimizer adapter now projects only excursions within 64 machine epsilons times the bound scale back onto the declared bounds. It still rejects nonfinite values and material violations. The public normalizer remains strict. Fitted diagnostics record the number and maximum size of corrections. Replaying the failed candidate completed successfully with three corrections, each no larger than `6.938893903907228e-18`.

This changes numerical boundary handling, not the fitness, density family, data, seeds, candidate panels, or selection protocol.

## Recovery and provenance

Original failed run, preserved: `results/research_radial_diagnostic/20261016T150124_340504Z`.

Completed recovery: `results/research_radial_diagnostic/20261020T021208_103657Z`.

The recovery reused 17 completed jobs byte-for-byte and ran the other 19 jobs, restarting the incomplete job from its first candidate. The new manifest records predecessor source hashes, a copy of the predecessor manifest, and hashes for the reused artifacts; predecessor source snapshots are also retained. Resume rejects changes to the experimental configuration or helper code and accepts only the current core or the specifically reviewed predecessor core. The original files are untouched.

The command below has **already been run successfully**; it is recorded for reproducibility, not as an outstanding task:

```powershell
Set-Location "C:\Users\Peter\Desktop\Github\ATOMIC_Clustering"
& ".\.venv-research\Scripts\python.exe" ".\scripts\run_research_radial_diagnostic.py" --resume ".\results\research_radial_diagnostic\20261016T150124_340504Z"
```

## Verification

- **78 tests passed** across the radial model, diagnostic pipeline, optimizer boundary regression, and resume tests. Coverage includes the exact failed candidate, rejection of substantial boundary violations, unchanged completed artifacts, and rejection of incompatible or tampered resume sources.
- **All 36 jobs and 360 candidates completed.**
- The independent saved-state auditor passed **18,031 checks with zero errors**, including reused-artifact hashes, numerical densities, exported native rules, metrics, and validation selection. This verifies saved computation, not independent experimental replication or scientific cluster validity.

The next research step is to interpret the completed pilot before changing the method. Candidate lists still include the supplied informative panel, so these results assess representation and ranking rather than autonomous feature discovery.
