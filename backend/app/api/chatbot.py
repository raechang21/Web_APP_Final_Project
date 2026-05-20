import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..config import BIG_FIVE_DIMENSIONS
from ..db import get_db
from ..domain.dark_triad_result import DarkTriadResult
from ..domain.test_results import BigFiveResult, MBTIResult, ZodiacResult
from ..schemas.chatbot import ChatMessageIn
from ..services.chat_memory import repository as chat_memory
from ..services.chat_memory.welcome import build_returning_user_welcome
from ..services.llm.chatbot_prompts import ChatBotPrompts
from ..services.llm.gemini_client import GeminiClient


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


def _build_trait_map() -> dict[str, tuple[str, str]]:
    trait_map = {label: (key, label) for key, label in BIG_FIVE_DIMENSIONS.items()}
    trait_map.update({key: (key, label) for key, label in BIG_FIVE_DIMENSIONS.items()})
    return trait_map


TRAIT_MAP = _build_trait_map()

SCORE_QUERY_PATTERNS = [
    r"(我的|我).{0,5}(開放性|盡責性|外向性|友善性|神經質|openness|conscientiousness|extraversion|agreeableness|neuroticism).{0,8}(幾分|分數|多少)",
    r"(開放性|盡責性|外向性|友善性|神經質|openness|conscientiousness|extraversion|agreeableness|neuroticism).{0,8}(幾分|分數|多少)",
    r"(測驗結果|分數|成績).{0,8}(是多少|多少|幾分)",
]


def _is_score_query(message: str) -> bool:
    return any(re.search(pattern, message, re.IGNORECASE) for pattern in SCORE_QUERY_PATTERNS)


def _score_level(score: float) -> tuple[str, str]:
    if score <= 2.0:
        return "低", "相對不明顯"
    if score <= 3.0:
        return "偏低", "稍微保守"
    if score <= 4.0:
        return "中等", "平衡"
    if score <= 5.0:
        return "偏高", "相對明顯"
    return "高", "非常明顯"


