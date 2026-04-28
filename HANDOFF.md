# Handoff

## Current State

已完成一轮 Skill Runtime 产品化收敛，并已转入核心功能完成度收敛。当前结论：项目已经有可用本地 MVP，核心闭环 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 在代码结构上存在，CLI / MCP / 测试 / 治理基础也已成型；但核心功能还不能宣称完全完成。三条核心 dogfood 验收路径已新增：已知技能可通过 MCP host-style 调用完成搜索、执行、observed task、提升、复用，并确认 active 搜索没有 fixture-tier 污染；未知工作流进入 mock fallback 后会被审核挡住，不会自动提升到 active；配置外部命令型 fallback / semantic provider 后，未知工作流可以生成、审核、入库并复用。仓库现在包含两个本地 demo provider，可从 fresh clone 直接验证 provider hook，不需要测试临时生成脚本。验证层已拆分为日常快验和全量慢验：`tests.test_runtime_fast` 当前约 9-10 秒，`tests.test_runtime` 当前约 9 分钟。剩余主要短板是：还没有内置 OpenAI 或本地模型 provider；本地 demo provider 只证明 provider 接口和闭环可运行，不是通用生成后端；搜索质量仍是轻量关键词评分；active skill 库样本仍少。

## Last Completed

本轮已完成：
- 新增 `docs/core-dogfood-acceptance.md`，记录核心 dogfood 验收范围
- 新增 `tests/test_runtime_core_dogfood_acceptance.py`
- 将核心 dogfood 验收接入 `tests.test_runtime`
- 第一条验收路径覆盖：MCP 搜索、执行、observed task、提升、复用、active 搜索无 fixture-tier 污染
- 第二条验收路径覆盖：未知工作流进入 mock fallback 后不自动提升为 active
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：350 tests OK
- 新增 `docs/core-readiness-audit.md`，记录核心完成度盘点
- 明确当前状态是“可用本地 MVP”，不是“核心功能完成”
- 将下一阶段主线从产品化收敛切回核心 dogfood 验收
- 新增 `pyproject.toml`，声明 Python 3.11+ 和 MCP 运行依赖
- README / README.zh-CN 增加本地安装与最小验证步骤
- `.github/workflows/runtime-contracts.yml` 先执行 `python -m pip install -e .`
- 新增最小 MCP smoke 测试：验证 `build_mcp_server` 可 import 且能构造 server
- 修复 `RuntimeTools.copy_file` 在新建复制目标场景下的 rollback hint，与 `RuntimeService.rollback_operations` 保持一致
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
- 已执行 active skill 治理清理，且明确保留真实 dogfood skill
- 已重建 `skill_store/index.json`
- 当前 active skill 只剩：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 当前治理报告：
  - `active_count = 2`
  - `duplicate_candidates = []`
  - `fixture_count = 0`
- 当前搜索验证：
  - 查询 `merge txt files into markdown` 时，不再出现测试技能污染结果
- runtime 测试支撑层已切到隔离副本
- 搜索 / 治理 / 生命周期测试已补齐自带样本，不再依赖历史污染的 active skill 库
- 已重新运行：
  - `python -m unittest tests.test_runtime -v`
  - 结果：342 tests OK
- 已补齐安装配置中的递归包发现
- 已新增正式命令入口：
  - `skill-runtime`
  - `skill-runtime-mcp`
- 已保留旧入口兼容：
  - `python scripts/skill_cli.py`
  - `python scripts/skill_mcp_server.py`
- README / README.zh-CN 已补充：
  - 安装后命令入口
  - `python -m skill_runtime...` 模块入口
- 已再次运行：
  - `python -m pip install -e .`
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 安装后入口 `--help`
  - 结果：344 tests OK
- 已补充 `.gitattributes`，统一仓库文本换行规范
- 已将 `.claude/` 加入 `.gitignore`
- 已保留 `docs/gitnexus-local-runbook.md` 作为正式仓库文档
- 已将 active skill 的使用统计写回迁移到本地 `.skill_runtime/usage.json`
- README / README.zh-CN 已补充本地 usage 状态文件说明
- 已重新运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：345 tests OK
- 已为治理维护动作补齐索引合并保存策略
- 已新增回归测试，覆盖归档过程中出现晚到索引更新仍能保留
- 已再次运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：346 tests OK
- 已将 `AGENTS.md` 中的新会话接力、自动模式、GitNexus 使用规则纳入正式提交
- 已按 `.gitattributes` 规范化 `skill_store` 文本文件，清理历史换行噪音
- README / README.zh-CN 已补充 clone 后最短验证路径
- 已修复模块入口：
  - `python -m skill_runtime.cli ...`
  - `python -m skill_runtime.mcp_stdio ...`
- 已新增模块入口回归测试
- 新增外部命令型 fallback provider：
  - `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD`
- 新增外部命令型 semantic provider：
  - `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`
