from __future__ import annotations

from html import escape
from typing import Any

STYLE = """
:root {
  --background: #eff1f5;
  --foreground: #4c4f69;
  --card: #e6e9ef;
  --card-soft: #edf0f7;
  --muted: #bcc0cc;
  --muted-foreground: #6c6f85;
  --border: #bcc0cc;
  --border-strong: #a8adbe;
  --primary: #7e3ee6;
  --primary-soft: #e4dcff;
  --primary-foreground: #ffffff;
  --ring: #7287fd;
  --green: #40a02b;
  --yellow: #df8e1d;
  --red: #d20f39;
  --shadow: 0 8px 20px rgba(76, 79, 105, .10);
}
* { box-sizing: border-box; min-width: 0; }
[hidden] { display: none !important; }
html, body { height: 100%; }
html { scroll-behavior: auto; }
body {
  margin: 0;
  background: var(--background);
  color: var(--foreground);
  font-family: "JetBrains Mono", "JetBrains Mono Variable", "Geist Mono", "SFMono-Regular", Consolas, "Microsoft YaHei", monospace;
  font-size: 14px;
  overflow: hidden;
}
button, input { font: inherit; }
svg { display: block; }
.icon { align-items: center; display: inline-flex; flex: 0 0 auto; height: 20px; justify-content: center; width: 20px; }
.icon svg { fill: none; height: 20px; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2; width: 20px; }
.desktop-shell {
  background: var(--background);
  border: 0;
  border-radius: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  height: 100vh;
  margin: 0;
  max-width: none;
  overflow: hidden;
  width: 100vw;
}
.topbar {
  align-items: center;
  background: #f8f8f2;
  border-bottom: 1px solid var(--border);
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) 44px;
  height: 56px;
  padding: 0 16px;
  position: relative;
}
.topbar-icon {
  align-items: center;
  background: transparent;
  border: 0;
  border-radius: 8px;
  color: var(--ring);
  cursor: pointer;
  display: inline-flex;
  height: 34px;
  justify-content: center;
  padding: 0;
  width: 34px;
  z-index: 1;
}
.topbar-icon:hover { background: rgba(188, 192, 204, .45); }
.global-search {
  align-items: center;
  background: rgba(204, 208, 218, .68);
  border: 1px solid rgba(172, 176, 190, .72);
  border-radius: 10px;
  color: var(--muted-foreground);
  display: flex;
  gap: 10px;
  height: 36px;
  justify-self: center;
  padding: 0 12px;
  width: min(420px, 42vw);
  grid-column: 2;
}
.global-search span { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
kbd {
  border: 1px solid rgba(172, 176, 190, .72);
  border-radius: 6px;
  color: rgba(108, 111, 133, .65);
  font-size: 11px;
  padding: 2px 6px;
}
.app-body { display: flex; flex: 1; min-height: 0; }
.sidebar {
  background: #e6e9ef;
  border-right: 1px solid var(--border);
  color: var(--foreground);
  display: flex;
  flex: 0 0 250px;
  flex-direction: column;
  min-height: 0;
}
.sidebar-head {
  align-items: center;
  border-bottom: 1px solid var(--border);
  color: var(--ring);
  display: flex;
  font-size: 17px;
  justify-content: space-between;
  padding: 18px 14px;
}
.view-nav { align-content: start; display: grid; flex: 1; gap: 6px; overflow: auto; padding: 12px 8px; }
.view-link {
  align-items: center;
  background: transparent;
  border: 0;
  border-radius: 8px;
  color: var(--foreground);
  cursor: pointer;
  display: grid;
  gap: 10px;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  min-height: 38px;
  padding: 7px 10px;
  position: relative;
  text-align: left;
}
.view-link:hover { background: rgba(126, 62, 230, .12); color: var(--primary); }
.view-link.is-active { background: var(--primary); color: var(--primary-foreground); }
.view-link.is-active::before {
  background: #fff;
  border-radius: 0 3px 3px 0;
  bottom: 7px;
  content: "";
  left: 0;
  position: absolute;
  top: 7px;
  width: 3px;
}
.view-link span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nav-count {
  background: rgba(108, 111, 133, .16);
  border-radius: 999px;
  color: var(--muted-foreground);
  font-size: 12px;
  padding: 2px 8px;
}
.view-link.is-active .nav-count { background: rgba(255, 255, 255, .18); color: #fff; }
.sidebar-settings {
  align-items: center;
  background: transparent;
  border: 0;
  border-top: 1px solid var(--border);
  color: var(--foreground);
  cursor: pointer;
  display: flex;
  gap: 10px;
  min-height: 44px;
  padding: 10px 18px;
  text-align: left;
}
.sidebar-settings:hover { background: rgba(126, 62, 230, .12); color: var(--primary); }
.content-pane { flex: 1; min-height: 0; overflow: auto; }
.content-header {
  align-items: center;
  background: rgba(239, 241, 245, .96);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  min-height: 104px;
  padding: 24px 30px;
}
h1, h2, h3, p { margin: 0; }
h1 { color: var(--foreground); font-size: 30px; font-weight: 900; letter-spacing: 0; line-height: 1.12; }
h2 { color: var(--foreground); font-size: 22px; font-weight: 900; letter-spacing: 0; }
h3 { color: var(--foreground); font-size: 18px; font-weight: 900; letter-spacing: 0; line-height: 1.25; }
.content-header p, .muted, .section-note, .readonly-copy { color: var(--muted-foreground); }
.content-header p { font-size: 16px; margin-top: 8px; overflow-wrap: anywhere; }
.header-actions { align-items: flex-end; display: flex; flex-direction: column; gap: 8px; max-width: 440px; text-align: right; }
.readonly-pill, .count-pill {
  background: var(--primary-soft);
  border: 1px solid rgba(114, 135, 253, .34);
  border-radius: 999px;
  color: var(--ring);
  display: inline-flex;
  font-weight: 800;
  padding: 6px 13px;
}
.readonly-copy { font-size: 12px; line-height: 1.5; }
.search-row { border-bottom: 1px solid var(--border); padding: 16px 30px; }
.local-search {
  align-items: center;
  background: rgba(204, 208, 218, .62);
  border: 1px solid rgba(188, 192, 204, .88);
  border-radius: 10px;
  color: var(--muted-foreground);
  display: flex;
  gap: 10px;
  height: 40px;
  padding: 0 13px;
  width: 100%;
}
.panel { border-bottom: 1px solid var(--border); padding: 28px 30px; }
.dashboard-view-page { display: none; }
body[data-active-view="skill-tree"] [data-view-page="skill-tree"],
body[data-active-view="skill-evolution"] [data-view-page="skill-evolution"],
body[data-active-view="overview"] [data-view-page="overview"],
body[data-active-view="trigger-log"] [data-view-page="trigger-log"],
body[data-active-view="governance"] [data-view-page="governance"],
body[data-active-view="platforms"] [data-view-page="platforms"],
body[data-active-view="global-projects"] [data-view-page="global-projects"] { display: block; }
.view-kicker { color: var(--muted-foreground); font-size: 12px; font-weight: 800; margin-bottom: 7px; text-transform: uppercase; }
.overview-section + .overview-section { border-top: 1px solid var(--border); margin-top: 30px; padding-top: 30px; }
.overview-section-head {
  align-items: flex-start;
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 14px;
}
.overview-section-head p { font-size: 13px; text-align: left; }
.grid { display: grid; gap: 12px; }
.metric-grid { grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }
.metric {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  min-height: 92px;
  padding: 15px 16px;
}
.metric strong { color: var(--foreground); display: block; font-size: 27px; font-weight: 900; line-height: 1; margin-bottom: 10px; }
.metric span { color: var(--foreground); display: block; font-size: 13px; font-weight: 800; margin-bottom: 4px; }
.metric small { color: var(--muted-foreground); display: block; font-size: 12px; line-height: 1.35; }
.overview-meta { color: var(--muted-foreground); font-size: 13px; margin-top: 9px; }
.section-title-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title-row p { margin-top: 4px; }
.section-note { font-size: 13px; margin-bottom: 16px; }
.skill-card-grid, .project-grid, .collection-grid, .platform-card-grid, .evolution-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.skill-card, .project-card, .collection-card, .platform-skill-card, .evolution-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
  min-height: 170px;
  padding: 18px;
}
.skill-card { cursor: pointer; display: flex; flex-direction: column; gap: 15px; text-align: left; }
.skill-card:hover, .skill-card:focus-visible { border-color: rgba(114, 135, 253, .72); box-shadow: 0 10px 24px rgba(76, 79, 105, .16); outline: none; }
.skill-card-head, .platform-card-head { align-items: flex-start; display: flex; gap: 14px; justify-content: space-between; }
.skill-card-head p, .platform-summary {
  color: var(--muted-foreground);
  display: -webkit-box;
  font-size: 14px;
  line-height: 1.55;
  margin-top: 10px;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.platform-skill-card { display: flex; flex-direction: column; gap: 13px; min-height: 150px; }
.evolution-card { cursor: pointer; display: flex; flex-direction: column; gap: 14px; min-height: 210px; text-align: left; }
.evolution-card:hover, .evolution-card:focus-visible { border-color: rgba(114, 135, 253, .72); box-shadow: 0 10px 24px rgba(76, 79, 105, .16); outline: none; }
.evolution-detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.evolution-detail-grid dd { overflow-wrap: anywhere; }
.platform-card-head h3 { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.platform-path-chip {
  color: var(--muted-foreground);
  font-size: 12px;
  line-height: 1.4;
  margin-top: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-action { color: var(--muted-foreground); opacity: .9; }
.skill-card-meta, .project-stats {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-card-meta span:not(.badge), .project-stats span, .event-project, .collection-skill {
  background: rgba(204, 208, 218, .46);
  border-radius: 999px;
  color: var(--muted-foreground);
  font-size: 12px;
  padding: 5px 9px;
}
.platform-row {
  align-items: center;
  color: var(--ring);
  display: flex;
  flex-wrap: wrap;
  font-size: 13px;
  font-weight: 800;
  gap: 12px;
  margin-top: auto;
}
.platform-row span { align-items: center; display: inline-flex; gap: 6px; }
.badge {
  background: var(--muted-foreground);
  border-radius: 999px;
  color: #fff;
  display: inline-flex;
  font-size: 12px;
  font-weight: 800;
  padding: 5px 9px;
}
.badge.used, .badge.active { background: var(--green); }
.badge.applied { background: var(--green); }
.badge.rolled_back { background: var(--muted-foreground); }
.badge.entered, .badge.staging { background: var(--yellow); }
.badge.proposed { background: var(--yellow); }
.badge.reviewed, .badge.needs_more_evidence { background: var(--yellow); }
.badge.skipped, .badge.archived { background: var(--muted-foreground); }
.badge.rejected { background: var(--red); }
.event-filter {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.event-filter-button {
  background: rgba(204, 208, 218, .46);
  border: 1px solid rgba(188, 192, 204, .76);
  border-radius: 10px;
  color: var(--foreground);
  cursor: pointer;
  font-weight: 800;
  min-height: 34px;
  padding: 6px 11px;
}
.event-filter-button span {
  color: var(--muted-foreground);
  font-size: 12px;
  margin-left: 6px;
}
.event-filter-button:hover { border-color: rgba(114, 135, 253, .7); color: var(--ring); }
.event-filter-button.is-active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--primary-foreground);
}
.event-filter-button.is-active span { color: rgba(255, 255, 255, .78); }
.collection-section { margin-top: 22px; }
.collection-section + .collection-section {
  border-top: 1px solid var(--border);
  margin-top: 28px;
  padding-top: 24px;
}
.collection-section-head { margin-bottom: 14px; }
.collection-section-head p { font-size: 13px; margin-top: 5px; }
.collection-card { min-height: 0; }
.collection-head { align-items: flex-start; display: flex; gap: 14px; justify-content: space-between; }
.collection-head p { color: var(--muted-foreground); font-size: 13px; line-height: 1.5; margin-top: 6px; }
.collection-head strong { color: var(--ring); font-size: 28px; line-height: 1; }
.collection-skill-list { display: grid; gap: 8px; margin-top: 14px; }
.collection-skill { align-items: center; border-radius: 10px; display: flex; gap: 7px; justify-content: flex-start; }
.collection-skill-action { cursor: pointer; }
.collection-skill-action:hover, .collection-skill-action:focus-visible { color: var(--ring); outline: 1px solid rgba(114, 135, 253, .45); }
.collection-missing { color: var(--muted-foreground); font-size: 12px; margin-top: 10px; }
.event {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow);
  margin-bottom: 12px;
  padding: 14px;
}
.event-empty {
  background: rgba(204, 208, 218, .32);
  border: 1px dashed var(--border);
  border-radius: 12px;
  display: none;
  padding: 14px;
}
[data-active-event-filter="used"] .event[data-event-status]:not([data-event-status="used"]),
[data-active-event-filter="entered"] .event[data-event-status]:not([data-event-status="entered"]),
[data-active-event-filter="skipped"] .event[data-event-status]:not([data-event-status="skipped"]) {
  display: none;
}
[data-active-event-filter="used"] [data-event-empty="used"],
[data-active-event-filter="entered"] [data-event-empty="entered"],
[data-active-event-filter="skipped"] [data-event-empty="skipped"] {
  display: block;
}
.event strong { font-size: 14px; line-height: 1.45; }
.reason { color: var(--muted-foreground); line-height: 1.45; margin-top: 8px; }
.event-followup {
  border-left: 3px solid var(--ring);
  color: var(--muted-foreground);
  margin-top: 10px;
  padding-left: 10px;
}
.event-followup strong { color: var(--ring); display: block; margin-bottom: 2px; }
.event-actions { font-size: 13px; }
.project-card { min-height: 0; }
.project-name { font-size: 18px; font-weight: 900; margin-bottom: 6px; }
.project-path { color: var(--muted-foreground); font-size: 12px; line-height: 1.4; margin-bottom: 12px; overflow-wrap: anywhere; }
.scan-list { color: var(--muted-foreground); margin: 12px 0 18px; padding-left: 20px; }
pre {
  background: #4c4f69;
  border-radius: 12px;
  color: #eff1f5;
  overflow: auto;
  padding: 14px;
  white-space: pre-wrap;
}
.import-detail {
  border-top: 1px dashed var(--border);
  color: var(--muted-foreground);
  display: grid;
  font-size: 12px;
  gap: 5px;
  margin-top: 2px;
  padding-top: 10px;
}
.import-chip {
  background: rgba(114, 135, 253, .12);
  border: 1px solid rgba(114, 135, 253, .3);
  border-radius: 999px;
  color: var(--ring);
  display: inline-block;
  font-size: 11px;
  font-weight: 800;
  margin-right: 5px;
  padding: 2px 7px;
}
.skill-detail-layer {
  bottom: 0;
  left: 0;
  position: fixed;
  right: 0;
  top: 0;
  z-index: 30;
}
.skill-detail-backdrop {
  background: rgba(76, 79, 105, .22);
  border: 0;
  bottom: 0;
  cursor: default;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}
.skill-detail-drawer {
  background: var(--card-soft);
  border-left: 1px solid var(--border);
  box-shadow: -18px 0 34px rgba(76, 79, 105, .18);
  bottom: 0;
  display: flex;
  flex-direction: column;
  max-width: min(440px, calc(100vw - 28px));
  position: absolute;
  right: 0;
  top: 0;
  width: 420px;
}
.skill-detail-head {
  border-bottom: 1px solid var(--border);
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr) auto;
  padding: 22px;
}
.skill-detail-head p { color: var(--muted-foreground); font-size: 12px; margin-top: 6px; overflow-wrap: anywhere; }
.detail-close {
  align-self: start;
  background: var(--primary-soft);
  border: 1px solid rgba(114, 135, 253, .34);
  border-radius: 999px;
  color: var(--ring);
  cursor: pointer;
  font-weight: 800;
  padding: 6px 12px;
}
.skill-detail-body { display: grid; gap: 16px; overflow: auto; padding: 22px; }
.detail-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 0;
}
.detail-grid div, .detail-section {
  background: rgba(204, 208, 218, .42);
  border: 1px solid rgba(188, 192, 204, .72);
  border-radius: 12px;
  padding: 12px;
}
.detail-grid dt {
  color: var(--muted-foreground);
  font-size: 12px;
  margin-bottom: 6px;
}
.detail-grid dd {
  color: var(--foreground);
  font-weight: 900;
  margin: 0;
  overflow-wrap: anywhere;
}
.detail-section h3 { font-size: 15px; margin-bottom: 8px; }
.detail-section p { color: var(--muted-foreground); line-height: 1.55; overflow-wrap: anywhere; }
.lifecycle-list {
  color: var(--foreground);
  display: grid;
  gap: 6px;
  margin: 0 0 10px;
  padding-left: 20px;
}
.lifecycle-list li { font-weight: 800; }
::-webkit-scrollbar { height: 8px; width: 8px; }
::-webkit-scrollbar-thumb { background: rgba(108, 111, 133, .35); border-radius: 999px; }
::-webkit-scrollbar-track { background: transparent; }
@media (max-width: 980px) {
  body { overflow: auto; }
  .desktop-shell { border-radius: 0; height: 100vh; margin: 0; width: 100vw; }
  .topbar { grid-template-columns: 44px minmax(0, 1fr) 42px; }
  .global-search { grid-column: 2; width: 100%; }
  .app-body { flex-direction: column; overflow: auto; }
  .sidebar { border-bottom: 1px solid var(--border); border-right: 0; flex: none; }
  .sidebar-head { display: none; }
  .view-nav { display: flex; overflow-x: auto; padding: 10px; }
  .view-link { flex: 0 0 auto; grid-template-columns: 20px auto auto; }
  .sidebar-settings { display: none; }
  .content-pane { overflow: visible; }
  .content-header { align-items: flex-start; flex-direction: column; gap: 14px; padding: 20px; }
  .header-actions { align-items: flex-start; text-align: left; }
  .search-row, .panel { padding: 16px 20px; }
  .grid, .metric-grid, .skill-card-grid, .project-grid, .collection-grid, .platform-card-grid, .evolution-grid { grid-template-columns: 1fr; }
  .overview-section-head { align-items: flex-start; flex-direction: column; gap: 5px; }
  .overview-section-head p { text-align: left; }
  .skill-detail-drawer { max-width: none; width: min(100vw, 420px); }
  .detail-grid { grid-template-columns: 1fr; }
}
"""

