"""
綜合分析模組
"""

from typing import List, Tuple
from models.test_result import MBTIResult, BigFiveResult, ZodiacResult


class IntegrationAnalyzer:
    """綜合分析器"""
    
    @staticmethod
    def find_contradictions(
        mbti: MBTIResult,
        bigfive: BigFiveResult,
        zodiac: ZodiacResult
    ) -> List[Tuple[str, str]]:
        """
        找出測驗結果的矛盾點
        
        Args:
            mbti: MBTI 結果
            bigfive: Big Five 結果
            zodiac: 星座結果
            
        Returns:
            矛盾點列表 [(描述1, 描述2), ...]
        """
        contradictions = []
        
        # MBTI E/I vs Big Five 外向性
        if mbti.type[0] == 'E' and bigfive.extraversion < 3.0:
            contradictions.append((
                f"MBTI 顯示外向（{mbti.type[0]}）",
                f"但 Big Five 外向性偏低（{bigfive.extraversion:.1f}）"
            ))
        elif mbti.type[0] == 'I' and bigfive.extraversion > 4.5:
            contradictions.append((
                f"MBTI 顯示內向（{mbti.type[0]}）",
                f"但 Big Five 外向性偏高（{bigfive.extraversion:.1f}）"
            ))
        
        # MBTI T/F vs Big Five 友善性
        if mbti.type[2] == 'T' and bigfive.agreeableness > 5.0:
            contradictions.append((
                f"MBTI 顯示理性思考（{mbti.type[2]}）",
                f"但 Big Five 友善性很高（{bigfive.agreeableness:.1f}）"
            ))
        elif mbti.type[2] == 'F' and bigfive.agreeableness < 3.0:
            contradictions.append((
                f"MBTI 顯示情感導向（{mbti.type[2]}）",
                f"但 Big Five 友善性偏低（{bigfive.agreeableness:.1f}）"
            ))
        
        # MBTI J/P vs Big Five 盡責性
        if mbti.type[3] == 'J' and bigfive.conscientiousness < 3.0:
            contradictions.append((
                f"MBTI 顯示計劃性（{mbti.type[3]}）",
                f"但 Big Five 盡責性偏低（{bigfive.conscientiousness:.1f}）"
            ))
        elif mbti.type[3] == 'P' and bigfive.conscientiousness > 5.0:
            contradictions.append((
                f"MBTI 顯示彈性（{mbti.type[3]}）",
                f"但 Big Five 盡責性很高（{bigfive.conscientiousness:.1f}）"
            ))
        
        # Big Five 神經質 vs 星座（簡化版，可擴展）
        high_neuroticism_signs = ["巨蟹座", "雙魚座", "天蠍座"]
        if bigfive.neuroticism < 2.5 and zodiac.sign in high_neuroticism_signs:
            contradictions.append((
                f"Big Five 神經質很低（{bigfive.neuroticism:.1f}）",
                f"但 {zodiac.sign} 通常較為敏感"
            ))
        
        return contradictions
    
    @staticmethod
    def find_consistencies(
        mbti: MBTIResult,
        bigfive: BigFiveResult
    ) -> List[str]:
        """
        找出測驗結果的一致性
        
        Args:
            mbti: MBTI 結果
            bigfive: Big Five 結果
            
        Returns:
            一致性描述列表
        """
        consistencies = []
        
        # MBTI E/I vs Big Five 外向性
        if mbti.type[0] == 'E' and bigfive.extraversion > 4.0:
            consistencies.append("外向特質一致")
        elif mbti.type[0] == 'I' and bigfive.extraversion < 3.5:
            consistencies.append("內向特質一致")
        
        # MBTI J/P vs Big Five 盡責性
        if mbti.type[3] == 'J' and bigfive.conscientiousness > 4.0:
            consistencies.append("計劃性與盡責性一致")
        elif mbti.type[3] == 'P' and bigfive.conscientiousness < 3.5:
            consistencies.append("彈性與低盡責性一致")
        
        return consistencies
