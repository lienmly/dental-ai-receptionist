from datetime import date
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm import chat
from app.tools.definitions import DENTAL_TOOLS
from app.config.loader import build_system_prompt
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request

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

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    """Handle incoming Vapi webhook events."""
    body = await request.json()
    message = body.get("message", {})
    message_type = message.get("type")

    if message_type == "tool-calls":
        tool_call_list = message.get("toolCallList", [])
        results = []

        for tool_call in tool_call_list:
            # Vapi nests name/arguments under "function"
            function = tool_call.get("function", {})
            name = function.get("name", tool_call.get("name", ""))
            parameters = function.get("arguments", tool_call.get("parameters", {}))

            from app.tools.handler import execute_tool
            result = execute_tool(name, parameters)
            results.append({
                "name": name,
                "toolCallId": tool_call.get("id", ""),
                "result": result,
            })

        return {"results": results}

    return {"status": "ok"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")