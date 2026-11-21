# AAPL Fundamental Report — As of 2026-01-09

**Synthetic source-vintage regression reference L2-20261121T101320Z-1.** All data below come from a single synthetic dataset returned identically by all five requested tools (`get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`, `get_insider_transactions`). The reference ID is not a financial fact. Data coverage is very thin.

## 1. Opening Summary

- **Only two income-statement periods are usable as known evidence:** FY2025 Q1 (period ended 2024-12-28, filed 2025-01-31; revenue $124.3B, EPS $2.40) and FY2025 Q3 (period ended 2025-06-28, filed 2025-08-01; revenue $94.0B, EPS not supplied).
- **One balance-sheet data point is known:** cash of $35.9B at period end 2025-09-27, filed 2025-10-31.
- **Excluded — post-cutoff filing:** An FY2026 Q1 row (period end 2025-12-31, filed 2026-01-29) carrying revenue of $999.0B is excluded because its filing date is after the 2026-01-09 cutoff. It is not known evidence as of the analysis date, is implausible on its face, and is not used anywhere in this report; its filing date is cited only to explain the exclusion.
- **Not supplied / not available:** valuation, earnings-release calendar, cash-flow statement, insider transactions, company profile, income-statement detail (gross margin, operating income, net income), full balance sheet (assets, liabilities, debt, equity), any quarterly results for periods ending 2025-03-29 or 2025-09-27 (the latter appears in `missing_income_periods`), and shares outstanding.
- **Bottom line for traders:** The known record supports only a limited read: a large seasonal step-down from FY2025 Q1 (December-quarter) to FY2025 Q3 (June-quarter) revenue (~$124.3B → ~$94.0B, roughly –24%), consistent with Q1 being the holiday quarter. Current-period earnings, cash flow, valuation, insider activity and any near-term catalyst timing are **unknown** from supplied data. Do not price off the excluded row.

## 2. Company Profile

Not supplied in the tool results. No business description, segment mix, geography, or management information is available. This report does not supplement it from memory.

## 3. Reported Income (known periods only)

| Fiscal label | Period end | Filed | Revenue ($B) | EPS ($) |
|---|---|---|---|---|
| FY2025 Q1 | 2024-12-28 | 2025-01-31 | 124.3 | 2.40 |
| FY2025 Q3 | 2025-06-28 | 2025-08-01 | 94.0 | Not supplied |

**Analysis of available income data**
- **Seasonal revenue pattern confirmed in the two-point sample:** Q1 (holiday quarter) revenue of $124.3B versus Q3 revenue of $94.0B implies a sequential decline of about $30.3B, or roughly –24%. With only two non-adjacent quarters, no growth rate, trend, or average can be responsibly computed — the gap between period ends (2024-12-28 to 2025-06-28, ~6 months) does not represent consecutive quarters.
- **EPS available for one quarter only:** $2.40 in FY2025 Q1. No sequential or year-over-year comparison is possible because the prior-year Q1 was not supplied. Any margin, tax, or share-count inference from single-quarter EPS vs. revenue would be speculative and is not made.
- **Gap in the record:** FY2025 Q2 (period end 2025-03-29) is absent from the dataset entirely; no revenue, EPS, or filing date was returned for it. Treat that quarter as unreported in this dataset, not as zero or unchanged.

## 4. Balance Sheet (available facts)

| Period end | Filed | Cash ($B) |
|---|---|---|
| 2025-09-27 | 2025-10-31 | 35.9 |

- This is the most recent balance-sheet item available before the cutoff. Only cash is disclosed; total assets, total debt, liabilities, shareholders' equity, share count and net cash position are **not supplied**, so leverage, liquidity ratios and buyback capacity cannot be assessed.
- No period-over-period balance-sheet comparison is possible (single observation).

## 5. Income Periods Missing or Excluded

| Period end | Fiscal label | Status | Reason |
|---|---|---|---|
| 2025-09-27 | FY2025 Q4 (annual calendar label per record gap) | **Missing** (listed in `missing_income_periods`) | No income statement supplied for this period; only cash was reported at this date |
| 2025-12-31 | FY2026 Q1 | **Excluded** | Filed 2026-01-29, after the 2026-01-09 cutoff; the $999.0B revenue figure is not usable and is not carried into any table or calculation |
| 2025-03-29 | FY2025 Q2 | **Missing** (absent from dataset) | No rows returned for this period |

