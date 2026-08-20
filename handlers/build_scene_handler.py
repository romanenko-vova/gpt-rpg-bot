
from services.ask_gpt import generate_text


async def build_scene_image_prompt(scene: str, race: str, char_class: str) -> str:
    prompt = f"""
    Ты помогаешь генерировать изображения для RPG-игры.

    Описание сцены:
    {scene[:500]}

    Персонаж: {race} {char_class}

    Задача: напиши короткий промпт для генерации картинки — не больше 30 слов, только на английском языке.
    Включи: место действия, атмосферу, персонажа, стиль.
    Добавь в конце: "fantasy art, detailed digital art, dramatic lighting"
    Верни ТОЛЬКО промпт, без пояснений.
    """

    return await generate_text(prompt)