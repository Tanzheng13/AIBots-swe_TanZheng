from pydantic import BaseModel
from typing import List

class Conversation(BaseModel):
    history: List[str]

class Prompt(BaseModel):
    conversation: Conversation

class Response(BaseModel):
    response: str
