"""Opt-in sequential live comparison through the presentation's real run API."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from .console_service import ConsoleService


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Explicitly allow paid model calls')
    parser.add_argument('--date', default='2026-11-24')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cache-dir', type=Path, help='Reuse the matched control vendor cache')
    parser.add_argument('--runs', type=int, default=2, help='Candidate runs after one control')
    parser.add_argument('--candidate-only', action='store_true', help='Use an already recorded matched control separately')
    args = parser.parse_args(argv)
    if not args.live or not 1 <= args.runs <= 5:
        parser.error('Pass --live and choose 1–5 candidate runs.')
    args.output.mkdir(parents=True, exist_ok=True)
    source_files = ['agents/context.py', 'agents/analysts/sentiment_analyst.py',
                    'agents/managers/research_manager.py', 'agents/trader/trader.py',
                    'default_config.py', 'graph/trading_graph.py', 'runapi/execution.py']
    hashes = {name: hashlib.sha256((Path('tradingagents') / name).read_bytes()).hexdigest()
              for name in source_files}
    profiles = ([] if args.candidate_only else [('control', False)])
    profiles += [(f'compact-{i + 1}', True) for i in range(args.runs)]
    cache_dir = args.cache_dir or args.output / 'shared-cache'
    rows = []
    for profile, enabled in profiles:
        service = ConsoleService(args.output / profile)
        service.defaults['compact_evidence_handoff'] = enabled
        service.defaults['data_cache_dir'] = str(cache_dir)
        prepared = service.prepare_console({'config': {
            'ticker': 'NVDA', 'analysisDate': args.date,
            'selectedAnalysts': ['market', 'news', 'social', 'fundamentals'],
            'researchRounds': 1, 'riskRounds': 1, 'maxModelRequests': 40,
            'deepModel': 'deep-configured', 'quickModel': 'quick-configured', 'portfolioMode': 'none'}})
        # All cache paths are measurement isolation, not changed vendor responses.
        job = service.get(prepared['preparedId'])
        job.options['frozen_config']['data_cache_dir'] = str(cache_dir)
        run_id = service.start_console({'fingerprint': prepared['fingerprint'], 'confirmed': True})['runId']
        started = time.monotonic()
        while True:
            status = service.status(run_id)
            if status['status'] not in ('FROZEN', 'READY', 'RUNNING'):
                break
            if time.monotonic() - started > 600:
                raise TimeoutError('Live run exceeded 600 seconds; no completed measurement claimed.')
            time.sleep(2)
        rows.append({'profile': profile, 'compact_evidence_handoff': enabled,
                     'status': status, 'entry_point': 'run_analysis_api / CLI-equivalent streaming runner',
                     'input_mode': prepared['inputMode'], 'memory': 'isolated empty per run',
                     'llm_max_retries': 0, 'checkpoint_enabled': False,
                     'vendor_cache': 'ordinary shared cache; live vendors not replaced',
                     'source_sha256_at_start': hashes,
                     'stage_words': {row['agent']: len(row['content'].split())
                                     for row in service.discussion_list(run_id)}})
        (args.output / 'comparison.json').write_text(json.dumps(rows, indent=2))
        print(json.dumps({'profile': profile, 'status': status['status'],
                          'calls': status['modelCalls'], 'usage': status['usage'],
                          'output_check': status['outputCheck']}), flush=True)
        if status['status'] != 'COMPLETED':
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
