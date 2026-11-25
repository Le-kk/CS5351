# Interface Contracts (Member B)

Status: architecture draft (revised 2026-11-12 per the Stage-3 architecture review; implementation-aligned 2026-11-24; status refreshed to baseline `6b57aad`, 2026-11-25). Typed shapes were **proposed design contracts** for C (test seams) and D (implementation). As of `a62b801` the core `runapi/` contracts are **implemented** (verified against source; see §12). Where the implementation is narrower than this spec, §12 records the difference; the contract text below is the design of record. Independent acceptance (C) and enforcement (E) remain their owners'. Local role-permission control **exists and is E-native-verified** (69 cases on OpenCode V1 1.19.5), but is **conditionally active only under the explicit compatible launcher/profile**; **local version compatibility and activation remain unresolved** here (the known local executable reports 1.18.34 and launcher startup was refused), so this documentation session is not shown to run strict B. Synthetic examples are **document examples**, not passing application tests; see §11.

This revision designs the required contracts rather than deferring them to D. External-owner items remain: final D1 **adoption** of the 36-entry registry (which **contains** `REQ-TA-INV-014` and `REQ-TA-GOV-004`, both `status: proposed`) (A); C's tests/rubric and independent semantic acceptance; local activation/version-compatibility follow-up for the configured, E-native-verified role-permission package, confirmation of the seven required check names (E-reported; admin HTTP 401), and public-API-snapshot coordination for intentional migrations; instructor layout. `REQ-TA-GOV-004` (schema validation, `SEL-TA-GOV-002`) now has an implemented CI gate (`requirements schema`); runtime contracts here are unchanged by it.

---

## 1. Module map and ownership (addresses B3-10)

Paths below **exist in the `a62b801` checkout** (verified 2026-11-24) except where marked *(existing)*. Ownership is by team role.

| Planned path (new unless marked) | Responsibility | Owner (design / implement / test / enforce) |
|---|---|---|
| `tradingagents/runapi/__init__.py` | Package for the shared application boundary; **no `cli` import** | B / D / C / E |
| `tradingagents/runapi/context.py` | `RunContext`, `FrozenSnapshot`, canonicalization, deep immutability | B / D / C / E |
| `tradingagents/runapi/input_service.py` | `PortfolioInputService` (discover/precheck/freeze) — **noninteractive**, prompt-free | B / D / C / E |
| `tradingagents/runapi/checks.py` | `OutputChecker` (Q1–Q4, deterministic) | B / D / C / E |
| `tradingagents/runapi/result.py` | `RunResult`, `CheckResult`, findings, `InputError` schemas | B / D / C / E |
| `tradingagents/runapi/finalize.py` | `OutcomeFinalizer`, exception mapping | B / D / C / E |
| `tradingagents/runapi/persist.py` | Staging, commit, manifest, publication ordering | B / D / C / E |
| `tradingagents/runapi/events.py` | JSONL `EventSink` | B / D / C / E |
| `tradingagents/runapi/redact.py` | Central `Redactor` (sink boundary) | B / D / C / E |
| `tradingagents/runapi/execution.py` | **Shared application entry service** `run_analysis_api(...)` (see §5) | B / D / C / E |
| `cli/input_ui.py` | Interactive discovery/consent UI (prompts **only** here) | B / D / C / E |
| `cli/main.py`, `cli/run.py` (existing) | Thin adapters: call `execution.run_analysis_api` with confirmed input | adapted |
| `tradingagents/portfolio.py` (existing) | `PortfolioContext` model + `render`; upstream loader unchanged | preserved |
| `tradingagents/agents/context.py`, manager/trader prompts (existing) | Mode-aware wording; no-portfolio Hold meaning | adapted |
| `tradingagents/reporting.py`, `report_html.py` (existing) | Body rendering + final envelope header; projection-driven | adapted |

**Dependency rule:** `cli/*` → `tradingagents/runapi/*` → (engine, agents, portfolio, reporting). `tradingagents/runapi/*` must **not** import `cli`. This keeps the shared boundary usable without a terminal (B3-01, B3-10).

---

## 2. Design types and canonicalization (addresses B3-02, B3-03)

### 2.1 `InputMode`
```
InputMode = NO_PORTFOLIO | PORTFOLIO_PROVIDED
```
- `NO_PORTFOLIO`: holdings/cash unknown; nothing assumed.
- `PORTFOLIO_PROVIDED`: an explicitly selected, validated, frozen snapshot. An explicitly supplied empty `positions` list is a **flat** snapshot, not missing input.

### 2.2 Canonical fingerprint bytes (B3-03, F2)
The new provenance fingerprint is **SHA-256 (64 lowercase hex chars)** over a **canonical JSON byte string** of the normalized snapshot. Exact rules:

1. **Normalized object** contains exactly: `{"cash":…,"currency":…,"positions":[{"ticker":…,"quantity":…,"average_price":…}, …]}`. No other keys participate.
2. **Key order:** lexicographic ascending at every object level (`sort_keys=True`).
3. **Encoding:** UTF-8, **no BOM**, **no trailing newline**; bytes are `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`.
4. **Separators:** `,` and `:` with **no whitespace** (`separators=(",", ":")`).
5. **String escaping:** JSON string escaping only (`ensure_ascii=False`, so non-ASCII tickers are emitted as UTF-8, not `\uXXXX`); no additional escaping. Tickers are trimmed and uppercased before serialization.
6. **Null/default handling:** an absent optional field and an explicit JSON `null` are the **same** and are serialized as the JSON token `null` (`average_price`, `cash`, `currency`).
7. **Number-token serialization (exact):** every numeric field is first converted by `to_canonical_number(x)`:
   - reject non-finite (`NaN`/`±Inf`) at validation (never reach canonicalization);
   - normalize `-0.0` to `0.0`;
   - if the value is integral and `|x| < 2**53`, emit the **integer token** (e.g., `10`, `1`, `0`), so `1` and `1.0` → token `1`;
   - otherwise emit Python `float.__repr__` (shortest round-trippable decimal, e.g., `150.5`, `0.1`).
   This defines the exact byte token; it is not "whatever JSON does".
8. **Positions sort — total order (no `None`/float comparison):** sort the canonical **row objects** by the composite key `(ticker_upper, to_canonical_number(quantity), price_key)` where `price_key = (0, 0.0)` when `average_price is None` and `(1, to_canonical_number(average_price))` otherwise (a tagged tuple: null sorts **before** any number; numeric compares numerically). Because `ticker_upper` is a string and is part of the key, **two different broker spellings that normalize to the same symbol but differ in spelling sort by their hashed spelling**, and a full-row tie is impossible unless all three hashed fields are equal (identical rows are interchangeable, so input order cannot change the digest). This is a **total order over every field that participates in the digest**, so reordering input never changes the digest and no valid portfolio is rejected by sorting.
9. **Symbol spelling:** `ticker` is hashed using the **original spelling** as supplied (trimmed, uppercased). Holdings keep their spelling (`portfolio.py:40-68`); alias matching is a runtime concern, not identity. Two files differing only by broker alias spelling are **different** provenance and therefore **different** digests (both are accepted; ordering above remains total).
10. **Excluded fields:** `basename`, filesystem path, mtime, `portfolio_as_of`, `as_of_basis`, `mode` are recorded separately in metadata, **not** in the content digest.

> Invariant: INV-05. Upstream truncated 12-char checkpoint fingerprint (`portfolio.py:70-72`, `trading_graph.py:158`) is **preserved unchanged** and unrelated to this digest.

#### 2.2.1 Exact canonical-byte examples (verified against the rules above)
Row order after sorting is shown; bytes are exactly the string inside quotes.

- **Reason A — null vs numeric price (reversed input):**
  - Input `[("AAPL",10,None),("AAPL",10,2.0)]` and reversed `[("AAPL",10,2.0),("AAPL",10,None)]` both serialize to
    `{"cash":null,"currency":null,"positions":[{"average_price":null,"quantity":10,"ticker":"AAPL"},{"average_price":2,"quantity":10,"ticker":"AAPL"}]}` → **equal digest** (null sorts before numeric; `10`/`2` are integer tokens).
- **Reason B — broker-alias tie (reversed input):**
  - Input `[("BRK.B",5,100.0),("BRK-B",5,100.0)]` and reversed both serialize to
    `{"cash":null,"currency":null,"positions":[{"average_price":100,"quantity":5,"ticker":"BRK-B"},{"average_price":100,"quantity":5,"ticker":"BRK.B"}]}` → **equal digest** (`"BRK-B"` < `"BRK.B"`; spelling is part of the sort key). Reindexing the **spelling** (e.g., `BRK.B`→`BRK-B` on the other row) is a **different** portfolio by rule 9 and yields a different digest.
- **Reason C — numeric `1` vs `1.0`:**
  - `[("MSFT",1,50)]` cash `1` and `[("MSFT",1.0,50.0)]` cash `1.0` both serialize to
    `{"cash":1,"currency":null,"positions":[{"average_price":50,"quantity":1,"ticker":"MSFT"}]}` → **equal digest**.
- **Reason D — missing vs explicit null:** a position with absent `average_price` and one with explicit `null` serialize identically (`"average_price":null`) → **equal digest**.
- **Reason E — full example with cash:** `[("AAPL",10,150.5),("MSFT",5,None)]`, cash `2500.0`, currency `"USD"` →
  `{"cash":2500,"currency":"USD","positions":[{"average_price":150.5,"quantity":10,"ticker":"AAPL"},{"average_price":null,"quantity":5,"ticker":"MSFT"}]}`
  → SHA-256 `45f07d9eb3359b059525da0cee26f8a9810269dad11ffb4c42e1dcc7072cef72`.
- **Expected difference:** changing `quantity` from `10` to `10.5`, adding a position, or altering cash/currency changes the digest.

These are **document examples** checked against the written rules, not passing application tests.

### 2.3 Deep immutability (B3-03)
Upstream `PortfolioContext` holds a mutable `list[Position]` of mutable model instances. `RunContext` immutability alone is insufficient. Design:

- The frozen snapshot is stored as **immutable value tuples**:
  ```
  FrozenPositions = tuple[tuple[str, float, float | None], ...]   # (ticker, quantity, average_price)
  FrozenSnapshot = (basename, cash: float|None, currency: str|None,
                    positions: FrozenPositions, fingerprint_sha256, portfolio_as_of)
  ```
- `RunContext` is a frozen dataclass holding these tuples; it exposes **no mutable accessor**.
- When agents need a `PortfolioContext`, the boundary **constructs a fresh `PortfolioContext`** from the frozen tuples (defensive copy) on each use; it never hands out a shared mutable object. Mutation of that constructed object cannot affect the stored identity.
- The canonical bytes are computed from the frozen tuples, so they are stable regardless of later copies.

### 2.4 `RunContext`
```
RunContext (frozen dataclass) {
  run_id: str
  ticker: str
  analysis_date: str
  mode: InputMode
  snapshot: FrozenSnapshot | None      # None ⇔ NO_PORTFOLIO
  unverified_holdings: bool
  provider_transmission_disclosed: bool
  consent_state: FROZEN | CONFIRMED    # see §4
}
```
`snapshot is None` **iff** `mode == NO_PORTFOLIO`. `consent_state=FROZEN` ⇒ run not authorized; a snapshot existing does **not** authorize (B3-01, §4).

---

## 3. Complete schemas and conditional fields (addresses B3-02)

All projections below are **separately defined** and **never** serialize the portfolio payload or full `RunContext`. Field names use the selected spelling.

### 3.1 `InputError`
```
InputError {
  kind: "MALFORMED_JSON" | "MISSING_POSITIONS" | "MISSING_QUANTITY" | "NONFINITE_NUMBER"
        | "WRONG_SCALAR_TYPE" | "UNREADABLE_PATH" | "AS_OF_MISMATCH" | "FLAG_CONFLICT"
  basename: str | null          # null when path unreadable before basename known
  field: str | null             # e.g. "positions[2].quantity"
  detail: str                   # redacted, no file contents/credentials
}
```

### 3.2 `Finding`
```
Finding {
  rule: "Q1" | "Q2" | "Q3" | "Q4" | "CHECK_ERROR"
  status: "BLOCKING"
  detail: str                   # redacted
}
```

### 3.3 `CheckResult` (F3 — case table)
```
CheckResult {
  output_check: "PASSED" | "NEEDS_REVIEW" | "NOT_RUN"
  findings: Finding[]
}
```
Authoritative case table (**checker is invoked only on the completed path**, §6):

| Case | `output_check` | `findings` | When |
|---|---|---|---|
| All rules hold | `PASSED` | `[]` (exactly empty) | Completed run; Q1–Q4 all hold |
| Any rule broken OR checker exception | `NEEDS_REVIEW` | **≥ 1** blocking finding (Q1/Q2/Q3/Q4, or a single `CHECK_ERROR` on exception) | Completed run |
| Run incomplete | `NOT_RUN` | `[]` (exactly empty) | Checker **not invoked**; assigned by finalizer branch (§6) |

Invariants (H2 — empty-findings equivalence qualified to **completed** runs): **Completed** ⇒ `PASSED ⇔ findings==[]` and `NEEDS_REVIEW ⇒ findings≠[]`; **Incomplete** ⇒ `NOT_RUN` with `findings==[]` (checker not invoked). There is no global `PASSED ⇔ findings==[]` — `NOT_RUN` also has empty findings.

### 3.4 `RunResult` (returned to caller)
```
RunResult {
  run_id: str
  ticker: str
  analysis_date: str
  input_mode: InputMode
  run_outcome: "COMPLETED" | "INCOMPLETE"
  stop_reason: null | "MODEL_FAILURE" | "DATA_FAILURE" | "INTERNAL_ERROR"
               | "PERSISTENCE_ERROR" | "INTERRUPTED"
  final_rating: null | "Buy" | "Overweight" | "Hold" | "Underweight" | "Sell" | "REVIEW"
  output_check: "PASSED" | "NEEDS_REVIEW" | "NOT_RUN"
  findings: Finding[]
  manifest_path: str | null     # non-null iff the run directory was published (§7)
  report_path: str | null       # non-null iff the report was published (§7)
}
```
**Conditional fields (enforced by finalizer):**
- `COMPLETED` ⇒ `final_rating != null` and `stop_reason == null`.
- `INCOMPLETE` ⇒ `final_rating == null`, `output_check == "NOT_RUN"`, `findings == []`, `stop_reason != null`.

### 3.5 Safe input metadata projection (for sinks; never the payload)
```
SafeInputMetadata {
  run_id, ticker, analysis_date,
  input_mode: InputMode,
  basename: str | null,                 # null iff NO_PORTFOLIO
  fingerprint_sha256: str | null,       # null iff NO_PORTFOLIO (64 hex)
  portfolio_as_of: str | null,          # null iff NO_PORTFOLIO
  as_of_basis: "USER_CONFIRMED" | null  # null iff NO_PORTFOLIO
}
```
The `null` conditions are **portfolio-only** (mode-dependent); distinct from **outcome-conditional** `RunResult` fields.

### 3.6 `SafeRunMetadata` (durable run record; never the payload) — F3
```
SafeRunMetadata {
  schema_version: "1",
  run_id, ticker, analysis_date, input_mode,
  basename: str|null, fingerprint_sha256: str|null, portfolio_as_of: str|null, as_of_basis: "USER_CONFIRMED"|null,
  run_outcome: "COMPLETED" | "INCOMPLETE",
  stop_reason: ... | null,               # §3.4 conditional
  final_rating: ... | null,              # §3.4 conditional — NOW CARRIED IN THE DURABLE RECORD
  output_check: "PASSED" | "NEEDS_REVIEW" | "NOT_RUN",
  findings: Finding[],
  code_version: str,                     # tradingagents.__version__
  source_revision: str | null,           # separate source identifier, e.g. git describe or "unknown" (§3.7)
  prompt_hash: str,                      # §3.8
  effective_config: EffectiveConfig,     # §3.7
  start_ts_utc: str, end_ts_utc: str     # ISO-8601 UTC; set once at finalize
}
```
The **same** `final_rating` spelling/conditional rules as `RunResult` apply. Timestamps are captured once at finalize and are never mutated later.

### 3.7 `EffectiveConfig` (safe, behaviour-relevant; secrets/endpoints omitted) — F3
```
EffectiveConfig {
  llm_provider, deep_think_provider, deep_think_llm, quick_think_provider, quick_think_llm,
  analysts: str[], max_debate_rounds: int, max_risk_discuss_rounds: int,
  output_language: str,
  temperature: float | null, max_tokens: int | null,          # behaviour-affecting (baseline keys if set)
  context_cap_tokens: int, compaction_threshold_tokens: int,  # the designed context budget (ADR §Context)
  concise_intermediate_reports: bool,                         # concise-mode flag (feature 9102759); see §3.11/§3.8
  data_vendors: map, tool_vendors: map
}
```
Derived from `run_settings()` (`trading_graph.py:255-275`) **plus** the behaviour-affecting keys this design introduces (`temperature`, `max_tokens`, context cap/threshold, and the concise-mode flag). `backend_url`, keys, OAuth tokens, local paths are **never** included. `source_revision` is recorded **separately** from `code_version` (upstream `version` stays `0.7.1`; the revision id identifies the actual source state and is `"unknown"` when unavailable).

- **Concise-mode recording (integrated at `adb4dfc`):** the flag is recorded in `run_settings()` and `_effective_config()` with default `True`. An **old artifact that lacks the field** must NOT be read as having run with today's `True` default; absence is `unknown/legacy`, not `False` and not `True`. Do not infer historical mode from a missing field.
- **Mode is recorded separately from `prompt_hash`** (§3.8): the flag itself does not enter the hash material, but the feature's prompt-source edits do.

### 3.8 `prompt_hash` (deterministic input spec) — reconciled to the actual implementation

The implemented `_prompt_hash` (`tradingagents/runapi/execution.py`) hashes **selected source-file contents plus frozen strings**, not an extracted active runtime template/legend variant:

- **Inventory:** a fixed, selected set of prompt/source files — `agents/structured.py`, `agents/analysts/turn.py`, `portfolio.py`, `agents/context.py`, `agents/managers/research_manager.py`, `agents/managers/portfolio_manager.py`, `agents/trader/trader.py`, `agents/researchers/bull_researcher.py`, `agents/researchers/bear_researcher.py`, `agents/risk_mgmt/aggressive_debator.py`, `agents/risk_mgmt/conservative_debator.py`, `agents/risk_mgmt/neutral_debator.py`, plus the registered source file for each **selected** analyst (`market → agents/analysts/market_analyst.py`, `social → agents/analysts/sentiment_analyst.py`, `news → agents/analysts/news_analyst.py`, `fundamentals → agents/analysts/fundamentals_analyst.py`), plus the two frozen strings `frozen.disclaimer` (`DISCLAIMER`) and `frozen.no_portfolio_notice` (`NO_PORTFOLIO_NOTICE`). Identifiers such as `agents/context.py` are **relative to the `tradingagents` package directory** (the implementation resolves them as `Path(__file__).resolve().parents[1] / relative`); **their exact strings are preserved** in the hash material.
- **Source reading:** contents are read with `Path.read_text(encoding="utf-8")`, which opens in text mode and therefore applies **universal-newline translation** (`CRLF` and lone `CR` are translated to `LF` in the returned `str`). The returned text is hashed as-is; the implementation performs **no additional stripping or newline cleanup** beyond that text-mode translation. Characters already in the returned text remain included (no separate BOM removal or newline insertion outside the literal construction below). A file that raises `OSError` when read is **skipped** (not hashed) — see `risk-list.md` R-HASH.
- **Serialization (exact byte construction):**
  ```
  material = "\n\n".join(f"{identifier}\n{text}" for identifier, text in sorted(pairs))
  digest   = SHA256(material.encode("utf-8")).hexdigest()   # 64 lowercase hex
  ```
  where each `pairs` entry is `(identifier, text)` — `identifier` is the package-relative path (e.g. `agents/context.py`, preserved exactly) or the frozen-string key; `text` is the read (universal-newline-translated) file content or frozen string. `sorted(pairs)` sorts by the tuple (identifier first). The implementation adds no separate BOM or newline outside this literal construction; characters already in the returned text (including any leading BOM passed through by the decoder) remain included. This is the actual `_prompt_hash` construction, not a generic "joined deterministically" description. (The concise-context feature edits several included files, so it **changes `prompt_hash` for new runs even when concise mode is disabled** — the hash tracks source content, not the flag.)
