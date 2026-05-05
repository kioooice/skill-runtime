from __future__ import annotations

from typing import Any

from skill_runtime.dashboard.templates import SCRIPT, STYLE, badge, status_label, text


SKILL_NAME_LABELS = {
    "directory_json_to_csv_dogfood": "目录 JSON 批量转 CSV",
    "directory_text_cleanup_dogfood": "目录文本清理",
    "json_to_csv_dogfood": "JSON 转 CSV",
    "merge_text_files": "合并文本文件",
    "text_replace_dogfood": "文本替换",
    "archive_log_files_dogfood": "归档日志文件",
    "auto_mode_stage_runner": "自动模式阶段执行",
    "bridge_config_test": "桥接配置测试",
    "deployment_strategy_review": "部署策略审核",
    "explainable_rule_test": "可解释规则测试",
    "fallback_rule_test": "兜底规则测试",
    "generalized_merge_rule_test": "通用合并规则测试",
    "manual_fallback_demo": "手动兜底演示",
    "merge_text_files_generated_v2": "合并文本文件生成版 v2",
    "nontechnical_stage_report": "非技术阶段报告",
    "pre_implementation_workflow_review": "开发前方向审核",
    "repo_impact_analysis": "仓库影响分析",
    "runtime_gate_workflow": "运行时接入门禁",
    "runtime_verification_selector": "验证命令选择",
    "session_handoff_maintenance": "会话交接维护",
    "registry_refactor_test": "注册表重构测试",
    "semantic_provider_fallback_test": "语义提供器兜底测试",
    "service_audit_followup_test": "服务审核跟进测试",
    "service_distill_followup_test": "服务蒸馏跟进测试",
}

SKILL_SUMMARY_LABELS = {
    "Batch export all JSON records in a folder into CSV files.": "将文件夹中的所有 JSON 记录批量导出为 CSV 文件。",
    "Clean and normalize text files in a directory or folder by trimming trailing whitespace.": "清理并规范化目录中的文本文件，去除行尾多余空白。",
    "Convert a JSON list of records into a CSV file.": "将 JSON 记录列表转换为 CSV 文件。",
    "Merge all .txt files in an input directory into one markdown output file.": "将输入目录中的所有 .txt 文件合并为一个 Markdown 输出文件。",
    "Replace or update a word or text in one file and write the updated file.": "替换或更新单个文件中的词语或文本，并写出更新后的文件。",
    "Move all log files from inbox to archive.": "将收件箱中的所有日志文件移动到归档目录。",
    "Thin runtime adapter that points to the global auto-mode stage runner Codex skill.": "承接自动模式的连续执行、阶段汇报和停止条件。",
    "Thin runtime adapter that points to the global deployment strategy review Codex skill.": "根据真实项目结构判断部署方式和 Docker 策略。",
    "Thin runtime adapter that points to the global nontechnical stage report Codex skill.": "把阶段结果翻译成用户能判断价值和风险的说明。",
    "Thin runtime adapter that points to the global pre-implementation workflow review Codex skill.": "实现前审核开发方向是否值得做、是否需要先验证。",
    "Thin runtime adapter that points to the global repo impact analysis Codex skill.": "在改动前定位相关模块、调用链和影响范围。",
    "Thin runtime adapter that points to the global runtime gate workflow Codex skill.": "让具体开发任务先经过 Skill Runtime 接入门禁和收尾记录。",
    "Thin runtime adapter that points to the global runtime verification selector Codex skill.": "按风险选择最小但有用的测试、语法和静态检查命令。",
    "Thin runtime adapter that points to the global session handoff maintenance Codex skill.": "维护 HANDOFF、TASKS、DECISIONS，让新会话能继续接力。",
    "Merge all txt files in a directory into one markdown file.": "将目录中的所有 txt 文件合并为一个 Markdown 文件。",
    "Generate a report from mixed observations without a known deterministic file rule.": "从混合观察结果生成报告，适用于没有固定文件规则的场景。",
    "Generate a report from mixed observations without a deterministic rule.": "从混合观察结果生成报告，适用于没有固定规则的场景。",
    "Rename all txt files in a directory by prefixing them with a value.": "通过添加前缀批量重命名目录中的 txt 文件。",
}

TASK_DESCRIPTION_LABELS = {
    "capture a reusable workflow": "记录可复用工作流",
    "capture a reusable workflow through mcp": "通过 MCP 记录可复用工作流",
    "capture alpha workflow": "记录 alpha 工作流",
    "capture alpha workflow through mcp": "通过 MCP 记录 alpha 工作流",
    "capture shared global payload workflow": "记录全局共享工作流",
    "capture shared payload workflow": "记录共享工作流",
    "Clean dashboard overview chrome, workflow skill count, and duplicate log navigation": "清理总览页：修正工作流计数并合并日志入口",
    "Clean dashboard overview chrome, workflow count, and duplicate log navigation": "清理总览页：修正计数并合并日志入口",
    "Hide basic local dashboard collections and regroup workflow skills by function": "整理技能集合：隐藏基础技能，并按功能分组",
    "Localize dashboard trigger log wording": "优化触发日志中文表述",
    "merge alpha notes": "合并 alpha 笔记",
    "merge txt files into markdown": "合并 txt 文件为 Markdown",
    "Remove read-only dashboard labels and show full skill descriptions": "移除只读提示，并补全技能说明",
    "review beta roadmap": "评审 beta 路线",
}

TASK_WORD_LABELS = {
    "alpha": "alpha",
    "and": "并",
    "basic": "基础",
    "chrome": "界面",
    "clean": "清理",
    "collections": "集合",
    "count": "计数",
    "dashboard": "面板",
    "duplicate": "重复",
    "function": "功能",
    "global": "全局",
    "hide": "隐藏",
    "local": "本地",
    "log": "日志",
    "navigation": "导航",
    "notes": "笔记",
    "overview": "总览",
    "regroup": "重新分组",
    "review": "评审",
    "roadmap": "路线",
    "skill": "技能",
    "skills": "技能",
    "trigger": "触发",
    "wording": "表述",
    "workflow": "工作流",
}

RUNTIME_REASON_LABELS = {
    "auto-executed reusable skill": "已自动复用匹配的技能。",
    "captured learning payload": "已记录可复用经验，等待后续整理。",
    "default lane observation": "已进入运行时观察，但没有自动接管。",
    "kept on normal Codex path": "按普通 Codex 路径处理。",
    "outside default lane": "不属于当前默认运行时接管范围。",
}

SKILL_NAME_TOKEN_LABELS = {
    "active": "活跃",
    "agent": "代理",
    "alias": "别名",
    "archive": "归档",
    "audit": "审核",
    "backfill": "回填",
    "batch": "批量",
    "bridge": "桥接",
    "cli": "命令行",
    "compact": "压缩",
    "config": "配置",
    "csv": "CSV",
    "destination": "目标",
    "directory": "目录",
    "distill": "蒸馏",
    "dogfood": "自测",
    "duplicate": "重复",
    "explainable": "可解释",
    "fallback": "兜底",
    "file": "文件",
    "files": "文件",
    "followup": "跟进",
    "from": "从",
    "generated": "生成版",
    "generalized": "通用",
    "glob": "通配",
    "input": "输入",
    "json": "JSON",
    "lifecycle": "生命周期",
    "log": "日志",
    "manual": "手动",
    "merge": "合并",
    "name": "名称",
    "observed": "观察",
    "output": "输出",
    "prefix": "前缀",
    "promote": "提升",
    "provider": "提供器",
    "refactor": "重构",
    "registry": "注册表",
    "rename": "重命名",
    "replace": "替换",
    "rule": "规则",
    "semantic": "语义",
    "service": "服务",
    "source": "来源",
    "test": "测试",
    "text": "文本",
    "to": "到",
    "v2": "v2",
}

SKILL_GROUP_LABELS = {
    "structured-conversion": ("格式转换", "JSON、CSV、结构化导入导出"),
    "text-processing": ("文本处理", "合并、清理、替换、Markdown 输出"),
    "file-organization": ("文件整理", "归档、移动、批量重命名"),
    "runtime-governance": ("运行时治理", "测试、规则、审核、候选维护"),
    "other-workflows": ("其他工作流", "暂未归入固定能力类型"),
}

SKILL_GROUP_ORDER = [
    "structured-conversion",
    "text-processing",
    "file-organization",
    "runtime-governance",
    "other-workflows",
]

