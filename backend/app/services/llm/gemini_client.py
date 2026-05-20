import re

from google import genai
from google.genai import types

from ...config import settings


SYSTEM_PROMPT = "你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。"


class GeminiClient:
    def __init__(self, model: str | None = None):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API Key 尚未設置")
        self.model = model or settings.GEMINI_MODEL
        self.client = genai.Client(api_key = settings.GEMINI_API_KEY)    
    
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags = re.MULTILINE)
        text = re.sub(r'^#{1,6}\s+', '', text, flags = re.MULTILINE)
        text = re.sub(r'^\s*[\*\-]\s*\*\*', '', text, flags = re.MULTILINE)
        return text
    
    
    def generate(self, prompt: str, num_predict: int = 512) -> str:
        try:
            response = self.client.models.generate_content(
                model = self.model,
                contents = prompt,
                config = types.GenerateContentConfig(
                    system_instruction = SYSTEM_PROMPT,
                    temperature = 0.7,  # 降低隨機性
                    top_p = 0.9,
                    max_output_tokens = num_predict,    # 可自訂輸出長度
                ),
            )
            return self.clean_markdown(response.text or "")
        except Exception as e:
            return f"生成失敗：{str(e)}"
    
    
    def generate_stream(
        self, 
        prompt: str, 
        num_predict: int,
        system_prompt: str | None = None,
    ):
        try:
            if system_prompt is None:
                system_prompt = SYSTEM_PROMPT
            stream = self.client.models.generate_content_stream(
                model = self.model,
                contents = prompt,
                config = types.GenerateContentConfig(
                    system_instruction = system_prompt,
                    temperature = 0.7, 
                    top_p = 0.9,
                    max_output_tokens = num_predict,
                ),
            )
            
            for chunk in stream:
                if chunk.text:
                    yield self.clean_markdown(chunk.text)
            
        except Exception as e:
            yield f"Gemini 生成錯誤：{str(e)}"
