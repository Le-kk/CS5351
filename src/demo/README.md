# Local research demo backend

The presentation frontend is maintained locally and is not part of the repository delivery. Build it using its own local project. From the repository root, run `python -m demo.console --frontend-dir /path/to/local/frontend/build --compact-evidence-handoff --open`. On the original machine, the default finds the sibling nocode/build directory. Default URL: http://127.0.0.1:8766, loopback only. Keys stay in private backend configuration.

The backend validates and freezes inputs, requires explicit confirmation, and exposes real stage records, usage, result status and whitelisted report files. Missing holdings remain unknown; explicitly supplied empty input is a different mode. PASSED is an output check, not financial acceptance. A request cap is not a token ceiling. A model request timeout is not a total-run deadline.

A refresh does not cancel background work. Interrupted history is retained with partial usage and no forged success. Compact formatting changes existing model calls without adding a summarizer or truncating complete generated reports. Application default remains off; the demo flag enables it. Historical and later developer measurements are in docs/verification and do not establish universal or semantic acceptance.
