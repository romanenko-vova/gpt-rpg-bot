import json

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from config.states import GAME
from handlers.build_scene_handler import build_scene_image_prompt
from services.ask_gpt import generate_text
from services.create_system_promts import create_first_play_system_prompt
from services.generate_image import generate_image


async def handle_start_game(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if "stats" not in context.user_data:
        await query.message.reply_text(
            "Сначала нужно создать персонажа — нажми «🧙 Создать персонажа»"
        )
        return
    message = await query.message.reply_text("⚔️ Игра начинается...")
    stats = context.user_data["stats"]

    system_prompt = create_first_play_system_prompt(
        name=context.user_data["name"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
        backstory=stats["backstory"],
        stats=stats,
    )
    # словарь json "{'scene':'строка', 'actions':['действие 1', 'действие 2', 'действие 3']}"
    answer_str_json = await generate_text(system_prompt)
    answer_dic = json.loads(answer_str_json)
    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = answer_dic["scene"] + "\n"
    n = 1
    for action in answer_dic["actions"]:
        scene_text += "\n" + str(n) + ". " + action
        n += 1

    await message.edit_text("🖼 Рисую сцену...")

    # генерит английский промпт для генерации картики в шаге игры
    image_prompt = await build_scene_image_prompt(
        scene=answer_dic["scene"],
        race=context.user_data["race"],
        char_class=context.user_data["class"],
    )
    context.user_data["history"] = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "assistant",
            "content": scene_text,
        },
    ]
    context.user_data["last_scene_dic"] = answer_dic

    scene_image_path = await generate_image(
        image_prompt,
        reference_image_path=context.user_data["portrait"],
    )

    await message.delete()
    await query.message.reply_photo(
        photo=scene_image_path,
        caption=scene_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return GAME
