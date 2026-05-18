import re
from google import genai
from google.genai import types
from ...config import settings

# 初始化新版 Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# 👇 建立共用的安全設定，把所有敏感詞阻擋機制關閉 (因為我們是心理學分析)
unrestricted_safety = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
]

class GeminiClient:
    def __init__(self, model_name: str = settings.GEMINI_MODEL):
        self.model_name = model_name
    
    def generate(self, prompt: str, num_predict: int = 512) -> str:
        system_prompt = "你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。"
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=num_predict,
                    safety_settings=unrestricted_safety  # 加入安全設定
                )
            )
            return self.clean_markdown(response.text)
        except Exception as e:
            return f"生成失敗：{str(e)}"
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        if not text: return ""
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[\*\-]\s*\*\*', '', text, flags=re.MULTILINE)
        return text
    
    def generate_stream(self, prompt: str, system_prompt: str = None):
        try:
            if system_prompt is None:
                system_prompt = "你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。回應時請使用純文字，不要使用任何 Markdown 格式標記（如 *, **, _, # 等）。"
            
            response = client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2048, # 允許輸出更長的文章
                    safety_settings=unrestricted_safety # 加入安全設定
                )
            )
            
            for chunk in response:
                # 確保 chunk 有文字才處理，避免 safety block 時為空導致出錯
                if chunk.text:
                    cleaned_text = self.clean_markdown(chunk.text)
                    yield cleaned_text
                    
        except Exception as e:
            yield f"\n\n❌ 發生錯誤或遭安全機制阻擋：{str(e)}\n"
            
    def test_connection(self) -> bool:
        """
        測試 Gemini API 連接狀態
        發送一個極短的請求來驗證 API Key 是否有效且網路暢通。
        """
        try:
            # 使用一個最基礎的模型發送最簡單的內容，以減少延遲和成本
            response = client.models.generate_content(
                model=self.model_name,
                contents="ping",
                config=types.GenerateContentConfig(
                    max_output_tokens=5, # 我們只需要它能回應，不需要長篇大論
                )
            )
            # 只要有回應且沒有拋出異常，就代表連線成功
            return True if response.text else False
        except Exception as e:
            print(f"Gemini API Health Check Failed: {str(e)}")
            return False