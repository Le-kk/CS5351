"""D8 packaging/compatibility and retained gate boundaries; no live calls."""
import importlib.util

import pytest
import yaml

from tradingagents.agents.context import compact_handoff_instruction, concise_analysis_instruction
from tradingagents.dataflows.config import run_config
from tradingagents.paths import project_root

ROOT = project_root()


@pytest.mark.parametrize('old,new', [('tradingagents', 'src/tradingagents'), ('cli', 'src/cli'),
                                   ('demo', 'src/demo'), ('tests', 'test/offline'),
                                   ('tests/member_c_verification/live', 'test/live/member_c_verification')])
def test_old_paths_resolve_to_one_canonical_source(old, new):
    assert (ROOT / old).resolve() == (ROOT / new).resolve()
    assert (ROOT / new).is_dir()


def test_canonical_paths_require_ai_log_updates():
    spec = importlib.util.spec_from_file_location('layout_log_gate', ROOT / 'scripts/ci/check_ai_log_updated.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    for path in ['src/tradingagents/runapi/result.py', 'src/frontend/package.json',
                 'src/demo/console.py', 'test/live/example.py', 'test/offline/example.py']:
        assert gate.is_critical(path)
    assert not gate.is_critical('docs/submission/notes.md')


@pytest.mark.parametrize('version,enabled', [('1.0', False), ('1.1', True)])
def test_prompt_snapshot_matches_actual_runtime_fragments(version, enabled):
    data = yaml.safe_load((ROOT / f'prompts/prompt_v{version}.yaml').read_text())
    with run_config({'compact_evidence_handoff': enabled, 'concise_intermediate_reports': True}):
        assert data['analyst'] == concise_analysis_instruction()
        assert data['debate'] == concise_analysis_instruction('debate')
        assert data['research_manager'] == compact_handoff_instruction('research_manager')
        assert data['trader'] == compact_handoff_instruction('trader')


def test_frontend_failure_or_missing_result_blocks_required_summary():
    spec = importlib.util.spec_from_file_location('layout_summary_gate', ROOT / 'scripts/ci/check_required_tests.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    good = {'pytest': 'success', 'clean-install smoke': 'success', 'frontend build': 'success'}
    assert not gate.unsuccessful(good)
    for state in ['failure', 'cancelled', 'skipped', '']:
        assert gate.unsuccessful({**good, 'frontend build': state})
    assert gate.unsuccessful({k: v for k, v in good.items() if k != 'frontend build'})
