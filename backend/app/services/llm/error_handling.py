from dataclasses import dataclass


@dataclass(frozen=True)
class LlmErrorMessage:
    code: str
    message: str


DEFAULT_LLM_ERROR = LlmErrorMessage(
    code="llm_unknown",
    message="AI 分析暫時無法完成，請稍後再試一次。",
)


def classify_llm_error(error_text: str) -> LlmErrorMessage | None:
    lowered = (error_text or "").lower()

    if not lowered:
        return None

    if (
        "gemini_api_key" in lowered
        or "api key" in lowered
        or "permission" in lowered
        or "403" in lowered
    ):
        return LlmErrorMessage(
            code="llm_auth_error",
            message="AI 服務目前尚未正確設定，請稍後再試。",
        )

    if "quota" in lowered or "resource_exhausted" in lowered or "429" in lowered:
        return LlmErrorMessage(
            code="llm_quota_error",
            message="AI 服務目前使用量較高，請稍後再試一次。",
        )

    if "timeout" in lowered or "deadline" in lowered or "504" in lowered:
        return LlmErrorMessage(
            code="llm_timeout",
            message="AI 回應時間過長，請稍後重新生成。",
        )

    if "unavailable" in lowered or "503" in lowered or "overloaded" in lowered:
        return LlmErrorMessage(
            code="llm_unavailable",
            message="AI 服務暫時忙碌中，請稍後再試。",
        )

    if "safety" in lowered or "blocked" in lowered or "block_reason" in lowered:
        return LlmErrorMessage(
            code="llm_blocked",
            message="這次內容無法生成，請換一種方式再試一次。",
        )

    error_markers = (
        "gemini api",
        "getaddrinfo",
        "errno",
        "error",
        "exception",
        "?潛??航炊",
        "?航炊",
    )

    if any(marker in lowered for marker in error_markers):
        return DEFAULT_LLM_ERROR

    return None