# Handoff

## Current State

最新 workflow correction：用户明确指出两类流程错误已经重复出现，需要 durable guard。当前已固定两条规则：第一，在当前 PowerShell 环境下不要再用 `&&` 串联命令，顺序命令统一改用 `;` 或拆成独立 tool call；第二，长时验证命令如果先撞到 timeout，只能先报告为 `timed out / not yet verified`，然后单独放宽超时重跑或补验证，不能直接口头归类为失败。当前这两条是 workflow guard，不是产品功能变更，因此只记录在状态文件与决策日志中，不加到 `AGENTS.md` 里做案例化历史。

最新 v0.3 operator-summary / dashboard collector 接入：现有 collector 已经开始可选消费稳定导出的 operator summary，而不是只停在独立 export 脚本。当前 `skill_runtime.dashboard.collector.collect_dashboard_data(...)` 会在 `.skill_runtime/dashboard/operator-summary.json` 存在时读入 `operator_summary`；`collect_global_dashboard_data(...)` 会为每个已发现项目附带 `operator_summary_available`、`operator_summary_generated_at` 和三条 `operator_quality_gate_statuses` 元数据。当前仍然没有改 `skill_runtime/dashboard/render.py`、没有改 dashboard/global-dashboard 页面 HTML，也没有让页面直接依赖 full item lists 或底层散文件。collector 仍然只读取稳定字段，不执行 evaluator、不执行 host operation、不 promote、不 apply，也没有任何证据支持扩大 `default-in`。

最新本轮测试与边界：已先补定向失败测试，再落 collector 接入实现。当前新增快验覆盖三件事：本地 dashboard collector 在 export 存在时返回 `operator_summary`、export 缺失时返回 `None`、global collector 会为项目汇总附带 operator-summary availability/gate-status 元数据。当前这些测试已通过，且专门保持 dashboard 页面文件不变。针对本轮任务跑的 Codex runtime gate 结果仍是 `guarded-in / skipped`，原因是这类 collector/data 层产品化切片还不属于 phase-one `default-in` 家族；该观察样本也应保留在默认 lane 观察日志中。下一步需要完成状态文件更新、全量 gate 验证、commit + push。

最新 v0.3 product completeness 切片：已把 `operator-summary` 和现有 dashboard/global-dashboard 的关系往前推进一层，但仍停在 collector/data 层，没有改页面 UI。当前选择的是最小风险的 **方案 A**：新增 [docs/dashboard-operator-summary-integration-plan.md](/D:/02-Projects/vibe/docs/dashboard-operator-summary-integration-plan.md)、`skill_runtime.dashboard.collector.collect_dashboard_operator_summary_data(...)` / `export_dashboard_operator_summary_data(...)`，以及 `python scripts/export_operator_summary_for_dashboard.py --root .`。这条导出链会读取 `RuntimeService.operator_summary()`，仅保留稳定 contract 子集，并写到 `.skill_runtime/dashboard/operator-summary.json`，供未来 dashboard/operator workbench collector 消费。当前没有改 `skill_runtime/dashboard/render.py`、没有改 dashboard HTML 页面、没有改 `dashboard` / `global-dashboard` 命令输出结构。

最新导出 contract 边界：`.skill_runtime/dashboard/operator-summary.json` 当前只包含稳定字段子集：`generated_at`、`active_skills.count`、`staging_candidates.count`、`trajectories.count`、`recommended_host_operations.count`、三个 `quality_gates` 的 availability/report summary、`safe_next_steps`、`intentionally_not_automatic`、`missing_or_unavailable` 和 `non_automatic_explanation`。当前故意不把 full item lists 直接作为 dashboard 页面依赖，也不让 dashboard 直接读取不稳定低层文件 shape。导出链不执行 host operation、不运行 evaluator、不 promote、不 apply，也不会修改 `skill_store`；唯一写入是目标导出文件本身。当前仍然没有任何证据支持扩大 `default-in`。

最新验证结果：新增 dashboard/operator-summary export 定向测试已通过，覆盖 export 可运行、JSON 可解析、无 operator status 时保持 `unavailable`、fake operator status 时显示 `available`、不修改 `skill_store`、不执行 host operation、也不生成 dashboard HTML 页面。全量必需验证也已再次通过：`python scripts/check_mcp_architecture.py`、`python scripts/check_runtime_contracts.py`、`python -m unittest tests.test_runtime_fast -v`（当前为 202 tests OK）、`python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression`。当前三个 baseline 仍然全部通过。

最新 v0.3 product completeness 切片：`operator-summary` 已从“临时读取当前状态”推进到“有稳定 contract、且能读取本地持久化 gate status”的 Operator Workbench 数据源。现已新增 [docs/operator-summary-contract.md](/D:/02-Projects/vibe/docs/operator-summary-contract.md)，明确 v1 顶层字段、稳定字段、可 `unavailable` 的字段、未来 dashboard 如何消费、以及什么不会自动执行。当前 `operator-summary` 继续保持只读，不执行 host operation，不执行任何评估脚本，不 promote，不 apply evolution candidate，也不改 dashboard 页面。

最新本地 gate-status 持久化：`scripts/evaluate_provider_quality.py`、`scripts/evaluate_search_quality.py`、`scripts/evaluate_workflow_search_quality.py` 现在都支持可选 `--write-operator-status`，并可将结果写到 `.skill_runtime/operator_status/provider_quality.json`、`.skill_runtime/operator_status/search_quality.json`、`.skill_runtime/operator_status/workflow_search_quality.json`。默认行为不变：不带这个 flag 时，脚本仍然只输出原来的 JSON report，不写 operator status 文件，也不改 baseline JSON。写出的状态只包含 operator 侧需要的稳定摘要，例如 `status`、`generated_at`、`command`、`summary` 和 `baseline_comparison` 计数；不写入 `skill_store`。

最新主线已从 `v0.2 release readiness` 切到 `v0.3 product completeness`。当前第一条主线不是继续做 release tag / RC 包装，而是补一个最小但真实有用的 Operator Workbench summary。现已新增只读 CLI 命令 `python -m skill_runtime.cli --root . operator-summary`：默认输出 JSON，可选 `--format text`；当前能直接汇总 active skills、staging candidates、captured trajectories、recent runtime events、recommended host operations（若本地事件里存在）、recent audits、safe next steps，以及 `intentionally_not_automatic` 边界。当前实现明确不执行 host operation，不 promote，不 apply evolution candidate，也不改 runtime state。对于 provider/search/workflow baseline 状态，如果本地没有持久化评估报告，会诚实标记为 `unavailable`，不会伪造 pass。补充边界：当前仓库已经有 read-only dashboard / global-dashboard，这一轮不重做 dashboard；`operator-summary` 的定位应是未来 dashboard/operator workbench 的稳定数据源，现阶段只做最小接入点分析，不改 dashboard 页面。

最新 v0.3 产品判断：`v0.2.0rc1` 已经证明了 governed maintainer-workflow MVP 和 release-candidate 证据链，但没有解决“日常 operator 一眼看清当前 runtime 状态”的问题。为此已新增 `docs/v0.3-product-completeness-plan.md`，明确为什么暂停 release/tag 主线、v0.2 已证明什么、v0.2 没解决什么、为什么 Operator Workbench 是第一条主线，以及为什么这不构成扩大 `default-in` 的证据。README 只新增了一个很小的 `v0.3 Product Completeness Direction` 段落，把 `operator-summary` 暴露出来，并明确 `v0.2 RC` 只是阶段证据，不是最终产品完成。当前仍然没有任何证据支持扩大 `default-in`。

最新 v0.2 release candidate gate 主线：已完成整轮 RC 判断、最小 release 文档补齐、proof/baseline/test 验证和版本入口收口。当前新增 `docs/v0.2-release-candidate-checklist.md`；`CHANGELOG.md` 已新增 `v0.2.0-rc1` 条目；`pyproject.toml` 版本已从 `0.1.0` 收口到 `0.2.0rc1`，development status classifier 同步从 alpha 调整为 beta；README 只新增了 1 行 RC checklist 链接。当前结论是：在不改 ranking、不扩大 `default-in`、不新增 active skill、不自动 promote/apply、不扩 CLI recommendation scope、也不做 dashboard 大改的前提下，当前仓库已经可以称为 `v0.2.0rc1` release candidate。当前仍然没有任何证据支持扩大 `default-in`。

最新 RC gate 验证结果：`python scripts/check_mcp_architecture.py`、`python scripts/check_runtime_contracts.py`、`python -m unittest tests.test_runtime_fast -v`、`python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression`、`python scripts/run_v0_2_proof_bundle.py` 全部通过。proof bundle 仍然保持 governed boundary：有 recommendation、无自动 distill/promote/apply。当前 blocking gap 为无；non-blocking gaps 已固定到 `docs/v0.2-release-candidate-checklist.md`。

最新 v0.2 maintainer-facing proof bundle：已新增 `docs/v0.2-maintainer-proof-bundle.md`，并新增 `scripts/run_v0_2_proof_bundle.py` 把已验收的 maintainer path 收成一条可复现实例：`capture-trajectory --render-recommendation text` + `maintainer_review_cleanup` observed task + 三条 baseline gate。当前已把 proof artifacts 固定到 `docs/fixtures/v0.2-proof-bundle/`，包括 `stdout.capture-trajectory.json`、`stderr.capture-trajectory.txt` 和 `summary.capture-trajectory.json`。当前结论是：这套 bundle 已经能向外部读者证明项目的主价值是 maintainer workflow capture、governed follow-up recommendation、auditable JSON payload 和 explicit non-automatic boundary，而不是本地 utility script 执行。当前没有执行 `distill_trajectory`、没有 promote、没有 apply，也没有改 runtime decision、search ranking、workflow query 或 `default-in`。README 只做了最小链接更新，指向 proof bundle 文档。当前仍然没有任何证据支持扩大 `default-in`。

最新开发节奏记忆：后续默认切换为“较大步长的完整切片”。除非碰到高风险边界，否则单轮工作尽量一次完成：必要决策判断、最小但完整的实现、对应测试、相关文档/summary/runbook 更新、`HANDOFF.md / TASKS.md / DECISIONS.md` 状态更新、provider/search/workflow baseline gate 验证，以及 commit + push。默认不再把主线拆成“只做一个小文档、一个小验收点或一个很窄分析”的高频碎轮次。硬边界保持不变：不扩大 `default-in`、不自动 promote、不自动 apply evolution candidate、不把 expected gap 硬改成 pass、不把 lifecycle operation 包装成普通 active skill、不为了展示效果跳过 baseline、不做 dashboard 大改，除非已有明确 acceptance criteria。

最新 v0.2 release readiness / public positioning cleanup：已新增 `docs/v0.2-release-readiness-review.md`，并对 `README.md` 做了最小外部叙事收紧。当前结论是：README 顶层 maintainer/workflow/governed-learning 叙事已经基本正确，项目主价值仍然清楚是 `workflow skills + governed learning + auditable reuse`；唯一需要收口的是避免 `Distillation` 里的 rule registry 列表让新读者误读成“本地 utility script 工具箱”。本轮只加了一句 framing，明确这些 rule-based utilities 主要是本地 automation coverage / control examples，不是主 maintainer 价值故事；同时把 v0.2 三条 baseline gate 命令直接补进 README，降低 discoverability 成本。当前没有改 runtime、baseline JSON、ranking、workflow query、default-in 或 governed follow-up ownership，也仍然没有任何证据支持扩大 `default-in`。

最新 CLI recommendation adoption 决策：已新增 `docs/cli-recommendation-adoption-decision.md`，并对 README quick path 与 `docs/real-host-payload-rendering-runbook.md` 做了窄 adoption 更新。当前推荐是：可以正式把 `capture-trajectory --render-recommendation text` 写成 governed follow-up 的 operator path，但必须明确它仍然是 opt-in、仅限 `capture-trajectory`、text 走 `stderr`、JSON audit payload 仍在 `stdout`，而且不会执行 `recommended_host_operation`、不会 promote/apply。当前没有把这条能力扩到其他命令，也没有把它写成 dashboard feature 或 host UI adoption 完成。当前仍然没有任何证据支持扩大 `default-in`。

最新 CLI recommendation summary：已新增 `docs/cli-recommendation-presentation-summary.md`，并更新 `docs/v0.2-core-quality-summary.md`。当前结论是：`capture-trajectory --render-recommendation text` 已经是一个可接受的 CLI/operator surface，且对应 acceptance artifact、边界和副作用证据都已固定；但这还不是 README/runbook adoption 已完成的证明。下一步更应该判断是否要把它写成默认 operator path，而不是继续扩 flag 到其他命令、继续扩 presentation helper，或把它误写成 host UI 已收口。当前仍然没有任何证据支持扩大 `default-in`。

最新 CLI recommendation acceptance：已新增 `docs/cli-recommendation-presentation-acceptance.md`，并把真实命令的 `stdout` / `stderr` 固定到 `docs/fixtures/cli-recommendation-presentation/`。本轮真实命令是 `python -m skill_runtime.cli --root ./.tmp_cli_recommendation_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id cli_recommendation_demo --session-id cli_recommendation_demo --render-recommendation text`。结论是：`stdout` JSON audit payload 未变，`stderr` operator text 清楚显示 `Follow-up: Distill captured workflow`、`Recommended action: distill_trajectory` 和 `not automatic promotion` 边界；`.tmp_cli_recommendation_demo` 下只创建了 trajectory 文件，没有 `skill_store/staging` 或 `global-skills` 目录，因此没有执行 `recommended_host_operation`，也没有 promote/apply 副作用。当前 acceptance 没有暴露新的 CLI bug，不需要继续改逻辑。下一步更应该决定真实 host/operator 是否直接消费这条 CLI surface，而不是继续扩 CLI 或 dashboard。当前仍然没有任何证据支持扩大 `default-in`。

最新 CLI/operator text recommendation integration：已新增 `docs/cli-recommendation-presentation-integration-plan.md`，并在 `capture-trajectory` 上落了最小实现：显式传 `--render-recommendation text` 时，CLI 会把 operator-facing recommendation text 打到 `stderr`，同时保持原始 JSON audit payload 原样输出到 `stdout`。这条线没有改 runtime recommendation decision、没有改 JSON result shape、没有执行 `recommended_host_operation`，也没有引入自动 promote/apply。对应快验已补：默认输出仍是 JSON-only；显式 flag 时能看到 `Follow-up: Distill captured workflow` 和 `does not promote` 边界；staging 目录不变化，证明没有自动执行 distill。当前更应该验证真实 host/operator 是否直接采用这条 CLI surface，而不是继续扩 dashboard 或 presentation helper。当前仍然没有任何证据支持扩大 `default-in`。

最新 real host integration placement 决策：已新增 `docs/host-integration-placement-decision.md`。当前推荐的 first integration surface 是 CLI/operator text output，并保留原始 JSON payload 作为 audit companion；明确不是 dashboard first。原因是：当前证据已经证明 renderer、runbook 和真实 CLI payload flow 可用，但还没有证明 dashboard placement 或真实 UI ergonomics。当前 acceptance criteria 也已写清楚：operator 必须能看到 `recommended_next_action`、`recommended_host_operation.tool_name`、存在时的 `missing_inputs`、`requires_confirmation=true`、以及 `no automatic execution/promotion/apply` 边界；同时 raw `requires_confirmation=false` 不能被展示成允许自动运行，原始 JSON payload 仍要可审计。下一步更应该做 `operator flow acceptance criteria for dashboard/CLI integration` 或更窄的 real host integration plan。当前仍然没有任何证据支持扩大 `default-in`。

最新 host/operator validation 收口：已新增 `docs/host-operator-validation-summary.md`，把当前证据链收成一页：第一步是 `docs/host-integration-dogfood-report.md` 对 3 个 checked-in payload 做 fixture dogfood；第二步是 `docs/real-host-payload-rendering-runbook.md` 说明如何从真实 CLI 响应提取 inner payload 并用现有 renderer 渲染；第三步是 `docs/real-host-payload-rendering-report.md` 和 `docs/fixtures/real-host-payload-rendering/` 里真实跑通的 `capture-trajectory` 样例。当前结论是：这条线已经证明 current formatter / renderer / runbook 足以让 operator 理解受治理 follow-up 的下一步，但还没有证明真实 UI/host placement 已经正确，也没有证明应该继续靠新增样例推进。下一步更应该做 `real host integration decision: where should renderer output appear?` 或 `operator flow acceptance criteria for dashboard/CLI integration`。当前仍然没有任何证据支持扩大 `default-in`。