- 新增 provider dogfood 验收：未知工作流经外部 provider 生成、审核、promote、reuse
- 新增 semantic provider 阻断测试：外部审核器返回 high issue 时禁止 promote
- 新增 `docs/provider-integration.md`
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：352 tests OK
- 新增日常快验套件 `tests.test_runtime_fast`
- 新增慢测试定位脚本 `scripts/profile_runtime_tests.py`
- README / README.zh-CN / TESTS / AGENTS 已改为优先提示快验，full suite 标注为慢速全量验证
- CI 已增加快验步骤，并保留 full runtime suite
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime_fast -v`
  - `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 10`
  - 结果：快验 7 tests OK，约 10 秒；全量耗时分析 352 tests OK，约 11 分钟
- 当前最慢单项：
  - `test_check_runtime_contracts_script_passes`，约 47 秒
- 已优化 contract 检查的隔离沙箱：默认只复制验证真正需要的 `demo`、`skill_store`、`trajectories`，不再反复复制历史 observed task 和 output
- 已同步优化测试沙箱复制，跳过 `__pycache__`，减少 Windows 本地重复文件复制成本
- 已新增回归测试，保证 contract 检查默认不会把历史运行产物带进沙箱
- 已重新运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime_fast -v`
  - `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 10`
  - `git diff --check`
  - 结果：contract 检查约 12 秒；快验 7 tests OK，约 9-10 秒；全量耗时分析 353 tests OK，约 9 分钟；`git diff --check` 只有历史 CRLF 提示
- 新增仓库内本地 provider 示例：
  - `examples/providers/copy_metadata_fallback_provider.py`
  - `examples/providers/pass_semantic_review_provider.py`
- provider dogfood 测试不再临时写 provider 脚本，改为直接使用仓库内示例脚本
- README / README.zh-CN / provider 文档已补充本地 provider 示例启用方式
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime_fast -v`
  - `git diff --check`
  - 结果：全部通过；快验 7 tests OK，约 10 秒

## Next Action

下一步建议继续核心主线：为真实 LLM / 本地模型 provider 做接入方案选择，或先补搜索质量评估集。日常小改动默认先跑 `python -m unittest tests.test_runtime_fast -v`，只有发布级或大范围 runtime 行为变化再跑 full suite，并使用至少 900 秒超时。

## Important Files

- `AGENTS.md`
- `TASKS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `docs/gitnexus-local-runbook.md`
- `docs/core-readiness-audit.md`
- `docs/core-dogfood-acceptance.md`
- `docs/provider-integration.md`
- `examples/providers/copy_metadata_fallback_provider.py`
- `examples/providers/pass_semantic_review_provider.py`
- `TESTS.md`
- `pyproject.toml`
- `.github/workflows/runtime-contracts.yml`
- `scripts/profile_runtime_tests.py`
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
- `skill_runtime/governance/provenance_backfill.py`
- `tests/test_runtime_governance.py`
- `skill_store/active/merge_text_files.metadata.json`
- `skill_store/staging/*.metadata.json`
- `README.md`
- `README.zh-CN.md`
- `tests/test_runtime_contracts.py`
- `tests/test_runtime_core_dogfood_acceptance.py`
- `tests/test_runtime_audit_lifecycle.py`

## Known Issues

- 核心功能目前是本地 MVP，不应宣称已经完成。
- semantic audit 默认仍使用 mock provider；已支持外部 provider 命令，但未配置真实模型时质量判断仍不够强。
- fallback distillation 默认仍使用 mock provider；已支持外部 provider 命令和本地 demo provider，但当前仓库还没有内置 OpenAI 或本地模型 provider。
- 本地 demo provider 是窄场景示例，只证明 provider hook 和闭环可运行，不能代表通用自动生成能力。
- active skill 当前只保留少量真实技能，复用价值还需要更多 dogfood 验证。
- 当前仓库已完成 GitNexus 注册，但成功依赖本机 GitNexus 安装中的临时修改，不应误判为“默认官方路径已完全无问题”。
- 未来新的 dogfood 执行默认不再改写版本管理下的 active metadata 和主索引。
- 当前会话尝试 GitNexus MCP 查询时返回 `Transport closed`，本轮已退回普通文件检索。
- 全量 runtime suite 不是失败，但当前约 9 分钟，仍不适合作为每次小改动的默认第一验证命令。
- `git diff --check` 当前仍提示 `skill_store/index.json` 和 `trajectories/demo_merge_text_files.json` 未来会按 LF 写回；这是换行提示，不是本轮新增的失败。

## Constraints

- 当前阶段仍不要开始业务功能开发。
- 不要开始业务功能开发。
- 不要把产品化收敛误当成核心功能已经完成。
- 长期上下文应优先写入项目文件，而不是聊天记录。
- 自动模式阶段报告必须使用非技术语言，帮助非程序员用户理解项目进展。
- 不要为了让测试通过而重新把测试技能放回真实 active skill 库。

## Do Not Do

- 不要依赖旧对话历史恢复项目状态。
- 不要要求旧会话再生成大段交接提示词。
- 不要在没有必要时改动业务代码。
- 不要因为小改动、单个测试通过或单个文件修改完成就打断用户。
