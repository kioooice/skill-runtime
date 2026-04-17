# Skill Runtime 项目详细报告

## 1. 项目概述

本项目实现了一套面向 `Codex` 的本地 `skill runtime`，目标不是再做一个新的 AI 助手，而是给宿主 AI 加一层“技能运行时与治理内核”。

这套系统解决的问题不是“AI 会不会做任务”，而是：

- AI 做过的工作流能不能沉淀下来
- 沉淀下来的技能能不能被检查、治理和复用
- 宿主 AI 下次遇到类似任务时，能不能先复用已有技能，而不是从头再做

因此，这个项目的定位是：

- 不是独立 AI 产品
- 不是新的聊天界面
- 不是另一个 agent
- 而是 AI 应用内部的一个能力层

它更接近：

- `skill runtime`
- `workflow memory`
- `skill governance kernel`
- `host-AI capability layer`

当前这套实现已经可以挂到 Codex 下方，通过 MCP 工具方式被调用，并且具备一条完整闭环：

`search -> execute -> distill -> audit -> promote -> reuse`

---

## 2. 项目想解决的核心问题

### 2.1 传统 AI 工作流的缺陷

当前很多 AI 编程或任务执行系统虽然能完成任务，但通常有以下问题：

1. 重复任务反复从头规划  
   即使某类任务已经做过，下一次仍然会重新分析、重新写流程、重新调用工具。

2. 能做任务，但不能有效沉淀  
   任务完成之后，过程往往只留在聊天上下文里，没有被转化为结构化的可复用能力。

3. 技能复用缺乏治理  
   有些系统会“积累技能”，但只是简单保存脚本或记忆片段，缺少审计、入库、生命周期管理、命中解释等治理层能力。

4. 宿主 AI 和技能系统耦合不清  
   很多方案会演化成“再套一个 AI”或者“外部 agent 控制宿主 agent”，结果架构复杂、边界混乱、成本增加。

### 2.2 本项目的判断

本项目的判断是：

- 未来这类系统最合理的形态，不是独立 AI
- 而是作为现有 AI 应用内部的一层能力内核存在

也就是说：

- 宿主 AI 负责理解任务、和用户交互、做最终决策
- skill runtime 负责技能检索、执行、蒸馏、审计、入库和复用

这也是为什么项目最终选择用 MCP 把 runtime 暴露给 Codex，而不是把它做成独立聊天程序。

---

## 3. 项目定位与设计原则

### 3.1 项目定位

本项目的准确定位是：

**一套面向宿主 AI 的、本地可演化的技能运行时与治理系统**

### 3.2 设计原则

项目在演化过程中形成了以下核心原则：

1. 宿主优先  
   宿主 AI 是上层入口。skill runtime 不抢用户交互，不伪装成第二个 AI。

2. 先复用，再生成  
   面对任务，优先检索已有 skill；只有没命中时，才考虑新生成。

3. 生成必须可治理  
   新 skill 不能直接入库，必须进入 staging，并通过审计后再 promote。

4. 结构优先于智能  
   第一阶段先做稳固闭环和可解释结构，不急着一上来全靠 LLM 生成。

5. 能力层而不是产品壳  
   对外优先暴露 CLI、MCP tools、技能包装层，而不是新的 UI。

6. 可解释性很重要  
   skill 被检索、生成和复用时，要尽量知道：
   - 为什么命中
   - 来自哪条规则
   - 为什么推荐下一步执行或生成

---

## 4. 系统总体架构

系统结构可以概括为四层：

### 4.1 Host AI 层

当前宿主是 `Codex`。

宿主负责：

- 接收用户任务
- 理解需求
- 规划整体动作
- 决定何时调用 runtime

### 4.2 Adapter 层

当前实现了两个适配层：

1. CLI
2. MCP server

其中 MCP 是当前与 Codex 集成的主方式。

### 4.3 Skill Runtime 层

这是项目核心，负责：

- trajectory 存储
- skill 蒸馏
- skill 审计
- promote 守卫
- skill 检索
- skill 执行
- provenance 回填

