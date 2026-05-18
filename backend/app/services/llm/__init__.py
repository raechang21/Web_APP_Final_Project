"""
LLM 整合模組
"""

# OLLAMA
# from .ollama_client import OllamaClient

# Gemini
from .gemini_client import GeminiClient

from .prompt_templates import PromptTemplates

__all__ = ['GeminiClient', 'PromptTemplates']
