# Decisions

## Decision Log

### 2026-04-29 - 真实 provider 路径先采用可信本地命令契约

**Decision**

fallback distillation 和 semantic audit 的真实 provider 接入先采用外部命令契约：runtime 通过 stdin 发送结构化 JSON 请求，provider 命令通过 stdout 返回结构化 JSON 响应。未配置环境变量时继续使用内置 mock provider。

**Reason**

这样可以先打通真实 provider 的工程边界，而不把核心 runtime 绑定到某一家云服务、某种 API key 或某个本地模型实现。OpenAI、本地模型、企业内部审核器都可以包装成同一类本地命令，测试也能稳定验证。

**Impact**

- 新增 `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` 和 `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`
- 未知工作流在配置可信 provider 后可走生成、审核、入库、复用闭环
- mock provider 仍是安全默认值，不会因为这次改造自动放行模板技能
- provider 命令被视为可信本地命令，不能指向未审核脚本
- 当前还没有内置 OpenAI 或本地模型 provider，只完成了可插拔接入路径

### 2026-04-29 - mock fallback 默认不作为可自动晋级的核心能力

**Decision**

当前把 mock fallback 视为候选技能生成和提示产物，不视为可自动晋级到 active 的可靠核心能力。未知工作流如果只命中 mock fallback，必须被审核挡住，除非后续接入明确可信的真实 provider 或另行设计人工确认边界。

**Reason**

mock fallback 生成的是模板化技能，它能帮助暴露“未知工作流需要 provider”的缺口，但不能证明真实自动生成能力已经完成。如果允许这类候选直接提升，会把看似可复用但实际没有真实动作的技能放进 active 库，污染搜索和复用结果。

**Impact**

- 新增核心验收保证未知工作流进入 mock fallback 后不会自动提升
- 当前核心主线的下一步从“是否需要收紧 fallback”变为“是否接真实 provider”
- 在真实 provider 未接入前，不应宣称未知工作流自动生成已经完成

### 2026-04-28 - 核心 dogfood 验收先覆盖真实 MCP 主链路

**Decision**

第一条核心 dogfood 验收不新增业务能力，而是用 MCP host-style 调用串起现有主链路：搜索已有技能、执行、生成 observed task、从 observed task 提升为 active skill、再次复用，并检查 active 搜索结果没有 fixture-tier 污染。

**Reason**

此前已有很多单点测试，但用户关心的是核心功能本身是否建设完成。单点测试不能直接证明“从用户角度的一整条闭环能不能跑通”。先用真实 MCP 工具调用做验收，比继续补外围安装/文档更贴近核心主线。

**Impact**

- `tests.test_runtime` 会跑到新的核心 dogfood 验收
- MCP smoke 从“能构造 server”进一步扩展到“一条真实 host-style 闭环能跑通”
- 当前验收仍不证明 mock semantic audit / mock fallback provider 已经足够，下一步应补 fallback 路径验收

### 2026-04-28 - 主线从产品化收敛切回核心闭环验收

**Decision**

当前不把安装、CI、README、MCP smoke 和治理清理视为“核心功能完成”。Skill Runtime 只达到可用本地 MVP，下一步主线应回到核心闭环验收，优先证明 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 在真实 dogfood 任务上稳定成立。

**Reason**

上一阶段解决的是“别人 clone 后能装、能测、能 smoke、active skill 不被测试数据污染”的产品化基础问题，但这不能替代核心能力完成度判断。当前代码里仍存在默认 mock semantic review、默认 mock fallback distillation、轻量关键词检索、active skill 样本较少等核心缺口。

**Impact**

- 后续主线先做核心 dogfood 验收包，而不是继续扩展外围产品化事项
- 不新增大功能，先建立真实闭环的通过/失败标准
- 只有验收暴露出明确短板后，再决定升级真实 provider、搜索质量或 MCP host round-trip

### 2026-04-28 - Clone 后验证路径优先使用模块入口

**Decision**

