"""
Ollama 客戶端
"""

import ollama
from ...config import settings

# OLLAMA_MODEL = settings.OLLAMA_MODEL
# OLLAMA_TIMEOUT = settings.OLLAMA_TIMEOUT
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT = getattr(settings, "OLLAMA_TIMEOUT", 60)


class OllamaClient:
    """Ollama LLM 客戶端"""
    
    def __init__(self, model: str = OLLAMA_MODEL):
        """
        初始化 Ollama 客戶端
        
        Args:
            model: 模型名稱
        """
        self.model = model
        self.timeout = OLLAMA_TIMEOUT
    
    def generate(self, prompt: str, num_predict: int = 512) -> str:
        """
        生成文字
        
        Args:
            prompt: 提示詞
            num_predict: 最大輸出 token 數
            
        Returns:
            生成的文字
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                system="你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。",
                options={
                    "temperature": 0.7,  # 降低隨機性
                    "top_p": 0.9,
                    "num_predict": num_predict  # 可自訂輸出長度
                }
            )
            return response['response']
        except Exception as e:
            return f"生成失敗：{str(e)}"
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """
        移除 Markdown 格式標記
        
        Args:
            text: 原始文字
            
        Returns:
            清理後的純文字
        """
        import re
        # 移除粗體標記 **text** 或 __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        # 移除斜體標記 *text* 或 _text_
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # 移除開頭的列表標記
        text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
        # 移除標題標記
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 移除行首的獨立星號或破折號
        text = re.sub(r'^\s*[\*\-]\s*\*\*', '', text, flags=re.MULTILINE)
        return text
    
    def generate_stream(self, prompt: str, system_prompt: str = None):
        """
        串流生成文字 (逐字輸出)
        
        Args:
            prompt: 提示詞
            system_prompt: 系統提示詞（可選）
            
        Yields:
            逐步生成的文字片段
        """
        try:
            # 使用傳入的 system_prompt 或預設值
            if system_prompt is None:
                system_prompt = "你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。回應時請使用純文字，不要使用任何 Markdown 格式標記（如 *, **, _, # 等）。"
            
            stream = ollama.generate(
                model=self.model,
                prompt=prompt,
                system=system_prompt,
                stream=True,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512
                }
            )
            
            for chunk in stream:
                if 'response' in chunk:
                    # 清理 Markdown 格式後再輸出
                    cleaned_text = self.clean_markdown(chunk['response'])
                    yield cleaned_text
                    
        except ConnectionError as e:
            yield "❌ 無法連接到 Ollama 服務。請確認：\n"
            yield "1. Ollama 是否已安裝\n"
            yield "2. 執行命令：ollama serve\n"
            yield "3. gemma3:4b 模型是否已下載（ollama pull gemma3:4b）"
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "connect" in error_msg.lower():
                yield "❌ 無法連接到 Ollama 服務。\n"
                yield "請在終端機執行：ollama serve\n"
                yield "然後重新整理頁面再試一次。"
            else:
                yield f"❌ 發生錯誤：{error_msg}\n"
                yield "請檢查 Ollama 服務是否正常運行。"
    
    def test_connection(self) -> bool:
        """
        測試 Ollama 連接
        
        Returns:
            是否連接成功
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt="測試"
            )
            return True
        except Exception:
            return False
