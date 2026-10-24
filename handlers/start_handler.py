from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.states import MAINMENU
from db.charackter_crud import get_character_by_tg_id
from db.games_crud import get_game_by_tg_id
from db.users_crud import create_user, get_user_by_tg_id


async def remember_character(telegram_id, context):
    # после перезапуска память пустая, персонажа берём из базы
    character = await get_character_by_tg_id(telegram_id)
    if not character or not character.get("stats"):
        return False

    context.user_data["name"] = character.get("name")
    context.user_data["race"] = character.get("race")
    context.user_data["class"] = character.get("class_name")
    context.user_data["description"] = character.get("description")
    context.user_data["stats"] = character.get("stats")
    context.user_data["portrait"] = character.get("portrait")
    context.user_data["hp"] = character.get("hp")
    context.user_data["max_hp"] = character.get("max_hp")
    return True


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # подтверждение персонажа тоже попадает сюда, флаг ожидания кнопки сбрасываем
    context.user_data["waiting_confirm"] = False

    user = await get_user_by_tg_id(update.effective_user.id)
    if not user:
        user = await create_user(
            update.effective_user.id, update.effective_user.first_name
        )

    query = update.callback_query
    if query:
        await query.answer()
        await query.delete_message()

    saved_game = await get_game_by_tg_id(update.effective_user.id)

    if not context.user_data.get("stats"):
        await remember_character(update.effective_user.id, context)

    keyboard = []
    if not context.user_data.get("portrait"):
        keyboard += [
            [
                InlineKeyboardButton(
                    "🧙 Создать персонажа", callback_data="create_character"
                )
            ],
        ]
    else:
        keyboard += [
            [InlineKeyboardButton("👤 Мой персонаж", callback_data="check_character")],
        ]
    if saved_game:
        keyboard += [
            [InlineKeyboardButton("🎲 Продолжить игру", callback_data="continue_game")],
        ]
    else:
        keyboard += [
            [InlineKeyboardButton("🎲 Начать игру", callback_data="start_game")],
        ]
    keyboard += [
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}! Добро пожаловать в игру!",
        reply_markup=reply_markup,
    )
    return MAINMENU
