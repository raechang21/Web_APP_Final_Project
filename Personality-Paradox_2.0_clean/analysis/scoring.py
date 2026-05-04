"""
分數計算與標籤
"""

from typing import Dict, List
from config import SCORE_LABELS, SCORE_LABELS_ZH


def calculate_bigfive_scores(answers: Dict[int, int], questions: List[Dict]) -> Dict[str, float]:
    """
    計算 Big Five 分數
    
    Args:
        answers: 答案字典 {question_id: score}
        questions: 題目列表
        
    Returns:
        各維度分數字典（1.0-6.0 範圍）
    """
    dimension_scores = {
        'openness': [],
        'conscientiousness': [],
        'extraversion': [],
        'agreeableness': [],
        'neuroticism': []
    }
    
    for q in questions:
        q_id = q['id']
        dimension = q['dimension']
        is_reversed = q.get('reversed', False)
        
        if q_id in answers:
            score = answers[q_id]
            # 反向計分
            if is_reversed:
                score = 7 - score
            dimension_scores[dimension].append(score)
    
    # 計算平均分（保持 1-6 的原始分數範圍）
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            # 保持原始分數（1-6 範圍）
            final_scores[dim] = round(avg, 1)
        else:
            final_scores[dim] = 1.0
    
    return final_scores


def calculate_dark_triad_scores(answers: Dict[int, int], questions: List[Dict]) -> Dict[str, float]:
    """
    計算黑暗三角分數
    
    Args:
        answers: 答案字典 {question_id: score}
        questions: 題目列表
        
    Returns:
        各維度分數字典（1.0-6.0 範圍）
    """
    dimension_scores = {
        'machiavellianism': [],
        'narcissism': [],
        'psychopathy': []
    }
    
    for q in questions:
        q_id = q['id']
        dimension = q['dimension']
        is_reversed = q.get('reversed', False)
        
        if q_id in answers:
            score = answers[q_id]
            # 反向計分
            if is_reversed:
                score = 7 - score
            dimension_scores[dimension].append(score)
    
    # 計算平均分（保持 1-6 的原始分數範圍）
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            # 保持原始分數（1-6 範圍）
            final_scores[dim] = round(avg, 1)
        else:
            final_scores[dim] = 1.0
    
    return final_scores


def get_score_label(score: float) -> str:
    """
    根據分數獲取文字標籤
    
    Args:
        score: 分數（1.0-6.0）
        
    Returns:
        標籤文字（低/偏低/偏高/高）
    """
    for label, (min_score, max_score) in SCORE_LABELS.items():
        if min_score <= score <= max_score:
            return SCORE_LABELS_ZH[label]
    
    return "中等"


def get_progress_percentage(score: float, max_score: float = 6.0) -> float:
    """
    計算進度條百分比
    
    Args:
        score: 當前分數
        max_score: 最高分數
        
    Returns:
        百分比（0-100）
    """
    return (score / max_score) * 100
