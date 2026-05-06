# Skill Runtime

[English](./README.en.md)

`Skill Runtime` 是面向 Codex 风格编程代理的本地工作流治理层，帮助开源维护者把重复的 review、triage、release、handoff 和维护自动化流程沉淀成可审计、可复用、可改进的技能。

它不是第二个聊天 AI，而是挂在 Codex 这类宿主 AI 下方的一层能力内核。

## 面向谁

这个项目优先服务这些场景：

- 开源维护者希望把重复的维护任务从聊天记录里沉淀出来
- agent 完成过一次复杂流程后，下一次不想从头规划
- 团队需要在复用自动化前先看到审计、来源和提升记录
- Codex / MCP / CLI 等宿主需要一个本地优先、可治理的 skill 生命周期层

一句话定位：

```text
Skill Runtime helps Codex-style agents capture, audit, reuse, and improve repeatable maintainer workflows.
```

## 它解决什么问题

很多 AI 系统能完成任务，但并不能真正建立一套“被治理的技能层”。

常见问题包括：

- 重复任务每次都从头规划
- 成功工作流只留在上下文里，无法沉淀
- agent 生成的脚本或 skill 没有审计和生命周期管理
- skill 检索和复用缺乏解释，容易变成黑箱

Skill Runtime 的重点不是“积累技能”，而是“治理技能”，再把这套治理能力逐步藏到正常的 Codex 执行流程下面。

系统围绕一条完整闭环展开：

`检索 -> 执行 -> 蒸馏 -> 审计 -> 入库 -> 复用`

现在也支持一条更轻的执行反馈闭环：

`检索 -> 执行 -> observed task record -> capture/distill`

也就是说，宿主 AI 可以：

- 在重做工作流之前，先检索有没有现成 skill
- 通过统一的 `run(tools, **kwargs)` 接口执行 active skill
- 把成功任务轨迹蒸馏成 staging skill
- 对候选 skill 做静态和语义审计
- 只有通过审计的 skill 才能 promote 到 active 库
- 在后续类似任务中直接复用

## 核心特性

- `宿主优先`：宿主 AI 负责理解任务、规划和交互
- `可治理`：skill 必须走 staging -> audit -> promote 流程
- `可解释`：搜索结果可以返回命中原因、规则来源和推荐下一步动作
- `可扩展`：同一套 runtime 同时暴露 CLI 和 MCP，但它们都不是最终产品形态本身
- `本地优先`：文件型存储，容易检查和调试
- `来源可见`：导入、蒸馏、导出和 legacy skill 的 provenance 边界需要显式记录

## Maintainer workflow demos

- [Review cleanup](./docs/maintainer-review-cleanup-demo.md)
- [Release readiness](./docs/maintainer-release-readiness-demo.md)
- [Handoff continuation](./docs/maintainer-handoff-continuation-demo.md)

## 开源参与

- [贡献指南](./CONTRIBUTING.md)
- [安全政策](./SECURITY.md)
- [行为准则](./CODE_OF_CONDUCT.md)
- [开源发布就绪清单](./docs/open-source-release-readiness-checklist.md)
- [Codex Open Source 申请草稿](./docs/codex-open-source-application-draft.md)

## 产品形态

这个项目现在经历了两种不同的描述方式。

### 较早的描述方式

```text
Codex
-> MCP tool calls
-> runtime service
```

这个说法在技术上仍然成立，但已经不是最准确的产品描述。

### 现在更准确的描述方式

```text
User task
-> Codex
-> runtime gate
-> normal execution
-> runtime finalize
```

在这条链里：

- Codex 继续负责用户交互和任务完成
- runtime 在后台判断什么时候值得复用
- 任务成功后，runtime 再决定是否回收这次经验
- MCP 仍然重要，但它更像宿主接口，而不是这套系统的本体

## 当前架构

```text
Host AI
-> runtime gate / lifecycle adapter
-> Runtime service
-> skill store / trajectories / audits
-> CLI / MCP / scripts 作为接口层
```

