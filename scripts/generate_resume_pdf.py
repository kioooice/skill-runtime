from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


OUTPUT_DIR = Path(r"D:\02-Projects\vibe\output\pdf\zhang_qingdong_resume")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = OUTPUT_DIR / "张清栋_企业数字化产品经理_简历.pdf"

FONT_NAME = "STSong-Light"
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="Name",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=18,
        leading=21,
        textColor=HexColor("#0F172A"),
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="Meta",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9.0,
        leading=11.5,
        textColor=HexColor("#334155"),
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=10.8,
        leading=13.5,
        textColor=HexColor("#0F172A"),
        borderPadding=0,
        spaceBefore=5,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=8.2,
        leading=10.6,
        textColor=HexColor("#1E293B"),
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="ResumeBullet",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=8.0,
        leading=10.2,
        leftIndent=8,
        firstLineIndent=-8,
        textColor=HexColor("#1E293B"),
        spaceAfter=1,
    )
)
styles.add(
    ParagraphStyle(
        name="ResumeRole",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=8.8,
        leading=11.0,
        textColor=HexColor("#0F172A"),
        spaceAfter=1,
    )
)


def p(text: str, style: str) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), styles[style])


story = [
    p("张清栋", "Name"),
    p("福建·漳州｜16605965483｜2265298543@qq.com｜求职方向：企业数字化 / ToB 产品经理", "Meta"),
    p(
        "具备研发一线经验，长期参与实验分析、流程梳理、方案推进与技术文档沉淀，能够从实际业务场景中识别问题、提炼需求并推动改进。"
        "熟悉企业研发场景中的知识沉淀、流程标准化、数据整理与协同机制，关注 AI 与数字化工具在知识检索、辅助分析、视觉识别、流程提效等场景中的应用，"
        "期望转向企业数字化 / ToB 产品经理岗位。",
        "Body",
    ),
    Spacer(1, 2),
    p("教育背景", "Section"),
    p("四川农业大学｜化学生物学｜本科｜2020.09 - 2024.06", "ResumeRole"),
    p("毕业设计：《硅藻土表面氨基化改性及其对白藜芦醇的吸附效果研究》；独立完成材料合成、实验设计、数据分析与结果验证。", "ResumeBullet"),
    p("工作经历", "Section"),
    p("宏正（福建）化学品有限公司｜研发工程师｜2025.09 - 至今", "ResumeRole"),
    p("围绕电镀与防锈研发场景，识别配方筛选依赖经验、人工判断效率低且一致性不足等问题，梳理实验流程、关键节点、评价指标与数据口径，参与形成数字化改进方案并推动验证落地。", "ResumeBullet"),
    p("结合历史实验数据与实际使用场景，参与候选配方辅助分析逻辑梳理，明确输入数据、分析维度与输出方式，支持前期筛选环节提效。", "ResumeBullet"),
    p("参与视觉识别量化方案推进，围绕人工判断标准不统一、统计效率低等问题，协同梳理识别规则、结果呈现方式与应用流程，推动部分判断与统计环节由图像识别替代人工完成。", "ResumeBullet"),
    p("输出 SOP 与技术文档，协同业务、研发与客户推进方案应用、问题排查和反馈闭环，推动经验沉淀与流程标准化。", "ResumeBullet"),
    p("厦门特宝生物工程股份有限公司｜分析测试助理｜2024.07 - 2025.02", "ResumeRole"),
    p("参与生物样品前处理及理化分析，严格按照 GMP 规范执行实验流程，保证数据记录准确、可追溯。", "ResumeBullet"),
    p("使用 HPLC、GC 等仪器完成检测任务，支持研发与测试工作稳定开展，并参与分析方法转移与流程优化。", "ResumeBullet"),
    p("负责实验原始记录、技术报告及相关文档整理归档，形成较强的数据意识与结构化输出能力。", "ResumeBullet"),
    p("项目经历", "Section"),
    p("研发知识平台与配方辅助分析项目｜企业场景项目", "ResumeRole"),
    p("围绕实验数据分散、经验难复用、配方筛选依赖个人经验等问题，参与研发知识平台与辅助分析项目的需求梳理，拆解知识沉淀、检索复用、方案辅助分析等核心场景，明确建设方向。", "ResumeBullet"),
    p("围绕实验记录、配方数据、测试结果与检测方案等信息，梳理数据对象、关键字段、角色分工与使用场景，支持后续信息结构与核心流程设计。", "ResumeBullet"),
    p("参与设计“数据沉淀 - 知识检索 - 候选方案辅助分析”的核心流程，推动研发场景中的信息标准化、经验复用与前期筛选提效。", "ResumeBullet"),
    p("结合研发知识沉淀、信息检索与辅助分析场景，参与梳理 AI / 数字化能力可嵌入的业务节点，支持方案讨论与落地验证。", "ResumeBullet"),
    p("信息整合与项目起步助手｜个人项目", "ResumeRole"),
    p("针对项目起步阶段资料分散、信息来源碎片化、难以快速形成执行方向的问题，设计信息收集、筛选、重组与起步方案生成流程。", "ResumeBullet"),
    p("技能", "Section"),
    p("需求分析与流程梳理：能够结合业务场景识别问题，完成需求提炼、流程拆解与改进方案推进。", "ResumeBullet"),
    p("B 端产品与数字化理解：关注企业内部提效、知识沉淀、流程标准化、协同留痕等典型产品方向。", "ResumeBullet"),
    p("信息与数据分析：熟悉 Excel、Origin、结构化信息整理与基础数据分析，具备较强的数据意识与文档能力。", "ResumeBullet"),
    p("AI 与数字化应用：熟悉 Codex、Claude、Gemini 等工具使用，了解知识库、工作流自动化、Agent、视觉识别等企业应用方向，能够结合具体业务场景辅助方案设计。", "ResumeBullet"),
]


doc = SimpleDocTemplate(
    str(OUTPUT_PDF),
    pagesize=A4,
    leftMargin=12 * mm,
    rightMargin=12 * mm,
    topMargin=10 * mm,
    bottomMargin=10 * mm,
)
doc.build(story)

print(OUTPUT_PDF)
