# AAPL Fundamental Report — as of analysis date 2026-01-09

**Data quality caveat (read first):** All tool results are marked `"synthetic": true`, are identical across the five endpoints called (`get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`, `get_insider_transactions`), and contain no data newer than the analysis cutoff besides one explicitly excluded record. The reference "L2-20261121T100915Z-5" is a synthetic source-vintage identifier, not a financial fact. Nothing below should be treated as real Apple Inc. fundamentals; it describes only what the supplied source vintage contains.

## 1. What the data actually contains

| Item | Status in supplied results |
|---|---|
| Company profile / business description | **Not supplied** |
| Cash flow statement (CFO, capex, FCF) | **Not supplied** (`"cashflow": "not supplied"`) |
| Valuation (P/E, price, market cap, targets) | **Not supplied** (`"not available"`) |
| Insider transactions | **Not supplied** (`"not available"`) |
| Earnings-release calendar (next report date) | **Not supplied** (`"not supplied"`) |
| Income statement periods available | FY2025 Q1 and FY2025 Q3 only |
| Missing income periods flagged by source | 2025-09-27 and 2025-12-31 |
| Balance sheet | One data point: cash as of 2025-09-27 |

## 2. Income statement — usable periods

**FY2025 Q1** — period end 2024-12-28, filed 2025-01-31 (inside cutoff):
- Revenue: **$124.3B**
- EPS: **$2.40**

**FY2025 Q3** — period end 2025-06-28, filed 2025-08-01 (inside cutoff):
- Revenue: **$94.0B**
- EPS: **not reported in the source record**

**Segment or sequential revenue bridge:** Q3 revenue is ~$30.3B (≈24.4%) below Q1 revenue. Because the intervening FY2025 Q2 and the fiscal-year-end period (period end 2025-09-27) are absent, **no seasonal or trend conclusion can be drawn** — this gap may reflect ordinary seasonality, but the source cannot confirm it.

**FY2026 Q1** — period end 2025-12-31, filed **2026-01-29**: **EXCLUDED.** The filing date is 20 days after the 2026-01-09 analysis cutoff, so this period was not yet known and its figures (listed by the source as revenue $999.0B) must not be used. Note also that $999.0B is implausible for a single quarter of this company and appears to be a placeholder/sentinel value in the synthetic dataset — a further reason to discard it rather than cite it.

## 3. Balance sheet

Single observation only: **cash $35.9B as of period end 2025-09-27, filed 2025-10-31.**
- No debt, total assets, equity, inventory, receivables or share-count data was supplied.
- Because only one balance-sheet date exists, **no liquidity trend, net-cash position, or leverage assessment is possible.**
- The $35.9B is as of 2025-09-27 — roughly 3.5 months stale relative to the analysis date.

## 4. Financial history limitations

- Only two of four fiscal-Y2025 quarters have reported figures; the fiscal year-end quarter (2025-09-27) is explicitly missing, so **full-year FY2025 revenue and EPS cannot be computed.**
- FY2025 Q3 lacks EPS, so even the two available quarters cannot be assembled into a consistent EPS series.
- No prior-year comparatives (FY2024 or earlier) were supplied, so **no year-over-year growth rates can be calculated.**
- Cash flow: absent entirely, so free cash flow, capital returns, and cash conversion are **unknown**.

## 5. Actionable interpretation for traders

1. **The most recent fully usable print is FY2025 Q3 (period end 2025-06-28, filed 2025-08-01), ~5 months old.** Any trade premised on "latest fundamentals" is running on stale information.
2. **A next-quarter report is plausibly imminent but cannot be dated from the source.** The excluded FY2026 Q1 record carries a filing date of 2026-01-29, which — if the source vintage is accurate about *scheduling* — implies an information event roughly three weeks after the analysis date. Per the cutoff rule I have **not** treated it as reported, and I will not assert a confirmed release date because the earnings calendar is "not supplied."
3. **Directional data point:** Q3 revenue of $94.0B versus Q1's $124.3B marks a clearly lower-revenue quarter in the middle of the year; without Q2 or seasonality context this is not evidence of deterioration.
4. **Balance-sheet confidence is low:** the lone $35.9B cash figure predates the missing fiscal-year-end filing and says nothing about debt or net cash.
5. **No insider, valuation, or cash-flow signal exists** in this vintage — do not infer absence of insider selling as a bullish signal; the data is simply unavailable.

## 6. Explicitly not retrieved / unknown

- Company profile and business description: **not retrieved**
- Cash flow statement (operating, investing, financing, FCF): **not retrieved**
- Valuation metrics and share price: **not retrieved**
- Insider buying/selling: **not retrieved**
- FY2025 Q2, FY2025 Q4/fiscal-year-end, and all prior-year periods: **not supplied**
- Confirmed next earnings-release date: **unknown** (calendar not supplied)
- FY2026 Q1 actuals: **not available as of 2026-01-09** (filed after cutoff)

## Key points summary

| Category | Detail | Period end | Filed | Status |
|---|---|---|---|---|
| Revenue | $124.3B | 2024-12-28 (FY2025 Q1) | 2025-01-31 | Available |
| EPS | $2.40 | 2024-12-28 (FY2025 Q1) | 2025-01-31 | Available |
| Revenue | $94.0B | 2025-06-28 (FY2025 Q3) | 2025-08-01 | Available |
| EPS | Not reported | 2025-06-28 (FY2025 Q3) | 2025-08-01 | Missing in source |
| Revenue / EPS | Not supplied | 2025-03-31 quarter and 2025-09-27 fiscal year-end | — | Missing income periods |
| Cash | $35.9B | 2025-09-27 | 2025-10-31 | Available (only BS item) |
| Debt / assets / equity | Not supplied | — | — | Unknown |
| Cash flow | Not supplied | — | — | Unknown |
| Valuation | Not available | — | — | Unknown |
| Insider transactions | Not available | — | — | Unknown |
| Earnings calendar | Not supplied | — | — | Unknown |
| FY2026 Q1 revenue figure | Excluded — filed 2026-01-29, after 2026-01-09 cutoff; value also implausible | 2025-12-31 | 2026-01-29 | Not usable |
| Dataset provenance | Synthetic; identical payload returned by all five endpoints | — | — | Verify before any real use |