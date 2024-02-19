Frontend Instructions

1. npm install --global --production windows-build-tools , npm install axios
2. npm start
3. Click on create new chat

build and run dockerfile:
1. docker build -t frontend .  
2. run -p 3000:3000 frontend 

Backend Instrcutions

1. Git clone Backend and insert environmnet file .env with 2 variables , OPENAI_API_KEY and DB. 
2. Install all requirements or run the following step by step:
a. pip install uvicorn pip install uvicorn[standard]
b. pip install "fastapi[all]"
c. pip install pymongo
d.pip install timeout-decorator
e. pip install beanie
4. Run using : python -m uvicorn main:app --reload

build and run dockerfile
1. docker compose up -d --build
or 
1. docker build -t backend .
2. docker run -p 8000:8000 --env OPENAI_API_KEY=<your_openai_api_key> --env DB=<your_database_connection_string> backend
* for the key and string, use "" around the string*

Run test cases
1. pytest test.py 
