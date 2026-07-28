import asyncio

from openrouter import OpenRouter

from config.config import OPENROUTER_API_KEY


async def generate_text_with_context(list_messages: list[dict]) -> str:
    with OpenRouter(api_key=OPENROUTER_API_KEY) as openrouter:
        response = await openrouter.chat.send_async(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=list_messages,
        )
        return response.choices[0].message.content

    # он автоматически сделает openrouter.close()