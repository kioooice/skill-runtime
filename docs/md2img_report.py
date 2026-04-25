# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os, pypdfium2

# -- colors --
DARK_BG  = HexColor("#1a1a2e")
ACCENT   = HexColor("#4a90d9")
LIGHT_BG = HexColor("#f5f7fa")
TXT_DARK = HexColor("#2c3e50")
TXT_LITE = HexColor("#7f8c8d")
CODE_BG  = HexColor("#f0f4f8")
CODE_BDR = HexColor("#d0d7de")
INFO_BG  = HexColor("#e3f2fd")
INFO_BDR = HexColor("#2196f3")
FBOLD    = "Helvetica-Bold"
FREG     = "Helvetica"
FMON     = "Courier"

PDF_OUT  = r"D:/02-Projects/vibe/docs/skill-runtime-project.pdf"
IMG_OUT  = r"D:/02-Projects/vibe/docs/skill-runtime-images"
os.makedirs(IMG_OUT, exist_ok=True)

doc = SimpleDocTemplate(PDF_OUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
    title="Skill Runtime Project Report",
    author="Skill Runtime Team")

W, H = A4

# -- styles --
cover_title = ParagraphStyle("CT", fontName=FBOLD, fontSize=28,
    textColor=white, alignment=TA_CENTER, leading=36, spaceAfter=16)
cover_sub   = ParagraphStyle("CS", fontName=FREG, fontSize=14,
    textColor=HexColor("#a0b4c8"), alignment=TA_CENTER, leading=20)
cover_main  = ParagraphStyle("CM", fontName=FBOLD, fontSize=32,
    textColor=ACCENT, alignment=TA_CENTER, leading=42, spaceAfter=30)
cover_tag   = ParagraphStyle("CTag", fontName=FREG, fontSize=12,
    textColor=HexColor("#6c8ebf"), alignment=TA_CENTER, leading=18)
h1   = ParagraphStyle("H1", fontName=FBOLD, fontSize=20,
    textColor=DARK_BG, leading=26, spaceBefore=24, spaceAfter=10)
h2   = ParagraphStyle("H2", fontName=FBOLD, fontSize=14,
    textColor=HexColor("#34495e"), leading=20, spaceBefore=16, spaceAfter=6)
h3   = ParagraphStyle("H3", fontName=FBOLD, fontSize=12,
    textColor=HexColor("#4a5568"), leading=16, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("B", fontName=FREG, fontSize=10,
    textColor=TXT_DARK, leading=16, spaceAfter=6)
bullet = ParagraphStyle("BL", fontName=FREG, fontSize=10,
    textColor=TXT_DARK, leading=15, spaceAfter=4, leftIndent=16, bulletIndent=4)
bullet_b = ParagraphStyle("BLB", fontName=FBOLD, fontSize=10,
    textColor=TXT_DARK, leading=15, spaceAfter=4, leftIndent=16, bulletIndent=4)
code_sty = ParagraphStyle("CD", fontName=FMON, fontSize=9,
    textColor=HexColor("#d63384"), leading=13, spaceAfter=4, backColor=CODE_BG, borderPad=6)
tbl_hdr  = ParagraphStyle("TH", fontName=FBOLD, fontSize=9,
    textColor=white, leading=13)
tbl_cell  = ParagraphStyle("TC", fontName=FREG, fontSize=9,
    textColor=TXT_DARK, leading=13)
core_val  = ParagraphStyle("CV", fontName=FBOLD, fontSize=13,
    textColor=DARK_BG, leading=22, alignment=TA_CENTER)
concl_sty = ParagraphStyle("CST", fontName=FBOLD, fontSize=12,
    textColor=white, leading=18, alignment=TA_CENTER)

def make_table(headers, rows, widths):
    data = [[Paragraph(h, tbl_hdr) for h in headers]] + \
           [[Paragraph(str(c), tbl_cell) for c in r] for r in rows]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BG),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#f8f9fa")]),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#dee2e6")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    return t

