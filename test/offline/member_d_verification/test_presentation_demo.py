"""Real boundary behavior behind the local demo, with no live provider calls."""
from __future__ import annotations

import json
import socket
import threading
from http.client import HTTPConnection
from pathlib import Path

import pytest

from demo.server import DemoServer
from demo.service import DemoError, DemoService, history
from tradingagents.runapi.checks import DISCLAIMER
from tradingagents.runapi.result import InputError

_CONNECT, _GETADDRINFO = socket.socket.connect, socket.getaddrinfo


@pytest.fixture
def service(tmp_path):
    return DemoService(tmp_path, delay=0)


def inputs(**kwargs):
    return {'ticker': 'NVDA', 'analysis_date': '2026-01-09', **kwargs}


@pytest.mark.parametrize('mode', ['none', 'empty', 'holdings'])
def test_modes_run_through_real_api_and_publish_trusted_artifacts(service, mode):
    prepared = service.prepare(inputs(portfolio_mode=mode))
    assert prepared['state'] == 'FROZEN' and prepared['calls'] == 0
    assert prepared['input']['input_mode'] == ('NO_PORTFOLIO' if mode == 'none' else 'PORTFOLIO_PROVIDED')
    result = service.start(prepared['run_id'], consent=True, background=False)
    assert result['result']['run_outcome'] == 'COMPLETED'
    assert result['result']['output_check'] == 'PASSED'
    assert result['calls'] == 8 and result['usage_kind'] == 'synthetic'
    assert service.artifact(prepared['run_id'], 'markdown').read_text().startswith(DISCLAIMER)
    assert service.artifact(prepared['run_id'], 'manifest').is_file()
    html = service.artifact(prepared['run_id'], 'html').read_text()
    assert html.index(DISCLAIMER) < html.index('<header class="masthead">')


def test_real_validator_rejects_bad_input_without_a_job(service):
    with pytest.raises(InputError) as caught:
        service.prepare(inputs(portfolio_mode='invalid'))
    assert caught.value.kind == 'MISSING_QUANTITY'
    assert service.jobs == {}


def test_confirmation_cancellation_and_reuse_cannot_dispatch(service):
    job = service.prepare(inputs())
    with pytest.raises(DemoError, match='Confirm'):
        service.start(job['run_id'], consent=False, background=False)
    assert service.get(job['run_id']).snapshot()['calls'] == 0
    assert service.cancel(job['run_id'])['state'] == 'CANCELLED'
    with pytest.raises(DemoError, match='only once'):
        service.start(job['run_id'], consent=True, background=False)
    assert service.get(job['run_id']).snapshot()['calls'] == 0


def test_frozen_snapshot_is_not_reread_and_calls_consume_real_cap(service):
    job = service.prepare(inputs(portfolio_mode='holdings', scenario='budget'))
    original = service.get(job['run_id'])
    (original.directory / 'demo-portfolio.json').write_text('{"positions": []}')
    result = service.start(job['run_id'], consent=True, background=False)
    assert original.context.snapshot.positions[0][1] == 10
    assert result['input']['fingerprint_sha256'] == job['input']['fingerprint_sha256']
    assert result['calls'] == result['budget']['dispatched'] == 2
    assert result['budget']['denied'] == 1
    assert result['result']['stop_reason'] == 'BUDGET'
    assert result['result']['output_check'] == 'NOT_RUN'
    assert result['result']['final_rating'] is None


@pytest.mark.parametrize('cap', [0, 1, 8])
def test_exact_budget_and_zero_requests(service, cap):
    job = service.prepare(inputs(call_cap=cap))
    result = service.start(job['run_id'], consent=True, background=False)
    assert result['calls'] == cap
    assert result['result']['run_outcome'] == ('COMPLETED' if cap == 8 else 'INCOMPLETE')
    if cap == 0:
        assert result['tokens_in'] is None  # no invented zero-usage response


