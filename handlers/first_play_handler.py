from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.states import GAME, MAIN_MENU
from db.games_crud import (
    get_checkpoint,
    get_current_game,
    list_checkpoints,
    save_current_game,
)
from handlers.build_scene_handler import build_scene_image_prompt
from handlers.scene_message import format_scene, send_scene
from handlers.start_handler import load_character
from services.ask_gpt import generate_text
from services.generate_image import generate_image
from services.read_model_json import is_valid_scene, read_model_json
from services.scene_prompts import build_first_scene_prompt


async def restore_scene(update, context, game):
    if not context.user_data.get("stats"):
        await load_character(update.effective_user.id, context)

    history = game["history"]
    scene = game["last_scene"]
    if not is_valid_scene(scene, require_three_actions=False):
        await update.effective_message.reply_text(
            "Не получилось открыть сохранённую сцену."
        )
        return MAIN_MENU

    context.user_data["history"] = history
    context.user_data["last_scene_dic"] = scene

    # Коммит Артёма (52a6b6d): при продолжении берём номер из сохранения.
    saved_scene_count = game.get("scene_count")
    if saved_scene_count is not None:
        context.user_data["scene_count"] = saved_scene_count
    else:
        # В старых сохранениях счётчика нет. Один ответ ведущего — одна сцена.
        scene_count = 0
        for message in history:
            if message["role"] == "assistant":
                scene_count += 1
        context.user_data["scene_count"] = max(1, scene_count)

    await send_scene(
        update.effective_message,
        game["scene_image"],
        format_scene(scene),
        action_count=min(3, len(scene["actions"])),
    )
    return GAME


async def continue_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    game = await get_current_game(update.effective_user.id)
    if not game:
        await update.effective_message.reply_text(
            "Текущей игры нет. Открой меню командой /start."
        )
        return MAIN_MENU
    return await restore_scene(update, context, game)


async def show_checkpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    checkpoints = await list_checkpoints(update.effective_user.id)
    if not checkpoints:
        await update.effective_message.reply_text("Контрольных точек пока нет.")
        return MAIN_MENU

    buttons = []
    for checkpoint in checkpoints:
        slot_number = checkpoint["save_slot"].removeprefix("slot_")
        button = InlineKeyboardButton(
            f"Сцена {checkpoint['scene_count']}",
            callback_data=f"load_save_{slot_number}",
        )
        buttons.append([button])

    await update.effective_message.reply_text(
        "Выбери контрольную точку:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return MAIN_MENU


async def load_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slot_number = query.data.removeprefix("load_save_")
    game = await get_checkpoint(update.effective_user.id, f"slot_{slot_number}")
    if not game:
        await update.effective_message.reply_text("Такой контрольной точки нет.")
        return MAIN_MENU
    return await restore_scene(update, context, game)


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    if not context.user_data.get("stats"):
        await load_character(user_id, context)

    character = context.user_data
    stats = character.get("stats")
    if not stats:
        await update.effective_message.reply_text(
            "Сначала нужно создать персонажа — нажми «🧙 Создать персонажа»"
        )
        return MAIN_MENU

    status = await update.effective_message.reply_text("⚔️ Игра начинается...")
    prompt = build_first_scene_prompt(
        name=character["name"],
        race=character["race"],
        char_class=character["class"],
        backstory=stats["backstory"],
        stats=stats,
    )
    scene = read_model_json(await generate_text(prompt))
    if not is_valid_scene(scene):
        await status.edit_text(
            "Не получилось разобрать ответ. Нажми «Начать игру» ещё раз."
        )
        return MAIN_MENU

    # Первую сцену начинаем без проверки кубиком.
    scene["needs_roll"] = False
    scene_text = format_scene(scene)
    history = [
        {"role": "system", "content": prompt},
        {"role": "assistant", "content": scene_text},
    ]

    await status.edit_text("🖼 Рисую сцену...")
    image_prompt = await build_scene_image_prompt(
        scene=scene["scene"], race=character["race"], char_class=character["class"]
    )
    image_path = await generate_image(
        image_prompt, reference_image_path=character["portrait"]
    )

    # Коммит Артёма (52a6b6d): при старте сохраняем номер первой сцены.
    await save_current_game(user_id, history, scene, image_path, scene_count=1)
    character["history"] = history
    character["last_scene_dic"] = scene
    character["scene_count"] = 1

    await status.delete()
    await send_scene(update.effective_message, image_path, scene_text)
    return GAME
