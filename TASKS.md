# Tasks

## Current Focus

- 当前目标：从产品化收敛切回 Skill Runtime 核心功能完成度收敛
- 当前状态：已新增外部命令型 fallback / semantic provider 接入路径、仓库内本地 demo provider、DeepSeek provider 示例、测试分层与第一轮全量测试提速；已用真实 DeepSeek API 验证完整 provider dogfood 闭环，确认生成、审核、入库、复用可跑通；DeepSeek fallback 本地质量门禁已能阻止坏输出进入 staging，并已支持失败后自动返修一次；搜索质量已有最小评估脚本和快验覆盖
- 下一步：继续增加真实 dogfood 技能样本，或扩大搜索质量评估样本集

## Todo

- [ ] 继续增加真实 dogfood 技能样本
- [ ] 视需要扩大搜索质量评估样本集
- [ ] 视需要继续优化 full runtime suite 剩余慢点，优先看 MCP/provider dogfood 和生成规则组合测试
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
- [x] 新增第二条核心 dogfood 验收路径：未知工作流进入 mock fallback 后不会自动提升为 active
- [x] 运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`，共通过 350 个测试
- [x] 新增外部命令型 fallback provider，支持未知工作流由可信外部命令生成候选 skill
- [x] 新增外部命令型 semantic provider，支持外部审核器放行或阻止候选 skill
- [x] 新增 provider dogfood 验收：未知工作流经外部 provider 生成、审核、promote、reuse
- [x] 新增 semantic provider 阻断测试：外部审核器返回 high issue 时禁止 promote
- [x] 运行 `check_mcp_architecture`、`check_runtime_contracts` 和 `tests.test_runtime`，共通过 352 个测试
- [x] 新增日常快验套件 `tests.test_runtime_fast`，覆盖 MCP smoke、隔离运行、核心 dogfood、mock fallback 安全边界和外部 provider 闭环
- [x] 新增慢测试定位脚本 `scripts/profile_runtime_tests.py`
- [x] README / README.zh-CN / TESTS / AGENTS 已改为优先提示快验，full suite 标注为慢速全量验证
- [x] CI 已增加快验步骤，并保留 full runtime suite
- [x] 已运行快验：7 个测试约 10 秒通过
- [x] 已运行全量耗时分析：352 个测试约 11 分钟通过，最慢单项约 47 秒
- [x] 优化 runtime contract 检查沙箱复制，避免默认复制历史 observed task 和 output
- [x] 新增回归测试，保证 contract 检查默认不带入历史运行产物
- [x] 已重新运行架构检查、contract 检查、快验和全量耗时分析：353 个测试约 9 分钟通过，contract 检查约 12 秒
- [x] 新增仓库内本地 demo provider，覆盖 fallback 生成和 semantic review 两个 provider hook
- [x] provider dogfood 测试改为使用仓库内示例脚本，不再只依赖测试临时脚本
- [x] README / README.zh-CN / provider 文档已补充本地 provider 示例启用方式
- [x] 已重新运行架构检查、contract 检查、快验和 `git diff --check`
- [x] 新增 DeepSeek fallback provider 和 DeepSeek semantic review provider 示例脚本
- [x] DeepSeek provider 默认使用 `deepseek-v4-flash`，并通过环境变量读取 API key
- [x] 新增本地假 DeepSeek API 契约测试，避免测试依赖真实 key 或真实网络
- [x] README / README.zh-CN / provider 文档已补充 DeepSeek 配置方式和 key 不入库要求
- [x] 已重新运行架构检查、contract 检查、快验和 `git diff --check`；快验 9 个测试通过
- [x] 已按用户要求使用真实 DeepSeek API 做 live smoke
- [x] 已确认 DeepSeek API 可连通，fallback / semantic provider 都能返回结果
- [x] 已修复 DeepSeek fallback response 缺少非核心 `reason` 字段时直接失败的问题
- [x] 已加严 DeepSeek provider prompt，并补测试确认关键约束会发送给模型
- [x] 已确认用户提供的 DeepSeek key 未写入仓库文件
- [x] 为 DeepSeek fallback 输出增加本地质量门禁：`run`、docstring 结构、runtime tool 调用、必要 kwargs、runtime tool 调用签名
- [x] 补充 DeepSeek 门禁测试：低质量候选、schema kwargs 缺失、runtime tool 签名错误、双重转义代码字符串
- [x] 最新真实 live smoke 已证明坏签名输出会在 fallback 阶段被拦截，不再进入 staging / promote
- [x] 为 DeepSeek fallback provider 增加一次自动修复请求，质量门禁失败时把失败原因发回 DeepSeek 再验一次
- [x] 补充 DeepSeek 返修测试：一次返修成功，以及显式关闭返修时只失败不重试
- [x] 重新运行架构检查、runtime contract 检查、快验和真实 DeepSeek live smoke；真实 API 本轮返回了可直接通过门禁的候选技能
- [x] 新增 `scripts/smoke_deepseek_provider_loop.py`，把真实 DeepSeek 生成、审核、入库、复用 smoke 固化为可复用脚本
- [x] 修正 DeepSeek fallback 门禁中的 `write_json` 签名契约：真实参数是 `payload`，不是 `data`
- [x] 真实 DeepSeek provider dogfood 闭环通过：生成、审核、提升、复用均成功，并验证复制文件与 metadata sidecar
- [x] 新增 `scripts/evaluate_search_quality.py`，为当前 active 技能建立最小搜索质量评估入口
- [x] 将搜索质量基线接入 `tests.test_runtime_fast`

## Blocked

- 无
