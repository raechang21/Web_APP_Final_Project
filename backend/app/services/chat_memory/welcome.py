DISTRESS_KEYWORDS = [
    "被罵",
    "難過",
    "生氣",
    "傷心",
    "困擾",
    "壓力",
    "焦慮",
    "煩惱",
    "挫折",
    "失望",
    "沮喪",
]

NEGATIVE_STATE_KEYWORDS = [
    "不好",
    "不開心",
    "不舒服",
    "痛苦",
    "難受",
]


def _build_topic_follow_up(topic: str) -> str:
    if "？" in topic or "?" in topic:
        return "有試著做看看嗎？"

    if any(keyword in topic for keyword in DISTRESS_KEYWORDS):
        return "後來還好嗎？"

    if any(keyword in topic for keyword in NEGATIVE_STATE_KEYWORDS):
        return "現在好一點了嗎？"

    return "後來怎麼樣了？"


def build_returning_user_welcome(name: str, memory: dict) -> str:
    welcome = f"嗨，{name}，歡迎回來！很高興再次見到你。"

    summaries = memory.get("conversation_summaries") or []
    if not summaries:
        return welcome + " 今天想聊什麼呢？"

    topics = summaries[-1].get("topics") or []
    if not topics:
        return welcome + " 今天想聊什麼呢？"

    topic = topics[0]
    preview = topic[:20] + ("..." if len(topic) > 20 else "")
    follow = _build_topic_follow_up(topic)

    return f"{welcome} 我記得上次你提到『{preview}』，{follow}"