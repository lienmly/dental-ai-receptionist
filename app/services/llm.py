import json
from typing import Optional
from openai import OpenAI
from app.config.settings import settings
from app.tools.handler import execute_tool


client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


async def chat(messages: list, tools: Optional[list] = None) -> dict:
    """Send messages to the LLM, handle any tool calls, and return the final response."""
    kwargs = {
        "model": settings.llm_model,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    message = response.choices[0].message

    # If the LLM wants to call tools, execute them and send results back
    while message.tool_calls:
        # Add the assistant's tool call message to history
        messages.append(message)

        # Execute each tool call and add results
        for tool_call in message.tool_calls:
            arguments = json.loads(tool_call.function.arguments)
            result = execute_tool(tool_call.function.name, arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # Call the LLM again with the tool results
        kwargs["messages"] = messages
        response = client.chat.completions.create(**kwargs)
        message = response.choices[0].message

    return message