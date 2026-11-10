"""Recovery must preserve prior results and obey the recorded experiment plan."""
import json

import pytest

from scripts import run_research_radial_diagnostic as runner


@pytest.fixture
def stopped_run(tmp_path, monkeypatch):
    root = tmp_path / 'repo'
    monkeypatch.setattr(runner, 'ROOT', root)
    monkeypatch.setattr(runner, '__file__', str(root / 'scripts/run_research_radial_diagnostic.py'))
    parent = tmp_path / 'stopped'
    parent.mkdir()
    hashes = {}
    for relative in ('atomic_research/radial_panels.py', 'atomic_research/radial_diagnostics.py', 'scripts/run_research_radial_diagnostic.py'):
        source = root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(relative, encoding='utf-8')
        snapshot = parent / 'source_snapshot' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source.read_bytes())
        hashes[relative] = runner.digest(source)
    planned = [{'name': 'done', 'stage': 'candidate-ranking'}, {'name': 'unfinished', 'stage': 'candidate-ranking'}]
    completed = parent / 'done'
    completed.mkdir()
    report = {'job': planned[0], 'saved_marker': 'keep these exact bytes'}
    (completed / 'result.json').write_text(json.dumps(report), encoding='utf-8')
    for name in ('splits.npz', 'predictions.npz'):
        (completed / name).write_bytes(b'previous result bytes')
    manifest = {'status': 'failed', 'jobs': planned, 'completed': ['done'],
                'source_sha256': hashes, 'config': {'suite': 'pilot', 'seed_marker': 123}}
    (parent / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return parent, planned


def test_resume_preserves_parent_and_runs_only_incomplete_jobs(stopped_run, tmp_path, monkeypatch):
    parent, planned = stopped_run
    before = {p.relative_to(parent): p.read_bytes() for p in parent.rglob('*') if p.is_file()}
    called = []

    def run_case(job, directory, progress=None):
        called.append(job['name'])
        report = {'job': job}
        runner.write_json(directory / 'result.json', report)
        return report

    monkeypatch.setattr(runner, 'run_case', run_case)
    monkeypatch.setattr(runner, 'write_summary', lambda *args: None)
    output = tmp_path / 'continued'
    assert runner.main(['--resume', str(parent), '--output', str(output)]) == 0
    assert called == ['unfinished']
    after = {p.relative_to(parent): p.read_bytes() for p in parent.rglob('*') if p.is_file()}
    assert before == after
    run = next(output.iterdir())
    manifest = json.loads((run / 'manifest.json').read_text())
    assert manifest['jobs'] == planned
    assert manifest['status'] == 'complete'
    assert manifest['completed'] == ['done', 'unfinished']
    assert manifest['config']['seed_marker'] == 123
    for relative, expected in manifest['resume']['reused_jobs']['done']['files_sha256'].items():
        assert runner.digest(run / 'done' / relative) == expected == runner.digest(parent / 'done' / relative)


def test_resume_rejects_configuration_overrides(stopped_run):
    parent, _ = stopped_run
    with pytest.raises(SystemExit) as exc:
        runner.main(['--resume', str(parent), '--p', '100'])
    assert exc.value.code == 2


def test_resume_rejects_changed_experiment_code(stopped_run):
    parent, _ = stopped_run
    (runner.ROOT / 'atomic_research/radial_diagnostics.py').write_text('changed generator')
    with pytest.raises(ValueError, match='experiment/generator'):
        runner.load_resume(parent)


def test_resume_rejects_tampered_source_snapshot(stopped_run):
    parent, _ = stopped_run
    (parent / 'source_snapshot/atomic_research/radial_panels.py').write_text('tampered')
    with pytest.raises(ValueError, match='snapshot'):
        runner.load_resume(parent)
