from openrouter import OpenRouter

from config.config import OPENROUTER_API_KEY, TEXT_MODEL_NAME


async def generate_text(prompt: str) -> str:
    with OpenRouter(api_key=OPENROUTER_API_KEY) as openrouter:
        response = await openrouter.chat.send_async(
            model=TEXT_MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    # он автоматически сделает openrouter.close()
