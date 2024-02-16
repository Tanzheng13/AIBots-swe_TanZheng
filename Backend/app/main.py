from fastapi import FastAPI, HTTPException
from app.models.conversation import Conversation, ConversationCreate, ConversationResponse
from app.dependencies.database import database
from app.dependencies.openai import openai_client

app = FastAPI()

@app.post("/conversations/", response_model=ConversationResponse)
async def create_conversation(conversation_create: ConversationCreate):
    conversation = await Conversation.create(**conversation_create.dict())
    return ConversationResponse(**conversation.dict())

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def read_conversation(conversation_id: str):
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse(**conversation.dict())

@app.post("/conversations/{conversation_id}/query/", response_model=ConversationResponse)
async def query_openai(conversation_id: str, query: str):
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    prompt = f"{conversation.history}\nUser: {query}\nAI:"
    response = openai_client.complete_prompt(prompt)
    
    conversation.history += f"\nUser: {query}\nAI: {response['choices'][0]['text'].strip()}"
    await conversation.update()
    
    return ConversationResponse(**conversation.dict())