## 6. Cash Flow, Valuation, Insiders, Earnings Calendar

- **Cash-flow statement:** `cashflow: "not supplied"` — no operating, investing, or financing cash-flow figures, no free cash flow, no dividends or buybacks.
- **Valuation:** `valuation: "not available"` — no price, market cap, P/E, EV/EBITDA or other multiples. No valuation conclusions are drawn.
- **Insider transactions:** `insider_transactions: "not available"` — no open-market purchases or sales from officers or directors; no read on insider conviction.
- **Earnings-release calendar:** `earnings_release_calendar: "not supplied"`. The next report date and timing are **unknown**. The excluded FY2026 Q1 filing date (2026-01-29) cannot be used to infer an upcoming earnings schedule or event timing.

## 7. Actionable Insights (bounded by the data)

1. **Anchor on the two known quarters only.** FY2025 Q1 revenue $124.3B with EPS $2.40 is the sole earnings-quality data point; FY2025 Q3 revenue $94.0B is the only mid-year datapoint. Do not extrapolate a growth rate from two non-adjacent quarters.
2. **Treat the FY2025 Q4 (2025-09-27) income result as a key information gap.** The balance sheet at that date is known, but the associated quarter's revenue and earnings were not supplied. Until that period is confirmed as reported, holiday-quarter performance for the latest fiscal year is unverified in this dataset.
3. **The most recent calendar quarter (ending 2025-12-31) is unknown as of the cutoff.** No revenue, EPS, cash position or filing evidence is available on or before 2026-01-09. Position sizing should not assume any outcome for that quarter.
4. **Discard the $999.0B outlier.** It is post-cutoff and implausible; including it anywhere in models would be an error.
5. **Cash of $35.9B (2025-09-27) is the only capital-return/liquidity anchor available**, and without debt, equity or cash-flow context it cannot by itself support a balance-sheet thesis.

## 8. Caveats

- All data are synthetic and returned identically by every tool call; the five tools produced no differentiated statement detail.
- Fiscal labels are reproduced as reported and were not converted into calendar-year equivalents; period ends (e.g., 2024-12-28 for "FY2025 Q1") show the fiscal calendar is offset from the calendar year.
- Nothing in this report uses the 2026-01-29 filing date as evidence of an upcoming event. The next earnings date is unknown.
- No company profile, segment, geographic, macroeconomic, or peer data were available, so no comparative or qualitative assessment is offered.

### Key Points Summary

| Category | Item | Value / Status | Period end | Filed | Usable as of 2026-01-09? |
|---|---|---|---|---|---|
| Income | FY2025 Q1 revenue | $124.3B | 2024-12-28 | 2025-01-31 | Yes |
| Income | FY2025 Q1 EPS | $2.40 | 2024-12-28 | 2025-01-31 | Yes |
| Income | FY2025 Q3 revenue | $94.0B | 2025-06-28 | 2025-08-01 | Yes |
| Income | FY2025 Q3 EPS | Not supplied | 2025-06-28 | 2025-08-01 | n/a |
| Income | FY2025 Q2 | Missing (no row) | 2025-03-29 | Unknown | No |
| Income | FY2025 Q4 | Missing (listed gap) | 2025-09-27 | Unknown | No |
| Income | FY2026 Q1 | Excluded (post-cutoff filing) — $999.0B not used | 2025-12-31 | 2026-01-29 (excluded) | No |
| Balance sheet | Cash | $35.9B | 2025-09-27 | 2025-10-31 | Yes |
| Balance sheet | Debt / equity / assets | Not supplied | — | — | No |
| Cash flow | Operating/investing/financing, FCF | Not supplied | — | — | No |
| Valuation | Price, market cap, multiples | Not available | — | — | No |
| Insiders | Transactions | Not available | — | — | No |
| Calendar | Next earnings date | Not supplied / unknown | — | — | No |
| Profile | Business description, segments | Not supplied | — | — | No |