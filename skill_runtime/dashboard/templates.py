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
  --used: #1f7a4d;
  --entered: #9a6a16;
  --skipped: #6a7280;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: radial-gradient(circle at top left, #ffe7c2 0, transparent 34%), var(--bg);
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
}
main { width: min(1180px, calc(100% - 40px)); margin: 36px auto; }
.hero { display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 24px; }
.eyebrow { color: var(--muted); text-transform: uppercase; letter-spacing: .14em; font-size: 12px; }
h1 { font-size: 44px; margin: 8px 0; line-height: 1; }
h2 { margin: 0 0 14px; }
.panel { background: rgba(255,250,240,.92); border: 1px solid var(--line); border-radius: 22px; padding: 20px; box-shadow: 0 20px 60px rgba(79,54,27,.08); }
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.two { display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; margin-top: 16px; }
.metric { border-left: 4px solid #b8792f; padding-left: 12px; }
.metric strong { display: block; font-size: 30px; }
.metric span, .muted { color: var(--muted); }
.skill { border: 1px solid var(--line); border-radius: 16px; padding: 12px; margin: 10px 0; background: #fffdf7; }
.skill-name { font-weight: 700; }
.badge { display: inline-block; border-radius: 999px; padding: 3px 9px; font-size: 12px; color: white; background: var(--skipped); }
.badge.used { background: var(--used); }
.badge.entered { background: var(--entered); }
.badge.skipped { background: var(--skipped); }
.event { border-bottom: 1px solid var(--line); padding: 12px 0; }
.event:last-child { border-bottom: 0; }
.reason { color: var(--muted); margin-top: 4px; }
pre { white-space: pre-wrap; word-break: break-word; background: #2b2118; color: #fff6e8; padding: 12px; border-radius: 14px; }
@media (max-width: 860px) {
  .grid, .two { grid-template-columns: 1fr; }
  .hero { display: block; }
  h1 { font-size: 34px; }
}
"""


def text(value: Any) -> str:
    if value is None:
        return ""
    return escape(str(value))


def badge(status: Any) -> str:
    raw = str(status or "skipped")
    css = raw if raw in {"used", "entered", "skipped"} else "skipped"
    return f'<span class="badge {css}">{text(raw)}</span>'
