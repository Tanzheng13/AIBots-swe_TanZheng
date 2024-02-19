from bson import ObjectId
import bson
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from openai import OpenAI
from pymongo import MongoClient
from main import app  
import uuid,  os

client = TestClient(app)
load_dotenv()

DATABASE_URL = os.environ.get("DB")
DB_NAME = "conversation"
dbclient = MongoClient(DATABASE_URL)
database = dbclient[DB_NAME]
conversation_db = database["conversation"]

def test_create_conversation():

    data = {
        "name": "John",
        "additionalProp1": "value1",
        "additionalProp1o": "value2"
    }

    response = client.post("/conversations", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    returned_id = response.json()["id"]
    assert returned_id is not None
    assert len(returned_id) == 36 

def test_get_conversation_by_id():

    guid = uuid.uuid4() 
    test_id = str(guid)
    conversation_db.insert_one({
        "guid": test_id,
        "name": "John",
        "params": {"additionalProp1": "value1"},
        "additionalProp1": "value2",
        "messages": []
    })
    result = conversation_db.find_one({"guid": test_id})
    assert test_id == result["guid"]
    assert result["name"] == "John"
    assert result["messages"]  == []

def test_update_conversation_by_id():
    guid = uuid.uuid4()
    test_id = str(guid)
    conversation_db.insert_one({
        "guid": test_id,
        "name": "John",
        "params": {"additionalProp1": "value1"},
        "additionalProp1": "value2",
        "messages": [{"role": "user", "content": "oldquery"}]
    })

    update_data = {
        "oldquery": "oldquery",
        "newquery": "newquery",
        "params": {"additionalProp1": "updated_value"}
    }

    conversation_db.update_one({"guid": test_id}, {"$set": { "params": None}})
    result = conversation_db.find_one({"guid": test_id})
    assert result["params"] == None

def test_delete_conversation_by_id():
    # Create a conversation to delete
    guid = uuid.uuid4()
    test_id = str(guid)
    conversation_db.insert_one({
        "guid": test_id,
        "name": "John",
        "params": {"additionalProp1": "value1"},
        "additionalProp1": "value2",
        "messages": []
    })
    result = conversation_db.find_one({"guid": test_id})
    result2 = conversation_db.delete_one({"guid": test_id})
    assert result["guid"] == test_id
    assert result2.deleted_count == 1

