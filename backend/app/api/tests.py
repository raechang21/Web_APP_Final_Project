from fastapi import APIRouter, HTTPException, Request

from ..config import ZODIAC_SIGNS
from ..schemas.tests import (
    BigFiveAnswers,
    DarkTriadAnswers,
    MBTIIn,
    VALID_MBTI,
    ZodiacIn,
)
from ..services.analysis.scoring import (
    calculate_big_five_scores,
    calculate_dark_triad_scores,
)
from ..services.utils.data_loader import (
    load_big_five_questions,
    load_dark_triad_questions,
)


router = APIRouter(prefix = "/api", tags = ["tests"])


def _require_session_key(request: Request, key: str, message: str) -> None:
    if key not in request.session:
        raise HTTPException(400, message)
    

def _validate_answer_count(answers: dict[int, int], questions: list[dict]) -> None:
    if len(answers) != len(questions):
        raise HTTPException(400, "請回答所有題目")


@router.post("/mbti")
def submit_mbti(payload: MBTIIn, request: Request) -> dict:
    mbti = payload.mbti_type.upper().strip()
    if mbti not in VALID_MBTI:
        raise HTTPException(400, "請輸入有效的 MBTI 類型")
    
    request.session["mbti"] = mbti
    return {"mbti": mbti}


@router.get("/big-five/questions")
def big_five_questions() -> dict:
    questions, scale_labels = load_big_five_questions()
    return {
        "questions": questions, 
        "scale_labels": scale_labels
    }


@router.post("/big-five")
def submit_big_five(payload: BigFiveAnswers, request: Request) -> dict:
    _require_session_key(request, "mbti", "請先完成 MBTI 測驗")
    
    questions, _ = load_big_five_questions()
    _validate_answer_count(payload.answers, questions)

    scores = calculate_big_five_scores(payload.answers, questions)
    request.session["big_five_scores"] = scores
    
    return {"big_five_scores": scores}


@router.get("/zodiacs")
def zodiacs() -> dict:
    return {"zodiacs": ZODIAC_SIGNS}


@router.post("/zodiac")
def submit_zodiac(payload: ZodiacIn, request: Request) -> dict:
    _require_session_key(request, "big_five_scores", "請先完成 Big Five 測驗")
    
    if payload.zodiac not in ZODIAC_SIGNS:
        raise HTTPException(400, "無效的星座")
    
    request.session["zodiac"] = payload.zodiac
    return {"zodiac": payload.zodiac}


@router.get("/dark-triad/questions")
def dark_triad_questions() -> dict:
    questions = load_dark_triad_questions()
    return {"questions": questions}


@router.post("/dark-triad")
def submit_dark_triad(payload: DarkTriadAnswers, request: Request) -> dict:
    _require_session_key(request, "zodiac", "請先選擇星座")

    questions = load_dark_triad_questions()
    _validate_answer_count(payload.answers, questions)

    scores = calculate_dark_triad_scores(payload.answers, questions)
    request.session["dark_triad_scores"] = scores

    return {"dark_triad_scores": scores}


@router.post("/dark-triad/skip")
def skip_dark_triad(request: Request) -> dict:
    _require_session_key(request, "zodiac", "請先選擇星座")

    request.session["dark_triad_scores"] = None
    return {"skipped": True}
