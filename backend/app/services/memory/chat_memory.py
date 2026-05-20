"""DB-backed user memory + conversation persistence (replaces the JSON files)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ...models.conversation import Conversation, Message
from ...models.memory import UserMemory
from ...models.user import User


def upsert_user(db: Session, *, user_name: str, **fields: Any) -> User:
    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    for key, value in fields.items():
        if value is not None:
            setattr(user, key, value)
    return user


def load_memory(db: Session, user_name: str) -> dict | None:
    mem = db.get(UserMemory, user_name)
    return mem.memory_json if mem else None


def save_chat_memory(
    db: Session,
    *,
    user_name: str,
    chat_messages: list[dict],
    mbti: str | None,
    bigfive_scores: dict | None,
    zodiac: str | None,
    dark_triad_scores: dict | None,
) -> None:
    if not user_name:
        return

    upsert_user(
        db,
        user_name=user_name,
        mbti=mbti,
        bigfive_scores=bigfive_scores,
        zodiac=zodiac,
        dark_triad_scores=dark_triad_scores,
    )

    mem = db.get(UserMemory, user_name)
    existing = mem.memory_json if mem else {}

    key_topics = [
        m["content"]
        for m in chat_messages
        if m.get("role") == "user" and len(m.get("content", "")) > 5
    ]

    summaries = list(existing.get("conversation_summaries", []))
    if key_topics:
        summaries.append(
            {
                "date": datetime.now(timezone.utc).isoformat(),
                "topics": key_topics[:3],
            }
        )
        summaries = summaries[-3:]

    memory_data = {
        "user_name": user_name,
        "mbti": mbti,
        "bigfive_scores": bigfive_scores,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad_scores,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_conversations": existing.get("total_conversations", 0) + 1,
        "conversation_summaries": summaries,
        "key_topics": key_topics[:5],
    }

    if mem is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        mem.memory_json = memory_data

    db.commit()


def save_conversation(
    db: Session, *, user_name: str, messages: list[dict]
) -> Conversation | None:
    if not user_name or not messages:
        return None

    upsert_user(db, user_name=user_name)

    conv = Conversation(user_name=user_name, started_at=datetime.now(timezone.utc))
    db.add(conv)
    db.flush()
    for m in messages:
        ts = m.get("timestamp")
        try:
            created = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
        except ValueError:
            created = datetime.now(timezone.utc)
        db.add(
            Message(
                conversation_id=conv.id,
                role=m.get("role", "user"),
                content=m.get("content", ""),
                created_at=created,
            )
        )
    conv.ended_at = datetime.now(timezone.utc)
    db.commit()
    return conv


def list_conversations(db: Session, user_name: str) -> list[dict]:
    rows = (
        db.query(Conversation)
        .filter_by(user_name=user_name)
        .order_by(Conversation.started_at.desc())
        .all()
    )
    out = []
    for c in rows:
        first = c.messages[0].content if c.messages else ""
        out.append(
            {
                "id": c.id,
                "timestamp": c.started_at.isoformat() if c.started_at else None,
                "message_count": len(c.messages),
                "preview": first[:50],
            }
        )
    return out


def delete_conversation(
    db: Session, *, user_name: str, conversation_id: int
) -> bool:
    """刪除使用者的某筆對話。回傳是否成功刪除。"""
    conv = (
        db.query(Conversation)
        .filter_by(id=conversation_id, user_name=user_name)
        .first()
    )
    if not conv:
        return False
    db.delete(conv)  # messages 會自動 cascade 刪掉
    db.commit()
    return True


def delete_all_conversations(db: Session, *, user_name: str) -> int:
    """刪除使用者的全部對話。回傳刪除筆數。"""
    convs = db.query(Conversation).filter_by(user_name=user_name).all()
    count = len(convs)
    for c in convs:
        db.delete(c)
    db.commit()
    return count