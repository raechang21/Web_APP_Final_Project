from fastapi import APIRouter, Request
from ..services.llm.gemini_client import GeminiClient
from ..config import settings


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
    s = request.session
    return {
        "user_name": s.get("user_name"),
        "mbti": s.get("mbti"),
        "bigfive_scores": s.get("bigfive_scores"),
        "zodiac": s.get("zodiac"),
        "dark_triad_scores": s.get("dark_triad_scores"),
        "chat_messages_count": len(s.get("chat_messages", [])),
        "has_analysis": "analysis" in s,
        "has_comprehensive": "comprehensive" in s.get("analysis", {}),
    }


@router.post("/setup-test-data")
def setup_test_data(request: Request) -> dict:
    s = request.session
    s["mbti"] = "INTJ"
    s["bigfive_scores"] = {
        "openness": 5.5,
        "conscientiousness": 5.0,
        "extraversion": 2.5,
        "agreeableness": 4.0,
        "neuroticism": 3.5,
    }
    s["zodiac"] = "天蠍座"
    s["dark_triad_scores"] = None
    return {"status": "ok", "mbti": s["mbti"]}
