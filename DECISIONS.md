# Decisions

## Decision Log

### 2026-04-29 - 第六个真实 dogfood 技能选择目录文本清洗

**Decision**

新增 `directory_text_cleanup_dogfood` 作为第六个真实 active dogfood skill，并配套嵌套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

active 库已有单文件文本替换，但还缺少“批量清理一个目录里的文本文件”这种更接近真实资料整理的场景。目录文本清洗能复用已有 `directory_text_transform` 规则，不新增大功能，同时覆盖 clean / normalize / trailing whitespace 这类常见用户表达。

**Impact**

- active skill 数量从 5 增加到 6
- 搜索质量基线从 11 个检查扩展到 13 个检查
- 快验新增目录文本清洗 dogfood 搜索与执行覆盖
- 当前清洗语义是去掉文件末尾多余空白并统一最终换行，不是逐行格式化；后续如果要做逐行清洗，需要单独设计规则或明确作为新能力

### 2026-04-29 - 第五个真实 dogfood 技能选择单文件文本替换

**Decision**

新增 `text_replace_dogfood` 作为第五个真实 active dogfood skill，并配套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

active 库已有文本合并、日志归档、JSON 转 CSV 和目录 JSON 批量转 CSV，但还缺少最常见的“改一个文件里的某段文字”工作流。单文件文本替换能复用已有 `text_replace` 规则，不新增大功能，同时覆盖普通用户常说的 replace / update word 表述。

**Impact**

- active skill 数量从 4 增加到 5
- 搜索质量基线从 9 个检查扩展到 11 个检查
- 快验新增单文件文本替换 dogfood 搜索与执行覆盖
- 由于 `merge_text_files` 使用次数很高，文本类查询可能被 usage boost 干扰；本轮通过更明确的 replace / update / word 描述守住了当前查询命中

### 2026-04-29 - 第四个真实 dogfood 技能选择目录 JSON 批量转 CSV

**Decision**

新增 `directory_json_to_csv_dogfood` 作为第四个真实 active dogfood skill，并配套嵌套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

第三个样本已经覆盖单个 JSON 文件转 CSV，但 active 库仍缺少“批量处理整个文件夹”的真实样本。目录 JSON 批量转 CSV 能复用已有 `directory_json_to_csv` 规则，不需要新增大功能，同时可以验证嵌套目录保持相对结构这一类更接近真实工作的场景。

**Impact**

- active skill 数量从 3 增加到 4
- 搜索质量基线从 7 个检查扩展到 9 个检查
- 快验新增目录 JSON 批量转 CSV dogfood 搜索与执行覆盖
- 新增样本仍属于文件类工作流，后续还需要文本清洗、替换等不同类型 dogfood 扩大复用证明

### 2026-04-29 - 第三个真实 dogfood 技能选择 JSON 转 CSV

**Decision**

新增 `json_to_csv_dogfood` 作为第三个真实 active dogfood skill，并配套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

当前 active 库已有文本合并和日志归档，仍缺少结构化数据转换样本。JSON 转 CSV 属于常见文件工作流，能复用已有 `json_to_csv` 规则，不需要新增大功能或新规则。

**Impact**

- active skill 数量从 2 增加到 3
- 搜索质量基线从 5 个检查扩展到 7 个检查
- 快验新增 JSON 转 CSV dogfood 搜索与执行覆盖
- active 库仍然较小，后续还需要更多真实 dogfood 样本证明复用价值

### 2026-04-29 - 搜索分词过滤英文停用词

**Decision**

`SkillIndex` 搜索分词时过滤常见英文停用词，例如 `a`、`an`、`in`、`to`、`with`。无关查询不应因为这些低价值词返回弱相关技能。

**Reason**

搜索质量基线发现，`send an email newsletter campaign` 虽然不会产生推荐技能，但仍会因为 `an` 这类停用词返回 `merge_text_files` 的弱匹配结果。这会让用户误以为系统理解了无关需求。

**Impact**

- 无关查询更容易得到空结果
- 现有 merge/archive 正向查询仍通过
- 这是轻量修正，不替代后续更完整的搜索质量评估或语义检索

### 2026-04-29 - 搜索质量先用小型基线评估守住当前能力

**Decision**

新增 `scripts/evaluate_search_quality.py`，用少量代表性查询检查当前 active skill 能否命中预期技能，并把该基线接入 `tests.test_runtime_fast`。

**Reason**

