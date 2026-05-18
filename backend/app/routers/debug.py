from fastapi import APIRouter, Request
from ..config import settings

# OLLAMA
# import ollama

# Gemini
from ..services.llm.gemini_client import GeminiClient

router = APIRouter(prefix="/api", tags=["debug"])


# OLLAMA
# @router.get("/test-ollama")
# def test_ollama() -> dict:
#     try:
#         models = ollama.list()
#         response = ollama.generate(
#             model=settings.OLLAMA_MODEL,
#             prompt="請用繁體中文簡短回答：你好嗎？",
#             options={"num_predict": 20},
#         )
#         return {
#             "status": "success",
#             "models_count": len(models.models),
#             "response": response["response"],
#         }
#     except Exception as e:
#         return {"status": "error", "error": str(e)}

# Gemini
@router.get("/test-gemini")
def test_gemini() -> dict:
    try:
        llm_client = GeminiClient()
        
        # 呼叫我們在前一個步驟加入到 GeminiClient 的 test_connection 函式
        is_connected = llm_client.test_connection()
        
        if is_connected:
            return {
                "status": "success",
                "service": "Gemini API",
                "message": "連線成功！Gemini API 運作正常。"
            }
        else:
            return {
                "status": "error",
                "service": "Gemini API",
                "message": "連線失敗，請檢查 API Key 是否正確或網路狀態。"
            }
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