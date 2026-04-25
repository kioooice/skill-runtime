from io import BytesIO
from pathlib import Path
from textwrap import wrap

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import white, black
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


SOURCE_PDF = Path(r"D:\02-Projects\work\张清栋.pdf")
OUTPUT_DIR = Path(r"D:\02-Projects\vibe\output\pdf\zhang_qingdong_resume")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = OUTPUT_DIR / "张清栋_企业项目AI智能体版_原排版.pdf"

FONT_REGULAR = "SimHeiCustom"
FONT_BOLD = "SimHeiCustom"
pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\simhei.ttf"))

PAGE_WIDTH, PAGE_HEIGHT = A4

TITLE = "研发知识平台与 AI 智能体辅助分析项目｜企业场景项目"
BULLETS = [
    "围绕实验数据分散、经验难复用、研发需求整理效率低等问题，参与项目需求梳理与方案设计，拆解数据沉淀、知识检索、结果分析、方案生成等核心场景。",
    "基于对话式交互接收实验结果与研发需求，支持自动记录实验数据，并生成分析报告、趋势规律、项目方案与实验计划，提升研发信息处理与方案输出效率。",
    "结合历史实验记录、配方数据、测试结果与检测方案，梳理数据对象、关键字段、角色分工与使用流程，支持智能分析能力与项目管理系统衔接。",
    "联动检测项目管理、用户管理等模块，形成“结果录入 - 智能分析 - 方案生成 - 人工确认 - 实验执行反馈”的业务闭环，推动信息标准化、经验复用与辅助决策落地。",
]


def fit_lines(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    chars: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if pdfmetrics.stringWidth(trial, font_name, font_size) <= max_width:
            current = trial
        else:
            if current:
                chars.append(current)
            current = ch
    if current:
        chars.append(current)
    return chars


packet = BytesIO()
c = canvas.Canvas(packet, pagesize=A4)

# White cover over the original enterprise project block.
cover_top = 518
cover_bottom = 603.5
cover_left = 24
cover_right = 545
c.setFillColor(white)
c.setStrokeColor(white)
c.rect(
    cover_left,
    PAGE_HEIGHT - cover_bottom,
    cover_right - cover_left,
    cover_bottom - cover_top,
    stroke=1,
    fill=1,
)

c.setFillColor(black)
c.setFont(FONT_BOLD, 10)
c.drawString(27, PAGE_HEIGHT - 531.5, TITLE)

text = c.beginText()
text.setTextOrigin(45, PAGE_HEIGHT - 543.5)
text.setFont(FONT_REGULAR, 8.55)
text.setLeading(10.0)

max_text_width = 496
for bullet in BULLETS:
    lines = fit_lines(bullet, FONT_REGULAR, 8.55, max_text_width - 13)
    if not lines:
        continue
    text.textLine(f"● {lines[0]}")
    for line in lines[1:]:
        text.textLine(f"  {line}")

c.drawText(text)
c.save()
packet.seek(0)

overlay_reader = PdfReader(packet)
source_reader = PdfReader(str(SOURCE_PDF))
writer = PdfWriter()

base_page = source_reader.pages[0]
base_page.merge_page(overlay_reader.pages[0])
writer.add_page(base_page)

with OUTPUT_PDF.open("wb") as f:
    writer.write(f)

print(OUTPUT_PDF)
