from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from app.services.llm import chat
from app.tools.definitions import DENTAL_TOOLS

app = FastAPI(
    title="Dental AI Receptionist",
    description="AI-powered receptionist for dental offices",
    version="0.1.0",
)

# In-memory conversation store (good enough for demo, not production)
conversations: dict = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"


@app.get("/")
async def root():
    return {"status": "ok", "message": "Dental AI Receptionist is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    today = date.today().isoformat()
    conv_id = request.conversation_id

    # Start new conversation or continue existing one
    if conv_id not in conversations:
        conversations[conv_id] = [
            {"role": "system", "content": f"You are a friendly receptionist at Smile Dental Studio. Today's date is {today}. Help patients book, reschedule, and cancel appointments. Answer questions about the office. Always use the provided tools to look up real information rather than making things up. Be warm, professional, and concise."},
        ]

    # Add the user's message
    conversations[conv_id].append({"role": "user", "content": request.message})

    # Get response
    response = await chat(conversations[conv_id], tools=DENTAL_TOOLS)

    # Add assistant's response to history
    conversations[conv_id].append({"role": "assistant", "content": response.content})

    return {"reply": response.content, "conversation_id": conv_id}