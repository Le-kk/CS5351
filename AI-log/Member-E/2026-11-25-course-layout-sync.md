# Repository synchronization and course-layout assembly — 2026-11-25

## Selected original-language user request

> 请把GitHub和本地项目同步，并查看有没有文件需要更新，如果有，请你帮助它们更新，按课程要求的项目结构重组GitHub上的路径，一些过时的文件，可以看看创建一个history目录存放

## Actions and scope

Backed up 29 local files with SHA-256 under ignored local storage; committed existing demo/token/refresh work as 4575c4f. Merged origin/main be6b902, retaining A/B/C/D updates, reports and full transcript evidence without force push. Course project PDF pages 5–9 supplied the source/delivery structure. Physical Python/backend/frontend source moved under src; tests split into test/offline and test/live. Root legacy names are compatibility links to one physical source, not duplicated implementations. A small project_root helper preserves checkout paths; migrated test root calculations and qualified fixture imports retain all existing assertions. No network/model test was quietly enabled.

## Updated materials

Updated README, AGENTS layout guidance, trace paths, structural/governance paths, package discovery, CI, scoped permission equivalents and prompt-fragment snapshots. Archived superseded README/prototype/export material with paths/hashes; preserved dated failures, immutable transcripts and AI conversations. Moved D's formal report/reflection to docs/submission/member-d with old-location notices. Root Report.md is an explicitly incomplete, source-attributed assembly draft, not fabricated final acceptance. The E reflection is the user-requested draft; missing B/C/identity/contribution inputs are marked. Structured AI-use inventory hashes/counts are refreshed against the actual files.

## Verification and limits

Before migration, merged full suite: 2,024 passed, 2 skipped, 1 deselected, 100 subtests. Initial migration runs exposed root-path and same-name conftest import conflicts; corrected locations/imports without relaxing assertions. Migrated full suite then returned 2,024 passes. New negative checks cover legacy alias identity, canonical path log coverage, prompt snapshot equality and frontend failure propagation into required tests. Type coverage remains scoped; application security scanning now includes the demo. Frontend audit initially found 19 high and 1 critical issue; after compatible fixes, removal of unused vulnerable zod and Vite/plugin upgrade, build passed and no high/critical issue remained, with five moderate findings explicitly retained as debt. Exact final commands/results and remote PR outcome are recorded below after completion.

No hidden reasoning, full code/write payloads, secrets, real holdings or missing member approvals are included. Original user language is retained. History is not current acceptance evidence.

## Final pre-upload results

Full suite: 2,033 passed, 2 skipped, 1 deselected, 100 subtests passed. Ruff passed; mypy 15 files passed; registry 36 active/3 withdrawn, zero errors/warnings; workflow boundaries five passed; Bandit 115 Python application/demo files, zero medium/high findings. AI-log and required-summary negative self-tests passed. Production frontend build passed after audit fixes; npm audit zero high/critical, five moderate. Wheel built with isolation and imported application, CLI and demo from a separate target outside the checkout. Maintained README/Report/AGENTS/demo/trace links checked; replaced a deleted current evidence link with C's retained evidence index. Browser verified the src/frontend production build and actual backend validation on an isolated port; no additional model run started. Re-fetched origin/main be6b902 before upload; no concurrent remote change at this check. Hosted CI/merge still pending at this record snapshot.

Final pre-merge path review also gave the new demo/frontend modules the same per-role read rights as CLI, and only D's existing implementation-edit right; no other role gained implementation writes. Sensitive-path denies and default-deny remain. Native acceptance for the changed policy is still pending. The required-tests entry point now has an explicit success/failure/missing FRONTEND_RESULT probe, not only an internal dictionary test.

## Hosted packaging failure caught before merge

GitHub's real frontend build rejected missing src/lib/apiClient.js and utils.js. The upstream generic lib/ ignore rule had excluded these frontend source helpers even though the local working tree build could read them. Added narrow unignore rules for src/frontend/src/lib and committed the existing source files; no checks were removed or bypassed. Python matrix/installation passed in that failed run; required-tests correctly rejected the frontend failure. The failed hosted run is 45631744695.
