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
    zodiac: str | None = None, 
    dark_triad_scores: dict | None = None, 
    deep_analysis: str | None = None, 
) -> User: 
    user = db.get(User, user_name)
    
    if user is None:
        user = User(user_name = user_name)
        db.add(user)
        
    user.mbti = mbti
    user.bigfive_scores = bigfive_scores
    user.zodiac = zodiac
    user.dark_triad_scores = dark_triad_scores
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
    zodiac: str | None = None, 
    dark_triad_scores: dict | None = None, 
    deep_analysis: str | None = None, 
) -> None:
    if not user_name:
        return
    
    upsert_user(
        db,
        user_name = user_name, 
        mbti = mbti, 
        bigfive_scores = bigfive_scores, 
        zodiac = zodiac, 
        dark_triad_scores = dark_triad_scores, 
        deep_analysis = deep_analysis,
    )
    
    memory = db.get(UserMemory, user_name)
    existing = memory.memory_json if memory else {}
    
    memory_data = {
        **existing, 
        "user_name": user_name,
        "mbti": mbti,
        "bigfive_scores": bigfive_scores,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad_scores,
        "deep_analysis": deep_analysis,
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
        user.zodiac = None
        user.dark_triad_scores = None
        user.deep_analysis = None

    memory = db.get(UserMemory, user_name)
    memory_data = {
        "user_name": user_name,
        "mbti": None,
        "bigfive_scores": None,
        "zodiac": None,
        "dark_triad_scores": None,
        "deep_analysis": None,
        "last_updated": _now_iso(),
    }

    if memory is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        memory.memory_json = memory_data

    db.commit()
