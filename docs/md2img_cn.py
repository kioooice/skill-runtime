# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pypdfium2

# register Chinese fonts
pdfmetrics.registerFont(TTFont('SimHei', r'C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFont(TTFont('SimSun', r'C:/Windows/Fonts/simsun.ttc'))

DARK_BG  = HexColor("#1a1a2e")
ACCENT   = HexColor("#4a90d9")
LIGHT_BG = HexColor("#f5f7fa")
TXT_DARK = HexColor("#2c3e50")
TXT_LITE = HexColor("#7f8c8d")
CODE_BG  = HexColor("#f0f4f8")
CODE_BDR = HexColor("#d0d7de")
FBOLD = "SimHei"
FREG  = "SimHei"
FMON  = "Courier"

PDF_OUT = r"D:/02-Projects/vibe/docs/skill-runtime-project-cn.pdf"
IMG_OUT = r"D:/02-Projects/vibe/docs/skill-runtime-images-cn"
os.makedirs(IMG_OUT, exist_ok=True)

doc = SimpleDocTemplate(PDF_OUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
    title="Skill Runtime 项目详细报告")

W, H = A4

def ms(name, **kw):
    d = dict(fontName=FREG, fontSize=10, leading=15, textColor=TXT_DARK, spaceAfter=5)
    d.update(kw)
    return ParagraphStyle(name, **d)

ct_title = ms("CT", fontName=FBOLD, fontSize=28, textColor=white, alignment=TA_CENTER, leading=36)
ct_main  = ms("CM", fontName=FBOLD, fontSize=32, textColor=ACCENT, alignment=TA_CENTER, leading=42, spaceAfter=20)
ct_sub   = ms("CS", fontName=FREG, fontSize=13, textColor=HexColor("#a0b4c8"), alignment=TA_CENTER, leading=18)
ct_tag   = ms("CTag", fontName=FREG, fontSize=11, textColor=HexColor("#6c8ebf"), alignment=TA_CENTER, leading=16)
h1s = ms("H1S", fontName=FBOLD, fontSize=18, textColor=DARK_BG, leading=24, spaceBefore=20, spaceAfter=8)
h2s = ms("H2S", fontName=FBOLD, fontSize=13, textColor=HexColor("#34495e"), leading=18, spaceBefore=14, spaceAfter=5)
h3s = ms("H3S", fontName=FBOLD, fontSize=11, textColor=HexColor("#4a5568"), leading=15, spaceBefore=8, spaceAfter=3)
body = ms("Body")
bllt = ms("Blt", leftIndent=14, bulletIndent=2, spaceAfter=3)
tbl_h = ms("TH", fontName=FBOLD, fontSize=9, textColor=white, leading=12)
tbl_c = ms("TC", fontSize=9, leading=12)
cd_sty = ms("CD", fontName=FMON, fontSize=8.5, textColor=HexColor("#d63384"), leading=12, backColor=CODE_BG, borderPad=4)
warn_b = ms("WB", fontName=FBOLD, fontSize=10, textColor=HexColor("#e65100"), leading=15, spaceAfter=2, leftIndent=14, bulletIndent=2)
warn_d = ms("WD", fontSize=9.5, textColor=TXT_LITE, leading=13, spaceAfter=5, leftIndent=28)

def badge(num, title):
    bnum = ms("BN", fontName=FBOLD, fontSize=9, textColor=white, alignment=TA_CENTER)
    btit = ms("BT", fontName=FBOLD, fontSize=15, textColor=DARK_BG, leading=20)
    return [Spacer(1,4),
            Table([[Paragraph('%02d' % num, bnum), Paragraph(title, btit)]],
                colWidths=[1.2*cm, 14.3*cm],
                style=TableStyle([
                    ("BACKGROUND",(0,0),(0,0),ACCENT),
                    ("BACKGROUND",(1,0),(1,0),LIGHT_BG),
                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("TOPPADDING",(0,0),(-1,-1),7),
                    ("BOTTOMPADDING",(0,0),(-1,-1),7),
                    ("LEFTPADDING",(0,0),(0,0),3),
                    ("RIGHTPADDING",(0,0),(0,0),3),
                ])),
            Spacer(1,4)]

def ctable(hdrs, rows, widths):
    data = [[Paragraph(h, tbl_h) for h in hdrs]] + \
           [[Paragraph(str(c), tbl_c) for c in r] for r in rows]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#f8f9fa")]),
        ("GRID",(0,0),(-1,-1),0.5,HexColor("#dee2e6")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    return t

def cdblk(text):
    return Table([[Paragraph(text, cd_sty)]],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),CODE_BG),
            ("BOX",(0,0),(-1,-1),1,CODE_BDR),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10),
        ]))

