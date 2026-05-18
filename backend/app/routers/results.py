import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

# OLLAMA
# import ollama

# Gemini
from ..services.llm.gemini_client import GeminiClient

from ..config import settings
from ..services.llm.prompt_templates import PromptTemplates


router = APIRouter(prefix="/api", tags=["results"])


def _interpret(score: float) -> str:
    if score <= 2.0:
        return "極低"
    if score <= 3.0:
        return "偏低"
    if score <= 4.0:
        return "中等"
    if score <= 5.0:
        return "偏高"
    return "極高"


def _ensure_results(request: Request) -> tuple[str, dict, str, dict | None]:
    s = request.session
    mbti = s.get("mbti")
    bigfive = s.get("bigfive_scores")
    zodiac = s.get("zodiac")
    if not (mbti and bigfive and zodiac):
        raise HTTPException(400, "缺少測驗資料，請先完成所有測驗")
    return mbti, bigfive, zodiac, s.get("dark_triad_scores")


@router.get("/results")
def get_results(request: Request) -> dict:
    mbti, bigfive, zodiac, dark_triad = _ensure_results(request)
    
    # 每次即時組合，不要存進 request.session 中！
    analysis = {
        "mbti": PromptTemplates.get_mbti_template(mbti),
        "bigfive": PromptTemplates.get_bigfive_template(bigfive),
        "zodiac": PromptTemplates.get_zodiac_template(zodiac),
        "dark_triad": (
            PromptTemplates.get_dark_triad_template(dark_triad) if dark_triad else None
        ),
    }

    return {
        "mbti": mbti,
        "bigfive_scores": bigfive,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad,
        "analysis": analysis, # 直接回傳
    }


@router.get("/bigfive-chart")
def bigfive_chart(request: Request) -> dict:
    bigfive = request.session.get("bigfive_scores")
    if not bigfive:
        raise HTTPException(404, "尚未完成 Big Five 測驗")
    return {
        "data": [
            {
                "type": "scatterpolar",
                "r": [
                    bigfive["openness"],
                    bigfive["conscientiousness"],
                    bigfive["extraversion"],
                    bigfive["agreeableness"],
                    bigfive["neuroticism"],
                ],
                "theta": ["開放性", "盡責性", "外向性", "友善性", "神經質"],
                "fill": "toself",
                "name": "Big Five",
            }
        ],
        "layout": {
            "polar": {
                "radialaxis": {
                    "visible": True,
                    "range": [0, 6],
                    "tickvals": [1, 2, 3, 4, 5, 6],
                }
            },
            "showlegend": False,
            "title": "Big Five 人格特質",
        },
    }


@router.get("/deep-analysis")
def deep_analysis(request: Request) -> dict:
    mbti, bigfive, zodiac, dark_triad = _ensure_results(request)
    s = request.session
    s["viewed_deep_analysis"] = True
    analysis = s.get("analysis", {})
    return {
        "mbti": mbti,
        "bigfive_scores": bigfive,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad,
        "analysis": analysis,
        "has_analysis": "comprehensive" in analysis,
    }


def _build_comprehensive_prompt(
    mbti: str, bigfive: dict, zodiac: str, dark_triad: dict | None
) -> str:
    bf_levels = {k: _interpret(v) for k, v in bigfive.items()}
    dark_triad_text = ""
    dt_levels = {}
    if dark_triad:
        dt_levels = {k: _interpret(v) for k, v in dark_triad.items()}
        dark_triad_text = f"""
- 黑暗三角特質：
  · 馬基維利主義：{dark_triad['machiavellianism']:.1f}/6.0
  · 自戀：{dark_triad['narcissism']:.1f}/6.0
  · 心理病態：{dark_triad['psychopathy']:.1f}/6.0
"""

    prompt = f"""你是專業的心理學分析師。基於以下人格測驗結果，請撰寫一篇整合性分析。

【測驗結果】
- MBTI 類型：{mbti}
- Big Five 人格特質：
  · 開放性：{bigfive['openness']:.1f}/6.0
  · 盡責性：{bigfive['conscientiousness']:.1f}/6.0
  · 外向性：{bigfive['extraversion']:.1f}/6.0
  · 友善性：{bigfive['agreeableness']:.1f}/6.0
  · 神經質：{bigfive['neuroticism']:.1f}/6.0
- 星座：{zodiac}{dark_triad_text}

【分數判讀標準】（僅供你內部分析使用，不要在回答中顯示此標準）
- 開放性: {bf_levels['openness']}
- 盡責性: {bf_levels['conscientiousness']}
- 外向性: {bf_levels['extraversion']}
- 友善性: {bf_levels['agreeableness']}
- 神經質: {bf_levels['neuroticism']}"""

    if dark_triad:
        prompt += f"""
- 馬基維利主義: {dt_levels['machiavellianism']}
- 自戀: {dt_levels['narcissism']}
- 心理病態: {dt_levels['psychopathy']}"""

    prompt += """

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
    return prompt


def _clean_markdown(text: str) -> str:
    import re

    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"^\s*[\*\-\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    return text


@router.get("/deep-analysis/stream")
def deep_analysis_stream(request: Request) -> StreamingResponse:
    mbti, bigfive, zodiac, dark_triad = _ensure_results(request)
    prompt = _build_comprehensive_prompt(mbti, bigfive, zodiac, dark_triad)
    s = request.session

    def generate():
        full = ""
        try:
            # OLLAMA
            # response = ollama.generate(
            #     model=settings.OLLAMA_MODEL,
            #     prompt=prompt,
            #     system=(
            #         "你是一位專業的心理學分析師。請使用繁體中文，提供完整且深入的分析。"
            #         "回應時請使用純文字，不要使用任何 Markdown 格式標記。"
            #     ),
            #     stream=True,
            #     options={"temperature": 0.7, "top_p": 0.9, "num_predict": 2048},
            # )
            # for chunk in response:
            #     if "response" in chunk:
            #         text = _clean_markdown(chunk["response"])
            #         full += text
            #         yield f"data: {json.dumps({'chunk': text}, ensure_ascii=False)}\n\n"

            # Gemini
            llm_client = GeminiClient()
            system_msg = (
                "你是一位專業的心理學分析師。請使用繁體中文，提供完整且深入的分析。"
                "回應時請使用純文字，不要使用任何 Markdown 格式標記。"
            )
            for text_chunk in llm_client.generate_stream(prompt, system_msg):
                if text_chunk:
                    full += text_chunk
                    yield f"data: {json.dumps({'chunk': text_chunk}, ensure_ascii=False)}\n\n"
                    
            analysis = s.get("analysis", {})
            analysis["comprehensive"] = full
            s["analysis"] = analysis
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            # 強制把錯誤訊息包裝成 chunk 顯示在畫面上，避免前端吞掉錯誤
            error_msg = f"\n\n⚠️ [系統提示：生成中斷，原因 - {str(e)}]"
            yield f"data: {json.dumps({'chunk': error_msg}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