### 4.4 Storage / Governance 层

底层以本地文件为主，核心目录包括：

- `skill_store/staging`
- `skill_store/active`
- `skill_store/archive`
- `skill_store/rejected`
- `trajectories`
- `audits`
- `skill_store/index.json`

---

## 5. 目录与模块结构

当前项目的主要结构如下：

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

各模块职责如下。

### 5.1 `api/`

包含：

- 数据模型
- `RuntimeService`

这是整个系统的共用业务层。CLI 和 MCP 都不直接重复业务逻辑，而是统一调用 `RuntimeService`。

### 5.2 `memory/`

负责 trajectory 存取和校验。

核心能力：

- 保存任务轨迹
- 读取轨迹
- 校验轨迹结构
- 为 distill / audit 提供轨迹上下文

### 5.3 `distill/`

负责从成功 trajectory 生成 skill。

当前有两层路径：

1. 规则蒸馏
2. fallback provider 蒸馏

### 5.4 `audit/`

负责 skill 审计。

当前是双层：

1. 静态审计
2. 语义审计骨架

### 5.5 `retrieval/`

负责技能索引与检索。

当前是关键词打分为主，但已带推荐下一步动作和 provenance 解释。

### 5.6 `execution/`

负责：

- 工具注入
- skill 动态加载
- skill 执行
- 结果包装
- 使用统计回写

### 5.7 `governance/`

负责治理层逻辑，例如：

- promote guard
- provenance backfill

---

## 6. 核心数据模型

系统定义了几类关键数据结构。

### 6.1 Trajectory

表示一次任务执行轨迹。

核心字段：

- `task_id`
- `session_id`
- `task_description`
- `steps`
- `final_status`
- `artifacts`
- `started_at`
- `ended_at`

其中 `steps` 包含：

- `step_id`
- `tool_name`
- `tool_input`
- `observation`
- `status`
- `thought_summary`

### 6.2 SkillMetadata

表示一个 skill 的索引与治理信息。

主要包括：

- `skill_name`
- `file_path`
- `summary`
- `docstring`
- `input_schema`
- `output_schema`
- `source_trajectory_ids`
- `created_at`
- `last_used_at`
- `usage_count`
- `status`
- `audit_score`
- `tags`
- `rule_name`
- `rule_priority`
- `rule_reason`

后三个字段用于记录 skill provenance。

### 6.3 AuditReport

表示审计结果。

当前包含：

- `status`
- `security_score`
- `suggestions`
- `optimized_docstring`
- `refactored_code`
- `static_score`
- `semantic_score`
- `static_findings`
- `semantic_findings`
- `semantic_summary`

---

## 7. 主闭环：任务如何演化成技能

### 7.1 搜索

宿主 AI 首先调用 `search_skill` 或 CLI `search`：

- 输入一个任务描述
- 在 active skill 库里检索已有 skill
- 返回匹配列表
- 同时返回顶层建议：
  - `recommended_next_action`
  - `recommended_skill_name`

### 7.2 执行

如果存在强命中，则宿主调用 `execute_skill`：

- 只允许执行 active skill
- 动态加载 skill 模块
- 调用 `run(tools, **kwargs)`
- 返回结构化结果

### 7.3 完成任务

如果没有命中，宿主 AI 正常完成该任务。

### 7.4 记录轨迹

完成后，将此次任务的执行过程写成 trajectory。

### 7.5 蒸馏

trajectory 进入 distill 流程：

- 如果命中规则蒸馏路径，则生成真实可执行的 skill
- 如果没有命中规则，则走 fallback provider
- 新生成 skill 进入 `staging`

### 7.6 审计

staging skill 会进入 audit：

- 静态规则检查
- 语义层检查

### 7.7 Promote

只有 audit 通过的 skill 才允许 promote 到 `active`。

### 7.8 复用

下一次再遇到类似任务时，优先 `search -> execute`，不再从零规划。

---

## 8. Distillation 设计

