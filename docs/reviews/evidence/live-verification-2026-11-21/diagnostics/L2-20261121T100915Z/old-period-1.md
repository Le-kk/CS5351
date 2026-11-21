# AAPL Fundamental Report — as of 2026-01-09

**The bottom line first:** the five fundamental tools I'm allowed to use (`get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`, `get_insider_transactions`) all returned the **same single record** (reference L2-20261121T100915Z-1, `"synthetic": true`). That record is very thin. None of the detailed statements I asked for came back, so this report can only describe the few figures it contains. Most of the normal fundamental picture for AAPL can't be built from this data, and I have not filled any gaps from memory or outside knowledge.

---

## 1. What the data actually contains

| Item | Availability | Detail |
|---|---|---|
| Income statement (reported) | Partial | 2 quarterly periods only |
| Balance sheet | Very partial | 1 line item (cash) at 1 date |
| Cash flow statement | **Not supplied** | — |
| Company profile | **Not supplied** | — |
| Valuation (price, market cap, multiples) | **Not supplied** ("not available") | — |
| Insider transactions | **Not supplied** ("not available") | — |
| Earnings release calendar (next print) | **Not supplied** | — |
| Analyst expectations, guidance, segment data | **Not supplied** | — |

Every response is a synthetic stand-in (`"synthetic": true`). The reference ID L2-20261121T100915Z-1 is a data-provenance label, **not a financial fact**.

## 2. Reported income (only these periods are available)

| Fiscal label | Period end | Filed | Revenue (USD bn) | EPS (USD) |
|---|---|---|---|---|
| FY2025 Q1 | 2024-12-28 | 2025-01-31 | 124.3 | 2.40 |
| FY2025 Q3 | 2025-06-28 | 2025-08-01 | 94.0 | *not reported* |

Notes and cautions:
- **These two periods aren't adjacent.** The record gives no figures for FY2025 Q2 (which would sit between 2025-03-29 and 2025-06-28, based on the labelling convention of the periods shown), or any quarter after Q3 2025. The record does **not** say those filings are missing or unfiled; it simply omits them.
- **The two figures can't be compared directly as a trend.** FY2025 Q1 (period ending 2024-12-28) ended 2024-12-28, and FY2025 Q3 ended six months later. Comparing the two would show a 24% drop, but that mostly reflects seasonal patterns and the six-month gap, not a real quarter-on-quarter trend. **Don't use these two figures to estimate quarter-over-quarter growth.**
- Although **both filings come before the analysis cutoff of 2026-01-09**, the latest earnings evidence available is the FY2025 Q3 filing from 2025-08-01. That's **more than five months stale** as of the analysis date. There is **no earnings data for the post-June-2025 stretch**, including the December-quarter period.
- No gross margin, operating margin, net income, or segment detail is in the record.

## 3. Periods marked as missing in the income statement

| Period end | Status |
|---|---|
| 2025-09-27 | Marked as missing in the income data. **Not available; not claimed to have reported.** |
| 2025-12-31 | Marked as missing in the income data. **Not available; not claimed to have reported.** This period also ends *before* the analysis cutoff of 2026-01-09, but the company's result for it has clearly **not been filed** in this record. No expected release date was supplied, and I won't guess one. |

I'm deliberately not assigning a fiscal label to 2025-12-31 or 2025-09-27, because a fiscal label can't be borrowed from a different period.

## 4. Balance sheet

| Period end | Filed | Cash (USD bn) |
|---|---|---|
| 2025-09-27 | 2025-10-31 | 35.9 |

- The filing date is before the cutoff, so the cash figure is usable evidence as of 2026-01-09.
- **Only cash is available.** Total assets, total debt, net cash, equity, share count, and buybacks are **not supplied**. With only cash, you can't judge the balance sheet: without the other items, gross and net leverage can't be assessed.
- The balance-sheet date (2025-09-27) doesn't line up with either income period that has figures (2024-12-28 or 2025-06-28), so it can't be matched to them.

## 5. Things to watch for when reading this data

1. **Stale, partial data.** The newest numbers are Q3 2025 revenue (filed 2025-08-01) and cash at 2025-09-27 (filed 2025-10-31). There is nothing from the months just before 2026-01-09.
2. **The December quarter is unresolved.** The 2025-12-31 period is flagged as missing and has no release date on file. Exactly what the market does or doesn't know about it is unclear from this data.
3. **No valuation or price data.** You can't turn earnings into a buy/sell call without valuation, and none is available.
4. **No insider data.** There is no evidence of buying or selling by insiders. Don't read that as "no activity" — the data wasn't supplied.
5. **No cash-flow data.** Dividends, buybacks, and capital spending can't be assessed.

## 6. Data I couldn't retrieve

- Company profile, business description and segments, management and strategy.
- Cash flow statement (any period).
- Full balance sheet (anything beyond one cash line).
- FY2025 Q2, FY2025 Q4, and all periods between 2025-06-28 and 2025-12-31 (not in the record; not claimed to have reported).
- Valuation metrics, market price, market cap.
- Insider transactions.
- Earnings release dates and consensus estimates.
- Guidance, margins, EPS for FY2025 Q3.

## Key Points

| Category | Finding (as of 2026-01-09) | Status / Caveat |
|---|---|---|
| Data source | Synthetic single record, reference L2-20261121T100915Z-1 | `"synthetic": true`; reference ID is not a financial fact |
| Latest income data | FY2025 Q3: revenue $94.0bn, period ended 2025-06-28, filed 2025-08-01 | More than 5 months old; EPS not reported |
| Prior income data | FY2025 Q1: revenue $124.3bn, EPS $2.40, period ended 2024-12-28, filed 2025-01-31 | Not comparable to Q3 (six-month gap, seasonality) |
| Missing income periods | 2025-09-27; 2025-12-31 | Not available; not claimed to have reported |
| Balance sheet | Cash $35.9bn at 2025-09-27, filed 2025-10-31 | Only cash supplied; no assets, debt or equity |
| Cash flow | Not supplied | — |
| Valuation | Not available | — |
| Insider transactions | Not available | Don't read absence of data as no activity |
| Earnings calendar | Not supplied | Release date unknown; not estimated |
| Actionable read | Very limited: one stale quarter's revenue plus one cash figure | No basis for valuation or trend-driven trade in this dataset |

**Disclaimer:** This report comes only from the synthetic tool output above. It contains no outside data, no estimated upcoming results, and no reconstructed figures for missing periods. Any trading use should wait for a dataset with current filings, the full statements, valuation, and insider data.