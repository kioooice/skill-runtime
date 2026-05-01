from __future__ import annotations

from html import escape
from typing import Any

STYLE = """
:root {
  --bg: #f7f1e6;
  --panel: #fffaf0;
  --ink: #26221c;
  --muted: #6d6253;
  --line: #d9cbb7;
  --line-strong: #bd915a;
  --used: #1f7a4d;
  --entered: #9a6a16;
  --skipped: #6a7280;
  --active: #1f7a4d;
  --staging: #9a6a16;
  --archived: #667085;
  --rejected: #a33b33;
}
* { box-sizing: border-box; min-width: 0; }
html { scroll-behavior: auto; }
body {
  margin: 0;
  background: radial-gradient(circle at top left, #ffe7c2 0, transparent 34%), var(--bg);
  color: var(--ink);
  font-family: "Noto Serif SC", "Songti SC", "Microsoft YaHei", Georgia, "Times New Roman", serif;
  overflow-x: hidden;
}
main { width: min(1180px, calc(100% - 40px)); margin: 36px auto; }
.hero { display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 24px; }
.eyebrow { color: var(--muted); text-transform: uppercase; letter-spacing: .14em; font-size: 12px; }
h1 { font-size: clamp(34px, 4.5vw, 44px); margin: 8px 0; line-height: 1; overflow-wrap: anywhere; }
h2 { margin: 0 0 14px; }
p, span, div, article, section, li { overflow-wrap: anywhere; word-break: break-word; white-space: normal; }
.panel { background: rgba(255,250,240,.92); border: 1px solid var(--line); border-radius: 22px; padding: 20px; box-shadow: 0 20px 60px rgba(79,54,27,.08); min-width: 0; overflow: hidden; }
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.two { display: grid; grid-template-columns: 1fr; gap: 16px; margin-top: 16px; }
.view-nav { display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0; }
.view-link { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 999px; padding: 9px 14px; color: var(--ink); background: rgba(255,253,247,.78); text-decoration: none; box-shadow: 0 10px 24px rgba(79,54,27,.06); cursor: pointer; font: inherit; }
.view-link.is-active { border-color: var(--line-strong); background: #fff6e5; box-shadow: 0 14px 30px rgba(154,106,22,.12); }
.view-link span { color: var(--muted); font-size: 13px; }
.view-panel { margin-top: 16px; }
.dashboard-view-page { display: none; }
body[data-active-view="skill-tree"] [data-view-page="skill-tree"],
body[data-active-view="trigger-log"] [data-view-page="trigger-log"],
body[data-active-view="governance"] [data-view-page="governance"] { display: block; }
.view-kicker { color: var(--muted); text-transform: uppercase; letter-spacing: .12em; font-size: 12px; margin-bottom: 6px; }
.metric { border-left: 4px solid #b8792f; padding-left: 12px; }
.metric strong { display: block; font-size: 30px; }
.metric span, .muted { color: var(--muted); }
.tree-canvas { padding-top: 4px; }
.tree-root { display: flex; justify-content: center; position: relative; margin-bottom: 30px; }
.tree-root::after { content: ""; position: absolute; left: 50%; bottom: -24px; height: 24px; border-left: 2px solid var(--line-strong); }
.tree-node { background: #fffdf7; border: 1px solid var(--line); border-radius: 18px; padding: 12px 16px; box-shadow: 0 12px 30px rgba(79,54,27,.08); min-width: 0; overflow-wrap: anywhere; }
.tree-node.root { border-color: var(--line-strong); text-align: center; min-width: 220px; }
.tree-node strong { display: block; }
.tree-node span { color: var(--muted); font-size: 14px; }
.tree-branches { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; position: relative; }
.tree-branches::before { content: ""; position: absolute; top: -18px; left: 12%; right: 12%; border-top: 2px solid var(--line-strong); }
.tree-branch { position: relative; min-width: 0; padding-top: 18px; }
.tree-branch::before { content: ""; position: absolute; top: -18px; left: 50%; height: 18px; border-left: 2px solid var(--line-strong); }
.branch-head { border: 1px solid var(--line); border-top: 4px solid var(--skipped); border-radius: 18px; padding: 12px; background: rgba(255,253,247,.9); min-width: 0; overflow-wrap: anywhere; }
.branch-head strong { display: block; font-size: 28px; line-height: 1; margin-bottom: 4px; }
.branch-head span { color: var(--muted); font-size: 14px; }
.branch-head.active { border-top-color: var(--active); }
.branch-head.staging { border-top-color: var(--staging); }
.branch-head.archived { border-top-color: var(--archived); }
.branch-head.rejected { border-top-color: var(--rejected); }
.branch-skills { position: relative; margin-top: 14px; padding-left: 18px; display: grid; gap: 10px; }
.branch-skills::before { content: ""; position: absolute; left: 7px; top: 0; bottom: 12px; border-left: 2px dashed var(--line); }
.skill-node { position: relative; border: 1px solid var(--line); border-radius: 16px; padding: 12px; background: #fffdf7; min-width: 0; overflow-wrap: anywhere; }
.skill-node::before { content: ""; position: absolute; left: -12px; top: 22px; width: 12px; border-top: 2px dashed var(--line); }
.skill-name { display: block; font-weight: 700; margin-bottom: 8px; overflow-wrap: anywhere; }
.skill-summary { margin: 0 0 10px; }
.empty-branch, .more-node { border: 1px dashed var(--line); border-radius: 16px; padding: 12px; color: var(--muted); background: rgba(255,253,247,.55); }
.more-node { position: relative; font-style: italic; overflow-wrap: anywhere; }
.more-node::before { content: ""; position: absolute; left: -12px; top: 22px; width: 12px; border-top: 2px dashed var(--line); }
.badge { display: inline-block; border-radius: 999px; padding: 3px 9px; font-size: 12px; color: white; background: var(--skipped); }
.badge.used { background: var(--used); }
.badge.entered { background: var(--entered); }
.badge.skipped { background: var(--skipped); }
.badge.active { background: var(--active); }
.badge.staging { background: var(--staging); }
.badge.archived { background: var(--archived); }
.badge.rejected { background: var(--rejected); }
.event { border-bottom: 1px solid var(--line); padding: 12px 0; }
.event:last-child { border-bottom: 0; }
.reason { color: var(--muted); margin-top: 4px; }
pre { white-space: pre-wrap; word-break: break-word; background: #2b2118; color: #fff6e8; padding: 12px; border-radius: 14px; }
@media (max-width: 860px) {
  main { width: min(calc(100% - 24px), 1180px); margin: 20px auto; }
  .grid, .two { grid-template-columns: 1fr; }
  .hero { display: block; }
  h1 { font-size: 31px; }
  .panel { padding: 18px; }
  .hero .panel { margin-top: 14px; }
  .tree-root { justify-content: flex-start; margin-bottom: 18px; }
  .tree-node.root { width: 100%; min-width: 0; }
  .tree-root::after, .tree-branches::before, .tree-branch::before { display: none; }
  .tree-branches { grid-template-columns: 1fr; gap: 18px; }
  .tree-branch { padding-top: 0; }
  .tree-canvas, .tree-branches, .tree-branch, .branch-head, .branch-skills, .skill-node { width: 100%; max-width: 100%; }
  .branch-skills { padding-left: 12px; }
  .skill-node { padding: 10px; }
}
"""