README / README.zh-CN 中的 clone 后验证流程优先展示 `python -m skill_runtime...` 模块入口，同时保留安装后的 `skill-runtime` / `skill-runtime-mcp` 命令入口和旧脚本入口。为保证文档可执行，补齐 `skill_runtime.cli` 与 `skill_runtime.mcp_stdio` 的 `__main__` 调用，并新增回归测试。

**Reason**

安装后的 console scripts 在部分 Windows shell 中可能因为 Scripts 目录不在 `PATH` 而暂时不可见；模块入口更稳定，适合作为新用户从 clone 到验证的默认路径。但此前模块入口只可 import，直接 `python -m` 不会执行主函数，导致文档路径不可靠。

**Impact**

- 新用户可按 README 从安装一路验证到 MCP smoke 和搜索 smoke
- `python -m skill_runtime.cli search ...` 会真实输出搜索结果
- `python -m skill_runtime.mcp_stdio --help` 会真实显示帮助
- 安装后的 console scripts 和旧脚本入口继续保留

### 2026-04-28 - 提交项目规则并规范化 skill_store 文本文件

**Decision**

将 `AGENTS.md` 中已经生效的新会话接力、自动模式和 GitNexus 使用规则作为正式项目规则提交；同时按 `.gitattributes` 对 `skill_store` 下的文本文件做一次规范化，清理此前长期显示为修改状态的换行噪音。

**Reason**

工作区剩余差异里，`AGENTS.md` 是真实项目规则，不应继续悬空为本地改动；`skill_store/staging` 这批 metadata 则主要是 Windows 换行状态造成的噪音，不处理会持续干扰用户判断仓库是否真的发生了业务变化。

**Impact**

- 项目级接力和自动模式规则成为仓库内正式状态
- `skill_store` 的文本文件更符合当前 `.gitattributes` 规则
- 后续 `git status` 更容易暴露真正有意义的改动
- 没有改变 runtime 行为和业务功能

### 2026-04-28 - 治理维护动作保存索引时合并最新状态

**Decision**

对 `archive_cold`、`archive_duplicate_candidates`、`archive_fixture_skills` 以及 provenance 回填这类治理维护动作，不再在最后用一份旧的 skill 列表整包覆盖 `skill_store/index.json`。改为读取当前最新索引后按 `skill_name` 合并更新，再保存。

**Reason**

当前主线风险已经从“功能缺失”转成“维护动作之间互相覆盖”。如果一个治理动作开始后，期间又有另一项索引变化发生，最后那次整包保存就可能把中途新增或更新的索引项盖掉。

**Impact**

- 连续治理动作之间更不容易互相覆盖索引结果
- 新增了回归测试，专门覆盖“归档过程中出现晚到索引更新仍能保留”
- 现有治理 contract 不需要新增用户可见参数
- 当前完整验证已通过：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：346 tests OK

### 2026-04-28 - 将 active skill 使用统计移到本地运行状态文件

**Decision**

保留 active skill 的使用统计能力，但不再把执行产生的 `usage_count / last_used_at` 直接写回版本管理下的 `skill_store/index.json` 和 `skill_store/active/*.metadata.json`。改为把这类运行态统计写到本地 `.skill_runtime/usage.json`，并在读取 skill 索引时叠加到内存视图中。

**Reason**

当前最真实的工作区脏状态来自日常 dogfood 执行会改写版本文件，而不是代码本身真的发生了产品变更。把“技能定义”和“本地使用痕迹”拆开，既保留检索和排序需要的 usage 信号，也避免正常运行持续污染仓库状态。

**Impact**

- 正常执行 skill 后，使用统计仍会累积
- 搜索和索引读取仍能看到最新 usage 信息
- 默认不再改写版本管理下的 active metadata 和主索引文件
- 本地统计写入 `.skill_runtime/usage.json`，并通过 `.gitignore` 忽略
- 当前完整验证已通过：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：345 tests OK

### 2026-04-28 - 用仓库规则和忽略项收口本地杂项边界

**Decision**

