"""
星座輔助函數 - 生日轉星座判斷
"""

from datetime import datetime
import re


def parse_birthday(input_str: str) -> tuple:
    """
    解析生日字串
    
    Args:
        input_str: 生日輸入（例如：3/15、3月15日、03-15）
        
    Returns:
        (month, day) 或 (None, None) 如果解析失敗
    """
    input_str = input_str.strip()
    
    # 模式1: 3/15, 03/15
    pattern1 = r'(\d{1,2})[/\-](\d{1,2})'
    match = re.match(pattern1, input_str)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return (month, day) if validate_date(month, day) else (None, None)
    
    # 模式2: 3月15日, 03月15日
    pattern2 = r'(\d{1,2})月(\d{1,2})日?'
    match = re.match(pattern2, input_str)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return (month, day) if validate_date(month, day) else (None, None)
    
    # 模式3: 0315, 315
    pattern3 = r'(\d{1,2})(\d{2})'
    match = re.match(pattern3, input_str)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return (month, day) if validate_date(month, day) else (None, None)
    
    return (None, None)


def validate_date(month: int, day: int) -> bool:
    """
    驗證日期有效性
    
    Args:
        month: 月份
        day: 日期
        
    Returns:
        是否有效
    """
    if month < 1 or month > 12:
        return False
    
    days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    if day < 1 or day > days_in_month[month - 1]:
        return False
    
    return True


def get_zodiac_from_birthday(month: int, day: int) -> str:
    """
    根據生日判斷星座
    
    Args:
        month: 月份
        day: 日期
        
    Returns:
        星座名稱
    """
    zodiac_dates = [
        (1, 20, "摩羯座"), (2, 19, "水瓶座"), (3, 21, "雙魚座"),
        (4, 20, "牡羊座"), (5, 21, "金牛座"), (6, 22, "雙子座"),
        (7, 23, "巨蟹座"), (8, 23, "獅子座"), (9, 23, "處女座"),
        (10, 24, "天秤座"), (11, 23, "天蠍座"), (12, 22, "射手座"),
        (12, 31, "摩羯座")
    ]
    
    for end_month, end_day, zodiac in zodiac_dates:
        if month < end_month or (month == end_month and day <= end_day):
            return zodiac
    
    return "摩羯座"


def get_zodiac_emoji(zodiac: str) -> str:
    """
    獲取星座表情符號
    
    Args:
        zodiac: 星座名稱
        
    Returns:
        表情符號
    """
    emoji_map = {
        "牡羊座": "♈", "金牛座": "♉", "雙子座": "♊",
        "巨蟹座": "♋", "獅子座": "♌", "處女座": "♍",
        "天秤座": "♎", "天蠍座": "♏", "射手座": "♐",
        "摩羯座": "♑", "水瓶座": "♒", "雙魚座": "♓"
    }
    return emoji_map.get(zodiac, "⭐")
