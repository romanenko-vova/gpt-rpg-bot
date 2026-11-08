from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.states import MAIN_MENU
from db.character_crud import get_character
from db.games_crud import get_current_game, list_checkpoints
from db.users_crud import register_user


async def load_character(telegram_id, context):
    # После перезапуска берём персонажа из базы, если его ещё нет в памяти.
    character = await get_character(telegram_id)
    if not character or not character["stats"]:
        return

    context.user_data["name"] = character["name"]
    context.user_data["race"] = character["race"]
    context.user_data["class"] = character["class_name"]
    context.user_data["description"] = character["description"]
    context.user_data["stats"] = character["stats"]
    context.user_data["portrait"] = character["portrait"]
    context.user_data["hp"] = character["hp"]
    context.user_data["max_hp"] = character["max_hp"]


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Подтверждение карточки тоже открывает главное меню.
    context.user_data["waiting_confirm"] = False

    user = update.effective_user
    await register_user(user.id, user.first_name)

    query = update.callback_query
    if query:
        await query.answer()
        await query.delete_message()

    if not context.user_data.get("stats"):
        await load_character(user.id, context)

    # Текущая игра и старые контрольные точки открываются разными кнопками.
    current_game = await get_current_game(user.id)
    checkpoints = await list_checkpoints(user.id)

    if context.user_data.get("portrait"):
        character_button = InlineKeyboardButton(
            "👤 Мой персонаж", callback_data="check_character"
        )
    else:
        character_button = InlineKeyboardButton(
            "🧙 Создать персонажа", callback_data="create_character"
        )

    if current_game:
        game_button = InlineKeyboardButton(
            "🎲 Продолжить игру", callback_data="continue_game"
        )
    else:
        game_button = InlineKeyboardButton("🎲 Начать игру", callback_data="start_game")

    buttons = [[character_button], [game_button]]
    if checkpoints:
        buttons.append(
            [
                InlineKeyboardButton(
                    "💾 Контрольные точки", callback_data="show_checkpoints"
                )
            ]
        )
    buttons.append([InlineKeyboardButton("❓ Помощь", callback_data="help")])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {user.first_name}! Добро пожаловать в игру!",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return MAIN_MENU