新增仓库级 `.gitattributes`，统一 `md / py / json / toml / yml` 为 LF；同时把 `.claude/` 视为本地辅助目录加入 `.gitignore`，并将 `docs/gitnexus-local-runbook.md` 作为正式仓库文档保留，而不是继续悬空为未跟踪文件。

**Reason**

当前工作区的“脏状态”里，既有真实运行统计更新，也有 Windows 换行差异和本地辅助目录噪音。如果不先把这些边界说清楚，用户很难分辨哪些是正常运行痕迹，哪些只是本地环境噪音。

**Impact**

- 未来 clone / checkout 后，文本文件的换行规则更一致
- `.claude/` 这类本地辅助目录不再干扰仓库状态判断
- GitNexus 本机恢复说明现在正式纳入仓库，可随项目一起交接
- 当前工作区剩余差异更集中到真实运行统计和个别历史本地改动，后续更容易继续收口

### 2026-04-28 - 安装入口使用包内模块并同时保留旧脚本兼容

**Decision**

将 CLI 和 MCP stdio 启动逻辑收敛到 `skill_runtime.cli` 与 `skill_runtime.mcp_stdio` 两个包内模块里，通过 `pyproject.toml` 暴露正式命令入口 `skill-runtime` / `skill-runtime-mcp`；同时保留 `scripts/skill_cli.py` 与 `scripts/skill_mcp_server.py` 作为薄包装兼容层，不要求现有仓库内用法一次性迁移。

**Reason**

当前项目已经具备功能，但安装后仍主要依赖仓库脚本路径，产品感不完整，而且 `pyproject.toml` 只列顶层包，对安装产物也不够稳。把正式入口收回包内模块，同时保留旧脚本兼容，是收口成本最小、对现有使用者最不打扰的路径。

**Impact**

- 安装后可直接使用：
  - `skill-runtime`
  - `skill-runtime-mcp`
- 也可用更稳的模块入口：
  - `python -m skill_runtime.cli`
  - `python -m skill_runtime.mcp_stdio`
- 旧入口仍兼容：
  - `python scripts/skill_cli.py`
  - `python scripts/skill_mcp_server.py`
- `pyproject.toml` 已改为递归发现 `skill_runtime*` 包，降低安装缺子包风险
- 本轮验证已覆盖：
  - `python -m pip install -e .`
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 安装后入口 `--help`

### 2026-04-28 - runtime 测试默认使用隔离副本而不是直接写真实仓库

**Decision**

将 `RuntimeTestCase` 的默认运行根切到临时隔离副本；只有少量需要验证目录生成行为的测试模块，才把 `ROOT` 显式映射到隔离副本。与此同时，让搜索、治理和部分生命周期测试自己准备需要的样本技能，而不是继续依赖历史测试留下的 active skill 污染状态。

**Reason**

当前主线目标之一是“别人 clone 后能验证”，而不是“测试一跑就把仓库越跑越脏”。如果验证默认会改写真实 `skill_store`、`observed_tasks` 或隐式依赖旧的脏数据，那么 CI 和本地验证都不稳定，active library 清理后的产品承诺也站不住。

**Impact**

- `tests.test_runtime` 现在默认在隔离副本里运行 runtime service、CLI 和 MCP smoke
- 目录生成类测试仍能在隔离副本里按原样验证输出文件行为
- 搜索与治理测试会自己播种 `experimental / fixture` 样本，不再要求真实 active library 被测试技能污染
- `python -m unittest tests.test_runtime -v` 当前已通过 342 个测试
- 仓库里此前已经存在的历史验证产物仍需后续单独清理，但本轮修复后默认验证不应继续扩大这类污染

### 2026-04-28 - active skill 清理后立即重建索引

**Decision**

在完成 active skill 归档清理后，立即重建 active index，而不是只依赖前面的归档动作逐步更新索引状态。

**Reason**

这样可以确保治理报告和搜索结果直接对齐到文件系统里的真实 active skill 集合，避免“文件已归档，但旧索引仍把测试技能当 active”的残留污染。

