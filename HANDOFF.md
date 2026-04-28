# Handoff

## Current State

已完成一轮 Skill Runtime 产品化收敛，并已转入核心功能完成度收敛。当前结论：项目已经有可用本地 MVP，核心闭环 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 在代码结构上存在，CLI / MCP / 测试 / 治理基础也已成型；但核心功能不能算建设完成。第一条核心 dogfood 验收路径已新增：通过 MCP host-style 调用完成搜索、执行、observed task、提升、复用，并确认 active 搜索没有 fixture-tier 污染。剩余主要短板是：semantic audit 默认仍是 mock provider、未知任务 fallback distillation 默认仍是 mock provider、搜索质量仍是轻量关键词评分、active skill 库样本仍少。

## Last Completed

本轮已完成：
- 新增 `docs/core-dogfood-acceptance.md`，记录核心 dogfood 验收范围
- 新增 `tests/test_runtime_core_dogfood_acceptance.py`
- 将核心 dogfood 验收接入 `tests.test_runtime`
- 第一条验收路径覆盖：MCP 搜索、执行、observed task、提升、复用、active 搜索无 fixture-tier 污染
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：349 tests OK
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

## Next Action

继续补核心 dogfood 验收包的第二条路径：专门覆盖未知工作流进入 fallback distillation 后应如何处理。目标是判断下一步应优先接真实 provider，还是先把 mock fallback 的晋级路径收紧，避免把模板技能误提升为 active。

## Important Files

- `AGENTS.md`
- `TASKS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `docs/gitnexus-local-runbook.md`
- `docs/core-readiness-audit.md`
- `docs/core-dogfood-acceptance.md`
- `pyproject.toml`
- `.github/workflows/runtime-contracts.yml`
- `skill_runtime/execution/runtime_tools.py`
- `skill_runtime/cli.py`
- `skill_runtime/mcp_stdio.py`
- `tests/test_runtime_mcp_smoke.py`
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

## Known Issues

- 核心功能目前是本地 MVP，不应宣称已经完成。
- semantic audit 默认仍使用 mock provider，质量判断还不够强。
- fallback distillation 默认仍使用 mock provider，未知任务自动生成能力还没有真实闭环。
- active skill 当前只保留少量真实技能，复用价值还需要更多 dogfood 验证。
- 当前仓库已完成 GitNexus 注册，但成功依赖本机 GitNexus 安装中的临时修改，不应误判为“默认官方路径已完全无问题”。
- 未来新的 dogfood 执行默认不再改写版本管理下的 active metadata 和主索引。

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
