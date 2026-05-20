"""
圖表繪製模組
"""

import plotly.graph_objects as go
from ..models.test_result import BigFiveResult
from ...config import COLORS, BIG_FIVE_DIMENSIONS


def create_radar_chart(bigfive: BigFiveResult) -> go.Figure:
    """
    建立 Big Five 雷達圖
    
    Args:
        bigfive: Big Five 結果
        
    Returns:
        Plotly 圖表物件
    """
    # 維度名稱（中文）
    dimensions = list(BIG_FIVE_DIMENSIONS.values())
    
    # 分數
    scores = [
        bigfive.openness,
        bigfive.conscientiousness,
        bigfive.extraversion,
        bigfive.agreeableness,
        bigfive.neuroticism
    ]
    
    # 建立雷達圖
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=dimensions,
        fill='toself',
        fillcolor=COLORS['primary'],
        opacity=0.6,
        line=dict(color=COLORS['accent'], width=2),
        name='你的分數'
    ))
    
    # 設定布局
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 6],
                tickvals=[1, 2, 3, 4, 5, 6],
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                gridcolor='lightgray'
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_score_bars(bigfive: BigFiveResult) -> dict:
    """
    建立分數條形圖資料
    
    Args:
        bigfive: Big Five 結果
        
    Returns:
        包含維度、分數、顏色的字典
    """
    dimensions_en = list(BIG_FIVE_DIMENSIONS.keys())
    dimensions_zh = list(BIG_FIVE_DIMENSIONS.values())
    
    scores = [
        bigfive.openness,
        bigfive.conscientiousness,
        bigfive.extraversion,
        bigfive.agreeableness,
        bigfive.neuroticism
    ]
    
    colors = [
        COLORS['openness'],
        COLORS['conscientiousness'],
        COLORS['extraversion'],
        COLORS['agreeableness'],
        COLORS['neuroticism']
    ]
    
    return {
        'dimensions_zh': dimensions_zh,
        'scores': scores,
        'colors': colors
    }


def create_dark_triad_bars(dark_triad) -> dict:
    """
    建立黑暗三角條形圖資料
    
    Args:
        dark_triad: 黑暗三角結果
        
    Returns:
        包含維度、分數、顏色的字典
    """
    from ..models.dark_triad_result import DarkTriadResult
    
    # 維度名稱
    dimensions_zh = ['馬基維利主義', '自戀', '精神病態']
    dimensions_en = ['machiavellianism', 'narcissism', 'psychopathy']
    
    # 分數
    scores = [
        dark_triad.machiavellianism,
        dark_triad.narcissism,
        dark_triad.psychopathy
    ]
    
    # 配色（深色系）
    colors = ['#6B46C1', '#DC2626', '#374151']  # 深紫、深紅、深灰
    
    return {
        'dimensions_zh': dimensions_zh,
        'scores': scores,
        'colors': colors
    }