def hl(text):
    return Table([[Paragraph(text, ms("HL", fontName=FBOLD, fontSize=12,
        textColor=white, leading=18, alignment=TA_CENTER))]],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),DARK_BG),
            ("TOPPADDING",(0,0),(-1,-1),14),
            ("BOTTOMPADDING",(0,0),(-1,-1),14),
        ]))

S = []

# === 封面 ===
S += [Spacer(1,2.5*cm),
      Paragraph("Skill Runtime", ct_title),
      Paragraph("项目详细报告", ct_main),
      Spacer(1,0.8*cm),
      Paragraph("面向宿主 AI 的本地可演化技能运行时与治理系统", ct_sub),
      Spacer(1,0.5*cm),
      Paragraph("可治理  |  可审计  |  可复用  |  可解释", ct_tag),
      Spacer(1,1.5*cm),
      Paragraph("v1.0  |  2026", ms("Ver", fontName=FREG, fontSize=10,
          textColor=HexColor("#8899aa"), alignment=TA_CENTER)),
      PageBreak()]

# === 1. 项目概述 ===
S += badge(1,"项目概述")
S.append(Paragraph(
    '本项目实现了一套面向 <b>Codex</b> 的本地 <b>skill runtime</b>，'
    '目标不是再做一个新的 AI 助手，而是给宿主 AI 加一层'
    '<font color="#4a90d9"><b>「技能运行时与治理内核」</b></font>。', body))
S.append(Spacer(1,5))
S.append(Paragraph('这套系统解决的问题不是"AI 会不会做任务"，而是：', body))
for t in ['AI 做过的工作流能不能<b>沉淀下来</b>',
          '沉淀下来的技能能不能<b>被检查、治理和复用</b>',
          '宿主 AI 下次遇到类似任务时，能不能先复用已有技能，而不是从头再做']:
    S.append(Paragraph('  \u2022 ' + t, bllt))
S.append(Spacer(1,6))
S.append(Paragraph('因此，这个项目的定位是：', body))
for t in ['\u2717  不是独立 AI 产品',
          '\u2717  不是新的聊天界面',
          '\u2717  不是另一个 agent',
          '\u2713  而是 <b>AI 应用内部的一个能力层</b>']:
    S.append(Paragraph(t, ms("Pos", fontName=FBOLD if '\u2713' in t else FREG,
        fontSize=10, leading=15, spaceAfter=3, leftIndent=14, bulletIndent=2)))
S.append(Spacer(1,6))
S.append(Paragraph('它更接近：', body))
for t in ['skill runtime','workflow memory','skill governance kernel','host-AI capability layer']:
    S.append(Paragraph('  \u2022 <b>' + t + '</b>', bllt))
S.append(Spacer(1,6))
S.append(Paragraph(
    '当前这套实现已经可以挂到 Codex 下方，通过 <b>MCP</b> 工具方式被调用，'
    '并且具备一条完整闭环：', body))
S.append(Spacer(1,4))
S.append(ctable(
    ['search','execute','distill','audit','promote','reuse'],
    [['->','->','->','->','->','']],
    [2.3*cm]*6))
S.append(PageBreak())

