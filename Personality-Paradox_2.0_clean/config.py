"""
配置檔 - Personality Paradox 系統
"""

# Ollama 設定
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT = 60  # 秒

# 測驗設定
BIG_FIVE_QUESTIONS_COUNT = 15
SCALE_MIN = 1
SCALE_MAX = 6

# 分數解讀標準
SCORE_LABELS = {
    "low": (1.0, 2.5),
    "below_average": (2.6, 3.5),
    "above_average": (3.6, 4.5),
    "high": (4.6, 6.0)
}

SCORE_LABELS_ZH = {
    "low": "低",
    "below_average": "偏低",
    "above_average": "偏高",
    "high": "高"
}

# Big Five 維度
BIG_FIVE_DIMENSIONS = {
    "openness": "開放性",
    "conscientiousness": "盡責性",
    "extraversion": "外向性",
    "agreeableness": "友善性",
    "neuroticism": "神經質"
}

# 星座列表
ZODIAC_SIGNS = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座", 
    "獅子座", "處女座", "天秤座", "天蠍座",
    "射手座", "摩羯座", "水瓶座", "雙魚座"
]

# MBTI 外部測驗連結
MBTI_TEST_URL = "https://www.16personalities.com/tw/%E6%80%A7%E6%A0%BC%E6%B8%AC%E8%A9%A6"

# 視覺化配色（淺藍色系）
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
    "neuroticism": "#F5222D"
}

# 檔案路徑
DATA_DIR = "data"
BIGFIVE_QUESTIONS_FILE = f"{DATA_DIR}/bigfive_questions.json"
DARK_TRIAD_QUESTIONS_FILE = f"{DATA_DIR}/dark_triad_questions.json"
ZODIAC_DATA_FILE = f"{DATA_DIR}/zodiac_traits.json"