def section_badge(num, title):
    badge = ParagraphStyle("BD", fontName=FBOLD, fontSize=9,
        textColor=white, leading=12, alignment=TA_CENTER)
    btitle = ParagraphStyle("BT", fontName=FBOLD, fontSize=16,
        textColor=DARK_BG, leading=22, spaceAfter=2)
    return [
        Spacer(1, 6),
        Table([[Paragraph("%02d" % num, badge),
                Paragraph(title, btitle)]],
            colWidths=[1.2*cm, 14*cm],
            style=TableStyle([
                ("BACKGROUND", (0,0), (0,0), ACCENT),
                ("BACKGROUND", (1,0), (1,0), LIGHT_BG),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (0,0), 4),
                ("RIGHTPADDING", (0,0), (0,0), 4),
                ("TOPPADDING", (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ])),
        Spacer(1, 6),
    ]

def code_block(text):
    return Table([[Paragraph(text, code_sty)]],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), CODE_BG),
            ("BOX", (0,0), (-1,-1), 1, CODE_BDR),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
        ]))

# ===== BUILD STORY =====
story = []

# -- COVER --
story.append(Spacer(1, 3*cm))
story.append(Paragraph("Skill Runtime", cover_title))
story.append(Paragraph("Project Report", cover_main))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("A Local Evolvable Skill Runtime & Governance System for Host AI", cover_sub))
story.append(Spacer(1, 0.8*cm))
story.append(Paragraph("Governable | Auditable | Reusable | Explainable", cover_tag))
story.append(Spacer(1, 2*cm))
story.append(Paragraph("v1.0 | 2026", ParagraphStyle("Ver", fontName=FREG, fontSize=10,
    textColor=HexColor("#8899aa"), alignment=TA_CENTER)))
story.append(PageBreak())

# -- SECTION 1 --
story += section_badge(1, "Project Overview")
story.append(Paragraph(
    "This project implements a local <b>skill runtime</b> for <b>Codex</b>. "
    "The goal is not to build another AI assistant, but to add a layer of "
    "<font color='#4a90d9'><b>Skill Runtime &amp; Governance Kernel</b></font> to the host AI.", body))
story.append(Spacer(1, 6))
story.append(Paragraph("The core questions this system addresses:", body))
for item in [
    "Can AI workflows be <b>沉淀下来</b> (deposited/solidified)?",
    "Can deposited skills be <b>inspected, governed, and reused</b>?",
    "Can the host AI reuse existing skills when encountering similar tasks, "
    "rather than starting from scratch?",
]:
    story.append(Paragraph("  - " + item, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("The project's positioning:", body))
for item in [
    "NOT an independent AI product",
    "NOT a new chat interface",
    "NOT another agent",
    "BUT a <b>capability layer inside AI applications</b>",
]:
    prefix = "X  " if item.startswith("NOT") else ">> "
    story.append(Paragraph(prefix + item, bullet_b if "BUT" in item else bullet))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Currently, this implementation can be hooked below Codex via <b>MCP</b> tools "
    "and has a complete closed loop:", body))
story.append(Spacer(1, 6))
story.append(make_table(
    ["search", "execute", "distill", "audit", "promote", "reuse"],
    [["->", "->", "->", "->", "->", ""]],
    [2.4*cm]*6))
story.append(PageBreak())