# === 2. 核心问题 ===
S += badge(2,"项目想解决的核心问题")
S.append(Paragraph('2.1 传统 AI 工作流的缺陷', h2s))
defects = [
    ('重复任务反复从头规划', '即使某类任务已经做过，下一次仍然会重新分析、重新写流程、重新调用工具。'),
    ('能做任务，但不能有效沉淀', '任务完成之后，过程往往只留在聊天上下文里，没有被转化为结构化的可复用能力。'),
    ('技能复用缺乏治理', "有些系统会'积累技能'，但只是简单保存脚本或记忆片段，缺少审计、入库、生命周期管理等治理层能力。"),
    ('宿主 AI 和技能系统耦合不清', "很多方案会演化成'再套一个 AI'或者'外部 agent 控制宿主 agent'，结果架构复杂、边界混乱、成本增加。"),
]
for i,(t,d) in enumerate(defects,1):
    S.append(Paragraph('<b>%d. %s</b>' % (i,t),
        ms('D'+str(i), fontName=FBOLD, fontSize=10, leading=15, spaceAfter=2, leftIndent=14, bulletIndent=2)))
    S.append(Paragraph(d, ms('DD'+str(i), fontSize=9.5, textColor=TXT_LITE, leading=13, spaceAfter=6, leftIndent=28)))
S.append(Spacer(1,8))
S.append(Paragraph('2.2 本项目的判断', h2s))
S.append(Paragraph('未来这类系统最合理的形态，不是独立 AI，而是作为现有 AI 应用内部的一层能力内核存在。', body))
S.append(Spacer(1,4))
S.append(Paragraph('也就是说：', body))
S.append(Paragraph('  \u2022 <b>宿主 AI</b> 负责理解任务、和用户交互、做最终决策', bllt))
S.append(Paragraph('  \u2022 <b>skill runtime</b> 负责技能检索、执行、蒸馏、审计、入库和复用', bllt))
S.append(Spacer(1,4))
S.append(Paragraph('这也是为什么项目最终选择用 MCP 把 runtime 暴露给 Codex，而不是把它做成独立聊天程序。', body))
S.append(PageBreak())

# === 3. 定位与设计原则 ===
S += badge(3,"项目定位与设计原则")
S.append(Paragraph(
    '本项目的准确定位是：<br/><br/>'
    '<font size=14 color="#4a90d9"><b>一套面向宿主 AI 的、本地可演化的技能运行时与治理系统</b></font>',
    body))
S.append(Spacer(1,8))
S.append(Paragraph('设计原则', h2s))
for pt,pd in [
    ('P1 宿主优先', '宿主 AI 是上层入口。skill runtime 不抢用户交互，不伪装成第二个 AI。'),
    ('P2 先复用，再生成', '面对任务，优先检索已有 skill；只有没命中时，才考虑新生成。'),
    ('P3 生成必须可治理', '新 skill 不能直接入库，必须进入 staging，并通过审计后再 promote。'),
    ('P4 结构优先于智能', '第一阶段先做稳固闭环和可解释结构，不急着一上来全靠 LLM 生成。'),
    ('P5 能力层而不是产品壳', '对外优先暴露 CLI、MCP tools、技能包装层，而不是新的 UI。'),
    ('P6 可解释性很重要', 'skill 被检索、生成和复用时，要尽量知道：为什么命中、来自哪条规则、为什么推荐下一步。'),
]:
    S.append(Paragraph('<b>'+pt+'</b>', h3s))
    S.append(Paragraph(pd, body))
    S.append(Spacer(1,3))
S.append(PageBreak())

# === 4. 系统总体架构 ===
S += badge(4,"系统总体架构")
S.append(Paragraph('系统结构可以概括为四层：', body))
S.append(Spacer(1,5))
for lt in [
    ('\u2460 Host AI 层', '当前宿主是 Codex。负责接收用户任务、理解需求、规划整体动作、决定何时调用 runtime。'),
    ('\u2461 Adapter 层', '当前实现了 CLI 和 MCP server 两个适配层，其中 MCP 是与 Codex 集成的主方式。'),
    ('\u2462 Skill Runtime 层', '项目核心，负责 trajectory 存储、skill 蒸馏、skill 审计、promote 守卫、skill 检索、skill 执行、provenance 回填。'),
    ('\u2463 Storage / Governance 层', '底层以本地文件为主，包含 skill_store（staging/active/archive/rejected）、trajectories、audits、index.json。'),
]:
    S.append(Paragraph('<b>'+lt[0]+'</b>', h3s))
    S.append(Paragraph(lt[1], body))
    S.append(Spacer(1,4))
S.append(PageBreak())

