import json

from functools import lru_cache
from pathlib import Path
from typing import Any

from ...config import BIG_FIVE_QUESTIONS_FILE, DARK_TRIAD_QUESTIONS_FILE


def _load_json(path: str) -> dict[str, Any]:
    with Path(path).open("r", encoding = "utf-8") as file:
        return json.load(file)


@lru_cache(maxsize = 1)
def load_big_five_questions() -> tuple[list[dict], dict[str, str]]:
    data = _load_json(BIG_FIVE_QUESTIONS_FILE)
    return data["questions"], data["scale_labels"]


@lru_cache(maxsize = 1)
def load_dark_triad_questions() -> list[dict[str, Any]]:
    data = _load_json(DARK_TRIAD_QUESTIONS_FILE)
    return data["questions"]
