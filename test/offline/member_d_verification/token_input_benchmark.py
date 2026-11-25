"""Opt-in live NVDA benchmark. Secrets and model text are never printed."""
import argparse
import hashlib
import json
import signal
import sys
import time
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--runs', type=int, default=1)
    parser.add_argument('--live', action='store_true', help='Explicitly permit billable model calls')
    parser.add_argument('--legacy', action='store_true', help='Disable the optimization for a paired control')
    parser.add_argument('--cached-prices', action='store_true', help='Use the existing real Yahoo cache as a frozen price fixture; disclose this changed measurement profile')
    args = parser.parse_args()
    if args.runs < 1:
        parser.error('--runs must be at least 1')
    if not args.live:
        parser.error('--live is required')
    root = Path(args.repo).resolve()
    sys.path.insert(0, str(root))
    from dotenv import load_dotenv
    load_dotenv(root / '.env', override=True)
    from cli.stats_handler import StatsCallbackHandler
    from tradingagents.default_config import build_default_config
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.llm_clients import create_tier_client
    from tradingagents.runapi.redact import Redactor

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    config = build_default_config()
    config.update(output_language='English', checkpoint_enabled=False,
                  concise_intermediate_reports=not args.legacy,
                  max_debate_rounds=1, max_risk_discuss_rounds=1,
                  llm_max_retries=1, results_dir=str(output / 'artifacts'),
                  memory_log_path=str(output / 'empty-memory.md'))
    if args.cached_prices:
        import pandas as pd

        from tradingagents.dataflows import router
        from tradingagents.dataflows.vendors.yahoo.common import price_text
        source = Path(config['data_cache_dir']) / 'NVDA-YFin-data.csv'
        data = pd.read_csv(source)
        data = data[pd.to_datetime(data['Date']).dt.date <= pd.Timestamp('2026-01-09').date()].copy()
        cache = output / 'frozen-cache'
        cache.mkdir(exist_ok=True)
        data.to_csv(cache / 'NVDA-YFin-data.csv', index=False)
        config['data_cache_dir'] = str(cache)
        def cached_stock(symbol, start, end):
            assert symbol == 'NVDA'
            assert end <= '2026-01-09'
            selected = data[(data['Date'] >= start) & (data['Date'] <= end)].copy()
            for col in ['Open', 'High', 'Low', 'Close']:
                selected[col] = selected[col].map(price_text)
            return f'# Frozen real Yahoo cache for NVDA from {start} to {end}; rows: {len(selected)}\n' + selected.to_csv(index=False)
        router.VENDOR_METHODS['get_stock_data']['yfinance'] = cached_stock
        (output / 'price-fixture.json').write_text(json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'as_of': '2026-01-09', 'rows': len(data), 'profile': 'cached-prices; not the original live-vendor baseline profile'}, indent=2))

    # Capture actual tool payloads separately; attaching stats only to LLMs does not
    # receive tool callbacks. This does not change the payload sent to the model.
    import tradingagents.agents.tools as agent_tools
    tool_evidence = []
    original_route = agent_tools.route_to_vendor
    original_snapshot = agent_tools.build_verified_market_snapshot
    def tracked_route(method, *a, **kw):
        result = original_route(method, *a, **kw)
        tool_evidence.append({'name': method, 'args': list(a), 'result': result})
        return result
    def tracked_snapshot(*a, **kw):
        result = original_snapshot(*a, **kw)
        tool_evidence.append({'name': 'get_verified_market_snapshot', 'args': list(a), 'result': result})
        return result
    agent_tools.route_to_vendor = tracked_route
    agent_tools.build_verified_market_snapshot = tracked_snapshot
    assert config['quick_think_llm'] == config['deep_think_llm'] == 'CS5351/DeepSeek-V4-Flash'
    def client(*a, **kw):
        kw['timeout'] = 60
        return create_tier_client(*a, **kw)

    rows = []
    class MeasurementStats(StatsCallbackHandler):
        def __init__(self):
            super().__init__()
            self.tool_results = []
        def on_chat_model_start(self, serialized, messages, **kwargs):
            super().on_chat_model_start(serialized, messages, **kwargs)
            print('LLM call', self.llm_calls, 'starting', flush=True)
        def on_tool_end(self, output, **kwargs):
            self.tool_results.append({'name': getattr(output, 'name', None), 'text': str(getattr(output, 'content', output))})

    def timed_out(*_):
        raise TimeoutError('Benchmark exceeded 600 seconds; partial usage is not a successful result')
    signal.signal(signal.SIGALRM, timed_out)
    for index in range(args.runs):
        tool_evidence.clear()
        stats = MeasurementStats()
        signal.alarm(600)
        started = time.monotonic()
        row = {'run': index + 1, 'status': 'INCOMPLETE'}
        try:
            with patch('tradingagents.graph.trading_graph.create_tier_client', client):
                graph = TradingAgentsGraph(['market', 'news', 'social', 'fundamentals'], config=config, callbacks=[stats])
            state, rating = graph.run_transient('NVDA', '2026-01-09')
            row.update(status='COMPLETED', rating=rating,
                       report_lengths={k: len(state.get(k, '')) for k in ['market_report', 'news_report', 'sentiment_report', 'fundamentals_report', 'final_trade_decision']})
            (output / f'state-{index + 1}.json').write_text(json.dumps(Redactor().scrub(state), default=str, indent=2))
        except Exception as exc:
            row['error'] = Redactor().diagnostic(exc)
        finally:
            signal.alarm(0)
        (output / f'tools-{index + 1}.json').write_text(json.dumps(Redactor().scrub(tool_evidence), indent=2))
        row.update(stats.get_stats())
        row.pop('tool_calls', None)  # LLM-bound callback does not count tool executions.
        row['observed_vendor_results'] = len(tool_evidence)
        row['total_tokens'] = row['tokens_in'] + row['tokens_out']
        row['seconds'] = round(time.monotonic() - started, 2)
        rows.append(row)
        (output / 'measurements.json').write_text(json.dumps(rows, indent=2))
        print(json.dumps(row), flush=True)
        if row['status'] != 'COMPLETED':
            sys.exit(1)


if __name__ == "__main__":
    main()
