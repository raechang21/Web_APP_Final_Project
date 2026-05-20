import json
import logging

from pathlib import Path
from typing import Any

from ...config import BIG_FIVE_DIMENSIONS


DATA_DIR = Path(__file__).resolve().parents[3] / "data"

logger = logging.getLogger(__name__)


def _load_template_file(filename: str) -> dict:
    with (DATA_DIR / filename).open("r", encoding = "utf-8") as file:
        return json.load(file)


def _get_level(score: float) -> str:
    if score <= 2.5:
        return "low"
    if score <= 4.5:
        return "medium"
    return "high"


class PromptTemplates:
    @staticmethod
    def get_mbti_template(mbti_type: str) -> dict:
        try:
            templates = _load_template_file("mbti_templates.json")
            if mbti_type in templates:
                return templates[mbti_type]
            
        except Exception as e:
            logger.exception(f"❌ 讀取 MBTI 模板失敗: {e}")

        return {
            'nickname': mbti_type,
            'description': f'你的 MBTI 類型是 {mbti_type}',
            'strengths': ['請參考專業 MBTI 解讀'],
            'growth_areas': ['請參考專業 MBTI 解讀'],
            'career_suggestions': '請參考 16Personalities 網站獲取詳細分析',
            'interaction_style': '請參考專業 MBTI 資源'
        }
    
    
    @staticmethod
    def get_big_five_template(scores: dict) -> str:
        try:
            templates = _load_template_file("big_five_templates.json")
            
            dimensions = BIG_FIVE_DIMENSIONS
            
            analysis = "🌟 Big Five 人格特質分析\n\n"
            
            for dim_key, dim_name in dimensions.items():
                if dim_key not in scores:
                    continue
                
                score = scores[dim_key]
                level = _get_level(score)
                dim_data = templates[dim_key][level]
                
                analysis += f"""{dim_name}: {score: .1f}/6.0
{dim_data['interpretation']}
✨ 優勢：{', '.join(dim_data['strengths'])}
💡 建議：{dim_data['suggestion']}

"""
            
            return analysis.strip()
        
        except Exception as e:
            logger.exception(f"❌ 讀取 Big Five 模板失敗: {e}")
   
            result = "基於 Big Five 人格測驗結果：\n\n"
            for key, value in scores.items():
                result += f"{key}: {value: .1f}/6.0\n"
            result += "\n請參考專業心理資源獲取更詳細的解讀。"
            return result

    
    @staticmethod
    def get_zodiac_template(zodiac: str) -> dict:
        try:
            templates = _load_template_file("zodiac_templates.json")
            if zodiac in templates:
                return templates[zodiac]
            
        except Exception as e:
            print(f"❌ 讀取星座模板失敗: {e}")
        
        return {
            'emoji': '⭐',
            'date_range': '未知',
            'element': '未知',
            'description': f'{zodiac}的特質',
            'strengths': ['請參考專業星座解讀'],
            'growth_areas': ['請參考專業星座解讀'],
            'compatibility': '待補充',
            'career': '請參考專業星座資源',
            'interaction': '請參考專業星座資源',
            'life_motto': '做最好的自己'
        }
    
    
    @staticmethod
    def get_dark_triad_template(scores: dict) -> str:
        try:
            templates = _load_template_file("dark_triad_templates.json")
            
            mach_level = _get_level(scores['machiavellianism'])
            narc_level = _get_level(scores['narcissism'])
            psyc_level = _get_level(scores['psychopathy'])
            
            mach_data = templates['machiavellianism'][mach_level]
            narc_data = templates['narcissism'][narc_level]
            psyc_data = templates['psychopathy'][psyc_level]
            
            analysis = f"""🎭 黑暗三角人格特質分析

📊 馬基維利主義：{scores['machiavellianism']: .1f}/6.0
{mach_data['interpretation']}
💡 {mach_data['suggestion']}

👑 自戀：{scores['narcissism']: .1f}/6.0
{narc_data['interpretation']}
💡 {narc_data['suggestion']}

🧀 精神病態特質：{scores['psychopathy']: .1f}/6.0
{psyc_data['interpretation']}
💡 {psyc_data['suggestion']}

────────────────────

🔮 綜合評估
"""
            
            levels = [mach_level, narc_level, psyc_level]
            if levels.count('medium') == 3:
                analysis += templates['general_analysis']['balanced']['text']
            elif levels.count('low') >= 2:
                analysis += templates['general_analysis']['low_overall']['text']
            elif levels.count('high') >= 2:
                analysis += templates['general_analysis']['high_overall']['text']
            else:
                analysis += templates['general_analysis']['mixed']['text']
            
            return analysis
            
        except Exception as e:
            logger.exception(f"❌ 讀取黑暗三角模板失敗: {e}")

            return f"""基於黑暗三角測驗結果：
馬基維利主義：{scores['machiavellianism']: .1f}/6.0
自戀：{scores['narcissism']: .1f}/6.0
精神病態：{scores['psychopathy']: .1f}/6.0

這些特質反映了你在策略思維、自信心和情緒穩定性方面的傾向。請參考專業心理資源獲取更詳細的解讀。"""
    
    