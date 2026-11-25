"""Presentation adapter with real run boundaries and explicitly synthetic analysis."""
from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler
from openai import OpenAI

from tradingagents.dataflows.errors import VendorUnavailableError
from tradingagents.default_config import build_default_config
from tradingagents.llm_clients.budget_transport import BudgetTransport, http
from tradingagents.paths import project_root
from tradingagents.runapi.budget import ACTIVE_BUDGET
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import PortfolioInputService, freeze_no_portfolio

ROOT = project_root()
STAGES = ('Market analysis', 'News analysis', 'Sentiment analysis', 'Fundamentals analysis',
          'Research discussion', 'Trader plan', 'Risk discussion', 'Portfolio Manager')
SAMPLES = {
    'empty': {'cash': 0, 'currency': 'USD', 'positions': []},
    'holdings': {'cash': None, 'currency': 'USD', 'positions': [
        {'ticker': 'NVDA', 'quantity': 10, 'average_price': 120}]},
    'invalid': {'positions': [{'ticker': 'NVDA'}]},
}


class DemoError(ValueError):
    """Safe validation message for the local presentation UI."""


def history():
    """Use the actual checked-in evidence, never hard-code an efficiency claim."""
    source = 'tests/member_d_verification/evidence/token-input-reduction-2026-11-24.json'
    evidence = json.loads((ROOT / source).read_text())
    control = evidence['rows']['live_control']
    optimized = evidence['rows']['live_optimized']
    before = sum(row['total_tokens'] for row in control) / len(control)
    after = sum(row['total_tokens'] for row in optimized) / len(optimized)
    return {'date': evidence['date'], 'case': evidence['case'], 'model': evidence['model'],
            'before': before, 'after': after, 'control_samples': len(control),
            'optimized_samples': len(optimized), 'reduction': (before - after) / before * 100,
            'source': source, 'limitations': evidence['limitations']}


@dataclass
class Job:
    context: object
    options: dict
    directory: Path
    state: str = 'FROZEN'
    stage: str = 'Waiting for confirmation'
    events: list = field(default_factory=list)
    calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    usage_responses: int = 0
    usage_unknown: int = 0
    result: dict | None = None
    manifest: dict | None = None
    started: float | None = None
    elapsed: float = 0
    controller: object = None
    lock: object = field(default_factory=threading.RLock)

    def event(self, message):
        with self.lock:
            self.events.append({'time': round(time.monotonic() - self.started, 2)
                                if self.started else 0, 'message': message})

    def snapshot(self):
        with self.lock:
            cap = self.options['call_cap']
            budget = self.controller.audit() if self.controller is not None else None
            return {'run_id': self.context.run_id, 'state': self.state, 'stage': self.stage,
                    'mode': self.options['execution'], 'scenario': self.options['scenario'],
                    'input': self.context.safe_input_metadata(), 'call_cap': cap,
                    'calls': budget['dispatched'] if budget else self.calls,
                    'budget': (self.manifest or {}).get('run_budget', budget),
                    'tokens_in': self.tokens_in if self.usage_responses else None,
                    'tokens_out': self.tokens_out if self.usage_responses else None,
                    'usage_kind': 'synthetic' if self.options['execution'] == 'scripted' else 'provider',
                    'usage_complete': self.usage_responses > 0 and self.usage_unknown == 0,
                    'elapsed': round(time.monotonic() - self.started, 1)
                    if self.state == 'RUNNING' else round(self.elapsed, 1),
                    'events': list(self.events),
                    'result': ({key: value for key, value in self.result.items()
                                if key not in ('manifest_path', 'report_path')}
                               if self.result else None),
                    'artifact_ready': self.manifest is not None}


