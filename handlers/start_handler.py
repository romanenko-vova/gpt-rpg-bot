import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db.users_crud import create_user, get_user_by_tg_id
from config.states import MAINMENU


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_tg_id(update.effective_user.id)
    if not user:
        user = await create_user(update.effective_user.id, update.effective_user.first_name)
        
    query = update.callback_query
    if query:
        await query.answer()
        await query.delete_message()
    keyboard = []
    if "stats" not in context.user_data :
        keyboard += [
            [InlineKeyboardButton("🧙 Создать персонажа", callback_data="create_character")],
        ]
    else:
        keyboard += [
            [InlineKeyboardButton("👤 Мой персонаж", callback_data="check_character")],
            ]
    if "user_id" in user and await get_user_by_tg_id(update.effective_user.id):
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
