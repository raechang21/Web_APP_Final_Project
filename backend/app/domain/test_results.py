from dataclasses import dataclass

from ..config import (
    BIG_FIVE_DIMENSION_KEYS, 
    DARK_TRIAD_DIMENSION_KEYS, 
    SCALE_MIN, 
    SCALE_MAX, 
    SCORE_LABELS_ZH, 
    ZODIAC_SIGNS
)


VALID_MBTI_CHARS = {
    0: {"E", "I"},
    1: {"S", "N"},
    2: {"T", "F"},
    3: {"J", "P"},
}


@dataclass
class MBTIResult:
    type: str
    
    def __post_init__(self) -> None:
        value = self.type.upper().strip()
        
        if len(value) != 4:
            raise ValueError("MBTI 類型必須是 4 個字母")
        
        for i, char in enumerate(value):
            if char not in VALID_MBTI_CHARS[i]:
                raise ValueError(f"MBTI 第 {i + 1} 個字母必須是 {VALID_MBTI_CHARS[i]} 之一")
        
        self.type = value


@dataclass
class BigFiveResult:
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    
    def __post_init__(self):
        for dimension in BIG_FIVE_DIMENSION_KEYS:
            score = getattr(self, dimension)
            if not SCALE_MIN <= score <= SCALE_MAX:
                raise ValueError(f"{dimension} 分數 {score} 超出有效範圍 (1.0 - 6.0)，請檢查測驗結果")
    
    @classmethod
    def from_scores(cls, scores: dict | None) -> "BigFiveResult | None":
        if not scores:
            return None

        try:
            return cls(**scores)
        except ValueError:
            corrected = {
                key: max(SCALE_MIN, min(SCALE_MAX, value))
                for key, value in scores.items()
            }
            return cls(**corrected)
    
    def to_dict(self) -> dict[str, float]:
        return {
            'openness': self.openness,
            'conscientiousness': self.conscientiousness,
            'extraversion': self.extraversion,
            'agreeableness': self.agreeableness,
            'neuroticism': self.neuroticism
        }
    
    def get_label(self, dimension: str) -> str:
        score = getattr(self, dimension)
        if 1.0 <= score <= 3.0:
            return SCORE_LABELS_ZH["low"]
        elif 3.1 <= score <= 4.5:
            return SCORE_LABELS_ZH["below_average"]
        else:
            return SCORE_LABELS_ZH["high"]


@dataclass
class ZodiacResult:
    sign: str
    
    def __post_init__(self):
        if self.sign not in ZODIAC_SIGNS:
            raise ValueError(f"無效的星座名稱: {self.sign}")
