# Skill Runtime

[English](./README.md)

`Skill Runtime` 是一套面向宿主 AI 的本地技能运行时，目标是把成功完成过的任务流程，沉淀成可治理、可审计、可复用的技能。

它不是第二个聊天 AI，而是挂在 Codex 这类宿主 AI 下方的一层能力内核。

## 它解决什么问题

系统围绕一条完整闭环展开：

`检索 -> 执行 -> 蒸馏 -> 审计 -> 入库 -> 复用`

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

## 当前能力一览

### Runtime service

- CLI 和 MCP 共用同一层业务服务
- 搜索结果带顶层推荐字段：
  - `recommended_next_action`
  - `recommended_skill_name`

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
- 语义审计骨架：
  - 轨迹对齐
  - 参数覆盖
  - 模板 skill 检测
  - 面向检索的 docstring 结构检查

### Retrieval

- 用 `skill_store/index.json` 维护 active skill 索引
- 当前是轻量关键词检索
- 搜索结果可返回：
  - `rule_name`
  - `rule_priority`
  - `rule_reason`
  - `why_matched`

### Governance

- 严格的 staging -> audit -> promote 流程
- promote 后保留 provenance
- 支持 legacy skill provenance 回填

## CLI 快速开始

```bash
python scripts/skill_cli.py search --query "<task>"
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <skill.py>
python scripts/skill_cli.py promote --file <staging_skill.py>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py reindex
python scripts/skill_cli.py backfill-provenance
```

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
- `reindex_skills`
- `backfill_skill_provenance`

## Codex 接入方式

本项目已经按 “Codex 下方的本地能力层” 这个方向组织好。

推荐使用顺序：

1. `search_skill`
2. 有强命中时，调用 `execute_skill`
3. 没有强命中时，正常完成任务
4. 用 `distill_and_promote_candidate` 把任务回灌进技能库

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
python scripts/skill_cli.py search --query "merge txt files into markdown"
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## 文档入口

- [项目详细报告](./docs/skill-runtime-project-report.md)
- [MCP 接入说明](./docs/mcp-integration.md)
- [Codex 接入说明](./docs/codex-integration.md)
- [视频脚本素材包](./docs/skill-runtime-video-cover.md)

## 当前局限

- 语义审计仍然是 heuristic 骨架，不是真正的 LLM semantic auditor
- fallback distillation 默认还是 mock provider
- 检索仍然是轻量版本，还不是混合检索
- `archive-cold` 还是占位
- 当前最强的是本地文件工作流

## 当前阶段结论

这个项目已经是可用的本地 MVP。

下一步最值得继续补的方向通常是：

1. 真实的 LLM 语义审计
2. 轻量混合检索
3. 更长期的技能库治理
