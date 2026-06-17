from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.states import MAINMENU


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    if query:
        await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🧙 Создать персонажа", callback_data='create_character')],
        [InlineKeyboardButton("👤 Мой персонаж", callback_data='check_character')],
        [InlineKeyboardButton("🎲 Начать игру", callback_data='start_game')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Привет, {update.effective_user.first_name}! Добро пожаловать в игру!", reply_markup=reply_markup)
    return MAINMENU


    