# === 5. 目录与模块结构 ===
S += badge(5,"目录与模块结构")
S.append(cdblk(
    "scripts/\n"
    "  skill_cli.py        # CLI 入口\n"
    "  skill_mcp_server.py # MCP 服务\n\n"
    "skill_runtime/\n"
    "  api/        # RuntimeService 业务层\n"
    "  memory/     # trajectory 存取与校验\n"
    "  distill/    # 从 trajectory 生成 skill\n"
    "  audit/      # skill 审计（静态 + 语义）\n"
    "  retrieval/  # 技能索引与检索\n"
    "  execution/  # 工具注入与 skill 执行\n"
    "  governance/ # promote guard、provenance\n\n"
    "skill_store/\n"
    "  staging/  active/  archive/  rejected/\n"
    "  index.json\n\n"
    "trajectories/  audits/  demo/  tests/"))
S.append(Spacer(1,6))
S.append(Paragraph('各模块职责：', body))
for m,d in [
    ('api/', 'RuntimeService 业务层，CLI 和 MCP 统一调用'),
    ('memory/', 'trajectory 存取、校验，为 distill/audit 提供上下文'),
    ('distill/', '从成功 trajectory 生成 skill，规则蒸馏 + LLM fallback'),
    ('audit/', '双层审计：静态规则 + 语义骨架'),
    ('retrieval/', '关键词打分检索 + provenance 解释 + 顶层推荐动作'),
    ('execution/', '工具注入、动态加载、skill 执行、使用统计回写'),
    ('governance/', 'promote guard、provenance backfill'),
]:
    S.append(Paragraph('  \u2022 <b>'+m+'</b> '+d, bllt))
S.append(PageBreak())

# === 6. 核心数据模型 ===
S += badge(6,"核心数据模型")
for name,desc,fields in [
    ('Trajectory', '表示一次任务执行轨迹', [
        'task_id, session_id, task_description, steps, final_status, artifacts, started_at, ended_at',
        'steps 包含：step_id, tool_name, tool_input, observation, status, thought_summary',
    ]),
    ('SkillMetadata', '表示一个 skill 的索引与治理信息', [
        'skill_name, file_path, summary, docstring, input_schema, output_schema',
        'source_trajectory_ids, created_at, last_used_at, usage_count, status, audit_score, tags',
        'rule_name, rule_priority, rule_reason（用于 provenance）',
    ]),
    ('AuditReport', '表示审计结果', [
        'status, security_score, suggestions, optimized_docstring, refactored_code',
        'static_score, semantic_score, static_findings, semantic_findings, semantic_summary',
    ]),
]:
    S.append(Paragraph('<b>'+name+'</b> \u2014 '+desc, h3s))
    for f in fields:
        S.append(Paragraph('  \u2022 '+f, bllt))
    S.append(Spacer(1,5))
S.append(PageBreak())

# === 7. 主闭环 ===
S += badge(7,"主闭环：任务如何演化成技能")
for st in [
    ('\u2460 搜索 Search', '宿主 AI 调用 search_skill，输入任务描述，返回匹配 skill + 顶层建议'),
    ('\u2461 执行 Execute', '有强命中 \u2192 调用 execute_skill，动态加载并执行 active skill'),
    ('\u2462 完成任务', '无命中 \u2192 宿主 AI 正常完成该任务'),
    ('\u2463 记录轨迹', '将此次任务执行过程写成 trajectory'),
    ('\u2464 蒸馏 Distill', 'trajectory 进入 distill，符合规则 \u2192 生成真实可执行 skill \u2192 进入 staging'),
    ('\u2465 审计 Audit', 'staging skill 经过静态 + 语义双层审计'),
    ('\u2466 Promote', '只有 audit 通过的 skill 才允许 promote 到 active'),
    ('\u2467 复用 Reuse', '下次遇到类似任务，优先 search \u2192 execute，不再从零规划'),
]:
    S.append(Paragraph('<b>'+st[0]+'</b>', h3s))
    S.append(Paragraph(st[1], body))
    S.append(Spacer(1,3))
S.append(PageBreak())

