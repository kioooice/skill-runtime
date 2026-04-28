# Tasks

## Current Focus

- 当前目标：继续做 Skill Runtime 的产品化收敛，不新增大功能
- 当前状态：已补齐安装后的正式命令入口，并进一步收口仓库边界：新增换行规范、忽略本地 `.claude/` 辅助目录，并将 GitNexus 本机 runbook 作为正式仓库文档保留；`tests.test_runtime` 当前为 344 个测试并已通过
- 下一步：优先转向治理并行保护，避免多个治理动作并行后出现索引状态被后一次保存覆盖；工作区剩余的主要差异已收敛到真实运行统计和个别历史本地改动

## Todo

- [ ] 视需要补一层更稳的治理维护顺序保护，避免并行维护动作覆盖索引状态
- [ ] 视需要进一步收敛 active skill 使用统计写回策略，避免真实仓库因 dogfood 执行而持续显脏
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
- [x] 为安装配置补齐递归包发现，避免只打进顶层 `skill_runtime`
- [x] 为安装后使用补齐正式命令入口：`skill-runtime` / `skill-runtime-mcp`
- [x] 保持仓库内 `python scripts/skill_cli.py` / `python scripts/skill_mcp_server.py` 旧入口继续兼容
- [x] 更新 README / README.zh-CN，补充安装后命令入口和模块入口说明
- [x] 运行 `pip install -e .`、两个检查脚本、344 个 runtime 测试，以及安装后入口 help 验证
- [x] 为仓库补充 `.gitattributes` 换行规范，减少 Windows 下的伪脏改动噪音
- [x] 忽略本地 `.claude/` 辅助目录，并将 GitNexus 本机 runbook 作为正式仓库文档保留

## Blocked

- 无