主要目录结构：

```text
scripts/
  skill_cli.py
  skill_mcp_server.py

skill_runtime/
  api/
  mcp/
  memory/
  distill/
  audit/
  retrieval/
  execution/
  governance/

skill_store/
  staging/
  active/
  archive/
  rejected/
  index.json

trajectories/
audits/
demo/
tests/
docs/
```

架构维护 guard：

- 运行 `python scripts/check_mcp_architecture.py` 可验证当前文档化分层和 contract 边界
- 运行 `python scripts/check_runtime_contracts.py` 可验证 host-operation 和 recommendation payload 不变量
- 更细的 MCP contract 说明见 [MCP Integration](./docs/mcp-integration.md)
- Codex 默认通道说明见 [Codex Integration](./docs/codex-integration.md)
- 当前这次架构转向的总说明见 [Agent-First Runtime Architecture](./docs/agent-first-runtime-architecture.md)
- 当前运行时分层 guard 明确覆盖 `service / governance / retrieval`
- 也覆盖 `memory / distill / audit / execution`

## 当前能力一览

### Runtime service

- CLI 和 MCP 共用同一层业务服务
- 搜索结果带顶层推荐字段：
  - `recommended_next_action`
  - `recommended_skill_name`
  - `recommended_host_operation`
- 成功执行 `execute` 后也会带：
  - `recommended_next_action`
  - `recommended_reason`
  - `recommended_host_operation`
- 显式生命周期接口现在也会带宿主后续动作：
  - `log_trajectory -> distill_trajectory`
  - `capture_trajectory -> distill_trajectory`
  - `distill_trajectory -> audit_skill`
  - `audit_skill -> promote_skill`（通过时）
  - `promote_skill -> execute_skill`

### Distillation

- 已知本地工作流走规则蒸馏
- 未命中的成功轨迹可走 fallback provider
- 可通过 `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` 接入外部 fallback provider 命令
- 仓库内已提供本地示例 fallback provider：`examples/providers/copy_metadata_fallback_provider.py`
- 已提供 DeepSeek fallback provider：`examples/providers/deepseek_fallback_provider.py`
- 当前规则库包括：
  - 文本合并
  - 文本替换
  - 单文件转换
  - 批量重命名
  - 目录复制
  - 目录移动
  - 目录级文本替换
  - CSV 转 JSON
  - JSON 转 CSV

### Audit

- 静态审计：
  - 危险命令
  - shell 调用
  - 缺失入口函数
  - 硬编码路径
- provider-backed 语义审计：
  - 默认本地 mock provider
  - 可通过 `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD` 接入外部语义审核命令
  - provider 命令契约见 [Provider Integration](./docs/provider-integration.md)
  - 仓库内已提供本地示例 semantic provider：`examples/providers/pass_semantic_review_provider.py`
  - 已提供 DeepSeek semantic provider：`examples/providers/deepseek_semantic_review_provider.py`
  - 审计 prompt artifact
  - provider review summary
  - 轨迹对齐
  - 参数覆盖
  - 模板 skill 检测
  - 面向检索的 docstring 结构检查

### Retrieval

- 用 `skill_store/index.json` 维护 active skill 索引
- 当前是轻量混合检索
- 搜索结果可返回：
  - `host_operation`
  - `rule_name`
  - `rule_priority`
  - `rule_reason`
  - `why_matched`
  - `score_breakdown`
  - `library_tier`

### Governance

- 严格的 staging -> audit -> promote 流程
- promote 后保留 provenance
- 支持 legacy skill provenance 回填
- `archive-cold` 可用
- `governance-report` 可查看库状态和重复候选
  - 重复候选里会直接给 `canonical_skill` 和 `archive_candidates`
  - 还会给宿主更容易消费的 `recommended_actions`
  - 每条建议现在还会带 `host_operation`，直接给出 MCP `tool_name`
    和 `arguments`，方便宿主从“看建议”直接切到“执行建议”
