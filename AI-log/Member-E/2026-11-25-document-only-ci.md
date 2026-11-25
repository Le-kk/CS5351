# Document-only CI routing — 2026-11-25

## Selected original-language user request

> 请修改这个CI,
>
> - **纯文档 PR**：检查链接、文件格式和必要的内容一致性，跳过依赖安装及代码测试。
> - **代码、依赖、workflow 或关键配置变更**：继续完整检查。
> - 保留固定的必需检查名称，由汇总任务确认哪些检查可以合理跳过，避免分支保护一直等待。

## Public response and implementation

Added complete-diff conservative routing, standard-library document checks and strict fixed-name summaries. Pure document PRs do not install dependencies or execute application tests. Mixed/protected/unknown changes and main/version pushes retain complete CI. All seven branch-protection names remain present; failed classification, failed documents and unexpected skipped/cancelled/missing worker results do not pass. Code-to-Markdown renames retain the original code path and require full CI. No application or live-model behavior was changed; prior approval remains paused.

Changed .github/workflows/ci.yml; added ci_scope.py, check_documents.py and check_ci_results.py under scripts/ci, plus test_docs_ci.py under test/offline/member_d_verification. Added the governance guide and refreshed README/E14 usage notes. Detailed code/write payloads and hidden reasoning are omitted. Ruby's preinstalled safe YAML parser is used only for the structured AI-use index; parser absence/errors fail. No provider credentials are read or published.

## Verification and limits

40 focused negative/routing tests passed. Full local regression: 2074 passed, 2 skipped, 1 deselected, 100 subtests passed. Ruff and five-workflow permission checks passed; actionlint passed. The actual E14-only diff classified as docs and passed document checks using system Python without application dependencies. Format checks cover UTF-8, fences, JSON/SVG, PDF structure markers, report pairing/hash and safe AI-use index/source hashes. External link targets, heading fragments, complete PDF layout and semantic truth are not certified. Fresh hosted documentation-route verification is still required after deployment; no unexecuted tools are claimed to have passed.

E14 PR #51 finally passed required tests after hosted runner initialization/install delay and was normally merged before this separate CI branch; no protection bypass was used. Automatic merge was unavailable and was not enabled by this work.
