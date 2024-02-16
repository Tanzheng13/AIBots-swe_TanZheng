from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from beanie import init_beanie, Document, init_beanie
import os
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import openai
import uuid
from timeout_decorator import timeout

# FastAPI App
app = FastAPI()


load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

DATABASE_URL = os.environ.get("DB")
DB_NAME = "conversations"

dbclient = MongoClient(DATABASE_URL)
database = dbclient[DB_NAME]
conversation_db = database["conversation"]
query_db = database["query"]


# Beanie Config
class ConversationModel(Document):
    conversation: list

# Initialize Beanie
async def init():
    await init_beanie(database_url=DATABASE_URL, document_models=[ConversationModel], database=DB_NAME)

# Dependency to ensure database connection is established
async def get_db():
    await init()
    return ConversationModel

# Data Models
# class ConversationCreate(BaseModel):
#     query: str

# class ConversationResponse(BaseModel):
#     id: str
#     conversation: list
#     response: str

class QueryModel:
    def __init__(self, role, content, additionalProp1):
        self.role = role
        self.content = content
        self.additionalProp1 = additionalProp1

# CRUD Operations
    
@app.get("/test")
def test():
    return "Endpoint Reached"

# @app.post("/conversations", response_model=ConversationResponse)
# async def create_conversation(conversation_create: ConversationCreate, db: ConversationModel = Depends(get_db)):
#     # Fetch conversation history from the database
#     existing_conversation = db.get({})
#     if not existing_conversation:
#         existing_conversation = []
#     else:
#         existing_conversation = existing_conversation[0].conversation

#     # Add the new query to the conversation
#     existing_conversation.append(conversation_create.query)

#     # Generate response from OpenAI GPT-3
#     prompt = "\n".join(existing_conversation)
#     response = openai.complete(prompt)

#     # Store anonymized prompt and response in the database
#     db_id = str(db.id)
#     await db.update_one({"_id": db_id}, {"$set": {"conversation": existing_conversation}})

#     return {"id": db_id, "conversation": existing_conversation, "response": response.choices[0].text}

@app.post("/conversation")
def conversation():
    guid = uuid.uuid4()
    guid_str = str(guid)


    print("Generated GUID:", guid_str)
    return guid

@timeout(10)
@app.post("/queries")
async def conversation(request : Request):
    data = await request.json()

    role = data.get("role")
    content = data.get("content")
    additionalProp1 = data.get("additionalProp1", {})

    if not role or not content:
        raise HTTPException(status_code=400, detail="Invalid parameters provided")
    
    if DATABASE_URL is None or client is None:
        raise HTTPException(status_code=404, detail="Specified resource(s) not found")

    guid = uuid.uuid4()
    guid_str = str(guid)

    try: 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
        "role": role,
        "content": content,}])

    except TimeoutError:
        raise HTTPException(status_code=422, detail="Unable to create resource") 
    
    except Exception as e:
        # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e
        
    print(completion.choices[0].message)
    return completion.choices[0].message

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)