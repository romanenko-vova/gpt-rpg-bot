import random

from openrouter import OpenRouter

from config.config import OPENROUTER_API_KEY, TEXT_MODEL_NAME
from services.read_model_json import read_model_json

ABILITY_KEYWORDS = {
    "STR": [
        "удар",
        "атак",
        "сраз",
        "бить",
        "руб",
        "лом",
        "толк",
        "схват",
        "драться",
        "боев",
        "сил",
        "сраж",
    ],
    "AGI": [
        "уклон",
        "прыг",
        "краст",
        "скрыт",
        "ловк",
        "бег",
        "уверн",
        "схват",
        "перемещ",
        "пойм",
        "быст",
        "осторож",
    ],
    "INT": [
        "знание",
        "изуч",
        "маг",
        "тайн",
        "чары",
        "знак",
        "древ",
        "дум",
        "рассуж",
        "анализ",
        "заклин",
        "волш",
        "суд",
    ],
    "CON": [
        "выдерж",
        "сопротив",
        "стойк",
        "выносл",
        "блок",
        "усто",
        "сохран",
        "переж",
        "стоп",
        "терп",
    ],
    "CHA": [
        "уговор",
        "убеж",
        "обман",
        "переговор",
        "друж",
        "перед",
        "манип",
        "влия",
        "подкуп",
        "прируч",
        "соблаз",
    ],
    "LUCK": [
        "удач",
        "вез",
        "случ",
        "подсказ",
        "судьб",
        "счаст",
        "фортуна",
    ],
}


def _stat_modifier(stat_value: int) -> int:
    return (stat_value - 10) // 2


def _best_ability_for_action(action_text: str, char_class: str) -> str:
    action_lower = action_text.lower()
    char_class_lower = (char_class or "").lower()

    for ability, keywords in ABILITY_KEYWORDS.items():
        if any(keyword in action_lower for keyword in keywords):
            return ability

    if any(word in char_class_lower for word in ["воин", "warrior", "fighter"]):
        return "STR"
    if any(word in char_class_lower for word in ["вор", "rogue", "thief", "ninja"]):
        return "AGI"
    if any(
        word in char_class_lower
        for word in ["маг", "wizard", "mage", "sorcerer", "cleric"]
    ):
        return "INT"
    if any(word in char_class_lower for word in ["охотник", "hunter", "ranger"]):
        return "CHA"

    return "LUCK"


async def decide_if_roll_needed(
    action_text: str, history: list[dict] | None = None
) -> dict:
    message_history = history or []
    recent_history = message_history[-6:]

    system_prompt = """
        Ты — ведущий RPG. Ты решаешь, нужна ли проверка броска для выбранного действия игрока.
        Верни только JSON без лишнего текста.
        Формат:
        {"needs_roll": true/false, "ability": "STR|AGI|INT|CON|CHA|LUCK", "dc": 10, "reason": "короткое объяснение"}
        Если действие обычное, безопасное и не рискованное — needs_roll должно быть false.
        Если действие опасное, сложное, рискованное, магическое, скрытное, социальное или требующее силы/ловкости/интеллекта — needs_roll должно быть true.
        ability выбирай по смыслу действия.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Выбранное действие: {action_text}"},
    ]
    if recent_history:
        messages.extend(recent_history)

    with OpenRouter(api_key=OPENROUTER_API_KEY) as openrouter:
        response = await openrouter.chat.send_async(
            model=TEXT_MODEL_NAME,
            messages=messages,
        )
        content = response.choices[0].message.content

    # модель может обернуть JSON в ```json или текст — тогда считаем, что бросок не нужен
    data = read_model_json(content)
    if data is None:
        return {
            "needs_roll": False,
            "ability": "LUCK",
            "dc": 12,
            "reason": "Действие обычное, без проверки.",
        }

    data.setdefault("needs_roll", False)
    data.setdefault("ability", "LUCK")
    data.setdefault("dc", 12)
    data.setdefault("reason", "Действие прошло без специальных испытаний.")
    return data


def resolve_action_roll(
    action_text: str,
    stats: dict,
    char_class: str,
    ability: str | None = None,
    dc: int | None = None,
) -> dict:
    ability = ability or _best_ability_for_action(action_text, char_class)
    stat_value = int(stats.get(ability, 10))
    modifier = _stat_modifier(stat_value)
    roll = random.randint(1, 20)
    total = roll + modifier

    if dc is None:
        dc = 12
        if any(
            word in action_text.lower()
            for word in [
                "опас",
                "труд",
                "схват",
                "сраж",
                "маг",
                "тайн",
                "слишком",
                "больш",
            ]
        ):
            dc = 14

    success = total >= dc

    return {
        "ability": ability,
        "modifier": modifier,
        "roll": roll,
        "total": total,
        "dc": dc,
        "success": success,
    }
