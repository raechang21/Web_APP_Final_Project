from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so they're registered with Base.metadata before create_all.
    from .models_db import user, conversation, memory  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_schema()


def _migrate_sqlite_schema() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.begin() as conn: 
        if "users" in table_names:
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "deep_analysis" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN deep_analysis VARCHAR"))

        if "messages" in table_names:
            message_columns = {column["name"] for column in inspector.get_columns("messages")}
            if "scope" not in message_columns:
                conn.execute(text("ALTER TABLE messages ADD COLUMN scope VARCHAR DEFAULT 'in_scope'"))
