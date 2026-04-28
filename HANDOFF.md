# Handoff

## Current State

已完成一轮 Skill Runtime 产品化收敛：仓库已补齐最小 `pyproject.toml`、README 本地安装说明、CI 中的 `pip install -e .`、最小 MCP smoke 测试，以及 `copy_file` rollback 承诺修复。active skill 治理清理也已完成，并已重建 active index，使治理报告与搜索结果同步到真实状态。

## Last Completed

本轮已完成：
- 新增 `pyproject.toml`，声明 Python 3.11+ 和 MCP 运行依赖
- README / README.zh-CN 增加本地安装与最小验证步骤
- `.github/workflows/runtime-contracts.yml` 先执行 `python -m pip install -e .`
- 新增最小 MCP smoke 测试：验证 `build_mcp_server` 可 import 且能构造 server
- 修复 `RuntimeTools.copy_file` 在新建复制目标场景下的 rollback hint，与 `RuntimeService.rollback_operations` 保持一致
- 已运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
- 已执行 active skill 治理清理，且明确保留真实 dogfood skill
- 已重建 `skill_store/index.json`
- 当前 active skill 只剩：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 当前治理报告：
  - `active_count = 2`
  - `duplicate_candidates = []`
  - `fixture_count = 0`
- 当前搜索验证：
  - 查询 `merge txt files into markdown` 时，不再出现测试技能污染结果

## Next Action

如果继续做产品化收敛，优先处理治理层的小缺口：避免在并行执行多个治理维护动作时出现旧索引视图；如果当前更重视推进主线价值，也可以直接基于现在干净的 active library 继续下一项产品化任务。

## Important Files

- `AGENTS.md`
- `TASKS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `docs/gitnexus-local-runbook.md`
- `pyproject.toml`
- `.github/workflows/runtime-contracts.yml`
- `skill_runtime/execution/runtime_tools.py`
- `tests/test_runtime_mcp_smoke.py`

## Known Issues

- 如果多个治理维护动作并行执行，可能出现索引状态被后一次保存覆盖的情况；当前已通过顺序清理加重建索引收口，但更稳的顺序保护仍可继续补。
- 当前仓库已完成 GitNexus 注册，但成功依赖本机 GitNexus 安装中的临时修改，不应误判为“默认官方路径已完全无问题”。

## Constraints

- 当前阶段仍不要开始业务功能开发。
- 不要开始业务功能开发。
- 长期上下文应优先写入项目文件，而不是聊天记录。
- 自动模式阶段报告必须使用非技术语言，帮助非程序员用户理解项目进展。

## Do Not Do

- 不要依赖旧对话历史恢复项目状态。
- 不要要求旧会话再生成大段交接提示词。
- 不要在没有必要时改动业务代码。
- 不要因为小改动、单个测试通过或单个文件修改完成就打断用户。