# === 8. Distillation ===
S += badge(8,"Distillation 设计")
S.append(Paragraph('8.1 为什么要先做规则蒸馏', h2s))
S.append(Paragraph('项目没有一开始就完全依赖 LLM 生成 skill，而是先做规则蒸馏。原因是：规则蒸馏更可控、更容易验证、更容易解释、更适合先做闭环。', body))
S.append(Spacer(1,5))
S.append(Paragraph('8.2 当前规则库支持的模式', h2s))
for r in ['text_merge','text_replace','single_file_transform','batch_rename',
          'directory_copy','directory_move','directory_text_replace',
          'csv_to_json','json_to_csv']:
    S.append(Paragraph('  \u2022 <b>'+r+'</b>', bllt))
S.append(Spacer(1,5))
S.append(Paragraph('8.3 规则注册表', h2s))
S.append(Paragraph('每条规则都有：RULE_NAME、PRIORITY、match()、explain_match()。规则本身更易维护，生成结果具备 provenance 和解释性。', body))
S.append(Spacer(1,5))
S.append(Paragraph('8.4 LLM fallback', h2s))
S.append(Paragraph('当规则库无法命中时，进入 fallback provider 流程：构造 prompt \u2192 调用 provider \u2192 生成 candidate code \u2192 写入 staging。当前 provider 仍是 mock provider，目的是让 fallback 链路先可测试。', body))
S.append(PageBreak())