- `archive-duplicate-candidates` 可按建议安全归档重复候选

## 本地安装

### Clone 后最短验证路径

从一个全新 clone 下来的仓库开始，在项目根目录按顺序执行：

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
python -c "from skill_runtime.mcp import build_mcp_server; build_mcp_server('.')"
python -m skill_runtime.cli search --query "merge txt files into markdown"
python -m skill_runtime.mcp_stdio --help
```

预期结果：

- 架构检查和 runtime contract 检查通过
- runtime 快验通过
- MCP smoke 命令能构造 server，不会启动长期运行的 stdio loop
- search 命令能在靠前结果中看到 `merge_text_files`

完整 runtime 测试更全面，也更慢：

```bash
python -m unittest tests.test_runtime -v
```

它适合发布前、或影响大范围 runtime 行为时运行。当前 Windows 开发机上大约需要 9 分钟。要查看哪些测试最慢，可以运行：

```bash
python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20
```

如果安装后当前 shell 找不到 `skill-runtime` 或 `skill-runtime-mcp`，请优先使用上面的 `python -m skill_runtime...` 模块入口。

在项目根目录执行可编辑安装：

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

最小本地验证命令：

```bash
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
python -c "from skill_runtime.mcp import build_mcp_server; build_mcp_server('.')"
```

安装后可直接使用的命令入口：

```bash
skill-runtime search --query "<task>"
skill-runtime-mcp --root .
```

更稳的模块入口写法：

```bash
python -m skill_runtime.cli search --query "<task>"
python -m skill_runtime.mcp_stdio --root .
```

本地运行产生的 skill 使用统计会写到 `.skill_runtime/usage.json`，该文件默认已被 Git 忽略，因此日常执行 skill 不会继续改脏版本管理下的 active skill 元数据。

## CLI 快速开始

```bash
skill-runtime search --query "<task>"
skill-runtime execute --skill <skill_name> --args-file <json file>
skill-runtime distill --trajectory <trajectory.json> --skill-name <optional_name>
skill-runtime distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
skill-runtime distill-and-promote --observed-task <observed_task.json> --skill-name <optional_name>
skill-runtime audit --file <skill.py>
skill-runtime promote --file <staging_skill.py>
skill-runtime log-trajectory --file <trajectory.json>
skill-runtime capture-trajectory --file <observed_task.json>
skill-runtime reindex
skill-runtime archive-cold --days 30
skill-runtime governance-report
skill-runtime distill-coverage-report
skill-runtime archive-duplicate-candidates --dry-run
skill-runtime archive-duplicate-candidates --skill-name <name>
skill-runtime backfill-provenance
```

如果还在仓库根目录，也可以继续使用旧脚本路径：

```bash
python scripts/skill_cli.py search --query "<task>"
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --observed-task <observed_task.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <skill.py>
python scripts/skill_cli.py promote --file <staging_skill.py>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py capture-trajectory --file <observed_task.json>
python scripts/skill_cli.py reindex
python scripts/skill_cli.py archive-cold --days 30
python scripts/skill_cli.py governance-report
python scripts/skill_cli.py distill-coverage-report
python scripts/skill_cli.py archive-duplicate-candidates --dry-run
python scripts/skill_cli.py archive-duplicate-candidates --skill-name <name>
python scripts/skill_cli.py backfill-provenance
```

现在成功执行 `execute` 后，返回值里会带上 `observed_task_record` 路径。  
这份文件后面可以直接：

- 用 `capture-trajectory` 转成标准 trajectory
- 或直接喂给 `distill-and-promote --observed-task`

## MCP 快速开始

在项目根目录启动：

```bash
skill-runtime-mcp --root .
```

更稳的模块入口写法：

```bash
python -m skill_runtime.mcp_stdio --root .
```

如果仍想走旧脚本路径，也可以继续使用：

```bash
python scripts/skill_mcp_server.py
```

或者从任意目录启动：

```bash
python D:/02-Projects/vibe/scripts/skill_mcp_server.py --root D:/02-Projects/vibe
```

当前 MCP tools：

- `search_skill`
- `execute_skill`
- `distill_trajectory`
- `distill_and_promote_candidate`
- `audit_skill`
- `promote_skill`
- `log_trajectory`
- `capture_trajectory`
- `reindex_skills`
- `backfill_skill_provenance`
- `governance_report`
- `distill_coverage_report`
- `archive_duplicate_candidates`
- `archive_fixture_skills`
- `archive_cold_skills`

`distill_coverage_report` 会汇总当前成功 trajectory 中有多少已经命中 deterministic
rule、有多少仍落到 `llm_fallback`，并按工具序列与推断出的输入 schema 聚合剩余热点。

`governance_report` 现在返回可直接执行的宿主调用信息，例如：

```json
{
  "action": "archive_duplicate_candidates",
  "reason": "Keep \"merge_text_files\" as canonical and archive lower-priority duplicates.",
  "host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "archive_duplicate_candidates",
    "display_label": "Archive duplicates",
    "risk_level": "high",
    "requires_confirmation": true,
    "arguments": {
      "skill_names": ["merge_text_files_generated"],
      "dry_run": false
    },
    "preview": {
      "tool_name": "archive_duplicate_candidates",
      "display_label": "Preview archive",
      "risk_level": "low",
      "requires_confirmation": false,
      "arguments": {
        "skill_names": ["merge_text_files_generated"],
        "dry_run": true
      }
    }
  }
}
```

这样宿主侧可以直接：

- 用 `preview` 先做 dry-run 预览
- 再用主 `host_operation` 正式执行

治理维护闭环：

1. 在 active 库发生变化后先调用 `reindex_skills`
2. 调用 `governance_report` 查看重复项和维护建议
3. 需要为旧 metadata 补规则来源时调用 `backfill_skill_provenance`
4. 用 `archive_duplicate_candidates` 做重复技能的预览或正式归档
5. 用 `archive_fixture_skills` 做 fixture skill 的预览或正式归档
6. 用 `archive_cold_skills` 把长期未使用的 active skill 移入 archive

现在这些会改变或刷新库状态的治理工具都会把 `governance_report` 作为标准后续动作，
这样宿主侧在每一步维护之后都可以回到同一个稳定的检查入口。

`search_skill` 现在也用了同样的模式：

- 每条命中结果都带 `host_operation`
- 顶层响应带 `recommended_host_operation`
- 顶层响应也带 `available_host_operations`

例如：

```json
{
  "recommended_next_action": "execute_skill",
  "recommended_skill_name": "merge_text_files",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "execute_skill",
    "display_label": "Run recommended skill",
    "risk_level": "low",
    "requires_confirmation": false,
    "arguments": {
      "skill_name": "merge_text_files",
      "args": {}
    }
  }
}
```

对于没有强命中的查询，`search_skill` 现在会把 `capture_trajectory` 作为主推荐，
同时把 `distill_and_promote_candidate` 保留在 `available_host_operations`
里作为更短的次级路径，适合宿主已经拿到了可用 artifact 的情况。

成功执行 `execute_skill` 后也会返回同样的下一跳信息：

```json
{
  "skill_name": "merge_text_files",
  "observed_task_record": "/abs/path.json",
  "recommended_next_action": "distill_and_promote_candidate",
  "recommended_reason": "Execution succeeded and emitted an observed task record that can be sent directly into distill_and_promote_candidate.",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "distill_and_promote_candidate",
    "display_label": "Promote this execution",
    "risk_level": "medium",
    "requires_confirmation": false,
    "arguments": {
      "observed_task_path": "/abs/path.json"
    }
  }
}
```

这样宿主调用链就能闭环：

- `search_skill`
- `execute_skill`
- `recommended_host_operation`
- `distill_and_promote_candidate`

宿主现在还可以直接用这些字段驱动交互：

- `display_label`：按钮或菜单文案
- `risk_level`：风险提示等级
- `requires_confirmation`：是否需要二次确认

Host-call 生命周期闭环：

- `log_trajectory` 推荐 `distill_trajectory`
- `capture_trajectory` 推荐 `distill_trajectory`
- `distill_trajectory` 推荐 `audit_skill`
- `audit_skill` 在通过时推荐 `promote_skill`
- `promote_skill` 推荐 `execute_skill`
- `distill_and_promote_candidate` 在成功 promote 后也会推荐 `execute_skill`

这条短路径现在可以从两种输入开始：

- 一份完整 trajectory JSON
- 一份更轻量的 observed task record，系统会先自动 capture 成 trajectory

Observed task 输入格式现在统一收口在
[MCP Integration](./docs/mcp-integration.md#observed-task-input-shapes)：
其中包含 `capture_trajectory` 和 `distill_and_promote_candidate` 支持的详细格式、
压缩格式和嵌套工具日志格式。

## Codex 接入方式

本项目已经按 “Codex 下方的本地背景能力层” 这个方向组织好。

MCP 仍然是其中一个很重要的宿主接入面，但它已经不是全部。

推荐使用顺序：

1. 先让 Codex 判断这次任务是否属于 runtime lane
2. 如果属于，保守地尝试静默复用
3. 如果不适合复用，就正常完成任务
4. 任务成功后，再回收有复用价值的经验
5. 只有在需要手动控制、调试或治理时，才显式走 MCP 生命周期工具
6. 库状态变化后，再使用治理维护闭环

### 如何知道 runtime lane 有没有触发

Codex 侧的默认通道结果会返回两个可见字段：

- `runtime_lane_status`
  - `used`：runtime lane 真的执行了复用技能，或捕获了可沉淀的任务经验
  - `entered`：任务进入过 runtime lane 判断，但这次没有实际复用或捕获
  - `skipped`：任务被判定留在普通 Codex 路径，没有进入 runtime lane
- `runtime_lane_reason`：用一句话说明为什么进入、使用或跳过

这两个字段用于回答“这次到底有没有用上 Skill Runtime”。正常使用时不需要手动找技能；如果要排查体验，可以看这两个字段。

详细说明见：

- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)

## Demo 与验证

生成本地只读观察面板：

```bash
python -m skill_runtime.cli dashboard
```

一键生成并用默认浏览器打开：

```bash
python -m skill_runtime.cli dashboard --open
```

查看当前本地 operator summary，并同时看到当前 dashboard 摘要导出状态：

```bash
python -m skill_runtime.cli operator-summary
```

返回结果现在也会给出每个 gate status 自己的 freshness，便于先判断 provider / 基础检索 / 工作流检索状态是否已经过期，再决定要不要刷新。

先刷新本地持久化的 gate status，再返回 operator summary：

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status
```

