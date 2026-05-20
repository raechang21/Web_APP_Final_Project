from pydantic import BaseModel, Field


VALID_MBTI = {
    "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP",
}


class MBTIIn(BaseModel):
    mbti_type: str = Field(min_length = 4, max_length = 4)


class BigFiveAnswers(BaseModel):
    answers: dict[int, int]


class ZodiacIn(BaseModel):
    zodiac: str


class DarkTriadAnswers(BaseModel):
    answers: dict[int, int]
