import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.tests import ChatMessageIn
from ..services import chat_memory
from ..services.llm.chatbot_prompts import ChatBotPrompts
from ..services.llm.gemini_client import GeminiClient
from ..services.llm.error_handling import classify_llm_error, DEFAULT_LLM_ERROR
from ..services.models.dark_triad_result import DarkTriadResult
from ..services.models.test_result import (
    BigFiveResult,
    MBTIResult,
    ZodiacResult,
)


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

llm_client = GeminiClient()

TRAIT_MAP = {
    "開放性": ("openness", "開放性"),
    "盡責性": ("conscientiousness", "盡責性"),
    "外向性": ("extraversion", "外向性"),
    "友善性": ("agreeableness", "友善性"),
    "神經質": ("neuroticism", "神經質"),
}

SCORE_QUERY_PATTERNS = [
    r"(我的|我|自己的?)(.{0,3})(開放性|盡責性|外向性|友善性|神經質|conscientiousness|openness|extraversion|agreeableness|neuroticism)(.{0,5})(是?幾分|多少分|分數|是多少)",
    r"(開放性|盡責性|外向性|友善性|神經質)(.{0,3})(幾分|多少|分數)",
    r"(測驗結果|分數|成績)(.{0,3})(是什麼|是多少|代表什麼)",
]


def _is_score_query(message: str) -> bool:
    return any(re.search(p, message, re.IGNORECASE) for p in SCORE_QUERY_PATTERNS)


def _score_response(message: str, bigfive: BigFiveResult | None) -> str:
    if not bigfive:
        return "你還沒有完成測驗呢！要不要先去做測驗，了解自己的人格特質？"

    asked = next((t for t in TRAIT_MAP if t in message), None)
    if asked:
        attr, display = TRAIT_MAP[asked]
        score = getattr(bigfive, attr)
        if score <= 2.0:
            level, desc = "極低", "相對較少"
        elif score <= 3.0:
            level, desc = "偏低", "中等偏少"
        elif score <= 4.0:
            level, desc = "中等", "適中"
        elif score <= 5.0:
            level, desc = "偏高", "中等偏多"
        else:
            level, desc = "高", "相對突出"
        return (
            f"根據你的測驗結果，你的{display}分數是 {score:.1f}/6.0，屬於「{level}」的程度。"
            f"這表示你在這個特質上{desc}。\n\n"
            "有什麼想進一步了解的嗎？例如這個特質對你的影響，或是如何運用這個特點？"
        )

    parts = ["這是你的 Big Five 測驗結果：\n"]
    parts.append(f"• 開放性：{bigfive.openness:.1f}/6.0")
    parts.append(f"• 盡責性：{bigfive.conscientiousness:.1f}/6.0")
    parts.append(f"• 外向性：{bigfive.extraversion:.1f}/6.0")
    parts.append(f"• 友善性：{bigfive.agreeableness:.1f}/6.0")
    parts.append(f"• 神經質：{bigfive.neuroticism:.1f}/6.0\n")
    parts.append("想聊聊這些特質對你的影響嗎？")
    return "\n".join(parts)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persist_memory_with_messages(request: Request, db: Session, chat_messages: list[dict]) -> None:
    s = request.session
    user_name = s.get("user_name")
    if not user_name:
        return
    chat_memory.save_chat_memory(
        db,
        user_name=user_name,
        chat_messages=chat_messages,
        mbti=s.get("mbti"),
        bigfive_scores=s.get("bigfive_scores"),
        zodiac=s.get("zodiac"),
        dark_triad_scores=s.get("dark_triad_scores"),
    )


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _resolve_conversation_id(
    db: Session,
    *,
    user_name: str,
    requested_id: int | None,
) -> int | None:
    if requested_id is None:
        return None
    conversation = chat_memory.get_conversation(
        db,
        user_name=user_name,
        conversation_id=requested_id,
    )
    if not conversation:
        raise HTTPException(404, "找不到該對話")
    return conversation.id