- **Scope:** it hashes selected **source-file contents** and frozen strings; it does **not** serialize only the active template/legend variant actually rendered for this run.
- **Excluded:** dynamic holdings/evidence and the frozen portfolio **fingerprint** (separate identity, INV-04/05). Editing any included source file or frozen string changes `prompt_hash`.
- **Historical artifacts:** older `prompt_hash` values remain valid for their runs; do not recompute or relabel them with today's sources.

### 3.9 `Event` (JSONL)
```
Event {
  run_id, ticker,
  node: "input" | "engine" | "output",
  ts: str (UTC ISO-8601),
  elapsed_ms: int (>=0, monotonic),
  event: str,                 # e.g. input.selection, input.consent, run.terminal, output.check, output.persist
  event_outcome: str          # progress vocabulary, separate from run_outcome
}
```
Exactly one `event=run.terminal` logical decision per run (§7.5).

### 3.10 Final manifest (`manifest.json`) — F1/F3
```
Manifest = SafeRunMetadata + {
  report_paths: { markdown: str|null, html: str|null },
  terminal_event: { logical: "run.terminal", durable: bool }   # durable = JSONL terminal write succeeded before publication
}
```
The manifest is written **once**, atomically, **as part of the single publication commit** (§7), and contains **no** positions/cash/other-position list and no secrets. `terminal_event.durable` is known **before** publication because the terminal event is written **before** the commit (or its outcome is decided then) — a later append never changes the immutable manifest.

#### 3.10.1 Manifest examples (document examples; values illustrative)
Completed, portfolio-provided (fingerprint from §2.2.1 Reason E):
```
{"schema_version":"1","run_id":"20261112T101500Z-ab12cd","ticker":"AAPL","analysis_date":"2026-11-12",
 "input_mode":"PORTFOLIO_PROVIDED","basename":"b.json",
 "fingerprint_sha256":"45f07d9eb3359b059525da0cee26f8a9810269dad11ffb4c42e1dcc7072cef72",
 "portfolio_as_of":"2026-11-12","as_of_basis":"USER_CONFIRMED",
 "run_outcome":"COMPLETED","stop_reason":null,"final_rating":"Overweight","output_check":"PASSED","findings":[],
 "code_version":"0.7.1","source_revision":"git:abc1234","prompt_hash":"<64hex>",
 "effective_config":{"llm_provider":"openai","deep_think_llm":"gpt-x","quick_think_llm":"gpt-y","analysts":["market","news"],"max_debate_rounds":2,"max_risk_discuss_rounds":2,"output_language":"English","temperature":0.2,"max_tokens":4096,"context_cap_tokens":24000,"compaction_threshold_tokens":19200,"concise_intermediate_reports":true,"data_vendors":{},"tool_vendors":{}},
 "start_ts_utc":"2026-11-12T10:15:00Z","end_ts_utc":"2026-11-12T10:18:22Z",
 "report_paths":{"markdown":"reports/complete_report.md","html":"reports/complete_report.html"},
 "terminal_event":{"logical":"run.terminal","durable":true}}
```
Incomplete, no-portfolio (persistence failure example):
```
{"schema_version":"1","run_id":"20261112T090000Z-ef34gh","ticker":"NVDA","analysis_date":"2026-11-12",
 "input_mode":"NO_PORTFOLIO","basename":null,"fingerprint_sha256":null,"portfolio_as_of":null,"as_of_basis":null,
 "run_outcome":"INCOMPLETE","stop_reason":"PERSISTENCE_ERROR","final_rating":null,"output_check":"NOT_RUN","findings":[],
 "code_version":"0.7.1","source_revision":"git:abc1234","prompt_hash":"<64hex>",
 "effective_config":{...},"start_ts_utc":"2026-11-12T09:00:00Z","end_ts_utc":"2026-11-12T09:03:10Z",
 "report_paths":{"markdown":null,"html":null},"terminal_event":{"logical":"run.terminal","durable":true}}
```
(Conditional rules hold: COMPLETED has a rating and `stop_reason=null`; INCOMPLETE has `final_rating=null`, `output_check=NOT_RUN`, `findings=[]`, a `stop_reason`, and null report paths.)

### 3.11 Concise intermediate context assembly (integrated at `adb4dfc`, PR #18; contract scope)

Scoped to **intermediate context assembly** during analysis execution (blueprint §5 step 6). This section does **not** change checker/evidence/budget semantics.