# === 9. Audit ===
S += badge(9,"Audit 设计")
S.append(Paragraph('9.1 为什么审计是核心', h2s))
S.append(Paragraph("单纯'积累技能'并不稀缺，真正关键的是：新 skill 能不能安全复用、能不能以合理粒度存在、有没有过拟合一次性轨迹、是否真的适合入库。因此审计不是附属功能，而是整个治理闭环的核心。", body))
S.append(Spacer(1,5))
S.append(Paragraph('9.2 静态审计', h2s))
S.append(Paragraph('负责检查：', body))
for item in ['危险命令 / shell=True / os/system', '绝对路径硬编码 / 用户名硬编码',
             '缺失 run() / 缺失 docstring', 'run 函数过长 / 语法错误']:
    S.append(Paragraph('  \u2022 '+item, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('9.3 语义审计骨架', h2s))
S.append(Paragraph('还会检查：', body))
for item in ['docstring 是否利于检索', 'skill 是否承担过多职责',
             '是否和 trajectory 工具链一致', 'kwargs 是否覆盖关键输入',
             '是否把 artifact 名称硬编码进 skill', '是否是模板式或空操作式 skill']:
    S.append(Paragraph('  \u2022 '+item, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('现在的审计能力已经能拦住：静态高风险 skill、明显错配 trajectory 的模板 skill、不足以 promote 的伪 skill。但它仍然不是 LLM 驱动的深语义审计，只能算\u2018语义骨架版\u2019。', body))
S.append(PageBreak())

# === 10. Retrieval ===
S += badge(10,"Retrieval 设计")
S.append(Paragraph('10.1 当前检索方式', h2s))
S.append(Paragraph('当前检索以关键词打分为主，综合考虑：skill 名称、summary、docstring、tags、input/output schema、active 状态、audit_score。', body))
S.append(Spacer(1,5))
S.append(Paragraph('10.2 可解释性增强', h2s))
S.append(Paragraph('检索结果不仅返回 skill，还返回：why_matched、rule_name、rule_priority、rule_reason。当一个 skill 被搜出来时，系统会尽量说明为什么命中、它最初是按哪条规则生成的。', body))
S.append(Spacer(1,5))
S.append(Paragraph('10.3 顶层推荐动作', h2s))
S.append(ctable(['情况','推荐动作'],
    [['强命中','execute_skill'],
     ['弱命中/无命中','distill_and_promote_candidate']],
    [4*cm,11.5*cm]))
S.append(Spacer(1,5))
S.append(Paragraph('10.4 目前还没做的部分', h2s))
for item in ['向量检索','BM25','混合检索 rerank']:
    S.append(Paragraph('  \u2022 '+item, bllt))
S.append(Paragraph('这是有意控制节奏，因为在现阶段，错误 promote 的风险比排序不准更高，所以优先补了语义审计。', body))
S.append(PageBreak())

# === 11. Execution ===
S += badge(11,"Execution 设计")
S.append(Paragraph('11.1 技能统一入口', h2s))
S.append(Paragraph('所有 skill 统一暴露 run(tools, **kwargs) 接口，保证宿主执行接口稳定。', body))
S.append(Spacer(1,5))
S.append(Paragraph('11.2 RuntimeTools', h2s))
S.append(Paragraph('当前 RuntimeTools 提供了一套受控本地工具能力：', body))
for t in ['read_text / write_text','list_files','run_shell','rename_path',
          'copy_file / move_file','read_json / write_json']:
    S.append(Paragraph('  \u2022 '+t, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('11.3 使用统计', h2s))
S.append(Paragraph('skill 成功执行后，会回写 usage_count 和 last_used_at，为未来的治理和归档做了准备。', body))
S.append(PageBreak())

# === 12. MCP ===
S += badge(12,"MCP 与 Codex 集成")
S.append(Paragraph('12.1 为什么选择 MCP', h2s))
S.append(Paragraph('MCP 的价值在于：把 runtime 暴露成宿主可调用的工具层、保持 runtime 独立于特定宿主、让 Codex 直接把 runtime 当本地能力层使用。对工具层集成，MCP 足够合适。', body))
S.append(Spacer(1,5))
S.append(Paragraph('12.2 当前暴露的 MCP tools', h2s))
tools_list = ['search_skill','execute_skill','distill_trajectory',
              'distill_and_promote_candidate','audit_skill','promote_skill',
              'log_trajectory','reindex_skills','backfill_skill_provenance']
t_rows = [[tools_list[i] if i < len(tools_list) else '' for i in range(j*3,j*3+3)] for j in range(3)]
tt = Table([[Paragraph(x, tbl_c) for x in row] for row in t_rows], colWidths=[5*cm]*3)
tt.setStyle(TableStyle([
    ('GRID',(0,0),(-1,-1),0.5,HexColor("#dee2e6")),
    ('BACKGROUND',(0,0),(-1,-1),HexColor("#f8f9fa")),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('LEFTPADDING',(0,0),(-1,-1),8),
]))
S.append(tt)
S.append(Spacer(1,5))
S.append(Paragraph('12.3 Codex 全局接入', h2s))
S.append(Paragraph('通过 ~/.codex/config.toml 配置 skill_runtime MCP server。宿主层增强包括：全局 AGENTS 偏好、全局 MEMORY 记录、全局 skills 包装（skill-search / skill-execute / skill-distill / skill-audit / skill-promote / skill-distill-promote）。', body))
S.append(PageBreak())

# === 13. CLI ===
S += badge(13,"CLI、MCP 与组合编排")
S.append(Paragraph('13.1 CLI 命令', h2s))
for cmd in ['search','execute','distill','distill-and-promote','audit',
            'promote','log-trajectory','reindex','archive-cold','backfill-provenance']:
    S.append(Paragraph('  \u2022 '+cmd, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('13.2 为什么后来加了组合命令', h2s))
S.append(Paragraph('早期完整链路是 log \u2192 distill \u2192 audit \u2192 promote，但对于宿主来说这条链太长。因此加入了 distill-and-promote 和 distill_and_promote_candidate，这条短路径大幅降低了宿主使用成本。', body))
S.append(PageBreak())

# === 14. Provenance ===
S += badge(14,"Provenance 设计")
S.append(Paragraph('14.1 为什么 provenance 重要', h2s))
S.append(Paragraph("当 skill 越来越多时，如果只知道'它存在'，但不知道'它为什么存在、怎么来的'，治理就会迅速失控。", body))
S.append(Spacer(1,5))
S.append(Paragraph('14.2 记录的内容', h2s))
for item in ['rule_name \u2014 按哪条规则生成','rule_priority \u2014 规则优先级',
             'rule_reason \u2014 命中原因']:
    S.append(Paragraph('  \u2022 '+item, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('14.3 历史回填', h2s))
S.append(Paragraph('对于字段上线前就已存在的 legacy skill，做了 backfill-provenance。它会扫描现有 active skill，并尽量补齐 provenance，使整个 skill 库不会因历史数据不完整而割裂。', body))
S.append(PageBreak())

# === 15. 演示与验证 ===
S += badge(15,"演示闭环与验证")
S.append(Paragraph('15.1 demo 场景', h2s))
S.append(Paragraph('最早的 demo 是一个很典型的本地文件工作流：<b>merge txt files into markdown</b>。被选择的原因是：简单易懂、可本地复现、能清晰展示检索\u2192执行\u2192蒸馏\u2192审计\u2192复用的闭环。', body))
S.append(Spacer(1,5))
S.append(Paragraph('15.2 已验证的能力', h2s))
for item in ['search \u2192 execute','log \u2192 distill \u2192 audit \u2192 promote',
             'distill_and_promote_candidate','MCP 层搜索与执行',
             'Codex 通过 MCP 调 runtime','provenance 回写',
             'usage_count / last_used_at 回写']:
    S.append(Paragraph('  \u2705 '+item, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('15.3 当前测试覆盖', h2s))
S.append(Paragraph('测试已覆盖 trajectory 存取、skill index、execute path、static audit、semantic audit、distillation rules、fallback provider、provenance backfill、MCP search tool、orchestration service。测试数量已达 <b>25 条</b>，全部通过。', body))
S.append(PageBreak())

# === 16. 差异化 ===
S += badge(16,"与普通技能积累方案的差异")
S.append(Paragraph('本项目真正的差异化不在于\u2018会积累技能\u2019，真正的差异在于以下三点：', body))
S.append(Spacer(1,5))
S.append(Paragraph('16.1 它不是单纯积累，而是治理闭环', h2s))
S.append(Paragraph('不是做完任务就随便存下来，而是 distill \u2192 audit \u2192 promote \u2192 index \u2192 execute。这是一条完整治理链。', body))
S.append(Spacer(1,5))
S.append(Paragraph('16.2 它不是第二个 AI，而是宿主下的能力层', h2s))
S.append(Paragraph('项目一直坚持：不再额外造一个聊天 AI、不用第二个 agent 套娃、让宿主 AI 直接调 runtime。这让架构更干净，也更适合嵌入各种 AI 应用。', body))
S.append(Spacer(1,5))
S.append(Paragraph('16.3 它不是黑箱，而是尽量可解释', h2s))
S.append(Paragraph('当前系统已经尽量支持：why matched、rule provenance、recommended next action。这比\u2018神秘记忆技能然后执行\u2019要更容易治理，也更容易调试。', body))
S.append(PageBreak())

# === 17. 当前局限 ===
S += badge(17,"当前局限")
S.append(Paragraph('虽然系统已经可用，但当前仍有明显边界。', body))
for t,d in [
    ('语义审计还不是最终形态', '现在的语义审计是 heuristic 骨架，不是真正的 LLM 语义审计器。'),
    ('检索还是轻量版本', '当前仍然没有上混合检索，只是做了可解释和推荐动作增强。'),
    ('fallback provider 还是 mock', '规则未命中的 skill 生成路径已经打通，但真实外部 provider 还没接。'),
    ('archive-cold 仍是占位', '冷技能归档和长期库治理还没有完整落地。'),
    ('目前偏本地文件工作流', '浏览器、GUI、远程系统、更多复杂工具类型还没有接入。'),
]:
    S.append(Paragraph('  \u26a0 <b>'+t+'</b>', warn_b))
    S.append(Paragraph(d, warn_d))
S.append(PageBreak())

# === 18. 为什么可用 ===
S += badge(18,"为什么当前阶段可以先用")
S.append(Paragraph('尽管存在以上局限，但当前已经到了\u2018可以试用\u2019的阶段。原因是：', body))
for i,(t,d) in enumerate([
    ('核心闭环已成立', '检索、执行、蒸馏、审计、入库、复用都已具备。'),
    ('审计已经不是纯静态', '语义层虽然还不够深，但已经能拦住一批假 skill 和模板型 skill。'),
    ('宿主接入已经稳定', 'Codex 的 MCP 接入、全局 skills、AGENTS 偏好都已经就位。'),
    ('已经有可复用规则库', '不再只是概念 demo，而是已经有一批真实可执行的本地 workflow skill。'),
],1):
    S.append(Paragraph('<b>'+str(i)+'. '+t+'</b>',
        ms('R'+str(i), fontName=FBOLD, fontSize=10, leading=15, spaceAfter=2, leftIndent=14, bulletIndent=2)))
    S.append(Paragraph(d, ms('RD'+str(i), fontSize=9.5, textColor=TXT_LITE, leading=13, spaceAfter=5, leftIndent=28)))
S.append(Spacer(1,5))
S.append(Paragraph('合理的节奏不是继续无限堆功能，而是：先进入真实试用阶段、看审计、检索、蒸馏哪一块最容易暴露问题、再根据真实反馈补短板。', body))
S.append(PageBreak())

# === 19. 下阶段路线 ===
S += badge(19,"建议的下一阶段路线")
S.append(Paragraph('19.1 第一优先：真实 LLM 语义审计', h2s))
S.append(Paragraph('把当前 heuristic 语义审计升级成 trajectory-aware、code-aware、promote-aware 的 LLM semantic auditor。', body))
S.append(Spacer(1,5))
S.append(Paragraph('19.2 第二优先：轻量混合检索', h2s))
S.append(Paragraph('不是一上来上重型向量基础设施，而是先做：关键词 + schema 命中 + provenance 权重 + audit 加权 + usage 加权 + rerank。', body))
S.append(Spacer(1,5))
S.append(Paragraph('19.3 第三优先：长期治理', h2s))
for item in ['archive-cold 完整落地','重复 skill 合并','长期库清理','生命周期管理']:
    S.append(Paragraph('  \u2022 '+item, bllt))
S.append(Spacer(1,5))
S.append(Paragraph('19.4 第四优先：真实 provider 接入', h2s))
S.append(Paragraph('把 fallback provider 从 mock 切到真实模型 provider。', body))
S.append(PageBreak())

# === 20. 结论 ===
S += badge(20,"项目结论")
S.append(Paragraph('这套 skill runtime 的核心价值，不是\u2018又让 AI 多了一个功能\u2019，而是：', body))
S.append(Spacer(1,6))
S.append(Table([[Paragraph(
    '把 AI 做过的工作流，变成了一套<br/>'
    '<font size=14 color="#4a90d9"><b>可治理、可审计、可复用、可解释</b></font><br/>'
    '的能力层。',
    ms('CV', fontName=FBOLD, fontSize=13, textColor=DARK_BG, leading=22, alignment=TA_CENTER))]],
    style=TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),LIGHT_BG),
        ('BOX',(0,0),(-1,-1),2,ACCENT),
        ('TOPPADDING',(0,0),(-1,-1),18),
        ('BOTTOMPADDING',(0,0),(-1,-1),18),
    ])))
S.append(Spacer(1,10))
S.append(Paragraph('它的意义不在于替代宿主 AI，而在于：', body))
for c in [
    '让宿主 AI 不必每次都从头再做',
    '让技能沉淀不再只是上下文碎片',
    '让技能库有治理，而不是单纯堆脚本',
    '让未来的 AI 应用更像\u2018会积累经验的系统\u2019，而不是\u2018每次重新开始的助手\u2019',
]:
    S.append(Paragraph('  \u2705 '+c, bllt))
S.append(Spacer(1,10))
S.append(Paragraph('从工程角度看，这个项目当前阶段已经完成了最重要的一步：', body))
S.append(Spacer(1,5))
S.append(hl('<b>把概念变成了一个能跑通的本地闭环。</b>'))
S.append(Spacer(1,6))
S.append(Paragraph('这意味着它不再只是一个想法，而是一个已经具备继续演化价值的系统基础。', body))

# BUILD
doc.build(S)
print("PDF: " + PDF_OUT)

# IMAGES
pdf_doc = pypdfium2.PdfDocument(PDF_OUT)
n = len(pdf_doc)
print("PDF %d pages -> images..." % n)
for i in range(n):
    page = pdf_doc[i]
    bitmap = page.render(scale=2.0, rotation=0)
    pil_img = bitmap.to_pil()
    out = os.path.join(IMG_OUT, "page_%03d.png" % (i+1))
    pil_img.save(out)
    print("  [%d/%d] %s" % (i+1, n, out))
print("Done! -> " + IMG_OUT)
