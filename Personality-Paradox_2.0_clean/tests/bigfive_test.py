"""
Big Five 測驗模組
"""

import json
from typing import Dict, List
from models.test_result import BigFiveResult
from config import BIGFIVE_QUESTIONS_FILE


class BigFiveTest:
    """Big Five 測驗類別"""
    
    def __init__(self):
        """載入題庫"""
        with open(BIGFIVE_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.questions = data['questions']
            self.scale_labels = data['scale_labels']
    
    def get_questions(self) -> List[Dict]:
        """獲取所有題目"""
        return self.questions
    
    def get_scale_labels(self) -> Dict[str, str]:
        """獲取量表標籤"""
        return self.scale_labels
    
    def calculate_scores(self, answers: Dict[int, int]) -> BigFiveResult:
        """
        計算 Big Five 分數
        
        Args:
            answers: {題目id: 分數} 的字典
            
        Returns:
            BigFiveResult 物件
        """
        # 按維度分組計算
        dimension_scores = {
            'openness': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        for question in self.questions:
            q_id = question['id']
            dimension = question['dimension']
            
            if q_id in answers:
                score = answers[q_id]
                dimension_scores[dimension].append(score)
        
        # 計算每個維度的平均分
        avg_scores = {}
        for dimension, scores in dimension_scores.items():
            if scores:
                avg_scores[dimension] = round(sum(scores) / len(scores), 2)
            else:
                avg_scores[dimension] = 3.5  # 預設中間值
        
        return BigFiveResult(
            openness=avg_scores['openness'],
            conscientiousness=avg_scores['conscientiousness'],
            extraversion=avg_scores['extraversion'],
            agreeableness=avg_scores['agreeableness'],
            neuroticism=avg_scores['neuroticism']
        )
