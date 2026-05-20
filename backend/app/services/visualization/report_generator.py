"""
PDF 報告生成器
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
from ..models.user_profile import UserProfile
from io import BytesIO
import os


def generate_pdf_report(
    user_profile: UserProfile,
    mbti_analysis: str,
    bigfive_analysis: str,
    zodiac_analysis: str,
    integration_analysis: str,
    reflection: str
) -> BytesIO:
    """
    生成 PDF 報告
    
    Args:
        user_profile: 使用者資料
        mbti_analysis: MBTI 分析文字
        bigfive_analysis: Big Five 分析文字
        zodiac_analysis: 星座分析文字
        integration_analysis: 綜合分析文字
        reflection: 反思語句
        
    Returns:
        PDF 檔案的 BytesIO 物件
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 註冊中文字體（使用 Windows 內建字體或 ReportLab CID 字體）
    try:
        # 嘗試使用 Windows 系統字體
        font_path = "C:/Windows/Fonts/msjh.ttc"  # 微軟正黑體
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            chinese_font = 'ChineseFont'
        else:
            # 使用 ReportLab 內建的 CID 字體
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            chinese_font = 'STSong-Light'
    except:
        # 備用方案：使用 Helvetica（英文字體，中文會顯示方框）
        chinese_font = 'Helvetica'
    
    # 樣式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E5C8A'),
        spaceAfter=30,
        alignment=1,  # 置中
        fontName=chinese_font
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4A90E2'),
        spaceAfter=12,
        fontName=chinese_font
    )
    
    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=11,
        leading=16
    )
    
    # 標題
    story.append(Paragraph("Personality Paradox", title_style))
    story.append(Paragraph("多面向人格測驗報告", title_style))
    story.append(Spacer(1, 1*cm))
    
    # 測驗日期
    date_text = f"測驗日期：{user_profile.test_date.strftime('%Y-%m-%d %H:%M')}"
    story.append(Paragraph(date_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # MBTI 結果
    story.append(Paragraph("MBTI 類型", heading_style))
    story.append(Paragraph(f"類型：{user_profile.mbti.type}", normal_style))
    story.append(Paragraph(mbti_analysis.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Big Five 結果
    story.append(Paragraph("Big Five 人格特質", heading_style))
    bf = user_profile.bigfive
    bf_data = [
        ['維度', '分數'],
        ['開放性', f'{bf.openness:.1f}/6.0'],
        ['盡責性', f'{bf.conscientiousness:.1f}/6.0'],
        ['外向性', f'{bf.extraversion:.1f}/6.0'],
        ['友善性', f'{bf.agreeableness:.1f}/6.0'],
        ['神經質', f'{bf.neuroticism:.1f}/6.0']
    ]
    
    table = Table(bf_data, colWidths=[6*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F4F8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2E5C8A')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(bigfive_analysis.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 星座
    story.append(Paragraph("星座", heading_style))
    story.append(Paragraph(f"星座：{user_profile.zodiac.sign}", normal_style))
    story.append(Paragraph(zodiac_analysis.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 綜合分析
    story.append(Paragraph("綜合分析", heading_style))
    story.append(Paragraph(integration_analysis.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 反思語句
    story.append(Paragraph("反思", heading_style))
    story.append(Paragraph(reflection.replace('\n', '<br/>'), normal_style))
    
    # 生成 PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
