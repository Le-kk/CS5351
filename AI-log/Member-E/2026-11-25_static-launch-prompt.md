# Selected AI-use record — static launch instruction

Date: 2026-11-25. Role: E. Task: E8.

## Original user request

> 请完成E8**Root `Prompt.md` — Course-required; missing.\*\***
>   Define the static launch instruction: execution plan first, stop for human approval, then build and self-verification through the required human gates. Product runtime prompts are not a substitute.

## Public assistant reply

> 我会创建根目录的 `Prompt.md`，明确“先提交执行计划、等待人工批准，再实施和自验”的启动流程，并区分这类人工关卡与当前 GitHub 门禁，避免误启用已暂停的测试批准门。

## Work summary

Created the English root static launch instruction with plan-only inspection, H1 explicit execution-plan approval/stop, scoped implementation, conditional H2 material safety/scope decisions, self-verification and H3 human review/acceptance. Existing concrete authorization remains valid without repeated permission requests. Updated the root startup reference to the now-present file. No product runtime prompts or human-controlled operating rules were edited; no dependency, permission configuration, launcher, workflow, paid-model run or branch-protection change was made. Full write payloads/internal reasoning are omitted.

The document distinguishes prompted human checkpoints from automated enforcement. It does not fabricate earlier approvals, claim the launcher authenticates decisions, reinstate paused test pre-approval or add mandatory native peer Reviews. This task creates the requested launch artifact; it is not itself an invocation or approval of a future task plan.

## Observed verification

All local links and whitespace in Prompt.md and the updated AGENTS.md checked successfully. All three human checkpoints, the explicit planning stop and paused test-approval distinction are present. Existing native policy grants all five roles Prompt.md read access; no permission change was needed. This documentation-only change did not run behavior tests or claim a model followed the procedure.

Current file lengths (not added-line counts):

- `Prompt.md`: 63 lines.
- `AGENTS.md`: 86 lines.
