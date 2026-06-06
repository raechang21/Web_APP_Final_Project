from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import ZODIAC_SIGNS
from ..db import get_db
from ..schemas.tests import (
    BigFiveAnswers,
    DarkTriadAnswers,
    MBTIIn,
    VALID_MBTI,
    ZodiacIn,
)
from ..services import user_repo
from ..services.analysis.scoring import (
    calculate_bigfive_scores,
    calculate_dark_triad_scores,
)
from ..services.utils.data_loader import (
    load_bigfive_questions,
    load_dark_triad_questions,
)


router = APIRouter(prefix="/api", tags=["tests"])


def _reject_if_completed(request: Request, *keys: str, label: str) -> None:
    if request.session.get("profile_locked") or any(
        request.session.get(key) is not None for key in keys
    ):
        raise HTTPException(
            409,
            f"{label} 已完成，不能修改；請到結果頁查看以前的記錄",
        )


def _persist_profile(request: Request, db: Session) -> None:
    user_name = request.session.get("user_name")
    if not user_name:
        return
    
    user_repo.save_user_profile(
        db,
        user_name = user_name, 
        mbti = request.session.get("mbti"),
        bigfive_scores = request.session.get("bigfive_scores"),
        bigfive_answers = request.session.get("bigfive_answers"),
        zodiac = request.session.get("zodiac"),
        dark_triad_scores = request.session.get("dark_triad_scores"),
        dark_triad_answers = request.session.get("dark_triad_answers"),
        profile_locked = request.session.get("profile_locked", False),
    )


@router.post("/mbti")
def submit_mbti(
    payload: MBTIIn, 
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    _reject_if_completed(request, "mbti", label="MBTI")

    mbti = payload.mbti_type.upper().strip()
    if mbti not in VALID_MBTI:
        raise HTTPException(400, "請輸入有效的 MBTI 類型")
    
    request.session["mbti"] = mbti
    _persist_profile(request, db)
    
    return {"mbti": mbti}


@router.get("/bigfive/questions")
def bigfive_questions() -> dict:
    questions, scale_labels = load_bigfive_questions()
    return {"questions": questions, "scale_labels": scale_labels}


@router.post("/bigfive")
def submit_big_five(
    payload: BigFiveAnswers, 
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    if "mbti" not in request.session:
        raise HTTPException(400, "請先完成 MBTI 測驗")
    _reject_if_completed(
        request,
        "bigfive_scores",
        "bigfive_answers",
        label="Big Five",
    )
    
    questions, _ = load_bigfive_questions()
    if len(payload.answers) != len(questions):
        raise HTTPException(400, "請回答所有問題")
    
    scores = calculate_bigfive_scores(payload.answers, questions)
    request.session["bigfive_scores"] = scores
    request.session["bigfive_answers"] = payload.answers
    _persist_profile(request, db)
    
    return {"bigfive_scores": scores}


@router.get("/zodiacs")
def zodiacs() -> dict:
    return {"zodiacs": ZODIAC_SIGNS}


@router.post("/zodiac")
def submit_zodiac(
    payload: ZodiacIn, 
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    if "bigfive_scores" not in request.session:
        raise HTTPException(400, "請先完成 Big Five 測驗")
    _reject_if_completed(request, "zodiac", label="星座")
    
    if payload.zodiac not in ZODIAC_SIGNS:
        raise HTTPException(400, "無效的星座")
    
    request.session["zodiac"] = payload.zodiac
    _persist_profile(request, db)
    
    return {"zodiac": payload.zodiac}


@router.get("/dark-triad/questions")
def dark_triad_questions() -> dict:
    qs = load_dark_triad_questions()
    return {"questions": qs}


@router.post("/dark-triad")
def submit_dark_triad(
    payload: DarkTriadAnswers, 
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    if "zodiac" not in request.session:
        raise HTTPException(400, "請先選擇星座")
    _reject_if_completed(
        request,
        "dark_triad_scores",
        "dark_triad_answers",
        label="Dark Triad",
    )
    
    questions = load_dark_triad_questions()
    if len(payload.answers) != len(questions):
        raise HTTPException(400, "請回答所有問題")
    
    scores = calculate_dark_triad_scores(payload.answers, questions)
    request.session["dark_triad_scores"] = scores
    request.session["dark_triad_answers"] = payload.answers
    request.session["profile_locked"] = True
    _persist_profile(request, db)
    
    return {"dark_triad_scores": scores}


@router.post("/dark-triad/skip")
def skip_dark_triad(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    _reject_if_completed(
        request,
        "dark_triad_scores",
        "dark_triad_answers",
        label="Dark Triad",
    )

    request.session["dark_triad_scores"] = None
    request.session["dark_triad_answers"] = None
    request.session["profile_locked"] = True
    _persist_profile(request, db)
    return {"skipped": True}