SCRIPT = """
<script>
(function () {
  var defaultView = "skill-tree";
  var viewHashes = {
    "skill-tree": "#skill-tree-view",
    "trigger-log": "#trigger-log-view",
    "governance": "#governance-view"
  };
  var body = document.body;
  var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-view-target]"));
  var pages = Array.prototype.slice.call(document.querySelectorAll("[data-view-page]"));

  function viewFromHash() {
    if (window.location.hash === "#trigger-log-view") {
      return "trigger-log";
    }
    if (window.location.hash === "#governance-view") {
      return "governance";
    }
    return defaultView;
  }

  function hashForView(view) {
    return viewHashes[view] || viewHashes[defaultView];
  }

  function setDashboardView(view, updateHash) {
    var nextView = viewHashes[view] ? view : defaultView;
    body.setAttribute("data-active-view", nextView);

    buttons.forEach(function (button) {
      var active = button.getAttribute("data-view-target") === nextView;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });

    pages.forEach(function (page) {
      var active = page.getAttribute("data-view-page") === nextView;
      page.hidden = !active;
    });

    if (updateHash && window.history && window.history.pushState) {
      window.history.pushState({ dashboardView: nextView }, "", hashForView(nextView));
      window.scrollTo(0, 0);
    }
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      setDashboardView(button.getAttribute("data-view-target"), true);
    });
  });

  window.addEventListener("popstate", function () {
    setDashboardView(viewFromHash(), false);
  });

  window.addEventListener("hashchange", function () {
    setDashboardView(viewFromHash(), false);
  });

  window.setDashboardView = setDashboardView;
  setDashboardView(viewFromHash(), false);
})();
</script>
"""


def text(value: Any) -> str:
    if value is None:
        return ""
    return escape(str(value))


STATUS_LABELS = {
    "used": "已使用",
    "entered": "已进入",
    "skipped": "已跳过",
    "active": "活跃",
    "staging": "候选",
    "archived": "归档",
    "rejected": "拒绝",
}


def status_label(status: Any) -> str:
    raw = str(status or "skipped")
    return STATUS_LABELS.get(raw, raw)


def badge(status: Any) -> str:
    raw = str(status or "skipped")
    css = raw if raw in {"used", "entered", "skipped", "active", "staging", "archived", "rejected"} else "skipped"
    return f'<span class="badge {css}">{text(status_label(raw))}</span>'