# -- SECTION 2 --
story += section_badge(2, "Core Problems This Project Aims to Solve")
story.append(Paragraph("2.1 Deficiencies of Traditional AI Workflows", h2))
deficiencies = [
    ("Repeated tasks are planned from scratch every time",
     "Even if a task type has been done before, the next time it still re-analyzes, re-writes processes, and re-invokes tools."),
    ("Can do tasks, but cannot solidify effectively",
     "After task completion, the process is usually only in the chat context, without being converted into structured reusable capabilities."),
    ("Skill reuse lacks governance",
     "Some systems 'accumulate skills', but only save scripts or memory fragments simply, lacking governance capabilities like auditing, onboarding, lifecycle management."),
    ("Host AI and skill system are tightly coupled",
     "Many solutions evolve into 'another AI on top' or 'external agent controls host agent', resulting in complex architecture, messy boundaries, and increased costs."),
]
for i, (title, desc) in enumerate(deficiencies, 1):
    story.append(Paragraph("<b>%d. %s</b>" % (i, title), bullet_b))
    story.append(Paragraph(desc, ParagraphStyle("D", fontName=FREG, fontSize=10,
        textColor=TXT_LITE, leading=14, spaceAfter=8, leftIndent=28)))
story.append(Spacer(1, 10))
story.append(Paragraph("2.2 This Project's Judgment", h2))
story.append(Paragraph(
    "The project's judgment: the most reasonable form for such systems in the future "
    "is not an independent AI, but a capability kernel inside existing AI applications.", body))
story.append(Spacer(1, 6))
story.append(Paragraph("In other words:", body))
story.append(Paragraph("  - <b>Host AI</b>: understands tasks, interacts with users, makes final decisions", bullet_b))
story.append(Paragraph("  - <b>Skill Runtime</b>: skill retrieval, execution, distillation, auditing, onboarding, and reuse", bullet_b))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "This is why the project ultimately chose to expose runtime to Codex via MCP, "
    "rather than making it an independent chat program.", body))
story.append(PageBreak())

# -- SECTION 3 --
story += section_badge(3, "Project Positioning & Design Principles")
story.append(Paragraph(
    "The precise positioning of this project is:<br/><br/>"
    "<font size=14 color='#4a90d9'><b>A Local Evolvable Skill Runtime &amp; Governance System for Host AI</b></font>",
    body))
story.append(Spacer(1, 10))
story.append(Paragraph("Design Principles", h2))
principles = [
    ("P1: Host-First", "The host AI is the upper-layer entry. Skill runtime does not compete for user interaction or masquerade as a second AI."),
    ("P2: Reuse First, Then Generate", "When facing a task, first retrieve existing skills; only consider generating new ones when no match is found."),
    ("P3: Generated Skills Must Be Governable", "New skills cannot be directly onboarded; they must enter staging and be audited before promotion."),
    ("P4: Structure Over Intelligence", "The first phase focuses on a solid closed loop and explainable structure, not rushing into full LLM generation."),
    ("P5: Capability Layer, Not Product Shell", "Externally exposing CLI, MCP tools, and skill wrapping layers, not new UIs."),
    ("P6: Explainability Matters", "When skills are retrieved, generated, and reused, the system tries to explain: why matched, which rule, why recommended."),
]
for p in principles:
    story.append(Paragraph("<b>%s</b>" % p[0], h3))
    story.append(Paragraph(p[1], body))
    story.append(Spacer(1, 4))
story.append(PageBreak())

# -- SECTION 4 --
story += section_badge(4, "System Architecture")
story.append(Paragraph("The system can be summarized into four layers:", body))
story.append(Spacer(1, 8))
layers = [
    ("Layer 1: Host AI", "Currently Codex. Responsible for receiving user tasks, understanding requirements, planning actions, deciding when to invoke runtime."),
    ("Layer 2: Adapter", "Currently CLI and MCP server. MCP is the primary integration method with Codex."),
    ("Layer 3: Skill Runtime", "Project core. Responsible for trajectory storage, skill distillation, skill audit, promotion guard, skill retrieval, skill execution, provenance backfill."),
    ("Layer 4: Storage/Governance", "Local file-based. skill_store (staging/active/archive/rejected), trajectories, audits, index.json."),
]
for title, desc in layers:
    story.append(Paragraph("<b>%s</b>" % title, h3))
    story.append(Paragraph(desc, body))
    story.append(Spacer(1, 6))
story.append(PageBreak())

