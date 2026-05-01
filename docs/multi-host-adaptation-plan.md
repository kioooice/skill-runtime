# 多宿主适配方案

Date: 2026-04-30

## 目标

这份文档描述的是：

如果未来不只接入 Codex，而是要接入其他应用、其他代理或其他宿主，这套 `Skill Runtime` 应该怎样扩出去。

重点不是“再做一套新的技能系统”，而是：

保留同一个能力内核，让不同宿主通过各自的适配层来使用它。

## 先说结论

对外适配时，不应该把这个项目理解成：

- 一个只能给 Codex 用的 MCP 工具集

更合适的理解是：

- 一套宿主无关的背景能力层
- Codex 只是当前第一批接入得最深的宿主
- 其他应用以后通过适配层接入，而不是重做一套 runtime

## 适配原则

### 1. 核心 runtime 只保留一套

不要为每个宿主各写一套：

- skill 检索
- skill 执行
- observed task capture
- distill
- audit
- promote
- governance

这些都应该继续留在同一个 runtime core 里。

### 2. 每个宿主只做自己的 adapter

不同应用真正不同的，主要不是技能生命周期，而是：

- 任务是怎么进入系统的
- 宿主自己的任务对象长什么样
- 宿主怎么执行本地动作
- 宿主怎么把结果再交回来

所以以后真正要扩的，不是第二套 runtime，而是：

- Codex adapter
- IDE / editor adapter
- 通用 CLI agent adapter
- 服务端 agent adapter
- 自动化平台 adapter

### 3. 接口层和本体分开

MCP、CLI、脚本、HTTP 都可以存在，但它们都不应该变成“本体”。

它们负责的是：

- 传输
- 集成
- 调试
- 手动治理

真正的本体仍然应该是：

- reuse gate
- runtime lane
- capture + recommendation
- governed skill lifecycle

## 建议的分层

```text
User / Host App
-> Host Adapter
-> Runtime Gate / Lifecycle Adapter
-> Runtime Core
-> skill store / trajectories / audits / governance
-> MCP / CLI / HTTP / scripts as interface surfaces
```

## 各层职责

### 1. Host Adapter

负责把宿主自己的任务格式翻译成 runtime 能理解的格式。

最典型的输入包括：

- task_description
- working_directory
- known_inputs
- expected_outputs
- risk_level
- task_kind

最典型的输出包括：

- 是否进入 runtime lane
- 是否静默复用
- 如果没复用，是否继续正常执行
- 任务完成后是否 capture
- 是否给出 recommendation

### 2. Runtime Gate / Lifecycle Adapter

这是最靠近产品体验的一层。

它负责：

- 任务分类
- 是否允许进入 runtime lane
- 是否尝试静默复用
- 是否在任务结束后回收经验

这一层决定用户会不会感觉“系统在后台帮忙”，还是“系统在逼我用技能工具”。

### 3. Runtime Core

这一层负责真正的底层能力：

- search
- execute
- capture
- distill
- audit
- promote
- archive
- governance report

这一层应尽量不依赖具体宿主。

### 4. Interface Surfaces

这些都应该保留，但位置是接口层：

- MCP
- CLI
- scripts
- 未来可能的 HTTP API

它们不是产品本体，而是：

- 宿主接入面
- 调试面
- smoke 面
- 手动治理面

## 推荐的适配顺序

### 第一阶段：先把 Codex 跑稳

当前最重要的不是立刻扩到更多宿主，而是先确认：

- Codex 默认通道是否稳定
- 背景能力层的体验是否顺手
- 观察期里有没有明显误判

如果这一层都还不稳，直接扩多宿主只会把问题复制到更多地方。

### 第二阶段：抽象宿主协议

等 Codex 版本稳定后，再把当前已经存在的宿主输入输出抽成一个更清楚的宿主协议。

建议先固定三类对象：

- task request
- execution payload
- post-task recommendation

这一层清楚之后，别的宿主就不需要读懂内部细节才敢接。

### 第三阶段：补第二个宿主 adapter

不要一口气扩很多宿主。

建议只选一个与 Codex 差异明显、但仍然以本地任务为主的宿主作为第二个样本。

这样最容易验证：

- 哪些能力真的宿主无关
- 哪些地方其实还夹带了 Codex 假设

### 第四阶段：再考虑更多接口面

等第二宿主样本成立之后，再决定是否要补：

- 通用 HTTP API
- 标准化宿主 SDK
- 更独立的 runtime launcher

## 当前代码基础已经具备什么

现在已经有的基础包括：

- runtime service
- host-facing API
- Codex task classification
- runtime lane
- capture + recommendation
- MCP 接口层
- CLI 接口层
- 全局启动脚本支持按当前工作区选择 runtime root

所以未来适配别的应用，不是从零开始。

真正要补的是：

- 更通用的宿主协议抽象
- 第二宿主样本
- 跨宿主观察与治理规则

## 当前不建议怎么做

### 不建议直接复制一份仓库给别的宿主

这样会让：

- skill store 分叉
- governance 分叉
- lifecycle 分叉

最后变成多套弱系统，而不是一套强内核。

### 不建议先做很多插件壳

如果核心 runtime lane 还没稳定，先做很多插件只会放大集成表面，不会提升真实能力。

### 不建议把 MCP 当成多宿主战略本身

MCP 很重要，但它只是一个接口面。

如果以后别的宿主更适合：

- Python API
- HTTP API
- 本地 launcher

也不应该为了统一而强行把一切都压到 MCP 上。

## 对外一句话描述

如果要给别人介绍这套系统，更推荐这样说：

> `Skill Runtime` 不是单纯的 MCP 工具集，而是一套可以挂在不同宿主 AI 下方的背景能力层。
> Codex 是当前第一批深度接入的宿主；未来适配其他应用时，应复用同一套 runtime core，只新增宿主适配层，而不是重做一套技能系统。

## 当前建议

当前阶段先不要急着扩第二宿主。

先做两件事：

1. 继续观察 Codex 版本在真实工作区中的表现
2. 等观察期积累到足够真实样本后，再抽宿主无关协议

只有这两步站稳了，多宿主适配才值得继续推进。
