from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ai_engine.llm_client import LLMClient

router = APIRouter()

class MessageRequest(BaseModel):
    message: str

class TextRequest(BaseModel):
    text: str

# Main chat endpoint (handles /api/chat/)
@router.post("/")
async def chat(request: MessageRequest):
    """Main chat endpoint for the AI study assistant"""
    llm_client = LLMClient()
    response = await llm_client.generate_response(request.message)
    return {"response": response}

@router.post("/message")
async def send_message(request: MessageRequest):
    """Alternative message endpoint"""
    llm_client = LLMClient()
    response = await llm_client.generate_response(request.message)
    return {"response": response}

@router.post("/summarize")
async def summarize_text(request: TextRequest):
    """Summarize text content"""
    llm_client = LLMClient()
    summary = await llm_client.generate_summary(request.text)
    return {"summary": summary}