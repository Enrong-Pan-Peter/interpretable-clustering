from copy import deepcopy
from types import SimpleNamespace
import inspect
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from threadpoolctl import threadpool_limits

from atomic_research.datasets import DiscoveryScaler, split_rows, synthetic
from atomic_research import experiment
from atomic_research.search import FrozenObjective, ScoreCache, random_panels, search_discrete


def test_scaler_fits_discovery_only_and_handles_missing_columns():
    train = np.array([[1., np.nan, 4.], [3., np.nan, 4.]])
    scaler = DiscoveryScaler().fit(train)
    before = scaler.to_dict()
    changed_test = scaler.transform([[1000., 80., np.inf]])
    assert scaler.to_dict() == before
    assert np.isfinite(changed_test).all()
    assert changed_test[0, 0] == 998
    assert np.allclose(scaler.transform(train)[:, 0], [-1, 1])


def test_split_has_no_leakage_or_label_argument():
    splits = split_rows(163, 9)
    assert len(np.unique(np.concatenate(splits))) == 163
    assert sum(len(s) for s in splits) == 163
    assert list(inspect.signature(split_rows).parameters) == ["n", "seed"]


def test_frozen_comparison_units_do_not_depend_on_candidate_bank():
    references = [dict(graphcut=-.1, density=.2, legacy_graphcut=-.1, legacy_density=.5, valid=True, legacy_valid=True),
                  dict(graphcut=-.5, density=-.2, legacy_graphcut=-.5, legacy_density=.1, valid=True, legacy_valid=True)]
    objective = FrozenObjective(references)
    value = objective(references[0])
    moments = deepcopy(objective.moments)
    references.append(dict(references[0], graphcut=10000))
    assert objective(references[0]) == value
    assert objective.moments == moments


def test_legacy_and_new_objectives_share_reference_and_selection_eligibility():
    good = dict(graphcut=-.1, density=.2, legacy_graphcut=-.1, legacy_density=.5,
                valid=True, legacy_valid=True)
    bad = dict(good, graphcut=100, legacy_graphcut=100, valid=False)
    corrected = FrozenObjective([good, bad], "consistent")
    historical = FrozenObjective([good, bad], "legacy")
    assert corrected.reference_eligible == historical.reference_eligible == 1
    assert corrected.moments["graphcut"] == historical.moments["legacy_graphcut"]
    assert corrected(bad) == historical(bad) == -1e12


def test_search_budget_and_sizes_beyond_three():
    X = DiscoveryScaler().fit(synthetic("mean_shift", n=80, p=12).X)
    X = X.transform(synthetic("mean_shift", n=80, p=12).X)
    from atomic_research.scoring import score_panel
    with threadpool_limits(limits=1):
        objective = FrozenObjective([score_panel(X, (0,)), score_panel(X, (1, 2))])
        for method in ("random", "forward", "evolutionary"):
            cache = ScoreCache(X, objective, 16)
            search_discrete(method, cache, 8, seed=2)
            assert len(cache.records) == 16
            assert max(len(p) for p in cache.records) > 3
            assert all(1 <= len(p) <= 8 for p in cache.records)
            assert cache.scoring_seconds > 0
            assert all("y" not in r for r in cache.records.values())
    assert len(random_panels(1, 8, 500, 0)) == 1


def test_shell_nuisance_matches_population_marginals_without_label_signal():
    ds = synthetic("shells", n=16000, p=8, signal_features=5, seed=13)
    informative = list(ds.reference_panel)
    nuisance = [j for j in range(8) if j not in informative]
    assert abs(ds.X[:, informative].var() - ds.X[:, nuisance].var()) < .035
    signal_gap = abs(ds.X[ds.y == 1][:, informative].var() - ds.X[ds.y == 0][:, informative].var())
    noise_gap = abs(ds.X[ds.y == 1][:, nuisance].var() - ds.X[ds.y == 0][:, nuisance].var())
    assert signal_gap > .5
    assert noise_gap < .04


