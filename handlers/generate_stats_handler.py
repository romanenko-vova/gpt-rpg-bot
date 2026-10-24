from telegram.ext import ContextTypes

from services.ask_gpt import generate_text
from services.read_model_json import read_model_json


async def send_stats_error(context, chat_id):
    await context.bot.send_message(chat_id=chat_id, text="Ошибка")


async def generate_stats(context: ContextTypes.DEFAULT_TYPE, chat_id):
    answer = await generate_text(
        f"""Ты — система RPG. Определи начальные характеристики персонажа.
    
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
                "backstory": "Короткая предыстория персонажа.",
                "inventory": ["предмет","предмет","предмет"]
                }}
                """
    )
    stats = read_model_json(answer)
    if not stats:
        await send_stats_error(context, chat_id)
        return None

    required_keys = ["STR", "AGI", "INT", "CON", "CHA", "LUCK", "backstory"]
    for key in required_keys:
        if key not in stats:
            await send_stats_error(context, chat_id)
            return None

    if (
        type(stats["STR"]) is not int
        or type(stats["AGI"]) is not int
        or type(stats["INT"]) is not int
        or type(stats["CON"]) is not int
        or type(stats["CHA"]) is not int
        or type(stats["LUCK"]) is not int
    ):
        await send_stats_error(context, chat_id)
        return None

    stat_keys = ["STR", "AGI", "INT", "CON", "CHA", "LUCK"]

    total = sum(stats[key] for key in stat_keys)

    if total != 72:
        await send_stats_error(context, chat_id)
        return None

    if type(stats["backstory"]) is not str:
        await send_stats_error(context, chat_id)
        return None

    # без инвентаря портрет падает, пустой список тоже нормально
    if type(stats.get("inventory")) is not list:
        stats["inventory"] = []

    return stats
