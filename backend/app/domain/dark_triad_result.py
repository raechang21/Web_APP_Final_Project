"""
黑暗三角人格測驗結果模型
"""

from dataclasses import dataclass
from ...config import SCORE_LABELS, SCORE_LABELS_ZH


@dataclass
class DarkTriadResult:
    """黑暗三角人格測驗結果"""
    
    machiavellianism: float  # 馬基維利主義 (1.0-6.0)
    narcissism: float        # 自戀 (1.0-6.0)
    psychopathy: float       # 精神病態 (1.0-6.0)
    
    def get_label(self, dimension: str) -> str:
        """
        獲取維度的文字標籤
        
        Args:
            dimension: 維度名稱
            
        Returns:
            標籤文字
        """
        score = getattr(self, dimension)
        
        for label, (min_score, max_score) in SCORE_LABELS.items():
            if min_score <= score <= max_score:
                return SCORE_LABELS_ZH[label]
        
        return "中等"
    
    def to_dict(self) -> dict:
        """
        轉換為字典
        
        Returns:
            包含所有維度分數的字典
        """
        return {
            'machiavellianism': self.machiavellianism,
            'narcissism': self.narcissism,
            'psychopathy': self.psychopathy
        }
    
    def get_average(self) -> float:
        """
        獲取三個維度的平均分數
        
        Returns:
            平均分數
        """
        return (self.machiavellianism + self.narcissism + self.psychopathy) / 3
