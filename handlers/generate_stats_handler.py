from services.generate_text import generate_text
from telegram.ext import ContextTypes
import json

async def generate_stats(context: ContextTypes.DEFAULT_TYPE) -> dict:
    answer = await generate_text(
        prompt=f'''Ты — система RPG. Определи начальные характеристики персонажа.
    
                Персонаж:
                - Имя: {context.user_data["name"]}
                - Раса: {context.user_data["race"]}
                - Класс: {context.user_data["class"]}
                - Описание: {context.user_data["description"]}

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
                "backstory": "Короткая предыстория персонажа."
                }}
                ''',
        assistant_content= None
    )
    stats = json.loads(answer)

    if type(stats) is not dict:
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text="Ошибка",
        )
        raise ValueError(f"GPT вернул не словарь, а {type(stats)}")

    required_keys = ["STR", "AGI", "INT", "CON", "CHA", "LUCK", "backstory"]
    for key in required_keys:
        if key not in stats:
            await context.bot.send_message(
                chat_id=context.user_data["chat_id"],
                text="Ошибка",
            )
            raise ValueError(f"GPT не вернул ключ {key}")

    if not type(stats['STR']) is int or not type(stats['AGI']) is int or not type(stats['INT']) is int or not type(stats['CON']) is int or not type(stats['CHA']) is int or not type(stats['LUCK']) is int:
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text="Ошибка",
        )
        raise ValueError("GPT вернул некорректный тип данных для одной из характеристик")

    stat_keys = ["STR", "AGI", "INT", "CON", "CHA", "LUCK"]

    total = sum(stats[key] for key in stat_keys)

    if total != 72:
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text="Ошибка",
        )
        raise ValueError(f"Сумма характеристик должна быть 72, сейчас: {total}")

    if not type(stats['backstory']) is str:
        await context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text="Ошибка",
        )
        raise ValueError(f"backstory не является строкой, а {type(stats['backstory'])}")

    
    return stats