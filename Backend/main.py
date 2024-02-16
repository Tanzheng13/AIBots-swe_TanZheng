from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from beanie import init_beanie, Document, init_beanie
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import openai , uuid, bson , json , os
from timeout_decorator import timeout
from bson import ObjectId

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
        "message" : []
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
        print(result)
        to_return  = {
                "id" : guid,
                "name" : result['name'],
                "params" : result["params"],
                "tokens" : 0,
                "additionalProp1" : {}, 
                "messages" : result["messages"]
            }
        return result
    
    except Exception as e:
    # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e
    
@app.get("/conversations")
async def conversations(request : Request):
    try:
        data = await request.json()
        name_to_find = data.get("name")
        results = conversation_db.find({"name": name_to_find})
        conversation_list = []

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


@timeout(10)
@app.post("/queries")
async def queries(request : Request):
    data = await request.json()

    qrole = data.get("role")
    qcontent = data.get("content")
    additionalProp1 = data.get("additionalProp1", {})
    convo = data.get("convo")
    print(convo)

    if not convo or not qrole or not qcontent:
        raise HTTPException(status_code=400, detail="Invalid parameters provided")
    
    if DATABASE_URL is None or client is None:
        raise HTTPException(status_code=404, detail="Specified resource(s) not found")

    guid = uuid.uuid4()
    guid_str = str(guid)

    try: 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # messages=[{"role": qrole,"content": qcontent,}])
            messages=convo)

        content = completion.choices[0].message.content
        role = completion.choices[0].message.role
        function_call = completion.choices[0].message.function_call
        tool_calls = completion.choices[0].message.tool_calls

        response_to_insert = {
        "content": content,
        "role": role,
        "function_call": function_call,
        "tool_calls": tool_calls
        }

        query_to_insert = {
            "role" : qrole , 
            "content" : qcontent
        }

        if debug == True:
            # print(query_to_insert)
            print(response_to_insert)
    
        if debug == True:
            print(completion.choices[0].message)
        return completion.choices[0].message

    except TimeoutError:
        raise HTTPException(status_code=422, detail="Unable to create resource") 
    
    except Exception as e:
        # Catch any other exceptions and raise HTTP 500
        raise HTTPException(status_code=500, detail="Internal server error") from e

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)