"""
測驗結果資料結構
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class MBTIResult:
    """MBTI 測驗結果"""
    type: str  # 例如: "ENTJ"
    
    def __post_init__(self):
        """驗證 MBTI 類型格式"""
        if len(self.type) != 4:
            raise ValueError("MBTI 類型必須是 4 個字母")
        
        valid_chars = {
            0: ['E', 'I'],
            1: ['S', 'N'],
            2: ['T', 'F'],
            3: ['J', 'P']
        }
        
        for i, char in enumerate(self.type.upper()):
            if char not in valid_chars[i]:
                raise ValueError(f"MBTI 第 {i+1} 個字母必須是 {valid_chars[i]} 之一")
        
        self.type = self.type.upper()


@dataclass
class BigFiveResult:
    """Big Five 測驗結果"""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    
    def __post_init__(self):
        """驗證分數範圍（放寬限制以支援不同測驗版本）"""
        for dimension in ['openness', 'conscientiousness', 'extraversion', 
                         'agreeableness', 'neuroticism']:
            score = getattr(self, dimension)
            # 放寬範圍以支援不同的測驗計分方式
            if not (0.0 <= score <= 7.0):
                raise ValueError(f"{dimension} 分數 {score} 超出有效範圍 (0.0-7.0)，請檢查測驗結果")
    
    def to_dict(self) -> Dict[str, float]:
        """轉換為字典"""
        return {
            'openness': self.openness,
            'conscientiousness': self.conscientiousness,
            'extraversion': self.extraversion,
            'agreeableness': self.agreeableness,
            'neuroticism': self.neuroticism
        }
    
    def get_label(self, dimension: str) -> str:
        """獲取維度的文字標籤"""
        score = getattr(self, dimension)
        if 1.0 <= score <= 3.0:
            return "低"
        elif 3.1 <= score <= 4.5:
            return "中"
        else:
            return "高"


@dataclass
class ZodiacResult:
    """星座結果"""
    sign: str  # 星座名稱
    
    def __post_init__(self):
        """驗證星座名稱"""
        valid_signs = [
            "牡羊座", "金牛座", "雙子座", "巨蟹座",
            "獅子座", "處女座", "天秤座", "天蠍座",
            "射手座", "摩羯座", "水瓶座", "雙魚座"
        ]
        if self.sign not in valid_signs:
            raise ValueError(f"無效的星座名稱: {self.sign}")
