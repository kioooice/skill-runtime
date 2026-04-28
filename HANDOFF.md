# Handoff

## Current State

已完成一轮 Skill Runtime 产品化收敛：仓库已补齐最小 `pyproject.toml`、README 本地安装说明、CI 中的 `pip install -e .`、最小 MCP smoke 测试，以及 `copy_file` rollback 承诺修复。active skill 治理清理已完成，并已重建 active index，使治理报告与搜索结果同步到真实状态。runtime 测试隔离收敛也已完成，默认验证路径不再继续依赖被污染的 active skill 库，也不再默认把新的执行痕迹写回真实仓库。最新三轮已进一步补齐安装后的正式命令入口、收口本地杂项边界，并把 active skill 的 usage 写回从版本文件迁移到本地 `.skill_runtime/usage.json`：当前同时支持安装后直接使用 `skill-runtime` / `skill-runtime-mcp`，继续兼容仓库内 `scripts/*.py` 入口，正常执行 skill 仍可保留使用统计，但默认不再改脏版本管理下的 active skill 定义文件。

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
- runtime 测试支撑层已切到隔离副本
- 搜索 / 治理 / 生命周期测试已补齐自带样本，不再依赖历史污染的 active skill 库
- 已重新运行：
  - `python -m unittest tests.test_runtime -v`
  - 结果：342 tests OK
- 已补齐安装配置中的递归包发现
- 已新增正式命令入口：
  - `skill-runtime`
  - `skill-runtime-mcp`
- 已保留旧入口兼容：
  - `python scripts/skill_cli.py`
  - `python scripts/skill_mcp_server.py`
- README / README.zh-CN 已补充：
  - 安装后命令入口
  - `python -m skill_runtime...` 模块入口
- 已再次运行：
  - `python -m pip install -e .`
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 安装后入口 `--help`
  - 结果：344 tests OK
- 已补充 `.gitattributes`，统一仓库文本换行规范
- 已将 `.claude/` 加入 `.gitignore`
- 已保留 `docs/gitnexus-local-runbook.md` 作为正式仓库文档
- 已将 active skill 的使用统计写回迁移到本地 `.skill_runtime/usage.json`
- README / README.zh-CN 已补充本地 usage 状态文件说明
- 已重新运行：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：345 tests OK

## Next Action

如果继续做产品化收敛，优先继续补治理层并行保护，避免多个治理动作并行后出现索引状态被后一次保存覆盖。若之后仍要继续收口工作区状态，再处理已存在的历史 usage 差异和 line-ending 噪音的最终归零。

## Important Files

- `AGENTS.md`
- `TASKS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `docs/gitnexus-local-runbook.md`
- `pyproject.toml`
- `.github/workflows/runtime-contracts.yml`
- `skill_runtime/execution/runtime_tools.py`
- `skill_runtime/cli.py`
- `skill_runtime/mcp_stdio.py`
- `tests/test_runtime_mcp_smoke.py`
- `tests/runtime_test_support.py`
- `tests/test_runtime_isolation.py`
- `.gitattributes`
- `.gitignore`
- `skill_runtime/retrieval/skill_index.py`

## Known Issues

- 如果多个治理维护动作并行执行，可能出现索引状态被后一次保存覆盖的情况；当前已通过顺序清理加重建索引收口，但更稳的顺序保护仍可继续补。
- 当前仓库已完成 GitNexus 注册，但成功依赖本机 GitNexus 安装中的临时修改，不应误判为“默认官方路径已完全无问题”。
- 未来新的 dogfood 执行默认不再改写版本管理下的 active metadata 和主索引，但工作区里仍可能保留此前阶段已经产生的历史 usage 差异与 line-ending 噪音。

## Constraints

- 当前阶段仍不要开始业务功能开发。
- 不要开始业务功能开发。
- 长期上下文应优先写入项目文件，而不是聊天记录。
- 自动模式阶段报告必须使用非技术语言，帮助非程序员用户理解项目进展。
- 不要为了让测试通过而重新把测试技能放回真实 active skill 库。

## Do Not Do

- 不要依赖旧对话历史恢复项目状态。
- 不要要求旧会话再生成大段交接提示词。
- 不要在没有必要时改动业务代码。
- 不要因为小改动、单个测试通过或单个文件修改完成就打断用户。
