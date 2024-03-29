from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid,  os
from timeout_decorator import timeout
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie
from fastapi.middleware.cors import CORSMiddleware

# FastAPI App
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

DATABASE_URL = os.environ.get("DB")
DB_NAME = "conversation"

dbclient = MongoClient(DATABASE_URL)
database = dbclient[DB_NAME]
conversation_db = database["conversation"]
query_db = database["query"]
debug= False

class Conversation(BaseModel):
    name: str
    params: list
    additionalProp1: list

# CRUD Operations
@app.get("/test")
def test():
    return "Endpoint Reached"


@app.post("/conversations")
async def conversations(request : Request):
    try:
        guid = uuid.uuid4()
        guid_str = str(guid)
        data = await request.json()

        name = data.get("name")
        additionalProp1 = data.get("additionalProp1")
        additionalProp1o = data.get("additionalProp1o")

        if not name :
            raise HTTPException(status_code=400, detail="Invalid parameters provided")
        
        insert_data = {
        "guid" : str(guid), 
        "name": name,
        "params": {
            "additionalProp1": additionalProp1
        },
        "additionalProp1": additionalProp1o,
        "messages" : []
        }

        inserted_id = conversation_db.insert_one(insert_data).inserted_id

        return_data = {
            "id" : guid_str
        }

        return return_data

    except Exception as e:
    # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e
    

@app.get("/conversations/{id}")
async def conversations_by_id(id:str):
    try:
        guid = id
        result = conversation_db.find_one({"guid": guid})

        if result == None:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found") from e
        
        to_return  = {
                "id" : guid,
                "name" : result['name'],
                "params" : result["params"],
                "tokens" : 0,
                "additionalProp1" : {}, 
                "messages" : result["messages"]
            }
        
        return to_return
    
    except Exception as e:
    # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e
    
@app.put("/conversations/{id}")
async def update_conversation_by_id(id: str, request : Request):
    try:
        data = await request.json()
        oldquery = data.get("oldquery")
        newquery = data.get("newquery")
        params = data.get("params")
        guid = id
        if params is None:
            raise HTTPException(status_code=400, detail="Invalid parameters provided")
        
        to_find = conversation_db.find_one({"guid": guid})
        if to_find == None:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found")
        else:
            for i, message in enumerate(to_find['messages']):
                if message == oldquery:
                    to_find['messages'][i] = newquery
                    to_find['messages'] = to_find['messages'][:i+1]
                    break
            message = to_find['messages']
            try: 
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    # messages=[{"role": qrole,"content": qcontent,}])
                    messages=message)
                content = completion.choices[0].message.content
                role = completion.choices[0].message.role

                message.append({"role" : role , "content" : content})

                result = conversation_db.update_one({"guid": guid}, {"$set": {"messages" : message , "params": params}})
                if result.modified_count == 1:
                    # return {"status": "204", "message": "Successfully updated specified resource(s)"}
                    return message
                else:
                    raise HTTPException(status_code=404, detail="Specified resource(s) was not found")
            
            except TimeoutError:
                raise HTTPException(status_code=422, detail="Unable to create resource") 
            
            except Exception as e:
                # Catch any other exceptions and raise HTTP 500
                raise HTTPException(status_code=500, detail="Internal server error") from e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e
    
@app.get("/conversations")
async def conversations(request : Request):
    try:
        data = await request.json()
        name_to_find = data.get("name")
        results = conversation_db.find({"name": name_to_find})
        conversation_list = []
        if results is None:
            return 
        for result in results:
            guid = result["guid"]
            to_insert  = {
                "id" : guid,
                "name" : result['name'],
                "params" : result["params"],
                "tokens" : 0,
                "additionalProp1" : {}, 
                "messages" : result["messages"]
            }
            conversation_list.append(to_insert)
        
        return conversation_list
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

@app.delete("/conversations/{id}")
async def delete_conversation_by_id(id: str):
    try:
        guid = id
        result = conversation_db.delete_one({"guid": guid})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found")

        return {"status": "204", "message": "Successfully deleted specified resource(s)"}

    except Exception as e:
        # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e


@timeout(10)
@app.post("/queries")
async def queries(request : Request):
    data = await request.json()
    conversation_id = data.get("conversation_id")
    print("here")
    qrole = "user"
    qcontent = data.get("qcontent")
    params = data.get("params")
    search = conversation_db.find_one({"guid":conversation_id})
    message = search["messages"]
    message.append({"role" : qrole , "content" : qcontent,})
    if not qrole or not qcontent:
        raise HTTPException(status_code=400, detail="Invalid parameters provided")
    
    if DATABASE_URL is None or client is None:
        raise HTTPException(status_code=404, detail="Specified resource(s) not found")
    try: 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # messages=[{"role": qrole,"content": qcontent,}])
            messages=message)
        content = completion.choices[0].message.content
        role = completion.choices[0].message.role

        message.append({"role" : role , "content" : content})

        result = conversation_db.update_one({"guid": conversation_id}, {"$set": {"messages" : message , "params": params}})
        if result.modified_count == 1:
            # return {"status": "204", "message": "Successfully updated specified resource(s)"}
            return completion.choices[0].message
        else:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found")
    
    except TimeoutError:
        raise HTTPException(status_code=422, detail="Unable to create resource") 
    
    except Exception as e:
        # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)