from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.session import QuickLoginIn, SessionOut, StartSessionIn
from ..services.chat_memory.welcome import build_returning_user_welcome
from ..services.users import repository as user_repository


router = APIRouter(prefix = "/api", tags = ["session"])


@router.get("/session", response_model = SessionOut)
def get_session(request: Request) -> SessionOut:
    s = request.session
    has_results = bool(s.get("mbti") and s.get("big_five_scores") and s.get("zodiac"))
    has_analysis = bool(s.get("analysis", {}).get("comprehensive"))
    return SessionOut(
        user_name = s.get("user_name"),
        mbti = s.get("mbti"),
        big_five_scores = s.get("big_five_scores"),
        zodiac = s.get("zodiac"),
        dark_triad_scores = s.get("dark_triad_scores"),
        has_results = has_results,
        has_analysis = has_analysis,
        is_quick_login = s.get("quick_login", False),
        welcome_message = s.get("welcome_message"),
    )


@router.post("/session/start")
def start_session(
    payload: StartSessionIn, 
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    name = payload.name.strip()
    if not name:
        raise HTTPException(400, "請輸入名字")

    s = request.session
    s["user_name"] = name
    s["chat_messages"] = []
    s["quick_login"] = False
    s["welcome_message"] = f"嗨，{name}，歡迎你來這裡。今天想聊什麼呢？"
    
    user_repository.reset_user_profile(
        db,
        user_name = name,
    )
    
    return {"success": True, "user_name": name, "redirect": "/mbti"}


@router.post("/quick-login")
def quick_login(
    payload: QuickLoginIn, 
    request: Request, 
    db: Session = Depends(get_db), 
) -> dict:
    name = payload.name.strip()
    memory = user_repository.load_memory(db, name)
    
    if not memory:
        raise HTTPException(404, f"找不到「{name}」的測驗記錄，請先完成測驗")

    if not memory.get("mbti") or not memory.get("big_five_scores"):
        raise HTTPException(400, f"「{name}」的測驗記錄不完整，請重新完成測驗")

    s = request.session
    s["user_name"] = name
    s["mbti"] = memory.get("mbti")
    s["big_five_scores"] = memory.get("big_five_scores")
    s["zodiac"] = memory.get("zodiac")
    s["dark_triad_scores"] = memory.get("dark_triad_scores")
    s["chat_messages"] = []
    s["quick_login"] = True

    welcome = build_returning_user_welcome(name, memory)

    s["welcome_message"] = welcome

    return {"success": True, "message": f"歡迎回來，{name}！", "redirect": "/chatbot"}


@router.post("/restart")
def restart(request: Request) -> dict:
    request.session.clear()
    return {"success": True}
