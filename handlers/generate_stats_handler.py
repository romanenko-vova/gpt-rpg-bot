from config.stats import STAT_NAMES
from services.ask_gpt import generate_text
from services.read_model_json import read_model_json


async def generate_character_stats(character):
    # Модель придумывает характеристики, предысторию и стартовые вещи.
    answer = await generate_text(
        f"""Ты — система RPG. Определи начальные характеристики персонажа.

                Персонаж:
                - Имя: {character["name"]}
                - Раса: {character["race"]}
                - Класс: {character["class"]}
                - Описание: {character["description"]}

                Правила:
                - Каждая характеристика — целое число от 1 до 20
                - Сумма всех шести характеристик должна быть ровно 72
                - Распредели характеристики логично
                - Маг должен иметь высокий INT
                - Воин должен иметь высокий STR и CON
                - Вор должен иметь высокий AGI
                - Описание персонажа должно влиять на значения
                - Предыстория должна быть 2-3 предложения в стиле фэнтези

                Верни ТОЛЬКО JSON без markdown, без ``` и без пояснений.

                Формат ответа:
                {{"STR": 10,
                "AGI": 10,
                "INT": 10,
                "CON": 10,
                "CHA": 10,
                "LUCK": 10,
                "backstory": "Короткая предыстория персонажа.",
                "inventory": ["предмет","предмет","предмет"]
                }}
                """
    )
    stats = read_model_json(answer)
    if not stats:
        return None

    # Проверяем типы до сложения, чтобы модель не передала текст вместо числа.
    total = 0
    for name in STAT_NAMES:
        value = stats.get(name)
        if type(value) is not int:
            return None
        total += value

    if total != 72 or not isinstance(stats.get("backstory"), str):
        return None

    # Портрет можно нарисовать и без инвентаря.
    inventory = stats.get("inventory")
    if not isinstance(inventory, list) or any(
        not isinstance(item, str) for item in inventory
    ):
        stats["inventory"] = []

    return stats
