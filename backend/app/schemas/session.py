from pydantic import BaseModel, Field


class QuickLoginIn(BaseModel):
    name: str = Field(min_length = 1)


class StartSessionIn(BaseModel):
    name: str = Field(min_length = 1)
    
    
class SessionOut(BaseModel):
    user_name: str | None = None
    mbti: str | None = None
    big_five_scores: dict | None = None
    zodiac: str | None = None
    dark_triad_scores: dict | None = None
    has_results: bool = False
    has_analysis: bool = False
    is_quick_login: bool = False
    welcome_message: str | None = None
