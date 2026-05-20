from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
VAR_DIR = BACKEND_ROOT / "var"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = str(BACKEND_ROOT / ".env"),
        env_file_encoding = "utf-8",
        extra = "ignore",
    )

    SECRET_KEY: str = "dev-secret-change-me"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    DATABASE_URL: str = f"sqlite:///{BACKEND_ROOT / 'var' / 'personality_paradox.db'}"
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    SESSION_MAX_AGE: int = 60 * 60 * 2  # 2 hours


settings = Settings()


# Domain constants
BIG_FIVE_QUESTIONS_COUNT = 15
SCALE_MIN = 1
SCALE_MAX = 6

SCORE_LABELS = {
    "low": (1.0, 2.5),
    "below_average": (2.6, 3.5),
    "above_average": (3.6, 4.5),
    "high": (4.6, 6.0),
}

SCORE_LABELS_ZH = {
    "low": "低",
    "below_average": "偏低",
    "above_average": "偏高",
    "high": "高",
}

BIG_FIVE_DIMENSIONS = {
    "openness": "開放性",
    "conscientiousness": "盡責性",
    "extraversion": "外向性",
    "agreeableness": "友善性",
    "neuroticism": "神經質",
}

BIG_FIVE_DIMENSION_KEYS = tuple(BIG_FIVE_DIMENSIONS.keys())

ZODIAC_SIGNS = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座",
    "獅子座", "處女座", "天秤座", "天蠍座",
    "射手座", "摩羯座", "水瓶座", "雙魚座",
]

DARK_TRIAD_DIMENSIONS = {
    "machiavellianism": "馬基維利主義",
    "narcissism": "自戀",
    "psychopathy": "精神病態",
}

DARK_TRIAD_DIMENSION_KEYS = tuple(DARK_TRIAD_DIMENSIONS.keys())

MBTI_TEST_URL = "https://www.16personalities.com/tw/%E6%80%A7%E6%A0%BC%E6%B8%AC%E8%A9%A6"

COLORS = {
    "primary": "#4A90E2",
    "secondary": "#E8F4F8",
    "accent": "#2E5C8A",
    "text": "#2C3E50",
    "success": "#5DADE2",
    "warning": "#F39C12",
    "openness": "#4A90E2",
    "conscientiousness": "#52C41A",
    "extraversion": "#FAAD14",
    "agreeableness": "#9254DE",
    "neuroticism": "#F5222D",
}

BIG_FIVE_QUESTIONS_FILE = str(DATA_DIR / "big_five_questions.json")
DARK_TRIAD_QUESTIONS_FILE = str(DATA_DIR / "dark_triad_questions.json")