# -- SECTION 5 --
story += section_badge(5, "Directory & Module Structure")
story.append(Paragraph("Current project structure:", body))
story.append(Spacer(1, 6))
story.append(code_block(
    "scripts/\n"
    "  skill_cli.py        # CLI entry\n"
    "  skill_mcp_server.py # MCP server\n\n"
    "skill_runtime/\n"
    "  api/        # RuntimeService + data models\n"
    "  memory/     # Trajectory access & validation\n"
    "  distill/    # Trajectory -> skill distillation\n"
    "  audit/      # Static + semantic auditing\n"
    "  retrieval/  # Skill indexing & retrieval\n"
    "  execution/  # Tool injection & skill execution\n"
    "  governance/ # Promotion guard, provenance\n\n"
    "skill_store/\n"
    "  staging/  active/  archive/  rejected/\n"
    "  index.json\n\n"
    "trajectories/  audits/  demo/  tests/"))
story.append(Spacer(1, 8))
story.append(Paragraph("Module responsibilities:", body))
modules = [
    ("api/", "RuntimeService business layer shared by CLI and MCP"),
    ("memory/", "Trajectory access, validation, context for distill/audit"),
    ("distill/", "Rule-based distillation + LLM fallback provider"),
    ("audit/", "Two-layer: static rules + semantic skeleton"),
    ("retrieval/", "Keyword scoring + provenance + top-layer recommendations"),
    ("execution/", "Tool injection, dynamic loading, result wrapping, usage stats"),
    ("governance/", "Promotion guard, provenance backfill"),
]
for mod, desc in modules:
    story.append(Paragraph("  - <b>%s</b> %s" % (mod, desc), bullet))
story.append(PageBreak())

# -- SECTION 6 --
story += section_badge(6, "Core Data Models")
story.append(Paragraph("Three key data structures are defined:", body))
models = [
    ("Trajectory", "Represents one task execution trace", [
        "task_id, session_id, task_description, steps, final_status, artifacts, started_at, ended_at",
        "steps contains: step_id, tool_name, tool_input, observation, status, thought_summary",
    ]),
    ("SkillMetadata", "Skill index and governance information", [
        "skill_name, file_path, summary, docstring, input_schema, output_schema",
        "source_trajectory_ids, created_at, last_used_at, usage_count, status, audit_score, tags",
        "rule_name, rule_priority, rule_reason (for provenance)",
    ]),
    ("AuditReport", "Audit result", [
        "status, security_score, suggestions, optimized_docstring, refactored_code",
        "static_score, semantic_score, static_findings, semantic_findings, semantic_summary",
    ]),
]
for name, desc, fields in models:
    story.append(Paragraph("<b>%s</b> -- %s" % (name, desc), h3))
    for f in fields:
        story.append(Paragraph("  - " + f, bullet))
    story.append(Spacer(1, 8))
story.append(PageBreak())

# -- SECTION 7 --
story += section_badge(7, "Main Closed Loop: Task to Skill")
loop_steps = [
    ("1. Search", "Host AI calls search_skill with task description, returns matching skills + top recommendations"),
    ("2. Execute", "Strong match found -> call execute_skill, dynamically load and execute active skill"),
    ("3. Complete Task", "No match -> host AI completes the task normally"),
    ("4. Log Trajectory", "Write the task execution process as a trajectory"),
    ("5. Distill", "Trajectory enters distill: matches rules -> generate executable skill -> enters staging"),
    ("6. Audit", "Staging skill undergoes static + semantic double-layer audit"),
    ("7. Promote", "Only audit-passed skills are allowed to promote to active"),
    ("8. Reuse", "Next time similar task appears, prefer search -> execute instead of planning from scratch"),
]
for title, desc in loop_steps:
    story.append(Paragraph("<b>%s</b>" % title, h3))
    story.append(Paragraph(desc, body))
    story.append(Spacer(1, 4))
story.append(PageBreak())

