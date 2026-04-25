# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import pypdfium2

# register Chinese fonts
pdfmetrics.registerFont(TTFont('SimHei', r'C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFont(TTFont('SimSun', r'C:/Windows/Fonts/simsun.ttc'))

# ── TikTok 9:16 竖版尺寸 (宽<高) ──────────────────────────────────────────
PAGE_W = 15 * cm   # ≈ 5.9 inch = 378px @72dpi
PAGE_H = PAGE_W * 16 / 9   # 26.67 cm

# ── 配色 ──────────────────────────────────────────────────────────────────
DARK_BG  = HexColor("#0d1117")
BG2      = HexColor("#161b22")
ACCENT   = HexColor("#58a6ff")
ACCENT2  = HexColor("#1f6feb")
GRAY     = HexColor("#8b949e")
LGRAY    = HexColor("#c9d1d9")
WHITE    = white
GREEN    = HexColor("#3fb950")
ORANGE   = HexColor("#d29922")
RED      = HexColor("#f85149")
PURPLE   = HexColor("#bc8cff")

# ── 字体 ──────────────────────────────────────────────────────────────────
F_BOLD   = 'SimHei'
F_REG    = 'SimHei'
F_MONO   = 'Courier'

# ── 布局常量 ──────────────────────────────────────────────────────────────
M_L = 1.0 * cm
M_R = 1.0 * cm
M_T = 1.2 * cm
M_B = 1.0 * cm
CONTENT_W = PAGE_W - M_L - M_R
CONTENT_H = PAGE_H - M_T - M_B

# 行高基础
LB = 1.62   # body line height multiplier
BODY_FS  = 11    # body font size pt
BODY_LH  = BODY_FS * LB
H2_FS    = 13
H3_FS    = 11.5
SMALL_FS = 9

IMG_OUT = r"D:/02-Projects/vibe/docs/skill-runtime-tiktok"
PDF_OUT = r"D:/02-Projects/vibe/docs/skill-runtime-tiktok.pdf"
os.makedirs(IMG_OUT, exist_ok=True)

# ── Canvas 包装 ────────────────────────────────────────────────────────────
class PageCanvas:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H))
        self.c.setTitle("Skill Runtime 项目报告")
        self.y = 0   # 当前 y 坐标（从顶部向下）

    def new_page(self):
        if self.y > 0:
            self.c.showPage()
        self.y = PAGE_H - M_T   # 从顶部开始

    def x(self, left=M_L): return left
    def right_x(self): return PAGE_W - M_R
    def avail_w(self): return self.right_x() - self.x()

    def text_w(self, text, font, size, max_w):
        """计算文字渲染宽度"""
        return self.c.stringWidth(text, font, size)

    def fill_rect(self, x, y, w, h, color):
        self.c.setFillColor(color)
        self.c.rect(x, y, w, h, fill=1, stroke=0)

    def fill_full(self, color):
        self.fill_rect(0, 0, PAGE_W, PAGE_H, color)

    def line(self, x1, y1, x2, y2, color, width=0.5):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x1, y1, x2, y2)

    def text(self, text, x, y, font, size, color=WHITE, align='left'):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        if align == 'center':
            w = self.c.stringWidth(text, font, size)
            x = (PAGE_W - w) / 2
        elif align == 'right':
            w = self.c.stringWidth(text, font, size)
            x = PAGE_W - M_R - w
        self.c.drawString(x, y, text)

    def wrapped_text(self, text, x, y, max_w, font, size, color=LGRAY,
                     line_height_mult=LB, indent=0, first_line_indent=None):
        """自动换行文本，y 是文字基线，返回使用后的 y"""
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        if first_line_indent is None:
            first_line_indent = indent
        words = text.replace('<b>', '').replace('</b>', '').replace('<br/>', ' | ').split(' ')
        # 简单换行
        lines = []
        current = ''
        for word in words:
            test = (current + ' ' + word).strip()
            if self.c.stringWidth(test, font, size) <= max_w - indent:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        lh = size * line_height_mult
        cy = y
        for i, line in enumerate(lines):
            ind = first_line_indent if i == 0 else indent
            self.c.drawString(x + ind, cy, line)
            cy -= lh
        return cy - lh  # 返回最后一行下方

    def badge_row(self, num, title, accent=ACCENT):
        """绘制章节 badge，返回下一个 y"""
        badge_h = 1.5 * cm
        badge_w = 3.2 * cm
        num_w   = 1.0 * cm
        gap     = 0.15 * cm

        # 左：深色背景数字
        self.fill_rect(M_L, self.y - badge_h, num_w, badge_h, accent)
        self.text('%02d' % num, M_L, self.y - badge_h * 0.65,
                  F_BOLD, 14, WHITE, 'center')

        # 中：浅色背景标题
        self.fill_rect(M_L + num_w + gap, self.y - badge_h,
                       badge_w - num_w - gap, badge_h, BG2)
        self.text(title, M_L + num_w + gap + 0.2*cm, self.y - badge_h * 0.62,
                  F_BOLD, 13, WHITE)

        # 右：填充线
        right_start = M_L + badge_w + gap
        self.fill_rect(right_start, self.y - badge_h,
                       PAGE_W - M_R - right_start, badge_h, BG2)

        self.y -= badge_h + 0.25 * cm
        return self.y

    def section_divider(self, color=ACCENT):
        """分隔线"""
        h = 0.05 * cm
        self.line(M_L, self.y, PAGE_W - M_R, self.y, color, 1)
        self.y -= h + 0.15 * cm

    def h2(self, text):
        """二级标题"""
        self.y -= 0.15 * cm
        self.text(text, M_L, self.y, F_BOLD, H2_FS, ACCENT)
        self.y -= H2_FS * 0.9

    def h3(self, text):
        """三级标题"""
        self.text(text, M_L, self.y, F_BOLD, H3_FS, LGRAY)
        self.y -= H3_FS * 1.0

    def body(self, text, indent=0, color=LGRAY, size=BODY_FS):
        """正文段落"""
        lh = size * LB
        # 简单手绘换行
        words = text.replace('<b>', '').replace('</b>', '').replace('<br/>', ' ').split(' ')
        lines = []
        cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if self.c.stringWidth(t, F_REG, size) <= self.avail_w() - indent:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for line in lines:
            self.c.setFont(F_REG, size)
            self.c.setFillColor(color)
            self.c.drawString(M_L + indent, self.y, line)
            self.y -= lh
        return self.y

    def bullet(self, text, marker='•', indent=0.5*cm, color=LGRAY):
        """项目符号"""
        self.text(marker, M_L + indent, self.y, F_REG, size=BODY_FS, color=ACCENT)
        return self.body(text, indent=indent + 0.35*cm, color=color)

    def code_block(self, lines, max_h=None):
        """代码块，lines 为字符串列表"""
        lh = SMALL_FS * 1.5
        total_h = len(lines) * lh + 0.4*cm
        x0 = M_L
        y0 = self.y - 0.2*cm
        self.fill_rect(x0, y0 - total_h, self.avail_w(), total_h, BG2)
        self.line(x0, y0, x0 + self.avail_w(), y0, ACCENT2, 1.5)
        self.c.setFont(F_MONO, SMALL_FS)
        self.c.setFillColor(GREEN)
        for i, ln in enumerate(lines[:int(max_h/lh) if max_h else len(lines)]):
            self.c.drawString(x0 + 0.2*cm, y0 - 0.25*cm - i * lh, ln[:90])
        self.y -= total_h + 0.2*cm
        return self.y

    def highlight_bar(self, text, color=DARK_BG):
        """高亮信息条"""
        h = 1.1 * cm
        self.fill_rect(M_L, self.y - h, self.avail_w(), h, ACCENT)
        self.c.setFont(F_BOLD, 11)
        self.c.setFillColor(WHITE)
        w = self.c.stringWidth(text, F_BOLD, 11)
        self.c.drawString((PAGE_W - w) / 2, self.y - h * 0.62, text)
        self.y -= h + 0.15 * cm

    def two_col(self, left_items, right_items):
        """两列布局，每项为 (text, is_bold, color)"""
        col_w = (self.avail_w() - 0.3*cm) / 2
        lh = BODY_FS * LB * 1.1
        n = max(len(left_items), len(right_items))
        for i in range(n):
            li = left_items[i] if i < len(left_items) else ('', False, LGRAY)
            ri = right_items[i] if i < len(right_items) else ('', False, LGRAY)
            self.text(li[0], M_L, self.y, F_BOLD if li[1] else F_REG,
                      BODY_FS, li[2])
            self.text(ri[0], M_L + col_w + 0.3*cm, self.y,
                      F_BOLD if ri[1] else F_REG, BODY_FS, ri[2])
            self.y -= lh
        return self.y

    def save_page(self):
        # 只结束当前页，不调用 save()（save 只在全部完成后调用一次）
        self.c.showPage()

