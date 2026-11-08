from telegram import (
    Update,
)
from telegram.ext import ContextTypes

from config.stats import STAT_NAMES
from db.character_crud import update_character
from services.generate_image import generate_image


def build_portrait_prompt(
    race: str, char_class: str, description: str, stats: dict
) -> str:
    style_hints = {
        "STR": "muscular build, heavy armor, battle-worn scars",
        "AGI": "lean figure, leather armor, agile posture",
        "INT": "mage robes, glowing eyes, arcane symbols",
        "CON": "stocky build, scarred face, resilient expression",
        "CHA": "elegant appearance, confident posture, fine clothing",
        "LUCK": "mysterious smile, unusual trinkets, lucky charms",
    }

    # Самая высокая характеристика подсказывает, как изобразить героя.
    strongest_stat = STAT_NAMES[0]
    for name in STAT_NAMES:
        if stats[name] > stats[strongest_stat]:
            strongest_stat = name
    inventory = stats.get("inventory") or []

    return (
        f"{race} {char_class}, {style_hints[strongest_stat]}, "
        f"{description[:80]}, "
        f"with this equipment: {', '.join(inventory)}, "
        f"fantasy portrait, detailed digital art, dramatic lighting, dark background"
    )


async def create_character_portrait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = build_portrait_prompt(
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        description=context.user_data["description"],
        stats=context.user_data["stats"],
    )

    image_path = await generate_image(prompt)

    context.user_data["portrait"] = image_path
    await update_character(update.effective_user.id, portrait=image_path)
    return image_path