**Impact**

- 当前 active library 已收敛到 2 个 stable 技能：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 当前治理报告无 duplicate candidates
- 当前搜索结果不再被 fixture / demo / alias-rule 技能污染

### 2026-04-28 - active skill 清理优先保留 dogfood 与 canonical 技能

**Decision**

执行 active skill 清理时，优先归档 fixture、demo、rule-test、alias-rule、promote-smoke 类技能，明确保留真实 dogfood 技能和 canonical 技能。

**Reason**

这样可以先解决“active skill 污染搜索结果”的产品问题，同时避免误删仍有真实使用价值的主线技能。

**Impact**

- 已保留：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 已归档大量 fixture / duplicate / experimental 噪音技能
- active skill 默认搜索面已大幅收敛

### 2026-04-28 - 本轮先做产品化收敛，不新增大功能

**Decision**

本轮继续围绕安装、CI、MCP smoke、rollback 一致性和 active skill 治理做产品化收敛，不新增新的大能力面。

**Reason**

当前项目已经具备可用主线，下一步更重要的是让别人 clone 后能装起来、CI 能验证、MCP 能最小 smoke、搜索结果不被测试技能污染。

**Impact**

- 已新增最小 `pyproject.toml`
- README 中已有本地安装与最小验证步骤
- CI 会先执行 `python -m pip install -e .`
- 当前阶段剩余的主要拍板项是 active skill 治理清理

### 2026-04-28 - copy_file 复用现有 delete_created_file 回滚策略

**Decision**

不扩展 `rollback_operations` 去新增 `delete_copied_file`，而是把 `RuntimeTools.copy_file` 在“新建复制目标”场景下的 rollback strategy 改为现有的 `delete_created_file`。

**Reason**

这是更小、更稳定、对现有 contract 破坏最少的方案，同时能让 rollback hint 与实际自动回滚能力保持一致。

**Impact**

- 新建复制目标时，自动回滚会删除复制出来的文件
- 覆盖已有目标时，仍保持 `manual_restore_required`
- MCP / CLI / service 的 rollback 承诺现在一致

### 2026-04-28 - 当前阶段先收口基础设施，后续直接使用 GitNexus

**Decision**

当前阶段不再继续深挖 GitNexus 的长期底层修复，而是先把已经可用的结果收口，后续直接在真实任务中使用当前仓库已建好的 GitNexus 能力。

**Reason**

这样可以避免继续在低价值的底层整理上投入时间，先把已经打通的能力转化为后续任务中的实际效率收益。

**Impact**

- 当前 GitNexus 基础设施阶段视为完成
- 后续如果没有新的明确需求，不继续扩展本机补丁范围
- 新会话恢复后，默认优先使用当前已建好的 GitNexus 索引辅助任务

### 2026-04-28 - 将本机 GitNexus 补丁整理为仓库内 runbook

**Decision**

把当前成功依赖的 GitNexus 本机补丁点、验证方式和恢复步骤写进仓库内文档，而不是只保留在聊天记录里。

**Reason**

这样在重装、升级、换机器或开新会话后，可以直接按文件恢复，不需要再从零回忆这次排查过程。

**Impact**

当前仓库已经有一份可直接复用的操作说明：
- `docs/gitnexus-local-runbook.md`
- 后续若 GitNexus 重装、升级或迁移机器，可先按 runbook 恢复，再判断是否需要继续做更长期修复

### 2026-04-28 - 当前仓库采用本机补丁加单线程方式完成 GitNexus 注册

**Decision**

当前仓库的 GitNexus 索引先采用“本机最小补丁 + 单线程索引”的方式完成注册，而不是继续强求默认路径一次解决所有底层问题。

**Reason**

这样可以先拿到一个可用结果，确认仓库已经能被 GitNexus 查询，再决定是否继续处理更底层、更通用的长期修复。

**Impact**

