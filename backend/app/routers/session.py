from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.tests import QuickLoginIn, SessionOut, StartSessionIn
from ..services import user_repo


router = APIRouter(prefix="/api", tags=["session"])


@router.get("/session", response_model=SessionOut)
def get_session(request: Request, db: Session = Depends(get_db)) -> SessionOut:
    s = request.session
    bigfive_scores = s.get("bigfive_scores") or s.get("big_five_scores")
    has_results = bool(s.get("mbti") and bigfive_scores and s.get("zodiac"))
    memory = user_repo.load_memory(db, s.get("user_name")) if s.get("user_name") else None
    has_analysis = bool(memory and memory.get("deep_analysis"))
    return SessionOut(
        user_name=s.get("user_name"),
        mbti=s.get("mbti"),
        bigfive_scores=bigfive_scores,
        bigfive_answers=s.get("bigfive_answers"),
        zodiac=s.get("zodiac"),
        dark_triad_scores=s.get("dark_triad_scores"),
        dark_triad_answers=s.get("dark_triad_answers"),
        has_results=has_results,
        has_analysis=has_analysis,
        profile_locked=s.get("profile_locked", False),
        is_quick_login=s.get("quick_login", False),
        welcome_message=s.get("welcome_message"),
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

    request.session.clear()
    s = request.session
    s["user_name"] = name
    s["quick_login"] = False
    s["welcome_message"] = f"嗨，{name}，歡迎你來這裡。今天想聊什麼呢？"
    
    memory = user_repo.load_memory(db, name)
    if memory:
        bigfive_scores = memory.get("bigfive_scores") or memory.get("big_five_scores")

        if memory.get("mbti") and bigfive_scores and memory.get("zodiac"):
            request.session.clear()
            s = request.session
            s["user_name"] = name
            s["mbti"] = memory.get("mbti")
            s["bigfive_scores"] = bigfive_scores
            s["bigfive_answers"] = memory.get("bigfive_answers")
            s["zodiac"] = memory.get("zodiac")
            s["dark_triad_scores"] = memory.get("dark_triad_scores")
            s["dark_triad_answers"] = memory.get("dark_triad_answers")
            s["profile_locked"] = memory.get("profile_locked", True)
            s["quick_login"] = True
            s["welcome_message"] = f"嗨，{name}，歡迎回來！"

            return {
                "success": True,
                "user_name": name,
                "redirect": "/results",
            }
    
    user_repo.reset_user_profile(
        db,
        user_name = name,
    )

    return {"success": True, "user_name": name, "redirect": "/mbti"}


@router.post("/quick-login")
def quick_login(
    payload: QuickLoginIn, request: Request, db: Session = Depends(get_db)
) -> dict:
    name = payload.name.strip()
    memory = user_repo.load_memory(db, name)
    if not memory:
        raise HTTPException(404, f"找不到「{name}」的測驗記錄，請先完成測驗")

    bigfive_scores = memory.get("bigfive_scores") or memory.get("big_five_scores")

    if not memory.get("mbti") or not bigfive_scores:
        raise HTTPException(400, f"「{name}」的測驗記錄不完整，請重新完成測驗")

    request.session.clear()
    s = request.session
    s["user_name"] = name
    s["mbti"] = memory.get("mbti")
    s["bigfive_scores"] = bigfive_scores
    s["bigfive_answers"] = memory.get("bigfive_answers")
    s["zodiac"] = memory.get("zodiac")
    s["dark_triad_scores"] = memory.get("dark_triad_scores")
    s["dark_triad_answers"] = memory.get("dark_triad_answers")
    s["profile_locked"] = memory.get("profile_locked", True)
    s["quick_login"] = True

    welcome = f"嗨，{name}，歡迎回來！很高興再次見到你。"
    summaries = memory.get("conversation_summaries") or []
    if summaries:
        topics = summaries[-1].get("topics") or []
        if topics:
            preview = topics[0][:20] + ("..." if len(topics[0]) > 20 else "")
            if "？" in topics[0] or "?" in topics[0]:
                follow = "有試著做看看嗎？"
            elif any(w in topics[0] for w in ["被罵", "難過", "生氣", "傷心", "困擾", "壓力", "焦慮", "煩惱", "挫折", "失望", "沮喪"]):
                follow = "後來還好嗎？"
            elif any(w in topics[0] for w in ["不好", "不開心", "不舒服", "痛苦", "難受"]):
                follow = "現在好一點了嗎？"
            else:
                follow = "後來怎麼樣了？"
            welcome += f" 我記得上次你提到『{preview}』，{follow}"
    else:
        welcome += " 今天想聊什麼呢？"

    s["welcome_message"] = welcome

    return {"success": True, "message": f"歡迎回來，{name}！", "redirect": "/chatbot"}


@router.post("/restart")
def restart(request: Request) -> dict:
    request.session.clear()
    return {"success": True}
