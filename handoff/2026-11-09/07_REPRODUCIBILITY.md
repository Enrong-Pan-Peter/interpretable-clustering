# Open, inspect and continue

## First check the package

Extract the ZIP to a writable directory. Keep the complete folder structure. Run the bundled verifier from the extracted handoff directory:

```powershell
python .\verify_package.py
```

It uses only the Python standard library and checks the manifest's file sizes and SHA-256 hashes. It does not rerun clustering. `PACKAGE_REPORT.json` records packaging counts, read failures and intentional exclusions; `PACKAGE_VERIFICATION.json` records the archive verification performed before delivery. The hash list excludes itself to avoid a circular hash dependency.

## Python environment

The original project uses PowerShell and `.venv-research`. Its declared scientific dependencies are NumPy, SciPy, scikit-learn, pandas, pytest, threadpoolctl, xlrd and flowio. `requirements-research-lock.txt` records a pinned environment; `inventory/environment.json` records installed versions at handoff time. The broader `requirements.txt` includes legacy data/visualization dependencies. Neither requirements file establishes that a neural framework is installed.

For a new machine, create an environment inside `repository/` and install the requirements appropriate to the code being used. Do not assume Windows-specific paths in historical metadata exist on the new machine.

```powershell
Set-Location .\repository
python -m venv .venv-research
& ".\.venv-research\Scripts\python.exe" -m pip install -r requirements-research-lock.txt
```

The command form is important: `.\.venv-research`, not `..venv-research`. Activation is unnecessary when calling the executable directly. If exact locked versions are unavailable for the new interpreter/platform, record the change and run relevant checks instead of silently claiming identical reproduction.

## Read existing results before launching runs

The latest completed run is:

`results/research_feature_set_replication/20261027T163415_226880Z`.

Read its `summary.md`, `comparison.json`, `audit.json`, `assessment_decision.json` and manifest alongside the October 31 assessment. Earlier completed stages are mapped in chapters 02–04 and `inventory/run_index.json`.

No completed radial suite needs to be rerun merely to resume the thesis. The next proposed comparison is not implemented yet. A command for a new IDC/subject-aware run cannot honestly be supplied from this snapshot.

## Useful inspection commands

These inspect command interfaces or saved data; they do not start a long experiment:

```powershell
& ".\.venv-research\Scripts\python.exe" .\scripts\run_research_feature_set_replication.py --help
& ".\.venv-research\Scripts\python.exe" .\scripts\analyze_research_radial_search.py --help
& ".\.venv-research\Scripts\python.exe" .\scripts\run_research_radial_search.py --suite pilot --list-only
```

Use the matching test files for a changed component. A historical test-pass count in a report is not a current test run. Packaging verified file integrity, not all scientific computations. If running tests on a new platform, record interpreter/dependency versions and any differences.

## Preserve scientific provenance

- Make new timestamped run directories. Do not overwrite the only surviving historical CSV.
- Keep fit/search/validation/test roles distinct. Choosing or changing a method after looking at test outcomes makes those outcomes development evidence.
- Use grouped splits for repeated people, animals, donors or batches when that is the intended generalization unit.
- Preserve failures, controls, source snapshots, seeds, model states and candidate budgets.
- Exact recovery, assignment ARI, fidelity, feature count and split flags answer different questions. Report them separately.
- Frozen-run scripts validate code/configuration hashes. Do not weaken those checks just to make a relocated or modified run resume. Adapt paths transparently or start a new run with explicit provenance.
- Saved-state auditing validates the saved computation. An independent refit is a separate reproducibility exercise.

## What to ask the researcher only if still needed

Confirm the remaining proposal deadline if the handoff is resumed later. Decide which scientific grouping should anchor the next real-data test, and what limited expert input is feasible if a weakly supervised route is chosen. There is already permission to explore alternative model families and applications, and to prepare long-run commands. Do not ask again whether moving beyond EA, radial geometry, cytometry or three features is allowed.
