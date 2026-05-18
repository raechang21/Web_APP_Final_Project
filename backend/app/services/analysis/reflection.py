"""
反思語句生成模組
"""

from typing import List, Tuple
from ..models.test_result import MBTIResult, BigFiveResult, ZodiacResult

# OLLAMA
# from .ollama_client import OllamaClient

# Gemini
from ..llm.gemini_client import GeminiClient

from ..llm.prompt_templates import PromptTemplates


class ReflectionGenerator:
    """反思語句生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.llm_client = GeminiClient()
        self.prompt_templates = PromptTemplates()
    
    def generate_reflection(
        self,
        mbti: MBTIResult,
        bigfive: BigFiveResult,
        zodiac: ZodiacResult,
        contradictions: List[Tuple[str, str]]
    ) -> str:
        """
        生成反思語句
        
        Args:
            mbti: MBTI 結果
            bigfive: Big Five 結果
            zodiac: 星座結果
            contradictions: 矛盾點列表
            
        Returns:
            反思語句
        """
        prompt = self.prompt_templates.reflection_prompt(
            mbti, bigfive, zodiac, contradictions
        )
        
        reflection = self.llm_client.generate(prompt)
        return reflection
