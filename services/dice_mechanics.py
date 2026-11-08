import random


ABILITY_KEYWORDS = {
    "STR": ["удар", "атак", "сраз", "бить", "руб", "лом", "толк", "схват", "драться", "сил"],
    "AGI": ["уклон", "прыг", "бег", "красть", "скрыт", "ловк", "быст", "уверн", "пойм"],
    "INT": ["знание", "изуч", "маг", "тайн", "чары", "знак", "древ", "дум", "рассуж", "анализ", "заклин"],
    "CON": ["выдерж", "сопротив", "стойк", "выносл", "блок", "усто", "терп", "переж"],
    "CHA": ["уговор", "убеж", "обман", "переговор", "друж", "манип", "влия", "подкуп", "прируч"],
    "LUCK": ["удач", "вез", "случ", "судьб", "счаст", "фортуна"],
}


def _stat_modifier(stat_value: int) -> int:
    return (stat_value - 10) // 2


def _best_ability_for_action(action_text: str, char_class: str) -> str:
    action_lower = (action_text or "").lower()
    char_class_lower = (char_class or "").lower()

    for ability, keywords in ABILITY_KEYWORDS.items():
        if any(keyword in action_lower for keyword in keywords):
            return ability

    if any(word in char_class_lower for word in ["воин", "fighter", "warrior"]):
        return "STR"
    if any(word in char_class_lower for word in ["вор", "rogue", "thief"]):
        return "AGI"
    if any(word in char_class_lower for word in ["маг", "wizard", "mage"]):
        return "INT"
    if any(word in char_class_lower for word in ["паладин", "ranger", "bard"]):
        return "CHA"

    return "LUCK"


def resolve_action_roll(
    action_text: str,
    stats: dict,
    char_class: str,
    ability: str | None = None,
    dc: int | None = None,
) -> dict:
    ability = ability or _best_ability_for_action(action_text, char_class)
    modifier = _stat_modifier(int(stats.get(ability, 10)))
    roll = random.randint(1, 20)
    total = roll + modifier
    target_dc = dc if dc is not None else 12
    success = total >= target_dc

    return {
        "ability": ability,
        "modifier": modifier,
        "roll": roll,
        "total": total,
        "dc": target_dc,
        "success": success,
    }