- **`concise_analysis_instruction(stage)`** returns advisory evidence-first brevity text (~450 words for `analyst`, ~220 for `debate`) when `concise_intermediate_reports` is enabled, else `""`. **Placement differs by path:** in `analysts/turn.py` it is appended to the **assembled system message** (preserving tool schemas, call IDs and original input messages) on both tool-bound and wrap-up paths; in the Bull/Bear researchers and three risk debaters it is appended to their **assembled prompt strings**. It is advisory; it does not truncate and does not replace the existing guard.
- **Reference substitution** — `opponent_argument_or_opening(text, opponent, history)`: when `text.strip()` is non-empty, concise mode is enabled, and the exact stripped text occurs in `history`, return a reference notice instead of repeating it; an empty opponent yields an explicit opening notice. This is **exact Python string-substring matching**, not semantic deduplication.
- **Compaction safeguard** — `bound_debate_prompt(prompt, history, arguments)`: reconstruct the explicit copies; compute `threshold = min(context_cap_tokens, compaction_threshold_tokens) * 4`; if the reconstructed-original length exceeds `threshold`, pass the **restored** form to the existing `bound_agent_prompt` guard, else pass the reference form. **No unconditional no-dangling guarantee:** the reference notice can be longer than the argument it replaces, so the reference form can exceed the guard target even when the restored-original length fits; checking only the restored-original length can miss compaction of the reference form (and its cited history). The safeguard reduces but does not eliminate dangling-reference risk. See `docs/reviews/evidence/token-context-reference-probe-2026-11-24.json`; follow-up for E/C (risk `R-CONCISE`). It is **not** a guarantee every evidence item survives compaction.
- **No new forced truncation:** the feature adds no truncation of output or tool payloads; the existing per-prompt character/4 guard still trims narrative when a prompt exceeds its limit.
- **Kept separate:** the existing per-prompt guard (`bound_agent_prompt`, character/4 estimate — described in blueprint §5 and ADR-001's historical-vs-current clarification) and the proposed run-wide `CALL_CAP`/`BUDGET` controller (ADR-002 D3) are distinct; concise mode is neither.
- **Config/rollback:** `concise_intermediate_reports` default `True`; `TRADINGAGENTS_CONCISE_INTERMEDIATE_REPORTS=false` or programmatic `False` restores legacy. Recorded in `run_settings()`/`EffectiveConfig` (§3.7); the flag is not part of `prompt_hash`, but the touched prompt sources are (§3.8).

---

## 4. Input-mode state machine (addresses B3-08; both modes complete)

Interactive discovery/consent lives only in `cli/input_ui.py`. The **noninteractive service** (`input_service.py`) accepts explicit inputs/paths.

```
START
 ├─ explicit --portfolio PATH ─────────────► VALIDATING_EXPLICIT
 ├─ explicit --without-portfolio ──────────► NO_PORTFOLIO_FREEZE
 └─ interactive, no explicit flags ────────► DISCOVERING
DISCOVERING
 ├─ eligible files present ──► SELECTING ──cancel──► CANCELLED
 ├─ missing or empty dir ────► NO_PORTFOLIO_CONFIRM   (never described as "empty" if errored)
 └─ directory read error ────► DIR_ERROR ──retry──► DISCOVERING
                              └──choose no-portfolio──► NO_PORTFOLIO_CONFIRM
                              └──cancel──► CANCELLED
SELECTING ──file chosen──► VALIDATING
VALIDATING ──invalid──► INVALID ──reselect──► SELECTING / ──cancel──► CANCELLED
VALIDATING_EXPLICIT ──(noninteractive: --portfolio-as-of D required, D == analysis date)──►
   ──valid──► PORTFOLIO_FREEZE   ──invalid/as-of-mismatch/flags-conflict──► INPUT_ERROR (zero run)
VALIDATING ──valid──► PORTFOLIO_FREEZE
PORTFOLIO_FREEZE  (freeze bytes → FrozenSnapshot; consent_state=FROZEN)
   ──interactive: show notice (basename, D, unverified/as-of, provider-transmission)──► AWAITING_CONSENT
   ──noninteractive: explicit --portfolio already expresses consent──► CONFIRMED
AWAITING_CONSENT ──yes──► CONFIRMED ; ──no/EOF──► CANCELLED
NO_PORTFOLIO_FREEZE
   ──interactive: show frozen no-portfolio notice──► NO_PORTFOLIO_CONFIRM
   ──noninteractive: --without-portfolio expresses consent──► CONFIRMED
NO_PORTFOLIO_CONFIRM ──yes──► CONFIRMED ; ──no/EOF──► CANCELLED
CONFIRMED ──► RUNNING
CANCELLED / INPUT_ERROR → zero graph, zero LLM, no completed run
```

- **Both modes** reach a frozen candidate and explicit confirmation (interactive) or explicit flag consent (noninteractive).
- **Noninteractive flag rules:** neither `--portfolio` nor `--without-portfolio` ⇒ `INPUT_ERROR` (zero calls); **both** ⇒ `INPUT_ERROR`; `--portfolio` without `--portfolio-as-of` ⇒ `INPUT_ERROR`; `--portfolio-as-of` with `--without-portfolio` ⇒ `INPUT_ERROR`; `--portfolio-as-of D` ≠ analysis date ⇒ `AS_OF_MISMATCH`.

### 4.1 Consent as explicit transitions (B3-01; immutability ≠ bypass prevention)
| From | Trigger | To | Guard |
|---|---|---|---|
| `FROZEN` (PORTFOLIO_FREEZE/NO_PORTFOLIO_FREEZE) | interactive Yes, or valid explicit flag | `CONFIRMED` | notice for portfolio shown first (interactive) |
| `FROZEN` | interactive No/EOF/cancel | `CANCELLED` | zero run |
| `CONFIRMED` | (any) | `RUNNING` | **only** path to `execution.run` |

`execution.run_analysis_api` **rejects** a `RunContext` whose `consent_state != CONFIRMED`. A frozen snapshot existing does **not** authorize execution; the transition does.

- **No silent reread:** after freeze the file is never reopened; frozen bytes are the sole input.
- **Disclosure sequencing:** only the **notice** precedes consent; holdings are transmitted to the provider **only after** `CONFIRMED` (during `RUNNING`). No provider transmission before consent.

---

## 5. Shared CLI/API execution boundary (addresses B3-01, B3-10)

The **common application entry service** routes **every supported entry point** through the mandatory checks/finalization/persistence:

```
# tradingagents/runapi/execution.py  (prompt-free; no cli import)
run_analysis_api(
    run_context: RunContext,          # consent_state must be CONFIRMED
    graph_factory: Callable[..., Engine],  # injectable for tests; default TradingAgentsGraph
    event_sink: EventSink,
    redactor: Redactor,
) -> RunResult
sequence: validate_consent → engine.stream_run(portfolio or None)
          → render_body → check → finalize → stage → publish → terminal event
```

### 5.1 Entry points and which boundary they traverse
| Entry point | Interaction | Boundary traversal | Requirement coverage |
|---|---|---|---|
| CLI interactive (`cli/main.py`) | prompts in `cli/input_ui.py` | freezes+confirm → `run_analysis_api` | Full (FR/NFR) |
| CLI noninteractive (flags) | none | flags → freeze → `run_analysis_api` | Full |
| **Supported project API** (`tradingagents.runapi.execution.run_analysis_api`) | none | supplies a `RunContext` (built via input service or explicit `portfolio`/`None`) → `run_analysis_api` | Full |
| Low-level engine primitive (`TradingAgentsGraph.propagate/stream_run`) | none | **raw**; **does not** traverse the boundary | **Reduced** — see §5.3 |

### 5.2 Supported project API signature
The upstream engine signature is **preserved** (`trading_graph.py:167,293`: `portfolio=None|PortfolioContext`). A programmatic caller wanting the full contract uses:
```
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import freeze_explicit  # builds a FROZEN RunContext
ctx_frozen = freeze_explicit(ticker, analysis_date, portfolio=PortfolioContext(...) | None)  # no prompt; consent_state=FROZEN
ctx_confirmed = ctx_frozen.confirm()                      # explicit programmatic consent transition
result: RunResult = run_analysis_api(ctx_confirmed, event_sink=..., redactor=...)
```
- **Consent is consistent across all entry points:** `freeze_explicit` **always** returns `consent_state=FROZEN`; a programmatic caller must perform an explicit `confirm()` transition (the programmatic expression of consent; no prompt, no provider transmission before `run_analysis_api`). This matches the CLI/interactive rule that a frozen context is not executable.
- `freeze_explicit(..., portfolio=None)` ⇒ `NO_PORTFOLIO` RunContext with `basename/fingerprint/as_of=null`. `portfolio=PortfolioContext(...)` (in-memory) ⇒ frozen snapshot with **synthetic provenance**: `basename="<in-memory>"`, `fingerprint_sha256=<64-hex over §2.2 canonical bytes>`, `portfolio_as_of=<analysis_date>`, `as_of_basis="USER_CONFIRMED"` (the caller asserts the in-memory book is intended for that date).
- This path runs checks/finalization/redaction/single-commit publication — no compliance gap (B3-01 resolved at design level).

### 5.3 Low-level primitive (precise scope; A approval required for reduced coverage)
`TradingAgentsGraph.propagate/stream_run/create_run_state` remain available unchanged for baseline compatibility and upstream tests. They **do not** provide the output checker, outcome finalizer, redaction, manifest or events. Scope and honesty:
- Use is legitimate for baseline/existing upstream behaviour and for engine-level tests only.
- A caller using **only** the raw primitive **does not** satisfy FR-006/FR-007/NFR-002/003/004. This is a **declared, scoped low-level compatibility path**; **A must approve** any excluded requirement coverage if a product-facing path relies on it (R-API, pending A). It is not a D design task; only A's acceptance of reduced coverage is pending.
- **Mandatory CLI traversal:** the CLI (`cli/main.py`, `cli/run.py`) **must** call `run_analysis_api` for all product runs; it may not call the raw primitive directly. The raw primitive is not a product entry point.

---

## 6. Render / check / final envelope ordering (addresses B3-04)

**Problem fixed:** the check must run on content that does *not* yet contain its own result, yet the delivered header must display the check result. Resolution: separate the **immutable checked body** from the **trusted final envelope**.

### 6.1 Two-part document
- **Body** (model-generated sections + trusted frozen notice/disclaimer): rendered once from `final_state` + `RunContext`, **redacted before check**.
- **Pre-check provenance fragment** (trusted, deterministic): the exact header lines Q2 will inspect — analysis date, input mode, basename, full-64 fingerprint, as-of/basis — rendered from `SafeInputMetadata` **before** the check. This is the object Q2 compares; it is not the checker comparing metadata to itself, because it is an independently produced text fragment.
- **Envelope** (trusted): the delivered header, built **after** the check from `SafeRunMetadata` (which now includes outcome/check). It opens with the trusted frozen `DISCLAIMER` + blank separator, then the title/provenance/outcome/check lines, and must byte-match the pre-check provenance fragment for its Q2 fields (verified again before publication, §6.4). The deliverable is `final_doc_md = envelope + body`; the body keeps its own disclaimer footer (§6.4).

### 6.2 Single authoritative check — completed path only (F4)
```
1. final_state  (or an exception → go to 6.3 INCOMPLETE branch; checker NOT called)
2. body = render_body(final_state, RunContext)                 # trusted strings inserted
3. body = redactor.scrub(body)                                 # redaction BEFORE check
4. provenance_fragment = render_provenance(SafeInputMetadata)  # trusted header text Q2 inspects
5. final_rating = run_rating(final_state)  |  REVIEW           # deterministic
6. CheckResult = OutputChecker.evaluate(                        # ONE authoritative call
        trusted: SafeInputMetadata,     # Q2 authoritative expected values (explicit argument)
        provenance_fragment: str,       # Q2 subject (independently rendered trusted text, compared to `trusted`)
        final_rating: str,              # Q1 subject
        rendered_body: str)             # Q3/Q4 subject (disclaimer excluded from Q4)
   # if the checker raises → CheckResult{NEEDS_REVIEW,[CHECK_ERROR]} (fail closed, single decision)
7. result = OutcomeFinalizer.finalize(graph_returned=True, final_rating, exc=None)  # COMPLETED
8. envelope = build_envelope(SafeRunMetadata(result, CheckResult))   # uses the FROZEN CheckResult; no second verdict
9. verify_envelope_header_matches(envelope, trusted)     # publication-time guard vs AUTHORITATIVE metadata (§6.4)
10. final_doc_md = envelope + body ; final_doc_html = render_html(envelope, body)
11. stage → single publication commit (§7)
```
- The checker is invoked **exactly once** on the completed path; the envelope consumes the **frozen** `CheckResult`.
- **Q2 has a real subject and explicit trusted values:** Q2 compares `provenance_fragment` (independently rendered pre-check text) against the **explicitly supplied trusted `SafeInputMetadata`** argument. A fragment whose basename/fingerprint/as-of differs from trusted metadata produces a **Q2** finding, not a guaranteed pass. The trusted metadata is a call argument, not ambient state.

### 6.3 Incomplete branch — checker bypassed (F4)
```
1. engine raised OR graph did not return a usable final_state
2. result = OutcomeFinalizer.finalize(graph_returned=False, final_rating=None, exc=exc)
3. CheckResult = CheckResult{output_check:"NOT_RUN", findings:[]}   # assigned directly; checker NOT invoked
4. envelope = build_envelope(SafeRunMetadata(result, CheckResult))   # INCOMPLETE, NOT_RUN, no rating
5. no successful report body is published as PASSED; partial artifacts labelled INCOMPLETE (§7)
```
The checker signature never receives graph-returned data on this path, so there is no contradictory double verdict.

### 6.4 Envelope verification and source-of-truth (F4, H3)
- `OutputChecker.evaluate(trusted, provenance_fragment, final_rating, rendered_body)` calls no provider. Q1 = rating readable; **Q2 = every Q2 field in `provenance_fragment` equals the explicit trusted `SafeInputMetadata`** argument; Q3 = disclaimer present in body; Q4 = prohibited phrases absent in body (disclaimer excluded).
- **Publication-time guard — against authoritative metadata:** before the commit, the build verifies that the envelope's Q2 fields equal the **trusted `SafeInputMetadata`** (the same authoritative expected values). The guard does **not** compare the envelope to the possibly-defective `provenance_fragment`; it validates both the fragment's finding (already recorded by the checker) and the delivered envelope against the authoritative values.
- **Q2-defect path (consistent):** if the fragment disagrees with trusted metadata, the checker records a `Q2` finding (`NEEDS_REVIEW`) and that finding is **retained**; the envelope is built from trusted metadata (a **corrected** header) and passes the guard because it matches authoritative values. The run delivers the corrected header labelled `NEEDS_REVIEW` with the original Q2 finding — it is neither silently marked clean nor claimed to have equal-but-unequal values.
- **Disclaimer placement — leading notice + retained footer (as-built H5).** The Markdown deliverable is `final_doc_md = envelope + body`. The **envelope** begins with the trusted frozen `DISCLAIMER` followed by a blank separator, then the title/trusted provenance/outcome/check lines (`build_envelope`); the **body** retains its existing `## Disclaimer` footer (`render_body`). The frozen disclaimer string is a **single content source** even though its text appears in **two locations** (leading notice and footer); the notice is emitted by the **trusted renderer, not an LLM**. Q3 continues to check the disclaimer's presence in the **redacted rendered body**; Q2 continues to check trusted provenance — the check subject is unchanged. The static leading disclaimer does **not by itself** require a product schema bump.
- **HTML + legacy-exporter layout (as-built H5).** `report_html.render_report` emits an **escaped** disclaimer paragraph (`<p class="disclaimer">` with the frozen string) **before the masthead**, inside the valid `<!doctype html>`/`<head>`/`<body>` structure — visible leading report content, **not** literal prose before the doctype. This leading notice is **unconditional** (present whether `run_metadata` is `None`, empty or populated); the earlier metadata-only limitation is removed. The legacy `reporting.write_report_tree` now **prefixes `complete_report.md`** with the same frozen `DISCLAIMER` + blank separator. A explicitly chose **first rendered visible content** (Markdown: first nonblank line; HTML: structural markup excluded) and **permits the retained compatibility footer**. Broader consumer/reader acceptance and per-agent section fragments (which are not complete reports) are only established where a specific test/probe exists, else pending.
- **Redaction precedes checks**, so a checked artifact cannot later be invalidated by redaction.

### 6.5 Walkthroughs (synthetic; document examples; verified against §6.2–§6.4)
- **Completed-PASS (no-portfolio):** `final_rating="Hold"`; `provenance_fragment` renders `input_mode=NO_PORTFOLIO`, basename/fingerprint/as-of `null`; body has disclaimer, no prohibited phrase → `CheckResult{PASSED,[]}`; `RunResult{COMPLETED, stop_reason=null, final_rating="Hold", output_check=PASSED}`; envelope shows PASSED; guard passes (envelope matches trusted metadata).
- **Completed-REVIEW (Q2 defect):** renderer bug renders `basename="c.json"` in the `provenance_fragment` while trusted `SafeInputMetadata.basename="b.json"` → Q2 fails on the single checker call → `CheckResult{NEEDS_REVIEW,[Q2]}` (finding retained); `RunResult{COMPLETED, output_check=NEEDS_REVIEW}`; the envelope is built from trusted metadata (`b.json`, corrected) and the guard passes because it matches the **authoritative** metadata; the delivered header shows `b.json` and the retained Q2 finding, outcome not silently clean.
- **Completed-REVIEW (Q4):** body contains `guaranteed profit` outside disclaimer → `Finding{Q4}`; `NEEDS_REVIEW`.
- **Checker-error:** checker raises on the single call → `CheckResult{NEEDS_REVIEW,[CHECK_ERROR]}`; graph returned so `COMPLETED`; `output_check=NEEDS_REVIEW`; no second call to disagree.
- **Graph-failure (INCOMPLETE):** exception → INCOMPLETE branch; **checker not invoked**; `output_check=NOT_RUN`, `final_rating=null`, `stop_reason` set; nothing published as PASSED.

### 6.6 Rendering order for agents (identity vs display)
Canonicalization sorts positions for hashing; `PortfolioContext.render()` keeps upstream ordering for the prompt. Identity and display are intentionally separate; neither mutates the frozen tuple.

---

## 7. Staging, single publication commit, and terminal-event ordering (addresses F1)

### 7.1 Single publication commit point
The run directory is the unit of atomic publication on the same filesystem:
```
STAGING dir: <results>/_staging/<run_id>/         # not visible as a successful run
  reports/complete_report.md  (and .html if enabled)   # final envelope + checked body
  manifest.json                                        # fully populated incl. terminal_event.durable
COMMIT:  os.replace/rename  <results>/_staging/<run_id>  ->  <results>/<ticker>/<run_id>/
```
- **One commit point.** Everything the manifest describes (report MD/HTML, manifest itself) is written into the **staging** directory **first**; the **only** publication action is a single atomic directory rename. Before the rename, nothing exists at the published path; after it, a complete, self-consistent run directory exists.
- **No success is visible before the commit.** There is no earlier `rename` of the report into the published location; the "report staged but unpublished" state is real because the report lives only under `_staging`.
- **Terminal event ordering (truthful durability):** the **logical** terminal decision is computed before commit. The **JSONL terminal event is appended to the staging `events.jsonl` before the commit**, so its success/failure is **known before** the manifest is finalized. `terminal_event.durable = (jsonl terminal append succeeded)`. A later event append is **not** part of the immutable manifest's claim; best-effort events written after commit are separate and cannot change `manifest.json`.
- **Caller-visible terminal is resolved on commit (R5).** The terminal is first **staged privately** on the `EventSink` (included in the staged `events.jsonl` for durability, but not in the caller-inspectable `events`). Only after the single directory rename succeeds is the tentative terminal **committed** into the caller-visible event list (`commit_terminal`). If the critical report/manifest staging or the rename fails, the tentative terminal is **discarded** and `run_analysis_api` emits exactly one matching `INCOMPLETE` terminal, so a caller-owned sink can never retain a COMPLETED terminal for an unpublished run. The post-rename reveal is a **best-effort callback**: its failure does not revise the already-published logical outcome. Normal completed and engine-incomplete runs still expose exactly one matching terminal. The single-terminal rule is preserved. A legacy sink without the staging protocol has the terminal written into the staged file (truthful `durable`) and the one terminal emitted after the rename.
- **Reader behaviour:** a run directory is a valid published run iff it exists at `<results>/<ticker>/<run_id>/` (the rename completed). `_staging/**` is never treated as a published run. Readers may ignore `_staging`.

### 7.2 Sink criticality
| Sink | Criticality | Rule (with single-commit) |
|---|---|---|
| Report MD (and HTML if enabled) | **Critical** | Written to staging; part of the commit unit |
| Manifest | **Critical** | Written to staging with final `terminal_event.durable`; part of the commit unit |
| JSONL terminal event | **Best-effort (not critical)** | Appended to staging **before** commit; its outcome sets `terminal_event.durable` but **does not** block publication and does **not** change the logical outcome |
| Other JSONL progress events | Best-effort | May be appended pre- or post-commit; failure ⇒ redacted note; never changes the immutable manifest |
| State JSON / message log | Best-effort | Written to staging or post-commit; failure ⇒ redacted note; does not flip a completed decision |

### 7.3 Failure mapping (one per path)
- **Critical staging write fails** (report or manifest) **before commit:** no rename performed; nothing appears at the published path; result `INCOMPLETE`, `stop_reason=PERSISTENCE_ERROR`, `final_rating=null`, `output_check=NOT_RUN`, `findings=[]`, `report_path=null`, `manifest_path=null`. Staging dir is cleaned or left under `_staging` (not published).
- **Commit rename fails:** same as above — nothing published; typed `PERSISTENCE_ERROR`.
- **Best-effort sink fails (progress event / state log / message log):** the commit still proceeds; outcome is unchanged (`COMPLETED`/…); a redacted note is recorded; `terminal_event.durable` reflects the **terminal** append only.
- **Terminal-event append to staging fails (best-effort):** the **logical outcome is preserved** (`COMPLETED` if the graph returned); `terminal_event.durable=false` is recorded in the staging manifest **before** commit; the run directory is still published (report+manifest valid). This is **not** a critical failure and does **not** return `PERSISTENCE_ERROR`.
- **Logical outcome revision:** `OutcomeFinalizer` produces the logical outcome; only a **critical report/manifest staging-or-commit** failure (before any publication) revises the returned result to `INCOMPLETE/PERSISTENCE_ERROR`. Since nothing is published before commit, no published PASSED/COMPLETED can contradict the returned result. On such a failure the stage-private tentative terminal is discarded and exactly one `INCOMPLETE` terminal is emitted to the caller sink (R5).
- **Full-disk/power-loss durability:** out of scope; `PERSISTENCE_ERROR` is the cooperative contract.

### 7.4 Reconciliation with earlier finalization
`OutcomeFinalizer` sends the logical outcome and `terminal_event.durable` into the staging manifest **before** commit. If critical persistence fails, the **returned** result is revised to `INCOMPLETE/PERSISTENCE_ERROR` (satisfying INV-08); nothing was published, so there is no stale success artifact.

### 7.5 Chronological failure walkthroughs (document examples; states verified against §7.1–§7.4)
Legend: `VISIBLE` = present at published path; `STAGED` = under `_staging` only.

- **(a) Report staging write fails:** after staging the manifest is attempted? **No** — report write fails first → abort; no manifest, no commit. `STAGED`: partial report maybe; `VISIBLE`: nothing; returned `INCOMPLETE/PERSISTENCE_ERROR`, rating null, NOT_RUN, `report_path=null`, `manifest_path=null`.
- **(b) Manifest staging write fails:** report written to staging; manifest write fails → abort before commit; `STAGED`: report; `VISIBLE`: nothing; returned `INCOMPLETE/PERSISTENCE_ERROR`; no paths. No published COMPLETED exists.
- **(c) Final publication (rename) fails:** staging complete (report+manifest+terminal event); rename fails → `STAGED`: full run; `VISIBLE`: nothing; returned `INCOMPLETE/PERSISTENCE_ERROR`; no paths. Reader sees no published run.
- **(d) Best-effort JSONL progress write fails (after terminal already staged):** commit proceeds; `VISIBLE`: full run with `manifest.terminal_event.durable=true` (terminal append succeeded); returned `COMPLETED/…`; a redacted note about the dropped progress event. Immutable manifest unchanged by the dropped progress event.
- **(e) Terminal-event append to staging fails (best-effort):** `terminal_event.durable=false` recorded in the staging manifest **before** commit; commit still publishes the run directory (report+manifest valid); returned outcome is the **logical outcome** (COMPLETED if graph returned) — **not** PERSISTENCE_ERROR; a redacted note. The manifest truthfully states the terminal event is **not durable**; no later append alters it.

No walkthrough publishes a report that contradicts the returned terminal result.

---

## 8. CLI / API contract changes (intentional)
- Added: `--without-portfolio`; `--portfolio-as-of D`. Preserved: `--portfolio PATH` (may be outside `PORTFOLIO_DIR`; parent not scanned).
- Prompts suppressed under explicit flags; conflicts ⇒ `InputError` (no default). Intentional CLI changes (FR-002) recorded in ADR; not accidental compatibility failures.

## 9. Escaping and provenance values
- HTML escapes all model/file/provenance values (`report_html.py:10,226,255`); envelope values escaped too. Header uses `SafeInputMetadata`, never the payload.

## 10. Evaluation population interface (addresses B3-11; as-built `EvaluationPopulation` + `summarize_records`)

NFR-006 requires completion accounting over **started fresh runs**, with pre-run cancellations counted separately and **zero-completed ⇒ insufficient evidence**. The merged helper (`tradingagents/runapi/result.py`) is a **single-configuration declaration**, not the earlier deferred per-case sidecar design.

```
summarize_records(records: list[RunRecord], *, population: EvaluationPopulation | None = None) -> dict
```

`RunRecord` (one per attempt; persisted only in evaluation datasets, **NOT** in the run manifest) keeps its existing fields, then **four optional binding fields**:
```
RunRecord
  attempt_id: str
  category: "STARTED" | "PRE_RUN_REJECTED" | "PRE_RUN_CANCELLED"
  run_outcome: "COMPLETED" | "INCOMPLETE" | null
  output_check: "PASSED" | "NEEDS_REVIEW" | "NOT_RUN" | null
  stop_reason: ... | null
  controlled_change: {factor: str, value: str} | null
  case_id: str | None = None
  population_id: str | None = None
  source_revision: str | None = None
  prompt_hash: str | None = None
  configuration_fingerprint: str | None = None
```

```
EvaluationPopulation(population_id, source_revision, prompt_hash, configuration_fingerprint, case_ids)
  # population_id, source_revision: nonblank strings
  # prompt_hash, configuration_fingerprint: lower-case SHA-256 ([0-9a-f]{64})
  # case_ids: non-empty tuple of unique nonblank strings
```
These validate a **caller declaration**; they are **not** signatures, human approval or acceptance. `source_revision` is a nonblank label, not necessarily a 40-hex commit.

**Validation performed by the helper (raises `ValueError`):** duplicate or blank `attempt_id`; unknown `category`; a present but invalid `case_id` (non-string/blank). **When a `population` is supplied**, every `STARTED` record must have a `case_id` in `population.case_ids`, and must match the population's `population_id`/`source_revision`/`prompt_hash`/`configuration_fingerprint`; a **truthy `controlled_change`** on a bound `STARTED` record is **refused** (comparisons need a separate agreed interface). The helper does **not** require every declared case to be observed, and does **not** fully validate all outcome combinations.

The returned dict has **exactly** these ten fields:
`distinct_case_count, population_result_count, status, started_count, completed_count, completion_fraction, needs_review_count, incomplete_reason_counts, pre_run_rejected, pre_run_cancelled`.

**Exact behavior (from source):**
- **Denominator:** `STARTED` includes **unresolved** starts; only `COMPLETED` is in the numerator. No `STARTED` ⇒ `completion_fraction = None`; STARTED-but-none-completed ⇒ `0`.
- Pre-run categories are counted in their own fields, never in `STARTED`. `needs_review_count` is **completed-only**; `incomplete_reason_counts` is terminal-incomplete-only.
- **Status:** zero `COMPLETED` ⇒ `"INSUFFICIENT_EVIDENCE"`; `"AVAILABLE"` means **accounting data exists**, never a semantic PASS.
- **`distinct_case_count`:** size of the distinct `STARTED` `case_id` set **when STARTED is non-empty and every record has a truthy `case_id`**; otherwise `None`. Known explicit IDs can establish it **even with no population**; IDs are never inferred from `attempt_id`.
- **`population_result_count`** (null/1/0 matrix): **`1`** for non-empty STARTED **bound to a supplied population**; **`null`** for non-empty STARTED with **no** population; **`0`** when nothing `STARTED` (and then `distinct_case_count` is `null`).
- **`controlled_change` / comparisons:** a truthy `controlled_change` is refused **only** in bound (population-supplied) mode. The **unscoped** helper does **not** implement comparison validation; it is neither a validated before/after comparison mode nor `N_EVAL`/full-coverage proof.
- **Worked example:** 20 explicit cases × 2 attempts = **40 attempts**, **20 distinct cases**, **1 aggregate**; an unresolved attempt remains countable. This is **developer arithmetic**, not adoption of a 20-case formal profile.

**Retained-evidence adapter (`tests/member_c_verification/live/score_gov004.py::evaluation_counts`).** Before binding `RunRecord`s, it validates eligibility, the actual manifest and pre-start controls, and cohort identity, then calls `summarize_records(records, population=...)` and prints a machine-readable `Evaluation counts:` line beside completion/`NEEDS_REVIEW`. It preserves the scorer's anti-counterfeit/chronology/provider/config protections. The **pure summary alone does not authenticate evidence**; the adapter's cohort/manifest checks are what bind artifacts. The current **five cases / two trials** are a **project trial** relative to the provisional `N_EVAL=20` (five cases, not ten of twenty); the 20/40/1 example is developer arithmetic, not a formal cohort, and a raw legacy scorer PASS is not registry acceptance.

**Comparison / acceptance remain separate.** Fixed/versioned population, matching comparison controls and a declared single-factor comparison are still **requirement obligations** (`REQ-TA-NFR-EVAL-001` / `SEL-TA-NFR-006`), but the helper has **no** comparison reporter, evidence sidecar, expected-case-coverage requirement or `N_EVAL` acceptance. Whole requirement remains **partial**; ownership of a comparison interface is unresolved (owner question).

## 11. Pending (external owners)
Final D1/schema (A); C's test IDs, rubric/threshold, and independent evidence; E enforcement; instructor layout. A must approve any reliance on the reduced-coverage low-level primitive (§5.3). `REQ-TA-INV-014` (immutable input) and `REQ-TA-GOV-004` (schema validation) are now present in the 36-entry registry (`status: proposed`); their presence does not change this contract — input freezing is covered by INV-04/05/05b and schema validation belongs to the governance/CI boundary, where `REQ-TA-GOV-004` now has an implemented `requirements schema` CI gate (E-reported required; not adoption).

**Public-API compatibility guard (E-owned).** `docs/code-governance/public-api-contract.json` freezes the `runapi` exports, `run_analysis_api` parameter names/kinds/defaults and `RunResult` field names; drift fails CI. The **type-layer** additions are merged in source (`StopReason` now includes `BUDGET`; `Finding.status` includes `CORRECTED`; `Rating` includes `REVIEW` — §12.2/§12.5), the **call-cap admission controller is now merged** (`runapi/budget.py` + `llm_clients/budget_transport.py`), but the **remaining** mechanisms in §13–§15A (R1–R8 emission, `corrected_fields` rendering, cumulative **token** fields/coordinator) are **not** applied here. Any intentional contract migration must be coordinated as a single authorized change — E's public-API-snapshot update, D's implementation, the matching tests, the relevant `schema_version`/`check_rules_version` bumps, and the AI-log update — under explicit authorization. This document does not edit or weaken that snapshot, and merged type support does not by itself change the frozen API/version contract.

**Role-permission/handoff note (external, E-owned; runtime contracts unchanged).** Local coding-agent controls are now **configured** (`.opencode/permissions.jsonc`, launcher `scripts/run_role_agent.py`, `.opencode/rules.md` role prompt, `.agent/rules.md` covenant) and **E-native-verified** (69 cases on OpenCode V1 1.19.5), but **active only under the explicit compatible launcher/profile**; native precedence is last-matching-rule-wins (see `docs/architecture/permission-model.md` §4a). Strict B denies shell/Git/tests/search/delegation/web/MCP and edits to the prompt-pack proposal and `docs/req/README.md`; those two paths are **deferred to an owner/authorized external session** or a recorded configuration exception. This does not alter any interface or runtime contract below; OS ACLs, member identity and tamper-proof CI remain outside the guarantee.

## 12. Implementation status and deviations (verified at `a62b801`; updated for merged changes through `6b57aad`)

This section records what the checkout **actually implements** relative to the design above. Where the design is broader, the deviation is stated; none of these is a claim that a proposed `REQ-TA-*` obligation is met.

### 12.1 Implemented as designed
- **Consent gate (§4.1, §5):** `run_analysis_api` rejects any `RunContext` whose `consent_state != CONFIRMED` (`runapi/execution.py:149`); `freeze_explicit`/`freeze_no_portfolio` return `FROZEN` (`runapi/input_service.py`).
- **Canonical fingerprint (§2.2):** implemented in `runapi/context.py`; `FrozenSnapshot` carries the full-64 digest and `as_of_basis="USER_CONFIRMED"`.
- **Checker authority & Q1–Q4 (§3.3, §6):** `runapi/checks.py` `OutputChecker.evaluate(trusted, provenance_fragment, final_rating, rendered_body)`; checker exception → `CHECK_ERROR` via `error_result`.
- **Conditional result fields (§3.4):** enforced by `RunResult.__post_init__` (`runapi/result.py:78-90`): `COMPLETED` requires a rating and no stop reason; `INCOMPLETE` requires no rating, a stop reason, `NOT_RUN` and no findings.
- **Single publication commit + truthful terminal durability (§7):** `runapi/persist.py` writes report+manifest into `_staging`, appends the terminal event, and publishes with one `os.rename` (`:154`); a terminal-append failure yields `terminal_event.durable=false` without flipping the outcome. Stage-private tentative terminal is in `runapi/events.py` (`stage_tentative_terminal`/`commit_terminal`/`discard_tentative_terminal`).
- **Envelope + header guard (§6.4):** `runapi/reporting.py` `build_envelope` and `verify_envelope_header_matches`.
- **Evaluation population interface (§10):** `RunRecord` and `summarize_records` exist in `runapi/result.py` (`INSUFFICIENT_EVIDENCE` when no completed run).

### 12.2 As-built vocabulary (call cap emitted; token/R1–R8 still unimplemented)
- **`StopReason` + BUDGET emission (call cap — implemented):** six values incl. **`BUDGET`** (`MODEL_FAILURE`, `DATA_FAILURE`, `BUDGET`, `INTERNAL_ERROR`, `PERSISTENCE_ERROR`, `INTERRUPTED`). The call-cap controller (`runapi/budget.py` `RunBudgetController`, transport seam `llm_clients/budget_transport.py`) is **implemented for the bounded profile**; `finalize.classify_exception` maps `RunBudgetExhausted` → `BUDGET`. `PERSISTENCE_ERROR` remains primary over BUDGET. **Cumulative token/time admission (`REQ-TA-NFR-COST-001`, §15A, ADR-004) is still proposed/unimplemented** — call-count cap ≠ token cap.
- **`Finding.status` + `CheckResult`:** `status ∈ {BLOCKING, CORRECTED}`; `PASSED` permits corrected-only findings and rejects any `BLOCKING` finding; `NEEDS_REVIEW` still requires ≥1 **blocking** finding; `NOT_RUN` forbids findings. But the **checker emits only Q1–Q4** — no rule produces `CORRECTED`, and `Finding` carries no `original`/`corrected` fields here. R1–R8, evidence/coverage remain **unimplemented** (R1≈Q1, R8≈Q3/Q4, R2/R4–R7 no enforcing code).
- **Rating:** `Rating` includes `REVIEW` (unreadable-rating path). Types admit `BUDGET`/`CORRECTED`/`REVIEW`; **call-cap emission and the budget manifest schema are present**, while R1–R8 rules and cumulative-token admission are not.

### 12.3 Conditional-semantics corrections (aligned with the 24 November review)
- **Outcome-dependent fields, not blanket non-null:** `stop_reason` is present **only** for `INCOMPLETE`; `final_rating` is present **only** for `COMPLETED` (§3.4). Any proposed requirement wording that requires both fields non-null in every record is **inconsistent** with this contract and with `REQ-TA-RUN-001`'s own validity table; the correct check validates field presence/nullability per the validity table, not a blanket non-null assertion. (This is the `REQ-TA-NFR-REPRO-001` fit-(b) vs `REQ-TA-RUN-001` tension identified in the review; it is a requirements-wording item, not an architecture change.)
- **Critical publication failure cannot promise an artifact:** a critical report/manifest failure returns `INCOMPLETE/PERSISTENCE_ERROR` with `report_path=null`, `manifest_path=null` (§7.3). The contract does **not** promise an on-disk report/manifest on that path; a reproduction requirement should preserve the returned-logical-result vs artifact-publication distinction.
- **Fixture shorthand:** `INCOMPLETE(MODEL)` / `INCOMPLETE(DATA)` in fixture prose are human shorthand; serialized values remain `MODEL_FAILURE` / `DATA_FAILURE` (RUN-001 spelling rule).

### 12.4 Optional-portfolio scope (implemented; registry scope now includes it, adoption/OQ-16 open)
- The implemented contract supports `NO_PORTFOLIO` and an explicitly confirmed `PORTFOLIO_PROVIDED` snapshot, including an explicitly empty (flat) book and a supplied book that lacks the analyzed instrument (`§1`, `§2.1`). This is retained as implemented.
- The current registry's scope now **includes optional portfolio input** (profiles A-A/A-B/A-C), matching the implemented optional-input flow. The confirmation-flow ownership is still open (OQ-16); this document keeps the implemented flow and does not invent a consent requirement.

### 12.5 Call-cap implemented; schema/version and remaining mechanisms
- **Implemented — call-cap admission + BUDGET (bounded profile):** opt-in `RunBudgetController` (`runapi/budget.py`) with the synchronous SDK transport seam (`llm_clients/budget_transport.py`); supported tiers `deepseek`/`openai_compatible`, synchronous in-tree factory, **SDK/transport retries disabled**, async rejected; both tiers/plain/tools/structured/fallback/reflection share one run-local controller; grants monotonic/no refund, tickets single-use/run-bound, `seal()` waits active responses, counters per-run. `finalize` emits `BUDGET` on refusal; `PERSISTENCE_ERROR` primary. `call_cap=None` disables; `0` allows no dispatch; `TRADINGAGENTS_CALL_CAP` exposes the standard config. **Not** a token cap, elapsed-time cancellation guarantee, arbitrary-custom-code protection, or count of gateway-internal retries.
- **Implemented — budget manifest schema (validated):** `validate_budget_manifest`/scorer recognize **disabled legacy** `schema_version` string `'1'` with **no** `run_budget`/`check_rules_version`/`BUDGET`; **enabled budget-only** `schema_version` integer `2`, `check_rules_version` integer `1`, `run_budget` exactly `{call_cap, granted, dispatched, invalidated, denied}` (non-negative ints; `dispatched+invalidated == granted ≤ call_cap`; `effective_config.call_cap` agrees; `BUDGET` requires `denied`). Unknown/invalid versions fail closed. No fabricated R1–R8/cumulative-token migration.
- **Not implemented — R1–R8 / corrected emission / evidence-coverage:** checker emits only Q1–Q4; no `CORRECTED` emission; R1–R8, evidence-ID registry and per-run `data_coverage` absent; `corrected_fields` rendering under a version gate to be built.
- **Not implemented — cumulative token/time admission & resume:** `REQ-TA-NFR-COST-001`/`PERF` (§15A, ADR-004) and D-5 resume remain proposed (resume conflicts with INV-11/INV-12).

---

## 13. Evidence and coverage model — `REQ-TA-FR-001/004/005/006` (PROPOSED, not implemented)

Status: **proposed implementation-ready design** for D to build and C to test. Nothing here is implemented at `a62b801`; the existing run has **input provenance only** (`INV-04/05/05b`) and no per-run evidence or coverage record. This section is the **data contract** that the R2 (evidence-ID) and R7 (coverage-equality) check rules in §14 depend on; per the approved plan, this contract must be agreed **before** those checker integrations. Feasibility of implementing it before 25 Nov is **not promised** (see §16).

### 13.1 Proposed components and module boundaries
| Component | Responsibility | Proposed path (new) | Owner(design/impl/test/enforce) |
|---|---|---|---|
| `EvidenceRegistry` | Assign stable evidence IDs; retain per-item records; expose lookup for citation resolution | `tradingagents/runapi/evidence.py` | B / D / C / E |
| `CoverageTracker` | Accumulate one code per channel; classify core/non-core; compute `NOT_REQUESTED`; render deterministic section | `tradingagents/runapi/coverage.py` | B / D / C / E |
| Router/bypass seams | Emit a record/code for every channel, including the 2 router-bypass channels (3 and 11) | `tradingagents/dataflows/router.py` (+ bypass call sites) | B / D / C / E |

Dependency rule preserved: `runapi/*` must not import `cli`.

### 13.2 Field-level data contracts (authority noted per field)

```
EvidenceRecord {
  evidence_id: str            # stable within a run; assigned by EvidenceRegistry (AUTHORITATIVE, deterministic)
  channel: ChannelCode        # see §13.3 (deterministic)
  source: str                 # vendor/source label as supplied (SOURCE-PROVIDED metadata; not model text)
  ticker: str                 # instrument the item concerns (SOURCE-PROVIDED)
  observed_at: str | null     # ISO-8601 when observed, else null (SOURCE-PROVIDED)
  published_at: str | null    # ISO-8601 publication/filing date, else null (SOURCE-PROVIDED)
  as_of_window: str           # the FR-004 window this item was admitted under (deterministic)
  value_ref: str | null       # opaque pointer to the retained payload; NOT the payload text (deterministic)
}
```

- **Invariant:** at least one of `observed_at` / `published_at` is non-null for every admitted item (R2 resolution depends on it). Enforced by `EvidenceRegistry` on admission.
- **IDs are run-scoped** and never derived from model output. A citation in the rendered report references `evidence_id`; R2 (§14) resolves it against the registry.
- **Retention vs outage:** records are written to the run's own artifact area. "Retain evidence after an ordinary engine failure" is **not** a promise that storage succeeds during a critical persistence outage; on critical report/manifest failure the run is `INCOMPLETE/PERSISTENCE_ERROR` and no published paths are promised (§7.3). Evidence retention is best-effort relative to that critical boundary.

**Public operations (proposed) and behaviour:**
```
class EvidenceRegistry:
    def register(self, item: AdmittedItem) -> str        # returns stable evidence_id
    def resolve(self, evidence_id: str) -> EvidenceRecord   # raises EvidenceResolutionError if unknown
    def export_index(self) -> list[EvidenceRecord]       # safe fields only (no payload)
```
- **Stable ID / dedup:** assign `evidence_id` deterministically per run; dedup key = `(channel, source, ticker, observed_at, published_at, value_hash)`. A duplicate admission returns the existing ID (no second record, no second coverage bump).
- **Timestamp admission:** the registry records the caller-supplied `observed_at`/`published_at`; it never infers time from file mtime. An item lacking both timestamps is **rejected** (not admitted) and the channel is coded accordingly.
- **Lookup/error:** `resolve()` of an unknown ID raises `EvidenceResolutionError`; R2 turns that into a blocking finding.
- **Concurrency:** all mutations (`register`) and reads (`resolve`/`export_index`) are guarded by **one lock per registry**; IDs are unique under concurrent analyst fan-out.
- **Attachment before agents see text:** IDs and source dates are attached at the **data boundary** (router / bypass call site) **before** the analyst prompt is assembled, so the model can cite `[ev:ID]` and the renderer can show `source` + `DATE` beside it.
- **Citation syntax & visible source/date (satisfies FR-001, not just resolution):** citations use `[ev:<evidence_id>]`; the renderer resolves each to `source` + `published_at|observed_at` (`YYYY-MM-DD`) and **renders them beside the citation**. Resolving an ID alone does not satisfy the visible source/date criterion; the rendered text must show both.
- **Payload ownership / `value_ref`:** `value_ref` is an opaque key into a **run-owned** retained-payload store under the run's artifact directory (proposed `.../<run_id>/evidence/payloads/<hash>`). Evidence fields never depend on an unspecified store; if the payload is unavailable, the record still carries source/timestamps and `value_ref=null`. The store path is safe (no secrets); contents are redacted before persistence.

```
CoverageRecord {
  channel: ChannelCode        # one reportable unit from §13.3's proposed catalog (not a vendor call)
  code: "OK" | "UNAVAILABLE" | "NO_DATA" | "STALE" | "WITHHELD" | "NOT_REQUESTED"   # (deterministic)
  detail: str | null          # redacted, source-metadata-derived; never model prose
}
CoverageSet {
  entries: CoverageRecord[]           # one row per proposed channel unit (see §13.3)
  core_channels: ChannelCode[]        # mandatory core set per the requirement; NOT silently reduced
  run_core_ok: bool                   # every MANDATORY core channel == OK (strict; see below)
}
```

- **Coverage is built from tool results, never written by the model.** The rendered "Data coverage" section is produced deterministically from `CoverageSet`; R7 (§14) asserts the rendered section equals the record.
- `NOT_REQUESTED` = no selected analyst required any vendor call for this unit; valid for both COMPLETED and INCOMPLETE.
- **Core rule (published requirement — STRICT, preserved):** if **any mandatory core channel** has a code other than `OK` — including `NOT_REQUESTED` — the run ends `INCOMPLETE/DATA_FAILURE`. Non-core gaps do not stop the run. **Unrequested mandatory core data is NOT treated as “not applicable” or automatically exempt.** Excluding an unrequested mandatory core channel from finalization is permitted **only** if A/team explicitly adopt that exemption; until then this design applies the strict rule. (Surfaced, not adopted — §13.3; requirements decision for A/team.)

### 13.3 Channel units vs vendor calls, proposed catalog and core policy

> **Channels are not vendor calls.** A **coverage channel/unit** is a reportable availability unit; a **vendor call** is one router-method or direct-source invocation that feeds a unit. One unit may require several calls (e.g. fundamentals = balance sheet + cashflow + income statement); a unit is `OK` only if **all required calls** for it succeeded.

**Proposed catalog — REQUIRES A/C AGREEMENT (not adopted).** This is a **proposal**, visibly awaiting A's authoritative channel table and C's test review; it is **not** an adopted enumeration and must not be implemented as-if-approved. Derived from real code; the requirement's "12 channels / channels 3 and 11 bypass" **cannot be reconciled to code without A's table** (`requirements-draft-v4.md`, not in checkout). Verified reality: **11 router methods** (`VENDOR_METHODS`, `tradingagents/dataflows/router.py:97-150`) **plus direct sources** that bypass the router (`fetch_stocktwits_messages`, `fetch_reddit_posts` in `agents/analysts/sentiment_analyst.py`; `get_company_profile` in `agents/context.py`; `build_verified_market_snapshot` in `agents/tools.py`). So "two bypass channels" undercounts non-router sources.

| # (proposed) | Unit / channel | Source tool(s)/method(s) | Caller | Seam | Analyst / request relationship | Core? |
|---|---|---|---|---|---|---|
| 1 | price history (OHLCV) | `get_stock_data` | market analyst | router | market | **core** |
| 2 | technical indicators | `get_indicators` | market analyst | router | market | non-core (follows price) |
| 3 | fundamentals/statements | `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement` | fundamentals analyst | router | fundamentals | non-core |
| 4 | ticker news | `get_news` | news analyst | router | news | non-core |
| 5 | global news | `get_global_news` | news analyst | router | news | non-core |
| 6 | insider transactions | `get_insider_transactions` | news analyst | router | news | non-core |
| 7 | macro indicators | `get_macro_indicators` | (macro if selected) | router (optional category) | optional | non-core |
| 8 | prediction markets | `get_prediction_markets` | (if selected) | router (optional; live-only) | optional | non-core |
| 9 | social: StockTwits | `fetch_stocktwits_messages` | sentiment analyst | **direct/bypass** | sentiment | non-core |
| 10 | social: Reddit | `fetch_reddit_posts` | sentiment analyst | **direct/bypass** | sentiment | non-core |
| 11 | company profile | `get_company_profile` | `agents/context.py` | **direct/bypass** | identity/context | non-core |
| 12 | verified market snapshot | `build_verified_market_snapshot` | `agents/tools.py` | **direct/bypass** | market | non-core |

- Indices above are **proposed labels only**; they are **not** A's numeric channel IDs and must not be treated as the requirement's "channels 3 and 11". The discrepancy (11 router methods + 4 direct sources vs the requirement's 12-with-2-bypass) is surfaced for **A/C** to reconcile; this table is a starting proposal, not an adopted enumeration. **A/C agreement is required before D implements it and before any market-only coverage count is treated as authoritative.**
- **Core set default (proposed, requires A/C agreement):** price history only (per the requirement's price-core rule); technical indicators follow price. The core membership itself is part of the catalog A/C must confirm.
- **Behavior when a mandatory core channel was never requested (e.g. market analyst not selected):** under the **strict published rule** (§13.2), an unrequested mandatory core channel is `NOT_REQUESTED` ≠ `OK`, so the run **ends `INCOMPLETE/DATA_FAILURE`** — the run may not silently finish as if it had usable core evidence. **Excluding unrequested mandatory core channels from finalization is a proposed exemption that requires A/team adoption**; it is recorded here as **open, not applied**. If A/team adopts it, both §13.2 and the runtime policy R18 update together; until then D implements the strict branch.

### 13.4 Freshness (§`REQ-TA-FR-006`) — proposed parameters
- Price freshness: latest bar ≤ `STALE_PRICE_DAYS` (10, fixed) before *D*; exceeded ⇒ core gap ⇒ `INCOMPLETE/DATA_FAILURE`.
- Statement freshness: filed ≤ `STALE_STATEMENT_DAYS` (provisional, **open**) before *D*; exceeded ⇒ coded `STALE`, shown with filing date, run continues.
- News/social: item inside the *D*-clamped window; excluded items are `NO_DATA`/`UNAVAILABLE`, not `STALE`.
- `STALE_STATEMENT_DAYS` is a **configuration decision, not a measured value** (open; A owns).

### 13.5 Normal sequence
`admit(item) → assign evidence_id + record in EvidenceRegistry → set/refine CoverageRecord[channel]` for each retrieved item; at finalize, `coverage = CoverageSet.compute()` and `coverage.render()` produces the report section. Sequence integrates at the data boundary (`router`/bypass), before the checker runs.

### 13.6 Failure / concurrency / privacy / persistence policy
- **Availability after fallback (per call → per unit):** each vendor call resolves to one of `OK`, `UNAVAILABLE` (all vendors in the chain failed/absent), `NO_DATA` (call succeeded but returned a genuinely empty result), `STALE`, `WITHHELD` (live-only data on a historical run). A unit's code is the **worst** outcome across its required calls (`OK` only if all `OK`; else the highest-severity non-OK: `UNAVAILABLE` > `STALE` > `NO_DATA`/`WITHHELD`; `NO_DATA` on a non-core unit does not stop the run).
- **Unfinished/unavailable requests ≠ genuine empty results:** a request that was started but did not complete (exception, timeout, fallback exhausted) ⇒ `UNAVAILABLE`; a call that completed and returned zero items ⇒ `NO_DATA`; a call never made (analyst not selected) ⇒ `NOT_REQUESTED`. These three must not be conflated: `NO_DATA` means “asked and got nothing”, `UNAVAILABLE` means “asked but could not obtain”, `NOT_REQUESTED` means “never asked”.
- **Failure:** a malformed item that cannot be admitted is coded for its unit, not a crash; a **mandatory core unit** ≠ `OK` ⇒ `DATA_FAILURE` (strict rule; any exemption requires A/team adoption, §13.2/§13.3).
- **Concurrency:** analysts fan out; `EvidenceRegistry` and `CoverageTracker` mutations must be thread-safe (single lock per registry/tracker, or per-thread accumulation merged at join). IDs must remain unique under concurrency; per-unit code merge is worst-wins and commutative.
- **Privacy:** records carry source metadata and an opaque `value_ref`, not raw payloads; redaction applies at any sink that emits records; holdings/other-position content never enters an evidence record.
- **Persistence:** evidence/coverage are written into the run's artifact area; a critical publication failure does not promise their durability beyond §7.3; on ordinary engine failure, retained records stay available if storage worked.

### 13.7 Compatibility/migration
Additive fields only. Existing manifests gain `coverage` and (optionally) an evidence-index reference; the **manifest/result `schema_version`** bumps independently of the **`check_rules_version`** (§16.7). Old readers must tolerate the new fields or use the explicit version gate. No rename of existing `SafeRunMetadata` fields.

### 13.8 Proposed verification scenarios (C inputs; not accepted)
| # | Input | Expected | Violating negative |
|---|---|---|---|
| E1 | offline run, all 4 analysts | each requested unit `OK`; every citation resolves **and shows source+date** | dangling cited ID ⇒ R2 blocking; citation without visible source/date fails |
| E2 | market-only run (others not selected) | **proposed count (requires A/C agreement)**: market units `OK`, all unrequested units `NOT_REQUESTED`; **strict rule:** if price (mandatory core) is `OK` the run may complete; any mandatory-core unit left `NOT_REQUESTED` ⇒ `INCOMPLETE/DATA_FAILURE` | relying on an unadopted exemption/finishing with a mandatory core channel `NOT_REQUESTED` fails |
| E3 | mandatory price core `UNAVAILABLE` (requested) | `INCOMPLETE/DATA_FAILURE` | completed run with mandatory-core gap fails |
| E4 | all non-core units gapped | `COMPLETED`, units coded | incomplete on non-core gap fails |
| E5 | statement at `STALE_STATEMENT_DAYS`+1 | `STALE`, shown, run continues | run stops or hides fails |
| E6 | prose replaced, structure same | coverage section byte-identical | model-authored section differs fails |
| E7 | mandatory price at `STALE_PRICE_DAYS`+1 | `INCOMPLETE/DATA_FAILURE` | — |
| E8 | incomplete after price retrieved | evidence retained unchanged | erased evidence fails |
| E9 | vendor chain: primary fails, fallback succeeds | unit `OK` | coding `UNAVAILABLE` when fallback succeeded fails |
| E10 | all vendors fail (mandatory core) | unit `UNAVAILABLE`; core ⇒ `DATA_FAILURE`; non-core ⇒ coded | `NO_DATA` used for a failure fails |
| E11 | call succeeds, zero items | unit `NO_DATA` (non-core ⇒ run continues) | `UNAVAILABLE` used for an empty result fails |
| E12 | unit never requested | `NOT_REQUESTED`, never `UNAVAILABLE`/`NO_DATA` | conflating not-requested with gap fails |
| E13 | **mandatory core channel `NOT_REQUESTED`** (e.g. market analyst not selected) | **strict rule: `INCOMPLETE/DATA_FAILURE`** unless A/team adopt the exemption | completing as if core were usable without an adopted exemption fails |

---

## 14. Output-check v2 and result contract — `REQ-TA-ARCH-002`, `FR-007/008`, `SEC-003`, `INV-001..008` (PROPOSED target, not implemented)

Status: **proposed published target** for D/C. The as-built checker is Q1–Q4 with blocking-only findings (§12.2). This section defines the proposed target: **R1–R8** with a **corrected** finding class such that **corrected-only findings may coexist with `PASSED`** and **blocking findings produce `NEEDS_REVIEW`**. It **preserves the existing Q2 trusted-provenance guard unchanged**; A's evidence-ID **R2 is a separate rule** that depends on §13. Implementation order: §13 data contracts first, then R2/R7 integration (§16).

> **Namespace discipline.** `R1–R8` here = output-check rules (`REQ-TA-ARCH-002`). Distinct from: catalog runtime triggers `R1..R17` (`runtime-policy-catalog.md`), checker codes `Q1–Q4` (as-built), and the semantic rubric `R1–R7` (C). Do not equate by number.

### 14.1 Rule set (target)
| Rule | Check | Owner req | Kind | Depends |
|---|---|---|---|---|
| R1 | Final rating readable (not REVIEW) | RUN-001 | Blocking | — |
| R2 | Every cited evidence ID resolves to exactly one record | FR-001 | Blocking | **§13 EvidenceRegistry** |
| R3 | No banned ownership phrase (ownership-assertion check) | FR-007 | Blocking | — |
| R4 | Sentiment score lies in its band's range (only when sentiment selected & report present) | FR-008 | Blocking | — (applicability: §14.3) |
| R5 | Sentiment confidence within coverage cap (downgrade to `low`, record safely) | FR-008 | **Corrected** | §13 coverage (source availability) |
| R6 | No sentiment direction (non-Neutral band) when no source `OK` (only when sentiment selected & report present) | FR-008 | Blocking | §13 coverage |
| R7 | "Data coverage" section equals the CoverageRecord (incl. `NOT_REQUESTED`) | FR-005 | Blocking | **§13 CoverageSet** |
| R8 | Disclaimer present; no prohibited guarantee phrase | SEC-003 | Blocking | — |

- **Q2 is preserved separately.** The existing **Q2 trusted-provenance guard** (envelope provenance fragment equals explicit trusted `SafeInputMetadata`, §6.4) remains an independent, always-on check on the frozen input identity. It is **not** replaced or absorbed by R2. R2 concerns **cited evidence IDs**, a different subject (report citations vs input provenance). Both can co-exist; a run can fail Q2 (provenance mismatch) while passing R2, or vice-versa.

### 14.2 Finding and result types, and the single-verdict pipeline (target)
```
Finding {
  rule: "Q2" | "R1".."R8" | "CHECK_ERROR"   # Q2 retained; R* per table
  status: "BLOCKING" | "CORRECTED"           # NEW: corrected class added
  detail: str                                # redacted
  original: str | null                       # for CORRECTED: pre-correction value (safe field)
  corrected: str | null                      # for CORRECTED: post-correction value (safe field)
}
CheckResult {
  output_check: "PASSED" | "NEEDS_REVIEW" | "NOT_RUN"
  findings: Finding[]
  corrected_fields: SafeCorrectionFields | null  # ONLY explicitly-safe fields (e.g. sentiment confidence enum), never body text
}
```

**Single final verdict over the exact delivered body (no freeze-before-recheck).** The verdict must describe precisely what is delivered, so evaluation happens **once, on the final body**:

1. Render the body once from `final_state` + `RunContext` (§6.1), producing `body_fields`.
2. **Normalize first:** apply authorized corrections to `body_fields` (e.g. R5 confidence) → corrected `body_fields`.
3. **Re-render** the delivered body deterministically from the corrected `body_fields`.
4. **Redact the final re-rendered body** (`redactor.scrub`) — redaction happens **before** evaluation and before delivery, so the checked bytes equal the delivered bytes.
5. **Evaluate once** on that final redacted body: `Checker.evaluate(CheckInput{trusted, provenance, redacted_body, body_fields, evidence, coverage}) → CheckVerdict`. The single `CheckVerdict` (`output_check`, `findings`, `corrected_fields`) is the authoritative verdict for the delivered document. No second, competing verdict is produced.
6. Persist only the **safe** correction fields (`corrected_fields` restricted to enumerations/flags such as sentiment confidence/band/score — never narrative or free text), plus findings.

**Result mapping (target), scoped to a completed, evaluated run:**
- Any **BLOCKING** finding ⇒ `NEEDS_REVIEW`.
- **Only CORRECTED** findings (no blocking) ⇒ `PASSED` (corrections already reflected in the re-rendered delivered body). *(Approved R5 target; see §16.)*
- No findings ⇒ `PASSED`.
- Checker exception ⇒ `NEEDS_REVIEW` with single `CHECK_ERROR`.
- `INCOMPLETE` ⇒ `NOT_RUN`, findings `[]` (checker **not invoked**).

**Cross-field invariants (target), completed-and-evaluated only:**
- For a completed run whose checker was evaluated: `PASSED ⇔ findings contain no BLOCKING (CORRECTED allowed)`; `NEEDS_REVIEW ⇒ ≥1 BLOCKING` (CHECK_ERROR counts as blocking).
- **`INCOMPLETE ⇒ NOT_RUN` with findings `[]`.** Explicit negative: **incomplete + empty findings must remain `NOT_RUN`, never `PASSED`.** The `PASSED ⇔ no BLOCKING` equivalence therefore **does not** apply to incomplete runs.

### 14.2a Typed v2 checker/evidence contracts (target)

These are the exact types the pipeline (§14.2) and rules (§14.1) consume/produce. All are proposed; D implements, C tests.

```
BodyFields {                       # the structured fields the body was rendered from (trusted inputs to render)
  final_rating: "Buy"|"Overweight"|"Hold"|"Underweight"|"Sell"|"REVIEW"|null
  sentiment: SentimentFields | null        # null iff sentiment analyst not selected OR no report
}
SentimentFields {                  # present only when sentiment selected AND a SentimentReport exists
  overall_band: "Bullish"|"Mildly Bullish"|"Neutral"|"Mixed"|"Mildly Bearish"|"Bearish"
  overall_score: float             # 0.0–10.0 (schema-bounded)
  confidence: "low"|"medium"|"high"
}

EvidenceView {                     # read-only projection of the §13 EvidenceRegistry for R2
  resolve(evidence_id) -> EvidenceRecord | None    # None ⇒ dangling
  ids: set[str]                                     # admitted IDs for this run
}
CoverageView {                     # read-only projection of §13 CoverageSet for R6/R7
  channel_code(channel) -> "OK"|"UNAVAILABLE"|"NO_DATA"|"STALE"|"WITHHELD"|"NOT_REQUESTED"
  sentiment_source_status() -> {"stocktwits":"OK"|...,"reddit":...}   # per-source availability for R5/R6
  rendered_section() -> str        # deterministic coverage section for R7 equality
  mandatory_core_ok() -> bool      # strict: every mandatory core channel == OK (any NOT_REQUESTED ⇒ False)
}

CheckInput {
  trusted: SafeInputMetadata                 # Q2 authoritative expected values (unchanged)
  provenance_fragment: str                   # Q2 subject (independently rendered trusted text)
  redacted_body: str                         # final re-rendered + redacted body (checked == delivered)
  body_fields: BodyFields                    # post-normalization fields the body was rendered from
  evidence: EvidenceView                     # R2
  coverage: CoverageView | null              # R5/R6/R7; null only when coverage not available (then R7 blocks)
  check_rules_version: 2
}

CheckVerdict {                     # the single authoritative verdict for the delivered document
  output_check: "PASSED"|"NEEDS_REVIEW"|"NOT_RUN"
  findings: Finding[]                        # per §14.2
  corrected_fields: SafeCorrectionFields | null
}
```

**`SafeCorrectionFields` — exact safe R5 projection (only these keys are ever persisted/emitted):**
```
SafeCorrectionFields {
  sentiment_confidence: "low" | "medium" | "high" | null   # R5 correction target; the ONLY corrected value in v2
}
```
- **R5 correction is exactly:** `corrected_fields.sentiment_confidence = "low"` when coverage shows a sentiment source not `OK` and the model chose `"medium"|"high"`. Nothing else is corrected in v2; **no narrative text, no scores, no free text, no holdings** enter `SafeCorrectionFields`.
- `Finding{R5, CORRECTED}` carries `original`/`corrected` as **enum strings** (`"high"→"low"`), which are safe; the `detail` is redacted. The `Finding` fields never carry narrative.
- If a future correction to `overall_score`/`overall_band` is proposed, it must be added to `SafeCorrectionFields` only after A/C agreement that the value is safe to persist; the current target corrects **confidence only**.

**Evidence/check type rules:** `EvidenceView`/`CoverageView` are **read-only projections** (the checker never mutates the registries); `CheckInput.check_rules_version` is fixed to `2` for this target (§16.7); a checker that cannot build `CoverageView` emits a **blocking R7** (coverage section unavailable) rather than `PASSED`.
- `RunResult`/manifest authority unchanged: `PASSED` still certifies only R1–R8, not truth or suitability.

### 14.3 Corrected-finding handling (R5) and sentiment-output cases — concrete

**R5 correction (when sentiment is selected and a `SentimentReport` exists).** When coverage shows a sentiment source not `OK` and confidence `> low`: set `corrected_fields.sentiment_confidence="low"` and `Finding{R5, CORRECTED, original=<high>, corrected="low"}`. The re-render (§14.2 step 3) writes `low` into the delivered header; the single verdict is `PASSED` unless another rule blocks. Corrections and blocking findings may coexist; blocking dominates the verdict while the correction is still applied and recorded.

**Sentiment-output cases (explicit, distinct):**
- **Sentiment Analyst not selected** → R4–R6 **not applicable**; no finding. (Market-only fixture must not fail for an absent `SentimentReport`.)
- **Both generation paths fail** (structured call and free-text fallback both yield nothing usable) → the run is **`INCOMPLETE` / `stop_reason=MODEL_FAILURE` / `output_check=NOT_RUN`, no final rating, no findings** (classified by the finalizer as a model failure; the checker is not invoked). This matches `REQ-TA-NFR-001`.
- **Usable free text without structured fields** (the analyst produced usable narrative but no `SentimentReport`) → this is a **separate case**; it is **not** assigned a new adopted finding rule here. It is surfaced as an **open policy question for A/C** (whether to treat as `REVIEW`/`NEEDS_REVIEW` or to attempt extraction). The design records the case explicitly rather than inventing a rule.
- **All three sources unavailable** (selected, report present) → R6 requires `Neutral` band (blocking if not); R5 caps confidence at `low` (corrected). Availability comes from the **coverage record** (`SentimentReport` has no source-status field).

This is a **contract extension** shipped together: `Finding.status` gains `CORRECTED`, `CheckResult` gains `corrected_fields` (safe only), `CheckResult(PASSED)` no longer requires empty findings, and report/scorer render/interpret the new fields under the `check_rules_version` gate (§14.5, §16.7).

### 14.4 R3 ownership phrase check — target is a **blocking phrase check**
R3 is retained as a **deterministic blocking phrase/pattern check** over the delivered body for the banned-ownership list (`your position`, `current position`, `maintain the position`, `add to your position`, `exit your position`, `your holdings`, `you own`; list owned by A). A match ⇒ BLOCKING finding. This is the **published target**.
- **Alternative (requires A/C/team agreement, NOT the target):** contextual handling — assess ownership assertions only when not grounded in supplied facts and permit quoted/conditional uses. This cannot be implemented reliably as a deterministic classifier; it would become a semantic-rubric matter. It is recorded as an **alternative requiring agreement**, **not** an advisory replacement for R3.
- Interaction with R5-style correction: R3 corrections are **not** auto-applied; ownership wording is a content change the model must make, so R3 is blocking-only.

### 14.5 Report / manifest / scorer compatibility
- **Report:** envelope gains nothing secret; the re-rendered body shows corrected values; the findings list distinguishes blocking vs corrected with `original`/`corrected` where applicable.
- **Manifest:** add `check_rules_version` **separately from** the manifest/result `schema_version` (§16.7). Keep `findings` shape additive.
- **Scorer readers:** must accept `CORRECTED` and `corrected_fields`; a reader that only knows `BLOCKING` **fails closed** on an unknown `status`/version (never silently treats `CORRECTED` as non-blocking).
- **Schema/version policy:** see §16.7 (separate manifest/result schema version and check-rule version; explicit legacy path for schema-1 artifacts lacking `check_rules_version`; reject unknown/invalid new-format combinations).
- **Safe-only persistence:** manifest/report carry only `corrected_fields` (enumerations/flags), never narrative/free text; redaction precedes evaluation and delivery.

### 14.6 Incomplete / raise / block / correct decision table (target)
| Situation | run_outcome | output_check | findings |
|---|---|---|---|
| All rules pass | COMPLETED | PASSED | [] |
| Only R5 corrected | COMPLETED | PASSED | [R5 CORRECTED] |
| Any blocking rule fails | COMPLETED | NEEDS_REVIEW | ≥1 BLOCKING |
| Checker raises | COMPLETED | NEEDS_REVIEW | [CHECK_ERROR] |
| **Both sentiment paths fail** | **INCOMPLETE (`MODEL_FAILURE`)** | **NOT_RUN** | **[]** (no rating) |
| Engine incomplete (other) | INCOMPLETE | NOT_RUN | [] |

### 14.7 Proposed verification scenarios (C inputs; not accepted)
| # | Input | Expected | Violating negative |
|---|---|---|---|
| K1 | clean completed report | PASSED, [] | — |
| K2 | one blocking rule each (R1,R2,R3,R4,R6,R7,R8) | NEEDS_REVIEW + matching finding | wrong rule id fails |
| K3 | R5 corrected only | **PASSED** + R5 CORRECTED(original,corrected); delivered header shows `low`; `corrected_fields.sentiment_confidence=="low"` | treating corrected as blocking fails; losing original/corrected fails; delivered body not matching re-render fails |
| K4 | model text says "OUTPUT CHECK: PASSED" while R3 fails | NEEDS_REVIEW (model claim ignored) | PASSED fails |
| K5 | checker raises | NEEDS_REVIEW + CHECK_ERROR | PASSED fails |
| K6 | incomplete run | NOT_RUN, [] | checker invoked fails |
| K7 | Q2 provenance mismatch but R2 ids resolve | NEEDS_REVIEW via Q2 (R2 independent) | conflating Q2/R2 fails |
| K8 | dangling cited ID, provenance correct | NEEDS_REVIEW via R2 | PASSED fails |
| K9 | R3 banned phrase present | BLOCKING (target phrase check) | downgrading to corrected fails |
| K10 | incomplete + empty findings | **NOT_RUN** (never PASSED) | PASSED fails |
| K11 | market-only run (sentiment not selected) | PASSED; **no** R4–R6 finding | failing for absent SentimentReport fails |
| K12 | all 3 sentiment sources unavailable, band Bullish, confidence high | R6 BLOCKING + R5 CORRECTED (confidence→low) | passing without R6 fails; missing correction fails |
| K13 | blocking R3 + R5 corrected | NEEDS_REVIEW; correction still applied + recorded | dropping the correction fails |
| K14 | **both sentiment paths fail** | **INCOMPLETE/MODEL_FAILURE/NOT_RUN, no rating** | COMPLETED or a rating fails |
| K15 | usable free text, no structured fields | recorded as an **open policy case** (no invented finding rule); not silently PASSED or silently INCOMPLETE without a decision | inventing an adopted rule fails |
| K16 | redaction-sensitive text in corrected body | delivered body redacted **before** evaluation; checked bytes == delivered bytes | unredacted delivery or check-before-redact fails |

---

## 15. Run-wide request-budget boundary — `REQ-TA-NFR-COST-002` + `BUDGET` (IMPLEMENTED, bounded profile)

Status: **implemented** at `6b57aad` for the bounded profile (`tradingagents/runapi/budget.py` + the SDK transport seam `tradingagents/llm_clients/budget_transport.py`; `finalize` emits `BUDGET`). The sections below began as the design and now describe the as-built mechanism; the **cumulative token/time** cap (§15A, ADR-004) remains **proposed**. Original design replies: `docs/architecture/proposals/reply-to-A-cost002-2026-11-22.md`.

### 15.1 Component and boundary
| Component | Responsibility | Proposed path (new) | Owner |
|---|---|---|---|
| `RunBudgetController` | One per run; issues single-use, run-bound reservations; enforces `dispatch_attempts <= successful_reservations <= CALL_CAP`; monotonic grants (no refund); `seal()` waits for active responses; exposes safe audit counters | `tradingagents/runapi/budget.py` | B / D / C / E |
| `BudgetTransport` | **The actual SDK enforcement seam**: a synchronous transport wrapper over the **SDK-native HTTP transport family — `httpx` or `httpx2`, selected dynamically by `budget_transport.py` from `DefaultHttpxClient`'s MRO** — that meters each real SDK HTTP attempt (SDK/transport retries `0`); **async is rejected before network access** | `tradingagents/llm_clients/budget_transport.py` | B / D / C / E |

- The controller is **run-local** (set via `ACTIVE_BUDGET`), shared across quick/deep tiers and structured/plain/fallback/reflection paths **because they all issue their network attempt through the same synchronous SDK transport**; it must **not** be a global counter across runs and is **separate from the frozen input snapshot** (`RunContext`). Supported factory tiers: `deepseek`/`openai_compatible`, synchronous in-tree factory; **async and unsupported clients are rejected**; it does **not** bound arbitrary custom code, gateway-internal retries, or elapsed wall-clock time.
- **Token-cap integration (see §15A):** when cumulative token admission is enabled, the call-cap controller is consulted through the atomic `AdmissionCoordinator` (§15A.1) together with the token controller; the coordinator withholds a grant from **both** if either limit refuses. §15's call-counting rules (monotonic `granted`, no refund on invalidation) are **unchanged**; only the entry point is wrapped.
- `CALL_CAP` is a **configuration value** (test value 8; production default open, **not a measured value**).

### 15.2 Interface (proposed signatures)
```
class RunBudgetExhausted(Exception): ...       # distinguishable; must survive broad handlers
class BudgetProtocolError(Exception): ...      # reuse / wrong-run / invalid transition

Reservation {                                   # single-use; owned by one run/controller
  id: str
  controller_run_id: str
  state: "GRANTED" | "CONSUMED" | "INVALIDATED"
}
BudgetAudit {
  call_cap: int
  granted: int          # cumulative successful admissions (MONOTONIC; never refunded)
  dispatched: int       # CONSUMED count (attempts actually issued)
  invalidated: int      # granted-but-unused; capacity NOT refunded
  denied: int
}

class RunBudgetController:
    def __init__(self, call_cap: int, run_id: str): ...
    def reserve(self) -> Reservation:      # atomic; increments granted; raises RunBudgetExhausted if granted >= call_cap
    def dispatch(self, res: Reservation):  # GRANTED -> CONSUMED; must be called BEFORE the request issue
    def invalidate(self, res: Reservation):# GRANTED -> INVALIDATED; keeps cumulative count; NEVER frees capacity
    def audit(self) -> BudgetAudit: ...    # safe counts for manifest/event metadata
```
`Reservation` authorizes **exactly one** dispatch attempt and cannot be reused. A denied `reserve()` dispatches nothing. `dispatch()`/`invalidate()` raise `BudgetProtocolError` if `res.state != "GRANTED"` (reuse) or `res.controller_run_id != run_id` (wrong run / cross-run reuse). Between grant and request issue: if the dispatch never issues (exception before send), `invalidate()` is called and audited; `granted` stays consumed.

### 15.3 State machine and cumulative bound
- States per reservation: `GRANTED → CONSUMED` (dispatched) or `GRANTED → INVALIDATED` (granted but unused). **There is no return to available capacity.** The `granted` counter is **monotonic**, so `dispatched <= granted <= CALL_CAP` holds even if an unused grant is invalidated: invalidating never lets a second grant happen at a cap of 1.
- **Alternative (NOT the target):** a recycling policy that returns an unused slot to capacity would require a **different counting contract** and is an **explicit requirements decision**; it is recorded as an unapproved alternative (ADR 002 D3), not implemented.
- **Concurrency:** `reserve()` is atomic under a single lock/condition per controller; with 1 slot remaining and N concurrent callers, exactly 1 grants and N-1 raise. No branch overshoot allowance is needed (each concurrent branch holds its own reservation). Default START branches = 4 analysts + Memory Log (derived from constructed plan, not a hard-coded constant; branch count irrelevant to the strict bound).
- **SDK retries:** `max_retries=0` for the guaranteed-budget mode; every application retry takes a **fresh** reservation. If a client cannot disable hidden retries, that client is **rejected** in guaranteed-budget mode (not silently uncovered). Gateway-internal retries are outside the client-side guarantee (stated, not hidden).

### 15.4a Metering exactly once — SDK transport seam (as-built)
The cap is enforced at the **synchronous SDK-native HTTP transport** (`llm_clients/budget_transport.py` `BudgetTransport`), which wraps whichever family the installed SDK's `DefaultHttpxClient` uses — **`httpx` or `httpx2`, selected dynamically** — **not** by wrapping model objects or `invoke`. Every real request attempt — plain `invoke`, `bind_tools(...).invoke`, `with_structured_output(...).invoke`, free-text fallback and in-run reflection — issues its HTTP attempt through that transport, so each attempt is metered once; SDK/transport retries are `0`, and **async is rejected before any network access**. A stream wrapper (`BudgetStream`) holds the controller until the response closes so `seal()` waits for active responses. This is a client-side **call-count** cap only: it is **not** a token cap, an elapsed-time cancellation guarantee, protection against arbitrary custom code, or a count of gateway-internal retries. The earlier model-object invoke-wrapper sketch is **superseded** by this transport seam. Proposed C probes: P1 plain=1; P2 tool-bound=1; P3 structured=1; P4 no double-count; P5 each reservation pairs with ≤1 dispatch; P6 wrong-run/reuse rejected — **no runtime guarantee is claimed before these pass.**

### 15.4 Exhaustion propagation (must survive broad handlers)
- `RunBudgetExhausted` must **not** be swallowed by `agents/structured.py` free-text fallback, `memory/settlement.py` (`except Exception`), or the graph memory step. D must either re-raise it or consult an authoritative exhausted-state check, so a refused **required** attempt reaches finalization as `BUDGET`.
- **Trigger:** exhaustion stops a run only when a **required further** attempt is refused. Reaching the cap after the last needed request does **not** force failure; a workflow within cap completes normally.
- **In-flight:** already-issued requests are accounted for (consumed); their termination is awaited before publishing immutable final counts. No new wall-clock termination guarantee is introduced by COST-002.

### 15.5 Result / config / report / manifest / scorer compatibility (needed with BUDGET)
- **`StopReason`:** add `"BUDGET"` ⇒ six values. Every reader that enumerates `StopReason` (`result.py`, classifiers, report/manifest validators, scorer) must be updated together; an old reader must **fail closed** on the new value, not silently coerce.
- **Classifier precedence:** budget refusal is recognized **before** generic `INTERNAL_ERROR`/model classification. **Persistence failure stays primary** if critical report/manifest publication also fails; the budget cause is a secondary recorded diagnostic.
- **Result fields:** on `INCOMPLETE/BUDGET`: `final_rating=null`, `output_check=NOT_RUN`, `findings=[]`; safe audit names configured cap and counts.
- **Config:** `CALL_CAP` recorded in `EffectiveConfig` (safe) and manifest; open default is a configuration decision, not a measured number.
- **Report/manifest:** add `run_budget` summary (cap, granted, dispatched, invalidated, denied) — no prompts/secrets. **`schema_version` and `check_rules_version` are separate axes** (§16.7); budget-only ships as `schema_version=2, check_rules_version=1` (legacy Q1–Q4 preserved), not a vague "v2".
- **Observability (NFR-OBS-001 dependency):** the BUDGET run's log names the **limit hit** (calls here; tokens/time if separately adopted).

### 15.6 Runtime policy row
Adds catalog **R17** (see `runtime-policy-catalog.md`): trigger = required request refused by adopted budget → `INCOMPLETE/BUDGET`, partial content preserved through normal publication, no final rating, `NOT_RUN`; safe diagnostic (budget kind, limit, counters, run/attempt id).

### 15.7 Proposed verification scenarios (C inputs; not accepted)
| # | Input | Expected | Violating negative |
|---|---|---|---|
| B1 | within-cap workflow | COMPLETED, normal | INCOMPLETE fails |
| B2 | CALL_CAP=8, 7 granted, 4 workers (injected barrier) | exactly 1 grant, 3 denials | 2 grants fails |
| B3 | required attempt after cap exhausted | INCOMPLETE/BUDGET, NOT_RUN, rating null | INTERNAL_ERROR or COMPLETED fails |
| B4 | exhaustion inside structured fallback/memory | BUDGET not swallowed | fallback hides it fails |
| B5 | concurrent runs | isolated budgets per run | shared counter leaks fails |
| B6 | budget stop + critical persistence failure | PERSISTENCE_ERROR primary, budget secondary | two/zero reasons fails |
| B7 | any controlled attempt without reservation | none possible (audit pairs 1:1) | unpaired attempt fails |
| B8 | CAP=1: grant A, invalidate A (unsent), reserve B | token allowance fully released, but call grant stays charged → **B denied** (granted ≤ CAP; no call refund) | a coordinator that refunds the call grant and grants B fails |
| B9 | dispatch a reservation twice | second raises `BudgetProtocolError` | 2 consumptions from 1 reservation fails |
| B10 | pass run-1 reservation to run-2 controller | `BudgetProtocolError` | cross-run reuse accepted fails |
| B11 | grant then exception before dispatch → invalidate | `granted` unchanged; later reserve at cap denied | capacity freed fails |
| P1 | plain `llm.invoke` | exactly 1 reservation consumed | 0 or 2 fails |
| P2 | `llm.bind_tools(...).invoke` | exactly 1 reservation consumed | 0 (missed) or 2 (double) fails |
| P3 | `llm.with_structured_output(...).invoke` | exactly 1 reservation consumed | 0 or 2 fails |
| P4 | bound/structured path re-wrap check | not 2 reservations per call | double-wrap/double-charge fails |

---

## 15A. Atomic call + token admission — `REQ-TA-NFR-COST-001` (PROPOSED; Alt-B settlement)

Status: **proposed design (detailed contracts below; provider-bound evidence and parameter values remain open)** for cumulative **token** admission, sitting **beside** the existing call-cap (§15), not replacing it. **Not implemented.** Alt-B chosen (known-usage settlement with UNKNOWN retention); see [ADR-004](adr/004-cumulative-token-admission.md). Mutable state is per-run and **outside** the frozen `RunContext`.

### 15A.1 One atomic coordinator for both limits
One per-run `AdmissionCoordinator` consults the call controller (§15) and the token controller **under one critical section**, withholding a grant from **both** if **either** limit refuses (no partial grant). It lives at the §15 controlled application client boundary (`tradingagents/llm_clients` dispatch seam; proposed `tradingagents/runapi/token_admission.py`). Integration with §15 is **targeted**: §15's counting rules are preserved; only the entry point is wrapped (§15.1 gains a cross-reference; see §15A.6).

```
Ticket { id; coordinator_run_id; call_grant; token_reservation; state: GRANTED|DISPATCHED|SETTLED_KNOWN|SETTLED_UNKNOWN|INVALIDATED }

AdmissionCoordinator.admit(input_bound, output_allowance) -> Ticket
  # atomic: (call grant ok) AND (K+R+U + input_bound + output_allowance <= TOKEN_BUDGET)
  # if either refuses -> grant NEITHER; raise the refusing limit's typed error
coordinate.dispatch(ticket)                     # GRANTED -> DISPATCHED, immediately BEFORE the provider request issues
coordinate.settle_known(ticket, in_use, out_use)# DISPATCHED -> SETTLED_KNOWN
coordinate.settle_unknown(ticket)               # DISPATCHED -> SETTLED_UNKNOWN
coordinate.invalidate(ticket)                   # GRANTED -> INVALIDATED (unsent only; requires non-dispatch established)
```

**Reservation / request-binding type (proposed):**
```
TokenReservation {
  ticket_id: str
  allowance: int                 # input_bound + output_allowance; fixed at admit
  request_binding: RequestBinding
}
RequestBinding {                 # binds the reservation to the FINAL prepared request
  payload_fingerprint: str       # SHA-256 over the post-`_get_request_payload` serialized payload
  provider: str; model: str
  max_output_tokens: int         # the enforced finite allowance actually sent
  input_bound_method: str        # e.g. "exact:<tokenizer-id>" | "family:<id>x<multiplier>"
}
```
**Typed errors (proposed; no serialized stop reason):** `TokenBudgetExhausted` (required request cannot fit → `BUDGET`) and `TokenBoundViolation(reservation, actual_in, actual_out)` (actual > allowance → `INTERNAL_ERROR`); `TokenProtocolError` (reuse/duplicate/wrong-run/non-dispatched settle). `UnsupportedProfileError` (see §15A.2).

### 15A.2 Defensible bounds vs estimates (required, not parameter choices)
Reservation requires a **defensible upper bound**, not an estimate. Per enabled profile, the **provider/profile capability contract** must assert:
- **Input upper bound** — an exact model tokenizer, **or** a tokenizer-family + safety multiplier that is **justified for the complete supported request domain**. Empirical samples alone do **not** prove an upper bound.
- **Tool/schema overhead** — tool schemas, `bind_tools`, `with_structured_output` schema serialization and system-message overhead included in the input bound.
- **Finite enforced output allowance** — a per-attempt maximum the client/provider **enforces** (e.g. forwarded `max_tokens`). `max_tokens=None` and advisory 450/220-word targets are **not** finite bounds.
- **Request binding** — the reservation is bound to the **final prepared request + effective configuration**; the payload/config must not change after measurement (immutably referenced; a post-measurement mutation invalidates the ticket).

A profile lacking any of these is **UNSUPPORTED**: token admission refuses to run for it and surfaces the decision; it is not silently estimated. **Unsupported-profile validation timing:** capability is validated **once, at run/controller initialization (before any dispatch)** — the run is rejected fast with `UnsupportedProfileError` mapped to `INCOMPLETE/INTERNAL_ERROR` (safe diagnostic naming the missing capability) rather than admitting attempts and failing late; a profile cannot become "supported" mid-run. Character/4 is **not** an admissible input bound. Numeric values (`TOKEN_BUDGET`, multiplier, output allowance) remain parameters; the **method + UNSUPPORTED behaviour do not**. Offline accounting tests verify the *accounting logic against a scripted provider*, **not** the deployed provider's true bounds (that is separate E evidence).

### 15A.3 One precise token ledger (mutually exclusive buckets)
- **K** — known actual usage of **settled-known** attempts.
- **R** — outstanding reservations for **granted/dispatched (in-flight)** attempts.
- **U** — retained allowances for **UNKNOWN** attempts (held capacity; never reported as measured actual).

**Two distinct statements (do not conflate):**
- **Admission predicate** (a *gate checked per request*): `admit` succeeds iff `K + R + U + (input_bound + output_allowance) <= TOKEN_BUDGET`.
- **Ledger invariant** (a *postcondition on recorded state*): at all times the recorded buckets satisfy `K + R + U <= TOKEN_BUDGET`, **conditional on the asserted request bounds holding**. A detected bound/protocol violation breaks the conditional (actual may push `K` beyond allowance); that breach is **recorded and made visible** (§15A.4), not hidden or clamped.

**Held capacity** `H = K + R + U` is **not monotonic** (known settlement may reduce it). Keep **monotonic cumulative counters** separately: `cumulative_admitted`, `cumulative_consumed_known`.

### 15A.4 Transitions (no double charge; violations recorded, never clamped)
| Op | Precondition | Effect | Call counters (§15) |
|---|---|---|---|
| `admit` | call grant ok AND token fits | token reservation → **R** (full allowance); `cumulative_admitted += allowance` | `granted += 1` |
| `dispatch` | ticket GRANTED | ticket → DISPATCHED (request issues next) | `dispatched += 1` |
| `settle_known` | ticket DISPATCHED; **valid** input+output usage | remove allowance from **R**, add actual to **K**; `cumulative_consumed_known += actual`. H may decrease if actual < allowance | — |
| `settle_known` with **actual > allowance** | ticket DISPATCHED | **Bound/protocol violation — applied atomically:** in one critical section move allowance R − allowance, add actual to K in full (**not clamped**), mark violations/admissions-halted, record audit anomaly, **then** release the lock and propagate typed `TokenBoundViolation`. No partial state is observable between the ledger update and propagation. | — |
| `settle_unknown` | ticket DISPATCHED; usage missing/partial | move allowance **R → U** (retained; **not** in K, not reported as actual) | — |
| `invalidate` | ticket GRANTED; non-dispatch established | **release the complete token allowance** from **R** (returned to capacity); record invalidation | `invalidated += 1`; **`granted` stays `+1` permanently — the call grant is NOT refunded** |

- **Settlement requires a DISPATCHED ticket.** Reuse, duplicate callbacks (settle twice), a non-dispatched settle, or **wrong-run** tickets raise `TokenProtocolError`, rejected **atomically**, with no bucket move.
- **Dispatch/invalidation race:** exactly one of `DISPATCHED` or `INVALIDATED` per ticket; a second transition raises. If dispatch was issued, `invalidate` is refused (must settle).
- **UNKNOWN resolution:** in this version **U stays until finalization; no late U→K**. (A future resolved-late path is out of scope here.)
- **Token vs call invalidation are intentionally different:** token capacity **is** released on proven non-dispatch (no tokens spent); the **call** grant is **never** refunded (§15 monotonic admission). The coordinator does **not** refund call grants.
- **Violation ≠ exhaustion:** `actual > allowance` is a bound/protocol violation that **may occur while total usage < TOKEN_BUDGET**; it is not budget exhaustion. It halts new admissions and is mapped per §15A.5.

### 15A.5 Result mapping (no new serialized stop reason)
- **Bound/protocol violation** → `INCOMPLETE` / `stop_reason=INTERNAL_ERROR` with a safe diagnostic naming the overage (budget kind, allowance, actual, ticket id; no prompts/secrets). Not `BUDGET` — total may be under budget. The ledger state change and admissions-halt are committed **atomically before** the typed exception propagates (§15A.4), so a broad handler catching the exception cannot observe a half-updated ledger.
- **Unsupported profile** → `INCOMPLETE` / `stop_reason=INTERNAL_ERROR`, safe diagnostic naming the missing capability (validated pre-dispatch, §15A.2).
- **Ordinary refusal** of a *required* request that cannot fit → `INCOMPLETE` / `stop_reason=BUDGET`, `final_rating=null`, `output_check=NOT_RUN`, `findings=[]`.
- **`PERSISTENCE_ERROR` precedence** over all of the above (critical report/manifest failure). **In-flight** attempts are accounted (R→K/U or recorded overage) before **immutable** finalization; a refused-required drop preserves partial content through normal publication. Single terminal, truthful durability; **no** new enum value.

**Authoritative serialized `TokenAudit` shape (proposed; no prompts/secrets).** One canonical object, redacted before persistence; it appears nested under `run_budget.token_audit` in the manifest/result and is mirrored in the `run.terminal` event.

```
TokenAudit {
  enabled: bool                     # token admission active for this run
  status: "DISABLED" | "UNSUPPORTED" | "ACTIVE" | "VIOLATED"
  kind: "NONE" | "CALL_BUDGET" | "TOKEN_BUDGET" | "BOUND_VIOLATION" | "UNSUPPORTED_PROFILE"
  budget: int | null               # TOKEN_BUDGET (tokens); null when disabled/unsupported
  units: "tokens"                  # always tokens (input+output)
  K: int | null                    # known actual (tokens); null when disabled/unsupported
  R: int | null                    # reserved/in-flight (tokens); null when disabled/unsupported
  U: int | null                    # UNKNOWN retained capacity (tokens; NEVER measured actual); null when disabled/unsupported
  remaining: int | null            # budget - (K+R+U); null when disabled/unsupported; MAY be negative on overage (recorded, not clamped)
  cumulative_admitted: int | null  # monotonic tokens
  cumulative_consumed_known: int | null  # monotonic tokens
  bound_violation: bool            # true iff any reservation was exceeded
  violation: null | { allowance: int, actual_in: int, actual_out: int, ticket_id: str }  # present iff bound_violation
}
```
**Conditional rules (authoritative — readers enforce these):**
- `enabled=false` ⇒ `status="DISABLED"`, `kind="NONE"`, **all numeric fields `null`**, `bound_violation=false`, `violation=null`.
- **`enabled=true` + `status="UNSUPPORTED"` is explicitly valid** ⇒ `kind="UNSUPPORTED_PROFILE"`, `budget=null`, `K/R/U/remaining/cumulative_*=null`, `bound_violation=false`, `violation=null`; the accompanying run outcome **must** be `INCOMPLETE` with `stop_reason=INTERNAL_ERROR` (see "Invalid configuration vs run artifact"). A reader **accepts** this combination with null budget/counters and does not treat nulls as malformed.
- `status="ACTIVE"` ⇒ **`budget` must be a present non-negative integer**, `K/R/U` present, **non-negative** integers; `remaining` present (may be `≥0` here, never negative in a non-violated state); `bound_violation=false`, `violation=null`.
- `status="VIOLATED"` ⇒ **`budget` present non-negative integer**, `K/R/U` present non-negative integers, `bound_violation=true`, `violation` present; **`remaining` may be negative** (legitimately, after a recorded overage) — negative `remaining` is valid here and is *not* an invalid count.
- **Non-negative token counts vs `remaining`:** `budget`, `K`, `R`, `U`, `cumulative_admitted`, `cumulative_consumed_known`, and the `violation` counts are **≥ 0**; only `remaining` may be negative, and **only** under `status="VIOLATED"`.
- `kind` is `TOKEN_BUDGET` for a required-refusal stop and `BOUND_VIOLATION` for overage (§15A.4/§15A.5); `CALL_BUDGET` appears only when the **call** cap (§15) refused; `UNSUPPORTED_PROFILE` only with `status="UNSUPPORTED"`. **UNKNOWN (`U`) is retained capacity, never reported as measured actual.**

**Synthetic examples (illustrative):**
```
# disabled admission
{"enabled":false,"status":"DISABLED","kind":"NONE","budget":null,"units":"tokens","K":null,"R":null,"U":null,"remaining":null,"cumulative_admitted":null,"cumulative_consumed_known":null,"bound_violation":false,"violation":null}
# unsupported/unset configuration
{"enabled":true,"status":"UNSUPPORTED","kind":"UNSUPPORTED_PROFILE","budget":null,"units":"tokens","K":null,"R":null,"U":null,"remaining":null,"cumulative_admitted":null,"cumulative_consumed_known":null,"bound_violation":false,"violation":null}
# UNKNOWN usage retained (budget 100; one 60 allowance settled UNKNOWN)
{"enabled":true,"status":"ACTIVE","kind":"NONE","budget":100,"units":"tokens","K":0,"R":0,"U":60,"remaining":40,"cumulative_admitted":60,"cumulative_consumed_known":0,"bound_violation":false,"violation":null}
# bound overage (allowance 60, actual 75)
{"enabled":true,"status":"VIOLATED","kind":"BOUND_VIOLATION","budget":100,"units":"tokens","K":75,"R":0,"U":0,"remaining":25,"cumulative_admitted":60,"cumulative_consumed_known":75,"bound_violation":true,"violation":{"allowance":60,"actual_in":55,"actual_out":20,"ticket_id":"t-7"}}
# over-budget violation, chronological (budget 100)
# 1) earlier reservation 60 settles known at 60 -> K=60, cumulative_admitted=60, cumulative_consumed_known=60
# 2) next reservation 40: 60+40=100 <= 100 -> ADMITTED (R=40, cumulative_admitted=100)
# 3) dispatched request returns actual_in=55, actual_out=15 -> actual 70 > allowance 40 (violation)
# settle: K=60+70=130; R=0; U=0; remaining=100-(130+0+0)=-30; cumulative_admitted stays 100; cumulative_consumed_known=60+70=130
{"enabled":true,"status":"VIOLATED","kind":"BOUND_VIOLATION","budget":100,"units":"tokens","K":130,"R":0,"U":0,"remaining":-30,"cumulative_admitted":100,"cumulative_consumed_known":130,"bound_violation":true,"violation":{"allowance":40,"actual_in":55,"actual_out":15,"ticket_id":"t-8"}}
```

**Invalid configuration vs run artifact:** a missing/unset `TOKEN_BUDGET` or an UNSUPPORTED profile when token admission is **enabled** produces a **valid `INCOMPLETE` artifact** (status `UNSUPPORTED`, `stop_reason=INTERNAL_ERROR`, `output_check=NOT_RUN`) — not "no run" — so the refusal is auditable with truthful durability. Token admission **disabled** simply yields `status="DISABLED"` on a normal completed/other run. (A wholly malformed CLI invocation that never starts is a separate pre-run category, not this artifact.)

### 15A.6 Usage seam — request-scoped settlement with pre-dispatch capability exclusion

Reading the outer structured runnable's return value is **insufficient**: `with_structured_output(...)` returns a runnable that **parses** the model reply into a schema object (or raises), discarding the raw `AIMessage`/provider response. But **no single hook covers every path**. In the installed library (`langchain-openai` 1.8.1, `chat_models/base.py`), `_generate`/`_agenerate` branch into **three** result paths and, on error, raise with **no** result hook:

- **Chat-completions** (`else` branch) → `_create_chat_result(response, …)`.
- **`response_format` parse branch** → `with_raw_response.parse` then `_create_chat_result`.
- **Responses API** (`_use_responses_api(payload)` true) → `_construct_lc_result_from_responses_api(...)` and `return result` **without** calling `_create_chat_result`.
- **Exceptions** (`openai.BadRequestError`/`APIError`/other) → raised after wrapping; the sync/async wrappers do not invoke a result hook.
- **Streaming** (`_stream`/`_astream`) → yields chunks via `_convert_chunk_to_generation_chunk`; usage only if `stream_options.include_usage` is set; `_create_chat_result` is **not** called.

Therefore the design does **not** claim one `_create_chat_result` override covers every path.

**Pre-dispatch capability validation (exclusion, not silent miss).** At controller/run initialization, the profile is validated (already required for bounds, §15A.2). Extend that validation to assert the request **routing is token-accountable**. If the enabled profile/route would use the **Responses API**, or **streaming** without a supported usage-capture hook, or any path where the app cannot observe raw provider usage, the profile is **UNSUPPORTED** (token admission refuses to run; `UnsupportedProfileError` → `INCOMPLETE/INTERNAL_ERROR`, §15A.2/§15A.5). Concretely for the supported (chat-completions, non-streaming) route the interception point is:
- **Interception:** override `_create_chat_result(self, response, …)` on the metered chat class (pattern already used by `DeepSeekChatOpenAI`, `openai_client.py:118`). The **raw provider `response`** is available here (`response.usage`) **before** `_create_usage_metadata` normalizes it, and the produced `ChatResult` carries `usage_metadata`.
- **If a future profile needs Responses API or streaming,** it requires its **own** specified capture seam (e.g. wrapping `_construct_lc_result_from_responses_api` / the streaming aggregation) **and** its own tests; until specified, those routes are **excluded** by capability validation, not promised by one override.

**Request-scoped ticket association under concurrency.** A bare `_create_chat_result` override is called from whichever thread issues the request; it must not rely on a single "current ticket" global (concurrent analysts/debates). Each dispatch establishes a **request-scoped binding**: `dispatch(ticket)` stores the ticket in a **thread- and context-local** slot (e.g. `contextvars.ContextVar`, or pass a `run_manager.metadata`/config tag threaded into `_generate`), and `_create_chat_result` **resolves the ticket for its own request** from that scope, settles it once, and clears the binding. If no ticket is bound to the encountered request (e.g. an unexpected/auxiliary call), that is a **protocol condition** (unmetered request observed) → `TokenProtocolError` (mapped `INTERNAL_ERROR`), never a silent skip.

**Settlement when no response/result hook occurs (state-aware cleanup):**
- **Exception path:** if the provider raises, no result hook fires. The dispatch wrapper (`dispatch`→send) uses `try/except/finally` around the send:
  - **`except`:** settle to **UNKNOWN** (`settle_unknown`) **only if the ticket is still `DISPATCHED`** (no result hook already settled it). If the ticket is already `SETTLED_KNOWN`/`SETTLED_UNKNOWN`, leave it unchanged; if a **violation** was already recorded (e.g. overage detected before an exception in later handling), preserve it. **Never attempt a second settlement** and **never mask/replace the original exception** — re-raise the original (or a `TokenProtocolError` only if the ticket is in an impossible state, chaining the original via `from`).
  - **`finally`:** **always** reset the request-scoped context binding (`ContextVar`/config tag) for this request, regardless of outcome, so a later request on the same thread/context cannot inherit a stale ticket.
- **Valid usage then later failure:** if the result hook **did** run and settled known, a subsequent response-processing failure leaves the ticket `SETTLED_KNOWN` (usage already accounted); the wrapper must **not** re-settle to UNKNOWN.
- **Atomic overage update:** on overage, in one critical section update **both** `K` **and** `cumulative_consumed_known` (add full actual) together (plus the R decrement and violation flags) before propagating (§15A.4) — never expose `K` updated without the matching cumulative counter.
- **Streaming/Responses (if ever enabled):** must use their own hook; otherwise excluded above.
- **No double settle:** settlement requires `DISPATCHED`; a second hook for the same ticket is rejected (`TokenProtocolError`).

**Raw usage validation before normalization.** The installed normalizer (`_create_usage_metadata`) replaces missing counts with zero (`input_tokens = _input if _input is not None else 0`; same for output). Validating the **normalized** `usage_metadata` therefore **cannot** distinguish "provider reported 0" from "provider omitted the count". The metered seam must validate the **raw** provider usage **before** normalization:
- **Provider field mapping (supported route):** chat-completions → `response.usage.prompt_tokens` / `completion_tokens`. (Responses API would map to `usage.input_tokens` / `output_tokens`, but that route is **excluded** by §15A.6 capability validation until separately designed/tested.) These are **raw** fields, not the normalized `usage_metadata`.
- **Validity:** both raw counts must be present, integer, **≥ 0**. **Missing, partial, non-integer, negative, or absent `usage` object ⇒ `settle_unknown`** — even if the normalized `usage_metadata` contains integers (e.g. 0/0 synthesized by the normalizer). Only raw-valid values feed `settle_known(ticket, in, out)`.
- Do **not** copy `cli/stats_handler.py`'s `.get(..., 0)` zero-default.

**Admission/dispatch binding (final prepared request).** `admit` binds the reservation to the **post-`_get_request_payload`** serialized payload (provider-added fields such as DeepSeek `reasoning_content`, tool schemas, `tool_choice`, `max_tokens`) via the immutable `payload_fingerprint` (§15A.1); a caller-input mutation after measurement invalidates the ticket (`TokenProtocolError`) rather than dispatching a different request.

### 15A.7 Compatibility / migration (separate axes + token-capable record matrix)
`schema_version` (application result/manifest record format), `check_rules_version`, and the **requirements JSON-Schema version** (`docs/req/req-schema.json`, 1.2.0) are **three separate axes** (§16.7). The requirements-schema version is a D1 concern and never forces an application-format change.

**`EffectiveConfig` additions (safe; no prompts/secrets):**
```
token_admission_enabled: bool
token_budget: int | null              # TOKEN_BUDGET parameter (unset ⇒ null)
input_bound_method: str | null        # e.g. "exact:<tokenizer>" | "family:<id>x<mult" | null (unsupported)
output_allowance: int | null          # finite enforced per-attempt output allowance
```
plus the persisted audit fields in §15A.5.

**Compatibility matrix (explicit token-capable combinations; readers):**
| Record kind | `schema_version` | `check_rules_version` | token fields present | Reader behavior |
|---|---|---|---|---|
| Legacy (pre-token) | `1` | absent | no | **Explicit legacy path**: read Q1–Q4 semantics; token fields absent ⇒ no token accounting claim |
| Token-capable, budget-only | `2` | `1` | yes (`token_admission_enabled=true`, `token_budget`…) | readers accept `BUDGET`; token fields validated; checks stay Q1–Q4 |
| Token-capable, full checker | `2` | `2` | yes | readers understand `CORRECTED`/`corrected_fields` **and** token fields |
| Refused/unsupported token run | `2` | `1` or `2` | yes (`run_budget.token_audit.kind`, violation flags) | readers read the safe diagnostic + `INTERNAL_ERROR`/`BUDGET`; never coerce |

Rules: a `schema_version=2` record **with** token fields but an invalid `token_*` combination ⇒ readers **fail closed**. Concretely (agreeing with §15A.5 and §16.7): a missing/invalid `token_budget` is **rejected** when `token_audit.status ∈ {ACTIVE, VIOLATED}` (those require a present non-negative integer budget), while `enabled=true` + `status="UNSUPPORTED"` with `token_budget=null` and null `K/R/U/cumulative_*` is a **valid, accepted** combination (paired with `INCOMPLETE`/`INTERNAL_ERROR`); `enabled=false` (`DISABLED`) also legitimately carries nulls. Other invalid combinations — e.g. `K+R+U>budget` without `bound_violation=true`, negative `remaining` outside `VIOLATED`, or `UNSUPPORTED` carrying a non-null budget — ⇒ fail closed. Old readers that cannot interpret token fields/versions must **reject**, not silently ignore-then-claim. No new `StopReason` value is introduced. Preserve the legacy path exactly.

### 15A.8 Proposed verification scenarios (C inputs; not accepted)
| # | Scenario | Expected |
|---|---|---|
| T1 | reserve 60, settle known 20 (BUDGET 100) | R 60→0, K 20, H 20, remaining 80; calls granted 1, dispatched 1 |
| T2 | reserve 60, settle UNKNOWN | R→U=60, K=0, H 60, remaining 40; UNKNOWN not reported as actual |
| T3 | grant then invalidate unsent (CALL_CAP=1) | token fully released (H 0, remaining 100); calls granted 1, dispatched 0, invalidated 1; **next admit DENIED on call cap** |
| T4 | four concurrent, remaining fits one | exactly 1 admit, 3 refused; K+R+U ≤ BUDGET; calls granted +1 |
| T5 | duplicate settle / wrong-run / non-dispatched settle | `TokenProtocolError`, no bucket move |
| T6 | actual (75) > allowance (60), total < budget | INTERNAL_ERROR (not BUDGET), K=75, overage visible, admissions halted, no clamp |
| T7 | required request can't fit, total at budget | INCOMPLETE/BUDGET/NOT_RUN, no rating, findings [] |
| T8 | violation + critical persistence failure | PERSISTENCE_ERROR primary |
| T9 | usage missing/partial | settle UNKNOWN, capacity retained |
| T10 | old reader meets new field/version | fail closed |
| T11 | structured `.invoke` parses successfully | exactly one usage captured at `_create_chat_result`, one `settle_known`, one reservation consumed |
| T12 | structured `.invoke` **parse fails** → free-text fallback | first reply's usage **captured** (settled) despite parser discarding payload; fallback issues a **new** dispatch/ticket (no missed/double charge) |
| T13 | caller mutates inputs after `admit` | `payload_fingerprint` mismatch ⇒ ticket invalid / `TokenProtocolError`; no dispatch on a changed request |
| T14 | non-token-capable profile with token admission enabled | rejected pre-dispatch, `UnsupportedProfileError` → INCOMPLETE/INTERNAL_ERROR; no provider request |
| T15 | call cap refuses but token fits (or vice-versa) | **neither** resource granted (no partial grant); refusal is atomic |
| T16 | provider omits raw `usage`/one raw count while normalized `usage_metadata` shows synthesized `0`/`0` | raw validation detects the omission ⇒ **`settle_unknown`** (U retains capacity), **not** a known 0/0 settlement; normalized integers are ignored for validity |
| T17 | exception raised before any result hook | state-aware settlement (§15A.6): settle `settle_unknown` **only if the ticket is still `DISPATCHED`** (capacity retained), preserve any existing settlement/violation, original exception re-raised; `finally` **resets the request-scoped context**; no double settle (consistent with T20) |
| T18 | Responses API or streaming route enabled | rejected pre-dispatch by capability validation (`UnsupportedProfileError`), not silently unmetered |
| T19 | valid raw usage captured (settled known), then a **response-processing failure** occurs downstream | ticket stays `SETTLED_KNOWN` (usage accounted); wrapper does **not** re-settle to UNKNOWN; original exception preserved; request-scoped context reset in `finally` |
| T20 | exception after dispatch but before any result hook | ticket still `DISPATCHED` ⇒ `settle_unknown` (U retains capacity); original exception re-raised; context reset; no double settle |

**Handoff status:** this is a **proposed design with detailed contracts**, not an implementation commitment. Open before D can implement: provider-bound evidence per profile (E), parameter values (`TOKEN_BUDGET`/`CALL_CAP`/input multiplier/output allowance), and C's acceptance of the proposed scenarios. The usage seam (§15A.6) and failure contracts (§15A.4/15A.5) are specified; deployed-provider bound validity is **not** proven by offline tests.

---

## 16. Integration, implementation order and handoff — proposed

### 16.1 Dependency-aware implementation order
1. **§15 budget controller + `BUDGET`** (first handoff) — **READY FOR EXECUTION/TEST PLANNING** (see §16.6). Isolated, offline-testable; unblocks COST-002 (Must) + RUN-001 `BUDGET`. It does **not** depend on any unresolved Slice A/B policy decision. Remaining pre-build items are **explicit human authorization, an approved test plan/review, bounded scope and config choices**, not architecture blocks, and **not** a mandatory `/approve-tests` receipt (pre-approval is paused per `AGENTS.md`; the receipt applies only if explicitly re-enabled — see the prompt pack).
2. **§13 evidence/coverage data contracts** (data model): required **before** R2/R7 checker integration. **Blocked on A/C agreement** for the proposed channel catalog and any unrequested-core exemption; see §16.5.
3. **§14 checker v2 (R1–R8, R5 corrected+PASSED, R3 blocking)**: integrates R2/R7 after §13; Q2 preserved separately. Depends on §13 and on the A/C applicability decisions.
4. **Widen `NFR-REPRO-001`** record: fix `_prompt_hash` unreadable-file skip and `_effective_config` narrowing; **correct the blanket non-null fit** vs RUN-001 conditional fields.
5. **Optional / separate:** resume identity (FR-003), convergence (COST-003), PERF/COST-001 params — designed only if adopted; do not promise.

### 16.2 Slice A/B/C handoff boundaries
| Slice | Files (proposed) | D may touch | B supplies | C inputs |
|---|---|---|---|---|
| C (budget) | `runapi/budget.py` (new), `result.py`, `finalize.py`, `execution.py`, validators, OBS fields | code+tests (after approval) | §15 interfaces/invariants | B1–B7 scenarios |
| A (evidence) | `runapi/evidence.py`, `runapi/coverage.py` (new), `dataflows/router.py`, bypass sites | code+tests | §13 contracts | E1–E8 scenarios |
| B (checker) | `runapi/checks.py`, `result.py`, report/scorer readers | code+tests | §14 rule/finding/result contract | K1–K9 scenarios |

B does not edit D's application modules, C's tests, A's registry, or E's CI; B supplies interfaces and proposed scenarios only.

### 16.3 Genuine new design decisions (recorded in ADR 002)
These are a **genuine new design cycle** for the new requirements, **separate** from the preserved C2 evaluation (C1/C2/C3). ADR 002 records bounded alternatives for: (i) corrected-finding result contract; (ii) R3 phrase-check vs contextual; (iii) budget-controller reservation model; (iv) evidence/coverage component split. No historical alternatives, choices, experiments or ADD cycles are fabricated.

### 16.4 Feasibility (labelled ESTIMATE)
- **Design** of all slices by 25 Nov: feasible.
- **Slice C (budget + `BUDGET`)** is **ready for execution/test planning now** (§16.6); its design is complete and only standard gates remain.
- **Slice A (evidence/coverage) and Slice B (checker v2)** remain **blocked on A/C policy decisions** (§16.5) before they are execution-ready.
- **Implementation** of every new Must (FR-001 registry, FR-005 coverage, COST-002 controller, ARCH-002 R1–R8, BUDGET) **plus** C acceptance by 25 Nov: **unlikely / not promised** (ESTIMATE). Budget + BUDGET is the most feasible offline slice; the evidence registry is the largest risk.

### 16.5 Unresolved adoption / scope decisions (explicit)
- **Slice C (does NOT block budget planning):** `BUDGET` retained (assume yes; pending A/team) and `CALL_CAP` is a configuration value — both are confirmations, not architecture blockers; budget planning may proceed.
- **Slice A/B (block their own execution):**
  - **Channel catalog** (12-row proposal, bypass mapping) — **requires A/C agreement**; do not implement as adopted.
  - **Unrequested-mandatory-core exemption** — **requires A/team adoption**; strict rule applies until then.
  - R5 corrected+PASSED (approved as **published target**); R3 blocking phrase-check (target) with contextual handling an A/C/team alternative.
  - Sentiment **usable-free-text-without-structured** policy — open for A/C.
- `STALE_STATEMENT_DAYS`, `TOKEN_BUDGET`, `RUN_TIME_CAP`, `N_EVAL`, `QUALITY_THRESHOLD` — open configuration values (none blocks Slice C).
- Resume identity (separate, not implied).
- Optional-portfolio scope: **resolved** — the current registry scope includes optional portfolio input (profiles A-A/A-B/A-C), matching the implemented flow (OQ-13 closed). Separate open items remain: confirmation-flow ownership (**OQ-16**; no `REQ-TA-FR-009` invented) and the formal fixture population (**OQ-17**; structured `fixture_profiles.assignment` authoritative).

### 16.6 Slice C status (call-cap + `BUDGET`)
**Status: IMPLEMENTED for the bounded profile at `6b57aad`** (see §15/§12.5); the items below are retained as the original pre-build gate record for historical/review purposes, not as open requirements:
- **Explicit human authorization** for the change, an **approved test plan/review**, and bounded scope (prompt pack Templates 1/2/4/5). **Test-plan pre-approval is paused** per `AGENTS.md`; the `/approve-tests <SHA>` receipt is **optional/inactive while paused** and becomes a prerequisite only if explicitly re-enabled.
- Confirm `CALL_CAP` test value (8) and that the production default is a configuration decision (open, not measured).
- Include the mandatory hook files in the approved `implementation_paths[]` (`trading_graph.py`, `agents/structured.py`, `memory/settlement.py`, `llm_clients/factory.py`) plus `runapi/{budget,result,finalize,execution,reporting,persist,events}.py`.
- Run probes P1–P4 and B1–B11 as proposed C scenarios; **no runtime metering guarantee is claimed until they pass.**
- Ships as `schema_version=2, check_rules_version=1` (legacy Q1–Q4 preserved; BUDGET added), independent of the full checker-v2 rollout (§16.7).

### 16.7 Rollout: separate manifest/result version vs check-rule version (target)

Two **independent** version axes; do not conflate them:
- **`schema_version`** (manifest/result record format) — e.g. `1` (legacy) → `2`.
- **`check_rules_version`** — separate; `1` = legacy Q1–Q4 (blocking-only), `2` = R1–R8 with `CORRECTED`/`corrected_fields`.

A **third, external** axis is the **requirements JSON-Schema version** (`docs/req/req-schema.json`, currently 1.2.0) — that is a D1 registry concern and is **not** the application `schema_version`; an application-format change is never forced merely because D1's schema changed. The token-admission design (§15A) adds **no new `stop_reason`** (violation → `INTERNAL_ERROR`, refusal → `BUDGET`), so it does not add a stop-reason row here.

| Rollout stage | `schema_version` | `check_rules_version` | stop reasons | finding kinds | Q2 | Reader behaviour |
|---|---|---|---|---|---|---|
| Legacy artifacts (existing) | `1` | **absent** | five | `BLOCKING` only | on | **Explicit legacy path**: a schema-1 record with **no** `check_rules_version` is read under legacy Q1–Q4 semantics (allowed, not an error) |
| **Budget-only** (Slice C ships first) | `2` (adds `run_budget`) | `1` | six incl. `BUDGET` | `BLOCKING` only | on | readers accept `BUDGET`; checks stay Q1–Q4 |
| **Full checker v2** (Slice B later) | `2` | `2` | six incl. `BUDGET` | `BLOCKING`+`CORRECTED` | on | readers understand `CORRECTED`/`corrected_fields` |

Rules:
- **Q2 trusted-provenance guard is preserved in all three modes.**
- **Unknown/invalid new-format combinations are rejected (fail closed), not coerced**: e.g. `check_rules_version=2` in a record whose reader caps at 1; `schema_version=2` with a required field missing; a `check_rules_version` value other than the supported set; `CORRECTED` finding in a `check_rules_version=1` record (invalid combination). A reader that cannot interpret the declared versions must **reject**, never silently treat `CORRECTED` as non-blocking.
- **Legacy recognition is explicit and narrow:** only `schema_version=1` **and** `check_rules_version` **absent** takes the legacy path. A schema-1 record that *carries* a `check_rules_version` is **not** silently accepted.
- **A single vague "v2" label must not imply** that R1–R8 ran after only the budget slice shipped; `check_rules_version` distinguishes them.

**Required examples (to include in C's fixtures):**
- **Budget-only:** `schema_version=2, check_rules_version=1`, `run_outcome=INCOMPLETE`, `stop_reason=BUDGET`, `output_check=NOT_RUN`, `findings=[]` — accepted; findings are blocking-only.
- **Full v2 with corrected finding:** `schema_version=2, check_rules_version=2`, `output_check=PASSED`, `findings=[R5 CORRECTED]`, `corrected_fields={sentiment_confidence:"low"}` — accepted.
- **Rejected unknown-version:** e.g. `check_rules_version=3` (or `2` in a reader that supports only `1`), or a `CORRECTED` finding under `check_rules_version=1` — **rejected (fail closed)** with a typed reader error, not silently downgraded.

**Token-capable records reconciled with this matrix (§15A.7).** `TokenAudit` is an **additive** field under `run_budget.token_audit`; it does not add a `stop_reason` or `check_rules_version`. Reader acceptance:
- **Call-cap-only (no token admission):** `schema_version=2`, `run_budget` present without `token_audit` (or `token_audit.enabled=false`, `status="DISABLED"`). Readers accept; absence of `token_audit` or a `DISABLED` audit makes **no token-accounting claim**.
- **Token-capable, budget-only checks:** `schema_version=2`, `check_rules_version=1`, `token_audit.status ∈ {ACTIVE, VIOLATED, UNSUPPORTED}` — readers accept, validate the `TokenAudit` conditional rules (§15A.5), and do **not** imply R1–R8 ran. **`enabled=true`+`status="UNSUPPORTED"` with null `budget`/counters is explicitly accepted**, and the record's `run_outcome` must be `INCOMPLETE` with `stop_reason=INTERNAL_ERROR`.
- **Token-capable, full checker:** `schema_version=2`, `check_rules_version=2` with token audit — readers understand both.
- **Require valid budgets:** `status="ACTIVE"` or `"VIOLATED"` **without** a present non-negative integer `budget` is **invalid** (fail closed). `status="UNSUPPORTED"` **must** have null `budget`/`K`/`R`/`U`/`cumulative_*` (non-null there is invalid).
- **Fail closed (other violations):** a `schema_version=2` record whose `token_audit` violates the shape/conditional rules — e.g. `enabled=true` with `status="DISABLED"`; `ACTIVE` with `bound_violation=true`; `VIOLATED` with `violation=null`; `VIOLATED` with non-negative-required count negative; **negative `remaining` outside `VIOLATED`**; `units≠"tokens"`; `UNSUPPORTED` with a non-null budget — or a reader that cannot interpret `token_audit`, must **reject** — never coerce, never treat `U` as measured actual. The legacy `schema_version=1` path (no `run_budget`) is unchanged and makes no token claim.

> **ADR 002 wording clarification (AR24 06):** “approved published target” in ADR 002 means approval to **draft this architecture target** — it is **not** final team adoption of the requirements and **not** a completed, tested ADD iteration. The new decisions (D1–D5) are genuine new proposals for review; they do not reopen or restate C2.

---

## 17. Proposed semantic gate — trigger, binding, scoring and lifecycle (PROPOSED; not installed)

Status: **proposed interface** for `REQ-TA-GOV-001` (semantic evaluation; historical `SEL-TA-GOV-004`) — **distinct** from `REQ-TA-GOV-004` (requirements schema gate). The replay/scorer/packager **exist**; the **path classifier, gate wrapper/`GateEvaluation` metadata and CI blocking are NOT installed**. The current seven required checks do **not** include a semantic check; `ci.yml` keeps live replay opt-in. This section adds **no** required check, threshold, profile or provider change; it answers E's four interface questions and separates three layers: (1) existing opt-in tools, (2) this proposed trigger/head/CI adapter, (3) acceptance & activation owned by A/C/D/E.

### 17.1 GOV_PATHS v1 (proposed E-owned policy; not a committed enforcement file)
File-level conservative trigger — a matched edit triggers even if comment-only; **no ad-hoc per-PR exemption**. Case-sensitive repository-relative POSIX, no leading slash; trailing `/` = prefix, else exact. Use trusted base/head diff; add/modify/delete/type-change/copy and **both old and new paths of a rename**; moving a governed file out still triggers. Multiple matched files ⇒ **one decision per candidate commit**. Classification/diff failure ⇒ **UNKNOWN**, never NOT_APPLICABLE.

Prefix entries: `tradingagents/`, `cli/`, `prompts/`, `config/`, `configs/`, `.github/workflows/`. (prompts/config/configs reserved if absent.)

Exact entries (fully expanded): `main.py`; `pyproject.toml`; `requirements.txt`; `uv.lock`; `poetry.lock`; `tests/member_c_verification/live/cases.py`; `tests/member_c_verification/live/conftest.py`; `tests/member_c_verification/live/runner.py`; `tests/member_c_verification/live/replay_store.py`; `tests/member_c_verification/live/score_gov004.py`; `tests/member_c_verification/live/package_gov004.py`; `tests/member_c_verification/live/test_gov004_live.py`; `docs/verification/semantic-evaluation.md`; `docs/verification/gov004-evidence-package.md`; `docs/code-governance/verification-constraints.md`; `docs/req/requirements.yaml`; `docs/architecture/interface-contracts.md`; and the **future E-owned** (not current files) `scripts/ci/check_semantic_gate.py`; `docs/code-governance/semantic-gate-policy.json`.

No automatic live-replay trigger for changes confined to `AI-log/`, `docs/reviews/`, `docs/submission/`, ordinary architecture/ADR/README prose (other than the listed contract), images/video, `tests/member_c_verification/offline/`, `live/test_harness_selfcheck.py`, `live/test_score_gov004_exitcodes.py`, other test-only files, or generated/sanitized evidence. **Matched-path policy takes precedence** over these exclusions. Private runtime config changes still alter the config fingerprint and invalidate unmatched evidence.

### 17.2 Reuse existing tools; complete command templates; candidate binding
Reuse (no second scorer/counter). Complete templates (POSIX, from repo root, project venv):

```sh
# Replay (paid/live only when GOV004_LIVE=1; formal slots trial 1|2)
GOV004_LIVE=1 GOV004_TRIAL=1 GOV004_EVIDENCE_DIR="$PWD/<evidence-root>" \
  .venv/bin/python -m pytest -q -s -p no:cacheprovider tests/member_c_verification/live/test_gov004_live.py

# (A) Score the SOURCE evidence with the human scores file
GOV004_EVIDENCE_DIR="$PWD/<evidence-root>" \
  .venv/bin/python tests/member_c_verification/live/score_gov004.py <scores.json>

# (B) Package to a NEW independent destination (exports the scores file with the package)
.venv/bin/python tests/member_c_verification/live/package_gov004.py "$PWD/<evidence-root>" "<new-dest>" --scores <scores.json>

# (C) Re-score the PORTABLE package using ITS OWN exported scores file
GOV004_EVIDENCE_DIR="<new-dest>" .venv/bin/python tests/member_c_verification/live/score_gov004.py "<new-dest>/gov004_scores.json"
```
(`runner.run_case`→`run_analysis_api`, `replay_store.dispatch_slots`; ticker/date must match the frozen cohort; packaging success is not a semantic verdict.)

**Candidate binding:** evaluate the PR's **exact full head SHA**, not a mutable branch/merge; clean isolated checkout for formal approval. `_source_revision()`'s short git label (may append `+dirty`) is **not** exact PR-head proof — the adapter must independently bind the full SHA and require `evaluated_head_sha == current target_head_sha` immediately before posting. A **new head invalidates** approval (no cross-commit cache reuse). Dirty runs are diagnostics only. Reuse existing runner preflight (source/prompt identity, cohort schema/slots/chronology, ticker/date, model IDs, both tier providers). **Source-inventory `prompt_hash`** (identifies source; currently skips unreadable files — an R-HASH risk the gate must preflight) ≠ **per-call `PromptCapture.prompt_sha256`** (hashes assembled prompts, not stored). Separate purposes: source hash / per-call digest / commit identity / config-cohort identity.

**Proposed governance safeguards (PROPOSED, not enforced):**
- **A policy change cannot remove its own obligation:** classify the PR's changed paths against the **trusted previously-approved policy** and the **candidate policy**, and treat the **union of matches** as required — so editing `semantic-gate-policy.json`/GOV_PATHS to drop a path cannot exempt that same PR.
- **Grading tools are frozen before use:** changes to case catalog/rubric/scorer/packager/preflight require **owner (C/E) review and freeze** at approved immutable revisions **before** evaluation; code controlled by the PR under test cannot award itself a PASS. Compare results under the trusted approved policy/tools, not candidate-modified ones.

### 17.3 Scores, artifacts, typed `GateEvaluation`, retention
**Scores/submission distinction:** a scores JSON with a real reviewer, per item `case_id`, `run_id`, `trial`, `item`, integer `score ∈ {0,1}`, and an exact nonempty citation in the corresponding report; the scorer derives applicability (no fabricated N/A/identity/citation). **Missing/unsubmitted scoring ⇒ PENDING (2)**; a **submitted but incomplete/invalid** score matrix (bad schema, missing required applicable cells, wrong reviewer fields) is **FAIL (1)** under the existing scorer — these are different outcomes.

Evidence under a fresh `GOV004_EVIDENCE_DIR`: `cohort.json` (schema 2), `gov004_starts.json` (versioned STARTED ledger, durably claimed before dispatch), `gov004_attempt_<run_id>.json` mirrors, `runs/<stamp>/<case>/` artifacts; reports/manifests by portable relative path + SHA-256. `package_gov004.py` copies refs into a new destination and emits `integrity.json` (file digests); re-score the portable copy from a fresh directory.

**`GateEvaluation` — outer E-owned envelope (single typed shape; beside, not inside, the tool package; no new `RunResult`/manifest fields):**
```
GateEvaluation
  gate_contract_version: 1                 # int, exactly 1
  gate_mode: "PILOT" | "BLOCKING"          # enum
  applicability: "REQUIRED" | "NOT_APPLICABLE" | "UNKNOWN"   # enum
  policy_digest: str                       # lower-case SHA-256 hex
  base_sha: str | null                     # full commit id (null if unknown)
  target_head_sha: str | null              # full commit id
  evaluated_head_sha: str | null           # full commit id
  runner_revision: str | null              # immutable approved tool revision
  scorer_revision: str | null
  packager_revision: str | null
  case_catalog_sha256: str | null          # lower-case SHA-256 hex
  rubric_sha256: str | null
  cohort_sha256: str | null
  config_sha256: str | null
  prompt_hash: str | null
  evidence_root_ref: str | null            # safe relative ref
  portable_package_ref: str | null
  package_integrity_sha256: str | null
  scores_sha256: str | null
  raw_scorer_exit: int | null              # raw process exit; 0/1/2 are the recognized scorer protocol codes (PASS/FAIL/PENDING); any other exit is preserved for diagnostics
  semantic_verdict: "PASS" | "FAIL" | "PENDING" | null
  reason_code: str                         # bounded safe code (nonempty)
```
Unavailable fields are `null` and the verdict is `PENDING` — **`null` is never accepted as a matching binding**, and `NOT_APPLICABLE` carries `semantic_verdict = null` (not `PASS`). **Scorer-exit protocol:** `0/1/2` are the recognized protocol codes (PASS/FAIL/PENDING). Other process exits are recorded as-is for diagnostics but are **not** a verdict. An unexpected exit, a missing valid terminal verdict, or an **exit/verdict mismatch cannot establish PASS** — report **PENDING** with an execution/protocol `reason_code`, and formal acceptance is blocked. An **already-established valid FAIL is preserved** (do not overwrite it with PENDING).

**Retention/index binding (PROPOSED):** reviewed, **sanitized** package copies may be retained durably (E-owned CI artifact / archive / approved review location); the original private evidence stays ignored. The E-owned outer index must bind each `GateEvaluation` **digest** to `integrity.json` **and** the `scores`/package refs; an expiring unarchived artifact is **not** durable final-submission evidence. Commit only authorized sanitized artifacts.

### 17.4 Verdicts, lifecycle and PILOT/BLOCKING
Raw scorer semantics preserved: **PASS=0, FAIL=1, PENDING=2**; no permissive second scorer, no inferring PASS from pytest/package success, no lowered thresholds.
- **Valid, applicable, current-head scores satisfying fixed conditions** ⇒ PASS (limited to declared profile/mode).
- **Below threshold / critical / failed eligibility / malformed evidence / invalid score schema** ⇒ FAIL (distinguish invalid evidence from bad narrative).
- **No evidence / missing score file / scoring incomplete** ⇒ PENDING (never PASS); supplied-but-malformed scores ⇒ FAIL.
- **API unavailable before any start / no verdict / interrupted with no valid final scorer result** ⇒ PENDING (infra reason); retain logs/starts; do not overwrite an existing FAIL.
- **Failure/interruption after STARTED** ⇒ retain INCOMPLETE/`MODEL_FAILURE`/`INTERRUPTED`/unresolved; no fabricated rating; run scorer on retained evidence and keep its actual verdict (may PASS only if all acceptance still holds, with the incomplete attempt reported).
- **Hash/head mismatch or foreign-head evidence** ⇒ FAIL binding; old valid result ≠ current PASS (current state PENDING if no current-head run).
- **Classifier unavailable / required job skipped-cancelled / unsupported profile / missing policy adoption** ⇒ PENDING (explicit reason), never "no impacted path".
- **No GOV_PATHS change** ⇒ NOT_APPLICABLE, `semantic_verdict=null` (not PASS); no live calls.

**Unfinished evaluation ≠ incomplete application attempt.** This adds **no 100%-completion rule**: the existing formal policy may accept nine eligible completed + one correctly bound pending start (completion 9/10), with all cases covered, human scores complete and other conditions met — while still showing that one attempt is incomplete; missing required scoring/evidence is never PASS.

**PILOT** (current intent, per A's OQ-20): report raw PASS/FAIL/PENDING with target/profile + infrastructure status; it is **not** a required merge check while `QUALITY_THRESHOLD` remains open, so FAIL/PENDING may be nonblocking **because the gate is not blocking**, not because the verdict changed. Execution success of a report-uploading wrapper is labelled separately from the semantic verdict; never blanket `|| true`. **This does not waive behavior checks:** `REQ-TA-FR-005` (missing-data disclosure), `REQ-TA-FR-007` (ownership wording), `REQ-TA-SEC-001` (injection) and `REQ-TA-SEC-003`/`REQ-TA-INV-008` (guarantee/disclaimer) remain **minimum required behaviors in both phases** — expected, and **not claimed to pass** (each is `proposed`/`partial`); they are the *minimum* suite contents, not the whole 36-entry population. **BLOCKING** (future, explicit E/team activation only): only REQUIRED + current-head valid PASS satisfies; FAIL/PENDING block; missing/cancelled/skipped not success; NOT_APPLICABLE ≠ PASS. Enter BLOCKING only after the owners establish the required baseline/`QUALITY_THRESHOLD`/`N_EVAL`/profile/parameter and integration conditions, trigger/preflight/adapter tests exist, evidence access is available, and **E records activation**; this proposal makes **no current CI change**. Existing `MIN_SCORE=0.90` and green offline tests do not satisfy that transition.

**Boundary and owner map:** B (this section + current-vs-proposed), C (cases/rubric/scores/independent acceptance), D/E (adapter/workflow/retention), A (requirement meaning). The current **five cases / two trials** are a **project trial** relative to the provisional `N_EVAL=20` — **five cases remain five, not ten of twenty**; the raw legacy scorer `0/1/2` semantics, the 90% policy and cohort serialization (incl. tool-level formal/trial labels) are preserved, and a raw legacy scorer PASS is **not** registry acceptance. `N_EVAL` stays provisional 20 (any D-owned change is recorded in the parameter appendix/change log); `QUALITY_THRESHOLD` remains D/E-owned. Full `REQ-TA-GOV-001` compliance is **not** established by existing constants, and no team adoption is implied.