class LiveStats(BaseCallbackHandler):
    """Observe provider usage without retaining model prompts or credentials."""
    def __init__(self, job):
        self.job = job

    def on_chat_model_start(self, serialized, messages, **kwargs):
        metadata = kwargs.get('metadata') or {}
        with self.job.lock:
            self.job.calls += 1
            self.job.stage = str(metadata.get('langgraph_node') or 'Model request')
        self.job.event('Model invocation observed; waiting for a provider response.')

    def on_llm_end(self, response, **kwargs):
        try:
            usage = response.generations[0][0].message.usage_metadata
        except (AttributeError, IndexError, TypeError):
            usage = None
        with self.job.lock:
            if usage and isinstance(usage.get('input_tokens'), int) and isinstance(usage.get('output_tokens'), int):
                self.job.tokens_in += usage['input_tokens']
                self.job.tokens_out += usage['output_tokens']
                self.job.usage_responses += 1
            else:
                self.job.usage_unknown += 1
        self.job.event('Provider response received; available usage recorded.')

    def on_llm_error(self, error, **kwargs):
        with self.job.lock:
            self.job.usage_unknown += 1
        self.job.event('Model invocation failed; missing usage is not treated as zero.')


class ScriptedGraph:
    """Synthetic graph, real SDK transport and real per-run call controller.

    No remote request is possible: the SDK client has only MockTransport.
    This does not simulate production model quality or production call counts.
    """
    def __init__(self, job, delay):
        self.job, self.delay = job, delay
        self.job.controller = ACTIVE_BUDGET.get()

    def run(self, context):
        def respond(request):
            # Only requests admitted by BudgetTransport reach this fixture.
            with self.job.lock:
                self.job.calls += 1
                index = self.job.calls
                incoming, outgoing = 900 + 60 * index, 160 + 20 * index
                self.job.tokens_in += incoming
                self.job.tokens_out += outgoing
                self.job.usage_responses += 1
            return http.Response(200, json={
                'id': f'demo-{index}', 'object': 'chat.completion', 'model': 'scripted-fixture',
                'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Scripted response.'},
                             'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': incoming, 'completion_tokens': outgoing,
                          'total_tokens': incoming + outgoing}})

        transport = http.MockTransport(respond)
        if self.job.controller is not None:
            transport = BudgetTransport(self.job.controller, transport)
        with (http.Client(transport=transport, follow_redirects=False) as wire,
              OpenAI(api_key='demo-fixture-only', base_url='https://demo.invalid/v1',
                     http_client=wire, max_retries=0) as client):
            for index, stage in enumerate(STAGES):
                with self.job.lock:
                    self.job.stage = stage
                self.job.event(f'{stage}: requesting a local scripted response.')
                if index == 2 and self.job.options['scenario'] == 'model_failure':
                    raise TimeoutError('Scripted model timeout; no remote model was contacted.')
                if index == 0 and self.job.options['scenario'] == 'data_failure':
                    raise VendorUnavailableError('Scripted core-price failure; no vendor was contacted.')
                client.chat.completions.create(model='scripted-fixture', messages=[
                    {'role': 'user', 'content': f'Demo stage: {stage}. No market data.'}])
                self.job.event(f'{stage}: scripted response received.')
                if self.delay:
                    time.sleep(self.delay)
        if context.snapshot is None:
            facts = 'Holdings and cash were not provided; no ownership is assumed.'
        elif not context.snapshot.positions:
            facts = 'An explicitly empty portfolio was supplied; this is a known flat book.'
        else:
            facts = 'A user-supplied position is present. Cash is unknown unless explicitly supplied.'
        notice = ('**Scripted presentation fixture.** No market data or real model was queried. '
                  'The following text demonstrates report plumbing, not investment analysis.')
        rating = 'REVIEW' if self.job.options['scenario'] == 'review' else 'Hold'
        return {'market_report': notice + '\n\nNo price claim is made.',
                'news_report': notice + '\n\nNo live news was retrieved.',
                'sentiment_report': notice + '\n\nNo sentiment score was measured.',
                'fundamentals_report': notice + '\n\nNo filing was fetched.',
                'investment_debate_state': {'bull_history': 'Scripted bull discussion.',
                                           'bear_history': 'Scripted bear discussion.'},
                'investment_plan': 'Research Manager recommendation: gather current evidence. ' + facts,
                'trader_investment_plan': 'Trader plan: no order is placed. ' + facts,
                'risk_debate_state': {'neutral_history': 'Scripted risk discussion: uncertainty remains.'},
                'final_trade_decision': f'Rating: {rating}\n\n' + notice + '\n\n' + facts,
                'final_rating': rating}