只刷新稳定的 dashboard 摘要导出、不生成 HTML：

```bash
python -m skill_runtime.cli operator-summary --refresh-dashboard-export
```

如果希望把 gate status 和稳定导出一起刷新：

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status --refresh-dashboard-export
```

如果希望在生成前顺手刷新稳定的 operator-summary 导出：

```bash
python -m skill_runtime.cli dashboard --refresh-operator-summary --open
```

如果希望在生成前把 gate status 和稳定导出一起刷新：

```bash
python -m skill_runtime.cli dashboard --refresh-operator-status --refresh-operator-summary --open
```

如果已安装命令入口，也可以运行：

```bash
skill-runtime dashboard --open
```

默认输出到 `.skill_runtime/dashboard.html`。它只读取当前 runtime root 的本地数据，用于查看技能树、runtime lane 触发日志和治理快照；三者在面板中是独立视图，不混在同一页。技能树采用中心向四周发散的径向布局，四个象限分别展示 active / staging / archived / rejected 分支；分支内优先展示“格式转换、文本处理、文件整理、运行时治理”等组别，而不是逐个技能堆叠。点击组别时，组内技能会在居中的详情界面中凸显出来；页面不会自动滚动，技能树本身也不会被撑开。面板默认中文显示；技能调用仍使用原始英文 `skill_name`，页面只在展示层把技能名称和说明翻译成中文。

查看多个项目的全局触发记录：

```bash
python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open
```

全局面板默认输出到 `.skill_runtime/global-dashboard.html`。它和普通面板是同一套界面：仍然可以看当前项目的技能树、触发日志和治理快照，同时额外增加“全局项目”和“全局日志”两页，用来回答“其他工作区有没有触发过 runtime lane”。它只扫描指定目录下一层项目里的 `.skill_runtime/runtime_lane_events.jsonl`。如果不传 `--scan-root`，默认扫描当前 runtime root 的父目录。

这条最窄的 operator 可见性路径已经收成 [docs/operator-visibility-runbook.md](./docs/operator-visibility-runbook.md)。

运行本地快验：

```bash
python -m unittest tests.test_runtime_fast -v
```

运行当前 active 技能搜索质量基线：

```bash
python scripts/evaluate_search_quality.py
```

运行仓库内置的本地 provider 示例路径：

```bash
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