最新 real CLI payload validation：已按 `docs/real-host-payload-rendering-runbook.md` 真实跑通 `python -m skill_runtime.cli --root ./.tmp_real_payload_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id real_payload_demo --session-id real_payload_demo`，并把结果固定到 `docs/fixtures/real-host-payload-rendering/`。当前已保存 `raw-response.capture-trajectory.json`（保留外层 `status/data`）、`payload.capture-trajectory.json`（仅 inner `.data`）、`rendered.capture-trajectory.txt` 和 `rendered.capture-trajectory.json`（都由现有 renderer 生成），并新增 `docs/real-host-payload-rendering-report.md`。真实 command 确实产出了 `recommended_next_action=distill_trajectory`、`recommended_reason`、`recommended_host_operation.tool_name=distill_trajectory` 和 `available_host_operations`。当前 operator 能从 rendered 输出理解下一步是进入 staging distillation，而不是自动 promote；当前没有发现必须修改 helper 的阻塞歧义。仍然没有任何证据支持扩大 `default-in`。

最新 real host payload rendering runbook：已新增 `docs/real-host-payload-rendering-runbook.md`，把 checked-in fixture dogfood 推进一步，明确如何从当前 service/orchestration flow 拿到真实 recommendation payload 并通过现有 renderer 渲染。当前结论是：不需要新增 capture helper 脚本，因为 `python -m skill_runtime.cli` 已经会输出真实 JSON；真正需要补的是 operator-facing runbook，解释 CLI 外层 `status/data` envelope 与 renderer 需要的 inner payload object 之间的区别。当前 runbook 已写明：先把真实 CLI 响应保存为 `raw-response.json`，再提取 `.data` 为 `payload.json`，然后用 `python scripts/render_recommendation_presentation.py --input payload.json --format text|json` 渲染。`docs/host-integration-dogfood-report.md` 也已补 `Next validation target`，把下一步指向这个 runbook。当前仍然没有任何证据支持扩大 `default-in`。

最新 host integration dogfood / operator validation：已新增 `docs/host-integration-dogfood-plan.md`、`docs/fixtures/recommendation-payloads/`、`scripts/dogfood_recommendation_presentation.py` 和 `docs/host-integration-dogfood-report.md`。当前第一轮 dogfood 用 3 个 checked-in、service/orchestration-result-shaped payload 覆盖 `background_hint -> execute_skill with missing_inputs`、`new_skill_candidate -> distill_trajectory`、`improve_existing_skill_candidate -> review_evolution_candidate`。dogfood summary 结果是：operator 能从当前 card/text 输出理解下一步，且 `no automatic execution / no automatic promotion / no automatic apply` 边界仍然清楚；当前没有发现必须扩 helper 功能的阻塞歧义。最新验证已通过：`python scripts/check_mcp_architecture.py`、`python scripts/check_runtime_contracts.py`、`python -m unittest tests.test_runtime_fast -v`、`python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`、`python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression`、`python scripts/demo_recommendation_presentation.py`、`python scripts/dogfood_recommendation_presentation.py` 全部通过。当前仍然没有任何证据支持扩大 `default-in`。

最新 workflow-focused search baseline：已新增 `docs/workflow-search-quality-plan.md`、`docs/workflow-search-quality-baseline.json` 和 `scripts/evaluate_workflow_search_quality.py`，把 `v0.2-search-quality` 主线从 utility-heavy 对照重新拉回 maintainer workflow。当前 workflow evaluator 只导入 workflow-oriented active fixtures（如 `session_handoff_maintenance`、`pre_implementation_workflow_review`、`runtime_gate_workflow` 等），并把 query 明确分成 `should_match`、`expected_gap`、`should_not_match`。第一轮结果是：`handoff_continuation` 命中 `session_handoff_maintenance`，`pre_implementation_review` 命中 `pre_implementation_workflow_review`；`maintainer_review_cleanup` 和 `governed_learning_follow_up` 当前都保持 honest expected gap，没有 recommended workflow skill；utility 负例 `merge text files into markdown` 没有误命中 workflow skill。当前 workflow baseline 汇总为 `query_count=5`、`matched_count=2`、`expectation_met_count=5`、`positive_matched_count=2`、`expected_gap_confirmed_count=2`。这说明基础本地技能现在主要保留为测试夹具、执行 smoke 和现有 utility search baseline 对照组，不再作为项目主展示或主要价值证明。当前仍然没有任何证据支持扩大 `default-in`。

最新 search ranking diagnostics：已新增 `docs/search-ranking-diagnostics.md`，只分析当前固定 search baseline 的 `top_results / score / score_breakdown / why_matched / false neighbors`，不新增 query、不改检索算法、不调权重。当前结论是：negative queries 仍然没有推荐噪音；`alias boost` 在现有 baseline 下不显得过强；主要 false neighbors 都集中在 merge 查询，尤其是 `directory_text_cleanup_dogfood`，其次是 `json_to_csv_dogfood` 的弱邻近项，根因更像 broad metadata 而不是明显的权重失衡。当前更推荐下一步做 metadata 质量收紧，而不是马上调 ranking weights。baseline 结果仍然是 search `matched=7`、provider `matched=8`。当前仍然没有任何证据支持扩大 `default-in`。

最新 v0.2 search quality 收口：已新增 `docs/v0.2-search-quality-summary.md`，把当前 search baseline、alias recall 和 baseline comparison gate 收成一页。summary 明确记录：当前 gate 命令是 `python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`；当前 baseline comparison 结果为 `matched=7`、其余计数全 0；中文支持只来自显式 `search_aliases`，不是通用中文理解；当前没有 embedding、外部服务或 LLM retrieval。summary 也明确说明：这证明的是本地 retrieval-quality 行为已经可复现、可回归比较，不证明 semantic retrieval，也不证明应该扩大 `default-in`。当前仍然没有任何证据支持扩大 `default-in`。

最新 search quality baseline gate：已新增机器可读 baseline `docs/search-quality-baseline.json`，并让 `scripts/evaluate_search_quality.py` 支持 `--baseline` 与 `--fail-on-regression`。当前 search report 在提供 baseline 时会额外带 `baseline_comparison`，并区分 `matched / regressions / improvements / unexpected_failures / unexpected_passes / missing_queries / extra_queries`。当前 baseline 结果为 `matched=7`、其余计数全 0；`--fail-on-regression` 在当前 baseline 下返回 0。分类边界也已收紧：positive query 从 matched 变 unmatched 视为 regression，negative query 从无推荐变成有推荐视为 unexpected failure，query 消失视为 missing query。当前这只是本地可比较 retrieval-quality gate，不是 semantic retrieval，不是 default-in evidence，也没有任何证据支持扩大 `default-in`。

最新 search quality alias 支持：在不重写检索算法的前提下，已为本地 search 增加最小 metadata alias 召回能力。`skill_runtime/api/models.py` 中的 `SkillMetadata` 现在支持可选 `search_aliases`；`skill_runtime/retrieval/skill_index.py` 会把 aliases 纳入 searchable text 和轻量 score 计算，但不引入 embedding、外部搜索服务或复杂中文分词。当前 `merge_text_files` active metadata 已增加显式 aliases，包括 `合并 文本 文件 文档` 和 `把多个文本文件合并成一个文档`。`scripts/evaluate_search_quality.py` 也已更新：`chinese_merge_query` 从 known limitation failure 转为 expected pass，并新增中文负例 `发送邮件营销活动`。最新结果是 `query_count=7`、`matched_count=7`、`positive_matched_count=5/5`、`negative_matched_count=2/2`；中文正例现在可通过显式 alias 被召回，中文负例仍然没有 recommended skill。当前这只是 metadata-driven recall improvement，不是 semantic retrieval，不支持任意中文理解，也没有任何证据支持扩大 `default-in`。

最新 search quality baseline：已把主线切到本地可复现的 skill search/reuse baseline，并新增 `docs/v0.2-search-quality-plan.md` 与重写后的 `scripts/evaluate_search_quality.py`。当前脚本会在临时 runtime root 中导入一小组 active skill fixtures（`merge_text_files`、`json_to_csv_dogfood`、`session_handoff_maintenance`、`pre_implementation_workflow_review`、`directory_text_cleanup_dogfood`），再对固定 query set 跑 `RuntimeService.search`，输出结构化 JSON report。当前 baseline 已覆盖 exact English、fuzzy English、structured conversion、maintainer workflow、alias-driven Chinese positive 和中英文 negative no-strong-match 七类 query。最新结果是 `query_count=7`、`matched_count=7`、`positive_matched_count=5/5`、`negative_matched_count=2/2`。这次进展来自显式 metadata aliases，而不是检索算法重写；当前最大已知限制仍然是没有通用中文分词或 semantic retrieval，只能支持显式 aliases。当前这只是 search baseline + metadata-driven recall improvement，不是 dashboard 变更，不是 `default-in` 证据，也没有任何证据支持扩大 `default-in`。

最新 provider contract 收口：已把 `provider_guidance` 正式记录到 `docs/provider-integration.md` 的 fallback provider contract。当前 fallback request 字段明确为 `skill_name`、`summary`、`docstring`、`input_schema`、`provider_guidance`、`trajectory`、`prompt`。文档已明确：`provider_guidance` 是 structured guidance，同样内容也会嵌入 `prompt`；provider 可以直接读取 `provider_guidance`，也可以只消费 `prompt`；它不是放宽 audit、自动 promote 或绕过 maintainer judgment 的授权。对 `examples/providers/` 的兼容性也已确认：`copy_metadata_fallback_provider.py` 只读取 `summary`，会安全忽略新增字段；`review_cleanup_fallback_provider.py` 只要求 stdin 是合法 JSON，也会忽略新增字段；`deepseek_fallback_provider.py` 直接把整个 request 透传给模型，本地质量门禁针对生成 candidate 而不是固定 request schema，因此同样兼容。契约测试也已补成双重断言：fallback artifact 必须包含 `provider_guidance`，并且 prompt 中必须嵌入同一段 guidance。最新验证通过后，baseline comparison 仍是 `matched=8`、其余计数全 0，`review_cleanup_provider_quality` 仍然是 expected failure。当前仍然没有任何证据支持扩大 `default-in`。

最新 review cleanup provider guidance 接入：已把 gap analysis 里的最小 provider guidance 接到 fallback provider request 路径。当前 `skill_runtime/distill/fallback/service.py` 会为 fallback request 构造专门的 `provider_guidance`，并通过 `skill_runtime/distill/fallback/command_provider.py` 连同 prompt 一起发给 provider；同样的 guidance 也会嵌入 fallback prompt。本轮 guidance 强调生成可执行 workflow code、优先使用与 trajectory 对齐的 runtime tools（如 `tools.read_json` / `tools.write_text` / `tools.write_json`）、通过 kwargs 参数化输入输出路径、避免硬编码 demo artifact 名；对 review cleanup 还额外强调只写 cleanup plan artifact，不改源码、不自动 resolve review comments、不推断 merge approval、不绕过 maintainer judgment。当前这只增强 provider request 上下文，不放松 audit，不把 mock 负例强行改成 pass。针对 guidance 的回归测试已补齐，deterministic rule path 仍不走 fallback artifact；provider baseline gate 预期仍保持 `matched=8`，`review_cleanup_provider_quality` 仍应是 expected failure。当前仍然没有任何证据支持扩大 `default-in`。

最新 review cleanup provider fidelity gap 分析：已新增 `docs/review-cleanup-provider-gap-analysis.md`，只比较现有两个 fixture：`review_cleanup_provider_quality` 和 `review_cleanup_demo_provider_success`。当前结论很明确：负例不是生成崩溃，而是 mock fallback 生成了模板化 candidate，随后被 audit 以 `template-skill`、`artifact-overfit`、`provider-template-skill` 和 `provider-weak-runtime-alignment` 卡住；正例通过，是因为 `review_cleanup_fallback_provider` 直接补了真实 runtime tool 调用、输入校验、required/follow-up 分组和参数化产物写出。当前最小 provider guidance 应聚焦“生成可执行 cleanup plan workflow，而不是步骤摘要模板”，但仍不应自动改代码、自动 resolve review、自动决定 merge。最新验证已通过：`python scripts/check_mcp_architecture.py`、`python scripts/check_runtime_contracts.py`、`python -m unittest tests.test_runtime_fast -v` 和 `python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression` 全部通过；baseline comparison 仍是 `matched=8`、其余计数全 0。当前仍然没有任何证据支持扩大 `default-in`。

最新 v0.2 provider quality 收口：已新增 `docs/v0.2-provider-quality-summary.md`，把这一条主线的 completed capabilities、fidelity fixes、baseline gate、expected pass/failure、remaining gaps 和下一条推荐主线收成一页。当前 `skill_store/index.json` 的未暂存 diff 已确认只是本地 index rebuild / 序列化噪音：内容上只是给现有索引项补 `schema_source: null`，没有对应 active metadata 变化，也不代表真实 skill 更新，现已恢复为干净状态。最新验证也已完成：`python scripts/check_mcp_architecture.py`、`python scripts/check_runtime_contracts.py`、`python -m unittest tests.test_runtime_fast -v` 和 `python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression` 全部通过，baseline comparison 结果为 `matched=8`、其余计数全 0。当前仍然没有任何证据支持扩大 `default-in`。

最新 provider quality baseline gate：`docs/provider-quality-baseline.json` 已作为机器可读 baseline 落地，和 `docs/provider-quality-baseline.md` 放在一起。`scripts/evaluate_provider_quality.py` 现在支持 `--baseline PATH`，会继续输出完整 JSON report 并额外增加 `baseline_comparison`；`--fail-on-regression` 只在 regression、unexpected failure 或 missing fixture 时返回非 0。当前这仍是 provider-loop 质量门禁候选，不是 dashboard、不是扩大 `default-in` 的证据，也不会自动 promote 或 apply evolution candidate。

最新 dogfood 收口：已新增 `docs/host-follow-up-recommendation-dogfood.md`，用三条真实边界验证顶层 recommendation contract。当前已确认：缺输入的强匹配复用会停在 `background_hint`，但顶层直接给 `execute_skill`；`capture-trajectory` 顶层直接给 `distill_trajectory`；明确 existing-skill gap 的 finalizer 顶层直接给 `review_evolution_candidate`。这意味着宿主现在可以统一消费顶层 recommendation 字段，把嵌套 recommendation 只当 provenance。验证中还看到当前会话内 MCP 工具返回的结构可能没有立刻反映新字段，因此本轮结论以本地 CLI / 当前代码导入路径为准。

最新序列验收：已新增 `docs/host-follow-up-sequence-runbook.md`，并补 acceptance-style 快验，把 `background_hint -> distill_trajectory -> review_evolution_candidate` 收成一条 operator-facing sequence。当前结论是：这三类 follow-up 不只是散装能力，而是已经可以作为一条非自动、显式、可治理的宿主顺序链存在。快验已更新为 146 tests OK。

最新方向门判断：是否要在当前阶段继续做一个更窄的 host UI / CLI 展示层，结论是 `manual_validation_first`，已写入 `docs/host-follow-up-presentation-review.md`。当前不直接实现，因为顶层 recommendation contract、dogfood 和 sequence acceptance 已经足够让宿主先用起来；现在缺的不是又一个表面，而是确认 raw JSON + runbook 对真实 maintainer/operator 是否仍然不够顺手。

最新内部验证：已新增 `docs/host-follow-up-manual-validation-round-1.md`，用三条 maintainer-style 流做了第一轮人工验证。当前结论没有改变，仍然是 `manual_validation_first`，但现在有更具体的判断：对 `background_hint`、`distill_trajectory`、`review_evolution_candidate` 这三类 follow-up，raw JSON + runbook 已经至少可用，还没有出现足够强的 presentation 痛点来 justify 一个新展示层。

最新阶段完成：Stage 4 operator-facing recommendation contract 已收口。`AgentOrchestrationResult` 现在统一承载顶层 follow-up recommendation 字段：`recommended_next_action`、`recommended_reason`、`recommended_host_operation`、`available_host_operations`。当前 `background_hint` 会冒泡成顶层 `execute_skill`，`new_skill_candidate` 在 capture 后会冒泡成顶层 `distill_trajectory`，`improve_existing_skill_candidate` 在 candidate 创建后会冒泡成顶层 `review_evolution_candidate`。CLI 和 MCP 的 plan/result 重建层也已补齐这些字段，避免 recommendation 在宿主边界丢失。验证已通过：`python -m unittest tests.test_runtime_fast -v` 通过 145 tests OK，`git diff --check` 通过，新增回归测试覆盖 host、MCP 和 finalizer recommendation 透传。

