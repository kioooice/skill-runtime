# Tasks

## Current Focus

- 当前目标：继续做 Skill Runtime 的产品化收敛，不新增大功能
- 当前状态：已补齐最小安装入口、CI 安装步骤、MCP smoke、copy_file rollback 一致性，并完成主验证；active skill 治理清理计划已生成，等待用户拍板
- 下一步：决定是否按治理清理计划归档 fixture / duplicate 噪音技能，避免 active skill 污染搜索结果

## Todo

- [ ] 视需要执行 active skill 治理清理计划，先归档 fixture 与 duplicate 噪音技能
- [ ] 视需要把 `merge_text_files_generated` 这类 experimental active skill 从默认搜索面移出
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

## Blocked

- 无
