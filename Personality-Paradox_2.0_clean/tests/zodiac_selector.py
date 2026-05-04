"""
星座選擇模組
"""

from typing import List
from models.test_result import ZodiacResult
from config import ZODIAC_SIGNS


def get_zodiac_signs() -> List[str]:
    """
    獲取所有星座列表
    
    Returns:
        星座名稱列表
    """
    return ZODIAC_SIGNS


def create_zodiac_result(zodiac_sign: str) -> ZodiacResult:
    """
    建立星座結果物件
    
    Args:
        zodiac_sign: 星座名稱
        
    Returns:
        ZodiacResult 物件
    """
    return ZodiacResult(sign=zodiac_sign)
