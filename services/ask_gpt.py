from openrouter import OpenRouter

from config.config import OPENROUTER_API_KEY, TEXT_MODEL_NAME


async def generate_text(prompt: str) -> str:
    # Для одного запроса отправляем модели одно сообщение.
    return await generate_text_with_history([{"role": "user", "content": prompt}])


async def generate_text_with_history(history: list[dict]) -> str:
    # В игре модель получает и новый ход, и предыдущие реплики.
    with OpenRouter(api_key=OPENROUTER_API_KEY) as openrouter:
        response = await openrouter.chat.send_async(
            model=TEXT_MODEL_NAME,
            messages=history,
        )
        return response.choices[0].message.content
