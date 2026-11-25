"""Real-run REST contract for the exported presentation frontend."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from tradingagents.default_config import build_default_config
from tradingagents.runapi.budget import ACTIVE_BUDGET
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.redact import Redactor

from .service import DemoError, DemoService, LiveStats, history

ANALYSTS = [('market', 'Market Analyst'), ('news', 'News Analyst'),
            ('social', 'Sentiment Analyst'), ('fundamentals', 'Fundamentals Analyst')]
REPORTS = [('market_report', 'Market Analyst'), ('news_report', 'News Analyst'),
           ('sentiment_report', 'Sentiment Analyst'), ('fundamentals_report', 'Fundamentals Analyst')]


def stamp():
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


class ConsoleStats(LiveStats):
    def __init__(self, job, service):
        super().__init__(job)
        self.service = service

    def on_llm_end(self, response, **kwargs):
        super().on_llm_end(response, **kwargs)
        self.service.save(self.job)

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = self.service.redactor.scrub(str((serialized or {}).get('name') or 'data tool'))
        self.job.event(f'Data tool started: {name}.')


class ConsoleService(DemoService):
    """A same-origin local adapter; every execution uses the actual graph.

    Only an explicit confirmation token can start a run. Tokens bind the entire
    effective configuration plus the frozen portfolio, not just a file hash.
    """
    def __init__(self, root=None, *, graph_factory=None):
        from .service import ROOT
        super().__init__(root or ROOT / '.local-review/presentation-console', allow_live=True, delay=0)
        self.defaults = build_default_config()
        self.redactor = Redactor()
        self.graph_factory = graph_factory  # injection only for offline developer probes
        self.tickets, self.records, self.files, self.discussions = {}, {}, {}, {}
        self._persist_lock = threading.RLock()
        self.model_map = {}
        for tier in ('deep', 'quick'):
            self.model_map[f'{tier}-configured'] = {
                'model': self.defaults[f'{tier}_think_llm'],
                'provider': self.defaults.get(f'{tier}_think_provider') or self.defaults['llm_provider'],
                'url': self.defaults.get(f'{tier}_think_backend_url') or self.defaults.get('backend_url'),
            }
        (self.root / 'registry').mkdir(exist_ok=True)
        self._load_history()

    def configuration(self):
        return {'models': [{'id': key, 'label': f"{spec['model']} ({spec['provider']})"}
                           for key, spec in self.model_map.items()],
                'analysts': [{'id': key, 'label': label} for key, label in ANALYSTS],
                'limits': {'maxRounds': 5, 'maxModelRequests': 500},
                'defaults': {'ticker': 'NVDA', 'analysisDate': '2026-01-09',
                             'selectedAnalysts': [key for key, _ in ANALYSTS],
                             'deepModel': 'deep-configured', 'quickModel': 'quick-configured',
                             'researchRounds': 1, 'riskRounds': 1, 'portfolioMode': 'none',
                             'portfolioText': '', 'maxModelRequests': ''},
                'execution': 'live', 'language': 'English',
                'compactEvidenceHandoff': bool(self.defaults.get('compact_evidence_handoff', False))}

    def prepare_console(self, payload):
        form = payload.get('config')
        if not isinstance(form, dict):
            raise DemoError('A configuration object is required.')
        chosen = form.get('selectedAnalysts')
        allowed = {key for key, _label in ANALYSTS}
        if (not isinstance(chosen, list) or not chosen or
                any(not isinstance(key, str) or key not in allowed for key in chosen) or
                len(chosen) != len(set(chosen))):
            raise DemoError('Select one or more distinct analysts from the backend options.')
        for name in ('researchRounds', 'riskRounds'):
            if type(form.get(name)) is not int or not 1 <= form[name] <= 5:
                raise DemoError('Research and risk rounds must be integers between 1 and 5.')
        for name in ('deepModel', 'quickModel'):
            if form.get(name) not in self.model_map:
                raise DemoError('Select an approved model for each tier.')
        raw_cap = form.get('maxModelRequests')
        if raw_cap in ('', None):
            cap = None
        elif type(raw_cap) is int or isinstance(raw_cap, str) and raw_cap.isdigit():
            cap = int(raw_cap)
        else:
            raise DemoError('Model-request limit must be an integer, or blank for no limit.')
        mode = {'none': 'none', 'empty': 'empty', 'json': 'custom'}.get(form.get('portfolioMode'))
        if not mode:
            raise DemoError('Choose a supported portfolio mode.')
        if cap is not None and any(self.model_map[form[name]]['provider'] not in
                                   ('deepseek', 'openai_compatible') for name in ('deepModel', 'quickModel')):
            raise DemoError('The current call-cap profile supports deepseek/openai_compatible model tiers.')
        prepared = super().prepare({'ticker': form.get('ticker'), 'analysis_date': form.get('analysisDate'),
                                    'portfolio_mode': mode, 'portfolio_json': form.get('portfolioText'),
                                    'filename': form.get('portfolioFilename') or 'portfolio.json',
                                    'execution': 'live', 'call_cap': cap})
        job = self.get(prepared['run_id'])
        effective = {'ticker': job.context.ticker, 'analysisDate': job.context.analysis_date,
                     'selectedAnalysts': chosen, 'researchRounds': form['researchRounds'],
                     'riskRounds': form['riskRounds'], 'maxModelRequests': cap,
                     'deepModel': self.model_map[form['deepModel']]['model'],
                     'quickModel': self.model_map[form['quickModel']]['model'],
                     'deepProvider': self.model_map[form['deepModel']]['provider'],
                     'quickProvider': self.model_map[form['quickModel']]['provider'],
                     'outputLanguage': 'English', 'conciseIntermediateReports': True,
                     'compactEvidenceHandoff': bool(self.defaults.get('compact_evidence_handoff', False)),
                     'modelRequestTimeoutSeconds': 120}
        cfg = copy.deepcopy(self.defaults)
        for tier, name in [('deep', 'deepModel'), ('quick', 'quickModel')]:
            spec = self.model_map[form[name]]
            cfg.update({f'{tier}_think_llm': spec['model'], f'{tier}_think_provider': spec['provider'],
                        f'{tier}_think_backend_url': spec['url']})
        cfg.update({'max_debate_rounds': form['researchRounds'], 'max_risk_discuss_rounds': form['riskRounds'],
                    'selected_analysts': list(chosen), 'call_cap': cap, 'checkpoint_enabled': False,
                    'output_language': 'English', 'concise_intermediate_reports': True,
                    'llm_max_retries': 0, 'llm_request_timeout': 120, 'results_dir': str(job.directory / 'results'),
                    'memory_log_path': str(job.directory / 'memory.md'),
                    'data_cache_dir': str(self.root / 'cache')})
        job.options.update(effective=effective, frozen_config=cfg, started_at=None, seen={})
        token = hashlib.sha256(json.dumps({'nonce': secrets.token_hex(24), 'effective': effective,
                                          'input': prepared['input']}, sort_keys=True).encode()).hexdigest()
        with self.lock:
            self.tickets[token] = job.context.run_id
            self.files[job.context.run_id], self.discussions[job.context.run_id] = {}, []
        return {'fingerprint': token, 'inputMode': job.context.mode.value,
                'portfolioFingerprint': prepared['input']['fingerprint_sha256'],
                'filename': prepared['input']['basename'], 'effectiveConfig': effective,
                'preparedId': job.context.run_id}

    def start_console(self, payload, *, background=True):
        if payload.get('confirmed') is not True:
            raise DemoError('Explicit confirmation is required before any real model execution.')
        token = payload.get('fingerprint')
        if not isinstance(token, str) or token not in self.tickets:
            raise DemoError('Validate the configuration again; confirmation token is unknown.')
        with self.lock:
            run_id = self.tickets[token]
            job = self.get(run_id)
            if job.state != 'FROZEN':
                raise DemoError('This confirmed configuration has already been used.')
            job.options['started_at'] = stamp()
            super().start(run_id, consent=True, background=background)
        return {'runId': run_id}

    def _execute(self, job):
        cfg = job.options['frozen_config']
        tracker = ConsoleStats(job, self)

        def factory(**kwargs):
            job.controller = ACTIVE_BUDGET.get()
            if self.graph_factory:
                return self.graph_factory(**kwargs)
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            return TradingAgentsGraph(debug=False, **kwargs)

        def runner(graph, context):
            # Same stream/checkpoint lifecycle as the CLI; shared API retains all
            # checking/publication authority. Raw message/tool payloads are ignored.
            initial = graph.create_run_state(context.ticker, context.analysis_date, 'stock',
                                             context.portfolio_context())
            args = graph.propagator.get_graph_args(callbacks=[tracker])
            thread_id = graph.begin_checkpoint(context.ticker, context.analysis_date, 'stock',
                                               context.portfolio_context())
            if thread_id is not None:
                args.setdefault('config', {}).setdefault('configurable', {})['thread_id'] = thread_id
            final = {}
            try:
                for _messages, state in graph.stream_run(graph.checkpoint_input(initial), **args):
                    if isinstance(state, dict):
                        final.update(state)
                        self.capture_state(job, state)
                return final
            finally:
                graph.end_checkpoint()

        try:
            self.save(job)
            job.event('Confirmed configuration entered the actual graph through the shared run API.')
            result = run_analysis_api(job.context, config=cfg,
                                      selected_analysts=cfg['selected_analysts'], graph_factory=factory,
                                      engine_runner=runner, callbacks=[tracker], html=True)
            with job.lock:
                job.result = result.as_dict()
                if result.manifest_path:
                    job.manifest = json.loads(Path(result.manifest_path).read_text())
                job.state, job.stage = 'FINISHED', 'Report published' if job.manifest else 'Publication incomplete'
                job.elapsed = time.monotonic() - job.started
            self.publish_files(job)
            job.event(f'System outcome: {result.run_outcome}; output check: {result.output_check}.')
        except Exception as exc:
            with job.lock:
                job.state, job.stage = 'ERROR', 'Presentation adapter could not finish publication'
                job.elapsed = time.monotonic() - job.started
            # Error category only: no credentials, request URLs or raw payloads.
            job.event(f'Presentation adapter error: {type(exc).__name__}. No successful verdict is claimed.')
        finally:
            self.save(job)

    def capture_state(self, job, state):
        def emit(key, text, category, agent, round_number=None):
            if not isinstance(text, str) or not text.strip():
                return
            previous = job.options['seen'].get(key, '')
            if previous == text:
                return
            job.options['seen'][key] = text
            content = text[len(previous):].strip() if previous and text.startswith(previous) else text.strip()
            content = self.redactor.scrub(content)
            if not content:
                return
            with self.lock:
                sequence = len(self.discussions[job.context.run_id]) + 1
                record = {'id': f'm{sequence}', 'category': category, 'agent': agent,
                          'sequence': sequence, 'timestamp': stamp(), 'content': content}
                if round_number is not None:
                    record['round'] = round_number
                self.discussions[job.context.run_id].append(record)
            with job.lock:
                job.stage = agent
            job.event(f'{agent} published a sanitized output.')
            path = job.directory / 'presentation' / f'{sequence:03d}-{key}.md'
            path.parent.mkdir(exist_ok=True)
            path.write_text(f'# {agent}\n\n{content}\n')
            self.register(job, f'stage-{sequence}', path, category, 'markdown')
        for key, agent in REPORTS:
            emit(key, state.get(key), 'analyst', agent)
        debate = state.get('investment_debate_state') or {}
        count = debate.get('count')
        round_number = (count + 1) // 2 if type(count) is int and count > 0 else None
        for key, agent in [('bull_history', 'Bull Researcher'), ('bear_history', 'Bear Researcher')]:
            emit(key, debate.get(key), 'research', agent, round_number)
        emit('investment_plan', state.get('investment_plan'), 'research', 'Research Manager')
        emit('trader_investment_plan', state.get('trader_investment_plan'), 'trader', 'Trader')
        risk = state.get('risk_debate_state') or {}
        count = risk.get('count')
        round_number = (count + 2) // 3 if type(count) is int and count > 0 else None
        for key, agent in [('aggressive_history', 'Aggressive Analyst'),
                           ('conservative_history', 'Conservative Analyst'), ('neutral_history', 'Neutral Analyst')]:
            emit(key, risk.get(key), 'risk', agent, round_number)
        emit('final_trade_decision', state.get('final_trade_decision'), 'risk', 'Portfolio Manager')
        self.save(job)

    def register(self, job, file_id, path, category, kind):
        path = Path(path).resolve()
        if not path.is_relative_to(self.root.resolve()) or not path.is_file():
            raise DemoError('Run artifact is outside the presentation storage.')
        with self.lock:
            self.files[job.context.run_id][file_id] = {
                'path': str(path.relative_to(self.root.resolve())), 'name': path.name,
                'category': category, 'kind': kind}

    def publish_files(self, job):
        presentation = job.directory / 'presentation'
        presentation.mkdir(exist_ok=True)
        if job.manifest:
            manifest = Path(job.result['manifest_path'])
            self.register(job, 'manifest', manifest, 'evidence', 'json')
            self.register(job, 'complete-markdown', Path(job.result['report_path']), 'final', 'markdown')
            html_path = manifest.parent / job.manifest['report_paths']['html']
            # Keep the canonical report untouched; only its presentation copy is unbranded.
            html = html_path.read_text()
            html = re.sub(r'<a\s+class="logo"[^>]*>.*?</a>', '', html, flags=re.S)
            html = re.sub(r'<footer\b.*?</footer>', '', html, flags=re.S)
            html = html.replace('TradingAgents report', 'Research report')
            display = presentation / 'research-report.html'
            display.write_text(html)
            self.register(job, 'complete-html', display, 'final', 'html')
            event_path = manifest.parent / 'events.jsonl'
            if event_path.is_file():
                self.register(job, 'system-events', event_path, 'evidence', 'text')
        discussion_path = presentation / 'discussions.json'
        discussion_path.write_text(json.dumps(self.discussions[job.context.run_id], ensure_ascii=False, indent=2))
        self.register(job, 'discussions', discussion_path, 'discussions', 'json')

    def _status(self, job):
        state = job.snapshot()
        result = state['result'] or {}
        status = result.get('run_outcome') if job.state == 'FINISHED' and result else (
            'FAILED' if job.state == 'ERROR' else 'RUNNING' if job.state == 'RUNNING' else 'NOT_RUN')
        tokens_in, tokens_out = state['tokens_in'], state['tokens_out']
        return {'runId': job.context.run_id, 'ticker': job.context.ticker, 'status': status,
                'currentAgent': state['stage'], 'currentStage': state['stage'],
                'startedAt': job.options.get('started_at'), 'elapsedSeconds': int(state['elapsed']),
                'modelCalls': state['calls'], 'callBudget': state['budget'],
                'usage': {'inputTokens': tokens_in, 'outputTokens': tokens_out,
                          'totalTokens': tokens_in + tokens_out if tokens_in is not None and tokens_out is not None else None,
                          'complete': job.state == 'FINISHED' and job.usage_unknown == 0 and
                                      job.usage_responses >= state['calls'] and job.usage_responses > 0},
                'finalRating': result.get('final_rating'), 'outputCheck': result.get('output_check') or 'NOT_RUN',
                'stopReason': result.get('stop_reason'), 'findings': result.get('findings', []),
                'effectiveConfig': job.options.get('effective')}

    def save(self, job):
        if not job.options.get('started_at'):
            return
        status = self._status(job)
        with self._persist_lock, self.lock:
            self.records[job.context.run_id] = status
            document = {'status': status, 'discussions': list(self.discussions[job.context.run_id]),
                        'files': copy.deepcopy(self.files[job.context.run_id]), 'events': list(job.events)}
            destination = self.root / 'registry' / f'{job.context.run_id}.json'
            temporary = destination.with_suffix('.tmp')
            temporary.write_text(json.dumps(document, ensure_ascii=False))
            temporary.replace(destination)

    def _load_history(self):
        for path in (self.root / 'registry').glob('*.json'):
            try:
                doc = json.loads(path.read_text())
                run_id = doc['status']['runId']
                from tradingagents.runapi.context import validate_run_id
                validate_run_id(run_id)
                if doc['status']['status'] == 'RUNNING':
                    doc['status'].update(status='INTERRUPTED', currentStage='Backend restarted; final outcome not recovered',
                                         currentAgent='Backend restarted', finalRating=None, outputCheck='NOT_RUN')
                self.records[run_id] = doc['status']
                self.discussions[run_id] = doc.get('discussions', [])
                self.files[run_id] = doc.get('files', {})
            except (ValueError, KeyError, TypeError):
                continue

    def status(self, run_id):
        if run_id in self.jobs and self.jobs[run_id].options.get('started_at'):
            return self._status(self.jobs[run_id])
        if run_id not in self.records:
            raise DemoError('Run not found.')
        return self.records[run_id]

    def run_history(self):
        return sorted((self.status(run_id) for run_id in list(self.records)),
                      key=lambda row: row.get('startedAt') or '', reverse=True)

    def discussion_list(self, run_id):
        self.status(run_id)
        with self.lock:
            return list(self.discussions.get(run_id, []))

    def file_list(self, run_id):
        self.status(run_id)
        result = []
        with self.lock:
            registered = copy.deepcopy(self.files.get(run_id, {}))
        for file_id, item in registered.items():
            path = self.file_path(run_id, file_id)
            result.append({'fileId': file_id, 'name': item['name'], 'category': item['category'],
                           'kind': item['kind'], 'size': path.stat().st_size,
                           'downloadUrl': f'/api/runs/{run_id}/files/{file_id}/download'})
        return result

    def file_path(self, run_id, file_id):
        from tradingagents.runapi.context import validate_run_id
        try:
            validate_run_id(run_id)
            item = self.files[run_id][file_id]
            path = (self.root / item['path']).resolve()
        except (ValueError, KeyError, TypeError):
            raise DemoError('File not found.') from None
        if not path.is_relative_to(self.root.resolve()) or not path.is_file():
            raise DemoError('File is outside this presentation session.')
        return path

    def events(self, run_id):
        self.status(run_id)
        if run_id in self.jobs:
            return self.jobs[run_id].snapshot()['events']
        path = self.root / 'registry' / f'{run_id}.json'
        return json.loads(path.read_text()).get('events', [])

    def benchmark(self):
        data = history()
        return {'controlTotalTokens': data['before'], 'optimizedAverageTokens': data['after'],
                'optimizedRunCount': data['optimized_samples'], 'controlRunCount': data['control_samples'],
                'reductionPercent': round(data['reduction'], 2),
                'context': {'date': data['date'], 'case': data['case'], 'model': data['model'],
                            'source': data['source'], 'limitations': data['limitations']}}