### 8.1 为什么要先做规则蒸馏

项目没有一开始就完全依赖 LLM 生成 skill，而是先做规则蒸馏。

原因是：

- 规则蒸馏更可控
- 更容易验证
- 更容易解释
- 更适合先做闭环

### 8.2 当前规则库

当前规则注册表已经支持以下模式：

- `text_merge`
- `text_replace`
- `single_file_transform`
- `batch_rename`
- `directory_copy`
- `directory_move`
- `directory_text_replace`
- `csv_to_json`
- `json_to_csv`

这些规则已经能生成真正可执行的本地文件工作流 skill。

### 8.3 规则注册表

为了避免生成器变成一个巨型文件，后续把规则拆成了独立注册表结构。

每条规则都有：

- `RULE_NAME`
- `PRIORITY`
- `match(...)`
- `explain_match(...)`

这带来了两点好处：

1. 规则本身更易维护
2. 生成结果具备 provenance 和解释性

### 8.4 LLM fallback

当规则库无法命中时，系统不会直接失败，而是进入 fallback provider 流程：

1. 构造 prompt artifact
2. 调用 provider 抽象
3. 生成 candidate code
4. 写入 staging

当前 provider 仍然是 `mock provider`，目的是让 fallback 链路先可测试，而不强依赖外部模型。

---

## 9. Audit 设计

### 9.1 为什么审计是这套系统的核心

单纯“积累技能”并不稀缺，真正关键的是：

- 新 skill 能不能安全复用
- 新 skill 能不能以合理粒度存在
- 新 skill 有没有过拟合一次性轨迹
- 新 skill 是否真的适合入库

因此审计不是附属功能，而是整个治理闭环的核心。

### 9.2 静态审计

静态审计负责检查：

- 危险命令
- `shell=True`
- `os.system`
- 绝对路径硬编码
- 用户名或用户目录硬编码
- 缺失 `run()`
- 缺失 docstring
- run 函数过长
- 语法错误

### 9.3 语义审计骨架

为了避免 skill 只是“看起来结构合法”，后续又加了语义审计骨架。

当前会检查：

- docstring 是否真的利于检索
- skill 是否明显承担过多职责
- skill 是否和 trajectory 的工具链一致
- kwargs 是否覆盖关键输入
- 是否把 trajectory artifact 名称硬编码进 skill
- 是否是模板式或空操作式 skill

### 9.4 当前结论

现在的审计能力已经能拦住：

- 静态高风险 skill
- 明显错配 trajectory 的模板 skill
- 不足以 promote 的伪 skill

但它仍然不是 LLM 驱动的深语义审计，只能算“语义骨架版”。

---

## 10. Retrieval 设计

### 10.1 当前检索方式

当前检索仍然以关键词打分为主。

会综合：

- skill 名称
- summary
- docstring
- tags
- input/output schema
- active 状态
- audit_score

### 10.2 可解释性增强

检索结果不仅返回 skill，还返回：

- `why_matched`
- `rule_name`
- `rule_priority`
- `rule_reason`

也就是说，当一个 skill 被搜出来时，系统会尽量说明：

- 为什么这个 skill 命中了
- 它最初是按哪条规则生成的

### 10.3 顶层推荐动作

为了让宿主更容易决策，还加入了搜索后的顶层推荐动作：

- 强命中时推荐 `execute_skill`
- 弱命中或无强命中时推荐 `distill_and_promote_candidate`

这一步不是混合检索，但显著提升了宿主的决策质量。

### 10.4 目前还没做的部分

当前还没有真正实现：

- 向量检索
- BM25
- 混合检索 rerank

但这是有意控制节奏，因为在现阶段，错误 promote 的风险比排序不准更高，所以优先补了语义审计。

---

## 11. Execution 设计

### 11.1 技能统一入口

所有 skill 统一暴露：

```python
def run(tools, **kwargs):
    ...
```

这样可以保证：

- 宿主执行接口稳定
- 工具注入方式稳定
- 后续扩展时不需要改 skill 协议