当前搜索仍是轻量关键词评分，不适合立刻大改算法。先建立可重复评估入口，可以在后续增加 dogfood 技能或调整评分时快速发现明显退化。

**Impact**

- 快验会覆盖搜索质量基线
- 当前基线只覆盖现有两个真实 active 技能，不代表完整搜索质量评测
- 后续如果 active 技能库扩充，应同步增加评估样本

### 2026-04-29 - DeepSeek live 闭环 smoke 固化为临时沙箱脚本

**Decision**

新增 `scripts/smoke_deepseek_provider_loop.py` 作为手动 live smoke 入口。脚本要求 `DEEPSEEK_API_KEY` 从环境变量读取，自动创建临时 runtime 沙箱，配置 DeepSeek fallback 和 semantic provider，执行生成、审核、提升、复用，并验证复制文件和 metadata sidecar。

**Reason**

一次性手工命令虽然能证明 API 可用，但不适合后续重复验证。把完整闭环固化为脚本，可以让真实 provider 验收变成可复用操作，同时避免污染仓库真实 active skill 库。

**Impact**

- DeepSeek 完整 provider dogfood 现在有明确手动验证入口
- 该脚本不进 CI，因为它依赖真实 API key 和网络
- smoke 过程中发现并修正了 `write_json` 签名契约错误：真实参数是 `payload`，不是 `data`
- 最新真实 smoke 结果：生成、审核、提升、复用均通过

### 2026-04-29 - DeepSeek fallback 失败时允许一次自动返修

**Decision**

DeepSeek fallback provider 在本地质量门禁失败后，默认把具体失败原因和上一版候选 JSON 发回 DeepSeek，请模型修复一次；修复后的候选仍必须通过同一套本地门禁。`DEEPSEEK_REPAIR_ATTEMPTS=0` 可关闭返修。

**Reason**

真实 live smoke 已证明 DeepSeek 会偶发生成调用签名错误的代码。只拦截会保证安全，但用户每次都需要手工重试；允许一次受控返修，可以用本地门禁的具体错误指导模型修正，同时仍避免坏候选进入 staging / promote。

**Impact**

- 默认多一次 DeepSeek API 调用，仅在首次候选未过门禁时发生
- 修复不绕过本地门禁，失败后仍明确退出
- 快验新增一次返修成功和返修关闭两个回归测试
- 真实 API 本轮 smoke 返回了可直接通过门禁的候选，没有触发返修

### 2026-04-29 - DeepSeek fallback 输出必须先过本地质量门禁

**Decision**

DeepSeek fallback provider 在返回生成代码前，必须先通过本地质量门禁。门禁检查 Python 语法、`run(tools, **kwargs)` 入口、三段式 docstring、轨迹对应 runtime tool 调用、`input_schema` 声明的 kwargs，以及 `RuntimeTools` 常用方法的真实调用签名。

**Reason**

真实 live smoke 发现 DeepSeek 会生成看似合理但运行必失败的代码，例如 `tools.copy_file(destination_path=...)` 或 `tools.write_json(metadata_path=...)`。这些问题不能等到 promote 后复用时才发现，必须在 fallback provider 返回前就拦住。

**Impact**

- 坏输出不再进入 staging / audit / promote
- 快验新增 DeepSeek 质量门禁回归测试
- 当前门禁只负责拦截，不负责自动修复
- 下一步应增加一次修复请求，用门禁失败原因指导 DeepSeek 重新输出

### 2026-04-29 - DeepSeek live smoke 后先补本地质量门禁

**Decision**

DeepSeek provider 已经真实连通，但暂不把它标记为稳定核心闭环能力。下一步先为 DeepSeek fallback 输出增加本地质量门禁，至少检查生成代码是否包含 `run`、docstring 结构、轨迹对应 runtime tool 调用和必要 kwargs；不满足时应失败或触发一次修复请求，而不是继续盲目 promote / reuse。

**Reason**

真实 live smoke 结果显示模型输出有波动：出现过通过审核、审核挡住、以及 promote 后复用未产出目标文件的情况。继续重试只会消耗额度，不能提升稳定性。把可验证的结构要求放在本地门禁里，比完全依赖模型自觉遵守 prompt 更可靠。

**Impact**

- DeepSeek API 接入层可继续保留
- 当前不能宣称 DeepSeek provider 端到端稳定可用
- 后续工作重点从“能否调用 API”转为“模型输出能否被本地验证和修复”
- 本轮确认用户提供的 key 没有写入仓库文件

