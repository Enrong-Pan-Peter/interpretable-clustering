# Start here: ATOMIC clustering thesis handoff

Prepared November 9–10, 2026, for a new research agent. This is a handoff of work already done, not a claim that the thesis method is finished.

## Read in this order

1. This file, then `01_USER_REQUEST_AND_TRACE.md` for the researcher's priorities.
2. `05_DECISIONS_AND_OBSTACLES.md` for the most important lessons and unresolved choices.
3. `04_RADIAL_WORK_AND_PIVOT.md` for the latest implemented method, completed results and proposed pivot.
4. Use `02_EARLY_EXPERIMENTS.md` and `03_DIAGNOSTICS_AND_KERNELS.md` when investigating earlier attempts. They are detailed history, not an instruction to repeat every experiment.
5. Use `06_DATA_AND_CODE_MAP.md`, `07_REPRODUCIBILITY.md` and the machine-readable inventory to inspect evidence or run code.

In the ZIP, `repository/` preserves the source repository's relative layout. Paths beginning `docs/`, `scripts/`, `results/`, `data/`, `atomicplus/` or `atomic_research/` in these notes are relative to `repository/`. Original proposal and meeting materials are in `attachments/`. Other numbered handoff files are beside this guide.

## What the researcher wants

Find meaningful clusters supported by small, verifiable feature sets. Ideally, show the cluster shape and provide a readable way to assign new observations. Scientific usefulness matters more than an attractive internal score. Feature sets may contain more than three variables when their value can be explained. The researcher explicitly permits a major change of method, application or proposal; evolutionary computing, a tree, radial geometry and cytometry are not requirements.

Use the words **feature sets**, not the old term used in many historical filenames. Preserve historical names when referring to code and evidence.

## Current state in plain language

There is substantial working code and a long experiment history. Early ATOMIC/ATOMIC+ experiments found evaluation problems, weak objectives, misleading claims about evolutionary search, and real-data difficulties. September experiments separated candidate search, score ranking, representation, compression, reproducibility and split acceptance. Kernel and rank-constrained models improved particular synthetic cases but did not solve general nonconvex discovery.

The latest implemented method fits a restricted radial density model to a selected feature set. A budgeted, kernel-guided search can discover useful sets beyond three features on clearly separated synthetic shells. It does not enumerate all allowed sets. Its native rule is an explicit threshold on a squared standardized radius. This is a real implemented result, but its geometry is narrow and its novelty and real-world usefulness are not established.

The latest frozen replication has 126 jobs, 252 method runs and 64,512 fitted candidates. These are 63 data blocks searched twice, with shared structure between some conditions—not 126 independent populations. Clear 24-feature shells gave 30/30 exact recoveries; dependent Gaussian nuisance groups gave 18/18. At 72 features recovery was 12/18 and only 3/9 datasets succeeded under both search seeds. With weaker separation, mean test ARI was 0.398; models given the true feature set averaged 0.612. Search, model limitations and finite-sample ranking all remain relevant. See `docs/research/feature-set-replication-assessment-2026-10-31.md`.

The November 5 recommendation was to preserve that method and pivot the main question toward **small original-feature sets that support useful assignments on new subjects or samples**. Existing sparse or neural methods should be baselines. A specific shortcoming must be demonstrated before designing a new mechanism. This is a proposed direction, not a completed replacement. No IDC/DUFS/GroupFS reproduction or new subject-aware comparison runner was implemented in that reassessment or during this packaging task.

## Immediate next decision

On November 5 the researcher said the revised proposal should be settled within one week. As of this handoff, that decision is urgent; the deadline may need reconfirming if a later agent resumes much later.

Read `docs/research/thesis-direction-reassessment-2026-11-05.md`. The preferred next build is a small subject-aware comparison using existing methods, starting with the activity data already available. Check whether credible full-feature clusters exist, whether selected features suffice for prediction, and whether that survives a subject split. Add weak supervision if it supplies missing task meaning. The researcher remains open to a better justified alternative; do not treat the last assistant's recommendation as an irrevocable user commitment.

## Claims you must not repeat

- The EA has not demonstrated a reliable advantage in the tested settings. This is not a proof that all evolutionary search fails.
- Strong enumeration results do not establish efficient discovery, and successful growth from an oracle seed is not autonomous discovery.
- Stable assignments or fidelity to a teacher do not establish real clusters, biological meaning or calibrated uncertainty.
- Independent-column permutation tests dependence, not a universal absence of clusters.
- A low-dimensional embedding can still depend on many original measurements.
- Pure leaves or high average node purity do not establish good final clustering. Legacy Levine tree code used evaluation labels in stopping.
- There is no established novelty claim for the current method or the proposed pivot.
- Huge numerical audit counts are saved-state consistency checks, not independent replications or proof of validity.

## Evidence precedence

Use current code and preserved run artifacts to verify execution; use the matching protocol and dated assessment for interpretation. Preserve old reports as history. `docs/CORRECTIONS.md`, `docs/research-assessment-2026-09-09.md`, and later stage audits qualify or overturn many early claims. Some old CSVs no longer contain the runs described by their old writeups; see `inventory/csv_inventory.json` and the early-history chapter. Never silently promote a historical claim to a newly verified result.

## Package limits

The package includes source code, tests, original notes, substantive saved results, model/prediction/data arrays, source snapshots, manageable input datasets, the original proposal and meeting transcript. Large METABRIC assay matrices are inventoried instead of bundled; the full HAR archive is bundled instead of duplicate extracted sensor arrays. Environments, Git internals and temporary test products are omitted. `inventory/omitted_files.json` and `PACKAGE_REPORT.json` give exact exclusions and any read failures.

This is a reconstructed research trace from saved records and the visible conversation, not a verbatim export of every chat. It contains documented reasons, tradeoffs and decisions. It does not contain private internal reasoning or claim to recover missing historical outputs. No new clustering experiment was run to prepare it.
