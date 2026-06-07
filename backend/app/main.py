from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .db import init_db
from .routers import chatbot, debug, results, session as session_router, tests


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Personality Paradox API", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="pp_session",
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=settings.COOKIE_SECURE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


app.include_router(session_router.router)
app.include_router(tests.router)
app.include_router(results.router)
app.include_router(chatbot.router)
app.include_router(debug.router)
