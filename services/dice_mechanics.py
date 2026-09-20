import random


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
    if any(word in char_class_lower for word in ["маг", "wizard", "mage", "sorcerer", "cleric"]):
        return "INT"
    if any(word in char_class_lower for word in ["паладин", "бард", "ranger", "bard"]):
        return "CHA"

    return "LUCK"


def resolve_action_roll(action_text: str, stats: dict, char_class: str) -> dict:
    ability = _best_ability_for_action(action_text, char_class)
    stat_value = int(stats.get(ability, 10))
    modifier = _stat_modifier(stat_value)
    roll = random.randint(1, 20)
    total = roll + modifier
    dc = 12
    if any(word in action_text.lower() for word in ["опас", "труд", "схват", "сраж", "маг", "тайн", "слишком", "больш"]):
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
