from typing import List
from pydantic import BaseModel


class ChatbotRequest(BaseModel):
    query: str


class ChatbotResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
