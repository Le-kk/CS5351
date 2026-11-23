# Team reviewer roster update — 2026-11-23

## Original user replies

能否给所有成员都加入审核权限，然后我来审核自己的

允许验证成功后新增第五个必需检查

## Public assistant clarification

可以把所有成员加入门禁的审批名单；他们目前已有仓库写权限，通常也就具备 PR Review 权限。

但加名单不能解决“审核自己的 PR”：GitHub 不允许作者对自己的 PR 提交 Approve，新门也单独禁止自我批准。我会核对权限并准备全员名单更新，保留自批限制。PR #11 的管理员合并授权仍未获得，因此暂不合并；你已授权的第五项必需检查，会在验证成功后再添加。

## Changes and boundaries

Updated both policy reviewer lists to include the five verified repository collaborators, and updated the approval archive documentation. GitHub account handles are used as supplied identities; no real names or A–D member mapping is invented. All five accounts already have push/write access, so repository access permissions are not changed.

The policy update is proposed in PR #11, not silently applied to the protected default branch. Self-approval remains prohibited. The earlier one-time administrator authorization for PR #9 is not reused for PR #11. Adding the fifth required check is authorized only after the positive/negative deployment verification succeeds.

Changed files in this task: the reviewer policy, approval README, and this AI-use record. Tool calls, edit payloads and internal reasoning are omitted. No human approval or receipt is fabricated.
