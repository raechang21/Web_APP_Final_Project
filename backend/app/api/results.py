import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..services.llm.gemini_client import GeminiClient
from ..services.llm.prompt_templates import PromptTemplates
from ..services.results.analysis import (
    DEEP_ANALYSIS_SYSTEM_PROMPT,
    build_comprehensive_prompt,
)
from ..services.results.charts import build_big_five_radar_chart


router = APIRouter(prefix = "/api", tags = ["results"])


def _ensure_results(request: Request) -> tuple[str, dict, str, dict | None]:
    session = request.session
    mbti = session.get("mbti")
    big_five = session.get("big_five_scores")
    zodiac = session.get("zodiac")
    
    if not (mbti and big_five and zodiac):
        raise HTTPException(400, "缺少測驗資料，請先完成所有測驗")
    
    return mbti, big_five, zodiac, session.get("dark_triad_scores")


@router.get("/results")
def get_results(request: Request) -> dict:
    mbti, big_five, zodiac, dark_triad = _ensure_results(request)
    session = request.session

    if "analysis" not in session:
        session["analysis"] = {
            "mbti": PromptTemplates.get_mbti_template(mbti),
            "big_five": PromptTemplates.get_big_five_template(big_five),
            "zodiac": PromptTemplates.get_zodiac_template(zodiac),
            "dark_triad": (
                PromptTemplates.get_dark_triad_template(dark_triad)
                if dark_triad
                else None
            ),
        }

    return {
        "mbti": mbti,
        "big_five_scores": big_five,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad,
        "analysis": session["analysis"],
    }


@router.get("/big-five-chart")
def big_five_chart(request: Request) -> dict:
    big_five = request.session.get("big_five_scores")
    if not big_five:
        raise HTTPException(404, "尚未完成 Big Five 測驗")
    
    return build_big_five_radar_chart(big_five)


@router.get("/deep-analysis")
def deep_analysis(request: Request) -> dict:
    mbti, big_five, zodiac, dark_triad = _ensure_results(request)
    session = request.session
    analysis = session.get("analysis", {})
    
    session["viewed_deep_analysis"] = True
    
    return {
        "mbti": mbti,
        "big_five_scores": big_five,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad,
        "analysis": analysis,
        "has_analysis": "comprehensive" in analysis,
    }


@router.get("/deep-analysis/stream")
def deep_analysis_stream(request: Request) -> StreamingResponse:
    mbti, big_five, zodiac, dark_triad = _ensure_results(request)
    prompt = build_comprehensive_prompt(mbti, big_five, zodiac, dark_triad)
    session = request.session

    def generate():
        full = ""
        
        try:
            client = GeminiClient()
            
            for text in client.generate_stream(
                prompt, 
                system_prompt = DEEP_ANALYSIS_SYSTEM_PROMPT, 
            ):
                if text:
                    full += text
                    yield f"data: {json.dumps({'chunk': text}, ensure_ascii = False)}\n\n"
            
            analysis = session.get("analysis", {})
            analysis["comprehensive"] = full
            session["analysis"] = analysis
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii = False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type = "text/event-stream",
        headers = {
            "Cache-Control": "no-cache", 
            "X-Accel-Buffering": "no"},
    )