def _score_response(message: str, big_five: BigFiveResult | None) -> str:
    if not big_five:
        return "你目前還沒有 Big Five 測驗結果。請先完成 Big Five 測驗，我才能告訴你分數。"

    asked = next((trait for trait in TRAIT_MAP if trait.lower() in message.lower()), None)
    if asked:
        attr, display = TRAIT_MAP[asked]
        score = getattr(big_five, attr)
        level, desc = _score_level(score)
        return (
            f"你的 {display} 分數是 {score:.1f}/6.0，屬於「{level}」。"
            f"這代表這項特質在你身上{desc}。"
        )

    scores = big_five.to_dict()
    return "\n".join(
        ["這是你的 Big Five 測驗結果："]
        + [
            f"{label}：{scores[key]:.1f}/6.0"
            for key, label in BIG_FIVE_DIMENSIONS.items()
        ]
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persist_memory(request: Request, db: Session) -> None:
    session = request.session
    user_name = session.get("user_name")
    if not user_name:
        return

    chat_memory.save_chat_memory(
        db,
        user_name=user_name,
        chat_messages=session.get("chat_messages", []),
        mbti=session.get("mbti"),
        big_five_scores=session.get("big_five_scores"),
        zodiac=session.get("zodiac"),
        dark_triad_scores=session.get("dark_triad_scores"),
    )


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/stream")
def chatbot_stream(
    payload: ChatMessageIn,
    request: Request,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(400, "訊息不能是空的")

    session = request.session
    user_name = session.get("user_name")
    chat_history: list[dict] = session.get("chat_messages", [])

    if not user_name and not chat_history:
        potential_name = user_message
        memory = chat_memory.load_memory(db, potential_name)

        if memory:
            session["user_name"] = potential_name
            session["mbti"] = memory.get("mbti")
            session["big_five_scores"] = memory.get("big_five_scores")
            session["zodiac"] = memory.get("zodiac")
            session["dark_triad_scores"] = memory.get("dark_triad_scores")
            session["chat_messages"] = []

            welcome = build_returning_user_welcome(potential_name, memory)

            def generate_returning_user():
                yield _sse({"chunk": welcome})
                yield _sse({"done": True})

            return StreamingResponse(
                generate_returning_user(),
                media_type="text/event-stream",
            )

        session["user_name"] = potential_name
        session["chat_messages"] = []

        first_prompt = f"使用者的名字是：{potential_name}。請產生第一次見面的聊天回覆。"
        first_system_prompt = ChatBotPrompts.first_reply_after_name_prompt()

        def generate_new_user():
            full = ""
            try:
                client = GeminiClient()
                for chunk in client.generate_stream(
                    first_prompt,
                    system_prompt=first_system_prompt,
                ):
                    if chunk:
                        full += chunk
                        yield _sse({"chunk": chunk})

                session["chat_messages"] = [
                    {
                        "role": "assistant",
                        "content": full,
                        "timestamp": _now_iso(),
                    }
                ]
                yield _sse({"done": True})
            except Exception as error:
                yield _sse({"error": str(error)})

        return StreamingResponse(generate_new_user(), media_type="text/event-stream")

    mbti = session.get("mbti")
    big_five_scores = session.get("big_five_scores")
    zodiac = session.get("zodiac")
    dark_triad_scores = session.get("dark_triad_scores")

    mbti_result = MBTIResult(type=mbti) if mbti else None
    big_five_result = BigFiveResult.from_scores(big_five_scores)
    zodiac_result = ZodiacResult(sign=zodiac) if zodiac else None
    dark_triad_result = (
        DarkTriadResult(**dark_triad_scores) if dark_triad_scores else None
    )

    system_prompt = ChatBotPrompts.system_prompt_with_results(
        mbti=mbti_result,
        big_five=big_five_result,
        zodiac=zodiac_result,
        dark_triad=dark_triad_result,
    )

    if _is_score_query(user_message):
        direct = _score_response(user_message, big_five_result)
        chat_history.append(
            {"role": "user", "content": user_message, "timestamp": _now_iso()}
        )
        chat_history.append(
            {"role": "assistant", "content": direct, "timestamp": _now_iso()}
        )
        session["chat_messages"] = chat_history
        _persist_memory(request, db)

        def generate_direct():
            yield _sse({"chunk": direct})
            yield _sse({"done": True})

        return StreamingResponse(generate_direct(), media_type="text/event-stream")

    recent_history = chat_history[-6:]
    formatted = ChatBotPrompts.format_user_message(user_message, recent_history)
    chat_history.append(
        {"role": "user", "content": user_message, "timestamp": _now_iso()}
    )

    def generate_llm():
        full = ""
        try:
            client = GeminiClient()
            for chunk in client.generate_stream(
                formatted,
                system_prompt=system_prompt,
            ):
                if chunk:
                    full += chunk
                    yield _sse({"chunk": chunk})

            chat_history.append(
                {"role": "assistant", "content": full, "timestamp": _now_iso()}
            )
            session["chat_messages"] = chat_history
            chat_memory.save_conversation(db, user_name = user_name, messages = chat_history)
            _persist_memory(request, db)
            yield _sse({"done": True})
            
        except Exception as error:
            yield _sse({"error": str(error)})

    return StreamingResponse(
        generate_llm(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/clear")
def chatbot_clear(request: Request) -> dict:
    request.session["chat_messages"] = []
    return {"success": True}


@router.post("/save")
def chatbot_save(request: Request, db: Session = Depends(get_db)) -> dict:
    session = request.session
    user_name = session.get("user_name")
    messages = session.get("chat_messages", [])

    if not user_name:
        raise HTTPException(400, "尚未設定使用者名稱")

    chat_memory.save_conversation(db, user_name = user_name, messages = messages)
    _persist_memory(request, db)

    return {"success": True, "message": "聊天紀錄已儲存"}


@router.get("/history")
def chatbot_history(request: Request) -> dict:
    return {"messages": request.session.get("chat_messages", [])}


@router.get("/history/all")
def chatbot_history_all(request: Request, db: Session = Depends(get_db)) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        return {"histories": []}

    return {
        "user_name": user_name,
        "histories": chat_memory.list_conversations(db, user_name),
    }


@router.delete("/history/all")
def chatbot_delete_all_histories(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        raise HTTPException(400, "尚未設定使用者名稱")

    count = chat_memory.delete_all_conversations(db, user_name=user_name)
    return {"success": True, "deleted": count}


@router.delete("/history/{conversation_id}")
def chatbot_delete_history(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        raise HTTPException(400, "尚未設定使用者名稱")

    success = chat_memory.delete_conversation(
        db,
        user_name=user_name,
        conversation_id=conversation_id,
    )
    if not success:
        raise HTTPException(404, "找不到聊天紀錄")

    return {"success": True}
