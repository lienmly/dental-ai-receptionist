from datetime import date
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm import chat
from app.tools.definitions import DENTAL_TOOLS
from app.config.loader import build_system_prompt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dental AI Receptionist",
    description="AI-powered receptionist for dental offices",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    if conv_id not in conversations:
        conversations[conv_id] = [
            {"role": "system", "content": build_system_prompt(today)},
        ]

    conversations[conv_id].append({"role": "user", "content": request.message})
    response = await chat(conversations[conv_id], tools=DENTAL_TOOLS)
    conversations[conv_id].append({"role": "assistant", "content": response.content})

    return {"reply": response.content, "conversation_id": conv_id}