# Compact intermediate evidence experiment — 2026-11-25

## Selected original-language user request

> 请你尝试上述减少token的方法，尽量少改动现有架构

## Selected public assistant response

> 现有代码已经能给下游复用中间报告，所以先不加新的摘要模型或改变角色流程。我会让分析师在原来的一次调用中，用紧凑的“结论、证据、冲突、缺失数据”格式写报告，并缩短研究经理的重复解释。完整生成内容仍会保存，来源、日期、数值和风险提示优先于篇幅目标；新方案加独立开关，便于对照和回退。

## Changes and intervention

The user authorized a small implementation experiment and live verification. Added an opt-in writing-format instruction in seven application files, an environment/configuration switch and manifest records. Covered the separately invoked Sentiment Analyst after finding that it bypassed the earlier brevity helper. Added developer negative tests and demo confirmation/launcher support. Existing uncommitted demo work was preserved. No architecture owner approval or independent verification is fabricated. Full code/write/tool payloads and private reasoning are omitted.

## Actual evidence

Reference: docs/verification/compact-evidence-handoff-2026-11-25.md and tests/member_d_verification/evidence/compact-evidence-handoff-2026-11-25.json. Sequential real run_analysis_api measurements under NVDA/2026-11-24/all four analysts/one research and risk round/English/empty memory/school model/40-request cap/zero SDK retries: control 130,787; final candidates 96,160 and 95,023 total input+output tokens. Mean 95,591.5, 26.91% below control. All completed; Q1–Q4 PASSED is not semantic approval. Two preliminary results, 123,111 and 110,213, are retained separately. General application default remains off; demo explicitly enables the reversible switch. No new summary model, report truncation, requirement-budget adoption or GitHub deployment is claimed.

## Checks and limitations

New negative tests preserve source evidence, schemas, complete generated output and tool messages. Static/type/schema/workflow/security checks passed. Full regression count is recorded in the verification report. Data availability, model variability and free-text financial reasoning limitations remain; one control and two candidates do not establish a universal reduction. Existing and new user requests are preserved in their original language.
