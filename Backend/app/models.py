from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class ConversationHistoryItem(BaseModel):
    prompt: str
    response: str

class Conversation(Document, BaseModel):
    id: PydanticObjectId
    history: list[ConversationHistoryItem] = []