最新战略目标：用户已明确希望把本项目朝“可申请 OpenAI Codex for Open Source / 开源支持”的方向推进。价值门判断：`manual_validation_first`，目标可以成立，但不能为了“免费会员”直接堆插件功能；更合理路线是把项目打磨成公开、可安装、可演示、对开源维护者有真实价值的 Codex workflow/plugin layer。官方页面当前强调 Codex for Open Source 面向关键开源软件维护者，申请需要公开 GitHub 用户和公开仓库，说明 primary/core maintainer 角色、仓库为什么重要，以及如何使用 API credits；入选维护者可获得 6 个月 ChatGPT Pro（含 Codex）、Codex Security 条件访问和 API credits。Codex open source fund 另一个入口偏 API credits，最高 $25,000。后续不要承诺一定能拿到免费会员，应先补齐公开仓库、README、license、安装/demo、真实 maintainer workflow 用例和 500 字申请材料。

最新阶段完成：Stage 2 项目定位和 README/application narrative 已完成。README / README.zh-CN / README.en 顶部已改成公开维护者价值叙事，不再先从内部 MCP/runtime 形态讲起。新增 `docs/codex-open-source-positioning.md`：一句话定位是 “Skill Runtime helps Codex-style agents capture, audit, reuse, and improve repeatable maintainer workflows.” 文档还记录了公开叙事、差异化、社区文件清单、review cleanup / release readiness / handoff continuation 三个 maintainer workflow demo 候选及成功标准、Codex for Open Source 申请文案草稿。下一阶段进入 Stage 3：做 demo maintainer workflows 和验证路径。

最新阶段完成：Stage 3 maintainer workflow demo set 已完成。当前有三个公开维护者 demo：`docs/maintainer-review-cleanup-demo.md`、`docs/maintainer-release-readiness-demo.md`、`docs/maintainer-handoff-continuation-demo.md`。它们分别覆盖 PR review cleanup、release readiness、handoff continuation。每个 demo 都有 `demo/maintainer_*` 下的本地 input fixture、expected output、observed_task record，并已用临时 runtime root 跑通 `capture-trajectory`；临时目录均已清理。README 和 DEMO.md 已链接这三个 demo。下一步进入 Stage 4：决定 packaging route，是 docs-first release、CLI package hardening，还是 Codex plugin path。

最新阶段完成：Stage 4 docs-first open-source readiness release 已完成。用户已接受 docs-first 路线；当前已新增 `CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`.env` ignore 规则、`docs/open-source-release-readiness-checklist.md` 和 `docs/codex-open-source-application-draft.md`，并更新 README、readiness audit、packaging decision、TASKS/DECISIONS/观察日志。下一步进入 Stage 5：用 application draft 收集最终提交所需用户信息；不要为了申请效果直接转入 Codex plugin path。

最新验证结果：Stage 4 文档收口后已运行 `git diff --check` 和 `python -m unittest tests.test_runtime_fast -v`；结果分别通过，快验 126 tests OK。Codex runtime gate 对本轮 docs-first 文档任务返回 `runtime_lane_status: skipped`，原因是文档申请准备不属于默认 runtime 接管的 workflow-like 任务；该样本已写入观察日志。

最新申请字段：用户确认 GitHub profile 是 `https://github.com/kioooice`，GitHub username 是 `kioooice`，repo URL 是 `https://github.com/kioooice/skill-runtime`，申请范围选择 Codex Security 和 API credits 两项都勾选，当前没有可声明的外部 traction。OpenAI organization ID 用户已在 OpenAI Platform organization settings 找到，但不要写入仓库文件或公开文档；只在申请表私下填写。

最新仓库发布状态：开源申请准备材料、个人简历产物删除、dashboard 技能详情文案润色均已提交并推送到 `origin/main`。当前 `main...origin/main` 同步，最新提交为 `9e9f0c7 Polish dashboard skill detail descriptions`，之前两次提交为 `10a5c2e Remove personal resume artifacts` 和 `b5cbb81 Prepare open source readiness materials`。当前公开树里已删除 `scripts/generate_resume_pdf.py`、`scripts/replace_project_section_in_resume.py`、`docs/skill-runtime-tiktok.pdf` 以及相关本地产物；注意这些文件曾经存在于旧提交历史中，如果用户要求彻底从历史移除，需要单独做 history rewrite / force push 风险评估。

最新申请和产品状态：用户已提交 OpenAI Codex for Open Source / Open Source Fund 表单，申请准备阶段收口。随后主线回到 dashboard 产品能力，已完成 `技能进化生命周期详情面板`：技能进化候选卡片现在可点击打开右侧详情抽屉，显示候选提案、审核结果、应用记录、回滚记录、来源任务、风险、原因、证据、建议修改和关联文件路径。该面板仍是静态 HTML 只读交互，不增加 promote/apply/rollback 等写操作。验证已通过：新增 TDD 回归测试先失败后通过，`python -m unittest tests.test_runtime_fast -v` 通过 127 tests OK，`git diff --check` 通过，`python -m skill_runtime.cli dashboard --output .skill_runtime\dashboard.html` 可生成本地页面。

最新触发日志修复：用户发现触发日志里 `已使用` 和 `进入观察` 变成 0。根因不是日志丢失，而是 dashboard 先按最近 N 条总记录截断，再统计状态；最近 skipped 记录过多时会把较早的 used / entered 挤出页面。当前已改为完整日志计数，并为 used / entered / skipped 各自保留最近样本。真实 dashboard 生成后显示 `已使用 17 / 进入观察 39 / 已跳过 105`，并且 HTML 中包含 used / entered 事件行。新增回归测试覆盖该场景，`python -m unittest tests.test_runtime_fast -v` 通过 129 tests OK。

最新治理快照解释优化：用户继续指出 `治理快照` 页面也看不懂，尤其是 `Missing skill directory: skill_store\rejected` 这种内部诊断。当前已把治理快照空状态和诊断文案改成人话：没有重复候选时会解释“当前没有需要合并处理的重复候选”，缺少 `skill_store\rejected` 时会明确说明“当前还没有已拒绝候选目录，这不是错误，暂时不需要处理”。新增回归测试覆盖这个场景，快验已更新为 130 tests OK。

最新触发日志文案收口：用户认为触发日志观感已经够用，不值得继续扩张大量交互。当前只做了最小解释优化，不新增详情抽屉：当 `used` 事件没有 `selected_skill_name` 时，处理方式显示为“运行时参与（记录经验）”；`entered` 显示为“运行时观察”；后续动作 `distill_trajectory` 和常见 host operation label 也改成中文说明。快验继续保持 130 tests OK。

最新主流程收口：用户要求回到更核心的机制和主流程，不再继续扩 dashboard。当前已新增 `docs/maintainer-mainline-acceptance.md`，把核心产品主线明确成一条 maintainer acceptance path，并选定 `handoff continuation` 作为第一条样板工作流。文档明确了什么时候才需要 `pre-implementation-workflow-review`、runtime gate 的职责、Codex 应产出的 continuation brief、finalizer 的受控学习结果，以及何时应优先产生 `improve_existing_skill_candidate` 而不是重复新技能。

最新主流程 runbook：已新增 `docs/maintainer-handoff-mainline-runbook.md`，用现有 handoff continuation demo 把第一条 maintainer mainline 写成可执行步骤。当前 runbook 已实际验证：demo JSON 输入可通过 `json.tool`，`capture-trajectory` 能在临时 runtime root 下产出 trajectory 并推荐 `distill_trajectory`；Codex-facing `codex-run` 对“continue from HANDOFF.md”这类请求当前会返回 `guarded-in` / `runtime_lane_status: skipped`，说明这条主线已经有明确的当前边界，而不是伪装成已经自动接管。

最新 handoff 边界固化：已补回归测试和文档，明确 `handoff continuation` 不是“一刀切升成 default-in”。当前规则是：显式 state-file 输入的结构化 continuation 继续属于 `default-in` / `project-state-maintenance`，而自然语言的 `continue from HANDOFF.md` 继续保持 `guarded-in`。这条边界已写入 `docs/codex-task-classification-boundary.md` 和 handoff mainline runbook，并由快验中的新增分类测试覆盖。

最新 handoff 主线验收：已新增 acceptance-style 快验，直接覆盖 maintainer handoff continuation 主线的三件事：expected continuation brief 必须是 maintainer-facing 结构、显式 state-file continuation 通过 `codex-classify` 保持 `default-in / project-state-maintenance`、`capture-trajectory` 只生成受控 trajectory 并推荐 `distill_trajectory`，不会越界成自动 promote。

最新 rollback 主线验收：已新增 acceptance-style 快验，直接覆盖 `candidate -> review -> apply -> rollback` 的审计闭环。当前 rollback 记录除了 `application_path` 外，还会直接保留 `review_path`，因此一条 rollback 记录本身就能追溯完整技能进化生命周期，不需要再从 application 记录间接回跳。

最新 evolution host 路径：`review_evolution_candidate`、`apply_evolution_candidate`、`rollback_evolution_candidate` 现在都返回统一的 host-facing recommendation。review 完成后会明确推荐显式 apply；apply 完成后会明确把 rollback 保留为下一步安全动作，并附带 governance refresh；rollback 完成后会明确推荐 governance refresh。当前 host 不需要再靠文档猜“下一步该点什么”。

最新 evolution 主线文档：已新增 `docs/evolution-lifecycle-acceptance.md` 和 `docs/evolution-lifecycle-runbook.md`。现在 skill evolution lifecycle 已经和 handoff mainline 一样，有 acceptance path、runbook、host follow-up 和 rollback audit chain，不再只是散落的 service / CLI / MCP 能力。

最新 evolution 主线 dogfood：已按 `docs/evolution-lifecycle-runbook.md` 在临时 runtime root 下真实跑通一条 BOM-backed skill file 场景的 `candidate -> review -> apply -> rollback`。这次 dogfood 暴露了 rollback 原先是“文本恢复”而不是“字节恢复”，会把 UTF-8 BOM 归一化掉，导致 `restored_content_hash` 和 apply 前原始 hash 不一致。当前已修复为：apply 阶段按原始字节写 backup，rollback 阶段按 backup 原始字节恢复目标文件，因此回滚不仅语义恢复，而且字节级恢复；真实 CLI dogfood 里 `application.previous_content_hash` 现在已经和 `rollback.restored_content_hash` 对齐。

最新 finalizer 边界收紧：`plan_learning` / `finalize_task` 现在不会因为 execution payload 里出现一个模糊的 `skill_gap` 字典就直接生成 `improve_existing_skill_candidate`。当前规则改成：只有当 existing-skill gap 信号同时带出明确 `evidence` 和 `proposed_changes` 时，才会进入 evolution candidate 主线；如果只是弱提示或泛泛的“可能要改”，学习决策会降级成 `observed_only`，只保留 trajectory，不创建 evolution candidate。这样可以避免“只因任务和某个技能相关就改那个技能”的误报。

最新 new-skill 学习边界：`plan_learning` 对 `new_skill_candidate` 也已经加了“具体产出信号”约束。当前不再因为一个 workflow 任务成功、带了 `expected_outputs` 就直接进入 distill；还必须满足两点：执行里存在成功写入类操作，且 `expected_outputs` 能被真实 artifacts / 写入路径覆盖。读操作任务、只说了预期输出但没真正写出来、或者输出路径和真实产物对不上的任务，现在都会降级成 `observed_only`。

最新 silent reuse 边界：`plan_reuse` 现在除了已有的强匹配、完整输入、scope 兼容之外，又补了一条输出对齐约束：如果请求声明了 `expected_outputs`，而这些输出和已知输出参数（如 `output_path`）对不上，就不再允许 `auto_execute`，而是降级成 `background_hint`。这让 silent reuse 不会在“请求说要产出 A，但输入其实指向 B”的情况下直接接管。scope 不兼容场景也已补成 acceptance-style 负例，确认会走 `background_hint` 而不是 `auto_execute`。

最新 learning matrix 文档：已新增 `docs/finalizer-learning-decision-matrix.md`，把 finalizer 侧四种学习结果 `skip / observed_only / new_skill_candidate / improve_existing_skill_candidate` 收成一张明确矩阵。当前主线已经不只是若干单测规则，而是有一份 operator-facing 文档说明为什么一个任务会进入观察、新技能候选或既有技能进化候选。

最新第二条 maintainer mainline：已选 `review cleanup` 作为第二条 maintainer-facing 主线，并新增 `docs/maintainer-review-cleanup-mainline-acceptance.md` 与 `docs/maintainer-review-cleanup-mainline-runbook.md`。当前真实边界已经验证：这类任务的 Codex-facing runtime gate 现在属于 `default-out / skipped`，原因是它仍由开放式评审判断主导；但 observed-task capture 路径成立，能够留下 trajectory 并推荐 `distill_trajectory`。这意味着项目现在不只证明了 `handoff continuation`，也证明了“保守 gate + 真实 maintainer workflow + governed learning artifact”这一类更开放的主线。

