from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ai_engine.llm_client import LLMClient

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageRequest(BaseModel):
    message: str

class TextRequest(BaseModel):
    text: str

@router.post("/message")
async def send_message(request: MessageRequest):
    llm_client = LLMClient()
    response = await llm_client.generate_response(request.message)
    return {"response": response}

@router.post("/summarize")
async def summarize_text(request: TextRequest):
    llm_client = LLMClient()
    summary = await llm_client.generate_summary(request.text)
    return {"summary": summary}