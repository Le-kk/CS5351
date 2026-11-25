# E integration addendum: course layout and browser adapter

Status: implementation/integration record, not a new B architecture approval. The original C2 shared run boundary remains authoritative; proposed budget/semantic/evidence obligations are not adopted by this file.

Physical source is now under src/tradingagents, src/cli, src/demo and src/frontend. Deterministic tests and opt-in live tests are under test/offline and test/live. Historical root names are compatibility aliases to the same files, not second modules. Package names/entry contracts are unchanged; a stable project_root helper replaces assumptions about source-directory depth.

The English browser adapter prepares and freezes inputs through the input service and invokes run_analysis_api only after explicit confirmation. It uses loopback HTTP, same-origin requests, an ephemeral CSRF token, a whitelist of public stage records/file IDs and existing redaction/publication. Model credentials stay server-side. It does not expose system prompts or hidden reasoning and is not a public authenticated deployment or broker integration.

Browser sessionStorage retains only a run ID. The adapter keeps local registry/stage records under ignored local storage and restores interrupted jobs as INTERRUPTED/NOT_RUN with partial usage, never a forged completed result. Refresh is not cancellation; one background run is active at a time. A 120-second request timeout is not a run-wide deadline or a process-safe cancellation mechanism. Actual in-flight usage can remain unknown after interruption.

The compact_evidence_handoff switch changes intermediate writing in existing calls, including the separately invoked Sentiment Analyst. Complete generated reports remain in graph state and outputs; no new summarizer, lossy downstream extractor or graph topology is introduced. The application default is off; the demo launcher explicitly enables it. Measured reduction is small-sample developer evidence, not independent semantic acceptance or aggregate token admission.

E's current README, trace links and coverage guide describe the integration. B should verify affected component/memory mappings and C should evaluate semantic/operational quality at the final delivery SHA. Existing native permission evidence is historical after policy path updates. No owner sign-off is invented.
