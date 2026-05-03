from __future__ import annotations

from typing import Any

from skill_runtime.dashboard.templates import SCRIPT, STYLE, badge, text


SKILL_NAME_LABELS = {
    "directory_json_to_csv_dogfood": "目录 JSON 批量转 CSV",
    "directory_text_cleanup_dogfood": "目录文本清理",
    "json_to_csv_dogfood": "JSON 转 CSV",
    "merge_text_files": "合并文本文件",
    "text_replace_dogfood": "文本替换",
    "archive_log_files_dogfood": "归档日志文件",
    "bridge_config_test": "桥接配置测试",
    "explainable_rule_test": "可解释规则测试",
    "fallback_rule_test": "兜底规则测试",
    "generalized_merge_rule_test": "通用合并规则测试",
    "manual_fallback_demo": "手动兜底演示",
    "merge_text_files_generated_v2": "合并文本文件生成版 v2",
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
    "Merge all txt files in a directory into one markdown file.": "将目录中的所有 txt 文件合并为一个 Markdown 文件。",
    "Generate a report from mixed observations without a known deterministic file rule.": "从混合观察结果生成报告，适用于没有固定文件规则的场景。",
    "Generate a report from mixed observations without a deterministic rule.": "从混合观察结果生成报告，适用于没有固定规则的场景。",
    "Rename all txt files in a directory by prefixing them with a value.": "通过添加前缀批量重命名目录中的 txt 文件。",
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


def render_dashboard_html(data: dict[str, Any]) -> str:
    global_data = data.get("global") if isinstance(data.get("global"), dict) else None
    title = "全局运行时观察面板" if global_data else "运行时可观察面板"
    subtitle = (
        f"{text(data.get('root'))} · 已合并跨工作区调用记录"
        if global_data
        else text(data.get("root"))
    )
    read_only_text = (
        "同一页面内查看当前项目技能树、触发日志、治理快照，以及跨工作区调用记录。"
        if global_data
        else "不编辑技能、不提升、不归档，也不做跨工作区聚合。"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{STYLE}</style>
</head>
<body data-active-view="skill-tree">
  <main>
    <section class="hero">
      <div>
        <div class="eyebrow">技能运行时</div>
        <h1>{title}</h1>
        <div class="muted">{subtitle}</div>
      </div>
      <div class="panel">
        <strong>只读视图</strong>
        <div class="muted">{read_only_text}</div>
      </div>
    </section>
    {_overview(data.get("overview", {}))}
    {_global_overview(global_data.get("overview", {})) if global_data else ""}
    {_view_nav(global_enabled=bool(global_data))}
    {_skill_tree(data.get("skills", []))}
    {_capability_collections(data.get("capability_collections", []))}
    {_trigger_log(data.get("events", []))}
    {_governance(data.get("governance", {}), data.get("diagnostics", []))}
    {_platform_inventory(data.get("platform_inventory", {}))}
    {_global_projects_view(global_data) if global_data else ""}
    {_global_log_view(global_data) if global_data else ""}
  </main>
  {SCRIPT}
</body>
</html>
"""


def _overview(overview: dict[str, Any]) -> str:
    counts = overview.get("recent_event_counts", {})
    return f"""<section class="panel">
  <h2>当前项目总览</h2>
  <div class="grid">
    {_metric("活跃", overview.get("active_count", 0), "可用技能")}
    {_metric("候选", overview.get("staging_count", 0), "候选技能")}
    {_metric("已使用", counts.get("used", 0), "runtime 完成参与")}
    {_metric("已进入", counts.get("entered", 0), "进入 runtime 观察")}
    {_metric("已跳过", counts.get("skipped", 0), "普通 Codex 路径")}
  </div>
  <p class="muted">最近事件：{text(overview.get("latest_event_time") or "暂无运行通道事件")}</p>
</section>"""


def _global_overview(overview: dict[str, Any]) -> str:
    counts = overview.get("recent_event_counts", {})
    return f"""<section class="panel">
  <h2>全局总览</h2>
  <div class="grid">
    {_metric("项目数", overview.get("project_count", 0), "发现调用记录的工作区")}
    {_metric("事件数", overview.get("event_count", 0), "最近全局事件")}
    {_metric("已使用", counts.get("used", 0), "runtime 完成参与")}
    {_metric("已进入", counts.get("entered", 0), "进入 runtime 观察")}
    {_metric("已跳过", counts.get("skipped", 0), "普通 Codex 路径")}
  </div>
  <p class="muted">最近事件：{text(overview.get("latest_event_time") or "暂无全局运行通道事件")}</p>
</section>"""


def _project_card(project: dict[str, Any]) -> str:
    counts = project.get("recent_event_counts", {})
    return f"""<article class="project-card">
  <div class="project-name">{text(project.get("project_name"))}</div>
  <div class="project-path">{text(project.get("project_root"))}</div>
  <div class="project-stats">
    <span>{text(project.get("event_count", 0))} 条事件</span>
    <span>{text(counts.get("used", 0))} 次使用</span>
    <span>{text(counts.get("entered", 0))} 次进入</span>
    <span>{text(counts.get("skipped", 0))} 次跳过</span>
  </div>
  <div class="muted">最近：{text(project.get("latest_event_time") or "暂无")}</div>
</article>"""


def _global_event_row(event: dict[str, Any]) -> str:
    selected_skill_name = event.get("selected_skill_name")
    skill = _skill_display_name(selected_skill_name) if selected_skill_name else "普通 Codex 路径"
    return f"""<article class="event">
  <div><span class="event-project">{text(event.get("project_name"))}</span> {badge(event.get("runtime_lane_status"))} <strong>{text(event.get("task_description"))}</strong></div>
  <div class="muted">{text(event.get("timestamp"))} - {text(skill)}</div>
  <div class="reason">{text(event.get("runtime_lane_reason"))}</div>
  {_event_follow_up(event)}
</article>"""


def _global_projects_view(global_data: dict[str, Any]) -> str:
    return f"""<section id="global-projects-view" class="panel view-panel dashboard-view-page" data-view-page="global-projects" hidden>
  <div class="view-kicker">视图 06</div>
  <h2>全局项目概览</h2>
  {_project_overview_body(global_data.get("projects", []))}
  <h3>扫描范围</h3>
  {_scan_root_lists(global_data.get("scan_roots", []), global_data.get("diagnostics", []))}
</section>"""


def _global_log_view(global_data: dict[str, Any]) -> str:
    events = global_data.get("events", [])
    if not events:
        body = '<p class="muted">暂无全局运行通道事件。</p>'
    else:
        body = "\n".join(_global_event_row(event) for event in events[:100])
    return f"""<section id="global-log-view" class="panel view-panel dashboard-view-page" data-view-page="global-log" hidden>
  <div class="view-kicker">视图 07</div>
  <h2>全局触发日志</h2>
  {body}
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


def _view_nav(*, global_enabled: bool = False) -> str:
    global_links = ""
    if global_enabled:
        global_links = """
  <button class="view-link" type="button" data-view-target="global-projects" aria-controls="global-projects-view" aria-current="false"><strong>全局项目</strong><span>跨工作区概览</span></button>
  <button class="view-link" type="button" data-view-target="global-log" aria-controls="global-log-view" aria-current="false"><strong>全局日志</strong><span>跨项目事件</span></button>"""
    return f"""<nav class="view-nav" aria-label="面板视图">
  <button class="view-link is-active" type="button" data-view-target="skill-tree" aria-controls="skill-tree-view" aria-current="page"><strong>技能树</strong><span>生命周期分支</span></button>
  <button class="view-link" type="button" data-view-target="collections" aria-controls="collections-view" aria-current="false"><strong>能力集合</strong><span>组织层</span></button>
  <button class="view-link" type="button" data-view-target="trigger-log" aria-controls="trigger-log-view" aria-current="false"><strong>触发日志</strong><span>运行通道事件</span></button>
  <button class="view-link" type="button" data-view-target="governance" aria-controls="governance-view" aria-current="false"><strong>治理快照</strong><span>技能库健康</span></button>
  <button class="view-link" type="button" data-view-target="platforms" aria-controls="platforms-view" aria-current="false"><strong>平台与项目</strong><span>只读来源</span></button>
  {global_links}
</nav>"""


def _metric(label: str, value: Any, caption: str) -> str:
    return f'<div class="metric"><strong>{text(value)}</strong><span>{text(label)} - {text(caption)}</span></div>'


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


def _skill_tree(skills: list[dict[str, Any]]) -> str:
    if not skills:
        body = '<p class="muted">当前运行根目录没有找到技能。</p>'
    else:
        body = _skill_tree_branches(skills[:80])
    return f"""<section id="skill-tree-view" class="panel view-panel dashboard-view-page" data-view-page="skill-tree">
  <div class="view-kicker">视图 01</div>
  <h2>技能树视图</h2>
  {body}
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
        body = '<div class="collection-grid">' + "\n".join(_collection_card(collection) for collection in collections[:40]) + "</div>"
    else:
        body = '<p class="muted">暂无能力集合。</p>'
    return f"""<section id="collections-view" class="panel view-panel dashboard-view-page" data-view-page="collections" hidden>
  <div class="view-kicker">视图 02</div>
  <h2>能力集合</h2>
  <p class="muted">集合是只读组织层，不改变执行、审核、提升或归档语义。</p>
  {body}
</section>"""


def _collection_card(collection: dict[str, Any]) -> str:
    skills = collection.get("skills") if isinstance(collection.get("skills"), list) else []
    status_counts = collection.get("status_counts") if isinstance(collection.get("status_counts"), dict) else {}
    missing = collection.get("missing_skill_names") if isinstance(collection.get("missing_skill_names"), list) else []
    skill_items = "\n".join(_collection_skill_item(skill) for skill in skills[:8])
    if not skill_items:
        skill_items = '<p class="muted">该集合暂未匹配到当前技能。</p>'
    missing_text = ""
    if missing:
        missing_text = f'<div class="collection-missing">缺失引用：{text("、".join(str(item) for item in missing[:8]))}</div>'
    return f"""<article class="collection-card" data-collection-id="{text(collection.get("collection_id"))}">
  <div class="collection-head">
    <div>
      <div class="project-name">{text(collection.get("label"))}</div>
      <p class="muted">{text(collection.get("description"))}</p>
    </div>
    <strong>{text(len(skills))}</strong>
  </div>
  <div class="project-stats">
    <span>活跃 {text(status_counts.get("active", 0))}</span>
    <span>候选 {text(status_counts.get("staging", 0))}</span>
    <span>归档 {text(status_counts.get("archived", 0))}</span>
  </div>
  <div class="collection-skill-list">{skill_items}</div>
  {missing_text}
</article>"""


def _collection_skill_item(skill: dict[str, Any]) -> str:
    status = str(skill.get("status") or "skipped")
    return f"""<div class="collection-skill">
  {badge(status)} <span>{text(_skill_display_name(skill.get("skill_name")))}</span>
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


def _audit_status_label(value: Any) -> str:
    labels = {
        "requires_review": "需要审核",
        "passed": "已通过审核",
        "failed": "审核未通过",
    }
    return labels.get(str(value or ""), str(value or "未记录审核状态"))


def _trigger_log(events: list[dict[str, Any]]) -> str:
    if not events:
        body = '<p class="muted">暂无运行通道事件。</p>'
    else:
        body = "\n".join(_event_row(event) for event in events[:50])
    return f"""<section id="trigger-log-view" class="panel view-panel dashboard-view-page" data-view-page="trigger-log" hidden>
  <div class="view-kicker">视图 03</div>
  <h2>触发日志视图</h2>
  {body}
</section>"""


def _event_row(event: dict[str, Any]) -> str:
    selected_skill_name = event.get("selected_skill_name")
    skill = _skill_display_name(selected_skill_name) if selected_skill_name else "普通 Codex 路径"
    return f"""<article class="event">
  <div>{badge(event.get("runtime_lane_status"))} <strong>{text(event.get("task_description"))}</strong></div>
  <div class="muted">{text(event.get("timestamp"))} - {text(skill)}</div>
  <div class="reason">{text(event.get("runtime_lane_reason"))}</div>
  {_event_follow_up(event)}
</article>"""


def _event_follow_up(event: dict[str, Any]) -> str:
    next_action = event.get("recommended_next_action")
    labels = event.get("available_host_operation_labels")
    if not isinstance(next_action, str) or not next_action:
        return ""
    operation_labels = [str(label) for label in labels if isinstance(label, str)] if isinstance(labels, list) else []
    labels_html = ""
    if operation_labels:
        labels_html = f"""<div class="event-actions">{text("；".join(operation_labels[:4]))}</div>"""
    return f"""<div class="event-followup"><strong>下一步：{text(next_action)}</strong>{labels_html}</div>"""


def _governance(governance: dict[str, Any], diagnostics: list[str]) -> str:
    duplicate_candidates = governance.get("duplicate_candidates") or []
    if duplicate_candidates:
        duplicate_body = f"<pre>{text(duplicate_candidates)}</pre>"
    else:
        duplicate_body = '<p class="muted">没有发现重复候选。</p>'
    diagnostics_body = "".join(f"<li>{text(item)}</li>" for item in diagnostics) or "<li>没有诊断信息。</li>"
    return f"""<section id="governance-view" class="panel view-panel dashboard-view-page" data-view-page="governance" hidden>
  <div class="view-kicker">视图 04</div>
  <h2>治理快照</h2>
  {duplicate_body}
  <h3>诊断信息</h3>
  <ul>{diagnostics_body}</ul>
</section>"""


def _platform_inventory(inventory: dict[str, Any]) -> str:
    items = inventory.get("items") if isinstance(inventory, dict) else []
    diagnostics = inventory.get("diagnostics") if isinstance(inventory, dict) else []
    if not isinstance(items, list):
        items = []
    if not isinstance(diagnostics, list):
        diagnostics = []
    if items:
        body = '<div class="project-grid">' + "\n".join(_platform_item_card(item) for item in items[:80]) + "</div>"
    else:
        body = '<p class="muted">尚未在已知平台目录中发现 SKILL.md 技能。</p>'
    diagnostics_body = "".join(f"<li>{text(item)}</li>" for item in diagnostics[:20]) or "<li>没有平台目录诊断信息。</li>"
    return f"""<section id="platforms-view" class="panel view-panel dashboard-view-page" data-view-page="platforms" hidden>
  <div class="view-kicker">视图 05</div>
  <h2>平台与项目</h2>
  <p class="muted">只读查看 Codex、Claude Code、Cursor、Gemini CLI 和共享 Agents 技能目录，不复制、不链接、不安装。</p>
  {body}
  <h3>平台诊断</h3>
  <ul class="scan-list">{diagnostics_body}</ul>
</section>"""


def _platform_item_card(item: dict[str, Any]) -> str:
    description = item.get("description")
    description_html = f"""  <div class="muted">{text(description)}</div>\n""" if description else ""
    return f"""<article class="project-card">
  <div class="project-name">{text(item.get("skill_name"))}</div>
  <div class="project-path">{text(item.get("skill_path"))}</div>
{description_html}  <div class="muted">角色：{text(item.get("source_role"))}</div>
  <div class="project-stats">
    <span>{text(item.get("display_name"))}</span>
    <span>{text(item.get("ownership"))}</span>
    <span>{text(item.get("link_type"))}</span>
  </div>
  <div class="muted">来源：{text(item.get("source_root"))}</div>
</article>"""
