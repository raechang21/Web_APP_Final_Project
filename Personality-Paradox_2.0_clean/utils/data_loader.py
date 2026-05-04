"""
資料載入工具
"""

import json
from typing import Dict, List
from config import BIGFIVE_QUESTIONS_FILE, DARK_TRIAD_QUESTIONS_FILE


def load_bigfive_questions() -> tuple[List[Dict], Dict[str, str]]:
    """
    載入 Big Five 題庫
    
    Returns:
        (題目列表, 量表標籤)
    """
    with open(BIGFIVE_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['questions'], data['scale_labels']


def load_dark_triad_questions() -> List[Dict]:
    """
    載入黑暗三角題庫
    
    Returns:
        題目列表
    """
    with open(DARK_TRIAD_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['questions']