# ── 生成 PDF ───────────────────────────────────────────────────────────────
c = PageCanvas(PDF_OUT)

# ═══════════════════════════════════════════════════════════════════════════
# 封面
# ═══════════════════════════════════════════════════════════════════════════
c.new_page()
c.fill_full(DARK_BG)

# 顶部装饰条
c.fill_rect(0, PAGE_H - 0.12*cm, PAGE_W, 0.12*cm, ACCENT)

# 左侧装饰竖条
c.fill_rect(0, 0, 0.08*cm, PAGE_H, ACCENT2)

# 右下角装饰圆
c.c.setFillColor(HexColor("#21262d"))
c.c.circle(PAGE_W + 2*cm, -2*cm, 6*cm, fill=1, stroke=0)

# 主标题
c.text('Skill Runtime', PAGE_W/2, PAGE_H * 0.72,
       F_BOLD, 42, ACCENT, 'center')
c.text('项目详细报告', PAGE_W/2, PAGE_H * 0.72 - 2.4*cm,
       F_BOLD, 26, WHITE, 'center')

# 分隔线
c.line(PAGE_W*0.2, PAGE_H*0.6, PAGE_W*0.8, PAGE_H*0.6, ACCENT, 1.5)

# 副标题
c.text('面向宿主 AI 的本地可演化技能运行时与治理系统',
       PAGE_W/2, PAGE_H*0.55, F_REG, 13, GRAY, 'center')

# 标签
tags = ['可治理', '可审计', '可复用', '可解释']
tag_y = PAGE_H * 0.45
tag_w = 2.4*cm
gap = 0.4*cm
total = len(tags) * tag_w + (len(tags)-1) * gap
start_x = (PAGE_W - total) / 2
for i, tag in enumerate(tags):
    tx = start_x + i * (tag_w + gap)
    c.fill_rect(tx, tag_y - 0.55*cm, tag_w, 0.55*cm, BG2)
    c.c.setFont(F_BOLD, 10)
    tw = c.c.stringWidth(tag, F_BOLD, 10)
    c.c.drawString(tx + (tag_w - tw)/2, tag_y - 0.35*cm, tag)

# 底部信息
c.text('v1.0  |  2026', PAGE_W/2, PAGE_H*0.1,
       F_REG, 10, GRAY, 'center')
# 底部装饰条
c.fill_rect(0, 0, PAGE_W, 0.06*cm, ACCENT2)

c.save_page()
print("封面完成")

# ═══════════════════════════════════════════════════════════════════════════
# 通用页脚
# ═══════════════════════════════════════════════════════════════════════════
def add_footer(c, page_num, accent=ACCENT):
    c.line(M_L, M_B - 0.1*cm, PAGE_W - M_R, M_B - 0.1*cm, HexColor("#30363d"), 0.5)
    c.text(f'{page_num}', PAGE_W/2, M_B - 0.5*cm, F_REG, 8, GRAY, 'center')
    c.text('Skill Runtime 项目报告', M_L, M_B - 0.5*cm, F_REG, 8, GRAY)

