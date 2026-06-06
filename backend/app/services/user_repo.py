from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..models_db.memory import UserMemory
from ..models_db.user import User


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_user(
    db: Session, 
    *, 
    user_name: str, 
    mbti: str | None = None, 
    bigfive_scores: dict | None = None, 
    bigfive_answers: dict | None = None,
    zodiac: str | None = None, 
    dark_triad_scores: dict | None = None, 
    dark_triad_answers: dict | None = None,
    deep_analysis: str | None = None, 
) -> User: 
    user = db.get(User, user_name)
    
    if user is None:
        user = User(user_name = user_name)
        db.add(user)
        
    user.mbti = mbti
    user.bigfive_scores = bigfive_scores
    user.bigfive_answers = bigfive_answers
    user.zodiac = zodiac
    user.dark_triad_scores = dark_triad_scores
    user.dark_triad_answers = dark_triad_answers
    if deep_analysis is not None:
        user.deep_analysis = deep_analysis
        
    return user


def load_memory(db: Session, user_name: str) -> dict | None:
    memory = db.get(UserMemory, user_name)
    return memory.memory_json if memory else None


def save_user_profile(
    db: Session, 
    *, 
    user_name: str, 
    mbti: str | None = None, 
    bigfive_scores: dict | None = None, 
    bigfive_answers: dict | None = None,
    zodiac: str | None = None, 
    dark_triad_scores: dict | None = None, 
    dark_triad_answers: dict | None = None,
    deep_analysis: str | None = None, 
    profile_locked: bool | None = None,
) -> None:
    if not user_name:
        return
    
    upsert_user(
        db,
        user_name = user_name, 
        mbti = mbti, 
        bigfive_scores = bigfive_scores, 
        bigfive_answers = bigfive_answers,
        zodiac = zodiac, 
        dark_triad_scores = dark_triad_scores, 
        dark_triad_answers = dark_triad_answers,
        deep_analysis = deep_analysis,
    )
    
    memory = db.get(UserMemory, user_name)
    existing = memory.memory_json if memory else {}
    
    saved_deep_analysis = deep_analysis if deep_analysis is not None else existing.get("deep_analysis")
    saved_profile_locked = (
        profile_locked if profile_locked is not None else existing.get("profile_locked", False)
    )

    memory_data = {
        **existing, 
        "user_name": user_name,
        "mbti": mbti,
        "bigfive_scores": bigfive_scores,
        "bigfive_answers": bigfive_answers,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad_scores,
        "dark_triad_answers": dark_triad_answers,
        "deep_analysis": saved_deep_analysis,
        "profile_locked": saved_profile_locked,
        "last_updated": _now_iso(),
    }
    
    if memory is None:
        db.add(UserMemory(user_name = user_name, memory_json = memory_data))
    else:
        memory.memory_json = memory_data
        
    db.commit()
    
    
def reset_user_profile(db: Session, *, user_name: str) -> None:
    if not user_name:
        return

    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    else:
        user.mbti = None
        user.bigfive_scores = None
        user.bigfive_answers = None
        user.zodiac = None
        user.dark_triad_scores = None
        user.dark_triad_answers = None
        user.deep_analysis = None

    memory = db.get(UserMemory, user_name)
    memory_data = {
        "user_name": user_name,
        "mbti": None,
        "bigfive_scores": None,
        "bigfive_answers": None,
        "zodiac": None,
        "dark_triad_scores": None,
        "dark_triad_answers": None,
        "deep_analysis": None,
        "profile_locked": False,
        "last_updated": _now_iso(),
    }

    if memory is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        memory.memory_json = memory_data

    db.commit()
