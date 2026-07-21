from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes
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
        f"fantasy portrait, detailed digital art, dramatic lighting, dark background"
    )


test_stats = {
    "STR": 4,
    "AGI": 10,
    "INT": 10,
    "CON": 6,
    "CHA": 12,
    "LUCK": 14,   
}


async def create_character_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = "Эльфийский маг"
    context.user_data["race"] = "Эльф"
    context.user_data["class"] = "Маг"
    context.user_data["description"] = (
        "Могущественный маг, владеющий древними заклинаниями и магическими артефактами. Его знания в области магии позволяют ему управлять стихиями и создавать могущественные заклинания, которые поражают врагов и защищают союзников. Он носит длинные мантии, украшенные магическими символами, и всегда держит при себе посох, который усиливает его магические способности."
    )
    context.user_data["stats"] = test_stats
    context.user_data["backstory"] = (
        "Эльфийский маг родился в древнем лесу, где с детства изучал магию и природу. Он был учеником великого мага, который обучил его искусству заклинаний и магических ритуалов. После многих лет обучения он стал мастером магии и отправился в путешествие, чтобы исследовать мир и защищать его от темных сил. Его цель — найти древние артефакты, которые помогут ему стать еще могущественнее и защитить свой народ от угроз."
    )
    prompt = build_image_prompt(
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        description=context.user_data["description"],
        stats=context.user_data["stats"] if "stats" in context.user_data else test_stats,
    )
    await update.message.reply_text("🎨 Рисую портрет...")

    image_path = await generate_image(prompt)

    await update.message.reply_photo(photo=image_path)

    context.user_data["portrait"] = image_path

