# Tasks

## Current Focus

- 当前目标：从产品化收敛切回 Skill Runtime 核心功能完成度收敛
- 当前状态：已新增第一条核心 dogfood 验收路径，覆盖 MCP 搜索、执行、observed task、提升、复用，并确认 active 搜索不出现 fixture-tier 污染；架构检查、contract 检查和 349 个 runtime 测试已通过
- 下一步：补第二条核心验收路径，专门覆盖未知工作流进入 fallback distillation 后应如何处理，从而决定是接真实 provider 还是先收紧 fallback 晋级

## Todo

- [ ] 补一条未知工作流 / fallback distillation 的核心验收路径
- [ ] 视验收结果决定是否优先升级真实 semantic audit / fallback provider
- [ ] 视验收结果决定是否补搜索质量评估集
- [ ] 视需要继续收敛 GitNexus 本机补丁为更长期方案
- [ ] 视需要继续统一其余治理写路径的索引刷新策略，减少未来新增治理入口时出现行为分叉

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
- [x] 将 active skill 使用统计写到本地 `.skill_runtime/usage.json`，避免正常执行继续改写版本管理下的技能定义文件
- [x] 更新 README / README.zh-CN，说明本地 usage 状态文件的存放位置与忽略策略
- [x] 重新运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`，共通过 345 个测试
- [x] 为治理维护动作补齐索引合并保存策略，减少连续治理动作互相覆盖索引结果的风险
- [x] 新增并通过“归档过程中出现晚到索引更新也能保留”的回归测试
- [x] 重新运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`，共通过 346 个测试
- [x] 将 `AGENTS.md` 中的新会话接力、自动模式、GitNexus 使用规则正式纳入仓库提交
- [x] 按 `.gitattributes` 对 `skill_store` 文本文件做一次规范化，清理历史换行噪音
- [x] 收口 README / README.zh-CN 中的 clone 后验证流程，覆盖安装、检查、测试、MCP smoke 和搜索 smoke
- [x] 修复 `python -m skill_runtime.cli` 与 `python -m skill_runtime.mcp_stdio` 模块入口，确保 README 推荐的模块命令真实可运行
- [x] 新增模块入口回归测试
- [x] 完成核心功能完成度盘点，并新增 `docs/core-readiness-audit.md`
- [x] 新增第一条核心 dogfood 验收路径：MCP 搜索、执行、记录、提升、复用、搜索污染检查
- [x] 运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`，共通过 349 个测试

## Blocked

- 无