最新开源准备进展：用户确认采用 MIT。当前已新增 `LICENSE`，`pyproject.toml` 已补 license、author、project URLs、keywords 和 classifiers，README / README.zh-CN / README.en 已增加许可证说明。readiness audit 文档也已记录这项进展。剩余开源阻塞主要是 `CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、README 顶部公开叙事和 maintainer workflow demo。

最新阶段完成：Open Source readiness audit 已完成并写入 `docs/codex-open-source-readiness-audit.md`。结论：当前不适合直接申请。优势是仓库已公开、已有安装包元数据、CI、README、测试文档、隐私/provenance 文档和本地 demo；`LICENSE` 和基础 package metadata 已在审计后补齐；剩余主要阻塞是缺 `CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`，README 顶部还不是面向新维护者的 60 秒价值叙事，缺 2-3 个真实 maintainer workflow demo，公开 GitHub traction 当前很弱。下一阶段应做项目定位和 README/application narrative，不要先堆新插件功能。

最新全局技能新增：已新增全局 Codex skill `parallel-subagent-orchestration`，位置是 `C:\Users\Administrator\.codex\skills\parallel-subagent-orchestration\SKILL.md`。它用于复杂且可并行的任务：Codex 当前主线程默认作为主代理，负责目标、拆分、关键路径、审核、集成、验证和最终汇报；子代理只接收边界清晰、可并行、可审核的子任务。该技能明确不用于小任务、紧耦合阻塞调试、无法审核的外部副作用或未被用户/项目规则授权的子代理使用。项目和全局 `AGENTS.md` 只新增一行短路由，避免把完整流程复制进 AGENTS。

最新技能进化闭环：已完成 `skill evolution candidate` MVP、`review_evolution_candidate` 审核流程、确认后应用路径和确认后回滚路径。现在任务完成后的学习决策不再只有 `observed_only` 和 `new_skill_candidate`，当执行结果明确带出 `skill_gap` / `skill_improvement` / `evolution_candidate` 信号时，会生成 `improve_existing_skill_candidate`，把“改进已有技能”优先于“新建重复技能”。候选会落盘到 `.skill_runtime/evolution_candidates/*.json`，绑定目标技能、来源任务、证据、建议修改、风险等级和来源轨迹。`review_evolution_candidate` 已接入 RuntimeService、CLI 和 MCP：目标全局技能不存在时会 `rejected`，证据或建议不足时会 `needs_more_evidence`，证据足够时会写出 `.skill_runtime/evolution_reviews/*.review.json` 和 `.diff`，但不会修改全局 `SKILL.md`。`apply_evolution_candidate` 必须显式 `confirm_apply=true` / `--confirm-apply`，会校验 review 后目标 hash、写 `.skill_runtime/evolution_backups` 备份、写 `.skill_runtime/evolution_applications/*.apply.json` 应用记录，并把候选状态更新为 `applied`。`rollback_evolution_candidate` 现在也已接入 RuntimeService、CLI 和 MCP：必须显式 `confirm_rollback=true` / `--confirm-rollback`，只支持从 apply 记录里的 `restore_backup_file` 恢复；如果目标文件在 apply 后又被人工修改，会拒绝覆盖，并写 `.skill_runtime/evolution_rollbacks/*.rollback.json` 后把候选更新为 `rolled_back`。dashboard `技能进化` 页面状态标签支持待审核、已审核、需补证据、已应用和已回滚。下一步更适合进入版本收口，检查当前 diff 后提交这一批 workflow/global-skill 和 skill evolution 改造；如果继续功能开发，优先做 evolution 生命周期详情面板，而不是再扩 runtime 触发样本验证。

最新全局技能新增：已新增全局 Codex skill `plan-progress-tracker`，位置是 `C:\Users\Administrator\.codex\skills\plan-progress-tracker\SKILL.md`。它用于多阶段计划执行中的进度坐标维护：计划创建后、每个阶段开始/完成后、用户说“继续”时、自动模式阶段报告前、压缩恢复或会话接力时，都应明确当前是第几阶段、已完成什么、正在做什么、下一步是什么、是否偏离原计划。它已与 `auto-mode-stage-runner`、`nontechnical-stage-report`、`session-handoff-maintenance` 和 `context-compaction-audit` 联动，避免计划列完后用户只能不断回复“继续”却不知道推进到哪里。

最新全局技能新增：已新增全局 Codex skill `context-compaction-audit`，位置是 `C:\Users\Administrator\.codex\skills\context-compaction-audit\SKILL.md`。它用于每次上下文压缩或 summary-based resume 后做轻量审计：判断是否真的发生压缩、记录/推断压缩时间、在可行时估算压缩率、评估信息丢失风险，并给出 `continue_current_chat`、`checkpoint_then_continue`、`finish_stage_then_reopen` 或 `reopen_now` 建议。该技能明确不伪造精确 token 指标；没有原始 token 或 transcript baseline 时，会输出“无法可靠计算”或低置信估算。现在它已与 `session-handoff-maintenance` 联动：只要审计建议 checkpoint、完成当前阶段后新开、或立即新开，就先用会话接力技能刷新 `HANDOFF.md` / `TASKS.md` / `DECISIONS.md`，让新会话不依赖旧聊天记录。全局和当前项目 `AGENTS.md` 只保留短路由，避免把长规则塞回 AGENTS。

最新中央技能库收口：用户澄清不是不要功能组别，而是不要 `中央技能库` 和 `技能集合` 两套重复页面。当前已把功能组别收敛到 `中央技能库` 主页面：左侧只保留 `中央技能库` 入口，计数为 8 个 active workflow skills；页面内按 `方向与策略`、`自动推进`、`运行时与验证`、`会话接续` 四组展示。独立 `技能集合` 导航和页面已移除，基础本地技能仍保留在运行时/检索层，但不作为默认可视化内容展示。组内技能条目现在可点击打开详情抽屉，保持“按组浏览 + 点开看信息”的面板形态。已重新生成 `.skill_runtime/dashboard.html`，并检查 `output/playwright/dashboard-central-grouped-workflow-library.png`。

最新平台页压缩：按用户反馈，`平台与项目` 页面不再用大段说明卡展示平台技能。现在改成类似 `中央技能库` 的紧凑卡片：顶部是 skill 名和一行路径，中间是最多两行的摘要，下面用标签显示平台、全局权威/项目来源、外部/本地、只读来源，底部只保留一条来源根路径。`角色：...`、`来源：...` 这种展开式调试文案已从平台卡片中移除。已重新生成 `.skill_runtime/dashboard.html`，并检查 `output/playwright/dashboard-platforms-compact-cards.png`。

最新触发日志筛选：按用户要求，`触发日志` 页面已新增 `已使用 / 进入观察 / 已跳过` 三个状态筛选，并默认只显示 `已使用` 记录。每条事件卡片现在带 `data-event-status`，页面 section 带 `data-active-event-filter="used"`，因此即使只是打开静态 HTML，也会先看到 runtime 实际参与并复用技能的记录；点击 `进入观察` 或 `已跳过` 时再切换到对应事件。已重新生成 `.skill_runtime/dashboard.html`，并用 Playwright 确认默认可见事件状态只有 `used`，切换 `进入观察` 后可见事件状态只有 `entered`。

最新 dashboard 清理：按用户标注，`总览` 页已经去掉路径副标题和本页搜索栏，只保留全局顶部搜索；`中央技能库` 左侧计数现在只统计 active workflow skills，因此从 14 改为 8；全局 dashboard 不再单独显示 `全局日志` 导航，跨工作区事件合并到唯一的 `触发日志` 页面中。已重新生成 `.skill_runtime/dashboard.html`，并用截图确认总览页和侧栏状态。

最新集合页再收口：用户明确不想在可视化界面看到基础本地技能，因为它们对当前判断工作流价值没有意义。`能力集合` 页面现在只展示 8 个 active workflow skills，并按功能分成 4 组：`方向与策略`、`自动推进`、`运行时与验证`、`会话接续`。`基础本地技能`、`文本处理`、`格式转换`、`文件整理` 不再作为默认 dashboard 集合显示；底层 basic skill 数据仍保留给运行时和显式检索，不作为用户主界面内容。

最新触发日志可读性调整：`触发日志` 页面不再直接展示英文 task description 和 runtime lane reason。事件卡片现在用中文结构显示 `任务`、`时间`、`处理方式` 和 `结果`，并把常见内部原因翻译为“Codex 直接处理，运行时没有接管”“本地可复用任务，但不属于当前默认接管范围”等用户可理解表述。已重新生成 dashboard，并检查 `output/playwright/dashboard-trigger-log-localized.png`。

最新只读交互面板：已开始把静态 dashboard 升级成真正可点击的面板，但仍不涉及 promote、reject、edit、archive 等写操作。新增 `docs/runtime-readonly-panel-plan.md` 明确第一阶段只做“中央技能库卡片 -> 右侧技能详情抽屉”。当前技能卡片已经可以点击，右侧抽屉展示名称、原始 skill 名、状态、复用次数、来源轨迹、分类来源、完整说明和外部导入来源信息；关闭抽屉不会改变视图或 runtime 状态。按用户反馈，界面里的“只读视图 / 只读详情 / 只读链接 / read_only”提示已经移除，说明区域改为使用 `summary + docstring` 形成完整段落。

最新总览页优化：`总览` 页面已从“观察面板”口径改为“运行时总览”口径，标题说明、只读说明和指标卡文案都更偏用户可理解的产品语言。当前项目与跨工作区两组指标不再使用“标签 - 说明”结构，而是改成数字、指标名、短说明三层；“运行时参与 / 进入观察 / 普通路径”分别表达完成参与、进入但未接管、Codex 直接处理。小节说明现在跟随标题左对齐，避免说明文字漂到右侧造成阅读断裂。

最新集合页调整：`能力集合` 页面已从 workflow-first 进一步收口为 workflow-only。默认集合只保留工作流功能组，不再显示基础本地技能分区；候选技能数量和候选列表项已从默认 dashboard 展示中隐藏，只保留活跃工作流技能；候选数据仍在 staging/governance 路径里，不做删除。左侧导航也修正为靠上排列，避免选中项被侧栏高度拉成大块。全局说明和“搜索当前视图”现在只在 `总览` 页显示；其他页面顶部原位置只显示当前页面标题和说明。

最新 UI 改造：用户明确否定了上一版 dashboard 视觉，要求按 `https://github.com/iamzhihuix/skills-manage` 的界面重做。当前已克隆参考项目到本地 `.skill_runtime/reference/skills-manage` 供对照，并参考其截图/源码把 dashboard 静态 HTML 改成桌面管理应用壳：mac 风格顶部栏、全局搜索、左侧导航、内容标题区、当前视图搜索、两列技能卡片、Catppuccin Latte 风格配色和紫色选中态。旧的 radial-tree / tree-fan / branch-map 默认结构已从当前渲染与测试中移除。默认页仍是工作流技能主视图，基础 helpers 仍在 `基础本地技能` 集合。

最新可视化收口：用户不需要在默认技能树里看到普通本地文件处理技能，只想看 workflow skills。当前 dashboard collector 已给技能增加 `skill_surface`，renderer 默认只展示 `workflow` 技能；`merge_text_files`、JSON 转 CSV、文本替换、目录清理等普通 helpers 被归入内置 `basic-skills` / `基础本地技能` 能力集合，不删除、不丢失，但不再占用工作流主视图。相关快验已覆盖 workflow skill 保持可见、basic skill 从默认树移出、基础集合仍可访问。

最新语义纠正：用户澄清 `workflow-error-correction` 不应该只是记录工具，而是要让 Codex 以后少犯同类错误。当前已把全局 `workflow-error-correction` 改成已知错误防复发 guard：主要产物是“改变下一步行为”，不是更好的错误日志。它现在在 AGENTS 编辑、runtime 验证循环、方向未审先实现、重复纠错、auto-mode 漂移、AGENTS 膨胀等风险场景下，要求先应用已知 guard；只有新错误模式才新增记录。

最新错误修正规则：用户进一步澄清，已有错误记录后不应该继续等用户指出同一个错误；只有新问题才需要新记录。当前已升级全局 `workflow-error-correction` 为 prevention-first：执行时先查 `HANDOFF.md`、`TASKS.md`、`DECISIONS.md`、相关专门文档和全局 workflow skills 中的既有纠错；如果匹配，就直接应用预防规则并说明复用了旧纠错；只有新模式、范围明显扩大或缺少可用预防规则时才新增记录。

最新流程纠错：用户指出刚才不应该把具体路线纠正继续加进 `AGENTS.md`。这个判断成立。当前已新增全局权威技能 `C:\Users\Administrator\.codex\skills\workflow-error-correction\SKILL.md`，用于记录重复流程错误、路线漂移、AGENTS 膨胀、validation theater 等问题；项目和全局 `AGENTS.md` 已删除两条具体 runtime-validation-loop 事故规则，只保留“保持 AGENTS 轻量、错误记录走 workflow-error-correction”的短规则和路由。后续用户指出类似错误时，不要再把完整事故写进 AGENTS，而是用该技能记录到 `DECISIONS.md`、`TASKS.md`、`HANDOFF.md` 或合适的专门文档。

最新主线改造：用户要求先把“开发前方向审核工作流”做成真正可用的主流程。当前已升级全局权威技能 `C:\Users\Administrator\.codex\skills\pre-implementation-workflow-review\SKILL.md`，它现在不是普通 checklist，而是实现前的 build gate：只有 `build_now` 允许同一流程进入实现；`manual_validation_first`、`revise_direction`、`do_not_build_now` 都必须先验证、改路线或停止。项目 `AGENTS.md` 和全局 `C:\Users\Administrator\.codex\AGENTS.md` 已同步该口径。新增快验覆盖全局 skill 必须包含主流程护栏、最小闭环验证和 runtime-loop guardrail。后续新开发方向必须先走这个工作流，不要直接转回 runtime/sample/dashboard 验证。

最新路线纠偏：用户指出“继续验证 default lane 样本不够多”已经有滑回旧问题的风险，也就是不断验证本地技能、继续加技能、继续收集触发样本，却没有推进项目真实价值。这个判断成立。后续必须把主线锁回“开发前方向审核 / 防止无意义开发”。Skill Runtime、local skills、`entered / used` 样本、dashboard 事件和 trigger validation 都只能作为底层工具，不能再成为默认开发目标。项目 `AGENTS.md` 和全局 `C:\Users\Administrator\.codex\AGENTS.md` 已新增硬性规则：如果工作开始漂移到“证明 runtime 能跑”的循环，必须停下来回到 development-direction value gate。下一步优先 dogfood 和强化 `pre_implementation_workflow_review`，不是继续扩 runtime 验证面。本次记录 finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/record_route_correction_stop_repeating_local_ski_20260503093009.json`。

最新一轮回应用户指出的关键问题：此前 dashboard 里真实开发任务几乎全部是 `skipped`，而 phase-one `default-in` 的低风险文件任务在日常 Codex 开发中价值不高。当前已新增 `development-workflow-observation` Codex 默认通道家族：当任务有明确工作区、明确产物，并且属于代码、测试、dashboard、文档或配置类开发工作流时，会进入 `default-in`，但仍建议对这类广义开发任务传 `allow_silent_reuse=false`，让 runtime 参与检索、观察和收尾学习，而不是静默自动执行。dashboard 总览也新增 `已进入` 指标，用来区分“runtime 已观察但未自动执行”和“完全跳过”。本轮实际本地 API gate 已从变更前的 `runtime_lane_status: skipped` 改成变更后的 `runtime_lane_status: entered`，finalizer 已产生 `runtime_lane_status: used` 和 captured trajectory。新 Codex 会话里的 app 级 MCP 连接已复测通过：`mcp__skill_runtime__.run_codex_task_experimental` 对明确工作区和明确输出的仓库状态维护工作流返回 `task_classification.bucket: default-in` 和 `runtime_lane_status: entered`。随后按用户反馈新增并升级 `pre_implementation_workflow_review` active skill 和 `AGENTS.md` 规则，把“开发方向是否正确、有无价值、是否值得继续做”的判断放到实现前。最新一轮又将 `AGENTS.md` 从长操作手册收成短规则和 workflow skill 路由，自动模式、部署判断、session handoff、runtime gate、验证选择、仓库影响分析和非技术阶段报告都已下沉为 active runtime workflow skills，并同步安装为全局 Codex skills，供新会话和其他项目直接触发。当前原则已经明确：通用工作流技能的唯一权威来源是全局 Codex skills，项目内只保留路由、局部约束、索引或薄适配。

已完成一轮 Skill Runtime 产品化收敛，也已证明核心闭环 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 在本地 MVP 中真实存在。当前阶段的主要问题已经不是“底层零件有没有”，而是“Codex 默认执行任务时会不会自动用上这层”。此前 agent-first runtime 已完成一轮阶段性收口：静默自动复用、失败时不越界、任务完成后 capture trajectory 并给出 recommendation，这一层现在停在 `capture + recommendation`，不默认继续自动 `distill/promote`。新的主线已切到 Codex 默认接入：不是一次性把 Skill Runtime 全量挂到所有 Codex 任务上，而是先采用受控低风险任务通道。现在除了分类文档、host API、MCP 实验入口和 Codex CLI 默认通道以外，phase-one `default-in` 还进一步收窄成四类白名单家族：

- `project-state-maintenance`
- `local-text-transformation`
- `structured-format-conversion`
- `low-risk-workspace-organization`
- `development-workflow-observation`

当前已经具备三种 Codex 接入层次：

- host API
- MCP 实验入口
- CLI 默认通道

并且都遵守同一套 `default-in / guarded-in / default-out` 分流规则，且 `default-in` 已经不是宽泛条件，而是小范围白名单。现在第一处现有入口也已经正式切过去：

- `agent-plan`
- `agent-plan-learning`

它们默认走 Codex 默认通道，而不再直接走旧的纯 agent lifecycle helper。当前阶段已从“是否让某个现有入口正式改走 Codex 默认通道”推进到“要不要继续切第二处现有入口，还是先做更大范围验证”。
它们默认走 Codex 默认通道，而不再直接走旧的纯 agent lifecycle helper。并且这一轮更大范围验证也已经通过：

- `python scripts/check_mcp_architecture.py`
- `python scripts/check_runtime_contracts.py`
- `python -m skill_runtime.cli codex-run ...`
- `python -m skill_runtime.cli agent-plan --task-description "Review this architecture and decide the roadmap."`

当前阶段已从“要不要先做更大范围验证”推进到“第一处现有入口已经完成阶段性验证点收口，并进入观察期”。在此基础上，`skill_runtime` 也已经进一步上收成 Codex 全局默认背景能力：全局规则已改为优先采用 runtime lane，全局 `skill_runtime` MCP 启动也不再写死在 `D:/02-Projects/vibe`，而会优先把当前工作区识别为 runtime root。默认不再继续马上切第二处现有入口，除非后续真实使用明确暴露出需要扩大默认通道覆盖面的价值。

同时，仓库主说明已经完成一轮口径切换：现在不再把这套系统主要描述成 “MCP 工具集”，而是描述成 “Codex 下方的背景能力层”；MCP、CLI 和脚本保留为接口层和传输层。

另外，仓库根入口也已切成中文默认：

- `README.md` 现在作为中文主入口
- `README.en.md` 保留英文版

最新一轮已补上 Codex 默认通道的触发可见性：Codex-facing orchestration 结果现在会返回 `runtime_lane_status` 和 `runtime_lane_reason`，用于说明本次任务是实际使用了 runtime lane、只是进入判断、还是被跳过留在普通 Codex 路径。这解决了“在其他项目里没感觉到它存在时如何判断是否触发”的问题。

用户随后提出希望做一个能看技能树和触发日志的可视化界面。当前已将第一版收窄为“只读观察面板”，不做完整后台、不做 skill 编辑、不做 promote/archive 操作。设计文档已写入 `docs/superpowers/specs/2026-05-01-runtime-observability-dashboard-design.md`。

用户已批准该设计进入实现计划阶段。当前实现计划已写入 `docs/superpowers/plans/2026-05-01-runtime-observability-dashboard.md`，计划拆成事件日志、host 接入、dashboard 数据收集、HTML 渲染、CLI 入口和最终验证六个任务。

当前实现也已经完成：`python -m skill_runtime.cli dashboard --output .skill_runtime/dashboard.html` 可以生成本地只读观察面板。页面展示总览、技能树视图、触发日志视图和治理快照。Codex-facing runtime lane 入口现在会把 `used / entered / skipped` 事件写入 `.skill_runtime/runtime_lane_events.jsonl`。最新一轮根据用户反馈，已把 Skill Tree 从单列长列表改成中心向四周发散的径向布局：运行时根节点在中心，active / staging / archived / rejected 四个状态分支分布在四个象限；分支内第一层展示能力组别，例如格式转换、文本处理、文件整理和运行时治理；中心节点已放到上下分支之间，避免压到组别卡片；点击组别时，组内技能会在居中凸显的详情界面中展开，页面不自动滚动，也不再把树枝撑长；同时去掉交叉连接线和硬分界线，改用位置、状态圆点和组别卡片表达结构。随后又把 Trigger Log 和治理快照都改成独立页面式视图，顶部导航不再用同页锚点滚动；点击触发日志只显示日志页，点击治理快照只显示库健康页。dashboard CLI 现在还支持 `--open`，可一键生成并用系统默认浏览器打开本地面板。现在又新增全局只读 dashboard，并已按用户反馈与普通 dashboard 合并：`python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open` 仍然显示当前项目技能树、当前项目触发日志、当前项目治理快照，同时增加“全局项目”和“全局日志”两页，用来查看其他工作区是否触发过 Skill Runtime。固定界面文案、技能名称和技能说明已经中文显示；内部执行、检索和索引仍使用原始英文 `skill_name`。当前还把全局和项目 `AGENTS.md` 规则加严：具体项目开发任务在实质性读代码或改动前必须先调用 Codex-facing runtime gate，优先走 `run_codex_task_experimental`，必要时用 CLI `codex-run` 兜底产生 dashboard 可见事件；任务完成后如有结构化执行结果，再调用 `finalize_codex_task_experimental`。本轮继续主线时，MCP `run_codex_task_experimental` 和 `finalize_codex_task_experimental` 都已确认会返回 `runtime_lane_status: skipped`，并把对应事件写入 `.skill_runtime/runtime_lane_events.jsonl`，说明 dashboard 可见触发链路已经覆盖 MCP start gate 和 finalizer 路径。用户随后确认其他项目目前也可以正常调用 Skill Runtime，因此观察期已从“是否能跨项目触发”推进到“跨项目触发是否稳定、是否产生有价值的 `entered` / `used` 样本”。用户又指出 `iamzhihuix/skills-manage` 与本项目相似。当前结论是：`skills-manage` 更像跨平台 skill asset manager / control plane，本项目更像 runtime lane / learning engine。已新增方案 `docs/superpowers/plans/2026-05-03-skills-manage-lessons-integration.md`，建议吸收中央技能库、平台 inventory、导出计划、import-to-staging、collections、隐私和 provenance 表达等外围经验，但不改变“创造、蒸馏、进化、治理”的主线。当前已完成第一阶段 read-only 平台/项目 inventory：新增平台目录注册表、只读 `SKILL.md` 发现器、dashboard `平台与项目` 视图和 `docs/platform-skill-inventory-design.md`。该阶段不创建目录、不复制、不 symlink、不安装。第二阶段 `platform-export-plan` 也已完成：新增导出预览策略文档、只读导出计划模块和 CLI 命令，能预览 active skill 暴露到平台目录时的目标路径、copy/symlink 计划和冲突，不执行任何写操作。

GitNexus 当前结论：之前“一直没效果”不是因为没安装，也不是仓库没索引，而是查询路径在 Windows 上加载 LadybugDB FTS/VECTOR 扩展时触发 native crash。这个 crash 会把 MCP transport 直接带断，所以 Codex 里表现为 `Transport closed`。本机已在全局安装的 GitNexus 包里增加临时补丁：查询池不再加载 FTS/VECTOR，BM25 搜索在 Windows 下退回较慢的 `CONTAINS` 扫描；当前仓库索引已在 2026-05-03 重新运行 `gitnexus analyze`，更新到提交 `c9f2c2c`，CLI 的 `status` / `cypher` / `query` / `context RuntimeService` 已验证可用。搜索排序仍低于正常 FTS/vector 路径，复杂影响分析优先用 `cypher` 或 `context`。

## Last Completed

本轮已完成：
- 全局计划进度跟踪技能：
  - 新增 `C:\Users\Administrator\.codex\skills\plan-progress-tracker\SKILL.md`
  - 新增 `agents/openai.yaml`
  - 全局和项目 `AGENTS.md` 增加短路由
  - 技能输出固定包含计划名、阶段坐标、已完成、当前状态、下一步、偏离风险和是否需要用户决定
  - 已与 `auto-mode-stage-runner`、`nontechnical-stage-report`、`session-handoff-maintenance` 和 `context-compaction-audit` 联动
- 全局上下文压缩审计技能：
  - 新增 `C:\Users\Administrator\.codex\skills\context-compaction-audit\SKILL.md`
  - 新增 `agents/openai.yaml`
  - 全局和项目 `AGENTS.md` 增加短路由
  - 技能输出会区分精确、估算和不可用的压缩指标
  - 技能会根据目标清晰度、缺失上下文、diff 范围、测试状态和 handoff 新鲜度建议是否新开会话
  - 已与 `session-handoff-maintenance` 双向联动：压缩审计做继续/新开判断，会话接力负责写清新会话入口
  - 已通过 `quick_validate.py`
  - `python -m unittest tests.test_runtime_fast -v` 通过，110 tests OK
- dashboard 中央技能库信息架构收口：
  - 移除重复的 `技能集合` 导航、header 和页面 route
  - `中央技能库` 现在直接承载工作流功能组
  - 8 个 active workflow skills 按 `方向与策略`、`自动推进`、`运行时与验证`、`会话接续` 展示
  - 基础本地技能不再进入默认可视化主界面
  - 组内技能条目新增详情抽屉触发数据，点击可查看完整说明和来源信息
  - 已重新生成 `.skill_runtime/dashboard.html`
  - 已生成并检查 `output/playwright/dashboard-central-grouped-workflow-library.png`
  - `python -m unittest tests.test_runtime_fast -v` 通过，110 tests OK
  - `git diff --check` 通过
- dashboard 平台页压缩：
  - `平台与项目` 页面从展开式 `project-card` 改为 `platform-skill-card`
  - 平台卡片新增 `platform-card-grid`、`platform-card-head`、`platform-summary` 和 `platform-path-chip`
  - 长说明通过卡片样式截断为摘要，路径单行省略
  - `authoritative_global_skill` 显示为 `全局权威`，`external` 显示为 `外部`，`read_only` 显示为 `只读来源`
  - 移除平台卡片里的 `角色：...` 和 `来源：...` 前缀式长文本
  - 已生成并检查 `output/playwright/dashboard-platforms-compact-cards.png`
  - 新增平台页紧凑卡片回归测试，完整 fast suite 110 tests OK
- dashboard 触发日志状态筛选：
  - `触发日志` 页面新增 `已使用 / 进入观察 / 已跳过` 三个筛选按钮
  - 默认筛选为 `已使用`，首屏只显示 runtime 实际参与并复用技能的记录
  - 每条事件卡片新增 `data-event-status`，静态 CSS 与 JS 点击切换共用同一状态字段
  - 无对应状态记录时会显示中文空状态提示
  - 已重新生成 `.skill_runtime/dashboard.html`
  - 已生成并检查 `output/playwright/dashboard-trigger-log-status-filter.png`
  - Playwright 验证默认可见状态为 `used`，点击 `进入观察` 后可见状态为 `entered`
  - 目标 dashboard 测试、Python 编译检查、完整 fast suite 均通过
- dashboard 总览与导航清理：
  - `总览` 页去掉路径副标题和本页搜索栏，避免页面上出现被标注的多余说明线和长搜索条
  - 左侧 `中央技能库` 计数改为 active workflow skills 数量，当前为 8
  - 全局 dashboard 只保留一个日志入口：`触发日志`；跨工作区事件在该页面中合并展示
  - 已重新生成 `.skill_runtime/dashboard.html`
  - 已生成并检查 `output/playwright/dashboard-overview-cleaned.png` 和 `output/playwright/dashboard-sidebar-workflow-count.png`
  - 目标 dashboard 测试、Python 编译检查、完整 fast suite 均通过
- dashboard 集合页 workflow-only 调整：
  - 默认能力集合从“工作流在前、基础本地在后”改为只显示工作流集合
  - 8 个 workflow skills 分成功能组：方向与策略 3 个、自动推进 2 个、运行时与验证 2 个、会话接续 1 个
  - `基础本地技能`、`文本处理`、`格式转换`、`文件整理` 不再出现在默认 dashboard 集合页
  - 中央技能库不再显示“基础本地技能集合”说明
  - 已生成并检查 `output/playwright/dashboard-workflow-collections-only.png`
- dashboard 触发日志中文化：
  - 事件卡片改为 `任务 / 时间 / 处理方式 / 结果` 结构
  - 常见英文任务描述和 runtime reason 映射为中文
  - 不再直接向用户显示 `task bucket guarded-in skipped...` 这类内部原因文本
  - 已生成并检查 `output/playwright/dashboard-trigger-log-localized.png`
- 只读交互面板第一阶段：
  - 新增 `docs/runtime-readonly-panel-plan.md`
  - 中央技能库技能卡片现在可点击
  - 新增右侧技能详情抽屉
  - 抽屉展示技能基础信息、完整说明、来源轨迹数量和分类来源
  - 外部导入技能可在详情里显示 provenance 文本
  - 移除 dashboard 可见的“只读”提示，包括卡片底部、抽屉标题和总览标题区
  - workflow adapter 的详情说明会合并 `docstring`，解释全局权威 skill 与项目薄适配层的关系
  - 前端只使用静态 HTML `data-*` 字段和 `textContent`，不做任何写操作
  - 已生成并检查 `output/playwright/dashboard-skill-detail-drawer-no-readonly.png`
  - `python -m unittest tests.test_runtime_fast -v` 通过，109 tests OK
  - `git diff --check` 通过
- 总览页文案与排版优化：
  - 页面标题改为 `全局运行时总览` / `运行时总览`
  - 总览指标卡改成数字、指标名、短说明三层结构
  - `runtime 参与` 改为 `运行时参与`
  - 当前项目与跨工作区说明改为标题下左对齐
  - 重新生成 `.skill_runtime/dashboard.html`
  - 已生成并检查 `output/playwright/dashboard-overview-copy-layout.png`
  - 目标 dashboard 测试、Python 编译检查通过
- 技能集合 workflow-first 调整：
  - 默认集合顺序先改为工作流集合在前，随后按用户反馈收口为 workflow-only
  - `能力集合` 页面只展示工作流技能功能组
  - `基础本地技能`、`文本处理`、`格式转换`、`文件整理` 不再出现在默认 dashboard 集合页
  - 默认 dashboard 不再显示候选技能数量和候选列表项，只显示活跃技能
  - 全局说明和当前视图搜索框只保留在 `总览` 页
  - 其他页面顶部原位置改为当前页面标题
  - 修正左侧导航被拉伸的问题
  - 已生成 `output/playwright/dashboard-collections-no-candidate-noise.png` 并检查
  - 目标测试、语法检查通过
- skills-manage 风格 dashboard 重做：
  - 静态 dashboard 改成桌面应用壳，而不是旧放射树
  - 顶部标题栏、全局搜索、左侧导航、内容标题、当前视图搜索和两列技能卡片已落地
  - workflow skill 名称和说明补充中文展示
  - Playwright 已生成并检查桌面和移动截图
  - 旧 radial tree 断言已替换为 app-shell 断言
- dashboard 默认工作流视图收口：
  - 技能 payload 新增 `skill_surface`
  - 默认技能树只展示 workflow skills
  - 普通本地 helpers 移入 `基础本地技能` 能力集合
  - imported/global workflow candidates 保持在默认树可见
  - `python -m unittest tests.test_runtime_fast -v` 通过，106 tests OK
  - `git diff --check` 通过
- 已知错误防复发 guard：
  - `workflow-error-correction` 不再以记录为主要目标
  - 明确主要产物是减少重复错误
  - 增加 AGENTS 编辑、runtime 验证循环、方向未审先实现、重复纠错、auto-mode 漂移和 AGENTS 膨胀的 known guards
  - 新增快验保护“改变下一步行为优先于记录”的语义
- 错误记录防复发语义：
  - `workflow-error-correction` 现在先查旧纠错并复用
  - 明确不要求用户重复指出已记录错误
  - 只有新模式、范围扩大或缺少预防规则时才新增记录
  - 新增快验保护该语义
- 工作流错误记录迁出 AGENTS：
  - 新增全局 `workflow-error-correction`
  - 项目和全局 `AGENTS.md` 删除具体 runtime-validation-loop 事故规则
  - AGENTS 只保留轻量边界和技能路由
  - 新增快验保护项目与全局 AGENTS 不重新引入这类具体事故规则
- 开发前方向审核主流程改造：
  - 升级全局 `pre-implementation-workflow-review` 为实现前 build gate
  - 四类 verdict：`build_now`、`manual_validation_first`、`revise_direction`、`do_not_build_now`
  - 明确只有 `build_now` 允许同一流程进入实现
  - 补充最小闭环验证、现有替代方案检查、当前信息搜索规则和 runtime-loop guardrail
  - 同步项目和全局 `AGENTS.md` 路由口径
  - 新增快验覆盖全局 skill 主流程护栏
- `AGENTS.md` 瘦身和 workflow skill 下沉：
  - `AGENTS.md` 现在只保留 workspace purpose、standing rules、workflow skill routing 和 minimal handoff rule
  - 新增 `auto_mode_stage_runner`
  - 新增 `deployment_strategy_review`
  - 新增 `session_handoff_maintenance`
  - 新增 `runtime_gate_workflow`
  - 新增 `runtime_verification_selector`
  - 新增 `repo_impact_analysis`
  - 新增 `nontechnical_stage_report`
  - active skill 数量从 7 增加到 14
  - 搜索质量基线扩展到 23/23
  - 新增执行测试覆盖这些从 `AGENTS.md` 下沉的 workflow skills
  - `python -m unittest tests.test_runtime_fast -v` 通过，83 tests OK
  - `python scripts/evaluate_search_quality.py --root .` 通过，23/23
  - `git diff --check` 无 whitespace error，仅有 `skill_store/index.json` 后续 LF 规范化提示
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/agents_workflow_skill_extraction_20260503043555.json`
- 全局配置同步：
  - `C:\Users\Administrator\.codex\AGENTS.md` 已同步为短规则和全局 workflow skill routing
  - 新增 8 个全局 Codex skills：`pre-implementation-workflow-review`、`auto-mode-stage-runner`、`deployment-strategy-review`、`session-handoff-maintenance`、`runtime-gate-workflow`、`runtime-verification-selector`、`repo-impact-analysis`、`nontechnical-stage-report`
  - 8 个全局 skills 均通过 `C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py`
  - 项目 `AGENTS.md` 路由名已对齐全局连字符 skill 名；直接调用 Skill Runtime active skills 时仍使用下划线 runtime 名
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/sync_global_agents_workflow_routing_20260503052119.json`
- 全局 skill 单一权威来源策略：
  - 新增 `docs/global-skill-source-of-truth-policy.md`
  - 全局 `C:\Users\Administrator\.codex\AGENTS.md` 和项目 `AGENTS.md` 都记录新通用 workflow skills 默认进入全局 skills 目录
  - `skill_runtime/platforms/discovery.py` 现在解析 `SKILL.md` frontmatter，并把外部 Codex skills 标记为 `source_role: authoritative_global_skill`
  - dashboard 平台视图会显示 global skill 的 source role 和 description
  - 修复 dashboard 同名 skill 计数：active 与 staging 同名时优先显示 active，当前 dashboard active_count 为 14
  - `python -m unittest tests.test_runtime_fast -v` 通过，85 tests OK
  - `python scripts/evaluate_search_quality.py --root .` 通过，23/23
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/convert_project_workflow_runtime_skills_to_thin__20260503054607.json`
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/global_skills_as_authoritative_source_for_new_wo_20260503053856.json`
- 项目 workflow active skills adapter 化：
  - 新增 `skill_runtime/execution/global_skill_adapter.py`
  - 8 个 workflow active skills 现在只作为全局 Codex skills 的薄 adapter
  - 执行结果写出 `adapter_role: global_codex_skill_adapter`、`global_skill_name`、`global_skill_path` 和 `source_role: authoritative_global_skill`
  - active metadata 已改成 adapter 口径，输入 schema 保留用于搜索和执行提示
  - `python -m unittest tests.test_runtime_fast -v` 通过，85 tests OK
  - `python scripts/evaluate_search_quality.py --root .` 通过，23/23
- 全局 Codex skill promotion 生命周期：
  - 新增 `RuntimeService.promote_to_global_codex_skill(...)`
  - 新增 CLI `promote-global-codex-skill`
  - 新增 MCP/host operation `promote_global_codex_skill`
  - 带 `workflow`、`global-workflow` 或 `codex-skill` 标签的 staging metadata 在 audit 通过后优先推荐全局 promotion
  - 全局 promotion 写入 `SKILL.md` 和 `agents/openai.yaml`，不创建项目 active copy，不更新项目 active index
  - `python -m unittest tests.test_runtime_fast -v` 通过，87 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
- `distill-and-promote` 全局目标闭环：
  - `RuntimeService.distill_and_promote(...)` 新增 `promotion_target`
  - CLI 新增 `distill-and-promote --promotion-target global-codex`
  - MCP `distill_and_promote_candidate` 支持 `promotion_target: global_codex`
  - 默认仍为项目 active promotion；只有显式指定全局目标时才写入全局 Codex skills
  - 全局目标不会创建项目 active copy，也不会更新 active index
  - `python -m unittest tests.test_runtime_fast -v` 通过，92 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
- captured trajectory 后续操作闭环：
  - `captured_trajectory_recommendation(...)` 仍默认推荐 `distill_trajectory`
  - 同时在 `available_host_operations` 暴露两条 `distill_and_promote_candidate`
  - 一条走项目 active promotion，一条显式走 `promotion_target: global_codex`
  - 这让 finalizer 捕获的成功工作流可以被宿主直接接到完整 promotion 闭环，但不会自动提升
  - `python -m unittest tests.test_runtime_fast -v` 通过，92 tests OK
- 新增开发方向价值门禁 active skill：
  - 新增 `skill_store/active/pre_implementation_workflow_review.py`
  - 新增 `skill_store/active/pre_implementation_workflow_review.metadata.json`
  - 更新 `AGENTS.md`，新增 Development Direction Value Gate
  - 重建 `skill_store/index.json`，active skill 数量为 7
  - 搜索质量基线新增 review / audit / direction value 查询
  - 新增执行测试覆盖低价值本地基础技能路线会返回 `change_route_before_implementation`，并输出 research queries、validation plan 和 stop condition
- 新增开发工作流 observation lane：
  - `skill_runtime/api/classification.py` 新增 `development-workflow-observation` 家族
  - 有明确工作区和明确产物的代码、测试、dashboard、文档、配置类开发工作流会进入 `default-in`
  - 对广义开发任务仍通过 `allow_silent_reuse=false` 避免静默自动执行
  - `skill_runtime/dashboard/render.py` 当前项目和全局总览新增 `已进入` 指标
  - 新增回归测试覆盖分类、进入 runtime lane、finalizer 捕获和 dashboard 展示
- 开发产物路径触发 observation lane：
  - `development-workflow-observation` 现在也能由明确输出路径触发
  - 例如 `skill_runtime/`、`tests/`、`docs/`、`scripts/`、`.github/` 下的代码、测试、文档和配置文件
  - 中性描述如“Expose captured trajectory promotion follow-ups”只要明确输出到代码/测试文件，也会进入 `default-in`
  - 没有明确输出的宽泛本地重构仍保持 `guarded-in`
  - `python -m unittest tests.test_runtime_fast -v` 通过，93 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/teach_the_codex_default_classifier_to_recognize__20260503063126.json`
- runtime lane follow-up 可视化：
  - `.skill_runtime/runtime_lane_events.jsonl` 现在记录 `recommended_next_action`
  - 同时记录 available host operation 的数量、标签和 tool 名
  - dashboard 当前项目和全局触发日志会显示“下一步”和 follow-up 操作标签
  - 面板仍然只读，不增加 promote/edit 按钮
  - `python -m unittest tests.test_runtime_fast -v` 通过，94 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/show_finalizer_learning_follow_up_actions_in_the_20260503063848.json`
- runtime lane 事件 CLI：
  - 新增 `python -m skill_runtime.cli runtime-events`
  - `--limit` 控制返回最近事件数量
  - `--global --scan-root <dir>` 返回跨项目事件、项目列表和事件统计
  - 输出包含 `recommended_next_action` 和 follow-up operation 标签
  - README、README.en 和 `docs/codex-integration.md` 已记录本地与全局 JSON 查看命令
  - `python -m unittest tests.test_runtime_fast -v` 通过，96 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
  - 本地和全局 `runtime-events` CLI smoke 均已通过
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/add_a_read_only_cli_command_to_inspect_recent_ru_20260503083440.json`
- runtime lane 事件 MCP：
  - 新增只读 MCP 工具 `runtime_events`
  - `limit` 控制返回最近事件数量
  - `global_events=true` 加 `scan_roots=[...]` 返回跨项目事件、项目列表和事件统计
  - 输出与 CLI 事件检查保持同一结构
  - `python -m unittest tests.test_runtime_fast -v` 通过，98 tests OK
  - `python scripts/evaluate_search_quality.py` 通过，23/23
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/add_a_read_only_mcp_tool_for_inspecting_recent_r_20260503084625.json`
- runtime event payload 去重：
  - 新增 `build_runtime_events_payload` 和 `build_global_runtime_events_payload`
  - `runtime-events` CLI 和 `runtime_events` MCP 现在共用同一套输出组装逻辑
  - TDD 红灯确认 builder 不存在时失败，随后 6 个事件相关 targeted tests 通过
  - `python -m py_compile skill_runtime\observability\events.py skill_runtime\cli.py skill_runtime\mcp\server.py` 通过
  - `python -m unittest tests.test_runtime_fast -v` 通过，100 tests OK
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/share_runtime_event_payload_assembly_between_cli_20260503085311.json`
- Codex CLI JSON file 参数：
  - `agent-plan`、`agent-plan-learning`、`codex-classify`、`codex-run`、`codex-finalize` 现在支持 `--known-inputs-json-file` 和 `--expected-outputs-json-file`
  - `agent-plan-learning` 和 `codex-finalize` 现在支持 `--plan-json-file` 和 `--execution-json-file`
  - 解决 PowerShell 下复杂内联 JSON 参数容易解析失败的问题
  - targeted Codex CLI tests 通过，`python -m py_compile skill_runtime\cli.py` 通过
  - `python -m unittest tests.test_runtime_fast -v` 通过，102 tests OK
  - 使用 `--known-inputs-json-file`、`--expected-outputs-json-file` 和 `--execution-json-file` 跑通真实 `codex-finalize`
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/add_json_file_argument_support_for_codex_task_cl_20260503085918.json`
- 全局 runtime gate skill 同步：
  - 已更新 `C:\Users\Administrator\.codex\skills\runtime-gate-workflow\SKILL.md`
  - 新会话使用 CLI fallback 时，会看到 PowerShell 场景优先使用 JSON file 参数的规则
  - 这项改动在全局配置目录，不在本仓库 git 跟踪范围内
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/update_the_global_runtime_gate_workflow_skill_to_20260503090117.json`
- 治理写路径索引刷新：
  - 发现旧逻辑能保住晚到新技能，但会覆盖非目标同名技能的晚到索引更新
  - 新增 targeted 回归：归档 fixture 过程中同名稳定技能被更新时，更新必须保留
  - `archive_cold`、`archive_duplicate_candidates`、`archive_fixture_skills` 和 `ProvenanceBackfill` 现在只把实际变更的 metadata 传给 `save_merged`
  - targeted governance tests 通过，`python -m py_compile skill_runtime\api\service.py skill_runtime\governance\provenance_backfill.py` 通过
  - `python -m unittest tests.test_runtime_fast -v` 通过，102 tests OK
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/review_and_tighten_index_refresh_behavior_for_go_20260503090649.json`
  - 该回归已抽入 `RuntimeGovernanceFastTestsMixin` 并接入 `tests.test_runtime_fast`
  - 最新 `python -m unittest tests.test_runtime_fast -v` 通过，103 tests OK
  - 快测覆盖 finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/add_the_governance_same_skill_late_update_regres_20260503091127.json`
- runtime test profiler JSON 输出：
  - `scripts/profile_runtime_tests.py` 新增 `--json-output <path>`
  - JSON 包含 `successful`、`tests_run`、`total_elapsed_seconds` 和 `slowest_tests`
  - 原有文本输出保持不变
  - README 已补充 `--json-output` 示例
  - contract 单测覆盖 JSON shape，CLI smoke 已写出 `.skill_runtime\profile-runtime-tests-smoke.json`
  - `python -m unittest tests.test_runtime_fast -v` 通过，103 tests OK
  - Codex finalizer 返回 `runtime_lane_status: used`，并捕获 `trajectories/add_json_output_support_to_the_runtime_test_prof_20260503091829.json`
- GitNexus 索引刷新：
  - `gitnexus status` 原先显示索引停在 `992f36e`，当前提交为 `c9f2c2c`
  - 已运行 `gitnexus analyze`，12.0s 完成，9,282 nodes / 13,651 edges / 124 clusters / 300 flows
  - `gitnexus status` 现在为 up-to-date at `c9f2c2c`
  - `gitnexus cypher "RETURN 1 AS c" --repo skill-runtime` 成功
  - `gitnexus query "runtime profiler json output" --repo skill-runtime --limit 3` 成功
  - `gitnexus context RuntimeService --repo skill-runtime` 成功
  - `gitnexus analyze` 自动写入的 AGENTS/CLAUDE 通用指令块已移除，保持本项目 AGENTS 瘦身策略
- 完成 `skills-manage` 吸收方案第一阶段：
  - 新增 `docs/platform-skill-inventory-design.md`
  - 新增 `skill_runtime/platforms/registry.py`
  - 新增 `skill_runtime/platforms/discovery.py`
  - 新增 `tests/test_runtime_platform_inventory.py`
  - dashboard collector 现在会收集 `platform_inventory`
  - dashboard 新增 `平台与项目` 只读视图
  - 快验 `python -m unittest tests.test_runtime_fast -v` 通过，66 tests OK
- 完成 `skills-manage` 吸收方案第二阶段：
  - 新增 `docs/platform-export-policy.md`
  - 新增 `skill_runtime/platforms/export_plan.py`
  - 新增 `tests/test_runtime_platform_export.py`
  - 新增 CLI `platform-export-plan`
  - 预览只支持 active 技能，非 active 技能返回 `skill_not_active`
  - 真实目录/文件冲突会标记为不 eligible
  - 快验 `python -m unittest tests.test_runtime_fast -v` 通过，70 tests OK
- 完成 `skills-manage` 吸收方案第三阶段本地导入部分：
  - 新增 `docs/import-to-staging-policy.md`
  - 新增 `skill_runtime/importers/local_skill_importer.py`
  - 新增 `tests/test_runtime_skill_import.py`
  - 新增 CLI `import-skill-to-staging`
  - 导入结果只进入 `skill_store/staging/imported/<skill_name>` 和 staging metadata
  - metadata 包含 `audit_status: requires_review`、`import_source`、`content_hash` 和 `provenance`
  - 快验 `python -m unittest tests.test_runtime_fast -v` 通过，73 tests OK
- 完成 `skills-manage` 吸收方案第三阶段 follow-up：
  - dashboard collector 现在保留导入候选的 `audit_status`、`import_source`、`imported_at`、`content_hash` 和 `provenance`
  - dashboard 组内技能详情会显示“外部导入”“需要审核”、来源路径和短 hash
  - 新增 dashboard 回归测试覆盖导入候选 provenance
  - dashboard 子集验证通过
- 完成 `skills-manage` 吸收方案第四阶段 capability collections：
  - 新增 `docs/capability-collections-design.md`
  - 新增 `skill_runtime/collections/model.py`
  - 新增 `skill_runtime/collections/store.py`
  - 新增 `tests/test_runtime_collections.py`
  - dashboard collector 现在会返回 `capability_collections`
  - dashboard 新增 `能力集合` 只读视图
  - 集合只作为组织层，不改变执行、审核、提升或归档语义
- 完成 `skills-manage` 吸收方案第五阶段 privacy and provenance：
  - 新增 `docs/privacy-and-provenance.md`
  - 说明哪些数据默认留在本地：skill store、trajectories、audits、runtime lane events、usage overlay、dashboard HTML
  - 说明哪些路径可能离开机器：外部 provider、DeepSeek provider、future GitHub/marketplace import、宿主外部转发
  - 明确 provider/GitHub/marketplace 凭据不能写入仓库
  - README / README.en 已增加 privacy and provenance 文档入口
- 分析 `iamzhihuix/skills-manage` 并形成具体吸收方案：
  - 明确它是 skill asset manager / control plane，本项目是 runtime lane / learning engine
  - 新增 `docs/superpowers/plans/2026-05-03-skills-manage-lessons-integration.md`
  - 新增决策：吸收 control-plane 经验但不转向桌面技能管理器
  - 推荐第一阶段先做 read-only 平台/项目 inventory 设计
- 记录用户确认的跨项目调用成功：
  - 用户确认其他项目目前可以正常调用 Skill Runtime
  - 已将该正样本写入 `docs/codex-default-lane-observation-log.md`
  - `TASKS.md` 中“观察全局默认能力在真实工作区中的表现”已标为完成
  - 下一步观察重点转为跨项目调用质量和 `entered` / `used` 样本
- 回到 Skill Runtime 默认触发和 dashboard 观察主线：
  - 按项目规则先调用 `mcp__skill_runtime__.run_codex_task_experimental`
  - 本轮任务被分类为 `default-out`
  - MCP gate 返回 `runtime_lane_status: skipped`
  - 同一事件已写入 `.skill_runtime/runtime_lane_events.jsonl`
  - MCP finalizer 也返回 `runtime_lane_status: skipped`
  - finalization 事件也已写入 `.skill_runtime/runtime_lane_events.jsonl`
  - 已将该真实样本补入 `docs/codex-default-lane-observation-log.md`
- 定位 GitNexus 查询失败根因：
  - GitNexus 已安装，仓库也已注册
  - 原索引落后当前提交 33 个提交
  - 真正导致“没效果”的问题是 LadybugDB FTS/VECTOR 扩展在 Windows 查询路径中崩溃
  - MCP 的 `Transport closed` 是 native crash 的结果，不是主要根因
- 修复本机 GitNexus 查询路径：
  - `pool-adapter.js` 跳过 pooled read path 的 FTS/VECTOR 扩展加载
  - `bm25-index.js` 在 Windows 下用 `CONTAINS` 扫描兜底，避免 FTS 崩溃
  - 保留结构查询和上下文查询能力，搜索排序质量会低于正常 FTS/vector 路径
- 重建当前仓库 GitNexus 索引：
  - Indexed commit: `992f36e`
  - Stats: `3032 files`, `8671 symbols`, `12478 edges`, `271 processes`
  - `gitnexus status` 已显示 `✅ up-to-date`
- 验证 GitNexus CLI 可用：
  - `gitnexus cypher "RETURN 1 AS c" --repo skill-runtime`
  - `gitnexus query "runtime service" --repo skill-runtime --limit 3`
  - `gitnexus context RuntimeService --repo skill-runtime`
  - dashboard 相关文件可通过 `cypher` 查到
- 更新 `docs/gitnexus-local-runbook.md`，记录新增补丁点、恢复步骤和当前限制
- 新增全局只读 dashboard，并与普通 dashboard 合并：
  - `python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open`
  - 默认输出 `.skill_runtime/global-dashboard.html`
  - 页面同时展示当前项目技能树、当前项目触发日志、当前项目治理快照、全局项目概览、全局触发日志
  - 全局部分只扫描指定目录下一层项目中的 `.skill_runtime/runtime_lane_events.jsonl`
  - 不跨项目编辑技能、不归档、不提升
- 已验证全局 dashboard：
  - `python -m unittest tests.test_runtime_fast -v`，63 tests OK
  - `python -m skill_runtime.cli dashboard --help`
  - `python -m skill_runtime.cli --root . dashboard --global --scan-root D:\02-Projects --output .skill_runtime\global-dashboard.html`
  - `git diff --check`
  - 截图检查：`output/playwright/runtime-dashboard-global-combined.png`
  - 全局日志页截图检查：`output/playwright/runtime-dashboard-global-log-view.png`
- 将 Codex 开发任务默认触发 runtime 的规则写入：
  - 全局 `C:\Users\Administrator\.codex\AGENTS.md`
  - 项目 `AGENTS.md`
  - 具体开发任务开始前先调用 `run_codex_task_experimental`
  - 如 MCP gate 不可用或没有可见 runtime 状态，使用 CLI `codex-run` 兜底
  - 任务完成后有结构化执行结果时，再调用 `finalize_codex_task_experimental`
- 验证 CLI 可见触发事件：
  - `python -m skill_runtime.cli --root . codex-run --task-description "update Codex agent rules for runtime gate" --working-directory . --risk-level low --task-kind project-state-maintenance --disable-silent-reuse --disable-learning`
  - 已写入 `.skill_runtime/runtime_lane_events.jsonl`
  - 本轮事件状态为 `runtime_lane_status: skipped`，原因是该规则更新任务被分类为 `default-out`
- 将 dashboard 的 Skill Tree 从长列表改成状态分支树：
  - 根节点显示当前 runtime root 的技能总量
  - 下方按 active / staging / archive / rejected 分枝
  - 每个技能作为分支下的节点展示
  - archive 等长分支不再全部铺满首屏，而是显示代表性节点和剩余数量
- 将 Skill Tree 进一步从长条卡片收成分支簇和叶子节点：
  - 分支不再用大矩形卡片撑满高度
  - 技能默认显示为紧凑叶子
  - 技能说明保留在可展开叶子内
  - 候选和归档分支默认收起多余节点
- 将 Skill Tree 改成径向布局：
  - 运行时根节点固定在中心
  - active / staging / archived / rejected 分布在四个象限
  - 移动端仍降级为单列，避免小屏挤压
- 调整 Skill Tree 中心节点位置：
  - 中心运行时根节点放到上下分支之间
  - 上下两排分支间距拉开，避免中心节点压到组别卡片
  - 截图检查：`output/playwright/runtime-dashboard-skill-tree-current-scrolled.png`
  - 对照首屏截图：`output/playwright/runtime-dashboard-skill-tree-center-spacing.png`
- 将 Skill Tree 第一层改成能力组别：
  - 默认显示格式转换、文本处理、文件整理、运行时治理等组别
  - 单个技能保留在居中详情界面里
  - 分组只用于 dashboard 展示，不回写 metadata 或索引
- 将组别展开改成居中详情界面：
  - 组别卡片点击后不再内联展开
  - 组内技能在居中弹出的详情界面中显示
  - 打开组别不会滚动页面
  - 详情界面提供“收起详情”，点击背景或按 Esc 也可关闭
  - 截图检查：`output/playwright/runtime-dashboard-group-detail-modal.png`
- 去掉 Skill Tree 中影响视觉的线条：
  - 移除中心向外的交叉连接线
  - 移除状态分支旁的硬竖向分界线
  - 改用四象限位置、状态圆点和能力组别卡片表达结构
  - 截图检查：`output/playwright/runtime-dashboard-skill-tree-groups-soft.png`
- 已验证本轮 dashboard 视觉调整：
  - `python -m unittest tests.test_runtime_fast -v`，60 tests OK
  - `git diff --check`
  - `python -m skill_runtime.cli dashboard --open`
  - 居中详情界面截图验证时页面滚动位置保持 `scrollY:0->0`，并锁定背景滚动
- 将 Trigger Log 从技能树区域中拆出：
  - 新增 `Skill Tree View`
  - 新增 `Trigger Log View`
  - 增加顶部视图导航，方便在两个视图之间切换
  - 改为页面式切换，不再点击后滚动到技能树下方
- 将治理快照从日志页底部拆出：
  - 新增 `Governance View`
  - 顶部导航现在是技能树、触发日志、治理快照三页
  - 触发日志只展示触发事件，治理快照只展示技能库健康状态
- 新增 dashboard 一键打开命令：
  - `python -m skill_runtime.cli dashboard --open`
  - `skill-runtime dashboard --open`
  - JSON 输出新增 `dashboard_url` 和 `opened`
- 将 dashboard 固定界面文案切换为中文：
  - HTML `lang` 改为 `zh-CN`
  - 标题、总览、技能树视图、触发日志视图、治理快照、状态标签和空状态均为中文
- 将技能卡片改成中文展示：
  - 技能名称显示中文
  - 技能说明显示中文
  - 原始英文 `skill_name` 保留为 HTML `data-skill-name`，不回写 metadata 或索引
  - 来源轨迹在界面上显示为“已记录 N 条来源轨迹”，原始轨迹 ID 保留为节点属性
- 顺手补了 dashboard 窄屏换行和布局保护
- 已验证：
  - `python -m unittest tests.test_runtime_fast -v`，60 tests OK
  - `python -m unittest tests.test_runtime_fast.RuntimeFastTests.test_dashboard_renderer_includes_core_sections tests.test_runtime_fast.RuntimeFastTests.test_dashboard_cli_writes_static_html_file -v`
  - `python -m unittest tests.test_runtime_fast.RuntimeFastTests.test_dashboard_command_can_open_generated_html -v`
  - `python -m unittest tests.test_runtime_fast.RuntimeFastTests.test_dashboard_renderer_includes_core_sections tests.test_runtime_fast.RuntimeFastTests.test_dashboard_cli_writes_static_html_file tests.test_runtime_fast.RuntimeFastTests.test_dashboard_command_can_open_generated_html -v`
  - `python -m py_compile skill_runtime/dashboard/templates.py skill_runtime/dashboard/render.py tests/test_runtime_dashboard.py`
  - `python -m py_compile skill_runtime/cli.py tests/test_runtime_dashboard.py`
  - `python -m skill_runtime.cli dashboard --help`
  - `git diff --check`
  - `python -m skill_runtime.cli dashboard --output .skill_runtime/dashboard.html`
  - `python -m skill_runtime.cli dashboard --open`
- 实现只读 runtime observability dashboard：
  - 新增 runtime lane 事件日志 `.skill_runtime/runtime_lane_events.jsonl`
  - 新增 dashboard 数据收集层
  - 新增静态 HTML 渲染层
  - 新增 `dashboard` CLI 命令
  - README / README.zh-CN 已补充使用方式
- 已验证：
  - `python -m unittest tests.test_runtime_fast -v`，59 tests OK
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `git diff --check`
  - `python -m skill_runtime.cli dashboard --output .skill_runtime/dashboard.html`
- 完成只读可视化观察面板设计：
  - 第一版只看当前 runtime root
  - 展示技能树、触发日志、治理快照和概览
  - 需要新增 `.skill_runtime/runtime_lane_events.jsonl` 作为自动触发事件日志
  - 不做编辑、promote、archive、跨工作区聚合或常驻 Web 服务
- 完成只读 dashboard 实现计划：
  - 计划文件：`docs/superpowers/plans/2026-05-01-runtime-observability-dashboard.md`
  - 实现顺序：事件日志 -> host 接入 -> 数据收集 -> HTML 渲染 -> CLI 命令 -> 验证与状态收口
- 新增 runtime lane 可见性字段：
  - `runtime_lane_status`
  - `runtime_lane_reason`
- 统一 Codex host API、CLI 和 MCP payload 重建路径对这两个字段的传递
- 补充快验，覆盖 default-in 被实际使用、default-out 被跳过、CLI plan 输出可见状态
- 更新 README、Codex 接入文档和默认通道观察日志，说明如何判断是否触发
- 已运行：
  - `python -m unittest tests.test_runtime_fast.RuntimeFastTests.test_codex_host_api_run_task_executes_default_in_flow tests.test_runtime_fast.RuntimeFastTests.test_codex_host_api_run_task_keeps_default_out_work_on_normal_path tests.test_runtime_fast.RuntimeFastTests.test_agent_plan_cli_returns_reuse_decision_for_workflow_request tests.test_runtime_fast.RuntimeFastTests.test_agent_plan_cli_now_keeps_default_out_work_on_normal_path -v`
  - 结果：4 tests OK
- 完成第一处现有入口切换后的更大范围验证
- 验证 `check_mcp_architecture` 通过
- 验证 `check_runtime_contracts` 通过
- 验证 `codex-run` 可真实执行 default-in 文本工作流
- 验证 `agent-plan` 可真实把开放式 review 任务留在普通路径
- 验证 `python -m unittest tests.test_runtime -v` 全量慢验通过，399 tests OK
- 新增 `docs/codex-default-lane-stage-closure.md`
- 新增 `docs/codex-default-lane-observation-plan.md`
- 新增 `docs/codex-default-lane-observation-log.md`
- 完成全局 `skill_runtime` 启动收口：
  - 全局 `AGENTS.md` / `MEMORY.md` 已改
  - 全局 `config.toml` 已改
  - 新增 `C:\Users\Administrator\.codex\launch-skill-runtime.ps1`
- 验证全局启动脚本在不同工作区会解析到不同 root
- 完成仓库主文档口径切换：
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/mcp-integration.md`
  - `docs/codex-integration.md`
- 新增对外说明文档：
  - `docs/multi-host-adaptation-plan.md`
- 正式将第一处现有入口迁移收口为阶段性默认路径验证点
- 正式将下一阶段切换为“观察期”，不再默认继续扩大入口数量
- 已运行：
  - `powershell -File C:\Users\Administrator\.codex\launch-skill-runtime.ps1 -PrintRoot`
  - `python -m skill_runtime.cli --root D:\02-Projects\work search --query "test workflow"`
  - `python -m unittest tests.test_runtime -v`
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m skill_runtime.cli codex-run --task-description "merge txt files into markdown" ...`
  - `python -m skill_runtime.cli agent-plan --task-description "Review this architecture and decide the roadmap."`
  - `git diff --check`
  - 结果：全量慢验 399 tests OK；架构检查通过；contract 检查通过；CLI smoke 通过；全局启动脚本可在不同工作区解析到不同 root；`python -m skill_runtime.cli --root D:\02-Projects\work search --query "test workflow"` 可正常空跑；`git diff --check` 仅剩既有 LF 换行提示
- 将现有 `agent-plan` / `agent-plan-learning` 正式切换到 Codex 默认通道
- 验证 `agent-plan` 现在会返回 `task_classification`
- 验证 `agent-plan` 在 `default-out` 任务上会留在普通路径
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/cli.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 53 tests OK；语法检查通过；格式检查通过
- 将 phase-one `default-in` 收窄为四类白名单家族
- 验证结构化转换任务会进入 `structured-format-conversion`
- 验证低风险工作区整理任务会进入 `low-risk-workspace-organization`
- 修复一个关键误判：
  - 带本地输出路径的外部登录/网站任务不再因为有 `output_path` 就误入 `default-in`
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/classification.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 52 tests OK；语法检查通过；格式检查通过
- 新增 Codex CLI 默认通道：
  - `codex-classify`
  - `codex-run`
  - `codex-finalize`
- 验证 `codex-classify` 可正确识别项目状态文件维护任务为 `default-in`
- 验证 `codex-run` 可让 `default-in` 任务自动进入 runtime lane 并执行
- 验证 `codex-finalize` 可让 `default-in` 欠覆盖任务继续 capture trajectory 并给出 recommendation
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/cli.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 49 tests OK；语法检查通过；格式检查通过
- 新增 `skill_runtime/api/classification.py`
- 把 Codex 任务分类边界落成可运行判断器
- 新增 Codex host API：
  - `classify_codex_task`
  - `start_codex_task`
  - `run_codex_task`
  - `finalize_codex_task`
- 新增 Codex MCP 实验入口：
  - `run_codex_task_experimental`
  - `finalize_codex_task_experimental`
- 验证 `default-in` 任务可直接走新 Codex 路径并自动复用
- 验证 `default-out` 任务会留在普通路径，不会误入 runtime lane
- 验证 `default-in` 欠覆盖任务在完成后仍可 capture trajectory 并给出后续 recommendation
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/classification.py skill_runtime/api/models.py skill_runtime/api/orchestration.py skill_runtime/api/host.py skill_runtime/api/__init__.py skill_runtime/mcp/server.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 46 tests OK；语法检查通过；格式检查通过
- 新增 `docs/codex-task-classification-boundary.md`
- 明确 Codex 任务先分为三类：
  - `default-in`
  - `guarded-in`
  - `default-out`
- 明确 phase one 默认只让 `default-in` 自动进入 runtime lane
- 明确第一批推荐 `default-in`：
  - 本地文本处理
  - 结构化转换
  - 项目状态文件维护
  - 低风险工作区整理
- 明确 `guarded-in` 先不静默自动进入
- 明确 `default-out` 继续留在普通 Codex 路径
- 新增 `docs/codex-default-integration-plan.md`
- 明确 Codex 默认接入先采用受控低风险任务通道，而不是一次性全量切换
- 明确 runtime 在 Codex 中的目标位置是：
  - 任务开始前作为 reuse gate
  - 任务完成后作为 learning gate
- 明确 phase one 的 default-in 任务：
  - 本地文件转换
  - 本地文件整理
  - 项目维护类任务
  - 结构化导出和格式转换
- 明确 phase one 的 default-out 任务：
  - 开放式对话
  - 高风险操作
  - 外部系统依赖重的任务
  - 成功标准不清晰的任务
- 明确 Codex 默认接入当前仍停在 `capture + recommendation`，不默认自动继续 `distill/promote`
- 停止默认继续补通用 dogfood 技能样本
- 新增 `docs/agent-first-runtime-architecture.md`
- 把目标应用形态明确改写为：代理先完成任务，runtime 在后台自动复用、自动沉淀、自动优化
- 明确 MCP / CLI / 治理脚本继续保留，但定位退居接口层、调试层和治理层
- 将“通用样本已足够，后续优先做自动沉淀主线”的判断写入 `docs/core-readiness-audit.md`
- 将这一轮方向转向写入 `DECISIONS.md`、`TASKS.md` 和 `HANDOFF.md`
- 新增 `docs/agent-side-reuse-policy.md`
- 明确自动复用先采用三段式决策带：
  - `>= 0.85` 才允许进入静默自动复用候选
  - `0.75 ~ 0.85` 只做后台提示，不默认自动执行
  - `< 0.75` 不复用
- 明确自动复用第一处代码接入点应在 `skill_runtime/api/` 附近的新 orchestration / policy 边界，而不是 MCP 层
- 新增 `docs/post-task-distillation-policy.md`
- 明确自动沉淀先采用四种结果分流：
  - `skip`
  - `observed_only`
  - `new_skill_candidate`
  - `improve_existing_skill`
- 明确自动沉淀默认采用“观测优先、蒸馏保守”策略，避免成功任务自动把 active skill 库重新搞脏
- 新增 `docs/agent-orchestration-interface.md`
- 明确第一版 orchestration 先收口为小边界，不接管完整任务规划
- 在 `skill_runtime/api/models.py` 中加入最小请求/决策/结果结构：
  - `AgentTaskRequest`
  - `ReuseDecision`
  - `LearningDecision`
  - `AgentOrchestrationResult`
- 新增 `skill_runtime/api/orchestration.py`
- 落地第一版 `AgentOrchestrationService`
- 新增并通过第一版 orchestration 快验：
  - 强匹配且参数齐全时允许 `auto_execute`
  - 参数缺失时退回 `background_hint`
  - 已有技能干净完成任务时学习决策为 `skip`
  - 具体且成功的欠覆盖工作流可标记为 `new_skill_candidate`
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `git diff --check`
  - `python -m py_compile skill_runtime/api/models.py skill_runtime/api/__init__.py`
  - 结果：快验 24 tests OK；格式检查通过；新 API 模型语法检查通过
- 在 `skill_runtime/cli.py` 中新增最小真实调用点：
  - `agent-plan`
  - `agent-plan-learning`
- 新增并通过 CLI 调用点快验：
  - `agent-plan` 返回复用判断
  - `agent-plan-learning` 返回学习判断
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/orchestration.py skill_runtime/cli.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 26 tests OK；语法检查通过；格式检查通过
- 在 `AgentOrchestrationService` 中新增双阶段 helper：
  - `start_task(...)`
  - `finalize_task(...)`
- 新增并通过 helper 快验：
  - `start_task(...)` 返回组合后的上层计划
  - `finalize_task(...)` 把学习判断附着回原计划
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/orchestration.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 28 tests OK；语法检查通过；格式检查通过
- 将现有 CLI 调用点改为真正走 lifecycle helper：
  - `agent-plan -> start_task(...)`
  - `agent-plan-learning -> finalize_task(...)`
- `agent-plan-learning` 现在支持直接接收 `plan-json`，把学习判断附着回同一份 plan
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/cli.py skill_runtime/api/orchestration.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 28 tests OK；语法检查通过；格式检查通过
- 在 `AgentOrchestrationService` 中新增最小真实任务流入口：
  - `run_task(...)`
- 新增并通过 `run_task(...)` 快验：
  - 强匹配工作流会自动执行并回收学习判断
  - 无自动复用条件时只返回 plan，不擅自执行
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/orchestration.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 30 tests OK；语法检查通过；格式检查通过
- 新增公开宿主入口 facade：
  - `skill_runtime/api/host.py`
  - `run_agent_task(...)`
  - `start_agent_task(...)`
  - `finalize_agent_task(...)`
- 并将其导出到 `skill_runtime.api`
- 新增并通过 facade 快验：
  - 外部代理可直接通过 host API 跑通最小真实任务流
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/host.py skill_runtime/api/__init__.py tests/test_runtime_agent_orchestration.py tests/test_runtime_contracts.py`
  - `git diff --check`
  - 结果：快验 31 tests OK；语法检查通过；格式检查通过
- 新增 `docs/agent-mainline-readiness-review.md`
- 盘点结论：
  - 新 agent-first 路径已经真实存在
  - 已具备 CLI、service、host API 三层入口
  - 但当前仍不建议立刻把默认上层整体切到新 host facade
  - 更合理定位是“preferred experimental path”
- 选择首个受控试运行入口为独立 MCP 实验工具 `run_agent_task_experimental`
- 将该实验入口直接接到 `skill_runtime.api.host.run_agent_task(...)`
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/mcp/server.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 32 tests OK；语法检查通过；格式检查通过
- 新增实验入口边界快验：
  - 自动执行时保留 `rollback_operations`
  - 欠覆盖工作流时只返回 plan-only
  - `allow_silent_reuse=False` 时不会偷跑
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 35 tests OK；语法检查通过；格式检查通过
- 新增实验型学习收尾入口：
  - `finalize_agent_task_experimental`
- 验证 under-covered workflow 可在宿主执行后重新接回学习链
- 验证 finalize 后会真实 capture trajectory，并返回 `distill_trajectory` 后续建议
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile skill_runtime/api/models.py skill_runtime/api/orchestration.py skill_runtime/mcp/server.py tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 36 tests OK；语法检查通过；格式检查通过
- 用“更新 HANDOFF / TASKS / DECISIONS”完成第一条真实任务 dogfood 验证
- 验证真实项目维护任务也能被 capture 为 trajectory，并给出 `distill_trajectory` 后续建议
- 已运行：
  - `python -m unittest tests.test_runtime_fast -v`
  - `python -m py_compile tests/test_runtime_agent_orchestration.py`
  - `git diff --check`
  - 结果：快验 37 tests OK；语法检查通过；格式检查通过
- 完成当前层阶段性收口判断：先停在 `capture + recommendation`
- 新增 `docs/agent-layer-stage-closure.md`
- 当前不再默认继续推进到自动 `distill/promote`

## Next Action

如果继续当前 `v0.3 product completeness` 主线，下一步优先不是加 dashboard 页面，而是判断 `operator-summary` 的哪些子字段已经足够稳定，可以被现有 dashboard collector 安全消费。重点不是 UI，而是收口数据依赖：例如是否要让现有 collector 直接读取 `RuntimeService.operator_summary()` 的稳定字段，而不是继续散读多处底层文件。不要让 dashboard 直接依赖不稳定字段，也不要把这条线变成 dashboard 重写。当前仍然不要扩大 `default-in`，不要自动 promote，不要自动 apply evolution candidate，也不要把 expected gap 硬改成 pass。

如果继续当前 `v0.3 product completeness` 主线，下一步优先不是继续写 release 材料，也不是扩 proof bundle，而是继续把 Operator Workbench 做成更完整但仍只读的 operator surface。优先补的应是：哪些 gate 状态值得持久化为本地状态索引、哪些 runtime event / governance event 应该被 summary 更稳定地消费，以及是否需要比 CLI text 更清楚的 maintainer-facing summary formatting。不要把这条线变成 dashboard 大改，也不要把 visibility 改造成自动 lifecycle 执行。当前仍然不要扩大 `default-in`，不要自动 promote，不要自动 apply evolution candidate，也不要把 expected gap 硬改成 pass。

如果继续 v0.2 release 主线，下一步优先做发布动作而不是继续扩功能：确认工作区只包含这轮 RC gate 的文档/元数据/state 更新，完成 commit + push；如果之后要正式 cut tag，再决定是否从 `0.2.0rc1` 进入最终 `v0.2.0`。不要借 RC 通过去改 ranking、扩大 `default-in`、把 expected gap 硬做成 pass、扩 CLI recommendation 到别的命令，或把 dashboard 继续包装成 release proof。

如果继续 `v0.2-search-quality`，下一步不要回到 utility skill 过度优化，也不要调 ranking weight。优先判断是否需要补 workflow metadata 覆盖：重点看 `review cleanup` 和 `governed learning follow-up` 这两类 query 是否值得拥有真实 active workflow metadata，还是应继续作为 demo / host-follow-up 能力而保持 search expected gap。只有在这个产品边界明确之后，才考虑扩 workflow baseline query 集；不要把当前 workflow baseline 当成扩大 `default-in` 的证据。

当前新战略目标是“开源申请后继续产品化主线”。申请表已提交，dashboard 当前已经够用，主线已收回到核心机制。当前 recommendation contract 已经统一，边界 dogfood 和顺序链验收也都完成，而且这轮 checked-in payload dogfood 已进一步证明当前 helper 足够完成第一轮 operator comprehension。下一步不应继续扩 presentation code，而应按 `docs/real-host-payload-rendering-runbook.md` 做真实 host/operator validation。不要回到继续堆 runtime 样本；也不要把观察面当成产品本体。

技能进化闭环已经有 apply 和 rollback 两端的主线验收，也已经有明确的 host-facing follow-up，并且现在有独立 acceptance doc / runbook。下一步如果继续这条主线，不应再补“能不能回滚”或“按钮能不能显示”这种基础能力，而应判断是否要 dogfood 这条 operator-facing 路径，或者是否需要更强的人工审核策略；不要做无确认自动写全局技能。

开发前方向审核已经升级为主流程门禁。下一次任何新产品方向、新工具、新功能路线或“继续开发还是换方向”的问题，都先用全局 `pre-implementation-workflow-review` 输出 verdict；只有 `build_now` 可以进入实现，其余结论都先验证、改路线或停止。不要默认继续 runtime/sample/dashboard 验证，除非它直接服务于方向审核。下一次进入 AGENTS 编辑、runtime 验证、路线纠正、自动模式延续、方向审核等已知风险场景时，先应用全局 `workflow-error-correction` 里的 known guards，直接改变下一步行为；不要等用户重复指出，也不要把它当成单纯记录工具。后续新增通用工作流时，默认创建或提升为全局 Codex skill，再让项目 `AGENTS.md`、runtime inventory 或薄 adapter 指向它，不在项目内复制完整流程。dashboard 默认界面应继续保持 `skills-manage` 式管理应用外壳、workflow-first 主视图和 workflow-only 集合页；基础本地 helpers 不再作为默认可视化界面内容出现，只保留底层能力和显式检索路径。`总览` 页不要恢复路径副标题或本页搜索栏；`中央技能库` 导航计数按 active workflow skills 统计；跨工作区日志合并到唯一的 `触发日志` 入口，不再单独放 `全局日志`；触发日志卡片必须用中文解释任务、处理方式和结果，不要直接展示英文 runtime 内部原因。`skills-manage` control-plane 吸收方案 Phase 1-5 已完成；下一步不默认做 GitHub import。查看当前项目用 `python -m skill_runtime.cli dashboard --open` 或 `python -m skill_runtime.cli runtime-events`；查看多个项目用 `python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open` 或 `python -m skill_runtime.cli runtime-events --global --scan-root D:\02-Projects`。如果下一轮需要 GitNexus 做精确影响分析，先更新当前仓库 GitNexus 索引。

## Important Files

- `AGENTS.md`
- `TASKS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `docs/gitnexus-local-runbook.md`
- `docs/global-skill-source-of-truth-policy.md`
- `docs/codex-open-source-readiness-audit.md`
- `docs/codex-open-source-positioning.md`
- `docs/open-source-release-readiness-checklist.md`
- `docs/codex-open-source-application-draft.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `docs/maintainer-review-cleanup-demo.md`
- `docs/maintainer-release-readiness-demo.md`
- `docs/maintainer-handoff-continuation-demo.md`
- `docs/codex-open-source-packaging-decision.md`
- `C:\Users\Administrator\.codex\skills\parallel-subagent-orchestration\SKILL.md`
- `docs/core-readiness-audit.md`
- `docs/agent-first-runtime-architecture.md`
- `docs/agent-side-reuse-policy.md`
- `docs/post-task-distillation-policy.md`
- `docs/agent-orchestration-interface.md`
- `docs/core-dogfood-acceptance.md`
- `skill_runtime/api/models.py`
- `skill_runtime/api/orchestration.py`
- `skill_runtime/api/host.py`
- `skill_runtime/observability/events.py`
- `skill_runtime/dashboard/collector.py`
- `skill_runtime/dashboard/render.py`
- `skill_runtime/dashboard/templates.py`
- `skill_runtime/cli.py`
- `skill_runtime/mcp/server.py`
- `skill_runtime/api/classification.py`
- `tests/test_runtime_agent_orchestration.py`
- `docs/agent-mainline-readiness-review.md`
- `docs/codex-default-integration-plan.md`
- `docs/codex-task-classification-boundary.md`
- `docs/codex-default-lane-stage-closure.md`
- `docs/codex-default-lane-observation-plan.md`
- `docs/codex-default-lane-observation-log.md`
- `docs/superpowers/specs/2026-05-01-runtime-observability-dashboard-design.md`
- `docs/superpowers/plans/2026-05-01-runtime-observability-dashboard.md`
- `docs/provider-integration.md`
- `examples/providers/copy_metadata_fallback_provider.py`
- `examples/providers/pass_semantic_review_provider.py`
- `examples/providers/deepseek_fallback_provider.py`
- `examples/providers/deepseek_semantic_review_provider.py`
- `tests/test_runtime_deepseek_provider_examples.py`
- `TESTS.md`
- `pyproject.toml`
- `.github/workflows/runtime-contracts.yml`
- `scripts/profile_runtime_tests.py`
- `scripts/smoke_deepseek_provider_loop.py`
- `scripts/evaluate_search_quality.py`
- `scripts/check_runtime_contracts.py`
- `skill_runtime/execution/runtime_tools.py`
- `skill_runtime/cli.py`
- `skill_runtime/mcp_stdio.py`
- `skill_runtime/distill/fallback/command_provider.py`
- `skill_runtime/distill/fallback/service.py`
- `skill_runtime/audit/command_semantic_provider.py`
- `skill_runtime/audit/semantic_review_service.py`
- `tests/test_runtime_mcp_smoke.py`
- `tests/test_runtime_fast.py`
- `tests/runtime_test_support.py`
- `tests/test_runtime_isolation.py`
- `.gitattributes`
- `.gitignore`
- `skill_runtime/retrieval/skill_index.py`
- `skill_runtime/api/service.py`
- `skill_runtime/mcp/operation_builders.py`
- `skill_runtime/mcp/recommendation_builders.py`
- `skill_runtime/governance/provenance_backfill.py`
- `tests/test_runtime_governance.py`
- `skill_store/active/merge_text_files.metadata.json`
- `skill_store/active/json_to_csv_dogfood.py`
- `skill_store/active/json_to_csv_dogfood.metadata.json`
- `skill_store/active/directory_json_to_csv_dogfood.py`
- `skill_store/active/directory_json_to_csv_dogfood.metadata.json`
- `skill_store/active/text_replace_dogfood.py`
- `skill_store/active/text_replace_dogfood.metadata.json`
- `skill_store/active/directory_text_cleanup_dogfood.py`
- `skill_store/active/directory_text_cleanup_dogfood.metadata.json`
- `trajectories/dogfood_json_to_csv_20260429.json`
- `trajectories/dogfood_directory_json_to_csv_20260429.json`
- `trajectories/dogfood_text_replace_20260429.json`
- `trajectories/dogfood_directory_text_cleanup_20260429.json`
- `audits/json_to_csv_dogfood.audit.json`
- `audits/directory_json_to_csv_dogfood.audit.json`
- `audits/text_replace_dogfood.audit.json`
- `audits/directory_text_cleanup_dogfood.audit.json`
- `demo/input/json_records/`
- `demo/input/template_note.txt`
- `demo/input/text_notes/`
- `skill_store/staging/*.metadata.json`
- `README.md`
- `README.zh-CN.md`
- `tests/test_runtime_contracts.py`
- `tests/test_runtime_core_dogfood_acceptance.py`
- `tests/test_runtime_audit_lifecycle.py`
- `tests/test_runtime_search_quality.py`
- `skill_runtime/mcp/server.py`

## Known Issues

- 核心功能目前是本地 MVP，不应宣称已经完成。
- semantic audit 默认仍使用 mock provider；已支持外部 provider 命令、本地 demo provider 和 DeepSeek provider，但未配置真实模型时质量判断仍不够强。
- fallback distillation 默认仍使用 mock provider；已支持外部 provider 命令、本地 demo provider 和 DeepSeek provider。
- 本地 demo provider 是窄场景示例，只证明 provider hook 和闭环可运行，不能代表通用自动生成能力。
- 用户曾在聊天中暴露 DeepSeek API key；不要把该 key 写入文件或提交。本轮已按用户要求直接使用，但仓库文件中未检测到该 key。
- DeepSeek live smoke 已证明 API 可连通，且完整 provider 闭环已在临时沙箱中跑通；仍不应把单次 live smoke 等同于长期稳定 SLA。
- DeepSeek 质量门禁已经能阻止坏输出进入 staging，并默认允许一次自动返修；如果返修后仍失败，候选仍不会进入 staging。
- active skill 当前已有 6 个真实技能，已足够证明主链路存在；当前风险转为“默认工作方式仍偏手动技能库”，不是“样本数量继续不够”。
- 当前仓库 GitNexus 索引已更新到当前提交，CLI 查询已恢复；但成功依赖本机 GitNexus 安装中的临时修改，不应误判为“默认官方路径已完全无问题”。
- 新会话 app 级 `mcp__skill_runtime__` 连接已能返回 `default-in/entered`；早先同一会话里的旧 MCP server 热加载问题已不再是当前提交阻塞点。
- 未来新的 dogfood 执行默认不再改写版本管理下的 active metadata 和主索引。
- 当前会话尝试 GitNexus MCP 查询时返回 `Transport closed`；根因已定位为 native crash，CLI 已恢复，但当前会话内 MCP transport 仍需新会话或重启后复测。
- 本轮内置 Browser/IAB 预览因为本机 Node 版本低于插件要求不可用，已退回本机 Chrome headless 截图检查。
- 全量 runtime suite 不是失败，但当前约 9 分钟，仍不适合作为每次小改动的默认第一验证命令。
- `git diff --check` 当前仍提示 `skill_store/index.json` 和 `trajectories/demo_merge_text_files.json` 未来会按 LF 写回；这是换行提示，不是本轮新增的失败。

## Constraints

- 当前阶段仍不要开始业务功能开发。
- 不要开始业务功能开发。
- 不要把产品化收敛误当成核心功能已经完成。
- 不要再把“增加通用 dogfood 技能数量”当作默认主线。
- 长期上下文应优先写入项目文件，而不是聊天记录。
- 自动模式阶段报告必须使用非技术语言，帮助非程序员用户理解项目进展。
- 不要为了让测试通过而重新把测试技能放回真实 active skill 库。

## Do Not Do

- 不要依赖旧对话历史恢复项目状态。
- 不要要求旧会话再生成大段交接提示词。
- 不要在没有必要时改动业务代码。
- 不要为了增加样本数量继续机械补第 7 个、第 8 个通用技能。
- 不要因为小改动、单个测试通过或单个文件修改完成就打断用户。
