from ...config import BIG_FIVE_DIMENSIONS, DARK_TRIAD_DIMENSIONS


def interpret_score(score: float) -> str:
    if score <= 2.0:
        return "極低"
    if score <= 3.0:
        return "偏低"
    if score <= 4.0:
        return "中等"
    if score <= 5.0:
        return "偏高"
    return "極高"


def _format_scores(
    scores: dict[str, float], 
    dimensions: dict[str, str], 
) -> str:
    lines = []
    for key, label in dimensions.items():
        if key in scores:
            lines.append(f"· {label}: {scores[key]: .1f}/6.0 ({interpret_score(scores[key])})")
    return "\n".join(lines)


def build_comprehensive_prompt(
    mbti: str, 
    big_five: dict[str, float], 
    zodiac: str, 
    dark_triad: dict[str, float] | None = None, 
) -> str:
    big_five_text = _format_scores(big_five, BIG_FIVE_DIMENSIONS)
    
    dark_triad_text = ""
    if dark_triad:
        dark_triad_text = f"""
- 黑暗三角特質：
{_format_scores(dark_triad, DARK_TRIAD_DIMENSIONS)}
"""

    return f"""你是專業的心理學分析師。基於以下人格測驗結果，請撰寫一篇整合性分析。

【測驗結果】
- MBTI 類型：{mbti}
- 星座：{zodiac}

- Big Five 人格特質：
{big_five_text}
{dark_triad_text}

判讀規則: ≤2.0=極低 | 2.1-3.0=偏低 | 3.1-4.0=中等 | 4.1-5.0=偏高 | >5.0=極高

【分析要求】
1. **使用第二人稱「你」**
2. **請嚴格依照以下順序，將分析分為獨立的段落（每個段落之間【必須使用一個空白行】隔開）：**
   - 第一段：專注於 MBTI 類型的核心特質與行為模式分析。
   - 第二段：專注於 Big Five 人格特質分析（嚴格依照判讀標準描述高低）。
   - 第三段：專注於星座特質分析，並探討它與前面測驗的關聯或矛盾。
   - 第四段（若有黑暗三角數據）：專注於黑暗三角特質分析。
3. **嚴格依照「分數判讀標準」描述 Big Five 特質高低**
4. **聚焦於不同測驗結果之間的「呼應」與「矛盾」**
5. **不要在文中提及具體分數**
6. **嚴格控制字數在 400-450 字以內**

【禁止事項】
✗ 絕對禁止任何開場白或自我介紹
✗ 必須直接以第一段的 MBTI 分析作為文章的開頭
✗ 不要使用「這位客人」「該受測者」等第三人稱
✗ 不要在分析文中寫出具體分數
✗ 不要誤判分數高低
✗ 不要分段標題
✗ 不要超過 450 字
✗ 絕對不要使用任何 Markdown 格式

請直接開始分析，用流暢的段落形式書寫，使用純文字不要任何格式標記。"""
