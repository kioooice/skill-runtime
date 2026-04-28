# Tasks

## Current Focus

- 当前目标：继续做 Skill Runtime 的产品化收敛，不新增大功能
- 当前状态：已完成 active skill 治理清理与重建索引；当前 active 只剩 2 个 stable 技能，治理报告无重复候选，搜索结果不再被测试技能污染
- 下一步：决定是否继续收敛治理层的小缺口，例如避免治理报告在并行维护动作下出现旧索引视图，或先转入下一项产品化收口任务

## Todo

- [ ] 视需要补一层更稳的治理维护顺序保护，避免并行维护动作覆盖索引状态
- [ ] 视需要继续收敛 GitNexus 本机补丁为更长期方案

## In Progress

- [ ] 

## Done

- [x] 初始化 AGENTS.md / TASKS.md / DECISIONS.md / HANDOFF.md
- [x] 将自动模式阶段汇报规则沉淀为项目默认规则
- [x] 将 GitNexus 安装到 Codex 全局环境并接入全局配置
- [x] 为当前仓库成功建立 GitNexus 索引并完成注册
- [x] 将 GitNexus 本机补丁点与恢复步骤整理成仓库内 runbook
- [x] 收口当前 GitNexus 基础设施阶段，后续默认直接用于真实任务
- [x] 为仓库补齐最小 `pyproject.toml` 与本地安装说明
- [x] 为 CI 增加 `python -m pip install -e .` 安装步骤
- [x] 增加最小 MCP smoke 测试并接入 `tests.test_runtime`
- [x] 修复 `RuntimeTools.copy_file` rollback hint 与 `RuntimeService.rollback_operations` 支持策略不一致的问题
- [x] 运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`
- [x] 生成 active skill 治理清理计划并保留 dogfood skill
- [x] 执行 active skill 治理清理，保留 `merge_text_files` 与 `archive_log_files_dogfood`
- [x] 重建 active index，使治理报告与搜索结果同步到清理后的真实状态

## Blocked

- 无
