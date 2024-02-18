Frontend Instructions

1. npm install --global --production windows-build-tools
2. npm start



Backend Instrcutions

1.Git clone Backend and insert environmnet file .env with 2 variables , OPENAI_API_KEY and DB. 
2.Install all requirements or run the following step by step:
a. pip install uvicorn pip install uvicorn[standard] b. pip install "fastapi[all]" c. pip install pymongo d.pip install timeout-decorator e. pip install beanie
3.Run using : python -m uvicorn main:app --reload 
