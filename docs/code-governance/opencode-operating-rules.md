# OpenCode operating rules — loading and verification

Date: 2026-11-25 (Asia/Hong_Kong). E6 supplements the local E5 permission package.

## Files and activation

[.opencode/rules.md](../../.opencode/rules.md) contains the behavioral rules for all five roles. Each native V1 profile in [permissions.jsonc](../../.opencode/permissions.jsonc) sets `prompt: "{file:rules.md}"`. OpenCode resolves that file reference relative to the configuration directory. The [role launcher](../../scripts/run_role_agent.py) checks that the resolved native agent prompt exactly equals the nonempty rules file before starting a fresh session. A missing file or mismatched prompt refuses startup.

Use the existing activation command; no new workflow is required:

```sh
python scripts/run_role_agent.py D --check
python scripts/run_role_agent.py D
```

Replace D with the assigned A–E role. The root AGENTS.md remains the repository entry point; this rules file supplies the shared role prompt. It is not automatically activated merely by its filename. Native role configuration plus the explicit launcher provide the tested loading path. Use a new session after rule changes.

## Content and authority

The rules cover instruction authority, task scope, role boundaries, preservation of other work, architecture direction, input consent/freezing, no-portfolio semantics, privacy, deterministic outcome authority, verification honesty, token-measurement limits, CI protection and AI-use evidence. Required tests that cannot run within the strict profile are handed to an authorized human/session and remain unexecuted until results exist. Test-plan pre-approval remains paused as a required merge check.

All roles may read the file. Native edit permission remains **deny for every role**, including E, and prior human-only write denial probes are retained. The initial file creation and loading changes were explicitly requested by the user; this is not a grant to models to rewrite their rules during ordinary work. Future changes are human-controlled governance actions, not a self-approval mechanism.

Rules are model instructions, not proof of perfect compliance. Native permission denials constrain tool operations separately; they do not certify semantic correctness, filesystem isolation or member identity. Existing [permission limitations](opencode-permissions.md) still apply. No paid-model behavior or independent acceptance is claimed by prompt-loading tests.

## Verification and evidence

The updated [native probe runner](../../scripts/verify_role_permissions.py) checks all five resolved prompts and read access to the rules in addition to the previous permission cases. It copies the rules into its synthetic workspace and binds both policy and rules SHA-256 hashes. File changes during verification invalidate the run.

Evidence for the E6 configuration is [the E6 permission/rules record](../verification/opencode-rules-probes-2026-11-25.json). The [E5 record](../verification/opencode-permission-probes-2026-11-25.json) is preserved as evidence for the earlier configuration hash, not claimed as verification of the updated configuration. The later [E7 record](../verification/project-covenant-probes-2026-11-25.json) covers the current policy plus covenant access. Reproduce with:

```sh
python scripts/verify_role_permissions.py --output /tmp/opencode-rules-probes.json
```

No business logic, dependency, CI job or required merge-check setting is changed by E6.

Version-specific references: [OpenCode V1 file-substitution implementation](https://github.com/anomalyco/opencode/blob/v1.19.5/packages/opencode/src/config/variable.ts) and [V1/V2 agent configuration names](https://opencode.ai/docs/migrate-v1/). Native executable validation is used for the pinned V1 setup.
