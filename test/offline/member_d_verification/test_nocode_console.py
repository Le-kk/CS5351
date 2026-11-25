"""Real publication behind the nocode REST contract, with a scripted test graph only."""
from types import SimpleNamespace

import pytest

from demo.console_service import ConsoleService
from demo.service import DemoError


class FixtureGraph:
    def __init__(self, **kwargs):
        self.propagator = SimpleNamespace(get_graph_args=lambda **kw: {})

    def create_run_state(self, *args):
        return {}

    def begin_checkpoint(self, *args):
        return None

    def checkpoint_input(self, state):
        return state

    def end_checkpoint(self):
        pass

    def stream_run(self, state, **kwargs):
        # Inputs such as messages/system prompts are deliberately not exported.
        yield [], {'messages': [{'content': 'PRIVATE_SYSTEM_PROMPT'}], 'market_report': 'Market evidence.',
                   'investment_debate_state': {'bull_history': 'Bull: growth.', 'count': 1}}
        yield [], {'investment_debate_state': {'bull_history': 'Bull: growth.',
                                               'bear_history': 'Bear: uncertainty.', 'count': 2},
                   'investment_plan': 'Recommendation: Hold.', 'trader_investment_plan': 'No order.',
                   'risk_debate_state': {'aggressive_history': 'Risk viewpoint.', 'count': 1},
                   'final_trade_decision': 'Rating: Hold\nEvidence remains uncertain.', 'final_rating': 'Hold'}


@pytest.fixture
def console(tmp_path):
    return ConsoleService(tmp_path, graph_factory=FixtureGraph)


def config():
    return {'config': {'ticker': 'NVDA', 'analysisDate': '2026-01-09',
                       'selectedAnalysts': ['market'], 'researchRounds': 1, 'riskRounds': 1,
                       'deepModel': 'deep-configured', 'quickModel': 'quick-configured',
                       'portfolioMode': 'none', 'maxModelRequests': ''}}


def test_explicit_confirmation_real_result_and_safe_stage_exports(console):
    prepared = console.prepare_console(config())
    assert prepared['inputMode'] == 'NO_PORTFOLIO'
    assert len(prepared['fingerprint']) == 64
    with pytest.raises(DemoError):
        console.start_console({'fingerprint': prepared['fingerprint']}, background=False)
    started = console.start_console({'fingerprint': prepared['fingerprint'], 'confirmed': True}, background=False)
    run_id = started['runId']
    status = console.status(run_id)
    assert status['status'] == 'COMPLETED' and status['outputCheck'] == 'PASSED'
    assert status['finalRating'] == 'Hold'
    discussion = console.discussion_list(run_id)
    assert len([m for m in discussion if m['agent'] == 'Bull Researcher']) == 1
    assert all('PRIVATE_SYSTEM_PROMPT' not in m['content'] for m in discussion)
    files = console.file_list(run_id)
    assert {'manifest', 'complete-markdown', 'complete-html', 'discussions'} <= {f['fileId'] for f in files}
    html = console.file_path(run_id, 'complete-html').read_text()
    assert '<a class="logo"' not in html and 'Tauric Research' not in html
    assert 'Research output only.' in html
    assert status['usage']['totalTokens'] is None  # test graph has no provider usage
    with pytest.raises(DemoError):
        console.start_console({'fingerprint': prepared['fingerprint'], 'confirmed': True}, background=False)


def test_history_survives_a_backend_restart(console):
    prepared = console.prepare_console(config())
    run_id = console.start_console({'fingerprint': prepared['fingerprint'], 'confirmed': True}, background=False)['runId']
    restored = ConsoleService(console.root, graph_factory=FixtureGraph)
    assert restored.status(run_id)['status'] == 'COMPLETED'
    assert restored.discussion_list(run_id) == console.discussion_list(run_id)
    assert restored.file_path(run_id, 'manifest').read_bytes() == console.file_path(run_id, 'manifest').read_bytes()
    with pytest.raises(DemoError):
        restored.file_path(run_id, '../.env')


@pytest.mark.parametrize('key,value', [('deepModel', 'unapproved'), ('selectedAnalysts', []),
                                       ('researchRounds', True), ('riskRounds', 6),
                                       ('maxModelRequests', '2.5')])
def test_all_frontend_controls_are_validated_before_model_dispatch(console, key, value):
    payload = config()
    payload['config'][key] = value
    with pytest.raises(DemoError):
        console.prepare_console(payload)
    assert not any(job.started for job in console.jobs.values())


def test_configuration_change_produces_an_independent_confirmation(console):
    first = console.prepare_console(config())
    second_input = config()
    second_input['config']['researchRounds'] = 2
    second = console.prepare_console(second_input)
    assert first['fingerprint'] != second['fingerprint']
    assert first['effectiveConfig']['researchRounds'] == 1
    assert second['effectiveConfig']['researchRounds'] == 2


def test_compact_mode_is_frozen_and_visible_before_confirmation(console):
    console.defaults['compact_evidence_handoff'] = True
    prepared = console.prepare_console(config())
    assert prepared['effectiveConfig']['compactEvidenceHandoff'] is True
    job = console.get(prepared['preparedId'])
    assert job.options['frozen_config']['compact_evidence_handoff'] is True
    console.defaults['compact_evidence_handoff'] = False
    assert job.options['frozen_config']['compact_evidence_handoff'] is True
    assert console.configuration()['compactEvidenceHandoff'] is False


def test_restarted_active_record_does_not_block_fresh_confirmation(console):
    prepared = console.prepare_console(config())
    job = console.get(prepared['preparedId'])
    job.options['started_at'] = '2026-11-25T12:28:58Z'
    import time
    job.started = time.monotonic()
    job.state = 'RUNNING'
    console.save(job)
    restored = ConsoleService(console.root, graph_factory=FixtureGraph)
    old = restored.status(job.context.run_id)
    assert old['status'] == 'INTERRUPTED'
    assert old['finalRating'] is None and old['outputCheck'] == 'NOT_RUN'
    fresh = restored.prepare_console(config())
    new_id = restored.start_console({'fingerprint': fresh['fingerprint'], 'confirmed': True}, background=False)['runId']
    assert restored.status(new_id)['status'] == 'COMPLETED'
    assert restored.status(job.context.run_id)['status'] == 'INTERRUPTED'


@pytest.mark.parametrize('timeout', [0, -1, True, float('nan'), float('inf'), '120'])
def test_invalid_model_timeouts_are_rejected(timeout):
    from tradingagents.llm_clients.factory import build_llm_kwargs
    with pytest.raises(ValueError):
        build_llm_kwargs({'llm_request_timeout': timeout})


def test_demo_has_explicit_request_timeout(console):
    from tradingagents.llm_clients.factory import build_llm_kwargs
    prepared = console.prepare_console(config())
    cfg = console.get(prepared['preparedId']).options['frozen_config']
    assert build_llm_kwargs(cfg)['timeout'] == 120
    assert 'timeout' not in build_llm_kwargs({})
    assert prepared['effectiveConfig']['modelRequestTimeoutSeconds'] == 120