当前 `vibe` 仓库已经成功注册并处于 `up-to-date` 状态；但这次成功依赖本机 GitNexus 安装中的临时修改，包括：
- Python 重解析路径补充 tree-sitter `bufferSize`
- `runFullAnalysis` 透传 `skipWorkers`
- 暂时跳过 VECTOR 扩展加载
- 使用单线程索引路径完成注册

### 2026-04-28 - 先拆开验证“分析阶段”和“写库阶段”

**Decision**

将 GitNexus 的“代码分析”和“LadybugDB 写入”拆开分别验证，而不是继续只跑整条 `gitnexus analyze` 命令。

**Reason**

这样可以快速判断问题是在前半段代码理解，还是后半段数据库落盘。当前结果已经证明：前半段在单线程模式下可以完整跑通，真正阻塞点在 LadybugDB / lbug 的写入阶段。

**Impact**

后续排查重点从 Python 解析切换到 LadybugDB / lbug。当前最值得验证的是：是否因为 VECTOR 扩展加载副作用导致后续 `COPY` 失败。

### 2026-04-28 - 先做本机最小补丁验证 GitNexus 根因

**Decision**

在不改业务代码的前提下，先对本机 GitNexus 安装做最小补丁验证：给 Python scope capture 的重解析路径补上 tree-sitter `bufferSize`，并打通 `runFullAnalysis -> runPipelineFromRepo` 的选项透传，用于验证 `skipWorkers`。

**Reason**

当前问题首先需要确认是仓库内容问题，还是 GitNexus 自身实现问题。最小补丁可以快速证明根因，避免在业务仓库里做无价值试错。

**Impact**

已确认第一层失败并非仓库代码语法问题，而是 GitNexus 的 Python 重解析路径缺少 `bufferSize`；在单线程模式下，索引流程已能越过原来的 Python 失败点并推进到 LadybugDB / lbug 写入阶段。后续仍需继续排查写库阶段问题。

### 2026-04-28 - GitNexus 先全局接入，再按仓库逐步验证

**Decision**

先将 GitNexus 安装并接入 Codex 全局配置，让它成为默认可用能力；如果某个仓库索引失败，不阻塞其他工作，先把失败点记录到项目状态文件中，再决定是否专项排查。

**Reason**

这样可以先完成“全局可用”这个基础能力，同时避免因为单个仓库的索引异常卡住整个流程。

**Impact**

后续在支持正常索引的仓库中可以直接优先使用 GitNexus；当前 `vibe` 仓库则需要先处理 `gitnexus analyze` 的失败问题，短期内仍可能回退到普通文件检索。

### 2026-04-28 - 自动模式按阶段汇报且面向非技术用户

**Decision**

自动模式不再采用“持续执行但全程静默”的方式。改为按有意义阶段连续推进，并在每个阶段结束后输出面向非技术用户的阶段报告，同时更新 `HANDOFF.md`、`TASKS.md`、`DECISIONS.md`。

**Reason**

用户没有系统编程基础，仅靠技术术语或零散进度无法判断项目实际进展。阶段报告需要直接解释“做了什么、带来了什么能力、有什么风险、下一步怎么选”，这样用户才能拍板。

**Impact**

后续自动模式下，Codex 需要以产品和结果导向组织汇报，而不是以文件、测试或代码细节为主；同时每轮阶段结束都要同步刷新仓库内状态文件，保证新会话可接力。

### 2026-04-28 - 使用仓库内状态文件承接新会话上下文

**Decision**

将 `HANDOFF.md` 作为新会话默认入口，将 `TASKS.md` 和 `DECISIONS.md` 作为辅助状态文件，要求 Codex 在继续任务时优先读取这些文件，而不是依赖旧对话历史。

**Reason**

这样可以把长期上下文沉淀在仓库内，降低对单个聊天线程的依赖，并避免每次开新会话都重新整理长篇交接提示。

**Impact**

后续每个重要阶段、决策和阻塞都需要同步更新这些文件；新会话可以直接用简短启动语恢复上下文，但前提是状态文件保持最新。
