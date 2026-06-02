from typing import Literal

from pydantic import BaseModel, Field


VALID_MBTI = {
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
}


class MBTIIn(BaseModel):
    mbti_type: str = Field(min_length=4, max_length=4)


class BigFiveAnswers(BaseModel):
    answers: dict[int, int]


class ZodiacIn(BaseModel):
    zodiac: str


class DarkTriadAnswers(BaseModel):
    answers: dict[int, int]


class QuickLoginIn(BaseModel):
    name: str = Field(min_length=1)


class StartSessionIn(BaseModel):
    name: str = Field(min_length=1)


class ChatMessageIn(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: int | None = None


class SessionOut(BaseModel):
    user_name: str | None = None
    mbti: str | None = None
    bigfive_scores: dict | None = None
    zodiac: str | None = None
    dark_triad_scores: dict | None = None
    has_results: bool = False
    has_analysis: bool = False
    is_quick_login: bool = False
    welcome_message: str | None = None
