"""DB-backed user memory + conversation persistence (replaces the JSON files)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ..models_db.conversation import Conversation, Message
from ..models_db.memory import UserMemory
from ..models_db.user import User


def _serialize_messages(conv: Conversation) -> list[dict]:
    return [
        {
            "role": message.role,
            "content": message.content,
            "timestamp": message.created_at.isoformat() if message.created_at else None,
            "scope": message.scope,
        }
        for message in conv.messages
    ]


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
        if (
            m.get("role") == "user"
            and m.get("scope") in ["in_scope", "followup"]
            and len(m.get("content", "")) > 5
        )
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
        **existing,
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
                scope=m.get("scope", "in_scope"),
                created_at=created,
            )
        )
    conv.ended_at = datetime.now(timezone.utc)
    db.commit()
    return conv


def get_conversation(
    db: Session, *, user_name: str, conversation_id: int
) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter_by(id=conversation_id, user_name=user_name)
        .first()
    )


def latest_conversation(db: Session, user_name: str) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter_by(user_name=user_name)
        .order_by(Conversation.ended_at.desc(), Conversation.started_at.desc())
        .first()
    )


def list_conversations(db: Session, user_name: str) -> list[dict]:
    rows = (
        db.query(Conversation)
        .filter_by(user_name=user_name)
        .order_by(Conversation.ended_at.desc(), Conversation.started_at.desc())
        .all()
    )
    out = []
    for c in rows:
        first_user_message = next(
            (message.content for message in c.messages if message.role == "user"),
            c.messages[0].content if c.messages else "",
        )
        out.append(
            {
                "id": c.id,
                "timestamp": c.started_at.isoformat() if c.started_at else None,
                "message_count": len(c.messages),
                "preview": first_user_message[:50],
            }
        )
    return out


def latest_conversation_messages(db: Session, user_name: str) -> list[dict]:
    conv = latest_conversation(db, user_name)
    if not conv:
        return []

    return _serialize_messages(conv)


def conversation_messages(
    db: Session, *, user_name: str, conversation_id: int
) -> list[dict] | None:
    conv = get_conversation(db, user_name=user_name, conversation_id=conversation_id)
    if not conv:
        return None
    return _serialize_messages(conv)


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


def recent_prompt_context_messages(
    db: Session,
    user_name: str,
    limit: int = 12,
    conversation_id: int | None = None,
) -> list[dict]:
    query = (
        db.query(Message)
        .join(Conversation)
        .filter(Conversation.user_name == user_name)
        .filter(Message.scope.in_(["in_scope", "followup"]))
    )
    if conversation_id is not None:
        query = query.filter(Conversation.id == conversation_id)

    rows = query.order_by(Message.created_at.desc()).limit(limit).all()

    rows = list(reversed(rows))

    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": m.created_at.isoformat() if m.created_at else None,
            "scope": m.scope,
        }
        for m in rows
    ]


def create_conversation_with_message(
    db: Session,
    *,
    user_name: str,
    message: dict,
) -> Conversation | None:
    if not user_name or not message:
        return None

    upsert_user(db, user_name=user_name)

    conv = Conversation(user_name=user_name, started_at=datetime.now(timezone.utc))
    db.add(conv)
    db.flush()

    ts = message.get("timestamp")
    try:
        created = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
    except ValueError:
        created = datetime.now(timezone.utc)

    db.add(
        Message(
            conversation_id=conv.id,
            role=message.get("role", "user"),
            content=message.get("content", ""),
            scope=message.get("scope", "in_scope"),
            created_at=created,
        )
    )

    conv.ended_at = created
    db.commit()
    return conv


def append_message_to_conversation(
    db: Session,
    *,
    conversation_id: int,
    message: dict,
) -> None:
    conv = db.get(Conversation, conversation_id)
    if not conv:
        return

    ts = message.get("timestamp")
    try:
        created = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
    except ValueError:
        created = datetime.now(timezone.utc)

    db.add(
        Message(
            conversation_id=conversation_id,
            role=message.get("role", "assistant"),
            content=message.get("content", ""),
            scope=message.get("scope", "in_scope"),
            created_at=created,
        )
    )
    conv.ended_at = created
    db.commit()


def latest_message_scope(
    db: Session,
    user_name: str,
    conversation_id: int | None = None,
) -> str | None:
    query = (
        db.query(Message)
        .join(Conversation)
        .filter(Conversation.user_name == user_name)
    )
    if conversation_id is not None:
        query = query.filter(Conversation.id == conversation_id)

    message = query.order_by(Message.created_at.desc()).first()
    return message.scope if message else None
