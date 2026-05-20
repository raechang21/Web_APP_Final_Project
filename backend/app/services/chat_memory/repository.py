from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session

from ...models.conversation import Conversation, Message
from ...models.memory import UserMemory
from ...models.user import User
from .summaries import build_memory_data


def _normalize_memory(memory: dict) -> dict:
    if "big_five_scores" not in memory and "bigfive_scores" in memory:
        memory = dict(memory)
        memory["big_five_scores"] = memory["bigfive_scores"]
    return memory


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
    memory = db.get(UserMemory, user_name)
    return _normalize_memory(memory.memory_json) if memory else None


def save_chat_memory(
    db: Session,
    *,
    user_name: str,
    chat_messages: list[dict],
    mbti: str | None,
    big_five_scores: dict | None,
    zodiac: str | None,
    dark_triad_scores: dict | None,
) -> None:
    if not user_name:
        return

    upsert_user(
        db,
        user_name = user_name,
        mbti = mbti,
        big_five_scores = big_five_scores,
        zodiac=zodiac,
        dark_triad_scores=dark_triad_scores,
    )

    memory = db.get(UserMemory, user_name)
    existing = memory.memory_json if memory else {}

    memory_data = build_memory_data(
        existing_memory=existing,
        user_name=user_name,
        chat_messages=chat_messages,
        mbti=mbti,
        big_five_scores=big_five_scores,
        zodiac=zodiac,
        dark_triad_scores=dark_triad_scores,
    )

    if memory is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        memory.memory_json = memory_data

    db.commit()


def save_conversation(
    db: Session, 
    *, 
    user_name: str, 
    messages: list[dict]
) -> Conversation | None:
    if not user_name or not messages:
        return None

    upsert_user(db, user_name=user_name)

    conversation = Conversation(
        user_name = user_name,
        started_at = datetime.now(timezone.utc),
    )
    db.add(conversation)
    db.flush()
    
    for message in messages:
        timestamp = message.get("timestamp")
        try:
            created_at = (
                datetime.fromisoformat(timestamp)
                if timestamp
                else datetime.now(timezone.utc)
            )
        except ValueError:
            created_at = datetime.now(timezone.utc)
            
        db.add(
            Message(
                conversation_id = conversation.id,
                role = message.get("role", "user"),
                content = message.get("content", ""),
                created_at = created_at,
            )
        )
        
    conversation.ended_at = datetime.now(timezone.utc)
    db.commit()
    return conversation


def list_conversations(db: Session, user_name: str) -> list[dict]:
    conversations = (
        db.query(Conversation)
        .filter_by(user_name = user_name)
        .order_by(Conversation.started_at.desc())
        .all()
    )
   
    return [
        {
            "id": conversation.id,
            "timestamp": (
                conversation.started_at.isoformat()
                if conversation.started_at
                else None
            ),
            "message_count": len(conversation.messages),
            "preview": conversation.messages[0].content[:50]
            if conversation.messages
            else "",
        }
        for conversation in conversations
    ]


def delete_conversation(
    db: Session, 
    *, user_name: str, 
    conversation_id: int
) -> bool:
    conversation = (
        db.query(Conversation)
        .filter_by(id = conversation_id, user_name = user_name)
        .first()
    )
    
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True


def delete_all_conversations(db: Session, *, user_name: str) -> int:
    conversations = db.query(Conversation).filter_by(user_name = user_name).all()
    count = len(conversations)
    for conversation in conversations:
        db.delete(conversation)
        
    db.commit()
    return count