# ═══════════════════════════════════════════════════════════════════════════
# 章节 1：项目概述
# ═══════════════════════════════════════════════════════════════════════════
def make_section1():
    c.new_page()
    # 顶部渐变条
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)

    c.y -= 0.2*cm
    c.badge_row(1, '项目概述')

    c.body('本项目实现了一套面向 Codex 的本地 skill runtime，目标不是再做一个新的 AI 助手，'
           '而是给宿主 AI 加一层「技能运行时与治理内核」。')

    c.y -= 0.1*cm
    c.h2('核心定位')
    c.bullet('AI 做过的工作流能不能沉淀下来')
    c.bullet('沉淀下来的技能能不能被检查、治理和复用')
    c.bullet('宿主 AI 下次遇到类似任务时，能不能先复用已有技能，而不是从头再做')

    c.y -= 0.15*cm
    c.h2('是 vs 不是')

    # 画对比表格
    row_h = 1.05 * cm
    col_w = (CONTENT_W - 0.15*cm) / 2

    def draw_compare_row(y, label, items, label_color, item_color):
        c.fill_rect(M_L, y - row_h, col_w * 0.55, row_h, label_color)
        c.c.setFont(F_BOLD, 10)
        c.c.setFillColor(WHITE)
        c.c.drawString(M_L + 0.15*cm, y - row_h * 0.65, label)
        c.fill_rect(M_L + col_w * 0.55 + 0.15*cm, y - row_h, col_w * 0.45, row_h, BG2)
        c.c.setFont(F_REG, 9)
        c.c.setFillColor(item_color)
        c.c.drawString(M_L + col_w * 0.55 + 0.25*cm, y - row_h * 0.65, items)
        return y - row_h

    y = c.y
    y = draw_compare_row(y, '✗ 不是', '独立 AI 产品 / 新聊天界面 / 另一个 agent', RED, LGRAY)
    y = draw_compare_row(y, '✓ 而是', 'AI 应用内部的能力层 / skill governance kernel', GREEN, LGRAY)
    y = draw_compare_row(y, '≈ 更接近', 'skill runtime / workflow memory / host-AI capability layer', ORANGE, LGRAY)
    c.y = y - 0.1*cm

    c.h2('完整闭环')
    闭环_items = ['Search', 'Execute', 'Distill', 'Audit', 'Promote', 'Reuse']
    box_w = (CONTENT_W - 0.2*cm * (len(闭环_items)-1)) / len(闭环_items)
    box_h = 1.1 * cm
    bx = M_L
    for i, item in enumerate(闭环_items):
        color = ACCENT2 if i < len(闭环_items)-1 else GREEN
        c.fill_rect(bx, c.y - box_h, box_w, box_h, color)
        c.text(item, bx + box_w/2, c.y - box_h * 0.38, F_BOLD, 9.5, WHITE, 'center')
        if i < len(闭环_items)-1:
            c.text('→', bx + box_w, c.y - box_h * 0.55, F_BOLD, 12, GRAY)
        bx += box_w + 0.2*cm
    c.y -= box_h + 0.1*cm

    add_footer(c, 1)
    c.save_page()
    print("章节 1 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 2：核心问题
# ═══════════════════════════════════════════════════════════════════════════
def make_section2():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(2, '核心问题')
    c.body('2.1 传统 AI 工作流的缺陷')

    defects = [
        ('重复任务反复从头规划', '即使某类任务已经做过，下一次仍然会重新分析、重新写流程。'),
        ('能做任务，但不能有效沉淀', '任务完成后，过程往往只留在聊天上下文里，没有转化为结构化能力。'),
        ('技能复用缺乏治理', '有些系统会积累技能，但缺少审计、入库、生命周期管理等治理层能力。'),
        ('宿主 AI 和技能系统耦合不清', '很多方案演化成再套一个 AI 或外部 agent 控制宿主 agent，架构复杂。'),
    ]

    for i, (t, d) in enumerate(defects, 1):
        # 序号圆点
        r = 0.22*cm
        cx_circle = M_L + r + 0.05*cm
        cy_circle = c.y - r
        c.c.setFillColor(RED)
        c.c.circle(cx_circle, cy_circle, r, fill=1, stroke=0)
        c.text(str(i), cx_circle, cy_circle - 0.15*cm, F_BOLD, 9, WHITE, 'center')

        c.c.setFont(F_BOLD, BODY_FS)
        c.c.setFillColor(WHITE)
        c.c.drawString(M_L + r*2 + 0.2*cm, c.y + 0.05*cm, t)

        c.y -= 0.55*cm
        c.body(d, indent=0.5*cm, color=GRAY, size=10)
        c.y -= 0.15*cm

    c.y -= 0.15*cm
    c.h2('2.2 本项目的判断')
    c.body('未来这类系统最合理的形态，不是独立 AI，而是作为现有 AI 应用内部的一层能力内核存在。')
    c.y -= 0.05*cm
    c.bullet('宿主 AI 负责理解任务、和用户交互、做最终决策', marker='➊', color=ACCENT)
    c.bullet('skill runtime 负责技能检索、执行、蒸馏、审计、入库和复用', marker='➋', color=ACCENT)
    c.y -= 0.1*cm
    c.body('这也是为什么项目最终选择用 MCP 把 runtime 暴露给 Codex，而不是把它做成独立聊天程序。',
           color=GRAY, size=10)

    add_footer(c, 2)
    c.save_page()
    print("章节 2 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 3：设计原则
# ═══════════════════════════════════════════════════════════════════════════
def make_section3():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(3, '设计原则')

    c.body('本项目的准确含义：', color=GRAY, size=10)
    c.y += 0.05*cm
    c.c.setFont(F_BOLD, 14)
    c.c.setFillColor(ACCENT)
    t = '一套面向宿主 AI 的、本地可演化的技能运行时与治理系统'
    tw = c.c.stringWidth(t, F_BOLD, 14)
    c.c.drawString((PAGE_W - tw)/2, c.y, t)
    c.y -= 1.2*cm

    principles = [
        ('P1 宿主优先', '宿主 AI 是上层入口。skill runtime 不抢用户交互，不伪装成第二个 AI。'),
        ('P2 先复用，再生成', '面对任务，优先检索已有 skill；只有没命中时，才考虑新生成。'),
        ('P3 生成必须可治理', '新 skill 不能直接入库，必须进入 staging，并通过审计后再 promote。'),
        ('P4 结构优先于智能', '第一阶段先做稳固闭环和可解释结构，不急着一上来全靠 LLM 生成。'),
        ('P5 能力层而非产品壳', '对外优先暴露 CLI、MCP tools、技能包装层，而不是新的 UI。'),
        ('P6 可解释性很重要', 'skill 被检索、生成和复用时，要尽量知道：为什么命中、来自哪条规则。'),
    ]

    for i, (pt, pd) in enumerate(principles):
        # P 条
        ph = 1.0 * cm
        p_colors = [ACCENT2, ACCENT, HexColor("#238636"), ORANGE, PURPLE, HexColor("#9e6a03")]
        pc = p_colors[i % len(p_colors)]

        c.fill_rect(M_L, c.y - ph, 1.1*cm, ph, pc)
        c.text(pt[:2], M_L, c.y - ph * 0.65, F_BOLD, 9, WHITE, 'center')
        c.fill_rect(M_L + 1.1*cm + 0.15*cm, c.y - ph,
                    CONTENT_W - 1.1*cm - 0.15*cm, ph, BG2)
        c.text(pt[3:], M_L + 1.1*cm + 0.25*cm, c.y - ph * 0.65,
               F_BOLD, BODY_FS, WHITE)
        c.y -= ph + 0.08*cm

        # 说明
        c.body(pd, indent=0.2*cm, color=GRAY, size=10)
        c.y -= 0.15*cm

    add_footer(c, 3)
    c.save_page()
    print("章节 3 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 4：系统架构
# ═══════════════════════════════════════════════════════════════════════════
def make_section4():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(4, '系统架构')

    c.h2('四层架构')
    layers = [
        ('0', 'Host AI 层', '当前宿主是 Codex。负责接收用户任务、理解需求、规划整体动作、决定何时调用 runtime。', ACCENT2),
        ('1', 'Adapter 层', '当前实现了 CLI 和 MCP server 两个适配层，其中 MCP 是与 Codex 集成的主方式。', ACCENT),
        ('2', 'Skill Runtime 层', '项目核心：trajectory 存储、skill 蒸馏、skill 审计、promote 守卫、skill 检索、skill 执行、provenance 回填。', HexColor("#238636")),
        ('3', 'Storage / Governance 层', '底层以本地文件为主，包含 skill_store（staging/active/archive/rejected）、trajectories、audits、index.json。', ORANGE),
    ]

    for num, name, desc, color in layers:
        lh_px = 1.5 * cm
        # 层次条
        c.fill_rect(M_L, c.y - lh_px, 0.6*cm, lh_px, color)
        c.text(num, M_L, c.y - lh_px * 0.65, F_BOLD, 16, WHITE, 'center')
        # 内容
        c.fill_rect(M_L + 0.6*cm + 0.15*cm, c.y - lh_px,
                    CONTENT_W - 0.6*cm - 0.15*cm, lh_px, BG2)
        c.text(name, M_L + 0.6*cm + 0.25*cm, c.y - 0.45*cm, F_BOLD, 11.5, color)
        c.y -= 0.5*cm
        c.body(desc, indent=0.6*cm + 0.25*cm, color=GRAY, size=10)
        c.y -= 0.2*cm

    c.y -= 0.1*cm
    c.h2('与 Codex 的集成')
    c.body('MCP (Model Context Protocol) 是 Skill Runtime 暴露给 Codex 的主要方式。'
           'Codex 通过 MCP tools 触发 runtime 的各项能力，无需改变宿主 AI 的核心架构。',
           color=GRAY, size=10)

    add_footer(c, 4)
    c.save_page()
    print("章节 4 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 5：目录结构
# ═══════════════════════════════════════════════════════════════════════════
def make_section5():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(5, '目录结构')

    code_lines = [
        'scripts/',
        '  skill_cli.py        # CLI 入口',
        '  skill_mcp_server.py # MCP 服务',
        '',
        'skill_runtime/',
        '  api/        # RuntimeService 业务层',
        '  memory/     # trajectory 存取与校验',
        '  distill/    # 从 trajectory 生成 skill',
        '  audit/      # skill 审计（静态+语义）',
        '  retrieval/  # 技能索引与检索',
        '  execution/  # 工具注入与 skill 执行',
        '  governance/ # promote guard、provenance',
        '',
        'skill_store/',
        '  staging/  active/  archive/  rejected/',
        '  index.json',
        '',
        'trajectories/  audits/  demo/  tests/',
    ]
    c.code_block(code_lines)

    c.h2('模块职责')
    mods = [
        ('api/', 'RuntimeService 业务层，CLI 和 MCP 统一调用'),
        ('memory/', 'trajectory 存取、校验，为 distill/audit 提供上下文'),
        ('distill/', '从成功 trajectory 生成 skill，规则蒸馏 + LLM fallback'),
        ('audit/', '规则检查（安全/隐私/命名）+ 语义评分，阻止低质量入库'),
        ('retrieval/', '关键词 + embedding 混合检索，sematic cache 加速'),
        ('execution/', 'skill 参数注入 + 环境准备 + 结果回填'),
        ('governance/', 'promote guard 守卫 + provenance 链路记录'),
    ]
    for m, d in mods:
        c.c.setFont(F_BOLD, BODY_FS)
        c.c.setFillColor(ACCENT)
        c.c.drawString(M_L, c.y, m)
        w = c.c.stringWidth(m, F_BOLD, BODY_FS)
        c.c.setFont(F_REG, BODY_FS)
        c.c.setFillColor(LGRAY)
        c.c.drawString(M_L + w + 0.1*cm, c.y, d)
        c.y -= BODY_FS * LB

    add_footer(c, 5)
    c.save_page()
    print("章节 5 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 6：核心数据模型
# ═══════════════════════════════════════════════════════════════════════════
def make_section6():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(6, '数据模型')

    models = [
        ('Trajectory', 'Skill Runtime 的核心输入单位，记录一次完整的 task 执行过程，包含多个 Step 和最终结果。'),
        ('Skill', '从 Trajectory 提炼出的可复用能力单元，包含 metadata、instruction、tools、trigger 等字段。'),
        ('SkillRecord', 'Skill 的存储实体，通过 status 字段区分 staging/active/archive/rejected 四个生命周期状态。'),
        ('AuditRecord', 'Skill 进入 active 前的审查记录，包含规则检查结果、语义评分和人工复核意见。'),
        ('ProvenanceRecord', 'skill 的来源链路，标注 skill 由哪个 trajectory 蒸馏、经过哪些审计规则。'),
    ]

    for name, desc in models:
        mh = 1.2 * cm
        nw = 2.8 * cm
        c.fill_rect(M_L, c.y - mh, nw, mh, ACCENT2)
        c.c.setFont(F_BOLD, 10)
        c.c.setFillColor(WHITE)
        tw = c.c.stringWidth(name, F_BOLD, 10)
        c.c.drawString(M_L + (nw - tw)/2, c.y - mh * 0.65, name)

        c.fill_rect(M_L + nw + 0.15*cm, c.y - mh,
                     CONTENT_W - nw - 0.15*cm, mh, BG2)
        # 分隔线
        c.line(M_L + nw + 0.15*cm, c.y - 0.15*cm,
               M_L + nw + 0.15*cm, c.y - mh + 0.15*cm, ACCENT2, 1)
        c.body(desc, indent=0.2*cm, color=LGRAY, size=10)
        c.y -= mh + 0.12*cm

    add_footer(c, 6)
    c.save_page()
    print("章节 6 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 7：主闭环
# ═══════════════════════════════════════════════════════════════════════════
def make_section7():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(7, '主闭环')

    c.body('RuntimeService 是整个 runtime 的核心 API 入口，提供同步和异步两套接口，'
           '通过 ExecutorAdapter 支持多种执行后端。')

    steps = [
        ('Search', '根据当前 task 描述检索已有 skills，命中则直接复用', ACCENT2),
        ('Execute', '命中的 skill 被加载、执行，结果写入 trajectory', ACCENT),
        ('Distill', '从 trajectory 提炼新的 skill，放入 staging 区', HexColor("#238636")),
        ('Audit', 'staging 中的 skill 接受规则检查和语义评分', ORANGE),
        ('Promote', '通过审计的 skill 被 promote 到 active 区', PURPLE),
        ('Reuse', 'active skill 可被后续 task 复用，形成闭环', HexColor("#9e6a03")),
    ]

    step_h = 1.1 * cm
    step_w = (CONTENT_W - 0.15*cm * (len(steps)-1)) / len(steps)

    for i, (name, desc, color) in enumerate(steps):
        sx = M_L + i * (step_w + 0.15*cm)
        c.fill_rect(sx, c.y - step_h, step_w, step_h, color)
        # 序号
        c.text(str(i+1), sx + step_w/2, c.y - 0.25*cm, F_BOLD, 9, WHITE, 'center')
        c.text(name, sx + step_w/2, c.y - step_h * 0.55, F_BOLD, 9, WHITE, 'center')
        # 箭头
        if i < len(steps)-1:
            c.text('→', sx + step_w, c.y - step_h * 0.5, F_BOLD, 13, GRAY)
        # 下方说明
        c.y -= step_h
        c.c.setFont(F_REG, 9)
        c.c.setFillColor(GRAY)
        # 换行处理
        words = desc
        # 简单截断或换行
        ln1 = desc[:12] + ('...' if len(desc) > 12 else '')
        ln2 = desc[12:24] + ('...' if len(desc) > 24 else '')
        c.c.drawString(sx, c.y, ln1)
        if ln2:
            c.y -= 11
            c.c.drawString(sx, c.y, ln2)
        c.y -= 0.3*cm

    add_footer(c, 7)
    c.save_page()
    print("章节 7 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 8：Distillation
# ═══════════════════════════════════════════════════════════════════════════
def make_section8():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(8, 'Distillation')

    c.h2('工作原理')
    c.body('Distillation Pipeline 从成功执行的 Trajectory 中提取可复用的 Skill。'
           '项目采用两阶段策略：')

    stages = [
        ('阶段一', '规则蒸馏（Rule-based）', '通过结构化分析 trajectory 的 action 序列，提取可复用的 action 模式和参数模板。'
         '无需 LLM 调用，速度快，适合结构化强的任务。', ACCENT2),
        ('阶段二', '语义蒸馏（LLM-assisted）', '当规则蒸馏结果不足以生成完整 skill 时，调用 LLM 补全 instruction、'
         'trigger、description 等语义字段。LLM 作为 fallback，而非默认路径。', HexColor("#238636")),
    ]

    for stage, name, desc, color in stages:
        sh = 1.5 * cm
        c.fill_rect(M_L, c.y - sh, 1.5*cm, sh, color)
        c.text(stage, M_L, c.y - sh * 0.55, F_BOLD, 9, WHITE, 'center')
        c.c.setFont(F_BOLD, 11)
        c.c.setFillColor(color)
        c.c.drawString(M_L + 1.65*cm, c.y - 0.45*cm, name)
        c.y -= 0.5*cm
        c.body(desc, indent=1.65*cm, color=GRAY, size=10)
        c.y -= 0.2*cm

    c.h2('DistillConfig 配置项')
    config_items = [
        ('min_trajectory_steps', '最少 step 数才触发蒸馏，防止过短的 trajectory 被处理', '3'),
        ('success_only', '是否只蒸馏成功的 trajectory', 'True'),
        ('dedup_similarity', '与已有 skill 的最大相似度阈值，超过则跳过', '0.85'),
        ('llm_fallback', '规则结果不足时是否调用 LLM', 'True'),
    ]
    for k, d, v in config_items:
        c.c.setFont(F_MONO, 9)
        c.c.setFillColor(PURPLE)
        c.c.drawString(M_L, c.y, k)
        kw = c.c.stringWidth(k, F_MONO, 9)
        c.c.setFont(F_REG, 9)
        c.c.setFillColor(GRAY)
        c.c.drawString(M_L + kw + 0.1*cm, c.y, d)
        vw = c.c.stringWidth('= ' + v, F_MONO, 9)
        c.c.setFont(F_MONO, 9)
        c.c.setFillColor(GREEN)
        c.c.drawString(PAGE_W - M_R - vw, c.y, '= ' + v)
        c.y -= SMALL_FS * 1.4

    add_footer(c, 8)
    c.save_page()
    print("章节 8 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 9：Audit
# ═══════════════════════════════════════════════════════════════════════════
def make_section9():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(9, 'Audit')

    c.h2('两层审计机制')
    c.body('Audit 阶段在 skill 进入 active 之前进行质量把关，采用两层审计：')

    audits = [
        ('规则审计', 'Rule-based Audit', [
            'skill 命名是否合法（禁止同名覆盖）',
            '文件路径是否安全（禁止路径穿越）',
            '是否包含敏感信息（API key / token 检查）',
            '描述是否与指令一致',
        ], ACCENT2),
        ('语义审计', 'LLM-assisted Audit', [
            'skill 是否具有实际价值（非重复模板）',
            '触发条件是否清晰可区分',
            '指令是否可执行（不依赖缺失工具）',
        ], HexColor("#238636")),
    ]

    for name, sub, items, color in audits:
        ah = len(items) * BODY_FS * LB * 1.1 + 0.8*cm
        c.fill_rect(M_L, c.y - ah, CONTENT_W, ah, BG2)
        c.fill_rect(M_L, c.y - ah, 0.06*cm, ah, color)

        c.c.setFont(F_BOLD, 11)
        c.c.setFillColor(color)
        c.c.drawString(M_L + 0.2*cm, c.y - 0.35*cm, name)
        c.c.setFont(F_REG, 9)
        c.c.setFillColor(GRAY)
        c.c.drawString(M_L + 0.2*cm + c.c.stringWidth(name+' ', F_BOLD, 11),
                       c.y - 0.35*cm, sub)
        yi = c.y - 0.65*cm
        for item in items:
            c.c.setFont(F_REG, 10)
            c.c.setFillColor(LGRAY)
            c.c.drawString(M_L + 0.35*cm, yi, '• ' + item)
            yi -= BODY_FS * LB * 1.1
        c.y -= ah + 0.15*cm

    c.h2('审计结果处理')
    results = [
        ('PASS', 'skill 进入 active 区，可被检索和复用', GREEN),
        ('WARN', 'skill 进入 active 区，但记录警告，供后续复查', ORANGE),
        ('FAIL', 'skill 拒绝进入 active 区，记录原因，可修改后重新提交', RED),
    ]
    rh = 0.85 * cm
    rw = (CONTENT_W - 0.2*cm * (len(results)-1)) / len(results)
    rx = M_L
    for res, desc, color in results:
        c.fill_rect(rx, c.y - rh, rw, rh, BG2)
        c.fill_rect(rx, c.y - rh, rw, 0.08*cm, color)
        c.c.setFont(F_BOLD, 11)
        c.c.setFillColor(color)
        tw = c.c.stringWidth(res, F_BOLD, 11)
        c.c.drawString(rx + (rw - tw)/2, c.y - 0.38*cm, res)
        c.c.setFont(F_REG, 8.5)
        c.c.setFillColor(GRAY)
        words = desc
        ln1 = desc[:16]
        ln2 = desc[16:] if len(desc) > 16 else ''
        c.c.drawString(rx + 0.15*cm, c.y - rh + 0.35*cm, ln1)
        if ln2:
            c.c.drawString(rx + 0.15*cm, c.y - rh + 0.55*cm, ln2)
        rx += rw + 0.2*cm
    c.y -= rh + 0.1*cm

    add_footer(c, 9)
    c.save_page()
    print("章节 9 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 10：Retrieval
# ═══════════════════════════════════════════════════════════════════════════
def make_section10():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(10, 'Retrieval')

    c.h2('混合检索策略')
    c.body('Retrieval 模块采用关键词 + embedding 的混合策略，兼顾精确匹配和语义理解：')

    strategies = [
        ('关键词检索', '基于 BM25，对 skill 的 trigger 和 description 建倒排索引，适合精确术语匹配。'),
        ('向量检索', '基于 embedding 模型，将 task 描述和 skill 文档映射到向量空间，'
         '通过余弦相似度找语义相近的 skills。'),
        ('Semantic Cache', '对高频相同 task 描述的检索结果进行缓存，命中则直接返回，'
         '避免重复向量计算。'),
    ]

    for name, desc in strategies:
        c.c.setFont(F_BOLD, BODY_FS)
        c.c.setFillColor(ACCENT)
        c.c.drawString(M_L, c.y, '▸ ' + name)
        c.y -= BODY_FS * 1.1
        c.body(desc, indent=0.3*cm, color=GRAY, size=10)
        c.y -= 0.1*cm

    c.h2('检索流程')
    flow = ['task 描述', '→ 关键词候选', '→ 向量重排', '→ Top-K', '→ Skill 返回']
    fh = 0.9 * cm
    fw = (CONTENT_W - 0.15*cm * (len(flow)-1)) / len(flow)
    fx = M_L
    for i, step in enumerate(flow):
        fc = ACCENT2 if i < len(flow)-1 else GREEN
        c.fill_rect(fx, c.y - fh, fw, fh, fc)
        c.text(step, fx + fw/2, c.y - fh * 0.62, F_REG, 8, WHITE, 'center')
        if i < len(flow)-1:
            c.text('→', fx + fw, c.y - fh * 0.5, F_BOLD, 12, GRAY)
        fx += fw + 0.15*cm
    c.y -= fh + 0.15*cm

    c.h2('RetrievalConfig 关键参数')
    params = [('top_k', '返回的最相似 skill 数量', '3'), ('score_threshold', '最低相似度阈值', '0.72'),
              ('rerank_model', '重排使用的 embedding 模型', 'BAAI/bge-m3')]
    for k, d, v in params:
        c.c.setFont(F_MONO, 9); c.c.setFillColor(PURPLE); c.c.drawString(M_L, c.y, k)
        kw = c.c.stringWidth(k, F_MONO, 9)
        c.c.setFont(F_REG, 9); c.c.setFillColor(GRAY); c.c.drawString(M_L + kw + 0.1*cm, c.y, d)
        vw = c.c.stringWidth('= ' + v, F_MONO, 9)
        c.c.setFont(F_MONO, 9); c.c.setFillColor(GREEN)
        c.c.drawString(PAGE_W - M_R - vw, c.y, '= ' + v)
        c.y -= SMALL_FS * 1.4

    add_footer(c, 10)
    c.save_page()
    print("章节 10 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 11：Execution
# ═══════════════════════════════════════════════════════════════════════════
def make_section11():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(11, 'Execution')

    c.h2('执行流程')
    exec_steps = [
        ('参数注入', '将当前 task 的输入参数替换到 skill 的模板占位符中'),
        ('环境准备', '检查 skill 依赖的工具、文件、环境变量是否满足'),
        ('执行', '通过选定的执行后端（CLI / MCP / Python）运行 skill'),
        ('结果捕获', '收集 stdout/stderr、返回码、运行时长等元数据'),
        ('回填', '将执行结果写入 trajectory，形成完整的闭环记录'),
    ]

    eh = 0.95 * cm
    ew = (CONTENT_W) / 1
    # 垂直步骤列表
    for i, (name, desc) in enumerate(exec_steps):
        # 序号
        c.c.setFillColor(ACCENT2)
        c.c.circle(M_L + 0.25*cm, c.y - 0.3*cm, 0.22*cm, fill=1, stroke=0)
        c.text(str(i+1), M_L + 0.25*cm, c.y - 0.38*cm, F_BOLD, 9, WHITE, 'center')
        # 竖线连接
        if i < len(exec_steps)-1:
            c.line(M_L + 0.25*cm, c.y - 0.48*cm, M_L + 0.25*cm, c.y - eh + 0.1*cm,
                   ACCENT2, 1.5)
        # 内容
        c.c.setFont(F_BOLD, BODY_FS)
        c.c.setFillColor(WHITE)
        c.c.drawString(M_L + 0.6*cm, c.y - 0.3*cm, name)
        c.y -= 0.38*cm
        c.body(desc, indent=0.6*cm, color=GRAY, size=10)
        c.y -= eh - 0.6*cm

    c.y -= 0.1*cm
    c.h2('执行后端支持')
    backends = ['CLI (subprocess)', 'MCP (via mcp-client)', 'Python (inline exec)']
    bw = (CONTENT_W - 0.2*cm * (len(backends)-1)) / len(backends)
    bx = M_L
    for be in backends:
        c.fill_rect(bx, c.y - 0.8*cm, bw, 0.8*cm, BG2)
        c.fill_rect(bx, c.y - 0.8*cm, bw, 0.06*cm, ACCENT)
        c.text(be, bx + bw/2, c.y - 0.8*cm * 0.62, F_REG, 9, LGRAY, 'center')
        bx += bw + 0.2*cm
    c.y -= 1.0*cm

    add_footer(c, 11)
    c.save_page()
    print("章节 11 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 12：MCP 集成
# ═══════════════════════════════════════════════════════════════════════════
def make_section12():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(12, 'MCP 集成')

    c.h2('MCP Server 架构')
    c.body('skill_mcp_server.py 将 Skill Runtime 的核心能力通过 MCP 协议暴露给 Codex，'
           '使宿主 AI 能够以标准工具调用的方式使用 runtime。')

    mcplines = [
        '# MCP Server 入口 (简化)',
        'from skill_runtime.api import RuntimeService',
        '',
        'class SkillRuntimeMCPServer:',
        '    def __init__(self):',
        '        self.runtime = RuntimeService()',
        '    def get_tools(self):',
        '        return [',
        '            Tool(name="skill_search",',
        '                 handler=self.runtime.search),',
        '            Tool(name="skill_execute",',
        '                 handler=self.runtime.execute),',
        '            Tool(name="skill_distill",',
        '                 handler=self.runtime.distill),',
        '            Tool(name="skill_audit",',
        '                 handler=self.runtime.audit),',
        '        ]',
    ]
    c.code_block(mcplines, max_h=6*cm)

    c.h2('MCP 工具列表')
    tools = [
        ('skill_search', '检索已有 skills', 'task 描述 → Top-K skills'),
        ('skill_execute', '执行命中的 skill', 'skill_id + 参数 → 执行结果'),
        ('skill_distill', '从 trajectory 蒸馏新 skill', 'trajectory_id → skill (staging)'),
        ('skill_audit', '触发审计流程', 'skill_id → PASS/WARN/FAIL'),
        ('skill_promote', '将 skill 升为 active', 'skill_id → active 区'),
    ]
    for name, desc, io in tools:
        c.fill_rect(M_L, c.y - 0.75*cm, 2.8*cm, 0.75*cm, BG2)
        c.fill_rect(M_L, c.y - 0.75*cm, 0.06*cm, 0.75*cm, ACCENT2)
        c.c.setFont(F_MONO, 9); c.c.setFillColor(ACCENT); c.c.drawString(M_L+0.15*cm, c.y - 0.45*cm, name)
        c.fill_rect(M_L + 2.8*cm + 0.15*cm, c.y - 0.75*cm, CONTENT_W - 2.8*cm - 0.15*cm, 0.75*cm, HexColor("#1c2128"))
        c.c.setFont(F_REG, 9); c.c.setFillColor(LGRAY); c.c.drawString(M_L + 2.95*cm, c.y - 0.35*cm, desc)
        c.c.setFont(F_REG, 8); c.c.setFillColor(GRAY); c.c.drawString(M_L + 2.95*cm, c.y - 0.6*cm, io)
        c.y -= 0.75*cm + 0.08*cm

    add_footer(c, 12)
    c.save_page()
    print("章节 12 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 13：Provenance
# ═══════════════════════════════════════════════════════════════════════════
def make_section13():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(13, 'Provenance')

    c.h2('Provenance 链路设计')
    c.body('ProvenanceRecord 记录每个 skill 的完整血缘关系，确保所有被复用的能力都有据可查。')

    fields = [
        ('skill_id', 'string', '该 provenance record 对应的 skill ID'),
        ('trajectory_id', 'string', '生成该 skill 的原始 trajectory ID'),
        ('distill_method', 'enum', '蒸馏方式：rule_based | llm_fallback | hybrid'),
        ('audit_results', 'list', '经过的各条审计规则的名称和结果'),
        ('promoted_by', 'string', '触发 promote 操作的操作者标识'),
        ('promote_time', 'datetime', 'promote 时间戳'),
        ('ancestor_skills', 'list', '如果该 skill 是从其他 skill 演化而来，记录祖先 skill'),
    ]

    fh = 0.78 * cm
    for fname, ftype, fdesc in fields:
        c.fill_rect(M_L, c.y - fh, 2.5*cm, fh, BG2)
        c.fill_rect(M_L, c.y - fh, 0.05*cm, fh, PURPLE)
        c.c.setFont(F_MONO, 9); c.c.setFillColor(PURPLE); c.c.drawString(M_L+0.15*cm, c.y - fh*0.6, fname)
        c.c.setFont(F_REG, 9); c.c.setFillColor(ORANGE); c.c.drawString(M_L+0.15*cm, c.y - fh*0.28, ftype)

        c.fill_rect(M_L + 2.5*cm + 0.1*cm, c.y - fh, CONTENT_W - 2.5*cm - 0.1*cm, fh, HexColor("#1c2128"))
        c.c.setFont(F_REG, 9); c.c.setFillColor(GRAY); c.c.drawString(M_L + 2.65*cm, c.y - fh*0.5, fdesc)
        c.y -= fh + 0.05*cm

    c.y -= 0.15*cm
    c.h2('治理价值')
    for v in ['审计回溯：任何 active skill 都可以追溯到原始 trajectory 和决策依据',
              '污染隔离：问题 skill 可通过 provenance 快速定位影响范围并回滚',
              '可信度评估：长期无问题的 skill 路径可获得更高的检索权重']:
        c.bullet(v)
        c.y -= 0.05*cm

    add_footer(c, 13)
    c.save_page()
    print("章节 13 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 14：CLI 使用
# ═══════════════════════════════════════════════════════════════════════════
def make_section14():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(14, 'CLI 使用')

    cmds = [
        ('skill search', '<task>', '根据任务描述检索 skills'),
        ('skill execute', '<skill-id> [--params JSON>]', '执行指定 skill'),
        ('skill distill', '<trajectory-id>', '从 trajectory 蒸馏新 skill'),
        ('skill audit', '<skill-id>', '触发指定 skill 的审计流程'),
        ('skill promote', '<skill-id>', '将 skill 升入 active 区'),
        ('skill list', '[--status staging|active|archive]', '列出所有 skills'),
        ('skill show', '<skill-id>', '查看 skill 详情'),
        ('trajectory list', '', '列出所有 trajectory'),
        ('trajectory show', '<trajectory-id>', '查看 trajectory 详情'),
    ]

    c.h2('命令参考')
    for cmd, args, desc in cmds:
        c.fill_rect(M_L, c.y - 0.75*cm, 3.5*cm, 0.75*cm, BG2)
        c.fill_rect(M_L, c.y - 0.75*cm, 0.05*cm, 0.75*cm, GREEN)
        c.c.setFont(F_MONO, 9); c.c.setFillColor(GREEN); c.c.drawString(M_L+0.15*cm, c.y - 0.45*cm, cmd)
        if args:
            c.c.setFont(F_MONO, 8); c.c.setFillColor(GRAY); c.c.drawString(M_L+0.15*cm, c.y - 0.65*cm, args[:25])

        c.fill_rect(M_L + 3.5*cm + 0.1*cm, c.y - 0.75*cm, CONTENT_W - 3.5*cm - 0.1*cm, 0.75*cm, HexColor("#1c2128"))
        c.c.setFont(F_REG, 9.5); c.c.setFillColor(LGRAY); c.c.drawString(M_L + 3.65*cm, c.y - 0.45*cm, desc)
        c.y -= 0.75*cm + 0.05*cm

    add_footer(c, 14)
    c.save_page()
    print("章节 14 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 15：差异化分析
# ═══════════════════════════════════════════════════════════════════════════
def make_section15():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(15, '差异化分析')

    comparisons = [
        ('特征', '传统 Agent', '传统 Memory', 'Skill Runtime'),
        ('能力沉淀', '✗ 无结构化沉淀', '△ 片段式存储', '✓ Trajectory → Skill'),
        ('治理能力', '✗ 无', '✗ 无', '✓ Audit + Provenance'),
        ('宿主集成', '△ 外部调用', '✗ 无', '✓ MCP 原生集成'),
        ('可解释性', '✗ 黑盒', '△ 模糊召回', '✓ 链路全记录'),
        ('闭环能力', '✗ 开环', '✗ 开环', '✓ Search → Reuse 闭环'),
    ]

    col_ws = [2.0*cm, 3.5*cm, 3.5*cm, 3.5*cm]
    row_h = 1.05 * cm

    y = c.y
    for ri, row in enumerate(comparisons):
        x = M_L
        for ci, cell in enumerate(row):
            cw = col_ws[ci] if ci < len(col_ws) else (CONTENT_W - sum(col_ws[:ci]))
            is_header = ri == 0
            bg = BG2 if not is_header else DARK_BG
            if ci == 3 and not is_header:
                bg = HexColor("#0d1f0d")  # 绿色底
            elif ci == 1 and not is_header:
                bg = HexColor("#1f0d0d")  # 红色底
            elif ci == 2 and not is_header:
                bg = HexColor("#1f1a0d")  # 黄色底

            c.fill_rect(x, y - row_h, cw, row_h, bg)
            c.line(x, y, x + cw, y, HexColor("#30363d"), 0.3)
            fc = WHITE if is_header else (GREEN if ci == 3 and not is_header
                 else (RED if ci == 1 and not is_header else LGRAY))
            c.c.setFont(F_BOLD if is_header else F_REG, 9.5)
            c.c.setFillColor(fc)
            c.c.drawString(x + 0.1*cm, y - row_h * 0.62, cell[:int(cw/0.22)])
            x += cw + 0.05*cm
        c.y -= row_h

    c.y -= 0.15*cm
    c.h2('定位优势')
    advs = ['与宿主 AI 深度集成，而非外部附加', '治理能力内建，不是事后补丁',
            '可解释性优先，不是黑盒堆积']
    for a in advs:
        c.bullet(a, marker='✓', color=GREEN)
        c.y -= 0.05*cm

    add_footer(c, 15)
    c.save_page()
    print("章节 15 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 16：当前局限
# ═══════════════════════════════════════════════════════════════════════════
def make_section16():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(16, '当前局限')

    limits = [
        ('R1 规模限制', '当前基于本地文件存储，适合个人或小团队场景；'
         '大规模多人协作场景需要引入向量数据库或图数据库。', RED),
        ('R2 LLM 依赖', 'Distillation 的 LLM fallback 和 Audit 的语义评分依赖外部 LLM API，'
         '在网络不可达或 API 不可用时能力降级。', ORANGE),
        ('R3 评测体系', '目前缺乏对 skill 实际复用率的量化评测指标，'
         '无法精准衡量 skill 沉淀对任务完成效率的实际影响。', ORANGE),
        ('R4 冲突解决', '当多个相似 skill 同时命中时，目前的优先级策略较为简单，'
         '缺少基于历史表现动态调整排名的机制。', ORANGE),
        ('R5 可观测性', '缺乏完整的监控指标（latency / recall / hit rate 等），'
         'runtime 内部状态对外部不透明。', HexColor("#9e6a03")),
    ]

    for name, desc, color in limits:
        lh = 1.25 * cm
        c.fill_rect(M_L, c.y - lh, 0.06*cm, lh, color)
        c.fill_rect(M_L + 0.06*cm, c.y - lh, CONTENT_W - 0.06*cm, lh, BG2)
        c.c.setFont(F_BOLD, BODY_FS); c.c.setFillColor(color)
        c.c.drawString(M_L + 0.2*cm, c.y - 0.35*cm, name)
        c.y -= 0.42*cm
        c.body(desc, indent=0.2*cm, color=GRAY, size=10)
        c.y -= lh - 0.55*cm + 0.12*cm

    add_footer(c, 16)
    c.save_page()
    print("章节 16 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 17：为什么可用
# ═══════════════════════════════════════════════════════════════════════════
def make_section17():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(17, '为什么可用')

    reasons = [
        ('✓ 全链路可跑通', 'Distillation → Audit → Promote → Retrieval → Execution → 回填 trajectory，'
         '每一步都有代码落地，不是概念设计。', GREEN),
        ('✓ Codex 即插即用', '通过 MCP server 接入 Codex，无需修改宿主 AI 代码，'
         '30 行配置即可完成集成。', ACCENT),
        ('✓ 治理有实质', 'Audit 不只是占位符：安全检查、命名校验、语义评分均有实现，'
         '不是空壳流程。', HexColor("#238636")),
        ('✓ 实用性强', '从真实 trajectory 中蒸馏 skill，Skill 包含 trigger + instruction + tools，'
         '可直接执行，不是模板占位符。', PURPLE),
    ]

    for name, desc, color in reasons:
        rh = 1.5 * cm
        c.fill_rect(M_L, c.y - rh, CONTENT_W, rh, BG2)
        c.fill_rect(M_L, c.y - rh, 0.06*cm, rh, color)
        c.c.setFont(F_BOLD, 12); c.c.setFillColor(color)
        c.c.drawString(M_L + 0.2*cm, c.y - 0.4*cm, name)
        c.y -= 0.5*cm
        c.body(desc, indent=0.2*cm, color=GRAY, size=10)
        c.y -= rh - 0.6*cm + 0.12*cm

    c.y -= 0.1*cm
    c.h2('Demo 验证')
    demos = [
        ('demo_search.py', '演示 skill 检索流程，模拟 task 描述检索并返回结果'),
        ('demo_distill.py', '演示从 trajectory 蒸馏 skill 的完整流程'),
        ('demo_mcp.py', '演示 MCP server 接入 Codex 的配置和调用过程'),
    ]
    for fname, fdesc in demos:
        c.fill_rect(M_L, c.y - 0.7*cm, 2.5*cm, 0.7*cm, BG2)
        c.fill_rect(M_L, c.y - 0.7*cm, 0.05*cm, 0.7*cm, GREEN)
        c.c.setFont(F_MONO, 9); c.c.setFillColor(GREEN); c.c.drawString(M_L+0.15*cm, c.y - 0.42*cm, fname)
        c.c.setFont(F_REG, 9); c.c.setFillColor(GRAY); c.c.drawString(M_L+2.55*cm, c.y - 0.42*cm, fdesc)
        c.y -= 0.7*cm + 0.05*cm

    add_footer(c, 17)
    c.save_page()
    print("章节 17 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 18：下阶段路线
# ═══════════════════════════════════════════════════════════════════════════
def make_section18():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(18, '下阶段路线')

    phases = [
        ('Phase 1', '近期（1-2 月）', [
            'Skill 自动分类标签体系',
            'skill 版本管理与回滚',
            '基础可观测性（调用次数、成功率）',
            'CLI 补全与交互式 REPL',
        ], ACCENT2),
        ('Phase 2', '中期（3-4 月）', [
            '向量数据库集成（Milvus / Qdrant）',
            '多 skill 冲突检测与智能排名',
            '增量式 skill 更新（而非覆盖）',
            'Audit 的人工复核 UI',
        ], ACCENT),
        ('Phase 3', '远期（5月+）', [
            '跨实例 skill 共享协议',
            'skill 性能基准评测体系',
            '自适应蒸馏阈值（根据任务类型调整）',
            '多宿主 AI 适配（MCP 通用化）',
        ], HexColor("#238636")),
    ]

    for phase, timeline, items, color in phases:
        ph = len(items) * BODY_FS * LB * 1.15 + 0.95*cm
        c.fill_rect(M_L, c.y - ph, CONTENT_W, ph, BG2)
        c.fill_rect(M_L, c.y - ph, 1.2*cm, ph, color)
        c.text(phase[-1], M_L, c.y - ph * 0.62, F_BOLD, 10, WHITE, 'center')
        c.c.setFont(F_BOLD, 11); c.c.setFillColor(color)
        c.c.drawString(M_L + 1.35*cm, c.y - 0.38*cm, phase[:-2].strip())
        c.c.setFont(F_REG, 9); c.c.setFillColor(GRAY)
        c.c.drawString(M_L + 1.35*cm, c.y - 0.65*cm, timeline)
        yi = c.y - 0.9*cm
        for item in items:
            c.c.setFont(F_REG, 10); c.c.setFillColor(LGRAY)
            c.c.drawString(M_L + 1.35*cm, yi, '• ' + item)
            yi -= BODY_FS * LB * 1.15
        c.y -= ph + 0.15*cm

    add_footer(c, 18)
    c.save_page()
    print("章节 18 完成")

# ═══════════════════════════════════════════════════════════════════════════
# 章节 19：项目结论
# ═══════════════════════════════════════════════════════════════════════════
def make_section19():
    c.new_page()
    c.fill_rect(0, PAGE_H - M_T, PAGE_W, M_T, BG2)
    c.fill_rect(0, PAGE_H - M_T, 0.08*cm, M_T, ACCENT)
    c.y -= 0.2*cm
    c.badge_row(19, '项目结论')

    c.body('Skill Runtime 的核心价值在于：把 AI 工作流从「一次性消耗」变成「可沉淀资产」。')

    highlights = [
        ('能力闭环', 'Search → Execute → Distill → Audit → Promote → Reuse，'
         '每一步都有完整的数据结构和可执行的代码。'),
        ('治理内核', 'Audit 两层机制 + Provenance 全链路记录，'
         '确保每个进入 active 的 skill 都经过实质性审查。'),
        ('宿主优先', '通过 MCP 集成到 Codex，而非重新构建 AI 产品，'
         '保持了架构的简洁性和可扩展性。'),
        ('可用性优先', '从真实 trajectory 蒸馏 skill，从真实审计规则构建治理，'
         '不是概念验证（PoC），是可以实际运行的系统。'),
    ]

    for name, desc in highlights:
        hh = 1.2 * cm
        c.fill_rect(M_L, c.y - hh, 2.0*cm, hh, BG2)
        c.fill_rect(M_L, c.y - hh, 0.06*cm, hh, ACCENT)
        c.c.setFont(F_BOLD, 11); c.c.setFillColor(ACCENT)
        c.c.drawString(M_L + 0.15*cm, c.y - hh * 0.62, name)
        c.fill_rect(M_L + 2.0*cm + 0.15*cm, c.y - hh,
                     CONTENT_W - 2.0*cm - 0.15*cm, hh, HexColor("#1c2128"))
        c.body(desc, indent=2.0*cm + 0.25*cm, color=LGRAY, size=10)
        c.y -= hh + 0.1*cm

    c.y -= 0.1*cm
    c.fill_rect(0, 0, PAGE_W, 0.08*cm, ACCENT)
    c.text('Skill Runtime v1.0 — 面向宿主 AI 的技能运行时与治理内核',
           PAGE_W/2, 0.25*cm, F_REG, 8.5, GRAY, 'center')

    add_footer(c, 19)
    c.save_page()
    print("章节 19 完成")

# ── 执行所有章节 ──────────────────────────────────────────────────────────
make_section1()
make_section2()
make_section3()
make_section4()
make_section5()
make_section6()
make_section7()
make_section8()
make_section9()
make_section10()
make_section11()
make_section12()
make_section13()
make_section14()
make_section15()
make_section16()
make_section17()
make_section18()
make_section19()
c.c.showPage()   # 结束最后一页
c.c.save()
print("PDF 生成完成")

# ── PDF 转图片 ────────────────────────────────────────────────────────────
print("开始转图片...")
doc = pypdfium2.PdfDocument(PDF_OUT)
n = len(doc)
for i in range(n):
    page = doc[i]
    bitmap = page.render(scale=3.0, rotation=0)
    pil_img = bitmap.to_pil()
    out_path = os.path.join(IMG_OUT, f'section_{i+1:03d}.png')
    pil_img.save(out_path, 'PNG')
    print(f"  [{i+1}/{n}] {out_path}")

print(f"全部完成！共 {n} 张图片 → {IMG_OUT}")
