"""
Gemini 客戶端
"""

from google import genai
from google.genai import types

from ...config import settings


GEMINI_MODEL = settings.GEMINI_MODEL
GEMINI_TIMEOUT = settings.GEMINI_TIMEOUT


class GeminiClient:
    """Gemini LLM 客戶端"""

    def __init__(self, model: str = GEMINI_MODEL):
        self.model = model
        self.timeout = GEMINI_TIMEOUT
        self._client: genai.Client | None = None

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

        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"__(.+?)__", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"_(.+?)_", r"\1", text)
        text = re.sub(r"^\s*[\*\-\+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*[\*\-]\s*\*\*", "", text, flags=re.MULTILINE)
        return text

    def _get_client(self) -> genai.Client:
        if self._client is None:
            api_key = settings.GEMINI_API_KEY.strip()
            if not api_key:
                raise RuntimeError("尚未設定 GEMINI_API_KEY")
            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=self.timeout * 1000),
            )
        return self._client

    def _build_config(
        self, system_prompt: str | None, num_predict: int
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=num_predict,
        )

    @staticmethod
    def _extract_text(response) -> str:
        text = getattr(response, "text", None)
        if text:
            return text

        prompt_feedback = getattr(response, "prompt_feedback", None)
        if prompt_feedback and getattr(prompt_feedback, "block_reason_message", None):
            return f"生成失敗：{prompt_feedback.block_reason_message}"

        return ""

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
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._build_config(
                    "你是一位專業的心理學分析師。你必須只使用繁體中文回答，絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。",
                    num_predict,
                ),
            )
            text = self.clean_markdown(self._extract_text(response))
            return text or "生成失敗：模型沒有返回內容"
        except Exception as e:
            return f"生成失敗：{str(e)}"

    def generate_stream(self, prompt: str, system_prompt: str = None, num_predict: int = 512):
        """
        串流生成文字 (逐字輸出)

        Args:
            prompt: 提示詞
            system_prompt: 系統提示詞（可選）
            num_predict: 最大輸出 token 數

        Yields:
            逐步生成的文字片段
        """
        try:
            if system_prompt is None:
                system_prompt = (
                    "你是一位專業的心理學分析師。你必須只使用繁體中文回答，"
                    "絕對不可以使用英文、簡體中文或其他語言。請提供專業、客觀、具啟發性的分析。"
                    "回應時請使用純文字，不要使用任何 Markdown 格式標記（如 *, **, _, # 等）。"
                )

            stream = self._get_client().models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=self._build_config(system_prompt, num_predict),
            )

            for chunk in stream:
                text = self.clean_markdown(getattr(chunk, "text", "") or "")
                if text:
                    yield text
        except Exception as e:
            error_msg = str(e)
            if "api key" in error_msg.lower() or "permission" in error_msg.lower():
                yield "❌ 無法連接 Gemini 服務。\n"
                yield "請確認 GEMINI_API_KEY 是否正確設定。\n"
                yield "並檢查該金鑰是否有 Gemini API 權限。"
            else:
                yield f"❌ 發生錯誤：{error_msg}\n"
                yield "請檢查 Gemini API 設定是否正確。"

    def test_connection(self) -> bool:
        """
        測試 Gemini 連接

        Returns:
            是否連接成功
        """
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents="測試",
                config=self._build_config(None, 32),
            )
            return bool(self._extract_text(response))
        except Exception:
            return False
