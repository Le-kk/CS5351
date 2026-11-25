# AI-assisted frontend and backend integration — 2026-11-25

## Selected original-language user request

> 我已把前端放在软工->nocode里面，请你1.去除商标2.把残存的中文翻译成英文3.实现后端部署

## Work and human intervention

The user supplied the exported frontend and requested real-model execution, wrapped configuration choices, visible debate records and generated files. The assistant removed platform icons/injection plugins and used English interface labels. The human authorizes local integration; no public hosting or GitHub publication is claimed.

## Changes

Added demo/console.py and demo/console_service.py to adapt the existing production run API, graph, budget controller, output checker and report publisher. Added independent tests in tests/member_d_verification/test_nocode_console.py. Existing untracked demo modules and their tests were retained. Updated the external nocode frontend's API client, confirmation flow, status/discussion/file polling, history, report previews, benchmark evidence and build configuration. Added deployment documentation and a launcher. Full code/tool payloads are omitted; original conversation language is retained above. No credentials are included.

## Verification evidence

A real run, 20261125T070128Z-bc0a6376, completed: NVDA / 2026-01-09 / four analysts / one round per debate / no portfolio / cap 30. Actual dispatched requests: 20. Provider usage: 88,116 input + 13,125 output = 101,241 tokens. Elapsed 84 seconds. Output check PASSED, Hold. Browser showed discussions, stage files and final HTML preview. This is not semantic acceptance or a matched token baseline. Data feed limitations remain explicitly visible. New console tests initially passed 8 cases; full regression results are recorded in deployment verification after completion.

## Limits

Loopback deployment only; the school model provider and external market data remain network-dependent. Unavailable data and incomplete usage are not fabricated. Original frontend backup and runtime records remain in ignored local storage.

Final checks: full offline suite 2,003 passed, 2 skipped, 1 deselected, 100 subtests passed; Ruff passed; Bandit demo scan reported no medium/high findings; frontend production build passed. HTTP probes rejected missing-CSRF start (403) and an unknown file (404). Browser HTML preview and actual HTML download succeeded.
