from fastapi import FastAPI
from models.models import UserRequest
from services.llm import call_agent
from services.db import save_data
app = FastAPI()




@app.post("/analyze-competitor")
async def analyze_competitor(request: UserRequest):
    result = call_agent(request)
    await save_data(result)
    return {"response": result}


