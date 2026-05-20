from dataclasses import dataclass

from ..config import SCALE_MIN, SCALE_MAX, SCORE_LABELS, SCORE_LABELS_ZH


DARK_TRIAD_DIMENSIONS = (
    "machiavellianism",     # 馬基維利主義 
    "narcissism",       # 自戀
    "psychopathy",      # 精神病態
)


@dataclass
class DarkTriadResult:
    machiavellianism: float
    narcissism: float
    psychopathy: float
    
    def __post_init__(self) -> None:
        for dimension in DARK_TRIAD_DIMENSIONS:
            score = getattr(self, dimension)
            if not SCALE_MIN <= score <= SCALE_MAX:
                raise ValueError(f"{dimension} 分數 {score} 超出有效範圍 (1.0 - 6.0)，請檢查測驗結果")
    
    def get_label(self, dimension: str) -> str:
        score = getattr(self, dimension)
        
        for label, (min_score, max_score) in SCORE_LABELS.items():
            if min_score <= score <= max_score:
                return SCORE_LABELS_ZH[label]
        
        return SCORE_LABELS_ZH["below_average"]
    
    def to_dict(self) -> dict:
        return {
            'machiavellianism': self.machiavellianism,
            'narcissism': self.narcissism,
            'psychopathy': self.psychopathy
        }
    
    def get_average(self) -> float:
        return (self.machiavellianism + self.narcissism + self.psychopathy) / 3
