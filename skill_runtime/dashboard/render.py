from __future__ import annotations

from typing import Any

from skill_runtime.dashboard.templates import STYLE, badge, text


def render_dashboard_html(data: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Runtime Observability Dashboard</title>
  <style>{STYLE}</style>
</head>
<body>
  <main>
    <section class="hero">
      <div>
        <div class="eyebrow">Skill Runtime</div>
        <h1>Runtime Observability Dashboard</h1>
        <div class="muted">{text(data.get("root"))}</div>
      </div>
      <div class="panel">
        <strong>Read-only view</strong>
        <div class="muted">No skill edits, promotion, archive, or cross-workspace aggregation.</div>
      </div>
    </section>
    {_overview(data.get("overview", {}))}
    <section class="two">
      {_skill_tree(data.get("skills", []))}
      {_trigger_log(data.get("events", []))}
    </section>
    {_governance(data.get("governance", {}), data.get("diagnostics", []))}
  </main>
</body>
</html>
"""


def _overview(overview: dict[str, Any]) -> str:
    counts = overview.get("recent_event_counts", {})
    return f"""<section class="panel">
  <h2>Overview</h2>
  <div class="grid">
    {_metric("Active", overview.get("active_count", 0), "usable skills")}
    {_metric("Staging", overview.get("staging_count", 0), "candidate skills")}
    {_metric("Used", counts.get("used", 0), "recent lane events")}
    {_metric("Skipped", counts.get("skipped", 0), "normal Codex path")}
  </div>
  <p class="muted">Latest event: {text(overview.get("latest_event_time") or "No runtime lane events yet")}</p>
</section>"""


def _metric(label: str, value: Any, caption: str) -> str:
    return f'<div class="metric"><strong>{text(value)}</strong><span>{text(label)} - {text(caption)}</span></div>'


def _skill_tree(skills: list[dict[str, Any]]) -> str:
    if not skills:
        body = '<p class="muted">No skills found in this runtime root.</p>'
    else:
        body = "\n".join(_skill_card(skill) for skill in skills[:80])
    return f'<section class="panel"><h2>Skill Tree</h2>{body}</section>'


def _skill_card(skill: dict[str, Any]) -> str:
    sources = skill.get("source_trajectory_ids") or []
    source_text = ", ".join(text(item) for item in sources) if sources else "No source trajectory recorded"
    return f"""<article class="skill">
  <div>{badge(skill.get("status"))} <span class="skill-name">{text(skill.get("skill_name"))}</span></div>
  <p>{text(skill.get("summary"))}</p>
  <div class="muted">trajectory -> {source_text}</div>
  <div class="muted">reuse count: {text(skill.get("usage_count", 0))}</div>
</article>"""


def _trigger_log(events: list[dict[str, Any]]) -> str:
    if not events:
        body = '<p class="muted">No runtime lane events yet.</p>'
    else:
        body = "\n".join(_event_row(event) for event in events[:50])
    return f'<section class="panel"><h2>Trigger Log</h2>{body}</section>'


def _event_row(event: dict[str, Any]) -> str:
    skill = event.get("selected_skill_name") or "normal Codex path"
    return f"""<article class="event">
  <div>{badge(event.get("runtime_lane_status"))} <strong>{text(event.get("task_description"))}</strong></div>
  <div class="muted">{text(event.get("timestamp"))} - {text(skill)}</div>
  <div class="reason">{text(event.get("runtime_lane_reason"))}</div>
</article>"""


def _governance(governance: dict[str, Any], diagnostics: list[str]) -> str:
    duplicate_candidates = governance.get("duplicate_candidates") or []
    if duplicate_candidates:
        duplicate_body = f"<pre>{text(duplicate_candidates)}</pre>"
    else:
        duplicate_body = '<p class="muted">No duplicate candidates reported.</p>'
    diagnostics_body = "".join(f"<li>{text(item)}</li>" for item in diagnostics) or "<li>No diagnostics.</li>"
    return f"""<section class="panel" style="margin-top:16px">
  <h2>Governance Snapshot</h2>
  {duplicate_body}
  <h3>Diagnostics</h3>
  <ul>{diagnostics_body}</ul>
</section>"""
