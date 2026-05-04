"""
MBTI 測驗模組
"""

from models.test_result import MBTIResult


def validate_mbti_input(mbti_input: str) -> tuple[bool, str]:
    """
    驗證 MBTI 輸入格式
    
    Args:
        mbti_input: 使用者輸入的 MBTI 類型
        
    Returns:
        (是否有效, 錯誤訊息或成功訊息)
    """
    if not mbti_input:
        return False, "請輸入 MBTI 類型"
    
    mbti_input = mbti_input.strip().upper()
    
    if len(mbti_input) != 4:
        return False, "MBTI 類型必須是 4 個字母（例如：ENTJ）"
    
    valid_chars = {
        0: ['E', 'I'],
        1: ['S', 'N'],
        2: ['T', 'F'],
        3: ['J', 'P']
    }
    
    for i, char in enumerate(mbti_input):
        if char not in valid_chars[i]:
            expected = '/'.join(valid_chars[i])
            return False, f"第 {i+1} 個字母必須是 {expected}"
    
    return True, mbti_input


def create_mbti_result(mbti_type: str) -> MBTIResult:
    """
    建立 MBTI 結果物件
    
    Args:
        mbti_type: MBTI 類型（已驗證）
        
    Returns:
        MBTIResult 物件
    """
    return MBTIResult(type=mbti_type)
