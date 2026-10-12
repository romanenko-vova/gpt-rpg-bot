from telegram import (
    Update,
)
from telegram.ext import ContextTypes

from db.charackter_crud import update_character
from services.generate_image import generate_image


def build_image_prompt(
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

    stat_keys = ["STR", "AGI", "INT", "CON", "CHA", "LUCK"]
    dominant = max(stat_keys, key=lambda s: stats[s])

    return (
        f"{race} {char_class}, {style_hints[dominant]}, "
        f"{description[:80]}, "
        f"with this equipment: {', '.join(stats['inventory'])}, "
        f"fantasy portrait, detailed digital art, dramatic lighting, dark background"
    )


async def create_character_image(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    prompt = build_image_prompt(
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        description=context.user_data["description"],
        stats=context.user_data["stats"],
    )
    await update.message.reply_text("🎨 Рисую портрет...")

    image_path = await generate_image(prompt)

    await update.message.reply_photo(photo=image_path)

    context.user_data["portrait"] = image_path
    await update_character(update.effective_user.id, portrait=image_path)
    return image_path
