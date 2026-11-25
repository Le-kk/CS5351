# OpenCode role permission configuration

Date: 2026-11-25 (Asia/Hong_Kong). E5 implementation supplement to main `14b06a5`.

E6 loading supplement (2026-11-25): [operating rules](../../.opencode/rules.md) now load as the shared role prompt; see the [loading/verification notes](opencode-operating-rules.md). The E6 configuration is covered by the [E6 verification record](../verification/opencode-rules-probes-2026-11-25.json); the E5 record below is retained for its original hash.

E7 covenant supplement (2026-11-25): all five roles can read the [project covenant](../../.agent/rules.md); only E can edit it by default. AGENTS.md requires reading it at startup. It is not automatically injected as a prompt. The latest policy and covenant are covered by the [E7 verification record](../verification/project-covenant-probes-2026-11-25.json). Safety review and freshness requirements are process obligations, not a new merge gate.

## Configuration and activation

[.opencode/permissions.jsonc](../../.opencode/permissions.jsonc) contains native **OpenCode V1 1.19.5** configuration (`permission` and `agent`). It is a real configuration, not a proposed permission matrix. It is intentionally version-pinned: current V2 documentation uses different fields and must not be copied into this V1 file. The installed executable validates the configuration during the checks below.

The course-required filename is not an automatically discovered configuration filename. Start from the repository root using:

```sh
python scripts/run_role_agent.py D --check
python scripts/run_role_agent.py D
```

Replace D with A, B, C or E for the assigned role. The [launcher](../../scripts/run_role_agent.py) selects the explicit `member-a` through `member-e` profile, sets `OPENCODE_CONFIG` to the course file, removes inline permission/config overrides, requests pure mode (external plugins disabled), checks the executable version and checks the native resolved permission rules before starting a fresh session. A failed check refuses startup. It does not resume an existing session or pass an auto-approve flag. Merely starting an unrelated session does not establish that this policy was loaded.

## Role scope

All profiles default to deny. Read allowances include the non-secret startup documents and relevant source/tests/requirements; write allowances are scoped:

- A: `docs/req/`.
- B: root blueprint, ADRs and individually enumerated existing B architecture documents; no blanket architecture write grant and no final trace-matrix write grant.
- C: tests, verification material, review/bug/debt records and `docs/code-governance/verification-constraints.md`.
- D: application, CLI, prompts and implementation experiments; tests remain readable but not writable.
- E: root agent instructions, permission configuration, governance/CI, final trace matrix and submission integration; implementation, tests and requirements remain outside its write scope. C's verification-constraints file is explicitly excluded from E's broad governance write allowance.

Each role may update its own `AI-log/Member-<role>/` records, subject to the authenticity rules in AGENTS.md. Relative to B's design, E's writable governance tooling explicitly includes `scripts/ci/` and the two permission helper scripts, and all roles can read the named governance startup guides. These are documented integration additions, not undisclosed implementation/test access.

`.opencode/rules.md` is human-only for writes, including E. Sensitive environment/authentication/key files, credential paths, private portfolio/log/result locations, Git internals and generated/private areas have explicit trailing denies. The configuration does not embed credentials or select a paid model/provider.

OpenCode's native V1 rule resolution is ordered: the **last matching rule wins**, not a universal deny-wins algorithm. Accordingly each role's broad deny precedes path allowances and sensitive denies come last. This is a translation of the intended protection outcomes in B's design; the original draft's abstract precedence wording is not the native matching algorithm. Future changes must preserve this order and rerun the probes.

## Closed bypass channels

Shell commands, grep, glob, directory-list tools, LSP tools, skills, delegation, web access and unspecified tools (including MCP actions) are denied in these strict profiles. In particular, a shell or broad text search cannot be used to bypass a file-read deny. Native `read` can list an explicitly readable directory; this is not a general search allowance. Native `write` and `edit` use the scoped edit permission.

Run tests and administrative Git operations through an authorized human/session outside these restricted profiles. This limitation is deliberate: allowing a Python interpreter or arbitrary test command would permit code to perform file access beyond a path whitelist. This configuration does not claim to confine arbitrary shell execution.

The launcher rejects a workspace containing symlinks before launch, excluding the contents of denied Git/generated directories from traversal. This guard is necessary because native V1 path rules alone are not a demonstrated canonical-target sandbox. Do not introduce symlinks while the session runs; restart through the launcher after external tree changes. It is a startup check, not race-free continuous filesystem isolation.

## Verification and retained evidence

Run the [native probe tool](../../scripts/verify_role_permissions.py):

```sh
python scripts/verify_role_permissions.py --output /tmp/opencode-permission-probes.json
```

It creates a temporary synthetic Git workspace, loads the same configuration into OpenCode, and calls native `debug agent --tool read/edit/write`. No model inference is needed. It verifies allowed startup reads and role-owned creation, denied cross-role writes, secret/private/external reads, human-only writes, D's test-write denial, C/E ownership exceptions, native write-tool behavior, a disabled shell and startup rejection of a symlink. Denied creation probes verify that the target remains absent/unchanged. The native debug entry checks deny decisions directly; this evidence is not a paid-model conversation or a demonstration of interactive ask/approval handling.

The retained [verification record](../verification/opencode-permission-probes-2026-11-25.json) records tool version, configuration hash, each expected/observed outcome and permission-denial indicators. Re-run after configuration changes; a configuration change during a probe run is rejected. Synthetic fixtures contain no real account data. A denial, configuration failure or incomplete run must never be labelled a pass.

## Enforcement limits and maintenance

These are checked **local tool permissions**, not OS ACLs or authenticated member identities. A human who controls the machine can choose another profile, bypass the launcher or change the policy. E's permission-file write authority is privileged; changes require explicit governance authorization and a new verification record. The configuration cannot make evidence append-only or determine whether an arbitrary document contains undisclosed private data. Only sanitized task material should be placed in readable paths.

V1 also appends a native external-directory allowance for its managed tool-output area. The launcher verifies the explicit external-directory deny but does not claim to remove that internal allowance. General external-file reads are tested as denied. Automatic host context, attachments and higher-priority administrator settings are not certified as a universal information-flow sandbox by these file-tool probes.

The probe runner is a local executable verification tool; no new GitHub job or required check has been installed here. Existing CI and branch protection remain unchanged. Test-plan pre-approval remains paused as a required merge check. This file and evidence establish the configured/tested scope, not unrelated course process compliance or independent acceptance.

Sources: B's [permission model](../architecture/permission-model.md); [OpenCode permission documentation](https://opencode.ai/docs/permissions/) and [V1 migration notes](https://opencode.ai/docs/migrate-v1/); version-pinned [native debug tool entry](https://github.com/anomalyco/opencode/blob/v1.19.5/packages/opencode/src/cli/cmd/debug/agent.handler.ts) and [native read tool](https://github.com/anomalyco/opencode/blob/v1.19.5/packages/opencode/src/tool/read.ts). Use executable validation for the pinned V1 configuration rather than assuming the current online V2 schema is identical.
