from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_name: Mapped[str] = mapped_column(String(100), primary_key = True)
    
    mbti: Mapped[str | None] = mapped_column(String, nullable = True)
    big_five_scores: Mapped[dict | None] = mapped_column(JSON, nullable = True)
    zodiac: Mapped[str | None] = mapped_column(String, nullable = True)
    dark_triad_scores: Mapped[dict | None] = mapped_column(JSON, nullable = True)
    
    deep_analysis: Mapped[str | None] = mapped_column(String, nullable = True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = _utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True), 
        default = _utcnow, 
        onupdate = _utcnow
    )