# -- SECTION 8 --
story += section_badge(8, "Distillation Design")
story.append(Paragraph("8.1 Why Start with Rule Distillation", h2))
story.append(Paragraph(
    "The project did not start by fully relying on LLM to generate skills, but started with rule distillation. "
    "Reason: rule distillation is more controllable, easier to verify, easier to explain, and better for building a closed loop first.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("8.2 Current Supported Rule Patterns", h2))
rules = ["text_merge", "text_replace", "single_file_transform", "batch_rename",
         "directory_copy", "directory_move", "directory_text_replace",
         "csv_to_json", "json_to_csv"]
for r in rules:
    story.append(Paragraph("  - <b>%s</b>" % r, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("8.3 Rule Registry", h2))
story.append(Paragraph(
    "Each rule has: RULE_NAME, PRIORITY, match(), explain_match(). "
    "Benefits: rules are more maintainable; generated results have provenance and explainability.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("8.4 LLM Fallback", h2))
story.append(Paragraph(
    "When rules cannot match: construct prompt -> call provider -> generate candidate code -> write to staging. "
    "Current provider is still mock provider, purpose is to make fallback chain testable first.", body))
story.append(PageBreak())

# -- SECTION 9 --
story += section_badge(9, "Audit Design")
story.append(Paragraph("9.1 Why Audit is Core", h2))
story.append(Paragraph(
    "Simply 'accumulating skills' is not scarce; what is truly critical is: "
    "Can new skills be safely reused? Can they exist at a reasonable granularity? "
    "Have they overfitted to a one-time trajectory? Are they truly suitable for onboarding? "
    "Therefore, audit is not an accessory, but the core of the entire governance closed loop.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("9.2 Static Audit", h2))
story.append(Paragraph("Checks: dangerous commands, shell=True/os.system, hardcoded absolute paths, "
    "hardcoded usernames/paths, missing run(), missing docstring, run() too long, syntax errors.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("9.3 Semantic Audit Skeleton", h2))
story.append(Paragraph("To avoid skills that 'look structurally legal but are not', also checks:", body))
for item in ["Is docstring truly conducive to retrieval?", "Does skill take on too many responsibilities?",
             "Is it consistent with trajectory toolchain?", "Do kwargs cover key inputs?",
             "Are artifact names hardcoded into the skill?", "Is it a template-style or no-op skill?"]:
    story.append(Paragraph("  - " + item, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Current audit capability can already block: static high-risk skills, template skills "
    "clearly mismatched with trajectories, pseudo-skills insufficient for promotion. "
    "But it is still not LLM-driven deep semantic audit.", body))
story.append(PageBreak())

# -- SECTION 10 --
story += section_badge(10, "Retrieval Design")
story.append(Paragraph("10.1 Current Retrieval Method", h2))
story.append(Paragraph(
    "Current retrieval is primarily keyword scoring, considering: skill name, summary, docstring, tags, "
    "input/output schema, active status, audit_score.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("10.2 Explainability Enhancement", h2))
story.append(Paragraph(
    "Retrieval results return not just skills, but also: why_matched, rule_name, rule_priority, rule_reason. "
    "The system explains why a skill was matched and which rule it was generated from.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("10.3 Top-Layer Recommended Actions", h2))
story.append(make_table(
    ["Situation", "Recommended Action"],
    [["Strong match", "execute_skill"],
     ["Weak/No match", "distill_and_promote_candidate"]],
    [4*cm, 11.5*cm]))
story.append(Spacer(1, 8))
story.append(Paragraph("10.4 Not Yet Implemented", h2))
for item in ["Vector retrieval", "BM25", "Hybrid retrieval rerank"]:
    story.append(Paragraph("  - " + item, bullet))
story.append(Paragraph(
    "This is deliberate pace control: at this stage, the risk of wrong promotion is higher than "
    "inaccurate ranking, so semantic audit was prioritized over retrieval ranking.", body))
story.append(PageBreak())

# -- SECTION 11 --
story += section_badge(11, "Execution Design")
story.append(Paragraph("11.1 Unified Skill Entry", h2))
story.append(Paragraph(
    "All skills uniformly expose run(tools, **kwargs), ensuring stable host execution interface, "
    "stable tool injection, and no need to change skill protocol for future extensions.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("11.2 RuntimeTools", h2))
story.append(Paragraph("Current RuntimeTools provides a controlled local tool capability:", body))
for t in ["read_text / write_text", "list_files", "run_shell", "rename_path",
          "copy_file / move_file", "read_json / write_json"]:
    story.append(Paragraph("  - " + t, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("11.3 Usage Statistics", h2))
story.append(Paragraph(
    "After skill successful execution: usage_count and last_used_at are written back. "
    "This prepares for future governance and archiving.", body))
story.append(PageBreak())

# -- SECTION 12 --
story += section_badge(12, "MCP & Codex Integration")
story.append(Paragraph("12.1 Why Choose MCP", h2))
story.append(Paragraph(
    "MCP's value: expose runtime as a callable tool layer for the host, keep runtime independent "
    "from any specific host, let Codex directly use runtime as a local capability layer. "
    "MCP is sufficiently appropriate for tool-layer integration.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("12.2 Currently Exposed MCP Tools", h2))
tools_list = ["search_skill", "execute_skill", "distill_trajectory",
              "distill_and_promote_candidate", "audit_skill", "promote_skill",
              "log_trajectory", "reindex_skills", "backfill_skill_provenance"]
t_rows = [[tools_list[i] if i < len(tools_list) else "" for i in range(j*3, j*3+3)]
           for j in range(3)]
t = Table([[Paragraph(x, tbl_cell) for x in row] for row in t_rows], colWidths=[5*cm]*3)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, HexColor("#dee2e6")),
    ("BACKGROUND", (0,0), (-1,-1), HexColor("#f8f9fa")),
    ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
]))
story.append(t)
story.append(Spacer(1, 8))
story.append(Paragraph("12.3 Codex Global Integration", h2))
story.append(Paragraph(
    "Configured via ~/.codex/config.toml with skill_runtime MCP server. "
    "Host layer enhancements: global AGENTS preferences, global MEMORY, "
    "global skills wrappers (skill-search / skill-execute / skill-distill / "
    "skill-audit / skill-promote / skill-distill-promote).", body))
story.append(PageBreak())

# -- SECTION 13 --
story += section_badge(13, "CLI, MCP, and Orchestration")
story.append(Paragraph("13.1 CLI Commands", h2))
for cmd in ["search", "execute", "distill", "distill-and-promote", "audit",
            "promote", "log-trajectory", "reindex", "archive-cold", "backfill-provenance"]:
    story.append(Paragraph("  - " + cmd, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("13.2 Why Composite Commands Were Added Later", h2))
story.append(Paragraph(
    "Early full chain: log -> distill -> audit -> promote. "
    "But for the host, this chain was too long, so distill-and-promote and "
    "distill_and_promote_candidate were added. This short path significantly reduces host usage cost.", body))
story.append(PageBreak())

# -- SECTION 14 --
story += section_badge(14, "Provenance Design")
story.append(Paragraph("14.1 Why Provenance Matters", h2))
story.append(Paragraph(
    "As skills grow in number, if we only know 'it exists' but not 'why it exists and where it came from', "
    "governance will quickly become uncontrollable.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("14.2 What is Recorded", h2))
for item in ["rule_name -- which rule generated this", "rule_priority -- rule priority",
             "rule_reason -- why matched"]:
    story.append(Paragraph("  - " + item, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("14.3 Historical Backfill", h2))
story.append(Paragraph(
    "For legacy skills existing before the provenance field was added, backfill-provenance "
    "scans existing active skills and tries to fill in provenance. "
    "This prevents the skill library from being split due to incomplete historical data.", body))
story.append(PageBreak())

# -- SECTION 15 --
story += section_badge(15, "Demo & Verification")
story.append(Paragraph("15.1 Demo Scenario", h2))
story.append(Paragraph(
    "The earliest demo was a typical local file workflow: <b>merge txt files into markdown</b>. "
    "Chosen because: simple and easy to understand, locally reproducible, "
    "clearly demonstrates the closed loop of retrieval->execution->distillation->audit->reuse.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("15.2 Verified Capabilities", h2))
for item in [
    "search -> execute",
    "log -> distill -> audit -> promote",
    "distill_and_promote_candidate",
    "MCP layer search and execution",
    "Codex calling runtime via MCP",
    "provenance write-back",
    "usage_count / last_used_at write-back",
]:
    story.append(Paragraph("  [OK] " + item, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("15.3 Current Test Coverage", h2))
story.append(Paragraph(
    "25 tests covering: trajectory access, skill index, execute path, static audit, semantic audit, "
    "distillation rules, fallback provider, provenance backfill, MCP search tool, orchestration service. "
    "All 25 tests currently pass.", body))
story.append(PageBreak())

# -- SECTION 16 --
story += section_badge(16, "Differentiation from Ordinary Skill Accumulation")
story.append(Paragraph(
    "The true differentiation is not 'accumulating skills', but the following three points:", body))
story.append(Spacer(1, 8))
story.append(Paragraph("16.1 Not Just Accumulation, But Governance Closed Loop", h2))
story.append(Paragraph(
    "Not casually saving after completing a task, but: distill -> audit -> promote -> index -> execute. "
    "This is a complete governance chain.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("16.2 Not a Second AI, But a Capability Layer Under the Host", h2))
story.append(Paragraph(
    "The project consistently坚持: no extra chat AI, no second agent nesting, "
    "let host AI directly call runtime. This makes the architecture cleaner and more suitable for embedding in various AI applications.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("16.3 Not a Black Box, But尽量可解释", h2))
story.append(Paragraph(
    "System supports: why matched, rule provenance, recommended next action. "
    "This is easier to govern and debug than 'mysterious memory skill then execute'.", body))
story.append(PageBreak())

# -- SECTION 17 --
story += section_badge(17, "Current Limitations")
story.append(Paragraph("While the system is usable, there are still clear boundaries:", body))
limits = [
    ("Semantic audit is not final form",
     "Current semantic audit is a heuristic skeleton, not a true LLM semantic auditor."),
    ("Retrieval is still lightweight",
     "Hybrid retrieval has not been implemented; only explainability and recommended actions are added."),
    ("Fallback provider is still mock",
     "Rule-unmatched skill generation path is open, but real external provider not yet connected."),
    ("archive-cold is still a placeholder",
     "Cold skill archiving and long-term library governance not fully implemented."),
    ("Currently偏向local file workflows",
     "Browser, GUI, remote systems, more complex tool types not yet connected."),
]
for title, desc in limits:
    story.append(Paragraph("<b>  ! %s</b>" % title, bullet_b))
    story.append(Paragraph(desc, ParagraphStyle("LD", fontName=FREG, fontSize=10,
        textColor=TXT_LITE, leading=14, spaceAfter=8, leftIndent=28)))
story.append(PageBreak())

# -- SECTION 18 --
story += section_badge(18, "Why It Can Be Used Now")
story.append(Paragraph("Despite the above limitations, it has reached a 'usable for trial' stage. Reason:", body))
reasons = [
    ("Core closed loop is established",
     "Retrieval, execution, distillation, audit, onboarding, reuse all in place."),
    ("Audit is no longer purely static",
     "Semantic layer is not deep enough, but can already block a batch of fake skills and template skills."),
    ("Host integration is stable",
     "Codex MCP integration, global skills, AGENTS preferences all in place."),
    ("Reusable rule library already exists",
     "Not just a concept demo, but already has a batch of real executable local workflow skills."),
]
for i, (title, desc) in enumerate(reasons, 1):
    story.append(Paragraph("<b>%d. %s</b>" % (i, title), bullet_b))
    story.append(Paragraph(desc, ParagraphStyle("RD", fontName=FREG, fontSize=10,
        textColor=TXT_LITE, leading=14, spaceAfter=8, leftIndent=28)))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The reasonable pace is not to continue indefinitely stacking features, but: "
    "enter real trial phase, observe which of audit/retrieval/distillation most easily exposes problems, "
    "then fill in weaknesses based on real feedback.", body))
story.append(PageBreak())

# -- SECTION 19 --
story += section_badge(19, "Suggested Next Phase Roadmap")
story.append(Paragraph("19.1 First Priority: Real LLM Semantic Audit", h2))
story.append(Paragraph(
    "Upgrade current heuristic semantic audit to trajectory-aware, code-aware, promote-aware "
    "LLM semantic auditor.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("19.2 Second Priority: Lightweight Hybrid Retrieval", h2))
story.append(Paragraph(
    "Not rushing into heavy vector infrastructure, but first doing: keyword + schema matching + "
    "provenance weighting + audit weighting + usage weighting + rerank.", body))
story.append(Spacer(1, 8))
story.append(Paragraph("19.3 Third Priority: Long-term Governance", h2))
for item in ["archive-cold full implementation",
             "Duplicate skill merging",
             "Long-term library cleanup",
             "Lifecycle management"]:
    story.append(Paragraph("  - " + item, bullet))
story.append(Spacer(1, 8))
story.append(Paragraph("19.4 Fourth Priority: Real Provider Integration", h2))
story.append(Paragraph(
    "Switch fallback provider from mock to real model provider.", body))
story.append(PageBreak())

# -- SECTION 20 --
story += section_badge(20, "Conclusion")
story.append(Paragraph(
    "The core value of this skill runtime is not 'giving AI one more feature', but:", body))
story.append(Spacer(1, 8))
story.append(Table([[Paragraph(
    "Transforming AI workflows into a<br/>"
    "<font size=14 color='#4a90d9'><b>Governable | Auditable | Reusable | Explainable</b></font><br/>"
    "Capability Layer",
    core_val)]],
    style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
        ("BOX", (0,0), (-1,-1), 2, ACCENT),
        ("TOPPADDING", (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
    ])))
story.append(Spacer(1, 12))
story.append(Paragraph("Its significance is not to replace the host AI, but to:", body))
for c in [
    "Let host AI not have to start from scratch every time",
    "Let skill deposits no longer be just context fragments",
    "Let skill library have governance, not just pile of scripts",
    "Let future AI applications be more like 'systems that accumulate experience', "
    "not 'assistants that start over every time'",
]:
    story.append(Paragraph("  + " + c, bullet))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "From an engineering perspective, this project has completed the most important step at its current stage:", body))
story.append(Spacer(1, 6))
story.append(Table([[Paragraph(
    "<b>Transforming a concept into a runnable local closed loop.</b>",
    concl_sty)]],
    style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
        ("TOPPADDING", (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
    ])))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "This means it is no longer just an idea, but a system foundation that already has "
    "value for continued evolution.", body))

# -- BUILD PDF --
doc.build(story)
print("PDF generated: " + PDF_OUT)

# -- CONVERT TO IMAGES --
pdf_doc = pypdfium2.PdfDocument(PDF_OUT)
n_pages = len(pdf_doc)
print("PDF has %d pages, converting to images..." % n_pages)
for i in range(n_pages):
    page = pdf_doc[i]
    bitmap = page.render(scale=2.0, rotation=0)
    pil_img = bitmap.to_pil()
    out_path = os.path.join(IMG_OUT, "section_%03d.png" % (i+1))
    pil_img.save(out_path)
    print("  [%d/%d] %s" % (i+1, n_pages, out_path))
print("All done! Images in: " + IMG_OUT)
