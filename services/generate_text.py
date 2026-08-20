
from openrouter import OpenRouter

from config.config import OPENROUTER_API_KEY, TEXT_MODEL_NAME


async def generate_text(prompt: str, assistant_content: str) -> str:
    with OpenRouter(api_key=OPENROUTER_API_KEY) as openrouter:
        response = await openrouter.chat.send_async(
            model=TEXT_MODEL_NAME,
            messages=[
                {"role": "system", "content": "Ты ассистент, по рпг игре"},
                {
                    "role": "assistant",
                    "content": assistant_content,
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