def test_external_label_changes_leave_selected_and_compressed_panels_unchanged(tmp_path, monkeypatch):
    args = SimpleNamespace(mode="search", dataset="mean_shift", n=80, p=10, signal_features=5,
                           seed=7, separation=3., contrast=None, output=str(tmp_path), max_features=5,
                           reference_budget=5, objective="consistent", budget=8, methods=["random", "forward", "evolutionary"],
                           splitter="spectral", k=5, fidelity=.9)
    original = experiment.load_dataset
    first = experiment.run(args)
    def permuted_annotations(*a, **kw):
        data = original(*a, **kw)
        data.y = np.random.default_rng(909).permutation(data.y)
        return data
    monkeypatch.setattr(experiment, "load_dataset", permuted_annotations)
    second = experiment.run(args)
    assert first != second
    reports = [json.loads((d / "summary.json").read_text()) for d in (first, second)]
    for method in args.methods:
        for field in ("panel", "reduced_panel", "reduction_trace"):
            assert reports[0]["methods"][method][field] == reports[1]["methods"][method][field]
    for directory in (first, second):
        assert json.loads((directory / "manifest.json").read_text())["status"] == "complete"
        assert (directory / "random_assignment.npz").exists()
        assert len((directory / "random_progress.jsonl").read_text().splitlines()) == 8
    # Saved assignment and preprocessing reproduce a new command-line prediction.
    import pandas as pd
    data = original("mean_shift", n=80, p=10, signal_features=5, seed=7)
    protocol = json.loads((first / "data_protocol.json").read_text())
    raw = data.X[protocol["rows"]["discovery"][:10]]
    csv_path, predicted_path = tmp_path / "input.csv", tmp_path / "predicted.csv"
    pd.DataFrame(raw, columns=data.names).to_csv(csv_path, index=False)
    subprocess.run([sys.executable, str(Path(experiment.ROOT) / "scripts/predict_research_panel.py"),
                    str(first), "random", str(csv_path), "--output", str(predicted_path)], check=True)
    expected = np.load(first / "random_assignment.npz")["labels"][:10]
    assert np.array_equal(pd.read_csv(predicted_path).algorithm_cluster, expected)


def test_null_singleton_is_exactly_invariant():
    data = synthetic("bimodal", n=80, p=4, signal_features=1, seed=4)
    X = DiscoveryScaler().fit(data.X).transform(data.X)
    with threadpool_limits(limits=1):
        result = experiment.null_audit(SimpleNamespace(seed=0, k=5, permutations=3, splitter="spectral"), X, data)
    assert result["graphcut_independence_null"]["degenerate"]
    assert result["graphcut_independence_null"]["p_value"] == 1.


def test_pruning_uses_only_frozen_algorithm_partition():
    rng = np.random.default_rng(3)
    train = rng.normal(size=(100, 3))
    validation = rng.normal(size=(50, 3))
    train[:, 1] = train[:, 0]
    validation[:, 1] = validation[:, 0]
    labels = (train[:, 0] > 0).astype(int)
    with threadpool_limits(limits=1):
        reduced, trace, _ = experiment.compress_panel(train, labels, validation, (0, 1), .95)
    assert len(reduced) == 1
    assert trace[-1]["validation_fidelity"] >= .95


def test_invalid_test_reclustering_is_reported_and_not_scored(tmp_path, monkeypatch):
    from atomic_research.scoring import score_panel
    data = synthetic("bimodal", n=80, p=4, signal_features=1, seed=2)
    X = DiscoveryScaler().fit(data.X).transform(data.X)
    with threadpool_limits(limits=1):
        original = score_panel(X[:40], data.reference_panel, k=5)
        def invalid_reclustering(values, panel, **kwargs):
            return dict(original, labels=np.arange(len(values)) % 2, valid=False, reason="cluster_too_small")
        monkeypatch.setattr(experiment, "score_panel", invalid_reclustering)
        outcome = experiment.fit_and_report(original, X[:40], X[40:60], X[60:],
                    data.y[:40], data.y[60:], data,
                    SimpleNamespace(seed=2, splitter="spectral", k=5, fidelity=.95), tmp_path, "demo")
    assert outcome["test_reclustered_ari"] is None
    assert outcome["test_replication_fidelity"] is None
    assert outcome["test_independent_reclustering"]["reason"] == "cluster_too_small"