@router.post("/stream")
def chatbot_stream(
    payload: ChatMessageIn,
    request: Request,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(400, "Empty message")

    s = request.session
    user_name = s.get("user_name")
    active_conversation_id = (
        _resolve_conversation_id(
            db,
            user_name=user_name,
            requested_id=payload.conversation_id,
        )
        if user_name and payload.conversation_id is not None
        else None
    )
    chat_history = (
        chat_memory.recent_prompt_context_messages(
            db,
            user_name,
            limit=12,
            conversation_id=active_conversation_id,
        )
        if user_name and active_conversation_id is not None
        else []
    )
    previous_scope = (
        chat_memory.latest_message_scope(
            db,
            user_name,
            conversation_id=active_conversation_id,
        )
        if user_name
        else None
    )

    # First message → treat as user name; check DB for returning user.
    if not user_name and not chat_history:
        potential_name = user_message
        memory = chat_memory.load_memory(db, potential_name)

        if memory:
            bigfive_scores = memory.get("bigfive_scores") or memory.get("big_five_scores")
            s["user_name"] = potential_name
            s["mbti"] = memory.get("mbti")
            s["bigfive_scores"] = bigfive_scores
            s["bigfive_answers"] = memory.get("bigfive_answers")
            s["zodiac"] = memory.get("zodiac")
            s["dark_triad_scores"] = memory.get("dark_triad_scores")
            s["dark_triad_answers"] = memory.get("dark_triad_answers")
            s["profile_locked"] = memory.get("profile_locked", True)

            welcome = f"嗨，{potential_name}，歡迎回來！很高興再次見到你。"
            summaries = memory.get("conversation_summaries") or []
            if summaries:
                topics = summaries[-1].get("topics") or []
                if topics:
                    preview = topics[0][:20] + ("..." if len(topics[0]) > 20 else "")
                    welcome += f" 我記得上次你提到『{preview}』，後來還好嗎？"
            else:
                welcome += " 今天想聊什麼呢？"

            def gen_back():
                yield _sse({"conversation_id": None})
                yield _sse({"chunk": welcome})
                yield _sse({"done": True})

            return StreamingResponse(gen_back(), media_type="text/event-stream")

        s["user_name"] = potential_name

        first_reply_prompt = ChatBotPrompts.first_reply_after_name()
        formatted = f"使用者的名字是：{potential_name}\n請產生第一次打招呼的回覆。"

        def gen_new():
            full = ""
            try:
                for chunk in llm_client.generate_stream(
                    formatted,
                    system_prompt=first_reply_prompt,
                    num_predict=256,
                ):
                    if chunk:
                        full += chunk
                        yield _sse({"chunk": chunk})

                # optional: save assistant welcome message to DB
                welcome_messages = [
                    {
                        "role": "assistant",
                        "content": full,
                        "timestamp": _now_iso(),
                        "scope": "in_scope",
                    }
                ]
                chat_memory.save_conversation(
                    db,
                    user_name=potential_name,
                    messages=welcome_messages,
                )

                latest = chat_memory.latest_conversation(db, potential_name)
                yield _sse({"conversation_id": latest.id if latest else None})
                yield _sse({"done": True})
            except Exception as e:
                yield _sse({"error": str(e)})
                yield _sse({"done": True})

        return StreamingResponse(gen_new(), media_type="text/event-stream")

    # Normal conversation flow.
    mbti = s.get("mbti")
    bigfive_scores = s.get("bigfive_scores")
    zodiac = s.get("zodiac")
    dark_triad_scores = s.get("dark_triad_scores")

    mbti_result = MBTIResult(type=mbti) if mbti else None

    bigfive_result = None
    if bigfive_scores:
        try:
            bigfive_result = BigFiveResult(**bigfive_scores)
        except ValueError:
            corrected = {k: max(0.0, min(7.0, v)) for k, v in bigfive_scores.items()}
            bigfive_result = BigFiveResult(**corrected)

    zodiac_result = ZodiacResult(sign=zodiac) if zodiac else None
    dark_triad_result = (
        DarkTriadResult(**dark_triad_scores) if dark_triad_scores else None
    )
    
    message_scope = llm_client.classify_scope_with_ai(user_message)

    if message_scope == "followup":
        if previous_scope == "out_of_scope" or previous_scope is None:
            message_scope = "out_of_scope"

    # Score query short-circuit (no LLM call).
    if _is_score_query(user_message):
        direct = _score_response(user_message, bigfive_result)
        user_entry = {
            "role": "user",
            "content": user_message,
            "timestamp": _now_iso(),
            "scope": "in_scope",
        }
        assistant_entry = {
            "role": "assistant",
            "content": direct,
            "timestamp": _now_iso(),
            "scope": "in_scope",
        }
        if active_conversation_id:
            chat_memory.append_message_to_conversation(
                db,
                conversation_id=active_conversation_id,
                message=user_entry,
            )
        else:
            conversation = chat_memory.create_conversation_with_message(
                db,
                user_name=user_name,
                message=user_entry,
            )
            active_conversation_id = conversation.id if conversation else None
        if active_conversation_id:
            chat_memory.append_message_to_conversation(
                db,
                conversation_id=active_conversation_id,
                message=assistant_entry,
            )
        _persist_memory_with_messages(request, db, [user_entry, assistant_entry])

        def gen_direct():
            yield _sse({"conversation_id": active_conversation_id})
            yield _sse({"chunk": direct})
            yield _sse({"done": True})

        return StreamingResponse(gen_direct(), media_type="text/event-stream")

    # Trim history to last 6 messages.
    recent_history = chat_history[-6:]

    if message_scope == "out_of_scope":
        formatted = user_message
        system_prompt = ChatBotPrompts.out_of_scope_system_prompt()
    else:
        formatted = ChatBotPrompts.format_user_message(user_message, recent_history)
        system_prompt = ChatBotPrompts.system_prompt_with_results(
            mbti=mbti_result,
            bigfive=bigfive_result,
            zodiac=zodiac_result,
            dark_triad=dark_triad_result,
        )

    user_entry = {
        "role": "user",
        "content": user_message,
        "timestamp": _now_iso(),
        "scope": message_scope,
    }
    
    if active_conversation_id:
        chat_memory.append_message_to_conversation(
            db,
            conversation_id=active_conversation_id,
            message=user_entry,
        )
        conversation_id = active_conversation_id
    else:
        conversation = chat_memory.create_conversation_with_message(
            db,
            user_name=user_name,
            message=user_entry,
        )
        conversation_id = conversation.id if conversation else None

    def gen_llm():
        full = ""
        try:
            yield _sse({"conversation_id": conversation_id})
            for chunk in llm_client.generate_stream(formatted, system_prompt):
                if not chunk:
                    continue

                llm_error = classify_llm_error(chunk)
                if llm_error:
                    error_entry = {
                        "role": "assistant",
                        "content": llm_error.message,
                        "timestamp": _now_iso(),
                        "scope": message_scope,
                    }

                    if conversation_id:
                        chat_memory.append_message_to_conversation(
                            db,
                            conversation_id=conversation_id,
                            message=error_entry,
                        )

                    yield _sse({"error_code": llm_error.code, "message": llm_error.message})
                    yield _sse({"done": True})
                    return

                full += chunk
                yield _sse({"chunk": chunk})
            assistant_scope = "followup" if message_scope == "out_of_scope" else message_scope
            assistant_entry = {
                "role": "assistant",
                "content": full,
                "timestamp": _now_iso(),
                "scope": assistant_scope,
            }
            if conversation_id:
                chat_memory.append_message_to_conversation(
                    db,
                    conversation_id=conversation_id,
                    message=assistant_entry,
                )
            _persist_memory_with_messages(request, db, [user_entry, assistant_entry])
            yield _sse({"done": True})
        except Exception as e:
            llm_error = classify_llm_error(str(e)) or DEFAULT_LLM_ERROR

            error_entry = {
                "role": "assistant",
                "content": llm_error.message,
                "timestamp": _now_iso(),
                "scope": message_scope,
            }

            if conversation_id:
                chat_memory.append_message_to_conversation(
                    db,
                    conversation_id=conversation_id,
                    message=error_entry,
                )

            yield _sse({"error_code": llm_error.code, "message": llm_error.message})
            yield _sse({"done": True})
    
    return StreamingResponse(
        gen_llm(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/clear")
def chatbot_clear(request: Request) -> dict:
    return {"success": True}


@router.post("/save")
def chatbot_save(request: Request, db: Session = Depends(get_db)) -> dict:
    s = request.session
    user_name = s.get("user_name")
    if not user_name:
        raise HTTPException(400, "尚未取得使用者名稱")
    return {"success": True, "message": "對話已保存"}


@router.get("/history")
def chatbot_history(request: Request, db: Session = Depends(get_db)) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        return {"conversation_id": None, "messages": []}
    conversation = chat_memory.latest_conversation(db, user_name)
    return {
        "conversation_id": conversation.id if conversation else None,
        "messages": chat_memory.latest_conversation_messages(db, user_name),
    }


@router.get("/history/all")
def chatbot_history_all(request: Request, db: Session = Depends(get_db)) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        return {"histories": []}
    return {
        "user_name": user_name,
        "histories": chat_memory.list_conversations(db, user_name),
    }


@router.get("/history/conversation/{conversation_id}")
def chatbot_history_by_conversation(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        raise HTTPException(400, "尚未取得使用者名稱")

    messages = chat_memory.conversation_messages(
        db,
        user_name=user_name,
        conversation_id=conversation_id,
    )
    if messages is None:
        raise HTTPException(404, "找不到該對話")

    return {"conversation_id": conversation_id, "messages": messages}


@router.delete("/history/all")
def chatbot_delete_all_histories(
    request: Request, db: Session = Depends(get_db)
) -> dict:
    user_name = request.session.get("user_name")
    if not user_name:
        raise HTTPException(400, "尚未取得使用者名稱")
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
        raise HTTPException(400, "尚未取得使用者名稱")
    success = chat_memory.delete_conversation(
        db, user_name=user_name, conversation_id=conversation_id
    )
    if not success:
        raise HTTPException(404, "找不到該對話")
    return {"success": True}
