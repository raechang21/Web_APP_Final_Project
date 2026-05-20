from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite") 
    else {}
)

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args = connect_args, 
    echo = False
)

SessionLocal = sessionmaker(
    bind = engine, 
    autoflush = False, 
    autocommit = False, 
    expire_on_commit = False
)


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
    from .models import user, conversation, memory  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