### 11.2 RuntimeTools

当前 `RuntimeTools` 提供了一套受控本地工具能力：

- `read_text`
- `write_text`
- `list_files`
- `run_shell`
- `rename_path`
- `copy_file`
- `move_file`
- `read_json`
- `write_json`

并且对路径和 shell 有基本策略控制。

### 11.3 使用统计

skill 成功执行后，会回写：

- `usage_count`
- `last_used_at`

这为未来的治理和归档做了准备。

---

## 12. MCP 与 Codex 集成

### 12.1 为什么选择 MCP

对于本项目来说，MCP 的价值不在于“复用宿主当前模型会话”，而在于：

- 把 runtime 暴露成宿主可调用的工具层
- 保持 runtime 独立于某个特定宿主
- 让 Codex 直接把 runtime 当本地能力层使用

因此项目当前判断是：

- 对工具层集成，MCP 足够合适
- 更深的 Codex harness 级集成，长期可以考虑 App Server
- 但当前阶段没必要过早走那条更重的路径

### 12.2 当前暴露的 MCP tools

当前 MCP server 暴露的 tools 包括：

- `search_skill`
- `execute_skill`
- `distill_trajectory`
- `distill_and_promote_candidate`
- `audit_skill`
- `promote_skill`
- `log_trajectory`
- `reindex_skills`
- `backfill_skill_provenance`

### 12.3 Codex 全局接入

在这台机器上，已经通过全局 `~/.codex/config.toml` 配置了 `skill_runtime` MCP server。

同时还做了宿主层增强：

- 全局 AGENTS 偏好
- 全局 MEMORY 记录
- 全局 skills 包装

这些包装层包括：

- `skill-search`
- `skill-execute`
- `skill-distill`
- `skill-audit`
- `skill-promote`
- `skill-distill-promote`

它们让 Codex 更容易按预期方式使用 runtime，而不是把它当成一个模糊的外部工具。

---

## 13. CLI、MCP、组合编排

### 13.1 CLI 命令

当前支持：

- `search`
- `execute`
- `distill`
- `distill-and-promote`
- `audit`
- `promote`
- `log-trajectory`
- `reindex`
- `archive-cold`
- `backfill-provenance`

### 13.2 为什么后来加了组合命令

早期完整链路是：

`log -> distill -> audit -> promote`

但对于宿主来说，这条链太长，因此又加入了：

- `distill-and-promote`
- MCP tool：`distill_and_promote_candidate`

这条短路径大幅降低了宿主使用成本。

---

## 14. Provenance 设计

### 14.1 为什么 provenance 重要

当 skill 越来越多时，如果只知道“它存在”，但不知道“它为什么存在、怎么来的”，治理就会迅速失控。

因此项目后来加入了 provenance 字段。

### 14.2 记录的内容

每个 skill 可以记录：

- `rule_name`
- `rule_priority`
- `rule_reason`

### 14.3 历史回填

对于字段上线前就已经存在的 legacy skill，又做了：

- `backfill-provenance`

它会扫描现有 active skill，并尽量补齐 provenance。

这使得整个 skill 库不会因为历史数据不完整而割裂。

---

## 15. 演示闭环与验证

### 15.1 demo 场景

最早的 demo 是一个很典型的本地文件工作流：

`merge txt files into markdown`

这个例子被选择的原因是：

- 简单易懂
- 可本地复现
- 能清晰展示检索、执行、蒸馏、审计、复用的闭环

### 15.2 已验证的能力

当前已经验证过：

1. `search -> execute`
2. `log -> distill -> audit -> promote`
3. `distill_and_promote_candidate`
4. MCP 层搜索与执行
5. Codex 通过 MCP 调 runtime
6. provenance 回写
7. usage_count / last_used_at 回写

### 15.3 当前测试覆盖

当前项目已有一组 focused test suite，覆盖：

- trajectory 存取
- skill index
- execute path
- static audit
- semantic audit
- distillation rules
- fallback provider
- provenance backfill
- MCP search tool
- orchestration service

