# Tasks

## Current Focus

- 当前目标：继续做 Skill Runtime 的产品化收敛，不新增大功能
- 当前状态：已完成测试运行隔离收敛；`tests.test_runtime` 的 342 个测试已通过，默认验证路径不再依赖被污染的 active skill 库，也不再默认把新的执行痕迹写回真实仓库
- 下一步：处理仓库里已经存在的历史验证产物和忽略策略，例如清理旧的 `observed_tasks` / `skill_store/staging` 产物，或补一层更明确的本地产物忽略约定

## Todo

- [ ] 评估并清理仓库中已有的历史验证产物，避免旧脏数据继续干扰状态判断
- [ ] 视需要补充本地产物忽略策略，例如 `skill_runtime.egg-info/`
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
- [x] 将 runtime 测试默认运行根切到隔离副本，避免验证过程继续污染真实仓库
- [x] 为搜索 / 治理 / 生命周期测试补齐自带样本，移除对历史污染 active skill 库的隐式依赖
- [x] 重新运行 `python -m unittest tests.test_runtime -v` 并通过 342 个测试

## Blocked

- 无
