from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm import chat

app = FastAPI(
    title="Dental AI Receptionist",
    description="AI-powered receptionist for dental offices",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"status": "ok", "message": "Dental AI Receptionist is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    messages = [
        {"role": "system", "content": "You are a friendly dental office receptionist."},
        {"role": "user", "content": request.message},
    ]
    response = await chat(messages)
    return {"reply": response.content}