class DemoService:
    def __init__(self, root=None, *, allow_live=False, delay=0.25):
        self.root = Path(root or ROOT / '.local-review/demo' / uuid4().hex)
        self.root.mkdir(parents=True, exist_ok=True)
        self.allow_live, self.delay = allow_live, delay
        self.jobs, self.lock = {}, threading.RLock()

    def bootstrap(self):
        return {'allow_live': self.allow_live, 'stages': STAGES, 'samples': SAMPLES,
                'history': history(), 'default_date': '2026-01-09'}

    def prepare(self, payload):
        ticker = str(payload.get('ticker', '')).strip().upper()
        if not re.fullmatch(r'[A-Z0-9.^=-]{1,16}', ticker):
            raise DemoError('Use a ticker of 1–16 letters, numbers, or . ^ = - characters.')
        analysis_date = payload.get('analysis_date')
        try:
            parsed = date.fromisoformat(analysis_date)
        except (ValueError, TypeError):
            raise DemoError('Choose a valid analysis date (YYYY-MM-DD).') from None
        if parsed > date.today() or parsed.year < 1900:
            raise DemoError('Choose a historical analysis date, not a future date.')
        execution = payload.get('execution', 'scripted')
        if execution not in ('scripted', 'live') or (execution == 'live' and not self.allow_live):
            raise DemoError('Live execution is disabled. Restart with --allow-live to enable it.')
        scenario = payload.get('scenario', 'normal')
        if scenario not in ('normal', 'budget', 'review', 'model_failure', 'data_failure'):
            raise DemoError('Choose one of the available presentation scenarios.')
        if execution == 'live' and scenario not in ('normal', 'budget'):
            raise DemoError('Injected failure/review scenarios use scripted responses only.')
        cap = payload.get('call_cap')
        if scenario == 'budget':
            cap = 2 if cap is None else cap
        if cap is not None and (type(cap) is not int or not 0 <= cap <= 500):
            raise DemoError('Call limit must be an integer between 0 and 500, or blank.')
        mode = payload.get('portfolio_mode', 'none')
        directory = self.root / uuid4().hex
        directory.mkdir()
        if mode == 'none':
            context = freeze_no_portfolio(ticker, analysis_date)
        elif mode in ('empty', 'holdings', 'invalid', 'custom'):
            content = payload.get('portfolio_json') if mode == 'custom' else json.dumps(SAMPLES[mode])
            if not isinstance(content, str) or len(content.encode()) > 32768:
                raise DemoError('Choose a JSON portfolio file smaller than 32 KB.')
            filename = str(payload.get('filename', 'demo-portfolio.json')).replace('\\', '/').split('/')[-1]
            if not filename or len(filename) > 128 or not filename.lower().endswith('.json'):
                filename = 'demo-portfolio.json'
            path = directory / filename
            path.write_text(content)
            context = PortfolioInputService().freeze_path(ticker, analysis_date, path, analysis_date)
        else:
            raise DemoError('Choose a portfolio input mode.')
        options = {'execution': execution, 'scenario': scenario, 'call_cap': cap}
        job = Job(context, options, directory)
        with self.lock:
            self.jobs[context.run_id] = job
        return job.snapshot()

    def get(self, run_id):
        if not isinstance(run_id, str):
            raise DemoError('A valid run identifier is required.')
        with self.lock:
            if run_id not in self.jobs:
                raise DemoError('This run does not exist in this demo session.')
            return self.jobs[run_id]

    def cancel(self, run_id):
        job = self.get(run_id)
        with job.lock:
            if job.state != 'FROZEN':
                raise DemoError('Only an unstarted, frozen input can be cancelled.')
            job.state, job.stage = 'CANCELLED', 'Cancelled before model dispatch'
        return job.snapshot()

    def start(self, run_id, *, consent, background=True):
        job = self.get(run_id)
        with self.lock, job.lock:
            if consent is not True:
                raise DemoError('Confirm the frozen inputs before starting any model invocation.')
            if job.state != 'FROZEN':
                raise DemoError('A frozen input can be started only once.')
            if any(j.state == 'RUNNING' for j in self.jobs.values()):
                raise DemoError('A run is already active. Wait before starting another.')
            job.context = job.context.confirm()
            job.state, job.started = 'RUNNING', time.monotonic()
        if background:
            threading.Thread(target=self._execute, args=(job,), daemon=True).start()
        else:
            self._execute(job)
        return job.snapshot()

    def _execute(self, job):
        config = build_default_config()
        config.update({'results_dir': str(job.directory / 'results'),
                       'data_cache_dir': str(self.root / 'cache'),
                       'memory_log_path': str(job.directory / 'memory.md'),
                       'checkpoint_enabled': False, 'call_cap': job.options['call_cap'],
                       'max_debate_rounds': 1, 'max_risk_discuss_rounds': 1,
                       'output_language': 'English', 'concise_intermediate_reports': True,
                       'selected_analysts': ['market', 'news', 'social', 'fundamentals']})
        kwargs = {}
        if job.options['execution'] == 'scripted':
            config.update({'llm_provider': 'openai_compatible', 'deep_think_provider': None,
                           'quick_think_provider': None, 'deep_think_llm': 'scripted-fixture',
                           'quick_think_llm': 'scripted-fixture', 'backend_url': 'https://demo.invalid/v1',
                           'data_vendors': {}, 'tool_vendors': {}})
            kwargs = {'graph_factory': lambda **kw: ScriptedGraph(job, self.delay),
                      'engine_runner': lambda graph, context: graph.run(context)}
        else:
            def factory(**kw):
                from tradingagents.graph.trading_graph import TradingAgentsGraph
                job.controller = ACTIVE_BUDGET.get()
                return TradingAgentsGraph(debug=False, **kw)
            kwargs = {'graph_factory': factory, 'callbacks': [LiveStats(job)]}
        try:
            job.event('Confirmed input entered the real shared run API.')
            result = run_analysis_api(job.context, config=config,
                                      selected_analysts=['market', 'news', 'social', 'fundamentals'], **kwargs)
            with job.lock:
                job.result = result.as_dict()
                if result.manifest_path:
                    job.manifest = json.loads(Path(result.manifest_path).read_text())
                job.state, job.stage = 'FINISHED', 'Report published'
                job.elapsed = time.monotonic() - job.started
            job.event(f'Real system verdict: {result.run_outcome} / {result.output_check}.')
        except Exception:
            with job.lock:
                job.state, job.stage = 'ERROR', 'No report could be published'
                job.elapsed = time.monotonic() - job.started
            job.event('Presentation adapter failed. No successful result is claimed.')

    def artifact(self, run_id, kind):
        job = self.get(run_id)
        if job.manifest is None or not job.result:
            raise DemoError('Run artifacts are not available yet.')
        manifest = Path(job.result['manifest_path'])
        mapping = {'manifest': manifest, 'markdown': Path(job.result['report_path']),
                   'html': manifest.parent / job.manifest['report_paths']['html']}
        if kind not in mapping:
            raise DemoError('Unknown artifact.')
        path = mapping[kind].resolve()
        if not path.is_relative_to(job.directory.resolve()) or not path.is_file():
            raise DemoError('Artifact is unavailable.')
        return path