在最近一次状态下，测试数量已经达到 `25` 条，并全部通过。

---

## 16. 与“普通技能积累”方案的差异

这是项目最重要的部分之一。

本项目真正的差异化不在于“会积累技能”，因为这一点已经不稀缺了。

真正的差异在于以下三点：

### 16.1 它不是单纯积累，而是治理闭环

不是做完任务就随便存下来，而是：

- distill
- audit
- promote
- index
- execute

这是一条完整治理链。

### 16.2 它不是第二个 AI，而是宿主下的能力层

项目一直坚持：

- 不再额外造一个聊天 AI
- 不用第二个 agent 套娃
- 让宿主 AI 直接调 runtime

这让系统架构更干净，也更适合以后嵌入各种 AI 应用。

### 16.3 它不是黑箱，而是尽量可解释

当前系统已经尽量支持：

- why matched
- rule provenance
- recommended next action

这比“神秘记忆技能然后执行”要更容易治理，也更容易调试。

---

## 17. 当前局限

虽然系统已经可用，但当前仍有明显边界。

### 17.1 语义审计还不是最终形态

现在的语义审计是 heuristic 骨架，不是真正的 LLM 语义审计器。

### 17.2 检索还是轻量版本

当前仍然没有上混合检索，只是做了可解释和推荐动作增强。

### 17.3 fallback provider 还是 mock

规则未命中的 skill 生成路径已经打通，但真实外部 provider 还没接。

### 17.4 archive-cold 仍是占位

冷技能归档和长期库治理还没有完整落地。

### 17.5 目前偏本地文件工作流

浏览器、GUI、远程系统、更多复杂工具类型还没有接入。

---

## 18. 为什么当前阶段可以先用

尽管存在以上局限，但当前已经到了“可以试用”的阶段。

原因是：

1. 核心闭环已成立  
   检索、执行、蒸馏、审计、入库、复用都已具备。

2. 审计已经不是纯静态  
   语义层虽然还不够深，但已经能拦住一批假 skill 和模板型 skill。

3. 宿主接入已经稳定  
   Codex 的 MCP 接入、全局 skills、AGENTS 偏好都已经就位。

4. 已经有可复用规则库  
   不再只是概念 demo，而是已经有一批真实可执行的本地 workflow skill。

因此合理的节奏不是继续无限堆功能，而是：

- 先进入真实试用阶段
- 看审计、检索、蒸馏哪一块最容易暴露问题
- 再根据真实反馈补短板

---

## 19. 建议的下一阶段路线

如果后续继续演化，这里有一个比较合理的优先级顺序。

### 19.1 第一优先：真实 LLM 语义审计

把当前 heuristic 语义审计升级成：

- trajectory-aware
- code-aware
- promote-aware

的 LLM semantic auditor。

### 19.2 第二优先：轻量混合检索

不是一上来上重型向量基础设施，而是先做：

- 关键词
- schema 命中
- provenance 权重
- audit 加权
- usage 加权
- rerank

### 19.3 第三优先：长期治理

包括：

- archive-cold
- 重复 skill 合并
- 长期库清理
- 生命周期管理

### 19.4 第四优先：真实 provider 接入

把 fallback provider 从 mock 切到真实模型 provider。

---

## 20. 项目结论

这套 skill runtime 的核心价值，不是“又让 AI 多了一个功能”，而是：

**把 AI 做过的工作流，变成了一套可治理、可审计、可复用、可解释的能力层。**

它的意义不在于替代宿主 AI，而在于：

- 让宿主 AI 不必每次都从头再做
- 让技能沉淀不再只是上下文碎片
- 让技能库有治理，而不是单纯堆脚本
- 让未来的 AI 应用更像“会积累经验的系统”，而不是“每次重新开始的助手”

从工程角度看，这个项目当前阶段已经完成了最重要的一步：

**把概念变成了一个能跑通的本地闭环。**

这意味着它不再只是一个想法，而是一个已经具备继续演化价值的系统基础。

