"""
使用者資料模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .test_result import MBTIResult, BigFiveResult, ZodiacResult
from .dark_triad_result import DarkTriadResult


@dataclass
class UserProfile:
    """使用者完整資料"""
    mbti: Optional[MBTIResult] = None
    bigfive: Optional[BigFiveResult] = None
    zodiac: Optional[ZodiacResult] = None
    dark_triad: Optional[DarkTriadResult] = None
    test_date: datetime = None
    
    def __post_init__(self):
        if self.test_date is None:
            self.test_date = datetime.now()
    
    def is_complete(self) -> bool:
        """檢查是否完成所有測驗"""
        return all([self.mbti, self.bigfive, self.zodiac])
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            'mbti': self.mbti.type if self.mbti else None,
            'bigfive': self.bigfive.to_dict() if self.bigfive else None,
            'zodiac': self.zodiac.sign if self.zodiac else None,
            'dark_triad': self.dark_triad.to_dict() if self.dark_triad else None,
            'test_date': self.test_date.isoformat()
        }