SCRIPT = """
<script>
(function () {
  var defaultView = "skill-tree";
  var viewHashes = {
    "overview": "#overview-view",
    "skill-tree": "#skill-tree-view",
    "skill-evolution": "#skill-evolution-view",
    "trigger-log": "#trigger-log-view",
    "governance": "#governance-view",
    "platforms": "#platforms-view",
    "global-projects": "#global-projects-view"
  };
  var body = document.body;
  var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-view-target]"));
  var pages = Array.prototype.slice.call(document.querySelectorAll("[data-view-page]"));
  var headers = Array.prototype.slice.call(document.querySelectorAll("[data-view-header]"));
  var skillDetailDrawer = document.querySelector("[data-skill-detail-drawer]");
  var skillDetailButtons = Array.prototype.slice.call(document.querySelectorAll("[data-skill-detail-open]"));
  var skillDetailCloseButtons = Array.prototype.slice.call(document.querySelectorAll("[data-skill-detail-close]"));
  var evolutionDetailDrawer = document.querySelector("[data-evolution-detail-drawer]");
  var evolutionDetailButtons = Array.prototype.slice.call(document.querySelectorAll("[data-evolution-detail-open]"));
  var evolutionDetailCloseButtons = Array.prototype.slice.call(document.querySelectorAll("[data-evolution-detail-close]"));
  var eventFilterButtons = Array.prototype.slice.call(document.querySelectorAll("[data-event-filter]"));

  function viewFromHash() {
    var match = Object.keys(viewHashes).find(function (view) {
      return window.location.hash === viewHashes[view];
    });
    return match || defaultView;
  }

  function setDashboardView(view, updateHash) {
    var nextView = viewHashes[view] ? view : defaultView;
    function resetContentScroll() {
      var content = document.querySelector(".content-pane");
      if (content) {
        content.scrollTop = 0;
      }
    }
    body.setAttribute("data-active-view", nextView);
    buttons.forEach(function (button) {
      var active = button.getAttribute("data-view-target") === nextView;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
    pages.forEach(function (page) {
      page.hidden = page.getAttribute("data-view-page") !== nextView;
    });
    headers.forEach(function (header) {
      header.hidden = header.getAttribute("data-view-header") !== nextView;
    });
    resetContentScroll();
    window.setTimeout(resetContentScroll, 0);
    if (updateHash && window.history && window.history.pushState) {
      window.history.pushState({ dashboardView: nextView }, "", viewHashes[nextView]);
    }
    clearActiveSkillDetail();
    clearActiveEvolutionDetail();
  }

  function setDetailText(field, value) {
    if (!skillDetailDrawer) {
      return;
    }
    var target = skillDetailDrawer.querySelector('[data-detail-field="' + field + '"]');
    if (target) {
      target.textContent = value || "-";
    }
  }

  function setActiveSkillDetail(source) {
    if (!skillDetailDrawer || !source) {
      return;
    }
    clearActiveEvolutionDetail();
    setDetailText("name", source.getAttribute("data-detail-name"));
    setDetailText("rawName", source.getAttribute("data-detail-raw-name"));
    setDetailText("status", source.getAttribute("data-detail-status"));
    setDetailText("usageCount", source.getAttribute("data-detail-usage-count"));
    setDetailText("sourceCount", source.getAttribute("data-detail-source-count"));
    setDetailText("sourceLabel", source.getAttribute("data-detail-source-label"));
    setDetailText("summary", source.getAttribute("data-detail-summary"));
    var provenance = source.getAttribute("data-detail-provenance") || "";
    var provenanceSection = skillDetailDrawer.querySelector("[data-detail-provenance-section]");
    if (provenanceSection) {
      provenanceSection.hidden = !provenance;
    }
    setDetailText("provenance", provenance);
    skillDetailDrawer.hidden = false;
    body.classList.add("has-skill-detail-open");
  }

  function clearActiveSkillDetail() {
    if (!skillDetailDrawer) {
      return;
    }
    skillDetailDrawer.hidden = true;
    body.classList.remove("has-skill-detail-open");
  }

  function setEvolutionText(field, value) {
    if (!evolutionDetailDrawer) {
      return;
    }
    var target = evolutionDetailDrawer.querySelector('[data-evolution-field="' + field + '"]');
    if (target) {
      target.textContent = value || "-";
    }
  }

  function setActiveEvolutionDetail(source) {
    if (!evolutionDetailDrawer || !source) {
      return;
    }
    clearActiveSkillDetail();
    setEvolutionText("target", source.getAttribute("data-evolution-target"));
    setEvolutionText("rawTarget", source.getAttribute("data-evolution-raw-target"));
    setEvolutionText("status", source.getAttribute("data-evolution-status"));
    setEvolutionText("risk", source.getAttribute("data-evolution-risk"));
    setEvolutionText("sourceTask", source.getAttribute("data-evolution-source-task"));
    setEvolutionText("updatedAt", source.getAttribute("data-evolution-updated-at"));
    setEvolutionText("lifecycle", source.getAttribute("data-evolution-lifecycle"));
    setEvolutionText("reason", source.getAttribute("data-evolution-reason"));
    setEvolutionText("evidence", source.getAttribute("data-evolution-evidence"));
    setEvolutionText("changes", source.getAttribute("data-evolution-changes"));
    setEvolutionText("candidatePath", source.getAttribute("data-evolution-candidate-path"));
    setEvolutionText("reviewPath", source.getAttribute("data-evolution-review-path"));
    setEvolutionText("applicationPath", source.getAttribute("data-evolution-application-path"));
    setEvolutionText("rollbackPath", source.getAttribute("data-evolution-rollback-path"));
    evolutionDetailDrawer.hidden = false;
    body.classList.add("has-evolution-detail-open");
  }

  function clearActiveEvolutionDetail() {
    if (!evolutionDetailDrawer) {
      return;
    }
    evolutionDetailDrawer.hidden = true;
    body.classList.remove("has-evolution-detail-open");
  }

  function setEventFilter(button) {
    if (!button) {
      return;
    }
    var status = button.getAttribute("data-event-filter") || "used";
    var section = button.closest("[data-active-event-filter]");
    if (!section) {
      return;
    }
    section.setAttribute("data-active-event-filter", status);
    Array.prototype.slice.call(section.querySelectorAll("[data-event-filter]")).forEach(function (item) {
      var active = item.getAttribute("data-event-filter") === status;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      setDashboardView(button.getAttribute("data-view-target"), true);
    });
  });

  skillDetailButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setActiveSkillDetail(button);
    });
    button.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setActiveSkillDetail(button);
      }
    });
  });

  skillDetailCloseButtons.forEach(function (button) {
    button.addEventListener("click", clearActiveSkillDetail);
  });

  evolutionDetailButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setActiveEvolutionDetail(button);
    });
    button.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setActiveEvolutionDetail(button);
      }
    });
  });

  evolutionDetailCloseButtons.forEach(function (button) {
    button.addEventListener("click", clearActiveEvolutionDetail);
  });

  eventFilterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setEventFilter(button);
    });
  });

  window.addEventListener("popstate", function () {
    setDashboardView(viewFromHash(), false);
  });
  window.addEventListener("hashchange", function () {
    setDashboardView(viewFromHash(), false);
  });
  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      clearActiveSkillDetail();
      clearActiveEvolutionDetail();
    }
  });
  window.setDashboardView = setDashboardView;
  window.setActiveSkillDetail = setActiveSkillDetail;
  window.clearActiveSkillDetail = clearActiveSkillDetail;
  window.setActiveEvolutionDetail = setActiveEvolutionDetail;
  window.clearActiveEvolutionDetail = clearActiveEvolutionDetail;
  window.setEventFilter = setEventFilter;
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
    "entered": "进入观察",
    "skipped": "已跳过",
    "active": "活跃",
    "staging": "候选",
    "archived": "归档",
    "rejected": "拒绝",
    "proposed": "待审核",
    "reviewed": "已审核",
    "needs_more_evidence": "需补证据",
    "applied": "已应用",
    "rolled_back": "已回滚",
}


def status_label(status: Any) -> str:
    raw = str(status or "skipped")
    return STATUS_LABELS.get(raw, raw)


def badge(status: Any) -> str:
    raw = str(status or "skipped")
    css = raw if raw in {"used", "entered", "skipped", "active", "staging", "archived", "rejected", "proposed", "reviewed", "needs_more_evidence", "applied", "rolled_back"} else "skipped"
    return f'<span class="badge {css}">{text(status_label(raw))}</span>'
