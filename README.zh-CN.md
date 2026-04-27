# Skill Runtime

[English](./README.md)

`Skill Runtime` 是一套面向宿主 AI 的本地技能运行时，目标是把成功完成过的任务流程，沉淀成可治理、可审计、可复用的技能。

它不是第二个聊天 AI，而是挂在 Codex 这类宿主 AI 下方的一层能力内核。

## 它解决什么问题

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

## 为什么要做这个项目

很多 AI 系统能完成任务，但并不能真正建立一套“被治理的技能层”。

常见问题包括：

- 重复任务每次都从头规划
- 成功工作流只留在上下文里，无法沉淀
- skill 只是存下来，没有审计和生命周期管理
- skill 检索和复用缺乏解释，容易变成黑箱

这个项目的重点不是“积累技能”，而是“治理技能”。

## 核心特性

- `宿主优先`：宿主 AI 负责理解任务、规划和交互
- `可治理`：skill 必须走 staging -> audit -> promote 流程
- `可解释`：搜索结果可以返回命中原因、规则来源和推荐下一步动作
- `可扩展`：同一套 runtime 同时暴露 CLI 和 MCP
- `本地优先`：文件型存储，容易检查和调试

## 当前架构

```text
Host AI
-> CLI / MCP adapter
-> Runtime service
-> skill store / trajectories / audits
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
- Codex 侧 contract 说明见 [Codex Integration](./docs/codex-integration.md)
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

## CLI 快速开始

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

本项目已经按 “Codex 下方的本地能力层” 这个方向组织好。

推荐使用顺序：

1. `search_skill`
2. 有强命中时，调用 `execute_skill`
3. 如果这次任务是新解法或更优解法，沿 `recommended_host_operation` 进入 `distill_and_promote_candidate`
4. 没有强命中时，正常完成任务
5. 需要走显式受治理路径时，使用上面的 host-call 生命周期闭环
6. 库状态变化后，使用治理维护闭环

详细说明见：

- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)

## Demo 与验证

运行测试：

```bash
python -m unittest tests.test_runtime -v
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

- [项目详细报告](./docs/skill-runtime-project-report.md)
- [MCP 接入说明](./docs/mcp-integration.md)
- [Codex 接入说明](./docs/codex-integration.md)
- [视频脚本素材包](./docs/skill-runtime-video-cover.md)

## 当前局限

- 语义审计已经是 provider-backed，但默认 provider 还是 mock
- fallback distillation 默认还是 mock provider
- 检索目前是轻量混合版本，但还不是 embedding / 向量检索
- `archive-cold` 已经可用，但还没有更复杂的重复检测和自动治理
- 当前最强的是本地文件工作流

## 当前阶段结论

这个项目已经是可用的本地 MVP。

下一步最值得继续补的方向通常是：

1. 真实的 LLM 语义审计
2. 轻量混合检索
3. 更长期的技能库治理
