from typing import Optional
from openai import OpenAI
from app.config.settings import settings


client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


async def chat(messages: list, tools: Optional[list] = None) -> dict:
    """Send messages to the LLM and return the response.

    Args:
        messages: Conversation history in OpenAI message format.
        tools: Optional list of tool/function definitions.

    Returns:
        The assistant's response message as a dict.
    """
    kwargs = {
        "model": settings.llm_model,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message