PowerShell：

```powershell
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

这两个 provider 是很窄的本地示例，不是通用 LLM 后端。它们用于验证真实 provider hook 可以在不临时写脚本的情况下完成生成、审核、入库和复用。

使用 DeepSeek 作为真实 provider：

```bash
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"
export DEEPSEEK_MODEL="deepseek-v4-flash"
export DEEPSEEK_REPAIR_ATTEMPTS="1"
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="<your-deepseek-api-key>"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:DEEPSEEK_REPAIR_ATTEMPTS="1"
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

不要把 API key 提交进仓库。fallback provider 会先做本地质量检查，失败时可让 DeepSeek 自动修复一次；细节见 [Provider Integration](./docs/provider-integration.md#deepseek-providers)。

可选真实 DeepSeek 闭环 smoke：

```bash
python scripts/smoke_deepseek_provider_loop.py
```

运行 demo：

```bash
python scripts/skill_cli.py log-trajectory --file trajectories/demo_merge_text_files.json
python scripts/skill_cli.py distill --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_generated
python scripts/skill_cli.py audit --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py promote --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py distill-and-promote --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_one_shot
python scripts/skill_cli.py distill-and-promote --observed-task output/observed_task.json --skill-name merge_text_files_from_observed
python scripts/skill_cli.py search --query "merge txt files into markdown"
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## 文档入口

- [开源发布就绪清单](./docs/open-source-release-readiness-checklist.md)
- [Codex Open Source 申请草稿](./docs/codex-open-source-application-draft.md)
- [项目详细报告](./docs/skill-runtime-project-report.md)
- [MCP 接入说明](./docs/mcp-integration.md)
- [Codex 接入说明](./docs/codex-integration.md)
- [隐私与 Provenance 边界](./docs/privacy-and-provenance.md)
- [多宿主适配方案](./docs/multi-host-adaptation-plan.md)
- [Codex 默认通道阶段收口](./docs/codex-default-lane-stage-closure.md)
- [Codex 默认通道观察计划](./docs/codex-default-lane-observation-plan.md)
- [Agent-First 架构说明](./docs/agent-first-runtime-architecture.md)
- [视频脚本素材包](./docs/skill-runtime-video-cover.md)

## 当前局限

- 语义审计已经是 provider-backed，但默认 provider 还是 mock
- fallback distillation 默认还是 mock provider
- 检索目前是轻量混合版本，但还不是 embedding / 向量检索
- `archive-cold` 已经可用，但还没有更复杂的重复检测和自动治理
- 当前最强的是本地文件工作流

## 许可证

本项目采用 [MIT License](./LICENSE)。

## 当前阶段结论

这个项目已经是可用的本地 MVP。

下一步最值得继续补的方向通常是：

1. 真实的 LLM 语义审计
2. 轻量混合检索
3. 更长期的技能库治理
