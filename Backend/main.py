from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid,  os
from timeout_decorator import timeout
from pydantic import BaseModel
from beanie import Document, Indexed, init_beanie

# FastAPI App
app = FastAPI()


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
        params = data["params"]
        guid = id

        if params is None:
            raise HTTPException(status_code=400, detail="Invalid parameters provided")
        
        # Assuming conversation_db.update_one is a method to update the conversation by ID
        result = conversation_db.update_one({"guid": guid}, {"$set": {"params" : params}})
        if result.modified_count == 1:
            updated_result = conversation_db.find_one({"guid": guid})
            # return {
            #     "name": updated_result['name'],
            #     "params": updated_result["params"],
            # }
            return {"status": "204", "message": "Successfully updated specified resource(s)"}
        else:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found")

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
    # qrole = data.get("qrole")
    qrole = "user"
    qcontent = data.get("qcontent")
    search = conversation_db.find_one({"guid":conversation_id})
    message = search["messages"]
    message.append({"role" : qrole , "content" : qcontent,})
    if not qrole or not qcontent:
        raise HTTPException(status_code=400, detail="Invalid parameters provided")
    
    if DATABASE_URL is None or client is None:
        raise HTTPException(status_code=404, detail="Specified resource(s) not found")
    print(message)
    try: 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # messages=[{"role": qrole,"content": qcontent,}])
            messages=message)
        print("here")
        content = completion.choices[0].message.content
        role = completion.choices[0].message.role

        response_to_insert = {
        "role": role,
        "content": content,
        }

        message.append({"role" : role , "content" : content})

        result = conversation_db.update_one({"guid": conversation_id}, {"$set": {"messages" : message}})
        if result.modified_count == 1:
            # return {"status": "204", "message": "Successfully updated specified resource(s)"}
            return completion.choices[0].message
        else:
            raise HTTPException(status_code=404, detail="Specified resource(s) was not found")
    
        # if debug == True:
        #     print(completion.choices[0].message)
        # return completion.choices[0].message

    except TimeoutError:
        raise HTTPException(status_code=422, detail="Unable to create resource") 
    
    except Exception as e:
        # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)