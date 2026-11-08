import random

def resolve_action_roll(
    ability: str | None = None,
    dc: int | None = None,
) -> dict:
    ability
    roll = random.randint(1, 20)
    total = roll 
    target_dc = dc if dc is not None else 12
    success = total >= target_dc

    return {
        "ability": ability,
        "roll": roll,
        "total": total,
        "dc": target_dc,
        "success": success,
    }
