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
body.has-skill-group-open { overflow: hidden; }
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
body[data-active-view="collections"] [data-view-page="collections"],
body[data-active-view="trigger-log"] [data-view-page="trigger-log"],
body[data-active-view="governance"] [data-view-page="governance"],
body[data-active-view="platforms"] [data-view-page="platforms"],
body[data-active-view="global-projects"] [data-view-page="global-projects"],
body[data-active-view="global-log"] [data-view-page="global-log"] { display: block; }
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
.tree-fan { position: relative; padding: 8px 4px 2px; }
.tree-fan .tree-root { margin-bottom: 12px; }
.tree-fan .tree-root::after { display: none; }
.tree-trunk { width: 2px; height: 30px; margin: 0 auto; background: linear-gradient(to bottom, var(--line-strong), rgba(189,145,90,.15)); }
.branch-map { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px 28px; align-items: start; position: relative; }
.branch-map::before { content: ""; position: absolute; top: -15px; left: 20%; right: 20%; border-top: 2px solid var(--line-strong); }
.radial-tree { min-height: 860px; padding: 36px 12px; background: radial-gradient(circle at 50% 53%, rgba(255,250,238,.92) 0, rgba(255,250,238,.62) 15%, rgba(255,250,238,0) 32%); border-radius: 28px; }
.radial-tree .radial-center { position: absolute; left: 50%; top: 430px; z-index: 4; margin: 0; transform: translate(-50%, -50%); }
.radial-tree .tree-node.root { min-width: 210px; border-radius: 999px; background: #fffaf0; box-shadow: 0 18px 42px rgba(79,54,27,.13); }
.radial-quadrants { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); grid-template-rows: 360px minmax(320px, auto); gap: 120px 96px; position: relative; z-index: 2; }
.radial-quadrants::before { display: none; }
.branch-cluster { --branch-color: var(--skipped); position: relative; min-width: 0; padding: 10px 0 4px; border: 0; border-radius: 0; background: transparent; box-shadow: none; }
.branch-cluster::before { display: none; }
.branch-cluster.active { --branch-color: var(--active); transform: translateY(-4px); }
.branch-cluster.staging { --branch-color: var(--staging); transform: translateY(-6px); }
.branch-cluster.archived { --branch-color: var(--archived); }
.branch-cluster.rejected { --branch-color: var(--rejected); transform: translateY(28px); }
.quadrant-nw { grid-column: 1; grid-row: 1; justify-self: end; align-self: start; max-width: 475px; padding-right: 34px; }
.quadrant-ne { grid-column: 2; grid-row: 1; justify-self: start; align-self: start; max-width: 475px; padding-left: 34px; }
.quadrant-sw { grid-column: 1; grid-row: 2; justify-self: end; align-self: start; max-width: 475px; padding-right: 34px; }
.quadrant-se { grid-column: 2; grid-row: 2; justify-self: start; align-self: start; max-width: 475px; padding-left: 34px; }
.quadrant-nw .branch-head, .quadrant-sw .branch-head { justify-content: flex-end; text-align: right; margin-left: auto; }
.quadrant-nw .branch-canopy, .quadrant-sw .branch-canopy { justify-content: flex-end; padding-left: 0; padding-right: 12px; }
.branch-cluster .branch-head { display: inline-flex; align-items: center; gap: 10px; border: 0; border-radius: 999px; padding: 7px 12px; background: rgba(255,253,247,.78); margin-bottom: 14px; box-shadow: 0 8px 22px rgba(79,54,27,.06); }
.branch-cluster .branch-head::before { content: ""; width: 10px; height: 10px; border-radius: 999px; background: var(--branch-color); flex: 0 0 auto; opacity: .85; }
.branch-cluster .branch-head strong { display: inline; font-size: 28px; line-height: 1; margin: 0; }
.branch-cluster .branch-head span { color: var(--muted); font-size: 14px; }
.branch-canopy { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-start; position: relative; padding-left: 12px; }
.skill-group { appearance: none; border: 1px solid var(--line); border-radius: 24px; background: #fffdf7; color: var(--ink); cursor: pointer; font: inherit; box-shadow: 0 14px 30px rgba(79,54,27,.07); max-width: 315px; min-width: 210px; padding: 13px 15px; text-align: left; transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
.skill-group.active { border-color: rgba(31,122,77,.34); }
.skill-group.staging { border-color: rgba(154,106,22,.34); }
.skill-group.archived { border-color: rgba(102,112,128,.34); }
.skill-group.rejected { border-color: rgba(163,59,51,.34); }
.skill-group:hover { transform: translateY(-1px); box-shadow: 0 18px 34px rgba(79,54,27,.1); }
.skill-group:focus-visible { outline: 3px solid rgba(191,133,57,.28); outline-offset: 3px; }
.skill-group.is-selected, .skill-group[aria-expanded="true"] { border-color: rgba(191,133,57,.65); box-shadow: 0 22px 42px rgba(79,54,27,.12); }
.group-title { display: inline-block; font-weight: 800; font-size: 17px; margin-right: 8px; }
.group-count { color: var(--muted); font-size: 13px; }
.group-caption, .group-meta { display: block; color: var(--muted); font-size: 12px; line-height: 1.45; margin-top: 4px; }
.group-action { display: inline-block; color: #9a6a16; font-size: 12px; font-weight: 700; margin-top: 10px; }
.group-detail-modal { display: grid; inset: 0; padding: 38px; place-items: center; position: fixed; z-index: 60; }
.group-detail-modal[hidden], .group-detail-panel[hidden] { display: none; }
.group-detail-backdrop { appearance: none; background: rgba(43,33,24,.28); backdrop-filter: blur(4px); border: 0; cursor: default; inset: 0; position: absolute; }
.group-detail-surface { background: rgba(255,253,247,.98); border: 1px solid rgba(217,203,183,.96); border-radius: 32px; box-shadow: 0 34px 92px rgba(79,54,27,.28); max-height: min(760px, calc(100vh - 76px)); overflow: auto; padding: 22px; position: relative; width: min(900px, calc(100vw - 76px)); }
.group-detail-panel { display: flex; flex-direction: column; min-height: 0; }
.group-detail-head { display: grid; gap: 14px 22px; grid-template-columns: minmax(0, 1fr) auto; margin-bottom: 16px; }
.group-detail-kicker { color: #9a6a16; font-size: 12px; font-weight: 800; letter-spacing: .08em; margin-bottom: 5px; }
.group-detail-head h3 { margin: 0 0 5px; }
.group-detail-head p { color: var(--muted); margin: 0; }
.group-detail-stats { border-top: 1px dashed var(--line); color: var(--muted); display: flex; gap: 12px; grid-column: 1 / -1; grid-row: 2; padding-top: 12px; }
.group-detail-stats strong { color: var(--ink); font-size: 34px; line-height: 1; }
.group-detail-close { align-self: start; appearance: none; border: 1px solid var(--line); border-radius: 999px; background: #fffaf0; color: #9a6a16; cursor: pointer; font: inherit; font-size: 12px; font-weight: 800; padding: 8px 12px; }
.group-detail-close:hover { border-color: rgba(191,133,57,.55); }
.group-skill-list { display: grid; gap: 8px; border-top: 1px dashed var(--line); padding: 10px 12px 12px; }
.group-detail-panel .group-skill-list { border-top: 0; grid-template-columns: repeat(2, minmax(0, 1fr)); overflow: visible; padding: 0; }
.group-skill { border: 1px solid rgba(217,203,183,.72); border-radius: 15px; background: rgba(255,250,240,.72); padding: 10px; }
.group-skill .skill-name { display: inline; margin: 0; font-weight: 700; line-height: 1.25; }
.group-skill-meta { color: var(--muted); font-size: 12px; margin-top: 4px; }
.group-skill .skill-summary { margin: 7px 0 0; color: var(--ink); font-size: 13px; line-height: 1.5; }
.group-more, .empty-group, .more-group { border: 1px dashed var(--line); border-radius: 999px; padding: 10px 13px; color: var(--muted); background: rgba(255,253,247,.58); }
.more-group, .group-more { font-style: italic; }
.skill-leaf { border: 1px solid var(--line); border-radius: 999px; background: #fffdf7; box-shadow: 0 10px 24px rgba(79,54,27,.06); max-width: 270px; transition: border-radius .18s ease, transform .18s ease, box-shadow .18s ease; }
.skill-leaf.active { border-color: rgba(31,122,77,.34); }
.skill-leaf.staging { border-color: rgba(154,106,22,.34); }
.skill-leaf.archived { border-color: rgba(102,112,128,.34); }
.skill-leaf.rejected { border-color: rgba(163,59,51,.34); }
.skill-leaf:hover { transform: translateY(-1px); box-shadow: 0 14px 28px rgba(79,54,27,.09); }
.skill-leaf[open] { flex: 1 1 270px; max-width: 360px; border-radius: 18px; }
.skill-leaf summary { cursor: pointer; list-style: none; padding: 10px 13px; }
.skill-leaf summary::-webkit-details-marker { display: none; }
.leaf-top { display: inline-flex; align-items: center; gap: 7px; }
.skill-leaf .skill-name { display: inline; margin: 0; font-weight: 700; line-height: 1.25; }
.leaf-meta { display: block; margin-top: 3px; color: var(--muted); font-size: 12px; line-height: 1.35; }
.skill-leaf .skill-summary { margin: 0 13px 8px; color: var(--ink); font-size: 13px; line-height: 1.55; }
.leaf-detail { border-top: 1px dashed var(--line); color: var(--muted); font-size: 12px; margin: 8px 13px 12px; padding-top: 8px; }
.group-skill .leaf-detail { margin-left: 0; margin-right: 0; margin-bottom: 0; }
.import-detail { display: grid; gap: 5px; }
.import-chip { border: 1px solid rgba(154,106,22,.32); border-radius: 999px; color: #8a5b13; display: inline-block; font-size: 11px; font-weight: 800; margin-right: 5px; padding: 2px 7px; }
.empty-leaf, .more-leaf { border: 1px dashed var(--line); border-radius: 999px; padding: 10px 13px; color: var(--muted); background: rgba(255,253,247,.58); }
.more-leaf { font-style: italic; }
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
.project-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.collection-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }
.collection-card { border: 1px solid var(--line); border-radius: 20px; background: rgba(255,253,247,.76); padding: 14px; box-shadow: 0 12px 28px rgba(79,54,27,.06); }
.collection-head { align-items: start; display: flex; gap: 12px; justify-content: space-between; }
.collection-head p { margin: 4px 0 0; }
.collection-head strong { color: #8a5b13; font-size: 30px; line-height: 1; }
.collection-skill-list { display: grid; gap: 8px; margin-top: 12px; }
.collection-skill { align-items: center; border-top: 1px dashed var(--line); display: flex; gap: 7px; padding-top: 8px; }
.collection-missing { border-top: 1px dashed var(--line); color: var(--muted); font-size: 12px; margin-top: 10px; padding-top: 8px; }
.project-card { border: 1px solid var(--line); border-radius: 20px; background: rgba(255,253,247,.76); padding: 14px; box-shadow: 0 12px 28px rgba(79,54,27,.06); }
.project-name { font-size: 20px; font-weight: 800; margin-bottom: 5px; }
.project-path { color: var(--muted); font-size: 12px; margin-bottom: 12px; }
.project-stats { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.project-stats span, .event-project { border: 1px solid rgba(217,203,183,.9); border-radius: 999px; background: rgba(255,250,240,.8); color: var(--muted); display: inline-block; font-size: 12px; padding: 4px 8px; }
.event-project { color: #8a5b13; font-weight: 800; margin-right: 6px; }
.scan-list { color: var(--muted); margin: 8px 0 14px; padding-left: 20px; }
pre { white-space: pre-wrap; word-break: break-word; background: #2b2118; color: #fff6e8; padding: 12px; border-radius: 14px; }
@media (max-width: 860px) {
  main { width: min(calc(100% - 24px), 1180px); margin: 20px auto; }
  .grid, .two, .project-grid, .collection-grid { grid-template-columns: 1fr; }
  .hero { display: block; }
  h1 { font-size: 31px; }
  .panel { padding: 18px; }
  .hero .panel { margin-top: 14px; }
  .tree-root { justify-content: flex-start; margin-bottom: 18px; }
  .tree-node.root { width: 100%; min-width: 0; }
  .tree-root::after, .tree-branches::before, .tree-branch::before { display: none; }
  .tree-branches { grid-template-columns: 1fr; gap: 18px; }
  .tree-trunk, .branch-map::before, .branch-cluster::before { display: none; }
  .radial-tree { min-height: 0; padding: 4px 0; }
  .radial-tree .radial-center { position: static; transform: none; margin-bottom: 18px; }
  .branch-map, .radial-quadrants { grid-template-columns: 1fr; grid-template-rows: none; gap: 18px; }
  .branch-cluster, .branch-cluster.active, .branch-cluster.staging, .branch-cluster.archived, .branch-cluster.rejected, .quadrant-nw, .quadrant-ne, .quadrant-sw, .quadrant-se { grid-column: auto; grid-row: auto; justify-self: stretch; align-self: auto; max-width: none; transform: none; padding: 10px 0 4px; }
  .quadrant-nw .branch-head, .quadrant-sw .branch-head { justify-content: flex-start; text-align: left; margin-left: 0; }
  .quadrant-nw .branch-canopy, .quadrant-sw .branch-canopy { justify-content: flex-start; padding-left: 12px; padding-right: 0; }
  .tree-branch { padding-top: 0; }
  .tree-canvas, .tree-branches, .branch-map, .tree-branch, .branch-head, .branch-skills, .branch-canopy, .skill-node, .skill-leaf, .skill-group { width: 100%; max-width: 100%; }
  .branch-skills { padding-left: 12px; }
  .branch-canopy { display: grid; grid-template-columns: 1fr; }
  .group-detail-modal { padding: 14px; }
  .group-detail-surface { max-height: calc(100vh - 28px); padding: 14px; width: calc(100vw - 28px); }
  .group-detail-head { grid-template-columns: minmax(0, 1fr) auto; }
  .group-detail-stats { margin-top: 0; }
  .group-detail-panel .group-skill-list { grid-template-columns: 1fr; }
  .skill-node { padding: 10px; }
  .skill-leaf { border-radius: 18px; }
}
"""

SCRIPT = """
<script>
(function () {
  var defaultView = "skill-tree";
  var viewHashes = {
    "skill-tree": "#skill-tree-view",
    "collections": "#collections-view",
    "trigger-log": "#trigger-log-view",
    "governance": "#governance-view",
    "platforms": "#platforms-view",
    "global-projects": "#global-projects-view",
    "global-log": "#global-log-view"
  };
  var body = document.body;
  var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-view-target]"));
  var pages = Array.prototype.slice.call(document.querySelectorAll("[data-view-page]"));
  var groupButtons = Array.prototype.slice.call(document.querySelectorAll("[data-skill-group-target]"));
  var groupPanels = Array.prototype.slice.call(document.querySelectorAll("[data-skill-group-panel]"));
  var groupCloseButtons = Array.prototype.slice.call(document.querySelectorAll("[data-skill-group-close]"));
  var groupModal = document.querySelector("[data-skill-group-modal]");

  function viewFromHash() {
    if (window.location.hash === "#trigger-log-view") {
      return "trigger-log";
    }
    if (window.location.hash === "#collections-view") {
      return "collections";
    }
    if (window.location.hash === "#governance-view") {
      return "governance";
    }
    if (window.location.hash === "#platforms-view") {
      return "platforms";
    }
    if (window.location.hash === "#global-projects-view") {
      return "global-projects";
    }
    if (window.location.hash === "#global-log-view") {
      return "global-log";
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

    if (nextView !== "skill-tree") {
      setActiveSkillGroup(null);
    }

    if (updateHash && window.history && window.history.pushState) {
      window.history.pushState({ dashboardView: nextView }, "", hashForView(nextView));
      window.scrollTo(0, 0);
    }
  }

  function setActiveSkillGroup(target) {
    var found = false;

    groupButtons.forEach(function (button) {
      var active = target && button.getAttribute("data-skill-group-target") === target;
      button.classList.toggle("is-selected", active);
      button.setAttribute("aria-expanded", active ? "true" : "false");
    });

    groupPanels.forEach(function (panel) {
      var active = target && panel.getAttribute("data-skill-group-panel") === target;
      panel.hidden = !active;
      if (active) {
        found = true;
      }
    });

    if (groupModal) {
      groupModal.hidden = !found;
    }
    body.classList.toggle("has-skill-group-open", found);
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      setDashboardView(button.getAttribute("data-view-target"), true);
    });
  });

  groupButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var target = button.getAttribute("data-skill-group-target");
      var isOpen = button.getAttribute("aria-expanded") === "true";
      setActiveSkillGroup(isOpen ? null : target);
    });
  });

  groupCloseButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      setActiveSkillGroup(null);
    });
  });

  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setActiveSkillGroup(null);
    }
  });

  window.addEventListener("popstate", function () {
    setDashboardView(viewFromHash(), false);
  });

  window.addEventListener("hashchange", function () {
    setDashboardView(viewFromHash(), false);
  });

  window.setDashboardView = setDashboardView;
  window.setActiveSkillGroup = setActiveSkillGroup;
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
