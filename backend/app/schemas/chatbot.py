from pydantic import BaseModel, Field


class ChatMessageIn(BaseModel):
    message: str = Field(min_length = 1)
