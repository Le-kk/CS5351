"""Developer regressions for population integrity and every full-report export."""
from dataclasses import replace

import pytest

from tradingagents.report_html import render_report
from tradingagents.reporting import write_report_tree
from tradingagents.runapi.checks import DISCLAIMER
from tradingagents.runapi.result import RunRecord, summarize_records


def test_legacy_complete_exports_lead_with_canonical_disclaimer(tmp_path):
    path = write_report_tree({'final_trade_decision': 'Rating: Hold'}, 'AAPL', tmp_path)
    assert path.read_text().lstrip().startswith(DISCLAIMER)
    html = (tmp_path / 'complete_report.html').read_text()
    assert html.index(DISCLAIMER) < html.index('<header class="masthead">')


@pytest.mark.parametrize('metadata', [None, {}, {'run_id': 'fixture'}])
def test_direct_html_notice_does_not_depend_on_metadata(metadata):
    html = render_report('AAPL', {}, {}, [], run_metadata=metadata)
    assert html.index(DISCLAIMER) < html.index('<header class="masthead">')


def test_duplicate_attempt_cannot_change_completion_denominator():
    records = [RunRecord('same', 'STARTED', 'COMPLETED', 'PASSED'),
               RunRecord('same', 'STARTED')]
    with pytest.raises(ValueError, match='Duplicate attempt'):
        summarize_records(records)


def test_blank_case_is_not_a_distinct_case():
    with pytest.raises(ValueError, match='case identity'):
        summarize_records([RunRecord('a', 'STARTED', case_id='  ')])


def test_legacy_records_cannot_assert_a_validated_population():
    result = summarize_records([RunRecord('a', 'STARTED', case_id='C1')])
    assert result['distinct_case_count'] == 1
    assert result['population_result_count'] is None


def population():
    from tradingagents.runapi.result import EvaluationPopulation
    return EvaluationPopulation('cohort', 'git:fixture', 'a' * 64, 'b' * 64,
                                tuple(f'C{i}' for i in range(20)))


def record(pop, case='C0', attempt='a', outcome='COMPLETED'):
    return RunRecord(attempt, 'STARTED', outcome, 'PASSED' if outcome else None,
                     case_id=case, population_id=pop.population_id,
                     source_revision=pop.source_revision, prompt_hash=pop.prompt_hash,
                     configuration_fingerprint=pop.configuration_fingerprint)


def test_twenty_cases_forty_attempts_one_validated_population():
    pop = population()
    records = [record(pop, case, f'{case}-{trial}') for case in pop.case_ids for trial in range(2)]
    result = summarize_records(records, population=pop)
    assert result['distinct_case_count'] == 20
    assert result['started_count'] == 40
    assert result['population_result_count'] == 1
    assert result['completion_fraction'] == 1


@pytest.mark.parametrize('field,value', [
    ('population_id', 'another'), ('source_revision', 'git:other'),
    ('prompt_hash', 'c' * 64), ('configuration_fingerprint', 'd' * 64),
    ('case_id', 'unknown'), ('controlled_change', {'model': 'different'}),
])
def test_mixed_or_unsupported_comparison_population_is_rejected(field, value):
    pop = population()
    with pytest.raises(ValueError):
        summarize_records([record(pop), replace(record(pop, attempt='b'), **{field: value})],
                          population=pop)


def test_pending_started_attempt_stays_in_validated_denominator():
    pop = population()
    result = summarize_records([record(pop), record(pop, attempt='b', outcome=None)], population=pop)
    assert result['started_count'] == 2
    assert result['completion_fraction'] == 0.5
    assert result['population_result_count'] == 1


def test_context_does_not_manufacture_started_cases():
    result = summarize_records([], population=population())
    assert result['population_result_count'] == 0
    assert result['distinct_case_count'] is None
    assert result['status'] == 'INSUFFICIENT_EVIDENCE'
