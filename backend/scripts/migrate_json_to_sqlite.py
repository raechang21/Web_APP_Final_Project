"""
One-shot migration: import legacy chat_histories/{user}_memory.json (and any
chat_histories/{user}/conversation_*.json) into the SQLite database.

Run from backend/:
    .venv/bin/python -m scripts.migrate_json_to_sqlite

Idempotent: re-running upserts users and memories, and skips already-imported
conversations (matched by started_at timestamp).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# Allow running as a script (`python -m scripts.migrate_json_to_sqlite`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR
from app.db import SessionLocal, init_db
from app.models_db.conversation import Conversation, Message
from app.models_db.memory import UserMemory
from app.models_db.user import User


def parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def import_memory_file(db, path: Path) -> str | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    user_name = data.get("user_name") or path.stem.removesuffix("_memory")
    if not user_name:
        return None

    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    user.mbti = data.get("mbti") or user.mbti
    user.bigfive_scores = data.get("bigfive_scores") or user.bigfive_scores
    user.zodiac = data.get("zodiac") or user.zodiac
    user.dark_triad_scores = data.get("dark_triad_scores") or user.dark_triad_scores

    mem = db.get(UserMemory, user_name)
    if mem is None:
        mem = UserMemory(user_name=user_name, memory_json=data)
        db.add(mem)
    else:
        mem.memory_json = data

    return user_name


def import_conversation_dir(db, user_dir: Path) -> int:
    user_name = user_dir.name
    if db.get(User, user_name) is None:
        db.add(User(user_name=user_name))

    imported = 0
    for f in sorted(user_dir.glob("conversation_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        started = parse_dt(data.get("started_at")) or datetime.utcnow()

        existing = (
            db.query(Conversation)
            .filter_by(user_name=user_name, started_at=started)
            .first()
        )
        if existing is not None:
            continue

        conv = Conversation(
            user_name=user_name,
            started_at=started,
            ended_at=parse_dt(data.get("ended_at")),
        )
        db.add(conv)
        db.flush()
        for m in data.get("messages", []):
            db.add(
                Message(
                    conversation_id=conv.id,
                    role=m.get("role", "user"),
                    content=m.get("content", ""),
                    created_at=parse_dt(m.get("timestamp")) or started,
                )
            )
        imported += 1
    return imported


def main() -> None:
    init_db()
    chat_root = Path(DATA_DIR) / "chat_histories"
    if not chat_root.exists():
        print(f"No chat_histories at {chat_root}; nothing to do.")
        return

    db = SessionLocal()
    try:
        users = []
        for memory_file in chat_root.glob("*_memory.json"):
            name = import_memory_file(db, memory_file)
            if name:
                users.append(name)

        total_convs = 0
        for sub in chat_root.iterdir():
            if sub.is_dir():
                total_convs += import_conversation_dir(db, sub)

        db.commit()
        print(f"Imported {len(users)} users, {total_convs} conversations.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
