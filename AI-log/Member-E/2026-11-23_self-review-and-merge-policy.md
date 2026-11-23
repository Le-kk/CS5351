# Self-review and merge-policy change — 2026-11-23

## Original user request

请问现在的逻辑是不同的人来review和批准吗，能不能改成可以任意成员（包括自己）批准和合并

## Policy interpretation and boundaries

The user requested that all current team members may approve and merge their own work. The implementation explicitly allows test-plan and governance self-review for the confirmed roster, labels self versus peer review in schema-2 receipts, and preserves comment provenance, revision fingerprints, scope, timing and CI checks.

GitHub does not permit a PR author to submit a native approving Review on their own PR. The requested merge policy is therefore implemented by setting the mandatory native approving-review count to zero, not by fabricating a Review or granting administrative privileges to all members. Required status checks, PR use, strict up-to-date checking and other protections are retained. This intentionally removes the former independent-review guarantee; self-review must not be described as independent verification.

The repository-setting update and actual merge/verification are checked separately after the code tests pass. The earlier authorization to add the fifth `test approval` check applies only after positive/negative deployment verification. This record does not invent a test-plan approval, governance command or implementation self-review comment.

Changed artifacts include the verifier and reviewer policy, self-review/approval usage documents, current CI gate descriptions and this AI-use record. Tool calls/results, write payloads and internal reasoning are omitted.
