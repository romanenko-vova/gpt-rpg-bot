import json

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from config.states import GAME, MAINMENU
from db.games_crud import create_game, get_game_by_tg_id
from handlers.build_scene_handler import build_scene_image_prompt
from handlers.start_handler import remember_character
from services.ask_gpt import generate_text
from services.create_system_promts import create_first_play_system_prompt
from services.generate_image import generate_image
from services.read_model_json import read_model_json, scene_is_ok


def _build_scene_text(scene_dic: dict) -> str:
    scene_text = scene_dic["scene"] + "\n"
    for n, action in enumerate(scene_dic["actions"], start=1):
        scene_text += f"\n{n}. {action}"
    return scene_text


async def handle_continue_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # продолжение само по себе статы не хранит, поднимаем персонажа
    if not context.user_data.get("stats"):
        await remember_character(update.effective_user.id, context)

    game = await get_game_by_tg_id(update.effective_user.id)
    if not game:
        if query:
            await query.message.reply_text(
                "Сохранённой игры не найдено. Начинаем заново."
            )
        return await handle_start_game(update, context)

    if query:
        await query.answer()

    context.user_data["history"] = game["history"]
    context.user_data["last_scene_dic"] = game["last_scene"]

    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = _build_scene_text(game["last_scene"])

    if query:
        await query.message.reply_photo(
            photo=game["scene_image"],
            caption=scene_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.effective_message.reply_photo(
            photo=game["scene_image"],
            caption=scene_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    return GAME


async def handle_start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    if not context.user_data.get("stats"):
        await remember_character(update.effective_user.id, context)

    if not context.user_data.get("stats"):
        if query:
            await query.message.reply_text(
                "Сначала нужно создать персонажа — нажми «🧙 Создать персонажа»"
            )
        return MAINMENU
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
    answer_dic = read_model_json(answer_str_json)
    if not scene_is_ok(answer_dic):
        await message.edit_text(
            "Не получилось разобрать ответ. Нажми «Начать игру» ещё раз."
        )
        return MAINMENU
    keyboard = [
        [InlineKeyboardButton("действие 1", callback_data="action_1")],
        [InlineKeyboardButton("действие 2", callback_data="action_2")],
        [InlineKeyboardButton("действие 3", callback_data="action_3")],
    ]
    scene_text = _build_scene_text(answer_dic)

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
            # именно JSON, чтобы модель и дальше отвечала в этом формате
            "content": json.dumps(answer_dic, ensure_ascii=False),
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
    await create_game(
        update.effective_user.id,
        history=context.user_data["history"],
        last_scene=context.user_data["last_scene_dic"],
        scene_image=scene_image_path,
    )
    return GAME