### 2026-04-29 - DeepSeek 接入采用命令型 provider 示例，不保存 API key

**Decision**

新增 `examples/providers/deepseek_fallback_provider.py` 和 `examples/providers/deepseek_semantic_review_provider.py`，通过 DeepSeek OpenAI-compatible Chat Completions API 接入 fallback 生成和 semantic review。默认模型为 `deepseek-v4-flash`，API key 只从 `DEEPSEEK_API_KEY` 环境变量读取，不写入仓库、文档示例或测试。

**Reason**

项目已有命令型 provider 契约，继续沿用这个边界能用最小改动接入真实模型，同时不把 runtime 核心绑定死到某一家 SDK 或新增依赖。用户提供的 key 已出现在聊天中，不能再沉淀到项目文件里。

**Impact**

- DeepSeek provider 可以通过 `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` 和 `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD` 启用
- 测试使用本地假 DeepSeek API 验证请求格式和响应解析，不依赖真实 key 或真实网络
- 后续 live smoke 需要用户先在本地环境设置轮换后的 `DEEPSEEK_API_KEY`
- 如果 DeepSeek 返回质量不稳定，下一步需要补 provider 输出质量约束或更严格的审核边界

### 2026-04-29 - 先用仓库内本地 demo provider 固化 provider 接口闭环

**Decision**

新增仓库内本地 demo provider：`examples/providers/copy_metadata_fallback_provider.py` 和 `examples/providers/pass_semantic_review_provider.py`。现有 provider dogfood 测试改为直接调用这些示例脚本，而不是在测试过程中临时写 provider 脚本。

**Reason**

上一阶段已经有外部命令 provider 契约，但新用户 clone 后仍看不到一个可直接运行的 provider 后端示例。把最小 provider 示例放进仓库，可以证明真实 provider hook 从配置、生成、审核、入库到复用都可运行，同时不引入云 API key、新依赖或更大的功能面。

**Impact**

- fresh clone 用户可直接按文档配置本地 demo provider
- 快验中的 provider dogfood 覆盖仓库内真实示例脚本
- 本地 demo provider 只覆盖窄场景文件复制和 metadata sidecar，不代表通用 LLM 生成能力
- 下一步仍需选择是否接 OpenAI、本地模型，或继续保持 provider 命令契约由宿主自带

### 2026-04-29 - Contract 检查沙箱默认不复制历史运行产物

**Decision**

`scripts/check_runtime_contracts.py` 的隔离沙箱默认只复制 contract 验证真正需要的 `demo`、`skill_store`、`trajectories`，并创建空的 `audits`、`observed_tasks`、`output` 目录；只有显式传入 `copy_runtime_history=True` 时才复制历史运行产物。测试沙箱复制 `skill_store` 时也跳过 `__pycache__`。

**Reason**

全量测试反复超时的最大慢点不是业务逻辑，而是 contract 检查每次都复制大量历史 observed task、output 和缓存文件。默认不复制这些历史产物，可以保持验证语义不变，同时大幅降低本地文件复制成本。

**Impact**

- `check_runtime_contracts.py` 从约 47-52 秒降到约 12 秒
- full runtime suite 从约 11 分钟降到约 9 分钟
- 新增回归测试保证默认隔离沙箱不会把历史运行产物带进验证
- 如果未来确实需要验证历史运行产物复制行为，可显式启用 `copy_runtime_history=True`

### 2026-04-29 - Runtime 验证拆分快验和全量慢验

**Decision**

新增 `tests.test_runtime_fast` 作为日常快验入口，保留 `tests.test_runtime` 作为发布级全量慢验入口；新增 `scripts/profile_runtime_tests.py` 用于定位慢测试。README、TESTS、AGENTS 和 CI 都明确区分两类验证。

**Reason**

全量 runtime suite 当前约 11 分钟，继续把它当作每次小改动的默认验证会导致本地执行反复撞短超时，也会拖慢反馈。快验保留最关键的用户闭环和安全边界，让日常迭代先得到快速结果。

**Impact**

- 日常验证可先跑 `python -m unittest tests.test_runtime_fast -v`，当前约 10 秒
- 全量验证仍跑 `python -m unittest tests.test_runtime -v`，当前约 11 分钟
- 慢测试定位可跑 `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20`
- CI 先跑快验，再跑全量，既有快速失败信号，也保留完整保护

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
