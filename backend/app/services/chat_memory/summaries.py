from datetime import datetime, timezone


MAX_KEY_TOPICS = 5
MAX_SUMMARY_TOPICS = 3
MAX_STORED_SUMMARIES = 3
MIN_TOPIC_LENGTH = 5


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_key_topics(chat_messages: list[dict]) -> list[str]:
    return [
        message["content"]
        for message in chat_messages
        if message.get("role") == "user"
        and len(message.get("content", "")) > MIN_TOPIC_LENGTH
    ]
    
    
def update_conversation_summaries(
    exisiting_memory: dict, 
    key_topics: list[str], 
    *, 
    timestamp: str | None = None, 
) -> list[dict]:
    summaries = list(exisiting_memory.get("conversation_summaries", []))
    
    if key_topics:
        summaries.append(
            {
                "date": timestamp or utc_now_iso(), 
                "topics": key_topics[:MAX_SUMMARY_TOPICS], 
            }
        )
        
    return summaries[-MAX_STORED_SUMMARIES:]


def build_memory_data(
    *, 
    existing_memory: dict, 
    user_name: str, 
    chat_messages: list[dict], 
    mbti: str | None, 
    big_five_scores: dict | None, 
    zodiac: str | None,
    dark_triad_scores: dict | None,
) -> dict:
    timestamp = utc_now_iso()
    key_topics = extract_key_topics(chat_messages)
    
    return {
        "user_name": user_name,
        "mbti": mbti,
        "big_five_scores": big_five_scores,
        "zodiac": zodiac,
        "dark_triad_scores": dark_triad_scores,
        "last_updated": timestamp,
        "total_conversations": existing_memory.get("total_conversations", 0) + 1,
        "conversation_summaries": update_conversation_summaries(
            existing_memory,
            key_topics,
            timestamp = timestamp,
        ),
        "key_topics": key_topics[:MAX_KEY_TOPICS],
    }
    