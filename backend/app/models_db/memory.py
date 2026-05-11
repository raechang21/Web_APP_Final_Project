from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserMemory(Base):
    __tablename__ = "user_memories"

    user_name: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.user_name", ondelete="CASCADE"),
        primary_key=True,
    )
    memory_json: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