LOCAL_COLLECTION_IDS = {
    "basic-skills",
    "text-processing",
    "structured-conversion",
    "file-organization",
}


def render_dashboard_html(data: dict[str, Any]) -> str:
    global_data = data.get("global") if isinstance(data.get("global"), dict) else None
    title = "跨项目运行状态总览" if global_data else "运行状态总览"
    subtitle = ""
    read_only_text = (
        "先看系统现在的状态，再看跨项目记录和来源范围。"
        if global_data
        else "先看现在能不能直接用、最近发生了什么，以及是否有待你判断的事项。"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{STYLE}</style>
</head>
<body data-active-view="overview">
  <div class="desktop-shell">
    <header class="topbar">
      <button class="topbar-icon" type="button" aria-label="应用入口">{_icon("blocks")}</button>
      <div class="global-search">{_icon("search")}<span>搜索技能...</span><kbd>Ctrl K</kbd></div>
    </header>
    <div class="app-body">
      <aside class="sidebar">
        <div class="sidebar-head"><strong>skills-runtime</strong><span aria-hidden="true">‹</span></div>
        {_view_nav(data.get("overview", {}), global_enabled=bool(global_data))}
        <button class="sidebar-settings" type="button">{_icon("settings")}<span>设置</span></button>
      </aside>
        <main class="content-pane">
        {_view_headers(title, subtitle, read_only_text, global_enabled=bool(global_data))}
        {_overview_page(
            data.get("overview", {}),
            global_data.get("overview", {}) if global_data else None,
            data.get("operator_summary"),
        )}
        {_skill_tree(data.get("skills", []), data.get("capability_collections", []))}
        {_evolution_candidates(data.get("evolution_candidates", []))}
        {_trigger_log(
            global_data.get("events", []) if global_data else data.get("events", []),
            include_project=bool(global_data),
            counts=(
                global_data.get("overview", {}).get("recent_event_counts", {})
                if global_data
                else data.get("overview", {}).get("recent_event_counts", {})
            ),
        )}
        {_governance(data.get("governance", {}), data.get("diagnostics", []))}
        {_platform_inventory(data.get("platform_inventory", {}))}
        {_global_projects_view(global_data) if global_data else ""}
        {_skill_detail_drawer()}
        {_evolution_detail_drawer()}
      </main>
    </div>
  </div>
  {SCRIPT}
</body>
</html>
"""


def _view_headers(title: str, subtitle: str, read_only_text: str, *, global_enabled: bool) -> str:
    headers = [
        _view_header(
            "overview",
            title,
            subtitle,
        ),
        _view_header("skill-tree", "可直接复用的流程", "已经审核通过、现在能直接复用的流程。"),
        _view_header(
            "skill-evolution",
            "待你决定的事项",
            "这里放需要你判断是否保留、改进或处理的候选事项。",
        ),
        _view_header(
            "trigger-log",
            "最近发生了什么",
            "按人话解释最近任务是被系统接管、进入观察，还是保持普通处理。",
        ),
        _view_header("governance", "系统检查", "集中放系统自检、诊断信息和需要维护者关注的健康状态。"),
        _view_header("platforms", "来源与范围", "查看这些流程和平台信息是从哪里来的、当前扫描了哪些范围。"),
    ]
    if global_enabled:
        headers.extend(
            [
                _view_header("global-projects", "跨项目情况", "跨工作区查看哪里有调用记录、哪里最近更活跃。"),
            ]
        )
    return "\n".join(headers)


def _view_header(view: str, title: str, subtitle: str, *, actions: str = "") -> str:
    subtitle_html = f"<p>{text(subtitle)}</p>" if subtitle else ""
    return f"""<section class="content-header view-header" data-view-header="{text(view)}" hidden>
          <div>
            <h1>{text(title)}</h1>
            {subtitle_html}
          </div>
          {actions}
        </section>"""


def _icon(name: str) -> str:
    icons = {
        "blocks": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>',
        "radar": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21a9 9 0 1 0-9-9"/><path d="M12 17a5 5 0 1 0-5-5"/><path d="m12 12 6-6"/><path d="M12 8v4h4"/></svg>',
        "store": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10h16l-2-5H6z"/><path d="M6 10v9h12v-9"/><path d="M9 19v-5h6v5"/></svg>',
        "layers": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 16 9 5 9-5"/></svg>',
        "activity": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h4l2-7 4 14 2-7h4"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"/></svg>',
        "platform": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v10H4z"/><path d="M8 19h8"/><path d="M12 15v4"/></svg>',
        "spark": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="m18 15 .8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8z"/></svg>',
        "globe": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18"/><path d="M12 3a14 14 0 0 0 0 18"/></svg>',
        "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/></svg>',
        "settings": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.5-2.4 1a7 7 0 0 0-1.7-1L14.5 3h-5l-.3 3a7 7 0 0 0-1.7 1l-2.4-1-2 3.5L5.1 11a7 7 0 0 0 0 2l-2 1.5 2 3.5 2.4-1a7 7 0 0 0 1.7 1l.3 3h5l.3-3a7 7 0 0 0 1.7-1l2.4 1 2-3.5-2-1.5a7 7 0 0 0 .1-1z"/></svg>',
        "package": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 8 4v10l-8 4-8-4V7z"/><path d="m4 7 8 4 8-4"/><path d="M12 11v10"/></svg>',
        "link": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1"/></svg>',
    }
    return f'<span class="icon">{icons.get(name, icons["blocks"])}</span>'


def _overview_page(
    overview: dict[str, Any],
    global_overview: dict[str, Any] | None = None,
    operator_summary: dict[str, Any] | None = None,
) -> str:
    global_html = _global_overview(global_overview) if global_overview else ""
    operator_html = _operator_summary_overview(operator_summary) if isinstance(operator_summary, dict) else ""
    return f"""<section id="dashboard-page-overview" class="view-panel dashboard-view-page overview-page" data-view-page="overview" hidden>
  <section class="panel overview-panel">
    {_overview(overview)}
    {operator_html}
    {global_html}
  </section>
</section>"""


def _overview(overview: dict[str, Any]) -> str:
    counts = overview.get("recent_event_counts", {})
    return f"""<section class="overview-section">
  <div class="overview-section-head">
    <h2>先看这里</h2>
    <p class="muted">如果你是第一次打开，先看这四块：现在能直接用什么、最近系统怎么处理任务、以及系统有没有明显异常。</p>
  </div>
  <div class="grid metric-grid">
    {_metric("当前可直接用", overview.get("active_count", 0), "已审核、可直接复用")}
    {_metric("最近已自动处理", counts.get("used", 0), "系统已接管完成")}
    {_metric("仍在观察", counts.get("entered", 0), "有记录，但还没接管")}
    {_metric("保持普通处理", counts.get("skipped", 0), "由 Codex 直接完成")}
  </div>
  <div class="overview-callout">
    <strong>最近系统处理</strong>
    <p>最近一条记录：{text(overview.get("latest_event_time") or "暂无运行通道事件")}</p>
  </div>
</section>"""


def _global_overview(overview: dict[str, Any]) -> str:
    counts = overview.get("recent_event_counts", {})
    return f"""<section class="overview-section">
  <div class="overview-section-head">
    <h2>跨项目情况</h2>
    <p class="muted">这里看哪些工作区最近有调用记录，方便判断问题是局部还是跨项目共性。</p>
  </div>
  <div class="grid metric-grid">
    {_metric("有记录的工作区", overview.get("project_count", 0), "最近被扫描到")}
    {_metric("最近记录总数", overview.get("event_count", 0), "跨项目汇总")}
    {_metric("已自动处理", counts.get("used", 0), "系统已接管")}
    {_metric("进入观察", counts.get("entered", 0), "已记录未接管")}
    {_metric("普通处理", counts.get("skipped", 0), "保持 Codex 直处理")}
  </div>
  <p class="overview-meta">最近跨项目记录：{text(overview.get("latest_event_time") or "暂无全局运行通道事件")}</p>
</section>"""


def _project_card(project: dict[str, Any]) -> str:
    counts = project.get("recent_event_counts", {})
    operator_summary = _project_operator_summary(project)
    return f"""<article class="project-card">
  <div class="project-name">{text(project.get("project_name"))}</div>
  <div class="project-path">{text(project.get("project_root"))}</div>
  <div class="project-stats">
    <span>{text(project.get("event_count", 0))} 条事件</span>
    <span>{text(counts.get("used", 0))} 次使用</span>
    <span>{text(counts.get("entered", 0))} 次进入</span>
    <span>{text(counts.get("skipped", 0))} 次跳过</span>
  </div>
  {operator_summary}
  <div class="muted">最近：{text(project.get("latest_event_time") or "暂无")}</div>
</article>"""


def _global_projects_view(global_data: dict[str, Any]) -> str:
    return f"""<section id="dashboard-page-global-projects" class="panel view-panel dashboard-view-page" data-view-page="global-projects" hidden>
  {_project_overview_body(global_data.get("projects", []))}
  <h3>扫描范围</h3>
  {_scan_root_lists(global_data.get("scan_roots", []), global_data.get("diagnostics", []))}
</section>"""


def _project_overview_body(projects: list[dict[str, Any]]) -> str:
    if not projects:
        return '<p class="muted">没有在扫描范围内发现项目调用记录。</p>'
    return '<div class="project-grid">' + "\n".join(_project_card(project) for project in projects) + "</div>"


def _scan_root_lists(scan_roots: list[Any], diagnostics: list[str]) -> str:
    scan_body = "".join(f"<li>{text(item)}</li>" for item in scan_roots) or "<li>没有扫描范围。</li>"
    diagnostics_body = "".join(f"<li>{text(item)}</li>" for item in diagnostics) or "<li>没有诊断信息。</li>"
    return f"""<ul class="scan-list">{scan_body}</ul>
  <h3>诊断信息</h3>
  <ul class="scan-list">{diagnostics_body}</ul>"""


def _nav_count(value: Any) -> str:
    count = _safe_int(value)
    return f'<span class="nav-count">{text(count)}</span>' if count > 0 else ""


def _view_nav(overview: dict[str, Any] | None = None, *, global_enabled: bool = False) -> str:
    overview = overview or {}
    counts = overview.get("recent_event_counts", {}) if isinstance(overview.get("recent_event_counts"), dict) else {}
    global_links = ""
    if global_enabled:
        global_links = f"""
        <button class="view-link" type="button" data-view-target="global-projects" aria-controls="dashboard-page-global-projects" aria-current="false">{_icon("globe")}<span>跨项目情况</span></button>"""
    return f"""<nav class="view-nav" aria-label="面板视图">
        <button class="view-link is-active" type="button" data-view-target="overview" aria-controls="dashboard-page-overview" aria-current="page">{_icon("radar")}<span>现在先看什么</span></button>
        <button class="view-link" type="button" data-view-target="skill-tree" aria-controls="dashboard-page-skill-tree" aria-current="false">{_icon("blocks")}<span>可直接复用的流程</span>{_nav_count(overview.get("active_count", 0))}</button>
        <button class="view-link" type="button" data-view-target="skill-evolution" aria-controls="dashboard-page-skill-evolution" aria-current="false">{_icon("spark")}<span>待你决定的事项</span>{_nav_count(overview.get("evolution_candidate_count", 0))}</button>
        <button class="view-link" type="button" data-view-target="trigger-log" aria-controls="dashboard-page-trigger-log" aria-current="false">{_icon("activity")}<span>最近发生了什么</span>{_nav_count(counts.get("used", 0) + counts.get("entered", 0))}</button>
        <button class="view-link" type="button" data-view-target="governance" aria-controls="dashboard-page-governance" aria-current="false">{_icon("shield")}<span>系统检查</span></button>
        <button class="view-link" type="button" data-view-target="platforms" aria-controls="dashboard-page-platforms" aria-current="false">{_icon("platform")}<span>来源与范围</span></button>
        {global_links}
      </nav>"""


def _metric(label: str, value: Any, caption: str) -> str:
    return f"""<div class="metric">
  <strong>{text(value)}</strong>
  <span>{text(label)}</span>
  <small>{text(caption)}</small>
</div>"""


def _operator_summary_overview(summary: dict[str, Any]) -> str:
    freshness = summary.get("freshness") if isinstance(summary.get("freshness"), dict) else {}
    quality_gates = summary.get("quality_gates") if isinstance(summary.get("quality_gates"), dict) else {}
    safe_next_steps = summary.get("safe_next_steps") if isinstance(summary.get("safe_next_steps"), list) else []
    intentionally_not_automatic = (
        summary.get("intentionally_not_automatic") if isinstance(summary.get("intentionally_not_automatic"), list) else []
    )
    missing_or_unavailable = (
        summary.get("missing_or_unavailable") if isinstance(summary.get("missing_or_unavailable"), list) else []
    )
    gate_lines = []
    for key in ("provider_quality", "utility_search_quality", "workflow_search_quality"):
        gate = quality_gates.get(key) if isinstance(quality_gates.get(key), dict) else {}
        gate_lines.append(
            f"""<div class="operator-summary-gate">
  <strong>{text(_operator_gate_display_name(key))}</strong>
  <span>状态：{text(_operator_gate_status_label(gate.get("status")))}</span>
  <span>时效：{text(_operator_freshness_label((gate.get("freshness") or {}).get("status")))}</span>
</div>"""
        )
    next_steps_text = "、".join(
        str(item.get("label")).strip()
        for item in safe_next_steps
        if isinstance(item, dict) and str(item.get("label") or "").strip()
    )
    return f"""<section class="overview-section operator-summary-section" data-operator-summary>
  <div class="overview-section-head">
    <h2>系统当前状态</h2>
    <p class="muted">这块只回答现在系统大概处在什么状态，不直接执行任何后续动作。</p>
  </div>
  <div class="grid metric-grid">
    {_metric("可直接复用的流程", _summary_count(summary.get("active_skills")), "已经审核通过")}
    {_metric("待审核流程", _summary_count(summary.get("staging_candidates")), "还需要人工判断")}
    {_metric("已记录任务样本", _summary_count(summary.get("trajectories")), "后续可能整理成流程")}
    {_metric("待你确认的建议", _summary_count(summary.get("recommended_host_operations")), "只读建议，不会自动执行")}
  </div>
  <p class="overview-meta">系统状态：{text(_operator_freshness_label(freshness.get("status")))} · 生成时间：{text(summary.get("generated_at") or "未记录")}</p>
  <div class="operator-summary-checks">
    <div class="overview-section-head">
      <h3>系统检查</h3>
      <p class="muted">下面三项是系统自检，用来判断底层链路最近是否健康，不代表会自动替你执行动作。</p>
    </div>
  <div class="operator-summary-gates">
    {"".join(gate_lines)}
  </div>
  </div>
  <div class="operator-summary-notes">
    <p>待你确认的建议：{text(next_steps_text or "暂无")}</p>
    <p>这些动作不会自动执行：{text("、".join(str(item) for item in intentionally_not_automatic) or "暂无")}</p>
    <p>暂时缺失或不可用：{text("、".join(_operator_gate_display_name(item) for item in missing_or_unavailable) or "无")}</p>
    <p>{text(summary.get("non_automatic_explanation") or "只显示稳定摘要，不推进自动生命周期。")}</p>
  </div>
</section>"""


def _project_operator_summary(project: dict[str, Any]) -> str:
    if not project.get("operator_summary_available"):
        return ""
    freshness = _operator_freshness_label(project.get("operator_summary_freshness_status"))
    statuses = project.get("operator_quality_gate_statuses") if isinstance(project.get("operator_quality_gate_statuses"), dict) else {}
    freshness_statuses = (
        project.get("operator_quality_gate_freshness_statuses")
        if isinstance(project.get("operator_quality_gate_freshness_statuses"), dict)
        else {}
    )
    gate_lines = []
    for key in ("provider_quality", "utility_search_quality", "workflow_search_quality"):
        status = _operator_gate_status_label(statuses.get(key))
        gate_freshness = _operator_freshness_label(freshness_statuses.get(key))
        gate_lines.append(
            f"<div>{text(_project_operator_gate_display_name(key))}：{text(status)} / {text(gate_freshness)}</div>"
        )
    return f"""<div class="project-operator-summary">
  <div class="project-stats">
    <span>系统摘要：{text(freshness)}</span>
    <span>最近摘要时间：{text(project.get("operator_summary_generated_at") or "未记录")}</span>
  </div>
  <div class="muted project-operator-summary-lines">
    {"".join(gate_lines)}
  </div>
</div>"""


def _summary_count(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 0
    value = payload.get("count")
    return value if isinstance(value, int) else 0


def _operator_gate_status_label(value: Any) -> str:
    labels = {
        "available": "可用",
        "unavailable": "不可用",
        "unknown": "未知",
    }
    return labels.get(str(value or ""), str(value or "未知"))


def _operator_freshness_label(value: Any) -> str:
    labels = {
        "fresh": "新鲜",
        "stale": "过期",
        "unknown": "未知",
    }
    return labels.get(str(value or ""), str(value or "未知"))


def _operator_gate_display_name(value: Any) -> str:
    labels = {
        "provider_quality": "提供器质量",
        "utility_search_quality": "基础技能检索质量",
        "workflow_search_quality": "工作流检索质量",
    }
    return labels.get(str(value or ""), str(value or "未知检查项"))


def _project_operator_gate_display_name(value: Any) -> str:
    labels = {
        "provider_quality": "提供器质量",
        "utility_search_quality": "基础技能检索",
        "workflow_search_quality": "工作流检索",
    }
    return labels.get(str(value or ""), _operator_gate_display_name(value))


def _skill_display_name(raw_name: Any) -> str:
    raw = str(raw_name or "").strip()
    if not raw:
        return "未命名技能"
    if raw in SKILL_NAME_LABELS:
        return SKILL_NAME_LABELS[raw]
    tokens = raw.split("_")
    translated = [SKILL_NAME_TOKEN_LABELS.get(token, token) for token in tokens]
    return " ".join(translated)


def _skill_display_summary(raw_summary: Any) -> str:
    raw = str(raw_summary or "").strip()
    if not raw:
        return "该技能没有说明。"
    return SKILL_SUMMARY_LABELS.get(raw, "该技能还没有中文说明，原始说明保留在技能元数据中。")


def _skill_detail_description(skill: dict[str, Any]) -> str:
    authoritative_description = str(skill.get("authoritative_description") or "").strip()
    if authoritative_description:
        return authoritative_description
    summary = _skill_display_summary(skill.get("summary"))
    docstring = str(skill.get("docstring") or "").strip()
    if docstring.startswith("Runtime adapter only. The authoritative workflow lives in the global Codex skill"):
        return summary
    if docstring and docstring != str(skill.get("summary") or "").strip():
        return f"{summary} 原始补充说明：{docstring}"
    return summary


def _source_display_text(sources: list[Any]) -> str:
    if not sources:
        return "没有记录来源轨迹"
    return f"已记录 {len(sources)} 条来源轨迹"


def _skill_group_key(skill: dict[str, Any]) -> str:
    raw_name = str(skill.get("skill_name") or "").lower()
    summary = str(skill.get("summary") or "").lower()
    raw_hint = f" {raw_name} "
    combined = f"{raw_name} {summary}"

    governance_markers = (
        "audit",
        "bridge",
        "config",
        "demo",
        "deployment",
        "distill",
        "explainable",
        "fallback",
        "followup",
        "gate",
        "generated",
        "generalized",
        "handoff",
        "impact",
        "manual",
        "provider",
        "registry",
        "repo",
        "review",
        "rule",
        "semantic",
        "service",
        "test",
        "implementation",
        "verification",
        "stage",
        "report",
    )
    if any(marker in raw_hint for marker in governance_markers):
        return "runtime-governance"
    if any(marker in combined for marker in ("json", "csv", "convert", "export", "record")):
        return "structured-conversion"
    if any(marker in combined for marker in ("markdown", "merge", "normalize", "replace", "text", "txt", "whitespace")):
        return "text-processing"
    if any(marker in combined for marker in ("archive", "log", "move", "prefix", "rename")):
        return "file-organization"
    return "other-workflows"


def _group_skills_by_type(skills: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for skill in skills:
        grouped.setdefault(_skill_group_key(skill), []).append(skill)
    return [(group_id, grouped[group_id]) for group_id in SKILL_GROUP_ORDER if grouped.get(group_id)]


def _skill_tree(skills: list[dict[str, Any]], collections: list[dict[str, Any]] | None = None) -> str:
    workflow_skills = [skill for skill in skills if skill.get("skill_surface") == "workflow"]
    workflow_collections = collections or []
    if not workflow_skills and not workflow_collections:
        body = '<p class="muted">当前运行根目录没有找到工作流技能。</p>'
    else:
        body = _workflow_skill_group_cards(workflow_skills, workflow_collections)
    return f"""<section id="dashboard-page-skill-tree" class="panel view-panel dashboard-view-page" data-view-page="skill-tree">
  {body}
</section>"""


def _evolution_candidates(candidates: list[dict[str, Any]]) -> str:
    visible_candidates = [candidate for candidate in candidates if isinstance(candidate, dict)][:50]
    if not visible_candidates:
        body = _evolution_empty_state()
    else:
        body = '<div class="evolution-grid">' + "\n".join(
            _evolution_candidate_card(candidate) for candidate in visible_candidates
        ) + "</div>"
    return f"""<section id="dashboard-page-skill-evolution" class="panel view-panel dashboard-view-page" data-view-page="skill-evolution" hidden>
  {body}
</section>"""


def _evolution_empty_state() -> str:
    steps = [
        ("真实任务", "Codex 完成一次实际维护、审核、收口或纠错任务。"),
        ("暴露缺口", "任务结果显示某个已有工作流技能缺少规则、边界或停止条件。"),
        ("候选提案", "系统只生成改进建议，记录证据和目标技能。"),
        ("人工审核", "审核提案和 diff，判断证据是否足够。"),
        ("确认应用", "只有显式确认后才写入全局技能。"),
        ("可回滚", "应用记录保留备份，必要时可以恢复。"),
    ]
    flow = "\n".join(
        f"""<div class="evolution-empty-step">
      <strong>{text(label)}</strong>
      <span>{text(description)}</span>
    </div>"""
        for label, description in steps
    )
    return f"""<div class="evolution-empty-state" data-evolution-empty-state>
  <div class="evolution-empty-head">
    <h3>暂无技能进化候选</h3>
    <p>只有真实任务暴露出已有技能缺口时，这里才会出现提案。</p>
  </div>
  <div class="evolution-flow">{flow}</div>
  <div class="evolution-example">
    <strong>例如：开发前方向审核</strong>
    <p>如果一次任务说明它没有及时阻止低价值路线，就会形成候选：目标技能、问题证据、建议修改和风险等级。候选不会自动改写全局技能。</p>
  </div>
</div>"""


def _evolution_candidate_card(candidate: dict[str, Any]) -> str:
    evidence = candidate.get("evidence") if isinstance(candidate.get("evidence"), list) else []
    proposed_changes = candidate.get("proposed_changes") if isinstance(candidate.get("proposed_changes"), list) else []
    evidence_text = "；".join(str(item) for item in evidence[:2]) if evidence else "来源任务已记录，待人工审核具体差异。"
    change_text = "；".join(str(item) for item in proposed_changes[:2]) if proposed_changes else "先审核是否需要补触发条件、步骤或停止条件。"
    target_name = _skill_display_name(candidate.get("target_skill_name"))
    raw_status = str(candidate.get("status") or "proposed")
    lifecycle = _evolution_lifecycle_summary(candidate)
    return f"""<article class="evolution-card" role="button" tabindex="0" data-evolution-detail-open data-evolution-target="{text(target_name)}" data-evolution-raw-target="{text(candidate.get("target_skill_name"))}" data-evolution-status="{text(status_label(raw_status))}" data-evolution-risk="{text(_risk_label(candidate.get("risk_level")))}" data-evolution-source-task="{text(_event_task_label(candidate.get("source_task_description")))}" data-evolution-reason="{text(candidate.get("reason") or "该任务暴露了已有技能的改进机会。")}" data-evolution-evidence="{text(evidence_text)}" data-evolution-changes="{text(change_text)}" data-evolution-candidate-path="{text(candidate.get("candidate_path"))}" data-evolution-review-path="{text(candidate.get("review_path"))}" data-evolution-review-decision="{text(candidate.get("review_decision"))}" data-evolution-application-path="{text(candidate.get("application_path"))}" data-evolution-rollback-path="{text(candidate.get("rollback_path"))}" data-evolution-created-at="{text(candidate.get("created_at"))}" data-evolution-updated-at="{text(candidate.get("updated_at"))}" data-evolution-applied-at="{text(candidate.get("applied_at"))}" data-evolution-rolled-back-at="{text(candidate.get("rolled_back_at"))}" data-evolution-lifecycle="{text(lifecycle)}">
  <div class="skill-card-head">
    <div>
      <h3>{text(target_name)}</h3>
      <p>{text(candidate.get("reason") or "该任务暴露了已有技能的改进机会。")}</p>
    </div>
    {badge(raw_status)}
  </div>
  <div class="detail-grid evolution-detail-grid">
    <div><dt>来源任务</dt><dd>{text(_event_task_label(candidate.get("source_task_description")))}</dd></div>
    <div><dt>风险</dt><dd>{text(_risk_label(candidate.get("risk_level")))}</dd></div>
    <div><dt>证据</dt><dd>{text(evidence_text)}</dd></div>
    <div><dt>建议</dt><dd>{text(change_text)}</dd></div>
  </div>
  <div class="platform-row">
    <span>{_icon("link")} {text(candidate.get("candidate_path"))}</span>
  </div>
</article>"""


def _evolution_lifecycle_summary(candidate: dict[str, Any]) -> str:
    steps = ["候选提案：已生成"]
    status = str(candidate.get("status") or "proposed")
    review_path = str(candidate.get("review_path") or "")
    application_path = str(candidate.get("application_path") or "")
    rollback_path = str(candidate.get("rollback_path") or "")
    if review_path or status in {"reviewed", "needs_more_evidence", "applied", "rolled_back"}:
        review_decision = str(candidate.get("review_decision") or "已记录")
        steps.append(f"审核结果：{review_decision}")
    else:
        steps.append("审核结果：等待审核")
    if application_path or status in {"applied", "rolled_back"}:
        steps.append("应用记录：已应用")
    else:
        steps.append("应用记录：未应用")
    if rollback_path or status == "rolled_back":
        steps.append("回滚记录：已回滚")
    else:
        steps.append("回滚记录：未回滚")
    return "；".join(steps)


def _risk_label(value: Any) -> str:
    labels = {
        "low": "低风险",
        "medium": "中风险",
        "high": "高风险",
        "destructive": "破坏性风险",
    }
    raw = str(value or "medium")
    return labels.get(raw, raw)


def _workflow_skill_group_cards(skills: list[dict[str, Any]], collections: list[dict[str, Any]]) -> str:
    workflow_collections = [
        collection for collection in collections if collection.get("collection_id") not in LOCAL_COLLECTION_IDS
    ]
    if not workflow_collections:
        workflow_collections = _workflow_collections_from_skills(skills)
    body = _collection_section(
        "流程分组",
        "按功能分组查看当前可直接复用的流程。",
        workflow_collections,
        show_candidates=False,
    )
    return body or '<p class="muted">当前运行根目录没有找到工作流技能。</p>'


def _workflow_collections_from_skills(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for skill in skills:
        group_id = _skill_group_key(skill)
        grouped.setdefault(group_id, []).append(skill)
    collections = []
    for group_id in SKILL_GROUP_ORDER:
        group_skills = grouped.get(group_id, [])
        if not group_skills:
            continue
        label, description = SKILL_GROUP_LABELS.get(group_id, SKILL_GROUP_LABELS["other-workflows"])
        collections.append(
            {
                "collection_id": group_id,
                "label": label,
                "description": description,
                "skills": group_skills,
                "status_counts": _status_counts_for_display(group_skills),
            }
        )
    return collections


def _skill_card(skill: dict[str, Any]) -> str:
    raw_name = str(skill.get("skill_name") or "")
    status = str(skill.get("status") or "skipped")
    sources = skill.get("source_trajectory_ids") if isinstance(skill.get("source_trajectory_ids"), list) else []
    usage_count = _safe_int(skill.get("usage_count", 0))
    group_id = _skill_group_key(skill)
    group_label, _ = SKILL_GROUP_LABELS.get(group_id, SKILL_GROUP_LABELS["other-workflows"])
    source_label = "全局 Codex Skill" if "global codex skill" in str(skill.get("summary") or "").lower() else group_label
    import_detail = _import_provenance_detail(skill)
    display_name = _skill_display_name(raw_name)
    display_summary = _skill_display_summary(skill.get("summary"))
    detail_summary = _skill_detail_description(skill)
    provenance = _import_provenance_text(skill)
    return f"""<article class="skill-card {text(status)}" role="button" tabindex="0" data-skill-detail-open data-skill-name="{text(raw_name)}" data-detail-name="{text(display_name)}" data-detail-raw-name="{text(raw_name)}" data-detail-status="{text(status)}" data-detail-summary="{text(detail_summary)}" data-detail-usage-count="{text(usage_count)}" data-detail-source-count="{text(len(sources))}" data-detail-source-label="{text(source_label)}" data-detail-provenance="{text(provenance)}">
  <div class="skill-card-head">
    <div>
      <h3>{text(display_name)}</h3>
      <p>{text(display_summary)}</p>
    </div>
    <span class="card-action" title="查看详情">{_icon("package")}</span>
  </div>
  <div class="skill-card-meta">
    <span>{badge(status)}</span>
    <span>复用 {text(usage_count)} 次</span>
    <span>来源 {text(len(sources))} 条</span>
  </div>
  <div class="platform-row">
    <span>{_icon("link")} {text(source_label)}</span>
  </div>
  {import_detail}
</article>"""


def _skill_detail_drawer() -> str:
    return f"""<section class="skill-detail-layer" data-skill-detail-drawer hidden>
  <button class="skill-detail-backdrop" type="button" data-skill-detail-close aria-label="关闭技能详情"></button>
  <aside class="skill-detail-drawer" role="dialog" aria-modal="true" aria-labelledby="skill-detail-title">
    <div class="skill-detail-head">
      <div>
        <div class="view-kicker">技能详情</div>
        <h2 id="skill-detail-title" data-detail-field="name">选择技能</h2>
        <p data-detail-field="rawName">点击流程卡片查看详情。</p>
      </div>
      <button class="detail-close" type="button" data-skill-detail-close aria-label="关闭技能详情">关闭</button>
    </div>
    <div class="skill-detail-body">
      <dl class="detail-grid">
        <div><dt>状态</dt><dd data-detail-field="status">-</dd></div>
        <div><dt>复用次数</dt><dd data-detail-field="usageCount">-</dd></div>
        <div><dt>来源轨迹</dt><dd data-detail-field="sourceCount">-</dd></div>
        <div><dt>分类来源</dt><dd data-detail-field="sourceLabel">-</dd></div>
      </dl>
      <section class="detail-section">
        <h3>说明</h3>
        <p data-detail-field="summary">暂无说明。</p>
      </section>
      <section class="detail-section" data-detail-provenance-section hidden>
        <h3>来源信息</h3>
        <p data-detail-field="provenance"></p>
      </section>
    </div>
  </aside>
</section>"""


def _evolution_detail_drawer() -> str:
    return f"""<section class="skill-detail-layer evolution-detail-layer" data-evolution-detail-drawer hidden>
  <button class="skill-detail-backdrop" type="button" data-evolution-detail-close aria-label="关闭技能进化详情"></button>
  <aside class="skill-detail-drawer" role="dialog" aria-modal="true" aria-labelledby="evolution-detail-title">
    <div class="skill-detail-head">
      <div>
        <div class="view-kicker">技能进化详情</div>
        <h2 id="evolution-detail-title" data-evolution-field="target">选择候选</h2>
        <p data-evolution-field="rawTarget">点击技能进化卡片查看生命周期。</p>
      </div>
      <button class="detail-close" type="button" data-evolution-detail-close aria-label="关闭技能进化详情">关闭</button>
    </div>
    <div class="skill-detail-body">
      <dl class="detail-grid">
        <div><dt>状态</dt><dd data-evolution-field="status">-</dd></div>
        <div><dt>风险</dt><dd data-evolution-field="risk">-</dd></div>
        <div><dt>来源任务</dt><dd data-evolution-field="sourceTask">-</dd></div>
        <div><dt>更新时间</dt><dd data-evolution-field="updatedAt">-</dd></div>
      </dl>
      <section class="detail-section">
        <h3>生命周期</h3>
        <ol class="lifecycle-list">
          <li>候选提案</li>
          <li>审核结果</li>
          <li>应用记录</li>
          <li>回滚记录</li>
        </ol>
        <p data-evolution-field="lifecycle">暂无生命周期记录。</p>
      </section>
      <section class="detail-section">
        <h3>为什么要改</h3>
        <p data-evolution-field="reason">暂无说明。</p>
      </section>
      <section class="detail-section">
        <h3>证据</h3>
        <p data-evolution-field="evidence">暂无证据。</p>
      </section>
      <section class="detail-section">
        <h3>建议修改</h3>
        <p data-evolution-field="changes">暂无建议。</p>
      </section>
      <section class="detail-section">
        <h3>关联文件</h3>
        <p>候选：<span data-evolution-field="candidatePath">-</span></p>
        <p>审核：<span data-evolution-field="reviewPath">-</span></p>
        <p>应用：<span data-evolution-field="applicationPath">-</span></p>
        <p>回滚：<span data-evolution-field="rollbackPath">-</span></p>
      </section>
    </div>
  </aside>
</section>"""


def _skill_tree_branches(skills: list[dict[str, Any]]) -> str:
    branches = [
        ("active", "活跃", "可用技能", 8, "nw"),
        ("staging", "候选", "候选技能", 5, "ne"),
        ("archived", "归档", "已退役技能", 3, "sw"),
        ("rejected", "拒绝", "已阻断候选", 6, "se"),
    ]
    grouped: dict[str, list[dict[str, Any]]] = {status: [] for status, _, _, _, _ in branches}
    for skill in skills:
        grouped.setdefault(str(skill.get("status") or "unknown"), []).append(skill)
    branch_html = "\n".join(
        _skill_branch(status, label, caption, grouped.get(status, []), limit, quadrant)
        for status, label, caption, limit, quadrant in branches
    )
    detail_html = "\n".join(
        _skill_group_detail_panel(status, label, group_id, group_skills)
        for status, label, _, _, _ in branches
        for group_id, group_skills in _group_skills_by_type(grouped.get(status, []))
    )
    total_count = sum(len(grouped.get(status, [])) for status, _, _, _, _ in branches)
    return f"""<div class="tree-canvas tree-fan radial-tree">
  <div class="tree-root radial-center">
    <div class="tree-node root"><strong>运行时根节点</strong><span>{text(total_count)} 个已索引技能</span></div>
  </div>
  <div class="branch-map radial-quadrants">{branch_html}</div>
  <section class="group-detail-modal" data-skill-group-modal role="dialog" aria-modal="true" aria-live="polite" hidden>
    <button class="group-detail-backdrop" type="button" data-skill-group-close aria-label="关闭组别详情"></button>
    <div class="group-detail-surface">{detail_html}</div>
  </section>
</div>"""


def _skill_branch(
    status: str,
    label: str,
    caption: str,
    skills: list[dict[str, Any]],
    limit: int,
    quadrant: str,
) -> str:
    if skills:
        skill_groups = _group_skills_by_type(skills)
        visible_groups = skill_groups[:limit]
        body_parts = [_skill_group_node(group_id, group_skills, status) for group_id, group_skills in visible_groups]
        hidden_count = sum(len(group_skills) for _, group_skills in skill_groups[len(visible_groups) :])
        if hidden_count > 0:
            body_parts.append(f'<div class="more-group">还有 {text(hidden_count)} 个技能分布在更多组别中</div>')
        body = "\n".join(body_parts)
    else:
        body = '<div class="empty-group">该分支暂无技能。</div>'
    return f"""<section class="tree-branch branch-cluster {text(status)} quadrant-{text(quadrant)}">
  <div class="branch-head {text(status)}"><strong>{text(len(skills))}</strong><span>{text(label)} - {text(caption)}</span></div>
  <div class="branch-canopy">{body}</div>
</section>"""


def _skill_group_node(group_id: str, skills: list[dict[str, Any]], status: str) -> str:
    label, caption = SKILL_GROUP_LABELS.get(group_id, SKILL_GROUP_LABELS["other-workflows"])
    usage_count = sum(_safe_int(skill.get("usage_count", 0)) for skill in skills)
    example_names = "、".join(_skill_display_name(skill.get("skill_name")) for skill in skills[:2])
    examples = f"代表：{example_names}" if example_names else "暂无代表技能"
    target_id = _skill_group_target_id(status, group_id)
    return f"""<button class="skill-group {text(status)}" type="button" data-skill-group="{text(group_id)}" data-skill-group-target="{text(target_id)}" aria-controls="{text(target_id)}" aria-expanded="false">
  <span class="group-title">{text(label)}</span>
  <span class="group-count">{text(len(skills))} 个技能</span>
  <span class="group-caption">{text(caption)}</span>
  <span class="group-meta">总复用 {text(usage_count)} 次 · {text(examples)}</span>
  <span class="group-action">查看组内技能</span>
</button>"""


def _skill_group_target_id(status: str, group_id: str) -> str:
    return f"group-{status}-{group_id}"


def _skill_group_detail_panel(status: str, status_name: str, group_id: str, skills: list[dict[str, Any]]) -> str:
    label, caption = SKILL_GROUP_LABELS.get(group_id, SKILL_GROUP_LABELS["other-workflows"])
    visible_skills = skills[:10]
    hidden_count = len(skills) - len(visible_skills)
    usage_count = sum(_safe_int(skill.get("usage_count", 0)) for skill in skills)
    member_body = "\n".join(_skill_group_member(skill) for skill in visible_skills)
    if hidden_count > 0:
        member_body += f'\n<div class="group-more">还有 {text(hidden_count)} 个技能未在面板中展开。</div>'
    target_id = _skill_group_target_id(status, group_id)
    return f"""<article id="{text(target_id)}" class="group-detail-panel {text(status)}" data-skill-group-panel="{text(target_id)}" hidden>
  <div class="group-detail-head">
    <div>
      <div class="group-detail-kicker">{text(status_name)}能力组</div>
      <h3>{text(label)}</h3>
      <p>{text(caption)}</p>
    </div>
    <div class="group-detail-stats"><strong>{text(len(skills))}</strong><span>组内技能</span><span>总复用 {text(usage_count)} 次</span></div>
    <button class="group-detail-close" type="button" data-skill-group-close>收起详情</button>
  </div>
  <div class="group-skill-list">{member_body}</div>
</article>"""


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _skill_group_member(skill: dict[str, Any]) -> str:
    raw_name = str(skill.get("skill_name") or "")
    status = str(skill.get("status") or "skipped")
    sources = skill.get("source_trajectory_ids") or []
    source_text = _source_display_text(sources)
    source_ids = ",".join(str(item) for item in sources)
    usage_count = skill.get("usage_count", 0)
    import_detail = _import_provenance_detail(skill)
    return f"""<article class="group-skill" data-skill-name="{text(raw_name)}" data-source-trajectories="{text(source_ids)}">
  <div>{badge(status)} <span class="skill-name">{text(_skill_display_name(raw_name))}</span></div>
  <div class="group-skill-meta">复用 {text(usage_count)} 次 · 来源 {text(len(sources))} 条</div>
  <p class="skill-summary">{text(_skill_display_summary(skill.get("summary")))}</p>
  <div class="leaf-detail">来源轨迹：{text(source_text)}</div>
  {import_detail}
</article>"""


def _capability_collections(collections: list[dict[str, Any]]) -> str:
    if collections:
        workflow_collections = [
            collection for collection in collections if collection.get("collection_id") not in LOCAL_COLLECTION_IDS
        ]
        body = _collection_section(
            "工作流技能",
            "只展示会影响开发路线、项目维护、运行时接入和阶段推进的工作流技能。",
            workflow_collections,
            show_candidates=False,
        )
        if not body:
            body = '<p class="muted">暂无工作流技能集合。</p>'
    else:
        body = '<p class="muted">暂无能力集合。</p>'
    return f"""<section id="dashboard-page-collections" class="panel view-panel dashboard-view-page" data-view-page="collections" hidden>
  {body}
</section>"""


def _collection_section(
    title: str,
    description: str,
    collections: list[dict[str, Any]],
    *,
    show_candidates: bool,
) -> str:
    if not collections:
        return ""
    cards = "\n".join(_collection_card(collection, show_candidates=show_candidates) for collection in collections[:40])
    return f"""<section class="collection-section">
  <div class="collection-section-head">
    <h3>{text(title)}</h3>
    <p class="muted">{text(description)}</p>
  </div>
  <div class="collection-grid">{cards}</div>
</section>"""


def _collection_card(collection: dict[str, Any], *, show_candidates: bool = True) -> str:
    skills = collection.get("skills") if isinstance(collection.get("skills"), list) else []
    status_counts = collection.get("status_counts") if isinstance(collection.get("status_counts"), dict) else {}
    missing = collection.get("missing_skill_names") if isinstance(collection.get("missing_skill_names"), list) else []
    visible_skills = skills if show_candidates else [skill for skill in skills if skill.get("status") == "active"]
    visible_status_counts = status_counts if show_candidates else _status_counts_for_display(visible_skills)
    skill_items = "\n".join(_collection_skill_item(skill) for skill in visible_skills[:8])
    if not skill_items:
        skill_items = '<p class="muted">该集合暂未匹配到当前技能。</p>'
    missing_text = ""
    if missing:
        missing_text = f'<div class="collection-missing">缺失引用：{text("、".join(str(item) for item in missing[:8]))}</div>'
    status_badges = _collection_status_badges(visible_status_counts, show_candidates=show_candidates)
    return f"""<article class="collection-card" data-collection-id="{text(collection.get("collection_id"))}">
  <div class="collection-head">
    <div>
      <div class="project-name">{text(collection.get("label"))}</div>
      <p class="muted">{text(collection.get("description"))}</p>
    </div>
    <strong>{text(len(visible_skills))}</strong>
  </div>
  {status_badges}
  <div class="collection-skill-list">{skill_items}</div>
  {missing_text}
</article>"""


def _collection_status_badges(status_counts: dict[str, Any], *, show_candidates: bool) -> str:
    badges = [f"<span>活跃 {text(status_counts.get('active', 0))}</span>"]
    if show_candidates:
        badges.append(f"<span>候选 {text(status_counts.get('staging', 0))}</span>")
    archived_count = _safe_int(status_counts.get("archived", 0))
    if show_candidates or archived_count:
        badges.append(f"<span>归档 {text(archived_count)}</span>")
    return f'<div class="project-stats">{"".join(badges)}</div>'


def _status_counts_for_display(skills: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"active": 0, "staging": 0, "archived": 0, "rejected": 0}
    for skill in skills:
        status = skill.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _collection_skill_item(skill: dict[str, Any]) -> str:
    raw_name = str(skill.get("skill_name") or "")
    status = str(skill.get("status") or "skipped")
    sources = skill.get("source_trajectory_ids") if isinstance(skill.get("source_trajectory_ids"), list) else []
    usage_count = _safe_int(skill.get("usage_count", 0))
    group_id = _skill_group_key(skill)
    group_label, _ = SKILL_GROUP_LABELS.get(group_id, SKILL_GROUP_LABELS["other-workflows"])
    source_label = "全局 Codex Skill" if "global codex skill" in str(skill.get("summary") or "").lower() else group_label
    display_name = _skill_display_name(raw_name)
    detail_summary = _skill_detail_description(skill)
    provenance = _import_provenance_text(skill)
    return f"""<div class="collection-skill collection-skill-action" role="button" tabindex="0" data-skill-detail-open data-skill-name="{text(raw_name)}" data-detail-name="{text(display_name)}" data-detail-raw-name="{text(raw_name)}" data-detail-status="{text(status)}" data-detail-summary="{text(detail_summary)}" data-detail-usage-count="{text(usage_count)}" data-detail-source-count="{text(len(sources))}" data-detail-source-label="{text(source_label)}" data-detail-provenance="{text(provenance)}">
  {badge(status)} <span>{text(display_name)}</span>
</div>"""


def _import_provenance_detail(skill: dict[str, Any]) -> str:
    if not skill.get("is_imported"):
        return ""
    audit_label = _audit_status_label(skill.get("audit_status"))
    source = skill.get("import_source") or "未知来源"
    content_hash = str(skill.get("content_hash") or "")
    hash_text = content_hash[:12] if content_hash else "未记录"
    imported_at = skill.get("imported_at") or "未记录"
    return f"""<div class="leaf-detail import-detail">
    <span class="import-chip">外部导入</span>
    <span class="import-chip">{text(audit_label)}</span>
    <div>来源：{text(source)}</div>
    <div>内容哈希：{text(hash_text)} · 导入时间：{text(imported_at)}</div>
  </div>"""


def _import_provenance_text(skill: dict[str, Any]) -> str:
    if not skill.get("is_imported"):
        return ""
    audit_label = _audit_status_label(skill.get("audit_status"))
    source = skill.get("import_source") or "未知来源"
    content_hash = str(skill.get("content_hash") or "")
    hash_text = content_hash[:12] if content_hash else "未记录"
    imported_at = skill.get("imported_at") or "未记录"
    return f"外部导入；{audit_label}；来源：{source}；内容哈希：{hash_text}；导入时间：{imported_at}"


def _audit_status_label(value: Any) -> str:
    labels = {
        "requires_review": "需要审核",
        "passed": "已通过审核",
        "failed": "审核未通过",
    }
    return labels.get(str(value or ""), str(value or "未记录审核状态"))


def _trigger_log(
    events: list[dict[str, Any]],
    *,
    include_project: bool = False,
    counts: dict[str, int] | None = None,
) -> str:
    if not events:
        body = '<p class="muted">暂无运行通道事件。</p>'
    else:
        visible_events = events
        visible_counts = counts if isinstance(counts, dict) else _event_status_counts(visible_events)
        if include_project:
            event_rows = "\n".join(_global_event_row(event) for event in visible_events)
        else:
            event_rows = "\n".join(_event_row(event) for event in visible_events)
        body = f"""{_event_filter_bar(visible_counts)}
  <div class="event-list">
    {event_rows}
    {_event_empty_states(_event_status_counts(visible_events))}
  </div>"""
    return f"""<section id="dashboard-page-trigger-log" class="panel view-panel dashboard-view-page" data-view-page="trigger-log" data-active-event-filter="used" hidden>
  {body}
</section>"""


def _event_row(event: dict[str, Any]) -> str:
    return f"""<article class="event" data-event-status="{text(_event_status(event))}">
  {_event_body(event)}
  {_event_follow_up(event)}
</article>"""


def _global_event_row(event: dict[str, Any]) -> str:
    project = f'<span class="event-project">{text(event.get("project_name"))}</span> '
    return f"""<article class="event" data-event-status="{text(_event_status(event))}">
  {_event_body(event, project_prefix=project)}
  {_event_follow_up(event)}
</article>"""


def _event_filter_bar(counts: dict[str, int]) -> str:
    items = [
        ("used", "已使用", "运行时真正参与并复用了技能"),
        ("entered", "进入观察", "进入运行时观察但未接管"),
        ("skipped", "已跳过", "由普通 Codex 路径直接处理"),
    ]
    buttons = []
    for status, label, title in items:
        active = status == "used"
        buttons.append(
            f"""<button class="event-filter-button{' is-active' if active else ''}" type="button" data-event-filter="{status}" aria-pressed="{'true' if active else 'false'}" title="{text(title)}">{text(label)} <span>{text(counts.get(status, 0))}</span></button>"""
        )
    return f"""<div class="event-filter" role="group" aria-label="触发日志状态筛选">
    {"".join(buttons)}
  </div>"""


def _event_empty_states(counts: dict[str, int]) -> str:
    messages = {
        "used": "暂无已使用记录。",
        "entered": "暂无进入观察记录。",
        "skipped": "暂无已跳过记录。",
    }
    return "\n".join(
        f'<p class="muted event-empty" data-event-empty="{status}">{text(message)}</p>'
        for status, message in messages.items()
        if counts.get(status, 0) == 0
    )


def _event_status_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"used": 0, "entered": 0, "skipped": 0}
    for event in events:
        counts[_event_status(event)] += 1
    return counts


def _event_status(event: dict[str, Any]) -> str:
    raw = str(event.get("runtime_lane_status") or "skipped")
    return raw if raw in {"used", "entered", "skipped"} else "skipped"


def _event_body(event: dict[str, Any], *, project_prefix: str = "") -> str:
    selected_skill_name = event.get("selected_skill_name")
    handler = _event_handler_label(event, selected_skill_name)
    return f"""<div>{project_prefix}{badge(event.get("runtime_lane_status"))} <strong>任务：{text(_event_task_label(event.get("task_description")))}</strong></div>
  <div class="muted">时间：{text(event.get("timestamp"))} · 处理方式：{text(handler)}</div>
  <div class="reason">结果：{text(_event_reason_label(event))}</div>"""


def _event_handler_label(event: dict[str, Any], selected_skill_name: Any) -> str:
    if selected_skill_name:
        return _skill_display_name(selected_skill_name)
    status = _event_status(event)
    if status == "used":
        return "运行时参与（记录经验）"
    if status == "entered":
        return "运行时观察"
    return "普通 Codex 处理"


def _event_task_label(value: Any) -> str:
    raw = str(value or "未记录任务").strip()
    if raw in TASK_DESCRIPTION_LABELS:
        return TASK_DESCRIPTION_LABELS[raw]
    words = raw.replace("-", " ").replace("_", " ").split()
    if not words:
        return "未记录任务"
    translated = [TASK_WORD_LABELS.get(word.lower(), word) for word in words]
    if translated == words:
        return raw
    return " ".join(translated)


def _event_reason_label(event: dict[str, Any]) -> str:
    status = str(event.get("runtime_lane_status") or "")
    reason = str(event.get("runtime_lane_reason") or "").strip()
    reason_detail = _runtime_reason_detail(reason)
    if status == "used":
        prefix = "运行时已参与处理，并复用了匹配技能。"
    elif status == "entered":
        prefix = "任务已进入运行时观察，但没有自动接管。"
    elif status == "skipped":
        prefix = "Codex 直接处理，运行时没有接管。"
    else:
        prefix = "已记录运行时事件。"
    if reason_detail and reason_detail != prefix:
        return f"{prefix}原因：{reason_detail}"
    return prefix


def _runtime_reason_detail(reason: str) -> str:
    if not reason:
        return ""
    if reason in RUNTIME_REASON_LABELS:
        return RUNTIME_REASON_LABELS[reason]
    lowered = reason.lower()
    if "does not match a phase-one default-in family yet" in lowered:
        return "这是本地可复用任务，但不属于当前默认接管范围。"
    if "guarded-in" in lowered and "skipped" in lowered:
        return "任务被判定为需要 Codex 正常处理的本地工作，运行时只记录结果。"
    if "default-out" in lowered:
        return "任务不适合进入当前运行时接管范围。"
    if "auto-executed" in lowered:
        return RUNTIME_REASON_LABELS["auto-executed reusable skill"]
    if "captured learning payload" in lowered:
        return RUNTIME_REASON_LABELS["captured learning payload"]
    return reason


def _event_follow_up(event: dict[str, Any]) -> str:
    next_action = event.get("recommended_next_action")
    labels = event.get("available_host_operation_labels")
    if not isinstance(next_action, str) or not next_action:
        return ""
    operation_labels = [_event_follow_up_label(str(label)) for label in labels if isinstance(label, str)] if isinstance(labels, list) else []
    labels_html = ""
    if operation_labels:
        labels_html = f"""<div class="event-actions">{text("；".join(operation_labels[:4]))}</div>"""
    return f"""<div class="event-followup"><strong>下一步：{text(_event_follow_up_label(next_action))}</strong>{labels_html}</div>"""


def _event_follow_up_label(value: Any) -> str:
    labels = {
        "distill_trajectory": "整理这次任务轨迹",
        "Distill captured trajectory": "整理这次任务轨迹",
        "Promote captured workflow": "提升这条捕获到的工作流",
        "Promote captured workflow globally": "提升这条捕获到的工作流到全局",
    }
    raw = str(value or "").strip()
    return labels.get(raw, raw)


def _governance(governance: dict[str, Any], diagnostics: list[str]) -> str:
    duplicate_candidates = governance.get("duplicate_candidates") or []
    if duplicate_candidates:
        duplicate_body = f"<pre>{text(duplicate_candidates)}</pre>"
    else:
        duplicate_body = """<div class="muted">
  <p>当前没有发现需要合并处理的重复候选。</p>
  <p>这表示目前没有两条过于相似、可能其实是同一项技能的候选。</p>
</div>"""
    diagnostics_body = "".join(_governance_diagnostic_item(item) for item in diagnostics) or "<li>没有诊断信息。</li>"
    return f"""<section id="dashboard-page-governance" class="panel view-panel dashboard-view-page" data-view-page="governance" hidden>
  {duplicate_body}
  <h3>诊断信息</h3>
  <ul>{diagnostics_body}</ul>
</section>"""


def _governance_diagnostic_item(item: Any) -> str:
    raw = str(item or "").strip()
    if not raw:
        return "<li>没有诊断信息。</li>"
    lowered = raw.lower()
    normalized = raw.replace("/", "\\")
    if lowered.startswith("missing skill directory:") and normalized.endswith("skill_store\\rejected"):
        return """<li>
  <strong>当前还没有“已拒绝候选”目录。</strong>
  <div class="muted">这不是错误，只表示你还没有把候选明确标记为拒绝。</div>
  <div class="muted">暂时不需要处理。只有你开始使用“拒绝候选”流程时，这个目录才会出现。</div>
</li>"""
    if lowered.startswith("missing skill directory:"):
        missing_target = raw.split(":", 1)[1].strip() if ":" in raw else raw
        return f"""<li>
  <strong>缺少技能目录：{text(missing_target)}</strong>
  <div class="muted">运行时原本希望在这里找到对应状态的技能文件。</div>
</li>"""
    if lowered.startswith("could not build governance report:"):
        detail = raw.split(":", 1)[1].strip() if ":" in raw else raw
        return f"""<li>
  <strong>治理报告暂时无法生成。</strong>
  <div class="muted">原因：{text(detail)}</div>
</li>"""
    if lowered.startswith("could not read skill index:"):
        detail = raw.split(":", 1)[1].strip() if ":" in raw else raw
        return f"""<li>
  <strong>技能索引暂时读不到。</strong>
  <div class="muted">原因：{text(detail)}</div>
</li>"""
    return f"<li>{text(raw)}</li>"


def _platform_inventory(inventory: dict[str, Any]) -> str:
    items = inventory.get("items") if isinstance(inventory, dict) else []
    diagnostics = inventory.get("diagnostics") if isinstance(inventory, dict) else []
    if not isinstance(items, list):
        items = []
    if not isinstance(diagnostics, list):
        diagnostics = []
    if items:
        body = '<div class="platform-card-grid">' + "\n".join(_platform_item_card(item) for item in items[:80]) + "</div>"
    else:
        body = '<p class="muted">尚未在已知平台目录中发现 SKILL.md 技能。</p>'
    diagnostics_body = "".join(f"<li>{text(item)}</li>" for item in diagnostics[:20]) or "<li>没有平台目录诊断信息。</li>"
    return f"""<section id="dashboard-page-platforms" class="panel view-panel dashboard-view-page" data-view-page="platforms" hidden>
  {body}
  <h3>平台诊断</h3>
  <ul class="scan-list">{diagnostics_body}</ul>
</section>"""


def _platform_item_card(item: dict[str, Any]) -> str:
    description = item.get("description")
    description_html = f"""  <p class="platform-summary">{text(description)}</p>\n""" if description else ""
    return f"""<article class="platform-skill-card">
  <div class="platform-card-head">
    <div>
      <h3>{text(item.get("skill_name"))}</h3>
      <div class="platform-path-chip" title="{text(item.get("skill_path"))}">{text(item.get("skill_path"))}</div>
    </div>
    <span class="card-action" title="平台技能">{_icon("package")}</span>
  </div>
{description_html}  <div class="skill-card-meta">
    <span>{text(item.get("display_name"))}</span>
    <span>{text(_platform_source_role_label(item.get("source_role")))}</span>
    <span>{text(_platform_ownership_label(item.get("ownership")))}</span>
    <span>{text(_platform_link_type_label(item.get("link_type")))}</span>
  </div>
  <div class="platform-row">
    <span>{_icon("link")} {text(item.get("source_root"))}</span>
  </div>
</article>"""


def _platform_source_role_label(value: Any) -> str:
    labels = {
        "authoritative_global_skill": "全局权威",
        "project_runtime_skill": "项目运行时",
        "platform_skill": "平台技能",
    }
    raw = str(value or "")
    return labels.get(raw, raw or "未标记")


def _platform_ownership_label(value: Any) -> str:
    labels = {
        "external": "外部",
        "local": "本地",
        "project": "项目",
    }
    raw = str(value or "")
    return labels.get(raw, raw or "未知归属")


def _platform_link_type_label(value: Any) -> str:
    labels = {
        "read_only": "只读来源",
        "copy": "复制",
        "symlink": "链接",
    }
    raw = str(value or "")
    return labels.get(raw, raw or "未知来源")