@pytest.mark.parametrize('scenario,reason,check', [
    ('review', None, 'NEEDS_REVIEW'), ('model_failure', 'MODEL_FAILURE', 'NOT_RUN'),
    ('data_failure', 'DATA_FAILURE', 'NOT_RUN'),
])
def test_real_result_authority_not_scripted_status_badges(service, scenario, reason, check):
    job = service.prepare(inputs(scenario=scenario))
    state = service.start(job['run_id'], consent=True, background=False)
    assert state['result']['stop_reason'] == reason
    assert state['result']['output_check'] == check
    if scenario == 'review':
        assert state['result']['final_rating'] == 'REVIEW'


@pytest.mark.parametrize('update', [
    {'execution': 'live'}, {'ticker': '../escape'}, {'analysis_date': 'not-a-date'},
    {'analysis_date': '2099-01-01'}, {'call_cap': True}, {'scenario': 'unknown'},
])
def test_invalid_controls_and_unenabled_live_mode_are_refused(service, update):
    with pytest.raises(DemoError):
        service.prepare(inputs(**update))
    assert not any(j.state == 'RUNNING' for j in service.jobs.values())


def test_history_reads_actual_evidence_and_keeps_sample_sizes():
    data = history()
    assert data['before'] == 160826 and data['after'] == 104459
    assert data['reduction'] == pytest.approx(35.048437441707186)
    assert data['control_samples'] == 1 and data['optimized_samples'] == 3
    assert data['case']['ticker'] == 'NVDA'


def test_server_boundary_requires_local_host_csrf_and_json(service, monkeypatch):
    # Retain the suite's network ban except for this server's exact loopback host.
    refused_connect, refused_lookup = socket.socket.connect, socket.getaddrinfo
    monkeypatch.setattr(socket.socket, 'connect', lambda sock, address: (
        _CONNECT(sock, address) if address[0] == '127.0.0.1' else refused_connect(sock, address)))
    monkeypatch.setattr(socket, 'getaddrinfo', lambda host, *args, **kwargs: (
        _GETADDRINFO(host, *args, **kwargs) if host == '127.0.0.1' else refused_lookup(host, *args, **kwargs)))
    server = DemoServer(('127.0.0.1', 0), service)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def request(method, path, data=None, headers=None):
        conn = HTTPConnection('127.0.0.1', server.server_port, timeout=10)
        try:
            conn.request(method, path, body=data, headers=headers or {})
            response = conn.getresponse()
            return response.status, dict(response.headers), response.read()
        finally:
            conn.close()

    try:
        status, _, body = request('GET', '/api/bootstrap')
        assert status == 200
        token = json.loads(body)['csrf_token']
        assert request('POST', '/api/prepare', '{}', {'Content-Type': 'application/json'})[0] == 403
        headers = {'Content-Type': 'application/json', 'X-Demo-Token': token}
        assert request('POST', '/api/prepare', '{}', {**headers, 'Origin': 'https://other.invalid'})[0] == 403
        assert request('GET', '/', headers={'Host': 'other.invalid'})[0] == 403
        assert request('POST', '/api/prepare', '{}', {**headers, 'Content-Type': 'text/plain'})[0] == 415
        assert request('GET', '/.env')[0] == 404
        assert request('POST', '/api/prepare', json.dumps(inputs(portfolio_mode='invalid')), headers)[0] == 400
        status, _, data = request('POST', '/api/prepare', json.dumps(inputs()), headers)
        assert status == 200
        run_id = json.loads(data)['run_id']
        service.start(run_id, consent=True, background=False)
        status, head, body = request('GET', f'/api/runs/{run_id}/html')
        assert status == 200 and DISCLAIMER.encode() in body
        assert "style-src 'unsafe-inline'" in head['Content-Security-Policy']
        assert request('GET', f'/api/runs/{run_id}/../.env')[0] == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_custom_file_path_is_kept_inside_the_demo(service):
    prepared = service.prepare(inputs(portfolio_mode='custom', filename='../../outside.json',
                                      portfolio_json='{"positions": []}'))
    assert prepared['input']['basename'] == 'outside.json'
    job = service.get(prepared['run_id'])
    assert Path(job.directory / 'outside.json').is_relative_to(service.root)
