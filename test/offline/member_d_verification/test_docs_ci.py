"""Routing and negative evidence for document-only CI
no live services."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / 'scripts/ci'


def load(name):
    spec = importlib.util.spec_from_file_location(name, DIRECTORY / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scope = load('ci_scope')
summary = load('check_ci_results')
documents = load('check_documents')


def row(path, old='100644', new='100644', status='M'):
    return {'path': path, 'old_mode': old, 'new_mode': new, 'status': status}


@pytest.mark.parametrize('path', ['README.md', 'docs/submission/contents-and-build.md',
                                  'AI-log/Member-E/log.md', 'docs/ai-use-log.yaml',
                                  'Report.pdf', 'report-assets/token-observations.svg'])
def test_explicit_documents_use_fast_pr_route(path):
    assert scope.mode([row(path)], 'pull_request') == 'docs'
    assert scope.mode([row(path)], 'push') == 'full'


@pytest.mark.parametrize('path', ['src/example.py', 'main.py', 'requirements.txt', 'pyproject.toml',
                                  '.github/workflows/ci.yml', '.opencode/permissions.jsonc',
                                  'AGENTS.md', 'Prompt.md', '.agent/rules.md', 'prompts/runtime.md',
                                  'docs/code-governance/dependency-reviews.md',
                                  'docs/req/requirements.yaml', 'unknown.config', 'docs/executable.sh'])
def test_protected_unknown_and_mixed_changes_require_full_ci(path):
    assert scope.mode([row('README.md'), row(path)], 'pull_request') == 'full'


@pytest.mark.parametrize('old,new', [('120000', '100644'), ('100644', '120000'),
                                    ('100644', '100755'), ('160000', '000000')])
def test_symlinks_executables_and_type_changes_require_full_ci(old, new):
    assert scope.mode([row('docs/note.md', old, new)], 'pull_request') == 'full'


def test_empty_or_unknown_event_is_full():
    assert scope.mode([], 'pull_request') == 'full'
    assert scope.mode([row('README.md')], 'unexpected') == 'full'


def needs(mode):
    state = 'skipped' if mode == 'docs' else 'success'
    data = {job: {'result': state} for jobs in summary.GATES.values() for job in jobs}
    data.update(scope={'result': 'success', 'outputs': {'mode': mode}},
                documents={'result': 'success' if mode == 'docs' else 'skipped'})
    return data


@pytest.mark.parametrize('gate', summary.GATES)
def test_fixed_gate_accepts_only_verified_route(gate):
    assert not summary.problems(gate, needs('full'))
    assert not summary.problems(gate, needs('docs'))
    for state in ['failure', 'cancelled', 'skipped', '']:
        n = needs('docs')
        n['documents']['result'] = state
        assert summary.problems(gate, n)
        n = needs('full')
        n[summary.GATES[gate][0]]['result'] = state
        assert summary.problems(gate, n)
    for selected in ['unknown', '', None]:
        n = needs('docs')
        n['scope']['outputs']['mode'] = selected
        assert summary.problems(gate, n)
    for state in ['failure', 'cancelled', 'skipped', '']:
        n = needs('docs')
        n['scope']['result'] = state
        assert summary.problems(gate, n)


def test_docs_summary_does_not_mask_failed_worker_or_missing_result():
    for state in ['failure', 'cancelled', 'success', '']:
        n = needs('docs')
        n['test']['result'] = state
        assert summary.problems('required tests', n)
    n = needs('docs')
    del n['lint']
    assert summary.problems('security checks', n)
    assert summary.problems('unknown', needs('full'))


def test_invalid_summary_input_fails(monkeypatch):
    monkeypatch.setenv('CI_GATE', 'required tests')
    for data in ['{}', '[]', 'null', 'not-json']:
        monkeypatch.setenv('CI_NEEDS', data)
        assert summary.main() == 1


def test_markdown_links_fences_unicode_and_external_no_network(tmp_path):
    path = tmp_path / 'note.md'
    (tmp_path / 'target name.md').write_text('hello')
    good = '# Heading\n[local](target%20name.md)\n[web](https://example.invalid/path)\n```sh\n[x](absent)\n```\n'
    assert not documents.markdown_errors(path, good, tmp_path)
    assert documents.markdown_errors(path, '[x](missing.md)', tmp_path)
    assert documents.markdown_errors(path, '[x](../outside.md)', tmp_path)
    assert documents.markdown_errors(path, '```python\nunfinished', tmp_path)


def test_format_and_report_pair_failures(tmp_path):
    p = tmp_path / 'docs'
    p.mkdir()
    for filename, data in [('note.md', b'\xff'), ('chart.svg', b'<svg>'),
                           ('data.json', b'{oops'), ('doc.pdf', b'not PDF')]:
        (p / filename).write_bytes(data)
        assert documents.check(tmp_path, [row('docs/' + filename)])
    (tmp_path / 'Report.md').write_text('# New report')
    assert documents.check(tmp_path, [row('Report.md')])


def test_yaml_index_and_source_hashes(tmp_path):
    (tmp_path / 'docs').mkdir()
    source = tmp_path / 'AI-log/Member-E/log.md'
    source.parent.mkdir(parents=True)
    source.write_text('selected record')
    index = tmp_path / 'docs/ai-use-log.yaml'
    index.write_text('source_records:\n- path: AI-log/Member-E/log.md\n  sha256: wrong\n')
    assert documents.check(tmp_path, [row('docs/ai-use-log.yaml')])
    index.write_text('source_records: [broken')
    assert documents.check(tmp_path, [row('docs/ai-use-log.yaml')])
    index.write_text(yaml.safe_dump({'source_records': [{'path': 'AI-log/Member-E/log.md',
        'sha256': documents.hashlib.sha256(source.read_bytes()).hexdigest()}]}))
    assert not documents.check(tmp_path, [row('docs/ai-use-log.yaml')])


def test_actual_git_rename_out_of_code_is_full(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path).decode().strip()
    git('init', '-q')
    git('config', 'user.name', 'Fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    (tmp_path / 'main.py').write_text('print(1)\n')
    git('add', '.')
    git('commit', '-qm', 'base')
    base = git('rev-parse', 'HEAD')
    git('mv', 'main.py', 'note.md')
    git('commit', '-qm', 'rename')
    head = git('rev-parse', 'HEAD')
    monkeypatch.chdir(tmp_path)
    rows = scope.changes(base, head)
    assert {r['path'] for r in rows} == {'main.py', 'note.md'}
    assert scope.mode(rows, 'pull_request') == 'full'


def test_workflow_fixed_names_and_fail_closed_wiring():
    workflow = yaml.load((ROOT / '.github/workflows/ci.yml').read_text(), Loader=yaml.BaseLoader)
    jobs = workflow['jobs']
    gate = jobs['required-gates']
    assert set(gate['strategy']['matrix']['check']) == set(summary.GATES)
    assert gate['if'] == 'always()'
    assert set(gate['needs']) == {'scope', 'documents'} | {j for js in summary.GATES.values() for j in js}
    for job in {j for js in summary.GATES.values() for j in js}:
        assert jobs[job]['needs'] == ['scope']
        assert jobs[job]['if'] == "needs.scope.outputs.mode == 'full'"
    for name in ['scope', 'documents', 'required-gates']:
        assert not any('pip install' in str(step) for step in jobs[name]['steps'])
    assert 'paths-ignore' not in str(workflow.get('on'))
    assert json.dumps(jobs['documents']).find('check_documents.py') >= 0


def test_deleted_document_inbound_links_are_rejected(tmp_path):
    missing = (tmp_path / 'removed.md').resolve()
    # Ignore unrelated historical broken links; reject new deletion breakage.
    text = '[removed](removed.md)\n[old](already-absent.md)'
    errors = documents.markdown_errors(tmp_path / 'note.md', text, tmp_path, {missing})
    assert len(errors) == 1 and 'removed.md' in errors[0]
