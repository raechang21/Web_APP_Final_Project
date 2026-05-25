from fastapi import APIRouter, Request

from ..config import settings
from ..services.llm.gemini_client import GeminiClient


router = APIRouter(prefix="/api", tags=["debug"])


@router.get("/test-gemini")
def test_gemini() -> dict:
    try:
        client = GeminiClient()
        response = client.generate(
           "請用繁體中文簡短回答：你好嗎？",
            num_predict = 20,
        )
        return {"status": "success", "response": response}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/diagnostic")
def diagnostic(request: Request) -> dict:
    session = request.session
    return {
        "user_name": session.get("user_name"),
        "mbti": session.get("mbti"),
        "big_five_scores": session.get("big_five_scores"),
        "zodiac": session.get("zodiac"),
        "dark_triad_scores": session.get("dark_triad_scores"),
        "chat_messages_count": len(session.get("chat_messages", [])),
        "has_analysis": "analysis" in session,
        "has_comprehensive": "comprehensive" in session.get("analysis", {}),
    }
